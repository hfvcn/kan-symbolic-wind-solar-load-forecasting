#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.demo_midterm_support import (
    DEFAULT_DEMO_SYMBOLIC_RUN_ID,
    DEFAULT_DEMO_TEMPLATE_RUN_ID,
    build_evaluate_cmd,
    build_remote_baseline_cmd,
    infer_data_run_id_from_training_payload,
    load_comparison_rows,
    load_symbolic_summary,
    resolve_symbolic_run,
    run_payload_exists,
    validate_data_contract,
)
from src.demo_quick_train_support import (
    DEFAULT_HIDDEN_WIDTH,
    DEFAULT_MAX_TRAIN_ROWS,
    DEFAULT_REFINE_STEPS,
    DEFAULT_SPARSIFY_STEPS,
    DEFAULT_WARMUP_STEPS,
    SUMMARY_PATH,
    build_config,
    build_remote_train_cmd,
    load_summary,
    print_summary,
    remote_env,
    sanitize_text,
    sync_script,
)


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    raw_output: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="中期答辩一键演示入口。默认真实跑 quick KAN + quick baseline + 本地评估，并核验现成公式产物。")
    parser.add_argument("--runs-root", default="runs")
    parser.add_argument("--source-train-run-id", default=DEFAULT_DEMO_TEMPLATE_RUN_ID)
    parser.add_argument("--source-data-run-id", default="")
    parser.add_argument("--target", default="")
    parser.add_argument("--data-timestamp", default="")
    parser.add_argument("--symbolic-run-id", default=DEFAULT_DEMO_SYMBOLIC_RUN_ID)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--baseline-run-id", default="")
    parser.add_argument("--max-train-rows", type=int, default=DEFAULT_MAX_TRAIN_ROWS)
    parser.add_argument("--warmup-steps", type=int, default=DEFAULT_WARMUP_STEPS)
    parser.add_argument("--sparsify-steps", type=int, default=DEFAULT_SPARSIFY_STEPS)
    parser.add_argument("--refine-steps", type=int, default=DEFAULT_REFINE_STEPS)
    parser.add_argument("--hidden-width", type=int, default=DEFAULT_HIDDEN_WIDTH)
    parser.add_argument("--use-gpu", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def print_step(index: int, title: str) -> None:
    print(f"\n[{index}/5] {title}", flush=True)


def print_public_command(cmd: list[str], volume_name: str) -> None:
    print(f"[cmd] {sanitize_text(' '.join(cmd), volume_name)}", flush=True)


def run_command(cmd: list[str], *, env: dict[str, str] | None, volume_name: str, dry_run: bool) -> CommandResult:
    print_public_command(cmd, volume_name)
    if dry_run:
        return CommandResult(returncode=0, raw_output="")
    proc = subprocess.Popen(
        cmd,
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert proc.stdout is not None
    raw_lines: list[str] = []
    for line in proc.stdout:
        raw_lines.append(line)
        print(sanitize_text(line.rstrip("\n"), volume_name), flush=True)
    return CommandResult(returncode=int(proc.wait()), raw_output="".join(raw_lines))


def extract_last_json(text: str) -> dict:
    decoder = json.JSONDecoder()
    last_payload: dict | None = None
    for idx in reversed([i for i, ch in enumerate(text) if ch in "{["]):
        try:
            obj, _ = decoder.raw_decode(text[idx:])
        except Exception:
            continue
        if isinstance(obj, dict):
            last_payload = obj
            if "run_id" in obj:
                return obj
    if last_payload is None:
        raise RuntimeError("远端输出里没有找到可解析的结果摘要。")
    return last_payload


def ensure_success(result: CommandResult, title: str) -> None:
    if result.returncode != 0:
        raise RuntimeError(f"{title}失败，退出码={result.returncode}。")


def sync_run(run_id: str, *, env: dict[str, str], volume_name: str, dry_run: bool) -> None:
    result = run_command([str(sync_script()), run_id], env=env, volume_name=volume_name, dry_run=dry_run)
    ensure_success(result, "结果回传")


def _baseline_run_id(run_id: str, provided: str) -> str:
    return provided.strip() or f"{run_id}__baseline_mlp"


def write_demo_summary(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def bootstrap_env(volume_name: str, runs_root: Path) -> dict[str, str]:
    env = dict(os.environ)
    env["KAN_SR_VOLUME"] = volume_name
    env["VOLUME_NAME"] = volume_name
    env["LOCAL_BASE"] = str(runs_root)
    return env


def ensure_local_run(run_id: str, *, title: str, runs_root: Path, env: dict[str, str], volume_name: str, dry_run: bool) -> None:
    if not run_id or run_payload_exists(runs_root, run_id):
        return
    print(f"本地缺少{title}，开始回传: {run_id}", flush=True)
    sync_run(run_id, env=env, volume_name=volume_name, dry_run=dry_run)


def run_demo() -> None:
    args = parse_args()
    runs_root = Path(args.runs_root).expanduser().resolve()
    volume_name = os.environ.get("KAN_SR_VOLUME") or os.environ.get("VOLUME_NAME") or "kan-sr"
    base_env = bootstrap_env(volume_name, runs_root)
    source_train_run_id = str(args.source_train_run_id).strip()
    source_data_run_id = str(args.source_data_run_id).strip()
    symbolic_run_id_arg = str(args.symbolic_run_id).strip()

    ensure_local_run(
        source_train_run_id,
        title="模板训练结果",
        runs_root=runs_root,
        env=base_env,
        volume_name=volume_name,
        dry_run=args.dry_run,
    )
    if source_train_run_id and not source_data_run_id:
        source_data_run_id = infer_data_run_id_from_training_payload(runs_root, source_train_run_id)
    ensure_local_run(
        source_data_run_id,
        title="模板数据结果",
        runs_root=runs_root,
        env=base_env,
        volume_name=volume_name,
        dry_run=args.dry_run,
    )
    ensure_local_run(
        symbolic_run_id_arg,
        title="公式产物",
        runs_root=runs_root,
        env=base_env,
        volume_name=volume_name,
        dry_run=args.dry_run,
    )
    config = build_config(
        runs_root=args.runs_root,
        source_train_run_id=source_train_run_id,
        source_data_run_id=source_data_run_id,
        target=args.target,
        data_timestamp=args.data_timestamp,
        run_id=args.run_id,
        max_train_rows=args.max_train_rows,
        warmup_steps=args.warmup_steps,
        sparsify_steps=args.sparsify_steps,
        refine_steps=args.refine_steps,
        hidden_width=args.hidden_width,
        use_gpu=args.use_gpu,
        dry_run=args.dry_run,
    )
    env = remote_env(config)
    symbolic_run_id = resolve_symbolic_run(
        config.runs_root,
        explicit_run_id=symbolic_run_id_arg,
        template_train_run_id=config.template.run_id,
        target_col=config.template.target_col,
    )
    baseline_run_id = _baseline_run_id(config.run_id, str(args.baseline_run_id))

    print("中期答辩演示入口", flush=True)
    print("模式: 数据契约验证 + quick KAN + 公式产物核验 + quick baseline + 本地评估", flush=True)
    print(f"模板训练结果: {config.template.run_id}", flush=True)
    print(f"模板数据结果: {config.template.data_run_id}", flush=True)
    print(f"公式产物结果: {symbolic_run_id}", flush=True)
    print(f"本次训练结果: {config.run_id}", flush=True)
    print(f"本次基线结果: {baseline_run_id}", flush=True)

    print_step(1, "核验数据阶段产物")
    data_info = validate_data_contract(config)
    print(f"数据结果: {data_info['data_run_id']}", flush=True)
    print(f"train: {data_info['train_split']}", flush=True)
    print(f"val: {data_info['val_split']}", flush=True)
    print(f"test: {data_info['test_split']}", flush=True)

    print_step(2, "提交远端 quick KAN 训练")
    train_result = run_command(build_remote_train_cmd(config), env=env, volume_name=config.volume_name, dry_run=config.dry_run)
    ensure_success(train_result, "远端训练")
    if not config.dry_run:
        payload = extract_last_json(train_result.raw_output)
        if str(payload.get("run_id", "")).strip() and payload["run_id"] != config.run_id:
            raise RuntimeError("远端训练返回的结果编号与本地预期不一致。")
    sync_run(config.run_id, env=env, volume_name=config.volume_name, dry_run=config.dry_run)

    print_step(3, "核验公式提取阶段产物")
    symbolic_summary = load_symbolic_summary(config.runs_root, symbolic_run_id)
    print(f"公式结果编号: {symbolic_summary['run_id']}", flush=True)
    print(f"公式目标列: {symbolic_summary['target_col']}", flush=True)
    print(f"公式预览: {symbolic_summary['formula_preview']}", flush=True)

    print_step(4, "提交远端 quick baseline")
    baseline_result = run_command(
        build_remote_baseline_cmd(config, baseline_run_id=baseline_run_id),
        env=env,
        volume_name=config.volume_name,
        dry_run=config.dry_run,
    )
    ensure_success(baseline_result, "远端基线")
    if not config.dry_run:
        payload = extract_last_json(baseline_result.raw_output)
        if str(payload.get("run_id", "")).strip() and payload["run_id"] != baseline_run_id:
            raise RuntimeError("远端基线返回的结果编号与本地预期不一致。")
    sync_run(baseline_run_id, env=env, volume_name=config.volume_name, dry_run=config.dry_run)

    print_step(5, "运行本地评估并写出摘要")
    eval_dir = config.runs_root / config.run_id / "reports" / "midterm_eval"
    eval_cmd = build_evaluate_cmd(
        repo_root=REPO_ROOT,
        run_paths=[
            config.runs_root / config.run_id,
            config.runs_root / baseline_run_id,
            config.runs_root / symbolic_run_id,
        ],
        out_dir=eval_dir,
    )
    eval_result = run_command(eval_cmd, env=None, volume_name=config.volume_name, dry_run=config.dry_run)
    ensure_success(eval_result, "本地评估")
    if config.dry_run:
        print("[dry-run] 已跳过真实执行后的本地摘要写入。", flush=True)
        return

    train_summary = load_summary(config)
    comparison_rows = load_comparison_rows(eval_dir / "comparison_table.csv")
    payload = {
        "mode": "midterm_evidence_chain",
        "data_contract": data_info,
        "train_summary": train_summary,
        "symbolic_summary": symbolic_summary,
        "baseline_run_id": baseline_run_id,
        "evaluation_dir": str(eval_dir),
        "comparison_rows": comparison_rows,
    }
    write_demo_summary(config.runs_root / config.run_id / SUMMARY_PATH, payload)
    print_summary(train_summary)
    print(f"评估目录: {eval_dir}", flush=True)
    print(f"比较表: {eval_dir / 'comparison_table.csv'}", flush=True)


def main() -> None:
    try:
        run_demo()
    except Exception as exc:
        print(f"[失败] {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
