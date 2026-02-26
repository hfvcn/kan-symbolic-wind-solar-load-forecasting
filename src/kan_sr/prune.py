from __future__ import annotations

from typing import Any

import torch


def prune_kan_model(model: Any, x: torch.Tensor, *, node_th: float, edge_th: float) -> Any:
    """
    Prune a pykan `KAN` model without triggering its checkpoint/history side-effects.

    Notes:
    - `KAN.prune()` in pykan can attempt to write `ckpt_path/history.txt` due to an internal
      `auto_save=True` model created during pruning. In batch environments (e.g., containers),
      that directory may not exist and pruning will crash.
    - This helper reproduces pruning behavior by calling `prune_node` + `prune_edge` with
      `log_history=False` and disables `auto_save` on the returned pruned model.
    """
    if not isinstance(x, torch.Tensor):
        raise TypeError("x must be a torch.Tensor")

    _ = model(x)

    pruned = model.prune_node(threshold=float(node_th), log_history=False)
    _ = pruned(x)
    pruned.attribute()
    pruned.prune_edge(threshold=float(edge_th), log_history=False)

    try:
        pruned.auto_save = False
    except Exception:  # noqa: BLE001
        pass

    return pruned

