# 中期汇报 PPT 大纲

## Governing Thought

本课题已经完成从“公式坍缩现象识别”到“自回归捷径竞争机制验证”再到“结构化分解修复”的主体研究，中期之后的重点转向论文定稿与答辩交付。

## Slide List

1. 封面
   - Pattern: `p01-cover`
   - Action title: 基于KAN的可解释净负荷预测
   - Content summary: 中期检查汇报标题、副标题、汇报场景与日期
   - Data shape: cover metadata
2. 研究框架
   - Pattern: `p07-machine`
   - Action title: 本课题围绕“物理变量为何在公式中消失”搭建了从问题识别到修复验证的四步路径
   - Content summary: 背景问题、KAN 管线、S2 阻断、S3 分解
   - Data shape: 4-step process
3. 阶段成果
   - Pattern: `p04-scorecard`
   - Action title: 核心研究工作已基本完成，并同时拿到精度、机制与可解释性三类结果
   - Content summary: 数据管线、模型精度、公式坍缩、S2 结果、S3 结果、论文状态
   - Data shape: 6 KPI cards
4. 关键证据
   - Pattern: `p03-evidence`
   - Action title: KAN 教师在精度上领先基线，但直接符号提取会坍缩为仅含滞后项的公式
   - Content summary: skill 对比图 + 三个证据侧栏
   - Data shape: bar chart + 3 callouts
5. 后续安排
   - Pattern: `p05-narrative-arc`
   - Action title: 后续工作将集中在论文定稿、图表完善与答辩准备三个收尾动作
   - Content summary: 中期后到答辩前的 4 个里程碑，并穿插当前问题
   - Data shape: 4-point timeline
6. 结论页
   - Pattern: `p08-closer`
   - Action title: 当前阶段已经完成机制验证，后续重心转向论文与答辩交付
   - Content summary: 一句总结 + 三条下一步
   - Data shape: closing statement + bullets

## Flow Test

按标题顺序阅读，完整叙事为：
基于KAN的可解释净负荷预测 -> 已形成从问题识别到修复验证的研究路径 -> 当前阶段已拿到关键结果 -> 证据表明精度提升与公式坍缩并存 -> 后续工作转入论文与答辩收尾 -> 中期目标已经实现。

该顺序可以独立讲清楚“为什么做、做到哪里、证据是什么、接下来做什么”。

## Density Check

- `p07-machine`：4 步，信息密度适中，适合 1 分钟介绍研究框架
- `p04-scorecard`：6 张卡片，适合快速过关键产出，不会过满
- `p03-evidence`：1 张柱状图 + 3 条证据，适合 1 分钟讲核心发现
- `p05-narrative-arc`：4 个里程碑，适合 40 秒说明计划
- `p08-closer`：一句总结 + 3 条收尾动作，适合 20 秒结束

## Data Sufficiency

- 封面信息：已具备
- 研究路径：可由论文与中期报告直接提炼
- 阶段成果数值：已具备
- 精度对比图：已具备 KAN / MLP / PySR 三组 skill
- 后续计划：中期报告已给出
- 风险与局限：中期报告已给出，可作为时间轴描述补充
