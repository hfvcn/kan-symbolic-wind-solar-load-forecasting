from __future__ import annotations

import argparse

from src.thesis_sweep.types import PlannedCmd
from src.thesis_sweep.utils import REPO_ROOT, det_run_id, modal_run


def plan_derive_dataset(args: argparse.Namespace, *, session_id: str, detached: bool) -> tuple[list[PlannedCmd], list[str], str]:
    sweeps = {s.strip().lower() for s in str(args.sweeps).split(",") if s.strip()}
    derived_id = str(args.derived_data_run_id).strip() or det_run_id(session_id, "derived_h1_6_12_24")
    if not ({"s1", "s2", "s3"} & sweeps) or str(args.derived_data_run_id).strip():
        return [], [], derived_id

    ts_opt = str(args.source_timestamp).strip() or None
    source_id = str(args.source_data_run_id).strip()
    cmd = modal_run(
        REPO_ROOT / "modal_jobs" / "derive_dataset.py",
        [
            "--source-data-run-id",
            source_id,
            "--run-id",
            derived_id,
            "--horizon-steps",
            "1,6,12,24",
            "--net-load-lag-steps",
            "1,12,48",
        ]
        + (["--source-timestamp", ts_opt] if ts_opt else []),
        detached=detached,
    )
    return [PlannedCmd(name="derive_dataset", run_id=derived_id, cmd=cmd)], [derived_id], derived_id

