from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

PHYSICAL_FEATURES = (
    "wind_speed_10m_m_s",
    "wind_speed_10m_m_s_cubed",
    "wind_speed_hub_est",
    "ghi_w_m2",
    "ghi_day_w_m2",
    "ghi_temp_corr_w_m2",
    "temp_2m_c",
    "cdd_18c",
    "hdd_18c",
)
DEFAULT_BOOTSTRAP_SAMPLES = 10_000
DEFAULT_RANDOM_SEED = 7
LAG_FEATURE_TOKEN = "lag_"


def seed_from_run_id(run_id: str) -> int:
    match = re.search(r"seed(\d+)", str(run_id))
    if not match:
        raise ValueError(f"Could not infer seed from run_id: {run_id}")
    return int(match.group(1))


def read_payload(run_dir: Path) -> dict[str, Any]:
    payload_path = run_dir / "payload.json"
    if not payload_path.exists():
        raise FileNotFoundError(f"Missing payload.json: {payload_path}")
    return json.loads(payload_path.read_text())


def load_feature_importance_csv(run_dir: Path) -> pd.DataFrame | None:
    path = run_dir / "artifacts" / "feature_importance.csv"
    if not path.exists():
        return None
    frame = pd.read_csv(path)
    required = {"feature", "active_edges"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing columns in {path}: {sorted(missing)}")
    return frame


def eval_pruned_rmse(run_dir: Path) -> float:
    path = run_dir / "artifacts" / "eval_pruned.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing eval_pruned.json: {path}")
    payload = json.loads(path.read_text())
    return float(payload["rmse"])


