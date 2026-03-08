from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from src.kan_sr.metrics import mae, r2, rmse

_HORIZON_RE = re.compile(r"_h(\d+)$")
_QUANTILE_LOW = 1.0 / 3.0
_QUANTILE_HIGH = 2.0 / 3.0
_TARGET_FAMILIES = {
    "solar": ("day_night", "ghi_quantile"),
    "wind": ("wind_quantile",),
    "load": ("season", "weekpart", "volatility"),
    "net_load": ("season", "weekpart", "volatility"),
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def infer_target_col(payload: dict) -> str:
    target_col = payload.get("target_col")
    if target_col:
        return str(target_col)
    cfg = payload.get("cfg")
    if isinstance(cfg, dict) and cfg.get("target_col"):
        return str(cfg["target_col"])
    raise ValueError("target_col missing from payload")


def infer_target_family(target_col: str) -> str:
    base = str(target_col)
    if base.startswith("delta_"):
        base = base[len("delta_") :]
    return base.rsplit("_h", 1)[0]


def infer_volatility_col(target_col: str) -> str | None:
    if target_col.startswith("delta_"):
        return target_col
    if _HORIZON_RE.search(target_col):
        return f"delta_{target_col}"
    return None


def pick_predictions_path(artifacts_dir: Path) -> Path:
    for name in ("predictions_test_reconstructed.parquet", "predictions_test.parquet"):
        path = artifacts_dir / name
        if path.exists():
            return path
    raise FileNotFoundError(f"Missing predictions parquet under {artifacts_dir}")


def _processed_test_path(run_dir: Path, payload: dict) -> Path:
    data_run_id = payload.get("data_run_id")
    data_timestamp = payload.get("data_timestamp")
    if not data_run_id or not data_timestamp:
        raise ValueError(f"run {run_dir.name} missing data_run_id/data_timestamp")
    return run_dir.parent / str(data_run_id) / "processed" / f"test_{data_timestamp}.parquet"


def load_run_frame(run_dir: str | Path) -> tuple[str, pd.DataFrame]:
    path = Path(run_dir)
    payload = _read_json(path / "payload.json")
    target_col = infer_target_col(payload)
    pred_df = pd.read_parquet(pick_predictions_path(path / "artifacts"))
    pred_df = pred_df[["y_true", "y_pred"]].dropna().copy()

    test_path = _processed_test_path(path, payload)
    columns = {"is_night", "ghi_w_m2", "wind_speed_10m_m_s"}
    volatility_col = infer_volatility_col(target_col)
    if volatility_col:
        columns.add(volatility_col)
    test_df = pd.read_parquet(test_path, columns=sorted(columns))
    frame = pred_df.join(test_df, how="left")
    return target_col, frame


def _season_labels(index: pd.Index) -> pd.Series:
    if not isinstance(index, pd.DatetimeIndex):
        raise TypeError("season segmentation requires a DatetimeIndex")

    def _season(month: int) -> str:
        if month in (12, 1, 2):
            return "DJF"
        if month in (3, 4, 5):
            return "MAM"
        if month in (6, 7, 8):
            return "JJA"
        return "SON"

    return pd.Series([_season(int(month)) for month in index.month], index=index, dtype="object")


def _weekpart_labels(index: pd.Index) -> pd.Series:
    if not isinstance(index, pd.DatetimeIndex):
        raise TypeError("weekpart segmentation requires a DatetimeIndex")
    values = np.where(index.dayofweek >= 5, "weekend", "weekday")
    return pd.Series(values, index=index, dtype="object")


def _bool_labels(series: pd.Series, *, positive: str, negative: str) -> pd.Series:
    labels = pd.Series(index=series.index, dtype="object")
    labels.loc[series.astype(bool)] = positive
    labels.loc[~series.astype(bool)] = negative
    return labels


def _quantile_labels(series: pd.Series, *, prefix: str) -> tuple[pd.Series, dict[str, float]]:
    clean = series.dropna().astype(float)
    if len(clean) == 0:
        raise ValueError(f"{prefix} segmentation requires non-empty values")
    q_low = float(clean.quantile(_QUANTILE_LOW))
    q_high = float(clean.quantile(_QUANTILE_HIGH))
    bins = pd.Series(index=series.index, dtype="object")
    bins.loc[series <= q_low] = "low"
    bins.loc[(series > q_low) & (series <= q_high)] = "mid"
    bins.loc[series > q_high] = "high"
    return bins, {"q33": q_low, "q67": q_high}


def summarize_segments(
    frame: pd.DataFrame,
    *,
    family: str,
    labels: pd.Series,
    target_col: str,
    source_col: str | None = None,
    thresholds: dict[str, float] | None = None,
) -> pd.DataFrame:
    aligned = frame[["y_true", "y_pred"]].join(labels.rename("segment"), how="left")
    aligned = aligned.dropna(subset=["segment"])
    rows: list[dict[str, float | str | int | None]] = []
    for segment, group in aligned.groupby("segment", sort=True):
        y_true = group["y_true"].to_numpy(dtype=np.float64)
        y_pred = group["y_pred"].to_numpy(dtype=np.float64)
        rows.append(
            {
                "target_col": target_col,
                "family": family,
                "segment": str(segment),
                "n": int(len(group)),
                "rmse": float(rmse(y_true, y_pred)),
                "mae": float(mae(y_true, y_pred)),
                "r2": float(r2(y_true, y_pred)),
                "source_col": source_col,
                "q33": np.nan if not thresholds else thresholds.get("q33"),
                "q67": np.nan if not thresholds else thresholds.get("q67"),
            }
        )
    return pd.DataFrame(rows)


def analyze_frame(frame: pd.DataFrame, *, target_col: str, families: list[str] | None = None) -> pd.DataFrame:
    selected = families or list(_TARGET_FAMILIES.get(infer_target_family(target_col), ()))
    if not selected:
        raise ValueError(f"no default stratified analyses configured for {target_col}")

    builders: dict[str, Callable[[], pd.DataFrame]] = {
        "season": lambda: summarize_segments(
            frame,
            family="season",
            labels=_season_labels(frame.index),
            target_col=target_col,
        ),
        "weekpart": lambda: summarize_segments(
            frame,
            family="weekpart",
            labels=_weekpart_labels(frame.index),
            target_col=target_col,
        ),
        "day_night": lambda: summarize_segments(
            frame,
            family="day_night",
            labels=_bool_labels(frame["is_night"].fillna(False), positive="night", negative="day"),
            target_col=target_col,
            source_col="is_night",
        ),
        "ghi_quantile": lambda: _summarize_ghi_quantiles(frame, target_col),
        "wind_quantile": lambda: _summarize_quantiles(frame, target_col, source_col="wind_speed_10m_m_s", family="wind_quantile"),
        "volatility": lambda: _summarize_volatility(frame, target_col),
    }

    outputs: list[pd.DataFrame] = []
    for family in selected:
        if family not in builders:
            raise ValueError(f"unsupported family: {family}")
        outputs.append(builders[family]())
    return pd.concat(outputs, ignore_index=True)


def _summarize_quantiles(frame: pd.DataFrame, target_col: str, *, source_col: str, family: str) -> pd.DataFrame:
    labels, thresholds = _quantile_labels(frame[source_col], prefix=family)
    return summarize_segments(frame, family=family, labels=labels, target_col=target_col, source_col=source_col, thresholds=thresholds)


def _summarize_ghi_quantiles(frame: pd.DataFrame, target_col: str) -> pd.DataFrame:
    day_frame = frame.copy()
    if "is_night" in day_frame.columns:
        day_frame = day_frame.loc[~day_frame["is_night"].fillna(False)].copy()
    return _summarize_quantiles(day_frame, target_col, source_col="ghi_w_m2", family="ghi_quantile")


def _summarize_volatility(frame: pd.DataFrame, target_col: str) -> pd.DataFrame:
    source_col = infer_volatility_col(target_col)
    if not source_col or source_col not in frame.columns:
        raise ValueError(f"volatility segmentation requires {source_col!r} in frame")
    volatility = frame[source_col].abs()
    labels, thresholds = _quantile_labels(volatility, prefix="volatility")
    return summarize_segments(frame, family="volatility", labels=labels, target_col=target_col, source_col=source_col, thresholds=thresholds)
