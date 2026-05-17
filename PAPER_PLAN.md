# 论文计划 (Paper Plan)

**题目**: 基于KAN符号回归的风光耦合负荷预测模型可解释性研究
**英文题目**: Autoregressive Shortcut Competition Destroys Symbolic Identifiability — Evidence from KAN Net Load Forecasting
**类型**: 本科毕业设计论文（湘潭大学计算机学院·辅修专业）
**日期**: 2026-03-21
**预计篇幅**: 30,000–40,000字（含图表），约40–55页

---

## 论点-证据矩阵 (Claims-Evidence Matrix)

| 论点 (Claim) | 证据 (Evidence) | 强度 | 章节 |
|---|---|---|---|
| C1: KAN教师模型在净负荷预测中优于MLP和PySR | KAN skill=0.453 > MLP 0.430 (p=0.0005) > PySR 0.20 > persistence 0.0 | 高 | §5.1 |
| C2: 直接符号提取坍缩为仅含负荷的极简公式 | 9种符号配置全部退化为 `0.0007*load - 3.0`，VER(物理量)=0/9 | 高 | §5.2 |
| C3: 可辨识性取决于任务结构和特征竞争，而非变量信息量 | Solar VER=3/3（正例）、Wind非单调VER（边界案例）、**S2阻断 ΔVER=+0.60/+0.80，CI>0** | **非常高** | §5.3–§5.4 |
| C4: S3结构化分解保持物理变量在公式中的存在 | 三个子公式FAR=3/3，组合skill=0.456，优于直接KAN的0.453 | 高 | §5.5 |
| C5: 优势不来自更多参数或更长训练 | 参数匹配的MLP基线，符号公式参数远少于任何NN | 高 | §5.1 |

---

## 章节结构

### 摘要 (Abstract)
- **一句话问题**: 在KAN符号提取中，自回归滞后特征的捷径竞争导致气象物理量被稀疏化剪除，公式退化为仅含负荷的表达式
- **方法**: 提出KAN教师引导的符号提取框架，设计自回归阻断干预实验和结构化任务分解
- **核心结果**: 阻断风/光lag后，VER从0.40→1.00（聚焦任务）和0.00→0.80（直接任务），CI排除0；S3分解使skill=0.456且物理量全部保留
- **意义**: 揭示了符号可辨识性的竞争压力机制，为KAN在能源预测中的可解释应用提供了方法论指导
- **预计长度**: 中文300–500字 + 英文150–250词

### 第1章 绪论 (Introduction) — 约4页

#### 1.1 研究背景与意义
- **开篇钩子**: 新能源渗透率快速提升→净负荷波动加剧→需要准确且可解释的预测模型支撑电力调度
- **差距**: 现有深度学习模型（LSTM、Transformer）精度高但不可解释；传统统计模型可解释但精度不足；KAN提供了"高精度+可解释"的潜力，但在实际时序预测中遇到了物理变量被自回归项替代的结构性障碍
- **关键引用**: [1] Hong & Fan 2016, [2] Kaur et al. 2016, [5] Silva-Rodriguez et al. 2024, [22] Liu et al. 2024 (KAN)

#### 1.2 研究现状与不足
- KAN符号回归在清洁物理问题上成功（Liu et al. ICLR 2025），但**无人研究**实际时序预测中的自回归竞争问题
- MCKAN（Chen et al., 2025）关注精度，未涉及符号提取和可解释性
- PySR等GP方法缺乏KAN的结构化稀疏能力
- **核心空白**: 缺乏对"物理变量为何在符号提取中消失"的机制层面研究

#### 1.3 研究目标与内容
- 目标1: 建立KAN教师→符号提取的完整流程并验证在净负荷预测上的有效性
- 目标2: 提出可辨识性诊断指标（VER/FAR/edge_count），系统量化物理变量存活状况
- 目标3: 通过自回归阻断干预实验，为捷径竞争机制提供干预性证据
- 目标4: 设计S3结构化分解作为建设性解决方案

#### 1.4 论文组织结构
- 简要说明各章安排

---

### 第2章 文献综述 (Literature Review) — 约6页

#### 2.1 负荷与净负荷预测方法
- 传统统计方法（ARIMA、指数平滑）→ 机器学习（RF、SVM）→ 深度学习（LSTM、Transformer）
- 净负荷预测的特殊挑战：风光出力的不确定性叠加
- **引用**: [1]-[7], [6] Ebrahimzadeh 2024

#### 2.2 符号回归与方程发现
- GP-based SR（PySR, Operon）的原理与局限
- 神经符号回归方法（AI Feynman, Transformer-based）
- SR-LLM等前沿方法
- **引用**: [8]-[21]

