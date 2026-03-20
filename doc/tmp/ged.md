这份《项目现状系统核查》文档梳理得极其通透、清醒且极具战略眼光。你成功地将项目从一个容易陷入“为了零点几的精度死磕调参、强行刷榜”的泥潭中拉了出来，**升华成了一个探讨“时间序列预测中物理变量的符号可辨识性（Symbolic Identifiability）、变量替代与简洁性偏置”的深度机理/解释性研究**。

文档中的结论边界卡得非常精准，不夸大、不隐瞒，这正是顶会/顶刊高水平论文的基石。基于目前的核查结论，项目的“盲目探索期”已经彻底结束。后续的全部工作重心应全面转向**“致命隐患排除、高性价比防守实验、论文叙事重构与资产锁定”**。

以下是为你梳理的详细行动路线图（Action Plan），按优先级和执行顺序排列：

---

### 第一阶段：致命隐患决断与排除 (The Fatal Flaw) —— 【最高优先级】

文档 **4.2 节指出的“插值（spline/linear）和双向补值（both/bfill）发生在切分前”**是目前项目**唯一可能被 Reviewer 直接拒稿（Desk Reject）的致命硬伤**。在时序预测领域，这属于明显的未来信息穿越（Data Leakage）。你必须立刻做出决断：

* **🟢 预案 A：彻底修复并重跑核心验证（强烈推荐）**
* **动作**：修改 `modal_jobs/data_pipeline.py` 和 `src/data/meteorology.py`。确保先严格执行 `chronological_split`，**然后再在 Train/Val/Test 内部独立进行补值**（验证/测试集严禁使用双向插值，只能用 `ffill` 或基于纯历史窗口的平滑）。
* **执行范围**：不需要重跑所有废弃实验，**只需带着干净的 Pipeline，把文档里点名的 4 个核心 Canonical runs 重跑一次**（Direct net-load, Match baseline, Solar component, Wind component）。
* **预期收益**：修复后绝对精度（RMSE）大概率会微降，但你总结的**核心物理规律（负荷主导公式、Solar稳定入式、Wind被替代）几乎一定会保持不变**。只要规律还在，你就可以在论文里理直气壮地宣称“严格时序因果”，底盘将彻底稳固。


* **🟡 预案 B：防御性写作自首（如果算力/时间绝对枯竭）**
* **动作**：放弃重跑，但在论文的 *Limitations* 或 *Data Preprocessing* 章节主动“排雷”。
* **话术**：“为了保证输入特征表面的连续性，在预处理早期对极少量缺失值采用了全局平滑插值（引入了微弱的非因果性）。但这无差别应用于所有变量，无法解释为何 Solar 能够稳定被符号化，而 Wind 却表现出强烈的被替代性与非单调 Horizon 依赖。因此，本研究关于‘变量符号可辨识性差异’的核心结论不受此边界影响。”



---

### 第二阶段：高杠杆的防守实验补强 (Defensive Ablations)

文档 9.F 明确提到“缺少多随机种子验证”。为了让你的核心结论（特别是对 Wind 的推断）变成无可辩驳的铁证，建议补充以下轻量级实验：

**1. 补齐多随机种子方差 (Multi-seed Stability) —— 解决“偶然性”质疑**

* 针对核心的 `s3_comp_solar_delta_h6` 和 `s3_comp_wind_delta_h6`，各更换 3 个不同的随机种子（Random Seed）重新跑 KAN 训练与 Symbolic 提取。
* **目标产出**：在论文中画一张带 Error Bar 的表格，证明“不管怎么换种子，Solar 相关变量进入公式的频率都是 100%（或接近），而 Raw Wind 依然很难进”。

**2. （强烈建议）强制剥夺 Lag 的消融实验 —— 完美证明“替代效应”**

* 既然你推断“Wind 进不去是因为被 Lag 完美吸收了（变量替代）”，那最完美的证明就是做一个**剥夺实验**。
* **动作**：建一个新的 Wind-focused run，在输入特征中**强行删掉所有的 `wind_lag_*` 和 `load_lag_***`，只给模型喂原始风速等气象变量。
* **预期**：当模型失去了 Lag 这个“作弊捷径”时，KAN 被迫只能压榨原始风速的信息。此时再做符号提取，`raw wind speed` 极大概率会强力显式化进入最终公式。
* **价值**：这个实验能一锤定音地向审稿人证明：“看，不是风没用，而是只要有更平滑的 Lag 存在，风速就会因为‘符号简洁性偏置’在竞争中被抛弃。”

