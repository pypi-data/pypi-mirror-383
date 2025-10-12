from __future__ import annotations

from dataclasses import dataclass

import mlflow
from mlflow.tracking import MlflowClient


@dataclass
class RegistryCfg:
    tracking_uri: str
    register_name: str


def promote_latest_staging_to_production(cfg: RegistryCfg) -> str:
    mlflow.set_tracking_uri(cfg.tracking_uri)
    client = MlflowClient()
    versions = client.search_model_versions(f"name='{cfg.register_name}'")
    if not versions:
        raise RuntimeError("No versions found")
    # pick the highest version in STAGING
    stg = [v for v in versions if v.current_stage.upper() == "STAGING"]
    if not stg:
        raise RuntimeError("No STAGING versions")
    v = sorted(stg, key=lambda x: int(x.version))[-1]
    client.transition_model_version_stage(
        cfg.register_name, v.version, stage="Production", archive_existing_versions=True
    )
    return v.version


def smoke_load_production(cfg: RegistryCfg) -> None:
    mlflow.set_tracking_uri(cfg.tracking_uri)
    uri = f"models:/{cfg.register_name}/Production"
    m = mlflow.pyfunc.load_model(uri)
    _ = m  # would run a mock inference here in a full smoke


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--tracking-uri", type=str, default="file:./mlruns")
    ap.add_argument("--name", type=str, default="driftradar-vision/resnet18")
    args = ap.parse_args()
    print(promote_latest_staging_to_production(RegistryCfg(args.tracking_uri, args.name)))
