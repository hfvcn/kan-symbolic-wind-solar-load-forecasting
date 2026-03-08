#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _discover_manifest_commands(doc_root: Path) -> dict[str, dict[str, str]]:
    command_by_run: dict[str, dict[str, str]] = {}
    sweeps_root = doc_root / "thesis_sweeps"
    if not sweeps_root.exists():
        return command_by_run
    for manifest_path in sorted(sweeps_root.glob("*/manifest.json")):
        payload = _read_json(manifest_path)
        planned = payload.get("planned")
        if not isinstance(planned, list):
            continue
        for item in planned:
            if not isinstance(item, dict):
                continue
            run_id = item.get("run_id")
            cmd = item.get("cmd")
            if not run_id or not isinstance(cmd, list) or not cmd:
                continue
            command_by_run[str(run_id)] = {
                "manifest": str(manifest_path),
                "command": shlex.join(str(part) for part in cmd),
            }
    return command_by_run


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

    doc_root = paper_assets_dir.parent
    command_by_run = _discover_manifest_commands(doc_root)
    sweeps_root = doc_root / "thesis_sweeps"

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

        # Thesis-oriented sweep sessions (per-session outputs live under doc/thesis_sweeps/<session>/).
        if sweeps_root.exists():
            for sess in sorted([p for p in sweeps_root.iterdir() if p.is_dir()], key=lambda p: p.name):
                manifest = sess / "manifest.json"
                if manifest.exists():
                    md.append(f"- `{manifest}`")
                sess_assets = sess / "paper_assets"
                for name in ["comparison_table.csv", "pareto_rmse_vs_complexity.png", "transfer_gaps.csv", "transfer_gap_ratio.png"]:
                    p = sess_assets / name
                    if p.exists():
                        md.append(f"- `{p}`")

        # Reports / interpretability assets (dynamic names).
        for p in sorted(paper_assets_dir.glob("kan_pysr_cross_validation_*.md")):
            md.append(f"- `{p}`")
        for p in sorted(paper_assets_dir.glob("physics_mapping_*.md")):
            md.append(f"- `{p}`")
        for p in sorted(paper_assets_dir.glob("sensitivity_summary_*.csv")):
            md.append(f"- `{p}`")
        for p in sorted(paper_assets_dir.glob("wind_ablation_summary_*.csv")):
            md.append(f"- `{p}`")
        for p in sorted(paper_assets_dir.glob("PAPER_REPRO_MAP_*.md")):
            md.append(f"- `{p}`")
        for subdir in sorted([p for p in paper_assets_dir.iterdir() if p.is_dir() and p.name.startswith("paper_delivery_")], key=lambda p: p.name):
            for p in sorted(subdir.iterdir(), key=lambda path: path.name):
                if p.is_file():
                    md.append(f"- `{p}`")
    if doc_root.exists():
        for p in sorted(doc_root.glob("paper_delivery_closure_*.md")):
            md.append(f"- `{p}`")
        for p in sorted(doc_root.glob("*ablation_summary_*.csv")):
            md.append(f"- `{p}`")
    md.append("")

    # Per-run assets
    md.append("## Runs")
    md.append("")
    if not run_dirs:
        md.append("_No runs found._")
    else:
        for run_dir in run_dirs:
            payload = _read_json(run_dir / "payload.json")
            phase, kind = _infer_phase_and_kind(run_dir, payload)
            md.append(f"### {run_dir.name}")
            md.append("")
            md.append(f"- phase: `{phase}`")
            md.append(f"- kind: `{kind}`")
            command_info = command_by_run.get(run_dir.name)
            if command_info:
                md.append(f"- manifest: `{command_info['manifest']}`")
                md.append(f"- command: `{command_info['command']}`")

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
