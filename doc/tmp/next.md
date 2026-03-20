**后续计划建议：以创新驱动提升论文质量的系统性路线图（2026-2027）**

当前项目已通过系统核查清晰定位了强证据（solar物理量稳定入式、canonical KAN优于PySR、direct路线load主导退化、wind非单调horizon依赖）和关键局限（数据泄漏、wind符号可辨识性偏低、非严格蒸馏、历史run混淆、缺乏多种子/外部验证）。这些为论文提供了扎实材料，但要冲击高影响力期刊（如*Applied Energy*、*Renewable and Sustainable Energy Reviews* 或 *IEEE Transactions on Sustainable Energy*），需超越文档中已有思路，注入2025-2026最新文献驱动的创新尝试：KAN-SR分而治之框架、Physics-Informed Symbolic Regression (PiSR/PISR)、高级KAN变体（HG-KAN、KARN、T-KAN）、严格因果预处理、物理约束嵌入以及符号可辨识性量化指标。

以下计划不局限于“修复+验证”，而是构建一个**混合神经-符号-物理信息框架**，同时解决wind“有价值却难显式化”的核心科学问题、强化机制洞见，并实现可重复性/泛化跃升。每个部分包含：**问题映射**、**文献支撑**、**具体创新尝试**、**预期论文贡献**、**实施路径与边缘考虑**。整体分三阶段（短期1-3月、中期3-6月、长期6-12月），优先级由高到低排序，确保高效产出。

### 1. 基础可靠性升级：严格无泄漏管道 + 多种子/可重复性保障（短期优先，消除审稿人首要质疑）
**问题映射**：文档4.2明确指出切分前全局插值/气象补值导致未来信息泄漏（spline/linear + both方向），这虽非wind-specific bug，却削弱“机制发现”的强度；历史run与当前canonical混淆也需清晰区分。

**文献支撑**：2025风速预测论文强调“先切分后处理”（split-first原则），推荐rolling decomposition、stepwise decomposition或Maximal Overlap Discrete Wavelet Transform (MODWT)实现因果插值；时间序列最佳实践一致要求train-only scaler/imputer与forward-only imputation。

**创新尝试**：
- 重构`modal_jobs/data_pipeline.py`与`src/data/preprocess.py`：先`chronological_split`（保留48-step gap），再在**每个split内独立**执行forward-only linear/spline插值（禁用`limit_direction="both"`与`bfill`），气象对齐也移至split后并使用causal time interpolation。
- 添加“泄漏量化模块”：引入synthetic future-leakage ablation（人为注入未来信息对比性能/公式变化），并用blocked time-series CV + 10+随机种子重新跑canonical runs（paperref系列 + long-horizon）。
- 扩展：实现rolling-window预处理测试，量化泄漏对wind公式稳定性的具体影响（e.g., wind_speed项入式频率变化）。

**预期论文贡献**：允许论文用**强表述**“严格时间因果、无未来信息泄漏流程”，新增“泄漏敏感性分析”小节作为robustness证据；直接回应“流程可靠性”质疑，提升可重复性（代码+工件可公开）。

**实施路径与边缘考虑**：本地无kan/sympy环境可先用Docker/云GPU；边缘case：极端缺失值场景下forward-only可能降低填充质量——需额外ablation对比linear vs spline forward性能。若性能下降<5%，仍优先因果性。预计1个月完成管道+重跑，产出新feature_importance.csv与formula.sympy.txt。

### 2. 方法论核心创新：KAN-SR混合框架 + Physics-Informed Symbolic Extraction（中期核心，新颖性引擎）
**问题映射**：当前是“KAN teacher + post-hoc extraction”，非真正蒸馏；wind raw项易被lag/替代吸收；symbolic提取受简洁性偏置影响。

**文献支撑**：2025 KAN-SR框架（arxiv:2509.10089）采用divide-and-conquer（先检测separability/symmetry简化子问题，再单层KAN拟合+SymPy精简），在Feynman SRSD基准上Easy任务精确恢复率93.3%（PySR仅60%），对噪声/无关特征鲁棒；2026 in-context symbolic regression for KAN（arxiv:2603.15250）通过greedy/gated全网络上下文选择算子，提升公式一致性达99.8% MSE降低；power systems SR综述与PiSR工作强调将物理定律（风能立方律、solar几何）嵌入operator库或loss。

