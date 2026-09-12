# 宇多Yul细胞/yulcell：2026 年 9 月中旬精编更新

**冻结日期 / Snapshot date:** 2026-09-13<br>
**检索窗口 / Search window:** 2026/08/29..2026/09/13<br>
**本轮目标 / Goal:** 补进真正相关的新资料，同时清理重复、弱相关和放错层级的记录，让初中生也能看懂这张证据地图。

## 一句话结论 / One-Sentence Summary

这次不是“继续往里塞”。PubMed 检索找到 1,191 条匹配，其中 1,124 条是新候选；经过主题核对、去重和容量控制后，当前候选库从 11,104 条调整为 11,132 条，findings 从 3,039 条调整为 2,291 条。已满额主题以替换为主，未满额主题只在固定上限内补入合格记录。

This release adds and retires records within fixed capacity limits. Counts may rise or fall; older versions remain recoverable.

## 先看懂四个数字 / Four Numbers to Understand First

| 数字 | 是什么 | 不是什么 |
| ---: | --- | --- |
| 11,132 | 当前候选文献目录 | 不是 11,132 个已证实结论 |
| 2,291 | 与主题直接相关、进入复核层的 findings | 不是全部完成全文人工复核 |
| 1,500 | 公开证据矩阵行数 | 不是论文总数 |
| 28,346 | 五张公开 CSV 的处理层行数总和 | 同一论文可跨层出现，不能当成独立论文数 |

## 本轮找到了什么 / What the Search Found

- 20 个固定主题，各运行一条有限窗口查询。
- PubMed 唯一匹配：1,191 条。
- 新候选：1,124 条；已在库中：67 条。
- 最终保留近期候选：350 条；其中进入 findings：175 条。
- 新记录仍是自动整理草稿，不能因为标成 A 或 B 就直接改成医学结论。

## 为什么要删 / Why Active Records Were Retired

| 层级 | 退出原因 | 决定数 |
| --- | --- | --- |
| 候选层 | 重复记录 | 1 |
| 候选层 | 题名显示不是结果论文 | 19 |
| 候选层 | 超过主题容量，保留优先级更高者 | 1,076 |
| findings | 题名显示不是结果论文 | 6 |
| findings | 人体主题中的动物或细胞记录 | 32 |
| findings | 方案论文或注册计划 | 10 |
| findings | 题名与分配主题没有直接关系 | 682 |
| findings | 超过主题容量，保留优先级更高者 | 194 |
| findings | 虽命中关键词，但不属于本主题的长寿或健康寿命范围 | 988 |

