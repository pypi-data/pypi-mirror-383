from __future__ import annotations

from pathlib import Path

import torch
from torchvision import datasets, transforms

from .utils.hashing import merkle_hash
from .utils.io import write_json
from .utils.paths import DATA_ROOT
from .utils.seeds import set_seed


def load_cifar10(split: str, download: bool = True):
    tfm = transforms.ToTensor()
    is_train = split == "train"
    ds = datasets.CIFAR10(root=str(DATA_ROOT), train=is_train, transform=tfm, download=download)
    return ds


def build_reference(count: int, seed: int) -> tuple[Path, dict]:
    set_seed(seed)
    ds = load_cifar10("train")
    # Deterministic slice
    idx = torch.randperm(len(ds), generator=torch.Generator().manual_seed(seed))[:count]

    # Merkle hash over raw bytes (as provided by dataset samples)
    raw_bytes = []
    ids = []
    labels = []
    for i in idx.tolist():
        img, y = ds.data[i], ds.targets[i]
        raw_bytes.append(img.tobytes())
        ids.append(int(i))
        labels.append(int(y))
    h = merkle_hash(raw_bytes)

    meta = {
        "dataset": "cifar10",
        "count": int(count),
        "seed": int(seed),
        "split": "train",
        "indices": ids,
        "labels": labels,
        "merkle": h,
    }
    out = DATA_ROOT / "reference" / "meta.json"
    write_json(out, meta)
    return out, meta


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    path, meta = build_reference(args.count, args.seed)
    print(f"Reference slice written: {path} with merkle={meta['merkle']}")
