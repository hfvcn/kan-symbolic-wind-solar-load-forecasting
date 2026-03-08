#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.ablation_summary import AblationSummaryConfig, as_run_dir, summarize_run, write_csv

WIND_CONFIG = AblationSummaryConfig(
    target_prefix="delta_wind",
    edge_field_name="wind_speed_edges",
    feature_prefixes=("wind_speed_",),
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize wind ablation or horizon runs (abs(test) + delta(test/val) + wind_speed_edges)."
    )
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
            config=WIND_CONFIG,
            require_abs=bool(args.require_abs),
        )
        for run_arg in args.run
    ]
    write_csv(rows, edge_field_name=WIND_CONFIG.edge_field_name, output=sys.stdout)


if __name__ == "__main__":
    main()
