"""Generate all thesis figures for KAN symbolic identifiability paper."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# ── Style Setup ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.size": 11,
    "font.family": "serif",
    "font.serif": ["Times New Roman", "SimSong", "DejaVu Serif"],
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.08,
    "axes.grid": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "text.usetex": False,
    "mathtext.fontset": "stix",
})

# Use STHeiti for Chinese labels on macOS
ZH_FONT = matplotlib.font_manager.FontProperties(family="STHeiti")

OUT = "doc/paper_assets/thesis_figures"
os.makedirs(OUT, exist_ok=True)

C = plt.cm.tab10.colors  # color palette


def savefig(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(f"{OUT}/{name}.{ext}")
    plt.close(fig)
    print(f"  ✓ {name}")


# ══════════════════════════════════════════════════════════════════════════════
# Fig 7 — HIGHEST PRIORITY: Direct net_load VER blocking comparison
# ══════════════════════════════════════════════════════════════════════════════
def fig7_direct_blocking():
    fig, ax = plt.subplots(figsize=(5, 3.8))

    conditions = ["Unblocked\n(all lags)", "Blocked\n(load lag only)"]
    ver_vals = [0.0, 0.80]
    ci_lo = [0, 0.40]
    ci_hi = [0, 1.00]
    yerr = [[v - lo for v, lo in zip(ver_vals, ci_lo)],
            [hi - v for v, hi in zip(ver_vals, ci_hi)]]

    colors = [C[3], C[0]]  # red-ish, blue-ish
    bars = ax.bar(conditions, ver_vals, width=0.5, color=colors,
                  edgecolor="black", linewidth=0.8, alpha=0.85,
                  yerr=yerr, capsize=6, error_kw={"linewidth": 1.5})

    # Annotations
    ax.text(0, 0.02, "0/9", ha="center", va="bottom", fontsize=14, fontweight="bold", color="white")
    ax.text(1, ver_vals[1] + 0.06, "4/5", ha="center", va="bottom", fontsize=14, fontweight="bold")

    # ΔVER annotation with arrow
    ax.annotate("", xy=(1, 0.80), xytext=(0, 0.0),
                arrowprops=dict(arrowstyle="->", color=C[2], lw=2.5,
                               connectionstyle="arc3,rad=0.3"))
    ax.text(0.5, 0.50, "ΔVER = +0.80\n95% CI: [0.40, 1.00]",
            ha="center", va="center", fontsize=10, fontweight="bold",
            color=C[2], bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=C[2], alpha=0.9))

    ax.set_ylabel("VER (Variable Entry Rate)", fontsize=12)
    ax.set_ylim(0, 1.15)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])

    # Chinese subtitle
    ax.text(0.5, -0.18, "直接净负荷任务：移除风/光滞后特征后物理变量重新进入模型",
            ha="center", va="top", transform=ax.transAxes, fontsize=9,
            fontproperties=ZH_FONT, style="italic", color="gray")

    savefig(fig, "fig7_direct_blocking_ver")


# ══════════════════════════════════════════════════════════════════════════════
# Fig 6 — Case 3: Focused wind task blocking
# ══════════════════════════════════════════════════════════════════════════════
def fig6_wind_blocking():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.8), gridspec_kw={"width_ratios": [1, 1]})

    # Panel A: VER comparison
    conditions = ["Unblocked\n(wind lags)", "Blocked\n(no lags)"]
    ver_vals = [0.40, 1.00]
    colors = [C[3], C[0]]
    bars = ax1.bar(conditions, ver_vals, width=0.5, color=colors,
                   edgecolor="black", linewidth=0.8, alpha=0.85)
    ax1.text(0, 0.42, "2/5", ha="center", va="bottom", fontsize=13, fontweight="bold")
    ax1.text(1, 1.02, "5/5", ha="center", va="bottom", fontsize=13, fontweight="bold")

    ax1.annotate("", xy=(1, 1.0), xytext=(0, 0.40),
                 arrowprops=dict(arrowstyle="->", color=C[2], lw=2, connectionstyle="arc3,rad=0.3"))
    ax1.text(0.5, 0.78, "ΔVER = +0.60\nCI: [0.20, 1.00]",
             ha="center", fontsize=9, fontweight="bold", color=C[2],
             bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=C[2], alpha=0.9))

    ax1.set_ylabel("VER (Variable Entry Rate)")
    ax1.set_ylim(0, 1.2)
    ax1.set_title("(a) VER", fontsize=12)

    # Panel B: Edge count comparison (per seed)
    seeds = [1, 2, 3, 4, 5]
    edges_ub = [0, 8, 0, 0, 1]
    edges_bl = [19, 19, 8, 15, 1]

    x = np.arange(len(seeds))
    w = 0.35
    ax2.bar(x - w/2, edges_ub, w, label="Unblocked", color=C[3], edgecolor="black", linewidth=0.6, alpha=0.85)
    ax2.bar(x + w/2, edges_bl, w, label="Blocked", color=C[0], edgecolor="black", linewidth=0.6, alpha=0.85)
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"Seed {s}" for s in seeds])
    ax2.set_ylabel("Wind Speed Active Edges")
    ax2.legend(frameon=False, loc="upper right")
    ax2.set_title("(b) Active Edge Count", fontsize=12)

    fig.suptitle("", y=1.0)
    plt.tight_layout()
    savefig(fig, "fig6_wind_blocking")


# ══════════════════════════════════════════════════════════════════════════════
# Fig 5 — Wind edge_count vs horizon (non-monotonic)
# ══════════════════════════════════════════════════════════════════════════════
def fig5_wind_horizon():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.5))

    horizons = [6, 72, 144, 288, 576]
    h_labels = ["h=6\n(30min)", "h=72\n(6h)", "h=144\n(12h)", "h=288\n(24h)", "h=576\n(48h)"]
    wind_edges = [11, 0, 9, 0, 0]
    skill = [0.128, 0.588, 0.354, 0.193, 0.203]

    # Panel A: Edge count
    ax1.plot(range(len(horizons)), wind_edges, "o-", color=C[0], linewidth=2, markersize=8, zorder=3)
    ax1.fill_between(range(len(horizons)), wind_edges, alpha=0.15, color=C[0])
    ax1.set_xticks(range(len(horizons)))
    ax1.set_xticklabels(h_labels, fontsize=9)
    ax1.set_ylabel("wind_speed Active Edges")
    ax1.set_title("(a) Wind Speed Edge Count", fontsize=12)

    # Highlight non-monotonic peak
    ax1.annotate("Peak: h=144", xy=(2, 9), xytext=(3.2, 10),
                 arrowprops=dict(arrowstyle="->", color=C[2], lw=1.5),
                 fontsize=9, color=C[2], fontweight="bold")

    # Panel B: Skill
    ax2.plot(range(len(horizons)), skill, "s-", color=C[1], linewidth=2, markersize=8, zorder=3)
    ax2.fill_between(range(len(horizons)), skill, alpha=0.15, color=C[1])
    ax2.set_xticks(range(len(horizons)))
    ax2.set_xticklabels(h_labels, fontsize=9)
    ax2.set_ylabel("Absolute Skill Score")
    ax2.set_title("(b) Prediction Skill", fontsize=12)

    plt.tight_layout()
    savefig(fig, "fig5_wind_horizon")


# ══════════════════════════════════════════════════════════════════════════════
# Fig 8 — S3 composite prediction time series
# ══════════════════════════════════════════════════════════════════════════════
def fig8_s3_timeseries():
    df = pd.read_parquet("runs/paperref_20260306_121725_v2__s3_combo_net_load/artifacts/predictions_test.parquet")

    # Select a representative 3-day window
    n = len(df)
    # Find a window with good variability (around index 2000-2800 = ~3 days)
    start, end = 2000, 2864  # 3 days at 5-min = 864 points
    if end > n:
        start, end = 0, min(864, n)
    window = df.iloc[start:end]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5.5), height_ratios=[3, 1], sharex=True)

    x = range(len(window))
    hours = np.array(x) * 5 / 60  # convert to hours

    ax1.plot(hours, window["y_true"].values, color="black", linewidth=1, label="Actual", alpha=0.8)
    ax1.plot(hours, window["y_pred"].values, color=C[0], linewidth=1, label="S3 Composite", alpha=0.8)
    ax1.set_ylabel("Net Load (kW)")
    ax1.legend(frameon=False, loc="upper right")
    ax1.text(0.01, 0.95, f"RMSE = 1254.6 kW  |  Skill = 0.515",
             transform=ax1.transAxes, fontsize=9, va="top",
             bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="orange", alpha=0.8))

    # Residuals
    ax2.fill_between(hours, window["residual"].values, color=C[3], alpha=0.4)
    ax2.axhline(0, color="black", linewidth=0.5, linestyle="--")
    ax2.set_ylabel("Residual (kW)")
    ax2.set_xlabel("Time (hours)")

    plt.tight_layout()
    savefig(fig, "fig8_s3_composite_timeseries")


# ══════════════════════════════════════════════════════════════════════════════
# Fig 5b — Combined S2 Mechanism Summary (2-panel: Case 3 + Case 4)
# ══════════════════════════════════════════════════════════════════════════════
def fig_s2_summary():
    """Combined summary figure for the S2 blocking mechanism test."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))

    # Panel A: Case 3 (focused wind)
    x = [0, 1]
    ver = [0.40, 1.00]
    colors = [C[3], C[0]]
    ax1.bar(x, ver, width=0.5, color=colors, edgecolor="black", linewidth=0.8, alpha=0.85)
    ax1.text(0, 0.42, "2/5", ha="center", fontsize=13, fontweight="bold")
    ax1.text(1, 1.02, "5/5", ha="center", fontsize=13, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(["With\nwind lags", "Without\nwind lags"])
    ax1.set_ylabel("VER (Variable Entry Rate)")
    ax1.set_ylim(0, 1.25)
    ax1.set_title("(a) Focused Wind Task", fontsize=12, fontweight="bold")
    ax1.text(0.5, 0.70, "ΔVER=+0.60\np<0.05", ha="center", transform=ax1.transAxes,
             fontsize=10, color=C[2], fontweight="bold",
             bbox=dict(boxstyle="round", fc="white", ec=C[2], alpha=0.9))

    # Panel B: Case 4 (direct net_load)
    ver2 = [0.00, 0.80]
    ax2.bar(x, ver2, width=0.5, color=colors, edgecolor="black", linewidth=0.8, alpha=0.85)
    ax2.text(0, 0.02, "0/9", ha="center", fontsize=13, fontweight="bold", color="white")
    ax2.text(1, 0.82, "4/5", ha="center", fontsize=13, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(["With\nall lags", "Without\nwind/solar lags"])
    ax2.set_ylim(0, 1.25)
    ax2.set_title("(b) Direct Net Load Task", fontsize=12, fontweight="bold")
    ax2.text(0.5, 0.70, "ΔVER=+0.80\np<0.05", ha="center", transform=ax2.transAxes,
             fontsize=10, color=C[2], fontweight="bold",
             bbox=dict(boxstyle="round", fc="white", ec=C[2], alpha=0.9))

    plt.tight_layout()
    savefig(fig, "fig_s2_mechanism_summary")


# ══════════════════════════════════════════════════════════════════════════════
# Fig 9 — S3 sub-task identifiability heatmap
# ══════════════════════════════════════════════════════════════════════════════
def fig9_s3_identifiability():
    fig, ax = plt.subplots(figsize=(6, 3.5))

    # Data: edge_count per variable per sub-task
    subtasks = ["Load", "Wind", "Solar"]
    variables = ["temp/HDD", "wind_speed", "wind³", "wind_hub", "GHI", "GHI_day", "solar_alt"]

    data = np.array([
        [2, 0, 0, 0, 0, 0, 0],  # Load
        [0, 3, 3, 4, 0, 0, 0],  # Wind
        [1, 0, 0, 0, 2, 2, 2],  # Solar
    ], dtype=float)

    im = ax.imshow(data, cmap="YlOrRd", aspect="auto", vmin=0, vmax=5)
    ax.set_xticks(range(len(variables)))
    ax.set_xticklabels(variables, rotation=30, ha="right", fontsize=9)
    ax.set_yticks(range(len(subtasks)))
    ax.set_yticklabels(subtasks)

    # Add text annotations
    for i in range(len(subtasks)):
        for j in range(len(variables)):
            val = int(data[i, j])
            color = "white" if val >= 3 else "black"
            ax.text(j, i, str(val), ha="center", va="center", fontsize=11,
                    fontweight="bold" if val > 0 else "normal", color=color)

    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Active Edge Count", fontsize=10)

    plt.tight_layout()
    savefig(fig, "fig9_s3_identifiability_heatmap")


# ══════════════════════════════════════════════════════════════════════════════
# Fig 3 — Accuracy comparison bar chart
# ══════════════════════════════════════════════════════════════════════════════
def fig3_accuracy():
    fig, ax = plt.subplots(figsize=(5.5, 3.5))

    methods = ["Persistence", "PySR", "MLP\n(matched)", "KAN\n(teacher)", "S3\nComposite"]
    skill = [0.0, 0.20, 0.430, 0.453, 0.515]
    rmse = [2585.66, 2070, 1474.38, 1413.51, 1254.62]

    colors_bar = [C[7], C[4], C[1], C[0], C[2]]
    bars = ax.bar(methods, skill, width=0.6, color=colors_bar, edgecolor="black", linewidth=0.6, alpha=0.85)

    for bar, s, r in zip(bars, skill, rmse):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.012,
                f"{s:.3f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
                f"RMSE\n{r:.0f}", ha="center", va="center", fontsize=7, color="white")

    ax.set_ylabel("Skill Score")
    ax.set_ylim(0, 0.55)

    # Significance bracket for KAN vs MLP
    y_brack = 0.47
    ax.plot([2, 2, 3, 3], [y_brack-0.01, y_brack, y_brack, y_brack-0.01],
            color="black", linewidth=1)
    ax.text(2.5, y_brack + 0.005, "p=0.0005", ha="center", fontsize=8)

    plt.tight_layout()
    savefig(fig, "fig3_accuracy_comparison")


# ══════════════════════════════════════════════════════════════════════════════
# Fig 2 — Formula collapse illustration (text-based)
# ══════════════════════════════════════════════════════════════════════════════
def fig2_collapse():
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.axis("off")

    # Show the collapse: 9 configs → same formula
    ax.text(0.5, 0.92, "9 Symbolic Extraction Configurations",
            ha="center", fontsize=13, fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.78, "(3 libraries × 3 R² thresholds)",
            ha="center", fontsize=10, color="gray", transform=ax.transAxes)

    # Arrow
    ax.annotate("", xy=(0.5, 0.55), xytext=(0.5, 0.70),
                arrowprops=dict(arrowstyle="-|>", color="red", lw=3),
                transform=ax.transAxes)
    ax.text(0.5, 0.62, "ALL collapse to", ha="center", fontsize=10,
            color="red", fontweight="bold", transform=ax.transAxes)

    # Collapsed formula
    ax.text(0.5, 0.38, r"$\hat{y} = 0.000729 \times \mathrm{load} - 3.007$",
            ha="center", fontsize=16, fontweight="bold", transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.4", fc="#fff3e0", ec="red", linewidth=2))

    ax.text(0.5, 0.15, "VER(wind_speed) = 0/9    VER(GHI) = 0/9    VER(temp) = 0/9",
            ha="center", fontsize=10, color=C[3], transform=ax.transAxes)
    ax.text(0.5, 0.03, "All physical meteorological variables pruned to zero",
            ha="center", fontsize=9, color="gray", style="italic", transform=ax.transAxes)

    savefig(fig, "fig2_formula_collapse")


# ══════════════════════════════════════════════════════════════════════════════
# Run all
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating thesis figures...")
    fig7_direct_blocking()
    fig6_wind_blocking()
    fig5_wind_horizon()
    fig8_s3_timeseries()
    fig_s2_summary()
    fig9_s3_identifiability()
    fig3_accuracy()
    fig2_collapse()
    print(f"\nAll figures saved to {OUT}/")
    print(f"Files: {sorted(os.listdir(OUT))}")
