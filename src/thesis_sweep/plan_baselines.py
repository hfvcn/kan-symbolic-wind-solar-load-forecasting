from __future__ import annotations

import argparse

from src.thesis_sweep.baseline_protocols import NON_TORCH_MODELS, build_baseline_protocol_plans
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
    protocol_plans = build_baseline_protocol_plans(
        str(getattr(args, "baseline_protocols", "matched,best_effort")),
        model_types_csv=str(getattr(args, "baseline_models", "mlp,lstm")),
    )
    for kan_run_id, target_col in kan_target_by_run.items():
        if not str(target_col).startswith("delta_net_load"):
            continue
        for protocol in protocol_plans:
            rid = det_run_id(
                session_id,
                f"baseline_{protocol.model_type}_{protocol.protocol_name}_{protocol.protocol_trial}__{kan_run_id}",
            )

            if protocol.model_type in NON_TORCH_MODELS:
                cmd_args = [
                    "--data-run-id",
                    derived_id,
                    "--run-id",
                    rid,
                    "--model-type",
                    protocol.model_type,
                    "--target",
                    str(target_col),
                ]
                if protocol.max_train_rows is not None:
                    cmd_args += ["--max-train-rows", str(protocol.max_train_rows)]
                if kan_run_id:
                    cmd_args += ["--match-kan-run-id", kan_run_id]
                if protocol.sync_kan_feature_cols:
                    cmd_args.append("--sync-kan-feature-cols")
                ts_opt = str(args.source_timestamp).strip() or None
                if ts_opt:
                    cmd_args += ["--data-timestamp", ts_opt]
                job_file = REPO_ROOT / "modal_jobs" / "baseline_non_torch.py"
                cmd = modal_run(job_file, cmd_args, detached=detached)
                planned.append(PlannedCmd(name=f"baseline_{protocol.model_type}", run_id=rid, cmd=cmd))
                run_ids.append(rid)
                continue

            cmd_args = [
                "--data-run-id",
                derived_id,
                "--run-id",
                rid,
                "--model-type",
                protocol.model_type,
                "--target",
                str(target_col),
                "--protocol-name",
                protocol.protocol_name,
                "--protocol-trial",
                protocol.protocol_trial,
                "--epochs",
                str(protocol.epochs),
                "--lr",
                str(protocol.lr),
                "--patience",
                str(protocol.patience),
                "--hidden-dim",
                str(protocol.hidden_dim),
                "--dropout",
                str(protocol.dropout),
                "--seq-len",
                str(protocol.seq_len),
            ]
            if protocol.max_train_rows is not None:
                cmd_args += ["--max-train-rows", str(protocol.max_train_rows)]
            if kan_run_id:
                cmd_args += ["--match-kan-run-id", kan_run_id]
            if protocol.match_kan_param_count:
                cmd_args.append("--match-kan-param-count")
            if protocol.sync_kan_feature_cols:
                cmd_args.append("--sync-kan-feature-cols")
            if protocol.sync_kan_budget:
                cmd_args.append("--sync-kan-budget")
            if bool(args.use_gpu):
                cmd_args.append("--use-gpu")
            ts_opt = str(args.source_timestamp).strip() or None
            if ts_opt:
                cmd_args += ["--data-timestamp", ts_opt]
            cmd = modal_run(REPO_ROOT / "modal_jobs" / "baseline_torch.py", cmd_args, detached=detached)
            planned.append(PlannedCmd(name="baseline_torch", run_id=rid, cmd=cmd))
            run_ids.append(rid)
    return planned, run_ids
