from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.thesis_sweep.plan_baselines import plan_baselines
from src.thesis_sweep.plan_derive import plan_derive_dataset
from src.thesis_sweep.plan_kan import plan_kan_sweeps
from src.thesis_sweep.plan_symbolic import plan_symbolic
from src.thesis_sweep.postprocess import local_postprocess
from src.thesis_sweep.types import PlannedCmd
from src.thesis_sweep.utils import REPO_ROOT, VOLUME_NAME, run_cmd, sync_run, utc_session_id, write_manifest


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Thesis-oriented sweep driver (S0–S3).")
    ap.add_argument("--source-data-run-id", required=True, help="Synced Phase-1 run_id under runs/.")
    ap.add_argument("--source-timestamp", default="", help="Optional processed parquet timestamp.")
    ap.add_argument("--derived-data-run-id", default="", help="Optional existing Phase-1.5 derived run_id (skip derive).")
    ap.add_argument("--horizons", default="6,12,24", help="Horizon steps for S1/S2 (comma-separated).")
    ap.add_argument("--execute", action="store_true", help="Run commands (default: dry-run).")
    ap.add_argument("--dry-run", action="store_true", help="Print commands only.")
    ap.add_argument("--detached-remote", action="store_true", help="Submit Modal jobs with `modal run -d` and skip sync/local steps.")
    ap.add_argument("--no-auto-sync", action="store_true", help="Do not auto-sync remote runs.")
    ap.add_argument("--use-gpu", action="store_true", help="Use GPU variants (T4) when available.")
    ap.add_argument("--kan-hidden-width", default="10", help="KAN hidden width (single-layer fallback).")
    ap.add_argument("--kan-hidden-layers", default="", help="Optional CSV ints for deep KAN, e.g. 32,32.")
    ap.add_argument("--no-warmup-update-grid", action="store_true", help="Disable KAN warmup grid update.")
    ap.add_argument("--sweeps", default="s0,s1,s2,s3", help="Subset: s0,s1,s2,s3 (comma-separated).")
    ap.add_argument("--symbolic-train-run-id", action="append", default=[], help="Extra Phase-2 train run_id for S0 (repeatable).")
    ap.add_argument(
        "--symbolic-grid-mode",
        default="full",
        choices=["full", "auto_reduced"],
        help="S0 symbolic grid: full for all train runs, or full only for explicit --symbolic-train-run-id and reduced for auto runs.",
    )
    ap.add_argument("--session-id", default="", help="Optional fixed session id (folder under doc/thesis_sweeps/).")
    return ap.parse_args()


def _session_dir(session_id: str) -> Path:
    return REPO_ROOT / "doc" / "thesis_sweeps" / session_id


def _modal_env() -> dict[str, str]:
    env_modal = dict(os.environ)
    env_modal["KAN_SR_VOLUME"] = VOLUME_NAME
    env_modal["VOLUME_NAME"] = VOLUME_NAME
    return env_modal


def build_plan(args: argparse.Namespace, *, session_id: str, detached: bool) -> tuple[dict[str, Any], list[PlannedCmd], list[str], dict[str, str]]:
    planned: list[PlannedCmd] = []
    run_ids: list[str] = []

    derive_cmds, derive_run_ids, derived_id = plan_derive_dataset(args, session_id=session_id, detached=detached)
    planned += derive_cmds
    run_ids += derive_run_ids

    kan_cmds, kan_target_by_run, comp_runs = plan_kan_sweeps(args, session_id=session_id, detached=detached, derived_id=derived_id)
    planned += kan_cmds
    run_ids += list(kan_target_by_run.keys())

    baseline_cmds, baseline_runs = plan_baselines(args, session_id=session_id, detached=detached, derived_id=derived_id, kan_target_by_run=kan_target_by_run)
    planned += baseline_cmds
    run_ids += baseline_runs

    sym_cmds, symbolic_runs, symbolic_train_ids = plan_symbolic(args, session_id=session_id, detached=detached, kan_train_run_ids=list(kan_target_by_run.keys()))
    planned += sym_cmds
    run_ids += symbolic_runs
    run_ids += [rid for rid in symbolic_train_ids if rid not in run_ids]

    manifest = {
        "session_id": session_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "volume_name": VOLUME_NAME,
        "source_data_run_id": str(args.source_data_run_id).strip(),
        "source_timestamp": str(args.source_timestamp).strip() or None,
        "derived_data_run_id": derived_id,
        "planned": [{"name": p.name, "run_id": p.run_id, "cmd": p.cmd} for p in planned],
        "runs": {
            "kan_train": list(kan_target_by_run.keys()),
            "baselines": baseline_runs,
            "symbolic": symbolic_runs,
        },
        "structured_components": comp_runs,
    }

    return manifest, planned, run_ids, comp_runs


def execute_plan(planned: list[PlannedCmd], *, dry_run: bool, env_modal: dict[str, str]) -> None:
    for p in planned:
        run_cmd(p.cmd, dry_run=dry_run, cwd=REPO_ROOT, env=env_modal)


def sync_runs(run_ids: list[str], *, dry_run: bool) -> None:
    for rid in run_ids:
        sync_run(rid, dry_run=dry_run)


def main() -> None:
    args = parse_args()
    dry_run = bool(args.dry_run or (not args.execute))
    detached = bool(args.detached_remote)
    auto_sync = (not bool(args.no_auto_sync)) and (not detached)

    session_id = str(args.session_id).strip() or utc_session_id()
    session_dir = _session_dir(session_id)
    manifest_path = session_dir / "manifest.json"

    manifest, planned, run_ids, comp_runs = build_plan(args, session_id=session_id, detached=detached)
    manifest.update({"dry_run": dry_run, "detached_remote": detached, "auto_sync": auto_sync})
    write_manifest(manifest_path, manifest)

    execute_plan(planned, dry_run=dry_run, env_modal=_modal_env())
    if detached:
        print("\n[detached] Submitted with `modal run -d` (remote continues).")
        print(f"Manifest: {manifest_path}")
        print(f"To sync later: VOLUME_NAME={VOLUME_NAME} {REPO_ROOT / 'scripts' / 'sync_from_modal.sh'} <run_id>")
        return

    if auto_sync:
        sync_runs(run_ids, dry_run=dry_run)
    if auto_sync and (not dry_run):
        local_postprocess(run_ids=run_ids, comp_runs=comp_runs, session_id=session_id, session_dir=session_dir)
