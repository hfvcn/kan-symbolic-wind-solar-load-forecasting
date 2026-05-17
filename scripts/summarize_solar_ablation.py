#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.ablation_summary import AblationSummaryConfig, as_run_dir, summarize_run, write_csv

SOLAR_CONFIG = AblationSummaryConfig(
    target_prefix="delta_solar",
    edge_field_name="ghi_edges",
    feature_prefixes=("ghi_",),
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize solar ablation runs (abs(test) + delta(test/val) + ghi_edges).")
    parser.add_argument("--run", action="append", required=True, help="Run id or path to local run dir (repeatable).")
    parser.add_argument(
        "--require-abs",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Require predictions_test_reconstructed.parquet to exist (default: true).",
    )
    args = parser.parse_args()

    rows = [
        summarize_run(
            as_run_dir(str(run_arg), repo_root=REPO_ROOT),
            config=SOLAR_CONFIG,
            require_abs=bool(args.require_abs),
        )
        for run_arg in args.run
    ]
    write_csv(rows, edge_field_name=SOLAR_CONFIG.edge_field_name, output=sys.stdout)


if __name__ == "__main__":
    main()
