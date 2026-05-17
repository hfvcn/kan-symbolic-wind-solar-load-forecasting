# 论文落地 TODO（V3-修订版，2026-03-06）

目标：把现有工程闭环收敛成**论文级证据链**（主实验 + 机制验证 + 反例边界 + 稳健性统计 + 复杂度/精度权衡），而不是继续加新模块。

配套现状与审查快照：`doc/PROJECT_ARCHITECTURE_STATUS_FOR_AI_v3.md`

---

## 0. 论文主命题收口（必须先钉死，避免写散）

- [x] **一句话主命题**（写进摘要/答辩首页）：在 multi-horizon 的设置下，用稀疏 KAN + 符号提取，从风速/GHI/温度/历史量中提取可复算的解析关系，并用消融与反例边界证明“物理量入式/退式”主要由特征竞争与稀疏/剪枝轨迹共同决定。
- [x] **主结论 / 副结论 / 边界结论清单**：主结论绑定主实验表，副结论绑定 wind/solar 机制表，边界结论绑定 `delta_solar_h288` 反例；摘要、结论、答辩首页统一使用同一套表述。
- [x] **贡献点清单（3–5 条）**：每条对应一组可复现实验与一张图/一张表（禁止“只有观点没有证据”的贡献）。
- [x] **Claim 强度表（强说/弱说/边界）**：
  - 强说：有主表 + 消融/统计支撑的结论。
  - 弱说：只对特定数据集/特定 horizon/特定稀疏预算成立的结论。
  - 边界：明确的失败模式（如 solar `h=288` 越界崩坏）。
- [x] **Run 白名单**：正文只允许引用白名单里的 run_id；附录允许更多但必须可复现（manifest + 资产索引）。

状态（2026-03-09）：已完成；冻结稿已写入 `doc/paper_delivery_closure_20260306.md`，其中包含主命题、结论冻结、贡献点、claim 强度和 run 白名单。

---

## 1. 必须补的证据链（影响交付，按顺序执行）

### 1.1 主实验矩阵定版（论文主表的“设计”先固定）

- [x] **固定目标与 horizon（建议 2–3 个）**：
  - 主结果：`net_load`（或 `delta_net_load_h6` → 重建到 abs）优先；
  - 机制验证：solar 选 `h=72/h=144/h=576`（已有证据链），wind 选 `h=72/h=576`（补对称证据）。
- [x] **固定 baselines 范围**（正文只保留能回答问题的最小集合）：
  - persistence（按 `_h{n}` 做 `shift(n)`）；
  - baseline MLP（预算/特征对齐到对应 KAN run）；
  - （可选）PySR 基线：若能贡献“复杂度 vs 精度”对照就保留，否则降级到附录。
- [x] **固定指标与复杂度定义**：
  - 指标：RMSE / R² / skill（必选）；WAPE（若需要解释尺度）；
  - 复杂度：KAN 用 `edge_pruned_ratio` 或 active edge 数；公式用 `sympy_node_count`；baseline 用 `param_count`。

状态（2026-03-09）：已完成；主实验矩阵与口径冻结见 `doc/paper_delivery_closure_20260306.md` 第 5 节。

验收：主表结构在写作中不再变更（后续所有实验只是在该矩阵中填格子/补证据）。

### 1.2 口径门禁（delta→abs 重建与汇总一致）

- [x] 对所有 `delta_*` 目标：统一执行重建  
      `python3 scripts/reconstruct_predictions.py --run runs/<run_id>`
- [x] 汇总只使用 **abs(test)** 口径（重建后的 `predictions_test_reconstructed.parquet`），并确保 persistence 用 `shift(h)`。

状态（2026-03-09）：已完成；`scripts/reconstruct_predictions.py` 输出重建文件，`src/eval/runs.py` / `scripts/evaluate_runs.py` 已优先读取 `predictions_test_reconstructed.parquet` 并按 horizon 计算 persistence skill。

验收：`scripts/evaluate_runs.py` 的对比表不再混用 delta/abs（优先读取 reconstructed）。

### 1.3 主结果主表（预测有效 + 公平对照）

- [x] 选定一组“正文主结果” run（KAN + 对齐预算的 MLP + persistence），生成并冻结：
  - `doc/paper_assets/comparison_table.csv`
  - `doc/paper_assets/pareto_rmse_vs_complexity*.png`
