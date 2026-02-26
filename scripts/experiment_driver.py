#!/usr/bin/env python3
from __future__ import annotations

"""
Unified experiment driver for KAN-SR.

Goal: keep all frequently-tuned knobs (hyperparams + Modal calls + local eval/plots)
in ONE file so you can iterate quickly:

  # 1) Edit the CONFIG section below
  # 2) Dry-run to inspect commands
  python3 scripts/experiment_driver.py --dry-run
  # 3) Execute (Modal + sync + local evaluation)
  python3 scripts/experiment_driver.py --execute

Notes:
  - This script calls `modal run ...` via subprocess (so you keep Modal's logs).
  - It records a session manifest under `doc/optimization/<session_id>/`.
  - Failures are best-effort: it logs and continues to the next experiment.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# =============================================================================
# CONFIG (edit this block most often)
# =============================================================================


VOLUME_NAME = os.environ.get("VOLUME_NAME", "kan-sr")

# If you already have a Phase-1 run synced locally, set it here. Otherwise set
# RUN_DATA_PIPELINE=True to create one.
DATA_RUN_ID = "2026-02-26_032058_1957fda1"
RUN_DATA_PIPELINE = False
DATA_PIPELINE = {
    "year": 2018,
    "iso": "ERCOT",
    "target": "load",
    "force": False,
}

# Use existing KAN-train runs (skips training stage).
EXISTING_KAN_TRAIN_RUN_IDS: list[str] = [
    # Best preliminary run (ablation no_l1) — good test RMSE, but symbolic not yet re-tried.
    "2026-02-26_055200_958b3949",
]

# Optional: add NEW KAN training runs to sweep (each entry produces a new run_id).
# Tips:
#   - Set max_train_rows=0 to use full train split (no downsampling).
#   - Set include_groups / lag_series / lag_steps to encourage interpretability.
KAN_TRAIN_SWEEP: list[dict[str, Any]] = [
    # "physics-first" (exogenous-only) run: remove autoregressive load lags to encourage
    # temperature / irradiance / solar-geometry effects to appear in symbolic formulas.
    # (Accuracy will likely drop, but interpretability/physics mapping may improve.)
    {
        "name": "kan_exogenous_only_cpu",
        "target": "load",
        "use_gpu": False,
        "hidden_width": 10,
        "hidden_mult": 0,
        "mult_arity": 2,
        "warmup_steps": 200,
        "sparsify_steps": 800,
        "refine_steps": 200,
        "sparsify_lamb": 0.01,
        "sparsify_lamb_l1": 1.0,
        "sparsify_lamb_entropy": 2.0,
        "max_train_rows": 0,  # 0 => full train split
        "include_base": True,
        "include_groups": "meteorology,solar,cyclic",
        "lag_series": "none",
        "lag_steps": "none",
    },
    # Example "final-ish" run (edit/enable when you want a longer training):
    # {
    #     "name": "kan_full_gpu",
    #     "target": "load",
    #     "use_gpu": True,
    #     "hidden_width": 10,
    #     "hidden_mult": 0,
    #     "mult_arity": 2,
    #     "warmup_steps": 200,
    #     "sparsify_steps": 800,
    #     "refine_steps": 200,
    #     "sparsify_lamb": 0.01,
    #     "sparsify_lamb_l1": 1.0,
    #     "sparsify_lamb_entropy": 2.0,
    #     "sparsify_lamb_coef": 0.0,
    #     "sparsify_lamb_coefdiff": 0.0,
    #     "max_train_rows": 0,  # 0 => full train split
    #     "include_base": True,
    #     "include_groups": "meteorology,solar,cyclic",
    #     "lag_series": "load,wind,solar",
    #     "lag_steps": "1,12,48",
    # },
    # (Old commented "physics-first" example moved above and enabled.)
]

# Symbolic extraction sweep for each selected KAN-train run.
KAN_SYMBOLIC_SWEEP: list[dict[str, Any]] = [
    {
        "name": "sym_r2_0.95_defaultlib",
        "r2_threshold": 0.95,
        "weight_simple": 0.9,
        "fix_below_threshold_to_zero": False,
        "sample_rows": 20_000,
        "lib": "default",
    },
    {
        "name": "sym_r2_0.90_no_exp_gaussian",
        "r2_threshold": 0.90,
        "weight_simple": 0.85,
        "fix_below_threshold_to_zero": False,
        "sample_rows": 20_000,
        "lib": "x,x^2,x^3,x^4,sin,cos,abs",
    },
]

# Baselines (optional)
RUN_TORCH_BASELINES = False
TORCH_BASELINES = [
    {"model_type": "mlp", "target": "load"},
    {"model_type": "lstm", "target": "load"},
]
RUN_PYSR_BASELINE = False
PYSR_BASELINE = {"target": "load"}

# Local evaluation / plots (best-effort)
RUN_LOCAL_EVAL = True
LOCAL_OUT_DIR = Path("doc/paper_assets")

# If True, generate `doc/paper_assets/ASSET_INDEX.md` at end.
BUILD_ASSET_INDEX = True


# =============================================================================
# Implementation
# =============================================================================


@dataclass
class CmdResult:
    cmd: list[str]
    returncode: int
    output: str


def _utc_session_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    return f"{ts}_{os.getpid()}"


def _print_cmd(cmd: list[str]) -> None:
    printable = " ".join([json.dumps(c) if (" " in c or "\t" in c) else c for c in cmd])
    print(f"\n$ {printable}", flush=True)


def run_cmd(cmd: list[str], *, dry_run: bool, cwd: Path | None = None, env: dict[str, str] | None = None) -> CmdResult:
    _print_cmd(cmd)
    if dry_run:
        return CmdResult(cmd=cmd, returncode=0, output="")

    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert proc.stdout is not None
    out_lines: list[str] = []
    for line in proc.stdout:
        print(line, end="", flush=True)
        out_lines.append(line)
    rc = int(proc.wait())
    out = "".join(out_lines)
    return CmdResult(cmd=cmd, returncode=rc, output=out)


def extract_last_json(text: str) -> Any:
    """
    Modal logs include multi-line JSON printed by our jobs (indent=2), often
    mixed with other logs (and sometimes followed by additional lines, e.g.
    `data_pipeline.py` sync messages).

    This extracts the last JSON blob we can decode, preferring a dict that
    looks like a run payload (has `run_id` or `status`).
    """
    decoder = json.JSONDecoder()
    idxs = [i for i, ch in enumerate(text) if ch in "{["]
    last_any: Any | None = None
    for i in reversed(idxs):
        try:
            obj, _end = decoder.raw_decode(text[i:])
        except Exception:
            continue
        last_any = obj
        if isinstance(obj, dict) and ("run_id" in obj or "status" in obj):
            return obj
    if last_any is not None:
        return last_any
    raise ValueError("Failed to locate JSON in command output")


def modal_run(job: Path, args: list[str], *, dry_run: bool) -> tuple[CmdResult, dict[str, Any] | None]:
    cmd = ["modal", "run", str(job)] + args
    res = run_cmd(cmd, dry_run=dry_run, cwd=REPO_ROOT)
    if res.returncode != 0 or dry_run:
        return res, None
    try:
        payload = extract_last_json(res.output)
    except Exception as e:  # noqa: BLE001
        print(f"[WARN] Could not parse JSON result from modal output: {e}")
        payload = None
    if payload is not None and not isinstance(payload, dict):
        print(f"[WARN] Parsed JSON is not a dict (type={type(payload)}); ignoring")
        payload = None
    return res, payload


def modal_run_detached(job: Path, args: list[str], *, dry_run: bool) -> CmdResult:
    # `modal run -d` ensures remote execution continues if this local process dies/disconnects.
    cmd = ["modal", "run", "-d", str(job)] + args
    return run_cmd(cmd, dry_run=dry_run, cwd=REPO_ROOT)


def _slug(s: str) -> str:
    s = str(s).strip().lower()
    out: list[str] = []
    prev_us = False
    for ch in s:
        ok = ("a" <= ch <= "z") or ("0" <= ch <= "9")
        if ok:
            out.append(ch)
            prev_us = False
        else:
            if not prev_us:
                out.append("_")
                prev_us = True
    slug = "".join(out).strip("_")
    return slug or "run"


def _deterministic_run_id(*parts: str) -> str:
    # Keep it filesystem/CLI friendly (Modal run_id becomes the run directory name in the volume).
    cleaned = [_slug(p) for p in parts if str(p).strip()]
    return "__".join([p for p in cleaned if p])


def _parse_phases(phases_csv: str) -> set[str]:
    allowed = {"data", "train", "symbolic", "baselines", "local"}
    raw = [p.strip().lower() for p in str(phases_csv).split(",") if p.strip()]
    if not raw:
        return set(allowed)
    unknown = sorted({p for p in raw if p not in allowed})
    if unknown:
        raise ValueError(f"Unknown phases: {unknown}. Allowed: {sorted(allowed)}")
    return set(raw)


def sync_run(run_id: str, *, dry_run: bool) -> CmdResult:
    env = dict(os.environ)
    env["VOLUME_NAME"] = VOLUME_NAME
    return run_cmd([str(REPO_ROOT / "scripts" / "sync_from_modal.sh"), run_id], dry_run=dry_run, cwd=REPO_ROOT, env=env)


def _compute_test_metrics(run_dir: Path) -> dict[str, float] | None:
    pred_path = run_dir / "artifacts" / "predictions_test.parquet"
    if not pred_path.exists():
        return None
    try:
        import pandas as pd

        from src.kan_sr.metrics import mae, r2, rmse

        df = pd.read_parquet(pred_path).dropna(subset=["y_true", "y_pred"])
        if len(df) == 0:
            return None
        y_true = df["y_true"].to_numpy(dtype="float64")
        y_pred = df["y_pred"].to_numpy(dtype="float64")
        return {"rmse": float(rmse(y_true, y_pred)), "mae": float(mae(y_true, y_pred)), "r2": float(r2(y_true, y_pred))}
    except Exception:  # noqa: BLE001
        return None


def run_local(script: Path, args: list[str], *, dry_run: bool) -> CmdResult:
    return run_cmd(["python3", str(script)] + args, dry_run=dry_run, cwd=REPO_ROOT)


def main() -> None:
    ap = argparse.ArgumentParser(description="Unified driver for Modal training + tuning + local evaluation.")
    ap.add_argument("--execute", action="store_true", help="Actually run Modal jobs + local scripts.")
    ap.add_argument("--dry-run", action="store_true", help="Print commands only (no execution).")
    ap.add_argument("--session-id", default=None, help="Optional fixed session id (folder name under doc/optimization/).")
    ap.add_argument(
        "--phases",
        default="data,train,symbolic,baselines,local",
        help="Comma-separated subset of phases: data,train,symbolic,baselines,local (default: all).",
    )
    ap.add_argument(
        "--detached-remote",
        action="store_true",
        help="Submit Modal jobs with `modal run -d` (remote continues if you shut down). Implies --no-auto-sync and skips dependent phases (symbolic/local).",
    )
    ap.add_argument(
        "--no-auto-sync",
        action="store_true",
        help="Do not auto-sync remote runs (use scripts/sync_from_modal.sh manually).",
    )
    args = ap.parse_args()

    dry_run = bool(args.dry_run or (not args.execute))
    selected_phases = _parse_phases(str(args.phases))
    detached_remote = bool(args.detached_remote)
    auto_sync = (not bool(args.no_auto_sync)) and (not detached_remote)
    session_id = str(args.session_id or _utc_session_id())
    session_dir = REPO_ROOT / "doc" / "optimization" / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = session_dir / "manifest.json"
    log_path = session_dir / "run_log.md"

    manifest: dict[str, Any] = {
        "session_id": session_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "volume_name": VOLUME_NAME,
        "dry_run": dry_run,
        "data_run_id": DATA_RUN_ID,
        "runs": [],
        "local_outputs": {"out_dir": str(LOCAL_OUT_DIR)},
        "errors": [],
    }

    def log_md(line: str) -> None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as f:
            f.write(line.rstrip() + "\n")

    def persist_manifest() -> None:
        # Write early/often so detached mode still leaves breadcrumbs if this process is killed.
        manifest_path.write_text(json.dumps(manifest, indent=2, default=str))

    log_md(f"# Optimization Session: {session_id}")
    log_md("")
    log_md(f"- created_at: `{manifest['created_at']}`")
    log_md(f"- volume: `{VOLUME_NAME}`")
    log_md(f"- dry_run: `{dry_run}`")
    log_md(f"- phases: `{','.join(sorted(selected_phases))}`")
    log_md(f"- detached_remote: `{detached_remote}`")
    log_md(f"- auto_sync: `{auto_sync}`")
    log_md("")
    persist_manifest()

    # Phase 1: data pipeline (optional)
    data_run_id = DATA_RUN_ID
    if RUN_DATA_PIPELINE and ("data" in selected_phases):
        log_md("## Phase 1: Data pipeline")
        job = REPO_ROOT / "modal_jobs" / "data_pipeline.py"
        cmd_args = [
            "--year",
            str(DATA_PIPELINE["year"]),
            "--iso",
            str(DATA_PIPELINE["iso"]),
            "--target",
            str(DATA_PIPELINE["target"]),
        ]
        if bool(DATA_PIPELINE.get("force")):
            cmd_args.append("--force")
        res, payload = modal_run(job, cmd_args, dry_run=dry_run)
        if payload and payload.get("run_id"):
            data_run_id = str(payload["run_id"])
            manifest["data_run_id"] = data_run_id
            log_md(f"- data_run_id: `{data_run_id}`")
        else:
            manifest["errors"].append({"stage": "data_pipeline", "returncode": res.returncode})

    # Select KAN train run ids: existing + newly trained
    selected_kan_train_run_ids: list[str] = list(EXISTING_KAN_TRAIN_RUN_IDS)
    submitted_training_detached = bool(detached_remote and ("train" in selected_phases) and len(KAN_TRAIN_SWEEP) > 0)

    if len(KAN_TRAIN_SWEEP) > 0 and ("train" in selected_phases):
        log_md("")
        log_md("## Phase 2: KAN training sweep")
        for cfg in KAN_TRAIN_SWEEP:
            name = str(cfg.get("name") or "kan_train")
            try:
                job = REPO_ROOT / "modal_jobs" / "kan_train.py"
                det_run_id = _deterministic_run_id(session_id, "kan_train", name)
                cmd_args = [
                    "--data-run-id",
                    str(data_run_id),
                    "--target",
                    str(cfg.get("target", "load")),
                    "--hidden-width",
                    str(int(cfg.get("hidden_width", 10))),
                    "--hidden-mult",
                    str(int(cfg.get("hidden_mult", 0))),
                    "--mult-arity",
                    str(int(cfg.get("mult_arity", 2))),
                    "--warmup-steps",
                    str(int(cfg.get("warmup_steps", 200))),
                    "--sparsify-steps",
                    str(int(cfg.get("sparsify_steps", 800))),
                    "--refine-steps",
                    str(int(cfg.get("refine_steps", 200))),
                    "--sparsify-lamb",
                    str(float(cfg.get("sparsify_lamb", 0.01))),
                    "--sparsify-lamb-l1",
                    str(float(cfg.get("sparsify_lamb_l1", 1.0))),
                    "--sparsify-lamb-entropy",
                    str(float(cfg.get("sparsify_lamb_entropy", 2.0))),
                    "--sparsify-lamb-coef",
                    str(float(cfg.get("sparsify_lamb_coef", 0.0))),
                    "--sparsify-lamb-coefdiff",
                    str(float(cfg.get("sparsify_lamb_coefdiff", 0.0))),
                    "--max-train-rows",
                    str(int(cfg.get("max_train_rows", 50_000))),
                    "--include-groups",
                    str(cfg.get("include_groups", "meteorology,solar,cyclic")),
                    "--lag-series",
                    str(cfg.get("lag_series", "load,wind,solar")),
                    "--lag-steps",
                    str(cfg.get("lag_steps", "1,12,48")),
                ]
                if bool(cfg.get("include_base", True)) is False:
                    cmd_args.append("--no-include-base")
                if bool(cfg.get("use_gpu", False)):
                    cmd_args.append("--use-gpu")
                if cfg.get("kind"):
                    cmd_args += ["--kind", str(cfg["kind"])]
                if detached_remote:
                    cmd_args += ["--run-id", det_run_id]

                log_md(f"- training `{name}` ...")
                if detached_remote:
                    run_id = det_run_id
                    log_md(f"  - run_id: `{run_id}` (detached)")
                    rec = {"stage": "kan_train", "name": name, "run_id": run_id, "data_run_id": data_run_id, "cfg": cfg, "detached": True, "submitted": False}
                    manifest["runs"].append(rec)
                    persist_manifest()
                    res = modal_run_detached(job, cmd_args, dry_run=dry_run)
                    rec["submitted"] = bool(res.returncode == 0)
                    rec["returncode"] = int(res.returncode)
                    persist_manifest()
                    if res.returncode == 0:
                        selected_kan_train_run_ids.append(run_id)
                else:
                    res, payload = modal_run(job, cmd_args, dry_run=dry_run)
                    run_id = str(payload["run_id"]) if payload and payload.get("run_id") else None
                    if run_id:
                        selected_kan_train_run_ids.append(run_id)
                        manifest["runs"].append(
                            {"stage": "kan_train", "name": name, "run_id": run_id, "data_run_id": data_run_id, "cfg": cfg}
                        )
                        log_md(f"  - run_id: `{run_id}`")
                        if auto_sync:
                            sync_res = sync_run(run_id, dry_run=dry_run)
                            if sync_res.returncode != 0:
                                manifest["errors"].append({"stage": "sync", "run_id": run_id, "returncode": sync_res.returncode})
                    else:
                        manifest["errors"].append({"stage": "kan_train", "name": name, "returncode": res.returncode})
                if detached_remote and (res.returncode != 0):
                    manifest["errors"].append({"stage": "kan_train", "name": name, "run_id": det_run_id, "returncode": res.returncode})
            except Exception as e:  # noqa: BLE001
                manifest["errors"].append({"stage": "kan_train", "name": name, "error": str(e)})
                log_md(f"  - ERROR: `{e}`")

    # Phase 3: symbolic extraction sweep
    selected_symbolic_run_ids: list[str] = []
    if len(KAN_SYMBOLIC_SWEEP) > 0 and len(selected_kan_train_run_ids) > 0 and ("symbolic" in selected_phases):
        log_md("")
        log_md("## Phase 3: Symbolic extraction sweep")
        if submitted_training_detached:
            log_md("- SKIPPED: Phase-2 training was submitted detached; wait for completion, then run symbolic in a separate session.")
        else:
            for train_run_id in selected_kan_train_run_ids:
                for cfg in KAN_SYMBOLIC_SWEEP:
                    name = f"{train_run_id}::{cfg.get('name','sym')}"
                    try:
                        job = REPO_ROOT / "modal_jobs" / "kan_symbolic.py"
                        det_run_id = _deterministic_run_id(session_id, "kan_symbolic", name)
                        cmd_args = [
                            "--train-run-id",
                            str(train_run_id),
                            "--r2-threshold",
                            str(float(cfg.get("r2_threshold", 0.99))),
                            "--weight-simple",
                            str(float(cfg.get("weight_simple", 0.9))),
                            "--sample-rows",
                            str(int(cfg.get("sample_rows", 10_000))),
                        ]
                        if bool(cfg.get("fix_below_threshold_to_zero", False)):
                            cmd_args.append("--fix-below-threshold-to-zero")
                        if cfg.get("lib") is not None:
                            cmd_args += ["--lib", str(cfg.get("lib"))]
                        if detached_remote:
                            cmd_args += ["--run-id", det_run_id]

                        log_md(f"- symbolic `{name}` ...")
                        if detached_remote:
                            run_id = det_run_id
                            log_md(f"  - run_id: `{run_id}` (detached)")
                            rec = {
                                "stage": "kan_symbolic",
                                "name": name,
                                "run_id": run_id,
                                "train_run_id": train_run_id,
                                "cfg": cfg,
                                "detached": True,
                                "submitted": False,
                            }
                            manifest["runs"].append(rec)
                            persist_manifest()
                            res = modal_run_detached(job, cmd_args, dry_run=dry_run)
                            rec["submitted"] = bool(res.returncode == 0)
                            rec["returncode"] = int(res.returncode)
                            persist_manifest()
                            if res.returncode == 0:
                                selected_symbolic_run_ids.append(run_id)
                            else:
                                manifest["errors"].append({"stage": "kan_symbolic", "name": name, "run_id": det_run_id, "returncode": res.returncode})
                        else:
                            res, payload = modal_run(job, cmd_args, dry_run=dry_run)
                            run_id = str(payload["run_id"]) if payload and payload.get("run_id") else None
                            if run_id:
                                selected_symbolic_run_ids.append(run_id)
                                manifest["runs"].append(
                                    {"stage": "kan_symbolic", "name": name, "run_id": run_id, "train_run_id": train_run_id, "cfg": cfg}
                                )
                                log_md(f"  - run_id: `{run_id}`")
                                if auto_sync:
                                    sync_res = sync_run(run_id, dry_run=dry_run)
                                    if sync_res.returncode != 0:
                                        manifest["errors"].append({"stage": "sync", "run_id": run_id, "returncode": sync_res.returncode})
                            else:
                                manifest["errors"].append({"stage": "kan_symbolic", "name": name, "returncode": res.returncode})
                    except Exception as e:  # noqa: BLE001
                        manifest["errors"].append({"stage": "kan_symbolic", "name": name, "error": str(e)})
                        log_md(f"  - ERROR: `{e}`")

    # Phase 4: baselines (optional)
    selected_baseline_run_ids: list[str] = []
    if RUN_TORCH_BASELINES and ("baselines" in selected_phases):
        log_md("")
        log_md("## Phase 4: Torch baselines")
        for b in TORCH_BASELINES:
            try:
                job = REPO_ROOT / "modal_jobs" / "baseline_torch.py"
                cmd_args = [
                    "--data-run-id",
                    str(data_run_id),
                    "--model-type",
                    str(b["model_type"]),
                    "--target",
                    str(b.get("target", "load")),
                ]
                res, payload = modal_run(job, cmd_args, dry_run=dry_run)
                run_id = str(payload["run_id"]) if payload and payload.get("run_id") else None
                if run_id:
                    selected_baseline_run_ids.append(run_id)
                    manifest["runs"].append({"stage": "baseline_torch", "name": str(b["model_type"]), "run_id": run_id})
                    log_md(f"- {b['model_type']} run_id: `{run_id}`")
                    if auto_sync:
                        sync_run(run_id, dry_run=dry_run)
            except Exception as e:  # noqa: BLE001
                manifest["errors"].append({"stage": "baseline_torch", "error": str(e)})

    if RUN_PYSR_BASELINE and ("baselines" in selected_phases):
        log_md("")
        log_md("## Phase 4: PySR baseline")
        try:
            job = REPO_ROOT / "modal_jobs" / "pysr_baseline.py"
            cmd_args = ["--data-run-id", str(data_run_id), "--target", str(PYSR_BASELINE.get("target", "load"))]
            res, payload = modal_run(job, cmd_args, dry_run=dry_run)
            run_id = str(payload["run_id"]) if payload and payload.get("run_id") else None
            if run_id:
                selected_baseline_run_ids.append(run_id)
                manifest["runs"].append({"stage": "baseline_pysr", "name": "pysr", "run_id": run_id})
                log_md(f"- pysr run_id: `{run_id}`")
                if auto_sync:
                    sync_run(run_id, dry_run=dry_run)
            else:
                manifest["errors"].append({"stage": "baseline_pysr", "returncode": res.returncode})
        except Exception as e:  # noqa: BLE001
            manifest["errors"].append({"stage": "baseline_pysr", "error": str(e)})

    # Local evaluation / plots
    if RUN_LOCAL_EVAL and not dry_run and ("local" in selected_phases) and (not detached_remote):
        log_md("")
        log_md("## Local evaluation + plots")

        run_dirs: list[Path] = []
        for rid in selected_kan_train_run_ids + selected_symbolic_run_ids + selected_baseline_run_ids:
            p = REPO_ROOT / "runs" / rid
            if p.exists():
                run_dirs.append(p)

        # Best-effort: attach physics mapping + sensitivity to each symbolic run.
        for rid in selected_symbolic_run_ids:
            sym_dir = REPO_ROOT / "runs" / rid
            if not sym_dir.exists():
                continue
            run_local(REPO_ROOT / "scripts" / "physics_mapping.py", ["--symbolic-run", str(sym_dir), "--out-dir", str(LOCAL_OUT_DIR)], dry_run=dry_run)
            run_local(
                REPO_ROOT / "scripts" / "sensitivity_analysis.py",
                ["--symbolic-run", str(sym_dir), "--out-dir", str(LOCAL_OUT_DIR)],
                dry_run=dry_run,
            )

        # Comparison table + pareto plot
        if len(run_dirs) > 0:
            args_eval: list[str] = ["--out-dir", str(LOCAL_OUT_DIR)]
            for p in run_dirs:
                args_eval += ["--run", str(p)]
            run_local(REPO_ROOT / "scripts" / "evaluate_runs.py", args_eval, dry_run=dry_run)

            # Basic figures for each run (timeseries/residuals/latex render)
            args_fig: list[str] = ["--out-dir", str(LOCAL_OUT_DIR / "figures")]
            for p in run_dirs:
                args_fig += ["--run", str(p)]
            run_local(REPO_ROOT / "scripts" / "make_thesis_figures.py", args_fig, dry_run=dry_run)

        # Record metrics snapshot into manifest
        metrics_rows = []
        for p in run_dirs:
            m = _compute_test_metrics(p)
            if m is None:
                continue
            metrics_rows.append({"run_id": p.name, **m})
        manifest["metrics_snapshot"] = metrics_rows

    # Asset index (optional)
    if BUILD_ASSET_INDEX and not dry_run and ("local" in selected_phases) and (not detached_remote):
        run_local(REPO_ROOT / "scripts" / "build_asset_index.py", [], dry_run=dry_run)

    # Persist manifest (even for dry-run)
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str))
    log_md("")
    log_md(f"- manifest: `{manifest_path}`")
    log_md(f"- log: `{log_path}`")

    print(f"\n[done] session_dir={session_dir}")
    print(f"[done] manifest={manifest_path}")
    print(f"[done] log={log_path}")
    if detached_remote:
        print("\n[detached] Remote jobs were submitted with `modal run -d` (they continue if you shut down).")
        print("[detached] Manual sync example:")
        print(f"  VOLUME_NAME={VOLUME_NAME} {REPO_ROOT / 'scripts' / 'sync_from_modal.sh'} <run_id>")


if __name__ == "__main__":
    main()
