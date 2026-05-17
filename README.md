# KAN-SR：基于KAN的风光耦合负荷可解释符号回归预测

利用Kolmogorov-Arnold网络（KAN）进行风光耦合负荷的可解释符号回归预测。本项目通过结构化分解方法，发现气象因子（风速、太阳辐照、温度）与净负荷变化之间的数学关系。

## 主要贡献

1. **自回归捷径竞争机制**：发现并通过干预实验验证了滞后特征在KAN稀疏化过程中系统性压制物理变量的现象
2. **VER/FAR诊断指标**：提出用于度量符号公式中物理变量可辨识性的定量指标
3. **DS-KAN结构化分解方案**：先分解再符号化的方法，在保持预测精度的同时恢复物理可解释性
4. **33种方法系统对比**：在找到最终方案前，系统测试了33种不同方法/配置，揭示了精度-可读性-物理含义的三难困境
5. **DS-KAN + PySR两阶段流水线**：DS-KAN作为特征选择器 + PySR作为公式搜索器，是唯一同时突破三难困境的方法

## 最终结果

三条h72子公式（DS-KAN分解 + 纯净特征 + PySR搜索）：

| 子任务 | 公式 | R² | 变量数 |
|--------|------|-----|--------|
| Load | `107/85·lag_12 − 107/85·lag_48 + hour_sin·lag_48·(2/37·month_cos + 2/37·sin(sin(hour_cos)) − 224/3071)` | 0.887 | 5 |
| Solar | `lag_1 + (azimuth − 123.5)·(−0.258·azimuth + (lag_48 − altitude)·(exp(−40.49·lag_48) − 0.004) − 20.4)` | 0.888 | 4 |
| Wind | `91/73·lag_1 − 101/86·lag_48 + 101/86·exp(743/85·hour_sin) − 197907/85` | 0.890 | 3 |

三公式组合净负荷：**RMSE=5719, R²=0.868**，在所有纯公式方法中排名第一，超过XGBoost（R²=0.848）和DS-KAN KAN组合（R²=0.816），仅次于MLP（R²=0.892）和Direct KAN（R²=0.887）。

## 完整实验流水线

```
阶段1 数据协议        →  阶段2 KAN验证       →  阶段3 Direct诊断
  §1 泄漏探测              §2 六基线对比            §4 λ消融
  数据切分可信性            KAN预测能力验证          §5 特征消融
                                                    §7 符号化失败筛查

→  阶段4 DS-KAN分解     →  阶段5 多步长选域    →  阶段6 特征筛选
     §6 子任务分解            §9 h12/72/144/576      §14 跨种子稳定性
     Load/Solar/Wind          Wind h72 R²=0.757      纯净特征集确定
                              转向h72

→  阶段7 PySR搜索       →  阶段8 后处理
     §26 纯净特征PySR         §27 snap+BFGS+simplify
     3-5变量简洁公式          最终交付公式
```

## 项目结构

