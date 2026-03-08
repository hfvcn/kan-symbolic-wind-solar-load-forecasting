# Session Status

## Session

- session_id: `paperref_20260306_121725_v2`
- source_data_run_id: `2026-03-06_041802_0ad5813e`
- derived_data_run_id: `paperref_20260306_121725__derived_h1_6`
- paper_reference_dir: `doc/paper_assets/paper_reference_paperref_20260306_121725_v2`

## Completed Local Runs

- KAN train: `paperref_20260306_121725_v2__s1_delta_net_load_h6`
- KAN train: `paperref_20260306_121725_v2__s3_comp_load_delta_h6`
- KAN train: `paperref_20260306_121725_v2__s3_comp_wind_delta_h6`
- KAN train: `paperref_20260306_121725_v2__s3_comp_solar_delta_h6`
- KAN train: `paperref_20260306_121725_v2__s0p_wind_delta_h6`
- KAN train: `paperref_20260306_121725_v2__s0p_solar_delta_h6`
- Baseline: `paperref_20260306_121725_v2__baseline_torch_mlp_paperref_20260306_121725_v2_s1_delta_net_load_h6`
- Structured combo: `paperref_20260306_121725_v2__s3_combo_net_load`
- Symbolic total: `24`

## Symbolic Retry State

- `symbolic_spawns_detached_retry2.json`:
  - 3 runs `SUCCESS`
  - 20 runs `TERMINATED`
  - `0.99 solar` 来自更早 detached local-entrypoint 结果，已同步到本地
- `symbolic_spawns_detached_retry3_cpu.json`:
  - resubmitted_at: `2026-03-06T05:41:17.328114Z`
  - app id: `ap-mGqtlnL4v36SGEDXsOONO2`
  - stopped_at: `2026-03-06 15:07:50 +08:00`
  - result: 20 / 20 `SUCCESS`

## Current Snapshot

- session `paper_assets` 和 `paper_reference` 目录已经包含全部 24 个完整 symbolic 结果
- `session_meta/` 已收录：
  - `resume_after_timeout.json`
  - `symbolic_spawns_after_timeout.json`
  - `symbolic_spawns_detached.json`
  - `symbolic_spawns_detached_retry2.json`
  - `symbolic_spawns_detached_retry3_cpu.json`
- 全量测试：`python3 -m unittest discover -s tests -p 'test_*.py'` 通过（48 tests, OK）
