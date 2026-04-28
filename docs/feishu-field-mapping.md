# 飞书多维表格字段设计 / Feishu Field Mapping

GitHub CSV 是事实源，飞书多维表格是展示和审核层。正式证据只进入「文献总表」，原始抓取和草稿发现留在「候选文献」。

## 文献总表 / Papers

| CSV 字段 | 飞书字段名 | 推荐字段类型 |
|---|---|---|
| paper_id | paper_id | 文本 |
| year | 年份 | 文本 |
| topic | 主题 | 文本 |
| intervention_or_exposure | 干预/暴露 | 文本 |
| study_type | 研究类型 | 文本 |
| species | 物种 | 文本 |
| sample_size | 样本量 | 文本 |
| primary_endpoint | 主要终点 | 文本 |
| endpoint_class | 终点等级 | 文本 |
| effect_size | 效应量 | 文本 |
| evidence_level | 证据等级 | 文本 |
| risk_of_bias | 偏倚风险 | 文本 |
| actionability | 可行动性 | 文本 |
| medical_supervision | 是否需要医生监督 | 文本 |
| recommendation_class | 推荐等级 | 文本 |
| claim_supported | 支持的结论 | 长文本 |
| claim_not_supported | 不支持的结论 | 长文本 |
| zh_summary | 中文一句话结论 | 长文本 |
| en_summary | 英文一句话结论 | 长文本 |
| last_checked | 最后核查日期 | 文本 |

## 候选文献 / Candidate Sources

候选文献保留抓取元数据和自动抽取结果。`review_status` 决定是否可以进入公开草稿或正式纳入。

核心状态：

- `needs_review`: 未处理候选。
- `public_draft_not_fully_reviewed`: 可公开草稿，但未全文复核。
- `formal_include`: 已复核并进入正式证据矩阵。
- `exclude`: 排除。
- `duplicate`: 重复。

## 主题库 / Topics

主题库用于飞书导航和发布状态管理。首版主题状态为 `public_draft_not_fully_reviewed`。
