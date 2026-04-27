# 长寿抗衰与健康寿命证据图谱 / Longevity Anti-Aging Evidence Atlas EnCn

这是一个中英双语、可审计、可持续维护的长寿与健康寿命证据库。

项目目标不是提供医疗建议，也不是推荐药物、补剂或剂量，而是把长寿、健康寿命、抗衰、运动、心血管预防、代谢健康、生物年龄、补剂和前沿 geroscience 技术按证据强度重新整理。

## 项目原则

1. **证据优先**：区分人体硬终点、人体功能终点、临床风险指标、生物标志物、动物寿命实验和机制研究。
2. **双语维护**：英文用于文献元数据和国际核查，简体中文用于中文读者理解。
3. **不夸大**：不把动物实验写成人类延寿，不把 biomarker 改善写成“逆龄”。
4. **不提供处方**：药物、剂量、诊断和治疗必须由医生评估。
5. **GitHub 是唯一事实源**：飞书多维表格、知识库和后续中文发布内容都从本仓库同步。
6. **候选不等于收录**：PubMed、ClinicalTrials.gov、Crossref 抓取结果先进候选池，经过人工审核和贡献度评分后才进入正式证据矩阵。

## 当前阶段

第一阶段参考外部 longevity GitHub 项目的主题结构，但扩容到约十倍候选规模。以参考清单当前 75 条来源为基线，本项目第一阶段候选池目标为不少于 750 条。

候选池只是筛选入口，正式纳入需要看：

- 研究设计
- 终点质量
- 人类相关性
- 样本量和重复验证
- 效应量、风险收益和安全性
- IF、期刊声誉、引用和开放数据等权威性信号
- 对本图谱主题覆盖的贡献
- 能否清楚地中英双语解释

## 仓库结构

```text
AGENTS.md                         # Codex / AI agent 维护规则
README.md                         # English overview
README.zh-CN.md                   # 中文说明
DISCLAIMER.md                     # 医疗免责声明
CHANGELOG.md                      # 更新日志
data/                             # 结构化数据
content/                          # 论文卡片、主题页、分析页、推荐边界
methodology/                      # 纳入标准、证据分级、贡献度评分、搜索策略
prompts/                          # 给 Codex 的提示词
scripts/                          # 抓取、评分、检查、索引、飞书同步脚本
docs/                             # GitHub/Codex/飞书接入说明
.github/workflows/                # GitHub Actions
```

## 工作流

```text
文献检索
-> data/candidate_sources.csv
-> 飞书「候选文献」
-> 人工审核与贡献度评分
-> content/papers/ 论文卡片
-> data/evidence_matrix.csv
-> content/topics/ 主题页
-> lint / build index
-> GitHub commit
-> 同步飞书
```

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/lint.py
python scripts/build_index.py
```

## 飞书同步

详见：

- `docs/connect-feishu.md`
- `docs/feishu-field-mapping.md`
- `docs/feishu-base-schema.md`

## 免责声明

本项目仅用于研究整理和内容创作，不构成医疗建议、诊断或治疗建议。涉及药物、疾病、检查、补剂和治疗方案的问题，请咨询合格医疗专业人士。
