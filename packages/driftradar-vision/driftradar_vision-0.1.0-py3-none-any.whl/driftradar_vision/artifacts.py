from __future__ import annotations

import json
from pathlib import Path

import mlflow

ART = Path("artifacts")
SUMMARY_DIR = ART / "summary"
EV_DIR = ART / "reports" / "evidently"
GE_DIR = ART / "reports" / "ge"
ONNX_DIR = ART / "runs" / "onnx"


def _read_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _safe_float(v) -> float | None:
    try:
        return None if v is None else float(v)
    except Exception:
        return None


def latest_evidently_paths() -> dict[str, str]:
    # prefer real dated folders, else _latest
    dated = sorted([p for p in EV_DIR.glob("*/summary.json") if p.parent.name != "_latest"])
    summary = dated[-1] if dated else (EV_DIR / "_latest" / "summary.json")
    return {
        "summary": str(summary),
        "html": str(Path(str(summary).replace("summary.json", "report.html"))),
        "json": str(Path(str(summary).replace("summary.json", "report.json"))),
        "prediction": str(Path(str(summary).replace("summary.json", "prediction_drift.json"))),
    }


def ge_latest_summary() -> str:
    p = GE_DIR / "_latest" / "ge_summary.json"
    return str(p)


def get_registry_pair(tracking_uri: str, name: str) -> tuple[dict | None, dict | None]:
    """
    Return (production_run, staging_run) MLflow run dicts (metrics+params) or (None, None) if missing.
    """
    from mlflow.tracking import MlflowClient

    mlflow.set_tracking_uri(tracking_uri)
    c = MlflowClient()
    prod, stg = None, None

    for mv in c.search_model_versions(f"name='{name}'"):
        run = c.get_run(mv.run_id)
        rd = {
            "run_id": mv.run_id,
            "version": int(mv.version),
            "stage": mv.current_stage,
            "metrics": dict(run.data.metrics),
            "params": dict(run.data.params),
            "artifact_uri": run.info.artifact_uri,
        }
        if mv.current_stage == "Production":
            if (prod is None) or (int(mv.version) > prod["version"]):
                prod = rd
        elif mv.current_stage == "Staging" and (
            (stg is None) or (int(mv.version) > stg["version"])
        ):
            stg = rd

    return prod, stg


def _metric(run: dict | None, key: str) -> float | None:
    return _safe_float((run or {}).get("metrics", {}).get(key))


def build_metrics_delta_md(
    tracking_uri: str = "file:./mlruns",
    register_name: str = "driftradar-vision-resnet18",
    out_path: Path = SUMMARY_DIR / "metrics_delta.md",
) -> Path:
    """
    Writes a Markdown comparison table for PRs: Production vs Staging (best_val_acc1, final_val_ece, latency_ms, size_mb).
    Returns the path to the markdown file.
    """
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    prod, stg = get_registry_pair(tracking_uri, register_name)

    fields = [
        ("best_val_acc1", "Accuracy (val, top-1) â†‘"),
        ("final_val_ece", "ECE (lower is better) â†“"),
        ("inference_latency_ms", "Latency (ms/image) â†“"),
        ("artifact_size_mb", "File size (MB) â†“"),
    ]

    def row_for(label: str, run: dict | None) -> str:
        if run is None:
            return f"| **{label}** | â€“ | â€“ | â€“ | â€“ |\n"
        vals = []
        for k, _ in fields:
            v = _metric(run, k)
            vals.append("â€“" if v is None else f"{v:.4g}")
        return f"| **{label}** | {vals[0]} | {vals[1]} | {vals[2]} | {vals[3]} |\n"

    lines = []
    lines.append(f"### Model comparison â€” `{register_name}`\n\n")
    lines.append("| Stage | Acc@1 | ECE | Latency | Size |\n")
    lines.append("|---|---:|---:|---:|---:|\n")
    lines.append(row_for("Production", prod))
    lines.append(row_for("Staging", stg))

    # Deltas if both are present
    if prod and stg:
        deltas = []
        for k, _ in fields:
            pv, sv = _metric(prod, k), _metric(stg, k)
            if pv is None or sv is None:
                deltas.append("â€“")
            else:
                sign = "+" if (sv - pv) >= 0 else "âˆ’"
                deltas.append(f"{sign}{abs(sv - pv):.4g}")
        lines.append(
            f"| **Î” (Stagingâˆ’Prod)** | {deltas[0]} | {deltas[1]} | {deltas[2]} | {deltas[3]} |\n"
        )

    # Useful links / artifacts
    ev = latest_evidently_paths()
    lines.append("\n#### Artifacts\n")
    lines.append(f"- Evidently: `{ev['html']}` / `{ev['json']}`\n")
    lines.append(f"- GE summary: `{ge_latest_summary()}`\n")
    if (ONNX_DIR / "staging.onnx").exists():
        lines.append(f"- ONNX (staging): `{str(ONNX_DIR / 'staging.onnx')}`\n")
    if (SUMMARY_DIR / "latest_decision.json").exists():
        lines.append(f"- Decision: `{str(SUMMARY_DIR / 'latest_decision.json')}`\n")

    out_path.write_text("".join(lines), encoding="utf-8")
    print(out_path)
    return out_path


def build_pr_body_md(
    tracking_uri: str = "file:./mlruns",
    register_name: str = "driftradar-vision-resnet18",
    out_path: Path = SUMMARY_DIR / "pr_body.md",
) -> Path:
    """
    Compose a more verbose PR body snippet, referencing metrics_delta.md and latest artifacts.
    """
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    metrics_md = build_metrics_delta_md(tracking_uri, register_name)
    ev = latest_evidently_paths()
    ge = ge_latest_summary()

    # attempt to read decision (if present)
    dec = _read_json(SUMMARY_DIR / "latest_decision.json")
    run_id = dec.get("run_id", "")
    staging_version = dec.get("staging_version", "")

    content = []
    content.append("## ğŸ“¦ Auto Retrain â€” Candidate to Staging\n\n")
    content.append(f"- **Model:** `{register_name}`\n")
    content.append(f"- **Staging version:** `{staging_version}`  \n")
    content.append(f"- **Run ID:** `{run_id}`\n\n")
    content.append("### Drift summary\n")
    content.append(f"- `summary.json`: `{ev['summary']}`  \n")
    content.append(f"- `prediction_drift.json`: `{ev['prediction']}`\n\n")
    content.append("### Metrics delta\n")
    content.append(f"(See `{metrics_md}`)\n\n")
    content.append("### GE / Evidently\n")
    content.append(f"- GE summary: `{ge}`  \n")
    content.append(f"- Evidently HTML/JSON: `{ev['html']}`, `{ev['json']}`\n\n")
    content.append("### Checklist\n")
    content.append("- [ ] GE BLOCKERS == 0  \n")
    content.append("- [ ] Metrics meet promotion policy  \n")
    content.append("- [ ] Reviewer approves: comment **/promote**\n")

    out_path.write_text("".join(content), encoding="utf-8")
    print(out_path)
    return out_path


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Artifact helpers: metrics delta & PR body markdown.")
    ap.add_argument("--tracking-uri", type=str, default="file:./mlruns")
    ap.add_argument("--register-name", type=str, default="driftradar-vision-resnet18")
    ap.add_argument("--what", choices=["metrics-delta", "pr-body"], default="metrics-delta")
    args = ap.parse_args()

    if args.what == "metrics-delta":
        build_metrics_delta_md(args.tracking_uri, args.register_name)
    else:
        build_pr_body_md(args.tracking_uri, args.register_name)
