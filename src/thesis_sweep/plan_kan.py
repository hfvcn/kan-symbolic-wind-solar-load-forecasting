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
    sparsify_lamb: float | None = None,
    sparsify_lamb_entropy: float | None = None,
    hidden_width_override: int | None = None,
    force_no_warmup_update_grid: bool = False,
    seed: int | None = None,
) -> list[str]:
    hidden_layers = str(args.kan_hidden_layers).strip()
    # Use caller-supplied lamb override; fall back to CLI arg; fall back to modal default (0.01).
    lamb = sparsify_lamb if sparsify_lamb is not None else getattr(args, "sparsify_lamb", None)
    lamb_entropy = sparsify_lamb_entropy if sparsify_lamb_entropy is not None else getattr(args, "sparsify_lamb_entropy", None)
    hw = str(hidden_width_override) if hidden_width_override is not None else (str(args.kan_hidden_width).strip() or "10")
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
        hw,
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
    if lamb is not None:
        cmd_args += ["--sparsify-lamb", str(float(lamb))]
    if lamb_entropy is not None:
        cmd_args += ["--sparsify-lamb-entropy", str(float(lamb_entropy))]
    if hidden_layers:
        cmd_args += ["--hidden-layers", hidden_layers]
    if not include_base:
        cmd_args.append("--no-include-base")
    if bool(args.no_warmup_update_grid) or force_no_warmup_update_grid:
        cmd_args.append("--no-warmup-update-grid")
    if seed is not None:
        cmd_args += ["--seed", str(int(seed))]
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
    sparsify_lamb: float | None = None,
    sparsify_lamb_entropy: float | None = None,
    hidden_width_override: int | None = None,
    force_no_warmup_update_grid: bool = False,
    seed: int | None = None,
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
        sparsify_lamb=sparsify_lamb,
        sparsify_lamb_entropy=sparsify_lamb_entropy,
        hidden_width_override=hidden_width_override,
        force_no_warmup_update_grid=force_no_warmup_update_grid,
        seed=seed,
    )
    return PlannedCmd(name="kan_train", run_id=run_id, cmd=cmd), run_id


def _append_kan_train(
    planned: list[PlannedCmd],
    mapping: dict[str, str],
    *,
    args: argparse.Namespace,
    session_id: str,
    detached: bool,
    derived_id: str,
    map_label: str,
    name: str,
    target_col: str,
    include_groups: str,
    lag_steps: str,
    include_base: bool,
    lag_series: str,
    force_no_warmup_update_grid: bool = False,
    seed: int | None = None,
) -> None:
    cmd, run_id = _plan_kan_train(
        args=args,
        session_id=session_id,
        detached=detached,
        derived_id=derived_id,
        name=name,
        target_col=target_col,
        include_groups=include_groups,
        lag_steps=lag_steps,
        include_base=include_base,
        lag_series=lag_series,
        force_no_warmup_update_grid=force_no_warmup_update_grid,
        seed=seed,
    )
    planned.append(cmd)
    mapping[run_id] = map_label


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


def plan_s2b(
    args: argparse.Namespace, *, session_id: str, detached: bool, derived_id: str
) -> tuple[list[PlannedCmd], dict[str, str]]:
    """S2-blocking: interventional test of autoregressive shortcut competition.

    For each seed (1-5), train:
    - Focused wind teacher with wind lags (unblocked baseline)
    - Focused wind teacher WITHOUT wind lags (blocked — lag_series="load")
    - Direct net_load teacher with full canonical lags (unblocked)
    - Direct net_load teacher WITHOUT wind/solar lags (blocked — lag_series="load")

    The ΔVER between blocked and unblocked conditions measures
    the competition pressure of autoregressive shortcuts.
    """
    planned: list[PlannedCmd] = []
    mapping: dict[str, str] = {}
    seeds = [1, 2, 3, 4, 5]

    for s in seeds:
        _append_kan_train(
            planned,
            mapping,
            args=args,
            session_id=session_id,
            detached=detached,
            derived_id=derived_id,
            map_label=f"wind_unblocked_s{s}",
            name=f"s2b_wind_unblocked_seed{s}",
            target_col="delta_wind_h6",
            include_groups="cyclic,meteo_wind",
            lag_steps="24,48",
            include_base=False,
            lag_series="wind",
            seed=s,
        )

        _append_kan_train(
            planned,
            mapping,
            args=args,
            session_id=session_id,
            detached=detached,
            derived_id=derived_id,
            map_label=f"wind_blocked_s{s}",
            name=f"s2b_wind_blocked_seed{s}",
            target_col="delta_wind_h6",
            include_groups="cyclic,meteo_wind",
            lag_steps="none",
            include_base=False,
            lag_series="none",
            seed=s,
        )

        # --- Case 4a: Direct net_load, UNBLOCKED (canonical no-base teacher) ---
        _append_kan_train(
            planned,
            mapping,
            args=args,
            session_id=session_id,
            detached=detached,
            derived_id=derived_id,
            map_label=f"direct_unblocked_s{s}",
            name=f"s2b_direct_unblocked_seed{s}",
            target_col="delta_net_load_h6",
            include_groups="meteorology,solar,cyclic",
            lag_steps="12,24,48",
            include_base=False,
            lag_series="load,wind,solar",
            seed=s,
            force_no_warmup_update_grid=True,
        )

        # --- Case 4b: Direct net_load, BLOCKED (only load lags) ---
        _append_kan_train(
            planned,
            mapping,
            args=args,
            session_id=session_id,
            detached=detached,
            derived_id=derived_id,
            map_label=f"direct_blocked_s{s}",
            name=f"s2b_direct_blocked_seed{s}",
            target_col="delta_net_load_h6",
            include_groups="meteorology,solar,cyclic",
            lag_steps="12,24,48",
            include_base=False,
            lag_series="load",
            seed=s,
            force_no_warmup_update_grid=True,
        )

    return planned, mapping


