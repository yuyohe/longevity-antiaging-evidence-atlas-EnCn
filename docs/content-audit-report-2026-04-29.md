# 内容与评分审计报告 / Content and Scoring Audit Report

- 生成日期：2026-04-29
- 审计对象：健康寿命图谱、外观抗老/皮肤图谱、补剂证据矩阵、公开总览页和评分方法。
- 审计性质：结构化质量审计 + 方法学一致性审计；不是 1800 篇文献的逐篇全文人工复核。

## 1. 当前数据库里有什么

| 模块 | 数量 | 说明 |
| --- | --- | --- |
| 候选文献池 candidate_sources | 5983 | 来源分布：{'PubMed': 5637, 'ClinicalTrials.gov': 100, 'Crossref': 246} |
| 健康寿命 findings | 1800 | 20 个主题，每主题 90 条自动抽取 finding。 |
| 正式/高权重证据矩阵 evidence_matrix | 900 | 当前只收 A/B/部分 C 级记录，用于对外主表。 |
| 健康寿命主题 public_summary | 20 | 对外收束窗口，每个主题 1 行。 |
| 皮肤美容 findings | 160 | 8 个主题，每主题 20 条。 |
| 皮肤美容主题 skin_beauty_summary | 8 | 外观抗老对外收束窗口。 |
| 补剂证据矩阵 supplement_matrix | 100 | 100 个热门补剂/成分，当前为证据边界矩阵。 |
| 评分规则 scoring_policy_v0_4 | 11 | 公开方法学条目。 |

## 1.1 当前对外窗口

- GitHub 对外总览：`content/overview/public-summary.md`
- GitHub 皮肤美容总览：`content/overview/skin-beauty-summary.md`
- GitHub 补剂矩阵：`content/overview/supplement-summary.md`
- GitHub 评分方法：`content/overview/evidence-scoring-v0-4.md`
- 飞书对外总览表：`tblFsXTD5yqnJTFH`
- 飞书文献总表：`tblYryTL08h4jE53`
- 飞书候选文献：`tblBYXg91Wiw1BJl`
- 飞书外观抗老总览：`tbl9vcaOrwjPcWZt`
- 飞书补剂证据矩阵：`tblAfXqX6qHqpSKb`

## 1.2 已完成的关键工作

- 建立 GitHub + 飞书双端同步结构。
- 将健康寿命候选池扩展到 5983 条，健康寿命 findings 扩展到 1800 条。
- 生成 20 个健康寿命主题页、1800 个论文卡片草稿、900 条正式/高权重证据矩阵记录。
- 新增外观抗老/皮肤健康第二图谱：8 个主题、160 条皮肤 finding。
- 新增 100 个补剂/成分的证据边界矩阵。
- 建立 v0.4/v0.5 综合评分逻辑：研究设计、终点价值、人类相关性、来源深度、影响力信号、风险扣分、等级上限。
- 修正防晒/光防护公开等级：预防 UV 相关光老化为 A；不扩展到逆龄治疗或具体产品推荐。

## 2. 数据完整性检查

| 检查项 | 结果 |
| --- | --- |
| candidate_sources.id | 0 |
| evidence_findings.finding_id | 0 |
| evidence_matrix.paper_id | 0 |
| skin_beauty_findings.finding_id | 0 |
| supplement_matrix.supplement_id | 0 |

- 健康寿命 finding 必填字段缺失：{'finding_id': 0, 'candidate_id': 0, 'pmid': 0, 'topic_id': 0, 'title_en': 0, 'result_en': 0, 'result_zh': 0, 'conclusion_en': 0, 'conclusion_zh': 0, 'final_evidence_level': 0, 'scoring_note_zh': 0}
- 皮肤 finding 必填字段缺失：{'finding_id': 0, 'pmid': 0, 'topic_id': 0, 'title_en': 0, 'result_en': 0, 'result_zh': 0, 'conclusion_en': 0, 'conclusion_zh': 0, 'final_evidence_level': 0}
- 补剂矩阵必填字段缺失：{'supplement_id': 0, 'name_zh': 0, 'name_en': 0, 'longevity_evidence_level': 0, 'skin_beauty_evidence_level': 0, 'unsupported_claim_zh': 0, 'safety_notes_zh': 0}
- evidence_matrix 中找不到对应 candidate_id 的记录数：0
- 公开页面检查：{'overview_topic_pages_checked': 42, 'paper_pages_checked': 1800, 'draft_notice_missing': 0, 'paper_marker_missing': 0, 'mojibake_pages': 0}

