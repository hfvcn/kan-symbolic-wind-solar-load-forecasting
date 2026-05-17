#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.reconstruction import (
    delta_reconstruction_spec,
    infer_data_ref,
    infer_target_col,
    read_json,
    reconstruct_delta_run,
)


def main() -> None:
    ap = argparse.ArgumentParser(description="Reconstruct base-series predictions for delta targets.")
    ap.add_argument("--run", action="append", required=True, help="Path to a synced run directory (repeatable).")
    args = ap.parse_args()

    ok = 0
    skipped = 0
    for run_path in args.run:
        run_dir = Path(run_path)
        payload_path = run_dir / "payload.json"
        if not payload_path.exists():
            skipped += 1
            continue
        payload = read_json(payload_path)
        target_col = infer_target_col(payload)
        data_run_id, data_ts = infer_data_ref(payload)
        if not target_col or not data_run_id or not data_ts:
            skipped += 1
            continue
        if delta_reconstruction_spec(target_col) is None:
            skipped += 1
            continue
        did = reconstruct_delta_run(
            run_dir,
            runs_root=REPO_ROOT / "runs",
            target_col=target_col,
            data_run_id=data_run_id,
            data_timestamp=data_ts,
        )
        ok += int(bool(did))

    print(f"[reconstruct] done: ok={ok} skipped={skipped}")


if __name__ == "__main__":
    main()
