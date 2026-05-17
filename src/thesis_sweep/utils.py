from __future__ import annotations

import json
import os
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

VOLUME_NAME = os.environ.get("VOLUME_NAME", "kan-sr")

KAN_STEPS = {"warmup_steps": 200, "sparsify_steps": 800, "refine_steps": 200}

SYMBOLIC_SAFE_EXP_CLIP = 10.0
SYMBOLIC_EVAL_CLIP_QUANTILES = (0.01, 0.99)

S0_R2_GRID_MAIN = (0.98, 0.99, 0.995)
S0_R2_GRID_STRICT_ENHANCED = (0.99, 0.995, 0.999)

LIB_STRICT = "x,x^2,x^3,sin,cos,abs"
LIB_MEDIUM = "x,x^2,x^3,sin,cos,abs,exp"
LIB_STRICT_POLY4 = "x,x^2,x^3,x^4,sin,cos,abs"


def utc_session_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    return f"{ts}_{uuid.uuid4().hex[:8]}"


def slug(s: str) -> str:
    out: list[str] = []
    prev_us = False
    for ch in str(s).strip().lower():
        ok = ("a" <= ch <= "z") or ("0" <= ch <= "9")
        if ok:
            out.append(ch)
            prev_us = False
            continue
        if not prev_us:
            out.append("_")
            prev_us = True
    return "".join(out).strip("_") or "run"


def det_run_id(session_id: str, name: str) -> str:
    return f"{slug(session_id)}__{slug(name)}"


def parse_csv_ints(s: str) -> tuple[int, ...]:
    out: list[int] = []
    for p in [x.strip() for x in str(s).split(",") if x.strip()]:
        out.append(int(p))
    return tuple(out)


def run_cmd(cmd: list[str], *, dry_run: bool, cwd: Path, env: dict[str, str]) -> None:
    print("[cmd]", " ".join(cmd), flush=True)
    if dry_run:
        return
    subprocess.run(cmd, cwd=str(cwd), env=env, check=True)


def modal_run(module_path: Path, args: list[str], *, detached: bool) -> list[str]:
    base = ["modal", "run"]
    if detached:
        base.append("-d")
    return base + [str(module_path)] + args


def sync_run(run_id: str, *, dry_run: bool) -> None:
    env = dict(os.environ)
    env["VOLUME_NAME"] = VOLUME_NAME
    run_cmd([str(REPO_ROOT / "scripts" / "sync_from_modal.sh"), run_id], dry_run=dry_run, cwd=REPO_ROOT, env=env)


def local_py(script: Path, args: list[str], *, dry_run: bool) -> None:
    run_cmd(["python3", str(script)] + args, dry_run=dry_run, cwd=REPO_ROOT, env=dict(os.environ))


def write_manifest(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))

