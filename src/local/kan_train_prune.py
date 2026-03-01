from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import torch

from src.kan_sr.prune import prune_kan_model
from src.kan_sr.sparsity import compute_edge_sparsity
from src.local.kan_train_config import DEFAULT_PRUNE_CANDIDATES, TrainConfig
from src.local.kan_train_core import evaluate


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


def _is_better(best: PruneRecord, rec: PruneRecord) -> bool:
    best_good = bool(best.rmse_ok and best.sparse_ok)
    rec_good = bool(rec.rmse_ok and rec.sparse_ok)
    if rec_good and not best_good:
        return True
    if rec_good and best_good:
        if float(rec.sparsity["pruned_ratio"]) > float(best.sparsity["pruned_ratio"]):
            return True
        if float(rec.sparsity["pruned_ratio"]) == float(best.sparsity["pruned_ratio"]) and float(rec.eval_val["rmse"]) < float(best.eval_val["rmse"]):
            return True
        return False
    if (not rec_good) and (not best_good):
        if float(rec.sparsity["pruned_ratio"]) > float(best.sparsity["pruned_ratio"]):
            return True
        if float(rec.sparsity["pruned_ratio"]) == float(best.sparsity["pruned_ratio"]) and float(rec.eval_val["rmse"]) < float(best.eval_val["rmse"]):
            return True
        return False
    return False


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


def search_best_prune(
    model: Any,
    dataset: dict[str, torch.Tensor],
    *,
    target_scaler: dict[str, float] | None,
    baseline_rmse: float,
    cfg: TrainConfig,
    candidates: tuple[dict[str, float], ...] = DEFAULT_PRUNE_CANDIDATES,
) -> PruneRecord:
    state_before = {k: v.detach().clone() for k, v in model.state_dict().items()}
    _ = model(dataset["train_input"])

    best: Optional[PruneRecord] = None
    for cand in candidates:
        model.load_state_dict(state_before, strict=True)
        rec = _eval_candidate(
            model,
            dataset,
            target_scaler=target_scaler,
            baseline_rmse=float(baseline_rmse),
            cfg=cfg,
            cand=dict(cand),
        )
        if best is None or _is_better(best, rec):
            best = rec

    if best is None:
        raise RuntimeError("No prune candidate succeeded")
    return best


def apply_prune(model: Any, dataset: dict[str, torch.Tensor], *, record: PruneRecord) -> Any:
    _ = model(dataset["train_input"])
    return prune_kan_model(
        model,
        dataset["train_input"],
        node_th=float(record.candidate["node_th"]),
        edge_th=float(record.candidate["edge_th"]),
    )

