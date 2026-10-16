"""Shared reader-facing labels for the guide, visual captions and Feishu help."""

import html


EVIDENCE_GUIDE = """# 证据、数字和缩写怎么看 / Reading Evidence, Numbers and Codes

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
"""

VISUAL_NOTES = {
    "heatmap-dashboard": "只统计当前有容量上限的矩阵；颜色深是记录多，0 是本次未纳入，不是无研究或无效。 / Bounded matrix, not efficacy.",
    "heatmap-topic-year": "按论文年份统计当前矩阵；筛选与容量会影响数量。2026 年未结束，不能与完整年份直接比较。 / Selected records; partial year.",
    "heatmap-topic-evidence": "A–E 是本项目草稿排序，不是标准 GRADE 或疗效排名；还要看研究对象、终点和全文复核状态。 / Project draft grades, not efficacy.",
    "evidence-yield-ingredients": "A/B 证据面统计健康寿命、皮肤两个场景：1/2=50%，不是一半论文有效。产出分是代理指标。 / Two-context proxy, not effective-paper share.",
    "retraction-density": "每千篇=同检索条件下撤稿匹配数÷发表匹配数×1,000；小分母会放大比率，不证明成分无效。 / Retraction signal, not efficacy.",
    "topic-evidence-yield": "A/B 比例=该主题矩阵中 A/B 草稿数÷该主题记录数；分母为0时比例不可解释，不是疗效概率。 / Draft-grade share, not benefit probability.",
    "ingredient-card-wall": "评级为既有场景级暂定汇总，不是购买榜；图片区更新不等于评级重审。区分评级、查询和制图日期。 / Provisional context grades; dates differ.",
}

NAVIGATION_HELP = [
    ("这是把运动、睡眠、补剂等研究分开整理的证据图谱，说明研究对象、发现与限制。", "不是个人处方或购买清单；找到论文不等于确认功效。"),
    ("看当前研究在主题、年份和草稿等级中的分布。", "颜色深是记录多；0不是无研究；当前年未结束。"),
    ("查一种成分的用途、暂定证据、常见误解和注意事项。", "健康寿命和皮肤用途要分开看；评级不是购买推荐。"),
    ("先浏览50种成分，再进入单卡看具体限制。", "排列是索引，不是有效性或购买排名。"),
    ("选择运动、睡眠、饮食等自己关心的主题。", "人群关联不等于证明因果或每个人都适用。"),
    ("先看常见误解、注意事项，再看评级。", "成分卡不是购买清单，组合研究不能拆成单成分功效。"),
    ("先看研究测的是皱纹、屏障还是其他皮肤结果。", "外观改善不等于人体延寿。"),
    ("先看是否涉及处方药、疾病或特殊人群。", "不要按表格自行停药、加药或叠加补剂。"),
    ("先区分A/B草稿等级、H1至H6测量结果与复核进度。", "A/B不是有效率，not_assessed是未评估而非没有风险。"),
    ("先区分匹配行数、唯一PMID和每千篇比率。", "累计数不是本月新增；小分母可放大比率。"),
    ("先看五张表分别处于哪个处理层。", "总行数有重复；空白和not_assessed不是零风险。"),
    ("旧月份统一在归档中查找；当前入口只保留一套。", "退出当前集合不等于论文被撤稿或结论被否定。"),
    ("需要了解资料变化时，再看新增、退出和代表研究。", "新进入不等于新发表，更新日期也不等于评级升级。"),
    ("按看图、查证据和找原文选择当前入口。", "旧月份和维护工具不当作当前结论。"),
]

