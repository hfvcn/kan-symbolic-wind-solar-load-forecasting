from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
import sympy as sp

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)


DEFAULT_SYMBOLIC_LIB: tuple[str, ...] = (
    "x",
    "x^2",
    "x^3",
    "x^4",
    "sin",
    "cos",
    "exp",
    "abs",
    "gaussian",
)


@dataclass(frozen=True)
class SymbolicEdgeFit:
    layer: int
    i: int
    j: int
    best_name: str
    r2: float
    complexity: float
    fixed: bool
    fixed_as: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "layer": int(self.layer),
            "i": int(self.i),
            "j": int(self.j),
            "best_name": str(self.best_name),
            "r2": float(self.r2),
            "complexity": float(self.complexity),
            "fixed": bool(self.fixed),
            "fixed_as": str(self.fixed_as),
        }


def sympy_complexity(expr: sp.Expr) -> dict[str, Any]:
    """
    Compute simple, stable complexity metrics for Pareto analysis.
    """

    def depth(e: sp.Basic) -> int:
        if not getattr(e, "args", None):
            return 1
        return 1 + max(depth(a) for a in e.args)

    nodes = list(sp.preorder_traversal(expr))
    func_nodes = [n for n in nodes if isinstance(n, sp.Function)]
    sym_nodes = [n for n in nodes if isinstance(n, sp.Symbol)]
    num_nodes = [n for n in nodes if isinstance(n, sp.Number)]

    return {
        "node_count": int(len(nodes)),
        "function_count": int(len(func_nodes)),
        "symbol_count": int(len(set(sym_nodes))),
        "number_count": int(len(num_nodes)),
        "tree_depth": int(depth(expr)),
    }


def extract_symbolic_edges(
    model: Any,
    *,
    lib: Iterable[str] = DEFAULT_SYMBOLIC_LIB,
    r2_threshold: float = 0.99,
    weight_simple: float = 0.9,
    fix_below_threshold_to_zero: bool = False,
    a_range: tuple[float, float] = (-10, 10),
    b_range: tuple[float, float] = (-10, 10),
) -> list[SymbolicEdgeFit]:
    """
    Suggest and (optionally) fix symbolic functions per edge.

    Notes:
        - `model` is expected to be a `kan.KAN` instance (MultKAN).
        - Call a forward pass on representative inputs before this function so
          internal activations are available for symbolic fitting.
    """
    fits: list[SymbolicEdgeFit] = []

    for l in range(len(model.width_in) - 1):
        for i in range(model.width_in[l]):
            for j in range(model.width_out[l + 1]):
                # If pruned, fix to 0 for clean formulas.
                if model.symbolic_fun[l].mask[j, i] == 0.0 and model.act_fun[l].mask[i][j] == 0.0:
                    model.fix_symbolic(l, i, j, "0", verbose=False, log_history=False)
                    fits.append(
                        SymbolicEdgeFit(
                            layer=l,
                            i=i,
                            j=j,
                            best_name="0",
                            r2=1.0,
                            complexity=0.0,
                            fixed=True,
                            fixed_as="0",
                        )
                    )
                    continue

                best_name, _fun, r2, c = model.suggest_symbolic(
                    l,
                    i,
                    j,
                    a_range=a_range,
                    b_range=b_range,
                    lib=list(lib),
                    verbose=False,
                    weight_simple=weight_simple,
                )

                fixed = False
                fixed_as = ""

                if float(r2) >= r2_threshold:
                    model.fix_symbolic(l, i, j, best_name, verbose=False, log_history=False)
                    fixed = True
                    fixed_as = best_name
                elif fix_below_threshold_to_zero:
                    model.fix_symbolic(l, i, j, "0", verbose=False, log_history=False)
                    fixed = True
                    fixed_as = "0"

                fits.append(
                    SymbolicEdgeFit(
                        layer=l,
                        i=i,
                        j=j,
                        best_name=str(best_name),
                        r2=float(r2),
                        complexity=float(c),
                        fixed=fixed,
                        fixed_as=str(fixed_as),
                    )
                )

    return fits


def build_symbolic_formula(
    model: Any,
    *,
    feature_cols: list[str],
    input_normalizer: dict[str, Any] | None = None,
    output_normalizer: dict[str, Any] | None = None,
) -> sp.Expr:
    """
    Build a SymPy expression for the first output neuron.
    """
    means = None
    stds = None
    if input_normalizer is not None:
        means = input_normalizer["mean"]
        stds = input_normalizer["std"]

    out_means = None
    out_stds = None
    if output_normalizer is not None:
        out_means = output_normalizer["mean"]
        out_stds = output_normalizer["std"]

    normalizer = [means, stds] if means is not None and stds is not None else None
    output_norm = [out_means, out_stds] if out_means is not None and out_stds is not None else None

    formula_list, _ = model.symbolic_formula(var=feature_cols, normalizer=normalizer, output_normalizer=output_norm)
    if not formula_list:
        raise ValueError("symbolic_formula returned empty output list")
    expr = formula_list[0]
    return sp.simplify(expr)


def evaluate_symbolic_formula(
    expr: sp.Expr,
    *,
    feature_cols: list[str],
    x_df,
) -> np.ndarray:
    """
    Vectorized evaluation of a SymPy expression on a DataFrame.
    """
    f = sp.lambdify(feature_cols, expr, modules="numpy")
    args = [np.asarray(x_df[c].to_numpy()) for c in feature_cols]
    pred = f(*args)
    return np.asarray(pred, dtype=np.float64).reshape(-1)

