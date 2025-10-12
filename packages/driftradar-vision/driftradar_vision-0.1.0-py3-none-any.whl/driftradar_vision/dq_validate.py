from __future__ import annotations

import datetime as dt
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

# -----------------------------
# Utility helpers (local)
# -----------------------------
ART_ROOT = Path("artifacts")
REF_FEATURES = ART_ROOT / "reference" / "features" / "reference_features.parquet"
GE_REPORTS_ROOT = ART_ROOT / "reports" / "ge"
SUITES_DIR = Path("expectations") / "suites"


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


# -----------------------------
# Great Expectations / GX wiring
# -----------------------------
try:
    # GX ≥ 1.0 exposes get_context (with varying kwargs across releases)
    from great_expectations.data_context import get_context as _gx_get_context  # type: ignore[attr-defined]

    _USE_GX = True
except Exception:
    _USE_GX = False
    _gx_get_context = None  # type: ignore[assignment]


def _make_context(docs_dir: Path):
    """
    Create a local context that works across GE 0.17.x/0.18.x and GX ≥1.0.

    - On GX ≥1.0: try multiple get_context signatures to root the context under stores_root.
    - On GE 0.17.x/0.18.x: build a DataContext with FilesystemStoreBackendDefaults
      and write Data Docs directly into docs_dir (absolute path).
    """
    docs_dir_abs = docs_dir.resolve()
    docs_dir_abs.mkdir(parents=True, exist_ok=True)

    # Keep stores (expectations/validations/checkpoints) near reports
    stores_root = docs_dir_abs.parent.resolve()
    stores_root.mkdir(parents=True, exist_ok=True)

    if _USE_GX and _gx_get_context is not None:
        # GX signatures differ across versions; try a few in order.
        gx_attempts: list[dict[str, Any]] = [
            {"mode": "filesystem", "context_root_dir": str(stores_root)},
            {"context_root_dir": str(stores_root)},
            {"mode": "filesystem", "project_root_dir": str(stores_root)},
            {"mode": "filesystem", "project_root": str(stores_root)},
            {},  # last resort: let GX resolve defaults (gx.yml if present)
        ]
        for kw in gx_attempts:
            try:
                return _gx_get_context(**kw)  # type: ignore[misc]
            except Exception:
                continue

    # -------- Legacy GE path (0.17.x / 0.18.x) --------
    from great_expectations.data_context.types.base import (  # type: ignore
        DataContextConfig,
        FilesystemStoreBackendDefaults,
    )

    # Prefer BaseDataContext if present, else DataContext
    _DC = None
    try:
        from great_expectations.data_context import BaseDataContext as _DC  # type: ignore
    except Exception:
        try:
            from great_expectations.data_context import DataContext as _DC  # type: ignore
        except Exception as e:
            raise ImportError(
                "No compatible Great Expectations context found. "
                "Install 'great_expectations<1.0' or keep this module on GX ≥1.0."
            ) from e

    cfg = DataContextConfig(
        config_version=3.0,
        plugins_directory=None,
        datasources={},  # attach DataFrames programmatically
        anonymous_usage_statistics={"enabled": False},
        store_backend_defaults=FilesystemStoreBackendDefaults(
            root_directory=str(stores_root)  # absolute path required
        ),
        data_docs_sites={
            "local_site": {
                "class_name": "SiteBuilder",
                "store_backend": {
                    "class_name": "TupleFilesystemStoreBackend",
                    "base_directory": str(docs_dir_abs),  # absolute path required
                },
                "site_index_builder": {"class_name": "DefaultSiteIndexBuilder"},
            }
        },
    )
    return _DC(project_config=cfg)  # type: ignore[operator]


