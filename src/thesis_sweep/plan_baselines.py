from __future__ import annotations

import argparse

from src.thesis_sweep.types import PlannedCmd
from src.thesis_sweep.utils import REPO_ROOT, det_run_id, modal_run


def plan_baselines(
    args: argparse.Namespace,
    *,
    session_id: str,
    detached: bool,
    derived_id: str,
    kan_target_by_run: dict[str, str],
) -> tuple[list[PlannedCmd], list[str]]:
    planned: list[PlannedCmd] = []
    run_ids: list[str] = []
    for kan_run_id, target_col in kan_target_by_run.items():
        if not str(target_col).startswith("delta_net_load"):
            continue
        rid = det_run_id(session_id, f"baseline_torch_mlp__{kan_run_id}")
        cmd_args = [
            "--data-run-id",
            derived_id,
            "--run-id",
            rid,
            "--model-type",
            "mlp",
            "--target",
            str(target_col),
            "--match-kan-run-id",
            kan_run_id,
            "--sync-kan-feature-cols",
            "--sync-kan-budget",
            "--patience",
            "0",
            "--max-train-rows",
            "200000",
        ]
        if bool(args.use_gpu):
            cmd_args.append("--use-gpu")
        ts_opt = str(args.source_timestamp).strip() or None
        if ts_opt:
            cmd_args += ["--data-timestamp", ts_opt]
        cmd = modal_run(REPO_ROOT / "modal_jobs" / "baseline_torch.py", cmd_args, detached=detached)
        planned.append(PlannedCmd(name="baseline_torch", run_id=rid, cmd=cmd))
        run_ids.append(rid)
    return planned, run_ids

