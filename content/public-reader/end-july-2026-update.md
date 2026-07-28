# 宇多Yul细胞/yulcell | 2026 年 7 月底更新 / End-of-July 2026 Update

**冻结日期 / Snapshot date：** 2026-07-29<br>
**检索窗口 / Search window：** 2026-07-15 至 2026-07-29<br>
**项目 / Project：** 长寿抗衰与健康寿命证据图谱 / Longevity Anti-Aging & Healthspan Evidence Atlas

## 30 秒看懂 / 30-Second Summary

这次更新不是在宣布“又发现了 427 个有效抗衰方法”。准确的说法是：我们找到了 427 条可能相关的新资料，把它们放进候选库，再按统一规则整理、降级和等待人工复核。

| 数据层 | 7 月 14 日 | 7 月 29 日 | 这代表什么 |
| --- | ---: | ---: | --- |
| 候选文献 | 15,724 | 16,151 | 像图书馆刚收到的新书，可能相关，但还没逐本审完 |
| 证据发现 | 5,600 | 6,000 | 像读书笔记，记录研究设计、对象、终点和风险 |
| 证据矩阵 | 2,800 | 3,000 | 像分类地图，方便比较，不等于个人行动清单 |
| 公开 CSV 总行数 | 45,448 | 47,302 | 五张处理层表相加，同一篇论文可能重复出现 |
| 图片资产 | 57 | 57 | 7 张主图和 50 张成分卡，全部按月底数据重建 |

**最重要的一句：候选文献不等于有效，进入矩阵也不等于每个人都应该照着做。**

This release adds 427 PubMed candidates and rebuilds the public evidence layers. Candidate discovery is not proof of benefit, and matrix inclusion is not a treatment recommendation.

## 本轮目标 / Release Goal

把7月底版本做成一条普通读者能走完的阅读路线，而不是一堆只有研究人员会用的表格。我们用四个标准验收：

1. 第一次来的读者能在三分钟内分清“候选文献、证据发现、证据矩阵”。
2. GitHub 和飞书使用同一组 2026-07-29 冻结数字，并统一标注“宇多Yul细胞/yulcell”。
3. 每张公开图都说明它能回答什么、不能证明什么，避免把热度当疗效。
4. 所有新增资料保留来源和证据边界，候选记录不会被写成已经证实的结论。

The release goal is a consistent, traceable, plain-language route across GitHub, Feishu, data, and visuals.

## 这次具体做了什么

1. 使用 PubMed 官方 E-utilities 检索 20 个健康寿命主题，时间范围为 2026-07-15 至 2026-07-29。
2. 新增 427 条去重候选，候选库从 15,724 增至 16,151。
3. 将结构化 evidence findings 从 5,600 扩到 6,000，将 evidence matrix 从 2,800 扩到 3,000。
4. 在本轮 427 条新增候选中，有 161 条进入月底 findings，覆盖 18 个主题。其余记录继续停留在候选层，等待相关性和全文复核。
5. 重建主题年份热力图、主题证据等级热力图、证据产出图、撤稿风险图和 50 张成分卡。
6. 更新 GitHub 双语首页、普通读者路线、自包含报告、发帖面板和飞书多维表格。

## 本轮发现并修正的质量问题

自动分类以前会看到摘要中的“randomized trial”或“systematic review”字样，就可能把文章本身误判成随机试验或系统综述。例如，一篇“系统综述研究方案”并没有结果，不能与完成后的系统综述同级。

月底版加入了五条更保守的规则：

- 研究方案和 protocol 统一标为 `protocol_or_registered_plan`，最终证据等级最高只能是 E。
- 评论、社论、勘误和撤稿通知不是原始研究，统一标为 `non_primary_commentary_or_correction`，最高只能是 E。
- 先判断研究对象是人还是动物，再判断是否随机分组；动物随机实验不会再被写成人体随机试验。
- 研究设计优先看 PubMed Publication Type 和标题中的明确设计词，不再因为摘要提到别人的试验就升级。
- 不能可靠识别设计时，标为 `metadata_only_needs_classification`，留给人工复核，不猜测高等级。

