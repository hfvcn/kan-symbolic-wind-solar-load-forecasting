#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.structured_combo import (
    FORMULA_COMBINED_METRICS,
    FORMULA_COMBINED_SYMPY,
    FORMULA_COMBINED_TEX,
    FORMULA_EVAL_TEST,
    FORMULA_PREDICTIONS,
    combine_formula_components,
    combine_prediction_components,
    load_component_run,
    load_formula_run,
    require_complete_formula_runs,
    write_json,
)


def _utc_run_id(prefix: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    return f"{prefix}_{ts}_{uuid.uuid4().hex[:8]}"


def _parse_formula_run_args(args: argparse.Namespace) -> dict[str, Path] | None:
    return require_complete_formula_runs(
        {
            "load": args.load_formula_run,
            "wind": args.wind_formula_run,
            "solar": args.solar_formula_run,
        }
    )


def _build_output_payload(
    *,
    out_run_id: str,
    horizon: int,
    started_at: datetime,
    component_runs: dict[str, Path],
    component_targets: dict[str, str | None],
) -> dict[str, Any]:
    return {
        "run_id": out_run_id,
        "phase": "05-structured-combination",
        "kind": "net_load_from_components",
        "target_col": f"net_load_h{horizon}" if horizon != 1 else "net_load",
        "component_runs": {key: path.name for key, path in component_runs.items()},
        "component_targets": component_targets,
        "started_at": started_at.isoformat(),
    }


def _write_formula_artifacts(
    *,
    artifacts_dir: Path,
    formula_bundle: dict[str, Any],
) -> None:
    (artifacts_dir / FORMULA_COMBINED_SYMPY).write_text(str(formula_bundle["expr"]))
    (artifacts_dir / FORMULA_COMBINED_TEX).write_text(str(formula_bundle["tex"]))
    formula_bundle["pred_df"].to_parquet(artifacts_dir / FORMULA_PREDICTIONS, compression="snappy")
    write_json(artifacts_dir / FORMULA_EVAL_TEST, formula_bundle["metrics"])
    write_json(artifacts_dir / FORMULA_COMBINED_METRICS, formula_bundle["complexity"])


def main() -> None:
    ap = argparse.ArgumentParser(description="Combine load/wind/solar prediction runs into a net_load prediction run.")
    ap.add_argument("--load-run", required=True, help="Path to synced load(run) directory.")
    ap.add_argument("--wind-run", required=True, help="Path to synced wind(run) directory.")
    ap.add_argument("--solar-run", required=True, help="Path to synced solar(run) directory.")
    ap.add_argument("--load-formula-run", default="", help="Optional symbolic run for load local formula.")
    ap.add_argument("--wind-formula-run", default="", help="Optional symbolic run for wind local formula.")
    ap.add_argument("--solar-formula-run", default="", help="Optional symbolic run for solar local formula.")
    ap.add_argument("--out-run-id", default="", help="Output run_id under runs/ (default: auto).")
    ap.add_argument("--out-runs-dir", default="runs", help="Local runs/ directory.")
    args = ap.parse_args()

    started_at = datetime.now(timezone.utc)
    predictor_components = {
        "load": load_component_run(Path(args.load_run), label="load"),
        "wind": load_component_run(Path(args.wind_run), label="wind"),
        "solar": load_component_run(Path(args.solar_run), label="solar"),
    }
    predictor_df, predictor_metrics, horizon = combine_prediction_components(
        load=predictor_components["load"],
        wind=predictor_components["wind"],
        solar=predictor_components["solar"],
    )
    formula_run_paths = _parse_formula_run_args(args)

    out_run_id = args.out_run_id.strip() or _utc_run_id(prefix="combo_net_load")
    out_run_dir = Path(args.out_runs_dir) / out_run_id
    artifacts_dir = out_run_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    predictor_df.to_parquet(artifacts_dir / "predictions_test.parquet", compression="snappy")
    write_json(artifacts_dir / "eval_test.json", predictor_metrics)

    out_payload = _build_output_payload(
        out_run_id=out_run_id,
        horizon=horizon,
        started_at=started_at,
        component_runs={key: comp.run_dir for key, comp in predictor_components.items()},
        component_targets={key: comp.target_col for key, comp in predictor_components.items()},
    )
    out_payload["eval_test"] = predictor_metrics
    if formula_run_paths is not None:
        formula_bundle = combine_formula_components(
            load=load_formula_run(formula_run_paths["load"], label="load"),
            wind=load_formula_run(formula_run_paths["wind"], label="wind"),
            solar=load_formula_run(formula_run_paths["solar"], label="solar"),
        )
        _write_formula_artifacts(artifacts_dir=artifacts_dir, formula_bundle=formula_bundle)
        out_payload["formula_component_runs"] = {key: path.name for key, path in formula_run_paths.items()}
        out_payload["formula_component_targets"] = formula_bundle["targets"]
        out_payload["formula_eval_test"] = formula_bundle["metrics"]
    out_payload["completed_at"] = datetime.now(timezone.utc).isoformat()
    write_json(out_run_dir / "payload.json", out_payload)

    print(json.dumps({"out_run_id": out_run_id, "metrics": predictor_metrics, "has_formula": formula_run_paths is not None}, indent=2))


if __name__ == "__main__":
    main()
