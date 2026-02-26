#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import NormalDist

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _apply_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "font.size": 11,
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "legend.fontsize": 10,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def _plot_timeseries(pred_df: pd.DataFrame, out_path: Path, *, title: str) -> None:
    df = pred_df.dropna(subset=["y_true", "y_pred"]).copy()
    if len(df) == 0:
        return
    # For readability, plot a window (first 2 days) if index is datetime.
    if isinstance(df.index, pd.DatetimeIndex):
        start = df.index.min()
        end = start + pd.Timedelta(days=2)
        df = df.loc[(df.index >= start) & (df.index <= end)]

    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(df.index, df["y_true"], label="true", linewidth=1.2)
    ax.plot(df.index, df["y_pred"], label="pred", linewidth=1.2, alpha=0.8)
    ax.set_title(title)
    ax.set_xlabel("time")
    ax.set_ylabel("value")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def _plot_residual_hist(pred_df: pd.DataFrame, out_path: Path, *, title: str) -> None:
    df = pred_df.dropna(subset=["residual"]).copy()
    if len(df) == 0:
        return
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.hist(df["residual"].to_numpy(), bins=60, alpha=0.85)
    ax.set_title(title)
    ax.set_xlabel("residual")
    ax.set_ylabel("count")
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def _plot_residual_box(pred_df: pd.DataFrame, out_path: Path, *, title: str) -> None:
    df = pred_df.dropna(subset=["residual"]).copy()
    if len(df) == 0:
        return
    r = df["residual"].to_numpy(dtype=np.float64)
    r = r[np.isfinite(r)]
    if len(r) == 0:
        return
    fig, ax = plt.subplots(figsize=(6, 2))
    ax.boxplot(r, vert=False, showfliers=False)
    ax.set_title(title)
    ax.set_xlabel("residual")
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def _plot_residual_qq(pred_df: pd.DataFrame, out_path: Path, *, title: str) -> None:
    df = pred_df.dropna(subset=["residual"]).copy()
    if len(df) == 0:
        return
    r = df["residual"].to_numpy(dtype=np.float64)
    r = r[np.isfinite(r)]
    if len(r) < 50:
        return

    r_mean = float(np.mean(r))
    r_std = float(np.std(r))
    if not np.isfinite(r_std) or r_std <= 1e-12:
        return
    z = (r - r_mean) / r_std
    z = np.sort(z)
    n = len(z)

    nd = NormalDist()
    p = (np.arange(1, n + 1) - 0.5) / n
    q = np.asarray([nd.inv_cdf(float(pi)) for pi in p], dtype=np.float64)

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.scatter(q, z, s=6, alpha=0.5, linewidths=0)
    lo = float(min(q.min(), z.min()))
    hi = float(max(q.max(), z.max()))
    ax.plot([lo, hi], [lo, hi], color="black", linewidth=1.0, alpha=0.7)
    ax.set_title(title)
    ax.set_xlabel("Normal quantiles")
    ax.set_ylabel("Residual quantiles (standardized)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def _plot_seasonal_rmse(pred_df: pd.DataFrame, out_path: Path, *, title: str) -> None:
    if not isinstance(pred_df.index, pd.DatetimeIndex):
        return
    df = pred_df.dropna(subset=["y_true", "y_pred"]).copy()
    if len(df) == 0:
        return

    def season(month: int) -> str:
        if month in (12, 1, 2):
            return "DJF"
        if month in (3, 4, 5):
            return "MAM"
        if month in (6, 7, 8):
            return "JJA"
        return "SON"

    df["season"] = [season(int(m)) for m in df.index.month]
    rows = []
    for s, g in df.groupby("season"):
        y_true = g["y_true"].to_numpy(dtype=np.float64)
        y_pred = g["y_pred"].to_numpy(dtype=np.float64)
        rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
        rows.append((s, rmse))
    if not rows:
        return
    order = ["DJF", "MAM", "JJA", "SON"]
    rows = sorted(rows, key=lambda t: order.index(t[0]) if t[0] in order else 99)
    seasons = [r[0] for r in rows]
    rmses = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(seasons, rmses, color="#4C72B0")
    ax.set_title(title)
    ax.set_xlabel("season")
    ax.set_ylabel("RMSE")
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def _plot_feature_importance(run_dir: Path, out_path: Path) -> None:
    imp = run_dir / "artifacts" / "feature_importance.csv"
    if not imp.exists():
        return
    df = pd.read_csv(imp).head(25)
    if len(df) == 0:
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(df["feature"][::-1], df["active_edges"][::-1])
    ax.set_title("KAN input feature importance (active edges)")
    ax.set_xlabel("active_edges")
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def _render_formula(run_dir: Path, out_path: Path) -> None:
    tex = run_dir / "artifacts" / "formula.tex"
    if not tex.exists():
        return
    latex = tex.read_text()
    fig, ax = plt.subplots(figsize=(10, 2))
    ax.axis("off")
    # Matplotlib mathtext expects a single `$...$` wrapper (not `$$...$$`).
    ax.text(0.01, 0.5, f"${latex}$", fontsize=12, va="center")
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def _plot_kan_topology(run_dir: Path, out_dir: Path) -> None:
    ckpt = run_dir / "checkpoint" / "model.pt"
    if not ckpt.exists():
        return

    import torch
    from kan import KAN

    try:
        ck = torch.load(ckpt, map_location="cpu", weights_only=False)
    except TypeError:
        ck = torch.load(ckpt, map_location="cpu")
    payload = ck.get("payload", {})
    cfg = payload.get("cfg", {})
    feature_cols = ck.get("feature_cols") or payload.get("feature_cols")
    if not feature_cols:
        return

    in_dim = len(feature_cols)
    hidden_width = int(cfg.get("hidden_width", 10))
    hidden_mult = int(cfg.get("hidden_mult", 0))
    mult_arity = int(cfg.get("mult_arity", 2))
    grid = int(cfg.get("grid", 5))
    k = int(cfg.get("k", 3))
    grid_range_min = float(cfg.get("grid_range_min", -5.0))
    grid_range_max = float(cfg.get("grid_range_max", 5.0))
    target_col = str(cfg.get("target_col", "y"))

    model_width = ck.get("model_width") or payload.get("model_width")
    if model_width:
        width = [[int(a), int(b)] for a, b in model_width]
    else:
        sd = ck.get("model_state", {})
        inferred_hidden = None
        if "node_bias_0" in sd:
            inferred_hidden = int(sd["node_bias_0"].shape[0])
        elif "act_fun.0.mask" in sd:
            inferred_hidden = int(sd["act_fun.0.mask"].shape[1])
        width = [[in_dim, 0], [int(inferred_hidden or hidden_width), int(hidden_mult)], [1, 0]]

    model = KAN(
        width=width,
        grid=grid,
        k=k,
        mult_arity=mult_arity,
        grid_range=[grid_range_min, grid_range_max],
        seed=int(cfg.get("seed", 1)),
        auto_save=False,
        device="cpu",
    )
    model.load_state_dict(ck["model_state"], strict=True)

    out_dir.mkdir(parents=True, exist_ok=True)
    # KAN.plot() expects the model to have executed at least one forward pass so
    # internal activations are populated. When loading from checkpoint, we need
    # to "warm up" with some sample inputs.
    x_sample = None
    data_run_id = payload.get("data_run_id")
    data_timestamp = payload.get("data_timestamp")
    if data_run_id and data_timestamp:
        processed_dir = run_dir.parent / str(data_run_id) / "processed"
        train_path = processed_dir / f"train_{data_timestamp}.parquet"
        if train_path.exists():
            try:
                train_df = pd.read_parquet(train_path)
                x_df = train_df[feature_cols].iloc[:2048].copy()
                x_sample = torch.tensor(x_df.to_numpy(dtype=np.float32), device="cpu")
            except Exception:
                x_sample = None

    if x_sample is None:
        rng = np.random.default_rng(1)
        x_sample = torch.tensor(rng.standard_normal((512, in_dim)).astype(np.float32), device="cpu")

    try:
        with torch.no_grad():
            _ = model(x_sample)
        model.plot(folder=str(out_dir), in_vars=feature_cols, out_vars=[target_col], title=f"KAN topology ({run_dir.name})")
        # MultKAN.plot() saves per-edge spline PNGs into `folder/`, but it does not
        # save the final topology diagram; it remains as the current matplotlib
        # figure. Save it explicitly for thesis usage.
        topo_path = out_dir / "topology.png"
        plt.gcf().savefig(topo_path, dpi=300, bbox_inches="tight")
        plt.close(plt.gcf())
    except Exception as e:
        print(f"[WARN] KAN plot failed for {run_dir}: {e}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate thesis-ready figures from synced run directories.")
    ap.add_argument("--run", action="append", required=True, help="Path to a synced run directory (repeatable).")
    ap.add_argument("--out-dir", default="doc/paper_assets/figures", help="Output directory for figures.")
    ap.add_argument("--with-kan-plot", action="store_true", help="If set, tries to load KAN checkpoint and call model.plot().")
    args = ap.parse_args()

    _apply_style()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for run_path_str in args.run:
        run_dir = Path(run_path_str)
        pred_path = run_dir / "artifacts" / "predictions_test.parquet"
        if pred_path.exists():
            pred_df = pd.read_parquet(pred_path)
            _plot_timeseries(pred_df, out_dir / f"timeseries_{run_dir.name}.png", title=f"{run_dir.name} prediction vs actual")
            _plot_residual_hist(pred_df, out_dir / f"residual_hist_{run_dir.name}.png", title=f"{run_dir.name} residual distribution")
            _plot_residual_box(pred_df, out_dir / f"residual_box_{run_dir.name}.png", title=f"{run_dir.name} residual boxplot")
            _plot_residual_qq(pred_df, out_dir / f"residual_qq_{run_dir.name}.png", title=f"{run_dir.name} residual QQ plot")
            _plot_seasonal_rmse(pred_df, out_dir / f"seasonal_rmse_{run_dir.name}.png", title=f"{run_dir.name} RMSE by season")

        _plot_feature_importance(run_dir, out_dir / f"feature_importance_{run_dir.name}.png")
        _render_formula(run_dir, out_dir / f"formula_{run_dir.name}.png")

        if args.with_kan_plot:
            _plot_kan_topology(run_dir, out_dir / f"kan_plot_{run_dir.name}")


if __name__ == "__main__":
    main()