重算后，97 条研究方案和 74 条评论、社论、勘误等非原始研究全部为 E；动物研究与人体随机试验的物种错配为 0，本轮检查中的疑似系统综述误判和疑似随机试验误判也均为 0。这是自动分类和数据清理结果，不代表 6,000 篇文献都已完成人工全文偏倚风险评估。

## 六条值得继续看的新候选

下面只是“为什么值得继续读”的例子，不是疗效结论或个人建议。

| 方向 | 新候选 | 初中生版解释 | 不能说明什么 |
| --- | --- | --- | --- |
| 限时进食 | [PMID 42507108](https://pubmed.ncbi.nlm.nih.gov/42507108/) | 汇总糖尿病前期或 2 型糖尿病人群的随机试验，关注血糖调节指标 | 指标变化不等于延长寿命，也不能直接变成个人进食方案 |
| 睡眠呼吸暂停与体能 | [PMID 42516907](https://pubmed.ncbi.nlm.nih.gov/42516907/) | 队列研究观察睡眠呼吸暂停、运动能力和死亡风险之间的关系 | 相关性不能单独证明因果，也不能代替诊断和治疗 |
| 昼夜节律与认知 | [PMID 42458137](https://pubmed.ncbi.nlm.nih.gov/42458137/) | 系统综述整理老年人节律紊乱与认知下降的研究 | 不能据此声称某一种睡眠产品可以预防痴呆 |
| GLP-1 与急性心肌梗死 | [PMID 42479368](https://pubmed.ncbi.nlm.nih.gov/42479368/) | 汇总临床研究中的梗死面积、心功能和短期安全信号 | 这是特定临床场景，不是自行使用药物的抗衰依据 |
| 饮食模式与死亡风险 | [PMID 42464082](https://pubmed.ncbi.nlm.nih.gov/42464082/) | 队列研究比较临床肥胖人群中的不同饮食模式 | 观察研究会受生活方式等因素影响，不能证明某种饮食必然延寿 |
| 生物年龄与肝癌风险 | [PMID 42477571](https://pubmed.ncbi.nlm.nih.gov/42477571/) | 队列研究把生物年龄指标当作风险预测信号 | 风险预测不等于“逆龄”，时钟变年轻也不等于疾病已经减少 |

## 图片应该怎么看

- 热力图颜色深，表示进入矩阵的研究更多，不表示效果更强。
- A/B 比例高，表示当前自动分层里更靠近人体高等级证据，仍需全文偏倚风险复核。
- 撤稿密度是风险提醒，不是对某个成分有效或无效的最终判决。
- 成分卡是入口，不是购买清单、处方或剂量表。

## 最短阅读路线

1. [普通读者从这里开始](start-here.md)
2. [15 条最重要的结论](ten-takeaways.md)
3. [证据权重怎么看](evidence-weight.md)
4. [按主题阅读](topics.md)
5. [哪些内容必须先问医生](doctor-first.md)
6. [飞书阅读导航](feishu-navigation.md)

## English Summary

The end-of-July snapshot contains 16,151 candidate records, 6,000 structured findings, 3,000 matrix rows, and 57 rebuilt visual assets. The July 15-29 search added 427 deduplicated PubMed candidates; 161 entered the findings layer across 18 topics.

The release also makes study-design classification more conservative. Protocols and non-primary items such as editorials or corrections are capped at level E. Explicit animal subjects are separated from human trials, PubMed publication types and titles take priority, and uncertain records remain unclassified pending human review.

This repository is an evidence map, not medical advice. It does not provide prescriptions, dosing protocols, product endorsements, diagnostic decisions, or individualized treatment plans.

## 使用边界 / Boundary

不要把动物延寿写成人类延寿，不要把 biomarker 改善写成返老还童，不要把单篇论文写成定论。药物、注射、医美、高剂量或长期补剂、慢病指标和个人治疗方案，需要医生或合格专业人员评估。
