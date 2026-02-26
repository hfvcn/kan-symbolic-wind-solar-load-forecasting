# Phase 1: Data Pipeline & Infrastructure - Context

**Gathered:** 2025-02-25
**Status:** Ready for planning

<domain>
## Phase Boundary

构建基础设施以获取、预处理ARPA-E PERFORM ERCOT风光负荷数据，并将其持久化为ML可用的张量。包含数据下载、清洗、特征工程、时序切分，以及Modal Volume存储。不包含模型训练或评估。

</domain>

<decisions>
## Implementation Decisions

### 缺失数据处理
- 短时间缺失（<1小时）：遵循ARPA-E PERFORM数据集原有约定，由Claude根据数据特性自行决定插值方法
- 长时间缺失（>6小时）：由Claude根据具体情况决定（剔除、邻近插值等）
- 数据质量日志：生成详细日志，记录所有缺失数据的位置和处理方式，方便论文描述
- 异常值：不做处理，保留原始数据，但在日志中标记以便后续决策

### 特征工程
- 自回归滞后窗口：t-1到t-48（4小时，48个时间步，5分钟分辨率）
- 归一化策略：全部特征使用Z-score标准化
- 周期性时间特征：使用三角函数编码（sin/cos）处理小时、星期、月份
- 气象变量选择：由Claude根据数据集实际可用变量决定

### 管道行为
- 幂等性：管道可重入，再次运行时跳过已完成步骤
- 错误恢复：失败时回滚，清理部分输出，下次重试
- 日志详细程度：运行时精简输出（进度条+摘要），完成后生成详细报告
- 检查点策略：每个处理步骤都保存中间结果

### 存储与制品
- 存储层级：仅使用Modal Volume，不使用S3，简化架构
- 文件格式：特征数据用Parquet，元数据用JSON
- 版本管理：使用时间戳命名（data_20250225_143000.parquet）
- 本地同步：自动同步到本地runs/目录，方便查看和调试

### Claude's Discretion
- 具体插值算法选择
- 气象变量的具体选择（根据数据集实际内容）
- 长时间缺失的具体处理策略
- 进度条和报告的具体样式

</decisions>

<specifics>
## Specific Ideas

- 详细日志是为了论文可以准确描述数据预处理过程
- 异常值保留而非删除，因为可能需要在后续分析中了解数据分布
- 幂等设计是为了方便调试和迭代开发
- 每步保存中间结果便于排查问题和复现

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-data-pipeline-infrastructure*
*Context gathered: 2025-02-25*
