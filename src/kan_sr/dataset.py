from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)


@dataclass(frozen=True)
class TargetScaler:
    mean: float
    std: float

    def transform(self, y: np.ndarray) -> np.ndarray:
        return (y - self.mean) / self.std

    def inverse_transform(self, y: np.ndarray) -> np.ndarray:
        return y * self.std + self.mean

    def as_dict(self) -> dict[str, float]:
        return {"mean": float(self.mean), "std": float(self.std)}


def fit_target_scaler(y: np.ndarray, eps: float = 1e-8) -> TargetScaler:
    mean = float(np.mean(y))
    std = float(np.std(y))
    if std < eps:
        std = eps
    return TargetScaler(mean=mean, std=std)


def _to_float32_tensor(x: np.ndarray) -> torch.Tensor:
    import torch

    return torch.tensor(x.astype(np.float32), dtype=torch.float32)


def build_kan_dataset(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    *,
    target_col: str,
    feature_cols: list[str],
    scale_target: bool = True,
) -> tuple[dict[str, torch.Tensor], dict[str, Any]]:
    """
    Build a dataset dict compatible with `kan.KAN.fit()`.

    KAN expects a dict containing:
        - train_input, train_label
        - test_input, test_label

    Here we map validation split to KAN's "test_*" fields for training-time monitoring.
    """
    if target_col not in train_df.columns:
        raise ValueError(f"target_col not in train_df: {target_col}")
    if target_col not in val_df.columns:
        raise ValueError(f"target_col not in val_df: {target_col}")
    if not feature_cols:
        raise ValueError("feature_cols must be non-empty")

    missing = [c for c in feature_cols if c not in train_df.columns or c not in val_df.columns]
    if missing:
        raise ValueError(f"feature columns missing from dataframes: {missing}")

    x_train = train_df[feature_cols].to_numpy()
    y_train = train_df[[target_col]].to_numpy()

    x_val = val_df[feature_cols].to_numpy()
    y_val = val_df[[target_col]].to_numpy()

    meta: dict[str, Any] = {
        "target_col": target_col,
        "feature_cols": list(feature_cols),
        "scale_target": bool(scale_target),
    }

    if scale_target:
        scaler = fit_target_scaler(y_train)
        y_train = scaler.transform(y_train)
        y_val = scaler.transform(y_val)
        meta["target_scaler"] = scaler.as_dict()
        logger.info(f"Target scaled for training: mean={scaler.mean:.4f}, std={scaler.std:.4f}")

    dataset = {
        "train_input": _to_float32_tensor(x_train),
        "train_label": _to_float32_tensor(y_train),
        "test_input": _to_float32_tensor(x_val),
        "test_label": _to_float32_tensor(y_val),
    }

    return dataset, meta


def pick_feature_columns(
    df: pd.DataFrame,
    *,
    target_col: str,
    include_base: bool = True,
    include_groups: Iterable[str] = ("meteorology", "solar", "cyclic"),
    lag_steps: Iterable[int] = (1, 12, 48),
    lag_series: Iterable[str] = ("load", "wind", "solar"),
) -> list[str]:
    """
    Select a compact, thesis-friendly feature set.

    Default behavior keeps interpretability manageable:
      - Base cols: wind/solar (and load if target != load)
      - Groups: meteorology, solar-position, cyclic encoding
      - Sparse lag subset: (1, 12, 48) for each series in lag_series
    """
    from src.data.features import get_feature_groups

    groups = get_feature_groups()
    cols: list[str] = []

    if include_base:
        for base_col in ("load", "wind", "solar"):
            if base_col == target_col:
                continue
            if base_col in df.columns:
                cols.append(base_col)

    for g in include_groups:
        for c in groups.get(g, []):
            if c in df.columns and c != target_col:
                cols.append(c)

    lag_steps_list = sorted({int(s) for s in lag_steps})
    for series in lag_series:
        for step in lag_steps_list:
            name = f"{series}_lag_{step}"
            if name in df.columns and name != target_col:
                cols.append(name)

    # De-duplicate preserving order
    seen: set[str] = set()
    out: list[str] = []
    for c in cols:
        if c not in seen:
            seen.add(c)
            out.append(c)

    if not out:
        raise ValueError("No feature columns selected (check include_groups / lag_steps / schema)")

    return out