**创新尝试**（多角度组合）：
- **升级提取管道**：替换当前`kan_symbolic.py`为KAN-SR：KAN训练后先检测translational symmetry/separability（e.g., wind_lag与raw wind的乘性关系），分解子问题，再用in-context greedy匹配（而非孤立per-edge fit）。可选集成LLM（GPT-4o等）从KAN spline曲线生成初始ansatz，加速物理一致公式发现。
- **物理信息嵌入**：在PySR/KAN-SR operator库中**硬编码**物理先验（wind_power ~ v³、solar irradiance几何公式、温度-压力关系）；或soft constraint加入KAN loss（e.g., 最小化公式与物理定律偏差）。针对wind设计“cubic wind”专用特征并强制保留。
- **真正“guided distillation”变体**：用KAN teacher输出（而非真实y）作为PySR fitness额外项，或将提取公式反向初始化KAN（seed_from_symbolic_run升级版），形成闭环teacher-student。
- **新指标引入**：定义“Symbolic Identifiability Score”（SIS）：公式中目标物理量出现频率×物理一致性（能量守恒/单调性校验）×跨种子稳定性。量化wind vs solar差异。

**预期论文贡献**：首次（或早期）在净负荷预测中提出“KAN-SR + PiSR”混合框架，定位为“神经-符号物理信息可解释预测”新范式；直接解释wind“低符号可辨识性源于替代+简洁偏置+物理非线性”，而非训练失败；新增“物理一致公式发现”案例（solar稳定恢复GHI+geometry，wind恢复v³项），大幅提升讨论深度与理论价值。

**实施路径与边缘考虑**：先在solar focused run上pilot KAN-SR（1周验证），再推广wind；计算开销较高——用NCDE扩展处理动态horizon。边缘case：物理约束过强可能牺牲预测精度——需多目标优化（MSE + 物理偏差 + 复杂度）。文献直接可引，代码复现性高。

### 3. Wind/Solar专项深化 + Horizon非单调机制探究（中期并行，针对性解决核心反例）
**问题映射**：wind即使入式也性能差（s3_comp skill负）；horizon非单调但solar不支持单调叙事；load主导问题。

**文献支撑**：HG-KAN（2026）用异构图建模尾流/空间相关性提升风电时空预测；multi-horizon论文显示风电uncertainty在horizon 2-3天存在“切换点”（weather-to-power vs NWP主导），支持非单调；PiSR在wake modeling中成功提取可解释方程。

**创新尝试**：
- Wind专用：引入u/v分量、风切变、湍流强度、hub-height correction显式特征；用causal discovery（PCMCI等）量化lag吸收机制；尝试HG-KAN或Graph-KAN作为teacher建模多涡轮/站点交互。
- Solar扩展：已强，继续联合solar+load多任务提取“交互公式”（e.g., solar geometry抑制load主导）。
- Horizon创新：开发multi-output KAN（horizon embedding）+ ranking consistency loss（2025论文），联合预测所有horizon并提取“horizon-dependent公式”；聚类horizon regime（短/中/长）分别提取符号，解释wind“先增后降”窗口。
- 额外尝试：合成数据实验（物理仿真风场+噪声）隔离“替代机制” vs “简洁偏置”。

**预期论文贡献**：将wind从“异常”升级为“可解释边界案例”，新增“符号可辨识性horizon演化”图表与理论讨论；为能源调度提供实用洞见（中等horizon最适合符号公式）。

### 4. 验证广度与应用扩展（长期，提升泛化与影响力）
- **外部验证**：用公开数据集（NREL ERCOT/MISO 5min风光负荷、Open-Power-System-Data、GEFCom）重复实验，测试跨区域/气候泛化。
- **基线与架构扩展**：对比T-KAN（Temporal）、KARN（Recurrent）、MSN-KAN、PINN hybrids；添加XAI（SHAP on KAN）+ symbolic对比。
- **部署导向**：评估符号公式轻量部署（边缘设备MPC优化）；不确定性感知SR（ensemble公式置信区间）。
- **理论创新**：提出“变量符号可辨识性偏置”框架（generalizable到其他可再生任务），用复杂度度量/信息论解释。

**预期论文贡献**：从“单数据集应用”升级为“可泛化可解释能源预测方法论”，新增“实际影响”小节（电网调度案例），易获引用。

