---
phase: 05-evaluation-framework-ablation
verified: 2026-02-26T06:21:29Z
status: verified
score: "Evaluation tables/plots generated under doc/paper_assets/; ablation runs completed and synced"
evidence:
  - evaluation_outputs:
      - doc/paper_assets/comparison_table.csv
      - doc/paper_assets/pareto_rmse_vs_complexity.png
      - doc/paper_assets/ASSET_INDEX.md
  - ablation_runs:
      - 2026-02-26_053425_2e4bc623  # kan_full
      - 2026-02-26_054408_f605ac11  # kan_no_entropy
      - 2026-02-26_055200_958b3949  # kan_no_l1
      - 2026-02-26_060024_d6250f56  # kan_no_magnitude
  - ablation_outputs:
      - doc/paper_assets/ablation_table.csv
      - doc/paper_assets/ablation_rmse_pruned.png
      - doc/paper_assets/ablation_rmse_vs_sparsity.png
---

# Phase 05 Verification

已完成真实实验同步与本地论文资产生成：

- 对比表/评估：`doc/paper_assets/comparison_table.csv`
- Pareto 图：`doc/paper_assets/pareto_rmse_vs_complexity.png`
- 消融研究：
  - 表格：`doc/paper_assets/ablation_table.csv`
  - 图：`doc/paper_assets/ablation_rmse_pruned.png`, `doc/paper_assets/ablation_rmse_vs_sparsity.png`
