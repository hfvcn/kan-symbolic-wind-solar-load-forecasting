#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    ap = argparse.ArgumentParser(description="Plot Pareto frontier: PySR equations vs KAN-SR symbolic formula.")
    ap.add_argument("--pysr-run", required=True, help="Path to PySR run directory (synced).")
    ap.add_argument("--kan-symbolic-run", required=True, help="Path to KAN symbolic run directory (synced).")
    ap.add_argument("--out", default="doc/paper_assets/pareto_pysr_vs_kan.png", help="Output image path.")
    args = ap.parse_args()

    pysr_run = Path(args.pysr_run)
    kan_run = Path(args.kan_symbolic_run)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    eq_path = pysr_run / "artifacts" / "equations.csv"
    if not eq_path.exists():
        raise FileNotFoundError(eq_path)

    eq = pd.read_csv(eq_path)
    # Prefer test metrics; fallback to loss if needed.
    rmse_col = "test_rmse" if "test_rmse" in eq.columns else ("loss" if "loss" in eq.columns else None)
    if rmse_col is None:
        raise ValueError("PySR equations.csv missing test_rmse or loss column")
    if "complexity" not in eq.columns:
        raise ValueError("PySR equations.csv missing complexity column")

    eq = eq.dropna(subset=["complexity", rmse_col]).copy()

    # KAN symbolic point
    kan_eval = json.loads((kan_run / "artifacts" / "formula_eval_test.json").read_text())
    kan_cmp = json.loads((kan_run / "artifacts" / "formula_metrics.json").read_text())
    kan_rmse = float(kan_eval["rmse"])
    kan_complexity = float(kan_cmp.get("node_count", float("nan")))

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(eq["complexity"], eq[rmse_col], s=12, alpha=0.6, label=f"PySR ({rmse_col})")
    ax.scatter([kan_complexity], [kan_rmse], s=80, marker="*", label="KAN-SR (symbolic)")

    ax.set_xlabel("Complexity")
    ax.set_ylabel("RMSE")
    ax.set_title("Pareto: PySR vs KAN-SR")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)


if __name__ == "__main__":
    main()
