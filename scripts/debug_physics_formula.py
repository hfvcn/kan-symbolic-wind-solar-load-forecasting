"""
debug_physics_formula.py
========================
快速验证"物理因子入公式"：

  - Step 1: 用最新的 source_data_run_id 重新 derive 数据集（加入新物理特征 + 绝对值目标）
  - Step 2: 同时训练两个轻量 KAN：
      A) target = wind_h6   （绝对值水平预测）← 建议1
      B) target = delta_wind_h6 （原差分预测，对照组）
  - Step 3: 对两个模型提取符号公式，打印结果对比

用法：
    cd 
    python scripts/debug_physics_formula.py --source-run <source_data_run_id>

参数:
    --source-run   : 数据预处理的 run_id（含 scaler_params.json 和 processed/ 目录）
    --runs-root    : runs 目录（默认 ./runs）
    --max-rows     : 训练样本上限（默认 3000，快速验证）
    --device       : cpu / cuda
    --no-symbolic  : 跳过符号提取（只看 feature_importance）
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pandas as pd

from src.local.derive_dataset import DeriveDatasetConfig, derive_dataset_local
from src.local.kan_symbolic import SymbolicConfig, extract_symbolic_local
from src.local.kan_train import TrainConfig, train_kan_local


# ─── 快速调试参数（小模型） ────────────────────────────────────────
QUICK_TRAIN_CFG = TrainConfig(
    hidden_width=8,      # 小网络，快
    warmup_steps=100,
    sparsify_steps=300,
    refine_steps=100,
    sparsify_lamb=0.005,        # 稍微宽松一点，不要剪得太狠
    sparsify_lamb_l1=0.8,
    sparsify_lamb_entropy=1.5,
    target_pruned_ratio=0.6,    # 允许更多边保留
    max_rmse_degrade_ratio=1.2,
)

SYMBOLIC_CFG = SymbolicConfig(
    r2_threshold=0.95,   # 宽松阈值，让更多边能被拟合
    weight_simple=0.85,
    fix_below_threshold_to_zero=False,
    sample_rows=3000,
)


def _print_section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def _print_feature_importance(run_dir: Path, label: str) -> None:
    fi_path = run_dir / "artifacts" / "feature_importance.csv"
    if not fi_path.exists():
        print(f"  [{label}] feature_importance.csv not found")
        return
    df = pd.read_csv(fi_path)
    df = df.sort_values("active_ratio", ascending=False)
    print(f"\n  [{label}] Feature Importance (active edges ratio):")
    print(f"  {'Feature':<35} {'Active Edges':>12} {'Ratio':>8}")
    print(f"  {'-'*58}")
    for _, row in df.iterrows():
        marker = " ← 物理量!" if any(p in str(row["feature"]) for p in
                                    ["wind_speed", "ghi", "temp_2m", "hub_est", "temp_corr"]) else ""
        print(f"  {str(row['feature']):<35} {int(row['active_edges']):>12} {float(row['active_ratio']):>8.2f}{marker}")


def _print_formula(sym_run_dir: Path, label: str) -> None:
    formula_path = sym_run_dir / "artifacts" / "formula.sympy.txt"
    if not formula_path.exists():
        print(f"  [{label}] formula.sympy.txt not found")
        return
    formula = formula_path.read_text().strip()
    print(f"\n  [{label}] Symbolic Formula:")
    print(f"  {formula[:500]}{'...' if len(formula) > 500 else ''}")

    eval_path = sym_run_dir / "artifacts" / "formula_eval_test.json"
    if eval_path.exists():
        import json
        ev = json.loads(eval_path.read_text())
        print(f"\n  [{label}] Formula Eval: RMSE={ev.get('rmse', 'N/A'):.2f}  R²={ev.get('r2', 'N/A'):.4f}")


def main() -> None:
    p = argparse.ArgumentParser(description="Debug: 物理因子入公式实验")
    p.add_argument("--source-run", required=True, help="Source data run_id (含 scaler_params + processed/)")
    p.add_argument("--runs-root", default=str(REPO_ROOT / "runs"))
    p.add_argument("--max-rows", default=3000, type=int, help="训练样本上限（越小越快）")
    p.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    p.add_argument("--no-symbolic", action="store_true", help="跳过符号提取")
    p.add_argument("--horizon", default=6, type=int, help="预测步数（默认6）")
    p.add_argument("--skip-derive", default=None, metavar="DERIVED_RUN_ID",
                   help="跳过 derive 步骤，直接用已有的 derived run_id")
    args = p.parse_args()

    runs_root = Path(args.runs_root)
    h = args.horizon
    targets_to_test = [
        ("wind_absolute",  f"wind_h{h}",        "meteorology,solar,cyclic", "wind",       f"{6*2},{6*4}"),
        ("wind_delta",     f"delta_wind_h{h}",   "meteorology,solar,cyclic", "wind",       f"{6*2},{6*4}"),
        ("solar_absolute", f"solar_h{h}",        "meteorology,solar,cyclic", "solar",      f"{6*2},{6*4}"),
        ("net_absolute",   f"net_load_h{h}",     "meteorology,solar,cyclic", "load,wind,solar", f"{6*2},{6*4}"),
    ]

    # ── Step 1: Derive dataset ─────────────────────────────────────
    if args.skip_derive:
        derived_run_id = args.skip_derive
        _print_section(f"Step 1 SKIPPED — using derived run: {derived_run_id}")
    else:
        _print_section("Step 1: Derive dataset (with new physics features + absolute targets)")
        derive_cfg = DeriveDatasetConfig(
            horizon_steps=[h],
            add_physics_proxies=True,
            add_hub_wind=True,
            add_temp_ghi=True,
            add_absolute_targets=True,
        )
        derive_payload = derive_dataset_local(
            args.source_run,
            runs_root=runs_root,
            cfg=derive_cfg,
        )
        derived_run_id = derive_payload["run_id"]
        print(f"  Derived run_id: {derived_run_id}")
        print(f"  New features: {derive_payload['added_columns'].get('engineered_features', [])}")
        print(f"  Targets: {[t for t in derive_payload['added_columns'].get('targets', []) if 'h6' in t or 'net' in t]}")

    # ── Step 2 & 3: Train + Symbolic ──────────────────────────────
    results: list[dict] = []

    for kind, target_col, include_groups, lag_series, lag_steps in targets_to_test:
        _print_section(f"Step 2: KAN Train — [{kind}] target={target_col}")

        cfg = TrainConfig(
            target_col=target_col,
            hidden_width=QUICK_TRAIN_CFG.hidden_width,
            warmup_steps=QUICK_TRAIN_CFG.warmup_steps,
            sparsify_steps=QUICK_TRAIN_CFG.sparsify_steps,
            refine_steps=QUICK_TRAIN_CFG.refine_steps,
            sparsify_lamb=QUICK_TRAIN_CFG.sparsify_lamb,
            sparsify_lamb_l1=QUICK_TRAIN_CFG.sparsify_lamb_l1,
            sparsify_lamb_entropy=QUICK_TRAIN_CFG.sparsify_lamb_entropy,
            target_pruned_ratio=QUICK_TRAIN_CFG.target_pruned_ratio,
            max_rmse_degrade_ratio=QUICK_TRAIN_CFG.max_rmse_degrade_ratio,
        )

        try:
            train_result = train_kan_local(
                derived_run_id,
                runs_root=runs_root,
                device_name=args.device,
                kind=f"debug_physics_{kind}",
                cfg=cfg,
                include_base=False,
                include_groups=[g.strip() for g in include_groups.split(",")],
                lag_series=[s.strip() for s in lag_series.split(",")],
                lag_steps=[int(s) for s in lag_steps.split(",")],
                max_train_rows=args.max_rows,
                warmup_update_grid=False,
            )
            train_run_id = train_result["run_id"]
            train_run_dir = runs_root / train_run_id
            print(f"  Train complete: {train_run_id}")
            _print_feature_importance(train_run_dir, kind)

            sym_run_id = None
            if not args.no_symbolic:
                _print_section(f"Step 3: Symbolic Extraction — [{kind}]")
                sym_payload = extract_symbolic_local(
                    train_run_id,
                    runs_root=runs_root,
                    cfg=SYMBOLIC_CFG,
                )
                sym_run_id = sym_payload["run_id"]
                sym_run_dir = runs_root / sym_run_id
                _print_formula(sym_run_dir, kind)

            results.append({"kind": kind, "target": target_col, "train_run_id": train_run_id, "sym_run_id": sym_run_id, "status": "ok"})

        except Exception as e:
            print(f"  ERROR [{kind}]: {e}")
            results.append({"kind": kind, "target": target_col, "status": f"error: {e}"})

    # ── Summary ───────────────────────────────────────────────────
    _print_section("Summary")
    for r in results:
        print(f"  [{r['kind']}] target={r['target']}  status={r['status']}")
        if r.get("train_run_id"):
            print(f"    train_run_id = {r['train_run_id']}")
        if r.get("sym_run_id"):
            print(f"    sym_run_id   = {r['sym_run_id']}")


if __name__ == "__main__":
    main()
