# 宇多Yul细胞/yulcell：2026 年 8 月中期精编更新

**冻结日期 / Snapshot date:** 2026-08-09<br>
**检索窗口 / Search window:** 2026/07/30..2026/08/09<br>
**本轮目标 / Goal:** 补进真正相关的新资料，同时清理重复、弱相关和放错层级的记录，让初中生也能看懂这张证据地图。

## 一句话结论 / One-Sentence Summary

这次不是“继续往里塞”。PubMed 检索找到 1,042 条匹配，其中 834 条是新候选；经过主题核对、去重和容量控制后，当前候选库从 16,547 条精简为 11,079 条，findings 从 6,000 条精简为 2,966 条。

This release adds recent PubMed records while deliberately shrinking the active library. Smaller counts mean less noise, not lost history.

## 先看懂四个数字 / Four Numbers to Understand First

| 数字 | 是什么 | 不是什么 |
| ---: | --- | --- |
| 11,079 | 当前候选文献目录 | 不是 11,079 个已证实结论 |
| 2,966 | 与主题直接相关、进入复核层的 findings | 不是全部完成全文人工复核 |
| 1,500 | 公开证据矩阵行数 | 不是论文总数 |
| 29,590 | 五张公开 CSV 的处理层行数总和 | 同一论文可跨层出现，不能当成独立论文数 |

## 本轮找到了什么 / What the Search Found

- 20 个固定主题，各运行一条有限窗口查询。
- PubMed 唯一匹配：1,042 条。
- 新候选：834 条；已在库中：208 条。
- 最终保留近期候选：303 条；其中进入 findings：211 条。
- 新记录仍是自动整理草稿，不能因为标成 A 或 B 就直接改成医学结论。

## 为什么要删 / Why Active Records Were Retired