“退出”只表示不再占用当前公开层的位置，不代表论文被否定。每条决定都保留在 `data/archive/`，旧完整快照可从 ZIP 和 Git 历史恢复。

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
| [42700006](https://pubmed.ncbi.nlm.nih.gov/42700006/) | 抗阻训练、肌肉与衰弱 | systematic_review_or_meta_analysis | A | 力量训练、乳清蛋白与 HMB 对老年肌少症的系统综述与 Meta 分析；组合干预不能拆开解释为某一种补剂单独有效。 |
| [42711120](https://pubmed.ncbi.nlm.nih.gov/42711120/) | 身体活动与健康寿命 | human_cohort | B | 设备记录的步数与步行强度和较低死亡风险相关；这是前瞻性观察研究，不能据此给每个人设定同一个步数处方。 |
| [42373047](https://pubmed.ncbi.nlm.nih.gov/42373047/) | 饮食模式与死亡风险 | systematic_review_or_meta_analysis | B | 八个欧美队列的个体数据 Meta 分析观察饮食与老龄期认知的关系；饮食模式证据不能改写成单一食物或补剂的疗效。 |
| [42060953](https://pubmed.ncbi.nlm.nih.gov/42060953/) | 睡眠与健康结局 | human_cohort | C | 七年纵向研究观察失眠严重程度与痴呆风险；关联不证明失眠本身就是唯一原因，也不替代睡眠疾病评估。 |
| [42586098](https://pubmed.ncbi.nlm.nih.gov/42586098/) | 血压与健康寿命 | systematic_review_or_meta_analysis | B | 脑出血后二级预防降压的个体数据 Meta 分析；研究对象和治疗场景特殊，不能套用成普通人的自行降压方案。 |
| [42410309](https://pubmed.ncbi.nlm.nih.gov/42410309/) | GLP-1、减重与心代谢结局 | systematic_review_or_meta_analysis | A | 超重或肥胖人群中替尔泊肽与 GLP-1 受体激动剂心血管结局的 Meta 分析；属于处方药比较，必须由医生结合适应证和风险评估。 |

## 当前等级分布 / Current Draft Grades

| A | B | C | D | E |
| ---: | ---: | ---: | ---: | ---: |
| 223 | 1,270 | 425 | 326 | 47 |

等级是排序工具，不是处方。A 表示更值得优先复核，不代表“人人应该用”。

## 20 个主题的当前体量 / Active Size by Topic

| 主题 | Topic | 候选 | findings |
| --- | --- | --- | --- |
| 自噬/线粒体自噬 | Autophagy and Mitophagy | 600 | 61 |
| 血压与健康寿命 | Blood Pressure and Healthspan | 600 | 179 |
| 热量限制与人体衰老 | Caloric Restriction in Humans | 600 | 102 |
| 心肺适能与死亡风险 | Cardiorespiratory Fitness and Mortality | 600 | 141 |
| 饮食模式与死亡风险 | Dietary Patterns and Mortality | 600 | 200 |
| 表观遗传时钟 | Epigenetic Clocks | 600 | 111 |
| GLP-1、减重与心代谢结局 | GLP-1, Weight Loss, and Cardiometabolic Outcomes | 600 | 200 |
| ITP 小鼠寿命干预 | ITP Mouse Lifespan Interventions | 179 | 11 |
| Klotho / IL-11 | Klotho / IL-11 | 600 | 76 |
| LDL-C/apoB 与心血管风险 | LDL-C/apoB and Cardiovascular Risk | 600 | 188 |
| 二甲双胍与衰老 | Metformin and Aging | 600 | 46 |
| 微生物组与炎症性衰老 | Microbiome and Inflammaging | 600 | 76 |
| NAD/NMN/NR | NAD/NMN/NR | 529 | 37 |
| 部分重编程 | Partial Reprogramming | 318 | 30 |
| 身体活动与健康寿命 | Physical Activity and Healthspan | 600 | 200 |
| 雷帕霉素/mTOR 与衰老 | Rapamycin/mTOR and Aging | 506 | 54 |
| 抗阻训练、肌肉与衰弱 | Resistance Training, Muscle, and Frailty | 600 | 130 |
| Senolytics 清除衰老细胞 | Senolytics | 600 | 49 |
| 睡眠与健康结局 | Sleep and Aging Outcomes | 600 | 200 |
| 限时进食与代谢健康 | Time-Restricted Eating and Metabolic Health | 600 | 200 |

## 本轮修正的质量问题 / Quality Fixes

- PubMed XML 解析继续限制在论文本身的 ArticleIdList，参考文献 DOI/PMCID 不会覆盖主文献标识。
- 用 NCBI 官方 E-utilities 核对全部 2,291 个 findings PMID：缺失 0，实质题名冲突 0。
- 本轮修正 findings DOI 0 个、PMCID 9 个；候选 DOI 0 个、PMCID 62 个。
- 方案论文、评论勘误、明确动物实验不再被自动抬进人体高等级层。

## 图片与公开资产 / Visuals and Public Assets

- [自包含图文报告 / Self-contained report](../../docs/mid-september-public-update-2026-09.html)
- [2026-09 研究图片 / 2026-09 images](../../docs/assets/visual-assets/2026-09/)
- [飞书 9 张长期表 / Nine stable Feishu tables](../../docs/feishu-public-assets-2026-09.md)
- [公开 CSV / Public CSV package](../../public-data/README.md)
- [精编与归档规则 / Curation policy](../../docs/data-retention-and-curation-policy.md)

## 读者边界 / Reader Boundary

这张图谱用来帮助读者区分证据强弱，不提供个人诊断、处方、剂量、停药建议、医美操作或购买推荐。动物延寿不能写成人类延寿已经证实，指标改善不能写成返老还童，研究数量多也不能写成疗效更强。
