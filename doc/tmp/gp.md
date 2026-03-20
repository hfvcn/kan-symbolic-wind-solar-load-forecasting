基于这份核查文档，后续最重要的不是“继续把所有东西都试一遍”，而是把项目从“探索态”切到“可发表态”。核心判断很清楚：你现在已经有一条能成立的论文主线，但还没有把它收束成一个**证据强、表述稳、风险可控**的版本。文档里最稳的部分其实已经给出了：当前方法本质上是 **KAN teacher + post-hoc symbolic extraction**，不是传统蒸馏；direct net-load 路线会稳定退化成负荷主导；solar 已经能形成稳定正例；wind 更像“低符号可辨识性”的边界案例；同时流程还存在切分前插值带来的非严格无泄漏问题。

## 一句话说后续该怎么做

后续应该围绕这条主线推进：

**把论文定位成一篇“变量可辨识性 / 替代表达 / 符号简洁性偏置”的应用研究，而不是模型精度对比或蒸馏论文。**
这是文档最后的收束，也是最值得保住的叙事。

---

## 一、先定方向：哪些事情现在应该成为主线

### 1. 主问题要改写，不要再写成“谁预测更强”

从文档证据看，单纯写 “KAN vs PySR” 已经不是最强卖点。原因有两个：

第一，历史 run 里确实出现过 `PySR > KAN`，所以不能把故事写成“KAN 一直更强”；第二，当前真正有研究意味的现象，不在纯精度层，而在**为什么某些物理量能进公式，某些量进不去**。尤其是 direct net-load 路线下的 load-only 退化，以及 focused/component teacher 下 solar 和 wind 的明显分化，这比单纯精度表格更有论文价值。

所以主问题建议改成：

* **RQ1：高精度 teacher 能否稳定转化为含物理量的符号公式？**
* **RQ2：为什么 solar 能稳定显式化，而 wind 更难？**
* **RQ3：这种差异与 horizon、替代变量、公式简洁性偏置之间是什么关系？**

### 2. 方法定位要彻底纠正

文档已经明确：这里没有真正的 teacher-student distillation，symbolic 阶段是对已训练 KAN 的后验提取。这个点不能再含糊，因为一旦方法定义写错，整篇文章的可信度会直接受损。

所以后续所有写作、图示、实验章节都应该统一口径：

* 不要再说 symbolic student
* 不要再说 distillation training
* 统一改成
  **teacher-guided symbolic extraction**
  或
  **KAN teacher with post-hoc symbolic extraction**。

### 3. wind 不要被写成“失败样本”，而要写成“边界样本”

这是文档里最有价值的解释升级。现在最稳的说法不是 “wind 训练失败”，而是：

* wind 信息不一定不存在；
* 但它更容易被 lag、代理变量或替代表达吸收；
* 同时 symbolic extraction 又偏好简洁表达；
* 所以 raw wind term 更难以**简洁、稳定、泛化良好**的形式显式保留下来。

这会让你的论文从“某个变量就是学不会”变成“变量可辨识性受任务尺度与表达偏置共同制约”，层次会高很多。

---

## 二、实验上下一步该做什么：不是广撒网，而是补最关键缺口

我建议把后续工作拆成三个层级：**必须补、应该补、可以补**。

---

## 三、必须补的三件事

### A. 先补“流程可信度”这个硬伤

文档已经明确指出：当前流程不是严格无泄漏，因为缺失值插值和气象补值发生在切分前，而且用了 `limit_direction="both"`、`bfill()` 之类会引入未来信息的操作。这个问题不是 wind-specific bug，但它会削弱所有机制性结论的强度。

这意味着后续最优先的不是再跑更多 symbolic sweep，而是做一个**causal-clean 数据管道复刻版**。

建议你立刻加一个新实验分支：

* 先 split，再分别在 train / val / test 内做插值与补值
* 禁止任何会借用未来的 `bfill` 或双向插值
* meteorology 对齐也改成 split 内独立处理
* 保留与当前 canonical 设置尽量一致的其余步骤

你不一定要把整套实验全重跑，但至少要做下面这两个最小验证：

1. **direct delta_net_load_h6** 在无泄漏流程下是否仍然 load-dominated
2. **solar focused / wind focused** 的核心结论是否保持不变

