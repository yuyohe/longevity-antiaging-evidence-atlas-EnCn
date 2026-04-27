# 飞书多维表格结构 / Feishu Base Schema

飞书是展示层、筛选层和人工审核层。GitHub 仍然是唯一事实源。

Feishu is the display, screening, and manual review layer. GitHub remains the source of truth.

## Base Name / 表格名称

`长寿抗衰与健康寿命证据图谱`

## Table 1: 文献总表 / Papers

Purpose / 用途: formally included papers, evidence grades, and bilingual conclusions.

正式收录的文献、证据等级和中英双语结论。

Primary key / 主键: `paper_id`

Field mapping follows `docs/feishu-field-mapping.md`.

## Table 2: 候选文献 / Candidate Sources

Purpose / 用途: raw discovery results and manual screening queue. Candidate records are not formal inclusion.

抓取结果和人工审核队列。候选文献不等于正式收录。

Core fields / 核心字段:

| Field | Type | Meaning |
|---|---|---|
| id | Text | Candidate record ID, e.g. `pubmed-12345678` |
| title_en | Text | English title |
| title_zh | Text | Chinese translated title, filled during review |
| year | Text | Publication or trial start year |
| doi | Text | DOI |
| pmid | Text | PubMed ID |
| pmcid | Text | PubMed Central ID |
| url | Text | Source URL |
| source | Text | PubMed / ClinicalTrials.gov / Crossref |
| query | Text | Query name |
| include_status | Text | needs_review / shortlist / include / exclude / duplicate |
| notes | Text | Fetch or review notes |
| last_checked | Text | Last checked date |

Review and scoring fields / 审核与评分字段:

| Field | Meaning |
|---|---|
| reviewer | Reviewer |
| review_date | Review date |
| journal | Journal or registry |
| journal_if | Journal Impact Factor, if available |
| journal_if_year | IF year |
| journal_if_source | IF source |
| endpoint_value_score | Endpoint value subscore |
| study_design_score | Study design subscore |
| human_relevance_score | Human relevance subscore |
| scale_replication_score | Scale and replication subscore |
| effect_actionability_score | Effect and actionability subscore |
| authority_signal_score | IF, journal, citation, registry, open-data signal |
| atlas_coverage_score | Contribution to topic coverage |
| bilingual_explainability_score | Chinese/English explainability |
| penalty_score | Bias, safety, conflict, overclaim, duplicate penalty |
| contribution_score | Final contribution score |
| decision | high_priority_include / shortlist / candidate_hold / low_priority / exclude_or_archive |
| reviewer_notes | Manual review notes |

## Table 3: 主题库 / Topics

Purpose / 用途: topic management and future Feishu knowledge-base publishing.

主题页管理和后续飞书知识库发布导航。

| Field | Meaning |
|---|---|
| topic_id | Topic ID |
| title_zh | Chinese topic title |
| title_en | English topic title |
| scope | Inclusion scope |
| evidence_summary_zh | Chinese evidence overview |
| evidence_summary_en | English evidence overview |
| status | draft / review / published |
| paper_count | Linked paper count |
| last_checked | Last checked date |

## Table 4: 发布日志 / Publish Log

Purpose / 用途: record GitHub-to-Feishu sync and publishing events.

| Field | Meaning |
|---|---|
| publish_id | Publish ID |
| date | Date |
| target | GitHub / Feishu Base / Feishu Docs / Feishu Wiki |
| source_commit | Git commit SHA |
| changed_items | Changed items |
| status | success / failed / partial |
| notes | Notes |

## Feishu Knowledge Base Outline / 飞书知识库目录

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
