from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RunDirs:
    run_dir: Path
    processed_dir: Path
    artifacts_dir: Path
    checkpoint_dir: Path


def utc_run_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    return f"{ts}_{uuid.uuid4().hex[:8]}"


def ensure_run_dirs(runs_root: Path, run_id: str) -> RunDirs:
    root = Path(runs_root)
    run_dir = root / str(run_id)
    processed_dir = run_dir / "processed"
    artifacts_dir = run_dir / "artifacts"
    checkpoint_dir = run_dir / "checkpoint"

    run_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    return RunDirs(
        run_dir=run_dir,
        processed_dir=processed_dir,
        artifacts_dir=artifacts_dir,
        checkpoint_dir=checkpoint_dir,
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, default=str)

