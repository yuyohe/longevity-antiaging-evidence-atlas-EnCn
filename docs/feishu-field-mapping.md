# 飞书多维表格字段设计

建议表名：`文献总表`

| CSV 字段 | 飞书字段名 | 推荐字段类型 |
|---|---|---|
| paper_id | paper_id | 文本 |
| year | 年份 | 数字 |
| topic | 主题 | 文本或单选 |
| intervention_or_exposure | 干预/暴露 | 文本 |
| study_type | 研究类型 | 单选 |
| species | 物种 | 单选 |
| sample_size | 样本量 | 数字 |
| primary_endpoint | 主要终点 | 文本 |
| endpoint_class | 终点等级 | 单选 |
| effect_size | 效应量 | 文本 |
| evidence_level | 证据等级 | 单选 |
| risk_of_bias | 偏倚风险 | 单选 |
| actionability | 可行动性 | 单选 |
| medical_supervision | 是否需要医生监督 | 复选框 |
| recommendation_class | 推荐等级 | 单选 |
| claim_supported | 支持的结论 | 长文本 |
| claim_not_supported | 不支持的结论 | 长文本 |
| zh_summary | 中文一句话结论 | 长文本 |
| en_summary | 英文一句话结论 | 长文本 |
| last_checked | 最后核查日期 | 日期或文本 |

## 单选建议

### 研究类型

- RCT
- cohort
- meta-analysis
- review
- animal
- cell
- mechanism
- computational
- needs_classification

### 终点等级

- H1
- H2
- H3
- H4
- H5
- H6

### 证据等级

- A
- B
- C
- D
- E
- F

### 推荐等级

- Strong Action
- Medical Action
- Monitor
- Do Not Recommend
- Insufficient Evidence
