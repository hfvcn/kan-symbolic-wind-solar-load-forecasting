#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.stratified_analysis import analyze_frame, load_run_frame

_FAMILY_CHOICES = ("season", "weekpart", "day_night", "ghi_quantile", "wind_quantile", "volatility")


def _parse_run_spec(raw: str) -> tuple[str, Path]:
    if "=" not in raw:
        path = Path(raw)
        return path.name, path
    name, path_str = raw.split("=", 1)
    return name, Path(path_str)


def main() -> None:
    ap = argparse.ArgumentParser(description="Build stratified thesis tables from synced runs.")
    ap.add_argument("--run", action="append", required=True, help="Run spec as name=path or path.")
    ap.add_argument("--family", action="append", choices=_FAMILY_CHOICES, help="Optional explicit family filter.")
    ap.add_argument("--out", required=True, help="Output CSV path.")
    args = ap.parse_args()

    rows: list[pd.DataFrame] = []
    for raw in args.run:
        run_name, run_path = _parse_run_spec(raw)
        target_col, frame = load_run_frame(run_path)
        summary = analyze_frame(frame, target_col=target_col, families=args.family)
        summary.insert(0, "run_id", run_name)
        rows.append(summary)

    out_df = pd.concat(rows, ignore_index=True)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)


if __name__ == "__main__":
    main()
