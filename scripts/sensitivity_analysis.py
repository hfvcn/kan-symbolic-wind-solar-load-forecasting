#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sympy as sp

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.kan_sr.sensitivity import compute_partials, summarize_derivative


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=np.float64).reshape(-1)
    y_pred = np.asarray(y_pred, dtype=np.float64).reshape(-1)
    mask = np.isfinite(y_true) & np.isfinite(y_pred)
    if not np.any(mask):
        return float("nan")
    return float(np.sqrt(np.mean((y_true[mask] - y_pred[mask]) ** 2)))


def _clip_for_plot(values: np.ndarray, *, lo_q: float = 0.01, hi_q: float = 0.99) -> np.ndarray:
    v = np.asarray(values, dtype=np.float64)
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return v
    lo = float(np.quantile(v, lo_q))
    hi = float(np.quantile(v, hi_q))
    if not np.isfinite(lo) or not np.isfinite(hi) or lo >= hi:
        return v
    return np.clip(v, lo, hi)


def main() -> None:
    ap = argparse.ArgumentParser(description="Sensitivity analysis on extracted symbolic formula (Phase 7).")
    ap.add_argument("--symbolic-run", required=True, help="Path to synced symbolic run directory (runs/<id>).")
    ap.add_argument("--data-run", default=None, help="Path to synced data pipeline run directory (runs/<data_id>). If omitted, inferred from symbolic payload.")
    ap.add_argument("--out-dir", default="doc/paper_assets", help="Output directory.")
    ap.add_argument("--vars", default="temp_2m_c,wind_speed_10m_m_s,ghi_w_m2", help="Comma-separated variable names to differentiate.")
    ap.add_argument("--max-samples", type=int, default=20000, help="Max test rows to use for plots (subsamples deterministically if larger).")
    args = ap.parse_args()

    sym_run = Path(args.symbolic_run)
    print(
        f"[sensitivity] start run={sym_run} out_dir={args.out_dir} vars={args.vars} max_samples={args.max_samples}",
        flush=True,
    )
    payload = json.loads((sym_run / "payload.json").read_text())
    feature_cols = payload.get("feature_cols")
    if not feature_cols:
        raise ValueError("symbolic payload missing feature_cols")

    data_run_id = payload["data_run_id"]
    data_timestamp = payload["data_timestamp"]
    data_run = Path(args.data_run) if args.data_run else (sym_run.parent / data_run_id)
    processed_dir = data_run / "processed"

    from src.data.split import load_splits_from_parquet

    _train_df, _val_df, test_df = load_splits_from_parquet(processed_dir, timestamp=data_timestamp)

    target_col = str(payload.get("target_col", "load"))
    if target_col not in test_df.columns:
        raise ValueError(f"target_col not found in test split: {target_col}")

    expr_str = (sym_run / "artifacts" / "formula.sympy.txt").read_text()
    locals_map = {name: sp.Symbol(name, real=True) for name in feature_cols}
    expr = sp.sympify(expr_str, locals=locals_map)

    # Choose the correct input space for evaluating the extracted formula.
    # When `build_symbolic_formula(..., input_normalizer=...)` was used during extraction,
    # the saved SymPy expression expects ORIGINAL-SCALE features, not z-scored features.
    # For robustness (e.g., older runs), we auto-select the space by checking RMSE.
    y_true = test_df[target_col].to_numpy(dtype=np.float64).reshape(-1)
    input_df = test_df[feature_cols]
    chosen_space = "normalized"
    rmse_norm = float("nan")
    rmse_orig = float("nan")
    try:
        from src.data.split import inverse_transform

        scaler_path = (data_run / "artifacts" / "scaler_params.json")
        if scaler_path.exists():
            scaler_params = json.loads(scaler_path.read_text())
            test_x_orig = inverse_transform(test_df[feature_cols], scaler_params)
            # Compare on a small deterministic subset for speed.
            n = len(test_df)
            idx = np.arange(n)
            if n > 5000:
                idx = idx[:5000]
            f_expr = sp.lambdify(feature_cols, expr, modules="numpy")
            Xn = test_df[feature_cols].to_numpy(dtype=np.float64)
            Xo = test_x_orig.to_numpy(dtype=np.float64)
            args_n = [Xn[idx, i] for i in range(Xn.shape[1])]
            args_o = [Xo[idx, i] for i in range(Xo.shape[1])]
            pred_n = np.asarray(f_expr(*args_n), dtype=np.float64).reshape(-1)
            pred_o = np.asarray(f_expr(*args_o), dtype=np.float64).reshape(-1)
            rmse_norm = _rmse(y_true[idx], pred_n)
            rmse_orig = _rmse(y_true[idx], pred_o)
            if np.isfinite(rmse_orig) and (not np.isfinite(rmse_norm) or rmse_orig <= rmse_norm):
                input_df = test_x_orig
                chosen_space = "original"
    except Exception:
        pass
    print(f"[sensitivity] chosen_input_space={chosen_space} rmse_norm={rmse_norm:.6g} rmse_orig={rmse_orig:.6g}", flush=True)

    var_names = [v.strip() for v in args.vars.split(",") if v.strip()]
    vars_ = [locals_map[v] for v in var_names if v in locals_map]
    print(f"[sensitivity] computing_partials n_vars={len(vars_)}", flush=True)
    partials = compute_partials(expr, vars_)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Persist which space we used (important for interpretability in the thesis).
    (out_dir / f"sensitivity_meta_{sym_run.name}.json").write_text(
        json.dumps(
            {"symbolic_run": sym_run.name, "data_run": data_run.name, "chosen_input_space": chosen_space, "rmse_normalized": rmse_norm, "rmse_original": rmse_orig},
            indent=2,
        )
    )

    rows = []
    if args.max_samples is not None and len(input_df) > int(args.max_samples):
        input_df = input_df.iloc[: int(args.max_samples)].copy()
    for name, dexpr in partials.items():
        print(f"[sensitivity] var={name} computing", flush=True)
        f = sp.lambdify(feature_cols, dexpr, modules="numpy")
        X = input_df[feature_cols].to_numpy(dtype=np.float64)
        args_arr = [X[:, i] for i in range(X.shape[1])]
        vals = np.asarray(f(*args_arr), dtype=np.float64).reshape(-1)
        # Some derivatives are constant; lambdify may return a scalar. Broadcast to row count.
        if vals.shape[0] == 1 and X.shape[0] > 1:
            vals = np.full((X.shape[0],), float(vals[0]), dtype=np.float64)
        summ = summarize_derivative(vals, var=name)
        rows.append(summ.as_dict())

        # histogram
        v_plot = _clip_for_plot(vals)
        if len(v_plot) > 0:
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.hist(v_plot, bins=60, alpha=0.85)
            ax.set_title(f"Partial derivative distribution: dY/d{name}")
            ax.set_xlabel("value")
            ax.set_ylabel("count")
            fig.tight_layout()
            fig.savefig(out_dir / f"sensitivity_hist_{sym_run.name}_{name}.png", dpi=220)
            plt.close(fig)

        # boxplot
        if len(v_plot) > 0:
            fig, ax = plt.subplots(figsize=(6, 2))
            ax.boxplot(v_plot, vert=False, showfliers=False)
            ax.set_title(f"Partial derivative boxplot: dY/d{name}")
            ax.set_xlabel("value")
            fig.tight_layout()
            fig.savefig(out_dir / f"sensitivity_box_{sym_run.name}_{name}.png", dpi=220)
            plt.close(fig)

        # scatter vs variable (subsample for readability)
        if name in input_df.columns:
            x = input_df[name].to_numpy(dtype=np.float64).reshape(-1)
            m = np.isfinite(x) & np.isfinite(vals)
            if np.any(m):
                x_m = x[m]
                v_m = vals[m]
                if len(x_m) > 8000:
                    x_m = x_m[:8000]
                    v_m = v_m[:8000]
                fig, ax = plt.subplots(figsize=(6, 3))
                ax.scatter(x_m, v_m, s=4, alpha=0.25, linewidths=0)
                ax.set_title(f"Sensitivity scatter: dY/d{name} vs {name}")
                ax.set_xlabel(name)
                ax.set_ylabel(f"dY/d{name}")
                fig.tight_layout()
                fig.savefig(out_dir / f"sensitivity_scatter_{sym_run.name}_{name}.png", dpi=220)
                plt.close(fig)

    pd.DataFrame(rows).to_csv(out_dir / f"sensitivity_summary_{sym_run.name}.csv", index=False)


if __name__ == "__main__":
    main()
