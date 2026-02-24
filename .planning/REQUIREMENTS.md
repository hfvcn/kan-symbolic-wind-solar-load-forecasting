# Requirements: KAN-SR 风光负荷预测

**Defined:** 2026-02-24
**Core Value:** 从数据中提取人类可理解的物理公式 — 不仅预测准确，更要让电网工程师能看懂、能验证、能信任预测逻辑

## v1 Requirements

Requirements for graduation thesis completion. Each maps to roadmap phases.

### Data & Infrastructure

- [ ] **DATA-01**: 从 ARPA-E PERFORM 获取风光负荷同步数据（ERCOT 为主，HDF5 格式，5分钟分辨率）
- [ ] **DATA-02**: 数据预处理管线（时间戳对齐 UTC、缺失值样条插值、Z-score 归一化、周期性时间编码）
- [ ] **DATA-03**: 多模态特征工程（气象：温度/GHI/风速/气压；时空：太阳角/周期编码；自回归：滞后窗口 t-1 到 t-48）

### KAN-SR Core Pipeline

- [ ] **KAN-01**: KAN 网络实现（pykan，B样条激活函数，边上可学习单变量函数，节点仅求和）
- [ ] **KAN-02**: 复合正则化稀疏训练（L1 幅度惩罚 + 行列信息熵损失 + 线性权重 L1，渐进式 lambda 调度）
- [ ] **KAN-03**: 网络自动剪枝（pykan prune()，基于激活幅度阈值移除近零边/节点）
- [ ] **KAN-04**: 符号表达式提取（样条→符号库匹配，Gauss-Newton 曲线拟合，组合为闭式方程）

### KAN Enhancements

- [ ] **PIKAN-01**: PIKAN 物理约束集成（夜间光伏=0 硬约束，风速立方关系软约束，负荷-温度单调性）
- [ ] **PIKAN-02**: MultKAN 乘法节点（捕获变量乘积关系如 P = 0.5ρAv³）
- [ ] **PIKAN-03**: 可分性/对称性检测（AI Feynman 启发，平移对称性、加法可分性、乘法可分性检测）

### Baselines & Evaluation

- [ ] **EVAL-01**: PySR 基准对比（Julia 后端遗传规划 SR，帕累托前沿输出，与 KAN-SR 公式比较）
- [ ] **EVAL-02**: 深度学习基准对比（LSTM + MLP，同等参数量，RMSE/MAE/R² 比较）
- [ ] **EVAL-03**: 多维评估框架（预测精度 + 公式复杂度 + 帕累托分析 + 物理一致性 + 计算效率）
- [ ] **EVAL-04**: 论文可视化套件（KAN 拓扑图、样条曲线、帕累托前沿、时序对比、残差分布、LaTeX 公式渲染）
- [ ] **EVAL-05**: 正则化消融研究（逐个禁用幅度惩罚/熵损失/L1，量化对公式质量和精度的影响）
- [ ] **EVAL-06**: 物理解释映射（提取公式→已知定律：Betz 定律、NOCT 校正、热惯性效应）
- [ ] **EVAL-07**: 偏导数敏感性分析（sympy 符号微分，dLoad/dTemp、dPV/dWindSpeed 等，验证符号正确性）
- [ ] **EVAL-08**: PySR 交叉验证（KAN-SR 子表达式输入 PySR 独立验证，增强学术可信度）

### Generalization

- [ ] **GENL-01**: 多 ISO 区域泛化研究（ERCOT 训练 → MISO/NYISO/SPP 测试，零样本/少样本迁移）

## v2 Requirements

Deferred to future work. Tracked but not in current roadmap.

### Extended Capabilities

- **PROB-01**: 概率预测/不确定性量化（帕累托前沿公式集成）
- **TPSR-01**: TPSR (Transformer-based SR) 实现与比较
- **IMG-01**: 多模态图像融合（天空图像、云层遮挡检测）

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| 论文撰写本身 | 只准备撰写所需的所有内容（实验、结果、图表） |
| 实时在线调度系统部署 | 研究验证项目，不是生产工程 |
| 移动端/边缘部署优化 | 超出毕设范围，可在 Future Work 提及 |
| Web Dashboard / GUI | Jupyter notebook 是论文的正确媒介 |
| EQL (Equation Learner) 对比 | 已过时，存在梯度爆炸问题，不是可信现代基准 |
| 超参数自动调优 (NAS/贝叶斯) | 增加复杂度但不增强可解释性叙事 |
| 风电场尾流效应建模 | 需要 CFD 级空间数据，ARPA-E PERFORM 不包含 |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATA-01 | TBD | Pending |
| DATA-02 | TBD | Pending |
| DATA-03 | TBD | Pending |
| KAN-01 | TBD | Pending |
| KAN-02 | TBD | Pending |
| KAN-03 | TBD | Pending |
| KAN-04 | TBD | Pending |
| PIKAN-01 | TBD | Pending |
| PIKAN-02 | TBD | Pending |
| PIKAN-03 | TBD | Pending |
| EVAL-01 | TBD | Pending |
| EVAL-02 | TBD | Pending |
| EVAL-03 | TBD | Pending |
| EVAL-04 | TBD | Pending |
| EVAL-05 | TBD | Pending |
| EVAL-06 | TBD | Pending |
| EVAL-07 | TBD | Pending |
| EVAL-08 | TBD | Pending |
| GENL-01 | TBD | Pending |

**Coverage:**
- v1 requirements: 19 total
- Mapped to phases: 0
- Unmapped: 19 ⚠️

---
*Requirements defined: 2026-02-24*
*Last updated: 2026-02-24 after initial definition*
