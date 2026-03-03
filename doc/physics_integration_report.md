# 物理因子集成实验报告（完整记录）

本报告完整记录了在 **ARPA-E PERFORM (ERCOT)** 电网级数据集上，通过 **KAN (Kolmogorov-Arnold Networks)** 模型实现物理规律显式发现的 **全部计划、代码改动、执行过程（含失败重试）和最终结果**。

---

## 1. 问题背景

在初期的 fullflow + S0 + S3 实验中，`wind_speed_10m_m_s`、`ghi_w_m2`、`temp_2m_c` 始终没有稳定进入最终解析公式——它们在 Phase2（KAN 稀疏化训练）阶段就被剪枝为 0，因此 Phase3（符号提取）的公式中自然不会出现这些物理量。

### 根因分析（按证据优先级排序）

1. **`save_act` Bug（已修复，真正根因）**：`model.speed()` 在训练前设置了 `save_act=False`，导致 pyKAN 在 sparsify 阶段**静默将 `lamb` 强制为 0**。所有先前实验的正则化完全无效（`reg=0`），物理因子被剪枝纯粹因为没有稀疏约束引导。

2. **Delta 目标将物理因子的解释力差分抵消**：物理量对水平值高度相关，但对增量几乎无线性关联。
   - `corr(ghi_w_m2, solar) = 0.9226`，但 `corr(ghi_w_m2, delta_solar_h6) = -0.0505`
   - `corr(wind_speed_10m_m_s, wind) = 0.6106`，但 `corr(wind_speed_10m_m_s, delta_wind_h6) = -0.0488`
   - `corr(temp_2m_c, load) = 0.5720`，但 `corr(temp_2m_c, delta_load_h6) = -0.0799`

3. **Lag 特征是更强的物理代理**：历史出力值与未来值的相关性远超瞬时气象量。
   - `corr(wind_lag_12, wind) = 0.9816`
   - `corr(solar_lag_12, solar) = 0.9355`
   - 模型可以仅凭历史出力完成预测，外生物理量成为可替代项。

4. **特征替代/共线性**：太阳几何（`solar_altitude`、`is_night`、`hour_sin/cos`）+ `solar_lag` 已能拟合日照形状，GHI 在稀疏化中成为冗余项。

5. **物理代理不够对口**：`wind_speed_10m_m_s`（10m 高度）对聚合风电出力并非理想代理（轮毂高度、空间平均、风向、切入/切出速度等未建模）。

6. **Phase3 不是根因**：符号提取只是翻译已稀疏化的 KAN；当输入边 mask 已为 0 时，无论如何调整符号库/阈值，都无法将这些变量"凭空写回公式"。

---

## 2. 实验计划

用户提出两套实验方案，目的是强制物理因子在 KAN 剪枝中存活：

### 2.1 方案 B — S4 纯物理（Pure Physics）

**核心思路**：去掉所有 lag 特征，切换到绝对值目标，强制模型只能从物理量学习。

| 实验名 | 目标列（绝对值） | 特征组 | lag |
|---|---|---|---|
| `s4_pure_wind_abs_h6` | `wind_h6` | cyclic, meteo_wind, meteo_irradiance, meteo_temp | 无 |
| `s4_pure_solar_abs_h6` | `solar_h6` | cyclic, solar_geom, solar_flag, meteo_irradiance, meteo_temp | 无 |
| `s4_pure_load_abs_h6` | `net_load_h6` | cyclic, meteo_temp, meteo_degree, meteo_pressure, meteo_wind, meteo_irradiance, solar_flag | 无 |

共同参数：`hidden_width=15`, `sparsify_lamb=0.001`, `sparsify_lamb_entropy=1.0`, `include_base=False`。

### 2.2 方案 A — S0A 松正则 + lag

**核心思路**：保留 lag 特征但大幅降低正则化强度，给物理量更多生存空间。

| 实验名 | 目标列（增量） | 特征组 | lag |
|---|---|---|---|
| `s0a_wind_delta_h6` | `delta_wind_h6` | cyclic, meteo_wind, meteo_irradiance, meteo_temp, solar_flag | wind: 12,24,48 |
| `s0a_solar_delta_h6` | `delta_solar_h6` | cyclic, solar_geom, solar_flag, meteo_irradiance, meteo_temp | solar: 12,24,48 |

