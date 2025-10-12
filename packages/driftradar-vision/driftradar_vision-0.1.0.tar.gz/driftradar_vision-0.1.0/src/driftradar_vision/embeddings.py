from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import torch
from sklearn.decomposition import PCA
from torchvision import datasets, models, transforms

from .utils.paths import DATA_ROOT


@dataclass
class EmbedConfig:
    backbone: str = "resnet18"
    pca_dims: int = 20
    cache_dir: Path = Path("artifacts/reference/embeddings")


def _build_backbone(name: str) -> torch.nn.Module:
    if name == "resnet18":
        m = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        modules = list(m.children())[:-1]  # remove FC
        backbone = torch.nn.Sequential(*modules)
        backbone.eval()
        for p in backbone.parameters():
            p.requires_grad_(False)
        return backbone
    raise ValueError(f"Unsupported backbone: {name}")


def _preproc() -> transforms.Compose:
    return transforms.Compose(
        [
            transforms.Resize(224),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )


def fit_reference_pca(
    cfg: EmbedConfig, indices: np.ndarray, split: str = "train", seed: int = 42
) -> tuple[Path, Path]:
    cfg.cache_dir.mkdir(parents=True, exist_ok=True)
    ds = datasets.CIFAR10(
        root=str(DATA_ROOT), train=(split == "train"), transform=_preproc(), download=True
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    backbone = _build_backbone(cfg.backbone).to(device)

    feats = []
    with torch.inference_mode():
        for i in indices.tolist():
            x, _ = ds[i]
            x = x.unsqueeze(0).to(device)
            f = backbone(x).view(1, -1).cpu().numpy()  # (1, 512)
            feats.append(f)
    feats = np.concatenate(feats, axis=0)

    pca = PCA(n_components=cfg.pca_dims, random_state=seed)
    z = pca.fit_transform(feats)

    fpath = cfg.cache_dir / "ref_feats.npy"
    zpath = cfg.cache_dir / "ref_pca.npy"
    pcapath = cfg.cache_dir / "pca.joblib"

    np.save(fpath, feats)
    np.save(zpath, z)
    joblib.dump(pca, pcapath)

    return zpath, pcapath


def embed_batch(cfg: EmbedConfig, images: np.ndarray, pca_path: Path) -> np.ndarray:
    # images: uint8 [N,H,W,C] RGB 0..255
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    backbone = _build_backbone(cfg.backbone).to(device)
    pca: PCA = joblib.load(pca_path)

    tfm = _preproc()
    feats = []
    with torch.inference_mode():
        for img in images:
            x = tfm(transforms.ToPILImage()(img))  # to tensor normalized
            x = x.unsqueeze(0).to(device)
            f = backbone(x).view(1, -1).cpu().numpy()
            feats.append(f)
    feats = np.concatenate(feats, axis=0)
    z = pca.transform(feats)
    return z