| 层级 | 退出原因 | 决定数 |
| --- | --- | --- |
| 候选层 | 重复记录 | 101 |
| 候选层 | 题名显示不是结果论文 | 102 |
| 候选层 | 超过主题容量，保留优先级更高者 | 5,993 |
| 候选层 | 无法映射到当前 20 个主题 | 106 |
| findings | 候选已作为重复项退出 | 5 |
| findings | 评论、社论或勘误 | 73 |
| findings | 人体主题中的动物或细胞记录 | 65 |
| findings | 方案论文或注册计划 | 103 |
| findings | 题名与分配主题没有直接关系 | 3,431 |
| findings | 超过主题容量，保留优先级更高者 | 350 |

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
| [42543470](https://pubmed.ncbi.nlm.nih.gov/42543470/) | 心肺适能与死亡风险 | systematic_review_or_meta_analysis | A | 冠心病患者有氧加抗阻训练的系统综述与 Meta 分析；属于特定患者康复场景，不能直接外推到所有人。 |
| [42219271](https://pubmed.ncbi.nlm.nih.gov/42219271/) | GLP-1、减重与心代谢结局 | systematic_review_or_meta_analysis | A | 2 型糖尿病人群 GLP-1 类治疗与心血管结局的网络 Meta 分析；药物问题必须由医生评估。 |
| [42044540](https://pubmed.ncbi.nlm.nih.gov/42044540/) | 饮食模式与死亡风险 | systematic_review_or_meta_analysis | B | 地中海饮食与肿瘤一级预防的系统综述；饮食模式证据不等于某一种补剂有效。 |
| [42217831](https://pubmed.ncbi.nlm.nih.gov/42217831/) | 身体活动与健康寿命 | systematic_review_or_meta_analysis | B | 久坐、看电视时间与全因死亡风险的综述之综述；观察到关联不等于单篇研究证明因果。 |
| [42212393](https://pubmed.ncbi.nlm.nih.gov/42212393/) | 血压与健康寿命 | human_randomized_or_clinical_trial | C | 取栓成功后强化与常规降压的一年结局；研究对象很特殊，不能套用为普通人的降压方案。 |
| [42545663](https://pubmed.ncbi.nlm.nih.gov/42545663/) | 身体活动与健康寿命 | human_randomized_or_clinical_trial | B | 老年人运动获益是否达到临床意义的随机试验随访分析；仍需全文复核效果大小和适用人群。 |

## 当前等级分布 / Current Draft Grades

| A | B | C | D | E |
| ---: | ---: | ---: | ---: | ---: |
| 228 | 1,513 | 721 | 456 | 48 |

等级是排序工具，不是处方。A 表示更值得优先复核，不代表“人人应该用”。

## 20 个主题的当前体量 / Active Size by Topic

| 主题 | Topic | 候选 | findings |
| --- | --- | --- | --- |
| 自噬/线粒体自噬 | Autophagy and Mitophagy | 600 | 115 |
| 血压与健康寿命 | Blood Pressure and Healthspan | 600 | 158 |
| 热量限制与人体衰老 | Caloric Restriction in Humans | 600 | 104 |
| 心肺适能与死亡风险 | Cardiorespiratory Fitness and Mortality | 600 | 134 |
| 饮食模式与死亡风险 | Dietary Patterns and Mortality | 600 | 200 |
| 表观遗传时钟 | Epigenetic Clocks | 600 | 99 |
| GLP-1、减重与心代谢结局 | GLP-1, Weight Loss, and Cardiometabolic Outcomes | 600 | 200 |
| ITP 小鼠寿命干预 | ITP Mouse Lifespan Interventions | 179 | 11 |
| Klotho / IL-11 | Klotho / IL-11 | 600 | 183 |
| LDL-C/apoB 与心血管风险 | LDL-C/apoB and Cardiovascular Risk | 600 | 152 |
| 二甲双胍与衰老 | Metformin and Aging | 600 | 200 |
| 微生物组与炎症性衰老 | Microbiome and Inflammaging | 600 | 200 |
| NAD/NMN/NR | NAD/NMN/NR | 505 | 122 |
| 部分重编程 | Partial Reprogramming | 305 | 29 |
| 身体活动与健康寿命 | Physical Activity and Healthspan | 600 | 200 |
| 雷帕霉素/mTOR 与衰老 | Rapamycin/mTOR and Aging | 490 | 105 |
| 抗阻训练、肌肉与衰弱 | Resistance Training, Muscle, and Frailty | 600 | 200 |
| Senolytics 清除衰老细胞 | Senolytics | 600 | 154 |
| 睡眠与健康结局 | Sleep and Aging Outcomes | 600 | 200 |
| 限时进食与代谢健康 | Time-Restricted Eating and Metabolic Health | 600 | 200 |

## 本轮修正的质量问题 / Quality Fixes

- 修正 PubMed XML 解析范围，参考文献 DOI/PMCID 不再覆盖论文本身的标识。
- 用 NCBI 官方 E-utilities 核对全部 2,966 个 findings PMID：缺失 0，实质题名冲突 0。
- 修正 findings DOI 1,395 个、PMCID 1,814 个；修复后候选表与 findings DOI 不一致为 0。
- 方案论文、评论勘误、明确动物实验不再被自动抬进人体高等级层。

## 图片与公开资产 / Visuals and Public Assets

- [自包含图文报告 / Self-contained report](../../docs/mid-august-public-update-2026-08.html)
- [8 月研究图片 / August images](../../docs/assets/visual-assets/2026-08/)
- [飞书 9 张长期表 / Nine stable Feishu tables](../../docs/feishu-public-assets-2026-08.md)
- [公开 CSV / Public CSV package](../../public-data/README.md)
- [精编与归档规则 / Curation policy](../../docs/data-retention-and-curation-policy.md)

## 读者边界 / Reader Boundary

这张图谱用来帮助读者区分证据强弱，不提供个人诊断、处方、剂量、停药建议、医美操作或购买推荐。动物延寿不能写成人类延寿已经证实，指标改善不能写成返老还童，研究数量多也不能写成疗效更强。
