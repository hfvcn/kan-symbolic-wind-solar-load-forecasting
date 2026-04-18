from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any

from src.thesis_sweep.utils import REPO_ROOT, VOLUME_NAME, det_run_id, local_py, modal_run, run_cmd, sync_run

COMPONENT_RUN_PREFERENCES = {
    "load": ("load",),
    "wind": ("physics_wind", "wind"),
    "solar": ("solar", "physics_solar"),
}


def _modal_env() -> dict[str, str]:
    env = dict(os.environ)
    env["KAN_SR_VOLUME"] = VOLUME_NAME
    env["VOLUME_NAME"] = VOLUME_NAME
    return env


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def _prediction_rmse(run_dir: Path) -> float:
    artifacts = run_dir / "artifacts"
    for name in ("eval_test_reconstructed.json", "eval_test.json"):
        metrics = _read_json(artifacts / name) or {}
        if metrics.get("rmse") is not None:
            return float(metrics["rmse"])
    return float("inf")


def _select_best_component_run(runs_root: Path, *, comp_runs: dict[str, str], keys: tuple[str, ...]) -> str | None:
    candidates: list[tuple[float, int, str]] = []
    for idx, key in enumerate(keys):
        run_id = str(comp_runs.get(key) or "").strip()
        if not run_id:
            continue
        candidates.append((_prediction_rmse(runs_root / run_id), idx, run_id))
    if not candidates:
        return None
    candidates.sort()
    return candidates[0][2]


def _structured_component_runs(runs_root: Path, comp_runs: dict[str, str]) -> dict[str, str] | None:
    resolved: dict[str, str] = {}
    missing: list[str] = []
    for target, keys in COMPONENT_RUN_PREFERENCES.items():
        run_id = _select_best_component_run(runs_root, comp_runs=comp_runs, keys=keys)
        if not run_id:
            missing.append(target)
            continue
        resolved[target] = run_id
    if missing:
        print(f"[postprocess] structured combo skipped: missing component runs for {', '.join(missing)}", flush=True)
        return None
    return resolved


def _formula_candidate_sort_key(run_dir: Path, payload: dict[str, Any]) -> tuple[float, float, str]:
    metrics = _read_json(run_dir / "artifacts" / "formula_eval_test.json") or {}
    rmse = float(metrics.get("rmse")) if metrics.get("rmse") is not None else float("inf")
    threshold = float(payload.get("r2_threshold")) if payload.get("r2_threshold") is not None else 0.0
    return (rmse, -threshold, run_dir.name)


def _find_best_symbolic_run(runs_root: Path, *, train_run_ids: tuple[str, ...]) -> str | None:
    candidates: list[tuple[tuple[float, float, str], str]] = []
    train_id_set = set(train_run_ids)
    for payload_path in sorted(runs_root.glob("*/payload.json")):
        payload = _read_json(payload_path)
        if not payload or str(payload.get("train_run_id") or "").strip() not in train_id_set:
            continue
        run_dir = payload_path.parent
        if not (run_dir / "artifacts" / "formula.sympy.txt").exists():
            continue
        candidates.append((_formula_candidate_sort_key(run_dir, payload), run_dir.name))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0])
    return candidates[0][1]


def _resolve_formula_run_ids(runs_root: Path, comp_runs: dict[str, str]) -> dict[str, str] | None:
    resolved: dict[str, str] = {}
    missing: list[str] = []
    for target, keys in COMPONENT_RUN_PREFERENCES.items():
        train_run_ids = tuple(str(comp_runs[key]).strip() for key in keys if str(comp_runs.get(key) or "").strip())
        if not train_run_ids:
            missing.append(target)
            continue
        formula_run_id = _find_best_symbolic_run(runs_root, train_run_ids=train_run_ids)
        if not formula_run_id:
            missing.append(target)
            continue
        resolved[target] = formula_run_id
    if missing:
        print(f"[postprocess] combo formula disabled: missing symbolic runs for {', '.join(missing)}", flush=True)
        return None
    return resolved


def local_postprocess(*, run_ids: list[str], comp_runs: dict[str, str], session_id: str, session_dir: Path) -> list[str]:
    run_ids_out = list(run_ids)
    run_paths = [str(REPO_ROOT / "runs" / rid) for rid in run_ids_out if (REPO_ROOT / "runs" / rid).exists()]
    if run_paths:
        local_py(REPO_ROOT / "scripts" / "reconstruct_predictions.py", sum([["--run", p] for p in run_paths], []), dry_run=False)

    component_runs = _structured_component_runs(REPO_ROOT / "runs", comp_runs) if comp_runs else None
    if component_runs is not None:
        combo_id = det_run_id(session_id, "s3_combo_net_load")
        formula_run_ids = _resolve_formula_run_ids(REPO_ROOT / "runs", comp_runs)
        modal_args = [
            "--load-run-id",
            component_runs["load"],
            "--wind-run-id",
            component_runs["wind"],
            "--solar-run-id",
            component_runs["solar"],
            "--out-run-id",
            combo_id,
        ]
        if formula_run_ids is not None:
            modal_args += [
                "--load-formula-run-id",
                formula_run_ids["load"],
                "--wind-formula-run-id",
                formula_run_ids["wind"],
                "--solar-formula-run-id",
                formula_run_ids["solar"],
            ]
        run_cmd(
            modal_run(
                REPO_ROOT / "modal_jobs" / "combine_net_load_runs.py",
                modal_args,
                detached=False,
            ),
            dry_run=False,
            cwd=REPO_ROOT,
            env=_modal_env(),
        )
        sync_run(combo_id, dry_run=False)
        run_ids_out.append(combo_id)

    out_dir = session_dir / "paper_assets"
    out_dir.mkdir(parents=True, exist_ok=True)
    eval_args = sum([["--run", str(REPO_ROOT / "runs" / rid)] for rid in run_ids_out if (REPO_ROOT / "runs" / rid).exists()], [])
    if eval_args:
        local_py(REPO_ROOT / "scripts" / "evaluate_runs.py", eval_args + ["--out-dir", str(out_dir)], dry_run=False)

    paper_session_dir = REPO_ROOT / "doc" / "paper_assets" / f"thesis_sweep_{session_id}"
    if out_dir.exists():
        if paper_session_dir.exists():
            shutil.rmtree(paper_session_dir)
        shutil.copytree(out_dir, paper_session_dir)
        local_py(REPO_ROOT / "scripts" / "build_asset_index.py", [], dry_run=False)

    return run_ids_out
