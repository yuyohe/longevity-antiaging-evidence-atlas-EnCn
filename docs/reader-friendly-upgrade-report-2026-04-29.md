# 普通读者可读性升级报告 / Reader-Friendly Upgrade Report

- 日期：2026-04-29
- 目标读者：40-50 岁、不是生物科技背景、希望快速看懂证据边界的人。
- 原则：先解释，再给表；先说能看什么，再说不能怎么理解；所有药物、疾病、医美和高风险补剂都保留专业评估边界。

## 新增内容

| 产物 | 数量 | 作用 |
| --- | --- | --- |
| data/reader_guides.csv | 8 | 给普通读者的分步说明。 |
| data/reader_topic_guide.csv | 28 | 28 个主题的白话解释。 |
| data/plain_language_glossary.csv | 40 | 术语解释。 |
| data/feishu_table_guide.csv | 14 | 飞书表格使用说明。 |
| content/overview/start-here.md | 1 | 项目第一入口。 |
| content/overview/reader-topic-guide.md | 1 | 普通读者主题指南。 |
| content/overview/evidence-levels-plain-language.md | 1 | 证据等级白话说明。 |
| content/overview/feishu-reading-guide.md | 1 | 飞书阅读路径。 |
| content/overview/plain-language-glossary.md | 1 | 术语表。 |

## 飞书同步目标

- 新手阅读指南
- 普通读者主题指南
- 术语解释
- 飞书表格使用说明

## 已同步到飞书的表

| 表名 | table_id | 记录数 | 用途 |
| --- | --- | ---: | --- |
| 新手阅读指南 | tblaYnCNYIJnf0dG | 8 | 给第一次打开项目的人看的阅读入口。 |
| 普通读者主题指南 | tblUAsYxAzCtNBQc | 28 | 把 20 个健康寿命主题和 8 个皮肤主题翻译成白话。 |
| 术语解释 | tblTl9zuW2h4Aavp | 40 | 解释 RCT、终点、GRADE、IF、RCR、PMID 等常见词。 |
| 飞书表格使用说明 | tblM53UjZbx6VUJG | 14 | 告诉读者每张表做什么、适合谁看、不能怎么误读。 |

## 主表白话字段

这次不只新增说明表，也直接增强了三张主要飞书表：

- 对外总览：新增 `plain_takeaway_zh`、`read_first_zh`、`do_not_misread_zh`、`doctor_boundary_plain_zh`。
- 外观抗老总览：新增 `plain_takeaway_zh`、`endpoint_plain_zh`、`do_not_misread_zh`、`professional_boundary_plain_zh`。
- 补剂证据矩阵：新增 `plain_takeaway_zh`、`not_a_buying_guide_zh`、`overclaim_warning_plain_zh`、`safety_plain_zh`、`doctor_boundary_plain_zh`。

这些字段的目标是让读者在飞书表格里不用先懂生物统计，也能先看懂“这件事大概能说明什么、不能说明什么、什么时候需要医生或专业人士”。

## 后续还能继续做的提升

1. 给每个主题页顶部加入 3 行白话摘要：一句话结论、适合谁看、不要怎么理解。
2. 给补剂矩阵加“普通人一句话提醒”字段，例如“不要作为购买建议”。
3. 给 A/B 级主题做短文版解释，每篇控制在 800-1200 字。
4. 在飞书里为普通读者创建单独视图，隐藏复杂字段，只保留等级、白话解释、边界、是否需要医生。
