基于这份系统核查，后续最正确的方向不是继续把项目当成“谁的 RMSE 更低”的调参题，而是把它收束成一个更明确的研究问题：**高精度 teacher 能否转成物理上可信、变量上可辨识的符号公式；如果不能，卡在哪里。** 这份文档其实已经把主线压得很清楚了：direct net-load 会坍缩到 load-only，solar 是稳定正例，wind 是关键反例，而当前最大的短板不是想法不够，而是证据链还不够干净、不够稳。

所以，后续不建议再大范围扩散式试模型，而建议按下面这个顺序推进：**先修可信度底座，再做一组最小但关键的确认实验，最后再把论文主线定下来。**

## 一、先把项目定位收紧，不要再发散

现在这个项目最适合的定位，不是“提出了一个新的 teacher-student distillation 方法”，也不是“证明 KAN 永远优于 PySR”，而是：

**一篇围绕变量可辨识性、替代表达、以及符号简洁性偏置的应用/经验研究。**

更具体一点，论文真正值钱的主线应该是这四句：

1. **direct 的 net-load 符号提取会稳定坍缩到负荷主导。**
2. **focused/component teacher 能让真实物理量进入解释层。**
3. **solar 是稳定正例。**
4. **wind 不是“没用”，而是更难以简洁、稳定、泛化良好的原始风速项显式保留。**

这四句里，前两句和 solar 正例已经比较强；最需要补证据的是 wind 的机制解释，以及整个流程的可信度边界。

## 二、第一优先级：先修“能不能过审”的底座

### 1. 先把数据管道改成 split-aware，再谈机制

你现在最危险的点不是模型，而是**切分前插值/补值**。这个问题不一定会推翻 wind 现象，但它会让任何“机制性结论”先天变弱。审稿人很容易一句话就卡死你：**你观察到的现象，会不会只是全局预处理带来的副作用？**

后续应直接改成下面这个顺序：

**原始数据对齐（不补值） -> 时间切分 -> 各 split 内独立补值/插值 -> 各 split 内构造 lag/derived target -> scaler 只 fit train -> 应用到 val/test**

其中最低要求是：

* 先切分，再插值
* val/test 禁止用跨边界信息
* 最好不要在 val/test 用 `bfill`
* 气象对齐后的时间插值也必须 split 之后再做

更稳妥的版本是：

* train 内允许局部插值
* val/test 只用 forward-only 或保守填补
* 对太长的缺失段直接删窗口，而不是硬补

不要删除 legacy pipeline。应该保留两个模式：

* `legacy_full_impute`
* `clean_split_impute`

这样你才能做一张很重要的表：**legacy vs clean 的指标对比 + 公式结构对比**。只要 clean rerun 以后 qualitative pattern 还在，你的故事就会一下子稳很多。

### 2. 把环境补全到能完整回归

文档里已经说明了本地缺 `pytest`、`sympy`，而且没法重新训练完整 KAN，很多判断依赖历史工件。这个状态不适合直接进论文主线。

后续应立刻补三件事：

* 固化一个能跑训练、单测、symbolic 导出的环境
* 补齐 `pytest` / `sympy` / `kan` 依赖
* 把目前没跑通的 tests 跑全，并新增泄漏边界测试

最该新增的测试不是更多模型测试，而是**边界测试**：

* split 边界附近缺失值不会从未来 split 借值
* meteorology 对齐后不会跨 split `bfill`
* lag/derived feature 仍然只在 split 内构造
* symbolic feature group mapping 正确
* scaler 对 feature names 的映射仍然稳定

### 3. 建一个真正的 canonical manifest

你现在证据很多，但散在 run id、CSV、公式文件里。后续必须做一个 canonical manifest，把下面这些东西统一记录：

* run 名称
* 任务类型（direct / solar / wind / horizon）
* pipeline 模式（legacy / clean）
* feature set
* teacher 类型
* symbolic 配置
* seed
* 评价指标
* 公式复杂度
* 变量组进入频率

没有这个清单，后面写论文和做图会非常痛苦，而且容易在“历史 run / 当前主实验 / exploratory run”之间混淆。

---

## 三、第二优先级：不要再广撒网，先做一组“最小必做实验包”

我的建议是：**先只保留最能支撑主线的四类设置**，其它都往后放。

### A. direct `delta_net_load_h6`：作为“失败基线”重跑

这个实验的目的不是救活 direct，而是**固定一个很强的负结果**：

> 在系统级 net-load 目标上，直接抽单条公式会坍缩成 load-dominant 的极简关系。

