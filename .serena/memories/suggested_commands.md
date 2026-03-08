# 常用命令
- 运行全量测试：`python3 -m unittest discover -s tests -p 'test_*.py'`
- 生成主结果表/季节分解/Pareto：`python3 scripts/evaluate_runs.py --run runs/<id1> --run runs/<id2> ...`
- delta -> abs 重建：`python3 scripts/reconstruct_predictions.py --run runs/<run_id>`
- Solar 机制汇总：`python3 scripts/summarize_solar_ablation.py --run <run1> --run <run2> ...`
- Wind 机制汇总：`python3 scripts/summarize_wind_ablation.py --run <run1> --run <run2> ...`
- Solar 边界诊断：`python3 scripts/diagnose_solar_bounds.py --run <run_id>`
- 生成资产索引：`python3 scripts/build_asset_index.py`
- 从 Modal 同步 run：`scripts/sync_from_modal.sh <run_id>` 或 `scripts/sync_from_modal.sh latest`
- 论文导向 sweep：`python3 scripts/thesis_sweep_driver.py --source-data-run-id <phase1_run_id> --execute --use-gpu`