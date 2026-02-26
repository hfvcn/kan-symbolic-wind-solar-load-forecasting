from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import sympy as sp


@dataclass(frozen=True)
class SeparabilityReport:
    free_symbols: list[str]
    additive_separable: bool
    multiplicative_separable: bool
    additive_components: list[list[str]]
    multiplicative_components: list[list[str]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "free_symbols": list(self.free_symbols),
            "additive_separable": bool(self.additive_separable),
            "multiplicative_separable": bool(self.multiplicative_separable),
            "additive_components": [list(c) for c in self.additive_components],
            "multiplicative_components": [list(c) for c in self.multiplicative_components],
        }


def _union_find_components(symbol_sets: list[set[sp.Symbol]]) -> list[set[sp.Symbol]]:
    all_syms: set[sp.Symbol] = set()
    for s in symbol_sets:
        all_syms |= set(s)

    parent: dict[sp.Symbol, sp.Symbol] = {s: s for s in all_syms}

    def find(x: sp.Symbol) -> sp.Symbol:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: sp.Symbol, b: sp.Symbol) -> None:
        ra = find(a)
        rb = find(b)
        if ra != rb:
            parent[rb] = ra

    for s in symbol_sets:
        s = set(s)
        if len(s) <= 1:
            continue
        first = next(iter(s))
        for other in s:
            union(first, other)

    comps: dict[sp.Symbol, set[sp.Symbol]] = {}
    for s in all_syms:
        r = find(s)
        comps.setdefault(r, set()).add(s)
    return list(comps.values())


def detect_separability(expr: sp.Expr) -> SeparabilityReport:
    expr_s = sp.simplify(expr)
    syms = sorted(expr_s.free_symbols, key=lambda s: s.name)

    # Additive: components derived from term symbol co-occurrence.
    terms = list(expr_s.args) if isinstance(expr_s, sp.Add) else [expr_s]
    term_sets = [set(t.free_symbols) for t in terms if t.free_symbols]
    add_comps = _union_find_components(term_sets) if term_sets else []

    # Multiplicative: factor then components derived from factor symbol co-occurrence.
    factored = sp.factor_terms(expr_s)
    factors = list(factored.args) if isinstance(factored, sp.Mul) else [factored]
    factor_sets = [set(f.free_symbols) for f in factors if f.free_symbols]
    mul_comps = _union_find_components(factor_sets) if factor_sets else []

    add_components = [sorted([s.name for s in c]) for c in add_comps]
    mul_components = [sorted([s.name for s in c]) for c in mul_comps]

    return SeparabilityReport(
        free_symbols=[s.name for s in syms],
        additive_separable=len(add_components) > 1,
        multiplicative_separable=len(mul_components) > 1,
        additive_components=sorted(add_components),
        multiplicative_components=sorted(mul_components),
    )

