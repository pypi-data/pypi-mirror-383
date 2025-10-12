from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import mlflow
import mlflow.pytorch
import onnx
import onnxruntime as ort
import torch
from omegaconf import OmegaConf
from torch import nn
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms

from .metrics import confusion, ece, perclass_f1, top1
from .models import build_backbone
from .utils.paths import DATA_ROOT
from .utils.seeds import set_seed
from .viz import plot_calibration, plot_confusion


@dataclass
class TrainCfg:
    arch: str
    img_size: int
    optimizer: str
    lr: float
    weight_decay: float
    epochs: int
    batch_size: int
    num_workers: int
    label_smoothing: float
    amp: bool
    save_best: bool
    export_onnx: bool
    onnx_path: str
    seed: int
    mlflow_experiment: str
    tracking_uri: str
    register_name: str


def _build_loaders(cfg: TrainCfg) -> tuple[DataLoader, DataLoader]:
    tfm_train = transforms.Compose(
        [
            transforms.Resize(cfg.img_size),
            transforms.RandomCrop(cfg.img_size, padding=4),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
        ]
    )
    tfm_eval = transforms.Compose(
        [
            transforms.Resize(cfg.img_size),
            transforms.CenterCrop(cfg.img_size),
            transforms.ToTensor(),
        ]
    )

    ds = datasets.CIFAR10(root=str(DATA_ROOT), train=True, transform=tfm_train, download=True)
    n_val = int(0.1 * len(ds))
    n_train = len(ds) - n_val
    ds_train, ds_val = random_split(
        ds, [n_train, n_val], generator=torch.Generator().manual_seed(cfg.seed)
    )

    # For val, use eval transforms
    ds_val.dataset.transform = tfm_eval

    dl_train = DataLoader(
        ds_train,
        batch_size=cfg.batch_size,
        shuffle=True,
        num_workers=cfg.num_workers,
        pin_memory=True,
    )
    dl_val = DataLoader(
        ds_val,
        batch_size=cfg.batch_size,
        shuffle=False,
        num_workers=cfg.num_workers,
        pin_memory=True,
    )
    return dl_train, dl_val


def _criterion(cfg: TrainCfg) -> nn.Module:
    return nn.CrossEntropyLoss(label_smoothing=cfg.label_smoothing)


def _optim(cfg: TrainCfg, params):
    if cfg.optimizer == "adamw":
        return torch.optim.AdamW(params, lr=cfg.lr, weight_decay=cfg.weight_decay)
    if cfg.optimizer == "sgd":
        return torch.optim.SGD(params, lr=cfg.lr, momentum=0.9, weight_decay=cfg.weight_decay)
    raise ValueError("Unknown optimizer")


def _eval_epoch(model: nn.Module, dl: DataLoader, device: torch.device) -> dict:
    model.eval()
    logits_all, target_all = [], []
    with torch.no_grad():
        for x, y in dl:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            logits_all.append(logits)
            target_all.append(y)
    logits = torch.cat(logits_all, 0)
    target = torch.cat(target_all, 0)
    return {
        "acc1": top1(logits, target),
        "ece": ece(logits, target),
        "perclass_f1": perclass_f1(logits, target),
        "confusion": confusion(logits, target),
        "logits": logits.cpu(),
        "target": target.cpu(),
    }


def _export_onnx(model: nn.Module, img_size: int, onnx_path: Path, device: torch.device) -> dict:
    model.eval()
    dummy = torch.randn(1, 3, img_size, img_size, device=device)
    onnx_path.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(
        model,
        dummy,
        str(onnx_path),
        input_names=["input"],
        output_names=["logits"],
        opset_version=17,
        do_constant_folding=True,
        dynamic_axes={"input": {0: "N"}, "logits": {0: "N"}},
    )
    onnx_model = onnx.load(str(onnx_path))
    onnx.checker.check_model(onnx_model)
    # ORT check
    sess = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    out = sess.run(None, {"input": dummy.cpu().numpy()})
    return {"onnx_ok": True, "ort_out_shape": tuple(out[0].shape)}


