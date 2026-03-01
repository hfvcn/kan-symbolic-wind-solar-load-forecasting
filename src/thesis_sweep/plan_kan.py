from __future__ import annotations

import argparse

from src.thesis_sweep.types import PlannedCmd
from src.thesis_sweep.utils import KAN_STEPS, REPO_ROOT, det_run_id, modal_run, parse_csv_ints


def _plan_kan_train_cmd(
    *,
    args: argparse.Namespace,
    detached: bool,
    derived_id: str,
    run_id: str,
    kind: str,
    target_col: str,
    include_groups: str,
    lag_steps: str,
    include_base: bool,
    lag_series: str,
) -> list[str]:
    hidden_layers = str(args.kan_hidden_layers).strip()
    cmd_args = [
        "--data-run-id",
        derived_id,
        "--run-id",
        run_id,
        "--kind",
        kind,
        "--target",
        target_col,
        "--hidden-width",
        str(args.kan_hidden_width).strip() or "10",
        "--max-train-rows",
        "50000",
        "--include-groups",
        include_groups,
        "--lag-series",
        lag_series,
        "--lag-steps",
        lag_steps,
        "--warmup-steps",
        str(KAN_STEPS["warmup_steps"]),
        "--sparsify-steps",
        str(KAN_STEPS["sparsify_steps"]),
        "--refine-steps",
        str(KAN_STEPS["refine_steps"]),
    ]
    if hidden_layers:
        cmd_args += ["--hidden-layers", hidden_layers]
    if not include_base:
        cmd_args.append("--no-include-base")
    if bool(args.no_warmup_update_grid):
        cmd_args.append("--no-warmup-update-grid")
    if bool(args.use_gpu):
        cmd_args.append("--use-gpu")
    ts_opt = str(args.source_timestamp).strip() or None
    if ts_opt:
        cmd_args += ["--data-timestamp", ts_opt]
    return modal_run(REPO_ROOT / "modal_jobs" / "kan_train.py", cmd_args, detached=detached)


def _plan_kan_train(
    *,
    args: argparse.Namespace,
    session_id: str,
    detached: bool,
    derived_id: str,
    name: str,
    target_col: str,
    include_groups: str,
    lag_steps: str,
    include_base: bool,
    lag_series: str,
) -> tuple[PlannedCmd, str]:
    run_id = det_run_id(session_id, name)
    cmd = _plan_kan_train_cmd(
        args=args,
        detached=detached,
        derived_id=derived_id,
        run_id=run_id,
        kind=name,
        target_col=target_col,
        include_groups=include_groups,
        lag_steps=lag_steps,
        include_base=include_base,
        lag_series=lag_series,
    )
    return PlannedCmd(name="kan_train", run_id=run_id, cmd=cmd), run_id


def plan_s1(args: argparse.Namespace, *, session_id: str, detached: bool, derived_id: str) -> tuple[list[PlannedCmd], dict[str, str]]:
    planned: list[PlannedCmd] = []
    mapping: dict[str, str] = {}
    for h in parse_csv_ints(str(args.horizons)):
        lag = "12,24,48" if int(h) <= 12 else ("24,48" if int(h) <= 24 else "48")
        target_col = f"delta_net_load_h{h}"
        cmd, run_id = _plan_kan_train(
            args=args,
            session_id=session_id,
            detached=detached,
            derived_id=derived_id,
            name=f"s1_{target_col}",
            target_col=target_col,
            include_groups="meteorology,solar,cyclic",
            lag_steps=lag,
            include_base=True,
            lag_series="load,wind,solar",
        )
        planned.append(cmd)
        mapping[run_id] = target_col
    return planned, mapping


def plan_s2(args: argparse.Namespace, *, session_id: str, detached: bool, derived_id: str) -> tuple[list[PlannedCmd], dict[str, str]]:
    planned: list[PlannedCmd] = []
    mapping: dict[str, str] = {}
    base = ["cyclic", "solar_flag", "meteo_temp", "meteo_wind", "meteo_pressure", "meteo_degree"]
    variants = [
        ("full", [*base, "meteo_irradiance", "solar_geom"]),
        ("ghi_only", [*base, "meteo_irradiance"]),
        ("geom_only", [*base, "solar_geom"]),
        ("neither", [*base]),
    ]
    for h in parse_csv_ints(str(args.horizons)):
        lag = "12,24,48" if int(h) <= 12 else ("24,48" if int(h) <= 24 else "48")
        target_col = f"delta_net_load_h{h}"
        for suffix, groups in variants:
            cmd, run_id = _plan_kan_train(
                args=args,
                session_id=session_id,
                detached=detached,
                derived_id=derived_id,
                name=f"s2_{target_col}_{suffix}",
                target_col=target_col,
                include_groups=",".join(groups),
                lag_steps=lag,
                include_base=True,
                lag_series="load,wind,solar",
            )
            planned.append(cmd)
            mapping[run_id] = target_col
    return planned, mapping


def plan_s3(args: argparse.Namespace, *, session_id: str, detached: bool, derived_id: str) -> tuple[list[PlannedCmd], dict[str, str], dict[str, str]]:
    planned: list[PlannedCmd] = []
    mapping: dict[str, str] = {}
    comp_runs: dict[str, str] = {}

    def add_one(key: str, *, name: str, target_col: str, include_groups: str, lag_steps: str, lag_series: str) -> None:
        cmd, run_id = _plan_kan_train(
            args=args,
            session_id=session_id,
            detached=detached,
            derived_id=derived_id,
            name=name,
            target_col=target_col,
            include_groups=include_groups,
            lag_steps=lag_steps,
            include_base=False,
            lag_series=lag_series,
        )
        planned.append(cmd)
        mapping[run_id] = target_col
        comp_runs[key] = run_id

    add_one(
        "load",
        name="s3_comp_load_delta_h6",
        target_col="delta_load_h6",
        include_groups="cyclic,meteo_temp,meteo_degree,meteo_pressure,solar_flag",
        lag_steps="12,24,48",
        lag_series="load",
    )
    add_one(
        "wind",
        name="s3_comp_wind_delta_h6",
        target_col="delta_wind_h6",
        include_groups="cyclic,meteo_wind",
        lag_steps="24,48",
        lag_series="wind",
    )
    add_one(
        "solar",
        name="s3_comp_solar_delta_h6",
        target_col="delta_solar_h6",
        include_groups="cyclic,solar_geom,solar_flag,meteo_irradiance,meteo_temp",
        lag_steps="24,48",
        lag_series="solar",
    )
    return planned, mapping, comp_runs


def plan_kan_sweeps(args: argparse.Namespace, *, session_id: str, detached: bool, derived_id: str) -> tuple[list[PlannedCmd], dict[str, str], dict[str, str]]:
    sweeps = {s.strip().lower() for s in str(args.sweeps).split(",") if s.strip()}
    planned: list[PlannedCmd] = []
    mapping: dict[str, str] = {}
    comp_runs: dict[str, str] = {}

    if "s1" in sweeps:
        cmds, m = plan_s1(args, session_id=session_id, detached=detached, derived_id=derived_id)
        planned += cmds
        mapping.update(m)
    if "s2" in sweeps:
        cmds, m = plan_s2(args, session_id=session_id, detached=detached, derived_id=derived_id)
        planned += cmds
        mapping.update(m)
    if "s3" in sweeps:
        cmds, m, cr = plan_s3(args, session_id=session_id, detached=detached, derived_id=derived_id)
        planned += cmds
        mapping.update(m)
        comp_runs.update(cr)

    return planned, mapping, comp_runs