- [x] 对主结果 run：生成图表与索引（见 3.1 的最小图表集合）。

状态（2026-03-09）：已完成；主表与 Pareto 已冻结在 `doc/paper_assets/paper_delivery_20260306/`，复现映射见 `doc/paper_assets/PAPER_REPRO_MAP_20260306.md`。

验收：答辩追问“你到底提升了什么/和什么比”时，能用主表 30 秒讲清楚。

### 1.4 wind/solar 机制验证（必须对称，形成完整证据链）

Solar（已具备雏形，补“论文级封装”）：
- [x] 把 `doc/solar_ablation_summary_20260304.csv` 对应的三组结论收敛成“条件边际贡献 + 剪枝轨迹敏感”的可引用段落（正文）。
- [x] 把 `h=144 both` 作为“竞争导致外生量被淘汰且性能更差”的反例（正文或 5.3 小结）。

Wind（必须补齐，与 solar 同级别证据）：
- [x] 复刻最小三组对照：`lags-only / meteo-only / both`，horizon 先做 `h=72` 与 `h=576`。
- [x] 输出至少包含：abs(test) 指标 + `wind_speed_*`（或 `meteo_wind`）的 active_edges 统计。
- [x] 若缺少汇总脚本：新增一个与 `scripts/summarize_solar_ablation.py` 同构的 wind 汇总脚本（输出 CSV，供论文直接引用）。

状态（2026-03-08）：已完成；正文可直接使用 wind/solar 对称机制表。证据：`doc/solar_ablation_summary_20260304.csv`、`doc/paper_assets/paper_delivery_20260306/wind_ablation_summary_20260306.csv`、`doc/paper_assets/comparison_table.csv`、`doc/paper_delivery_closure_20260306.md`。

验收：正文可以用“wind/solar 两行对照表”统一讲清机制，而不是只在 solar 侧成立。

### 1.5 成功公式案例（至少 1 个能写进正文的“成功公式”）

目标：把“可解释公式”从“产物存在”升级为“正文结论成立”。

- [x] 优先路线（不改 teacher）：已完成 `delta_net_load_h6` teacher 的 Phase 3 sweep（S0）验证；当前 canonical grid 未找到满足“稳定/可复算/正 skill”的 direct 配置，失败证据已固定。
- [x] 兜底路线（保证交付）：走 S3 结构化分解，对 wind/solar/load 子任务分别提取子公式，再组合成可解释的 net_load 叙事。

成功公式的最低验收（写进正文的门槛）：
- [x] test 上 **skill 为正且稳定**（至少 3-seed 不全翻车）；
- [x] 公式显式包含关键物理量（风速/GHI/温度至少各有一个在对应子公式或总公式里出现）；
- [x] 公式可渲染（LaTeX）可复算（`formula_eval_test.json` 与脚本复算一致）。

状态（2026-03-08）：已完成；正文主路径采用 S3 结构化分解，不再把 direct `delta_net_load_h6` teacher 公式当作唯一交付路径。证据：`doc/paper_delivery_closure_20260306.md`、`doc/paper_assets/paper_reference_paperref_20260306_121725_v2/run_refs/`（S3 load/solar/wind 公式工件）、`doc/paper_assets/paper_reference_paperref_20260306_121725_v2/paper_assets_snapshot/figures/`。
优先路线状态（2026-03-09）：已追加尝试 direct teacher S0；发现当前 `paperref_20260306_121725_v2__s1_delta_net_load_h6` 的 pruned 结构只剩 `load` 活跃边，因此新增改在 `paperref_20260306_fullflow__kan_delta_net_load_h6` 上补发 CPU symbolic（`20260309_modal_direct_fullflow__sym_*`）验证 direct 路线是否仍可成立。
当前执行策略（2026-03-09）：direct S0 已切换为纯云端 detached 运行，不再依赖本地常驻进程；提交记录与后续同步入口见 `doc/thesis_sweeps/paperref_20260309_direct_fullflow_s0_cloud/manifest.json` 与 `doc/thesis_sweeps/paperref_20260309_direct_fullflow_s0_cloud/session_status_20260309.md`。
同步结论（2026-03-09）：远端巡检见 `doc/thesis_sweeps/paperref_20260309_direct_fullflow_s0_cloud/direct_sync_status_20260309.csv`；11 个 direct run 中已有 6 个形成完整 run 并完成本地重建/评估，但全部 `skill<0`。最佳配置 `20260309_modal_direct_fullflow__sym_strict_r2_0_98` 的 abs(test) `rmse=3779.76`、`skill=-0.459`；其余 5 个仅留下远端部分公式工件，没有形成完整成功 run。当前正文仍以 S3 结构化分解为主路径。
后续决策（2026-03-09）：同一 `delta_net_load_h6` teacher 的 direct S0 到此终止，不再继续追加同 teacher 的 Phase 3 参数 sweep。若后续仍要推进 direct 路线，只允许进入“改 teacher / 改 Phase 2 结构”的新路线；当前 teacher 下的 direct 结果仅作为失败证据与反例材料保留。