### 5. 整体论文定位、时间线与质量提升路径
- **定位转变**：从“KAN vs PySR精度对比”转向“一篇围绕‘物理变量符号可辨识性、替代表达与物理信息偏置’的应用理论研究”，强调“KAN-SR + PiSR”混合在解决load主导、wind边界问题上的突破。
- **时间线**：Phase 1（1-2月）→ Phase 2（2-4月）→ Phase 3（4-8月）→ 论文重写+投稿。
- **质量跃升机制**：
  - **Rigor**：泄漏修复+多种子+新指标，消除所有文档弱点。
  - **Novelty**：KAN-SR/PiSR混合、identifiability score、物理约束SR（2025-2026前沿，未见净负荷应用）。
  - **Impact**：物理一致公式可直接用于电网优化；讨论部分材料丰富（过程演化+机制收敛）。
  - **可视化与完整性**：KAN激活曲线、公式演化树、horizon skill热图；补充edge cases（极端天气、数据稀疏）讨论。

这些计划直接基于当前canonical runs工件（只需少量重跑），结合最新文献，提供可执行路径与清晰引用支持。若执行，论文可从“扎实应用”升级为“方法论突破”，极大提高接受率与引用潜力。建议优先启动管道修复与KAN-SR pilot，后续根据初步结果微调wind物理约束强度。如需具体代码伪码、引用列表或某创新的详细实验设计，可进一步讨论。

我先给结论：这份建议**方向是对的，但目前“创新密度过高、主线略散”**。我会给它 **8/10**。最强的地方，是它准确踩中了你这篇论文真正该回答的问题：不是继续证明“谁的 RMSE 更低”，而是解释**为什么 wind 有预测价值，却难以稳定显式化为简洁公式**。这和你上传文档里已经确认的主线是高度一致的：当前体系应写成 `KAN teacher + symbolic extraction`，direct net-load 路线会退化为负荷主导，solar 是稳定正例，wind 是“有信息但难显式化”的边界案例，而且流程目前还不属于严格无泄漏。

外部文献也基本支持你“往神经-符号-物理”方向走，但要分清**哪些是可直接转成投稿卖点，哪些只是探索性工具**。KAN-SR 的确是一个值得跟进的新方向，公开摘要明确强调 divide-and-conquer、对称性/可分离性简化，以及在 Feynman SRSD 上做 ground-truth equation recovery；更近的 in-context symbolic regression for KAN 也正面瞄准了 KAN 符号提取 bottleneck，并在摘要中报告了最高 99.8% 的 median OFAT test MSE 降幅。与此同时，PISR 说明“物理约束 + SR”在电力系统里是可行的，但它对应的是**power-system voltage**，不是你的净负荷预测，所以它更适合作为“方法学邻近证据”，不适合作为“本文已有同类先例”的强背书。([arXiv][1])

我对你这份计划的第一条判断是：**“基础可靠性升级”不是短期优先，而是绝对优先，且必须先做。** 这不是保守，而是因为你现在文档自己已经承认，现有流程里切分前插值和气象补值会削弱机制性表述强度；而标准 ML 最佳实践也明确要求预处理变换要以训练过程为基准并一致应用到后续数据，否则就会引入不当的信息使用。对这篇论文来说，先把 split-first、train-only preprocessing、blocked CV、多随机种子、泄漏敏感性分析补齐，带来的说服力很可能比再加两个新模型更大。 ([Scikit-Learn][2])

我最认可、也最建议你保留成**核心原创贡献**的，不是“再堆几个 KAN 变体”，而是你提的 **Symbolic Identifiability Score (SIS)**。这比单纯比较 KAN/PySR 更接近审稿人会记住的贡献点，因为它把“入式频率、跨种子稳定性、物理一致性、horizon 稳定性”统一成一个可量化对象，正好对应你文档里最稳的叙事：solar 是稳定正例，wind 是低可辨识性边界案例。
我建议把 SIS 做得比你现在更“可审稿”一点：
SIS = 变量入式频率 × 符号/方向一致性 × 物理可接受率 × 跨种子/跨切分稳定性 × horizon 一致性。
其中“物理可接受率”不要只看是否出现 `v^3`，还要看符号、单调区间、单位/量纲是否合理。这样它就不是一个 ad hoc 指标，而是一个围绕“可辨识性”的论文主轴。

