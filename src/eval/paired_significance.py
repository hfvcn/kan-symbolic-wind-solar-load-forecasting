from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

DEFAULT_BOOTSTRAP_SAMPLES = 2000
DEFAULT_PERMUTATION_SAMPLES = 2000
DEFAULT_RANDOM_SEED = 7
PERMUTATION_BATCH_SIZE = 128
PREDICTION_FILES = ("predictions_test_reconstructed.parquet", "predictions_test.parquet")


@dataclass(frozen=True)
class PairedTestConfig:
    metric: str
    bootstrap_samples: int = DEFAULT_BOOTSTRAP_SAMPLES
    permutation_samples: int = DEFAULT_PERMUTATION_SAMPLES
    random_seed: int = DEFAULT_RANDOM_SEED


@dataclass(frozen=True)
class RunPredictions:
    run_id: str
    target_col: str | None
    predictions_path: Path
    frame: pd.DataFrame


@dataclass(frozen=True)
class PairedComparisonResult:
    reference_run_id: str
    compare_run_id: str
    target_col: str | None
    metric: str
    n: int
    reference_mean_error: float
    compare_mean_error: float
    mean_diff: float
    median_diff: float
    win_rate: float
    tie_rate: float
    ci95_low: float
    ci95_high: float
    permutation_pvalue: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "reference_run_id": self.reference_run_id,
            "compare_run_id": self.compare_run_id,
            "target_col": self.target_col,
            "metric": self.metric,
            "n": self.n,
            "reference_mean_error": self.reference_mean_error,
            "compare_mean_error": self.compare_mean_error,
            "mean_diff": self.mean_diff,
            "median_diff": self.median_diff,
            "win_rate": self.win_rate,
            "tie_rate": self.tie_rate,
            "ci95_low": self.ci95_low,
            "ci95_high": self.ci95_high,
            "permutation_pvalue": self.permutation_pvalue,
        }


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _infer_target_col(payload: dict[str, Any]) -> str | None:
    target_col = payload.get("target_col")
    if target_col:
        return str(target_col)
    cfg = payload.get("cfg")
    if isinstance(cfg, dict) and cfg.get("target_col"):
        return str(cfg["target_col"])
    return None


def _pick_predictions_path(run_dir: Path) -> Path:
    artifacts_dir = run_dir / "artifacts"
    for name in PREDICTION_FILES:
        path = artifacts_dir / name
        if path.exists():
            return path
    raise FileNotFoundError(f"predictions_test parquet not found in: {artifacts_dir}")


def _load_frame(path: Path) -> pd.DataFrame:
    frame = pd.read_parquet(path)
    missing = {"y_true", "y_pred"} - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns in {path}: {sorted(missing)}")
    trimmed = frame[["y_true", "y_pred"]].dropna(subset=["y_true", "y_pred"]).copy()
    if len(trimmed) == 0:
        raise ValueError(f"No valid y_true/y_pred rows in: {path}")
    return trimmed


def load_run_predictions(run_dir: str | Path) -> RunPredictions:
    resolved_dir = Path(run_dir)
    payload_path = resolved_dir / "payload.json"
    if not payload_path.exists():
        raise FileNotFoundError(f"payload.json not found in: {resolved_dir}")
    payload = _read_json(payload_path)
    predictions_path = _pick_predictions_path(resolved_dir)
    return RunPredictions(
        run_id=str(payload.get("run_id") or resolved_dir.name),
        target_col=_infer_target_col(payload),
        predictions_path=predictions_path,
        frame=_load_frame(predictions_path),
    )


def _align_runs(reference: RunPredictions, compare: RunPredictions) -> pd.DataFrame:
    if reference.target_col != compare.target_col:
        raise ValueError(
            f"target_col mismatch: {reference.run_id}={reference.target_col} vs {compare.run_id}={compare.target_col}"
        )
    merged = reference.frame.rename(columns={"y_true": "y_true_ref", "y_pred": "y_pred_ref"}).join(
        compare.frame.rename(columns={"y_true": "y_true_cmp", "y_pred": "y_pred_cmp"}),
        how="inner",
    )
    if len(merged) == 0:
        raise ValueError(f"No overlapping prediction timestamps between {reference.run_id} and {compare.run_id}")
    if not np.allclose(
        merged["y_true_ref"].to_numpy(dtype=np.float64),
        merged["y_true_cmp"].to_numpy(dtype=np.float64),
        atol=1e-3,
        rtol=1e-9,
    ):
        raise ValueError(f"y_true mismatch between {reference.run_id} and {compare.run_id}")
    return merged