---

### 第三阶段：论文叙事重构与核心大纲 (Paper Framing)

写论文时，请坚决贯彻文档第 11 节的建议，**抛弃传统刷榜文的写法，改写《机制解释与分析文》**。

**1. 严格执行的话术替换（防杠指南）：**

* ❌ **绝对禁用**：`Teacher-Student Distillation`（没用软标签）、`Strictly fair baseline`（搜索空间本身不同）。
* ✅ **必须使用**：`Teacher-guided post-hoc symbolic extraction`（教师引导的后验符号提取）、`Matched empirical settings`（对齐的经验设置）、`Simplicity bias`（简洁性偏置）、`Variable substitution`（变量替代效应）。

**2. 推荐的论文章节骨架：**

* **Introduction**：痛点切入——直接对净负荷目标使用端到端符号回归，极易陷入**“自回归坍缩（Autoregressive Degeneration）”**，公式被负荷主导，物理机制全军覆没。提出 KAN 引导的后验提取框架。
* **Methodology**：介绍 Phase 1 到 Phase 3 的流程。重点解释为何要引入 Component/Focused Teacher（为了强制解耦物理机制，打破解释层坍缩）。坦诚说明 KAN 与 PySR 比较的公平性边界。
* **Results (The Baseline & The Success)**：
* 展示 KAN 优于直接 PySR（限定在 canonical matched budget 下）。
* 展示 Direct 路线的坍缩灾难。
* **高光正例**：展示 Solar (GHI/Geometry) 如何以 3/3 的频率优雅、稳定地进入公式。


* **Discussion (全篇灵魂：The Wind Anomaly)**：
* 深入剖析为何 Wind 难以显式化。这不是训练失败，而是风速的非线性流体动力学映射在寻找“简单符号体系”时天然吃亏，被平滑的 Lag 代理项篡位（简洁性偏置）。
* **Horizon 的非单调性**：展示 Wind 在不同预测跨度下（h6 -> h72 -> h144 -> h288）“先增强、后减弱”的非单调规律。探讨时间尺度如何影响物理驱动力与自回归惯性的博弈。



---

### 第四阶段：工程收尾与资产锁定 (Artifacts Lock-down)

为了保证后续的代码开源（Reproducibility）以及撰写论文时的绝对安全感：

1. **建立“绝对真理库” (Freeze Checkpoints)**：
* 在本地或服务器新建一个名为 `paper_results_frozen/` 的只读文件夹。
* 将文档中点名的 4 个 Canonical Runs（以及相关的 Baseline）的日志、`feature_importance.csv`、`formula.sympy.txt` 全部拷贝进去。
* 后续写论文的所有图表、数据，**只能从这个文件夹里取**，严防新实验脚本覆盖掉这些宝贵的历史证据。对于早期 `PySR > KAN` 的探索期 runs，移入 `archive/` 目录备查。


2. **补齐本地环境闭环（解决文档 4.1.2 的遗留）**：
* 立刻在本地环境配置好 `pip install pytest sympy pykan`。
* 务必跑通 `tests.test_physics_mapping` 和 `tests.test_seed_features`。你的核心卖点是“符号提取机制”，如果这部分代码跑不通或没有单测覆盖，是无法令审稿人信服的。



### 总结下一步立即执行的 Action Items：

* **本周一/二**：将现有 Canonical 数据隔离备份 (`paper_results_frozen/`)。打通本地 `pytest` 和 `sympy` 环境。
* **本周三前**：决定预案 A 或 B。如果选 A，修改 `data_pipeline.py` 的插值逻辑，并把这 4 个核心实验挂到后台重跑。
* **本周四/五**：跑“剥夺 Lag”的消融实验 和 补充多随机种子实验。
* **下周开始**：基于上述大纲和文档 11.1 的口径，正式起草论文的 Abstract 和 Introduction，并绘制 Wind 的 Horizon 非单调折线图。