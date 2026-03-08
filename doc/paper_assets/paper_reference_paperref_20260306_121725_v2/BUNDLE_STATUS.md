# Bundle Status

## Session

- session_id: `paperref_20260306_121725_v2`
- source_data_run_id: `2026-03-06_041802_0ad5813e`
- derived_data_run_id: `paperref_20260306_121725__derived_h1_6`
- refreshed comparison table: `paper_assets/comparison_table.csv`
- refreshed asset index snapshot: `ASSET_INDEX.md`

## Final State

- symbolic runs in bundle: `24 / 24`
- legacy detached symbolic success runs: `1`
- retry2 success runs: `3`
- retry2 terminated runs replaced by retry3_cpu: `20`
- retry3_cpu success runs: `20`
- pending symbolic runs: `0`
- status json: `symbolic_status_snapshot.json`

## Notes

- 当前论文引用目录已经包含全部 24 个完整 symbolic run。
- `session_meta/` 保留了 retry2 和 retry3_cpu 的提交记录，便于追溯。
- 旧的 pending symbolic 快照目录已移除。

## Example Complete Symbolic Runs

- `paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_solar_delta_h6`
- `paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_solar_delta_h6`
- `paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_solar_delta_h6`
- `paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_wind_delta_h6`
- `paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_wind_delta_h6`
- `paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_wind_delta_h6`
- `paperref_20260306_121725_v2__sym_strict_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6`
- `paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6`
