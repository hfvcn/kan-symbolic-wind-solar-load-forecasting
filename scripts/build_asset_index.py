#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _safe_read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _infer_phase_and_kind(run_dir: Path, payload: dict) -> tuple[str, str]:
    phase = payload.get("phase")
    kind = payload.get("kind") or payload.get("cfg", {}).get("model_type")

    artifacts = run_dir / "artifacts"

    # Heuristics for older payloads (pre-standardization).
    if not phase:
        if (run_dir / "processed").exists():
            phase = "01-data-pipeline"
        elif (artifacts / "formula.sympy.txt").exists() or (artifacts / "edge_symbolic_report.csv").exists():
            phase = "03-symbolic-extraction"
        elif (artifacts / "equations.csv").exists():
            phase = "04-baselines-pysr"
        elif payload.get("fanout") is not None:
            phase = "00-smoke-test"

    if not kind:
        if phase == "01-data-pipeline":
            kind = "data_pipeline"
        elif phase == "02-kan-training":
            kind = "kan"
        elif phase == "03-symbolic-extraction":
            kind = "kan_symbolic"
        elif phase == "04-baselines-pysr":
            kind = "pysr"
        elif phase == "00-smoke-test":
            kind = "smoke_test"
        else:
            kind = "unknown"

    # Tag seeded PySR cross-validation runs.
    if phase == "04-baselines-pysr" and payload.get("seed_from_symbolic_run"):
        kind = "pysr_seeded"

    return str(phase or "unknown"), str(kind)


def main() -> None:
    ap = argparse.ArgumentParser(description="Build a thesis asset index under doc/paper_assets (Phase 8).")
    ap.add_argument("--runs-dir", default="runs", help="Local synced runs/ directory.")
    ap.add_argument("--paper-assets-dir", default="doc/paper_assets", help="Paper assets directory.")
    ap.add_argument("--figures-dir", default="doc/paper_assets/figures", help="Figures output directory.")
    ap.add_argument("--out", default="doc/paper_assets/ASSET_INDEX.md", help="Output markdown path.")
    ap.add_argument("--run", action="append", default=None, help="Optional run dir path to include (repeatable).")
    args = ap.parse_args()

    runs_dir = Path(args.runs_dir)
    paper_assets_dir = Path(args.paper_assets_dir)
    figures_dir = Path(args.figures_dir)
    out_path = Path(args.out)

    if args.run:
        run_dirs = [Path(p) for p in args.run]
    else:
        run_dirs = sorted([p for p in runs_dir.iterdir() if p.is_dir() and (p / "payload.json").exists()], key=lambda p: p.name)

    md: list[str] = []
    md.append("# Thesis Asset Index")
    md.append("")
    md.append("本文件用于汇总 `runs/` 与 `doc/paper_assets/` 下可直接用于论文撰写的产物。")
    md.append("")

    # Global assets
    md.append("## Global Tables/Plots")
    md.append("")
    if paper_assets_dir.exists():
        for name in [
            "ablation_table.csv",
            "ablation_rmse_pruned.png",
            "ablation_rmse_vs_sparsity.png",
            "comparison_table.csv",
            "transfer_gaps.csv",
            "transfer_gap_ratio.png",
            "pareto_rmse_vs_complexity.png",
        ]:
            p = paper_assets_dir / name
            if p.exists():
                md.append(f"- `{p}`")

        # Reports / interpretability assets (dynamic names).
        for p in sorted(paper_assets_dir.glob("kan_pysr_cross_validation_*.md")):
            md.append(f"- `{p}`")
        for p in sorted(paper_assets_dir.glob("physics_mapping_*.md")):
            md.append(f"- `{p}`")
        for p in sorted(paper_assets_dir.glob("sensitivity_summary_*.csv")):
            md.append(f"- `{p}`")
    md.append("")

    # Per-run assets
    md.append("## Runs")
    md.append("")
    if not run_dirs:
        md.append("_No runs found._")
    else:
        for run_dir in run_dirs:
            payload = _safe_read_json(run_dir / "payload.json")
            phase, kind = _infer_phase_and_kind(run_dir, payload)
            md.append(f"### {run_dir.name}")
            md.append("")
            md.append(f"- phase: `{phase}`")
            md.append(f"- kind: `{kind}`")

            artifacts = run_dir / "artifacts"
            if artifacts.exists():
                for rel in [
                    "eval_test.json",
                    "eval_test_reconstructed.json",
                    "eval_pruned.json",
                    "formula_eval_test.json",
                    "formula.tex",
                    "formula_reconstructed.tex",
                    "formula.sympy.txt",
                    "formula_reconstructed.sympy.txt",
                    "formula_metrics.json",
                    "equations.csv",
                    "best_equation.txt",
                    "physics_mapping.json",
                    "seed_features.json",
                    "predictions_test.parquet",
                    "predictions_test_reconstructed.parquet",
                    "feature_importance.csv",
                    "sparsity.json",
                    "separability.json",
                ]:
                    p = artifacts / rel
                    if p.exists():
                        md.append(f"- `{p}`")

            # Figures generated by make_thesis_figures.py
            if figures_dir.exists():
                figs = sorted(figures_dir.glob(f"*_{run_dir.name}.png"))
                if figs:
                    md.append("- figures:")
                    for f in figs:
                        md.append(f"  - `{f}`")

                kan_plot_dir = figures_dir / f"kan_plot_{run_dir.name}"
                if kan_plot_dir.exists():
                    md.append("- kan_plot:")
                    topo = kan_plot_dir / "topology.png"
                    if topo.exists():
                        md.append(f"  - `{topo}`")
                    # Avoid listing hundreds of spline files; just count them.
                    sp = list(kan_plot_dir.glob("sp_*.png"))
                    if sp:
                        md.append(f"  - spline_plots: `{len(sp)}` files in `{kan_plot_dir}`")
            md.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
