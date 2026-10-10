# 宇多Yul细胞/yulcell：2026 年 10 月 10 日资产整理更新

**冻结日期 / Snapshot date:** 2026-10-10<br>
**检索窗口 / Search window:** 2026/10/02..2026/10/10<br>
**本轮目标 / Goal:** 补进真正相关的新资料，同时清理重复、弱相关和放错层级的记录，让初中生也能看懂这张证据地图。

## 一句话结论 / One-Sentence Summary

这次不是“继续往里塞”。PubMed 检索找到 298 条匹配，其中 289 条是新候选；经过主题核对、去重和容量控制后，当前候选库从 11,161 条调整为 11,167 条，findings 从 2,424 条调整为 2,450 条。已满额主题以替换为主，未满额主题只在固定上限内补入合格记录。

This release adds and retires records within fixed capacity limits. Counts may rise or fall; older versions remain recoverable.

| 层级 / Layer | 上期 / Before | 旧记录退出 / Retired | 新进入 / Added | 当前 / After | 净变化 / Net |
| --- | --- | --- | --- | --- | --- |
| 候选 / Candidates | 11,161 | 66 | 72 | 11,167 | +6 |
| 发现 / Findings | 2,424 | 9 | 35 | 2,450 | +26 |

按上期与本期记录 ID 比较；“新进入”可能来自原有候选，不等于本期新发表。Actual turnover compares stable record identifiers, not first-publication dates.

## 先看懂四个数字 / Four Numbers to Understand First

| 数字 | 是什么 | 不是什么 |
| ---: | --- | --- |
| 11,167 | 当前候选文献目录 | 不是 11,167 个已证实结论 |
| 2,450 | 与主题直接相关、进入复核层的 findings | 不是全部完成全文人工复核 |
| 1,500 | 公开证据矩阵行数 | 不是论文总数 |
| 28,734 | 五张公开 CSV 的处理层行数总和 | 同一论文可跨层出现，不能当成独立论文数 |

## 本轮找到了什么 / What the Search Found

- 20 个固定主题，各运行一条有限窗口查询。
- PubMed 唯一匹配：298 条。
- 新候选：289 条；已在库中：9 条。
- 最终保留近期候选：81 条；其中进入 findings：39 条。
- 新记录仍是自动整理草稿，不能因为标成 A 或 B 就直接改成医学结论。
- 检索按 PubMed 发表日期筛选，可能包含较早在线发表、最近编入期刊的文章；不等于这些论文都是本周首次公开。

## 为什么要删 / Why Active Records Were Retired

历史视觉归档收纳 241 个旧网页和图片原件，原始体积约 157.8 MiB。每个文件都校验 SHA-256；当前与上一期入口继续保留，旧网页改为归档提示。这整理的是公开工作目录，不代表 Git 全部历史的下载体积变小。 / Verified archives preserve 241 original historical files. Current and previous releases remain accessible; this tidies the working tree, not the size of the complete Git history.

| 层级 | 退出原因 | 决定数 |
| --- | --- | --- |
| 候选层 | 超过主题容量，保留优先级更高者 | 283 |
| findings | 人体主题中的动物或细胞记录 | 9 |
| findings | 方案论文或注册计划 | 3 |
| findings | 题名与分配主题没有直接关系 | 172 |
| findings | 超过主题容量，保留优先级更高者 | 40 |
| findings | 虽命中关键词，但不属于本主题的长寿或健康寿命范围 | 44 |

“退出”只表示不再占用当前公开层的位置，不代表论文被否定。决定数包含新抓取后未通过筛选的材料，不全是旧记录被移除。每条决定都保留在 `data/archive/`，旧完整快照可从 ZIP 和 Git 历史恢复。

## 容量规则 / Capacity Rules