## 3. 当前等级分布

| 对象 | 等级分布 |
| --- | --- |
| 健康寿命 findings final_evidence_level | A: 158, B: 726, C: 623, D: 263, E: 30 |
| 健康寿命主题 evidence_level_top | A: 8, B: 5, C: 5, D: 2 |
| 正式证据矩阵 evidence_level | A: 158, B: 726, C: 16 |
| 皮肤 findings final_evidence_level | B: 12, C: 59, D: 73, E: 16 |
| 皮肤主题 evidence_level_top | A: 1, B: 5, C: 2 |
| 补剂：健康寿命列 | C: 61, B: 20, D: 19 |
| 补剂：皮肤美容列 | D: 78, C: 19, B: 3 |

## 4. 健康寿命主题总览

| topic_id | 中文标题 | 公开等级 | finding_count | 质量中位分 | 状态 |
| --- | --- | --- | --- | --- | --- |
| cardiorespiratory-fitness | 心肺适能与死亡风险 | A | 90 | 80 | public_draft_not_fully_reviewed |
| physical-activity-healthspan | 身体活动与健康寿命 | A | 90 | 80 | public_draft_not_fully_reviewed |
| resistance-training-muscle | 抗阻训练、肌肉与衰弱 | A | 90 | 76 | public_draft_not_fully_reviewed |
| blood-pressure-aging | 血压与健康寿命 | A | 90 | 79 | public_draft_not_fully_reviewed |
| ldl-apob-cardiovascular-risk | LDL-C/apoB 与心血管风险 | A | 90 | 76 | public_draft_not_fully_reviewed |
| dietary-pattern-longevity | 饮食模式与死亡风险 | A | 90 | 80 | public_draft_not_fully_reviewed |
| sleep-aging | 睡眠与健康结局 | A | 90 | 70 | public_draft_not_fully_reviewed |
| glp1-weight-cardiometabolic | GLP-1、减重与心代谢结局 | A | 90 | 74 | public_draft_not_fully_reviewed |
| caloric-restriction-human | 热量限制与人体衰老 | B | 90 | 70 | public_draft_not_fully_reviewed |
| time-restricted-eating | 限时进食与代谢健康 | B | 90 | 74 | public_draft_not_fully_reviewed |
| metformin-aging | 二甲双胍与衰老 | B | 90 | 71 | public_draft_not_fully_reviewed |
| rapamycin-mtor-aging | 雷帕霉素/mTOR 与衰老 | C | 90 | 60 | public_draft_not_fully_reviewed |
| senolytics | Senolytics 清除衰老细胞 | C | 90 | 66 | public_draft_not_fully_reviewed |
| nad-nmn-nr-aging | NAD/NMN/NR | C | 90 | 64 | public_draft_not_fully_reviewed |
| epigenetic-clocks | 表观遗传时钟 | B | 90 | 74 | public_draft_not_fully_reviewed |
| itp-mouse-lifespan | ITP 小鼠寿命干预 | D | 90 | 47 | public_draft_not_fully_reviewed |
| klotho-il11-aging | Klotho / IL-11 | C | 90 | 65 | public_draft_not_fully_reviewed |
| partial-reprogramming | 部分重编程 | D | 90 | 48 | public_draft_not_fully_reviewed |
| autophagy-mitophagy | 自噬/线粒体自噬 | C | 90 | 64 | public_draft_not_fully_reviewed |
| microbiome-inflammaging | 微生物组与炎症性衰老 | B | 90 | 73 | public_draft_not_fully_reviewed |

## 5. 外观抗老/皮肤主题总览

| topic_id | 中文标题 | 公开等级 | finding_count | 质量中位分 | 状态 |
| --- | --- | --- | --- | --- | --- |
| sunscreen-photoaging-prevention | 防晒与光老化预防 | A | 20 | 42 | public_draft_not_fully_reviewed |
| retinoids-photoaging | 维A酸/视黄醇类与光老化 | B | 20 | 49 | public_draft_not_fully_reviewed |
| niacinamide-barrier-pigment | 烟酰胺与屏障/色素/炎症 | B | 20 | 49 | public_draft_not_fully_reviewed |
| topical-vitamin-c | 维C外用与色素/胶原 | B | 20 | 49 | public_draft_not_fully_reviewed |
| oral-collagen-peptides | 口服胶原肽与皮肤弹性/水分 | C | 20 | 46 | public_draft_not_fully_reviewed |
| hyaluronic-acid-ceramides-hydration | 透明质酸、神经酰胺与皮肤水分屏障 | B | 20 | 49 | public_draft_not_fully_reviewed |
| polyphenols-skin-photoprotection | 多酚/抗氧化剂与皮肤光保护 | C | 20 | 32 | public_draft_not_fully_reviewed |
| energy-devices-resurfacing | 医美能量设备和换肤类干预 | B | 20 | 49 | public_draft_not_fully_reviewed |

