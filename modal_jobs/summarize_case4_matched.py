from __future__ import annotations

import json
import os
from pathlib import Path

import modal

APP_NAME = "kan-sr-summarize-case4-matched"
DEFAULT_VOLUME_NAME = os.environ.get("KAN_SR_VOLUME", "kan-sr")
VOLUME_MOUNT = "/vol"

app = modal.App(APP_NAME)
volume = modal.Volume.from_name(DEFAULT_VOLUME_NAME, create_if_missing=True)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("numpy>=1.24", "pandas>=2.0", "torch>=2.1", "pyarrow>=14.0")
    .env({"PYTHONPATH": "/root/project"})
    .add_local_dir(SRC_DIR, remote_path="/root/project/src")
)


def _parse_csv_arg(value: str) -> list[str]:
    return [item.strip() for item in str(value).split(",") if item.strip()]


@app.function(image=image, volumes={VOLUME_MOUNT: volume}, timeout=3600)
def summarize_case4_matched_remote(
    *,
    unblocked_run_ids: list[str],
    blocked_run_ids: list[str],
    bootstrap_samples: int,
    seed: int,
) -> dict[str, list[dict[str, object]]]:
    from src.eval.case4_matched import paired_rows, summary_rows

    runs_root = Path(VOLUME_MOUNT) / "runs"
    unblocked_dirs = [runs_root / run_id for run_id in unblocked_run_ids]
    blocked_dirs = [runs_root / run_id for run_id in blocked_run_ids]
    detail = paired_rows(unblocked_dirs, blocked_dirs)
    summary = summary_rows(detail, samples=int(bootstrap_samples), seed=int(seed))
    return {"detail_rows": detail, "summary_rows": summary}


@app.local_entrypoint()
def main(
    unblocked_run_ids: str,
    blocked_run_ids: str,
    bootstrap_samples: int = 10_000,
    seed: int = 7,
) -> None:
    result = summarize_case4_matched_remote.remote(
        unblocked_run_ids=_parse_csv_arg(unblocked_run_ids),
        blocked_run_ids=_parse_csv_arg(blocked_run_ids),
        bootstrap_samples=int(bootstrap_samples),
        seed=int(seed),
    )
    print(json.dumps(result, indent=2))
