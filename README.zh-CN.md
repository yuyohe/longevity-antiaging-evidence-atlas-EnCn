# 长寿抗衰与健康寿命证据图谱 / Longevity Anti-Aging Evidence Atlas EnCn

> 一个双语、开源、可审计、可持续维护的长寿与抗衰研究证据库。

本项目目标不是给出医疗建议，也不是推荐补剂或药物，而是把长寿、健康寿命、抗衰、生物年龄、运动、心血管预防、代谢健康、补剂和前沿 geroscience 技术按**证据强度**重新整理。

## 项目原则

1. **证据优先**：区分人体硬终点、人体功能终点、临床风险指标、生物标志物、动物寿命实验和机制研究。
2. **双语维护**：英文用于文献元数据和国际核查，简体中文用于中文互联网读者理解。
3. **不做夸大**：不把动物实验写成人类延寿，不把 biomarker 改善写成“逆龄”。
4. **不提供处方**：药物、剂量、诊断和治疗必须由医生评估。
5. **GitHub 是唯一事实源头**：飞书、多维表格、知识库和公众号内容都从本仓库同步。
6. **候选不等于收录**：PubMed、ClinicalTrials.gov、Crossref 抓取结果先进入候选队列，经过人工审核后才进入证据矩阵。

## 仓库结构

```text
.
├── AGENTS.md                         # Codex / AI agent 维护规则
├── README.md                         # English overview
├── README.zh-CN.md                   # 中文说明
├── DISCLAIMER.md                     # 医疗免责声明
├── CHANGELOG.md                      # 更新日志
├── data/                             # 结构化数据
├── content/                          # 论文卡片、主题页、分析页、推荐页
├── methodology/                      # 纳入标准、证据分级、搜索策略
├── prompts/                          # 给 Codex 的提示词
├── scripts/                          # 抓取、检查、索引、飞书同步脚本
├── docs/                             # GitHub/Codex/飞书接入说明
└── .github/workflows/                # GitHub Actions
```

## 第一阶段目标

- 收录 40 篇核心文献。
- 建立 12 个主题页。
- 建立 1 个证据矩阵。
- 标准版抓取源：PubMed、ClinicalTrials.gov、Crossref。
- 同步到飞书多维表格。
- 生成飞书知识库/文档发布包。

## 推荐工作流

```text
文献检索 → candidate_sources.csv → 人工批准 → paper cards → evidence_matrix.csv
→ topic pages → lint / build index → PR → 人工 review → merge → 同步飞书
```

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/lint.py
python scripts/build_index.py
```

然后让 Codex 执行：

```bash
codex exec --sandbox workspace-write \
  "Read AGENTS.md. Initialize the first 10 candidate papers from data/candidate_sources.csv into paper cards, update evidence_matrix.csv and topic pages, then run scripts/lint.py."
```

## 飞书同步

详见：

- `docs/connect-feishu.md`
- `docs/feishu-field-mapping.md`

最小可运行方式是：

```bash
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
export FEISHU_BITABLE_APP_TOKEN="bascn_xxx"
export FEISHU_SOURCE_TABLE_ID="tblxxx"
python scripts/sync_feishu_bitable.py
```

## 免责声明

本项目仅用于研究整理和内容创作，不构成医疗建议、诊断或治疗建议。涉及药物、疾病、检查、补剂和治疗方案的问题，请咨询合格医疗专业人士。