### 1.6 反例边界（把弱点变贡献）

- [x] Solar `delta_solar_h288`：固定三层证据并写成论文段落模板：  
  1) val 不稳定预警（`eval_pruned.json`）  
  2) test 外推崩坏（分位数 + 越界率）  
  3) 最小修复对照（clip：风险缓解，不宣称性能提升）
- [x] 明确论文设定：Open-Meteo 历史档案为 **ex post explanatory setting**（避免被当作可上线预报特征）。

状态（2026-03-09）：已完成；证据与段落模板已冻结在 `doc/paper_delivery_closure_20260306.md` 与 `doc/paper_assets/paper_delivery_20260306/solar_h288_boundary_20260306.json`。

### 1.7 复杂度—精度 trade-off（把 Pareto 变成“正式结果”）

- [x] 在主实验矩阵内，对关键目标画 Pareto（RMSE vs complexity），并标注：
  - 物理变量是否入式（edges/公式包含变量）；
  - 解释性更强但精度下降的点（用于讨论章节）。

状态（2026-03-09）：已完成；主结果 Pareto 已落盘到 `doc/paper_assets/paper_delivery_20260306/pareto_rmse_vs_complexity.png`，主结果表同时保留 complexity 字段用于正文讨论。

验收：论文能回答“你牺牲了多少精度换来多少可解释性”。

---

## 2. 稳健性与统计补洞（答辩追问兜底：必须补，但可与 1.x 并行）

### 2.1 多 seed 稳健性（最少 3 seeds）

- [x] 主结果：`net_load_h6`（或 `delta_net_load_h6` abs 口径）补 3 seeds（KAN + baseline）。
- [x] 机制点：solar 选一个关键 horizon（如 `h=72` both），wind 选一个关键 horizon（如 `h=72` both）。
- [x] 公式点：对“成功公式配置”补 3 seeds（至少保证“能复现成功”的概率不是偶然）。

输出（建议落盘到 `doc/paper_assets/`）：
- [x] mean±std 的指标表（RMSE/R²/skill）；
- [x] “关键物理量入式概率”（`temp_*` / `ghi_*` / `wind_speed_*` / `wind_speed_*_cubed` 在 pruned 结构 edges>0、以及最终公式中显式出现的比例）。

状态（2026-03-09）：已完成；多 seed 稳健性结果已并入当前论文引用 bundle。索引与 run 集见 `doc/paper_assets/paper_reference_paperref_20260306_121725_v2/ASSET_INDEX.md`、`doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`，相关 seed 交叉验证说明见 `doc/paper_assets/paper_reference_paperref_20260306_121725_v2/paper_assets_snapshot/kan_pysr_cross_validation_2026-02-26_064508_3e631069.md`。

### 2.2 统计显著性（可用最轻量版本）

- [x] 对主结果与 baseline 做 paired 对比（同一 test 序列的误差差异），报告显著性与置信区间。

状态（2026-03-09）：已完成；结果见 `doc/paper_assets/paper_delivery_20260306/paired_significance_main_20260309.csv`。主结果 KAN 相对 matched MLP 的 absolute-error mean diff = 111.13，95% CI = [100.42, 122.29]，置换检验 `p=0.0005`。

---

## 3. 条件分层误差分析（回答“什么时候有效/什么时候失效”）

Solar：
- [x] day/night 分层（`is_night`）；
- [x] 辐照分位数分层（低/中/高 GHI）。