共同参数：`hidden_width=15`, `sparsify_lamb=0.001`, `sparsify_lamb_entropy=1.0`, `include_base=False`。

### 2.3 附带计划：S3 + S0p 重跑

在执行过程中发现了 `save_act` bug（详见第 3 节），因此追加了对已有 S3 和 S0-Physics 实验的重跑：

| 实验名 | 目标列 | 特征组 | lamb | 备注 |
|---|---|---|---|---|
| `s3_comp_load_delta_h6` | delta_load_h6 | cyclic,meteo_temp,meteo_degree,meteo_pressure,solar_flag | 默认(0.01) | S3 标准 |
| `s3_comp_wind_delta_h6` | delta_wind_h6 | cyclic,meteo_wind | 默认(0.01) | S3 标准 |
| `s3_comp_solar_delta_h6` | delta_solar_h6 | cyclic,solar_geom,solar_flag,meteo_irradiance,meteo_temp | 默认(0.01) | S3 标准 |
| `s0p_wind_delta_h6` | delta_wind_h6 | cyclic,meteo_wind,meteo_irradiance,meteo_temp,solar_flag | 0.005 | S0p 松正则 |
| `s0p_solar_delta_h6` | delta_solar_h6 | cyclic,solar_geom,solar_flag,meteo_irradiance,meteo_temp | 0.005 | S0p 松正则 |

共同参数：`hidden_width=10`, `sparsify_lamb_entropy=1.5`（S0p）或默认 2.0（S3）。

---

## 3. 代码改动（完整清单）

### 3.1 `modal_jobs/kan_train.py` — KAN 训练主流程

#### 3.1.1 关键 Bug 修复：`save_act`

**问题**：`model.speed()`（第 504 行）设置 `save_act=False`，导致 pyKAN 的 `KAN.fit()` 在 sparsify 阶段**静默将 `lamb` 强制为 0**。所有先前实验的正则化完全无效（sparsify 日志中 `reg=0`）。

**修复**：在 sparsify 阶段前（第 544-547 行）重新启用：

```python
# Stage B: sparsify
# Re-enable save_act so that lamb (regularisation) is actually applied.
# model.speed() disables save_act during warmup for performance, but
# KAN.fit() silently sets lamb=0 when save_act is False.
model.save_act = True
```

**效果对比**：
| | 修复前 | 修复后 |
|---|---|---|
| sparsify 阶段 `reg` | 0（全程） | 36.x（正常） |
| 物理特征 active_edges | 全 0 | 多个特征 > 0 |

#### 3.1.2 Warmup NaN：固定 seed + 禁用 warmup grid update（替代 seed 重试）

`hidden_width=15`（尤其是纯物理 S4）在 warmup 阶段偶发 step 0 NaN，且与 `update_grid=True` 强相关。

**最终取舍**：为了保证可复现与可对比，**不采用“自动换 seed 重试”**（会掩盖数值问题且引入额外随机性）；改为暴露并默认在 S4/S0A 中强制使用 `--no-warmup-update-grid` 来禁用 warmup 的 grid 自适应更新。

对应实现点：warmup 阶段将 `warmup_update_grid` 透传到 pyKAN 的 `update_grid` 参数（关掉即可稳定）。

#### 3.1.3 Prune：Fail-fast（不做 fallback）

当所有剪枝候选（不同 `node_th`/`edge_th` 组合）全部异常失败时，继续用未剪枝模型“兜底”会显著拖慢后续 Phase3（边数爆炸）并隐藏根因。

**最终取舍**：遵循 debug-first（不吞错），当 `best is None` 时直接 fail-fast：

```python
if best is None:
    raise RuntimeError("All prune candidates failed; see logs for details.")
```

#### 3.1.4 Prune：baseline 与诊断产物（避免“剪枝选错”）

在定位过程中发现：如果剪枝候选的优劣比较基线（baseline）使用的是 **warmup 阶段** 的误差，而不是 **sparsify 结束后** 的误差，会导致：