def main(config_path: str = "configs", model_name: str = "model.yaml") -> str:
    cfg = OmegaConf.load(Path(config_path) / model_name)
    tcfg = TrainCfg(
        arch=str(cfg.arch),
        img_size=int(cfg.img_size),
        optimizer=str(cfg.optimizer),
        lr=float(cfg.lr),
        weight_decay=float(cfg.weight_decay),
        epochs=int(cfg.epochs),
        batch_size=int(cfg.batch_size),
        num_workers=int(cfg.num_workers),
        label_smoothing=float(cfg.label_smoothing),
        amp=bool(cfg.amp),
        save_best=bool(cfg.save_best),
        export_onnx=bool(cfg.export_onnx),
        onnx_path=str(cfg.onnx_path),
        seed=int(cfg.seed),
        mlflow_experiment=str(cfg.mlflow.experiment),
        tracking_uri=str(cfg.mlflow.tracking_uri),
        register_name=str(cfg.mlflow.register_name),
    )

    set_seed(tcfg.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    dl_train, dl_val = _build_loaders(tcfg)
    model = build_backbone(tcfg.arch).to(device)
    crit = _criterion(tcfg)
    opt = _optim(tcfg, model.parameters())

    mlflow.set_tracking_uri(tcfg.tracking_uri)
    mlflow.set_experiment(tcfg.mlflow_experiment)

    scaler = torch.cuda.amp.GradScaler(enabled=tcfg.amp and torch.cuda.is_available())

    best_acc = -1.0
    run_id = ""

    with mlflow.start_run() as run:
        run_id = run.info.run_id
        mlflow.log_params(
            {
                "arch": tcfg.arch,
                "img_size": tcfg.img_size,
                "optimizer": tcfg.optimizer,
                "lr": tcfg.lr,
                "weight_decay": tcfg.weight_decay,
                "epochs": tcfg.epochs,
                "batch_size": tcfg.batch_size,
                "label_smoothing": tcfg.label_smoothing,
                "amp": tcfg.amp,
            }
        )

        for epoch in range(1, tcfg.epochs + 1):
            model.train()
            loss_sum = 0.0
            for x, y in dl_train:
                x, y = x.to(device), y.to(device)
                opt.zero_grad(set_to_none=True)
                if scaler.is_enabled():
                    with torch.cuda.amp.autocast():
                        out = model(x)
                        loss = crit(out, y)
                    scaler.scale(loss).backward()
                    scaler.step(opt)
                    scaler.update()
                else:
                    out = model(x)
                    loss = crit(out, y)
                    loss.backward()
                    opt.step()
                loss_sum += float(loss.item()) * x.size(0)

            val = _eval_epoch(model, dl_val, device)
            mlflow.log_metrics(
                {
                    "train_loss_epoch": loss_sum / len(dl_train.dataset),
                    "val_acc1": val["acc1"],
                    "val_ece": val["ece"],
                },
                step=epoch,
            )

            if tcfg.save_best and val["acc1"] > best_acc:
                best_acc = val["acc1"]
                torch.save(model.state_dict(), "artifacts/runs/best.pt")

        # Final eval artifacts
        cm = val["confusion"]
        per_f1 = val["perclass_f1"]
        plot_confusion(cm, out_png=Path("artifacts/runs/confusion.png"))
        plot_calibration(
            val["logits"], val["target"], out_png=Path("artifacts/runs/calibration.png")
        )
        mlflow.log_artifact("artifacts/runs/confusion.png")
        mlflow.log_artifact("artifacts/runs/calibration.png")

        if tcfg.export_onnx:
            onnx_info = _export_onnx(model, tcfg.img_size, Path(tcfg.onnx_path), device)
            mlflow.log_artifact(tcfg.onnx_path)
            mlflow.log_dict(onnx_info, "onnx_info.json")

        mlflow.pytorch.log_model(model, artifact_path="model")
        mlflow.log_metrics(
            {"best_val_acc1": best_acc, "final_val_acc1": val["acc1"], "final_val_ece": val["ece"]}
        )
        mlflow.log_dict(per_f1, "perclass_f1.json")

        # Register new version in MLflow Model Registry (local file store works too)
        mv = mlflow.register_model(f"runs:/{run_id}/model", tcfg.register_name)
        print(f"Registered model version: name={tcfg.register_name} version={mv.version}")
    return run_id


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--config-path", type=str, default="configs")
    ap.add_argument("--config-name", type=str, default="model.yaml")
    args = ap.parse_args()
    rid = main(args.config_path, args.config_name)
    print(f"MLflow run: {rid}")
