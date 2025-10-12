from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch


def plot_confusion(cm: np.ndarray, out_png: Path) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(6, 5))
    plt.imshow(cm, interpolation="nearest")
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.colorbar()
    plt.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def plot_calibration(
    logits: torch.Tensor, target: torch.Tensor, out_png: Path, n_bins: int = 15
) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    probs = logits.softmax(1)
    conf, pred = probs.max(1)
    acc = pred.eq(target)
    bins = torch.linspace(0, 1, n_bins + 1)
    xs, ys = [], []
    for i in range(n_bins):
        m = (conf > bins[i]) & (conf <= bins[i + 1])
        if m.any():
            xs.append(float(conf[m].mean()))
            ys.append(float(acc[m].float().mean()))
    fig = plt.figure(figsize=(5, 5))
    plt.plot([0, 1], [0, 1])
    plt.scatter(xs, ys)
    plt.xlabel("Confidence")
    plt.ylabel("Accuracy")
    plt.title("Calibration Curve")
    plt.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)
