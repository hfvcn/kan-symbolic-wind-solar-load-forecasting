#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.case4_matched import DEFAULT_BOOTSTRAP_SAMPLES, DEFAULT_RANDOM_SEED, paired_rows, summary_rows


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description="Summarize Case 4 matched blocking results from paired seed runs.")
    ap.add_argument("--unblocked-run", action="append", required=True, help="Path to unblocked run directory; repeatable.")
    ap.add_argument("--blocked-run", action="append", required=True, help="Path to blocked run directory; repeatable.")
    ap.add_argument("--out-dir", required=True, help="Directory for summary CSV assets.")
    ap.add_argument("--tag", default="20260417", help="Suffix tag for output asset names.")
    ap.add_argument("--bootstrap-samples", type=int, default=DEFAULT_BOOTSTRAP_SAMPLES)
    ap.add_argument("--seed", type=int, default=DEFAULT_RANDOM_SEED)
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    unblocked_dirs = [Path(path).resolve() for path in args.unblocked_run]
    blocked_dirs = [Path(path).resolve() for path in args.blocked_run]
    detail_rows = paired_rows(unblocked_dirs, blocked_dirs)
    summary = summary_rows(detail_rows, samples=int(args.bootstrap_samples), seed=int(args.seed))

    _write_csv(out_dir / f"case4_matched_blocking_seed_detail_{args.tag}.csv", detail_rows)
    _write_csv(out_dir / f"case4_matched_blocking_summary_{args.tag}.csv", summary)


if __name__ == "__main__":
    main()