FIELD_HELP = {
    "final_evidence_level": "A–E是本项目草稿排序，不是标准GRADE、疗效或购买评级；必须结合对象、终点与全文复核状态。 / Project draft grade, not efficacy.",
    "evidence_level_draft": "初步证据排序，待复核；A/B也可能报告无明显效果。 / Draft grade, not proven benefit.",
    "evidence_level": "本项目公开草稿等级；不是有效率、个体建议或标准GRADE。 / Project draft grade.",
    "quality_confidence_score": "0–100项目筛选分，综合设计、终点、资料深度等；不是疗效概率，等级还受上限限制。 / Screening score, not a probability.",
    "endpoint_class_draft": "测了什么而非质量等级：H1实际事件，H2功能，H3临床风险指标，H4标志物，H5衰老时钟，H6机制。 / Outcome code, not quality.",
    "endpoint_class": "终点是实际测量结果；H编号不是成绩。先看具体对象、指标和随访长度。 / Measured outcome, not quality.",
    "study_type_draft": "自动整理的研究类型，待全文核对；cohort是观察性队列，RCT是随机试验，meta是研究汇总。 / Draft study design.",
    "review_status": "复核进度；draft是草稿，abstract_read_full_text_pending是摘要已读、全文待核对。 / Review progress, not an approval.",
    "evidence_source_depth": "资料可获得程度；PMCID或full_text_available不代表我们已读完全文。 / Availability is not completed review.",
    "risk_of_bias_rating": "偏倚风险检查；not_assessed表示尚未评估，不是没有风险。 / Not assessed does not mean low risk.",
    "funding_bias_risk": "资助或利益冲突检查；未知/未评估不等于没有利益冲突。 / Unknown is not risk-free.",
    "amstar2_rating": "系统综述质量检查；not_assessed表示检查未完成，不是已通过。 / Pending assessment is not a pass.",
    "journal_tier": "S/A/B/C/D是发表地标签，不是证据A–E；期刊名气不能代替研究质量。 / Journal label, not evidence grade.",
    "journal_authority_tier": "期刊权威标签不是证据等级；有名期刊也可能有无效或有偏倚的研究。 / Journal prestige is not efficacy.",
    "pmid": "PubMed文献编号，便于追查来源；被收录不代表功效认证。 / Source identifier, not validation.",
    "doi": "论文持久标识，便于定位原文；有DOI不代表结论正确。 / Source identifier, not validation.",
    "pmcid": "PMC全文编号；全文可获取不等于已完成全文复核。 / Full-text link, not completed review.",
    "last_checked": "最近查询或核对来源日期，不一定是发表日期或评级重审日期。 / Source check date.",
    "result_zh": "根据摘要或现有资料整理的结果草稿；看正面和无明显变化的结果，并核对全文。 / Draft result, check full text.",
    "conclusion_zh": "资料层解读，不是个人医疗建议；须结合研究人群、设计和终点。 / Interpretation, not personal advice.",
    "说明": "先看统计范围、分母、复核状态及日期；图片新不等于评级重审。 / Read scope, denominator and dates.",
    "健康寿命证据": "场景级暂定汇总，不是单篇论文等级或购买推荐；不能把皮肤功效外推为延寿。 / Provisional healthspan context grade.",
    "健康证据": "健康寿命场景级暂定汇总，不是单篇等级或购买建议；A/B不代表适合所有人。 / Provisional healthspan context grade.",
    "皮肤证据": "只针对皮肤或外观场景；改善外观不等于延寿。 / Skin context, not longevity.",
    "阅读顺序": "14个可选入口的建议排列，不是必须读完的14步。 / Suggested order, not mandatory steps.",
    "状态": "公开/active表示当前使用的资产，不表示成分有效。 / Asset status, not biological activity.",
    "冻结日期": "数据快照日期；与论文发表、评级复核、图片制作日期分开看。 / Snapshot date, not revalidation.",
    "复核日期": "导航记录或资产最近核对日期，不代表每篇论文已完成全文复核。 / Asset check date, not paper approval.",
    "图片": "PNG原图；转发时请同时保留证据边界、统计分母及日期说明。 / Keep captions and limitations when sharing.",
    "先看什么 / Start with": "先从这条建议进入，不必按顺序读完所有入口。 / A suggested starting point.",
    "避免误读 / Do not infer": "这条内容不能支持的推断；与正文和图表一起读。 / Limits to keep with the content.",
    "funding_conflict_risk": "资金或利益冲突风险；not_assessed表示未评估，不是没有冲突。 / Unassessed is not conflict-free.",
    "industry_funding_risk": "行业资助风险；未知或未评估不能当作没有商业影响。 / Unknown is not risk-free.",
    "scoring_version": "内部评分版本名；即使含GRADE/RoB/AMSTAR，也不表示已逐篇完成这些人工评估。 / Version name is not completed assessment.",
    "评级资料日期": "暂定评级所依据资料的日期，不是图片更新日期；旧评级未自动因新图升级。 / Evidence source date, not image date.",
    "撤稿检查日期": "最近撤稿查询日期；匹配数为历史累计，不是本期新增。 / Search date; historical cumulative matches.",
    "图片更新日期": "PNG制作或更新日期，不代表文献结论或评级重新确认。 / Visual date, not revalidation.",
    "卡片图": "单成分原图；发帖请保留场景、评级资料日期、误解和风险说明。 / Share with context and limits.",
    "商业宣传风险": "宣传可能越过证据边界的风险，不是个人安全评级或购买排名。 / Overclaim risk, not safety score.",
    "recommendation_class_draft": "行动方向的草稿分类，不是个人处方；Medical Action需医生评估，Monitor是研究观察而非使用建议。 / Draft action category, not personal advice.",
    "recommendation_class": "项目行动方向分类，不是个人使用或购买方案；Medical Action需专业评估，Monitor仅继续观察。 / Action category, not personal advice.",
}


def reader_legend_html() -> str:
    points = [
        "五张表是同一资料的不同处理层，总行数不是独立论文数。 / CSV layers overlap.",
        "A–E是草稿排序；H1–H6是测量结果；全文待复核是工作进度。 / Grade, outcome and review status differ.",
        "颜色深不等于有效；矩阵里的0不等于没有研究；空白不等于安全。 / Counts and missing values are not efficacy.",
        "成分A/B证据面50%=两个场景中一个达到A/B，不是一半论文有效。 / Two-context proxy.",
        "新图不等于评级重审。若飞书跳到旧表，请先用GitHub入口。 / New visuals are not revalidation.",
    ]
    return '<details class="reader-legend"><summary>读表图例 / Reader Legend</summary><ul>' + ''.join(
        f"<li>{html.escape(point)}</li>" for point in points
    ) + '</ul><p><a href="https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn/blob/main/content/public-reader/evidence-weight.md">完整术语说明 / Full glossary</a></p></details>'
