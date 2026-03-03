from __future__ import annotations

import argparse

from src.thesis_sweep.types import PlannedCmd, SymbolicLibPlan
from src.thesis_sweep.utils import (
    LIB_MEDIUM,
    LIB_STRICT,
    LIB_STRICT_POLY4,
    REPO_ROOT,
    S0_R2_GRID_MAIN,
    S0_R2_GRID_STRICT_ENHANCED,
    SYMBOLIC_EVAL_CLIP_QUANTILES,
    SYMBOLIC_SAFE_EXP_CLIP,
    det_run_id,
    modal_run,
)


def _symbolic_lib_plans() -> tuple[SymbolicLibPlan, ...]:
    return (
        SymbolicLibPlan(name="strict", lib=LIB_STRICT, r2_thresholds=S0_R2_GRID_MAIN),
        SymbolicLibPlan(
            name="medium",
            lib=LIB_MEDIUM,
            r2_thresholds=S0_R2_GRID_MAIN,
            safe_exp_clip=SYMBOLIC_SAFE_EXP_CLIP,
            eval_clip_quantiles=SYMBOLIC_EVAL_CLIP_QUANTILES,
        ),
        SymbolicLibPlan(name="strict_poly4", lib=LIB_STRICT_POLY4, r2_thresholds=S0_R2_GRID_STRICT_ENHANCED),
    )


def _symbolic_lib_plans_reduced() -> tuple[SymbolicLibPlan, ...]:
    return (SymbolicLibPlan(name="strict", lib=LIB_STRICT, r2_thresholds=S0_R2_GRID_STRICT_ENHANCED),)


def plan_symbolic(
    args: argparse.Namespace,
    *,
    session_id: str,
    detached: bool,
    kan_train_run_ids: list[str],
) -> tuple[list[PlannedCmd], list[str], list[str]]:
    if bool(getattr(args, "no_symbolic", False)):
        return [], [], []
    sweeps = {s.strip().lower() for s in str(args.sweeps).split(",") if s.strip()}
    if "s0" not in sweeps:
        return [], [], []

    extra = [str(x).strip() for x in (args.symbolic_train_run_id or []) if str(x).strip()]
    train_ids = sorted({*kan_train_run_ids, *extra})
    if not train_ids:
        return [], [], []

    mode = str(getattr(args, "symbolic_grid_mode", "full")).strip().lower()
    if mode not in {"full", "auto_reduced"}:
        raise ValueError(f"Unknown symbolic_grid_mode: {mode}")

    planned: list[PlannedCmd] = []
    run_ids: list[str] = []
    for train_id in train_ids:
        use_full = (mode == "full") or (mode == "auto_reduced" and train_id in set(extra))
        lib_plans = _symbolic_lib_plans() if use_full else _symbolic_lib_plans_reduced()
        for lib_plan in lib_plans:
            for r2t in lib_plan.r2_thresholds:
                rid = det_run_id(session_id, f"sym_{lib_plan.name}_r2_{r2t}__{train_id}")
                cmd_args = [
                    "--train-run-id",
                    train_id,
                    "--run-id",
                    rid,
                    "--r2-threshold",
                    str(r2t),
                    "--weight-simple",
                    "0.9",
                    "--sample-rows",
                    "20000",
                    "--lib",
                    lib_plan.lib,
                ]
                if lib_plan.safe_exp_clip is not None:
                    cmd_args += ["--safe-exp-clip", str(lib_plan.safe_exp_clip)]
                if lib_plan.eval_clip_quantiles is not None:
                    ql, qh = lib_plan.eval_clip_quantiles
                    cmd_args += ["--eval-clip-quantiles", f"{ql},{qh}"]
                if bool(args.use_gpu):
                    cmd_args.append("--use-gpu")
                cmd = modal_run(REPO_ROOT / "modal_jobs" / "kan_symbolic.py", cmd_args, detached=detached)
                planned.append(PlannedCmd(name="kan_symbolic", run_id=rid, cmd=cmd))
                run_ids.append(rid)

    return planned, run_ids, train_ids
