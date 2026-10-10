# 证据、数字和缩写怎么看 / Reading Evidence, Numbers and Codes

**宇多Yul细胞/yulcell**。这页是 GitHub 与飞书共用的读表说明，不是医学建议。

## 先看三件事 / Three Checks

先问：研究了谁？实际测了什么？我们读到了哪一步？**等级、终点和复核状态是三件不同的事。**

例如：某条记录是 B 级、H3、全文待复核，意思是它在本项目草稿排序中较靠前，测的是临床风险指标，但全文还没核对。不能改写成“已证明延寿”或“建议购买”。

## 五张表不是五批论文 / Five Layers, Not Five Libraries

| 表名 / Layer | 人话解释 | 不能说明什么 |
| --- | --- | --- |
| 文献库 / Library | 找论文用的目录 | 不是全部已验证的结论 |
| 候选来源 / Candidates | 记录论文从哪里、用什么检索词找到 | 找到不等于值得采用 |
| 入选短名单 / Shortlist | 挑出来优先检查的论文 | 入选不等于已经读完全文 |
| 证据发现 / Findings | 自动抽取或根据摘要整理的待复核笔记 | “发现”不是已证实的人体功效 |
| 证据矩阵 / Matrix | 将部分记录放在同一张比较表里 | 没进入矩阵不等于没有价值 |

同一篇论文可以出现在多层；总行数不能相加当作独立论文数。`id` 是项目记录编号，PMID 才是追查 PubMed 文献的入口之一。

## A–E：本项目草稿排序 / Project Draft Grades

这里解释的是 `final_evidence_level` 等公开草稿字段，**不是标准 GRADE 确定性评级，也不是治疗效果、个人获益概率或购买排名**。即使内部版本名含 GRADE/RoB/AMSTAR，也不代表这些工具已经逐篇人工评估完成。

| 级别 | 先怎样理解 | 必须一起看 |
| --- | --- | --- |
| A | 草稿优先级较高 | 研究对象、结果方向、效果大小、全文和偏倚风险 |
| B | 草稿优先级次高，仍有边界 | 能否用于同样的人群和问题 |
| C | 限制较明显，适合继续核查 | 是否只是间接比较、早期人体信号等 |
| D | 早期、间接或资料深度不足 | 可能是动物/机制，也可能只是缺少摘要或全文信息 |
| E | 支持不足或不适合作为结果证据 | 信息缺失、方案或非结果性材料等 |

分数先产生草稿等级，再受研究对象、资料深度和主题上限限制；**同一分数未必得到同一等级**。`quality_confidence_score` 是 0–100 的项目筛选分，不是“有效率 80%”。A/B 记录也可能报告无明显效果。

成分卡的健康寿命、皮肤评级是场景级暂定汇总；不能当成某一篇论文的评级。期刊列的 **S/A/B/C/D** 又是另一套发表地标签，不是证据列的 A–E；期刊名气不能代替研究质量。

## H1–H6：测了什么 / Measured Outcomes

“终点”就是研究实际记录的结果；**H 编号不是成绩或安全等级**。

| 代码 | 人话解释 | 例子与边界 |
| --- | --- | --- |
| H1 | 死亡、重大疾病或住院等实际事件 | 仍要看是哪类人、观察多久，不能直接说所有人延寿 |
| H2 | 身体功能 | 步速、力量、日常活动能力；不是寿命本身 |
| H3 | 临床风险指标 | 血压、血脂等；指标改善不等于已观察到少死亡 |
| H4 | 生物标志物 | 炎症、细胞或分子指标；不等于身体返老还童 |
| H5 | 衰老时钟 | 模型算出的生物年龄；不是实际年龄或余下寿命 |
| H6 | 作用机制 | 解释可能怎样起作用；不能单独证明人体有效 |

皮肤或成分表用另一套代码：S1 是皱纹、色斑、水分等皮肤临床/外观结果；S2 是皮肤机制、仪器或动物/细胞模型结果；M 是机制、动物、细胞或题录级线索。它们不是 H1–H6，皮肤结果也不能改写成延寿。

## 研究类型 / Study Designs

