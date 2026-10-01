# 宇多Yul细胞/yulcell：2026 年 10 月初整理更新

**冻结日期 / Snapshot date:** 2026-10-01<br>
**检索窗口 / Search window:** 2026/09/22..2026/10/01<br>
**本轮目标 / Goal:** 补进真正相关的新资料，同时清理重复、弱相关和放错层级的记录，让初中生也能看懂这张证据地图。

## 一句话结论 / One-Sentence Summary

这次不是“继续往里塞”。PubMed 检索找到 1,216 条匹配，其中 1,129 条是新候选；经过主题核对、去重和容量控制后，当前候选库从 11,141 条调整为 11,161 条，findings 从 2,339 条调整为 2,424 条。已满额主题以替换为主，未满额主题只在固定上限内补入合格记录。

This release adds and retires records within fixed capacity limits. Counts may rise or fall; older versions remain recoverable.

## 先看懂四个数字 / Four Numbers to Understand First

| 数字 | 是什么 | 不是什么 |
| ---: | --- | --- |
| 11,161 | 当前候选文献目录 | 不是 11,161 个已证实结论 |
| 2,424 | 与主题直接相关、进入复核层的 findings | 不是全部完成全文人工复核 |
| 1,500 | 公开证据矩阵行数 | 不是论文总数 |
| 28,670 | 五张公开 CSV 的处理层行数总和 | 同一论文可跨层出现，不能当成独立论文数 |

## 本轮找到了什么 / What the Search Found

- 20 个固定主题，各运行一条有限窗口查询。
- PubMed 唯一匹配：1,216 条。
- 新候选：1,129 条；已在库中：87 条。
- 最终保留近期候选：307 条；其中进入 findings：161 条。
- 新记录仍是自动整理草稿，不能因为标成 A 或 B 就直接改成医学结论。
- 检索按 PubMed 发表日期筛选，可能包含较早在线发表、最近编入期刊的文章；不等于这些论文都是本周首次公开。

## 为什么要删 / Why Active Records Were Retired

历史视觉归档收纳 182 个旧网页和图片原件，原始体积约 126.5 MiB。每个文件都校验 SHA-256；当前与上一期入口继续保留，旧网页改为归档提示。这整理的是公开工作目录，不代表 Git 全部历史的下载体积变小。 / Verified archives preserve 182 original historical files. Current and previous releases remain accessible; this tidies the working tree, not the size of the complete Git history.

