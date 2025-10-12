from __future__ import annotations

from collections.abc import Iterable
from io import BytesIO

import numpy as np
import torch
from PIL import Image, ImageFilter
from torch.utils.data import DataLoader, Dataset, Subset
from torchvision import datasets, transforms

# ----------------------------
# Core utils
# ----------------------------


def _device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _pin_memory_default() -> bool:
    # Only pin when CUDA is available
    return bool(torch.cuda.is_available())


def _num_workers_default() -> int:
    # Windows spawn + Python 3.12 + local callables → pickling pain.
    # Force single-process loading on Windows to avoid errors like:
    # "AttributeError: Can't get local object ... _Wrap"
    import platform

    return 0 if platform.system() == "Windows" else 2


# ----------------------------
# Transforms
# ----------------------------


def _build_transform(img_size: int) -> transforms.Compose:
    return transforms.Compose(
        [
            transforms.Resize(img_size),
            transforms.CenterCrop(img_size),
            transforms.ToTensor(),
        ]
    )


# ----------------------------
# Dataset wrappers
# ----------------------------


class CorruptedCIFAR(Dataset):
    """
    CIFAR-10 with deterministic corruptions applied on-the-fly using PIL/numpy.
    Implemented as a top-level class so it's picklable by DataLoader workers.

    Supported corruptions:
      - "gaussian_noise": add N(0, sigma) in [0,255] space
      - "defocus_blur": approximate with GaussianBlur (radius by severity)
      - "jpeg_compression": re-encode with low quality
    """

    def __init__(
        self,
        root: str,
        split: str,
        transform: transforms.Compose | None,
        corruption_names: list[str],
        severity: int,
        indices: Iterable[int] | None = None,
    ):
        self.ds = datasets.CIFAR10(
            root=root,
            train=(split == "train"),
            transform=None,  # we handle transform after corruption
            download=True,
        )
        self.transform = transform
        self.corruption_names = [str(c).lower() for c in corruption_names]
        self.severity = int(severity)
        self.indices = list(indices) if indices is not None else list(range(len(self.ds)))

    def __len__(self) -> int:
        return len(self.indices)

    def __getitem__(self, i: int):
        j = self.indices[i]
        # raw numpy uint8 HxWxC (RGB)
        img_np = self.ds.data[j]
        label = int(self.ds.targets[j])

        # Apply corruptions deterministically based on (j, severity) if you wish.
        img = Image.fromarray(img_np, mode="RGB")
        img = _apply_corruptions_pil(img, self.corruption_names, self.severity)

        if self.transform is not None:
            img = self.transform(img)
        return img, label


# ----------------------------
# Corruptions (top-level, picklable)
# ----------------------------


def _apply_corruptions_pil(img: Image.Image, names: list[str], severity: int) -> Image.Image:
    out = img
    for name in names:
        if name == "gaussian_noise":
            out = _corr_gaussian_noise(out, severity)
        elif name == "defocus_blur":
            out = _corr_defocus_blur(out, severity)
        elif name == "jpeg_compression":
            out = _corr_jpeg(out, severity)
        # add more here if needed
    return out


def _severity_scale(severity: int, lo: float, hi: float) -> float:
    s = max(1, min(int(severity), 5))
    return lo + (hi - lo) * ((s - 1) / 4.0)


def _corr_gaussian_noise(img: Image.Image, severity: int) -> Image.Image:
    # Work in float, add noise, clip, back to uint8
    sigma = _severity_scale(severity, lo=5.0, hi=35.0)  # pixel space
    arr = np.asarray(img).astype(np.float32)
    noise = np.random.normal(0.0, sigma, size=arr.shape).astype(np.float32)
    arr = np.clip(arr + noise, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(arr, mode="RGB")


def _corr_defocus_blur(img: Image.Image, severity: int) -> Image.Image:
    radius = _severity_scale(severity, lo=0.5, hi=3.0)
    return img.filter(ImageFilter.GaussianBlur(radius=radius))


def _corr_jpeg(img: Image.Image, severity: int) -> Image.Image:
    quality = int(
        round(_severity_scale(6 - severity, lo=15, hi=60))
    )  # higher severity → lower quality
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


# ----------------------------
# Public API
# ----------------------------


def build_loader(
    split: str,
    img_size: int,
    limit: int | None = None,
    *,
    batch_size: int = 128,
    num_workers: int | None = None,
    pin_memory: bool | None = None,
) -> DataLoader:
    """
    Deterministic CIFAR-10 loader with optional limit on number of samples.
    """
    tfm = _build_transform(img_size)
    ds = datasets.CIFAR10(
        root="artifacts/data", train=(split == "train"), transform=tfm, download=True
    )

    if limit is not None:
        indices = list(range(min(int(limit), len(ds))))
        ds = Subset(ds, indices)

    if num_workers is None:
        num_workers = _num_workers_default()
    if pin_memory is None:
        pin_memory = _pin_memory_default()

    dl = DataLoader(
        ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
        drop_last=False,
    )
    return dl


@torch.no_grad()
def predict_loader(
    model: torch.nn.Module, dl: DataLoader, device: torch.device
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Run inference over a DataLoader, returning stacked logits and labels tensors (CPU).
    """
    model.eval().to(device)
    logits_list: list[torch.Tensor] = []
    labels_list: list[torch.Tensor] = []
    for x, y in dl:
        x = x.to(device, non_blocking=True)
        out = model(x)
        logits_list.append(out.detach().cpu())
        labels_list.append(y.detach().cpu())
    logits = torch.cat(logits_list, dim=0) if logits_list else torch.empty(0, 10)
    labels = torch.cat(labels_list, dim=0) if labels_list else torch.empty(0, dtype=torch.long)
    return logits, labels


@torch.no_grad()
def predict_corrupted(
    model: torch.nn.Module,
    split: str,
    img_size: int,
    corruption_names: list[str],
    severity: int,
    *,
    limit: int | None = None,
    batch_size: int = 128,
    num_workers: int | None = None,
    pin_memory: bool | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Build a corrupted CIFAR-10 dataset and run inference with the given model.
    Returns (logits, labels) on CPU.

    NOTE: To avoid Windows pickling issues, this function uses num_workers=0 by default on Windows.
    """
    if num_workers is None:
        num_workers = _num_workers_default()
    if pin_memory is None:
        pin_memory = _pin_memory_default()

    tfm = _build_transform(img_size)
    base = datasets.CIFAR10(
        root="artifacts/data", train=(split == "train"), transform=None, download=True
    )

    indices = list(range(len(base)))
    if limit is not None:
        indices = indices[: int(limit)]

    ds = CorruptedCIFAR(
        root="artifacts/data",
        split=split,
        transform=tfm,
        corruption_names=corruption_names,
        severity=severity,
        indices=indices,
    )

    dl = DataLoader(
        ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
        drop_last=False,
    )

    device = _device()
    return predict_loader(model.to(device), dl, device)
