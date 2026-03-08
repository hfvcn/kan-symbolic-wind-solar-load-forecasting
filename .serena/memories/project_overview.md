# graduation-design 项目概览
- 目标：用 KAN 稀疏化/剪枝与符号提取研究风光耦合负荷、多 horizon 预测与可解释公式。
- 主要流程：Phase 1 数据管道 -> Phase 1.5 派生数据集 -> Phase 2 KAN 训练 -> Phase 3 符号提取 -> Phase 4 baseline -> Phase 5+ 本地评估与论文资产生成。
- 关键目录：`src/` 为核心库，`modal_jobs/` 为云端入口，`scripts/` 为本地评估/绘图/资产工具，`runs/` 为同步下来的实验产物，`doc/` 为论文资产与分析文档。
- 论文资产集中在 `doc/paper_assets/`，批量实验 manifest 在 `doc/thesis_sweeps/*/manifest.json`。