"""Implement methods A and B as auditable data products.

Method A:
- Build a high-priority core review queue for A/B public topics.
- Add concise public explanations for why a topic is high confidence and why
  it is not personal medical advice.

Method B:
- Add PICO/PECO question framing for every public topic.
- Add claim-level grading so each topic can distinguish supported claims from
  unsupported/overstated claims.
- Add an appraisal plan assigning AMSTAR 2, RoB 2, ROBINS-I, or domain screen.

Also builds a Feishu-friendly full literature library table.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CONTENT = ROOT / "content" / "overview"
DOCS = ROOT / "docs"
TODAY = date.today().isoformat()


GRADE_ORDER = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1, "": 0}


HEALTH_TOPIC_FRAMES = {
    "cardiorespiratory-fitness": {
        "population": "Adults in general or clinical populations.",
        "population_zh": "普通成人或临床人群。",
        "intervention": "Higher measured cardiorespiratory fitness or interventions that improve CRF.",
        "intervention_zh": "较高心肺适能，或能够提高心肺适能的运动/康复干预。",
        "comparator": "Lower CRF, inactive control, or usual care.",
        "comparator_zh": "较低心肺适能、缺乏运动或常规照护。",
        "outcomes": "All-cause mortality, cardiovascular mortality, functional capacity.",
        "outcomes_zh": "全因死亡、心血管死亡、功能能力。",
        "main_claim_zh": "较高心肺适能与较低全因和心血管死亡风险稳定相关，是健康寿命图谱中的高优先级基础指标。",
        "main_claim_en": "Higher cardiorespiratory fitness is consistently associated with lower all-cause and cardiovascular mortality risk.",
        "boundary_zh": "不能把总体关联直接写成任何个体都适合高强度训练；运动处方需考虑疾病、年龄和风险。",
        "medical": "true",
    },
    "physical-activity-healthspan": {
        "population": "Adults across age groups.",
        "population_zh": "不同年龄段成人。",
        "intervention": "Regular physical activity, especially moderate-to-vigorous activity and reduced sedentary time.",
        "intervention_zh": "规律身体活动，尤其是中高强度活动和减少久坐。",
        "comparator": "Lower activity or sedentary behavior.",
        "comparator_zh": "低活动量或久坐行为。",
        "outcomes": "Mortality, cardiovascular disease, diabetes, function, frailty.",
        "outcomes_zh": "死亡、心血管疾病、糖尿病、功能、衰弱。",
        "main_claim_zh": "规律身体活动与较低死亡和多种慢病风险相关，是健康寿命的基础证据方向。",
        "main_claim_en": "Regular physical activity is linked to lower mortality and chronic disease risk.",
        "boundary_zh": "不能把它写成单一万能运动处方，也不能忽略伤病和基础疾病。",
        "medical": "false",
    },
    "resistance-training-muscle": {
        "population": "Adults, especially older adults or people at risk of sarcopenia/frailty.",
        "population_zh": "成人，尤其是老年人或肌少/衰弱风险人群。",
        "intervention": "Resistance training, strength training, muscle-preserving interventions.",
        "intervention_zh": "抗阻训练、力量训练和保肌干预。",
        "comparator": "No resistance training, usual care, or lower training exposure.",
        "comparator_zh": "无抗阻训练、常规照护或较低训练暴露。",
        "outcomes": "Strength, muscle mass, physical function, falls, frailty.",
        "outcomes_zh": "力量、肌肉量、身体功能、跌倒、衰弱。",
        "main_claim_zh": "抗阻训练对肌力、功能和衰弱风险管理有较强证据基础。",
        "main_claim_en": "Resistance training has strong evidence for improving strength, function, and frailty-related outcomes.",
        "boundary_zh": "不能保证每个人增肌或逆转衰弱；高龄、骨质疏松和慢病人群需评估。",
        "medical": "false",
    },
    "blood-pressure-aging": {
        "population": "Adults with normal, elevated, or hypertensive blood pressure.",
        "population_zh": "血压正常、升高或高血压成人。",
        "intervention": "Blood pressure monitoring, lifestyle management, and evidence-based antihypertensive treatment.",
        "intervention_zh": "血压监测、生活方式管理和循证降压治疗。",
        "comparator": "Untreated or less controlled blood pressure.",
        "comparator_zh": "未治疗或控制较差的血压。",
        "outcomes": "Stroke, cardiovascular events, kidney outcomes, mortality.",
        "outcomes_zh": "卒中、心血管事件、肾脏结局、死亡。",
        "main_claim_zh": "血压控制与心脑血管和肾脏硬终点风险降低高度相关，是医学管理型 A 级主题。",
        "main_claim_en": "Blood pressure control is strongly linked to lower vascular and renal hard-outcome risk.",
        "boundary_zh": "不能在图谱中给个人药物选择或剂量；治疗目标需医生决定。",
        "medical": "true",
    },
    "ldl-apob-cardiovascular-risk": {
        "population": "Adults with varying ASCVD risk, dyslipidemia, diabetes, or established cardiovascular disease.",
        "population_zh": "不同 ASCVD 风险、血脂异常、糖尿病或已确诊心血管病成人。",
        "intervention": "Lower LDL-C/apoB exposure or lipid-lowering treatment.",
        "intervention_zh": "降低 LDL-C/apoB 暴露或降脂治疗。",
        "comparator": "Higher LDL-C/apoB exposure or less intensive management.",
        "comparator_zh": "较高 LDL-C/apoB 暴露或较弱管理。",
        "outcomes": "ASCVD events, myocardial infarction, stroke, cardiovascular mortality.",
        "outcomes_zh": "ASCVD 事件、心梗、卒中、心血管死亡。",
        "main_claim_zh": "LDL-C/apoB 与动脉粥样硬化性心血管风险有强因果和干预证据。",
        "main_claim_en": "LDL-C/apoB has strong causal and interventional evidence for ASCVD risk.",
        "boundary_zh": "不能替代个体化风险分层和处方；过低/过高治疗强度都需医生判断。",
        "medical": "true",
    },
    "sleep-aging": {
        "population": "Adults with normal sleep, short/long sleep, insomnia symptoms, or sleep-disordered breathing risk.",
        "population_zh": "睡眠正常、短睡/长睡、失眠症状或睡眠呼吸障碍风险成人。",
        "intervention": "Sleep duration/quality improvement, sleep disorder identification and treatment.",
        "intervention_zh": "改善睡眠时长/质量，识别和治疗睡眠障碍。",
        "comparator": "Poor sleep, untreated sleep disorder, or irregular sleep patterns.",
        "comparator_zh": "睡眠差、未治疗睡眠障碍或睡眠节律不规律。",
        "outcomes": "Mortality, cardiometabolic outcomes, cognition, mental health, daytime function.",
        "outcomes_zh": "死亡、心代谢结局、认知、心理健康、日间功能。",
        "main_claim_zh": "睡眠问题与多类健康结局相关，识别严重失眠和睡眠呼吸暂停具有较高健康价值。",
        "main_claim_en": "Sleep problems are linked to multiple health outcomes, and identifying major sleep disorders has high clinical value.",
        "boundary_zh": "不能把睡眠关联直接写成某种补剂或单一技巧能延寿。",
        "medical": "true",
    },
    "dietary-pattern-longevity": {
        "population": "Adults in general population or cardiometabolic risk groups.",
        "population_zh": "普通成人或心代谢风险人群。",
        "intervention": "Healthy dietary patterns such as Mediterranean/DASH-style patterns or higher diet quality.",
        "intervention_zh": "地中海/DASH 等健康饮食模式或更高饮食质量。",
        "comparator": "Lower diet quality, ultra-processed or less healthy patterns.",
        "comparator_zh": "较低饮食质量、超加工或不健康饮食模式。",
        "outcomes": "Mortality, cardiovascular disease, diabetes, weight and metabolic markers.",
        "outcomes_zh": "死亡、心血管疾病、糖尿病、体重和代谢指标。",
        "main_claim_zh": "健康饮食模式与较低死亡和心代谢风险相关，证据强于单一食物或补剂神话。",
        "main_claim_en": "Healthy dietary patterns are associated with lower mortality and cardiometabolic risk.",
        "boundary_zh": "不能神化单一食物、超级食物或补剂，也不能给出个人治疗饮食。",
        "medical": "false",
    },
    "glp1-weight-cardiometabolic": {
        "population": "Adults with obesity, diabetes, or high cardiometabolic risk.",
        "population_zh": "肥胖、糖尿病或高心代谢风险成人。",
        "intervention": "GLP-1 receptor agonists or related incretin-based pharmacotherapy.",
        "intervention_zh": "GLP-1 受体激动剂或相关肠促胰素药物治疗。",
        "comparator": "Placebo, usual care, or alternative weight/cardiometabolic management.",
        "comparator_zh": "安慰剂、常规照护或其他体重/心代谢管理。",
        "outcomes": "Weight, glycemic outcomes, cardiovascular events, adverse events.",
        "outcomes_zh": "体重、血糖、心血管事件、不良反应。",
        "main_claim_zh": "GLP-1 类药物在肥胖/糖尿病/心代谢高风险人群中有较强临床结局证据。",
        "main_claim_en": "GLP-1 therapies have strong clinical evidence in obesity, diabetes, and cardiometabolic risk groups.",
        "boundary_zh": "这是处方药医学主题，不能被包装成普通抗衰或美容减肥建议。",
        "medical": "true",
    },
    "caloric-restriction-human": {
        "population": "Adults without contraindications to dietary energy restriction.",
        "population_zh": "没有禁忌证的成人。",
        "intervention": "Moderate caloric restriction with adequate nutrition.",
        "intervention_zh": "营养充足前提下的适度热量限制。",
        "comparator": "Ad libitum diet or usual diet.",
        "comparator_zh": "自由进食或常规饮食。",
        "outcomes": "Weight, cardiometabolic markers, aging biomarkers, safety.",
        "outcomes_zh": "体重、心代谢指标、衰老 biomarker、安全性。",
        "main_claim_zh": "人体热量限制有代谢和部分衰老指标证据，但不是人类延寿已证实。",
        "main_claim_en": "Human caloric restriction has metabolic and some aging-biomarker evidence, but not proven human lifespan extension.",
        "boundary_zh": "不能鼓励极端节食；孕期、进食障碍、慢病和高龄人群需谨慎。",
        "medical": "true",
    },
    "time-restricted-eating": {
        "population": "Adults with or without cardiometabolic risk.",
        "population_zh": "有或无心代谢风险的成人。",
        "intervention": "Time-restricted eating or intermittent fasting windows.",
        "intervention_zh": "限时进食或间歇性禁食窗口。",
        "comparator": "Usual eating timing or continuous energy restriction.",
        "comparator_zh": "常规进食时间或连续热量限制。",
        "outcomes": "Weight, glycemic markers, lipids, blood pressure, adherence and safety.",
        "outcomes_zh": "体重、血糖、血脂、血压、依从性和安全性。",
        "main_claim_zh": "限时进食可作为体重和代谢管理候选策略，但证据强度低于硬终点干预。",
        "main_claim_en": "Time-restricted eating is a candidate strategy for weight and metabolic management, but hard-outcome evidence is limited.",
        "boundary_zh": "糖尿病用药、孕期、进食障碍和低体重人群不应自行尝试。",
        "medical": "true",
    },
    "metformin-aging": {
        "population": "Adults with diabetes or populations studied for aging-related hypotheses.",
        "population_zh": "糖尿病成人或被纳入衰老假说研究的人群。",
        "intervention": "Metformin exposure or metformin treatment.",
        "intervention_zh": "二甲双胍暴露或治疗。",
        "comparator": "No metformin, placebo, or alternative diabetes treatment.",
        "comparator_zh": "未使用二甲双胍、安慰剂或其他糖尿病治疗。",
        "outcomes": "Diabetes outcomes, cardiovascular outcomes, cancer signals, aging-related composite outcomes.",
        "outcomes_zh": "糖尿病结局、心血管结局、癌症信号、衰老相关复合结局。",
        "main_claim_zh": "二甲双胍在糖尿病治疗中证据明确，但作为非糖尿病人群抗衰药仍属候选假说。",
        "main_claim_en": "Metformin is evidence-based for diabetes treatment, but anti-aging use in non-diabetic adults remains a hypothesis.",
        "boundary_zh": "不能把它写成普通人抗衰处方；肾功能、B12 和用药风险需医生评估。",
        "medical": "true",
    },
    "rapamycin-mtor-aging": {
        "population": "Animal models and limited human translational contexts.",
        "population_zh": "动物模型和有限人体转化场景。",
        "intervention": "Rapamycin, rapalogs, or mTOR modulation.",
        "intervention_zh": "雷帕霉素、rapalog 或 mTOR 调节。",
        "comparator": "Placebo, untreated control, or other mechanistic intervention.",
        "comparator_zh": "安慰剂、未处理对照或其他机制干预。",
        "outcomes": "Lifespan in animals, immune/skin/metabolic markers, adverse events.",
        "outcomes_zh": "动物寿命、免疫/皮肤/代谢指标、不良反应。",
        "main_claim_zh": "mTOR 是衰老机制重要通路，动物证据较强，但人体抗衰临床结论不足。",
        "main_claim_en": "mTOR is an important aging pathway with strong animal evidence, but human anti-aging conclusions remain limited.",
        "boundary_zh": "不能建议健康人自行使用免疫抑制相关药物。",
        "medical": "true",
    },
    "senolytics": {
        "population": "Preclinical models and limited early human studies.",
        "population_zh": "临床前模型和有限早期人体研究。",
        "intervention": "Senolytic candidates or senescence-targeting interventions.",
        "intervention_zh": "senolytic 候选药物或靶向细胞衰老干预。",
        "comparator": "Placebo, untreated controls, or standard care.",
        "comparator_zh": "安慰剂、未处理对照或标准照护。",
        "outcomes": "Senescence markers, disease-specific endpoints, safety.",
        "outcomes_zh": "衰老细胞标志物、疾病特异终点、安全性。",
        "main_claim_zh": "Senolytics 是前沿候选方向，但目前不能写成人体延寿或清除衰老细胞已证实。",
        "main_claim_en": "Senolytics are a frontier candidate area, not proven human lifespan or rejuvenation therapies.",
        "boundary_zh": "不能鼓励自行服用 dasatinib、quercetin、fisetin 等高剂量组合。",
        "medical": "true",
    },
    "nad-nmn-nr-aging": {
        "population": "Adults and preclinical models studied for NAD biology.",
        "population_zh": "NAD 生物学相关成人研究和临床前模型。",
        "intervention": "NMN, NR, NAD precursors, or NAD-modulating interventions.",
        "intervention_zh": "NMN、NR、NAD 前体或 NAD 调节干预。",
        "comparator": "Placebo or no supplementation.",
        "comparator_zh": "安慰剂或不补充。",
        "outcomes": "NAD metabolites, metabolic markers, physical function, safety.",
        "outcomes_zh": "NAD 代谢物、代谢指标、身体功能、安全性。",
        "main_claim_zh": "NAD 前体可影响部分生物标志物，但人体延寿或逆龄尚未证实。",
        "main_claim_en": "NAD precursors can affect some biomarkers, but human lifespan extension or rejuvenation is unproven.",
        "boundary_zh": "不能把提升 NAD 指标直接等同于延寿或抗衰成功。",
        "medical": "false",
    },
    "epigenetic-clocks": {
        "population": "Human cohorts, intervention studies, and biomarker validation sets.",
        "population_zh": "人体队列、干预研究和 biomarker 验证数据集。",
        "intervention": "Measurement or modification of epigenetic clock biomarkers.",
        "intervention_zh": "表观遗传时钟测量或相关干预。",
        "comparator": "Different clock measures, baseline, or control groups.",
        "comparator_zh": "不同表观时钟、基线或对照组。",
        "outcomes": "Clock age, disease risk prediction, mortality prediction, responsiveness to interventions.",
        "outcomes_zh": "时钟年龄、疾病风险预测、死亡预测、对干预的响应。",
        "main_claim_zh": "表观遗传时钟是有价值的衰老 biomarker 工具，但 biomarker 改善不等于临床获益。",
        "main_claim_en": "Epigenetic clocks are useful aging biomarkers, but biomarker changes do not equal clinical benefit.",
        "boundary_zh": "不能把时钟变年轻直接写成真正逆龄或延寿。",
        "medical": "false",
    },
    "itp-mouse-lifespan": {
        "population": "Mouse models in the Interventions Testing Program and related lifespan studies.",
        "population_zh": "ITP 小鼠模型和相关寿命实验。",
        "intervention": "Candidate lifespan interventions tested in mice.",
        "intervention_zh": "小鼠寿命候选干预。",
        "comparator": "Control diet or untreated mouse groups.",
        "comparator_zh": "对照饲料或未处理小鼠组。",
        "outcomes": "Mouse lifespan, healthspan proxies, sex-specific effects.",
        "outcomes_zh": "小鼠寿命、健康寿命代理指标、性别差异。",
        "main_claim_zh": "ITP 是动物寿命干预的重要筛选平台，但不能直接外推成人类延寿建议。",
        "main_claim_en": "ITP is an important mouse lifespan screening platform, not direct human longevity guidance.",
        "boundary_zh": "不能把小鼠寿命延长写成人类可用抗衰方案。",
        "medical": "false",
    },
    "klotho-il11-aging": {
        "population": "Preclinical models and early translational studies.",
        "population_zh": "临床前模型和早期转化研究。",
        "intervention": "Klotho modulation, IL-11 inhibition, or related pathway interventions.",
        "intervention_zh": "Klotho 调节、IL-11 抑制或相关通路干预。",
        "comparator": "Untreated controls, wild-type controls, or placebo.",
        "comparator_zh": "未处理对照、野生型对照或安慰剂。",
        "outcomes": "Mechanistic aging markers, disease models, lifespan/healthspan proxies.",
        "outcomes_zh": "机制性衰老标志物、疾病模型、寿命/健康寿命代理指标。",
        "main_claim_zh": "Klotho/IL-11 属于有潜力的机制和转化方向，但人体抗衰证据仍早期。",
        "main_claim_en": "Klotho/IL-11 is a promising mechanistic and translational area, but human anti-aging evidence is early.",
        "boundary_zh": "不能写成可自行应用的人体抗衰治疗。",
        "medical": "true",
    },
    "partial-reprogramming": {
        "population": "Cells, animal models, and early technology platforms.",
        "population_zh": "细胞、动物模型和早期技术平台。",
        "intervention": "Partial cellular reprogramming or Yamanaka-factor-related approaches.",
        "intervention_zh": "部分细胞重编程或 Yamanaka 因子相关方法。",
        "comparator": "Untreated or sham controls.",
        "comparator_zh": "未处理或假处理对照。",
        "outcomes": "Cellular markers, tissue function in models, safety and tumorigenicity signals.",
        "outcomes_zh": "细胞标志物、模型组织功能、安全性和肿瘤风险信号。",
        "main_claim_zh": "部分重编程是高潜力但高风险的前沿机制方向，目前不应作为人体抗衰结论。",
        "main_claim_en": "Partial reprogramming is high-potential but high-risk frontier biology, not a human anti-aging recommendation.",
        "boundary_zh": "不能把实验室 rejuvenation 写成人体可用疗法。",
        "medical": "true",
    },
    "autophagy-mitophagy": {
        "population": "Preclinical models and human biomarker/intervention studies.",
        "population_zh": "临床前模型和人体 biomarker/干预研究。",
        "intervention": "Autophagy or mitophagy-modulating interventions.",
        "intervention_zh": "自噬或线粒体自噬调节干预。",
        "comparator": "Control condition, placebo, or usual care.",
        "comparator_zh": "对照条件、安慰剂或常规照护。",
        "outcomes": "Mechanistic markers, metabolic/functional markers, disease-specific outcomes.",
        "outcomes_zh": "机制指标、代谢/功能指标、疾病特异结局。",
        "main_claim_zh": "自噬/线粒体自噬是衰老机制核心方向，但多数干预仍缺少人体硬终点证据。",
        "main_claim_en": "Autophagy/mitophagy is central aging biology, but most interventions lack human hard-outcome evidence.",
        "boundary_zh": "不能把激活自噬宣传成普遍延寿或排毒。",
        "medical": "false",
    },
    "microbiome-inflammaging": {
        "population": "Human cohorts, clinical conditions, and preclinical microbiome models.",
        "population_zh": "人体队列、临床疾病人群和临床前微生物组模型。",
        "intervention": "Microbiome composition, diet, probiotics/prebiotics, or microbiome-targeted interventions.",
        "intervention_zh": "微生物组组成、饮食、益生元/益生菌或靶向微生物组干预。",
        "comparator": "Different microbiome profiles, placebo, usual diet, or control groups.",
        "comparator_zh": "不同微生物组特征、安慰剂、常规饮食或对照组。",
        "outcomes": "Inflammation, metabolic outcomes, immune markers, disease risk, frailty.",
        "outcomes_zh": "炎症、代谢结局、免疫指标、疾病风险、衰弱。",
        "main_claim_zh": "微生物组与炎症性衰老相关，但个性化益生菌或泛化抗衰结论仍需谨慎。",
        "main_claim_en": "The microbiome is linked to inflammaging, but personalized probiotic or broad anti-aging claims remain uncertain.",
        "boundary_zh": "不能把单一益生菌写成抗衰处方。",
        "medical": "false",
    },
}


SKIN_TOPIC_FRAMES = {
    "sunscreen-photoaging-prevention": {
        "population": "People exposed to ultraviolet or visible-light-related photoaging risk.",
        "population_zh": "存在紫外线或可见光相关光老化风险的人群。",
        "intervention": "Broad-spectrum sunscreen and photoprotection.",
        "intervention_zh": "广谱防晒和综合光防护。",
        "comparator": "Discretionary, inadequate, or no photoprotection.",
        "comparator_zh": "不规律、不充分或无光防护。",
        "outcomes": "Photoaging, pigmentation, wrinkles, erythema, DNA damage.",
        "outcomes_zh": "光老化、色素、皱纹、红斑、DNA 损伤。",
        "main_claim_zh": "广谱防晒/光防护可预防和减缓 UV 相关光老化，是皮肤美容图谱中的 A 级基础结论。",
        "main_claim_en": "Broad-spectrum sunscreen/photoprotection can prevent or slow UV-related photoaging.",
        "boundary_zh": "不代表逆转所有已存在皮肤老化，也不代表某个具体产品优于其他产品。",
        "medical": "false",
    },
    "retinoids-photoaging": {
        "population": "Adults with photoaging signs or cosmetic dermatology concerns.",
        "population_zh": "有光老化表现或皮肤美容诉求的成人。",
        "intervention": "Topical retinoids, tretinoin, retinol, retinaldehyde.",
        "intervention_zh": "外用维A酸、视黄醇、视黄醛等。",
        "comparator": "Vehicle, placebo, usual skincare, or lower-strength formulations.",
        "comparator_zh": "基质、安慰剂、常规护肤或较弱配方。",
        "outcomes": "Wrinkles, texture, pigmentation, collagen-related markers, irritation.",
        "outcomes_zh": "皱纹、肤质、色素、胶原相关指标、刺激反应。",
        "main_claim_zh": "外用维A酸类对光老化相关皮肤终点有较多人体和临床经验支持。",
        "main_claim_en": "Topical retinoids have meaningful evidence for photoaging-related skin endpoints.",
        "boundary_zh": "处方维A酸、孕期、敏感肌和皮肤病人群需要医生评估。",
        "medical": "true",
    },
    "niacinamide-barrier-pigment": {
        "population": "People with barrier, pigment, inflammation, acne, or cosmetic skin concerns.",
        "population_zh": "有屏障、色素、炎症、痤疮或皮肤美容诉求的人群。",
        "intervention": "Topical or oral niacinamide/nicotinamide depending on claim.",
        "intervention_zh": "按具体问题区分外用或口服烟酰胺/烟酰胺类。",
        "comparator": "Vehicle, placebo, usual skincare, or no treatment.",
        "comparator_zh": "基质、安慰剂、常规护肤或不处理。",
        "outcomes": "Barrier function, pigmentation, inflammation, acne, tolerability.",
        "outcomes_zh": "屏障功能、色素、炎症、痤疮、耐受性。",
        "main_claim_zh": "烟酰胺可作为屏障、色素和炎症相关皮肤终点的候选成分。",
        "main_claim_en": "Niacinamide is a candidate ingredient for barrier, pigmentation, and inflammation-related skin endpoints.",
        "boundary_zh": "不能宣传为全身抗衰或延寿。",
        "medical": "false",
    },
    "topical-vitamin-c": {
        "population": "People with photoaging, pigment, or antioxidant skincare concerns.",
        "population_zh": "有光老化、色素或抗氧化护肤诉求的人群。",
        "intervention": "Topical vitamin C or ascorbic-acid formulations.",
        "intervention_zh": "外用维C或抗坏血酸配方。",
        "comparator": "Vehicle, placebo, usual skincare, or other active ingredients.",
        "comparator_zh": "基质、安慰剂、常规护肤或其他活性成分。",
        "outcomes": "Pigmentation, collagen markers, photoaging signs, irritation and stability.",
        "outcomes_zh": "色素、胶原指标、光老化表现、刺激和稳定性。",
        "main_claim_zh": "外用维C可作为色素、抗氧化和胶原相关皮肤终点的候选方向。",
        "main_claim_en": "Topical vitamin C is a candidate for pigment, antioxidant, and collagen-related skin endpoints.",
        "boundary_zh": "不能替代防晒、医美或疾病治疗。",
        "medical": "false",
    },
    "oral-collagen-peptides": {
        "population": "Adults using oral collagen peptides for skin appearance endpoints.",
        "population_zh": "以皮肤外观终点为目标使用口服胶原肽的成人。",
        "intervention": "Oral collagen peptides or hydrolyzed collagen.",
        "intervention_zh": "口服胶原肽或水解胶原。",
        "comparator": "Placebo or no supplementation.",
        "comparator_zh": "安慰剂或不补充。",
        "outcomes": "Hydration, elasticity, wrinkles, patient-reported appearance, adverse effects.",
        "outcomes_zh": "水分、弹性、皱纹、主观外观、不良反应。",
        "main_claim_zh": "口服胶原肽对水分和弹性等软终点有候选证据，但异质性和商业化风险较高。",
        "main_claim_en": "Oral collagen peptides have candidate evidence for soft endpoints such as hydration and elasticity, but heterogeneity and commercial risk are high.",
        "boundary_zh": "不能写成逆龄、延寿或替代均衡蛋白摄入。",
        "medical": "false",
    },
    "hyaluronic-acid-ceramides-hydration": {
        "population": "People with dry skin, impaired barrier, or hydration concerns.",
        "population_zh": "皮肤干燥、屏障受损或保湿诉求人群。",
        "intervention": "Topical or oral hyaluronic acid, ceramides, or barrier-supporting formulations.",
        "intervention_zh": "外用或口服透明质酸、神经酰胺或屏障支持配方。",
        "comparator": "Vehicle, placebo, usual moisturizer, or no intervention.",
        "comparator_zh": "基质、安慰剂、常规保湿或不干预。",
        "outcomes": "Skin hydration, transepidermal water loss, barrier function, dryness.",
        "outcomes_zh": "皮肤水分、经皮水分流失、屏障功能、干燥。",
        "main_claim_zh": "透明质酸和神经酰胺方向适合讨论保湿和屏障终点。",
        "main_claim_en": "Hyaluronic acid and ceramides are relevant to hydration and barrier endpoints.",
        "boundary_zh": "不能宣传为系统性抗衰或替代皮肤病治疗。",
        "medical": "false",
    },
    "polyphenols-skin-photoprotection": {
        "population": "People using polyphenols or antioxidants for skin photoprotection claims.",
        "population_zh": "以皮肤光保护为目标使用多酚或抗氧化剂的人群。",
        "intervention": "Polyphenols, antioxidants, carotenoids, botanical extracts.",
        "intervention_zh": "多酚、抗氧化剂、类胡萝卜素、植物提取物。",
        "comparator": "Placebo, vehicle, usual diet/skincare, or no supplementation.",
        "comparator_zh": "安慰剂、基质、常规饮食/护肤或不补充。",
        "outcomes": "Photoprotection markers, erythema, pigmentation, oxidative-stress markers.",
        "outcomes_zh": "光保护指标、红斑、色素、氧化应激指标。",
        "main_claim_zh": "多酚/抗氧化剂可作为皮肤光保护候选方向，但证据和产品差异较大。",
        "main_claim_en": "Polyphenols/antioxidants are candidate skin photoprotection interventions, but evidence and products vary widely.",
        "boundary_zh": "不能替代防晒，也不能把抗氧化机制写成抗老已证实。",
        "medical": "false",
    },
    "energy-devices-resurfacing": {
        "population": "People seeking procedural treatment for photoaging, wrinkles, scars, or texture concerns.",
        "population_zh": "因光老化、皱纹、瘢痕或肤质问题考虑医美操作的人群。",
        "intervention": "Laser, intense pulsed light, microneedling, peels, resurfacing devices.",
        "intervention_zh": "激光、强脉冲光、微针、换肤和 resurfacing 设备。",
        "comparator": "Sham, usual care, other devices, or baseline.",
        "comparator_zh": "假处理、常规护理、其他设备或基线。",
        "outcomes": "Wrinkles, texture, pigmentation, scars, adverse events, downtime.",
        "outcomes_zh": "皱纹、肤质、色素、瘢痕、不良反应、恢复期。",
        "main_claim_zh": "能量设备和换肤类干预可改善部分外观终点，但操作者、设备和风险差异极大。",
        "main_claim_en": "Energy devices and resurfacing can improve some appearance endpoints, but operator, device, and risk differences are substantial.",
        "boundary_zh": "必须由合格专业人员评估；不能提供参数、疗程或设备推荐。",
        "medical": "true",
    },
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def int_value(value: str) -> int:
    try:
        return int(float(value or 0))
    except ValueError:
        return 0


def pubmed_url(row: dict[str, str]) -> str:
    if row.get("url"):
        return row["url"]
    if row.get("pmid"):
        return f"https://pubmed.ncbi.nlm.nih.gov/{row['pmid']}/"
    return row.get("doi", "")


def review_tool(row: dict[str, str]) -> str:
    study = (row.get("study_type_draft") or "").lower()
    if "systematic" in study or "meta" in study:
        return "AMSTAR 2"
    if "random" in study or "clinical_trial" in study or "trial" in study:
        return "Cochrane RoB 2"
    if "cohort" in study or "observational" in study or "mendelian" in study:
        return "ROBINS-I"
    if "animal" in study or "mechanistic" in study or row.get("endpoint_class") == "M":
        return "preclinical/domain screen"
    return "domain screen"


def sort_key(row: dict[str, str]) -> tuple[int, int, int, int]:
    level = row.get("final_evidence_level") or row.get("evidence_level_draft") or row.get("evidence_level")
    return (
        GRADE_ORDER.get(level, 0),
        int_value(row.get("quality_confidence_score")),
        int_value(row.get("influence_score")),
        int_value(row.get("year")),
    )


def build_literature_library() -> list[dict[str, str]]:
    candidates = read_csv(DATA / "candidate_sources.csv")
    findings = read_csv(DATA / "evidence_findings.csv")
    skin = read_csv(DATA / "skin_beauty_findings.csv")
    matrix = read_csv(DATA / "evidence_matrix.csv")
    health_by_candidate: dict[str, list[str]] = defaultdict(list)
    skin_by_candidate: dict[str, list[str]] = defaultdict(list)
    for row in findings:
        health_by_candidate[row["candidate_id"]].append(row["topic_id"])
    for row in skin:
        skin_by_candidate[row["candidate_id"]].append(row["topic_id"])
    matrix_ids = {row["paper_id"] for row in matrix}
    rows = []
    for row in candidates:
        source_id = row["id"]
        rows.append(
            {
                "library_id": source_id,
                "title_en": row.get("title_en", ""),
                "title_zh": row.get("title_zh", ""),
                "year": row.get("year", ""),
                "source": row.get("source", ""),
                "pmid": row.get("pmid", ""),
                "pmcid": row.get("pmcid", ""),
                "doi": row.get("doi", ""),
                "url": row.get("url", ""),
                "query": row.get("query", ""),
                "include_status": row.get("include_status", ""),
                "in_healthspan_findings": "true" if source_id in health_by_candidate else "false",
                "health_topic_ids": "; ".join(sorted(set(health_by_candidate.get(source_id, [])))),
                "in_evidence_matrix": "true" if source_id in matrix_ids else "false",
                "in_skin_beauty_findings": "true" if source_id in skin_by_candidate else "false",
                "skin_topic_ids": "; ".join(sorted(set(skin_by_candidate.get(source_id, [])))),
                "last_checked": row.get("last_checked", TODAY),
            }
        )
    return rows


def build_core_review_queue() -> list[dict[str, str]]:
    health = read_csv(DATA / "evidence_findings.csv")
    public_summary = read_csv(DATA / "public_summary.csv")
    skin = read_csv(DATA / "skin_beauty_findings.csv")
    skin_summary = read_csv(DATA / "skin_beauty_summary.csv")
    by_topic: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in health:
        by_topic[("healthspan", row["topic_id"])].append(row)
    for row in skin:
        by_topic[("skin_beauty", row["topic_id"])].append(row)

    topic_rows = []
    for row in public_summary:
        if row["evidence_level_top"] in {"A", "B"}:
            topic_rows.append(("healthspan", row))
    for row in skin_summary:
        if row["evidence_level_top"] in {"A", "B"}:
            topic_rows.append(("skin_beauty", row))

    queue = []
    for domain, topic in topic_rows:
        items = sorted(by_topic[(domain, topic["topic_id"])], key=sort_key, reverse=True)[:5]
        for rank, item in enumerate(items, 1):
            cid = item.get("candidate_id") or item.get("finding_id")
            level = item.get("final_evidence_level") or item.get("evidence_level_draft")
            queue.append(
                {
                    "review_id": f"core-{domain}-{topic['topic_id']}-{rank:02d}",
                    "domain": domain,
                    "topic_id": topic["topic_id"],
                    "topic_zh": topic.get("title_zh", ""),
                    "topic_en": topic.get("title_en", ""),
                    "candidate_id": cid,
                    "finding_id": item.get("finding_id", ""),
                    "pmid": item.get("pmid", ""),
                    "doi": item.get("doi", ""),
                    "year": item.get("year", ""),
                    "journal": item.get("journal", ""),
                    "title_en": item.get("title_en", ""),
                    "study_type": item.get("study_type_draft", ""),
                    "endpoint_class": item.get("endpoint_class_draft") or item.get("endpoint_class", ""),
                    "final_evidence_level": level,
                    "quality_confidence_score": item.get("quality_confidence_score", ""),
                    "influence_score": item.get("influence_score", ""),
                    "review_tool": review_tool(item),
                    "review_priority": "P1" if topic.get("evidence_level_top") == "A" else "P2",
                    "why_selected_zh": "该条属于 A/B 级公开主题的核心候选文献，按等级、质量分、影响力和年份优先排序进入人工复核队列。",
                    "next_action_zh": "读取全文或摘要细节；按指定工具完成人工偏倚/方法学复核；确认该条是否支持公开 claim。",
                    "manual_review_status": "queued_not_started",
                    "reviewer": "",
                    "review_date": "",
                    "pubmed_url": pubmed_url(item),
                    "github_card_path": f"content/papers/{cid}.md" if cid else "",
                    "last_checked": TODAY,
                }
            )
    return queue


def build_topic_explanations() -> list[dict[str, str]]:
    rows = []
    for domain, path, frames in [
        ("healthspan", DATA / "public_summary.csv", HEALTH_TOPIC_FRAMES),
        ("skin_beauty", DATA / "skin_beauty_summary.csv", SKIN_TOPIC_FRAMES),
    ]:
        for row in read_csv(path):
            frame = frames.get(row["topic_id"], {})
            level = row.get("evidence_level_top", "")
            rows.append(
                {
                    "explanation_id": f"explain-{domain}-{row['topic_id']}",
                    "domain": domain,
                    "topic_id": row["topic_id"],
                    "title_zh": row.get("title_zh", ""),
                    "title_en": row.get("title_en", ""),
                    "public_level": level,
                    "why_this_level_zh": level_rationale(row, frame),
                    "why_not_medical_advice_zh": medical_boundary(row, frame),
                    "core_review_required": "true" if level in {"A", "B"} else "false",
                    "status": "public_draft_needs_manual_review",
                    "last_checked": TODAY,
                }
            )
    return rows


def level_rationale(row: dict[str, str], frame: dict[str, str]) -> str:
    level = row.get("evidence_level_top", "")
    if row.get("topic_id") == "sunscreen-photoaging-prevention":
        return "A 级限定于广谱防晒/光防护预防和减缓 UV 相关光老化；该结论有生物学因果、人体随机试验和皮肤科共识支持。"
    if level == "A":
        return "A 级表示该主题存在较强的人体研究、较重要终点和可转化结论，但仍需逐条人工复核核心文献。"
    if level == "B":
        return "B 级表示方向有较好人体或系统证据，但硬终点、直接因果、异质性或适用范围仍有限。"
    if level == "C":
        return "C 级表示候选证据存在，但通常受限于软终点、机制外推、早期研究、商业风险或研究异质性。"
    if level == "D":
        return "D 级表示主要为动物、机制或早期探索，不能作为人体行动建议。"
    return "当前等级仍需补充复核。"


def medical_boundary(row: dict[str, str], frame: dict[str, str]) -> str:
    base = frame.get("boundary_zh") or row.get("reader_boundary_zh") or "不能替代医生、营养师或合格专业人员的个体化评估。"
    if frame.get("medical") == "true":
        return f"{base} 该主题涉及疾病、药物、处方或专业操作，公开页只能提供证据边界，不能给个人医疗建议。"
    return f"{base} 公开页只说明人群层面证据，不提供个人剂量、疗程、品牌或处方建议。"


def build_pico_peco() -> list[dict[str, str]]:
    rows = []
    for domain, path, frames, framework in [
        ("healthspan", DATA / "public_summary.csv", HEALTH_TOPIC_FRAMES, "PICO/PECO"),
        ("skin_beauty", DATA / "skin_beauty_summary.csv", SKIN_TOPIC_FRAMES, "PICO"),
    ]:
        for row in read_csv(path):
            frame = frames[row["topic_id"]]
            rows.append(
                {
                    "question_id": f"q-{domain}-{row['topic_id']}",
                    "domain": domain,
                    "topic_id": row["topic_id"],
                    "title_zh": row.get("title_zh", ""),
                    "title_en": row.get("title_en", ""),
                    "framework": framework,
                    "population_zh": frame["population_zh"],
                    "population_en": frame["population"],
                    "intervention_or_exposure_zh": frame["intervention_zh"],
                    "intervention_or_exposure_en": frame["intervention"],
                    "comparator_zh": frame["comparator_zh"],
                    "comparator_en": frame["comparator"],
                    "outcomes_zh": frame["outcomes_zh"],
                    "outcomes_en": frame["outcomes"],
                    "preferred_study_designs": preferred_designs(row["evidence_level_top"]),
                    "exclusion_or_boundary_zh": frame["boundary_zh"],
                    "last_checked": TODAY,
                }
            )
    return rows


def preferred_designs(level: str) -> str:
    if level == "A":
        return "systematic review/meta-analysis; large RCT; large prospective cohort; Mendelian randomization where appropriate"
    if level == "B":
        return "systematic review/meta-analysis; RCT; prospective cohort; high-quality mechanistic bridge only as support"
    return "human pilot studies plus mechanistic/preclinical evidence, clearly separated from public claims"


def build_claim_grades() -> list[dict[str, str]]:
    rows = []
    for domain, path, frames in [
        ("healthspan", DATA / "public_summary.csv", HEALTH_TOPIC_FRAMES),
        ("skin_beauty", DATA / "skin_beauty_summary.csv", SKIN_TOPIC_FRAMES),
    ]:
        for row in read_csv(path):
            frame = frames[row["topic_id"]]
            level = row["evidence_level_top"]
            rows.append(
                {
                    "claim_id": f"claim-{domain}-{row['topic_id']}-supported-01",
                    "domain": domain,
                    "topic_id": row["topic_id"],
                    "title_zh": row.get("title_zh", ""),
                    "claim_type": "supported_public_claim",
                    "claim_zh": frame["main_claim_zh"],
                    "claim_en": frame["main_claim_en"],
                    "public_grade": level,
                    "endpoint_scope": frame["outcomes_zh"],
                    "evidence_basis_zh": evidence_basis(level, domain),
                    "downgrade_or_cap_reasons_zh": downgrade_reason(row, domain),
                    "does_not_mean_zh": frame["boundary_zh"],
                    "medical_supervision_needed": frame["medical"],
                    "status": "draft_claim_level_grade_needs_manual_review",
                    "last_checked": TODAY,
                }
            )
            rows.append(
                {
                    "claim_id": f"claim-{domain}-{row['topic_id']}-boundary-01",
                    "domain": domain,
                    "topic_id": row["topic_id"],
                    "title_zh": row.get("title_zh", ""),
                    "claim_type": "unsupported_or_overstated_claim",
                    "claim_zh": frame["boundary_zh"],
                    "claim_en": "This boundary or overstated claim is not supported as a public recommendation.",
                    "public_grade": "not_supported",
                    "endpoint_scope": "overclaim boundary",
                    "evidence_basis_zh": "作为公开传播边界列出，目的是防止把证据外推到剂量、处方、品牌、逆龄或延寿承诺。",
                    "downgrade_or_cap_reasons_zh": "该说法超出当前证据适用范围。",
                    "does_not_mean_zh": "不是否定主题本身，而是限制具体宣传语。",
                    "medical_supervision_needed": frame["medical"],
                    "status": "public_boundary",
                    "last_checked": TODAY,
                }
            )
    return rows


def evidence_basis(level: str, domain: str) -> str:
    if level == "A":
        return "有较强人体证据、较重要终点和/或领域共识支持；仍需保留草稿与非医疗建议标注。"
    if level == "B":
        return "有一定人体证据或系统证据，但硬终点、直接因果或适用范围仍有限。"
    if level == "C":
        return "候选证据存在，但多受限于软终点、异质性、摘要级抽取或商业化风险。"
    if level == "D":
        return "主要为动物、机制或早期探索证据。"
    return "证据仍不足。"


def downgrade_reason(row: dict[str, str], domain: str) -> str:
    level = row.get("evidence_level_top", "")
    if row.get("topic_id") == "sunscreen-photoaging-prevention":
        return "领域级预防结论可为 A；但单篇综述、具体产品、逆转皱纹或替代医美不得自动继承 A。"
    if domain == "skin_beauty":
        return "皮肤终点多为 S1/S2 外观或仪器指标，不能外推为延寿或系统抗衰。"
    if level in {"C", "D"}:
        return "主要受人体硬终点不足、机制/动物外推或安全性不确定限制。"
    return "主要限制包括摘要级自动抽取、尚未逐篇全文复核和个体适用性差异。"


def build_appraisal_plan(core_queue: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for item in core_queue:
        tool = item["review_tool"]
        rows.append(
            {
                "appraisal_id": f"appraise-{item['review_id']}",
                "review_id": item["review_id"],
                "domain": item["domain"],
                "topic_id": item["topic_id"],
                "candidate_id": item["candidate_id"],
                "pmid": item["pmid"],
                "title_en": item["title_en"],
                "assigned_tool": tool,
                "critical_domains_zh": critical_domains(tool),
                "current_status": "queued_not_started",
                "minimum_decision_needed_zh": "确认研究问题、纳入设计、偏倚风险、资金/利益冲突、结论是否支持当前 claim。",
                "output_fields_needed_zh": "risk_of_bias_rating; applicability; funding_conflict; claim_supported; reviewer_notes; lock_or_downgrade_decision",
                "reviewer": "",
                "review_date": "",
                "last_checked": TODAY,
            }
        )
    return rows


def critical_domains(tool: str) -> str:
    if tool == "AMSTAR 2":
        return "PICO 是否清楚；检索是否全面；排除研究是否说明；RoB 是否纳入解释；发表偏倚；利益冲突。"
    if tool == "Cochrane RoB 2":
        return "随机化；偏离预定干预；缺失结局数据；结局测量；选择性报告。"
    if tool == "ROBINS-I":
        return "混杂；选择偏倚；干预分类；偏离干预；缺失数据；结局测量；选择性报告。"
    if tool == "preclinical/domain screen":
        return "物种/模型可转化性；剂量和暴露；重复性；安全性；是否误外推到人体。"
    return "研究问题匹配；研究设计；终点；偏倚风险；利益冲突；适用范围。"


def write_high_priority_brief(core_queue: list[dict[str, str]], explanations: list[dict[str, str]]) -> None:
    CONTENT.mkdir(parents=True, exist_ok=True)
    lines = [
        "# A/B 级主题核心复核与解释 / High-Priority Review Brief",
        "",
        "> 草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。",
        "> Draft status: automatically prepared; not fully reviewed; not medical advice.",
        "",
        "## 目的",
        "",
        "本页落实方法 A：对 A/B 级公开主题建立核心文献人工复核队列，并解释为什么某些主题可以公开为高等级，同时为什么仍不能转化为个人医疗建议。",
        "",
        "## 高优先级主题解释",
        "",
        "| 主题 | 等级 | 为什么是这个等级 | 为什么不是医疗建议 |",
        "|---|---|---|---|",
    ]
    for row in explanations:
        if row["public_level"] in {"A", "B"}:
            lines.append(
                f"| {row['title_zh']}<br>{row['topic_id']} | {row['public_level']} | {row['why_this_level_zh']} | {row['why_not_medical_advice_zh']} |"
            )
    lines.extend(
        [
            "",
            "## 核心复核队列",
            "",
            "| Review ID | 主题 | PMID | 年份 | 等级 | 工具 | 下一步 |",
            "|---|---|---|---:|---|---|---|",
        ]
    )
    for row in core_queue:
        lines.append(
            f"| {row['review_id']} | {row['topic_zh']} | [{row['pmid']}]({row['pubmed_url']}) | {row['year']} | {row['final_evidence_level']} | {row['review_tool']} | {row['next_action_zh']} |"
        )
    (CONTENT / "high-priority-review-brief.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_claim_level_summary(claims: list[dict[str, str]], pico: list[dict[str, str]]) -> None:
    lines = [
        "# Claim 级证据评级与 PICO/PECO / Claim-Level Grading and PICO/PECO",
        "",
        "> 草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。",
        "> Draft status: automatically prepared; not fully reviewed; not medical advice.",
        "",
        "## 为什么要拆 claim",
        "",
        "同一个主题可以有强结论和弱结论。例如：防晒预防 UV 相关光老化可以是 A；但防晒逆转所有皱纹、替代医美或证明某个产品最好，不能继承 A。",
        "",
        "## Claim 级评级",
        "",
        "| 主题 | Claim 类型 | 公开等级 | Claim | 不能外推到 |",
        "|---|---|---|---|---|",
    ]
    for row in claims:
        if row["claim_type"] == "supported_public_claim":
            lines.append(
                f"| {row['title_zh']}<br>{row['topic_id']} | {row['claim_type']} | {row['public_grade']} | {row['claim_zh']} | {row['does_not_mean_zh']} |"
            )
    lines.extend(
        [
            "",
            "## PICO/PECO 摘要",
            "",
            "| 主题 | Population | Intervention/Exposure | Comparator | Outcomes |",
            "|---|---|---|---|---|",
        ]
    )
    for row in pico:
        lines.append(
            f"| {row['title_zh']}<br>{row['topic_id']} | {row['population_zh']} | {row['intervention_or_exposure_zh']} | {row['comparator_zh']} | {row['outcomes_zh']} |"
        )
    (CONTENT / "claim-level-grading.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(library_rows: list[dict[str, str]], core_queue: list[dict[str, str]], pico: list[dict[str, str]], claims: list[dict[str, str]], appraisal: list[dict[str, str]]) -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 方法 A/B 落地报告 / Methods A-B Implementation Report",
        "",
        f"- 日期：{TODAY}",
        "- 目的：把发布前最低加固版（方法 A）和方法学增强版（方法 B）做成可管理的数据层、页面和飞书表。",
        "",
        "## 已生成的数据表",
        "",
        "| 表 | 行数 | 用途 |",
        "|---|---:|---|",
        f"| data/literature_library.csv | {len(library_rows)} | 全量文献库，供飞书完整展示。 |",
        f"| data/core_review_queue.csv | {len(core_queue)} | A/B 级主题核心文献人工复核队列。 |",
        f"| data/public_topic_explanations.csv | {len(read_csv(DATA / 'public_summary.csv')) + len(read_csv(DATA / 'skin_beauty_summary.csv'))} | 每个主题为什么是当前等级、为什么不是医疗建议。 |",
        f"| data/topic_pico_peco.csv | {len(pico)} | 每个主题的 PICO/PECO 问题框架。 |",
        f"| data/claim_level_grading.csv | {len(claims)} | 每个主题拆成支持 claim 和不支持/过度宣传 claim。 |",
        f"| data/methodology_appraisal_plan.csv | {len(appraisal)} | 给核心队列分配 AMSTAR 2 / RoB 2 / ROBINS-I / domain screen。 |",
        "",
        "## 飞书同步目标表",
        "",
        "| 飞书表 | table_id | 行数 |",
        "|---|---|---:|",
        f"| 文献库全量 | tblphEOQSzMb3dFi | {len(library_rows)} |",
        f"| 核心复核队列 | tblRyAJ5afGo6tGj | {len(core_queue)} |",
        "| 主题评级说明 | tblMfLdNDc4zkrDk | 28 |",
        f"| PICO_PECO问题框架 | tblPJ2AHChIV7gGo | {len(pico)} |",
        f"| Claim级证据评级 | tblgsBeHJ7LI7uKf | {len(claims)} |",
        f"| 方法学复核计划 | tblwZVdgFQRYd1fA | {len(appraisal)} |",
        "",
        "## 关键原则",
        "",
        "- A/B 不是个人医疗建议；公开等级只说明人群层面证据和结论边界。",
        "- 同一主题必须按 claim 分级，不能把强结论扩展到弱结论。",
        "- 补剂矩阵仍是边界矩阵，不是购买清单或处方建议。",
        "- IF/JCR 仍不伪造；若后续导入授权数据，只作为 authority signal，不覆盖 GRADE/RoB。",
        "",
        "## 下一步复核动作",
        "",
        "1. 先复核所有 P1 核心文献，重点是 A 级主题。",
        "2. 每篇系统综述用 AMSTAR 2，每篇 RCT 用 RoB 2，每篇观察研究用 ROBINS-I。",
        "3. 对每个 public claim 做 lock / downgrade / rewrite 决策。",
        "4. 将飞书表中的 `manual_review_status` 从 `queued_not_started` 推进到 `reviewed_locked` 或 `reviewed_downgraded`。",
    ]
    (DOCS / f"methods-ab-implementation-report-{TODAY}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    library_rows = build_literature_library()
    core_queue = build_core_review_queue()
    explanations = build_topic_explanations()
    pico = build_pico_peco()
    claims = build_claim_grades()
    appraisal = build_appraisal_plan(core_queue)

    write_csv(
        DATA / "literature_library.csv",
        library_rows,
        [
            "library_id",
            "title_en",
            "title_zh",
            "year",
            "source",
            "pmid",
            "pmcid",
            "doi",
            "url",
            "query",
            "include_status",
            "in_healthspan_findings",
            "health_topic_ids",
            "in_evidence_matrix",
            "in_skin_beauty_findings",
            "skin_topic_ids",
            "last_checked",
        ],
    )
    write_csv(
        DATA / "core_review_queue.csv",
        core_queue,
        [
            "review_id",
            "domain",
            "topic_id",
            "topic_zh",
            "topic_en",
            "candidate_id",
            "finding_id",
            "pmid",
            "doi",
            "year",
            "journal",
            "title_en",
            "study_type",
            "endpoint_class",
            "final_evidence_level",
            "quality_confidence_score",
            "influence_score",
            "review_tool",
            "review_priority",
            "why_selected_zh",
            "next_action_zh",
            "manual_review_status",
            "reviewer",
            "review_date",
            "pubmed_url",
            "github_card_path",
            "last_checked",
        ],
    )
    write_csv(
        DATA / "public_topic_explanations.csv",
        explanations,
        [
            "explanation_id",
            "domain",
            "topic_id",
            "title_zh",
            "title_en",
            "public_level",
            "why_this_level_zh",
            "why_not_medical_advice_zh",
            "core_review_required",
            "status",
            "last_checked",
        ],
    )
    write_csv(
        DATA / "topic_pico_peco.csv",
        pico,
        [
            "question_id",
            "domain",
            "topic_id",
            "title_zh",
            "title_en",
            "framework",
            "population_zh",
            "population_en",
            "intervention_or_exposure_zh",
            "intervention_or_exposure_en",
            "comparator_zh",
            "comparator_en",
            "outcomes_zh",
            "outcomes_en",
            "preferred_study_designs",
            "exclusion_or_boundary_zh",
            "last_checked",
        ],
    )
    write_csv(
        DATA / "claim_level_grading.csv",
        claims,
        [
            "claim_id",
            "domain",
            "topic_id",
            "title_zh",
            "claim_type",
            "claim_zh",
            "claim_en",
            "public_grade",
            "endpoint_scope",
            "evidence_basis_zh",
            "downgrade_or_cap_reasons_zh",
            "does_not_mean_zh",
            "medical_supervision_needed",
            "status",
            "last_checked",
        ],
    )
    write_csv(
        DATA / "methodology_appraisal_plan.csv",
        appraisal,
        [
            "appraisal_id",
            "review_id",
            "domain",
            "topic_id",
            "candidate_id",
            "pmid",
            "title_en",
            "assigned_tool",
            "critical_domains_zh",
            "current_status",
            "minimum_decision_needed_zh",
            "output_fields_needed_zh",
            "reviewer",
            "review_date",
            "last_checked",
        ],
    )
    write_high_priority_brief(core_queue, explanations)
    write_claim_level_summary(claims, pico)
    write_report(library_rows, core_queue, pico, claims, appraisal)
    print(
        f"methods A/B implemented: literature={len(library_rows)}, core_queue={len(core_queue)}, "
        f"pico={len(pico)}, claims={len(claims)}, appraisal={len(appraisal)}"
    )


if __name__ == "__main__":
    main()
