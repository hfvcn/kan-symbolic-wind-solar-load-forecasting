#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


def _apply_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "font.size": 11,
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _box(ax, x: float, y: float, w: float, h: float, title: str, body: str, color: str) -> None:
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.03", linewidth=1.2, edgecolor=color, facecolor=color, alpha=0.12)
    ax.add_patch(patch)
    ax.text(x + 0.02, y + h - 0.07, title, fontsize=12, fontweight="bold", va="top")
    ax.text(x + 0.02, y + h - 0.13, body, fontsize=10, va="top")


def _arrow(ax, start: tuple[float, float], end: tuple[float, float]) -> None:
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=12, linewidth=1.2, color="#3a3a3a"))


def render_system_flow(out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    _box(ax, 0.03, 0.58, 0.18, 0.24, "Phase 1", "Data pipeline\nDownload, clean, derive horizons", "#5b8c85")
    _box(ax, 0.27, 0.58, 0.18, 0.24, "Phase 2", "KAN training\nSparse prune and export predictions", "#e29f47")
    _box(ax, 0.51, 0.58, 0.18, 0.24, "Phase 3", "Symbolic extraction\nFormula, LaTeX, replay, physics map", "#d66a4f")
    _box(ax, 0.75, 0.58, 0.2, 0.24, "Evaluation", "Main table, Pareto, ablation\nBoundary case, stratified error", "#6c7bd9")

    _box(ax, 0.18, 0.17, 0.22, 0.2, "1.5 / S3", "Load, solar, wind\nsub-formulas and recombination", "#7b4fa3")
    _box(ax, 0.46, 0.17, 0.2, 0.2, "Metric gate", "delta to abs reconstruction\nUnified persistence skill", "#4f7d3a")
    _box(ax, 0.72, 0.17, 0.22, 0.2, "Delivery", "Figures, manifest, asset index\nClaim freeze and todo closure", "#3c6e71")

    _arrow(ax, (0.21, 0.7), (0.27, 0.7))
    _arrow(ax, (0.45, 0.7), (0.51, 0.7))
    _arrow(ax, (0.69, 0.7), (0.75, 0.7))
    _arrow(ax, (0.36, 0.58), (0.29, 0.37))
    _arrow(ax, (0.6, 0.58), (0.56, 0.37))
    _arrow(ax, (0.86, 0.58), (0.83, 0.37))
    _arrow(ax, (0.4, 0.27), (0.46, 0.27))
    _arrow(ax, (0.66, 0.27), (0.72, 0.27))

    ax.text(0.03, 0.92, "Paper-grade evidence chain", fontsize=14, fontweight="bold")
    ax.text(0.03, 0.88, "Minimal closed loop from teacher to symbolic, boundary analysis, and thesis assets.", fontsize=10, color="#4a4a4a")
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def render_boundary_case(boundary_json: Path, out_path: Path) -> None:
    payload = _read_json(boundary_json)
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.6))

    rmse_values = [
        payload["abs_test"]["rmse"],
        payload["abs_test_clip_0_train_max"]["rmse"],
        payload["abs_test"]["rmse_persist"],
    ]
    skill_values = [
        payload["abs_test"]["skill"],
        payload["abs_test_clip_0_train_max"]["skill"],
        0.0,
    ]
    labels = ["raw formula", "clip to train max", "persistence"]
    colors = ["#d66a4f", "#e29f47", "#5b8c85"]

    axes[0].bar(labels, rmse_values, color=colors, alpha=0.9)
    axes[0].set_title("Solar h=288 boundary case")
    axes[0].set_ylabel("Abs-test RMSE")
    axes[0].tick_params(axis="x", rotation=15)
    for idx, value in enumerate(skill_values):
        axes[0].text(idx, rmse_values[idx] * 1.01, f"skill={value:.3f}", ha="center", va="bottom", fontsize=9)

    bounds = payload["abs_pred_out_of_bounds"]
    bound_labels = ["neg_ratio", "above_train_p99", "above_train_max"]
    bound_values = [bounds["neg_ratio"], bounds["above_train_p99_ratio"], bounds["above_train_max_ratio"]]
    axes[1].bar(bound_labels, bound_values, color=["#d66a4f", "#6c7bd9", "#3c6e71"], alpha=0.9)
    axes[1].set_ylim(0, max(0.75, float(np.max(bound_values) * 1.1)))
    axes[1].set_title("Out-of-bounds evidence")
    axes[1].set_ylabel("ratio")
    axes[1].tick_params(axis="x", rotation=15)
    for idx, value in enumerate(bound_values):
        axes[1].text(idx, value + 0.01, f"{value:.3f}", ha="center", va="bottom", fontsize=9)

    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def render_s3_formula_closure(closure_csv: Path, out_path: Path) -> None:
    rows = _read_csv_rows(closure_csv)
    by_label = {row["label"]: row for row in rows}
    ordered = [
        ("direct_kan_teacher", "Direct\nKAN", "#4C72B0"),
        ("direct_symbolic_formula", "Direct\nsymbolic", "#DD8452"),
        ("s3_composite_predictor", "S3\npredictor", "#55A868"),
        ("s3_composite_formula", "S3\nformula", "#C44E52"),
    ]
    labels = [item[1] for item in ordered]
    colors = [item[2] for item in ordered]
    rmse_vals = [float(by_label[item[0]]["rmse"]) for item in ordered]
    skill_vals = [float(by_label[item[0]]["skill_score"]) for item in ordered]
    ratio_vals = [float(by_label[item[0]]["rmse_ratio_vs_teacher"]) for item in ordered]

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.2))
    x = np.arange(len(labels))

    rmse_bars = axes[0].bar(x, rmse_vals, color=colors, alpha=0.9, edgecolor="black", linewidth=0.6)
    axes[0].set_xticks(x, labels)
    axes[0].set_ylabel("RMSE")
    axes[0].set_title("Closure Replay RMSE")
    axes[0].set_ylim(0, max(rmse_vals) * 1.18)
    for idx, bar in enumerate(rmse_bars):
        axes[0].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() * 1.01,
            f"{rmse_vals[idx]:.1f}\n{ratio_vals[idx]:.3f}x",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    skill_bars = axes[1].bar(x, skill_vals, color=colors, alpha=0.9, edgecolor="black", linewidth=0.6)
    axes[1].axhline(0.0, color="#333333", linewidth=1.0, alpha=0.8)
    axes[1].set_xticks(x, labels)
    axes[1].set_ylabel("Skill")
    axes[1].set_title("Predictor vs Formula Skill")
    ymin = min(skill_vals)
    ymax = max(skill_vals)
    span = max(0.15, ymax - ymin)
    axes[1].set_ylim(ymin - span * 0.25, ymax + span * 0.35)
    for idx, bar in enumerate(skill_bars):
        y = bar.get_height()
        va = "bottom" if y >= 0 else "top"
        offset = 0.015 if y >= 0 else -0.015
        axes[1].text(
            bar.get_x() + bar.get_width() / 2,
            y + offset,
            f"{skill_vals[idx]:.3f}",
            ha="center",
            va=va,
            fontsize=8,
        )

    fig.suptitle("S3 Closure: direct baseline, composite predictor, and composite formula", fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description="Render thesis delivery figures that are not tied to a single run.")
    ap.add_argument("--out-dir", default="doc/paper_assets/paper_delivery_20260306", help="Output directory.")
    ap.add_argument(
        "--boundary-json",
        default="doc/paper_assets/paper_delivery_20260306/solar_h288_boundary_20260306.json",
        help="Boundary-case JSON produced by diagnose_solar_bounds.py.",
    )
    ap.add_argument(
        "--s3-closure-csv",
        default="doc/paper_assets/paper_delivery_20260306/s3_main_comparison_20260417.csv",
        help="Four-object closure CSV for direct teacher / direct symbolic / S3 predictor / S3 formula.",
    )
    args = ap.parse_args()

    _apply_style()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    render_system_flow(out_dir / "system_flow_pipeline.png")
    render_boundary_case(Path(args.boundary_json), out_dir / "solar_h288_boundary_20260306.png")
    render_s3_formula_closure(Path(args.s3_closure_csv), out_dir / "s3_formula_closure_20260417.png")


if __name__ == "__main__":
    main()