def _attach_dataframe(context, df: pd.DataFrame, name: str):
    """
    Register an in-memory pandas DataFrame and return (batch_request, validator).

    Primary path: fluent API via `context.sources`.
    Fallback path (no `sources` attr): create a runtime Pandas datasource and build
    a RuntimeBatchRequest to obtain a validator.
    """
    # -------- Path A: fluent sources API (GE ≥0.17.* and many GX builds) --------
    sources = getattr(context, "sources", None)
    if sources is not None:
        # Add or update a pandas datasource that can take DataFrames
        ds = None
        for candidate in ("add_or_update_pandas", "add_pandas"):
            add_fn = getattr(sources, candidate, None)
            if callable(add_fn):
                try:
                    ds = add_fn(name="in_memory")
                    break
                except Exception:
                    pass
        if ds is None:
            raise RuntimeError("Unable to create a pandas datasource via 'sources'.")
        asset = ds.add_dataframe_asset(name=name)
        batch_request = asset.build_batch_request(dataframe=df)
        validator = context.get_validator(batch_request=batch_request)
        return batch_request, validator

    # -------- Path B: runtime datasource (no `sources` on context) -------------
    # Try to add a PandasExecutionEngine datasource with a RuntimeDataConnector,
    # then use RuntimeBatchRequest to feed the in-memory DataFrame.
    datasource_name = "in_memory"
    data_connector_name = "runtime_data_connector"

    # 1) Try add_or_update_datasource with kwargs form
    added = False
    for method_name in ("add_or_update_datasource", "add_datasource"):
        fn = getattr(context, method_name, None)
        if not callable(fn):
            continue
        try:
            # Many versions accept kwargs instead of a dict config:
            #   name=..., class_name="Datasource", execution_engine=..., data_connectors=...
            fn(
                name=datasource_name,
                class_name="Datasource",
                execution_engine={"class_name": "PandasExecutionEngine"},
                data_connectors={
                    data_connector_name: {
                        "class_name": "RuntimeDataConnector",
                        # identifier key name can vary; we'll use a generic "id"
                        "batch_identifiers": ["id"],
                    }
                },
            )
            added = True
            break
        except TypeError:
            # 2) Try dict-style config
            try:
                cfg = {
                    "name": datasource_name,
                    "class_name": "Datasource",
                    "execution_engine": {"class_name": "PandasExecutionEngine"},
                    "data_connectors": {
                        data_connector_name: {
                            "class_name": "RuntimeDataConnector",
                            "batch_identifiers": ["id"],
                        }
                    },
                }
                fn(**cfg)  # type: ignore[misc]
                added = True
                break
            except Exception:
                continue
        except Exception:
            continue

    if not added:
        raise RuntimeError("Unable to configure a runtime Pandas datasource on this GE/GX version.")

    # Build a RuntimeBatchRequest (try modern then legacy defaults)
    runtime_params = {"batch_data": df}
    batch_identifiers_variants = [
        {"id": "ref"},  # matches our configured "batch_identifiers": ["id"]
        {"default_identifier_name": "ref"},  # older defaults
    ]

    # Try modern import path first
    RuntimeBatchRequest = None
    try:
        from great_expectations.core.batch import RuntimeBatchRequest  # type: ignore
    except Exception:
        RuntimeBatchRequest = None

    last_err: Exception | None = None
    if RuntimeBatchRequest is not None:
        for ids in batch_identifiers_variants:
            try:
                batch_request = RuntimeBatchRequest(
                    datasource_name=datasource_name,
                    data_connector_name=data_connector_name,
                    data_asset_name=name,
                    runtime_parameters=runtime_params,
                    batch_identifiers=ids,
                )
                validator = context.get_validator(batch_request=batch_request)
                return batch_request, validator
            except Exception as e:
                last_err = e

    # As a final legacy fallback, try BatchRequest with runtime_parameters
    try:
        from great_expectations.core.batch import BatchRequest  # type: ignore
        for ids in batch_identifiers_variants:
            try:
                batch_request = BatchRequest(
                    datasource_name=datasource_name,
                    data_connector_name=data_connector_name,
                    data_asset_name=name,
                    runtime_parameters=runtime_params,
                    batch_identifiers=ids,
                )
                validator = context.get_validator(batch_request=batch_request)
                return batch_request, validator
            except Exception as e:
                last_err = e
    except Exception as e:
        last_err = e

    raise RuntimeError(
        f"Failed to create a validator via runtime batch request on this GE/GX version: {last_err}"
    )


def _load_reference_df() -> pd.DataFrame:
    if not REF_FEATURES.exists():
        raise FileNotFoundError(
            f"Missing reference features at {REF_FEATURES}. Run features.py first."
        )
    return pd.read_parquet(REF_FEATURES)


