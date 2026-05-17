from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from src.demo_quick_train_support import DemoConfig, load_payload, remote_cli, remote_job_dir

FORMULA_PREVIEW_CHARS = 180
DEFAULT_DEMO_TEMPLATE_RUN_ID = "tune_20260303_solar_pr08_rm11_hw60_l001_e10"
DEFAULT_DEMO_SYMBOLIC_RUN_ID = "demo_midterm_verify_20260412"


def _pick_processed_split(processed_dir: Path, split: str, timestamp: str) -> Path:
    if timestamp:
        path = processed_dir / f"{split}_{timestamp}.parquet"
        if not path.exists():
            raise FileNotFoundError(f"缺少数据切分文件: {path}")
        return path
    candidates = sorted(processed_dir.glob(f"{split}_*.parquet"))
    if not candidates:
        raise FileNotFoundError(f"缺少数据切分文件: {processed_dir}/{split}_*.parquet")
    return candidates[-1]


def validate_data_contract(config: DemoConfig) -> dict[str, Any]:
    run_dir = config.runs_root / config.template.data_run_id
    payload = load_payload(run_dir / "payload.json") or {}
    processed_dir = run_dir / "processed"
    artifacts_dir = run_dir / "artifacts"
    train_path = _pick_processed_split(processed_dir, "train", config.template.data_timestamp)
    val_path = _pick_processed_split(processed_dir, "val", config.template.data_timestamp)
    test_path = _pick_processed_split(processed_dir, "test", config.template.data_timestamp)
    scaler_path = artifacts_dir / "scaler_params.json"
    if not scaler_path.exists():
        raise FileNotFoundError(f"缺少 scaler 参数文件: {scaler_path}")
    return {
        "data_run_id": config.template.data_run_id,
        "data_phase": payload.get("phase"),
        "train_split": str(train_path),
        "val_split": str(val_path),
        "test_split": str(test_path),
        "scaler_params": str(scaler_path),
    }


def run_payload_exists(runs_root: Path, run_id: str) -> bool:
    return (runs_root / run_id / "payload.json").exists()


def infer_data_run_id_from_training_payload(runs_root: Path, run_id: str) -> str:
    payload = load_payload(runs_root / run_id / "payload.json")
    if payload is None:
        raise FileNotFoundError(f"缺少训练结果 payload: {runs_root / run_id}")
    data_run_id = str(payload.get("data_run_id") or "").strip()
    if not data_run_id:
        raise RuntimeError(f"训练结果缺少 data_run_id: {runs_root / run_id / 'payload.json'}")
    return data_run_id


def resolve_symbolic_run(runs_root: Path, *, explicit_run_id: str, template_train_run_id: str, target_col: str) -> str:
    if explicit_run_id:
        run_dir = runs_root / explicit_run_id
        if not (run_dir / "artifacts" / "formula.sympy.txt").exists():
            raise FileNotFoundError(f"指定的公式产物不存在: {run_dir}")
        return explicit_run_id

    matches_by_train: list[str] = []
    matches_by_target: list[str] = []
    for payload_path in sorted(runs_root.glob("*/payload.json")):
        payload = load_payload(payload_path)
        if not payload:
            continue
        run_dir = payload_path.parent
        if not (run_dir / "artifacts" / "formula.sympy.txt").exists():
            continue
        run_id = str(payload.get("run_id") or run_dir.name).strip()
        if str(payload.get("train_run_id") or "").strip() == template_train_run_id:
            matches_by_train.append(run_id)
            continue
        payload_target = str(payload.get("target_col") or (payload.get("cfg") or {}).get("target_col") or "").strip()
        if payload_target == target_col:
            matches_by_target.append(run_id)
    if matches_by_train:
        return matches_by_train[-1]
    if matches_by_target:
        return matches_by_target[-1]
    raise RuntimeError("找不到可用于答辩展示的公式产物，请显式传入 --symbolic-run-id。")


def load_symbolic_summary(runs_root: Path, run_id: str) -> dict[str, Any]:
    run_dir = runs_root / run_id
    payload = load_payload(run_dir / "payload.json")
    if payload is None:
        raise FileNotFoundError(f"缺少公式产物 payload: {run_dir}")
    formula_path = run_dir / "artifacts" / "formula.sympy.txt"
    metrics_path = run_dir / "artifacts" / "formula_metrics.json"
    eval_path = run_dir / "artifacts" / "formula_eval_test.json"
    for path in (formula_path, metrics_path, eval_path):
        if not path.exists():
            raise FileNotFoundError(f"缺少公式产物文件: {path}")
    formula_preview = formula_path.read_text(encoding="utf-8").strip()[:FORMULA_PREVIEW_CHARS].replace("\n", " ")
    return {
        "run_id": run_id,
        "train_run_id": payload.get("train_run_id"),
        "target_col": payload.get("target_col"),
        "formula_preview": formula_preview,
        "formula_metrics": json.loads(metrics_path.read_text(encoding="utf-8")),
        "eval_test": json.loads(eval_path.read_text(encoding="utf-8")),
    }


def build_remote_baseline_cmd(config: DemoConfig, *, baseline_run_id: str) -> list[str]:
    template = config.template
    cmd = [
        remote_cli(),
        "run",
        str(remote_job_dir() / "baseline_torch.py"),
        "--data-run-id",
        template.data_run_id,
        "--model-type",
        "mlp",
        "--target",
        template.target_col,
        "--run-id",
        baseline_run_id,
        "--match-kan-run-id",
        config.run_id,
        "--sync-kan-feature-cols",
        "--sync-kan-budget",
        "--patience",
        "0",
    ]
    if template.data_timestamp:
        cmd.extend(["--data-timestamp", template.data_timestamp])
    if config.use_gpu:
        cmd.append("--use-gpu")
    return cmd


def build_evaluate_cmd(*, repo_root: Path, run_paths: list[Path], out_dir: Path) -> list[str]:
    cmd = ["python3", str(repo_root / "scripts" / "evaluate_runs.py")]
    for run_path in run_paths:
        cmd.extend(["--run", str(run_path)])
    cmd.extend(["--out-dir", str(out_dir)])
    return cmd


def load_comparison_rows(table_path: Path) -> list[dict[str, str]]:
    if not table_path.exists():
        raise FileNotFoundError(f"缺少评估表: {table_path}")
    with table_path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))
