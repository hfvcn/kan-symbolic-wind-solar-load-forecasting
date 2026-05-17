#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.paired_significance import PairedTestConfig, compare_run_dirs

DEFAULT_METRICS = ("absolute_error", "squared_error")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run paired significance tests for synced run predictions.")
    parser.add_argument("--reference-run", required=True, help="Reference run directory.")
    parser.add_argument("--compare-run", action="append", required=True, help="Compare run directory (repeatable).")
    parser.add_argument(
        "--metric",
        action="append",
        choices=sorted(DEFAULT_METRICS),
        help="Error metric to compare. Repeatable; defaults to absolute_error and squared_error.",
    )
    parser.add_argument("--bootstrap-samples", type=int, default=2000, help="Bootstrap sample count.")
    parser.add_argument("--permutation-samples", type=int, default=2000, help="Permutation sample count.")
    parser.add_argument("--seed", type=int, default=7, help="Random seed for bootstrap/permutation.")
    parser.add_argument("--out", required=True, help="Output CSV path.")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    out_path = Path(args.out)
    metrics = tuple(args.metric or DEFAULT_METRICS)
    rows: list[pd.DataFrame] = []
    for metric in metrics:
        config = PairedTestConfig(
            metric=metric,
            bootstrap_samples=args.bootstrap_samples,
            permutation_samples=args.permutation_samples,
            random_seed=args.seed,
        )
        rows.append(compare_run_dirs(args.reference_run, args.compare_run, config=config))
    result = pd.concat(rows, ignore_index=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(out_path, index=False)


if __name__ == "__main__":
    main()
