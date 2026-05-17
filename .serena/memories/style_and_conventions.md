# 风格与约定
- 语言栈：Python 3，数据处理大量使用 pandas / numpy，测试使用 `unittest`。
- 代码倾向：小函数、显式报错、路径用 `pathlib.Path`、通过 `payload.json`/run 契约推断 phase/kind/target。
- 评估口径：delta 目标优先重建到 abs(test) 后再做主表与公平对比；`predictions_test_reconstructed.parquet` 优先于 `predictions_test.parquet`。
- 运行契约：每个 run 目录通常有 `payload.json` 与 `artifacts/`，Phase 2/3/4/5 的脚本都围绕这一契约工作。
- 用户约束：不要引入静默 fallback，不要伪造成功路径；论文文档里的 claim 必须绑定 run 或资产证据。