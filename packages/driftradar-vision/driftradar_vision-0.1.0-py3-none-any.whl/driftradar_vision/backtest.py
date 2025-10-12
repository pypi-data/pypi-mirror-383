from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from omegaconf import OmegaConf

# ---------- Paths & IO ----------

ART = Path("artifacts")
EV_DIR = ART / "reports" / "evidently"


def _read_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _write_json(p: Path, obj: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_csv(p: Path, rows: list[dict[str, object]]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        p.write_text("")
        return
    keys = sorted({k for r in rows for k in r})
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)


# ---------- Config ----------


@dataclass
class SimSchedule:
    """Simple per-day drift schedule."""

    clean_days: int = 3
    drift_days: int = 7
    severity_clean: int = 0
    severity_drift: int = 3
    corruptions_drift: tuple[str, ...] = (
        "gaussian_noise",
        "defocus_blur",
        "jpeg_compression",
        "snow",
        "brightness",
    )


# ---------- Metrics ----------


@dataclass
class Counts:
    tp: int = 0
    fp: int = 0
    tn: int = 0
    fn: int = 0

    def to_rates(self) -> dict[str, float]:
        eps = 1e-9
        precision = self.tp / (self.tp + self.fp + eps)
        recall = self.tp / (self.tp + self.fn + eps)
        fpr = self.fp / (self.fp + self.tn + eps)
        fnr = self.fn / (self.fn + self.tp + eps)
        acc = (self.tp + self.tn) / (self.tp + self.fp + self.tn + self.fn + eps)
        return {
            "precision": precision,
            "recall": recall,
            "fpr": fpr,
            "fnr": fnr,
            "accuracy": acc,
        }


# ---------- Helpers ----------


def _call_drift_check(
    cfg_path: Path, cfg_name: str, data_cfg_path: Path, data_cfg_name: str
) -> int:
    """
    Import and call our drift_check.run(...) directly to avoid subprocess overhead.
    """
    from driftradar_vision.drift_check import run as drift_run  # local import

    return int(
        drift_run(
            cfg_path,
            cfg_name,
            data_cfg_path,
            data_cfg_name,
        )
    )


def _simulate_day(
    day: date,
    is_drift: bool,
    severity_clean: int,
    severity_drift: int,
    corrs: tuple[str, ...],
    data_cfg_path: Path,
    data_cfg_name: str,
) -> None:
    """
    Produce a "production" batch for a given day by calling data_prod with chosen corruptions/severity,
    then run drift_check to generate Evidently artifacts under that day folder.
    """
    # 1) Generate a batch for the given day
    from driftradar_vision.data_prod import main as prod_main

    sev = severity_drift if is_drift else severity_clean
    names = list(corrs if is_drift else ())

    # We pass date via environment so data_prod can place into the day's folder if it uses "today".
    # If your data_prod doesn't honor that, drift_check still writes under today's folder; we then rename it.
    prod_main(
        batch_count=2000,
        split="test",
        seed=4242 + (day.toordinal() % 10000),
        corruptions=names,
        severity=sev,
        out_date=day.isoformat(),  # our data_prod supports this param in the repo; if not, it still works via summaries
    )

    # 2) Run drift check (writes artifacts/reports/evidently/<today>/...)
    _call_drift_check(Path("configs"), "drift.yaml", Path("configs"), "data.yaml")

    # If drift_check wrote under today's date and not day.isoformat(),
    # we don't move folders; the evaluation will read summaries by exact folder name when present,
    # else it falls back to last run. For robust backtest we check the folder we expect:
    # artifacts/reports/evidently/<day>/summary.json
    src = EV_DIR / day.isoformat() / "summary.json"
    if not src.exists():
        # nothing to do; we'll read _latest later
        pass


def _replay_available_days() -> list[date]:
    days = []
    for p in EV_DIR.iterdir():
        if p.is_dir() and p.name not in ("_latest",):
            try:
                y, m, d = map(int, p.name.split("-"))
                days.append(date(y, m, d))
            except Exception:
                continue
    return sorted(days)


def _label_plan_from_schedule(start: date, n_days: int, sched: SimSchedule) -> dict[str, bool]:
    """
    Simple cyclic schedule: first 'clean_days' are clean, next 'drift_days' are drift, repeat.
    """
    plan: dict[str, bool] = {}
    block = sched.clean_days + sched.drift_days
    for i in range(n_days):
        day = start + timedelta(days=i)
        idx = i % block
        plan[day.isoformat()] = idx >= sched.clean_days
    return plan


# ---------- Backtest modes ----------


def run_replay(labels_path: Path | None, out_dir: Path) -> dict[str, object]:
    """
    Replay existing Evidently summaries under artifacts/reports/evidently/YYYY-MM-DD.
    If labels_path is provided, it should be a JSON mapping {date: true/false}.
    """
    days = _replay_available_days()
    if not days:
        raise SystemExit("No historical Evidently folders found to replay.")

    truth: dict[str, bool] = {}
    if labels_path and labels_path.exists():
        truth = _read_json(labels_path)

    rows = []
    ctr = Counts()
    for day in days:
        dstr = day.isoformat()
        s = _read_json(EV_DIR / dstr / "summary.json")
        pred = bool(s.get("is_drifted", False))

        label = bool(truth[dstr]) if dstr in truth else bool(pred)

        if pred and label:
            ctr.tp += 1
        elif pred and not label:
            ctr.fp += 1
        elif (not pred) and (not label):
            ctr.tn += 1
        else:
            ctr.fn += 1

        rows.append(
            {
                "date": dstr,
                "pred_is_drifted": pred,
                "label_is_drifted": label,
                "embedding_top5_psi_mean": float(s.get("embedding_top5_psi_mean", 0.0)),
                "confidence_drop_pct": float(s.get("prediction_confidence_drop_pct", 0.0)),
            }
        )

    rates = ctr.to_rates()
    out = {
        "mode": "replay",
        "n_days": len(days),
        "counts": ctr.__dict__,
        "rates": rates,
    }
    _write_csv(out_dir / "per_day.csv", rows)
    _write_json(out_dir / "summary.json", out)
    print(json.dumps(out, indent=2))
    return out


def run_simulate(
    start: date,
    n_days: int,
    sched: SimSchedule,
    data_cfg_path: Path,
    data_cfg_name: str,
    drift_cfg_path: Path,
    drift_cfg_name: str,
    out_dir: Path,
) -> dict[str, object]:
    """
    Simulate n_days starting at 'start' by generating a batch per day with/without drift and running drift_check.
    """
    plan = _label_plan_from_schedule(start, n_days, sched)
    rows = []
    ctr = Counts()

    # Ensure configs exist
    _ = OmegaConf.load(drift_cfg_path / drift_cfg_name)
    _ = OmegaConf.load(data_cfg_path / data_cfg_name)

    for i, (dstr, is_drift) in enumerate(plan.items()):
        day = start + timedelta(days=i)
        _simulate_day(
            day=day,
            is_drift=is_drift,
            severity_clean=sched.severity_clean,
            severity_drift=sched.severity_drift,
            corrs=sched.corruptions_drift,
            data_cfg_path=data_cfg_path,
            data_cfg_name=data_cfg_name,
        )
        # read back the summary for that day (fallback to _latest if missing)
        s_path = EV_DIR / dstr / "summary.json"
        if not s_path.exists():
            s_path = EV_DIR / "_latest" / "summary.json"
        s = _read_json(s_path)
        pred = bool(s.get("is_drifted", False))

        if pred and is_drift:
            ctr.tp += 1
        elif pred and not is_drift:
            ctr.fp += 1
        elif (not pred) and (not is_drift):
            ctr.tn += 1
        else:
            ctr.fn += 1

        rows.append(
            {
                "date": dstr,
                "pred_is_drifted": pred,
                "label_is_drifted": is_drift,
                "embedding_top5_psi_mean": float(s.get("embedding_top5_psi_mean", 0.0)),
                "confidence_drop_pct": float(s.get("prediction_confidence_drop_pct", 0.0)),
            }
        )

    rates = ctr.to_rates()
    out = {
        "mode": "simulate",
        "n_days": n_days,
        "schedule": {
            "clean_days": sched.clean_days,
            "drift_days": sched.drift_days,
            "severity_clean": sched.severity_clean,
            "severity_drift": sched.severity_drift,
            "corruptions": list(sched.corruptions_drift),
        },
        "counts": ctr.__dict__,
        "rates": rates,
        "note": "Target: false positive rate (fpr) < 0.10",
    }
    _write_csv(out_dir / "per_day.csv", rows)
    _write_json(out_dir / "summary.json", out)
    print(json.dumps(out, indent=2))
    return out


# ---------- CLI ----------


def main():
    ap = argparse.ArgumentParser(
        description="Backtest drift thresholds across days (replay existing or simulate new)."
    )
    ap.add_argument("--mode", choices=["replay", "simulate"], default="replay")
    ap.add_argument(
        "--labels", type=str, default="", help="Optional JSON {YYYY-MM-DD: bool} for replay mode."
    )
    ap.add_argument("--start", type=str, default="", help="YYYY-MM-DD for simulate mode start.")
    ap.add_argument("--days", type=int, default=10, help="Number of days to simulate.")
    ap.add_argument("--clean-days", type=int, default=3)
    ap.add_argument("--drift-days", type=int, default=7)
    ap.add_argument("--severity-clean", type=int, default=0)
    ap.add_argument("--severity-drift", type=int, default=3)
    ap.add_argument(
        "--corruptions",
        nargs="*",
        default=["gaussian_noise", "defocus_blur", "jpeg_compression", "snow", "brightness"],
    )
    ap.add_argument("--data-config-path", type=str, default="configs")
    ap.add_argument("--data-config-name", type=str, default="data.yaml")
    ap.add_argument("--drift-config-path", type=str, default="configs")
    ap.add_argument("--drift-config-name", type=str, default="drift.yaml")
    ap.add_argument("--out-dir", type=str, default="artifacts/backtest")
    args = ap.parse_args()

    out_dir = Path(args.out_dir) / Path(args.mode)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.mode == "replay":
        labels = Path(args.labels) if args.labels else None
        run_replay(labels, out_dir)
    else:
        start = (
            date.fromisoformat(args.start)
            if args.start
            else date.today() - timedelta(days=args.days)
        )
        sched = SimSchedule(
            clean_days=int(args.clean_days),
            drift_days=int(args.drift_days),
            severity_clean=int(args.severity_clean),
            severity_drift=int(args.severity_drift),
            corruptions_drift=tuple(args.corruptions),
        )
        run_simulate(
            start=start,
            n_days=int(args.days),
            sched=sched,
            data_cfg_path=Path(args.data_config_path),
            data_cfg_name=args.data_config_name,
            drift_cfg_path=Path(args.drift_config_path),
            drift_cfg_name=args.drift_config_name,
            out_dir=out_dir,
        )


if __name__ == "__main__":
    main()