如果这两点成立，你的论文可信度会大幅提升。
如果不成立，那也不是坏事，因为你能明确界定“哪些现象是稳的，哪些依赖于旧管道”。

### B. 补“多随机种子稳定性”

文档里已经提到，当前还缺少多随机种子验证，所以不少机制性解释只能停留在“部分支持”。

这里不用做大规模 sweep，最小可行方案就够：

对以下 4 条代表性设置，各跑 3–5 个种子：

* direct `delta_net_load_h6`
* solar focused / component
* wind focused
* 1 个 long-horizon wind 代表点（建议 h144 或你认为最有结构的那个）

每个种子只记录四类输出：

* abs RMSE / skill
* feature importance 中核心变量是否活跃
* 最终公式中变量组进入频次
* 公式复杂度（term 数、operator 数、是否出现 raw wind）

你真正要证明的不是“某次跑得很好”，而是：

* load-dominated 退化是不是稳的
* solar 稳定入式是不是稳的
* wind 不稳定显式化是不是稳的

### C. 补一个“最小公平比较”版本

文档已经很谨慎：当前 matched 设置下可以说 `KAN > PySR`，但还不是绝对严格公平比较。

这个地方不建议无限追求完美公平，因为会把项目拖进 benchmark 泥潭。你需要的只是一个**够论文使用的最小公平版**：

* 固定同一目标：`delta_net_load_h6`
* 固定同一特征集
* 固定统一训练样本数
* 统一 wall-clock 或统一搜索预算
* 明确写出 KAN 在 normalized space，PySR 在原始量纲搜索，这是方法差异，不再假装“完全同预算”

然后结论只写到这一步：

> 在当前 matched setting 下，KAN teacher 在预测效果上优于直接 PySR，但比较仍非绝对一致预算。

这就够了，不要再把大量精力花在“让 PySR 看起来绝对输掉”上。

---

## 四、应该补的三件事

### D. 把“变量进入公式”从个例变成指标

现在文档里的论证已经很强，但很多地方还是基于 run case 叙述。后续你应该把它指标化，不然文章会显得像经验观察。

建议你建立一套统一指标，按变量组统计：

* **teacher activation rate**：feature importance 中活跃边比例
* **symbolic inclusion rate**：变量组在最终公式中出现的频次
* **formula stability**：同设置不同 symbolic sweep / seeds 中保留下来的比例
* **performance-retention**：显式入式后对应的 skill 是否保持

变量组可按以下划分：

* load / load lag
* solar geometry
* ghi
* temperature
* raw wind
* wind lag
* proxy terms / cross terms

这样你就能把文档里的文字判断，转成一张总表或几张柱状图：

* solar：高 activation + 高 inclusion + 高 stability
* wind lag：有时高 inclusion
* raw wind：可能 activation 有，但 inclusion / stability 低
* direct net-load：load 极高，其他接近 0

这一步很关键，因为它会把论文从“讲故事”推进到“可复核分析”。

### E. 把 horizon 分析重写成“非单调窗口”而不是“越长越弱”

文档已经明确：wind 的 horizon 效应最稳的说法是“先增强、后减弱”的非单调性；solar 目前不支持简单单调叙事。

所以后续不要再做那种“随着 horizon 增大物理量都会变弱”的泛化。正确做法是：

* 对 wind，重点分析 **可辨识窗口**
* 对 solar，重点分析 **稳定显式化与长时失稳并存**
* 对其他变量，除非证据补齐，否则只做弱表述

你可以把 horizon 部分写成：

> Not all physically meaningful variables become uniformly harder to extract with longer horizons. Instead, wind exhibits a non-monotonic identifiability profile, suggesting an intermediate horizon window where symbolic structure is easier to expose. 

### F. 加一个“负控 / 消融”来支撑可辨识性解释

为了证明 wind 的问题不是“单纯训练没训好”，最好加一个最小消融：

* 去掉 `wind_lag_*`，保留 raw wind，看 raw wind 是否更容易进公式
* 去掉 proxy / cross terms，看 raw wind 是否会被迫显式化
* 或反过来，只保留 wind lag，不保留 raw wind，比较性能损失

这会直接验证“替代表达吸收”这个核心解释。
因为现在文档对这个解释是中高支持，但还不是最硬证据。

---

