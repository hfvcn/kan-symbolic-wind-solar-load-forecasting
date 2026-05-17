#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.thesis_sweep.refresh_session import refresh_session, resolve_refresh_inputs


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Refresh a thesis sweep session after syncing extra runs.")
    ap.add_argument("--session-id", required=True, help="Target session id under doc/thesis_sweeps/.")
    ap.add_argument(
        "--sync-from-session",
        action="append",
        default=[],
        help="Extra thesis session id whose run_ids should be synced and included before refresh.",
    )
    ap.add_argument(
        "--run-id",
        action="append",
        default=[],
        help="Explicit extra run_id to sync and include in the refreshed asset table.",
    )
    ap.add_argument(
        "--collect-paper-reference",
        action="store_true",
        help="Also rebuild doc/paper_assets/paper_reference_<session-id> after refresh.",
    )
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    inputs = resolve_refresh_inputs(
        session_id=args.session_id,
        sync_from_sessions=args.sync_from_session,
        extra_run_ids=args.run_id,
    )
    print(
        f"[refresh] session={inputs.session_id} eval_runs={len(inputs.run_ids)} sync_runs={len(inputs.sync_run_ids)}",
        flush=True,
    )
    refresh_session(inputs, collect_paper_reference=bool(args.collect_paper_reference))


if __name__ == "__main__":
    main()
