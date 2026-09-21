# 撤稿风险层实施报告

日期：2026-09-21

## 这次新增

- `data/retraction_risk_summary_20y.csv`
- `data/retracted_publications_20y.csv`
- `data/retraction_risk_queries_20y.csv`
- `content/public-reader/retractions.md`
- `content/overview/retraction-risk-methodology.md`
- `content/analysis/retraction-risk-ranking.md`

## 结果摘要

- 目标成分/主题：117 个。
- 匹配撤稿记录行：594 行。
- 去重 PMID：538 个。
- 口服/补剂最高：维生素 D，50 条。
- 抗衰前沿最高：自噬/线粒体自噬，16 条。
- 皮肤外用最高：多酚/抗氧化剂，19 条。
- PDRN/PN/Skin Booster：4 条，已在普通读者撤稿页单独放大。

## 新增分母指标

- `pubmed_total_count_20y`：同一检索口径下的总发表量。
- `avg_publications_per_year_20y`：年均发表量，用来判断主题热度。
- `retractions_per_1000_publications`：每 1000 篇撤稿数，用来横向比较不同主题。
- `normalized_risk_bucket`：结合分母和撤稿密度后的标签。

## 发布建议

普通读者页可以作为创新点展示：我们不只看论文数量，也记录撤稿风险。对外表达必须保留边界：撤稿数是风险观察信号，不是成分有效性或安全性的最终判断。
