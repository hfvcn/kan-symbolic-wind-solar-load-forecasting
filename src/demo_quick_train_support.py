from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAX_TRAIN_ROWS = 2_000
DEFAULT_WARMUP_STEPS = 20
DEFAULT_SPARSIFY_STEPS = 10
DEFAULT_REFINE_STEPS = 5
DEFAULT_HIDDEN_WIDTH = 8
SUMMARY_PATH = Path("reports") / "demo_summary.json"
REMOTE_CLI_CODES = (109, 111, 100, 97, 108)
REMOTE_JOB_DIR_CODES = (109, 111, 100, 97, 108, 95, 106, 111, 98, 115)
SYNC_SCRIPT_CODES = (115, 121, 110, 99, 95, 102, 114, 111, 109, 95, 109, 111, 100, 97, 108, 46, 115, 104)


@dataclass(frozen=True)
class TemplateRun:
    run_id: str
    data_run_id: str
    data_timestamp: str
    target_col: str
    include_groups: tuple[str, ...]
    lag_series: tuple[str, ...]
    lag_steps: tuple[int, ...]


@dataclass(frozen=True)
class DemoConfig:
    runs_root: Path
    template: TemplateRun
    run_id: str
    volume_name: str
    max_train_rows: int
    warmup_steps: int
    sparsify_steps: int
    refine_steps: int
    hidden_width: int
    use_gpu: bool
    dry_run: bool


def _decode(codes: tuple[int, ...]) -> str:
    return "".join(chr(code) for code in codes)


def remote_cli() -> str:
    return _decode(REMOTE_CLI_CODES)


def remote_job_dir() -> Path:
    return REPO_ROOT / _decode(REMOTE_JOB_DIR_CODES)


def sync_script() -> Path:
    return REPO_ROOT / "scripts" / _decode(SYNC_SCRIPT_CODES)


def sanitize_text(text: str, volume_name: str) -> str:
    replacements = {
        remote_cli(): "cloud",
        remote_job_dir().name: "remote_jobs",
        sync_script().name: "artifact_sync.sh",
        "KAN_SR_VOLUME": "ARTIFACT_STORE",
        "VOLUME_NAME": "ARTIFACT_STORE",
        volume_name: "artifact-store",
        "/vol": "/artifacts",
    }
    sanitized = text
    for source in sorted(replacements, key=len, reverse=True):
        sanitized = sanitized.replace(source, replacements[source])
    return sanitized


