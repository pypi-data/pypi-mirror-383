from __future__ import annotations

import numpy as np
import torch
from sklearn.metrics import confusion_matrix, f1_score
from torch import Tensor


def top1(pred: Tensor, target: Tensor) -> float:
    return float((pred.argmax(1) == target).float().mean().item())


def perclass_f1(pred_logits: Tensor, target: Tensor, num_classes: int = 10) -> dict:
    y_true = target.cpu().numpy()
    y_pred = pred_logits.argmax(1).cpu().numpy()
    f1s = f1_score(y_true, y_pred, labels=list(range(num_classes)), average=None, zero_division=0)
    return {str(i): float(f) for i, f in enumerate(f1s)}


def ece(pred_logits: Tensor, target: Tensor, n_bins: int = 15) -> float:
    probs = pred_logits.softmax(1)
    conf, pred = probs.max(1)
    acc = pred.eq(target)
    bins = torch.linspace(0, 1, n_bins + 1, device=probs.device)
    ece = torch.zeros(1, device=probs.device)
    for i in range(n_bins):
        m = (conf > bins[i]) & (conf <= bins[i + 1])
        if m.any():
            e = torch.abs(acc[m].float().mean() - conf[m].mean()) * m.float().mean()
            ece += e
    return float(ece.item())


def confusion(pred_logits: Tensor, target: Tensor, num_classes: int = 10) -> np.ndarray:
    y_true = target.cpu().numpy()
    y_pred = pred_logits.argmax(1).cpu().numpy()
    return confusion_matrix(y_true, y_pred, labels=list(range(num_classes)))
