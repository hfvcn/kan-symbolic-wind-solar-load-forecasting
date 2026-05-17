from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.thesis_sweep.postprocess import local_postprocess
from src.thesis_sweep.utils import REPO_ROOT, local_py, sync_run


@dataclass(frozen=True)
class RefreshSessionInputs:
    session_id: str
    session_dir: Path
    run_ids: tuple[str, ...]
    sync_run_ids: tuple[str, ...]
    comp_runs: dict[str, str]


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return payload


def _append_unique(run_ids: list[str], value: Any) -> None:
    run_id = str(value or "").strip()
    if run_id and run_id not in run_ids:
        run_ids.append(run_id)


def _manifest_run_ids(manifest: dict[str, Any]) -> list[str]:
    run_ids: list[str] = []
    for planned in manifest.get("planned", []):
        if isinstance(planned, dict):
            _append_unique(run_ids, planned.get("run_id"))
    runs = manifest.get("runs")
    if not isinstance(runs, dict):
        return run_ids
    for value in runs.values():
        if isinstance(value, list):
            for item in value:
                _append_unique(run_ids, item)
            continue
        _append_unique(run_ids, value)
    return run_ids


def _load_session_manifest(repo_root: Path, session_id: str) -> tuple[Path, dict[str, Any]]:
    normalized = str(session_id).strip()
    session_dir = repo_root / "doc" / "thesis_sweeps" / normalized
    manifest_path = session_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    return session_dir, _read_json(manifest_path)


def resolve_refresh_inputs(
    *,
    repo_root: Path = REPO_ROOT,
    session_id: str,
    sync_from_sessions: list[str] | None = None,
    extra_run_ids: list[str] | None = None,
) -> RefreshSessionInputs:
    session_dir, manifest = _load_session_manifest(repo_root, session_id)
    run_ids = _manifest_run_ids(manifest)
    sync_run_ids: list[str] = []

    for sync_session_id in sync_from_sessions or []:
        _sync_session_dir, sync_manifest = _load_session_manifest(repo_root, sync_session_id)
        for run_id in _manifest_run_ids(sync_manifest):
            _append_unique(sync_run_ids, run_id)
            _append_unique(run_ids, run_id)

    for run_id in extra_run_ids or []:
        _append_unique(sync_run_ids, run_id)
        _append_unique(run_ids, run_id)

    raw_comp_runs = manifest.get("structured_components")
    comp_runs = (
        {str(key): str(value).strip() for key, value in raw_comp_runs.items() if str(value).strip()}
        if isinstance(raw_comp_runs, dict)
        else {}
    )
    return RefreshSessionInputs(
        session_id=str(manifest.get("session_id") or session_id).strip(),
        session_dir=session_dir,
        run_ids=tuple(run_ids),
        sync_run_ids=tuple(sync_run_ids),
        comp_runs=comp_runs,
    )


def refresh_session(
    inputs: RefreshSessionInputs,
    *,
    repo_root: Path = REPO_ROOT,
    collect_paper_reference: bool = False,
) -> list[str]:
    for run_id in inputs.sync_run_ids:
        sync_run(run_id, dry_run=False)

    run_ids_out = local_postprocess(
        run_ids=list(inputs.run_ids),
        comp_runs=inputs.comp_runs,
        session_id=inputs.session_id,
        session_dir=inputs.session_dir,
    )
    if collect_paper_reference:
        local_py(
            repo_root / "scripts" / "collect_paper_reference.py",
            ["--session-id", inputs.session_id],
            dry_run=False,
        )
    return run_ids_out