#### 2.3 Kolmogorov-Arnold Networks (KAN)
- KAN原理：基于Kolmogorov-Arnold定理的可学习激活函数
- KAN的稀疏化与符号提取：从学习到的B样条中恢复解析表达式
- KAN 2.0 (MultKAN)、pykan工具链
- KAN在科学发现中的应用（PRX 2025）
- **引用**: [22]-[25], Liu et al. ICLR 2025, PRX 2025

#### 2.4 MCKAN与风光预测参考
- MCKAN架构（多尺度卷积KAN）及其在风电/光伏预测中的应用
- Pearson相关性特征选择、Min-Max缩放、多步预测设计
- 与本文方法的对应关系
- **引用**: Chen et al. 2025 (MCKAN)

#### 2.5 物理信息学习与可解释性
- PINN/PIKAN在电力系统中的应用
- 可解释性的层次：特征重要性 → 注意力可视化 → 符号公式
- **引用**: [26]-[29]

#### 2.6 本章小结

---

### 第3章 数据与问题定义 (Data & Problem) — 约5页

#### 3.1 ARPA-E PERFORM数据集
- 数据来源：ERCOT区域，5分钟分辨率
- 变量描述：负荷(load)、风电出力(wind)、光伏出力(solar)、净负荷(net_load = load - wind - solar)
- 气象变量：wind_speed_10m, GHI, temp_2m, surface_pressure等
- 时间范围与数据规模
- **表**: 数据集变量描述表

#### 3.2 目标变量设计：delta目标与多步预测
- delta目标：`delta_net_load_h6 = net_load(t+6) - net_load(t)`（30分钟ahead）
- 多步horizon设计：h=6/12/24（30/60/120min）
- 为何使用delta而非绝对值（减小量纲差异，聚焦变化量）

#### 3.3 特征工程
- 特征组体系：meteo_wind, meteo_irradiance, solar_geom, solar_flag, meteo_temp, cyclic, lags
- 工程代理变量：wind_speed_cubed（风功率物理代理）、ghi_temp_corr（温度修正辐照）、HDD/CDD（度日数）
- 多尺度滞后特征：lag_steps=(12,24,48)对应(1h,2h,4h)
- **表**: 特征组定义与物理含义

#### 3.4 数据预处理
- 时间序列切分：训练/验证/测试 = 60/20/20，48步间隔防止泄漏
- Z-score标准化（仅在训练集拟合）
- 缺失值处理及其局限（切分前插值存在轻微信息泄漏，已记录为limitation）

#### 3.5 评估指标
- RMSE, MAE, R², skill score = 1 - RMSE/RMSE_persistence
- 配对t检验（p值）
- **表**: 评估指标定义

---

### 第4章 方法 (Method) — 约8页

#### 4.1 总体框架
- 四幕式研究设计：基线建立 → 问题发现 → 机制测试 → 建设性解决方案
- **图1（Hero Figure）**: 系统流程图——从数据到KAN训练→稀疏化→符号提取→公式评估→阻断测试/S3分解
- 流程不修改KAN训练本身，仅通过控制输入特征（lag blocking）和任务分解（S3）来研究可辨识性

#### 4.2 KAN教师模型训练
- KAN架构：[input_dim, hidden_width, 1]，grid=3-5, k=3
- 训练调度：warmup(200步) → sparsify(800步, λ_L1=1.0, λ_entropy=2.0) → prune(目标80%边剪除) → refine(200步)
- 剪枝策略：9种候选阈值组合，选择满足RMSE退化约束的最稀疏模型
- 与MCKAN的方法论对应：多尺度lag对应多尺度卷积，特征组选择对应Pearson相关性筛选

#### 4.3 Phase 3: 符号提取
- pykan的`suggest_symbolic`/`fix_symbolic`机制
- 符号库：strict（x, x², x³, sin, cos, abs）、medium（+exp）
- R²阈值网格：(0.98, 0.99, 0.995)
- 从KAN边到SymPy表达式的转换流程
- 安全函数处理（safe_exp_clip, eval_clip_quantiles）

#### 4.4 可辨识性诊断指标
- **VER (Variable Entry Rate)**: 变量在剪枝后保留活跃边的种子比例
- **FAR (Formula Appearance Rate)**: 变量在最终SymPy公式中出现的种子比例
- **edge_count(v)**: 连接到变量v的活跃边数（VER的连续补充）
- **TGR (Transfer Gap Ratio)**: RMSE_symbolic / RMSE_teacher（报告一次的诊断指标）
- **ΔVER**: VER(blocked) - VER(unblocked)——核心干预测量
- **公式与数学定义**
- **表**: 指标定义汇总