- 候选层：每个主题最多 600 条。
- findings：每个主题最多 200 条，不为填满而凑数。
- 证据矩阵：总计最多 1,500 条，每主题最多 100 条。
- 核心人工复核队列：每主题最多 3 条，本版共 54 条。
- 每周自动检索只能生成有上限的 intake Pull Request，不能再直接把候选推入 `main`。

完整规则：[精编与归档规则](../../docs/data-retention-and-curation-policy.md)

## 近期文献举例 / Recent Examples

这些例子只是说明本轮覆盖了哪些问题，不是疗效推荐。题名和标识已与 NCBI PubMed 核对；结论仍需全文复核。

### 社区运动：身体功能变好了，但研究没有随机对照组

人群追踪研究 / Cohort；B 级草稿。[官方来源 / PubMed 42832337](https://pubmed.ncbi.nlm.nih.gov/42832337/)

爱尔兰 ExWell 项目追踪了 1,290 名有慢性病的社区参与者，平均 69 岁。24 周后，虚弱人群的步速、起身行走和部分生活质量指标改善。它是队列的二次分析，不是随机分组试验；更虚弱的人退出也更多，留下来的参与者可能更健康。可理解为现实项目的积极信号，不能把改善全部归因于项目，也没有证明延寿。

A secondary analysis of the ExWell cohort followed 1,290 community participants with chronic conditions, mean age 69. Several functional measures improved by 24 weeks. There was no randomized comparator, and attrition was greater among frailer participants. This is an encouraging programme association, not proof of a causal effect or longer lifespan.

### 抗阻训练：体能有改善，认知与 BDNF 没有显著改善

非随机或混合分配研究 / Nonrandomized or mixed allocation；C 级草稿。[官方来源 / PubMed 42678372](https://pubmed.ncbi.nlm.nih.gov/42678372/)

研究把 30 名认知受损者随机分到两种训练组，另有 13 人非随机进入对照组，持续 8 周。两种训练组的身体功能有改善，但认知测验和 BDNF（与神经有关的一种蛋白）没有显著组间改善。训练组之间的随机化，不能使与非随机对照组的比较也变成随机试验。样本小、时间短，不能宣传为改善认知或治疗痴呆。

Thirty participants with cognitive impairment were randomized between two training groups, while 13 controls were allocated nonrandomly. After eight weeks, physical performance improved, but cognition and BDNF did not show significant between-group improvement. Randomization between training groups does not randomize their comparison with controls. This small mixed-allocation study does not establish a cognitive treatment benefit.

### 患癌前体能较好，与患癌后的较低死亡风险相关

人群追踪研究 / Cohort；B 级草稿。[官方来源 / PubMed 42849790](https://pubmed.ncbi.nlm.nih.gov/42849790/)

UK Biobank 队列分析了后来患癌的 10,462 人，随访中记录到 2,101 例死亡。患癌前估算的心肺体能越好，之后死亡风险总体越低，握力也有较弱关联。这里比较的是原本体能不同的人，不是把人随机分去训练；疾病、生活方式和选择因素仍可能影响结果。它支持关注体能的研究方向，不能保证某项运动让癌症患者多活多少年。

A UK Biobank cohort included 10,462 people who subsequently developed cancer, with 2,101 deaths. Higher estimated pre-diagnostic cardiorespiratory fitness was associated with lower later mortality; grip strength showed a weaker association. This was not a randomized exercise intervention. Confounding and selection remain possible, and the study cannot promise a survival gain from a particular exercise programme.

### 减重药与睡眠呼吸暂停：有改善信号，不能替代现有治疗

多项研究汇总 / Review & meta-analysis；B 级草稿。[官方来源 / PubMed 42837024](https://pubmed.ncbi.nlm.nih.gov/42837024/)

汇总 6 项随机试验、1,069 名中重度阻塞性睡眠呼吸暂停成人。相关治疗平均减少了每小时呼吸暂停或低通气次数，也减轻体重；不同研究结果差异很大，最低血氧等指标没有显著改善。研究主要涉及利拉鲁肽和替尔泊肽，不能推广到所有同类药。它没有证明可以替代 CPAP（气道正压通气）；处方药需医生评估，未观察到更多不良事件也不等于长期绝对安全。

Six randomized trials included 1,069 adults with moderate-to-severe obstructive sleep apnea. Liraglutide- or tirzepatide-based treatment reduced apnea-hypopnea frequency and weight, but effects varied substantially across studies. Minimum oxygen saturation did not improve significantly. This does not establish a class-wide effect or replacement for CPAP. Prescribing requires clinical assessment; a nonsignificant adverse-event difference does not establish long-term safety.

### 清除衰老细胞：人体研究仍少，不能当作成熟抗衰治疗

多项研究汇总 / Review & meta-analysis；C 级草稿。[官方来源 / PubMed 42834340](https://pubmed.ncbi.nlm.nih.gov/42834340/)

这篇系统综述纳入 6 项已完成的人体研究，另列出 1 项进行中试验。部分身体功能或衰老相关指标有早期信号，但研究混合了随机、非随机和小型探索试验，样本少、随访短。作者明确认为，临床疗效与长期安全性仍不足以确立。题名中的“逆转”不能直接理解为人已返老还童；这仍是研究方向，不是自行用药建议。

This systematic review synthesized six completed human studies and separately listed one ongoing trial. It mixed randomized, nonrandomized and pilot studies, reporting preliminary functional or biomarker signals. Small samples and short follow-up leave clinical efficacy and long-term safety unestablished. The title's reversal language does not prove human rejuvenation; these interventions remain investigational.

### 细胞的清理通路：小鼠机制发现，离人体应用还有距离

animal_study；D 级草稿。[官方来源 / PubMed 42834177](https://pubmed.ncbi.nlm.nih.gov/42834177/)

研究关注伴侣介导自噬，可粗略理解为细胞有选择地分解旧蛋白的通路。细胞与小鼠实验发现，这条通路减弱可能使免疫细胞更难清除衰老细胞；激活通路后，老年小鼠的衰老细胞负担等指标改善。它帮助解释机制，但没有人体疗效或安全性结果，也没有证明人类延寿。不能把机制图直接变成补剂功效或用药广告。

Cell and mouse experiments examined chaperone-mediated autophagy, a selective protein-degradation pathway. Its decline impaired macrophage clearance of senescent cells; activation reduced senescent-cell burden in aged mice and disease severity in a mouse fibrosis model. This is mechanistic, preclinical evidence, not a human efficacy, safety or lifespan result, and cannot substantiate a supplement claim.


## 当前等级分布 / Current Draft Grades

| A | B | C | D | E |
| ---: | ---: | ---: | ---: | ---: |
| 228 | 1,323 | 422 | 421 | 56 |

等级是排序工具，不是处方。A 表示更值得优先复核，不代表“人人应该用”。

## 20 个主题的当前体量 / Active Size by Topic

| 主题 | Topic | 候选 | findings |
| --- | --- | --- | --- |
| 自噬/线粒体自噬 | Autophagy and Mitophagy | 600 | 79 |
| 血压与健康寿命 | Blood Pressure and Healthspan | 600 | 200 |
| 热量限制与人体衰老 | Caloric Restriction in Humans | 600 | 103 |
| 心肺适能与死亡风险 | Cardiorespiratory Fitness and Mortality | 600 | 147 |
| 饮食模式与死亡风险 | Dietary Patterns and Mortality | 600 | 200 |
| 表观遗传时钟 | Epigenetic Clocks | 600 | 126 |
| GLP-1、减重与心代谢结局 | GLP-1, Weight Loss, and Cardiometabolic Outcomes | 600 | 200 |
| ITP 小鼠寿命干预 | ITP Mouse Lifespan Interventions | 179 | 11 |
| Klotho / IL-11 | Klotho / IL-11 | 600 | 77 |
| LDL-C/apoB 与心血管风险 | LDL-C/apoB and Cardiovascular Risk | 600 | 200 |
| 二甲双胍与衰老 | Metformin and Aging | 600 | 48 |
| 微生物组与炎症性衰老 | Microbiome and Inflammaging | 600 | 95 |
| NAD/NMN/NR | NAD/NMN/NR | 549 | 38 |
| 部分重编程 | Partial Reprogramming | 322 | 30 |
| 身体活动与健康寿命 | Physical Activity and Healthspan | 600 | 200 |
| 雷帕霉素/mTOR 与衰老 | Rapamycin/mTOR and Aging | 517 | 56 |
| 抗阻训练、肌肉与衰弱 | Resistance Training, Muscle, and Frailty | 600 | 185 |
| Senolytics 清除衰老细胞 | Senolytics | 600 | 55 |
| 睡眠与健康结局 | Sleep and Aging Outcomes | 600 | 200 |
| 限时进食与代谢健康 | Time-Restricted Eating and Metabolic Health | 600 | 200 |

## 本轮修正的质量问题 / Quality Fixes

- PubMed XML 解析继续限制在论文本身的 ArticleIdList，参考文献 DOI/PMCID 不会覆盖主文献标识。
- 用 NCBI 官方 E-utilities 核对全部 2,450 个 findings PMID：缺失 0，实质题名冲突 0。
- 本轮修正 findings DOI 0 个、PMCID 12 个；候选 DOI 0 个、PMCID 17 个。
- 方案论文、评论勘误、明确动物实验不再被自动抬进人体高等级层。
- 模型推算的安慰剂比较、试验中的观察性二次分析，不沿用母试验的随机对照身份；本版按更保守的独立类型标注，最高 C 级，仍待全文复核。
- 明确写作准实验、或对照组非随机分配的研究，独立标为非随机/混合分配研究，最高 C 级；不能因为一部分组间随机化，就把所有比较当作随机对照。 / Quasi-experimental and mixed-allocation studies are not fully randomized comparisons.
- 额外排除塑料老化等环境研究，以及没有老龄语境的青少年竞技训练；病例资料汇总最高按 C 级，主题等级不能放宽动物研究的 D 级上限。
- 50 张成分卡的评级沿用既有资料，本轮刷新撤稿检索、来源链接和图片；不表示 50 个成分都完成了新的全文复核。 / Ingredient grades remain provisional; refreshed counts and visuals do not imply a new full-text review of every ingredient.

## 图片与公开资产 / Visuals and Public Assets

撤稿风险最近查询于 2026-10-10，覆盖 117 个成分/主题，得到 596 条主题匹配记录、去重 540 个 PMID。这是自 2006 年起的发表日期窗口累计，不是本月新增撤稿；撤稿密度不能单独证明成分有效或无效。 / Retraction queries checked 2026-10-10: 117 targets, 596 matched rows, 540 unique PMIDs. Historical cumulative counts are not new monthly retractions or efficacy scores.

- [自包含图文报告 / Self-contained report](../../docs/october-10-public-update-2026-10.html)
- [当前、上一期与历史归档 / Asset catalog](../../docs/asset-catalog.md)
- [2026-10 研究图片 / 2026-10 images](../../docs/assets/visual-assets/2026-10/)
- [飞书 9 张长期表 / Nine stable Feishu tables](../../docs/feishu-public-assets-2026-10.md)
- [公开 CSV / Public CSV package](../../public-data/README.md)
- [精编与归档规则 / Curation policy](../../docs/data-retention-and-curation-policy.md)

## 读者边界 / Reader Boundary

这张图谱用来帮助读者区分证据强弱，不提供个人诊断、处方、剂量、停药建议、医美操作或购买推荐。动物延寿不能写成人类延寿已经证实，指标改善不能写成返老还童，研究数量多也不能写成疗效更强。
