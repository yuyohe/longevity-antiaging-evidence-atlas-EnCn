# Longevity Anti-Aging Evidence Atlas EnCn

**中文名 / Chinese public name:** 长寿抗衰与健康寿命证据图谱  
**Repository:** `longevity-antiaging-evidence-atlas-EnCn`

> **Public entry point / 公众入口：** [`content/overview/start-here.md`](content/overview/start-here.md)  
> **Evidence summary / 证据总览：** [`content/overview/public-summary.md`](content/overview/public-summary.md)  
> **Chinese README / 中文 README：** [`README.zh-CN.md`](README.zh-CN.md)

This is a bilingual evidence atlas for longevity, anti-aging claims, healthspan, supplements, skin-aging topics, biomarkers, and frontier geroscience.

这是一个中英文双语的证据图谱项目，用于整理长寿、抗衰、健康寿命、补剂、皮肤衰老、生物标志物和前沿老年科学相关主张。

## Mission / 项目使命

The goal is not to tell readers what to buy or try. The goal is to make longevity and anti-aging claims easier to audit.

本项目不是购买建议、用药建议或个人医疗建议，而是把抗衰与长寿相关主张拆成可以审查的证据层级。

- **English:** Separate hard human outcomes from biomarkers, animal studies, functional endpoints, risk markers, and mechanisms.
- **中文：** 区分真正的人体结局、功能终点、临床风险指标、生物标志物、动物寿命实验和机制假说。
- **English:** Separate healthspan evidence from skin and appearance evidence.
- **中文：** 区分健康寿命证据与皮肤、外观抗老证据。
- **English:** Separate supplement evidence from supplement marketing.
- **中文：** 区分补剂证据与补剂营销。
- **English:** Keep safety boundaries visible for drugs, medical aesthetics, chronic disease, and high-dose or long-term supplement use.
- **中文：** 对药物、医美、慢病、高剂量或长期补剂使用保留清晰的安全边界。

## Start Here / 从这里开始

If you are not a researcher, start with the plain-language entry and topic guides.

如果你不是研究人员，建议先从大众入口和主题速读开始。

- [Start here / 从这里开始](content/overview/start-here.md)
- [Public summary / 公众版总览](content/overview/public-summary.md)
- [Plain-language evidence levels / 大众版证据等级](content/overview/evidence-levels-plain-language.md)
- [Reader topic guide / 读者主题指南](content/overview/reader-topic-guide.md)
- [Supplement summary / 补剂总览](content/overview/supplement-summary.md)
- [Skin and appearance summary / 皮肤与外观抗老总览](content/overview/skin-beauty-summary.md)
- [Plain-language glossary / 大众版术语表](content/overview/plain-language-glossary.md)

## Published GitHub Snapshot / GitHub 当前公开快照

The public GitHub snapshot currently exposes the May 2026 data package. A larger June 2026 refresh has been generated locally and should be published as a separate data update.

GitHub 当前公开的是 2026 年 5 月数据包。2026 年 6 月扩展版已经在本地生成，后续应作为单独数据更新发布。

| Asset / 资产 | Published count / 已公开数量 | Link / 链接 |
| --- | ---: | --- |
| Candidate sources / 候选来源 | 11,480 records | [`candidate-sources-2026-05.csv`](public-data/candidate-sources-2026-05.csv) |
| Literature library / 文献库 | 11,480 records | [`literature-library-2026-05.csv`](public-data/literature-library-2026-05.csv) |
| Evidence findings / 证据发现 | 3,000 rows | [`evidence-findings-2026-05.csv`](public-data/evidence-findings-2026-05.csv) |
| Evidence matrix / 证据矩阵 | 1,500 rows | [`evidence-matrix-2026-05.csv`](public-data/evidence-matrix-2026-05.csv) |
| Shortlist sources / 入选来源 | 3,000 rows | [`shortlist-sources-2026-05.csv`](public-data/shortlist-sources-2026-05.csv) |
| Paper cards / 文献卡片 | 1,801 Markdown pages | [`content/papers/`](content/papers/) |
| Healthspan topics / 健康寿命主题 | 21 topic files | [`content/topics/`](content/topics/) |
| Skin and appearance topics / 皮肤与外观主题 | 8 topic files | [`content/skin-beauty-topics/`](content/skin-beauty-topics/) |
| Public data index / 公开数据索引 | 1 report | [`docs/public-full-data-index-2026-05.md`](docs/public-full-data-index-2026-05.md) |

## Evidence Rules / 证据规则

- **English:** Do not present animal lifespan studies as proven human lifespan extension.
- **中文：** 不把动物寿命实验表述成人类寿命延长已被证明。
- **English:** Do not present biomarker improvement as clinical rejuvenation.
- **中文：** 不把生物标志物改善直接表述成临床返老还童。
- **English:** Do not provide medical prescriptions, dosing protocols, diagnosis, or purchase recommendations.
- **中文：** 不提供个人处方、剂量方案、诊断或购买建议。
- **English:** GitHub is the source of truth; Feishu is the structured Chinese display and review layer.
- **中文：** GitHub 是数据与内容源头；飞书是结构化中文展示和复核层。

Scoring method / 评分方法：[`content/overview/evidence-scoring-v0-4.md`](content/overview/evidence-scoring-v0-4.md)

Methods and grading / 方法与分级：[`content/overview/methods-and-scoring.md`](content/overview/methods-and-scoring.md)

## Repository Structure / 仓库结构

```text
data/                       structured data / 结构化数据
public-data/                public CSV exports / 公开 CSV 导出
content/papers/             paper cards / 文献卡片
content/topics/             healthspan topic pages / 健康寿命主题页
content/skin-beauty-topics/ skin and appearance topic pages / 皮肤与外观主题页
content/overview/           overviews, methods, glossary / 总览、方法、术语表
content/analysis/           rankings and analysis / 排名与分析
methodology/                inclusion, grading, search strategy / 纳入、分级与检索策略
scripts/                    build, validation, Feishu export, sync scripts / 构建、校验、飞书导出与同步脚本
docs/                       reports and operations notes / 报告与运维记录
```

## Quick Start / 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/lint.py
python scripts/build_index.py
```

## Boundary Note / 边界说明

This project is for evidence review and content production. It does not provide personal medical advice, diagnosis, prescriptions, dosing protocols, or purchase recommendations.

本项目用于证据复核与内容生产，不提供个人医疗建议、诊断、处方、剂量方案或购买建议。
