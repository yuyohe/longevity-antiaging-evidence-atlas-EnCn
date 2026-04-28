"""Build the public-facing executive summary and overview table."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINDINGS = ROOT / "data" / "evidence_findings.csv"
MATRIX = ROOT / "data" / "evidence_matrix.csv"
SUMMARY_CSV = ROOT / "data" / "public_summary.csv"
SUMMARY_MD = ROOT / "content" / "overview" / "public-summary.md"

DRAFT_NOTICE_ZH = "草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。"
DRAFT_NOTICE_EN = "Draft status: automatically prepared; not fully reviewed; not medical advice."

TOPIC_ORDER = [
    "cardiorespiratory-fitness",
    "physical-activity-healthspan",
    "resistance-training-muscle",
    "blood-pressure-aging",
    "ldl-apob-cardiovascular-risk",
    "dietary-pattern-longevity",
    "sleep-aging",
    "glp1-weight-cardiometabolic",
    "caloric-restriction-human",
    "time-restricted-eating",
    "metformin-aging",
    "rapamycin-mtor-aging",
    "senolytics",
    "nad-nmn-nr-aging",
    "epigenetic-clocks",
    "itp-mouse-lifespan",
    "klotho-il11-aging",
    "partial-reprogramming",
    "autophagy-mitophagy",
    "microbiome-inflammaging",
]

TOPICS = {
    "cardiorespiratory-fitness": {
        "zh": "心肺适能与死亡风险",
        "en": "Cardiorespiratory Fitness and Mortality",
        "position": "目前最值得优先关注的健康寿命指标之一；较高心肺适能与更低死亡和心血管风险高度相关。",
        "know": "证据主要支持把心肺适能作为风险分层、运动干预和长期健康管理的核心指标。",
        "uncertain": "不同疾病人群、测试方式和干预强度之间仍需全文复核和分层。",
        "boundary": "可作为生活方式优先方向；个体运动处方需结合年龄、疾病和医生评估。",
    },
    "physical-activity-healthspan": {
        "zh": "身体活动与健康寿命",
        "en": "Physical Activity and Healthspan",
        "position": "整体证据方向稳定：规律身体活动支持更好的健康结局和功能维持。",
        "know": "观察研究、干预研究和指南体系普遍支持活动量、久坐减少和功能保持的重要性。",
        "uncertain": "最佳剂量、强度组合和不同慢病人群的个体化方案仍需分层。",
        "boundary": "支持行动方向，不等于给出单一万能运动处方。",
    },
    "resistance-training-muscle": {
        "zh": "抗阻训练、肌肉与衰弱",
        "en": "Resistance Training, Muscle, and Frailty",
        "position": "肌肉量、力量和功能是健康寿命的关键支点；抗阻训练是高优先级主题。",
        "know": "证据支持抗阻训练、综合运动和营养策略对肌少、衰弱和功能下降的管理价值。",
        "uncertain": "不同年龄、衰弱程度、合并症和训练模式下的最佳方案仍要细分。",
        "boundary": "可作为健康管理重点；高龄、骨质疏松或慢病人群需专业评估。",
    },
    "blood-pressure-aging": {
        "zh": "血压与健康寿命",
        "en": "Blood Pressure and Healthspan",
        "position": "血压控制是心脑血管风险和健康寿命管理中证据最成熟的方向之一。",
        "know": "硬终点、人群相关性和临床可行动性较强。",
        "uncertain": "不同年龄、虚弱状态和共病人群的目标值不能简单一刀切。",
        "boundary": "支持监测和医学管理；不提供药物选择或剂量建议。",
    },
    "ldl-apob-cardiovascular-risk": {
        "zh": "LDL-C/apoB 与心血管风险",
        "en": "LDL-C/apoB and Cardiovascular Risk",
        "position": "动脉粥样硬化风险管理中的核心证据方向；apoB/LDL-C 是重要风险指标。",
        "know": "遗传、队列和临床干预证据共同支持其风险解释价值。",
        "uncertain": "个体治疗阈值和药物策略需结合总体风险。",
        "boundary": "支持筛查和风险管理；药物治疗必须由医生决定。",
    },
    "dietary-pattern-longevity": {
        "zh": "饮食模式与死亡风险",
        "en": "Dietary Patterns and Mortality",
        "position": "饮食模式比单一补剂更适合作为对外健康建议框架。",
        "know": "整体饮食质量、能量平衡、蛋白和植物性食物结构等方向有较多流行病学和干预线索。",
        "uncertain": "不同文化、代谢状态和疾病背景下不能简单复制同一饮食方案。",
        "boundary": "支持模式层面的建议，不支持神化单一食物或补剂。",
    },
    "sleep-aging": {
        "zh": "睡眠与健康结局",
        "en": "Sleep and Aging Outcomes",
        "position": "睡眠是认知、代谢、心血管和整体健康的重要基础变量。",
        "know": "睡眠时长、睡眠质量、睡眠障碍与多类健康结局相关。",
        "uncertain": "因果方向、干预效果和不同睡眠问题的处理路径需要细分。",
        "boundary": "支持识别和管理睡眠问题；严重失眠、睡眠呼吸暂停需医疗评估。",
    },
    "glp1-weight-cardiometabolic": {
        "zh": "GLP-1、减重与心代谢结局",
        "en": "GLP-1, Weight Loss, and Cardiometabolic Outcomes",
        "position": "临床证据增长很快，主要价值在肥胖、糖代谢和心代谢风险管理。",
        "know": "部分药物在人群试验和真实世界研究中显示体重、糖代谢和心血管相关收益。",
        "uncertain": "长期安全性、停药后维持、非适应证使用和健康人群应用边界仍需谨慎。",
        "boundary": "这是医疗主题，不是普通抗衰保健建议；必须医生监督。",
    },
    "caloric-restriction-human": {
        "zh": "热量限制与人体衰老",
        "en": "Caloric Restriction in Humans",
        "position": "人体证据有价值但边界明显，不能直接等同于延寿已证实。",
        "know": "在人类中更适合讨论代谢、生物标志物和风险因素改善。",
        "uncertain": "长期依从性、安全性、肌肉骨骼影响和真实寿命终点尚不充分。",
        "boundary": "不建议盲目长期极端节食；需关注营养充足和个体风险。",
    },
    "time-restricted-eating": {
        "zh": "限时进食与代谢健康",
        "en": "Time-Restricted Eating and Metabolic Health",
        "position": "可作为代谢健康候选策略，但证据强度和适用人群仍不稳定。",
        "know": "部分研究提示体重、胰岛素敏感性或进食行为改善。",
        "uncertain": "与热量减少的独立作用、长期效果和不良反应仍需复核。",
        "boundary": "糖尿病、孕期、进食障碍或用药人群不应自行尝试。",
    },
    "metformin-aging": {
        "zh": "二甲双胍与衰老",
        "en": "Metformin and Aging",
        "position": "机制和流行病学兴趣很高，但健康人抗衰应用尚不能定论。",
        "know": "糖尿病和代谢疾病场景下证据更强，衰老干预仍处于验证阶段。",
        "uncertain": "非糖尿病人群、运动适应、长期净收益和真实健康寿命终点仍不清楚。",
        "boundary": "不支持自行用于抗衰；药物使用需医生判断。",
    },
    "rapamycin-mtor-aging": {
        "zh": "雷帕霉素/mTOR 与衰老",
        "en": "Rapamycin/mTOR and Aging",
        "position": "动物寿命证据强，人体健康寿命证据仍早期。",
        "know": "mTOR 通路是 geroscience 核心机制之一，动物和机制研究丰富。",
        "uncertain": "人体剂量、适应证、安全性、感染和代谢风险尚未解决。",
        "boundary": "不支持自行用药；任何尝试都属于医疗/研究级风险决策。",
    },
    "senolytics": {
        "zh": "Senolytics 清除衰老细胞",
        "en": "Senolytics",
        "position": "概念重要但临床证据仍早期，属于前沿研究而非成熟建议。",
        "know": "动物、机制和少量早期人体研究提示潜力。",
        "uncertain": "靶向性、安全性、适应证和长期效果仍未成熟。",
        "boundary": "不支持把 senolytics 当成已验证抗衰方案。",
    },
    "nad-nmn-nr-aging": {
        "zh": "NAD/NMN/NR",
        "en": "NAD/NMN/NR",
        "position": "补剂市场热度高，但人体硬终点证据不足。",
        "know": "部分研究关注 NAD 代谢、生物标志物和短期安全性。",
        "uncertain": "长期临床收益、真实健康寿命终点和不同人群反应尚不明确。",
        "boundary": "不支持宣传为逆龄或延寿已证实。",
    },
    "epigenetic-clocks": {
        "zh": "表观遗传时钟",
        "en": "Epigenetic Clocks",
        "position": "适合做风险和研究指标，不适合直接等同于真实年龄被逆转。",
        "know": "DNA 甲基化时钟与年龄、风险和干预研究高度相关。",
        "uncertain": "时钟变化是否代表临床收益仍需硬终点验证。",
        "boundary": "不能把 clock 下降直接写成延寿或逆龄已证实。",
    },
    "itp-mouse-lifespan": {
        "zh": "ITP 小鼠寿命干预",
        "en": "ITP Mouse Lifespan Interventions",
        "position": "动物寿命干预的重要筛选系统，但不能直接外推给人。",
        "know": "适合评估候选机制和干预方向的可重复性。",
        "uncertain": "跨物种转化、人类剂量和风险收益仍是核心限制。",
        "boundary": "只能作为转化线索，不能作为人类用药建议。",
    },
    "klotho-il11-aging": {
        "zh": "Klotho / IL-11",
        "en": "Klotho / IL-11",
        "position": "前沿机制方向，潜力较高但临床成熟度有限。",
        "know": "机制和动物研究提示与衰老表型、炎症和组织功能相关。",
        "uncertain": "人体疗法、递送、安全性和真实终点仍未建立。",
        "boundary": "目前不应作为个人干预建议。",
    },
    "partial-reprogramming": {
        "zh": "部分重编程",
        "en": "Partial Reprogramming",
        "position": "高度前沿且风险极高，更多属于未来技术储备。",
        "know": "细胞和动物模型提示表观遗传状态可塑性。",
        "uncertain": "肿瘤风险、组织特异性、可控性和人体应用仍是重大障碍。",
        "boundary": "不能作为现实抗衰建议或商业化承诺。",
    },
    "autophagy-mitophagy": {
        "zh": "自噬/线粒体自噬",
        "en": "Autophagy and Mitophagy",
        "position": "重要基础机制，但从机制到人类干预仍需严谨转化。",
        "know": "与细胞稳态、代谢压力、运动和多种疾病机制相关。",
        "uncertain": "如何安全、可控、长期地在人类中调节仍不明确。",
        "boundary": "不能把机制激活直接等同于抗衰成功。",
    },
    "microbiome-inflammaging": {
        "zh": "微生物组与炎症性衰老",
        "en": "Microbiome and Inflammaging",
        "position": "相关性丰富、机制复杂，干预结论仍需谨慎。",
        "know": "微生物组、炎症、代谢和免疫衰老之间存在大量关联证据。",
        "uncertain": "因果方向、个体差异和可重复干预效果仍是主要难点。",
        "boundary": "不支持把单一益生菌或菌群检测包装成抗衰方案。",
    },
}

FIELDNAMES = [
    "summary_id",
    "topic_id",
    "title_zh",
    "title_en",
    "current_public_position_zh",
    "current_public_position_en",
    "evidence_level_top",
    "recommendation_boundary",
    "finding_count",
    "formal_matrix_count",
    "pmc_or_abstract_count",
    "metadata_only_count",
    "what_we_know_zh",
    "what_remains_uncertain_zh",
    "reader_boundary_zh",
    "github_topic_path",
    "status",
    "last_checked",
]


def rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))


def top_level(levels: Counter[str]) -> str:
    for level in ["A", "B", "C", "D"]:
        if levels.get(level):
            return level
    return "pending"


def recommendation_boundary(topic_id: str) -> str:
    if topic_id in {"glp1-weight-cardiometabolic", "metformin-aging", "rapamycin-mtor-aging", "senolytics"}:
        return "medical_or_research_only"
    if topic_id in {"partial-reprogramming", "klotho-il11-aging", "itp-mouse-lifespan"}:
        return "research_only"
    if topic_id in {"nad-nmn-nr-aging", "epigenetic-clocks", "autophagy-mitophagy", "microbiome-inflammaging"}:
        return "do_not_overclaim"
    return "public_health_or_lifestyle_boundary"


def build_summary_rows() -> list[dict[str, str]]:
    findings = rows(FINDINGS)
    matrix = rows(MATRIX)
    findings_by_topic: dict[str, list[dict[str, str]]] = defaultdict(list)
    matrix_by_topic: dict[str, list[dict[str, str]]] = defaultdict(list)
    zh_to_topic_id = {topic["zh"]: topic_id for topic_id, topic in TOPICS.items()}
    for row in findings:
        findings_by_topic[row.get("topic_id", "")].append(row)
    for row in matrix:
        topic_id = row.get("topic_id", "") or zh_to_topic_id.get(row.get("topic", ""), "")
        matrix_by_topic[topic_id].append(row)

    out: list[dict[str, str]] = []
    for index, topic_id in enumerate(TOPIC_ORDER, start=1):
        topic = TOPICS[topic_id]
        topic_findings = findings_by_topic.get(topic_id, [])
        topic_matrix = matrix_by_topic.get(topic_id, [])
        levels = Counter(row.get("evidence_level", "") for row in topic_matrix)
        depth = Counter(row.get("evidence_source_depth", "") for row in topic_findings)
        abstract_count = depth.get("abstract_plus_open_pmc_available", 0) + depth.get("abstract_only", 0)
        out.append(
            {
                "summary_id": f"summary-{index:02d}-{topic_id}",
                "topic_id": topic_id,
                "title_zh": topic["zh"],
                "title_en": topic["en"],
                "current_public_position_zh": topic["position"],
                "current_public_position_en": f"Public draft position for {topic['en']}; see bilingual topic page for evidence boundaries.",
                "evidence_level_top": top_level(levels),
                "recommendation_boundary": recommendation_boundary(topic_id),
                "finding_count": str(len(topic_findings)),
                "formal_matrix_count": str(len(topic_matrix)),
                "pmc_or_abstract_count": str(abstract_count),
                "metadata_only_count": str(depth.get("metadata_only", 0)),
                "what_we_know_zh": topic["know"],
                "what_remains_uncertain_zh": topic["uncertain"],
                "reader_boundary_zh": topic["boundary"],
                "github_topic_path": f"content/topics/{topic_id}.md",
                "status": "public_draft_not_fully_reviewed",
                "last_checked": str(date.today()),
            }
        )
    return out


def write_csv(summary_rows: list[dict[str, str]]) -> None:
    SUMMARY_CSV.parent.mkdir(parents=True, exist_ok=True)
    with SUMMARY_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(summary_rows)


def write_markdown(summary_rows: list[dict[str, str]]) -> None:
    SUMMARY_MD.parent.mkdir(parents=True, exist_ok=True)
    total_findings = sum(int(row["finding_count"]) for row in summary_rows)
    total_matrix = sum(int(row["formal_matrix_count"]) for row in summary_rows)
    lines = [
        "# 长寿抗衰与健康寿命证据图谱：公开总览 / Public Summary",
        "",
        f"> {DRAFT_NOTICE_ZH}",
        f"> {DRAFT_NOTICE_EN}",
        "",
        "## 一句话说明",
        "",
        "这是一个中英双语、证据优先、可审计的长寿抗衰与健康寿命证据图谱。它不是药物、补剂或剂量推荐清单，而是把运动、心代谢、饮食、睡眠、药物、补剂和前沿 geroscience 技术按证据等级、终点价值和可转化边界重新整理。",
        "",
        "In short: this atlas separates mature healthspan evidence from early mechanistic or animal evidence, and makes the boundary visible before readers reach individual papers.",
        "",
        "## 当前版本说了什么",
        "",
        f"- 当前公开草稿覆盖 20 个主题、{total_findings} 条 finding、{total_matrix} 条正式纳入候选记录。",
        "- 最稳健的方向主要集中在心肺适能、身体活动、抗阻训练、血压、LDL-C/apoB、饮食模式和睡眠等公共健康或临床风险管理主题。",
        "- GLP-1、二甲双胍、雷帕霉素、senolytics、NAD/NMN/NR、表观遗传时钟和部分重编程等主题被保留为重点研究方向，但不会被写成普通人可以自行执行的抗衰建议。",
        "- 所有结论仍是公开草稿：自动整理已经完成，全文复核、人工校正和正式发布审稿仍在进行。",
        "",
        "## 不能这么说",
        "",
        "- 不能说某种药物、补剂或技术已经被证明可以让健康人延寿。",
        "- 不能把动物寿命实验直接写成人类延寿结论。",
        "- 不能把 biomarker 或表观遗传时钟改善直接写成“逆龄已证实”。",
        "- 不能根据单篇摘要给出剂量、处方或个人医疗建议。",
        "",
        "## 主题总览表",
        "",
        "| # | 主题 | 当前立场 | 证据等级草判 | 记录数 | 边界 |",
        "|---:|---|---|---|---:|---|",
    ]
    for index, row in enumerate(summary_rows, start=1):
        topic_link = f"[{row['title_zh']}](../topics/{row['topic_id']}.md)"
        lines.append(
            f"| {index} | {topic_link}<br>{row['title_en']} | {row['current_public_position_zh']} | "
            f"{row['evidence_level_top']} | {row['finding_count']} | {row['reader_boundary_zh']} |"
        )
    lines.extend(
        [
            "",
            "## 怎么读这个图谱",
            "",
            "1. 先读本页，了解哪些方向相对成熟、哪些仍是前沿研究。",
            "2. 再进入 20 个主题页，看该主题“我们知道什么、仍不确定什么、不能这么说”。",
            "3. 最后进入论文卡片，查看单篇研究的设计、结果、支持的结论和过度解读风险。",
            "",
            "## 内部管理方式",
            "",
            "- GitHub 是事实源：CSV、Markdown、方法学和脚本都从这里维护。",
            "- 飞书是展示和协作层：对外总览、主题库、候选文献、文献总表和发布日志用于筛选、复核和同步。",
            "- 正式发布前，应优先复核 `evidence_level_top=A` 且终点为硬终点或强临床相关终点的记录。",
        ]
    )
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    summary_rows = build_summary_rows()
    write_csv(summary_rows)
    write_markdown(summary_rows)
    print(f"Wrote {SUMMARY_CSV.relative_to(ROOT)} and {SUMMARY_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