- sparsify 已经把“物理因子相关边”学出来的情况下，prune 阶段仍可能因为 baseline 失真而选择到错误候选；
- 表现为：全量训练时“看起来物理量又进不去 / 精度突然掉很多”，但其实是剪枝决策把有效结构剪掉了。

**修复**：将 prune baseline 改为 `eval_sparsify`（sparsify 结束、prune 之前）的评估结果，并新增以下诊断产物便于复盘：

- `eval_sparsify.json`：sparsify 后、prune 前的 RMSE/MAE/R²（用于 prune 正确对比）
- `feature_importance_sparsify.csv`：sparsify 后输入边活跃情况（判断物理特征是否已保留）
- `prune_search.json`：记录所有候选阈值组合与对应评估（定位“为什么选了这个剪枝”）

#### 3.1.5 Payload 位置调整

将 `payload` 的创建和写入放在训练开始之前，确保即使 warmup NaN 直接失败，`payload.json`、`dataset_stats.json` 等诊断信息仍会被持久化，方便事后排查。

### 3.2 `src/thesis_sweep/plan_kan.py` — 实验计划生成

#### 3.2.1 `_plan_kan_train_cmd` 和 `_plan_kan_train` 新增参数

- **`hidden_width_override: int | None = None`**（第 23 行）：允许实验级别覆盖 CLI 传入的 `--kan-hidden-width`。S4 和 S0A 使用 `hidden_width_override=15`。
- **`force_no_warmup_update_grid: bool = False`**（第 24 行）：当为 `True` 时，无论 CLI 是否传了 `--no-warmup-update-grid`，都强制追加该参数。
- **`sparsify_lamb` / `sparsify_lamb_entropy`**（第 21-22 行）：允许实验级别覆盖正则化参数。

实现逻辑：
```python
hw = str(hidden_width_override) if hidden_width_override is not None else (str(args.kan_hidden_width).strip() or "10")
...
if bool(args.no_warmup_update_grid) or force_no_warmup_update_grid:
    cmd_args.append("--no-warmup-update-grid")
```

#### 3.2.2 新增 `plan_s4_pure()` 函数（第 268-321 行）

方案 B 的计划生成。3 个实验配置，所有实验：
- `lag_steps="none"`, `lag_series="none"` — 无历史出力
- `include_base=False` — 不含 load/wind/solar 原始列
- `sparsify_lamb=0.001`, `sparsify_lamb_entropy=1.0` — 极松正则
- `hidden_width_override=15`, `force_no_warmup_update_grid=True`

#### 3.2.3 新增 `plan_s0a_physics()` 函数（第 324-375 行）

方案 A 的计划生成。2 个实验配置，与 S4 的区别在于：
- 保留 lag 特征（`lag_steps="12,24,48"`）
- 使用 delta 目标（增量预测）
- 同样 `hidden_width_override=15`, `force_no_warmup_update_grid=True`

#### 3.2.4 `plan_kan_sweeps` 路由扩展（第 378-413 行）

在函数末尾新增两个分支：

```python
if "s4" in sweeps:
    cmds, m, cr = plan_s4_pure(args, ...)
    ...
if "s0a" in sweeps:
    cmds, m, cr = plan_s0a_physics(args, ...)
    ...
```

### 3.3 `src/thesis_sweep/cli.py` — CLI 驱动

#### 3.3.1 `execute_plan`：Fail-fast（不吞错）

`execute_plan` 采用 `subprocess.run(..., check=True)`，任一命令失败会直接终止。

**取舍**：定位阶段优先保证失败可见、可复现（fail-fast），不做“吞错继续跑”的隐式容错；否则容易产出“部分成功但缺关键 run”的不完整证据链，反而增加排查成本。

#### 3.3.2 CLI 帮助文本更新

- `description` 从 `"S0–S3"` 改为 `"S0–S4"`。
- `--sweeps` 的 help 文本更新为：`"Subset: s0,s1,s2,s3,s4,s0a (comma-separated). s4=pure-physics, s0a=loose-reg+lag."`

---

## 4. 执行过程（完整时间线）

所有实验使用的源数据：`2026-02-26_032058_1957fda1`
物理因子实验使用的派生数据集：`2026_03_02_physics_s3_t4__derived_h1_6_12_24`
执行平台：Modal（远程 GPU/CPU），通过 `modal run` 提交