#### 4.5 自回归阻断协议 (S2 Blocking Protocol)
- 实验设计原理：控制变量法——仅改变lag_series，其他全部固定
- Case 3（聚焦任务）：focused wind teacher，lag_series=["wind"] vs lag_series=[]
- Case 4（直接任务）：direct net_load teacher，lag_series=["load","wind","solar"] vs ["load"]
- 控制条件清单：相同KAN架构、相同grid、相同λ、相同剪枝阈值、相同符号库、相同种子(1-5)
- 预设判决规则：ΔVER的bootstrap 95% CI下界>0
- **图2**: 阻断实验设计示意图（对照组vs实验组）

#### 4.6 S3结构化分解
- 原理：net_load = load - wind - solar → 将净负荷分解为三个物理自然的子任务
- 子任务定义与特征配置：
  - Load子KAN：target=delta_load_h6, features=temp/HDD/CDD + load_lag + cyclic
  - Wind子KAN：target=delta_wind_h6, features=wind_speed/cubed/hub + wind_lag + cyclic
  - Solar子KAN：target=delta_solar_h6, features=GHI/solar_altitude/is_night + solar_lag + cyclic
- 组合规则：固定加法（无可学习权重）
- "保持"的操作定义：VER(目标物理量) ≥ 3/5 seeds
- **表**: S3子任务配置表

---

### 第5章 实验与结果 (Experiments) — 约12页

#### 5.1 精度基线 (Act 1) — 约2页
- **表1**: 主要精度比较表

| 模型 | RMSE | MAE | Skill | 备注 |
|------|------|-----|-------|------|
| KAN教师 | 1413.51 | — | 0.453 | 主模型 |
| 匹配MLP | 1474.38 | — | 0.430 | 参数匹配 |
| PySR | ~2070 | — | ~0.20 | 直接SR |
| 持久性基线 | 2585.66 | — | 0.0 | 基准 |

- 配对t检验：KAN vs MLP p=0.0005
- C5反论证：KAN并非通过更多参数取胜
- **图3**: Pareto前沿图（精度 vs 复杂度）

#### 5.2 公式坍缩 (Act 2) — 约2页
- 9种符号配置（3库×3阈值）在canonical教师上的结果
- **表2**: 符号配置sweep结果

| 库 | R²阈值 | 公式 | VER(物理) | Skill |
|----|--------|------|-----------|-------|
| strict | 0.98 | 0.0007*load - 3.0 | 0/9 | <0 |
| strict | 0.99 | 0.0007*load - 3.0 | 0/9 | <0 |
| ... | ... | ... | ... | ... |

- 所有9种配置均退化为仅含load的线性关系
- 11个额外直接S0运行全部skill<0
- **图4**: 退化公式的LaTeX渲染
- 分析：为何自回归项主导——5分钟分辨率下lag解释>90%方差

#### 5.3 Solar/Wind可辨识性观察 (Act 3, Cases 1-2) — 约3页

##### 5.3.1 Solar正例
- **表3**: Solar消融实验结果

| Horizon | 特征组 | VER(GHI) | FAR(GHI) | Skill |
|---------|--------|----------|----------|-------|
| h72 | lags+meteo | 3/3 | 3/3 | 0.590 |
| h144 | lags+meteo | 3/3 | 3/3 | 0.546 |
| ... | ... | ... | ... | ... |

- GHI在focused teacher中稳定进入公式
- 解释：太阳辐照信号强度足以在lag竞争中存活

##### 5.3.2 Wind边界案例
- **表4**: Wind horizon依赖实验

| Horizon | Skill | wind_speed_edges | VER(wind) |
|---------|-------|------------------|-----------|
| h6 | 0.128 | 11 | 1 |
| h72 | 0.588 | 0 | 0 |
| h144 | 0.354 | 9 | 1 |
| h288 | 0.193 | 0 | 0 |
| h576 | 0.203 | 0 | 0 |

- 非单调可辨识性：中等horizon(h=144)最容易显现风速结构
- **图5**: 风速edge_count随horizon变化曲线
- 解释：短horizon下lag太强，长horizon下信号衰减

#### 5.4 自回归阻断干预 (Act 3, Cases 3-4) — 约3页 ★核心章节★

##### 5.4.1 Case 3: 聚焦风电任务阻断
- **表5a**: 聚焦wind阻断实验（5 seeds paired）