这条负结果其实很值钱，因为它给后面 component/focused teacher 的存在提供了必要性。
这里至少做 3 个 seeds，统一 symbolic 配置，核心看：

* test skill
* `load` 占比
* 是否再次 collapse 到 load-only / near load-only
* 公式复杂度是否持续很低

### B. solar：只保留一条最强、最稳、最简的正例

文档已经表明 solar 路线证据足够强，所以不建议把两条 solar 都塞进主文。主文只保留**一条最干净的 solar 正例**即可，另一个放附录。

目标不是证明 solar “特别神”，而是证明：

> 当前链路并不是“任何物理量都进不去公式”；至少在 solar 上，物理信息是可以稳定显式化的。

因此 solar 需要的不是更多花样，而是：

* clean pipeline 下复现
* 3 seeds
* 变量组进入频率统计
* 公式复杂度和性能都稳定

### C. `s0p_wind_delta_h6`：作为“有预测价值但不显式”的 wind 难例

这条线很重要，因为它最能支撑：

> “没有进入最终符号公式” 不等于 “没有预测价值”。

你要把它固定成一个**高价值反例**：

* 表现不算差
* wind 相关信息并非完全消失
* 但最终显式留下的常常是 `wind_lag` 或代理项，而不是 raw wind

### D. `s3_comp_wind_delta_h6`：作为“显式进入但泛化差”的对照反例

这条线不要藏，反而要保留。因为它刚好提供另一个很强的论点：

> 让 raw wind 显式进入公式是做得到的，但“进公式”并不自动等价于“更好的泛化”。

这其实是整篇文章里最有研究味道的一点。
它和上一条 wind 组成一对非常漂亮的对照：

* 一条是“好用但不显式”
* 一条是“显式但不一定泛化好”

这个张力比再刷一个更高分 run 更值得写。

### E. KAN vs PySR：保留，但降级为次要问题

这部分不要再当主标题。最稳妥的做法是：

* 在 clean pipeline 下重跑一个 matched comparison
* 统一 feature set、train rows、预算、seed 数
* 主文只说“在当前 matched 主实验里 KAN teacher 更适合作为后续符号提取的高精度起点”
* 把早期 `PySR > KAN` 的历史 run 放附录，作为实验演化史

换句话说，**KAN vs PySR 是辅助背景，不是主线结论。**

---

## 四、所有新实验都不要只看 RMSE，要统一输出“可辨识性指标”

后面所有分析，建议不要再靠“人工读几条公式”。应该统一输出下面几类指标：

1. **预测指标**
   RMSE、MAE、skill vs persistence

2. **teacher 侧变量组活跃度**
   不是只看单列，而是看 group：

   * load
   * load lag
   * raw wind
   * wind lag
   * solar / GHI / geometry
   * solar lag
   * temp / pressure

3. **symbolic 侧变量组入式频率**
   某个变量组在多少个 seeds / sweeps 中进入最终公式

4. **teacher -> symbolic retention ratio**
   teacher 里活跃的组，有多少能进入最终公式

5. **公式复杂度**
   项数、深度、operator 数量、是否过于极简

6. **跨 seed 稳定性**
   不要追求逐字符公式一致，而是比较变量组集合的一致性

这一步很关键。因为你真正想写的不是“某一条公式长什么样”，而是：

> 哪类变量更容易被 teacher 学到，哪类变量更容易跨过 symbolic 提取，哪类变量会在简洁性压力下消失。

---

## 五、第三优先级：把 wind 的“机制解释”补成真正的证据

现在文档对 wind 的解释已经很像对的了，但还差“更直接的验证”。后续别再盲目调参，直接做三组针对性实验。

### 1. 做 teacher 侧 group ablation，而不是只看 edge count

最值得加的一步，是对已训练好的 canonical teachers 做**变量组遮蔽/置零 ablation**：

* 去掉 raw wind，性能掉多少
* 去掉 wind lag，性能掉多少
* 去掉 temp / GHI proxy，性能掉多少

这会比单看 edge count 更有说服力。因为你就能明确区分：

* **raw wind 对 teacher 是否真的有贡献**
* **最终为什么没有出现在公式里**
* **是不是 lag/proxy 把它吸收掉了**

这一步能直接支撑“absence from formula ≠ absence of predictive value”。

### 2. 做一个很小的替代性实验矩阵

我建议 wind 只做 2×2 或 3×2 的小矩阵，不要再铺太大：

* 有 / 无 wind lag
* 有 / 无 temp/GHI proxy
* 低复杂度 / 高复杂度 symbolic budget

你想验证的不是“哪套最强”，而是两个命题：