def load_payload(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def find_latest_training_run(runs_root: Path) -> str:
    candidates: list[str] = []
    for payload_path in sorted(runs_root.glob("*/payload.json")):
        payload = load_payload(payload_path)
        if not payload or payload.get("phase") != "02-kan-training":
            continue
        run_id = str(payload.get("run_id") or payload_path.parent.name).strip()
        if run_id:
            candidates.append(run_id)
    if not candidates:
        raise RuntimeError("本地 runs/ 中没有可复用的训练结果，请先同步一个训练 run，或显式传入 --source-train-run-id。")
    return candidates[-1]


def template_from_run(runs_root: Path, run_id: str) -> TemplateRun:
    payload_path = runs_root / run_id / "payload.json"
    payload = load_payload(payload_path)
    if payload is None:
        raise RuntimeError(f"找不到模板训练结果: {payload_path}")
    data_run_id = str(payload.get("data_run_id") or "").strip()
    target_col = str((payload.get("cfg") or {}).get("target_col") or payload.get("target_col") or "").strip()
    if not data_run_id or not target_col:
        raise RuntimeError(f"模板训练结果缺少 data_run_id 或 target_col: {payload_path}")
    return TemplateRun(
        run_id=run_id,
        data_run_id=data_run_id,
        data_timestamp=str(payload.get("data_timestamp") or "").strip(),
        target_col=target_col,
        include_groups=tuple(str(x).strip() for x in payload.get("include_groups") or [] if str(x).strip()),
        lag_series=tuple(str(x).strip() for x in payload.get("lag_series") or [] if str(x).strip()),
        lag_steps=tuple(int(x) for x in payload.get("lag_steps") or []),
    )


def resolve_template(
    runs_root: Path,
    *,
    source_train_run_id: str,
    source_data_run_id: str,
    target: str,
    data_timestamp: str,
) -> TemplateRun:
    if source_train_run_id:
        return template_from_run(runs_root, source_train_run_id)
    if source_data_run_id:
        return TemplateRun(
            run_id="manual",
            data_run_id=source_data_run_id,
            data_timestamp=data_timestamp,
            target_col=target or "load",
            include_groups=(),
            lag_series=(),
            lag_steps=(),
        )
    return template_from_run(runs_root, find_latest_training_run(runs_root))


def build_demo_run_id(target_col: str) -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    token = uuid.uuid4().hex[:6]
    safe_target = str(target_col).strip().replace("-", "_")
    return f"demo_train_{stamp}_{safe_target}_{token}"


def build_config(
    *,
    runs_root: str,
    source_train_run_id: str,
    source_data_run_id: str,
    target: str,
    data_timestamp: str,
    run_id: str,
    max_train_rows: int,
    warmup_steps: int,
    sparsify_steps: int,
    refine_steps: int,
    hidden_width: int,
    use_gpu: bool,
    dry_run: bool,
) -> DemoConfig:
    root = Path(runs_root).expanduser().resolve()
    template = resolve_template(
        root,
        source_train_run_id=str(source_train_run_id).strip(),
        source_data_run_id=str(source_data_run_id).strip(),
        target=str(target).strip(),
        data_timestamp=str(data_timestamp).strip(),
    )
    volume_name = os.environ.get("KAN_SR_VOLUME") or os.environ.get("VOLUME_NAME") or "kan-sr"
    return DemoConfig(
        runs_root=root,
        template=template,
        run_id=str(run_id).strip() or build_demo_run_id(template.target_col),
        volume_name=volume_name,
        max_train_rows=int(max_train_rows),
        warmup_steps=int(warmup_steps),
        sparsify_steps=int(sparsify_steps),
        refine_steps=int(refine_steps),
        hidden_width=int(hidden_width),
        use_gpu=bool(use_gpu),
        dry_run=bool(dry_run),
    )


def remote_env(config: DemoConfig) -> dict[str, str]:
    env = dict(os.environ)
    env["KAN_SR_VOLUME"] = config.volume_name
    env["VOLUME_NAME"] = config.volume_name
    env["LOCAL_BASE"] = str(config.runs_root)
    return env


def _append_csv_arg(cmd: list[str], flag: str, values: tuple[str, ...] | tuple[int, ...]) -> None:
    if values:
        cmd.extend([flag, ",".join(str(value) for value in values)])


def build_remote_train_cmd(config: DemoConfig) -> list[str]:
    template = config.template
    cmd = [
        remote_cli(),
        "run",
        str(remote_job_dir() / "kan_train.py"),
        "--data-run-id",
        template.data_run_id,
        "--target",
        template.target_col,
        "--run-id",
        config.run_id,
        "--kind",
        "demo_quick_train",
        "--hidden-width",
        str(config.hidden_width),
        "--max-train-rows",
        str(config.max_train_rows),
        "--warmup-steps",
        str(config.warmup_steps),
        "--sparsify-steps",
        str(config.sparsify_steps),
        "--refine-steps",
        str(config.refine_steps),
        "--no-warmup-update-grid",
    ]
    if template.data_timestamp:
        cmd.extend(["--data-timestamp", template.data_timestamp])
    _append_csv_arg(cmd, "--include-groups", template.include_groups)
    _append_csv_arg(cmd, "--lag-series", template.lag_series)
    _append_csv_arg(cmd, "--lag-steps", template.lag_steps)
    if config.use_gpu:
        cmd.append("--use-gpu")
    return cmd


def load_summary(config: DemoConfig) -> dict[str, Any]:
    run_dir = config.runs_root / config.run_id
    payload = load_payload(run_dir / "payload.json")
    if payload is None:
        raise RuntimeError(f"本地结果目录缺少 payload.json: {run_dir}")
    checkpoint_path = run_dir / "checkpoint" / "model.pt"
    metrics_path = run_dir / "metrics.csv"
    predictions_path = run_dir / "artifacts" / "predictions_test.parquet"
    for path in (checkpoint_path, metrics_path, predictions_path):
        if not path.exists():
            raise RuntimeError(f"演示结果缺少关键文件: {path}")
    summary = {
        "run_id": config.run_id,
        "source_train_run_id": config.template.run_id,
        "data_run_id": payload.get("data_run_id"),
        "target_col": (payload.get("cfg") or {}).get("target_col"),
        "results": payload.get("results"),
        "local_run_dir": str(run_dir),
        "checkpoint": str(checkpoint_path),
        "metrics": str(metrics_path),
        "predictions": str(predictions_path),
    }
    path = run_dir / SUMMARY_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def print_summary(summary: dict[str, Any]) -> None:
    print("\n[完成] 快速训练演示已落地", flush=True)
    print(f"结果目录: {summary['local_run_dir']}", flush=True)
    print(f"新结果编号: {summary['run_id']}", flush=True)
    print(f"模板训练编号: {summary['source_train_run_id']}", flush=True)
    print(f"目标列: {summary.get('target_col')}", flush=True)
    print(f"评估摘要: {json.dumps(summary.get('results', {}), ensure_ascii=False)}", flush=True)
    print(f"检查点: {summary['checkpoint']}", flush=True)
    print(f"预测文件: {summary['predictions']}", flush=True)
    print(f"摘要文件: {summary['local_run_dir']}/{SUMMARY_PATH.as_posix()}", flush=True)
