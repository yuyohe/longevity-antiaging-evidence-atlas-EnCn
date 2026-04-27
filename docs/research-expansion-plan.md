# Research Expansion Plan / 研究扩容计划

Project / 项目: Longevity Anti-Aging Evidence Atlas EnCn / 长寿抗衰与健康寿命证据图谱

Date / 日期: 2026-04-28

## Reference Baseline / 参考基线

The reference GitHub longevity folder is a Markdown knowledge tree with a canonical `sources.json`, paper pages, topic pages, generated indexes, and lint checks. Its README reports 40 curated sources, 32 topics, and 88 wiki pages, while the current `sources.json` available online contains 75 source entries across 54 topic tags.

参考仓库是一个 Markdown 知识库：用 `sources.json` 管理来源清单，用论文页和主题页建立双向链接，并用索引与 lint 保持一致。README 标称 40 个精选来源、32 个主题、88 个 wiki 页面；当前线上 `sources.json` 已扩展到 75 条来源、54 个主题标签。

## Expansion Target / 扩容目标

Phase 1 target: build a candidate pool of at least 750 records, roughly ten times the current 75-source reference manifest. Candidate records are discovery items only. They must pass manual screening before entering `data/evidence_matrix.csv`.

第一阶段目标：建立不少于 750 条候选文献/试验记录，约为参考仓库当前 75 条来源的十倍。候选记录只进入 `data/candidate_sources.csv` 和飞书「候选文献」，人工复核后才能进入正式证据总表。

## Evidence Priority / 证据优先级

Highest priority / 最高优先级:

- Human mortality, cardiovascular events, dementia, disability, frailty, falls, and validated clinical endpoints.
- 人类死亡率、心血管事件、痴呆、失能、衰弱、跌倒和可靠临床终点。

Second priority / 第二优先级:

- Human randomized trials, large cohorts, Mendelian randomization, and systematic reviews using validated risk factors or aging biomarkers.
- 人类随机试验、大型队列、孟德尔随机化、系统综述，以及经过验证的风险因子或衰老生物标志物。

Exploratory priority / 探索优先级:

- Mouse lifespan, cell rejuvenation, omics clocks, senolytics, mTOR, NAD, Klotho, IL-11, parabiosis, plasma exchange, and AI drug discovery.
- 小鼠寿命、细胞重编程、多组学时钟、清除衰老细胞、mTOR、NAD、Klotho、IL-11、异体共生、血浆置换和 AI 药物发现。

## Topic Coverage / 主题覆盖

Core human healthspan / 人类健康寿命核心主题:

- Cardiorespiratory fitness, resistance training, physical activity, blood pressure, LDL-C/apoB, sleep, diet quality, calorie restriction, time-restricted eating, obesity and GLP-1 therapies.
- 心肺适能、抗阻训练、身体活动、血压、LDL-C/apoB、血糖/糖尿病、睡眠、饮食质量、热量限制、限时进食、肥胖和 GLP-1 药物。

Translational geroscience / 转化老年科学:

- Metformin, rapamycin/mTOR inhibitors, senolytics, NAD precursors, epigenetic/proteomic/metabolomic clocks, partial reprogramming, Klotho, IL-11, autophagy/mitophagy, microbiome, inflammaging.
- 二甲双胍、雷帕霉素/mTOR 抑制剂、senolytics、NAD 前体、表观遗传/蛋白组/代谢组时钟、部分重编程、Klotho、IL-11、自噬/线粒体自噬、微生物组、炎症性衰老、ITP 小鼠干预、urolithin A、spermidine、taurine、GlyNAC。

Clinical trial watchlist / 临床试验观察:

- TAME/metformin, rapamycin/sirolimus, senolytics, NAD/NMN/NR, biological-age clock interventions, exercise/frailty trials, plasma exchange.
- TAME/二甲双胍、雷帕霉素/西罗莫司、senolytics、NAD/NMN/NR、生物年龄时钟干预、运动/衰弱试验、血浆置换。

## Workflow / 工作流

1. Fetch candidate records from PubMed, Crossref, and ClinicalTrials.gov.
2. De-duplicate by id, DOI, PMID, and URL.
3. Sync candidates to Feishu table `候选文献`.
4. Manually screen for relevance, endpoint quality, species, study design, and risk of bias.
5. Promote only reviewed records into `data/evidence_matrix.csv` and Feishu `文献总表`.

1. 从 PubMed、Crossref、ClinicalTrials.gov 抓取候选记录。
2. 按 id、DOI、PMID、URL 去重。
3. 同步候选记录到飞书「候选文献」。
4. 人工筛选相关性、终点质量、物种、研究设计和偏倚风险。
5. 只有复核过的记录才能进入 `data/evidence_matrix.csv` 和飞书「文献总表」。