## 6. 评分底层逻辑

当前 v0.4/v0.5 的评分不是单纯按期刊影响因子排序，而是 claim/topic-level 的综合置信度框架：

1. 检索与入库：从 PubMed 优先检索，辅以 Crossref 和 ClinicalTrials.gov 候选；v0.5 扩充时优先高权重期刊和高设计层级文献。
2. 自动抽取：从题录/摘要抽取题名、PMID/DOI、年份、期刊、研究类型、对象、干预/暴露、终点、主要结果、支持与不支持的结论。
3. 研究设计打分：系统综述/Meta、RCT、队列、Mendelian randomization、动物/机制研究分层；研究设计只是基础分，不单独决定 A/B/C/D。
4. 终点价值打分：死亡、疾病事件、骨折、心血管事件等硬终点权重最高；功能/代谢/认知等为中间终点；皮肤 S1 终点只回答外观/皮肤健康，不等同延寿。
5. 人类相关性：人体证据优先；动物、细胞、纯机制研究设置等级上限。
6. 来源深度：开放全文/PMC、摘要、仅题录分层；摘要级记录不得直接作为最终医疗建议。
7. 影响力信号：自动使用 NIH iCite RCR 和 OpenAlex cited_by_count；JCR IF/CiteScore/SJR 目前未授权导入，不伪造。
8. 风险扣分：摘要级、商业过度宣传、行业资助风险、软终点外推、仅题录等扣分。
9. 等级上限：机制/动物、仅题录、补剂商业化高风险、皮肤软终点等都有 cap rule；最后得到 final_evidence_level。
10. 公开主题等级：不是简单取平均；会结合最高质量文献、领域共识、终点性质和过度解读风险。防晒就是一个例子：单篇综述可为 C，但“广谱防晒预防 UV 光老化”这个结论为 A。

## 7. 本次审计发现

### 7.1 已通过的部分

- 主数据表没有发现重复主键。
- 健康寿命 1800 条 findings 均有基础结论字段和最终等级字段。
- 20 个健康寿命主题、8 个皮肤主题、100 个补剂条目数量完整。
- 公开页面未发现常见乱码标记；皮肤美容公开草稿校验已通过。
- 防晒等级已修正为 A，并限定为“预防/减缓 UV 相关光老化”。

### 7.2 仍需谨慎的部分

- 当前大量 finding 仍是摘要级自动抽取，不能等同全文系统综述。
- A/B 级主题里仍应建立人工 spot-check 队列，尤其是 GLP-1、饮食模式、睡眠、血压、LDL/apoB、运动等高影响主题。
- 补剂矩阵目前是“边界和方向矩阵”，不是每个补剂都已经绑定足够的 PMID/全文证据链；它适合对外防止过度宣传，但不适合作为最终推荐表。
- 皮肤美容图谱的主题等级含人工规则/领域判断；应在页面上继续显式区分“领域结论等级”和“单篇文献等级”。
- IF 没有被导入。使用 RCR/OpenAlex 是可公开复现的替代方案，但不能完全替代 JCR IF 或人工期刊分区判断。
- 目前没有完成每条系统综述的 AMSTAR 2、每条 RCT 的 RoB 2、每条观察研究的 ROBINS-I 人工评级。

## 8. 需要优先人工复核的高等级主题