相反，我会**下调**“全量引入 HG-KAN、KARN、TKAN、MSN-KAN 等一整串架构”的优先级。原因不是这些方向没价值，而是它们回答的问题和你当前论文主问题并不完全一致。HG-KAN 很新，也很有意思，但它的贡献点是风场里的 heterogeneous graph、wake-aware relation 和 turbine-level spatio-temporal dependency；论文自己也承认验证仍主要局限在单一 onshore site。KARN 是短期负荷预测跨多类消费者；TKAN 更偏通用多步时间序列预测。它们更适合充当“补充 baseline / appendix / follow-up project”，不适合在这篇稿子里成为主线，否则你会把论文从“identifiability 研究”拉回“模型 zoo 比赛”。([Springer][3])

我也会**保留但降级**“KAN-SR + in-context symbolic extraction”，把它从“主标题”改成“高风险高收益 pilot”。原因很简单：它们确实前沿，但目前一个是 2025 年预印本，一个是刚挂出的 2026 arXiv / XAI’2026 接收工作，适合做方法增强，不适合一开始就把整篇稿子的可信度压在它们身上。尤其是你建议里写到的某些具体 benchmark 数字，我没有在公开摘要页直接核到；正式计划或论文引言里不要先把这些百分比写死，除非你已经逐表核过原文。更稳的写法是：**“我们将把 KAN-SR / in-context extraction 作为符号提取增强器进行 pilot，对比当前 post-hoc edge-wise extraction 是否能提升公式稳定性和物理一致性。”** ([arXiv][1])

对于“physics-informed”这条线，我支持，但会把你现在的“硬编码物理定律”改成**弱物理约束 + 量纲约束 + 结构先验**。原因是：在净负荷任务里，raw wind 并不等价于 turbine power，`v^3` 也不必然应该直接以简单形式落在 net-load equation 里；如果你一开始就强推 cubic wind 项，审稿人很可能会问：你是在“发现规律”，还是在“把先验塞回公式”。更稳妥的办法，是先给 operator 库加上量纲一致或物理允许的结构约束，再把 `v^3`、solar geometry、pressure/temperature 关系作为**可选可竞争**的 operator family，而不是硬性保留。物理约束 SR 和 units constraints 的文献确实支持这种思路，而且在风机 wake 建模里，最近也已有“domain-informed decomposition + SR”实现 equation-level closure 的例子。([Anurag Mohapatra | CoSES, TUM][4])

你提到的 **PCMCI / causal discovery**，我建议只作为**支持性分析**，不要做主证据链。Tigramite/PCMCI 当然适合拿来检查 lag 吸收和 proxy substitution 的候选结构，但最新的真实世界评估也提醒，PCMCI+ 在复杂时序里会系统性漏掉部分关键机制，所以它更适合“提出假说”而不是“证明 wind 替代机制已被严格识别”。([Jakob Runge][5])

我反而想给你加一个你原文里**没强调但我认为很值的创新点**：把 **“substitution hypothesis” 做成正式实验对象**。你现在文档已经隐含这个观点：wind 信息可能被 lag 或代理变量吸收。
比起再上一个新模型，我更建议你设计三组专门实验：

1. **raw-only / lag-only / proxy-only / full-set** 四组 teacher；
2. 比较 teacher 精度、公式入式率、SIS、跨种子稳定性；
3. 再做“变量移除-替补”反事实实验，看拿掉 raw wind 后，哪些变量会系统性补位。
   这会比“我又试了一个 KAN 变体”更直接地回答论文问题，而且非常像一篇好论文的核心实验。

还有一个我会额外加入的建议：如果你真的要强化 SR baseline，不要只盯着 PySR。**把 PSE（parallel symbolic enumeration）作为小规模强基线引入，会比再加两三个 KAN 变体更能提高论文说服力。** 这篇 2026 年 Nature Computational Science 工作的卖点正是 SR 里最老的问题：candidate expression 搜索效率和 recovery accuracy；它强调 common-subtree reuse、GPU parallel evaluation，并在 200+ synthetic / experimental problems 上报告了更高 recovery accuracy 和更快速度。它未必一定在你的任务上赢，但它作为“我们确实对比过更强的 2025–2026 SR 方法”的证据，非常有价值。([Nature][6])