1. **加上 lag 和 proxy 后，raw wind 是否更不容易显式入式**
2. **放松公式复杂度后，raw wind 是否更容易进入，但泛化未必更好**

只要这两个趋势出来，文档里的“替代性 + 简洁性偏置”就不再只是推测，而会变成有实验支持的讨论。

### 3. horizon 只盯 wind 做主分析，solar 只做控制

现在最容易写稳的 horizon 叙事是：

> wind 的可辨识性具有非单调的 horizon 依赖。

不要再追求“别的变量是不是都单调下降”这种大叙事。这个从文档看并不稳。
更好的做法是：

* wind：固定 horizon grid（如 h6 / h72 / h144 / h288 / h576）
* 每个 horizon 统一 clean pipeline + fixed config + seeds
* 输出两条曲线：skill、raw wind 入式率（或 wind group retention）

solar 可以只做一条控制曲线，放附录，作用只是说明“这种形状不是所有变量都一样”。

---

## 六、论文应该怎么收束

### 最适合的主标题方向

不是“新模型更强”，而是：

**teacher-guided symbolic extraction reveals differential identifiability of physical drivers in net-load forecasting**

中文理解就是：
**用 teacher-guided symbolic extraction 去看，不同物理量进入公式的难度是不一样的。**

### 主文里可以强写的结论

1. 当前系统是 **KAN teacher + post-hoc symbolic extraction**，不是经典 student distillation
2. direct net-load 路线会坍缩到 load-dominant 公式
3. focused/component teacher 能恢复可解释的 physical structure
4. solar 是稳定正例
5. wind 是否入式，不等同于 wind 是否有预测价值
6. wind 的符号可辨识性具有 horizon 依赖，而且呈非单调

### 主文里要降级的内容

1. “wind 天生特殊”
   只能写讨论，不能写成定理

2. “一切都由替代机制严格导致”
   只能写成 supported hypothesis

3. “KAN 全程优于 PySR”
   只能限定到当前 clean matched setting

4. “流程严格无泄漏”
   在 clean rerun 之前绝对不要写

### 最好的文章结构

1. **问题定义**：高精度预测不等于可解释公式
2. **方法**：KAN teacher + post-hoc symbolic extraction
3. **可靠性边界**：clean pipeline、split-aware preprocessing、evaluation setup
4. **结果一**：direct net-load collapse
5. **结果二**：solar 正例与 component/focused teacher 的必要性
6. **结果三**：wind 的隐式性、显式性与泛化张力
7. **结果四**：wind 的 horizon 依赖
8. **讨论**：变量可辨识性、替代表达、符号简洁性偏置
9. **局限性**：早期历史 run、fairness 边界、clean rerun 前后差异

---

## 七、哪些事情现在不要做

这部分很重要，因为它能帮你避免继续陷进大坑。

**不要做的事有五个：**

1. **不要为了迎合措辞去做真正的 symbolic student distillation**
   这会把题目改掉，而且会稀释当前已经成形的主线。

2. **不要继续把 direct net-load 当成要“修成功”的主角**
   它更适合作为 failure case。

3. **不要再试图证明“所有其他变量都随 horizon 下降”**
   这条从文档看不稳。

4. **不要把 KAN vs PySR 放在标题级位置**
   这是次要背景，不是论文灵魂。

5. **不要押注单条漂亮公式**
   应该押注“公式族统计”和“变量组进入频率”。

---

## 八、我建议的实际执行顺序

最后把它压成一个最实用的顺序：

### 第一步

修 clean pipeline，补环境，跑全测试，新增 split-boundary 泄漏测试。

### 第二步

重跑最小主线实验包：

* direct net-load failure baseline
* 1 条 solar 正例
* `s0p_wind_delta_h6`
* `s3_comp_wind_delta_h6`

每条至少 3 个 seeds，统一 symbolic 配置。

### 第三步

对这几条 canonical teacher 做 group ablation，补 wind 的机制证据。

### 第四步

做 wind 的固定 horizon mini-grid；solar 只留一个控制。

### 第五步

clean matched KAN vs PySR，作为次要对照；根据结果决定放主文末段还是附录。

### 第六步

开始写论文，主文只保留最强主线；历史 run、公平性边界、legacy pipeline 对比都进附录。

---

一句话收束：
**这份文档已经足够说明项目值得继续，但后续不该再“广撒网找更好的结果”，而该“收敛成一条能过审的证据链”——先修 clean pipeline，再用 direct 失败、solar 正例、wind 双反例把主线钉死，最后再用 wind 的替代性与 horizon 依赖把讨论做深。**
