---
phase: 03-symbolic-expression-extraction
plan: 01
completed: 2026-02-25
status: complete
---

# Phase 03 Plan 01 Summary: Symbolic Extraction Pipeline

- 新增 `src/kan_sr/symbolic.py`：
  - `extract_symbolic_edges()`：逐边调用 `suggest_symbolic()`，可选 fix_symbolic
  - `build_symbolic_formula()`：生成 SymPy 表达式，并支持输入/输出反归一化
  - `sympy_complexity()`：输出论文可用的复杂度指标
  - `evaluate_symbolic_formula()`：在 DataFrame 上矢量化评估表达式
- 新增 Modal 作业 `modal_jobs/kan_symbolic.py`：
  - 输入 Phase 2 `checkpoint/model.pt`
  - 解析 payload 找到 Phase 1 `scaler_params.json`，用于把公式恢复到原始物理量尺度
  - 输出 per-edge 报告、公式文本/LaTeX、复杂度、test 上指标
- 新增 `tests/test_symbolic_extraction.py`：合成线性函数可恢复，RMSE < 0.05

