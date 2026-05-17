# 任务完成时的检查
- 若涉及评估表或论文图表，确认使用了 `predictions_test_reconstructed.parquet`，避免 delta/abs 混用。
- 运行 `python3 -m unittest discover -s tests -p 'test_*.py'` 做基础回归验证。
- 若新增或更新论文资产，重建 `doc/paper_assets/ASSET_INDEX.md`。
- 若依赖具体 run，尽量把 run_id、命令和产物路径写入文档或索引，保证可追溯。
- 如有多步骤任务，维护 `.codex-tasks/` 中的 SPEC/TODO/PROGRESS 以便上下文恢复。