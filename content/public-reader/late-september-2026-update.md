# 宇多Yul细胞/yulcell：2026 年 9 月下旬精编更新

**冻结日期 / Snapshot date:** 2026-09-21<br>
**检索窗口 / Search window:** 2026/09/14..2026/09/21<br>
**本轮目标 / Goal:** 补进真正相关的新资料，同时清理重复、弱相关和放错层级的记录，让初中生也能看懂这张证据地图。

## 一句话结论 / One-Sentence Summary

这次不是“继续往里塞”。PubMed 检索找到 386 条匹配，其中 379 条是新候选；经过主题核对、去重和容量控制后，当前候选库从 11,132 条调整为 11,141 条，findings 从 2,291 条调整为 2,339 条。已满额主题以替换为主，未满额主题只在固定上限内补入合格记录。

This release adds and retires records within fixed capacity limits. Counts may rise or fall; older versions remain recoverable.

## 先看懂四个数字 / Four Numbers to Understand First

| 数字 | 是什么 | 不是什么 |
| ---: | --- | --- |
| 11,141 | 当前候选文献目录 | 不是 11,141 个已证实结论 |
| 2,339 | 与主题直接相关、进入复核层的 findings | 不是全部完成全文人工复核 |
| 1,500 | 公开证据矩阵行数 | 不是论文总数 |
| 28,460 | 五张公开 CSV 的处理层行数总和 | 同一论文可跨层出现，不能当成独立论文数 |

## 本轮找到了什么 / What the Search Found

- 20 个固定主题，各运行一条有限窗口查询。
- PubMed 唯一匹配：386 条。
- 新候选：379 条；已在库中：7 条。
- 最终保留近期候选：116 条；其中进入 findings：62 条。
- 新记录仍是自动整理草稿，不能因为标成 A 或 B 就直接改成医学结论。

## 为什么要删 / Why Active Records Were Retired

| 层级 | 退出原因 | 决定数 |
| --- | --- | --- |
| 候选层 | 题名显示不是结果论文 | 2 |
| 候选层 | 超过主题容量，保留优先级更高者 | 368 |
| findings | 题名显示不是结果论文 | 2 |
| findings | 人体主题中的动物或细胞记录 | 4 |
| findings | 方案论文或注册计划 | 7 |
| findings | 题名与分配主题没有直接关系 | 198 |
| findings | 超过主题容量，保留优先级更高者 | 65 |
| findings | 虽命中关键词，但不属于本主题的长寿或健康寿命范围 | 61 |

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

