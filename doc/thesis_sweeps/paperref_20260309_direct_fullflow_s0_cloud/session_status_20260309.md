# Session Status

- session_id: `paperref_20260309_direct_fullflow_s0_cloud`
- created_at: `2026-03-09 00:35:24 CST`
- mode: `detached_remote_only`
- teacher_run_id: `paperref_20260306_fullflow__kan_delta_net_load_h6`
- target: `delta_net_load_h6`
- source_data_run_id: `2026-03-06_042129_03d4b407`
- derived_data_run_id: `paperref_20260306_fullflow__derived_h1_6_72_144_576`

## Policy

- 所有 direct Phase 3 尝试仅通过 `modal run -d` 提交。
- 不保留本地日志监听或本地轮询进程。
- 只在需要同步或收口时一次性查询 Modal 状态。

## Canonical Grid

- `20260309_modal_direct_fullflow__sym_strict_r2_0_98`
- `20260309_modal_direct_fullflow__sym_strict_r2_0_99`
- `20260309_modal_direct_fullflow__sym_strict_r2_0_995`
- `20260309_modal_direct_fullflow__sym_medium_r2_0_98`
- `20260309_modal_direct_fullflow__sym_medium_r2_0_99`
- `20260309_modal_direct_fullflow__sym_medium_r2_0_995`
- `20260309_modal_direct_fullflow__sym_strict_poly4_r2_0_99`
- `20260309_modal_direct_fullflow__sym_strict_poly4_r2_0_995`
- `20260309_modal_direct_fullflow__sym_strict_poly4_r2_0_999`

## Exploratory Sidecars

- `20260309_modal_direct_fullflow__sym_strict_r2_0_99_fast5k`
- `20260309_modal_direct_fullflow__sym_medium_r2_0_99_fast5k`

## App Snapshot

- `ap-ZlHT4BhKmueqjYhKyQDmrd`
- `ap-dwxeGR1cDGwhe4G67kZSEf`
- `ap-I6mEIpzAT8fHYlG5E88bOX`
- `ap-FFDGkgJgJVwJpMrNLv8FrW`
- `ap-oXuKNSDgFeDYqjCIdTwPca`
- `ap-6TH3aE0TZFvf58ULnXUED0`
- `ap-fQBODbrHaHmNBYPmI1mZim`
- `ap-BHxohSuiPB602oeMWhZ2w5`
- `ap-7a4AcDvSdQuqxf55n8a0wF`
- `ap-5QRh47RigRrW6UtBO3X5x8`
- `ap-djHFpj3hMIlnMJAEerRRdk`

## On-Demand Resume

1. 查询状态：`modal app list --json`
2. 同步结果：`VOLUME_NAME=kan-sr scripts/sync_from_modal.sh <run_id>`
3. 同步后再执行本地重建、评估、资产索引更新。

## Observed Warning

- `kan_symbolic` 在启动阶段持续告警：`is_night` 不在 `scaler_params` 中，公式反归一化时使用 `mean=0,std=1`。该问题未阻塞提交，但需要在后续同步后核查其是否影响 direct 公式质量。

## Sync Outcome (2026-03-09)

- 同步巡检见 `doc/thesis_sweeps/paperref_20260309_direct_fullflow_s0_cloud/direct_sync_status_20260309.csv`。
- 11 个 direct run 中，只有 `20260309_modal_direct_fullflow__sym_strict_r2_0_99_fast5k` 的 `artifacts/` 目录可见。
- 已对该 fast5k run 完成本地同步、重建、评估、出图与物理映射；摘要见 `doc/paper_assets/paper_delivery_20260306/direct_teacher_fast5k_assessment_20260309.csv`。
- 当前 direct fast5k 的 abs(test) `rmse=3797.18`、`skill=-0.466`、`complexity=433`，未达到“稳定/可复算/正 skill”的验收门槛。
- 结论：direct S0 路线本轮只形成失败证据，不进入正文主结论；成功公式主路径继续使用 S3 结构化分解。
