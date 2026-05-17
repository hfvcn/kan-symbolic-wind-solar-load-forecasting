from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

import torch

from src.kan_sr.prune import prune_kan_model
from src.kan_sr.sparsity import compute_edge_sparsity
from src.local.kan_train_config import TrainConfig, prune_candidates_for_profile
from src.local.kan_train_core import evaluate

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PruneRecord:
    candidate: dict[str, float]
    sparsity: dict[str, float | int]
    eval_val: dict[str, float]
    rmse_ok: bool
    sparse_ok: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "candidate": dict(self.candidate),
            "sparsity": dict(self.sparsity),
            "eval_val": dict(self.eval_val),
            "rmse_ok": bool(self.rmse_ok),
            "sparse_ok": bool(self.sparse_ok),
        }


def _eval_candidate(
    model: Any,
    dataset: dict[str, torch.Tensor],
    *,
    target_scaler: dict[str, float] | None,
    baseline_rmse: float,
    cfg: TrainConfig,
    cand: dict[str, float],
) -> PruneRecord:
    pruned = prune_kan_model(model, dataset["train_input"], node_th=float(cand["node_th"]), edge_th=float(cand["edge_th"]))
    sparsity = compute_edge_sparsity(pruned)
    eval_pruned = evaluate(pruned, dataset["test_input"], dataset["test_label"], target_scaler=target_scaler)

    rmse_ok = float(eval_pruned["rmse"]) <= float(baseline_rmse) * float(cfg.max_rmse_degrade_ratio)
    sparse_ok = float(sparsity.pruned_ratio) >= float(cfg.target_pruned_ratio)
    return PruneRecord(
        candidate=cand,
        sparsity=sparsity.as_dict(),
        eval_val=eval_pruned,
        rmse_ok=rmse_ok,
        sparse_ok=sparse_ok,
    )


def _pick_best_prune_record(records: list[PruneRecord]) -> tuple[PruneRecord, str]:
    """
    Match Modal pruning selection semantics:
    - If both constraints satisfied: prefer lowest RMSE, then higher sparsity.
    - If only RMSE satisfied: prefer higher sparsity, then lower RMSE.
    - If only sparsity satisfied: pick lowest RMSE among those.
    - Else: pick lowest RMSE overall.
    """
    if not records:
        raise ValueError("records must be non-empty")

    good = [r for r in records if r.rmse_ok and r.sparse_ok]
    rmse_only = [r for r in records if r.rmse_ok and (not r.sparse_ok)]
    sparse_only = [r for r in records if (not r.rmse_ok) and r.sparse_ok]

    if good:
        best = min(good, key=lambda r: (float(r.eval_val["rmse"]), -float(r.sparsity["pruned_ratio"])))
        return best, "both_ok"
    if rmse_only:
        best = max(rmse_only, key=lambda r: (float(r.sparsity["pruned_ratio"]), -float(r.eval_val["rmse"])))
        return best, "rmse_ok_only"
    if sparse_only:
        best = min(sparse_only, key=lambda r: float(r.eval_val["rmse"]))
        return best, "sparse_ok_only"
    best = min(records, key=lambda r: float(r.eval_val["rmse"]))
    return best, "min_rmse"


def search_best_prune(
    model: Any,
    dataset: dict[str, torch.Tensor],
    *,
    target_scaler: dict[str, float] | None,
    baseline_rmse: float,
    cfg: TrainConfig,
    candidates: tuple[dict[str, float], ...] | None = None,
) -> PruneRecord:
    state_before = {k: v.detach().clone() for k, v in model.state_dict().items()}
    _ = model(dataset["train_input"])

    prune_records: list[PruneRecord] = []
    active_candidates = tuple(candidates or prune_candidates_for_profile(cfg.prune_candidate_profile))
    for cand in active_candidates:
        model.load_state_dict(state_before, strict=True)
        try:
            rec = _eval_candidate(
                model,
                dataset,
                target_scaler=target_scaler,
                baseline_rmse=float(baseline_rmse),
                cfg=cfg,
                cand=dict(cand),
            )
        except Exception as e:  # noqa: BLE001
            logger.warning("Prune candidate failed (node_th=%s edge_th=%s): %s", cand.get("node_th"), cand.get("edge_th"), e)
            continue
        prune_records.append(rec)

    if not prune_records:
        raise RuntimeError("No prune candidate succeeded")
    best, _mode = _pick_best_prune_record(prune_records)
    return best


def apply_prune(model: Any, dataset: dict[str, torch.Tensor], *, record: PruneRecord) -> Any:
    _ = model(dataset["train_input"])
    return prune_kan_model(
        model,
        dataset["train_input"],
        node_th=float(record.candidate["node_th"]),
        edge_th=float(record.candidate["edge_th"]),
    )
