# Contribution Scoring / 贡献度测算方案

Contribution score measures how much a candidate source should contribute to this bilingual evidence atlas. It is used for triage, not as an automatic truth score.

贡献度分用于判断候选文献对本双语证据图谱的价值。它服务于筛选排序，不等于自动判定“真理”。

## Total Score / 总分

`contribution_score = base_score - penalty_score`

Maximum base score: 100. Minimum final score: 0.

基础分最高 100 分，扣分后最低为 0 分。

| Dimension | Points | What It Measures | 中文说明 |
|---|---:|---|---|
| Endpoint value | 20 | Hard, functional, clinical, biomarker, or mechanistic endpoint | 终点价值 |
| Study design | 20 | RCT/meta-analysis/cohort/MR/preclinical/mechanistic strength | 研究设计强度 |
| Human relevance | 15 | Human directness, population fit, clinical translatability | 人类相关性 |
| Scale and replication | 10 | Sample size, follow-up, multi-cohort replication, independent validation | 规模与重复验证 |
| Effect/actionability | 15 | Effect size, risk-benefit, practical relevance, safety clarity | 效应与可行动性 |
| Authority signal | 10 | IF, journal quartile, guideline status, registry, data/code openness | 权威性信号 |
| Atlas coverage value | 5 | Fills a topic gap, negative result, safety signal, under-covered area | 图谱覆盖贡献 |
| Bilingual explainability | 5 | Can be clearly explained in Chinese and English without hype | 双语解释价值 |

## Authority Signal / 权威性信号

Authority is capped at 10 points and must not dominate the score.

权威性最高 10 分，不能主导总分。

| Signal | Max | Rule |
|---|---:|---|
| Journal IF / 期刊 IF | 5 | `0`: unavailable or irrelevant; `1`: IF < 3; `2`: 3-5; `3`: 5-10; `4`: 10-30; `5`: >30 or top medical/science journal |
| Journal/venue quality / 期刊或平台质量 | 2 | Peer-reviewed, reputable society, major registry, or official government dataset |
| Citation or guideline influence / 引用或指南影响 | 2 | Highly cited, guideline-cited, or practice-changing |
| Open data/code/protocol / 数据代码方案开放 | 1 | Data, code, protocol, or trial registry is available |

IF should be captured as `journal_if`, with `journal_if_year` and `journal_if_source` when available.

IF 应记录为 `journal_if`，并尽量附上 `journal_if_year` 和 `journal_if_source`。

## Penalties / 扣分

| Problem | Penalty | 中文说明 |
|---|---:|---|
| High risk of bias | -10 to -25 | 高偏倚风险 |
| Major conflict of interest without transparency | -5 to -15 | 重大利益冲突且披露不足 |
| Endpoint mismatch or overclaiming | -5 to -20 | 终点与主张不匹配或过度宣传 |
| Non-human evidence marketed as human action | -10 to -25 | 把非人体证据包装成人体建议 |
| Safety concern not addressed | -5 to -20 | 安全性问题没有处理 |
| Duplicate or superseded record | -10 to -30 | 重复或已被更高质量证据替代 |

## Decision Thresholds / 决策阈值

| Final score | Action | 中文动作 |
|---:|---|---|
| 85-100 | High-priority inclusion | 优先进入正式证据总表和论文卡片 |
| 70-84 | Shortlist | 进入候选短名单，等待人工复核 |
| 50-69 | Keep as candidate | 保留在候选池，暂不进入正式图谱 |
| 30-49 | Low priority | 低优先级，仅在主题缺口时考虑 |
| 0-29 | Exclude or archive | 排除或归档 |

## Manual Review Formula / 人工复核公式

Reviewers should score each dimension independently before reading the generated summary. This reduces the risk that a fluent bilingual summary makes weak evidence look stronger than it is.

人工复核时，应先按维度打分，再看生成摘要，避免流畅的双语摘要让弱证据显得更强。

Required review fields:

- candidate_id
- reviewer
- review_date
- endpoint_value_score
- study_design_score
- human_relevance_score
- scale_replication_score
- effect_actionability_score
- authority_signal_score
- atlas_coverage_score
- bilingual_explainability_score
- penalty_score
- contribution_score
- decision
- reviewer_notes
