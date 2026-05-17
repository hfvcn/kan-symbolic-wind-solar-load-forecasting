from __future__ import annotations

import argparse

from src.thesis_sweep.types import PlannedCmd
from src.thesis_sweep.utils import REPO_ROOT, det_run_id, modal_run, parse_csv_ints


def plan_derive_dataset(args: argparse.Namespace, *, session_id: str, detached: bool) -> tuple[list[PlannedCmd], list[str], str]:
    sweeps = {s.strip().lower() for s in str(args.sweeps).split(",") if s.strip()}
    hs = sorted({1, *parse_csv_ints(str(getattr(args, "horizons", "6,12,24")))})
    hs_name = "_".join(str(h) for h in hs)
    rolling_origin_index = int(getattr(args, "rolling_origin_index", -1))
    rolling_suffix = "" if rolling_origin_index < 0 else f"_ro{rolling_origin_index:02d}"
    derived_id = str(args.derived_data_run_id).strip() or det_run_id(session_id, f"derived_h{hs_name}{rolling_suffix}")
    if not ({"s1", "s2", "s3"} & sweeps) or str(args.derived_data_run_id).strip():
        return [], [], derived_id

    ts_opt = str(args.source_timestamp).strip() or None
    source_id = str(args.source_data_run_id).strip()
    horizons_csv = ",".join(str(h) for h in hs)
    cmd = modal_run(
        REPO_ROOT / "modal_jobs" / "derive_dataset.py",
        [
            "--source-data-run-id",
            source_id,
            "--run-id",
            derived_id,
            "--horizon-steps",
            horizons_csv,
            "--net-load-lag-steps",
            "1,12,48",
            "--add-hub-wind",
            "--add-temp-ghi",
            "--add-absolute-targets",
        ]
        + (["--rolling-origin-index", str(rolling_origin_index)] if rolling_origin_index >= 0 else [])
        + (
            ["--rolling-origin-step-steps", str(int(getattr(args, "rolling_origin_step_steps", 0)))]
            if int(getattr(args, "rolling_origin_step_steps", 0)) > 0
            else []
        )
        + (["--source-timestamp", ts_opt] if ts_opt else []),
        detached=detached,
    )
    return [PlannedCmd(name="derive_dataset", run_id=derived_id, cmd=cmd)], [derived_id], derived_id
