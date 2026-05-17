"""
Structured net-load combination as a Modal job.

The job runs directly against the Modal volume:
1. Reconstructs absolute-series artifacts for delta component runs when needed.
2. Combines load / wind / solar predictor runs into a `phase=05` combo run.
3. Optionally combines three symbolic local formulas into a composite net-load formula.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import modal

APP_NAME = "kan-sr-combine-net-load"
DEFAULT_VOLUME_NAME = os.environ.get("KAN_SR_VOLUME", "kan-sr")
VOLUME_MOUNT = "/vol"

app = modal.App(APP_NAME)
volume = modal.Volume.from_name(DEFAULT_VOLUME_NAME, create_if_missing=True)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "numpy>=1.24",
        "pandas>=2.0",
        "pyarrow>=14.0",
        "scikit-learn>=1.3",
        "sympy>=1.13.3",
    )
    .env({"PYTHONPATH": "/root/project"})
    .add_local_dir(SRC_DIR, remote_path="/root/project/src")
)


def _utc_run_id(prefix: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    return f"{prefix}_{ts}_{uuid.uuid4().hex[:8]}"


def _build_output_payload(
    *,
    out_run_id: str,
    horizon: int,
    started_at: datetime,
    component_runs: dict[str, Any],
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


def _prepare_delta_run(run_dir: Path, *, runs_root: Path) -> None:
    from src.eval.reconstruction import delta_reconstruction_spec, infer_data_ref, infer_target_col, read_json, reconstruct_delta_run

    payload_path = run_dir / "payload.json"
    if not payload_path.exists():
        raise FileNotFoundError(f"payload.json not found: {payload_path}")
    payload = read_json(payload_path)
    target_col = infer_target_col(payload)
    data_run_id, data_timestamp = infer_data_ref(payload)
    if not target_col or not data_run_id or not data_timestamp:
        return
    if delta_reconstruction_spec(target_col) is None:
        return
    reconstruct_delta_run(
        run_dir,
        runs_root=runs_root,
        target_col=target_col,
        data_run_id=data_run_id,
        data_timestamp=data_timestamp,
    )


def _write_formula_artifacts(*, artifacts_dir: Path, formula_bundle: dict[str, Any]) -> None:
    from src.eval.structured_combo import (
        FORMULA_COMBINED_METRICS,
        FORMULA_COMBINED_SYMPY,
        FORMULA_COMBINED_TEX,
        FORMULA_EVAL_TEST,
        FORMULA_PREDICTIONS,
        write_json,
    )

    (artifacts_dir / FORMULA_COMBINED_SYMPY).write_text(str(formula_bundle["expr"]))
    (artifacts_dir / FORMULA_COMBINED_TEX).write_text(str(formula_bundle["tex"]))
    formula_bundle["pred_df"].to_parquet(artifacts_dir / FORMULA_PREDICTIONS, compression="snappy")
    write_json(artifacts_dir / FORMULA_EVAL_TEST, formula_bundle["metrics"])
    write_json(artifacts_dir / FORMULA_COMBINED_METRICS, formula_bundle["complexity"])


def _resolve_formula_run_paths(
    *,
    runs_root: Path,
    load_formula_run_id: str | None,
    wind_formula_run_id: str | None,
    solar_formula_run_id: str | None,
) -> dict[str, Path] | None:
    from src.eval.structured_combo import require_complete_formula_runs

    raw_paths = require_complete_formula_runs(
        {
            "load": load_formula_run_id or "",
            "wind": wind_formula_run_id or "",
            "solar": solar_formula_run_id or "",
        }
    )
    if raw_paths is None:
        return None
    return {key: runs_root / raw_paths[key].name for key in ("load", "wind", "solar")}


@app.function(image=image, volumes={VOLUME_MOUNT: volume}, timeout=60 * 60)
def combine_remote(
    load_run_id: str,
    wind_run_id: str,
    solar_run_id: str,
    *,
    out_run_id: str | None = None,
    load_formula_run_id: str | None = None,
    wind_formula_run_id: str | None = None,
    solar_formula_run_id: str | None = None,
) -> dict[str, Any]:
    from src.eval.structured_combo import combine_formula_components, combine_prediction_components, load_component_run, load_formula_run, require_complete_formula_runs, write_json

    runs_root = Path(VOLUME_MOUNT) / "runs"
    started_at = datetime.now(timezone.utc)
    component_paths = {
        "load": runs_root / str(load_run_id),
        "wind": runs_root / str(wind_run_id),
        "solar": runs_root / str(solar_run_id),
    }
    for run_dir in component_paths.values():
        _prepare_delta_run(run_dir, runs_root=runs_root)

    predictor_components = {
        "load": load_component_run(component_paths["load"], label="load"),
        "wind": load_component_run(component_paths["wind"], label="wind"),
        "solar": load_component_run(component_paths["solar"], label="solar"),
    }
    predictor_df, predictor_metrics, horizon = combine_prediction_components(
        load=predictor_components["load"],
        wind=predictor_components["wind"],
        solar=predictor_components["solar"],
    )

    formula_run_paths = _resolve_formula_run_paths(
        runs_root=runs_root,
        load_formula_run_id=load_formula_run_id,
        wind_formula_run_id=wind_formula_run_id,
        solar_formula_run_id=solar_formula_run_id,
    )
    if formula_run_paths is not None:
        for run_dir in formula_run_paths.values():
            _prepare_delta_run(run_dir, runs_root=runs_root)

    final_run_id = str(out_run_id or "").strip() or _utc_run_id("combo_net_load")
    out_run_dir = runs_root / final_run_id
    artifacts_dir = out_run_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    predictor_df.to_parquet(artifacts_dir / "predictions_test.parquet", compression="snappy")
    write_json(artifacts_dir / "eval_test.json", predictor_metrics)
    out_payload = _build_output_payload(
        out_run_id=final_run_id,
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
    volume.commit()
    return {"out_run_id": final_run_id, "metrics": predictor_metrics, "has_formula": formula_run_paths is not None}


@app.local_entrypoint()
def main(
    load_run_id: str,
    wind_run_id: str,
    solar_run_id: str,
    out_run_id: str = "",
    load_formula_run_id: str = "",
    wind_formula_run_id: str = "",
    solar_formula_run_id: str = "",
) -> None:
    result = combine_remote.remote(
        load_run_id,
        wind_run_id,
        solar_run_id,
        out_run_id=out_run_id.strip() or None,
        load_formula_run_id=load_formula_run_id.strip() or None,
        wind_formula_run_id=wind_formula_run_id.strip() or None,
        solar_formula_run_id=solar_formula_run_id.strip() or None,
    )
    print(json.dumps(result, indent=2))
