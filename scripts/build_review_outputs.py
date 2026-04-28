"""Build shortlist CSV and draft bilingual topic/paper pages from findings."""

from __future__ import annotations

import csv
import re
from datetime import date
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
FINDINGS = ROOT / "data" / "evidence_findings.csv"
SHORTLIST = ROOT / "data" / "shortlist_sources.csv"
TOPICS = ROOT / "data" / "topics.csv"
PAPERS = ROOT / "content" / "papers"
TOPIC_DIR = ROOT / "content" / "topics"

TOPIC_MAP = {
    "cardiorespiratory_fitness_mortality": ("cardiorespiratory-fitness", "心肺适能与死亡风险", "Cardiorespiratory Fitness and Mortality"),
    "resistance_training_mortality_sarcopenia": ("resistance-training-muscle", "抗阻训练、肌肉与衰弱", "Resistance Training, Muscle, and Frailty"),
    "physical_activity_longevity": ("physical-activity-healthspan", "身体活动与健康寿命", "Physical Activity and Healthspan"),
    "blood_pressure_mortality_aging": ("blood-pressure-aging", "血压与健康寿命", "Blood Pressure and Healthspan"),
    "ldl_apob_cardiovascular_mortality": ("ldl-apob-cardiovascular-risk", "LDL-C/apoB 与心血管风险", "LDL-C/apoB and Cardiovascular Risk"),
    "sleep_duration_mortality_aging": ("sleep-aging", "睡眠与健康结局", "Sleep and Aging Outcomes"),
    "dietary_pattern_longevity": ("dietary-pattern-longevity", "饮食模式与死亡风险", "Dietary Patterns and Longevity"),
    "caloric_restriction_human_aging": ("caloric-restriction-human", "热量限制与人体衰老", "Caloric Restriction in Humans"),
    "intermittent_fasting_aging_human": ("time-restricted-eating", "限时进食与代谢健康", "Time-Restricted Eating and Metabolic Health"),
    "glp1_obesity_cardiometabolic_outcomes": ("glp1-weight-cardiometabolic", "GLP-1、减重与心代谢结局", "GLP-1, Weight Loss, and Cardiometabolic Outcomes"),
    "metformin_aging_longevity": ("metformin-aging", "二甲双胍与衰老", "Metformin and Aging"),
    "rapamycin_mtor_aging": ("rapamycin-mtor-aging", "雷帕霉素/mTOR 与衰老", "Rapamycin/mTOR and Aging"),
    "senolytics_human_aging": ("senolytics", "Senolytics 与细胞衰老", "Senolytics and Cellular Senescence"),
    "nad_nmn_nr_human_aging": ("nad-nmn-nr-aging", "NAD/NMN/NR 与衰老", "NAD/NMN/NR and Aging"),
    "epigenetic_clocks_intervention": ("epigenetic-clocks", "表观遗传时钟与干预", "Epigenetic Clocks and Interventions"),
}


def slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return value[:80] or "paper"


def rank_key(row: Dict[str, str]) -> tuple[int, int]:
    level_score = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5}.get(row.get("evidence_level_draft", "E"), 5)
    endpoint_score = {"H1": 0, "H2": 1, "H3": 2, "H5": 3, "H4": 4, "H6": 5}.get(row.get("endpoint_class_draft", "H6"), 6)
    return level_score, endpoint_score


def read_findings() -> List[Dict[str, str]]:
    with FINDINGS.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    return sorted(rows, key=rank_key)


def build_shortlist(rows: List[Dict[str, str]], limit: int = 60) -> List[Dict[str, str]]:
    shortlist: List[Dict[str, str]] = []
    for i, row in enumerate(rows[:limit], start=1):
        topic_id, topic_zh, topic_en = TOPIC_MAP.get(row["query"], (row["query"], row["query"], row["query"]))
        shortlist.append(
            {
                "candidate_id": row["candidate_id"],
                "priority_rank": str(i),
                "topic_zh": topic_zh,
                "topic_en": topic_en,
                "title_en": row["title_en"],
                "title_zh": row["title_zh"],
                "year": row["year"],
                "journal": row["journal"],
                "source": row["source"],
                "pmid": row["pmid"],
                "doi": row["doi"],
                "evidence_level_draft": row["evidence_level_draft"],
                "endpoint_class_draft": row["endpoint_class_draft"],
                "reason_for_shortlist_zh": f"初筛优先：{topic_zh}；草判证据等级 {row['evidence_level_draft']}，终点等级 {row['endpoint_class_draft']}。需人工阅读全文复核。",
                "reason_for_shortlist_en": f"Initial shortlist: {topic_en}; draft evidence level {row['evidence_level_draft']}, endpoint class {row['endpoint_class_draft']}. Full-text review required.",
                "review_status": "shortlist_needs_full_text_review",
            }
        )
    return shortlist