def _metric_errors(y_true: np.ndarray, y_pred: np.ndarray, *, metric: str) -> np.ndarray:
    residual = np.asarray(y_pred - y_true, dtype=np.float64)
    if metric == "absolute_error":
        return np.abs(residual)
    if metric == "squared_error":
        return residual**2
    raise ValueError(f"Unsupported metric: {metric}")


def _bootstrap_ci(values: np.ndarray, *, samples: int, rng: np.random.Generator) -> tuple[float, float]:
    draws = np.empty(samples, dtype=np.float64)
    n = len(values)
    for idx in range(samples):
        sample_idx = rng.integers(0, n, size=n)
        draws[idx] = float(np.mean(values[sample_idx]))
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def _permutation_pvalue(values: np.ndarray, *, samples: int, rng: np.random.Generator) -> float:
    observed = float(abs(np.mean(values)))
    if observed == 0.0:
        return 1.0
    exceed = 0
    completed = 0
    while completed < samples:
        batch = min(PERMUTATION_BATCH_SIZE, samples - completed)
        signs = rng.integers(0, 2, size=(batch, len(values)), dtype=np.int8).astype(np.float64)
        signed_values = ((signs * 2.0) - 1.0) * values
        signed_means = np.abs(np.mean(signed_values, axis=1))
        exceed += int(np.sum(signed_means >= observed - 1e-12))
        completed += batch
    return float((exceed + 1) / (samples + 1))


def compare_predictions(
    reference: RunPredictions,
    compare: RunPredictions,
    *,
    config: PairedTestConfig,
) -> PairedComparisonResult:
    if config.bootstrap_samples < 1:
        raise ValueError("bootstrap_samples must be >= 1")
    if config.permutation_samples < 1:
        raise ValueError("permutation_samples must be >= 1")
    merged = _align_runs(reference, compare)
    y_true = merged["y_true_ref"].to_numpy(dtype=np.float64)
    ref_errors = _metric_errors(y_true, merged["y_pred_ref"].to_numpy(dtype=np.float64), metric=config.metric)
    cmp_errors = _metric_errors(y_true, merged["y_pred_cmp"].to_numpy(dtype=np.float64), metric=config.metric)
    diffs = cmp_errors - ref_errors
    rng = np.random.default_rng(config.random_seed)
    ci_low, ci_high = _bootstrap_ci(diffs, samples=config.bootstrap_samples, rng=rng)
    pvalue = _permutation_pvalue(diffs, samples=config.permutation_samples, rng=rng)
    ties = np.isclose(diffs, 0.0, atol=1e-12)
    wins = diffs > 0.0
    return PairedComparisonResult(
        reference_run_id=reference.run_id,
        compare_run_id=compare.run_id,
        target_col=reference.target_col,
        metric=config.metric,
        n=int(len(diffs)),
        reference_mean_error=float(np.mean(ref_errors)),
        compare_mean_error=float(np.mean(cmp_errors)),
        mean_diff=float(np.mean(diffs)),
        median_diff=float(np.median(diffs)),
        win_rate=float(np.mean(wins)),
        tie_rate=float(np.mean(ties)),
        ci95_low=ci_low,
        ci95_high=ci_high,
        permutation_pvalue=pvalue,
    )


def compare_run_dirs(
    reference_run_dir: str | Path,
    compare_run_dirs: list[str | Path],
    *,
    config: PairedTestConfig,
) -> pd.DataFrame:
    reference = load_run_predictions(reference_run_dir)
    rows = []
    for compare_run_dir in compare_run_dirs:
        compare = load_run_predictions(compare_run_dir)
        result = compare_predictions(reference, compare, config=config)
        rows.append(result.as_dict())
    return pd.DataFrame(rows)