def _load_suites() -> list[tuple[str, dict[str, Any]]]:
    """
    Load all expectation suites from expectations/suites/*.json.
    Returns list of (suite_name, suite_dict).
    """
    if not SUITES_DIR.exists():
        return []

    suites: list[tuple[str, dict[str, Any]]] = []
    for p in sorted(SUITES_DIR.glob("*.json")):
        try:
            s = read_json(p)
            suite_dict = s.get("expectation_suite", s)
            name = suite_dict.get("expectation_suite_name") or suite_dict.get("name") or p.stem
            suites.append((str(name), suite_dict))
        except Exception:
            continue
    return suites


# -----------------------------
# Summary & HTML rendering
# -----------------------------
BLOCKER_TAGS = {"BLOCKER", "blocker", "FAIL", "fail"}  # heuristic tags
WARN_TAGS = {"WARN", "warn", "WARNING", "warning"}  # heuristic tags


def _classify_severity(exp: dict[str, Any]) -> str:
    """Heuristic severity from expectation meta/kwargs."""
    meta = exp.get("meta") or {}
    kw = exp.get("kwargs") or {}
    for src in (meta.get("severity"), kw.get("severity")):
        if isinstance(src, str):
            up = src.upper()
            if up in BLOCKER_TAGS:
                return "BLOCKER"
            if up in WARN_TAGS:
                return "WARN"
    return "WARN"


def _summarize_results(suite_name: str, ge_result: dict[str, Any]) -> dict[str, Any]:
    """
    Convert GE/GX validation_result (dict-like) into a compact summary.
    """
    results = ge_result.get("results", [])
    rows = []
    fail_count = 0
    blockers = 0
    warns = 0
    for r in results:
        exp = r.get("expectation_config", {}) or {}
        etype = exp.get("expectation_type", "unknown")
        success = bool(r.get("success", False))
        severity = _classify_severity(exp) if not success else "OK"
        if not success:
            fail_count += 1
            blockers += int(severity == "BLOCKER")
            warns += int(severity == "WARN")
        kwargs = {
            k: v for k, v in (exp.get("kwargs") or {}).items() if not isinstance(v, (list, dict))
        }
        rows.append(
            {
                "suite": suite_name,
                "type": etype,
                "success": success,
                "severity": severity if not success else "",
                "kwargs": kwargs,
            }
        )
    return {
        "rows": rows,
        "fail_count": fail_count,
        "blockers": blockers,
        "warns": warns,
        "success": bool(ge_result.get("success", False)),
    }


def _render_light_html(summary: dict[str, Any]) -> str:
    """
    Self-contained HTML summary independent of GE/GX Data Docs.
    """
    head = """
<!doctype html><html><head>
<meta charset="utf-8">
<title>GE Summary</title>
<style>
body{font:14px/1.4 -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial;}
table{border-collapse:collapse;width:100%;}
th,td{border:1px solid #e5e7eb;padding:6px 8px;}
th{background:#f3f4f6;text-align:left;}
.badge{display:inline-block;padding:2px 8px;border-radius:12px;font-size:12px}
.ok{background:#ecfdf5;color:#065f46}
.warn{background:#fff7ed;color:#9a3412}
.block{background:#fef2f2;color:#991b1b}
</style></head><body>
<h2>Great Expectations — Validation Summary</h2>
"""
    meta = f"""
<p><b>Date:</b> {summary["date"]} &nbsp; | &nbsp;
<b>Suites:</b> {len(summary["suites"])} &nbsp; | &nbsp;
<b>Blockers:</b> {summary["blockers"]} &nbsp; | &nbsp;
<b>Warnings:</b> {summary["warns"]}</p>
"""
    rows_html = ""
    for r in summary["results"]:
        sev = r["severity"]
        badge = (
            "<span class='badge ok'>OK</span>"
            if r["success"]
            else ("<span class='badge block'>BLOCKER</span>" if sev == "BLOCKER" else "<span class='badge warn'>WARN</span>")
        )
        kwargs_str = ", ".join(f"{k}={v}" for k, v in (r["kwargs"] or {}).items())
        rows_html += f"<tr><td>{r['suite']}</td><td>{r['type']}</td><td>{badge}</td><td>{kwargs_str}</td></tr>\n"

    table = f"""
<table>
  <thead><tr><th>Suite</th><th>Expectation</th><th>Status</th><th>Args</th></tr></thead>
  <tbody>
  {rows_html}
  </tbody>
</table>
"""
    tail = "</body></html>"
    return head + meta + table + tail