| Seed | Unblocked VER | Unblocked edges | Blocked VER | Blocked edges |
|------|--------------|----------------|-------------|---------------|
| 1 | 0 | 0 | 1 | 19 |
| 2 | 1 | 8 | 1 | 19 |
| 3 | 0 | 0 | 1 | 8 |
| 4 | 0 | 0 | 1 | 15 |
| 5 | 1 | 1 | 1 | 1 |

- ΔVER = +0.60, Bootstrap 95% CI = [0.20, 1.00]，**CI排除0**
- Δedge_count = +10.6, CI = [4.6, 15.8]
- **图6**: ΔVER柱状图 + CI误差棒（核心figure）

##### 5.4.2 Case 4: 直接净负荷阻断
- **表5b**: 直接net_load阻断实验（5 seeds）

| Seed | VER(any_phys) | phys_edges | 进入变量 |
|------|--------------|------------|---------|
| 1 | 1 | 27 | 全部9个物理量 |
| 2 | 0 | 0 | 无 |
| 3 | 1 | 23 | 全部9个物理量 |
| 4 | 1 | 1 | GHI仅1个 |
| 5 | 1 | 21 | 全部9个物理量 |

- ΔVER = +0.80 (vs Act 2 baseline 0/9), CI = [0.40, 1.00]
- 精度代价：RMSE从1414→2025（+43%），揭示精度-可辨识性权衡
- **图7**: 阻断前后VER对比（最具冲击力的figure）
- 关键发现：Seeds 1,3,5中全部9个物理变量同时进入模型

##### 5.4.3 机制确认与总结
- **表6**: 预设判决规则与结果

| 预设规则 | 结果 | 判决 |
|---------|------|------|
| Case 3: ΔVER CI>0 | CI=[0.20,1.00] | SUCCESS |
| Case 3: edge_count一致 | ΔE=+10.6, CI=[4.6,15.8] | SUCCESS |
| Case 4: ≥1变量ΔVER CI>0 | 4/5 seeds有物理量 | SUCCESS |
| Case 4: ≥2变量（强成功） | Seeds 1,3,5含全部9个 | STRONG SUCCESS |

#### 5.5 S3结构化分解 (Act 4) — 约2页

- **表7**: S3子模型性能与可辨识性

| 子任务 | RMSE | FAR(target var) | TGR | 关键物理量 |
|--------|------|----------------|-----|-----------|
| Load | 401.0 | 3/3 (hdd_18c) | 2.569 | 温度/度日数 |
| Wind | 1008.8 | 3/3 (wind_speed) | 1.401 | 风速/立方/轮毂 |
| Solar | 1006.7 | 3/3 (ghi_w_m2) | 2.302 | GHI/太阳高度 |
| **组合** | **1407.4** | — | — | 全部保留 |

- 组合skill=0.456 > 直接KAN的0.453
- 三个子公式的LaTeX渲染展示
- **图8**: 组合预测时序图（actual vs predicted + 子模型贡献分解）
- 关键发现：S3在不损失精度的情况下保持了物理变量

---

### 第6章 讨论 (Discussion) — 约4页

#### 6.1 捷径竞争机制的解释
- 为何lag特征在稀疏化中胜出：5分钟分辨率下的信息冗余
- 不是KAN的缺陷，而是高频时序数据的固有结构属性
- 类比：特征选择中的遮蔽效应（masking effect）

#### 6.2 精度与可辨识性的权衡
- Case 4中阻断lag后RMSE升43%：精确预测与物理解释不可兼得
- S3分解提供了折中方案：精度保持+物理量保留

#### 6.3 对MCKAN的呼应与对比
- **表8**: MCKAN方法论映射表

| MCKAN贡献 | 本文对应元素 |
|-----------|------------|
| 多步预测 | 多horizon delta目标 |
| Pearson特征筛选 | VER/FAR可辨识性诊断 |
| 风/光子任务 | S3结构化分解 |
| 模块消融 | S2自回归阻断消融 |

#### 6.4 局限性
1. 单一数据集（PERFORM ERCOT）：泛化性未验证
2. 种子数量有限（5 seeds for S2，3 for others）
3. 切分前插值存在轻微信息泄漏（已记录，非wind-specific）
4. 未引入物理约束（PIKAN为未来方向）
5. 公式复杂度较高，人类可读性仍有提升空间

---

### 第7章 结论与展望 (Conclusion) — 约2页

#### 7.1 主要贡献
1. 建立了KAN教师引导的符号提取框架，在净负荷预测上验证了KAN的预测优势（skill=0.453, p=0.0005）
2. 发现并通过干预实验确认了自回归捷径竞争机制：阻断lag后物理变量VER从0→0.80（直接任务），置信区间排除0
3. 提出了VER/FAR/edge_count可辨识性诊断指标体系
4. 设计了S3结构化分解方案，在不损失精度(skill=0.456)的前提下保持全部物理变量

