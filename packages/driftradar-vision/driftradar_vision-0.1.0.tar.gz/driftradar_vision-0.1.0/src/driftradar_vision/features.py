from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import torch
from omegaconf import OmegaConf
from torchvision import datasets

from .utils.io import write_json
from .utils.paths import DATA_ROOT, REF_FEATURES
from .utils.seeds import set_seed


@dataclass
class FeatureRow:
    id: int
    label: int
    mean_r: float
    mean_g: float
    mean_b: float
    std_r: float
    std_g: float
    std_b: float
    brightness: float
    contrast: float
    edge_density: float


def _img_stats(img: np.ndarray) -> dict[str, float]:
    # img: HxWxC in [0,255] uint8
    arr = img.astype(np.float32) / 255.0
    means = arr.mean(axis=(0, 1))
    stds = arr.std(axis=(0, 1))

    # Brightness via Y (BT.601)
    y = 0.299 * arr[..., 2] + 0.587 * arr[..., 1] + 0.114 * arr[..., 0]
    brightness = float(y.mean())

    # Contrast as normalized RMS contrast
    contrast = float(y.std())

    # Edge density (Canny)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    edge_density = float((edges > 0).mean())

    return {
        "mean_r": float(means[0]),
        "mean_g": float(means[1]),
        "mean_b": float(means[2]),
        "std_r": float(stds[0]),
        "std_g": float(stds[1]),
        "std_b": float(stds[2]),
        "brightness": brightness,
        "contrast": contrast,
        "edge_density": edge_density,
    }


def compute_reference_features(count: int, seed: int) -> Path:
    set_seed(seed)
    ds = datasets.CIFAR10(root=str(DATA_ROOT), train=True, transform=None, download=True)
    idx = torch.randperm(len(ds), generator=torch.Generator().manual_seed(seed))[:count]

    rows: list[FeatureRow] = []
    for i in idx.tolist():
        img = ds.data[i]  # uint8 HxWxC (RGB)
        y = int(ds.targets[i])
        s = _img_stats(img)
        rows.append(FeatureRow(id=int(i), label=y, **s))

    df = pd.DataFrame([r.__dict__ for r in rows])
    out_dir = REF_FEATURES
    out_dir.mkdir(parents=True, exist_ok=True)
    pq = out_dir / "reference_features.parquet"
    df.to_parquet(pq, index=False)

    summary = {
        "count": int(len(df)),
        "columns": df.columns.tolist(),
        "means": df.mean(numeric_only=True).to_dict(),
        "stds": df.std(numeric_only=True).to_dict(),
    }
    write_json(out_dir / "stats.json", summary)
    return pq


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--config-path", type=str, default="configs")
    ap.add_argument("--config-name", type=str, default="data.yaml")
    args = ap.parse_args()
    cfg = OmegaConf.load(Path(args.config_path) / args.config_name)
    pq = compute_reference_features(cfg.reference.count, cfg.reference.seed)
    print(f"Wrote reference features: {pq}")

    # NEW: if embeddings enabled, fit PCA on reference indices and cache
    if bool(cfg.features.compute_embeddings):
        from .embeddings import EmbedConfig, fit_reference_pca
        from .utils.io import read_json

        meta = read_json(Path("artifacts/data/reference/meta.json"))
        ref_indices = np.array(meta["indices"])
        ebcfg = EmbedConfig(
            backbone=str(cfg.embeddings.backbone),
            pca_dims=int(cfg.embeddings.pca_dims),
            cache_dir=Path(str(cfg.embeddings.cache_dir)),
        )
        zpath, pca = fit_reference_pca(ebcfg, ref_indices, split=cfg.reference.split)
        print(f"Fitted PCA on reference → {zpath}")
