from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
import torch
from torchvision import datasets

from .corruptions import REGISTRY as CORR
from .utils.hashing import merkle_hash
from .utils.io import write_json
from .utils.paths import DATA_ROOT
from .utils.seeds import set_seed


def _apply_corruptions(x: np.ndarray, names: list[str], severity: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    img = x.astype(np.float32) / 255.0
    for name in names:
        fn = CORR.get(name)
        if fn is None:
            continue
        # re-seed per op for reproducibility
        _ = rng.integers(0, 2**31 - 1)
        np.random.seed(int(_))
        img = fn(img, severity)
    return (np.clip(img, 0.0, 1.0) * 255).astype(np.uint8)


def ingest_production(
    batch_count: int, split: str, seed: int, corruptions: list[str], severity: int
) -> Path:
    set_seed(seed)
    ds = datasets.CIFAR10(
        root=str(DATA_ROOT), train=(split == "train"), transform=None, download=True
    )
    idx = torch.randperm(len(ds), generator=torch.Generator().manual_seed(seed))[:batch_count]

    images = []
    labels = []
    raw_bytes = []
    for i in idx.tolist():
        img = ds.data[i]
        y = int(ds.targets[i])
        if corruptions:
            img = _apply_corruptions(img, corruptions, severity, seed + i)
        labels.append(y)
        images.append(img)
        raw_bytes.append(img.tobytes())

    h = merkle_hash(raw_bytes)
    stamp = dt.date.today().isoformat()
    out_dir = Path("artifacts/data/production") / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save a tiny sample grid for visual inspection (optional, could be added later)
    meta = {
        "dataset": "cifar10",
        "count": int(batch_count),
        "seed": int(seed),
        "split": split,
        "corruptions": corruptions,
        "severity": int(severity),
        "indices": idx.int().tolist(),
        "labels": labels,
        "merkle": h,
        "date": stamp,
    }
    write_json(out_dir / "batch_meta.json", meta)
    return out_dir


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-count", type=int, default=2000)
    ap.add_argument("--split", type=str, default="test")
    ap.add_argument("--seed", type=int, default=4242)
    ap.add_argument("--corruptions", nargs="*", default=["gaussian_noise", "defocus_blur"])
    ap.add_argument("--severity", type=int, default=3)
    args = ap.parse_args()
    out = ingest_production(
        args.batch_count, args.split, args.seed, args.corruptions, args.severity
    )
    print(f"Production batch ready at: {out}")
