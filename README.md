# KAN-SR：基于KAN的风光耦合负荷可解释符号回归预测

利用Kolmogorov-Arnold网络（KAN）进行风光耦合负荷的可解释符号回归预测。本项目通过结构化分解方法，发现气象因子（风速、太阳辐照、温度）与净负荷变化之间的数学关系。

## 主要贡献

1. **自回归捷径竞争机制**：发现并通过实验验证了滞后特征在KAN稀疏化过程中系统性压制物理变量的现象
2. **VER/FAR诊断指标**：提出用于度量符号公式中物理变量可辨识性的定量指标
3. **S3结构化分解方案**：先分解再符号化的方法，在保持预测精度的同时恢复物理可解释性
4. **边界分析**：系统研究风电低符号可辨识性及其与预测时域的非单调依赖关系

## 项目结构

```
kan-sr/
├── src/                    # 核心库
│   ├── config.py           # 集中配置
│   ├── data/               # 数据管道（下载、预处理、派生）
│   ├── kan_sr/             # KAN训练、剪枝、符号提取
│   ├── models/             # S2KAN架构变体
│   ├── baselines/          # MLP、LSTM、XGBoost、SARIMAX基线
│   ├── eval/               # 评估指标、物理映射、显著性检验
│   ├── local/              # 本地执行作业实现
│   └── thesis_sweep/       # 实验协议框架
├── modal_jobs/             # Modal云计算作业定义
├── scripts/                # 工具脚本与实验提交
├── tests/                  # 单元测试与集成测试
└── requirements.txt        # Python依赖
```

## 快速开始

### 环境要求

- Python >= 3.9
- [Modal](https://modal.com/) 账号（用于云端训练）

### 安装

```bash
git clone https://github.com/hfvcn/graduation-design.git
cd graduation-design
pip install -e ".[dev,modal]"
```

### 数据管道（Phase 1）

下载 ARPA-E PERFORM ERCOT 风/光/负荷实际值并生成特征：

```bash
modal run modal_jobs/data_pipeline.py --year 2018 --iso ERCOT
```

### 派生数据集（Phase 1.5）

生成净负荷、差分目标和物理代理特征：

```bash
modal run modal_jobs/derive_dataset.py \
  --source-data-run-id <data_run_id> \
  --horizon-steps 1,6,12,24 \
  --add-physics-proxies \
  --net-load-lag-steps 1,12,48 \
  --degree-base-c 18
```

### KAN训练（Phase 2）

```bash
modal run modal_jobs/kan_train.py \
  --data-run-id <data_run_id> \
  --target delta_net_load_h6 \
  --use-gpu
```

### 符号提取（Phase 3）

```bash
modal run modal_jobs/kan_symbolic.py \
  --train-run-id <kan_train_run_id> \
  --use-gpu
```

### 基线实验（Phase 4）

```bash
# MLP / LSTM
modal run modal_jobs/baseline_torch.py \
  --data-run-id <data_run_id> --model-type mlp --target delta_net_load_h6

# PySR 符号回归
modal run modal_jobs/pysr_baseline.py \
  --data-run-id <data_run_id> --target delta_net_load_h6
```

### 同步结果

```bash
# 查看远端 runs 列表
scripts/sync_from_modal.sh ls

# 同步最新 run 到本地 runs/ 目录
scripts/sync_from_modal.sh latest
```

### 本地评估（Phase 5+）

```bash
# 从差分预测重建绝对值
python scripts/reconstruct_predictions.py --run runs/<run_id>

# 生成对比表和图表
python scripts/evaluate_runs.py --run runs/<id1> --run runs/<id2>

# S3 结构化组合
python scripts/combine_net_load_runs.py \
  --load-run runs/<load_id> \
  --wind-run runs/<wind_id> \
  --solar-run runs/<solar_id> \
  --out-run-id <combo_id>
```

## 实验驱动

批量实验使用集成驱动脚本：

```bash
# 试运行（只打印命令不执行）
python scripts/experiment_driver.py --dry-run

# 执行完整流程
python scripts/experiment_driver.py --execute
```

## 数据来源

本项目使用 [ARPA-E PERFORM](https://arpa-e.energy.gov/technologies/programs/perform) 数据集（公开S3存储桶，匿名访问，无需API密钥）。

## 测试

```bash
pytest tests/
```

## 许可证

[MIT](LICENSE)
