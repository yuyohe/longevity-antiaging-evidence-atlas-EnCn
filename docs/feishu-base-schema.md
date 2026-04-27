# 飞书多维表格结构

飞书是展示层和人工审核层，GitHub 仍然是唯一事实源头。标准版第一阶段使用 PubMed、ClinicalTrials.gov、Crossref 三类来源。

## Base 名称

`长寿抗衰与健康寿命证据图谱`

## 表 1：文献总表 / Papers

用途：正式收录的文献、证据等级和双语结论。

主键：`paper_id`

字段沿用 `docs/feishu-field-mapping.md`。

## 表 2：候选文献 / Candidate Sources

用途：抓取结果和人工审核队列。候选文献不等于正式收录。

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | 文本 | 候选记录 ID，例如 `pubmed-12345678` |
| title_en | 长文本 | 英文标题 |
| title_zh | 长文本 | 中文暂译标题 |
| year | 数字 | 年份 |
| doi | 文本 | DOI |
| pmid | 文本 | PubMed ID |
| trial_id | 文本 | ClinicalTrials.gov ID |
| url | URL | 来源链接 |
| source | 单选 | PubMed / ClinicalTrials.gov / Crossref |
| query | 文本 | 来源查询名称 |
| include_status | 单选 | needs_review / include / exclude / duplicate |
| notes | 长文本 | 审核备注 |
| last_checked | 日期 | 最后核查日期 |

## 表 3：主题库 / Topics

用途：主题页管理和文库发布导航。

| 字段名 | 类型 | 说明 |
|---|---|---|
| topic_id | 文本 | 主题 ID |
| title_zh | 文本 | 中文主题名 |
| title_en | 文本 | 英文主题名 |
| scope | 长文本 | 纳入范围 |
| evidence_summary_zh | 长文本 | 中文证据总览 |
| evidence_summary_en | 长文本 | English summary |
| status | 单选 | draft / review / published |
| paper_count | 数字 | 关联文献数量 |
| last_checked | 日期 | 最后核查日期 |

## 表 4：发布日志 / Publish Log

用途：记录 GitHub 到飞书多维表格和文库的同步。

| 字段名 | 类型 | 说明 |
|---|---|---|
| publish_id | 文本 | 发布 ID |
| date | 日期 | 发布日期 |
| target | 单选 | GitHub / Feishu Base / Feishu Docs / Feishu Wiki |
| source_commit | 文本 | Git commit SHA |
| changed_items | 长文本 | 更新内容 |
| status | 单选 | success / failed / partial |
| notes | 长文本 | 备注 |

## 飞书文库目录

```text
长寿抗衰与健康寿命证据图谱
├── 00 项目说明
├── 01 方法学与证据分级
├── 02 证据总览
├── 03 主题页
├── 04 论文卡片
├── 05 普通读者建议边界
└── 99 更新日志
```