#### 7.2 未来工作
1. PIKAN物理约束：将领域知识（如风功率立方律）作为软约束引入训练
2. 更严格的时间因果数据管线：切分后插值
3. 多数据集验证：其他ISO区域、不同时间分辨率
4. 形式化可辨识性理论：建立VER/CPI的理论分析框架
5. 更丰富的符号库：rational函数、分段函数等

---

## 图表计划 (Figure & Table Plan)

| 编号 | 类型 | 描述 | 数据来源 | 优先级 |
|------|------|------|----------|--------|
| 图1 | 系统流程图 | Hero figure: 完整方法框架（数据→KAN→稀疏化→符号→阻断/S3） | 手绘 | **高** |
| 图2 | 示意图 | S2阻断实验设计对照图 | 手绘 | 高 |
| 图3 | 散点图 | Pareto前沿（精度 vs 复杂度） | paper_assets/pareto*.png | 中 |
| 图4 | 公式渲染 | 直接提取的退化公式（load-only）| formula.tex | 中 |
| 图5 | 折线图 | wind edge_count随horizon变化（非单调） | wind_ablation data | 高 |
| 图6 | 柱状图+CI | **ΔVER柱状图 — Case 3 聚焦风电** | M1_S2_BLOCKING_RESULTS | **高** |
| 图7 | 对比柱状图 | **VER阻断前后对比 — Case 4 直接任务（核心图）** | M1_S2_BLOCKING_RESULTS | **最高** |
| 图8 | 时序图 | S3组合预测 vs 实际值 + 子模型贡献 | predictions_test.parquet | 高 |
| 图9 | 公式渲染 | S3三个子公式的LaTeX渲染 | formula.tex files | 中 |
| 表1 | 比较表 | 主要精度对比（KAN/MLP/PySR/persistence） | comparison_table.csv | 高 |
| 表2 | Sweep表 | 9种符号配置的坍缩结果 | formula_metrics data | 高 |
| 表3 | 消融表 | Solar可辨识性（horizon × 特征组） | solar_ablation data | 高 |
| 表4 | 消融表 | Wind horizon依赖（VER × horizon） | wind experiment data | 高 |
| 表5 | **核心表** | **S2阻断结果（5 seeds × blocked/unblocked）** | M1 results | **最高** |
| 表6 | 判决表 | 预设规则 vs 实际结果 | M1 results | 高 |
| 表7 | S3表 | 子模型性能 + FAR + TGR | M0 results | 高 |
| 表8 | 映射表 | MCKAN方法论对应关系 | manual | 中 |

---

## 引用计划 (Citation Plan)

### 第1章 绪论
- [1]-[2] 负荷/净负荷预测意义
- [22] KAN原始论文（Liu et al. 2024）
- MCKAN (Chen et al. 2025) — 核心参考

### 第2章 文献综述
- [1]-[7] 负荷预测综述与方法
- [8]-[21] 符号回归方法
- [22]-[25] KAN理论与应用
- [26]-[29] 物理信息学习
- KAN ICLR 2025, PRX 2025
- arXiv 2504.03913 (KAN-SR for energy)
- MCKAN (Chen et al. 2025)

### 第3章 数据
- ARPA-E PERFORM dataset documentation
- [2] net_load定义来源

### 第4章 方法
- [22] KAN原理
- [11] PySR方法（作为baseline参考）
- MCKAN (特征选择、多步预测对应)

### 第5章 实验
- Bootstrap方法引用
- 持久性基线定义

### 第6章 讨论
- 特征选择masking effect相关文献
- MCKAN对照

**引用规则**: 所有引用均使用doc/文献仓库.md中已验证的DOI/arXiv ID，不从记忆中生成BibTeX。

---

## 附录计划

- **附录A**: 多Horizon可辨识性全景图（wind/solar各horizon的完整VER/FAR数据）
- **附录B**: S0安全函数实现细节（safe_exp_clip, quantile clipping）
- **附录C**: 季节/日夜分层误差分析表
- **附录D**: 所有符号公式的完整LaTeX渲染
- **附录E**: 太阳h=288边界失败案例详情
- **附录F**: 实验可复现性映射表（run_id → 命令 → 产物）

---

## 下一步

- [ ] `/paper-figure` 生成所有图表（特别是图6、图7核心ΔVER图）
- [ ] `/paper-write` 按章逐节撰写LaTeX
- [ ] `/paper-compile` 编译生成PDF
- [ ] 检查是否满足学校模板格式要求（字号、页眉页脚、目录等）