外部验证这部分，我认为你写得对，而且**应该比模型扩张更早做**。公开可复现实验资源是有的：OPSD 提供 version-controlled 的 load / wind / solar 时间序列；GEFCom2014 有 load、wind、solar 多赛道；NREL NSRDB 提供 GHI/DNI/DHI 与气象数据，WIND/WTK 体系则提供公开风资源与时序数据。对冲高一点的能源期刊，跨区域 / 跨数据源泛化通常比“本地再刷一组 RMSE”更值钱。([开放电力系统数据][7])

所以，如果是我来帮你重排这份计划，我会改成下面这个版本：

**第一优先级，必须先做：**
修复严格因果数据管道；补多随机种子、blocked CV、泄漏敏感性分析、预算公平性表；把论文口径锁死在 `KAN teacher + post-hoc symbolic extraction`，不要再写成蒸馏。这个阶段的目标不是“更创新”，而是让审稿人没有机会先把你打回到流程漏洞上。

**第二优先级，最值得押注的原创主线：**
围绕“变量符号可辨识性”做成一套完整方法：SIS 指标、公式稳定性分析、horizon regime 分段提取、反事实 substitution 实验、物理可接受性检验。这里才是你最像一篇好论文的地方，因为它把 solar 正例、wind 反例、load 主导退化、horizon 非单调全串起来了。

**第三优先级，方法增强而非主标题：**
做 KAN-SR 或 in-context symbolic extraction pilot，先在 solar 上验证是否真能提升公式稳定性，再迁移到 wind；同时把 PSE 作为强 SR baseline 引入。别一开始就把 HG-KAN、KARN、TKAN 全铺开。([arXiv][8])

**第四优先级，冲高影响力期刊时再补：**
外部数据复现、极端天气切片、不确定性/区间版本、轻量部署价值。能源 forecasting 的 XAI 文献综述已经指出，generation forecasting 本质上是物理建模问题，而且现有 XAI 实践和真实运营需求之间仍有脱节；你这篇稿子如果能把“可解释性”推进到“物理一致、跨数据源稳定、可部署”，档次会明显更高。([MDPI][9])

最后给你一句最直接的判断：
**这份建议里最该保留的是“无泄漏重构 + SIS + substitution 实验 + horizon regime 分析 + 外部验证”；最该降级的是“大量 KAN 变体堆叠”；最该谨慎的是“把 KAN-SR/PISR/LLM 直接写成主贡献”；最值得补进来的，是“PSE 强基线”和“反事实替代机制实验”。**

如果你愿意，我下一步可以直接把这份方案改写成一版**更像论文 roadmap / 开题答辩用**的正式版本。

[1]: https://arxiv.org/abs/2509.10089 "[2509.10089] KAN-SR: A Kolmogorov-Arnold Network Guided Symbolic Regression Framework"
[2]: https://scikit-learn.org/stable/common_pitfalls.html "11. Common pitfalls and recommended practices — scikit-learn 1.8.0 documentation"
[3]: https://link.springer.com/article/10.1007/s40866-026-00336-x "Heterogeneous Graph Kolmogorov–Arnold Networks for Spatio-Temporal Wind Power Forecasting | Smart Grids and Sustainable Energy | Springer Nature Link"
[4]: https://anuragmohapatra90.github.io/publication/2025-PISR-Physics-Informed-Symbolic-Regression-for-Pred " PISR: Physics-Informed Symbolic Regression for Predicting Power System Voltage Anurag Mohapatra CoSES, TUM"
[5]: https://jakobrunge.github.io/tigramite/?utm_source=chatgpt.com "Welcome to Tigramite’s documentation! — Tigramite 5.2 documentation"
[6]: https://www.nature.com/articles/s43588-025-00904-8.pdf "Discovering physical laws with parallel symbolic enumeration"
[7]: https://open-power-system-data.org/ "Open Power System Data – A platform for open data of the European power system."
[8]: https://arxiv.org/abs/2603.15250 "[2603.15250] In-Context Symbolic Regression for Robustness-Improved Kolmogorov-Arnold Networks"
[9]: https://www.mdpi.com/2504-4990/7/4/153 "A Four-Dimensional Analysis of Explainable AI in Energy Forecasting: A Domain-Specific Systematic Review"