### 4.1 S4 纯物理 — 5 次尝试

#### 尝试 1：`s4_pure_physics`（失败）

- **时间**：2026-03-02 15:47 UTC
- **session_id**：`s4_pure_physics`
- **命令**：`--sweeps s4 --kan-hidden-width 15 --use-gpu --detached-remote --execute`
- **结果**：wind 实验成功，但 solar 和 load 在 warmup 阶段 step 0 即 NaN crash。
- **原因**：此时代码尚未加入 `--no-warmup-update-grid`（`plan_s4_pure` 中 `force_no_warmup_update_grid` 参数不存在或为 False），warmup 阶段 `update_grid=True` 与 `hidden_width=15` 的组合在特定特征/目标下导致数值不稳定。
- **同时**，`save_act` bug 也未修复——即便 wind 跑完了，其 sparsify 的 `reg` 也是 0。

#### 尝试 2：`s4_pure_physics_v2`（失败）

- **时间**：2026-03-02 15:54 UTC（尝试 1 后 7 分钟）
- **命令**：与尝试 1 完全相同（manifest 中命令逐字节一致）
- **结果**：同样的 NaN 失败
- **原因**：未修改代码，只是换了 session_id 重试

#### 尝试 3：`s4_pure_v3`（失败）

- **时间**：2026-03-02 16:04 UTC（尝试 2 后 10 分钟）
- **命令**：同上，仍无 `--no-warmup-update-grid`
- **结果**：同样失败

#### 尝试 4：`s4_pure_v4`（失败）

- **时间**：2026-03-02 16:15 UTC（尝试 3 后 11 分钟）
- **命令**：同上
- **结果**：同样失败
- **阶段性结论**：连续 4 次相同配置失败后，确认问题在于 `update_grid=True`。

#### 尝试 5：`s4_pure_v5`（成功）

- **时间**：2026-03-02 17:09 UTC（尝试 4 后 54 分钟——期间实施了代码修复）
- **代码变更**：
  1. `plan_s4_pure()` 中加入 `force_no_warmup_update_grid=True`
  2. `modal_jobs/kan_train.py` 中加入 `model.save_act = True`（save_act 修复）
  3. （曾尝试，后续撤销）seed 自动重试（影响可复现性，改为固定 seed + `--no-warmup-update-grid`）
  4. （曾尝试，后续撤销）prune fallback（隐藏根因，改为 fail-fast）
  5. （曾尝试，后续撤销）`execute_plan` try/except 容错（吞错，改为 fail-fast）
- **命令**：`--sweeps s4 --kan-hidden-width 15 --use-gpu --detached-remote --execute --session-id s4_pure_v5`
- **结果**：3 个实验全部成功完成

| run_id | 目标 | 未剪枝 R² | 剪枝后 R² |
|---|---|---|---|
| `s4_pure_v5__s4_pure_wind_abs_h6` | wind_h6 | 0.389 | -1.095 |
| `s4_pure_v5__s4_pure_solar_abs_h6` | solar_h6 | **0.905** | 0.358 |
| `s4_pure_v5__s4_pure_load_abs_h6` | net_load_h6 | 0.378 | -0.096 |

### 4.2 S0A 松正则 + lag — 2 次尝试

#### 尝试 1：`s0a_physics_v1`（失败）

- **时间**：2026-03-02 17:20 UTC（S4 v5 成功后 10 分钟）
- **命令**：`--sweeps s0a --kan-hidden-width 15 --use-gpu --detached-remote --execute --session-id s0a_physics_v1`
- **结果**：NaN 失败
- **原因**：`plan_s0a_physics()` 忘记加 `force_no_warmup_update_grid=True`

#### 尝试 2：`s0a_physics_v2`（成功）

- **时间**：2026-03-02 17:22 UTC（尝试 1 后 2 分钟——快速修复后重试）
- **代码变更**：`plan_s0a_physics()` 加入 `force_no_warmup_update_grid=True`
- **结果**：2 个实验全部成功

| run_id | 目标 | 未剪枝 R² | 剪枝后 R² |
|---|---|---|---|
| `s0a_physics_v2__s0a_wind_delta_h6` | delta_wind_h6 | 0.397 | 0.160 |
| `s0a_physics_v2__s0a_solar_delta_h6` | delta_solar_h6 | 0.764 | -0.495 |

