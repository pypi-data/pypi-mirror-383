from __future__ import annotations

from torch import nn
from torchvision import models


def build_backbone(arch: str, num_classes: int = 10) -> nn.Module:
    if arch == "resnet18":
        m = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        in_feat = m.fc.in_features
        m.fc = nn.Linear(in_feat, num_classes)
        return m
    raise ValueError(f"Unsupported arch: {arch}")