| PMID | 主题 | 研究类型草稿 | 等级草稿 | 怎么理解 |
| --- | --- | --- | --- | --- |
| [42754260](https://pubmed.ncbi.nlm.nih.gov/42754260/) | 身体活动与健康寿命 | 多项研究汇总 / Review & meta-analysis | A | 冠心病患者的运动康复：心梗和住院更少。107 项试验、26,886 名冠心病患者。运动康复减少心梗和住院；短期总死亡的区间上限碰到无差异，不能说人人运动都能确定延寿。适用的是患者康复，需要个体评估。 / In 107 trials of coronary heart disease, rehabilitation reduced myocardial infarction and hospitalisation. Short-term all-cause mortality remained borderline; this is patient rehabilitation, not proof of universal lifespan extension. |
| [42742033](https://pubmed.ncbi.nlm.nih.gov/42742033/) | 心肺适能与死亡风险 | 多项研究汇总 / Review & meta-analysis | A | 卒中后的心肺训练：功能小幅改善，未见死亡减少。53 项试验、2,672 名卒中患者。心肺能力和步速可能小幅改善，但改善是否大到患者能明显感受到仍不确定；随访内未见死亡或再次心脑血管事件减少。功能进步不能改写成延寿。 / Across 53 stroke trials, fitness and walking gains were small and their clinical importance uncertain. Mortality and secondary vascular events were not reduced within follow-up. |
| [42744658](https://pubmed.ncbi.nlm.nih.gov/42744658/) | 身体活动与健康寿命 | 多项研究汇总 / Review & meta-analysis | B | 癌症照护中的结构化运动：生存获益有中等确定性信号。21 项随机试验的汇总中，总生存等结果有改善信号，作者评为中等确定性；不同结局来自不同试验子集，肿瘤类型和方案也不同。运动是照护的一部分，不能替代抗癌治疗。 / A synthesis of 21 randomised trials found moderate-certainty survival signals. Endpoints used different trial subsets and varied cancer settings; exercise is adjunctive care, not a replacement for cancer treatment. |
| [42744960](https://pubmed.ncbi.nlm.nih.gov/42744960/) | 饮食模式与死亡风险 | 多项研究汇总 / Review & meta-analysis | B | 地中海饮食与癌症风险：观察到关联，不等于证明因果。34 项观察研究、约 429 万人。较高的地中海饮食依从性与部分癌症风险较低相关；饮食多靠自报，部分结果差异较大。人数多也不能消除混杂，更不能推成某种食物或补剂防癌。 / Thirty-four observational studies linked Mediterranean diet adherence with lower risks of selected cancers. Self-reported diet, confounding and substantial heterogeneity limit causal interpretation. |
| [42744622](https://pubmed.ncbi.nlm.nih.gov/42744622/) | 睡眠与健康结局 | 人群追踪研究 / Cohort | B | 睡得较久与死亡风险相关，不表示少睡会更长寿。台湾 3,305 人随访中位 30.8 年，长睡眠与总死亡风险较高相关；心血管死亡未见显著差异，短睡眠组也未见显著关联。疾病可能同时影响睡眠和死亡，不能据此劝人刻意少睡。 / In a 3,305-person Taiwanese cohort, long sleep was associated with all-cause but not significantly with cardiovascular mortality. Short sleep associations were not significant; deliberately shortening sleep is not supported. |
| [42752289](https://pubmed.ncbi.nlm.nih.gov/42752289/) | 抗阻训练、肌肉与衰弱 | 临床试验 / Clinical trial | B | 98 人抗阻训练研究：功能与机制线索需要分开读。98 名有骨质疏松和肌肉萎缩的老年患者接受随机分组，论文另有细胞实验。摘要提示肌骨功能与 GLP-1/MSTN 通路变化，但仍需全文核对临床效果大小；不能把自身激素变化说成 GLP-1 药物的效果。 / A 98-person trial in older patients combined clinical and cell experiments. Clinical effect sizes need full-text review; endogenous GLP-1 pathway changes do not demonstrate an effect of GLP-1 medication. |

## 当前等级分布 / Current Draft Grades

| A | B | C | D | E |
| ---: | ---: | ---: | ---: | ---: |
| 226 | 1,278 | 417 | 363 | 55 |

等级是排序工具，不是处方。A 表示更值得优先复核，不代表“人人应该用”。

## 20 个主题的当前体量 / Active Size by Topic

| 主题 | Topic | 候选 | findings |
| --- | --- | --- | --- |
| 自噬/线粒体自噬 | Autophagy and Mitophagy | 600 | 64 |
| 血压与健康寿命 | Blood Pressure and Healthspan | 600 | 189 |
| 热量限制与人体衰老 | Caloric Restriction in Humans | 600 | 102 |
| 心肺适能与死亡风险 | Cardiorespiratory Fitness and Mortality | 600 | 142 |
| 饮食模式与死亡风险 | Dietary Patterns and Mortality | 600 | 200 |
| 表观遗传时钟 | Epigenetic Clocks | 600 | 118 |
| GLP-1、减重与心代谢结局 | GLP-1, Weight Loss, and Cardiometabolic Outcomes | 600 | 200 |
| ITP 小鼠寿命干预 | ITP Mouse Lifespan Interventions | 179 | 11 |
| Klotho / IL-11 | Klotho / IL-11 | 600 | 76 |
| LDL-C/apoB 与心血管风险 | LDL-C/apoB and Cardiovascular Risk | 600 | 195 |
| 二甲双胍与衰老 | Metformin and Aging | 600 | 46 |
| 微生物组与炎症性衰老 | Microbiome and Inflammaging | 600 | 81 |
| NAD/NMN/NR | NAD/NMN/NR | 534 | 37 |
| 部分重编程 | Partial Reprogramming | 318 | 30 |
| 身体活动与健康寿命 | Physical Activity and Healthspan | 600 | 200 |
| 雷帕霉素/mTOR 与衰老 | Rapamycin/mTOR and Aging | 510 | 55 |
| 抗阻训练、肌肉与衰弱 | Resistance Training, Muscle, and Frailty | 600 | 144 |
| Senolytics 清除衰老细胞 | Senolytics | 600 | 49 |
| 睡眠与健康结局 | Sleep and Aging Outcomes | 600 | 200 |
| 限时进食与代谢健康 | Time-Restricted Eating and Metabolic Health | 600 | 200 |

## 本轮修正的质量问题 / Quality Fixes

- PubMed XML 解析继续限制在论文本身的 ArticleIdList，参考文献 DOI/PMCID 不会覆盖主文献标识。
- 用 NCBI 官方 E-utilities 核对全部 2,339 个 findings PMID：缺失 0，实质题名冲突 0。
- 本轮修正 findings DOI 0 个、PMCID 9 个；候选 DOI 0 个、PMCID 18 个。
- 方案论文、评论勘误、明确动物实验不再被自动抬进人体高等级层。
- 额外排除塑料老化等环境研究，以及没有老龄语境的青少年竞技训练；病例资料汇总最高按 C 级，主题等级不能放宽动物研究的 D 级上限。
- 50 张成分卡的评级沿用既有资料，本轮刷新撤稿检索、来源链接和图片；不表示 50 个成分都完成了新的全文复核。 / Ingredient grades remain provisional; refreshed counts and visuals do not imply a new full-text review of every ingredient.

## 图片与公开资产 / Visuals and Public Assets

撤稿风险最近查询于 2026-09-21，覆盖 117 个成分/主题，得到 594 条主题匹配记录、去重 538 个 PMID。这是自 2006 年起的发表日期窗口累计，不是本月新增撤稿；撤稿密度不能单独证明成分有效或无效。 / Retraction queries checked 2026-09-21: 117 targets, 594 matched rows, 538 unique PMIDs. Historical cumulative counts are not new monthly retractions or efficacy scores.

- [自包含图文报告 / Self-contained report](../../docs/late-september-public-update-2026-09.html)
- [2026-09 研究图片 / 2026-09 images](../../docs/assets/visual-assets/2026-09/)
- [飞书 9 张长期表 / Nine stable Feishu tables](../../docs/feishu-public-assets-2026-09.md)
- [公开 CSV / Public CSV package](../../public-data/README.md)
- [精编与归档规则 / Curation policy](../../docs/data-retention-and-curation-policy.md)

## 读者边界 / Reader Boundary

这张图谱用来帮助读者区分证据强弱，不提供个人诊断、处方、剂量、停药建议、医美操作或购买推荐。动物延寿不能写成人类延寿已经证实，指标改善不能写成返老还童，研究数量多也不能写成疗效更强。
