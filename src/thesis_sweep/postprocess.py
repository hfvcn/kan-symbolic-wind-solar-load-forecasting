from __future__ import annotations

import shutil
from pathlib import Path

from src.thesis_sweep.utils import REPO_ROOT, det_run_id, local_py


def local_postprocess(*, run_ids: list[str], comp_runs: dict[str, str], session_id: str, session_dir: Path) -> list[str]:
    run_ids_out = list(run_ids)
    run_paths = [str(REPO_ROOT / "runs" / rid) for rid in run_ids_out if (REPO_ROOT / "runs" / rid).exists()]
    if run_paths:
        local_py(REPO_ROOT / "scripts" / "reconstruct_predictions.py", sum([["--run", p] for p in run_paths], []), dry_run=False)

    if comp_runs:
        combo_id = det_run_id(session_id, "s3_combo_net_load")
        local_py(
            REPO_ROOT / "scripts" / "combine_net_load_runs.py",
            [
                "--load-run",
                str(REPO_ROOT / "runs" / comp_runs["load"]),
                "--wind-run",
                str(REPO_ROOT / "runs" / comp_runs["wind"]),
                "--solar-run",
                str(REPO_ROOT / "runs" / comp_runs["solar"]),
                "--out-run-id",
                combo_id,
                "--out-runs-dir",
                "runs",
            ],
            dry_run=False,
        )
        run_ids_out.append(combo_id)

    out_dir = session_dir / "paper_assets"
    out_dir.mkdir(parents=True, exist_ok=True)
    eval_args = sum([["--run", str(REPO_ROOT / "runs" / rid)] for rid in run_ids_out if (REPO_ROOT / "runs" / rid).exists()], [])
    if eval_args:
        local_py(REPO_ROOT / "scripts" / "evaluate_runs.py", eval_args + ["--out-dir", str(out_dir)], dry_run=False)

    paper_session_dir = REPO_ROOT / "doc" / "paper_assets" / f"thesis_sweep_{session_id}"
    if out_dir.exists():
        if paper_session_dir.exists():
            shutil.rmtree(paper_session_dir)
        shutil.copytree(out_dir, paper_session_dir)
        local_py(REPO_ROOT / "scripts" / "build_asset_index.py", [], dry_run=False)

    return run_ids_out