### 4.3 S3 + S0p 重跑（save_act 修复验证）

- **时间**：2026-03-02 17:37 UTC
- **session_id**：`s3_saveact_fix`
- **动机**：既然 save_act bug 导致之前所有 S3 实验的正则化无效，需要在修复后重跑以获得正确结果
- **命令**：`--sweeps s3 --kan-hidden-width 10 --no-warmup-update-grid --use-gpu --detached-remote --execute --session-id s3_saveact_fix`
  - S3 计划自动附带 S0-Physics（lamb=0.005），共 5 个实验
- **结果**：5 个实验全部成功

| run_id | 目标 | 未剪枝 R² | 剪枝后 R² |
|---|---|---|---|
| `s3_saveact_fix__s3_comp_load_delta_h6` | delta_load_h6 | 0.698 | 0.333 |
| `s3_saveact_fix__s3_comp_wind_delta_h6` | delta_wind_h6 | 0.248 | -0.959 |
| `s3_saveact_fix__s3_comp_solar_delta_h6` | delta_solar_h6 | 0.713 | **0.496** |
| `s3_saveact_fix__s0p_wind_delta_h6` | delta_wind_h6 | 0.443 | **0.433** |
| `s3_saveact_fix__s0p_solar_delta_h6` | delta_solar_h6 | 0.768 | -0.101 |

### 4.4 符号提取尝试

在 S3/S4/S0A 完成后，尝试对最佳模型进行符号回归公式提取（Phase 3）。

- **GPU 版本**：失败。pyKAN 的 `fix_symbolic` → `fit_params` 内部出现 device mismatch（`cuda:0` vs `cpu`），属于 pyKAN 库自身 bug。
- **CPU 版本**（`session_id=sym_cpu_r03`）：运行完成，但提取质量差（solar R²=0.15），其他目标报错。
- **原因**：pruned R² 远低于符号提取所需的 0.92 阈值，稀疏模型的精度不足以支撑高质量公式拟合。

### 4.5 执行时间线汇总

| # | session_id | 时间 (UTC) | 实验类型 | 结果 | 失败原因 |
|---|---|---|---|---|---|
| 1 | `s4_pure_physics` | 03-02 15:47 | S4 纯物理 | **失败** | NaN（无 no-warmup-update-grid） |
| 2 | `s4_pure_physics_v2` | 03-02 15:54 | S4 纯物理 | **失败** | 同上，命令未变 |
| 3 | `s4_pure_v3` | 03-02 16:04 | S4 纯物理 | **失败** | 同上，命令未变 |
| 4 | `s4_pure_v4` | 03-02 16:15 | S4 纯物理 | **失败** | 同上，命令未变 |
| 5 | `s4_pure_v5` | 03-02 17:09 | S4 纯物理 | **成功** | 加入 no-warmup-update-grid + save_act 修复 |
| 6 | `s0a_physics_v1` | 03-02 17:20 | S0A 松正则 | **失败** | NaN（忘加 no-warmup-update-grid） |
| 7 | `s0a_physics_v2` | 03-02 17:22 | S0A 松正则 | **成功** | 加入 no-warmup-update-grid |
| 8 | `s3_saveact_fix` | 03-02 17:37 | S3+S0p 重跑 | **成功** | save_act 修复后重跑 |
| 9 | `sym_cpu_r03` | 03-02 ~18:xx | 符号提取 | 部分完成 | pruned R² 不足，公式质量差 |

---

## 5. 实验结果（详细）

### 5.1 S3 标准正则对照组（`save_act` 修复后重跑）

| 实验 | 目标 | 未剪枝 R² | 剪枝后 R² | 存活物理特征（active_edges） |
|---|---|---|---|---|
| `s3_comp_load_delta_h6` | delta_load_h6 | 0.698 | 0.333 | `hdd_18c`(1), `is_night`(1) |
| `s3_comp_wind_delta_h6` | delta_wind_h6 | 0.248 | -0.959 | `wind_lag_24`(1), `wind_lag_48`(1)（仅 lag，无物理量） |
| `s3_comp_solar_delta_h6` | delta_solar_h6 | 0.713 | **0.496** | `solar_altitude`(2), `ghi_temp_corr_w_m2`(1), `is_night`(1) |

