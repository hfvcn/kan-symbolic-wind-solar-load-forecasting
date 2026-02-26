---
phase: 07-interpretability-validation
verified: 2026-02-26T06:47:20Z
status: verified
score: "Sensitivity + physics mapping + seeded PySR cross-validation complete"
gaps: []
evidence:
  - symbolic_run_id: 2026-02-26_041718_5579aeeb
  - seeded_pysr_run_id: 2026-02-26_064508_3e631069
  - cross_validation_report: doc/paper_assets/kan_pysr_cross_validation_2026-02-26_064508_3e631069.md
  - sensitivity_outputs:
      - doc/paper_assets/sensitivity_summary_2026-02-26_041718_5579aeeb.csv
      - doc/paper_assets/sensitivity_hist_2026-02-26_041718_5579aeeb_temp_2m_c.png
      - doc/paper_assets/sensitivity_hist_2026-02-26_041718_5579aeeb_ghi_w_m2.png
      - doc/paper_assets/sensitivity_hist_2026-02-26_041718_5579aeeb_wind_speed_10m_m_s.png
  - physics_mapping_outputs:
      - doc/paper_assets/physics_mapping_2026-02-26_041718_5579aeeb.md
      - doc/paper_assets/physics_mapping_2026-02-26_041718_5579aeeb.json
---

# Phase 07 Verification

本阶段以“解释性与可信度增强”为目标：偏导敏感性 + 物理映射 + PySR 交叉验证。
已在真实实验 run 上生成论文资产并复核关键产物。

## Verified locally

- Unit tests pass:
  - `tests/test_sensitivity.py`
  - `tests/test_physics_mapping.py`
  - `tests/test_seed_features.py`

## Verified via Modal + local assets

- Seeded PySR cross-validation run: `runs/2026-02-26_064508_3e631069/`
- Cross-validation report: `doc/paper_assets/kan_pysr_cross_validation_2026-02-26_064508_3e631069.md`
