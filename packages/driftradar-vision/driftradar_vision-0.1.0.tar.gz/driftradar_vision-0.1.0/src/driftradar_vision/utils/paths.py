from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / "artifacts"
DATA_ROOT = ARTIFACTS / "data"
GE_REPORTS = ARTIFACTS / "reports" / "ge"
REF_FEATURES = ARTIFACTS / "reference" / "features"

for p in (ARTIFACTS, DATA_ROOT, GE_REPORTS, REF_FEATURES):
    p.mkdir(parents=True, exist_ok=True)
