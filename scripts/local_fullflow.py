from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.local.baseline_torch import BaselineConfig, BaselineRunOptions, run_baseline_local
from src.local.derive_dataset import DeriveDatasetConfig, derive_dataset_local
from src.local.kan_symbolic import SymbolicConfig, extract_symbolic_local
from src.local.kan_train import TrainConfig, train_kan_local


def _repo_root() -> Path:
    return REPO_ROOT


def _parse_csv_ints(s: str) -> list[int]:
    raw = [p.strip() for p in str(s).split(",") if p.strip()]
    out: list[int] = []
    for p in raw:
        out.append(int(p))
    return out


def _cmd_derive(args: argparse.Namespace) -> None:
    cfg = DeriveDatasetConfig(
        degree_base_c=float(args.degree_base_c),
        horizon_steps=_parse_csv_ints(args.horizon_steps) if args.horizon_steps else None,
        net_load_lag_steps=_parse_csv_ints(args.net_load_lag_steps) if args.net_load_lag_steps else None,
        add_physics_proxies=not bool(args.no_physics_proxies),
    )
    payload = derive_dataset_local(
        args.source_data_run_id,
        runs_root=Path(args.runs_root),
        source_timestamp=args.source_timestamp,
        run_id=args.run_id,
        cfg=cfg,
    )
    print(payload["run_id"], flush=True)


def _cmd_kan_train(args: argparse.Namespace) -> None:
    include_groups = [s.strip() for s in str(args.include_groups).split(",") if s.strip()] if args.include_groups else None
    lag_series = [s.strip() for s in str(args.lag_series).split(",") if s.strip()] if args.lag_series else None
    lag_steps = _parse_csv_ints(args.lag_steps) if args.lag_steps else None

    hidden_layers = tuple(_parse_csv_ints(args.hidden_layers)) if args.hidden_layers else None
    cfg = TrainConfig(
        target_col=str(args.target_col),
        hidden_width=int(args.hidden_width),
        hidden_layers=hidden_layers,
        warmup_steps=int(args.warmup_steps),
        sparsify_steps=int(args.sparsify_steps),
        refine_steps=int(args.refine_steps),
        sparsify_lamb=float(args.sparsify_lamb),
    )
    out = train_kan_local(
        args.data_run_id,
        runs_root=Path(args.runs_root),
        device_name=str(args.device),
        data_timestamp=args.data_timestamp,
        run_id=args.run_id,
        kind=args.kind,
        cfg=cfg,
        include_base=not bool(args.no_include_base),
        include_groups=include_groups,
        lag_series=lag_series,
        lag_steps=lag_steps,
        max_train_rows=int(args.max_train_rows) if args.max_train_rows is not None else None,
        warmup_update_grid=not bool(args.no_warmup_update_grid),
    )
    print(out["run_id"], flush=True)


def _cmd_symbolic(args: argparse.Namespace) -> None:
    lib = [s.strip() for s in str(args.lib).split(",") if s.strip()] if args.lib else None
    cfg = SymbolicConfig(
        r2_threshold=float(args.r2_threshold),
        weight_simple=float(args.weight_simple),
        fix_below_threshold_to_zero=bool(args.fix_below_threshold_to_zero),
        sample_rows=int(args.sample_rows),
        lib=lib,
        device_name=str(args.device),
    )
    payload = extract_symbolic_local(
        args.train_run_id,
        runs_root=Path(args.runs_root),
        run_id=args.run_id,
        cfg=cfg,
    )
    print(payload["run_id"], flush=True)


def _cmd_baseline(args: argparse.Namespace) -> None:
    cfg = BaselineConfig(
        model_type="mlp",
        target_col=str(args.target_col),
        epochs=int(args.epochs),
        lr=float(args.lr),
        batch_size=int(args.batch_size),
        patience=int(args.patience),
    )
    opts = BaselineRunOptions(
        runs_root=Path(args.runs_root),
        data_timestamp=args.data_timestamp,
        run_id=args.run_id,
        match_kan_run_id=args.match_kan_run_id,
        sync_kan_feature_cols=bool(args.sync_kan_feature_cols),
        sync_kan_budget=bool(args.sync_kan_budget),
        lag_steps=_parse_csv_ints(args.lag_steps) if args.lag_steps else None,
        max_train_rows=int(args.max_train_rows) if args.max_train_rows is not None else None,
        device_name=str(args.device),
    )
    payload = run_baseline_local(args.data_run_id, opts=opts, cfg=cfg)
    print(payload["run_id"], flush=True)