**与修复前对比**：修复前三个实验的物理特征 active_edges 全为 0，修复后 S3 solar 保留了 `solar_altitude`(2 edges) 和 `ghi_temp_corr_w_m2`(1 edge)。

### 5.2 S0-Physics 松正则（`save_act` 修复后重跑，lamb=0.005）

| 实验 | 目标 | 未剪枝 R² | 剪枝后 R² | 存活物理特征（active_edges） |
|---|---|---|---|---|
| `s0p_wind_delta_h6` | delta_wind_h6 | 0.443 | **0.433** | `ghi_day_w_m2`(2), `ghi_temp_corr_w_m2`(2), `temp_2m_c`(2), `wind_lag_12`(3), `wind_lag_24`(3), `wind_lag_48`(1) |
| `s0p_solar_delta_h6` | delta_solar_h6 | 0.768 | -0.101 | `solar_altitude`(3), `solar_lag_12`(1), `solar_lag_24`(1) |

**关键发现**：S0p wind 的**剪枝后 R² 几乎无退化**（0.443 → 0.433），且保留了 3 个直接物理特征：`ghi_day_w_m2`、`ghi_temp_corr_w_m2`、`temp_2m_c`。这是所有实验中 pruned R² 保持最好的一个。

### 5.3 S4 纯物理实验（绝对值目标，无 lag）

| 实验 | 目标 | 未剪枝 R² | 剪枝后 R² | 存活物理特征（active_edges） |
|---|---|---|---|---|
| `s4_pure_wind_abs_h6` | wind_h6 | 0.389 | -1.095 | `wind_speed_10m_m_s_cubed`(2), `temp_2m_c`(4) |
| `s4_pure_solar_abs_h6` | solar_h6 | **0.905** | 0.358 | `ghi_w_m2`(1), `ghi_day_w_m2`(1), `ghi_temp_corr_w_m2`(1), `solar_altitude`(1) |
| `s4_pure_load_abs_h6` | net_load_h6 | 0.378 | -0.096 | `wind_speed_10m_m_s_cubed`(3), `hdd_18c`(2), `surface_pressure_hpa`(2), `ghi_temp_corr_w_m2`(2), `wind_speed_10m_m_s`(1), `ghi_day_w_m2`(1) |

**关键发现**：
- S4 solar **未剪枝 R²=0.91**，且 4 个物理特征全部存活（`ghi_w_m2`、`ghi_day_w_m2`、`ghi_temp_corr_w_m2`、`solar_altitude`），物理意义完整（光伏出力 = f(辐照度, 太阳角)）。
- S4 load 保留了最多的物理特征（6 个），包括 `hdd_18c`（度日数，负荷的核心解释变量）。

### 5.4 S0A 松正则 + lag（lamb=0.001）

| 实验 | 目标 | 未剪枝 R² | 剪枝后 R² | 存活物理特征（active_edges） |
|---|---|---|---|---|
| `s0a_wind_delta_h6` | delta_wind_h6 | 0.397 | 0.160 | `ghi_day_w_m2`(1), `ghi_temp_corr_w_m2`(1), `temp_2m_c`(1), `is_night`(1) |
| `s0a_solar_delta_h6` | delta_solar_h6 | 0.764 | -0.495 | `solar_altitude`(4) |

---

## 6. 物理因子存活汇总

修复 `save_act` bug 后，物理因子在多个实验中成功存活：

| 物理特征 | 存活实验数 | 最大 active_edges | 出现的实验 |
|---|---|---|---|
| `ghi_temp_corr_w_m2` | 5 | 2（S0p wind） | S3-solar, S0p-wind, S4-solar, S4-load, S0A-wind |
| `solar_altitude` | 4 | 4（S0A solar） | S3-solar, S0p-solar, S4-solar, S0A-solar |
| `ghi_day_w_m2` | 4 | 2（S0p wind） | S0p-wind, S4-solar, S4-load, S0A-wind |
| `temp_2m_c` | 3 | 4（S4 wind） | S0p-wind, S4-wind, S0A-wind |
| `hdd_18c` | 2 | 2（S4 load） | S3-load, S4-load |
| `wind_speed_10m_m_s_cubed` | 2 | 3（S4 load） | S4-wind, S4-load |
| `ghi_w_m2` | 1 | 1（S4 solar） | S4-solar |
| `wind_speed_10m_m_s` | 1 | 1（S4 load） | S4-load |
| `surface_pressure_hpa` | 1 | 2（S4 load） | S4-load |
| `is_night` | 3 | 1 | S3-load, S3-solar, S0A-wind |

