from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from omegaconf import OmegaConf

# ------------------------
# Config dataclasses
# ------------------------


@dataclass
class Thresholds:
    psi_threshold: float = 0.2
    confidence_drop_pct: float = 10.0
    aggregate_threshold: float = 0.5
    probe_accuracy_drop_pp: float = 2.0
    require_drift_flag: bool = False


@dataclass
class Cooldowns:
    retrain_days: int = 7


@dataclass
class TrainingCfg:
    config_path: str = "configs"
    config_name: str = "model-ci.yaml"
    override: dict[str, Any] | None = None


@dataclass
class MlflowCfg:
    tracking_uri: str = "file:./mlruns"
    register_name: str = "driftradar-vision-resnet18"
    stage_after_retrain: str = "Staging"


@dataclass
class ArtifactsCfg:
    reports_dir: str = "artifacts/reports/evidently"
    ge_dir: str = "artifacts/reports/ge"
    out_dir: str = "artifacts/summary"


@dataclass
class DataCfg:
    reference_fraction: float = 1.0
    recent_batches: int = 5
    max_samples: int = 20000


# ------------------------
# Utils
# ------------------------


def _read_json(p: Path) -> dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _now_str() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _latest_evidently_dir(reports_dir: Path) -> Path:
    # choose today's folder if exists, else _latest
    candidates = [p for p in reports_dir.iterdir() if p.is_dir() and p.name != "_latest"]
    if candidates:
        latest = sorted(candidates, key=lambda x: x.name)[-1]
        return latest
    return reports_dir / "_latest"


def _last_retrain_marker(out_dir: Path) -> Path:
    return out_dir / "last_retrain.txt"


def _days_since(dt_str: str | None) -> int | None:
    if not dt_str:
        return None
    try:
        t = datetime.fromisoformat(dt_str.replace("Z", ""))
        return (datetime.utcnow() - t).days
    except Exception:
        return None