def main() -> None:
    p = argparse.ArgumentParser(description="Local (non-Modal) pipeline runner for KAN-SR.")
    p.add_argument("--runs-root", default=str(_repo_root() / "runs"), help="Local runs/ directory root.")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("derive-dataset", help="Phase 1.5: derive delta/net_load/horizon targets locally.")
    d.add_argument("--source-data-run-id", required=True)
    d.add_argument("--source-timestamp", default=None)
    d.add_argument("--run-id", default=None)
    d.add_argument("--degree-base-c", default=18.0, type=float)
    d.add_argument("--horizon-steps", default=None, help="CSV ints, e.g. 1,6,12,24")
    d.add_argument("--net-load-lag-steps", default=None, help="CSV ints, e.g. 1,12,48")
    d.add_argument("--no-physics-proxies", action="store_true")
    d.set_defaults(func=_cmd_derive)

    kt = sub.add_parser("kan-train", help="Phase 2: train KAN locally (CPU/CUDA).")
    kt.add_argument("--data-run-id", required=True)
    kt.add_argument("--data-timestamp", default=None)
    kt.add_argument("--run-id", default=None)
    kt.add_argument("--kind", default=None)
    kt.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    kt.add_argument("--target-col", default="load")
    kt.add_argument("--hidden-width", default=10, type=int)
    kt.add_argument("--hidden-layers", default=None, help="CSV ints, e.g. 32,32 (overrides hidden-width)")
    kt.add_argument("--warmup-steps", default=200, type=int)
    kt.add_argument("--sparsify-steps", default=800, type=int)
    kt.add_argument("--refine-steps", default=200, type=int)
    kt.add_argument("--sparsify-lamb", default=0.01, type=float)
    kt.add_argument("--max-train-rows", default=50_000, type=int)
    kt.add_argument("--include-groups", default="meteorology,solar,cyclic")
    kt.add_argument("--lag-series", default="load,wind,solar")
    kt.add_argument("--lag-steps", default="1,12,48")
    kt.add_argument("--no-include-base", action="store_true")
    kt.add_argument("--no-warmup-update-grid", action="store_true")
    kt.set_defaults(func=_cmd_kan_train)

    sy = sub.add_parser("kan-symbolic", help="Phase 3: extract symbolic formula locally.")
    sy.add_argument("--train-run-id", required=True)
    sy.add_argument("--run-id", default=None)
    sy.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    sy.add_argument("--r2-threshold", default=0.999, type=float)
    sy.add_argument("--weight-simple", default=0.9, type=float)
    sy.add_argument("--fix-below-threshold-to-zero", action="store_true")
    sy.add_argument("--sample-rows", default=20_000, type=int)
    sy.add_argument("--lib", default=None, help="CSV, e.g. x,x^2,x^3,sin,cos,abs")
    sy.set_defaults(func=_cmd_symbolic)

    bl = sub.add_parser("baseline-mlp", help="Phase 4: train MLP baseline locally.")
    bl.add_argument("--data-run-id", required=True)
    bl.add_argument("--data-timestamp", default=None)
    bl.add_argument("--run-id", default=None)
    bl.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    bl.add_argument("--target-col", default="load")
    bl.add_argument("--epochs", default=50, type=int)
    bl.add_argument("--lr", default=1e-3, type=float)
    bl.add_argument("--batch-size", default=512, type=int)
    bl.add_argument("--patience", default=8, type=int)
    bl.add_argument("--max-train-rows", default=200_000, type=int)
    bl.add_argument("--lag-steps", default=None, help="CSV ints, e.g. 1,12,48")
    bl.add_argument("--match-kan-run-id", default=None)
    bl.add_argument("--sync-kan-feature-cols", action="store_true")
    bl.add_argument("--sync-kan-budget", action="store_true")
    bl.set_defaults(func=_cmd_baseline)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