def write_shortlist(shortlist: List[Dict[str, str]]) -> None:
    fields = list(shortlist[0].keys()) if shortlist else []
    with SHORTLIST.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(shortlist)


def write_topic_pages(shortlist: List[Dict[str, str]]) -> None:
    TOPIC_DIR.mkdir(parents=True, exist_ok=True)
    PAPERS.mkdir(parents=True, exist_ok=True)

    grouped: Dict[str, List[Dict[str, str]]] = {}
    for row in shortlist:
        grouped.setdefault(row["topic_en"], []).append(row)

    topic_rows: List[Dict[str, str]] = []
    for topic_en, rows in grouped.items():
        first = rows[0]
        topic_id = slug(topic_en)
        lines = [
            f"# {first['topic_zh']} / {topic_en}",
            "",
            "## 状态 / Status",
            "",
            "Draft topic hub. This page is generated from the first PubMed finding extraction and requires manual full-text review.",
            "",
            "草稿主题页。当前内容来自第一批 PubMed 摘要结果抽取，仍需人工阅读全文复核。",
            "",
            "## 候选短名单 / Candidate Shortlist",
            "",
        ]
        for row in rows[:8]:
            lines.append(f"- {row['title_en']} ({row['year']}). PMID: {row['pmid']}. Draft level: {row['evidence_level_draft']}/{row['endpoint_class_draft']}.")
        lines.append("")
        lines.append("## 发布边界 / Publication Boundary")
        lines.append("")
        lines.append("Do not convert this topic into public advice until at least one reviewer has checked the full texts and completed contribution scoring.")
        lines.append("")
        lines.append("在至少一名复核者阅读全文并完成贡献度评分前，不应把本主题页转成公众建议。")
        (TOPIC_DIR / f"{topic_id}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        topic_rows.append(
            {
                "topic_id": topic_id,
                "title_zh": first["topic_zh"],
                "title_en": topic_en,
                "scope": "Draft scope generated from PubMed shortlist; full-text review required.",
                "evidence_summary_zh": "草稿：已有候选短名单，但尚未完成全文复核和贡献度评分。",
                "evidence_summary_en": "Draft: candidate shortlist exists, but full-text review and contribution scoring are not complete.",
                "status": "draft",
                "paper_count": str(len(rows)),
                "last_checked": str(date.today()),
            }
        )

    with TOPICS.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["topic_id", "title_zh", "title_en", "scope", "evidence_summary_zh", "evidence_summary_en", "status", "paper_count", "last_checked"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(topic_rows)


def write_paper_pages(rows: List[Dict[str, str]], limit: int = 20) -> None:
    PAPERS.mkdir(parents=True, exist_ok=True)
    for row in rows[:limit]:
        topic_id, topic_zh, topic_en = TOPIC_MAP.get(row["query"], (row["query"], row["query"], row["query"]))
        filename = f"{slug(row['candidate_id'])}.md"
        lines = [
            f"# {row['title_en']}",
            "",
            f"- Candidate ID: `{row['candidate_id']}`",
            f"- PMID: `{row['pmid']}`",
            f"- DOI: `{row['doi']}`",
            f"- Year: {row['year']}",
            f"- Journal: {row['journal']}",
            f"- Topic: {topic_zh} / {topic_en}",
            f"- Draft evidence level: {row['evidence_level_draft']}",
            f"- Draft endpoint class: {row['endpoint_class_draft']}",
            "",
            "## Main Finding / 主要发现",
            "",
            f"EN: {row['result_en']}",
            "",
            f"ZH draft: {row['result_zh']}",
            "",
            "## Conclusion Boundary / 结论边界",
            "",
            f"EN: {row['conclusion_en']}",
            "",
            f"ZH draft: {row['conclusion_zh']}",
            "",
            "## Review Status / 复核状态",
            "",
            "Needs manual full-text review and contribution scoring before formal inclusion.",
            "",
            "需要人工阅读全文和贡献度评分后，才能正式纳入证据总表。",
        ]
        (PAPERS / filename).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = read_findings()
    shortlist = build_shortlist(rows)
    if not shortlist:
        print("No findings available.")
        return
    write_shortlist(shortlist)
    write_topic_pages(shortlist)
    write_paper_pages(rows)
    print(f"Wrote {len(shortlist)} shortlist rows, {len(set(r['topic_en'] for r in shortlist))} topic pages, and 20 draft paper pages.")


if __name__ == "__main__":
    main()
