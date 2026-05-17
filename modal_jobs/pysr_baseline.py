"""
PySR baseline (Phase 4) as an isolated Modal job (Julia-backed).

Outputs:
  /vol/runs/<run_id>/
    payload.json
    artifacts/
      equations.csv
      best_equation.txt
      eval_test.json
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import modal

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)


APP_NAME = "kan-sr-baseline-pysr"
DEFAULT_VOLUME_NAME = os.environ.get("KAN_SR_VOLUME", "kan-sr")
VOLUME_MOUNT = "/vol"

app = modal.App(APP_NAME)
volume = modal.Volume.from_name(DEFAULT_VOLUME_NAME, create_if_missing=True)

# Include local source tree in Modal containers so `import src.*` works.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

image = (
    modal.Image.debian_slim(python_version="3.11")
    # PySR/Julia deps sometimes pull via git; Julia install needs curl+tar.
    .apt_install("git", "curl", "ca-certificates", "tar")
    # Pin a stable Julia runtime to avoid juliacall downloading newer versions that can segfault.
    .run_commands(
        "set -eux; "
        "JULIA_VERSION=1.10.4; "
        "JULIA_MINOR=1.10; "
        "curl -fsSL -o /tmp/julia.tgz "
        "https://julialang-s3.julialang.org/bin/linux/x64/${JULIA_MINOR}/julia-${JULIA_VERSION}-linux-x86_64.tar.gz; "
        "tar -xzf /tmp/julia.tgz -C /usr/local; "
        "rm -f /tmp/julia.tgz; "
        "mv /usr/local/julia-${JULIA_VERSION} /usr/local/julia; "
        "ln -sf /usr/local/julia/bin/julia /usr/local/bin/julia; "
        "julia --version"
    )
    .pip_install(
        "numpy>=1.24",
        "pandas>=2.0",
        "pyarrow>=14.0",
        "sympy>=1.13.3",
        # PySR (brings Julia runtime via juliacall in recent versions)
        "pysr>=1.5.0",
    )
    .env(
        {
            "PYTHONPATH": "/root/project",
            # Keep Julia single-threaded to reduce instability/segfault risk in containers.
            "JULIA_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            # Force juliapkg/juliacall to use the pinned Julia binary and persist env in the Volume.
            "PYTHON_JULIAPKG_EXE": "/usr/local/julia/bin/julia",
            "PYTHON_JULIAPKG_PROJECT": "/vol/julia_env",
            "JULIA_DEPOT_PATH": "/vol/julia_depot",
        }
    )
    .add_local_dir(SRC_DIR, remote_path="/root/project/src")
)


def _utc_run_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    return f"{ts}_{uuid.uuid4().hex[:8]}"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, default=str)


@dataclass(frozen=True)
class PySRConfig:
    target_col: str = "load"
    niterations: int = 200
    populations: int = 8
    population_size: int = 40
    maxsize: int = 20
    warm_start: bool = False
    use_original_features: bool = True
    complexity_of_variables: list[int] | None = None


def _load_kan_payload(run_id: str) -> dict[str, Any]:
    path = Path(VOLUME_MOUNT) / "runs" / run_id / "payload.json"
    if not path.exists():
        raise FileNotFoundError(f"KAN payload.json not found: {path}")
    return json.loads(path.read_text())


def _kan_total_steps(payload: dict[str, Any]) -> int:
    cfg = payload.get("cfg") or {}
    keys = ["warmup_steps", "sparsify_steps", "refine_steps"]
    missing = [k for k in keys if k not in cfg]
    if missing:
        raise ValueError(f"KAN payload cfg missing steps keys: {missing}")
    return int(cfg["warmup_steps"]) + int(cfg["sparsify_steps"]) + int(cfg["refine_steps"])


@app.function(image=image, volumes={VOLUME_MOUNT: volume}, timeout=6 * 3600)
def run_pysr(
    data_run_id: str,
    *,
    data_timestamp: str | None = None,
    run_id: str | None = None,
    seed: int = 1,
    cfg: PySRConfig = PySRConfig(),
    include_base: bool = True,
    include_groups: list[str] | None = None,
    lag_series: list[str] | None = None,
    lag_steps: list[int] | None = None,
    max_train_rows: int | None = 10_000,
    seed_from_symbolic_run: str | None = None,
    seed_max_seeds: int = 8,
    match_kan_run_id: str | None = None,
    sync_kan_feature_cols: bool = False,
    sync_kan_budget: bool = False,
) -> dict[str, Any]:
    import numpy as np
    import pandas as pd

    from pysr import PySRRegressor

    from src.data.split import load_splits_from_parquet
    from src.kan_sr.dataset import pick_feature_columns
    from src.kan_sr.metrics import mae, r2, rmse

    run_id = run_id or _utc_run_id()
    run_dir = Path(VOLUME_MOUNT) / "runs" / run_id
    artifacts_dir = run_dir / "artifacts"
    run_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    processed_dir = Path(VOLUME_MOUNT) / "runs" / data_run_id / "processed"
    train_df, val_df, test_df = load_splits_from_parquet(processed_dir, timestamp=data_timestamp)

    kan_payload = None
    if bool(sync_kan_feature_cols) or bool(sync_kan_budget):
        if match_kan_run_id is None:
            raise ValueError("sync_kan_feature_cols/sync_kan_budget requires match_kan_run_id")
        kan_payload = _load_kan_payload(match_kan_run_id)
        kan_data_run_id = kan_payload.get("data_run_id")
        if kan_data_run_id is not None and str(kan_data_run_id) != str(data_run_id):
            raise ValueError(f"KAN data_run_id mismatch: pysr={data_run_id} kan={kan_data_run_id}")
        kan_target = (kan_payload.get("cfg") or {}).get("target_col")
        if kan_target is not None and str(kan_target) != str(cfg.target_col):
            raise ValueError(f"KAN target_col mismatch: pysr={cfg.target_col} kan={kan_target}")

    if bool(sync_kan_budget):
        assert kan_payload is not None
        total_steps = _kan_total_steps(kan_payload)
        cfg = replace(cfg, niterations=int(total_steps))

    if max_train_rows is not None and len(train_df) > max_train_rows:
        train_df = train_df.sample(n=max_train_rows, random_state=seed).sort_index()
        logger.info(f"Downsampled train_df to {max_train_rows} sampled rows for PySR speed")

    from src.local.kan_train_prepare import normalize_feature_settings

    groups, series, steps = normalize_feature_settings(
        include_groups=include_groups, lag_series=lag_series, lag_steps=lag_steps,
    )
    feature_cols = pick_feature_columns(
        train_df, target_col=cfg.target_col, include_base=include_base,
        include_groups=groups, lag_steps=steps, lag_series=series,
    )

    if bool(sync_kan_feature_cols) and (not seed_from_symbolic_run):
        assert kan_payload is not None
        kan_feature_cols = kan_payload.get("feature_cols")
        if not kan_feature_cols:
            raise ValueError("KAN payload missing feature_cols")
        missing_cols = [c for c in kan_feature_cols if c not in train_df.columns]
        if missing_cols:
            raise ValueError(f"KAN feature cols missing from dataset: {missing_cols[:10]}")
        feature_cols = list(kan_feature_cols)
        lag_steps = list(kan_payload.get("lag_steps") or [])

    # If seeded cross-validation is requested, align to the symbolic run feature set.
    seed_features_meta: dict[str, Any] | None = None
    if seed_from_symbolic_run:
        sym_run = Path(VOLUME_MOUNT) / "runs" / seed_from_symbolic_run
        sym_payload_path = sym_run / "payload.json"
        if not sym_payload_path.exists():
            raise FileNotFoundError(f"symbolic payload not found: {sym_payload_path}")
        sym_payload = json.loads(sym_payload_path.read_text())
        sym_feature_cols = sym_payload.get("feature_cols")
        if not sym_feature_cols:
            raise ValueError("symbolic payload missing feature_cols")
        missing = [c for c in sym_feature_cols if c not in train_df.columns]
        if missing:
            raise ValueError(f"symbolic feature cols missing from dataset: {missing[:10]}")
        feature_cols = list(sym_feature_cols)

    # Optionally invert the Phase-1 z-score normalization so PySR learns in original units.
    if cfg.use_original_features:
        from src.data.split import inverse_transform

        scaler_params_path = Path(VOLUME_MOUNT) / "runs" / data_run_id / "artifacts" / "scaler_params.json"
        scaler_params = json.loads(scaler_params_path.read_text())
        x_train_df = inverse_transform(train_df[feature_cols], scaler_params)
        x_val_df = inverse_transform(val_df[feature_cols], scaler_params)
        x_test_df = inverse_transform(test_df[feature_cols], scaler_params)
    else:
        x_train_df = train_df[feature_cols]
        x_val_df = val_df[feature_cols]
        x_test_df = test_df[feature_cols]

    X_train = x_train_df.to_numpy(dtype=np.float64)
    y_train = train_df[cfg.target_col].to_numpy(dtype=np.float64)

    X_val = x_val_df.to_numpy(dtype=np.float64)
    y_val = val_df[cfg.target_col].to_numpy(dtype=np.float64)

    X_test = x_test_df.to_numpy(dtype=np.float64)
    y_test = test_df[cfg.target_col].to_numpy(dtype=np.float64)

    # KAN-seeded cross-validation: append seed sub-expression values as extra input columns.
    if seed_from_symbolic_run:
        from src.eval.seed_features import compute_seed_matrix, extract_seed_features

        expr_str = (Path(VOLUME_MOUNT) / "runs" / seed_from_symbolic_run / "artifacts" / "formula.sympy.txt").read_text()
        import sympy as sp

        locals_map = {name: sp.Symbol(name) for name in feature_cols}
        expr = sp.sympify(expr_str, locals=locals_map)
        seeds = extract_seed_features(expr, max_seeds=seed_max_seeds)

        seed_train, seed_names, kept = compute_seed_matrix(seeds, feature_cols=feature_cols, x_df=x_train_df)
        seed_val, _seed_names_v, _kept_v = compute_seed_matrix(kept, feature_cols=feature_cols, x_df=x_val_df)
        seed_test, _seed_names2, _kept2 = compute_seed_matrix(kept, feature_cols=feature_cols, x_df=x_test_df)

        if seed_train.shape[1] > 0:
            # Stabilize the Julia backend by keeping seed feature scales reasonable.
            # We robust-clip and z-score using *train* statistics, then apply to val/test.
            clip_lo = np.quantile(seed_train, 0.005, axis=0)
            clip_hi = np.quantile(seed_train, 0.995, axis=0)
            seed_train = np.clip(seed_train, clip_lo, clip_hi)
            seed_val = np.clip(seed_val, clip_lo, clip_hi)
            seed_test = np.clip(seed_test, clip_lo, clip_hi)

            seed_mean = seed_train.mean(axis=0)
            seed_std = seed_train.std(axis=0)
            seed_std = np.where(seed_std > 0, seed_std, 1.0)
            seed_train = (seed_train - seed_mean) / seed_std
            seed_val = (seed_val - seed_mean) / seed_std
            seed_test = (seed_test - seed_mean) / seed_std

            X_train = np.concatenate([X_train, seed_train], axis=1)
            X_val = np.concatenate([X_val, seed_val], axis=1)
            X_test = np.concatenate([X_test, seed_test], axis=1)
            feature_cols = list(feature_cols) + list(seed_names)
            seed_features_meta = {
                "seed_from_symbolic_run": seed_from_symbolic_run,
                "seed_max_seeds": int(seed_max_seeds),
                "seeds": [s.as_dict() for s in kept],
                "scaler": {
                    "clip_quantiles": [0.005, 0.995],
                    "clip_lo": clip_lo.tolist(),
                    "clip_hi": clip_hi.tolist(),
                    "mean": seed_mean.tolist(),
                    "std": seed_std.tolist(),
                },
            }

    payload = {
        "run_id": run_id,
        "phase": "04-baselines-pysr",
        "seed": int(seed),
        "data_run_id": data_run_id,
        "data_timestamp": data_timestamp,
        "cfg": asdict(cfg),
        "feature_cols": feature_cols,
        "lag_steps": list(lag_steps),
        "seed_from_symbolic_run": seed_from_symbolic_run,
        "seed_features_meta": seed_features_meta,
        "match_kan_run_id": match_kan_run_id,
        "sync_kan_feature_cols": bool(sync_kan_feature_cols),
        "sync_kan_budget": bool(sync_kan_budget),
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_json(run_dir / "payload.json", payload)
    volume.commit()

    # Configure PySR for interpretable equations.
    #
    # NOTE: We must avoid Julia segfaults in constant optimization, which are more likely
    # when feeding raw-scale + derived seed features. For seeded runs, we disable constant
    # optimization (and we also disable Julia multithreading) for stability.
    import inspect

    # Use a smaller/safer operator set for seeded runs to reduce segfault risk
    # (division and exp can easily produce huge/NaN values when combined with derived features).
    binary_ops = ["+", "-", "*", "/"]
    unary_ops = ["sin", "cos", "exp"]
    populations = cfg.populations
    population_size = cfg.population_size
    maxsize = cfg.maxsize
    if seed_from_symbolic_run:
        binary_ops = ["+", "-", "*"]
        unary_ops = ["sin", "cos"]
        populations = min(populations, 4)
        population_size = min(population_size, 30)
        maxsize = min(maxsize, 15)

    model_kwargs: dict[str, Any] = {
        "niterations": cfg.niterations,
        "populations": populations,
        "population_size": population_size,
        "maxsize": maxsize,
        "binary_operators": binary_ops,
        "unary_operators": unary_ops,
        "model_selection": "best",
        "warm_start": cfg.warm_start,
        # Use a stable, standard elementwise loss (MSE).
        "elementwise_loss": "L2DistLoss()",
        # Reduce crash risk in constrained environments.
        "parallelism": "serial",
        "procs": 1,
        "batching": True,
        "batch_size": 256,
        # Reduce verbosity in Modal logs.
        "progress": True,
    }
    if cfg.complexity_of_variables is not None:
        model_kwargs["complexity_of_variables"] = cfg.complexity_of_variables

    sig = inspect.signature(PySRRegressor)
    if "multithreading" in sig.parameters:
        model_kwargs["multithreading"] = False
    if "deterministic" in sig.parameters:
        model_kwargs["deterministic"] = True
    if "random_state" in sig.parameters:
        model_kwargs["random_state"] = int(seed)
    if seed_from_symbolic_run:
        # Extra guardrails against Julia crashes during constant optimization.
        if "should_optimize_constants" in sig.parameters:
            model_kwargs["should_optimize_constants"] = False
        if "optimize_probability" in sig.parameters:
            model_kwargs["optimize_probability"] = 0.0
        if "optimizer_iterations" in sig.parameters:
            model_kwargs["optimizer_iterations"] = 0
        if "optimizer_nrestarts" in sig.parameters:
            model_kwargs["optimizer_nrestarts"] = 0

    model = PySRRegressor(**model_kwargs)

    model.fit(X_train, y_train, variable_names=feature_cols)

    # Save equations table
    import sympy as sp

    eq_df = model.equations_.copy()

    # Add val/test metrics per equation when sympy representation is available.
    sym_col = "sympy_format" if "sympy_format" in eq_df.columns else ("equation" if "equation" in eq_df.columns else None)
    if sym_col is not None:
        locals_map = {name: sp.Symbol(name) for name in feature_cols}
        val_rmse, val_mae, val_r2_list = [], [], []
        test_rmse, test_mae, test_r2 = [], [], []
        for s in eq_df[sym_col].astype(str).tolist():
            try:
                expr = sp.sympify(s, locals=locals_map)
                f = sp.lambdify(feature_cols, expr, modules="numpy")

                vargs = [X_val[:, i] for i in range(X_val.shape[1])]
                vpred = np.asarray(f(*vargs), dtype=np.float64).reshape(-1)
                if vpred.shape[0] == 1 and y_val.shape[0] > 1:
                    vpred = np.full_like(y_val, float(vpred[0]), dtype=np.float64)
                val_rmse.append(rmse(y_val, vpred))
                val_mae.append(mae(y_val, vpred))
                val_r2_list.append(r2(y_val, vpred))

                args = [X_test[:, i] for i in range(X_test.shape[1])]
                pred = np.asarray(f(*args), dtype=np.float64).reshape(-1)
                if pred.shape[0] == 1 and y_test.shape[0] > 1:
                    pred = np.full_like(y_test, float(pred[0]), dtype=np.float64)
                test_rmse.append(rmse(y_test, pred))
                test_mae.append(mae(y_test, pred))
                test_r2.append(r2(y_test, pred))
            except Exception:  # noqa: BLE001
                val_rmse.append(float("nan"))
                val_mae.append(float("nan"))
                val_r2_list.append(float("nan"))
                test_rmse.append(float("nan"))
                test_mae.append(float("nan"))
                test_r2.append(float("nan"))

        eq_df["val_rmse"] = val_rmse
        eq_df["val_mae"] = val_mae
        eq_df["val_r2"] = val_r2_list
        eq_df["test_rmse"] = test_rmse
        eq_df["test_mae"] = test_mae
        eq_df["test_r2"] = test_r2

    eq_path = artifacts_dir / "equations.csv"
    eq_df.to_csv(eq_path, index=False)

    if seed_features_meta is not None:
        _write_json(artifacts_dir / "seed_features.json", seed_features_meta)

    # Pick best equation and evaluate on test
    y_pred = model.predict(X_test)
    eval_test = {"rmse": rmse(y_test, y_pred), "mae": mae(y_test, y_pred), "r2": r2(y_test, y_pred)}
    _write_json(artifacts_dir / "eval_test.json", eval_test)

    # Save test predictions for downstream evaluation/plots
    # Hard constraint (PIKAN): nighttime PV must be 0 (for solar target).
    if cfg.target_col == "solar" and "is_night" in test_df.columns:
        try:
            from src.data.split import inverse_transform

            scaler_params = json.loads(
                (Path(VOLUME_MOUNT) / "runs" / data_run_id / "artifacts" / "scaler_params.json").read_text()
            )
            is_night_orig = inverse_transform(test_df[["is_night"]], scaler_params)["is_night"].to_numpy(dtype=np.float64)
            y_pred = y_pred.copy()
            y_pred[is_night_orig > 0.5] = 0.0
        except Exception:  # noqa: BLE001
            pass

    pred_df = pd.DataFrame({"y_true": y_test, "y_pred": y_pred, "residual": y_pred - y_test}, index=test_df.index)
    pred_df.to_parquet(artifacts_dir / "predictions_test.parquet", compression="snappy")

    # Save best equation string (human-friendly)
    try:
        best = model.get_best()
        (artifacts_dir / "best_equation.txt").write_text(str(best))
    except Exception as e:  # noqa: BLE001
        (artifacts_dir / "best_equation.txt").write_text(f"Failed to get best equation: {e}")

    payload["completed_at"] = datetime.now(timezone.utc).isoformat()
    payload["eval_test"] = eval_test
    _write_json(run_dir / "payload.json", payload)
    volume.commit()

    return {"run_id": run_id, "status": "completed", "eval_test": eval_test, "artifacts_dir": str(artifacts_dir)}


def _parse_str_list(value: str) -> list[str] | None:
    text = str(value).strip().lower()
    if text in ("", "none"):
        return [] if text == "none" else None
    return [item.strip() for item in str(value).split(",") if item.strip()]


def _parse_int_list(value: str) -> list[int] | None:
    text = str(value).strip().lower()
    if text in ("", "none"):
        return [] if text == "none" else None
    return [int(item.strip()) for item in text.split(",") if item.strip()]


@app.local_entrypoint()
def main(
    data_run_id: str,
    run_id: str = "",
    target: str = "load",
    seed: int = 1,
    niterations: int = 200,
    populations: int = 8,
    population_size: int = 40,
    maxsize: int = 20,
    warm_start: bool = False,
    use_original_features: bool = True,
    complexity_of_variables: str = "",
    include_base: bool = True,
    include_groups: str = "",
    lag_series: str = "",
    lag_steps: str = "1,12,48",
    max_train_rows: int = 10_000,
    seed_from_symbolic_run: str = "",
    seed_max_seeds: int = 8,
    match_kan_run_id: str = "",
    sync_kan_feature_cols: bool = False,
    sync_kan_budget: bool = False,
    data_timestamp: str = "",
) -> None:
    max_train_rows_opt: int | None = int(max_train_rows)
    if max_train_rows_opt <= 0:
        max_train_rows_opt = None
    seed_run_id = seed_from_symbolic_run.strip() or None
    match = match_kan_run_id.strip() or None
    ts_opt = data_timestamp.strip() or None

    cfg = PySRConfig(
        target_col=target,
        niterations=int(niterations),
        populations=int(populations),
        population_size=int(population_size),
        maxsize=int(maxsize),
        warm_start=bool(warm_start),
        use_original_features=bool(use_original_features),
        complexity_of_variables=_parse_int_list(complexity_of_variables),
    )
    result = run_pysr.remote(
        data_run_id,
        run_id=run_id.strip() or None,
        data_timestamp=ts_opt,
        seed=int(seed),
        cfg=cfg,
        include_base=bool(include_base),
        include_groups=_parse_str_list(include_groups),
        lag_series=_parse_str_list(lag_series),
        lag_steps=_parse_int_list(lag_steps),
        max_train_rows=max_train_rows_opt,
        seed_from_symbolic_run=seed_run_id,
        seed_max_seeds=int(seed_max_seeds),
        match_kan_run_id=match,
        sync_kan_feature_cols=bool(sync_kan_feature_cols),
        sync_kan_budget=bool(sync_kan_budget),
    )
    print(json.dumps(result, indent=2))
