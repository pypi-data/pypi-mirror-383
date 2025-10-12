from __future__ import annotations

from pathlib import Path

import mlflow
import pandas as pd
import torch
from omegaconf import OmegaConf

from .metrics import ece, perclass_f1, top1
from .models import build_backbone
from .predict import build_loader, predict_corrupted, predict_loader
from .viz import plot_confusion


def run_eval(
    config_path: str = "configs",
    eval_name: str = "eval.yaml",
    model_cfg_path: str = "configs",
    model_name: str = "model.yaml",
) -> str:
    ecfg = OmegaConf.load(Path(config_path) / eval_name)
    mcfg = OmegaConf.load(Path(model_cfg_path) / model_name)

    out_dir = Path(ecfg.outputs.dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_backbone(str(mcfg.arch))
    # Load best checkpoint if available
    ckpt = Path("artifacts/runs/best.pt")
    if ckpt.exists():
        state = torch.load(ckpt, map_location="cpu")
        model.load_state_dict(state)
    model = model.to(device)

    # Reference evaluation
    dl = build_loader(
        split=str(ecfg.reference.split), img_size=int(mcfg.img_size), limit=ecfg.reference.limit
    )
    logits, y = predict_loader(model, dl, device)

    metrics = {
        "ref_acc1": top1(logits, y),
        "ref_ece": ece(logits, y),
        **{f"ref_f1_{k}": v for k, v in perclass_f1(logits, y).items()},
    }
    cm_path = out_dir / "ref_confusion.png"
    plot_confusion(
        (logits.argmax(1).cpu().numpy() == y.numpy()).astype(int).reshape(2, -1)[:2, :2], cm_path
    )  # quick placeholder for CI-safe image

    # Corruption robustness sweep
    rows: list[dict] = []
    for name in ecfg.corruptions.names:
        for sev in ecfg.corruptions.severities:
            clogits, cy = predict_corrupted(
                model,
                split=str(ecfg.reference.split),
                img_size=int(mcfg.img_size),
                corruption_names=[name],
                severity=int(sev),
                limit=ecfg.reference.limit,
            )
            rows.append(
                {
                    "corruption": name,
                    "severity": int(sev),
                    "acc1": top1(clogits, cy),
                    "ece": ece(clogits, cy),
                }
            )
    rob = pd.DataFrame(rows)

    # Persist
    rob.to_csv(out_dir / "robustness.csv", index=False)
    pd.Series(metrics).to_csv(out_dir / "reference_metrics.csv")

    # MLflow log (optional)
    mlflow.set_tracking_uri(str(mcfg.mlflow.tracking_uri))
    mlflow.set_experiment(str(mcfg.mlflow.experiment))
    with mlflow.start_run(run_name="eval"):
        mlflow.log_artifact(str(out_dir / "robustness.csv"))
        mlflow.log_artifact(str(out_dir / "reference_metrics.csv"))
        mlflow.log_metric("ref_acc1", float(metrics["ref_acc1"]))
        mlflow.log_metric("ref_ece", float(metrics["ref_ece"]))

    return str(out_dir)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--config-path", type=str, default="configs")
    ap.add_argument("--config-name", type=str, default="eval.yaml")
    ap.add_argument("--model-config-path", type=str, default="configs")
    ap.add_argument("--model-config-name", type=str, default="model.yaml")
    args = ap.parse_args()
    out = run_eval(
        args.config_path, args.config_name, args.model_config_path, args.model_config_name
    )
    print(f"Eval outputs at: {out}")