## 五、可以补，但优先级没那么高

### 1. 继续大规模 symbolic sweep

不建议现在作为第一优先级。因为你已经知道 direct 路线会坍缩，继续扫很多 threshold / lib，只会重复得到相似结论。

### 2. 继续追求“让 wind 也像 solar 一样稳定入式”

这个目标本身可能就不对。文档已经显示：即便 `s3_comp_wind_delta_h6` 里 raw wind 能 3/3 进入公式，泛化性能仍然差。

所以正确问题不是“怎样强行把 wind 塞进公式”，而是：

* 在什么条件下它能进
* 进了以后是否真的有助于泛化
* 为什么“显式进入”和“泛化更好”不等价

这比继续调参更像一个论文问题。

### 3. 扩太多新 baseline

现在 baseline 已经够用了：persistence、MLP、PySR。继续加很多模型会稀释主线。

---

## 六、论文结构上建议直接这样改

### 1. 引言

不要写成“我们提出一种蒸馏式符号建模框架”。
要写成：

* 高精度预测模型未必能转成物理可解释公式
* 变量的预测价值与其进入最终符号表达的能力并不等价
* 本文研究不同物理量在 teacher-guided symbolic extraction 中的**可辨识性差异**

### 2. 方法

方法图改成：

`Data pipeline -> KAN teacher -> symbolic extraction -> formula analysis`

不要出现 student distillation 箭头。

### 3. 实验问题

围绕三类现象组织：

* direct net-load 的退化
* focused/component teacher 的正反例
* horizon 对 identifiability 的影响

### 4. 结果

按下面顺序最顺：

1. current matched setting 下 `KAN > direct PySR`
2. 但 direct symbolic on net-load collapses to load-only
3. solar is a stable positive case
4. wind is an informative but hard-to-explicitly-retain case
5. horizon introduces non-monotonic identifiability for wind

### 5. 讨论

专门留一节讲限制：

* 非严格无泄漏
* 历史 run 与 current canonical 要区分
* 多种子不足
* 机制解释仍是“支持性证据”，不是严格证明

这会让整篇文章更稳，不会被 reviewer 一句话打穿。

---

## 七、你现在最该避免的写法

下面这些表述，基于文档内容，都不应该再写得太满：

不要写：

* “KAN 始终优于 PySR”
* “本文验证了蒸馏式 symbolic student 的有效性”
* “wind 没进公式说明它没有预测价值”
* “其他物理量都随 horizon 单调衰减”
* “我们的流程严格无泄漏”
* “现象已被严格证明来自变量替代机制” 

应该改成：

* “在当前 canonical matched setting 下，KAN 优于 direct PySR”
* “采用 KAN teacher with post-hoc symbolic extraction”
* “wind 的预测价值与其显式入式能力不等价”
* “wind 呈现非单调 horizon-dependent identifiability”
* “当前流程在严格因果意义上仍有限制”
* “现有证据支持替代表达与简洁性偏置的解释”

---

## 八、一个最实用的执行顺序

如果按投入产出比排序，我建议你就照这个顺序做：

### 第一步

把论文口径全改掉：
**蒸馏叙事删掉，改成 teacher-guided symbolic extraction。**

### 第二步

重做一个**无泄漏最小复刻实验**，只验证 2–3 个关键现象是否还在。

### 第三步

补 3–5 seeds 的稳定性，重点不是刷最好成绩，而是刷“现象是否稳定”。

### 第四步

把“变量是否进入公式”做成统一指标表和图，而不是只用 run case 讲。

### 第五步

补一个替代性消融，验证 raw wind 为什么容易被 lag / proxy 吸收。

### 第六步

再回头整理论文图表和结果章节。

---

## 九、如果让我替你做最终判断

这篇东西后续最值得走的，不是：

* “KAN 很强”
* “PySR 很弱”
* “wind 很难学”

而是：

**高精度 teacher 并不会自动产生物理上可信的简洁符号公式；变量能否被最终公式显式保留，取决于任务尺度、变量替代性、历史项吸收效应以及符号简洁性偏置。solar 提供了稳定正例，wind 提供了最有研究价值的边界案例。** 

这才是你现在最应该守住的主线。

如果你愿意，我下一步可以直接把这些内容整理成一份“论文后续执行清单 + 章节改写提纲”。
