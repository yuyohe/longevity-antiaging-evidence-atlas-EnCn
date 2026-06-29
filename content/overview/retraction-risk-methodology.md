# 撤稿风险观察方法 / Retraction Risk Methodology

Last updated / 更新时间：2026-05-14

## 目的

本模块用于补充 v0.5 证据评分。v0.5 已经评价研究设计、终点、人群、来源深度、文章影响力、发表地/期刊层级和风险边界；撤稿风险层回答另一个问题：某个成分或主题在公开文献中是否出现过撤稿记录。

## 纳入门槛

一条记录进入本模块，需要同时满足：

1. 来源为 PubMed。
2. PubMed Publication Type 包含 `Retracted Publication`。
3. 被撤稿论文的发表日期在 2006/01/01 到 2026/05/14。
4. 成分或主题词必须匹配题名，题名或摘要再匹配本项目补剂、护肤、抗衰前沿语境。
5. 查询必须可复跑，查询式写入 `data/retraction_risk_queries_20y.csv`。

## 分母和归一化指标

撤稿记录数是分子，不能单独比较。每个目标还会记录同一检索口径下的 PubMed 总发表量作为分母。

| 字段 | 含义 |
| --- | --- |
| `pubmed_total_count_20y` | 同一题名/语境/时间窗下的总发表量 |
| `pubmed_retracted_count_20y` | 其中被 PubMed 标记为撤稿的论文数 |
| `retraction_rate_percent` | 撤稿数 / 总发表量 × 100% |
| `retractions_per_1000_publications` | 撤稿数 / 总发表量 × 1000 |
| `avg_publications_per_year_20y` | 近 20 年窗口内年均发表量 |
| `normalized_risk_bucket` | 综合分母和撤稿密度后的风险标签 |

## 输出文件

| 文件 | 作用 |
| --- | --- |
| `data/retraction_risk_summary_20y.csv` | 每个成分/主题的撤稿计数和读者解释 |
| `data/retracted_publications_20y.csv` | 匹配到的撤稿 PubMed 记录清单 |
| `data/retraction_risk_queries_20y.csv` | 每个成分/主题的 PubMed 查询式 |
| `content/public-reader/retractions.md` | 普通读者解释页 |
| `content/analysis/retraction-risk-ranking.md` | 研究维护用排行 |

## 解释边界

- 撤稿多不等于成分一定无效。
- 撤稿少不等于成分一定有效或安全。
- 被撤稿的论文不作为正向证据，只作为风险观察记录。
- 撤稿数量受研究热度、期刊审查、数据库覆盖范围影响。
- 本模块暂不使用非公开或需授权数据库；后续可接入 Retraction Watch Database 等更完整来源，但需要遵守其使用条款。

## 本轮规模

- 目标成分/主题：117 个。
- 匹配撤稿记录行：538 行。
- 去重 PMID：487 个。
