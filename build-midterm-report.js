const { createDeck } = require('/Users/vfch/.claude/skills/deck-design-ppt/masters');

createDeck('consulting-mckinsey', [

  // ── Slide 1: Cover ──
  {
    pattern: 'p01-cover',
    data: {
      title: '基于KAN的可解释净负荷预测：\n自回归捷径竞争机制与结构化分解方案',
      subtitle: '毕业设计中期报告',
      scope: 'Interpretable Net Load Forecasting Based on KAN: Autoregressive Shortcut Competition & Structured Decomposition',
      org: '华北电力大学',
      date: '2026年4月',
    },
  },

  // ── Slide 2: Background & Problem ──
  {
    pattern: 'c04-facts-perspectives',
    data: {
      sectionTag: '研究背景',
      title: '新能源高渗透率要求净负荷预测兼具精度与可解释性，但KAN符号提取面临"公式坍缩"难题',
      facts: {
        bullets: [
          '新能源并网比例持续攀升，净负荷（总负荷−风电−光伏）波动性大幅增加，精准预测是电力系统安全运行的关键',
          'KAN (Kolmogorov-Arnold Network) 通过B样条可学习边函数，提供"先学习后提取"的符号回归路径，兼具精度与可解释性',
          '然而实验发现：当输入包含自回归滞后特征时，KAN符号提取会系统性地消除所有气象物理变量',
          '3×3网格搜索（3候选库×3阈值）下9/9配置均坍缩为纯滞后公式，VER(any_physical)=0/9',
        ],
      },
      perspectives: {
        bullets: [
          '核心科学问题：物理变量消失究竟是因为"变量无关"还是"自回归捷径竞争"？',
          '现有文献缺乏对此机制的因果分析与量化诊断方法',
          '需要设计干预实验验证竞争假说，并提出恢复可辨识性的解决方案',
        ],
        implication: '如果是捷径竞争而非变量无关，则可通过结构化分解打破竞争，同时保持预测精度',
      },
      source: 'ARPA-E PERFORM Dataset, ERCOT 2018',
    },
  },

  // ── Slide 3: Research Objectives — Four-Act Framework ──
  {
    pattern: 'p07-machine',
    data: {
      sectionTag: '研究目标',
      title: '四幕式递进研究框架：从基线构建到结构化分解',
      subtitle: '每一步仅改变输入特征与任务结构，不修改KAN算法本身',
      steps: [
        {
          num: 'S0',
          title: '基线构建 — KAN教师模型训练',
          description: '4阶段训练流程（预热→稀疏化→剪枝→符号拟合），构建预测精度基线',
        },
        {
          num: 'S1',
          title: '坍缩诊断 — VER/FAR可辨识性指标',
          description: '提出VER（变量出现率）/FAR（公式充分率）/TGR（目标捕获率）诊断体系，量化公式坍缩现象',
        },
        {
          num: 'S2',
          title: '因果干预 — 自回归阻断实验',
          description: '移除自回归滞后特征，观察气象变量能否重新进入符号公式，验证"捷径竞争"假说',
        },
        {
          num: 'S3',
          title: '结构化分解 — 子任务独立建模',
          description: '将净负荷分解为负荷/风电/光伏三个子任务，各配任务专属特征，打破竞争实现精度+可解释统一',
        },
      ],
      conclusion: '设计原则：全部干预仅通过输入特征与任务结构实现，KAN算法保持不变 → 结论具有方法论通用性',
    },
  },

  // ── Slide 4: Data & Features ──
  {
    pattern: 'p04-scorecard',
    data: {
      sectionTag: '数据与特征工程',
      title: 'ARPA-E PERFORM数据集：4类26维特征，覆盖时间编码、太阳几何、气象物理与自回归信息',
      cards: [
        {
          label: '数据集规模',
          value: '~105K',
          trend: 'ERCOT 2018, 5分钟采样',
          benchmark: '60/20/20 训练/验证/测试',
          statusColor: '3A8F5C',
        },
        {
          label: '周期编码',
          value: '6维',
          trend: 'hour_sin/cos, month_sin/cos, dow_sin/cos',
          benchmark: '时间节律信息',
          statusColor: '3A8F5C',
        },
        {
          label: '太阳几何',
          value: '3维',
          trend: 'solar_elevation, azimuth, zenith',
          benchmark: '光伏出力物理驱动',
          statusColor: '3A8F5C',
        },
        {
          label: '气象物理',
          value: '10维',
          trend: 'GHI, 风速, 温度, 气压, 度日等',
          benchmark: '核心可解释变量',
          statusColor: 'D4A843',
        },
        {
          label: '自回归滞后',
          value: '9维',
          trend: 'lag_12/24/48 × 负荷/风/光',
          benchmark: '自相关 > 0.95',
          statusColor: 'B66A5C',
        },
        {
          label: '预测视野',
          value: '3个',
          trend: 'h=6 (30min), 12 (1hr), 24 (2hr)',
          benchmark: '差分目标 Δnet_load',
          statusColor: '3A8F5C',
        },
      ],
      assessment: '关键张力：自回归滞后特征自相关>0.95，方差占净负荷主导地位 → 为后续捷径竞争现象埋下伏笔',
      source: 'ARPA-E PERFORM Dataset, ERCOT 2018, 5-min resolution',
    },
  },

  // ── Slide 5: S1 — KAN Accuracy Baseline ──
  {
    pattern: 'p03-evidence',
    data: {
      sectionTag: 'S0 — 基线结果',
      title: 'KAN教师模型预测精度显著优于MLP和PySR，建立可靠基线',
      chart: {
        type: 'bar',
        series: [
          {
            name: 'Skill Score',
            labels: ['KAN', 'MLP', 'PySR', 'Persistence'],
            values: [0.453, 0.430, 0.076, 0.000],
          },
        ],
        colors: ['123A63'],
        yMin: 0,
        yMax: 0.5,
        yStep: 0.1,
        yTitle: 'Skill Score',
      },
      callouts: [
        {
          label: 'KAN优势',
          text: 'Skill Score = 0.453，显著优于参数匹配的MLP (0.430, p=0.0005)，远超PySR纯符号方法 (0.076)',
        },
        {
          label: 'RMSE对比',
          text: 'KAN: 1413.51 MW\nMLP: 1474.38 MW\nPySR: 2388.46 MW',
        },
      ],
      source: '5-seed mean, ERCOT 2018 test set, h=12',
    },
  },

  // ── Slide 6: Formula Collapse ──
  {
    pattern: 'p09-data-table',
    data: {
      sectionTag: 'S1 — 核心发现',
      title: '公式坍缩：3×3网格搜索下所有9种配置均坍缩为纯自回归滞后公式',
      subtitle: 'VER(any_physical) = 0/9 — 气象物理变量被系统性消除',
      columns: [
        { label: '候选库', width: 2.2, align: 'left' },
        { label: 'R²≥0.90', width: 1.6, align: 'right' },
        { label: 'R²≥0.85', width: 1.6, align: 'right' },
        { label: 'R²≥0.80', width: 1.6, align: 'right' },
        { label: 'VER', width: 1.88, align: 'right' },
      ],
      rows: [
        { cells: ['strict (6函数)', 'lag only', 'lag only', 'lag only', '0/3'], highlight: true },
        { cells: ['medium (12函数)', 'lag only', 'lag only', 'lag only', '0/3'] },
        { cells: ['relaxed (18函数)', 'lag only', 'lag only', 'lag only', '0/3'] },
        { cells: ['合计 VER', '—', '—', '—', '0/9'], total: true },
      ],
      callout: {
        text: '所有公式仅保留load_lag_12、load_lag_24等自回归项 → 气象变量（GHI、风速、温度）在稀疏化-剪枝阶段被完全消除。但这究竟是因为变量本身无关，还是被自回归捷径"竞争压制"？',
      },
      source: 'KAN symbolic extraction, 3 candidate libraries × 3 R² thresholds',
    },
  },

  // ── Slide 7: S2 — Autoregressive Blocking Experiment ──
  {
    pattern: 'p03-evidence',
    data: {
      sectionTag: 'S2 — 因果验证',
      title: '自回归阻断实验证实：物理变量消失源于"捷径竞争"而非变量无关',
      chart: {
        type: 'bar',
        series: [
          {
            name: 'ΔVER (阻断后 − 阻断前)',
            labels: ['Case 3 (Wind)', 'Case 4 (Net Load)'],
            values: [0.60, 0.80],
          },
        ],
        colors: ['3A8F5C'],
        yMin: 0,
        yMax: 1.0,
        yStep: 0.2,
        yTitle: 'ΔVER',
      },
      callouts: [
        {
          label: '实验设计',
          text: '移除自回归滞后特征后重新训练KAN并提取符号公式。若气象变量重新出现 → 证明是竞争压制而非无关',
        },
        {
          label: 'Case 3 (风电)',
          text: 'ΔVER = +0.60\n95% CI = [0.20, 1.00]\n→ 显著成功',
        },
        {
          label: 'Case 4 (净负荷)',
          text: 'ΔVER = +0.80\n95% CI = [0.40, 1.00]\n→ 强烈成功',
        },
      ],
      source: '5-seed bootstrap, pre-registered decision rules',
    },
  },

  // ── Slide 8: S3 — Structured Decomposition ──
  {
    pattern: 'p04-scorecard',
    data: {
      sectionTag: 'S3 — 解决方案',
      title: '结构化分解方案：子任务独立建模实现精度与可解释性的统一 (FAR=3/3)',
      cards: [
        {
          label: '负荷子模型',
          value: 'RMSE 401',
          trend: '周期编码 + 自回归滞后',
          benchmark: 'FAR = 1/1 ✓',
          statusColor: '3A8F5C',
        },
        {
          label: '风电子模型',
          value: 'RMSE 1009',
          trend: '风速 + 太阳几何',
          benchmark: 'FAR = 1/1 ✓',
          statusColor: '3A8F5C',
        },
        {
          label: '光伏子模型',
          value: 'RMSE 1007',
          trend: 'GHI + 太阳几何',
          benchmark: 'FAR = 1/1 ✓',
          statusColor: '3A8F5C',
        },
        {
          label: '复合模型 Skill',
          value: '0.456',
          trend: '与原始KAN (0.453) 持平',
          benchmark: '精度无损',
          statusColor: '3A8F5C',
        },
        {
          label: '整体 FAR',
          value: '3/3',
          trend: '所有子任务公式均包含目标物理变量',
          benchmark: '完全可辨识',
          statusColor: '3A8F5C',
        },
        {
          label: '方法论意义',
          value: '通用',
          trend: '仅改变任务结构，不修改算法',
          benchmark: '可推广至其他SR方法',
          statusColor: 'D4A843',
        },
      ],
      assessment: '核心结论：通过将净负荷分解为负荷/风电/光伏三个子任务，每个子任务配置任务专属特征，成功打破自回归捷径竞争，实现 Skill=0.456 + FAR=3/3 的精度-可解释统一',
      source: 'S3 structured decomposition, 5-seed mean, h=12',
    },
  },

  // ── Slide 9: Progress & Issues ──
  {
    pattern: 'c04-facts-perspectives',
    data: {
      sectionTag: '中期进展',
      title: '全部核心实验已完成，当前处于论文撰写与补充阶段',
      facts: {
        bullets: [
          '✅ 数据管线完成：ARPA-E PERFORM数据集，26维特征工程，标准化预处理',
          '✅ KAN教师-符号提取管线完成：4阶段训练，Skill=0.453，显著优于MLP和PySR',
          '✅ 公式坍缩系统记录：3×3搜索，9/9坍缩，VER=0/9',
          '✅ S2阻断实验完成：ΔVER=+0.60/+0.80，确认捷径竞争机制',
          '✅ S3结构化分解完成：复合Skill=0.456，FAR=3/3',
        ],
      },
      perspectives: {
        bullets: [
          '论文撰写尚未完成，需按学校模板整理Word版',
          '种子数有限（5 seeds），置信区间较宽',
          '单一数据集局限（仅ERCOT），跨区域泛化未验证',
        ],
        implication: '核心创新与实验验证已就绪，后续工作以论文写作和答辩准备为主',
        nextStep: '补充实验图表、完善可视化、准备答辩材料',
      },
    },
  },

  // ── Slide 10: Closer ──
  {
    pattern: 'p08-closer',
    data: {
      title: '核心贡献与后续计划',
      body: '本研究首次识别并通过因果干预证实了KAN符号提取中的自回归捷径竞争机制，提出VER/FAR诊断体系和S3结构化分解方案，实现预测精度与公式可解释性的统一。',
      nextSteps: [
        '完成论文撰写，按学校模板规范格式',
        '补充实验可视化图表，提升论文质量',
        '准备答辩PPT与答辩材料',
        '探索未来方向：物理约束KAN、多数据集验证、更丰富符号库',
      ],
    },
  },

], '/Users/vfch/Documents/project/graduation-design/midterm-report.pptx')
  .then(() => console.log('Done!'))
  .catch(err => console.error('Error:', err));
