#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description="Build a KAN regularization ablation report (Phase 5).")
    ap.add_argument("--kan-run", action="append", required=True, help="Path to a synced Phase-2 KAN run directory (repeatable).")
    ap.add_argument("--out-dir", default="doc/paper_assets", help="Output directory for tables/figures.")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    for p in args.kan_run:
        run_dir = Path(p)
        payload = _read_json(run_dir / "payload.json")
        phase = payload.get("phase")
        if phase != "02-kan-training":
            raise ValueError(f"Expected phase=02-kan-training, got {phase} for {run_dir}")

        artifacts = run_dir / "artifacts"
        eval_unpruned = _read_json(artifacts / "eval_unpruned.json")
        eval_pruned = _read_json(artifacts / "eval_pruned.json")
        sparsity = _read_json(artifacts / "sparsity.json")

        started_at = _parse_dt(payload.get("started_at"))
        completed_at = _parse_dt(payload.get("completed_at"))
        compute_time_s = (completed_at - started_at).total_seconds() if started_at and completed_at else None

        cfg = payload.get("cfg", {}) or {}
        rmse_unpruned = eval_unpruned.get("rmse")
        rmse_pruned = eval_pruned.get("rmse")
        degrade_ratio = None
        if rmse_unpruned is not None and rmse_pruned is not None and float(rmse_unpruned) > 0:
            degrade_ratio = float(rmse_pruned) / float(rmse_unpruned)

        rows.append(
            {
                "run_id": payload.get("run_id", run_dir.name),
                "kind": payload.get("kind", "kan"),
                "rmse_unpruned": rmse_unpruned,
                "rmse_pruned": rmse_pruned,
                "rmse_degrade_ratio": degrade_ratio,
                "pruned_ratio": sparsity.get("pruned_ratio"),
                "pruned_edges": sparsity.get("pruned_edges"),
                "total_edges": sparsity.get("total_edges"),
                "sparsify_lamb": cfg.get("sparsify_lamb"),
                "sparsify_lamb_l1": cfg.get("sparsify_lamb_l1"),
                "sparsify_lamb_entropy": cfg.get("sparsify_lamb_entropy"),
                "max_train_rows": payload.get("max_train_rows", None),
                "compute_time_s": compute_time_s,
            }
        )

    df = pd.DataFrame(rows)
    if len(df) == 0:
        raise ValueError("No runs provided")

    df = df.sort_values(by=["rmse_pruned", "pruned_ratio"], ascending=[True, False], na_position="last")
    df.to_csv(out_dir / "ablation_table.csv", index=False)

    # Plot 1: RMSE bar chart (annotate sparsity).
    fig, ax = plt.subplots(figsize=(8, 3))
    kinds = df["kind"].astype(str).tolist()
    y = df["rmse_pruned"].astype(float).tolist()
    ax.bar(kinds, y, color="#4C72B0", alpha=0.9)
    for i, row in enumerate(df.itertuples(index=False)):
        try:
            pr = float(getattr(row, "pruned_ratio"))
            ax.text(i, float(getattr(row, "rmse_pruned")), f"pr={pr:.2f}", ha="center", va="bottom", fontsize=8)
        except Exception:
            pass
    ax.set_ylabel("Test RMSE (pruned)")
    ax.set_title("KAN regularization ablation (bar labels = pruned_ratio)")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(out_dir / "ablation_rmse_pruned.png", dpi=200)
    plt.close(fig)

    # Plot 2: Sparsity vs RMSE scatter.
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(df["pruned_ratio"].astype(float), df["rmse_pruned"].astype(float))
    for _, r in df.iterrows():
        ax.annotate(str(r["kind"]), (float(r["pruned_ratio"]), float(r["rmse_pruned"])), fontsize=8, alpha=0.85)
    ax.set_xlabel("edge_pruned_ratio")
    ax.set_ylabel("Test RMSE (pruned)")
    ax.set_title("Regularization ablation: sparsity vs accuracy")
    fig.tight_layout()
    fig.savefig(out_dir / "ablation_rmse_vs_sparsity.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()