| topic_id | 标题 | 等级 | finding_count | 边界摘要 |
| --- | --- | --- | --- | --- |
| cardiorespiratory-fitness | 心肺适能与死亡风险 | A | 90 | 可作为生活方式优先方向；个体运动处方需结合年龄、疾病和医生评估。 等级已按 v0.4 综合评分重算；A 不等于个人处方建议。 |
| physical-activity-healthspan | 身体活动与健康寿命 | A | 90 | 支持行动方向，不等于给出单一万能运动处方。 等级已按 v0.4 综合评分重算；A 不等于个人处方建议。 |
| resistance-training-muscle | 抗阻训练、肌肉与衰弱 | A | 90 | 可作为健康管理重点；高龄、骨质疏松或慢病人群需专业评估。 等级已按 v0.4 综合评分重算；A 不等于个人处方建议。 |
| blood-pressure-aging | 血压与健康寿命 | A | 90 | 支持监测和医学管理；不提供药物选择或剂量建议。 等级已按 v0.4 综合评分重算；A 不等于个人处方建议。 |
| ldl-apob-cardiovascular-risk | LDL-C/apoB 与心血管风险 | A | 90 | 支持筛查和风险管理；药物治疗必须由医生决定。 等级已按 v0.4 综合评分重算；A 不等于个人处方建议。 |
| dietary-pattern-longevity | 饮食模式与死亡风险 | A | 90 | 支持模式层面的建议，不支持神化单一食物或补剂。 等级已按 v0.4 综合评分重算；A 不等于个人处方建议。 |
| sleep-aging | 睡眠与健康结局 | A | 90 | 支持识别和管理睡眠问题；严重失眠、睡眠呼吸暂停需医疗评估。 等级已按 v0.4 综合评分重算；A 不等于个人处方建议。 |
| glp1-weight-cardiometabolic | GLP-1、减重与心代谢结局 | A | 90 | 这是医疗主题，不是普通抗衰保健建议；必须医生监督。 等级已按 v0.4 综合评分重算；A 不等于个人处方建议。 |
| caloric-restriction-human | 热量限制与人体衰老 | B | 90 | 不建议盲目长期极端节食；需关注营养充足和个体风险。 等级已按 v0.4 综合评分重算；A 不等于个人处方建议。 |
| time-restricted-eating | 限时进食与代谢健康 | B | 90 | 糖尿病、孕期、进食障碍或用药人群不应自行尝试。 等级已按 v0.4 综合评分重算；A 不等于个人处方建议。 |
| metformin-aging | 二甲双胍与衰老 | B | 90 | 不支持把候选证据写成个人医疗、补剂或抗衰处方。 等级已按 v0.4 综合评分重算；A 不等于个人处方建议。 |
| epigenetic-clocks | 表观遗传时钟 | B | 90 | 不支持把候选证据写成个人医疗、补剂或抗衰处方。 等级已按 v0.4 综合评分重算；A 不等于个人处方建议。 |
| microbiome-inflammaging | 微生物组与炎症性衰老 | B | 90 | 不支持把候选证据写成个人医疗、补剂或抗衰处方。 等级已按 v0.4 综合评分重算；A 不等于个人处方建议。 |

## 9. 机会与升级选择

### 方案 A：发布前最低加固版

- 对所有 A 级主题做 3-5 篇核心文献人工复核。
- 每个 A 级主题补一段“为什么是 A / 为什么不是医疗建议”。
- 把补剂矩阵标注为“方向性证据边界”，避免用户误读为购买建议。

### 方案 B：方法学增强版

- 为每个主题建立 PICO/PECO 问题。
- 系统综述用 AMSTAR 2，RCT 用 Cochrane RoB 2，观察研究用 ROBINS-I。
- 形成 claim-level grading：同一干预不同结论分开评级，例如“防晒预防光老化=A”，“防晒逆转皱纹=C/D”。

### 方案 C：高可信发布版

- 每个主题做 PRISMA-like 检索日志、纳入/排除原因、核心证据表。
- 两人独立复核前 200 条核心文献，冲突由第三人裁决。
- 导入 JCR IF 或 Scopus CiteScore/SJR 授权数据，只作为 authority signal，不覆盖 GRADE/RoB。
- 对飞书增加字段：人工复核人、复核日期、复核状态、是否锁定公开等级、争议说明。

## 10. 外部方法参考

- GRADE Working Group：https://www.gradeworkinggroup.org/ ，用于透明评估证据确定性和建议强度。
- CDC/ACIP GRADE Handbook：https://www.cdc.gov/acip-grade-handbook/ ，说明 RCT 与非随机研究的初始确定性和降级/升级逻辑。
- Cochrane RoB 2：https://methods.cochrane.org/risk-bias-2 ，RCT 风险偏倚工具。
- AMSTAR 2：https://www.bmj.com/content/358/bmj.j4008 ，系统综述方法学质量评价工具。
- NIH iCite RCR：https://support.icite.nih.gov/hc/en-us/articles/9062490125083-Metrics ，文章层级、领域和时间归一化的影响力指标。
- OpenAlex：https://openalex.org/ ，开放引用与文献元数据来源。

## 11. 结论

当前项目已经具备“公开草稿版证据图谱”的骨架和数据规模，但还没有达到医学指南或正式系统综述级别。最重要的下一步不是继续无限扩容，而是把 A/B 级主题做 claim-level 人工复核，并把补剂矩阵从方向性边界表升级为逐条证据链表。