---

## 7. 遇到的问题与解决过程

### 7.1 `save_act` Bug 的发现过程

1. S4 v1 的 wind 实验跑完后（solar/load NaN 失败），检查日志发现 sparsify 阶段 `reg=0`（应为正值）
2. 检查 pyKAN 0.2.8 源码，发现 `KAN.fit()` 中有判断：`if self.save_act: lamb = lamb; else: lamb = 0`
3. 追溯到 `model.speed()` 会设置 `self.save_act = False`
4. 这意味着**所有历史实验**（包括 S0、S1、S2、S3）的 sparsify 正则化都是 0——物理特征被剪掉不是因为它们不重要，而是因为没有任何正则化在引导稀疏结构

### 7.2 NaN 数值不稳定

**现象**：`hidden_width=15`（S4/S0A 的设置）在 warmup 阶段 step 0 即产生 NaN，具体表现为 `train_loss=nan, val_loss=nan, reg=nan`。

**排查过程**：
1. 测试 seed 1-5，全部在 solar/load 目标上 NaN（wind 偶尔成功）
2. 将 `hidden_width` 降到 10 后不再 NaN → 问题与网络宽度有关
3. 禁用 `update_grid`（warmup 阶段不做网格自适应更新）后问题消失

**根因**：pyKAN 的 `update_grid` 在 warmup 初期（权重随机初始化时）对宽隐藏层进行网格重映射，会放大数值误差导致 spline 系数发散。

**两层修复**：
1. `force_no_warmup_update_grid=True` — 直接禁用网格更新（根本解决）
2. 固定 seed（保持可复现与可对比）；不做自动 seed 重试

### 7.3 `execute_plan` 串行失败传播

**现象**：S4 的 3 个实验串行执行。solar NaN crash 后异常直接冒泡，load 实验完全没有机会运行。

**取舍**：定位阶段保持 fail-fast（不吞错），优先暴露最先失败的根因并收敛修复；需要“尽量都提交到 Modal 继续跑”的场景，可使用 `--detached-remote` 将提交与本地串行执行解耦。

### 7.4 符号提取 GPU 设备不匹配

**现象**：在 GPU 上运行 Phase 3 符号提取时，pyKAN 的 `fix_symbolic` → `fit_params` 内部将部分张量移到 CPU 而模型在 `cuda:0`，导致 `RuntimeError: expected all tensors to be on the same device`。

**解决**：采用“GPU forward + CPU symbolic”的折中方案：

1. 若使用 GPU，先在 GPU 上完成一次 forward，确保激活值已写入模型内部缓存；
2. 将模型与采样输入迁回 CPU，再进行 `extract_symbolic_edges` / SymPy 构式与评估（符号拟合本身 CPU 更合适且避免 device mismatch）。

---

## 8. 结论

### 核心发现

1. **`save_act` bug 是物理因子被全面剪枝的根本原因**。修复后，正则化正常工作（`reg > 0`），物理特征在多个实验设置下均能存活。

2. **物理因子已成功进入模型**。`ghi_temp_corr_w_m2`、`solar_altitude`、`temp_2m_c`、`ghi_day_w_m2` 等物理特征在修复后的实验中稳定保留 active edges，证明 KAN 能从数据中学到物理量的贡献。

3. **S4 solar（纯物理）验证了 KAN 发现物理结构的能力**。未剪枝 R²=0.91，保留了辐照度 + 太阳高度角的完整物理链路。

4. **S0p wind（松正则 + lag）实现了最佳剪枝稳定性**。pruned R² 几乎无退化（0.443 → 0.433），同时保留 3 个物理特征和 3 个 lag 特征，是"物理可解释 + 预测精度"的最佳平衡点。