def plan_s2c(
    args: argparse.Namespace, *, session_id: str, detached: bool, derived_id: str
) -> tuple[list[PlannedCmd], dict[str, str]]:
    """S2-strong-blocking: direct net-load variant with all autoregressive lags removed.

    This does not replace matched Case 4 (`s2b`); it adds a stronger intervention
    arm so we can test whether fully removing lag shortcuts yields cleaner
    physical-edge recovery than the load-only blocked condition.
    """
    planned: list[PlannedCmd] = []
    mapping: dict[str, str] = {}
    seeds = [1, 2, 3, 4, 5]

    for s in seeds:
        _append_kan_train(
            planned,
            mapping,
            args=args,
            session_id=session_id,
            detached=detached,
            derived_id=derived_id,
            map_label=f"direct_fully_blocked_s{s}",
            name=f"s2c_direct_fully_blocked_seed{s}",
            target_col="delta_net_load_h6",
            include_groups="meteorology,solar,cyclic",
            lag_steps="none",
            include_base=False,
            lag_series="none",
            seed=s,
            force_no_warmup_update_grid=True,
        )

    return planned, mapping


def plan_s0_physics(
    args: argparse.Namespace, *, session_id: str, detached: bool, derived_id: str
) -> tuple[list[PlannedCmd], dict[str, str], dict[str, str]]:
    """物理因子专用实验（S0-physics）：松正则 lambda=0.005，直接预测风光分量增量。

    目的：让 wind_speed_hub_est / ghi_temp_corr_w_m2 等物理量保住激活边，
    进而显式进入符号回归公式。
    """
    planned: list[PlannedCmd] = []
    mapping: dict[str, str] = {}
    comp_runs: dict[str, str] = {}

    configs = [
        # (comp_key, name_suffix, target, groups, lag_steps_str, lag_series)
        (
            "physics_wind",
            "s0p_wind_delta_h6",
            "delta_wind_h6",
            "cyclic,meteo_wind,meteo_irradiance,meteo_temp,solar_flag",
            "12,24,48",
            "wind",
        ),
        (
            "physics_solar",
            "s0p_solar_delta_h6",
            "delta_solar_h6",
            "cyclic,solar_geom,solar_flag,meteo_irradiance,meteo_temp",
            "12,24,48",
            "solar",
        ),
    ]
    for comp_key, name, target_col, groups, lag_steps, lag_series in configs:
        cmd, run_id = _plan_kan_train(
            args=args,
            session_id=session_id,
            detached=detached,
            derived_id=derived_id,
            name=name,
            target_col=target_col,
            include_groups=groups,
            lag_steps=lag_steps,
            include_base=False,
            lag_series=lag_series,
            sparsify_lamb=0.005,          # 关键：松正则，防止物理量被剪
            sparsify_lamb_entropy=1.5,    # 关键：降低熵惩罚
        )
        planned.append(cmd)
        mapping[run_id] = target_col
        comp_runs[comp_key] = run_id

    return planned, mapping, comp_runs


