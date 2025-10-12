from __future__ import annotations

from collections.abc import Callable

import cv2
import numpy as np

# Tiny ImageNet‑C inspired simple variants (fast, dependency‑light)


def _clip01(x: np.ndarray) -> np.ndarray:
    return np.clip(x, 0.0, 1.0)


def gaussian_noise(img: np.ndarray, severity: int) -> np.ndarray:
    # img: float32 in [0,1]
    std_map = {1: 0.03, 2: 0.06, 3: 0.1, 4: 0.15, 5: 0.2}
    noise = np.random.normal(0, std_map.get(severity, 0.1), img.shape).astype(np.float32)
    return _clip01(img + noise)


def defocus_blur(img: np.ndarray, severity: int) -> np.ndarray:
    k_map = {1: 3, 2: 5, 3: 7, 4: 11, 5: 15}
    k = k_map.get(severity, 7)
    out = cv2.GaussianBlur(img, (k, k), sigmaX=0)
    return out


def jpeg_compression(img: np.ndarray, severity: int) -> np.ndarray:
    q_map = {1: 80, 2: 60, 3: 40, 4: 25, 5: 15}
    q = q_map.get(severity, 40)
    x = (img * 255).astype(np.uint8)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), q]
    ok, enc = cv2.imencode(".jpg", cv2.cvtColor(x, cv2.COLOR_RGB2BGR), encode_param)
    if not ok:
        return img
    dec = cv2.imdecode(enc, cv2.IMREAD_COLOR)
    dec = cv2.cvtColor(dec, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    return dec


def snow(img: np.ndarray, severity: int) -> np.ndarray:
    density_map = {1: 0.02, 2: 0.04, 3: 0.06, 4: 0.1, 5: 0.15}
    density = density_map.get(severity, 0.06)
    h, w, _ = img.shape
    flakes = np.random.rand(h, w) < density
    kernel = np.ones((3, 3), np.uint8)
    snowmask = cv2.dilate(flakes.astype(np.uint8), kernel, iterations=1)
    snowmask = cv2.GaussianBlur(snowmask.astype(np.float32), (3, 3), 0)[..., None]
    out = _clip01(img + 0.8 * snowmask)
    return out


def brightness(img: np.ndarray, severity: int) -> np.ndarray:
    delta_map = {1: 0.1, 2: 0.2, 3: 0.3, 4: 0.4, 5: 0.5}
    delta = delta_map.get(severity, 0.3)
    out = _clip01(img + delta)
    return out


REGISTRY: dict[str, Callable[[np.ndarray, int], np.ndarray]] = {
    "gaussian_noise": gaussian_noise,
    "defocus_blur": defocus_blur,
    "jpeg_compression": jpeg_compression,
    "snow": snow,
    "brightness": brightness,
}
