# Current Output Status / 当前输出状态

Date / 日期: 2026-04-28

## What Is Production-Ready / 已经可作为项目资产使用

- Candidate pool: 938 unique records from PubMed, Crossref, and ClinicalTrials.gov.
- 候选池：来自 PubMed、Crossref、ClinicalTrials.gov 的 938 条唯一记录。

- Finding extraction layer: 60 PubMed records now include draft English result/conclusion extraction and Chinese draft interpretation fields.
- 主要发现层：60 条 PubMed 记录已包含英文结果/结论抽取和中文初稿解释字段。

- Shortlist: 60 records selected for full-text review.
- 短名单：60 条记录进入全文复核队列。

- Topic drafts: 15 topic hub pages generated from the first finding extraction.
- 主题草稿：已从第一批结果抽取生成 15 个主题页草稿。

- Paper-card drafts: 20 draft paper pages generated from PubMed findings.
- 论文卡片草稿：已从 PubMed 主要发现生成 20 个论文页草稿。

## What Is Not Yet Public-Ready / 尚不适合对外发布

- The extracted Chinese result fields are draft translations and must be checked before public publication.
- 中文结果字段仍是草稿翻译，公开前必须人工复核。

- Evidence levels and endpoint classes are draft classifications based on metadata and abstracts.
- 证据等级和终点等级是基于元数据和摘要的草判。

- The formal evidence matrix still contains only a placeholder; no candidate has been promoted into formal inclusion yet.
- 正式证据矩阵仍只有占位记录，还没有候选文献被正式纳入。

## Feishu Status / 飞书状态

- 候选文献: cleaned to 938 rows and 938 unique candidate IDs.
- 候选文献: 60 records updated with result/conclusion fields.
- 主题库: 15 draft topic records added.
- 文献总表: still only placeholder; use after full-text review.

## Next Output Goal / 下一步输出目标

Convert the 60-record shortlist into a publishable v0.1 knowledge base:

把 60 条短名单加工成 v0.1 可发布知识库：

1. Manually review full text or abstract-level details for 30 records.
2. Complete contribution scoring for those 30 records.
3. Promote 20-30 records into `data/evidence_matrix.csv`.
4. Rewrite paper cards from draft extraction into reviewed bilingual summaries.
5. Publish 12 reader-facing topic pages and one evidence overview page.

1. 对 30 条记录做人工全文/摘要级复核。
2. 完成 30 条记录的贡献度评分。
3. 将 20-30 条记录正式纳入 `data/evidence_matrix.csv`。
4. 把论文卡片从“抽取草稿”改写成“复核后的双语摘要”。
5. 发布 12 个面向读者的主题页和 1 个证据总览页。
