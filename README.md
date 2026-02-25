# graduation-design
*注意：本课题要求在Github中开源代码。
在能源领域，准确预测风力和光伏发电的耦合负荷对于电网的稳定运行和智能调度至关重要。与区块链风险检测类似，负荷预测模型也需要高度的可解释性，以便电力工程师理解和信任预测结果。本课题将符号回归应用于风光耦合负荷预测，旨在发现影响负荷变化的潜在物理规律和关键因素（如风速、光照强度、温度、历史负荷等）之间的内在数学关系。通过生成可解释的数学模型，本研究不仅追求预测精度，更致力于揭示能源系统的运行机理，为可再生能源的高效消纳提供理论依据。

## Modal 运行产物同步到本地

本项目的训练/基线/评估通常在 Modal 上运行，运行产物先落到 Modal Volume（持久化存储），再同步到本地 `runs/` 目录（不提交到 Git）。

详细约定见：`/Users/vfch/Documents/project/graduation-design/MODAL.md`

### Modal 功能自检（Smoke Test）

```bash
# 运行一次 CPU + Volume + 重试 + fanout 的自检
modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/smoke_test.py

# 可选：如果你的账号有 GPU 权限，额外跑 GPU 探测
modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/smoke_test.py --with-gpu
```

```bash
# 1) 查看远端 runs 列表
/Users/vfch/Documents/project/graduation-design/scripts/sync_from_modal.sh ls

# 2) 同步最新一次 run 到本地 /Users/vfch/Documents/project/graduation-design/runs/
/Users/vfch/Documents/project/graduation-design/scripts/sync_from_modal.sh latest

# 3) 同步指定 run（run_id 为远端目录名）
/Users/vfch/Documents/project/graduation-design/scripts/sync_from_modal.sh 2026-02-25_001
```
