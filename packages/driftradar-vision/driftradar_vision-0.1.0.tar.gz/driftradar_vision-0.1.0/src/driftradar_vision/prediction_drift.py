from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import mlflow
import numpy as np
import torch

from .utils.io import write_json


@dataclass
class PredDriftCfg:
    tracking_uri: str
    register_name: str
    img_size: int
    split: str
    limit: int | None
    outputs_dir: Path


def _load_production_pyfunc(tracking_uri: str, register_name: str):
    mlflow.set_tracking_uri(tracking_uri)
    uri = f"models:/{register_name}/Production"
    try:
        model = mlflow.pyfunc.load_model(uri)

        def f(x):
            return torch.tensor(model.predict(x)).float()

        return f
    except Exception:
        return None


def _fallback_best_local(img_size: int):
    from pathlib import Path

    from .models import build_backbone

    m = build_backbone("resnet18")
    ckpt = Path("artifacts/runs/best.pt")
    if ckpt.exists():
        m.load_state_dict(torch.load(ckpt, map_location="cpu"))
    m.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    m = m.to(device)

    def _pred(x: np.ndarray) -> torch.Tensor:
        with torch.no_grad():
            t = torch.from_numpy(x).float().to(device)
            if t.ndim == 3:
                t = t.unsqueeze(0)
            out = m(t)
            return out.cpu()

    return _pred


def _mean_confidence(logits: torch.Tensor) -> float:
    p = torch.softmax(logits, dim=1)
    c = torch.max(p, dim=1).values
    return float(c.mean().item())


def compute_prediction_drift(cfg: PredDriftCfg, corruption_names: list[str], severity: int) -> dict:
    # Predictor: prefer Production MLflow; fallback to local best
    pyfn = _load_production_pyfunc(cfg.tracking_uri, cfg.register_name)
    if pyfn is None:
        from .models import build_backbone
        from .predict import build_loader

        # fallback torch model pipeline
        def _torch_loader():
            from .predict import build_loader as _b
            from .predict import predict_loader as _p

            dl = _b(split=cfg.split, img_size=cfg.img_size, limit=cfg.limit)
            from .models import build_backbone

            m = build_backbone("resnet18")
            ckpt = Path("artifacts/runs/best.pt")
            if ckpt.exists():
                m.load_state_dict(torch.load(ckpt, map_location="cpu"))
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logits, y = _p(m.to(device), dl, device)
            return logits

        logits_ref = _torch_loader()
        from .predict import predict_corrupted

        def _torch_corrupted(names, sev):
            from .models import build_backbone

            m = build_backbone("resnet18")
            ckpt = Path("artifacts/runs/best.pt")
            if ckpt.exists():
                m.load_state_dict(torch.load(ckpt, map_location="cpu"))
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logits, y = predict_corrupted(
                m.to(device), cfg.split, cfg.img_size, names, sev, limit=cfg.limit
            )
            return logits

        logits_cor = _torch_corrupted(corruption_names, severity)
    else:
        # Use pyfunc to get logits; assume it outputs logits or probabilities; convert to logits if needed
        dl = build_loader(split=cfg.split, img_size=cfg.img_size, limit=cfg.limit)
        X = []
        for xb, _ in dl:
            X.append(xb.numpy())
        X = np.concatenate(X, axis=0)
        out = pyfn(X)
        logits_ref = out if out.shape[1] == 10 else torch.log(torch.tensor(out) + 1e-8)
        # Corrupted
        # For corruption path, fallback to torch helper that applies corruption
        from .models import build_backbone
        from .predict import build_loader, predict_corrupted

        m = build_backbone("resnet18")
        ckpt = Path("artifacts/runs/best.pt")
        if ckpt.exists():
            m.load_state_dict(torch.load(ckpt, map_location="cpu"))
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logits_cor, _ = predict_corrupted(
            m.to(device), cfg.split, cfg.img_size, corruption_names, severity, limit=cfg.limit
        )

    conf_ref = _mean_confidence(logits_ref)
    conf_cor = _mean_confidence(logits_cor)
    drop_pct = max(0.0, 100.0 * (conf_ref - conf_cor) / max(1e-8, conf_ref))

    out = {
        "mean_conf_reference": conf_ref,
        "mean_conf_corrupted": conf_cor,
        "confidence_drop_pct": drop_pct,
        "corruptions": corruption_names,
        "severity": int(severity),
    }

    cfg.outputs_dir.mkdir(parents=True, exist_ok=True)
    write_json(cfg.outputs_dir / "prediction_drift.json", out)
    return out