# -----------------------------
# Main runner
# -----------------------------
@dataclass
class DQCfg:
    # Placeholder for future toggles if you want to read from configs/dq.yaml
    pass


def _import_expectation_suite():
    """Import ExpectationSuite across GE/GX versions."""
    try:
        from great_expectations.core.expectation_suite import ExpectationSuite  # GE 0.17/0.18
        return ExpectationSuite
    except Exception:
        for mod_path in (
            "great_expectations.core.expectation_suite",
            "great_expectations.core",
            "great_expectations.expectations",
        ):
            try:
                mod = __import__(mod_path, fromlist=["ExpectationSuite"])
                return getattr(mod, "ExpectationSuite")
            except Exception:
                continue
        raise ImportError(
            "Could not import ExpectationSuite from Great Expectations/GX. "
            "Please ensure a compatible version is installed."
        )


def run_dq(config_path: Path, config_name: str) -> int:
    """
    Run GE/GX validations on the reference features table.
    - Loads all suites under expectations/suites/*.json
    - Writes compact JSON summary + small HTML overview
    """
    df = _load_reference_df()

    today = dt.date.today().isoformat()
    out_dir = GE_REPORTS_ROOT / today
    latest_dir = GE_REPORTS_ROOT / "_latest"
    out_dir.mkdir(parents=True, exist_ok=True)
    latest_dir.mkdir(parents=True, exist_ok=True)

    context = _make_context(out_dir)

    _, validator = _attach_dataframe(context, df, name="reference_features")

    suites = _load_suites()
    if not suites:
        suites = [
            (
                "auto_minimal",
                {
                    "expectation_suite_name": "auto_minimal",
                    "expectations": [
                        {"expectation_type": "expect_table_row_count_to_be_between", "kwargs": {"min_value": 1000}},
                        {"expectation_type": "expect_table_columns_to_not_contain_null", "kwargs": {"column_set": list(df.columns)}},
                    ],
                    "meta": {"generated_by": "dq_validate.py"},
                },
            )
        ]

    ExpectationSuite = _import_expectation_suite()

    all_rows: list[dict[str, Any]] = []
    total_blockers = 0
    total_warns = 0
    suite_names: list[str] = []
    for sname, sdict in suites:
        suite_names.append(sname)
        try:
            suite_obj = ExpectationSuite(
                expectation_suite_name=sdict.get("expectation_suite_name", sname),
                expectations=sdict.get("expectations", []),
                meta=sdict.get("meta", {}),
            )
            ge_result = validator.validate(expectation_suite=suite_obj, result_format="SUMMARY")
            summary = _summarize_results(sname, ge_result)
            all_rows.extend(summary["rows"])
            total_blockers += summary["blockers"]
            total_warns += summary["warns"]
        except Exception as e:
            all_rows.append(
                {
                    "suite": sname,
                    "type": "suite_execution",
                    "success": False,
                    "severity": "WARN",
                    "kwargs": {"error": str(e)[:200]},
                }
            )
            total_warns += 1

    ge_summary = {
        "date": today,
        "suites": suite_names,
        "results": all_rows,
        "blockers": int(total_blockers),
        "warns": int(total_warns),
        "docs_root": str(out_dir.resolve()),
    }

    write_json(out_dir / "ge_summary.json", ge_summary)
    write_json(latest_dir / "ge_summary.json", ge_summary)

    html = _render_light_html(ge_summary)
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    (latest_dir / "index.html").write_text(html, encoding="utf-8")

    print(f"[GE] date={today} suites={len(suite_names)} blockers={total_blockers} warns={total_warns} out={out_dir}")
    return 0


# -----------------------------
# CLI
# -----------------------------
if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--config-path", type=str, default="configs")
    ap.add_argument("--config-name", type=str, default="dq.yaml")
    args = ap.parse_args()
    sys.exit(run_dq(Path(args.config_path), args.config_name))