| 名称 | 是什么 | 读的时候留意 |
| --- | --- | --- |
| RCT / 随机对照试验 | 随机分组后比较结果 | 随机不保证样本大、随访长或偏倚低 |
| Cohort / 队列 | 跟踪一群人，比较暴露与结局 | 主要说明关联；生活习惯、疾病等因素可能混杂 |
| Meta-analysis / Meta 分析 | 用统计方法汇总多项研究 | 原研究质量差、差异大，汇总也不能自动变可靠 |
| Nonrandomized / 非随机 | 分组不是完全随机 | 组间原有差异可能影响结果，不能当作完全随机试验 |
| Animal / 动物；in vitro / 体外 | 动物、细胞或实验室研究 | 有助于理解机制，不能直接外推为人体延寿 |

## 状态和编号 / Status and Identifiers

| 常见字段或文字 | 普通读者怎样理解 |
| --- | --- |
| draft / 草稿 | 自动整理或初步判断，仍可能需要修正 |
| abstract_read_full_text_pending / 全文待复核 | 读了摘要，不等于核对了全文方法和完整结果 |
| not_assessed / 未评估 | 这项检查还没做；不是“没有风险” |
| active / 当前使用 | 仍在当前公开集合；不是“有效成分” |
| Strong Action / 生活方式方向 | 项目对一般生活方式方向的分类，不是个人行动处方 |
| Medical Action / 需医生评估 | 涉及诊断、监测或用药等，不能自行执行 |
| Monitor / 继续观察 | 仍是研究方向，不是公众使用建议 |
| Do Not Recommend / 不建议；Insufficient Evidence / 证据不足 | 在该问题范围内不支持或不足；不是对所有用途的判断 |
| PMID | PubMed 文献编号；收录不是功效认证 |
| DOI | 找论文的持久标识；有 DOI 不代表结论正确 |
| PMCID / full_text_available | PMC 全文入口或全文可获得；不代表我们已读完全文 |
| last_checked / 查询日期 | 最近核对记录或查询来源的日期；不一定是论文发表或评级复核日期 |
| 空白、unknown、pending | 未知、未填写或待处理；不能当作 0、无效或安全 |

## 图片、百分比和日期 / Charts, Percentages and Dates

- 主题热力图只统计当前有容量上限的矩阵，不是全球论文总量。颜色深表示该格记录多；**0 表示这次集合里没有记录，不是这个方向没有研究或无效**。2026 年尚未结束，不能直接与完整年份比较。
- 主题 A/B 比例 = 当前矩阵里 A/B 草稿记录数 ÷ 该主题矩阵记录数；不是疗效比例。分母为 0 时，没有可解释的比例，即使绘图显示 0。
- 成分的 A/B 证据面只有“健康寿命、皮肤”两个场景。1/2 = 50%，不是一半论文有效。0–100 产出分是代理指标，不是疗效或安全评分。
- 撤稿每千篇 = 同一检索条件下撤稿匹配数 ÷ 发表匹配数 × 1,000。小分母容易使比率很高，同一论文也可能匹配多个成分；它是复核提醒，不是成分有害或无效的证明。
- **图片制作日期、评级资料日期、撤稿查询日期分开读**；新图不代表结论刚被重新证明。

## 飞书入口打不开时 / If Feishu Opens an Old Table

导航有 14 个可选入口，不是必须读完的 14 步。若链接跳到旧“数据表”，或侧栏没有“当前阅读导航”，先用 [GitHub 普通读者入口](start-here.md) 和 [资产总目录](../../docs/asset-catalog.md)中的当期飞书索引。不要把旧表当成当前数据；公开分享范围需要表格管理员核对。

## English Summary

Project draft grades, outcome codes and review status describe different things. A/B is not clinical GRADE certainty, efficacy, safety or a purchase recommendation. Findings may be abstract-based drafts. PMID/DOI/PMCID identify sources, not validation. The five CSV layers overlap. Heatmaps show a bounded selected matrix, not worldwide research. Ingredient A/B surface share covers two use contexts, not the proportion of effective papers. Missing values and zero denominators are not negative findings. New image dates do not imply revalidated evidence.
