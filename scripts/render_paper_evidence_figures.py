#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np

CASE3_UNBLOCKED_EDGES = [0, 8, 0, 0, 1]
CASE3_BLOCKED_EDGES = [19, 19, 8, 15, 1]
SOLAR_GROUPS = ["lags_only", "meteo_only", "both"]
SOLAR_LABELS = {"lags_only": "lags", "meteo_only": "meteo", "both": "both"}
SOLAR_COLORS = {"lags_only": "#4C72B0", "meteo_only": "#55A868", "both": "#C44E52"}


def _apply_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _find_metric(rows: list[dict[str, str]], metric: str) -> dict[str, str]:
    for row in rows:
        if str(row.get("metric") or "").strip() == metric:
            return row
    raise ValueError(f"Metric not found in summary CSV: {metric}")


def render_direct_collapse(out_path: Path) -> None:
    configs = ["s98", "s99", "s995", "m98", "m99", "m995", "x98", "x99", "x995"]
    families = ["load lag", "wind", "GHI", "temp"]
    matrix = np.array(
        [
            [1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
        dtype=float,
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.8, 4.0), gridspec_kw={"width_ratios": [1.15, 0.95]})
    im = ax1.imshow(matrix, cmap="YlOrRd", vmin=0, vmax=1, aspect="auto")
    ax1.set_xticks(np.arange(len(configs)), configs)
    ax1.set_yticks(np.arange(len(families)), families)
    ax1.set_title("Direct symbolic presence matrix")
    ax1.set_xlabel("3 libraries x 3 thresholds")
    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            color = "white" if matrix[row, col] > 0 else "black"
            ax1.text(col, row, str(int(matrix[row, col])), ha="center", va="center", fontsize=10, color=color)
    cbar = fig.colorbar(im, ax=ax1, fraction=0.046, pad=0.04)
    cbar.set_label("presence")

    ax2.axis("off")
    ax2.text(0.02, 0.88, "Collapsed support", fontsize=12, fontweight="bold", transform=ax2.transAxes)
    ax2.text(
        0.02,
        0.70,
        "All 9 direct symbolic configs retain only\nload lag support while pruning wind, GHI,\nand temperature to zero.",
        fontsize=10,
        transform=ax2.transAxes,
    )
    ax2.text(
        0.02,
        0.46,
        r"$\hat{y} \approx 0.0007 \times load - 3.0$",
        fontsize=15,
        transform=ax2.transAxes,
        bbox={"boxstyle": "round,pad=0.3", "fc": "#fff3e0", "ec": "#C44E52", "lw": 1.2},
    )
    ax2.text(0.02, 0.22, "VER(any physical) = 0/9", fontsize=11, fontweight="bold", transform=ax2.transAxes)
    ax2.text(0.02, 0.10, "Direct symbolic skill = 0.076, TGR = 1.690", fontsize=10, transform=ax2.transAxes)

    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def render_horizon_patterns(wind_csv: Path, solar_csv: Path, out_path: Path) -> None:
    wind_rows = sorted(_read_csv_rows(wind_csv), key=lambda row: int(row["horizon_steps"]))
    solar_rows = sorted(_read_csv_rows(solar_csv), key=lambda row: (int(row["horizon_steps"]), row["kind"]))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.1))

    horizons = [int(row["horizon_steps"]) for row in wind_rows]
    wind_skill = [float(row["abs_test_skill"]) for row in wind_rows]
    wind_edges = [float(row["wind_speed_edges"]) for row in wind_rows]
    x = np.arange(len(horizons))

    ax1.plot(x, wind_skill, marker="o", linewidth=2.0, color="#4C72B0", label="skill")
    ax1.set_xticks(x, [f"h={h}" for h in horizons])
    ax1.set_ylabel("abs-test skill")
    ax1.set_title("Wind horizon pattern")
    ax1.set_ylim(0.0, max(wind_skill) * 1.2)
    for idx, value in enumerate(wind_skill):
        ax1.text(idx, value + 0.02, f"{value:.3f}", ha="center", va="bottom", fontsize=8)

    ax1b = ax1.twinx()
    ax1b.plot(x, wind_edges, marker="s", linewidth=1.8, linestyle="--", color="#C44E52", label="wind edges")
    ax1b.set_ylabel("wind_speed edges")
    ax1b.set_ylim(0, max(wind_edges) + 3)
    for idx, value in enumerate(wind_edges):
        ax1b.text(idx, value + 0.4, f"{int(value)}", ha="center", va="bottom", fontsize=8, color="#C44E52")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1b.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, frameon=False, loc="upper right")

    solar_horizons = sorted({int(row["horizon_steps"]) for row in solar_rows})
    base = np.arange(len(solar_horizons))
    width = 0.23
    offsets = {"lags_only": -width, "meteo_only": 0.0, "both": width}

    for group in SOLAR_GROUPS:
        rows = [row for row in solar_rows if row["kind"].endswith(group)]
        xs = base + offsets[group]
        skills = [float(row["abs_test_skill"]) for row in rows]
        edges = [int(row["ghi_edges"]) for row in rows]
        bars = ax2.bar(xs, skills, width=width, color=SOLAR_COLORS[group], alpha=0.9, label=SOLAR_LABELS[group])
        for idx, bar in enumerate(bars):
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.015,
                f"e={edges[idx]}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    ax2.set_xticks(base, [f"h={h}" for h in solar_horizons])
    ax2.set_ylabel("abs-test skill")
    ax2.set_title("Solar positive control")
    ax2.legend(frameon=False, ncols=3, loc="upper center")
    ax2.set_ylim(0.0, 0.85)
    ax2.text(0.02, -0.18, "bar height = skill, label e = GHI edges", transform=ax2.transAxes, fontsize=8, color="gray")

    fig.suptitle("Horizon-dependent identifiability: wind boundary and solar positive control", fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def render_s2_summary(case4_detail_csv: Path, case4_summary_csv: Path, out_path: Path) -> None:
    case4_detail = sorted(_read_csv_rows(case4_detail_csv), key=lambda row: int(row["seed"]))
    case4_summary = _read_csv_rows(case4_summary_csv)
    case4_lag_share = _find_metric(case4_summary, "lag_edge_share")
    case4_final_rmse = _find_metric(case4_summary, "final_test_rmse")

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(14.4, 4.1), gridspec_kw={"width_ratios": [1.0, 1.0, 1.0]})

    seeds = np.arange(1, 6)
    for idx, seed in enumerate(seeds):
        ax1.plot(
            [0, 1],
            [CASE3_UNBLOCKED_EDGES[idx], CASE3_BLOCKED_EDGES[idx]],
            marker="o",
            linewidth=2.0,
            color="#4C72B0" if CASE3_BLOCKED_EDGES[idx] > CASE3_UNBLOCKED_EDGES[idx] else "#999999",
        )
        ax1.text(-0.03, CASE3_UNBLOCKED_EDGES[idx], str(CASE3_UNBLOCKED_EDGES[idx]), ha="right", va="center", fontsize=8)
        ax1.text(1.03, CASE3_BLOCKED_EDGES[idx], str(CASE3_BLOCKED_EDGES[idx]), ha="left", va="center", fontsize=8)
    ax1.set_xlim(-0.2, 1.2)
    ax1.set_xticks([0, 1], ["Case 3\nunblocked", "Case 3\nblocked"])
    ax1.set_ylabel("wind_speed active edges")
    ax1.set_title("Seed-level paired edge counts")
    ax1.grid(axis="y", alpha=0.2)

    for row in case4_detail:
        seed = int(row["seed"])
        unblocked = float(row["unblocked_lag_edge_share"])
        blocked = float(row["blocked_lag_edge_share"])
        ax2.plot(
            [0, 1],
            [unblocked, blocked],
            marker="o",
            linewidth=2.0,
            color="#55A868" if blocked < unblocked else "#999999",
        )
        ax2.text(-0.04, unblocked, f"{unblocked:.2f}", ha="right", va="center", fontsize=8)
        ax2.text(1.04, blocked, f"{blocked:.2f}", ha="left", va="center", fontsize=8)
        ax2.text(0.5, max(unblocked, blocked) + 0.03, f"s{seed}", ha="center", va="bottom", fontsize=7, color="gray")
    ax2.set_xlim(-0.2, 1.2)
    ax2.set_xticks([0, 1], ["Case 4\nunblocked", "Case 4\nblocked"])
    ax2.set_ylabel("lag edge share")
    ax2.set_ylim(-0.02, 0.42)
    ax2.set_title("Matched direct-task lag suppression")
    ax2.grid(axis="y", alpha=0.2)
    ax2.text(
        0.02,
        -0.22,
        r"$\Delta$lag-share"
        + f" = {float(case4_lag_share['delta_mean']):+.3f}\n95% CI [{float(case4_lag_share['ci95_low']):+.3f}, {float(case4_lag_share['ci95_high']):+.3f}]",
        transform=ax2.transAxes,
        fontsize=8,
        color="gray",
    )

    for row in case4_detail:
        seed = int(row["seed"])
        unblocked = float(row["unblocked_final_test_rmse"])
        blocked = float(row["blocked_final_test_rmse"])
        ax3.plot(
            [0, 1],
            [unblocked, blocked],
            marker="o",
            linewidth=2.0,
            color="#C44E52" if blocked > unblocked else "#999999",
        )
        ax3.text(-0.04, unblocked, f"{unblocked:.0f}", ha="right", va="center", fontsize=8)
        ax3.text(1.04, blocked, f"{blocked:.0f}", ha="left", va="center", fontsize=8)
        ax3.text(0.5, max(unblocked, blocked) + 45, f"s{seed}", ha="center", va="bottom", fontsize=7, color="gray")
    ax3.set_xlim(-0.2, 1.2)
    ax3.set_xticks([0, 1], ["Case 4\nunblocked", "Case 4\nblocked"])
    ax3.set_ylabel("final test RMSE")
    ax3.set_title("Matched direct-task accuracy cost")
    ax3.grid(axis="y", alpha=0.2)
    ax3.text(
        0.02,
        -0.22,
        r"$\Delta$RMSE"
        + f" = {float(case4_final_rmse['delta_mean']):+.1f}\n95% CI [{float(case4_final_rmse['ci95_low']):+.1f}, {float(case4_final_rmse['ci95_high']):+.1f}]",
        transform=ax3.transAxes,
        fontsize=8,
        color="gray",
    )

    fig.suptitle("S2 blocking evidence: focused-wind edge recovery and direct-task lag suppression", fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description="Render paper evidence figures for protocol and mechanism sections.")
    ap.add_argument("--out-dir", default="doc/paper_assets/paper_delivery_20260306")
    ap.add_argument("--wind-csv", default="doc/paper_assets/paper_delivery_20260306/wind_ablation_summary_20260306.csv")
    ap.add_argument("--solar-csv", default="doc/paper_assets/paper_delivery_20260306/solar_ablation_summary_20260304.csv")
    ap.add_argument(
        "--case4-detail-csv",
        default="doc/paper_assets/paper_delivery_20260306/case4_matched_blocking_seed_detail_20260417.csv",
    )
    ap.add_argument(
        "--case4-summary-csv",
        default="doc/paper_assets/paper_delivery_20260306/case4_matched_blocking_summary_20260417.csv",
    )
    args = ap.parse_args()

    _apply_style()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    render_direct_collapse(out_dir / "direct_symbolic_collapse_20260417.png")
    render_horizon_patterns(Path(args.wind_csv), Path(args.solar_csv), out_dir / "wind_solar_horizon_20260417.png")
    render_s2_summary(Path(args.case4_detail_csv), Path(args.case4_summary_csv), out_dir / "s2_blocking_summary_20260417.png")


if __name__ == "__main__":
    main()