def plan_s4_pure(
    args: argparse.Namespace, *, session_id: str, detached: bool, derived_id: str
) -> tuple[list[PlannedCmd], dict[str, str], dict[str, str]]:
    """方案 B — 纯物理（S4-Pure）：去掉所有 lag，切换到绝对值目标，强制模型从物理量学习。

    hidden_width=15, include_base=False, sparsify_lamb=0.001, sparsify_lamb_entropy=1.0
    """
    planned: list[PlannedCmd] = []
    mapping: dict[str, str] = {}
    comp_runs: dict[str, str] = {}

    configs = [
        # (comp_key, name, target, groups)
        (
            "s4_wind",
            "s4_pure_wind_abs_h6",
            "wind_h6",
            "cyclic,meteo_wind,meteo_irradiance,meteo_temp",
        ),
        (
            "s4_solar",
            "s4_pure_solar_abs_h6",
            "solar_h6",
            "cyclic,solar_geom,solar_flag,meteo_irradiance,meteo_temp",
        ),
        (
            "s4_load",
            "s4_pure_load_abs_h6",
            "net_load_h6",
            "cyclic,meteo_temp,meteo_degree,meteo_pressure,meteo_wind,meteo_irradiance,solar_flag",
        ),
    ]
    for comp_key, name, target_col, groups in configs:
        cmd, run_id = _plan_kan_train(
            args=args,
            session_id=session_id,
            detached=detached,
            derived_id=derived_id,
            name=name,
            target_col=target_col,
            include_groups=groups,
            lag_steps="none",
            include_base=False,
            lag_series="none",
            sparsify_lamb=0.001,
            sparsify_lamb_entropy=1.0,
            hidden_width_override=15,
            force_no_warmup_update_grid=True,
        )
        planned.append(cmd)
        mapping[run_id] = target_col
        comp_runs[comp_key] = run_id

    return planned, mapping, comp_runs


def plan_s0a_physics(
    args: argparse.Namespace, *, session_id: str, detached: bool, derived_id: str
) -> tuple[list[PlannedCmd], dict[str, str], dict[str, str]]:
    """方案 A — 松正则 + lag（S0A）：保留 lag，进一步降低正则到 0.001，看物理量能否存活。

    hidden_width=15, include_base=False, sparsify_lamb=0.001, sparsify_lamb_entropy=1.0
    """
    planned: list[PlannedCmd] = []
    mapping: dict[str, str] = {}
    comp_runs: dict[str, str] = {}

    configs = [
        # (comp_key, name, target, groups, lag_steps, lag_series)
        (
            "s0a_wind",
            "s0a_wind_delta_h6",
            "delta_wind_h6",
            "cyclic,meteo_wind,meteo_irradiance,meteo_temp,solar_flag",
            "12,24,48",
            "wind",
        ),
        (
            "s0a_solar",
            "s0a_solar_delta_h6",
            "delta_solar_h6",
            "cyclic,solar_geom,solar_flag,meteo_irradiance,meteo_temp",
            "12,24,48",
            "solar",
        ),
    ]
    for comp_key, name, target_col, groups, lag_steps, lag_series in configs:
        cmd, run_id = _plan_kan_train(
            args=args,
            session_id=session_id,
            detached=detached,
            derived_id=derived_id,
            name=name,
            target_col=target_col,
            include_groups=groups,
            lag_steps=lag_steps,
            include_base=False,
            lag_series=lag_series,
            sparsify_lamb=0.001,
            sparsify_lamb_entropy=1.0,
            hidden_width_override=15,
            force_no_warmup_update_grid=True,
        )
        planned.append(cmd)
        mapping[run_id] = target_col
        comp_runs[comp_key] = run_id

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
    if "s2b" in sweeps:
        cmds, m = plan_s2b(args, session_id=session_id, detached=detached, derived_id=derived_id)
        planned += cmds
        mapping.update(m)
    if "s2c" in sweeps:
        cmds, m = plan_s2c(args, session_id=session_id, detached=detached, derived_id=derived_id)
        planned += cmds
        mapping.update(m)
    if "s3" in sweeps:
        cmds, m, cr = plan_s3(args, session_id=session_id, detached=detached, derived_id=derived_id)
        planned += cmds
        mapping.update(m)
        comp_runs.update(cr)
        # S0-physics always runs alongside S3 to get physical factor formulas
        cmds, m, cr = plan_s0_physics(args, session_id=session_id, detached=detached, derived_id=derived_id)
        planned += cmds
        mapping.update(m)
        comp_runs.update(cr)
    if "s4" in sweeps:
        cmds, m, cr = plan_s4_pure(args, session_id=session_id, detached=detached, derived_id=derived_id)
        planned += cmds
        mapping.update(m)
        comp_runs.update(cr)
    if "s0a" in sweeps:
        cmds, m, cr = plan_s0a_physics(args, session_id=session_id, detached=detached, derived_id=derived_id)
        planned += cmds
        mapping.update(m)
        comp_runs.update(cr)

    return planned, mapping, comp_runs
