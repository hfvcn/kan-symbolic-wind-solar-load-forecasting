#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.thesis_sweep.utils import det_run_id

TEXT_SUFFIXES = {".json", ".csv", ".md", ".tex", ".txt", ".png", ".pdf", ".parquet"}
DATA_PHASES = {"01-data-pipeline", "01.5-derived-dataset"}
DOC_SNAPSHOT_GLOBS = ("paper_delivery_closure_*.md",)
SESSION_META_SUFFIXES = {".json", ".md", ".txt", ".log"}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def _copy_paper_assets_snapshot(paper_assets_dir: Path, snapshot_dir: Path, *, out_dir: Path) -> None:
    for path in paper_assets_dir.rglob("*"):
        if not path.is_file():
            continue
        if path == out_dir or out_dir in path.parents:
            continue
        rel = path.relative_to(paper_assets_dir)
        _copy_file(path, snapshot_dir / rel)


def _copy_doc_snapshot(repo_root: Path, snapshot_dir: Path) -> None:
    doc_dir = repo_root / "doc"
    for pattern in DOC_SNAPSHOT_GLOBS:
        for path in sorted(doc_dir.glob(pattern)):
            _copy_file(path, snapshot_dir / path.name)


def _copy_session_meta(session_dir: Path, out_dir: Path) -> None:
    meta_dir = out_dir / "session_meta"
    for path in sorted(session_dir.iterdir()):
        if not path.is_file():
            continue
        if path.name == "manifest.json":
            continue
        if path.suffix.lower() not in SESSION_META_SUFFIXES:
            continue
        _copy_file(path, meta_dir / path.name)


def _copy_artifacts(run_dir: Path, out_dir: Path) -> None:
    artifacts_dir = run_dir / "artifacts"
    if not artifacts_dir.exists():
        return
    for path in artifacts_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        rel = path.relative_to(run_dir)
        _copy_file(path, out_dir / rel)


def _copy_data_run_metadata(run_dir: Path, out_dir: Path) -> None:
    for path in sorted((run_dir / "processed").glob("*_meta.json")):
        rel = path.relative_to(run_dir)
        _copy_file(path, out_dir / rel)
    report = run_dir / "reports" / "quality_report.json"
    if report.exists():
        _copy_file(report, out_dir / "reports" / "quality_report.json")


def _collect_run_ids(manifest: dict[str, Any], session_id: str, *, repo_root: Path) -> list[str]:
    run_ids: list[str] = []
    for key in ("source_data_run_id", "derived_data_run_id"):
        value = manifest.get(key)
        if value:
            run_ids.append(str(value))
    for values in (manifest.get("runs") or {}).values():
        if isinstance(values, list):
            run_ids.extend(str(v) for v in values)
    for value in (manifest.get("structured_components") or {}).values():
        run_ids.append(str(value))
    combo_run_id = det_run_id(session_id, "s3_combo_net_load")
    if (repo_root / "runs" / combo_run_id / "payload.json").exists():
        run_ids.append(combo_run_id)
    return sorted(dict.fromkeys(run_ids))


def _copy_run_refs(run_ids: list[str], out_dir: Path, *, repo_root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    refs_dir = out_dir / "run_refs"
    for run_id in run_ids:
        run_dir = repo_root / "runs" / run_id
        if not (run_dir / "payload.json").exists():
            continue
        payload = _read_json(run_dir / "payload.json")
        run_out_dir = refs_dir / run_id
        _copy_file(run_dir / "payload.json", run_out_dir / "payload.json")
        _copy_artifacts(run_dir, run_out_dir)
        if str(payload.get("phase")) in DATA_PHASES:
            _copy_data_run_metadata(run_dir, run_out_dir)
        rows.append(
            {
                "run_id": run_id,
                "phase": str(payload.get("phase") or "unknown"),
                "kind": str(payload.get("kind") or "unknown"),
                "source_path": str(run_dir),
                "ref_path": str(run_out_dir),
            }
        )
    return rows


def _write_readme(
    *,
    out_dir: Path,
    session_id: str,
    manifest: dict[str, Any],
    run_rows: list[dict[str, str]],
) -> None:
    lines = [
        f"# Paper Reference Bundle: {session_id}",
        "",
        "本目录集中存放本次 thesis fullflow session 可直接用于论文撰写、复现和答辩追溯的资产。",
        "",
        "## Session",
        "",
        f"- session_id: `{session_id}`",
        f"- source_data_run_id: `{manifest.get('source_data_run_id')}`",
        f"- derived_data_run_id: `{manifest.get('derived_data_run_id')}`",
        f"- manifest: `{out_dir / 'manifest.json'}`",
        f"- session_paper_assets: `{out_dir / 'paper_assets'}`",
        f"- asset_index_snapshot: `{out_dir / 'ASSET_INDEX.md'}`",
        f"- paper_assets_snapshot: `{out_dir / 'paper_assets_snapshot'}`",
        f"- doc_snapshot: `{out_dir / 'doc_snapshot'}`",
        f"- session_meta: `{out_dir / 'session_meta'}`",
        "",
        "## Runs",
        "",
        "| run_id | phase | kind | source | bundle |",
        "|---|---|---|---|---|",
    ]
    for row in run_rows:
        lines.append(
            f"| `{row['run_id']}` | `{row['phase']}` | `{row['kind']}` | `{row['source_path']}` | `{row['ref_path']}` |"
        )
    (out_dir / "README.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect thesis session assets into a single paper reference bundle.")
    parser.add_argument("--session-id", required=True, help="Session id under doc/thesis_sweeps/<session_id>.")
    parser.add_argument("--out-dir", default="", help="Optional output directory. Defaults to doc/paper_assets/paper_reference_<session_id>.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root. Defaults to the current project root.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    session_id = str(args.session_id).strip()
    session_dir = repo_root / "doc" / "thesis_sweeps" / session_id
    manifest_path = session_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    out_dir = (
        Path(args.out_dir)
        if str(args.out_dir).strip()
        else repo_root / "doc" / "paper_assets" / f"paper_reference_{session_id}"
    ).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = _read_json(manifest_path)
    _copy_file(manifest_path, out_dir / "manifest.json")
    _copy_session_meta(session_dir, out_dir)

    session_assets_dir = session_dir / "paper_assets"
    if session_assets_dir.exists():
        _copy_tree(session_assets_dir, out_dir / "paper_assets")

    asset_index = repo_root / "doc" / "paper_assets" / "ASSET_INDEX.md"
    if asset_index.exists():
        _copy_file(asset_index, out_dir / "ASSET_INDEX.md")
        _copy_paper_assets_snapshot(asset_index.parent.resolve(), out_dir / "paper_assets_snapshot", out_dir=out_dir)
    _copy_doc_snapshot(repo_root, out_dir / "doc_snapshot")

    run_ids = _collect_run_ids(manifest, session_id, repo_root=repo_root)
    run_rows = _copy_run_refs(run_ids, out_dir, repo_root=repo_root)
    _write_readme(out_dir=out_dir, session_id=session_id, manifest=manifest, run_rows=run_rows)


if __name__ == "__main__":
    main()
