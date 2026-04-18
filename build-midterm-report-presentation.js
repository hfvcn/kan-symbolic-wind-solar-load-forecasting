const path = require('path');
const {
  createDeck,
  loadTheme,
} = require('/Users/vfch/Downloads/MCP/MCP-tool-use/presentation/deck-design-ppt/masters');

const OUTPUT_PATH = path.join(__dirname, 'midterm-report-presentation.pptx');
const PALETTE = 'consulting-mckinsey';

function buildSlides(theme) {
  return [
    {
      pattern: 'p01-cover',
      data: {
        title: '基于KAN的可解释净负荷预测',
        subtitle: '自回归捷径竞争机制与结构化分解方案',
        scope: '毕业设计中期检查汇报 | 聚焦研究问题、阶段成果、关键证据与后续计划',
        org: '毕业设计中期汇报',
        location: 'graduation-design',
        date: '2026年4月11日',
        confidentiality: 'MIDTERM REVIEW',
      },
    },
    {
      pattern: 'p07-machine',
      data: {
        sectionTag: '01 研究框架',
        title: '本课题围绕“物理变量为何在公式中消失”搭建了从问题识别到修复验证的四步路径',
        subtitle: '问题定义 -> 管线搭建 -> 机制验证 -> 解决方案',
        steps: [
          {
            num: '1',
            title: '定义问题场景',
            description:
              '面向高比例可再生能源场景下的净负荷预测，研究目标不是只提高精度，而是同时输出具有物理含义的符号公式。',
          },
          {
            num: '2',
            title: '完成 KAN 教师到符号提取管线',
            description:
              '基于 ARPA-E PERFORM 数据集完成 26 维特征工程、60/20/20 时序划分，以及预热、稀疏化、剪枝、符号拟合四阶段训练流程。',
          },
          {
            num: '3',
            title: '用 S2 阻断实验验证捷径竞争机制',
            description:
              '在保持模型结构和训练设置不变的条件下，仅阻断自回归滞后通路，观察气象物理变量的 VER 变化并用置信区间判断显著性。',
          },
          {
            num: '4',
            title: '用 S3 结构化分解恢复可解释性',
            description:
              '将净负荷拆分为负荷、风电、光伏三个子任务，各自提取局部公式，再按固定加法规则组合预测，兼顾精度与公式可读性。',
          },
        ],
        conclusion:
          '当前中期阶段的核心成果，是把“公式坍缩”从现象描述推进为可验证机制，并给出可操作的结构化修复路径。',
        source: 'Source: doc/论文_pandoc.docx, doc/中期报告_filled.docx',
      },
    },
    {
      pattern: 'p04-scorecard',
      data: {
        sectionTag: '02 阶段成果',
        title: '核心研究工作已基本完成，并同时拿到精度、机制与可解释性三类结果',
        subtitle: '中期检查时点的主要完成情况',
        cards: [
          {
            label: '数据管线',
            value: '26维',
            trend: '完成特征工程与时序划分',
            benchmark: 'PERFORM 数据集 | 5分钟采样',
            statusColor: theme.positive,
          },
          {
            label: 'KAN 精度',
            value: '0.453',
            trend: 'skill score 优于 MLP 0.430',
            benchmark: 'p = 0.0005',
            statusColor: theme.positive,
          },
          {
            label: 'PySR 对比',
            value: '0.076',
            trend: '直接符号回归精度明显偏低',
            benchmark: '验证“先训练后提取”必要性',
            statusColor: theme.caution,
          },
          {
            label: '公式坍缩',
            value: '9/9',
            trend: 'direct net load 配置全部坍缩',
            benchmark: 'VER(any_physical)=0/9',
            statusColor: theme.negative,
          },
          {
            label: 'S2 阻断',
            value: '+0.80',
            trend: 'Case 4 ΔVER 显著提升',
            benchmark: '95% CI [0.40, 1.00]',
            statusColor: theme.positive,
          },
          {
            label: 'S3 分解',
            value: '0.456',
            trend: '组合模型 skill 与直接模型持平',
            benchmark: '三个子任务 FAR=3/3',
            statusColor: theme.positive,
          },
        ],
        assessment:
          '截至中期，研究主体已完成：数据、训练、机制检验与解决方案均已有结果；剩余工作主要是论文定稿、图表打磨与答辩材料组织。',
        source: 'Source: 中期报告“当前工作的进展”',
      },
    },
    {
      pattern: 'p03-evidence',
      data: {
        sectionTag: '03 关键证据',
        title: 'KAN 教师在精度上领先基线，但直接符号提取会坍缩为仅含滞后项的公式',
        chart: {
          type: 'bar',
          series: [
            {
              name: 'Skill Score',
              labels: ['KAN', 'MLP', 'PySR'],
              values: [0.453, 0.43, 0.076],
            },
          ],
          colors: [theme.accent],
          yMin: 0,
          yMax: 0.5,
          yStep: 0.1,
          yTitle: 'Skill score',
        },
        callouts: [
          {
            label: '证据 1 | 预测有效',
            text: 'KAN 教师模型 skill=0.453，显著优于参数对齐 MLP 的 0.430 和 PySR 的 0.076，说明 KAN 适合作为符号提取起点。',
          },
          {
            label: '证据 2 | 直接提取坍缩',
            text: '在直接净负荷目标上，3×3 共 9 组符号配置全部退化为仅含负荷滞后项的极简公式，VER(any_physical)=0/9。',
          },
          {
            label: '证据 3 | 机制被验证',
            text: '阻断自回归后，Case 3 的 ΔVER=+0.60，Case 4 的 ΔVER=+0.80，置信区间均不含零，支持“自回归捷径竞争”而非“变量无关性”。',
          },
        ],
        source: 'Source: 论文摘要与第五章实验结果',
      },
    },
    {
      pattern: 'p05-narrative-arc',
      data: {
        sectionTag: '04 后续安排',
        title: '后续工作将集中在论文定稿、图表完善与答辩准备三个收尾动作',
        milestones: [
          {
            year: '现在',
            label: '中期完成',
            description: '主体实验、S2 阻断与 S3 分解结果均已跑通',
            highlight: true,
          },
          {
            year: '阶段一',
            label: '论文定稿',
            description: '完成 Word 正文整理与学校模板排版',
          },
          {
            year: '阶段二',
            label: '图表补强',
            description: '补充关键图表与可视化，提升论文表达完整性',
          },
          {
            year: '阶段三',
            label: '答辩准备',
            description: '整理口头讲稿与最终演示材料，并回应单数据集与种子数局限',
          },
        ],
        source: 'Source: 中期报告“存在的问题”与“后期工作及计划”',
      },
    },
    {
      pattern: 'p08-closer',
      data: {
        title: '当前阶段已经完成机制验证，后续重心转向论文与答辩交付',
        body: '中期阶段的关键目标已经实现：不仅证明了 KAN 在净负荷预测上的有效性，也解释了物理变量在符号提取中消失的原因，并给出了结构化分解这一可落地修复路径。',
        nextSteps: [
          '完成论文撰写、排版与图表整理，形成可提交版本',
          '围绕种子数量和单一数据集局限补充说明，收紧论文论证边界',
          '准备最终答辩 PPT 与讲稿，把“问题-证据-结论”表达再压缩',
        ],
      },
    },
  ];
}

async function main() {
  const theme = loadTheme(PALETTE);
  const slides = buildSlides(theme);
  await createDeck(PALETTE, slides, OUTPUT_PATH);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
