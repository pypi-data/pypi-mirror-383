from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from omegaconf import OmegaConf
from torchvision import datasets

# Evidently import compatibility: 0.7+ (new API) and legacy (<0.7)
try:
    # Evidently >= 0.7
    from evidently import Report

    try:
        from evidently.presets import DataDriftPreset  # primary location in 0.7+
    except Exception:
        from evidently.metric_preset import DataDriftPreset  # rare fallback
except Exception:
    # Evidently < 0.7
    from evidently.metric_preset import DataDriftPreset
    from evidently.report import Report

from .data_prod import _apply_corruptions
from .embeddings import EmbedConfig, embed_batch, fit_reference_pca
from .utils.io import read_json, write_json
from .utils.paths import REF_FEATURES


@dataclass
class DriftCfg:
    psi_threshold: float
    js_threshold: float
    ks_pvalue_min: float
    embedding_pca_dims: int
    weights_features: float
    weights_embeddings: float
    reports_dir: Path


# ----------------- helpers ----------------- #
def _load_reference_features() -> pd.DataFrame:
    pq = REF_FEATURES / "reference_features.parquet"
    if not pq.exists():
        raise FileNotFoundError("Run features.py first to build reference features.")
    return pd.read_parquet(pq)


def _distribution_features_corrupted(
    indices: list[int],
    split: str,
    corruptions: list[str],
    severity: int,
    seed: int,
) -> pd.DataFrame:
    """
    Recompute the same basic image stats used in features.py, but on a corrupted batch.
    """
    from .features import _img_stats  # reuse exactly the same stats code
    from .utils.paths import DATA_ROOT

    ds = datasets.CIFAR10(
        root=str(DATA_ROOT),
        train=(split == "train"),
        transform=None,
        download=True,
    )
    rows = []
    for i in indices:
        raw = ds.data[i]
        img = _apply_corruptions(raw, corruptions, severity, seed + i)
        y = int(ds.targets[i])
        s = _img_stats(img)
        s.update({"id": int(i), "label": y})
        rows.append(s)
    return pd.DataFrame(rows)


def _ensure_reference_embeddings(cfg: EmbedConfig, ref_indices: np.ndarray) -> Path:
    """
    Ensure PCA is fit and cached on the reference slice; return PCA joblib path.
    """
    pca_path = Path(cfg.cache_dir) / "pca.joblib"
    if not pca_path.exists():
        _, ppath = fit_reference_pca(cfg, ref_indices, split="train")
        return ppath
    return pca_path


def _embed_corrupted_batch(
    cfg: EmbedConfig,
    indices: list[int],
    split: str,
    corruptions: list[str],
    severity: int,
    seed: int,
) -> np.ndarray:
    """
    Embed a corrupted batch and project with cached PCA.
    """
    from .utils.paths import DATA_ROOT

    ds = datasets.CIFAR10(
        root=str(DATA_ROOT),
        train=(split == "train"),
        transform=None,
        download=True,
    )
    imgs = []
    for i in indices:
        raw = ds.data[i]
        img = _apply_corruptions(raw, corruptions, severity, seed + i)
        imgs.append(img)
    imgs = np.stack(imgs, axis=0)
    z = embed_batch(cfg, imgs, Path(cfg.cache_dir) / "pca.joblib")
    return z


def _psi(a: np.ndarray, b: np.ndarray, bins: int = 20) -> float:
    """
    Population Stability Index between two 1D distributions.
    """
    lo = min(np.nanmin(a), np.nanmin(b))
    hi = max(np.nanmax(a), np.nanmax(b)) + 1e-8
    hist_a, edges = np.histogram(a, bins=bins, range=(lo, hi), density=True)
    hist_b, _ = np.histogram(b, bins=edges, density=True)
    hist_a = hist_a.astype(np.float64) + 1e-8
    hist_b = hist_b.astype(np.float64) + 1e-8
    psi = np.sum((hist_b - hist_a) * np.log(hist_b / hist_a))
    return float(abs(psi))