```
kan-sr/
├── src/                    # 核心库
│   ├── config.py           # 集中配置（数据源、切分比例、Modal路径）
│   ├── data/               # 数据管道
│   │   ├── download.py     #   ARPA-E PERFORM S3匿名下载
│   │   ├── preprocess.py   #   缺失值插值、质量报告
│   │   ├── features.py     #   滞后特征、周期编码、太阳角
│   │   ├── meteorology.py  #   Open-Meteo气象代理特征
│   │   ├── derived.py      #   净负荷、delta目标、物理代理
│   │   ├── split.py        #   时序切分（70/15/15 + 48步gap防泄漏）
│   │   └── rolling_origin.py
│   ├── kan_sr/             # KAN符号回归核心
│   │   ├── dataset.py      #   数据集构建与z-score归一化
│   │   ├── symbolic.py     #   KAN→符号公式提取（auto_symbolic）
│   │   ├── prune.py        #   多轮渐进剪枝（edge_th扫描）
│   │   ├── sparsity.py     #   L1+熵正则化稀疏化训练
│   │   ├── sensitivity.py  #   公式变量敏感性分析
│   │   ├── separability.py #   变量可分离性检测
│   │   ├── feature_scaling.py
│   │   ├── formula_quality.py
│   │   └── metrics.py      #   VER/FAR/TGR/skill等指标
│   ├── models/             # S2KAN架构（训练时符号集成）
│   │   ├── s2kan.py        #   S2KAN核心：符号原语字典 + B-spline + 门控
│   │   ├── s2kan_gam.py    #   加性GAM变体
│   │   ├── s2kan_bottleneck.py  # 瓶颈压缩变体
│   │   └── s2kan_masked.py #   物理字典约束变体
│   ├── baselines/          # 基线模型
│   │   ├── torch_models.py #   MLP、LSTM
│   │   ├── torch_training.py
│   │   ├── statistical_models.py  # SARIMAX
│   │   └── tree_models.py  #   XGBoost
│   ├── eval/               # 评估与分析
│   │   ├── runs.py         #   run产物加载与指标提取
│   │   ├── physics_mapping.py  # 公式物理含义评分
│   │   ├── paired_significance.py  # Wilcoxon配对检验
│   │   ├── seed_stability.py   # 跨种子特征重叠度
│   │   ├── case4_matched.py    # S2阻断实验配对评估
│   │   ├── reconstruction.py   # delta→绝对值重建
│   │   └── formula_contribution.py
│   ├── local/              # 本地执行作业（与modal_jobs对应的纯Python实现）
│   │   ├── kan_train_job.py    # KAN训练全流程
│   │   ├── kan_symbolic.py     # 符号提取
│   │   ├── baseline_torch_job.py
│   │   ├── s2kan_job.py        # S2KAN训练
│   │   ├── s2kan_*_job.py      # 各S2KAN变体（10种压缩方案）
│   │   └── hybrid_kan_ann_job.py  # Hybrid KAN-ANN复现
│   └── thesis_sweep/       # 论文实验协议框架
│       ├── cli.py          #   统一命令行入口
│       ├── plan_kan.py     #   KAN训练sweep规划
│       ├── plan_rq_experiments.py  # RQ实验矩阵生成
│       ├── kan_67_execution.py    # 中间态搜索网格执行
│       └── postprocess.py  #   结果聚合与论文资产生成
├── modal_jobs/             # Modal云计算作业定义（27个文件）
│   ├── data_pipeline.py    #   Phase 1：ERCOT数据下载与预处理
│   ├── derive_dataset.py   #   Phase 1.5：派生数据集
│   ├── kan_train.py        #   Phase 2：KAN训练
│   ├── kan_symbolic.py     #   Phase 3：符号提取
│   ├── baseline_torch.py   #   Phase 4：MLP/LSTM基线
│   ├── baseline_non_torch.py   # XGBoost/SARIMAX基线
│   ├── pysr_baseline.py    #   PySR符号回归
│   ├── s2kan_train.py      #   S2KAN训练
│   ├── s2kan_*.py          #   S2KAN各压缩方案（13个变体）
│   ├── hybrid_kan_ann.py   #   Hybrid KAN-ANN
│   └── combine_net_load_runs.py  # 子任务组合
├── scripts/                # 工具脚本
│   ├── experiment_driver.py    # 一键实验驱动（Phase 1→5全流程）
│   ├── thesis_sweep_driver.py  # 论文sweep驱动（S0-S3全覆盖）
│   ├── sync_from_modal.sh      # Modal Volume产物同步到本地
│   ├── reconstruct_predictions.py  # delta→绝对值重建
│   ├── evaluate_runs.py        # 多run对比表 + Pareto图
│   ├── combine_net_load_runs.py    # Load+Wind+Solar→NetLoad组合
│   ├── postprocess_formula.py  # KAN-SR风格后处理（snap+BFGS+simplify）
│   ├── sensitivity_analysis.py # 公式变量敏感性
│   ├── physics_mapping.py      # 物理含义评分
│   ├── paired_significance.py  # 统计显著性检验
│   └── submit_*.sh             # Modal作业提交脚本
├── tests/                  # 测试（40+文件）
├── pyproject.toml          # Python包定义
├── requirements.txt        # 依赖
└── LICENSE                 # MIT
```

