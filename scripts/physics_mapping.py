#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import sympy as sp

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.physics_mapping import analyze_physics


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str))


def _md_table(rows: list[dict], headers: list[str]) -> str:
    def esc(x: object) -> str:
        s = "" if x is None else str(x)
        return s.replace("|", "\\|")

    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in rows:
        lines.append("| " + " | ".join(esc(r.get(h)) for h in headers) + " |")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="Map extracted symbolic formula to physical relationships (Phase 7).")
    ap.add_argument("--symbolic-run", required=True, help="Path to synced symbolic run directory (runs/<id>).")
    ap.add_argument("--data-run", default=None, help="Path to synced data pipeline run directory (runs/<data_id>). If omitted, inferred from symbolic payload.")
    ap.add_argument("--out-dir", default="doc/paper_assets", help="Output directory.")
    ap.add_argument("--max-samples", type=int, default=20000, help="Max test rows to use for derivative evaluation.")
    args = ap.parse_args()

    sym_run = Path(args.symbolic_run)
    print(f"[physics_mapping] start run={sym_run} out_dir={args.out_dir} max_samples={args.max_samples}", flush=True)
    payload = json.loads((sym_run / "payload.json").read_text())
    feature_cols = payload.get("feature_cols")
    if not feature_cols:
        raise ValueError("symbolic payload missing feature_cols")

    target_col = str(payload.get("target_col", "load"))
    data_run_id = str(payload["data_run_id"])
    data_timestamp = payload.get("data_timestamp")
    data_run = Path(args.data_run) if args.data_run else (sym_run.parent / data_run_id)

    from src.data.split import inverse_transform, load_splits_from_parquet

    processed_dir = data_run / "processed"
    _train_df, _val_df, test_df = load_splits_from_parquet(processed_dir, timestamp=data_timestamp)

    scaler_path = data_run / "artifacts" / "scaler_params.json"
    if not scaler_path.exists():
        raise FileNotFoundError(f"scaler_params.json not found: {scaler_path}")
    scaler_params = json.loads(scaler_path.read_text())

    x_test_orig = inverse_transform(test_df[feature_cols], scaler_params)
    if args.max_samples is not None and len(x_test_orig) > int(args.max_samples):
        x_test_orig = x_test_orig.iloc[: int(args.max_samples)].copy()

    expr_str = (sym_run / "artifacts" / "formula.sympy.txt").read_text()
    locals_map = {name: sp.Symbol(name, real=True) for name in feature_cols}
    expr = sp.sympify(expr_str, locals=locals_map)

    print(f"[physics_mapping] analyzing target={target_col} n_features={len(feature_cols)} n_samples={len(x_test_orig)}", flush=True)
    rep = analyze_physics(expr, feature_cols=feature_cols, x_df=x_test_orig, target_col=target_col)
    print(f"[physics_mapping] done score={rep.get('score')} n_checks={rep.get('n_checks')}", flush=True)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / f"physics_mapping_{sym_run.name}.json"
    _write_json(json_path, rep)

    # Also attach to the run itself for downstream aggregation (evaluation tables).
    _write_json(sym_run / "artifacts" / "physics_mapping.json", rep)

    # Markdown report
    tex_path = sym_run / "artifacts" / "formula.tex"
    latex = tex_path.read_text().strip() if tex_path.exists() else ""

    md_lines = []
    md_lines.append(f"# Physics Mapping Report: {sym_run.name}")
    md_lines.append("")
    md_lines.append(f"- target: `{target_col}`")
    md_lines.append(f"- data_run: `{data_run_id}` (timestamp: `{data_timestamp}`)")
    md_lines.append(f"- score: `{rep.get('score')}` (n_checks={rep.get('n_checks')})")
    md_lines.append(f"- json: `{json_path}`")
    md_lines.append("")

    if latex:
        md_lines.append("## Extracted Formula (LaTeX)")
        md_lines.append("")
        md_lines.append("$$")
        md_lines.append(latex)
        md_lines.append("$$")
        md_lines.append("")

    md_lines.append("## Checks")
    md_lines.append("")
    checks = rep.get("checks", []) or []
    if len(checks) == 0:
        md_lines.append("_No checks produced (target not supported or variables missing)._")
    else:
        # Flatten a few common details for readability
        rows = []
        for c in checks:
            det = c.get("details", {}) or {}
            ds = det.get("derivative_summary", {}) or {}
            rows.append(
                {
                    "name": c.get("name"),
                    "passed": c.get("passed"),
                    "score": c.get("score"),
                    "var": det.get("var"),
                    "pct_positive": ds.get("pct_positive"),
                    "pct_negative": ds.get("pct_negative"),
                    "power_counts": det.get("power_counts"),
                }
            )
        md_lines.append(
            _md_table(
                rows,
                headers=["name", "passed", "score", "var", "pct_positive", "pct_negative", "power_counts"],
            )
        )
    md_lines.append("")

    md_path = out_dir / f"physics_mapping_{sym_run.name}.md"
    _write_text(md_path, "\n".join(md_lines) + "\n")

    _write_text(sym_run / "artifacts" / "physics_mapping.md", "\n".join(md_lines) + "\n")


if __name__ == "__main__":
    main()
