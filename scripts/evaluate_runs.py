#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.runs import build_comparison_table, seasonal_breakdown
from src.kan_sr.metrics import rmse


def main() -> None:
    ap = argparse.ArgumentParser(description="Build comparison tables/plots from synced runs/ artifacts.")
    ap.add_argument("--run", action="append", required=True, help="Path to a synced run directory (repeatable).")
    ap.add_argument("--out-dir", default="doc/paper_assets", help="Output directory for tables/figures.")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = build_comparison_table([Path(p) for p in args.run])
    table_path = out_dir / "comparison_table.csv"
    df.to_csv(table_path, index=False)

    # Transfer gap table (Phase 8): compare transfer runs against their source training run on TEST.
    run_paths = [Path(p) for p in args.run]
    run_by_name = {p.name: p for p in run_paths}
    gap_rows = []
    for p in run_paths:
        try:
            payload = json.loads((p / "payload.json").read_text())
        except Exception:
            continue
        if payload.get("phase") != "08-transfer-eval":
            continue
        src_id = payload.get("train_run_id")
        if not src_id or src_id not in run_by_name:
            continue
        src_run = run_by_name[str(src_id)]
        pred_src = src_run / "artifacts" / "predictions_test.parquet"
        pred_tgt = p / "artifacts" / "predictions_test.parquet"
        if not (pred_src.exists() and pred_tgt.exists()):
            continue
        try:
            src_df = pd.read_parquet(pred_src).dropna(subset=["y_true", "y_pred"])
            tgt_df = pd.read_parquet(pred_tgt).dropna(subset=["y_true", "y_pred"])
            r_src = rmse(src_df["y_true"].to_numpy(dtype="float64"), src_df["y_pred"].to_numpy(dtype="float64"))
            r_tgt = rmse(tgt_df["y_true"].to_numpy(dtype="float64"), tgt_df["y_pred"].to_numpy(dtype="float64"))
            gap_rows.append(
                {
                    "train_run_id": str(src_id),
                    "transfer_run_id": p.name,
                    "target_col": payload.get("target_col"),
                    "target_data_run_id": payload.get("target_data_run_id"),
                    "rmse_source_test": r_src,
                    "rmse_transfer_test": r_tgt,
                    "gap_ratio": (r_tgt / r_src) if (r_src is not None and r_src > 0) else None,
                }
            )
        except Exception:
            continue

    if gap_rows:
        gap_df = pd.DataFrame(gap_rows)
        gap_df.to_csv(out_dir / "transfer_gaps.csv", index=False)

        # Simple thesis-ready visualization of generalization gap.
        try:
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.bar(gap_df["transfer_run_id"], gap_df["gap_ratio"], color="#C44E52", alpha=0.9)
            ax.axhline(1.0, color="black", linewidth=1.0, alpha=0.7)
            ax.set_ylabel("RMSE (transfer) / RMSE (source)")
            ax.set_title("Cross-ISO generalization gap")
            fig.tight_layout()
            fig.savefig(out_dir / "transfer_gap_ratio.png", dpi=200)
            plt.close(fig)
        except Exception:
            pass

    # Per-run seasonal breakdown (if predictions_test.parquet exists)
    for run_path in [Path(p) for p in args.run]:
        pred_path = run_path / "artifacts" / "predictions_test_reconstructed.parquet"
        if not pred_path.exists():
            pred_path = run_path / "artifacts" / "predictions_test.parquet"
        if not pred_path.exists():
            continue
        try:
            pred_df = pd.read_parquet(pred_path)
            sb = seasonal_breakdown(pred_df)
            sb.to_csv(out_dir / f"seasonal_{run_path.name}.csv", index=False)
        except Exception:
            # Keep evaluation best-effort; some runs may not have datetime index.
            continue

    # Pareto-style scatter: RMSE vs complexity (if present)
    plot_df = df.dropna(subset=["rmse", "complexity"]).copy()
    if len(plot_df) > 0:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.scatter(plot_df["complexity"], plot_df["rmse"])
        for _, row in plot_df.iterrows():
            ax.annotate(str(row["kind"]), (row["complexity"], row["rmse"]), fontsize=8, alpha=0.8)
        ax.set_xlabel("Complexity")
        ax.set_ylabel("Test RMSE")
        ax.set_title("Accuracy vs Complexity (synced runs)")
        fig.tight_layout()
        fig.savefig(out_dir / "pareto_rmse_vs_complexity.png", dpi=200)


if __name__ == "__main__":
    main()