Wind：
- [x] 风速分位数分层（低/中/高 wind_speed）。

Load/Net-load：
- [x] 季节分层（DJF/MAM/JJA/SON）；
- [x] 工作日/周末分层；
- [x] 高波动切片（按 `|delta|` 或变化率分位数）。

验收：讨论章节能明确方法的适用条件与风险边界，而不是只给总体 RMSE。
状态（2026-03-09）：已完成；资产见 `doc/paper_assets/paper_delivery_20260306/solar_stratified_error_20260309.csv`、`doc/paper_assets/paper_delivery_20260306/wind_stratified_error_20260309.csv`、`doc/paper_assets/paper_delivery_20260306/net_load_stratified_error_20260309.csv`。

---

## 4. 写作与答辩兜底（最小图表集合 + 附录复现链路 + 有效的 threats to validity）

### 4.1 图表最小集合（建议正文只放“必须回答问题”的）

- [x] Fig：系统流程图（Phase 1/1.5/2/3/评估/资产输出）  
- [x] Table：主实验对比表（KAN vs baseline vs persistence）  
- [x] Fig：复杂度—精度 Pareto 图  
- [x] Table：Solar 消融表（含 `ghi_edges`）  
- [x] Table：Wind 消融表（对称项）  
- [x] Fig/Table：`h=288` 反例（分位数/越界率 + clip 对照）  
- [x] Fig：成功公式渲染图（LaTeX）+ 复算指标

状态（2026-03-09）：已完成；最小图表集合已补齐到 `doc/paper_assets/paper_delivery_20260306/`，新增 `system_flow_pipeline.png`、`solar_h288_boundary_20260306.png`、`successful_formula_summary_20260309.csv`、主 symbolic 公式图和 S3 子公式渲染图。

### 4.2 附录（复现/审稿兜底）

- [x] 每张图/每张表对应的 run_id 与生成命令（“run_id→命令→产物路径”三列对照）。
- [x] `doc/thesis_sweeps/<session_id>/manifest.json` 与 `doc/paper_assets/ASSET_INDEX.md` 同步更新。
- [x] threats to validity 最小集合：ex post 气象、长 horizon 外推、稀疏/剪枝路径依赖、Modal vs local schema 漂移、指标口径（delta/abs）。

状态（2026-03-09）：已完成；复现映射在 `doc/paper_assets/PAPER_REPRO_MAP_20260306.md`，会话 manifest 与索引快照已同步进 `doc/paper_assets/paper_reference_paperref_20260306_121725_v2/`。

---

## 5. 可选加分项（不阻塞交付，做不完就写 future work）

- [x] 更多 baselines / 更多 horizons（只在能回答新问题时做）  本轮明确不新增，正式降级为 future work。
- [x] 更强物理约束（例如 solar 非负/夜间硬约束、更严格的有界算子）  正式降级为 future work。
- [x] 架构创新（建议降级为 future work）：残差学习、lag/phys 双分支、group sparsity、边预算（Top‑K gating）、prune/符号搜索的“必须包含物理变量”约束强化  正式降级为 future work。
- [x] direct 公式主线的后续尝试：仅在更换 teacher 或调整 Phase 2 稀疏/结构设计时重启；禁止继续在当前 `paperref_20260306_fullflow__kan_delta_net_load_h6` teacher 上追加同类 symbolic sweep。  正式降级为 future work / 新实验路线。

---

## 6. 每轮实验结束后的固定动作（流水线，防止资产断链）

- [x] 同步：`scripts/sync_from_modal.sh <run_id>`（或 `latest`）  
- [x] 重建（如需）：`scripts/reconstruct_predictions.py`  
- [x] 评估：`scripts/evaluate_runs.py --run runs/<id1> --run runs/<id2> ...`  
- [x] 出图：`scripts/make_thesis_figures.py --run runs/<id>`（关键 run）  
- [x] 物理报告：`scripts/physics_mapping.py --symbolic-run runs/<sym_id>`（关键公式）  
- [x] 更新索引：`scripts/build_asset_index.py`
- [x] 质量门禁：`python3 -m unittest discover -s tests -p 'test_*.py'`

状态（2026-03-09）：本轮已对 direct fast5k 与主结果 run 执行同步、重建、评估、出图、物理报告、索引更新与质量门禁。