| 层级 | 退出原因 | 决定数 |
| --- | --- | --- |
| 候选层 | 题名显示不是结果论文 | 13 |
| 候选层 | 超过主题容量，保留优先级更高者 | 1,096 |
| findings | 题名显示不是结果论文 | 13 |
| findings | 人体主题中的动物或细胞记录 | 16 |
| findings | 方案论文或注册计划 | 10 |
| findings | 题名与分配主题没有直接关系 | 675 |
| findings | 超过主题容量，保留优先级更高者 | 186 |
| findings | 虽命中关键词，但不属于本主题的长寿或健康寿命范围 | 200 |

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
| [42773062](https://pubmed.ncbi.nlm.nih.gov/42773062/) | 饮食模式与死亡风险 | 多项研究汇总 / Review & meta-analysis | A | 超加工食品与慢病风险：人数很多，仍是关联证据。51 个前瞻性队列、约 882 万人的汇总，发现吃较多超加工食品与多种慢病及死亡风险较高相关。作者评为低到中等确定性；饮食测量误差和其他生活习惯仍可能影响结果。不能改写成某一种食品一定致病。 / A synthesis of 51 prospective cohorts linked higher ultra-processed food intake with multiple chronic outcomes. Low-to-moderate certainty and confounding limit causal claims about individual foods. |
| [42551769](https://pubmed.ncbi.nlm.nih.gov/42551769/) | 抗阻训练、肌肉与衰弱 | 多项研究汇总 / Review & meta-analysis | B | 线上辅助运动对肌少症可能有帮助，但不是已证实延寿。14 项试验、927 名肌少症老人，数字化运动干预对力量、平衡和行走有改善信号，但生活质量未见明确改善。证据确定性从极低到中等，部分结果在新场景中可能不同；不能把功能改善写成寿命延长。 / Fourteen trials in 927 older adults with sarcopenia suggest functional benefits from digital exercise, with no clear quality-of-life improvement. Very-low-to-moderate certainty and variable effects do not establish lifespan extension. |
| [42730869](https://pubmed.ncbi.nlm.nih.gov/42730869/) | GLP-1、减重与心代谢结局 | 多项研究汇总 / Review & meta-analysis | A | GLP-1 类药物与瘦体重：身体成分变化不等于功能受损。60 篇临床资料的汇总提示瘦体重下降，证据确定性较低，可能与减重有关。瘦体重不只包含肌肉；是否带来力量或日常活动能力下降仍不清楚。骨骼和关节未见明确效应也不等于证明完全无风险，不能据此自行停药。 / This review found lower lean mass with GLP-1 therapies, with low certainty and uncertain functional consequences. Lean mass is not muscle alone; unclear bone or joint effects do not establish absence of risk. |
| [42786612](https://pubmed.ncbi.nlm.nih.gov/42786612/) | 睡眠与健康结局 | 临床试验 / Clinical trial | B | 卒中合并睡眠呼吸暂停：主要心脏指标未见明确组间差异。71 人随机试验中，CPAP 治疗的 12 个月左心房容积指标变化，与对照组没有显著差异。随时间变化的轨迹和部分功能结果出现信号，但不能用这些次要发现掩盖主要比较不显著。结果只适用于研究人群，不是自行使用设备的建议。 / In 71 stroke patients with sleep apnea, the 12-month change in left atrial volume did not differ significantly between groups. Trajectory and functional signals should not obscure this main comparison or be generalized beyond the studied population. |
| [42782098](https://pubmed.ncbi.nlm.nih.gov/42782098/) | 抗阻训练、肌肉与衰弱 | 观察性二次分析 / Observational secondary analysis | C | 肌少症与癌症治疗风险：用过试验数据，不代表这个比较是随机的。研究只分析母试验常规照护组中的 161 名高龄晚期癌症患者，观察到肌少症与严重毒性和部分生存结局相关。患者不是被随机分成有、无肌少症两组，所以这是观察性二次分析，不能证明补肌肉就能减少死亡。 / This analysis used 161 usual-care participants from a parent trial. Sarcopenia was not randomized, so associations with toxicity and survival are observational and do not establish that increasing muscle reduces mortality. |
| [41940793](https://pubmed.ncbi.nlm.nih.gov/41940793/) | GLP-1、减重与心代谢结局 | 模型间接比较 / Indirect model analysis | C | 替尔泊肽的推算对照：模型结果不等于真实安慰剂组。作者借助两项既有试验，调整人群差异后推算替尔泊肽相对安慰剂的心血管结果。这是间接、探索性比较，不是新开展的替尔泊肽对安慰剂随机试验；结果依赖模型假设，不能说已经证明健康人用药可延寿。 / An exploratory indirect comparison combined two trials to estimate an imputed placebo contrast. Model assumptions matter; this is not a new randomized tirzepatide-placebo trial or evidence of lifespan extension in healthy people. |

## 当前等级分布 / Current Draft Grades

| A | B | C | D | E |
| ---: | ---: | ---: | ---: | ---: |
| 228 | 1,308 | 415 | 419 | 54 |

等级是排序工具，不是处方。A 表示更值得优先复核，不代表“人人应该用”。

## 20 个主题的当前体量 / Active Size by Topic

| 主题 | Topic | 候选 | findings |
| --- | --- | --- | --- |
| 自噬/线粒体自噬 | Autophagy and Mitophagy | 600 | 74 |
| 血压与健康寿命 | Blood Pressure and Healthspan | 600 | 200 |
| 热量限制与人体衰老 | Caloric Restriction in Humans | 600 | 102 |
| 心肺适能与死亡风险 | Cardiorespiratory Fitness and Mortality | 600 | 142 |
| 饮食模式与死亡风险 | Dietary Patterns and Mortality | 600 | 200 |
| 表观遗传时钟 | Epigenetic Clocks | 600 | 125 |
| GLP-1、减重与心代谢结局 | GLP-1, Weight Loss, and Cardiometabolic Outcomes | 600 | 200 |
| ITP 小鼠寿命干预 | ITP Mouse Lifespan Interventions | 179 | 11 |
| Klotho / IL-11 | Klotho / IL-11 | 600 | 77 |
| LDL-C/apoB 与心血管风险 | LDL-C/apoB and Cardiovascular Risk | 600 | 200 |
| 二甲双胍与衰老 | Metformin and Aging | 600 | 47 |
| 微生物组与炎症性衰老 | Microbiome and Inflammaging | 600 | 91 |
| NAD/NMN/NR | NAD/NMN/NR | 546 | 38 |
| 部分重编程 | Partial Reprogramming | 321 | 30 |
| 身体活动与健康寿命 | Physical Activity and Healthspan | 600 | 200 |
| 雷帕霉素/mTOR 与衰老 | Rapamycin/mTOR and Aging | 515 | 56 |
| 抗阻训练、肌肉与衰弱 | Resistance Training, Muscle, and Frailty | 600 | 179 |
| Senolytics 清除衰老细胞 | Senolytics | 600 | 52 |
| 睡眠与健康结局 | Sleep and Aging Outcomes | 600 | 200 |
| 限时进食与代谢健康 | Time-Restricted Eating and Metabolic Health | 600 | 200 |

## 本轮修正的质量问题 / Quality Fixes

- PubMed XML 解析继续限制在论文本身的 ArticleIdList，参考文献 DOI/PMCID 不会覆盖主文献标识。
- 用 NCBI 官方 E-utilities 核对全部 2,424 个 findings PMID：缺失 0，实质题名冲突 0。
- 本轮修正 findings DOI 0 个、PMCID 10 个；候选 DOI 0 个、PMCID 44 个。
- 方案论文、评论勘误、明确动物实验不再被自动抬进人体高等级层。
- 模型推算的安慰剂比较、试验中的观察性二次分析，不沿用母试验的随机对照身份；本版按更保守的独立类型标注，最高 C 级，仍待全文复核。
- 额外排除塑料老化等环境研究，以及没有老龄语境的青少年竞技训练；病例资料汇总最高按 C 级，主题等级不能放宽动物研究的 D 级上限。
- 50 张成分卡的评级沿用既有资料，本轮刷新撤稿检索、来源链接和图片；不表示 50 个成分都完成了新的全文复核。 / Ingredient grades remain provisional; refreshed counts and visuals do not imply a new full-text review of every ingredient.

## 图片与公开资产 / Visuals and Public Assets

撤稿风险最近查询于 2026-10-01，覆盖 117 个成分/主题，得到 595 条主题匹配记录、去重 539 个 PMID。这是自 2006 年起的发表日期窗口累计，不是本月新增撤稿；撤稿密度不能单独证明成分有效或无效。 / Retraction queries checked 2026-10-01: 117 targets, 595 matched rows, 539 unique PMIDs. Historical cumulative counts are not new monthly retractions or efficacy scores.

- [自包含图文报告 / Self-contained report](../../docs/october-public-update-2026-10.html)
- [当前、上一期与历史归档 / Asset catalog](../../docs/asset-catalog.md)
- [2026-10 研究图片 / 2026-10 images](../../docs/assets/visual-assets/2026-10/)
- [飞书 9 张长期表 / Nine stable Feishu tables](../../docs/feishu-public-assets-2026-10.md)
- [公开 CSV / Public CSV package](../../public-data/README.md)
- [精编与归档规则 / Curation policy](../../docs/data-retention-and-curation-policy.md)

## 读者边界 / Reader Boundary

这张图谱用来帮助读者区分证据强弱，不提供个人诊断、处方、剂量、停药建议、医美操作或购买推荐。动物延寿不能写成人类延寿已经证实，指标改善不能写成返老还童，研究数量多也不能写成疗效更强。
