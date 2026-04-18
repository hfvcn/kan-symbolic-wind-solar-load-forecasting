# 中期报告汇报 — Deck Outline

**Governing thought:** KAN符号提取中存在自回归捷径竞争机制，结构化分解方案可在保持预测精度的同时恢复物理变量的可辨识性。

## Slide List

| # | Action Title | Pattern | Content Summary |
|---|---|---|---|
| 1 | 封面 | p01-cover | 论文标题、学生信息、日期 |
| 2 | 研究背景与问题 | c04-facts-perspectives | 左列：新能源并网→净负荷预测需求→KAN可解释优势；右列：公式坍缩问题→核心科学问题 |
| 3 | 研究目标：四幕式递进框架 | p07-machine | 4步：基线构建→坍缩诊断→因果干预→结构化分解 |
| 4 | 数据与特征工程 | p04-scorecard | ARPA-E数据集、4类26维特征、数据划分 |
| 5 | S1：KAN预测精度优于基线 | p03-evidence | 柱状图：KAN vs MLP vs PySR vs Persistence，skill score对比 |
| 6 | 核心发现：公式坍缩与捷径竞争 | p09-data-table | 3×3网格搜索全部坍缩，VER=0/9 |
| 7 | S2：自回归阻断实验证实竞争机制 | p03-evidence | 柱状图显示delta-VER提升，CI区间 |
| 8 | S3：结构化分解方案 | p04-scorecard | 3个子模型性能 + 复合模型 + FAR=3/3 |
| 9 | 当前进度与存在问题 | c04-facts-perspectives | 左列：5项已完成工作；右列：3项待解决问题 |
| 10 | 结论与下一步工作 | p08-closer | 核心贡献总结 + 后续计划 |

## Flow Test
封面 → 背景问题 → 研究目标 → 数据准备 → 精度基线 → 核心发现 → 因果验证 → 解决方案 → 当前进度 → 总结展望
(完整的"发现问题→分析原因→解决问题"叙事弧)

## Density Check
- L1-L2 Structured: 学术中期汇报，适度密度
- 每张幻灯片内容充实但不拥挤，5分钟汇报节奏 ~30s/slide
