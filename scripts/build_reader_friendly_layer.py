"""Build plain-language reader guidance for GitHub and Feishu.

The target reader is a non-specialist adult. Keep explanations short,
concrete, and action-boundary oriented.
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OVERVIEW = ROOT / "content" / "overview"
DOCS = ROOT / "docs"
TODAY = date.today().isoformat()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def md_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("|", "\\|") for cell in row) + " |")
    return lines


def level_plain(level: str) -> tuple[str, str, str]:
    mapping = {
        "A": ("强", "比较可靠，可以优先看，但仍不是个人处方。", "适合放在第一梯队理解。"),
        "B": ("中上", "有较多支持，但还有适用范围或不确定性。", "可以关注，但不要过度理解。"),
        "C": ("早期/有限", "有线索，但还不能当成确定结论。", "适合继续观察，不适合自己激进尝试。"),
        "D": ("很早期", "主要是动物、细胞、机制或很初步的人体线索。", "只能当研究方向看。"),
        "E": ("不足", "目前证据太弱或信息不足。", "不应作为行动依据。"),
    }
    return mapping.get(level, ("待定", "还没有足够信息。", "先不要下结论。"))


def doctor_rule(topic_id: str, title: str, level: str) -> str:
    medical_keywords = ["blood-pressure", "ldl", "glp1", "metformin", "rapamycin", "senolytics", "klotho", "partial", "retinoids", "energy"]
    if any(key in topic_id for key in medical_keywords):
        return "是。涉及药物、疾病指标、处方药或医美操作时，应先问医生或合格专业人员。"
    if level in {"C", "D", "E"}:
        return "如果想尝试任何激进干预，需要先问医生；普通阅读不需要。"
    return "一般生活方式方向可先理解原则；有慢病、用药、孕期或高龄情况应问医生。"


def reader_action(topic_id: str, title: str, level: str) -> str:
    if "fitness" in topic_id or "physical-activity" in topic_id:
        return "先把它理解为：规律活动和心肺能力很重要。不要突然上高强度训练。"
    if "resistance" in topic_id:
        return "先把它理解为：肌肉和力量是中年以后健康的重要资产。动作和负重要循序渐进。"
    if "blood-pressure" in topic_id:
        return "先把它理解为：知道自己的血压，并按医生建议管理，比追逐抗衰补剂更重要。"
    if "ldl" in topic_id:
        return "先把它理解为：LDL-C/apoB 是心血管风险管理的重要指标，是否用药要医生判断。"
    if "dietary" in topic_id:
        return "先看整体饮食模式，不要迷信单一食物、超级食物或补剂。"
    if "sleep" in topic_id:
        return "先把它理解为：长期睡不好值得认真处理，严重打鼾或白天嗜睡要评估睡眠呼吸问题。"
    if "glp1" in topic_id:
        return "这是处方药主题，只能在医生管理下讨论，不是普通抗衰工具。"
    if "sunscreen" in topic_id:
        return "先把它理解为：长期光防护是外观抗老的基础，但不是逆转所有皱纹。"
    if "collagen" in topic_id:
        return "可以把它当成皮肤水分/弹性软终点候选，不要当成逆龄或延寿方案。"
    if level in {"C", "D", "E"}:
        return "先当作研究方向看，不建议自行尝试或购买高风险产品。"
    return "先读结论边界，再看是否属于生活方式、医学治疗、补剂或医美场景。"


def build_reader_guides() -> list[dict[str, str]]:
    rows = [
        {
            "guide_id": "start-here",
            "title_zh": "从这里开始",
            "who_should_read": "第一次打开这个项目的人。",
            "plain_explanation_zh": "这个项目不是卖药、卖补剂或给处方。它把长寿、抗衰、皮肤抗老相关研究整理成能读懂的证据地图。",
            "what_to_do_zh": "先看 A/B 级主题，再看每个主题的“不能这么说”。如果涉及药物、疾病或医美，先问医生。",
            "what_not_to_do_zh": "不要看到某个东西是 A 或 B，就立刻买药、买补剂或自行治疗。",
            "github_path": "content/overview/start-here.md",
            "last_checked": TODAY,
        },
        {
            "guide_id": "how-to-read-levels",
            "title_zh": "怎么看 A/B/C/D/E",
            "who_should_read": "不知道证据等级是什么意思的人。",
            "plain_explanation_zh": "A 不是“马上去做”，D 也不是“一定没用”。等级只表示当前证据可靠程度和适用范围。",
            "what_to_do_zh": "A/B 先看，C/D 当研究线索，涉及个人健康决策时找专业人员。",
            "what_not_to_do_zh": "不要把证据等级当成个人剂量、处方或购买建议。",
            "github_path": "content/overview/evidence-levels-plain-language.md",
            "last_checked": TODAY,
        },
        {
            "guide_id": "healthspan-vs-appearance",
            "title_zh": "健康寿命和外观抗老不是一回事",
            "who_should_read": "想同时看寿命和美容的人。",
            "plain_explanation_zh": "健康寿命主要看死亡、疾病、功能和代谢；外观抗老主要看皮肤、皱纹、色斑、水分和光老化。",
            "what_to_do_zh": "先分清你问的是“活得更健康”还是“皮肤看起来更年轻”。两个问题不能混在一起。",
            "what_not_to_do_zh": "不能把皮肤水分改善写成延寿，也不能把动物延寿写成人类抗老成功。",
            "github_path": "content/overview/start-here.md",
            "last_checked": TODAY,
        },
        {
            "guide_id": "supplement-warning",
            "title_zh": "补剂表怎么读",
            "who_should_read": "想看维生素、NMN、胶原蛋白、鱼油、虾青素等补剂的人。",
            "plain_explanation_zh": "补剂表主要告诉你：哪些说法有一点证据，哪些说法容易夸大，哪些人需要谨慎。",
            "what_to_do_zh": "先看“不支持的说法”和“安全边界”，再看等级。",
            "what_not_to_do_zh": "不要把补剂表当购买清单；不要自行高剂量长期叠加。",
            "github_path": "content/overview/supplement-summary.md",
            "last_checked": TODAY,
        },
        {
            "guide_id": "doctor-first",
            "title_zh": "什么时候必须问医生",
            "who_should_read": "有慢病、正在用药、准备尝试药物/医美/强干预的人。",
            "plain_explanation_zh": "血压、血脂、GLP-1、二甲双胍、雷帕霉素、senolytics、激光医美等都不是普通自助项目。",
            "what_to_do_zh": "有慢病、怀孕、备孕、肝肾问题、正在用药、年龄较大或要做医美时，先找医生或合格专业人员。",
            "what_not_to_do_zh": "不要根据网上表格自行停药、加药或组合药物。",
            "github_path": "content/overview/start-here.md",
            "last_checked": TODAY,
        },
        {
            "guide_id": "draft-status",
            "title_zh": "为什么一直写“草稿”",
            "who_should_read": "担心内容是否已经最终定稿的人。",
            "plain_explanation_zh": "草稿表示已经自动整理和初步评分，但还没有把每篇核心文献都做完人工全文复核。",
            "what_to_do_zh": "可以用它快速了解方向，但不能把它当医学指南。",
            "what_not_to_do_zh": "不要把草稿内容作为个人治疗决定的唯一依据。",
            "github_path": "docs/content-audit-report-2026-04-29.md",
            "last_checked": TODAY,
        },
        {
            "guide_id": "claim-level",
            "title_zh": "同一个主题为什么要拆说法",
            "who_should_read": "看到一个主题等级后想知道到底能说什么的人。",
            "plain_explanation_zh": "同一主题有强说法和弱说法。比如防晒预防光老化可以是 A，但防晒逆转所有皱纹不能是 A。",
            "what_to_do_zh": "看 Claim 级评级表，先确认你关心的具体说法是否被支持。",
            "what_not_to_do_zh": "不要把一个强结论扩展成所有相关说法都成立。",
            "github_path": "content/overview/claim-level-grading.md",
            "last_checked": TODAY,
        },
        {
            "guide_id": "how-to-use-feishu",
            "title_zh": "飞书里先看哪张表",
            "who_should_read": "在飞书里找不到入口的人。",
            "plain_explanation_zh": "普通读者先看“新手阅读指南”和“普通读者主题指南”；研究管理者再看“文献库全量”和“核心复核队列”。",
            "what_to_do_zh": "按阅读顺序看：新手阅读指南、普通读者主题指南、Claim 级证据评级、补剂证据矩阵、文献库全量。",
            "what_not_to_do_zh": "不要一上来就钻进 5983 条文献库，容易迷路。",
            "github_path": "content/overview/feishu-reading-guide.md",
            "last_checked": TODAY,
        },
    ]
    return rows


def build_table_guides() -> list[dict[str, str]]:
    rows = [
        ("新手阅读指南", "给第一次看的普通读者。先读这个。", "读标题、解释、该做什么、不该做什么。", "所有人"),
        ("普通读者主题指南", "把 28 个主题翻译成人话。", "先看等级，再看普通人怎么看、要不要问医生。", "普通读者"),
        ("术语解释", "解释 RCT、终点、biomarker、GRADE 等词。", "看到不懂的词就来查。", "普通读者和编辑"),
        ("对外总览", "健康寿命主图谱的 20 个主题总表。", "看哪些方向更成熟，哪些仍早期。", "普通读者"),
        ("外观抗老总览", "皮肤和外观抗老的 8 个主题。", "区分皮肤证据和寿命证据。", "普通读者"),
        ("补剂证据矩阵", "100 个补剂/成分的证据边界。", "重点看不支持的说法和安全边界。", "普通读者"),
        ("Claim级证据评级", "把每个主题拆成具体说法。", "确认某句话是否被支持。", "编辑和严肃读者"),
        ("PICO_PECO问题框架", "每个主题到底问什么问题。", "看研究对象、干预/暴露、对照和结局。", "研究管理者"),
        ("核心复核队列", "A/B 级主题需要优先人工复核的核心文献。", "按 P1/P2 和工具逐条复核。", "内部复核者"),
        ("方法学复核计划", "告诉复核者该用 AMSTAR 2、RoB 2 还是 ROBINS-I。", "按工具填复核结论。", "内部复核者"),
        ("文献库全量", "5983 条全量文献候选库。", "搜索 PMID、标题、主题，确认文献是否已入库。", "内部和进阶读者"),
        ("文献总表", "900 条当前较高权重的证据矩阵。", "看正式纳入候选的研究类型、终点、等级。", "研究管理者"),
        ("候选文献", "原始候选池和同步字段。", "保留全部来源，不代表都支持结论。", "内部管理者"),
        ("发布日志", "每次 GitHub 和飞书同步记录。", "看什么时候更新了什么。", "项目管理者"),
    ]
    return [
        {
            "table_guide_id": f"table-{i:02d}",
            "table_name": name,
            "plain_purpose_zh": purpose,
            "how_to_read_zh": how,
            "best_for": best_for,
            "do_not_misread_zh": "表里的记录不等于个人建议；涉及疾病、药物、医美和高剂量补剂时先问专业人员。",
            "last_checked": TODAY,
        }
        for i, (name, purpose, how, best_for) in enumerate(rows, 1)
    ]


def build_glossary() -> list[dict[str, str]]:
    terms = [
        ("健康寿命", "不是只看活多久，而是看能不能少生病、功能更好、生活质量更高。", "运动、血压、饮食、睡眠都属于健康寿命话题。"),
        ("抗衰", "很容易被商业宣传滥用。本项目只把它当作研究问题，不把它当承诺。", "NMN、雷帕霉素、senolytics 都要谨慎。"),
        ("外观抗老", "主要看皮肤外观，例如光老化、皱纹、色斑、水分、屏障。", "防晒是外观抗老基础证据。"),
        ("证据等级", "表示当前证据可靠程度，不是个人行动命令。", "A 比 C 更可靠，但 A 也不等于你应该马上做。"),
        ("A 级", "当前比较可靠、可优先理解的方向。", "防晒预防光老化、血压管理等。"),
        ("B 级", "有较多支持，但仍有限制。", "热量限制、限时进食等。"),
        ("C 级", "有线索，但不够确定。", "很多补剂和前沿机制方向。"),
        ("D 级", "很早期，多为动物、细胞或机制研究。", "小鼠寿命实验不能直接变成人类建议。"),
        ("硬终点", "比较实在、重要的结果，比如死亡、心梗、卒中、骨折。", "比单纯指标变化更重要。"),
        ("软终点", "有意义但不一定等于真正健康获益的结果，比如皮肤水分、皱纹评分、某些体感指标。", "皮肤水分改善不等于延寿。"),
        ("Biomarker 生物标志物", "身体里的某个指标，可能提示风险或变化，但不一定代表真正结局。", "表观遗传时钟变年轻不等于一定活得更久。"),
        ("RCT 随机对照试验", "把人随机分到干预组和对照组，通常比普通观察更可靠。", "但也要看样本量、时间和偏倚。"),
        ("系统综述", "把同一问题的很多研究系统找出来、整理和评价。", "质量高低要用 AMSTAR 2 等工具看。"),
        ("Meta 分析", "把多个研究的数据合并计算。", "合并不代表一定正确，要看研究是否能合并。"),
        ("队列研究", "跟踪一群人一段时间，看暴露和结局关系。", "能发现关联，但不一定证明因果。"),
        ("机制研究", "解释可能为什么有效，常见于细胞、动物或分子层面。", "机制好看不等于人体有效。"),
        ("动物研究", "在小鼠等动物上做实验。", "很重要，但不能直接当成人类建议。"),
        ("相关不等于因果", "两个事情一起出现，不代表一个一定导致另一个。", "睡眠差和疾病相关，但具体原因要进一步研究。"),
        ("风险偏倚", "研究设计或执行中的问题，可能让结果看起来比真实更好或更差。", "没有盲法、失访多、选择性报告都可能带来偏倚。"),
        ("GRADE", "一种评价证据确定性的成熟框架。", "帮助判断结论有多可靠。"),
        ("RoB 2", "Cochrane 用来评估随机试验偏倚风险的工具。", "看随机化、缺失数据、选择性报告等。"),
        ("ROBINS-I", "评估非随机研究偏倚风险的工具。", "常用于观察研究。"),
        ("AMSTAR 2", "评估系统综述质量的工具。", "看检索是否全面、偏倚是否处理等。"),
        ("IF 影响因子", "期刊层面的影响力指标，不等于单篇文章质量。", "高 IF 文章也可能有偏倚，低 IF 文章也可能有价值。"),
        ("RCR", "NIH iCite 的文章层影响力指标，考虑领域和时间差异。", "比单看期刊名更接近单篇文章影响。"),
        ("OpenAlex 引用数", "开放数据库中的被引用次数。", "引用多不一定代表结论正确。"),
        ("PMID", "PubMed 给每篇文献的编号。", "可以用 PMID 快速找到原文摘要。"),
        ("DOI", "论文的数字对象标识。", "像论文身份证。"),
        ("PubMed", "医学和生命科学文献数据库。", "本项目优先使用 PubMed。"),
        ("PICO", "研究问题框架：人群、干预、对照、结局。", "用来防止问题问得太模糊。"),
        ("PECO", "类似 PICO，但用于暴露因素。", "如 LDL-C 暴露和心血管风险。"),
        ("Claim 级评级", "不是给整个主题一句话定生死，而是给具体说法评级。", "防晒预防光老化=A；防晒逆转全部老化不支持。"),
        ("医学监督", "需要医生或专业人员判断。", "处方药、慢病、怀孕、医美操作都需要。"),
        ("补剂", "膳食补充剂，不是药。", "不应替代治疗，也不应自行高剂量叠加。"),
        ("医美", "激光、换肤、注射、设备等专业操作。", "效果和风险都与机构、医生、设备和个体情况有关。"),
        ("光老化", "紫外线和可见光等造成的皮肤老化表现。", "防晒主要预防和减缓光老化。"),
        ("UV 紫外线", "阳光中会伤害皮肤的波段之一。", "UVA 和 UVB 都需要关注。"),
        ("草稿状态", "说明内容已自动整理，但还没完成全部人工全文复核。", "可以读，不要当最终指南。"),
        ("正式纳入", "比候选更靠前，进入证据矩阵，但仍需看复核状态。", "不是个人处方。"),
        ("候选文献", "先收进库里的文献，等待筛选和复核。", "候选不代表支持结论。"),
    ]
    return [
        {
            "term_id": f"term-{i:03d}",
            "term_zh": term,
            "plain_explanation_zh": explanation,
            "example_zh": example,
            "reader_warning_zh": "不要只看一个术语就下健康决定；要结合主题等级、边界和医生建议。",
            "last_checked": TODAY,
        }
        for i, (term, explanation, example) in enumerate(terms, 1)
    ]


def build_topic_guides() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    public = read_csv(DATA / "public_summary.csv")
    skin = read_csv(DATA / "skin_beauty_summary.csv")
    for domain, source_rows in [("健康寿命", public), ("外观抗老", skin)]:
        for index, row in enumerate(source_rows, 1):
            level = row.get("evidence_level_top", "")
            strength, meaning, action = level_plain(level)
            title = row.get("title_zh", "")
            topic_id = row.get("topic_id", "")
            rows.append(
                {
                    "reader_topic_id": f"reader-{domain}-{topic_id}",
                    "display_order": str(index),
                    "domain": domain,
                    "topic_id": topic_id,
                    "title_zh": title,
                    "title_en": row.get("title_en", ""),
                    "public_level": level,
                    "level_plain_zh": strength,
                    "one_sentence_zh": row.get("current_public_position_zh", ""),
                    "what_this_means_for_reader_zh": reader_action(topic_id, title, level),
                    "what_not_to_conclude_zh": row.get("reader_boundary_zh", row.get("recommendation_boundary", "")),
                    "doctor_or_professional_needed_zh": doctor_rule(topic_id, title, level),
                    "how_to_read_next_zh": "先看这一行，再看 Claim 级证据评级；如果想追原文，再去文献库全量搜索 PMID 或标题。",
                    "evidence_level_explained_zh": f"{level} 级：{meaning} {action}",
                    "last_checked": TODAY,
                }
            )
    return rows


def write_markdown(guides: list[dict[str, str]], table_guides: list[dict[str, str]], glossary: list[dict[str, str]], topic_guides: list[dict[str, str]]) -> None:
    OVERVIEW.mkdir(parents=True, exist_ok=True)
    start_lines = [
        "# 从这里开始 / Start Here",
        "",
        "> 草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。",
        "> Draft status: automatically prepared; not fully reviewed; not medical advice.",
        "",
        "## 这个项目是干什么的",
        "",
        "这是一个中英文双语证据图谱。它把长寿、健康寿命、外观抗老、皮肤健康和补剂相关研究整理成表格和文章，帮助读者先看清楚证据强弱和不能夸大的地方。",
        "",
        "它不是药品、补剂、医美或剂量推荐。它也不是个人体检报告。你可以用它了解方向，但不能用它替代医生、营养师或合格专业人员的判断。",
        "",
        "## 最简单的阅读顺序",
        "",
        "1. 先看本页，知道项目边界。",
        "2. 再看 [普通读者主题指南](reader-topic-guide.md)，找到你关心的主题。",
        "3. 看 [证据等级白话说明](evidence-levels-plain-language.md)，理解 A/B/C/D/E。",
        "4. 如果想看具体说法，看 [Claim 级评级](claim-level-grading.md)。",
        "5. 如果想查论文，再去飞书或 CSV 的“文献库全量”。",
        "",
        "## 先记住三句话",
        "",
        "- A 级也不等于你应该马上去做，它只是说明这个方向证据比较可靠。",
        "- C/D 级不是一定没用，而是目前还早，不能当确定建议。",
        "- 药物、疾病、医美、高剂量补剂，一律先问医生或专业人员。",
        "",
        "## 飞书里先看哪里",
        "",
        "| 你是谁 | 先看 | 再看 |",
        "|---|---|---|",
        "| 普通读者 | 新手阅读指南、普通读者主题指南 | Claim级证据评级、补剂证据矩阵 |",
        "| 想查补剂的人 | 补剂证据矩阵 | 术语解释、Claim级证据评级 |",
        "| 内部复核者 | 核心复核队列 | 方法学复核计划、文献库全量 |",
        "| 想找原始文献的人 | 文献库全量 | 文献总表、候选文献 |",
    ]
    (OVERVIEW / "start-here.md").write_text("\n".join(start_lines) + "\n", encoding="utf-8")

    level_lines = [
        "# 证据等级白话说明 / Plain-Language Evidence Levels",
        "",
        "> 草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。",
        "> Draft status: automatically prepared; not fully reviewed; not medical advice.",
        "",
        "## 等级不是行动命令",
        "",
        "等级只回答一个问题：这个说法目前有多可靠。它不回答你个人是否应该做、做多少、买什么、用什么药。",
        "",
        *md_table(
            ["等级", "白话意思", "普通人怎么看", "常见误读"],
            [
                ["A", "比较可靠。通常有人体证据、重要终点或强共识。", "优先理解，但仍要看边界。", "误读为马上照做或人人适用。"],
                ["B", "有不少支持，但还有限制。", "可以关注，适合继续看具体人群和条件。", "误读为已经完全确定。"],
                ["C", "有线索，但不够确定。", "当研究方向看，不适合激进尝试。", "误读为商家说的都成立。"],
                ["D", "很早期。多是动物、细胞或机制。", "只能当科学前沿看。", "误读为人类也有效。"],
                ["E", "信息不足或证据太弱。", "先不要作为行动依据。", "误读为只是还没火。"],
            ],
        ),
        "",
        "## 为什么要看 Claim 级评级",
        "",
        "一个主题里可能有强结论，也有不支持的说法。防晒就是例子：防晒预防 UV 相关光老化可以是 A；但防晒逆转所有皱纹、替代医美或证明某个产品最好，不能继承 A。",
    ]
    (OVERVIEW / "evidence-levels-plain-language.md").write_text("\n".join(level_lines) + "\n", encoding="utf-8")

    feishu_lines = [
        "# 飞书阅读指南 / How to Read the Feishu Base",
        "",
        "> 草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。",
        "> Draft status: automatically prepared; not fully reviewed; not medical advice.",
        "",
        "## 不要一上来就看 5983 条文献",
        "",
        "全量文献库是给查证和管理用的。普通读者如果直接看，会很容易迷路。更好的顺序是：先看指南，再看主题，再看具体 claim，最后再查文献。",
        "",
        *md_table(
            ["飞书表", "用途", "怎么读", "适合谁"],
            [[row["table_name"], row["plain_purpose_zh"], row["how_to_read_zh"], row["best_for"]] for row in table_guides],
        ),
    ]
    (OVERVIEW / "feishu-reading-guide.md").write_text("\n".join(feishu_lines) + "\n", encoding="utf-8")

    glossary_lines = [
        "# 术语解释 / Plain-Language Glossary",
        "",
        "> 草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。",
        "> Draft status: automatically prepared; not fully reviewed; not medical advice.",
        "",
        *md_table(
            ["术语", "白话解释", "例子"],
            [[row["term_zh"], row["plain_explanation_zh"], row["example_zh"]] for row in glossary],
        ),
    ]
    (OVERVIEW / "plain-language-glossary.md").write_text("\n".join(glossary_lines) + "\n", encoding="utf-8")

    topic_lines = [
        "# 普通读者主题指南 / Reader Topic Guide",
        "",
        "> 草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。",
        "> Draft status: automatically prepared; not fully reviewed; not medical advice.",
        "",
        "这张表把研究语言翻译成普通读者能读懂的话。先看“普通人怎么看”和“不要怎么理解”。",
        "",
        *md_table(
            ["领域", "主题", "等级", "普通人怎么看", "不要怎么理解", "要不要问医生"],
            [
                [
                    row["domain"],
                    row["title_zh"],
                    row["public_level"],
                    row["what_this_means_for_reader_zh"],
                    row["what_not_to_conclude_zh"],
                    row["doctor_or_professional_needed_zh"],
                ]
                for row in topic_guides
            ],
        ),
    ]
    (OVERVIEW / "reader-topic-guide.md").write_text("\n".join(topic_lines) + "\n", encoding="utf-8")


def patch_public_summary() -> None:
    path = OVERVIEW / "public-summary.md"
    text = path.read_text(encoding="utf-8")
    additions = [
        "| 新手阅读指南 | 给第一次打开项目的人，先讲这个项目是什么、不是什么、怎么读。 | [从这里开始](start-here.md) |",
        "| 普通读者主题指南 | 把 28 个主题翻译成白话，说明普通人怎么看、哪些需要问医生。 | [普通读者主题指南](reader-topic-guide.md) |",
        "| 证据等级白话说明 | 用普通话解释 A/B/C/D/E，不把等级误读成处方。 | [证据等级白话说明](evidence-levels-plain-language.md) |",
        "| 飞书阅读指南 | 说明飞书里每张表是干什么的，先看哪张，后看哪张。 | [飞书阅读指南](feishu-reading-guide.md) |",
        "| 术语解释 | 解释 RCT、biomarker、硬终点、IF、GRADE 等词。 | [术语解释](plain-language-glossary.md) |",
    ]
    if "start-here.md" in text:
        return
    marker = "| Claim 级评级 | 把同一主题拆成“支持的说法”和“不能外推的说法”，并配 PICO/PECO。 | [Claim 级评级](claim-level-grading.md) |"
    if marker in text:
        text = text.replace(marker, marker + "\n" + "\n".join(additions))
    else:
        text += "\n\n## 普通读者入口\n\n" + "\n".join(additions) + "\n"
    path.write_text(text, encoding="utf-8")


def write_report(guides: list[dict[str, str]], table_guides: list[dict[str, str]], glossary: list[dict[str, str]], topic_guides: list[dict[str, str]]) -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 普通读者可读性升级报告 / Reader-Friendly Upgrade Report",
        "",
        f"- 日期：{TODAY}",
        "- 目标读者：40-50 岁、不是生物科技背景、希望快速看懂证据边界的人。",
        "- 原则：先解释，再给表；先说能看什么，再说不能怎么理解；所有药物、疾病、医美和高风险补剂都保留专业评估边界。",
        "",
        "## 新增内容",
        "",
        *md_table(
            ["产物", "数量", "作用"],
            [
                ["data/reader_guides.csv", len(guides), "给普通读者的分步说明。"],
                ["data/reader_topic_guide.csv", len(topic_guides), "28 个主题的白话解释。"],
                ["data/plain_language_glossary.csv", len(glossary), "术语解释。"],
                ["data/feishu_table_guide.csv", len(table_guides), "飞书表格使用说明。"],
                ["content/overview/start-here.md", 1, "项目第一入口。"],
                ["content/overview/reader-topic-guide.md", 1, "普通读者主题指南。"],
                ["content/overview/evidence-levels-plain-language.md", 1, "证据等级白话说明。"],
                ["content/overview/feishu-reading-guide.md", 1, "飞书阅读路径。"],
                ["content/overview/plain-language-glossary.md", 1, "术语表。"],
            ],
        ),
        "",
        "## 飞书同步目标",
        "",
        "- 新手阅读指南",
        "- 普通读者主题指南",
        "- 术语解释",
        "- 飞书表格使用说明",
        "",
        "## 后续还能继续做的提升",
        "",
        "1. 给每个主题页顶部加入 3 行白话摘要：一句话结论、适合谁看、不要怎么理解。",
        "2. 给补剂矩阵加“普通人一句话提醒”字段，例如“不要作为购买建议”。",
        "3. 给 A/B 级主题做短文版解释，每篇控制在 800-1200 字。",
        "4. 在飞书里为普通读者创建单独视图，隐藏复杂字段，只保留等级、白话解释、边界、是否需要医生。",
    ]
    (DOCS / f"reader-friendly-upgrade-report-{TODAY}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    guides = build_reader_guides()
    table_guides = build_table_guides()
    glossary = build_glossary()
    topic_guides = build_topic_guides()
    write_csv(
        DATA / "reader_guides.csv",
        guides,
        ["guide_id", "title_zh", "who_should_read", "plain_explanation_zh", "what_to_do_zh", "what_not_to_do_zh", "github_path", "last_checked"],
    )
    write_csv(
        DATA / "feishu_table_guide.csv",
        table_guides,
        ["table_guide_id", "table_name", "plain_purpose_zh", "how_to_read_zh", "best_for", "do_not_misread_zh", "last_checked"],
    )
    write_csv(
        DATA / "plain_language_glossary.csv",
        glossary,
        ["term_id", "term_zh", "plain_explanation_zh", "example_zh", "reader_warning_zh", "last_checked"],
    )
    write_csv(
        DATA / "reader_topic_guide.csv",
        topic_guides,
        [
            "reader_topic_id",
            "display_order",
            "domain",
            "topic_id",
            "title_zh",
            "title_en",
            "public_level",
            "level_plain_zh",
            "one_sentence_zh",
            "what_this_means_for_reader_zh",
            "what_not_to_conclude_zh",
            "doctor_or_professional_needed_zh",
            "how_to_read_next_zh",
            "evidence_level_explained_zh",
            "last_checked",
        ],
    )
    write_markdown(guides, table_guides, glossary, topic_guides)
    patch_public_summary()
    write_report(guides, table_guides, glossary, topic_guides)
    print(
        f"reader-friendly layer built: guides={len(guides)}, table_guides={len(table_guides)}, "
        f"glossary={len(glossary)}, topic_guides={len(topic_guides)}"
    )


if __name__ == "__main__":
    main()