# ----------------- main ----------------- #
def run(config_path: Path, drift_name: str, data_cfg_path: Path, data_name: str) -> int:
    dcfg = OmegaConf.load(config_path / drift_name)
    pcfg = OmegaConf.load(data_cfg_path / data_name)

    cfg = DriftCfg(
        psi_threshold=float(dcfg.signals.psi_threshold),
        js_threshold=float(dcfg.signals.js_threshold),
        ks_pvalue_min=float(dcfg.signals.ks_pvalue_min),
        embedding_pca_dims=int(dcfg.signals.embedding_pca_dims),
        weights_features=float(dcfg.weights.features),
        weights_embeddings=float(dcfg.weights.embeddings),
        reports_dir=Path(dcfg.output.reports_dir),
    )

    ref_df = _load_reference_features()

    # Determine indices for the current "production" batch (from meta if present)
    batch_meta = (
        Path(pcfg.production.out_dir) / pd.Timestamp.today().date().isoformat() / "batch_meta.json"
    )
    if batch_meta.exists():
        meta = read_json(batch_meta)
        indices: list[int] = meta["indices"]
    else:
        # Deterministic fallback if meta not found
        indices = list(range(int(pcfg.production.batch_count)))

    corruptions = list(pcfg.production.corruptions)
    severity = int(pcfg.production.severity)

    # Build current (corrupted) feature table to feed Evidently
    prod_df = _distribution_features_corrupted(
        indices,
        pcfg.production.split,
        corruptions,
        severity,
        int(pcfg.production.seed),
    )

    # Evidently on tabular feature drift
    ref_df_e = ref_df.drop(columns=["id", "label"], errors="ignore")
    prod_df_e = prod_df.drop(columns=["id", "label"], errors="ignore")
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=ref_df_e, current_data=prod_df_e)

    # Embedding drift via PCA
    ebcfg = EmbedConfig(
        backbone=str(pcfg.embeddings.backbone),
        pca_dims=int(pcfg.embeddings.pca_dims),
        cache_dir=Path(str(pcfg.embeddings.cache_dir)),
    )

    # Reference indices for PCA fit cache
    if Path("artifacts/data/reference/meta.json").exists():
        ref_indices = np.array(read_json(Path("artifacts/data/reference/meta.json"))["indices"])
    else:
        ref_indices = np.arange(min(10000, len(ref_df)))

    pca_path = _ensure_reference_embeddings(ebcfg, ref_indices)
    z_prod = _embed_corrupted_batch(
        ebcfg,
        indices,
        pcfg.production.split,
        corruptions,
        severity,
        int(pcfg.production.seed),
    )

    # Load reference PCA projections
    from joblib import load as _load_joblib

    _ = _load_joblib(pca_path)  # ensure readable
    ref_z = np.load(ebcfg.cache_dir / "ref_pca.npy")

    # PSI across PCA dims (top-5 mean is our summary)
    psi_dims = []
    D = min(ref_z.shape[1], z_prod.shape[1], cfg.embedding_pca_dims)
    for d in range(D):
        psi_dims.append(_psi(ref_z[:, d], z_prod[:, d], bins=30))
    emb_agg = float(np.mean(sorted(psi_dims, reverse=True)[:5])) if psi_dims else 0.0

    # Compose decision
    # Feature drift flag from Evidently (version-adaptive dict extraction)
    def _report_to_dict(_report: Report) -> dict:
        # Try as_dict (legacy), then dict(), then json()
        try:
            return _report.as_dict()  # <0.7 and some 0.7 builds
        except Exception:
            try:
                return _report.dict()  # pydantic-style in 0.7+
            except Exception:
                try:
                    return json.loads(_report.json())
                except Exception:
                    return {}

    ev_dict = _report_to_dict(report)

    # Different Evidently versions may store keys differently; try robust access:
    feat_drift_flag = False
    try:
        feat_drift_flag = bool(ev_dict["metrics"][0]["result"]["dataset_drift"])
    except Exception:
        # Fallback heuristic: look for any "dataset_drift" flags in the structure
        def _scan_for_drift(node):
            if isinstance(node, dict):
                if "dataset_drift" in node:
                    return bool(node["dataset_drift"])
                return any(_scan_for_drift(v) for v in node.values())
            if isinstance(node, list):
                return any(_scan_for_drift(v) for v in node)
            return False

        feat_drift_flag = _scan_for_drift(ev_dict)

    agg_score = float(
        min(
            1.0,
            cfg.weights_features * (1.0 if feat_drift_flag else 0.0)
            + cfg.weights_embeddings * (emb_agg > cfg.psi_threshold),
        )
    )
    is_drifted = bool(
        (feat_drift_flag or (emb_agg > cfg.psi_threshold))
        or (agg_score >= float(dcfg.policy.aggregate_threshold))
    )

    # Write outputs
    out_dir = cfg.reports_dir / pd.Timestamp.today().date().isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / "report.html"
    json_path = out_dir / "report.json"

    # Robust saving across Evidently versions
    saved_html = False
    saved_json = False
    try:
        report.save_html(str(html_path))
        saved_html = True
    except Exception:
        try:
            report.save(str(html_path))  # some 0.7 builds expose generic save()
            saved_html = True
        except Exception:
            pass

    try:
        report.save_json(str(json_path))
        saved_json = True
    except Exception:
        try:
            # final fallback: write dict/json ourselves
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(ev_dict if ev_dict else _report_to_dict(report), f)
            saved_json = True
        except Exception:
            pass

    if not (saved_html and saved_json):
        print("[Evidently] Warning: report saved with fallback path (API mismatch).")

    summary = {
        "is_drifted": is_drifted,
        "feature_drift_flag": bool(feat_drift_flag),
        "embedding_top5_psi_mean": emb_agg,
        "psi_threshold": cfg.psi_threshold,
        "corruptions": corruptions,
        "severity": severity,
        "indices_preview": indices[:10],
        "html": str(html_path),
        "json": str(json_path),
    }
    write_json(out_dir / "summary.json", summary)

    latest = cfg.reports_dir / "_latest"
    latest.mkdir(parents=True, exist_ok=True)
    write_json(latest / "summary.json", summary)

    # ---------- Milestone D: prediction drift ----------
    # Compute prediction drift with current Production model if available,
    # otherwise fallback to best local checkpoint. Persist alongside Evidently artifacts.
    from shutil import copyfile

    from .prediction_drift import PredDriftCfg, compute_prediction_drift

    pdcfg = PredDriftCfg(
        tracking_uri="file:./mlruns",
        register_name="driftradar-vision-resnet18",
        img_size=224,
        split=str(pcfg.production.split),
        limit=1000,  # small probe
        outputs_dir=out_dir,
    )
    pred = compute_prediction_drift(pdcfg, corruptions, severity)
    # mirror to _latest
    copyfile(out_dir / "prediction_drift.json", latest / "prediction_drift.json")

    # Echo compact combined view for logs
    combined = {
        **summary,
        "prediction_confidence_drop_pct": float(pred.get("confidence_drop_pct", 0.0)),
        "mean_conf_reference": float(pred.get("mean_conf_reference", 0.0)),
        "mean_conf_corrupted": float(pred.get("mean_conf_corrupted", 0.0)),
    }
    print(json.dumps(combined, indent=2))

    return 0


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--config-path", type=str, default="configs")
    ap.add_argument("--config-name", type=str, default="drift.yaml")
    ap.add_argument("--data-config-path", type=str, default="configs")
    ap.add_argument("--data-config-name", type=str, default="data.yaml")
    args = ap.parse_args()
    raise SystemExit(
        run(
            Path(args.config_path),
            args.config_name,
            Path(args.data_config_path),
            args.data_config_name,
        )
    )
