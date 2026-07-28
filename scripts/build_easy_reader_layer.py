"""Build an easy-reader layer for non-specialist readers.

This layer is intentionally separate from the research-facing atlas. It creates
short Chinese-only pages and Feishu-ready CSVs for readers who may not know
medical research terms.
"""

from __future__ import annotations

import csv
import os
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PUBLIC_READER = ROOT / "content" / "public-reader"
DOCS = ROOT / "docs"
TODAY = date.today().isoformat()
MONTH = os.environ.get("EVIDENCE_ATLAS_ASSET_MONTH", "2026-07")
SNAPSHOT_DATE = os.environ.get("EVIDENCE_ATLAS_UPDATE_DATE", TODAY)
RELEASE_LABEL = os.environ.get("EVIDENCE_ATLAS_RELEASE_LABEL", "7 月中旬")
RELEASE_FILE = os.environ.get("EVIDENCE_ATLAS_RELEASE_FILE", "mid-july-2026-update.md")
RELEASE_EXPORT_NAME = os.environ.get("EVIDENCE_ATLAS_RELEASE_EXPORT_NAME", "001-2026-07中旬更新说明.md")
FEISHU_NAV_URL = os.environ.get(
    "EVIDENCE_ATLAS_FEISHU_NAV_URL",
    "https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tblVZxT68e7JiBTv",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def count_csv(path: Path) -> int:
    if not path.exists():
        return 0
    return len(read_csv(path))


def paper_page_count() -> int:
    papers = ROOT / "content" / "papers"
    return sum(1 for path in papers.glob("*.md") if not path.name.startswith("_"))


def clean(text: str) -> str:
    text = text or ""
    text = text.replace("等级已按 v0.4 综合评分重算；A 不等于个人处方建议。", "")
    text = text.replace("等级已按 v0.4 综合评分重算；", "")
    text = text.replace("A 不等于个人处方建议。", "")
    text = text.replace("Draft status: automatically prepared; not fully reviewed; not medical advice.", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def shorten(text: str, limit: int = 78) -> str:
    text = clean(text)
    if len(text) <= limit:
        return text
    for mark in ["。", "；", "，"]:
        cut = text.find(mark)
        if 20 <= cut <= limit:
            return text[: cut + 1]
    return text[:limit].rstrip("，；。 ") + "。"


def level_word(level: str) -> str:
    return {
        "A": "较强",
        "B": "中等",
        "C": "有限",
        "D": "很早期",
        "E": "不足",
    }.get(level, "待定")


def level_sentence(level: str) -> str:
    return {
        "A": "证据比较扎实，可以优先了解，但不是个人处方。",
        "B": "有不少支持，可以关注，但还要看适合谁。",
        "C": "有线索，但还不能当确定建议。",
        "D": "多是早期或机制线索，先当科学方向看。",
        "E": "信息太少，先不要作为行动依据。",
    }.get(level, "信息还不够，先不要下结论。")


def doctor_need(topic_id: str, text: str, level: str) -> str:
    topic_id = topic_id.lower()
    medical_keys = [
        "blood-pressure",
        "ldl",
        "glp1",
        "metformin",
        "rapamycin",
        "senolytics",
        "retinoids",
        "energy",
        "device",
        "resurfacing",
        "pdrn",
        "polynucleotide",
        "skin-boosters",
    ]
    if any(key in topic_id for key in medical_keys):
        return "需要。疾病指标、处方药或医美操作，要专业评估。"
    if "医生" in text or "专业" in text or "处方" in text or "医美" in text:
        return "可能需要。只了解原则不用；准备尝试前要看个人情况。"
    if level in {"C", "D", "E"}:
        return "阅读不用；要自己尝试，先做专业评估。"
    return "阅读不用；慢病、用药、孕期、高龄或明显不适时需要。"


def simple_topic_takeaway(topic_id: str, title: str, position: str, boundary: str, level: str) -> str:
    topic_id = topic_id.lower()
    if "fitness" in topic_id:
        return "简单说，就是心肺能力越好，长期健康风险通常越低。不要突然猛练。"
    if "physical-activity" in topic_id:
        return "规律活动、少久坐，是最值得先做好的基础方向之一。"
    if "resistance" in topic_id:
        return "中年以后，肌肉和力量很重要；训练要循序渐进。"
    if "blood-pressure" in topic_id:
        return "知道并管理血压，比追逐抗衰产品更重要。用药问题交给医生。"
    if "ldl" in topic_id:
        return "LDL-C 和 apoB 是心血管风险的重要指标；是否用药要医生判断。"
    if "sleep" in topic_id:
        return "长期睡不好值得认真处理，打鼾严重或白天嗜睡要评估。"
    if "dietary" in topic_id:
        return "重点看整体饮食模式，不要迷信单一食物或超级补剂。"
    if "caloric" in topic_id:
        return "少吃一点可能有代谢好处，但不等于人人都该节食。"
    if "time-restricted" in topic_id:
        return "限时进食可关注，但不要把它当成万能减肥或延寿办法。"
    if "glp1" in topic_id:
        return "这是处方药主题，不是普通抗衰工具。"
    if "metformin" in topic_id:
        return "二甲双胍是药物，不是健康人随便吃的抗衰补剂。"
    if "rapamycin" in topic_id:
        return "雷帕霉素属于高风险药物方向，不能自行尝试。"
    if "nad" in topic_id or "nmn" in topic_id:
        return "NAD/NMN/NR 还属于候选方向，不等于已经证明能延寿。"
    if "epigenetic" in topic_id:
        return "表观遗传时钟是指标，不等于真正变年轻或活更久。"
    if "senolytics" in topic_id:
        return "清除衰老细胞是前沿方向，不是普通人自用方案。"
    if "sunscreen" in topic_id:
        return "防晒主要是预防和减缓光老化，不是逆转所有皮肤老化。"
    if "retinoids" in topic_id:
        return "维A酸类有皮肤证据，但处方、刺激和孕期风险要重视。"
    if "collagen" in topic_id:
        return "胶原肽主要看皮肤水分和弹性，不要理解成逆龄或延寿。"
    if "ceramide" in topic_id or "hyaluronic" in topic_id:
        return "主要看皮肤水分和屏障，不等于全身抗衰。"
    if "pdrn" in topic_id or "polynucleotide" in topic_id:
        return "PDRN/PN 要先分清外用、导入、注射和填充；撤稿记录要前置看。"
    return shorten(position or boundary or title, 82)


def simple_not_to_conclude(boundary: str, domain: str) -> str:
    boundary = clean(boundary)
    if domain == "皮肤外观":
        base = "不要把皮肤水分、皱纹或色斑改善说成延寿或逆龄。"
    else:
        base = "不要把群体研究直接当成个人方案。"
    if boundary:
        return shorten(base + " " + boundary, 110)
    return base


def supplement_summary(row: dict[str, str]) -> str:
    claim = clean(row.get("supported_claim_zh", ""))
    if not claim:
        summary = clean(row.get("summary_zh", ""))
        parts = [part for part in summary.split("。") if part]
        if parts and "证据" in parts[0] and len(parts) > 1:
            claim = parts[1]
        else:
            claim = summary
    if not claim or "先看安全边界" in claim:
        claim = clean(row.get("plain_takeaway_zh", ""))
    claim = claim.replace("可支持", "主要看")
    claim = claim.replace("可作为", "可看作")
    claim = claim.replace("候选证据", "证据线索")
    return shorten(claim, 82)


def public_safety_note(row: dict[str, str]) -> str:
    note = shorten(row.get("safety_plain_zh") or row.get("safety_notes_zh", ""), 96)
    note = note.replace("需提示", "要留意")
    note = note.replace("需要提示", "要留意")
    return note


def build_easy_topics() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    sources = [
        ("健康寿命", read_csv(DATA / "public_summary.csv")),
        ("皮肤外观", read_csv(DATA / "skin_beauty_summary.csv")),
    ]
    seq = 1
    for domain, source_rows in sources:
        for row in source_rows:
            topic_id = row["topic_id"]
            title = row["title_zh"]
            level = row.get("evidence_level_top", "")
            position = row.get("current_public_position_zh", "")
            boundary = row.get("reader_boundary_zh", "")
            if not boundary:
                boundary = row.get("recommendation_boundary", "")
            simple = simple_topic_takeaway(topic_id, title, position, boundary, level)
            rows.append(
                {
                    "编号": f"T{seq:03d}",
                    "领域": domain,
                    "主题": title,
                    "证据": f"{level or '待定'}：{level_word(level)}",
                    "一句话": shorten(position, 88),
                    "一句话总结": simple,
                    "常见误解": simple_not_to_conclude(boundary, domain),
                    "注意": doctor_need(topic_id, boundary + position, level),
                    "打开": "研究版主题页",
                    "研究版路径": row.get("github_topic_path", ""),
                    "更新日期": TODAY,
                }
            )
            seq += 1
    return rows


def build_easy_supplements() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index, row in enumerate(read_csv(DATA / "supplement_matrix.csv"), 1):
        health = row.get("longevity_evidence_level", "")
        skin = row.get("skin_beauty_evidence_level", "")
        need_doctor = row.get("medical_supervision_needed", "").lower() == "true"
        risk = row.get("commercial_overclaim_risk", "")
        rows.append(
            {
                "编号": f"S{index:03d}",
                "补剂": row.get("name_zh", ""),
                "英文名": row.get("name_en", ""),
                "类别": row.get("category", ""),
                "健康证据": f"{health or '待定'}：{level_word(health)}",
                "皮肤证据": f"{skin or '待定'}：{level_word(skin)}",
                "一句话总结": supplement_summary(row),
                "常见误解": shorten((row.get("unsupported_claim_zh") or row.get("overclaim_warning_plain_zh", "")).replace("常见误读：", ""), 96),
                "注意": public_safety_note(row),
                "专业评估": "慢病、用药、孕期备孕、肝肾问题或长期高剂量使用时需要。" if need_doctor else "阅读不用；长期、高剂量或多种叠加前再评估。",
                "商业宣传风险": {"high": "高", "medium": "中", "low": "低"}.get(risk, risk or "待定"),
                "更新日期": TODAY,
            }
        )
    return rows


def build_navigation() -> list[dict[str, str]]:
    candidate_count = count_csv(DATA / "candidate_sources.csv")
    return [
        {
            "编号": "N01",
            "我想了解": "我第一次打开这个项目",
            "打开": "大众版首页",
            "继续看": "大众主题速读",
            "说明": "这是证据地图，不是医疗建议或购买清单。",
            "避免": f"一上来翻 {candidate_count} 条文献库。",
        },
        {
            "编号": "N02",
            "我想了解": "我想看运动、睡眠、饮食",
            "打开": "大众主题速读中的健康寿命主题",
            "继续看": "研究版主题页",
            "说明": "先理解原则，再看个人边界。",
            "避免": "把群体研究直接照搬成个人方案。",
        },
        {
            "编号": "N03",
            "我想了解": "我想查补剂",
            "打开": "大众补剂速查",
            "继续看": "补剂证据矩阵",
            "说明": "阅读顺序：一句话总结、常见误解、注意、证据等级。",
            "避免": "把等级当购买建议。",
        },
        {
            "编号": "N04",
            "我想了解": "我想看护肤和外观抗老",
            "打开": "大众主题速读中的皮肤外观主题",
            "继续看": "皮肤主题页",
            "说明": "皮肤改善不等于延寿。",
            "避免": "把单个成分当万能方案。",
        },
        {
            "编号": "N05",
            "我想了解": "我想看药物或医美",
            "打开": "必须问医生的内容",
            "继续看": "研究版资料",
            "说明": "处方药、疾病指标、激光、换肤、注射都不能自己决定。",
            "避免": "按表格自行用药或停药。",
        },
        {
            "编号": "N06",
            "我想了解": "我想知道哪些成分或方向有撤稿记录",
            "打开": "撤稿风险怎么看",
            "继续看": "证据权重怎么看",
            "说明": "只统计近 20 年发表、且被 PubMed 标记为撤稿的记录，并用保守规则过滤。",
            "避免": "把撤稿多直接理解成某成分一定无效。",
        },
        {
            "编号": "N07",
            "我想了解": "我是维护者或研究者",
            "打开": "项目交接日志",
            "继续看": "核心复核队列和方法学复核计划",
            "说明": "GitHub 是事实源，飞书是展示层。",
            "避免": "在飞书手工改出另一套事实。",
        },
    ]


def build_home() -> list[dict[str, str]]:
    return [
        {
            "编号": "H01",
            "入口": "总览",
            "适合谁": "第一次打开项目的人",
            "一句话说明": "这是证据地图，不是医疗建议、用药建议或购买清单。",
            "常见误区": "看到 A 级就马上买产品、吃药或做医美。",
            "注意": "药物、处方、医美和高剂量补剂要专业评估。",
            "打开": "大众主题速读",
        },
        {
            "编号": "H02",
            "入口": "健康寿命",
            "适合谁": "关心运动、睡眠、饮食、血压、血脂的人",
            "一句话说明": "生活方式和风险指标比大多数抗衰产品更值得优先理解。",
            "常见误区": "把群体研究当成自己的训练处方或治疗方案。",
            "注意": "慢病、用药、高龄、孕期或明显不适时需要专业评估。",
            "打开": "大众主题速读",
        },
        {
            "编号": "H03",
            "入口": "补剂速查",
            "适合谁": "想查维生素、NMN、胶原蛋白、鱼油等的人",
            "一句话说明": "重点看证据、常见误解和安全边界。",
            "常见误区": "把补剂矩阵当购买清单。",
            "注意": "慢病、用药、孕期备孕、肝肾问题、长期高剂量使用时需要专业评估。",
            "打开": "大众补剂速查",
        },
        {
            "编号": "H04",
            "入口": "皮肤外观",
            "适合谁": "关心防晒、皱纹、色斑、屏障、医美的人",
            "一句话说明": "皮肤证据只回答皮肤问题，不回答延寿问题。",
            "常见误区": "把皮肤水分或皱纹改善说成逆龄或延寿。",
            "注意": "处方维A酸、激光、换肤、注射、皮肤病时需要专业评估。",
            "打开": "护肤与外观抗老速读",
        },
        {
            "编号": "H05",
            "入口": "撤稿观察",
            "适合谁": "想知道哪些成分或方向出现过撤稿记录的人",
            "一句话说明": "不只看论文数量，也看撤稿风险和复核状态。",
            "常见误区": "撤稿多就等于成分一定无效。",
            "注意": "撤稿是风险信号，不是购买、停用或治疗建议。",
            "打开": "撤稿风险怎么看",
        },
        {
            "编号": "H06",
            "入口": "必须问医生",
            "适合谁": "准备尝试药物、医美或高风险干预的人",
            "一句话说明": "药物、疾病指标、医美操作不能自己决定。",
            "常见误区": "按网上表格自行停药、加药、混药或做操作。",
            "注意": "需要专业评估。",
            "打开": "哪些内容必须先问医生",
        },
    ]


def md_table(headers: list[str], rows: list[list[str]], max_rows: int | None = None) -> str:
    shown = rows[:max_rows] if max_rows else rows
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in shown:
        safe = [str(cell).replace("|", "\\|").replace("\n", " ") for cell in row]
        lines.append("| " + " | ".join(safe) + " |")
    return "\n".join(lines)


def write_markdown_pages(home: list[dict[str, str]], topics: list[dict[str, str]], supplements: list[dict[str, str]], navigation: list[dict[str, str]]) -> None:
    candidate_count = count_csv(DATA / "candidate_sources.csv")
    matrix_count = count_csv(DATA / "evidence_matrix.csv")
    finding_count = count_csv(DATA / "evidence_findings.csv")
    skin_topic_count = count_csv(DATA / "skin_beauty_summary.csv")
    skin_finding_count = count_csv(DATA / "skin_beauty_findings.csv")
    retraction_target_count = count_csv(DATA / "retraction_risk_summary_20y.csv")
    retraction_row_count = count_csv(DATA / "retracted_publications_20y.csv")
    paper_count = paper_page_count()
    public_csv_rows = candidate_count * 2 + finding_count * 2 + matrix_count
    feishu_table_count = count_csv(DATA / f"feishu_live_tables_{MONTH.replace('-', '_')}.csv")

    intro = """# 大众版入口表

这页是总入口。先选你关心的问题，再进入对应页面。

## 三句话

1. 这里不是医疗建议，也不是购买清单。
2. 证据强，不等于你个人马上要做。
3. 补剂、药物、医美、慢病用药，一定要看安全边界。

## 你想了解什么
"""
    home_table = md_table(
        ["入口", "适合谁", "一句话说明", "常见误区", "注意"],
        [[r["入口"], r["适合谁"], r["一句话说明"], r["常见误区"], r["注意"]] for r in home],
    )
    write_text(PUBLIC_READER / "index.md", intro + "\n" + home_table + "\n")

    topics_intro = """# 大众主题速读

每个方向压成三件事：一句话总结、常见误解、注意。研究细节见研究版主题页。
"""
    topics_table = md_table(
        ["领域", "主题", "证据", "一句话总结", "常见误解", "注意"],
        [[r["领域"], r["主题"], r["证据"], r["一句话总结"], r["常见误解"], r["注意"]] for r in topics],
    )
    write_text(PUBLIC_READER / "topics.md", topics_intro + "\n" + topics_table + "\n")

    supplements_intro = """# 大众补剂速查

这页不是购买清单，不提供品牌、剂量或处方。阅读顺序：一句话总结、常见误解、注意、证据等级。
"""
    supplements_table = md_table(
        ["补剂", "健康证据", "皮肤证据", "一句话总结", "常见误解", "注意", "专业评估"],
        [
            [
                r["补剂"],
                r["健康证据"],
                r["皮肤证据"],
                r["一句话总结"],
                r["常见误解"],
                r["注意"],
                r["专业评估"],
            ]
            for r in supplements
        ],
    )
    write_text(PUBLIC_READER / "supplements.md", supplements_intro + "\n" + supplements_table + "\n")

    skin_rows = [r for r in topics if r["领域"] == "皮肤外观"]
    skin_intro = """# 大众护肤与外观抗老速读

这里回答皮肤和外观问题，不回答延寿问题。皮肤水分、皱纹、色斑改善，不等于全身变年轻。
"""
    skin_table = md_table(
        ["主题", "证据", "一句话总结", "常见误解", "注意"],
        [[r["主题"], r["证据"], r["一句话总结"], r["常见误解"], r["注意"]] for r in skin_rows],
    )
    write_text(PUBLIC_READER / "skin.md", skin_intro + "\n" + skin_table + "\n")

    doctor_intro = """# 哪些内容必须先问医生

普通阅读不需要医生。但如果你准备自己尝试，下面这些情况不要自己决定。

## 先做专业评估

- 处方药：GLP-1、二甲双胍、雷帕霉素等。
- 疾病指标：血压、血脂、血糖、肝肾功能异常。
- 医美操作：激光、换肤、注射、设备类项目。
- 高剂量或长期补剂：尤其是多种叠加使用。
- 特殊人群：孕期备孕、慢病、正在用药、高龄、肝肾问题。

## 避免

- 按表格自行停药、加药、换药。
- 把补剂当治疗。
- 把皮肤改善当延寿。
- 把动物实验当成人体结论。
"""
    write_text(PUBLIC_READER / "doctor-first.md", doctor_intro)

    evidence_weight = """# 证据权重怎么看

这页回答一个问题：为什么有些文献权重高，有些只能当线索。

## 一句话

我们不是按标题热度排序，而是按“研究对象、研究设计、终点硬度、来源深度、发表地/期刊、偏倚风险、外推风险”一起判断。

## 先分五层

| 层级 | 普通说法 | 我们怎么看 |
| --- | --- | --- |
| A | 比较扎实 | 多来自人体研究、硬终点或高质量系统综述，适合优先理解 |
| B | 有不少支持 | 有人体数据或较强一致性，但仍要看人群和边界 |
| C | 有线索 | 可以继续关注，不能当确定建议 |
| D | 很早期 | 多是机制、动物、细胞、小样本或替代指标 |
| E | 不足 | 信息太少，不能作为行动依据 |

## 什么文献权重更高

| 判断项 | 权重更高 | 权重更低 |
| --- | --- | --- |
| 研究对象 | 人体研究，尤其是目标人群相近 | 动物、细胞、体外实验 |
| 研究设计 | 系统综述、Meta 分析、随机对照试验、大队列、孟德尔随机化 | 个案、开放标签、小样本、没有对照 |
| 终点 | 死亡、心血管事件、骨折、痴呆、功能、疾病风险 | 只看某个指标、短期感受或机制变化 |
| 来源深度 | 有摘要、全文、PMCID、清楚方法和结果 | 只有题录或营销材料 |
| 发表地/期刊 | 顶级综合/临床期刊、领域头部期刊、正规专业期刊 | 未知来源、预印本、只在注册库里有记录 |
| 一致性 | 多个研究方向一致 | 单篇研究、结果冲突明显 |
| 风险 | 偏倚低、利益冲突少、可重复 | 商业宣传强、样本小、选择性报告 |

## 发表地怎么加权

我们给期刊和发表地单独做一层分级：

| 层级 | 加分 | 人话解释 |
| --- | ---: | --- |
| S | 10 | 顶级综合医学、综合科学或主要临床专科期刊 |
| A | 7 | 衰老、营养、代谢、老年医学、皮肤等领域头部期刊 |
| B | 4 | 常见正规专业或综合期刊 |
| C | 1 | 有 DOI/PMID 或注册记录，但不是高权重发表地 |
| D | 0 | 未知、缺少发表地或预印本 |

期刊好，只是加分；不代表这篇一定对。期刊普通，也不代表一定没价值。最后仍然要看研究是不是人体、终点是不是硬、样本是不是够、偏倚风险高不高。

## 我们怎么把文献筛成证据

1. 先进入候选库：来自 PubMed、Crossref、ClinicalTrials.gov 等来源。
2. 再按主题映射：看它属于运动、睡眠、血压、补剂、皮肤外观还是前沿技术。
3. 再做草稿抽取：提取研究对象、设计、终点、结论和不能外推的地方。
4. 再做权重评分：看设计、终点、人类相关性、来源深度、引用信号、发表地/期刊和偏倚风险。
5. 再进入公开矩阵：只有一部分高相关记录进入证据矩阵。
6. 最后保留边界：即使是 A/B 级，也不等于个人处方、剂量或购买建议。

## 三个常见误解

| 常见误解 | 正确理解 |
| --- | --- |
| 有论文就等于有效 | 论文只是入口，要看设计、终点和人群 |
| 指标变好就等于延寿 | 指标只是线索，不能直接等同死亡风险下降 |
| 动物延寿就等于人能延寿 | 动物研究有价值，但不能直接变成人体方案 |

## 普通人怎么用

- 先看 A/B 级生活方式和风险指标：运动、力量、睡眠、血压、血脂、血糖、腰围、防晒。
- 看补剂时，先看“常见误解”和“注意”，再看证据等级。
- 看到药物、医美、高剂量补剂，直接进入专业评估边界。
- 不要把证据矩阵当购买清单。
"""
    write_text(PUBLIC_READER / "evidence-weight.md", evidence_weight)

    nav_intro = """# 飞书大众阅读导航

这张表可以同步到飞书，作为普通读者的第一张导航表。
"""
    nav_table = md_table(
        ["我想了解", "打开", "继续看", "说明", "避免"],
        [[r["我想了解"], r["打开"], r["继续看"], r["说明"], r["避免"]] for r in navigation],
    )
    write_text(PUBLIC_READER / "feishu-navigation.md", nav_intro + "\n" + nav_table + "\n")

    start_here = f"""# 普通读者入口：从这里开始

**品牌 / Brand：** 宇多Yul细胞/yulcell<br>
**当前公开快照 / Current public snapshot：** {SNAPSHOT_DATE}

如果你第一次打开这个项目，读这一页。你不需要懂论文，也不需要懂医学统计。

这个项目做一件事：把“抗衰、长寿、补剂、护肤和前沿技术”的说法拆开，看它们到底有没有证据。

## 人话版

网上很多抗衰内容会把几种东西混在一起：

- 真的和健康寿命有关的事，比如运动、睡眠、血压、血脂、血糖、体重、控烟酒。
- 可能有帮助但要看人群和风险的事，比如补剂、体重管理药物、医美项目。
- 还在研究中的事，比如衰老时钟、动物延寿实验、清除衰老细胞、部分重编程。
- 商业宣传很容易夸大的事，比如把一个补剂说成逆龄，把皮肤变好说成延寿。

我们把这些东西分开写，避免普通人一看到“抗衰”两个字就被带去买东西。

## {RELEASE_LABEL}更新

本次快照包括 {candidate_count:,} 条候选文献、{finding_count:,} 条证据发现、{matrix_count:,} 条证据矩阵、{public_csv_rows:,} 行公开 CSV，以及 57 张图片。请先读[2026 年 {RELEASE_LABEL}更新说明]({RELEASE_FILE})，再按自己的问题选择下面的入口。

## 从这里进入

| 需求 | 打开 | 得到什么 |
| --- | --- | --- |
| 我完全不知道从哪里开始 | [大众版入口表](index.md) | 项目有哪几类内容 |
| 我想看 15 条结论 | [15 条结论](ten-takeaways.md) | 哪些抗衰说法最容易误解 |
| 我想知道哪些方向更靠谱 | [大众主题速读](topics.md) | 运动、睡眠、饮食、血压、血脂等主题怎么理解 |
| 我想知道证据怎么分级 | [证据权重怎么看](evidence-weight.md) | 哪些文献权重高，哪些只能当线索 |
| 我想知道哪些成分或方向有撤稿记录 | [撤稿风险怎么看](retractions.md) | 近 20 年发表且已撤稿的 PubMed 观察 |
| 我想查 NMN、鱼油、胶原蛋白、维生素 | [最常见 30 个补剂](supplements-top-30.md) | 常见补剂的结论、误解和注意 |
| 我想查完整补剂表 | [大众补剂速查](supplements.md) | 100 个补剂的证据和边界 |
| 我关心防晒、皱纹、色斑、屏障、医美 | [护肤与外观抗老速读](skin.md) | 皮肤证据和延寿证据不是一回事 |
| 我看到药物、医美、高剂量补剂 | [哪些内容必须先问医生](doctor-first.md) | 哪些情况不能自己决定 |

## 三个判断

1. 这个说法是人类研究，还是动物/细胞研究？
2. 它改善的是死亡、疾病风险和功能，还是只改善某个指标？
3. 它适合普通人了解，还是需要医生或专业人员参与？

能回答这三个问题，就不容易被“抗衰营销”带偏。

## 现有资产

| 资产 | 数量 | 说明 |
| --- | ---: | --- |
| 文献候选库 | {candidate_count} 条 | 原始资料池，不建议普通人直接看 |
| 证据矩阵 | {matrix_count} 条 | 已经筛过一轮的研究资料 |
| 健康寿命发现 | {finding_count} 条 | 和运动、代谢、疾病风险等有关的证据 |
| 健康寿命主题 | 20 个 | 普通人最常问的健康寿命方向 |
| 皮肤外观主题 | {skin_topic_count} 个 | 防晒、皱纹、色斑、屏障、PDRN/PN、医美等 |
| 皮肤外观证据 | {skin_finding_count} 条 | 只回答皮肤和外观，不等于延寿 |
| 补剂条目 | 100 个 | 看常见误解和注意最重要 |
| 撤稿观察目标 | {retraction_target_count} 个 | 补剂、护肤、抗衰前沿目标 |
| 撤稿明细 | {retraction_row_count} 条 | 近 20 年发表且题名匹配的 PubMed 撤稿记录 |
| 论文卡片 | {paper_count} 个 | 给研究者和深度读者查证 |
| 公开 CSV | {public_csv_rows} 行 | 五张处理层表的行数相加，不是独立论文数 |
| 图片资产 | 57 张 | 7 张主图和 50 张成分卡 |
| 飞书在线表 | {feishu_table_count} 张 | [打开飞书公开资产索引](../../docs/feishu-public-assets-{MONTH}.md) |

## English Summary

This is the plain-language entry page for non-specialist readers. The current snapshot is dated {SNAPSHOT_DATE} and contains {candidate_count:,} candidate records, {finding_count:,} findings, and {matrix_count:,} matrix rows. The project separates stronger human evidence from early research, biomarkers, animal studies, supplement marketing, and skin-appearance claims.

One boundary note: this project is for evidence review and content production. It does not provide personal medical advice, prescriptions, dosing protocols, diagnosis, or purchase recommendations."""
    write_text(PUBLIC_READER / "start-here.md", start_here)

    curated_index = """# 大众版入口表 / Easy Reader Home

第一次打开项目，从 [普通读者入口：从这里开始](start-here.md) 开始。然后按需求进入对应页面。

| 入口 | 适合谁 | 一句话说明 | 打开 |
| --- | --- | --- | --- |
| 总览 | 第一次打开项目的人 | 这是证据地图，不是购买清单 | [普通读者入口](start-here.md) |
| 15 条结论 | 想快速判断抗衰说法的人 | 最容易误解的抗衰结论 | [15 条结论](ten-takeaways.md) |
| 证据权重 | 想知道我们怎么筛文献的人 | 为什么有些文献权重高，有些只是线索 | [证据权重怎么看](evidence-weight.md) |
| 撤稿观察 | 想知道哪些成分或方向出现过撤稿记录的人 | 不只看论文数量，也看撤稿风险 | [撤稿风险怎么看](retractions.md) |
| 健康寿命 | 关心运动、睡眠、饮食、血压、血脂的人 | 生活方式和风险指标优先于神奇产品 | [大众主题速读](topics.md) |
| 常见补剂 | 想查维生素、NMN、胶原蛋白、鱼油等的人 | 30 个常见补剂的结论、误解和注意 | [最常见 30 个补剂](supplements-top-30.md) |
| 补剂总表 | 想完整搜索 100 个补剂的人 | 全量补剂的证据、误解和安全边界 | [大众补剂速查](supplements.md) |
| 皮肤外观 | 关心防晒、皱纹、色斑、屏障、医美的人 | 皮肤改善不等于延寿 | [护肤与外观抗老速读](skin.md) |
| 必须问医生 | 准备用药、做医美、长期高剂量补剂的人 | 药物、医美和高风险干预不能自己决定 | [哪些内容必须先问医生](doctor-first.md) |

## English

This page is the navigation table for non-specialist readers. Start with `start-here.md`, then choose the topic, supplement, skin, or doctor-first page based on what you want to understand."""
    write_text(PUBLIC_READER / "index.md", curated_index)

    curated_nav = f"""# 飞书阅读导航 / Feishu Reading Guide

**品牌 / Brand：** 宇多Yul细胞/yulcell<br>
**当前快照 / Current snapshot：** {SNAPSHOT_DATE}

第一次打开时，先用[飞书 {RELEASE_LABEL}阅读导航]({FEISHU_NAV_URL})。不要从 {candidate_count:,} 条全量候选库开始读。

## 普通读者包 / Public Reader Package

| 我想了解 | 打开哪个文件 | 下一步 |
| --- | --- | --- |
| 我第一次打开项目 | `000-普通读者入口-从这里开始.md` | `{RELEASE_EXPORT_NAME}` |
| 我想知道这次更新了什么 | `{RELEASE_EXPORT_NAME}` | `002-15条结论.md` |
| 我想看 15 条结论 | `002-15条结论.md` | `003-证据权重怎么看.md` |
| 我想知道证据怎么分级 | `003-证据权重怎么看.md` | `004-撤稿风险怎么看.md` |
| 我想找适合自己的主题入口 | `005-大众版入口表.md` | `006-大众主题速读.md` |
| 我想查常见补剂 | `007-最常见30个补剂.md` | `008-大众补剂速查.md` |
| 我想看护肤、防晒或医美 | `009-护肤与外观抗老速读.md` | `010-哪些内容必须先问医生.md` |
| 我想看成分图片 | `012-前50常见成分卡片库.md` | 飞书 50 张成分卡表 |
| 我想看热力图 | `013-抗衰研究热力图.md` | `014-{MONTH}月度更新报告.md` |

## 在线多维表格 / Live Bitable Tables

- [9 张飞书在线表总索引](../../docs/feishu-public-assets-{MONTH}.md)
- [普通读者导航：14 条入口]({FEISHU_NAV_URL})
- [热力图与证据产出图：6 条](https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tblASMHdK01yuvjL)
- [前 50 成分单卡：50 条](https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tbliLsUC2T8lXHla)
- [证据矩阵：{matrix_count:,} 条](https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tblLnS2g439w9pir)
- [全量文献候选库：{candidate_count:,} 条](https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tblIPdcBJPH6UkAE)

## 摆放原则 / Publishing Order

1. 普通读者空间只导入 `build/feishu-public-reader/` 的 15 个入口文件。
2. 研究维护空间再导入 `build/feishu-docs/` 全量包。
3. {paper_count:,} 个论文页面留在研究维护空间，不放在普通读者首页。
4. 热力图表示研究数量和证据分布，不表示疗效排行。

The Feishu layer is the structured Chinese reading and review interface. GitHub remains the versioned source of truth. These assets are not medical advice, prescriptions, dosing protocols, or purchase recommendations."""
    write_text(PUBLIC_READER / "feishu-navigation.md", curated_nav)


def write_report(home: list[dict[str, str]], topics: list[dict[str, str]], supplements: list[dict[str, str]], navigation: list[dict[str, str]]) -> None:
    report = f"""# 大众版知识库与飞书简化视图实施报告

日期：{SNAPSHOT_DATE}

## 这次做了什么

本次按“方向 B + 方向 C”新增一套独立的大众版阅读层，同时准备飞书可同步的简化 CSV。研究版资料、论文卡片和原始矩阵不被删除，也不被改写。

## 新增资产

| 资产 | 数量 | 用途 |
| --- | ---: | --- |
| 大众首页入口 | {len(home)} | 按需求进入对应页面 |
| 大众主题速读 | {len(topics)} | 覆盖 20 个健康寿命主题和 9 个皮肤外观主题 |
| 大众补剂速查 | {len(supplements)} | 覆盖 100 个补剂/营养条目 |
| 飞书大众导航 | {len(navigation)} | 给飞书做第一层导航 |

## 飞书建议新建或同步的表

| 表名 | CSV | 作用 |
| --- | --- | --- |
| 大众阅读首页 | data/easy_reader_home.csv | 第一入口 |
| 大众主题速读 | data/easy_reader_topics.csv | 29 个主题的人话解释 |
| 大众补剂速查 | data/easy_reader_supplements.csv | 100 个补剂的人话解释 |
| 大众阅读导航 | data/easy_reader_navigation.csv | 告诉读者打开哪张表 |

## 飞书 Markdown 导出

运行 `python scripts\\prepare_feishu_docs.py` 后，大众版页面会以 `public-reader-*.md` 文件名输出到 `build/feishu-docs/`，方便人工导入飞书时识别。

## 同步命令建议

```powershell
python scripts\\sync_feishu_csv_table.py --csv data/easy_reader_home.csv --table-name 大众阅读首页 --primary-key 编号 --primary-field 入口 --delete-stale
python scripts\\sync_feishu_csv_table.py --csv data/easy_reader_topics.csv --table-name 大众主题速读 --primary-key 编号 --primary-field 主题 --delete-stale
python scripts\\sync_feishu_csv_table.py --csv data/easy_reader_supplements.csv --table-name 大众补剂速查 --primary-key 编号 --primary-field 补剂 --delete-stale
python scripts\\sync_feishu_csv_table.py --csv data/easy_reader_navigation.csv --table-name 大众阅读导航 --primary-key 编号 --primary-field 我想了解 --delete-stale
```

## 读者层规则

- 第一层不出现 PICO、AMSTAR、ROBINS-I、RoB、v0.4、v0.5 等术语。
- 公开页优先使用“一句话总结、常见误解、注意”。
- 补剂页避免重复空话，优先放具体证据结论和安全边界。
- 药物、疾病指标、医美、高剂量补剂标出专业评估边界。
- 研究版内容仍保留给维护者和深度读者。
"""
    write_text(DOCS / f"easy-reader-layer-report-{SNAPSHOT_DATE}.md", report)


def main() -> None:
    home = build_home()
    topics = build_easy_topics()
    supplements = build_easy_supplements()
    navigation = build_navigation()

    write_csv(
        DATA / "easy_reader_home.csv",
        home,
        ["编号", "入口", "适合谁", "一句话说明", "常见误区", "注意", "打开"],
    )
    write_csv(
        DATA / "easy_reader_topics.csv",
        topics,
        ["编号", "领域", "主题", "证据", "一句话", "一句话总结", "常见误解", "注意", "打开", "研究版路径", "更新日期"],
    )
    write_csv(
        DATA / "easy_reader_supplements.csv",
        supplements,
        ["编号", "补剂", "英文名", "类别", "健康证据", "皮肤证据", "一句话总结", "常见误解", "注意", "专业评估", "商业宣传风险", "更新日期"],
    )
    write_csv(
        DATA / "easy_reader_navigation.csv",
        navigation,
        ["编号", "我想了解", "打开", "继续看", "说明", "避免"],
    )
    write_markdown_pages(home, topics, supplements, navigation)
    write_report(home, topics, supplements, navigation)
    print(
        "Easy reader layer built: "
        f"home={len(home)}, topics={len(topics)}, supplements={len(supplements)}, navigation={len(navigation)}"
    )


if __name__ == "__main__":
    main()
