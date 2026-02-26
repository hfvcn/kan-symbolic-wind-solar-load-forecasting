from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import sympy as sp


@dataclass(frozen=True)
class SeedFeature:
    name: str
    expr: sp.Expr
    node_count: int
    symbol_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "expr": str(self.expr),
            "node_count": int(self.node_count),
            "symbol_count": int(self.symbol_count),
        }


def _node_count(expr: sp.Expr) -> int:
    return int(sum(1 for _ in sp.preorder_traversal(expr)))


def _symbol_count(expr: sp.Expr) -> int:
    return int(len({s for s in expr.free_symbols if isinstance(s, sp.Symbol)}))


def extract_seed_features(
    expr: sp.Expr,
    *,
    max_seeds: int = 8,
    max_nodes: int = 60,
    min_nodes: int = 4,
    require_multi_symbol: bool = True,
) -> list[SeedFeature]:
    """
    Extract a small set of evaluatable sub-expressions as seed features (Phase 7).

    Philosophy:
      - Keep seeds small enough for stable evaluation
      - Prefer sub-expressions involving multiple symbols (captures structure)
      - Exclude trivial symbols/constants and the full expression itself
    """
    candidates: dict[str, sp.Expr] = {}
    for node in sp.preorder_traversal(expr):
        if not isinstance(node, sp.Expr):
            continue
        if node == expr:
            continue
        if isinstance(node, (sp.Symbol, sp.Number)):
            continue

        nc = _node_count(node)
        if nc < int(min_nodes) or nc > int(max_nodes):
            continue

        sc = _symbol_count(node)
        if require_multi_symbol and sc < 2:
            continue

        key = str(node)
        candidates.setdefault(key, node)

    scored: list[tuple[int, int, int, str, sp.Expr]] = []
    for k, node in candidates.items():
        sc = _symbol_count(node)
        nc = _node_count(node)
        # Score: prioritize multi-symbol structure, then complexity.
        score = sc * 1000 + nc
        scored.append((score, sc, nc, k, node))

    scored.sort(key=lambda t: (t[0], t[1], t[2]), reverse=True)

    seeds: list[SeedFeature] = []
    for i, (_score, sc, nc, _k, node) in enumerate(scored[: int(max_seeds)], start=1):
        seeds.append(SeedFeature(name=f"seed_{i:02d}", expr=sp.simplify(node), node_count=int(nc), symbol_count=int(sc)))
    return seeds


def compute_seed_matrix(
    seeds: list[SeedFeature],
    *,
    feature_cols: list[str],
    x_df,
    min_finite_fraction: float = 0.999,
) -> tuple[np.ndarray, list[str], list[SeedFeature]]:
    """
    Evaluate seed expressions on a DataFrame, returning a matrix to append to X.

    Seeds that produce non-finite values are dropped.
    """
    if not seeds:
        return np.zeros((len(x_df), 0), dtype=np.float64), [], []

    X = x_df[feature_cols].to_numpy(dtype=np.float64)
    args_arr = [X[:, i] for i in range(X.shape[1])]

    cols: list[np.ndarray] = []
    names: list[str] = []
    kept: list[SeedFeature] = []

    for s in seeds:
        try:
            f = sp.lambdify(feature_cols, s.expr, modules="numpy")
            v = np.asarray(f(*args_arr), dtype=np.float64).reshape(-1)
            if v.shape[0] == 1 and X.shape[0] > 1:
                v = np.full((X.shape[0],), float(v[0]), dtype=np.float64)
            finite = np.isfinite(v)
            frac = float(np.mean(finite)) if len(v) else 0.0
            if frac < float(min_finite_fraction):
                continue
            cols.append(v)
            names.append(s.name)
            kept.append(s)
        except Exception:  # noqa: BLE001
            continue

    if not cols:
        return np.zeros((len(x_df), 0), dtype=np.float64), [], []

    mat = np.stack(cols, axis=1)
    return mat, names, kept

