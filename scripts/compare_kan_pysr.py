#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    ap = argparse.ArgumentParser(description="Compare seeded PySR equations with KAN symbolic seeds (Phase 7).")
    ap.add_argument("--pysr-run", required=True, help="Path to synced PySR run directory (runs/<id>).")
    ap.add_argument("--symbolic-run", required=True, help="Path to synced KAN symbolic run directory (runs/<id>).")
    ap.add_argument("--out-dir", default="doc/paper_assets", help="Output directory.")
    args = ap.parse_args()

    pysr_run = Path(args.pysr_run)
    sym_run = Path(args.symbolic_run)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = _read_json(pysr_run / "payload.json")
    feature_cols = payload.get("feature_cols", [])
    seed_names = [c for c in feature_cols if str(c).startswith("seed_")]

    seed_meta_path = pysr_run / "artifacts" / "seed_features.json"
    seed_meta = _read_json(seed_meta_path) if seed_meta_path.exists() else None

    eq_path = pysr_run / "artifacts" / "equations.csv"
    if not eq_path.exists():
        raise FileNotFoundError(f"equations.csv not found: {eq_path}")
    eq_df = pd.read_csv(eq_path)

    sym_col = "sympy_format" if "sympy_format" in eq_df.columns else ("equation" if "equation" in eq_df.columns else None)
    if sym_col is None:
        raise ValueError("equations.csv missing sympy/equation column")

    eq_strs = eq_df[sym_col].astype(str).tolist()
    used = []
    for s in eq_strs:
        used.append(any(n in s for n in seed_names))
    used_count = int(sum(bool(u) for u in used))

    best_text_path = pysr_run / "artifacts" / "best_equation.txt"
    best_text = best_text_path.read_text() if best_text_path.exists() else ""
    best_uses_seed = any(n in best_text for n in seed_names)

    md = []
    md.append("# KAN ↔ PySR Cross-Validation Report")
    md.append("")
    md.append(f"- pysr_run: `{pysr_run.name}`")
    md.append(f"- symbolic_run: `{sym_run.name}`")
    md.append(f"- n_seed_features: `{len(seed_names)}`")
    md.append(f"- equations_using_seeds: `{used_count}` / `{len(eq_strs)}`")
    md.append(f"- best_equation_uses_seed: `{bool(best_uses_seed)}`")
    md.append("")
    if seed_meta is not None:
        md.append("## Seed Features")
        md.append("")
        for s in (seed_meta.get("seeds") or [])[:10]:
            md.append(f"- `{s.get('name')}` (nodes={s.get('node_count')}, symbols={s.get('symbol_count')}): `{s.get('expr')}`")
        md.append("")

    md.append("## Notes")
    md.append("")
    md.append("- Seed usage indicates PySR explicitly selected KAN-derived sub-expressions as building blocks.")
    md.append("- This is evidence for independent cross-checking (EVAL-08), not a proof of causal physics.")
    md.append("")

    out_path = out_dir / f"kan_pysr_cross_validation_{pysr_run.name}.md"
    out_path.write_text("\n".join(md) + "\n")


if __name__ == "__main__":
    main()

