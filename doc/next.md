修改配置（只改这一个文件）：experiment_driver.py
把顶部 CONFIG 区域改成下面这样（直接覆盖对应变量即可）：

DATA_RUN_ID = "2026-02-26_032058_1957fda1"
RUN_DATA_PIPELINE = False

RUN_DERIVED_DATASET = True
DERIVED_DATASET = {
    "degree_base_c": 18.0,
    "net_load_lag_steps": "1,12,24,48",
    "add_physics_proxies": True,
}

EXISTING_KAN_TRAIN_RUN_IDS = []

KAN_TRAIN_SWEEP = [
    {
        "name": "kan_delta_load_slow_lags",
        "target": "delta_load",
        "use_gpu": False,
        "hidden_width": 10,
        "hidden_mult": 0,
        "mult_arity": 2,
        "warmup_steps": 400,
        "sparsify_steps": 1600,
        "refine_steps": 400,
        "sparsify_lamb": 0.005,
        "sparsify_lamb_l1": 0.5,
        "sparsify_lamb_entropy": 1.0,
        "max_train_rows": 0,
        "include_base": False,
        "include_groups": "meteorology,solar,cyclic",
        "lag_series": "load",
        "lag_steps": "12,24,48",
    },
    {
        "name": "kan_delta_net_load_physics",
        "target": "delta_net_load",
        "use_gpu": False,
        "hidden_width": 10,
        "hidden_mult": 0,
        "mult_arity": 2,
        "warmup_steps": 400,
        "sparsify_steps": 1600,
        "refine_steps": 400,
        "sparsify_lamb": 0.005,
        "sparsify_lamb_l1": 0.5,
        "sparsify_lamb_entropy": 1.0,
        "max_train_rows": 0,
        "include_base": False,
        "include_groups": "meteorology,solar,cyclic",
        "lag_series": "net_load",
        "lag_steps": "12,24,48",
    },
]

KAN_SYMBOLIC_SWEEP = [
    {"name": "sym_r2_0.92_interp", "r2_threshold": 0.92, "weight_simple": 0.9, "fix_below_threshold_to_zero": False, "sample_rows": 20000, "lib": "x,x^2,x^3,sin,cos,abs"},
    {"name": "sym_r2_0.88_interp", "r2_threshold": 0.88, "weight_simple": 0.85, "fix_below_threshold_to_zero": False, "sample_rows": 20000, "lib": "x,x^2,x^3,sin,cos,abs"},
]

RUN_TORCH_BASELINES = False
RUN_PYSR_BASELINE = False
RUN_LOCAL_EVAL = True
BUILD_ASSET_INDEX = True
接下来要运行的指令（按顺序执行）
cd /Users/vfch/Documents/project/graduation-design

python3 scripts/experiment_driver.py --dry-run --phases data,train,symbolic,local
python3 scripts/experiment_driver.py --execute --phases data,train,symbolic,local
跑完后看结果（不需要再手工跑评估，driver 已自动做）
表格：comparison_table.csv（重点看 rmse_persistence、skill_score）
索引：ASSET_INDEX.md
（如果后续不想每次都重新派生数据集：把 RUN_DERIVED_DATASET=False，并把 DATA_RUN_ID 改成上一轮 manifest.json 里的 derived_data_run_id。）


