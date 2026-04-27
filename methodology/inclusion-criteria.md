# Inclusion and Exclusion Criteria / 纳入与排除标准

This project separates discovery from evidence inclusion. A paper, trial, or dataset can be collected as a candidate without being accepted into the formal evidence matrix.

本项目把“候选收集”和“正式纳入”分开。论文、临床试验或数据集可以先进入候选池，但不等于已经进入正式证据图谱。

## Priority Inclusion / 优先纳入

- Human randomized controlled trials, systematic reviews, meta-analyses, and major guideline-level evidence.
- 人体随机对照试验、系统综述、荟萃分析，以及接近指南级别的证据。

- Large prospective cohorts with hard or functional endpoints: all-cause mortality, MACE, stroke, cancer incidence, dementia, disability, hospitalization, frailty, falls, VO2max, grip strength, cognition, sleep apnea severity.
- 含硬终点或功能终点的大型前瞻队列：全因死亡、主要心血管事件、卒中、癌症发生、痴呆、失能、住院、衰弱、跌倒、VO2max、握力、认知、睡眠呼吸暂停严重度。

- Human trials or cohorts using validated clinical risk markers: BP, LDL-C, apoB, HbA1c, waist circumference, body composition, CRP, kidney function.
- 使用可靠临床风险指标的人体试验或队列：血压、LDL-C、apoB、HbA1c、腰围、身体成分、CRP、肾功能等。

- High-value translational geroscience: mTOR/rapamycin, metformin, senolytics, NAD/NMN/NR, epigenetic clocks, proteomic/metabolomic clocks, partial reprogramming, Klotho, IL-11, autophagy/mitophagy, microbiome, ITP mouse lifespan studies.
- 高价值转化老年科学：mTOR/雷帕霉素、二甲双胍、senolytics、NAD/NMN/NR、表观遗传时钟、蛋白组/代谢组时钟、部分重编程、Klotho、IL-11、自噬/线粒体自噬、微生物组、ITP 小鼠寿命研究。

- Negative, null, replication, and safety findings.
- 阴性结果、无效结果、重复验证、安全性研究同样优先保留。

## Deprioritize / 暂缓纳入

- Cell-only studies with weak linkage to healthspan, lifespan, or clinical prevention.
- 仅有细胞实验且与健康寿命、寿命或临床预防关联较弱的研究。

- Marketing material, commercial white papers, influencer claims, uncontrolled self-experiments, and papers without traceable DOI/PMID/PMCID/preprint/registry identifiers.
- 营销材料、商业白皮书、社交媒体主张、无对照自我实验，以及无法追溯 DOI/PMID/PMCID/预印本/注册号的内容。

- Biomarker-only claims presented as “reversal of aging” without clinical or functional validation.
- 只有 biomarker 改善却宣称“逆龄/逆转衰老”，且缺少临床或功能验证的内容。

## Required Screening Fields / 必填筛选字段

Every candidate that is manually reviewed should receive:

每条人工复核候选都应填写：

- include_status: `needs_review`, `shortlist`, `include`, `exclude`, `duplicate`
- exclusion_reason, if excluded / 如排除，必须写明原因
- study_type / 研究类型
- species / 物种
- endpoint_class / 终点等级
- risk_of_bias / 偏倚风险
- contribution_score / 贡献度总分
- reviewer_notes / 审核备注