def final_test_rmse(run_dir: Path) -> float:
    path = run_dir / "artifacts" / "predictions_test.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Missing predictions_test.parquet: {path}")
    frame = pd.read_parquet(path)
    required = {"y_true", "y_pred"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing columns in {path}: {sorted(missing)}")
    err = frame["y_pred"].astype(float) - frame["y_true"].astype(float)
    return float(np.sqrt(np.mean(np.square(err.to_numpy(dtype=np.float64)))))


def feature_map_from_frame(frame: pd.DataFrame) -> dict[str, int]:
    subset = frame.loc[frame["feature"].isin(PHYSICAL_FEATURES), ["feature", "active_edges"]]
    out = {feature: 0 for feature in PHYSICAL_FEATURES}
    for row in subset.itertuples(index=False):
        out[str(row.feature)] = int(row.active_edges)
    return out


def all_feature_map_from_frame(frame: pd.DataFrame) -> dict[str, int]:
    return {str(row.feature): int(row.active_edges) for row in frame.itertuples(index=False)}


def checkpoint_path(run_dir: Path) -> Path:
    candidates = (
        run_dir / "checkpoint" / "model_refine_step50.pt",
        run_dir / "checkpoint" / "model.pt",
    )
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(f"Missing supported checkpoint under {run_dir / 'checkpoint'}")


def mask_to_numpy(mask: Any) -> np.ndarray:
    if hasattr(mask, "detach"):
        return np.asarray(mask.detach().cpu().numpy())
    return np.asarray(mask)


def feature_map_from_checkpoint(run_dir: Path, payload: dict[str, Any]) -> dict[str, int]:
    import torch

    ckpt_path = checkpoint_path(run_dir)
    try:
        ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    except TypeError:
        ckpt = torch.load(ckpt_path, map_location="cpu")
    state = ckpt.get("model_state") or ckpt.get("state_dict") or ckpt
    mask = state.get("act_fun.0.mask")
    if mask is None:
        raise ValueError(f"Missing act_fun.0.mask in checkpoint: {ckpt_path}")
    feature_cols = payload.get("feature_cols") or []
    mask_np = mask_to_numpy(mask)
    if mask_np.ndim != 2:
        raise ValueError(f"Unexpected mask ndim for {ckpt_path}: {mask_np.ndim}")
    if len(feature_cols) != int(mask_np.shape[0]):
        raise ValueError(f"feature_cols / mask shape mismatch for {run_dir.name}: {len(feature_cols)} vs {mask_np.shape[0]}")
    out = {feature: 0 for feature in PHYSICAL_FEATURES}
    active_edges = (mask_np != 0).sum(axis=1).tolist()
    for feature, count in zip(feature_cols, active_edges):
        if feature in out:
            out[str(feature)] = int(count)
    return out


def all_feature_map_from_checkpoint(run_dir: Path, payload: dict[str, Any]) -> dict[str, int]:
    import torch

    ckpt_path = checkpoint_path(run_dir)
    try:
        ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    except TypeError:
        ckpt = torch.load(ckpt_path, map_location="cpu")
    state = ckpt.get("model_state") or ckpt.get("state_dict") or ckpt
    mask = state.get("act_fun.0.mask")
    if mask is None:
        raise ValueError(f"Missing act_fun.0.mask in checkpoint: {ckpt_path}")
    feature_cols = payload.get("feature_cols") or []
    mask_np = mask_to_numpy(mask)
    if mask_np.ndim != 2:
        raise ValueError(f"Unexpected mask ndim for {ckpt_path}: {mask_np.ndim}")
    if len(feature_cols) != int(mask_np.shape[0]):
        raise ValueError(f"feature_cols / mask shape mismatch for {run_dir.name}: {len(feature_cols)} vs {mask_np.shape[0]}")
    active_edges = (mask_np != 0).sum(axis=1).tolist()
    return {str(feature): int(count) for feature, count in zip(feature_cols, active_edges)}


def load_all_feature_map(run_dir: Path, payload: dict[str, Any]) -> dict[str, int]:
    frame = load_feature_importance_csv(run_dir)
    if frame is not None:
        return all_feature_map_from_frame(frame)
    return all_feature_map_from_checkpoint(run_dir, payload)


def load_feature_map(run_dir: Path, payload: dict[str, Any]) -> dict[str, int]:
    all_features = load_all_feature_map(run_dir, payload)
    return {feature: int(all_features.get(feature, 0)) for feature in PHYSICAL_FEATURES}


def lag_edge_count(feature_map: dict[str, int]) -> int:
    return int(sum(count for feature, count in feature_map.items() if LAG_FEATURE_TOKEN in str(feature)))


def paired_bootstrap_ci(diffs: np.ndarray, *, samples: int, seed: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    draws = np.empty(samples, dtype=np.float64)
    size = len(diffs)
    for idx in range(samples):
        sample_idx = rng.integers(0, size, size=size)
        draws[idx] = float(np.mean(diffs[sample_idx]))
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def paired_rows(unblocked_dirs: list[Path], blocked_dirs: list[Path]) -> list[dict[str, object]]:
    if len(unblocked_dirs) != len(blocked_dirs):
        raise ValueError("unblocked and blocked runs must have the same count")
    blocked_by_seed = {seed_from_run_id(path.name): path for path in blocked_dirs}
    rows: list[dict[str, object]] = []
    for unblocked_dir in sorted(unblocked_dirs, key=lambda item: seed_from_run_id(item.name)):
        seed = seed_from_run_id(unblocked_dir.name)
        blocked_dir = blocked_by_seed.get(seed)
        if blocked_dir is None:
            raise ValueError(f"Missing blocked run for seed={seed}")
        unblocked_payload = read_payload(unblocked_dir)
        blocked_payload = read_payload(blocked_dir)
        unblocked_target = unblocked_payload.get("target_col") or (unblocked_payload.get("cfg") or {}).get("target_col")
        blocked_target = blocked_payload.get("target_col") or (blocked_payload.get("cfg") or {}).get("target_col")
        if str(unblocked_target) != str(blocked_target):
            raise ValueError(f"target_col mismatch for seed={seed}")
        unblocked_all_map = load_all_feature_map(unblocked_dir, unblocked_payload)
        blocked_all_map = load_all_feature_map(blocked_dir, blocked_payload)
        unblocked_map = {feature: int(unblocked_all_map.get(feature, 0)) for feature in PHYSICAL_FEATURES}
        blocked_map = {feature: int(blocked_all_map.get(feature, 0)) for feature in PHYSICAL_FEATURES}
        unblocked_edge_count = int(sum(unblocked_map.values()))
        blocked_edge_count = int(sum(blocked_map.values()))
        unblocked_total_edges = int(sum(unblocked_all_map.values()))
        blocked_total_edges = int(sum(blocked_all_map.values()))
        unblocked_lag_edges = lag_edge_count(unblocked_all_map)
        blocked_lag_edges = lag_edge_count(blocked_all_map)
        unblocked_pruned = eval_pruned_rmse(unblocked_dir)
        blocked_pruned = eval_pruned_rmse(blocked_dir)
        unblocked_final = final_test_rmse(unblocked_dir)
        blocked_final = final_test_rmse(blocked_dir)
        row: dict[str, object] = {
            "seed": seed,
            "unblocked_run_id": unblocked_dir.name,
            "blocked_run_id": blocked_dir.name,
            "unblocked_any_physical": int(any(count > 0 for count in unblocked_map.values())),
            "blocked_any_physical": int(any(count > 0 for count in blocked_map.values())),
            "delta_any_physical": int(any(count > 0 for count in blocked_map.values())) - int(any(count > 0 for count in unblocked_map.values())),
            "unblocked_edge_count": unblocked_edge_count,
            "blocked_edge_count": blocked_edge_count,
            "delta_edge_count": blocked_edge_count - unblocked_edge_count,
            "unblocked_total_edges": unblocked_total_edges,
            "blocked_total_edges": blocked_total_edges,
            "delta_total_edges": blocked_total_edges - unblocked_total_edges,
            "unblocked_lag_edge_count": unblocked_lag_edges,
            "blocked_lag_edge_count": blocked_lag_edges,
            "delta_lag_edge_count": blocked_lag_edges - unblocked_lag_edges,
            "unblocked_physical_edge_share": float(unblocked_edge_count / unblocked_total_edges) if unblocked_total_edges else 0.0,
            "blocked_physical_edge_share": float(blocked_edge_count / blocked_total_edges) if blocked_total_edges else 0.0,
            "delta_physical_edge_share": (float(blocked_edge_count / blocked_total_edges) if blocked_total_edges else 0.0)
            - (float(unblocked_edge_count / unblocked_total_edges) if unblocked_total_edges else 0.0),
            "unblocked_lag_edge_share": float(unblocked_lag_edges / unblocked_total_edges) if unblocked_total_edges else 0.0,
            "blocked_lag_edge_share": float(blocked_lag_edges / blocked_total_edges) if blocked_total_edges else 0.0,
            "delta_lag_edge_share": (float(blocked_lag_edges / blocked_total_edges) if blocked_total_edges else 0.0)
            - (float(unblocked_lag_edges / unblocked_total_edges) if unblocked_total_edges else 0.0),
            "unblocked_pruned_rmse": unblocked_pruned,
            "blocked_pruned_rmse": blocked_pruned,
            "delta_pruned_rmse": blocked_pruned - unblocked_pruned,
            "unblocked_final_test_rmse": unblocked_final,
            "blocked_final_test_rmse": blocked_final,
            "delta_final_test_rmse": blocked_final - unblocked_final,
        }
        for feature in PHYSICAL_FEATURES:
            row[f"unblocked_{feature}"] = unblocked_map[feature]
            row[f"blocked_{feature}"] = blocked_map[feature]
            row[f"delta_{feature}"] = blocked_map[feature] - unblocked_map[feature]
        rows.append(row)
    return rows


def summary_rows(detail_rows: list[dict[str, object]], *, samples: int, seed: int) -> list[dict[str, object]]:
    frame = pd.DataFrame(detail_rows).sort_values("seed")

    def add_metric(metric: str, unblocked: np.ndarray, blocked: np.ndarray) -> dict[str, object]:
        diffs = blocked - unblocked
        ci_low, ci_high = paired_bootstrap_ci(diffs, samples=samples, seed=seed)
        return {
            "metric": metric,
            "n": int(len(diffs)),
            "unblocked_mean": float(np.mean(unblocked)),
            "blocked_mean": float(np.mean(blocked)),
            "delta_mean": float(np.mean(diffs)),
            "ci95_low": ci_low,
            "ci95_high": ci_high,
        }

    rows = [
        add_metric(
            "any_physical_ver",
            frame["unblocked_any_physical"].to_numpy(dtype=np.float64),
            frame["blocked_any_physical"].to_numpy(dtype=np.float64),
        ),
        add_metric(
            "physical_edge_count",
            frame["unblocked_edge_count"].to_numpy(dtype=np.float64),
            frame["blocked_edge_count"].to_numpy(dtype=np.float64),
        ),
        add_metric(
            "total_edge_count",
            frame["unblocked_total_edges"].to_numpy(dtype=np.float64),
            frame["blocked_total_edges"].to_numpy(dtype=np.float64),
        ),
        add_metric(
            "lag_edge_count",
            frame["unblocked_lag_edge_count"].to_numpy(dtype=np.float64),
            frame["blocked_lag_edge_count"].to_numpy(dtype=np.float64),
        ),
        add_metric(
            "physical_edge_share",
            frame["unblocked_physical_edge_share"].to_numpy(dtype=np.float64),
            frame["blocked_physical_edge_share"].to_numpy(dtype=np.float64),
        ),
        add_metric(
            "lag_edge_share",
            frame["unblocked_lag_edge_share"].to_numpy(dtype=np.float64),
            frame["blocked_lag_edge_share"].to_numpy(dtype=np.float64),
        ),
        add_metric(
            "pruned_rmse",
            frame["unblocked_pruned_rmse"].to_numpy(dtype=np.float64),
            frame["blocked_pruned_rmse"].to_numpy(dtype=np.float64),
        ),
        add_metric(
            "final_test_rmse",
            frame["unblocked_final_test_rmse"].to_numpy(dtype=np.float64),
            frame["blocked_final_test_rmse"].to_numpy(dtype=np.float64),
        ),
    ]
    for feature in PHYSICAL_FEATURES:
        rows.append(
            add_metric(
                f"ver::{feature}",
                (frame[f"unblocked_{feature}"].to_numpy(dtype=np.float64) > 0).astype(np.float64),
                (frame[f"blocked_{feature}"].to_numpy(dtype=np.float64) > 0).astype(np.float64),
            )
        )
    return rows