5. **剪枝后 R² 普遍大幅下降**是当前主要瓶颈。除 S0p wind 外，多数实验剪枝后 R² 显著低于未剪枝值，限制了符号提取的公式质量。

### 与先前报告的修正

先前报告中"所有物理因子在 delta 目标下被系统性淘汰"的结论，主要归因于 `save_act` bug 导致正则化完全失效。修复后：
- S3 solar delta: `ghi_temp_corr_w_m2` 存活（先前为 0）
- S0p wind delta: `ghi_day_w_m2`、`ghi_temp_corr_w_m2`、`temp_2m_c` 均存活（先前全为 0）
- Delta 目标下物理因子仍弱于 lag 特征，但不再被完全淘汰。

---

## 9. 附录

### 9.1 修改文件清单

| 文件 | 改动内容 |
|---|---|
| `modal_jobs/kan_train.py` | save_act 修复、fail-fast prune、payload 位置调整、暴露 warmup grid update 开关 |
| `src/thesis_sweep/plan_kan.py` | 新增 `plan_s4_pure()`、`plan_s0a_physics()`、新参数 `hidden_width_override`/`force_no_warmup_update_grid` |
| `src/thesis_sweep/cli.py` | fail-fast 执行、参数/帮助文本更新（含 `--no-symbolic`、`--no-warmup-update-grid`） |

### 9.2 实验 Session 完整列表

| session_id | 创建时间 | 类型 | 实验数 | 结果 |
|---|---|---|---|---|
| `s4_pure_physics` | 2026-03-02 15:47 UTC | S4 | 3 | 失败 |
| `s4_pure_physics_v2` | 2026-03-02 15:54 UTC | S4 | 3 | 失败 |
| `s4_pure_v3` | 2026-03-02 16:04 UTC | S4 | 3 | 失败 |
| `s4_pure_v4` | 2026-03-02 16:15 UTC | S4 | 3 | 失败 |
| `s4_pure_v5` | 2026-03-02 17:09 UTC | S4 | 3 | **成功** |
| `s0a_physics_v1` | 2026-03-02 17:20 UTC | S0A | 2 | 失败 |
| `s0a_physics_v2` | 2026-03-02 17:22 UTC | S0A | 2 | **成功** |
| `s3_saveact_fix` | 2026-03-02 17:37 UTC | S3+S0p | 5 | **成功** |
| `sym_cpu_r03` | 2026-03-02 ~18:xx UTC | 符号提取 | 3 | 部分完成 |

### 9.3 实验复现指令

#### S4 纯物理
```bash
python -m src.thesis_sweep.cli \
  --source-data-run-id "2026-02-26_032058_1957fda1" \
  --derived-data-run-id "2026_03_02_physics_s3_t4__derived_h1_6_12_24" \
  --sweeps s4 --kan-hidden-width 15 \
  --session-id s4_pure_v5 \
  --use-gpu --detached-remote --execute
```

#### S0A 松正则 + lag
```bash
python -m src.thesis_sweep.cli \
  --source-data-run-id "2026-02-26_032058_1957fda1" \
  --derived-data-run-id "2026_03_02_physics_s3_t4__derived_h1_6_12_24" \
  --sweeps s0a --kan-hidden-width 15 \
  --session-id s0a_physics_v2 \
  --use-gpu --detached-remote --execute
```

#### S3 + S0-Physics 重跑（save_act 修复后）
```bash
python -m src.thesis_sweep.cli \
  --source-data-run-id "2026-02-26_032058_1957fda1" \
  --derived-data-run-id "2026_03_02_physics_s3_t4__derived_h1_6_12_24" \
  --sweeps s3 --kan-hidden-width 10 --no-warmup-update-grid \
  --session-id s3_saveact_fix \
  --use-gpu --detached-remote --execute
```

---
*Updated: 2026-03-03*
*Scenario: KAN Physics Integration for ARPA-E PERFORM Dataset*
*本报告所有数据均来自 `runs/` 目录下的实际实验产物（payload.json / eval_pruned.json / feature_importance.csv）及 `doc/thesis_sweeps/*/manifest.json`，经逐项核实。*