## 快速开始

### 环境要求

- Python >= 3.9
- [Modal](https://modal.com/) 账号（用于云端训练，`modal setup` 初始化）

### 安装

```bash
git clone https://github.com/hfvcn/kan-symbolic-wind-solar-load-forecasting.git
cd kan-symbolic-wind-solar-load-forecasting
pip install -e ".[dev,modal]"
```

### 功能自检

```bash
# Modal连通性自检
modal run modal_jobs/smoke_test.py

# 本地单元测试
pytest tests/
```

## 复现全流程

### Phase 1：数据管道

从ARPA-E PERFORM公开S3存储桶下载ERCOT 2018年风/光/负荷5分钟级实际值，完成缺失值插值、气象代理特征（Open-Meteo温度/GHI/风速/气压）、周期编码、太阳角、48步滞后特征，按70/15/15时序切分（48步gap防泄漏），z-score仅拟合训练集。

```bash
modal run modal_jobs/data_pipeline.py --year 2018 --iso ERCOT
```

### Phase 1.5：派生数据集

生成净负荷（net_load = load − wind − solar）、多步差分目标（delta_*_h6/h12/h24/h72）、物理代理特征（wind_speed_cubed、ghi_day、cdd_18c、hdd_18c）：

```bash
modal run modal_jobs/derive_dataset.py \
  --source-data-run-id <phase1_run_id> \
  --horizon-steps 1,6,12,24,72 \
  --add-physics-proxies \
  --net-load-lag-steps 1,12,48 \
  --degree-base-c 18
```

### Phase 2：KAN训练（Direct KAN + DS-KAN子任务）

```bash
# Direct KAN（净负荷直接预测，用于基线对比和公式坍缩诊断）
modal run modal_jobs/kan_train.py \
  --data-run-id <derived_run_id> \
  --target delta_net_load_h6 \
  --hidden-width 24 --no-include-base --use-gpu

# DS-KAN子任务（结构化分解：拆成Load/Solar/Wind分别训练）
# Load子任务
modal run modal_jobs/kan_train.py \
  --data-run-id <derived_run_id> \
  --target delta_load_h72 \
  --hidden-width 10 \
  --include-groups cyclic,meteo_degree \
  --lag-series load --lag-steps 1,12,48 \
  --no-include-base --use-gpu

# Solar子任务
modal run modal_jobs/kan_train.py \
  --data-run-id <derived_run_id> \
  --target delta_solar_h72 \
  --hidden-width 10 \
  --include-groups meteo_irradiance,solar_geom,solar_flag \
  --lag-series solar --lag-steps 1,12,48 \
  --no-include-base --use-gpu

# Wind子任务
modal run modal_jobs/kan_train.py \
  --data-run-id <derived_run_id> \
  --target delta_wind_h72 \
  --hidden-width 24 \
  --include-groups cyclic,meteo_wind \
  --lag-series wind --lag-steps 1,12,48 \
  --no-include-base --use-gpu
```

### Phase 3：符号提取（KAN auto_symbolic）

```bash
modal run modal_jobs/kan_symbolic.py \
  --train-run-id <kan_train_run_id> \
  --r2-threshold 0.98 \
  --lib-csv x,x^2,x^3,sin,cos,abs \
  --use-gpu
```

### Phase 4：基线实验

```bash
# Persistence（持续性基线，RMSE即为预测难度的下界参照）
# 由evaluate_runs.py自动计算

# MLP（匹配KAN的特征列和训练预算）
modal run modal_jobs/baseline_torch.py \
  --data-run-id <derived_run_id> \
  --model-type mlp --target delta_net_load_h72 \
  --match-kan-run-id <kan_train_run_id> \
  --sync-kan-feature-cols --sync-kan-budget --use-gpu

# LSTM
modal run modal_jobs/baseline_torch.py \
  --data-run-id <derived_run_id> \
  --model-type lstm --target delta_net_load_h72 \
  --match-kan-run-id <kan_train_run_id> \
  --sync-kan-feature-cols --sync-kan-budget --use-gpu

# XGBoost / SARIMAX
modal run modal_jobs/baseline_non_torch.py \
  --data-run-id <derived_run_id> \
  --model-type xgboost --target delta_net_load_h72

# PySR（28维全特征直接搜索 vs DS-KAN分解后纯净特征搜索）
# 28维全特征（预期R²≈0.665，搜索空间爆炸）
modal run modal_jobs/pysr_baseline.py \
  --data-run-id <derived_run_id> \
  --target delta_net_load_h72

# DS-KAN分解后纯净特征（预期R²≈0.87-0.89）
modal run modal_jobs/pysr_baseline.py \
  --data-run-id <derived_run_id> \
  --target delta_load_h72 \
  --include-groups cyclic,meteo_degree \
  --lag-series load --lag-steps 1,12,48
```

### Phase 5：结果同步与评估

```bash
# 同步Modal Volume产物到本地
scripts/sync_from_modal.sh ls          # 查看远端runs列表
scripts/sync_from_modal.sh latest      # 同步最新run
scripts/sync_from_modal.sh <run_id>    # 同步指定run

# delta→绝对值重建（便于论文图表对比）
python scripts/reconstruct_predictions.py --run runs/<run_id>

# 多模型对比表 + Pareto图
python scripts/evaluate_runs.py --run runs/<id1> --run runs/<id2> ...

# S3结构化组合：Load + Wind + Solar → NetLoad
python scripts/combine_net_load_runs.py \
  --load-run runs/<load_id> \
  --wind-run runs/<wind_id> \
  --solar-run runs/<solar_id> \
  --out-run-id <combo_id>

# 公式后处理（snap近整数 + 有理化 + BFGS常数重优化 + SymPy化简）
python scripts/postprocess_formula.py --run runs/<symbolic_run_id>

# 敏感性分析与物理映射
python scripts/sensitivity_analysis.py --symbolic-run runs/<sym_id>
python scripts/physics_mapping.py --symbolic-run runs/<sym_id>
```

### 一键实验驱动

```bash
# 试运行（只打印将执行的命令）
python scripts/experiment_driver.py --dry-run

# 执行完整流程（Phase 1 → 5）
python scripts/experiment_driver.py --execute

# 论文导向sweep（覆盖S0-S3全实验矩阵）
python scripts/thesis_sweep_driver.py \
  --source-data-run-id <phase1_run_id> \
  --execute --use-gpu
```

## 关键实验说明

### 为什么不直接用PySR搜索28维全特征？

PySR在28维全特征上搜索空间爆炸（h6 R²=0.367, h72 R²=0.665）。经DS-KAN分解 + 特征筛选降至9-12维后，同一PySR算法R²跃升到0.87-0.89。**DS-KAN的核心价值不在于直接出公式，而在于为下游PySR做任务分解和特征筛选。**

### 为什么从h6转向h72？

h6（30分钟）下delta被高频噪声主导，48个符号提取run全部R²<0.1。多步长实验发现Wind在h72达到R²=0.757（h6时≈0），Solar在h72达到R²=0.901。h72的中期天气信号更适合KAN学习和符号提取。

### Wind为什么最难？

Wind在所有方法中都是最难的子任务：DS-KAN公式physics_score=0，short-lag R²=0.987但纯粹是lag复制。最终PySR c=18是整个实验体系中唯一包含v³风功率物理项的可读Wind公式。

## 数据来源

[ARPA-E PERFORM](https://arpa-e.energy.gov/technologies/programs/perform) 数据集（公开S3存储桶 `arpa-e-perform`，匿名访问，无需API密钥）。

## 测试

```bash
pytest tests/
```

## 许可证

[MIT](LICENSE)