def _write_decision(out_dir: Path, payload: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "latest_decision.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _copy_staging_onnx() -> str | None:
    """Copy artifacts/runs/onnx/model.onnx -> staging.onnx if present."""
    from shutil import copyfile

    onnx = Path("artifacts/runs/onnx/model.onnx")
    if not onnx.exists():
        # Some trainers may export production.onnx / staging.onnx directly
        alt = Path("artifacts/runs/onnx/staging.onnx")
        return str(alt) if alt.exists() else None
    dst = onnx.with_name("staging.onnx")
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        copyfile(onnx, dst)
        return str(dst)
    except Exception:
        return None


# ------------------------
# Core logic
# ------------------------


def should_retrain(
    summary: dict[str, Any], thresholds: Thresholds
) -> tuple[bool, str, float, float]:
    """Decide whether to retrain based on summary.json and prediction_drift.json."""
    # Evidently / embedding summary
    is_drifted = bool(summary.get("is_drifted", False))
    feature_drift_flag = bool(summary.get("feature_drift_flag", False))
    emb_psi = float(summary.get("embedding_top5_psi_mean", 0.0))

    # Prediction drift (confidence drop)
    conf_drop = float(summary.get("prediction_confidence_drop_pct", 0.0))

    reasons = []
    tr = False

    if thresholds.require_drift_flag:
        if feature_drift_flag or is_drifted:
            reasons.append("evidently_dataset_drift_flag")
        else:
            reasons.append("no_evidently_flag")

    # Embedding PSI gate
    if emb_psi >= thresholds.psi_threshold:
        tr = True
        reasons.append(f"emb_psi({emb_psi:.3f})>=psi({thresholds.psi_threshold})")

    # Confidence drop gate
    if conf_drop >= thresholds.confidence_drop_pct:
        tr = True
        reasons.append(f"conf_drop({conf_drop:.1f}%)>=thr({thresholds.confidence_drop_pct}%)")

    # Aggregate gate (optional)
    if not tr and thresholds.aggregate_threshold is not None:
        agg = 0.0
        agg += 0.5 if emb_psi >= thresholds.psi_threshold else 0.0
        agg += 0.5 if conf_drop >= thresholds.confidence_drop_pct else 0.0
        if agg >= thresholds.aggregate_threshold:
            tr = True
            reasons.append(f"agg({agg:.2f})>=agg_thr({thresholds.aggregate_threshold:.2f})")

    # If require_drift_flag, enforce
    if thresholds.require_drift_flag and not (feature_drift_flag or is_drifted):
        tr = False

    return tr, ";".join(reasons) if reasons else "no_trigger", emb_psi, conf_drop


def load_policy(config_path: Path, config_name: str):
    p = config_path / config_name
    if not p.exists():
        raise FileNotFoundError(f"Policy file not found: {p}")
    pcfg = OmegaConf.load(p)

    thresholds = Thresholds(
        psi_threshold=float(pcfg.thresholds.psi_threshold),
        confidence_drop_pct=float(pcfg.thresholds.confidence_drop_pct),
        aggregate_threshold=float(pcfg.thresholds.aggregate_threshold),
        probe_accuracy_drop_pp=float(pcfg.thresholds.get("probe_accuracy_drop_pp", 2.0)),
        require_drift_flag=bool(pcfg.thresholds.get("require_drift_flag", False)),
    )
    cooldowns = Cooldowns(retrain_days=int(pcfg.cooldowns.retrain_days))
    training = TrainingCfg(
        config_path=str(pcfg.training.config_path),
        config_name=str(pcfg.training.config_name),
        override=OmegaConf.to_container(pcfg.training.get("override", {}), resolve=True),
    )
    mlflowc = MlflowCfg(
        tracking_uri=str(pcfg.mlflow.tracking_uri),
        register_name=str(pcfg.mlflow.register_name),
        stage_after_retrain=str(pcfg.mlflow.stage_after_retrain),
    )
    artifacts = ArtifactsCfg(
        reports_dir=str(pcfg.artifacts.reports_dir),
        ge_dir=str(pcfg.artifacts.ge_dir),
        out_dir=str(pcfg.artifacts.out_dir),
    )
    data = DataCfg(
        reference_fraction=float(pcfg.data.get("reference_fraction", 1.0)),
        recent_batches=int(pcfg.data.get("recent_batches", 5)),
        max_samples=int(pcfg.data.get("max_samples", 20000)),
    )
    return thresholds, cooldowns, training, mlflowc, artifacts, data


def build_train_config_with_overrides(
    base_path: Path, base_name: str, overrides: dict[str, Any] | None
) -> tuple[Path, str]:
    """Create a temporary train config YAML applying overrides; return (path, name)."""
    if not overrides:
        return base_path, base_name
    cfg_path = base_path / base_name
    cfg = OmegaConf.load(cfg_path)
    for k, v in (overrides or {}).items():
        # simple top-level overrides (epochs, batch_size, num_workers, pin_memory, etc.)
        cfg[k] = v
    out_dir = Path("artifacts") / "temp"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_name = f"{Path(base_name).stem}-retrain.yaml"
    out_path = out_dir / out_name
    OmegaConf.save(cfg, out_path)
    return out_dir, out_name


def call_trainer(train_path: Path, train_name: str) -> str:
    """Invoke the trainer module; return MLflow run_id printed by train.py (or empty)."""
    # We rely on train.py printing the run_id on success (your train.py returns it).
    cmd = [
        sys.executable,
        "-m",
        "driftradar_vision.train",
        "--config-path",
        str(train_path),
        "--config-name",
        str(train_name),
    ]
    print(f"[retrain] Launching trainer: {' '.join(cmd)}")
    cp = subprocess.run(cmd, capture_output=True, text=True)
    sys.stdout.write(cp.stdout)
    sys.stderr.write(cp.stderr)
    if cp.returncode != 0:
        raise SystemExit(f"Trainer failed (exit={cp.returncode}). See logs above.")
    # Best-effort parse: search last line for run id like "run_id: <id>"
    run_id = ""
    for line in reversed(cp.stdout.strip().splitlines()):
        if "run_id" in line.lower():
            run_id = line.split(":")[-1].strip()
            break
    return run_id


def discover_latest_staging(mlflow_uri: str, name: str) -> tuple[str | None, int | None]:
    """Return (run_id, version) of the latest Staging model, or (None, None)."""
    import mlflow
    from mlflow.tracking import MlflowClient

    mlflow.set_tracking_uri(mlflow_uri)
    c = MlflowClient()
    versions = c.search_model_versions(f"name='{name}'")
    staging = [v for v in versions if v.current_stage == "Staging"]
    if not staging:
        return None, None
    # choose highest version number
    v = sorted(staging, key=lambda x: int(x.version))[-1]
    return v.run_id, int(v.version)


def main(config_path: str, config_name: str) -> int:
    # Load policy
    thresholds, cooldowns, training, mlflowc, artifacts, _ = load_policy(
        Path(config_path), config_name
    )

    reports_dir = Path(artifacts.reports_dir)
    out_dir = Path(artifacts.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load latest Evidently summary + prediction drift
    ev_dir = _latest_evidently_dir(reports_dir)
    ev_summary = _read_json(ev_dir / "summary.json")
    pred = _read_json(ev_dir / "prediction_drift.json")
    merged = dict(ev_summary)
    merged.update(
        {
            "prediction_confidence_drop_pct": pred.get("confidence_drop_pct", 0.0),
            "mean_conf_reference": pred.get("mean_conf_reference", 0.0),
            "mean_conf_corrupted": pred.get("mean_conf_corrupted", 0.0),
        }
    )

    # Decision: thresholds
    trigger, reason, emb_psi, conf_drop = should_retrain(merged, thresholds)

    # Decision: cooldown
    last_marker = _last_retrain_marker(out_dir)
    last_str = last_marker.read_text(encoding="utf-8").strip() if last_marker.exists() else None
    days = _days_since(last_str)
    cooldown_ok = (days is None) or (days >= int(cooldowns.retrain_days))
    if not cooldown_ok:
        reason = f"{reason};cooldown({days}d)<min({cooldowns.retrain_days}d)"

    # Final decision
    retrain_triggered = bool(trigger and cooldown_ok)

    decision_payload: dict[str, Any] = {
        "time_utc": _now_str(),
        "retrain_triggered": retrain_triggered,
        "reason": reason,
        "cooldown_days_min": cooldowns.retrain_days,
        "days_since_last_retrain": days,
        "thresholds": {
            "psi_threshold": thresholds.psi_threshold,
            "confidence_drop_pct": thresholds.confidence_drop_pct,
            "aggregate_threshold": thresholds.aggregate_threshold,
            "require_drift_flag": thresholds.require_drift_flag,
        },
        "observed": {
            "embedding_top5_psi_mean": emb_psi,
            "prediction_confidence_drop_pct": conf_drop,
        },
        "run_id": "",
        "staging_version": "",
        "onnx_staging_path": "",
        "mlflow_uri": mlflowc.tracking_uri,
        "register_name": mlflowc.register_name,
        "evidently_dir": str(ev_dir),
    }

    if not retrain_triggered:
        _write_decision(out_dir, decision_payload)
        print(json.dumps(decision_payload, indent=2))
        return 0

    # Build temp train config if overrides provided
    train_path, train_name = build_train_config_with_overrides(
        Path(training.config_path), training.config_name, training.override
    )

    # Run trainer
    run_id = call_trainer(train_path, train_name)
    decision_payload["run_id"] = run_id

    # Copy ONNX to "staging.onnx" as a convenience for smoke tests
    onnx_path = _copy_staging_onnx()
    if onnx_path:
        decision_payload["onnx_staging_path"] = onnx_path

    # Discover latest Staging version (the trainer already registers + stages)
    run_id2, version = discover_latest_staging(mlflowc.tracking_uri, mlflowc.register_name)
    decision_payload["staging_version"] = version if version is not None else ""

    # Update cooldown marker
    last_marker.write_text(_now_str(), encoding="utf-8")

    # Persist decision
    _write_decision(out_dir, decision_payload)
    print(json.dumps(decision_payload, indent=2))
    return 0


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--config-path", type=str, default="configs")
    ap.add_argument("--config-name", type=str, default="policy.yaml")
    args = ap.parse_args()
    sys.exit(main(args.config_path, args.config_name))
