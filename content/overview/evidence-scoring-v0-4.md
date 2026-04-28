# 证据评分方法 v0.4 / Evidence Scoring Method v0.4

草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。  
Draft status: automatically prepared; not fully reviewed; not medical advice.

Last updated / 更新时间：2026-04-28

## 我们为什么重做评分

旧版本主要用“研究类型 + 终点类型”直接映射 A/B/C/D，容易把一篇系统综述或 Meta 分析自动抬到 A。这个做法对死亡、疾病等硬终点仍然偏粗，对外观抗老、补剂、口服胶原这类高商业化主题尤其危险。

v0.4 改为混合框架：**GRADE 作为公开结论置信度框架，Cochrane RoB 2 / ROBINS-I / AMSTAR 2 作为全文复核工具，NIH iCite RCR 与 OpenAlex 引用数作为可公开获得的影响力信号**。JCR Impact Factor、CiteScore、SJR 可以后续导入，但不会被伪造，也不会单独决定单篇研究质量。

## 评分组成 / Score Components

| 维度 | 权重/规则 | 说明 |
|---|---:|---|
| 研究设计 / Study design | 0-34 | 系统综述、RCT、队列、观察、动物/机制分层。 |
| 终点价值 / Endpoint value | 0-25 | 死亡/疾病硬终点最高；皮肤水分、弹性、皱纹为 S1 软临床/仪器终点。 |
| 人类相关性 / Human relevance | 0-15 | 人体证据优先；动物/细胞证据设置上限。 |
| 来源深度 / Source depth | 0-10 | 开放全文/摘要/仅题录分层。 |
| 权威与影响力信号 / Authority signals | 0-20 | DOI、PMID、PMCID、NIH iCite RCR、OpenAlex cited_by_count。 |
| 风险扣分 / Risk adjustments | 0 到 -20 | 仅摘要、仅题录、商业过度宣传、可能行业资助、软终点外推等扣分。 |
| 等级上限 / Confidence caps | hard cap | 动物/机制最高 D；仅题录最高 D；皮肤软终点和高商业风险主题不能仅凭 Meta 分析进入 A。 |

## 公开等级解释 / Public Level Meaning

| 等级 | 含义 |
|---|---|
| A | 高置信候选方向。通常需要硬终点或强人体证据、较低风险、足够来源深度和影响力信号。不是个人处方。 |
| B | 中高置信候选方向。适合进入公开总览，但需要边界和分层。 |
| C | 有信号但限制明显。常见于软终点、样本较小、异质性高或商业化风险高的主题。 |
| D | 机制、动物、仅题录、摘要不足或结论外推风险高。 |
| E | 证据不足或当前不宜支持公开结论。 |

## IF 政策 / Impact Factor Policy

我们目前没有自动使用 JCR Impact Factor。原因有三点：

1. JCR IF 通常需要授权，不应从非授权网页抓取或伪造。
2. IF 是期刊层指标，不等于单篇论文质量。
3. 国际上 DORA、Leiden Manifesto 等负责任指标原则均反对用单一期刊指标替代研究质量评价。

如果后续导入 JCR IF、CiteScore 或 SJR，它们只会作为 `authority_signal_score` 的一部分，并且会被 RoB/GRADE、终点硬度、来源深度和上限规则约束。

## 关键修正：口服胶原 / Oral Collagen

口服胶原肽当前不再因为“有系统综述/Meta 分析 + S1 皮肤终点”自动显示为 A。v0.4 将其降为 C：主要理由是终点多为皮肤水分、弹性、皱纹评分等软终点，研究异质性和商业过度宣传风险较高，不能外推为逆龄、延寿或替代均衡蛋白摄入。

## 数据字段 / Data Fields

本轮新增字段包括：`quality_confidence_score`, `influence_score`, `journal_metric_source`, `journal_metric_value`, `openalex_cited_by_count`, `icite_rcr`, `risk_of_bias_tool`, `risk_of_bias_rating`, `amstar2_rating`, `funding_conflict_risk`, `industry_funding_risk`, `confidence_cap_rule`, `final_evidence_level`。
