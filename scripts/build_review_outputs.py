"""Generate v0.3 publication draft outputs from evidence_findings.csv."""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List

ROOT = Path(__file__).resolve().parents[1]
FINDINGS = ROOT / "data" / "evidence_findings.csv"
SHORTLIST = ROOT / "data" / "shortlist_sources.csv"
TOPICS = ROOT / "data" / "topics.csv"
MATRIX = ROOT / "data" / "evidence_matrix.csv"
PAPERS = ROOT / "content" / "papers"
TOPIC_DIR = ROOT / "content" / "topics"
ANALYSIS = ROOT / "content" / "analysis" / "evidence-ranking.md"
RECOMMENDATIONS = ROOT / "content" / "recommendations" / "for-general-readers.md"
STATUS_DOC = ROOT / "docs" / "current-output-status.md"

DRAFT_NOTICE_ZH = "草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。"
DRAFT_NOTICE_EN = "Draft status: automatically prepared; not fully reviewed; not medical advice."

MATRIX_FIELDS = [
    "paper_id", "year", "topic", "intervention_or_exposure", "study_type",
    "species", "sample_size", "primary_endpoint", "endpoint_class", "effect_size",
    "evidence_level", "risk_of_bias", "actionability", "medical_supervision",
    "recommendation_class", "claim_supported", "claim_not_supported",
    "zh_summary", "en_summary", "last_checked",
]


def slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return value[:100] or "item"


def read_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, str]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in rows])


def rank_key(row: Dict[str, str]) -> tuple[int, int, int]:
    level_score = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5}.get(row.get("evidence_level_draft", "E"), 5)
    endpoint_score = {"H1": 0, "H2": 1, "H3": 2, "H5": 3, "H4": 4, "H6": 5}.get(row.get("endpoint_class_draft", "H6"), 6)
    contribution = -int(row.get("contribution_score_draft") or 0)
    return level_score, endpoint_score, contribution


def grouped_by_topic(rows: Iterable[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    grouped: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row.get("topic_id", "unknown")].append(row)
    return grouped


def build_shortlist(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    out = []
    for i, row in enumerate(sorted(rows, key=rank_key), start=1):
        out.append({
            "candidate_id": row["candidate_id"],
            "priority_rank": str(i),
            "topic_id": row["topic_id"],
            "topic_zh": row["topic_zh"],
            "topic_en": row["topic_en"],
            "title_en": row["title_en"],
            "title_zh": row["title_zh"],
            "year": row["year"],
            "journal": row["journal"],
            "source": row["source"],
            "pmid": row["pmid"],
            "pmcid": row.get("pmcid", ""),
            "doi": row["doi"],
            "evidence_level_draft": row["evidence_level_draft"],
            "endpoint_class_draft": row["endpoint_class_draft"],
            "contribution_score_draft": row["contribution_score_draft"],
            "evidence_source_depth": row["evidence_source_depth"],
            "reason_for_shortlist_zh": f"v0.3 短名单：{row['topic_zh']}；草判证据等级 {row['evidence_level_draft']}，终点等级 {row['endpoint_class_draft']}，代理可信度 {row['contribution_score_draft']}。公开前仍需人工复核。",
            "reason_for_shortlist_en": f"v0.3 shortlist: {row['topic_en']}; draft evidence level {row['evidence_level_draft']}, endpoint class {row['endpoint_class_draft']}, proxy credibility {row['contribution_score_draft']}. Human review still required.",
            "review_status": row["review_status"],
        })
    return out


def matrix_rows(rows: List[Dict[str, str]], limit: int) -> List[Dict[str, str]]:
    out = []
    for row in sorted(rows, key=rank_key)[:limit]:
        out.append({
            "paper_id": row["candidate_id"],
            "year": row["year"],
            "topic": row["topic_zh"],
            "intervention_or_exposure": row["intervention_or_exposure_draft"],
            "study_type": row["study_type_draft"],
            "species": row["species_draft"],
            "sample_size": row["sample_size_draft"],
            "primary_endpoint": row["endpoint_draft"],
            "endpoint_class": row["endpoint_class_draft"],
            "effect_size": "摘要级/题录级待复核",
            "evidence_level": row["evidence_level_draft"],
            "risk_of_bias": "not_checked_public_draft",
            "actionability": "high" if row["recommendation_class_draft"] == "Strong Action" else "medium" if row["recommendation_class_draft"] == "Medical Action" else "low",
            "medical_supervision": row["medical_supervision_draft"],
            "recommendation_class": row["recommendation_class_draft"],
            "claim_supported": row["claim_supported_zh"],
            "claim_not_supported": row["claim_not_supported_zh"],
            "zh_summary": f"{DRAFT_NOTICE_ZH} {row['conclusion_zh']}",
            "en_summary": f"{DRAFT_NOTICE_EN} {row['conclusion_en']}",
            "last_checked": str(date.today()),
        })
    return out


def clean_generated_pages() -> None:
    for path in PAPERS.glob("pubmed-*.md"):
        path.unlink()
    for path in PAPERS.glob("crossref-*.md"):
        path.unlink()
    for path in PAPERS.glob("clinicaltrials-*.md"):
        path.unlink()
    for path in TOPIC_DIR.glob("*.md"):
        if path.name != "_template.md":
            path.unlink()


def write_paper_pages(rows: List[Dict[str, str]]) -> None:
    PAPERS.mkdir(parents=True, exist_ok=True)
    for row in sorted(rows, key=rank_key):
        lines = [
            f"# {row['title_en']}",
            "",
            f"> {DRAFT_NOTICE_ZH}",
            f"> {DRAFT_NOTICE_EN}",
            "",
            "## Metadata / 元数据",
            "",
            f"- Candidate ID: `{row['candidate_id']}`",
            f"- Source: `{row['source']}`",
            f"- PMID: `{row['pmid']}`",
            f"- PMCID: `{row.get('pmcid','')}`",
            f"- DOI: `{row['doi']}`",
            f"- Year: {row['year']}",
            f"- Journal/Registry: {row['journal']}",
            f"- Topic: {row['topic_zh']} / {row['topic_en']}",
            f"- Evidence source depth: `{row['evidence_source_depth']}`",
            "",
            "## Study Design / 研究设计",
            "",
            f"- Draft study type: `{row['study_type_draft']}`",
            f"- Draft species/population: `{row['species_draft']}` / {row['population_draft']}",
            f"- Draft intervention or exposure: {row['intervention_or_exposure_draft']}",
            f"- Draft comparator: {row['comparator_draft']}",
            f"- Draft primary endpoint: {row['endpoint_draft']}",
            f"- Draft sample size: {row['sample_size_draft']}",
            "",
            "## Main Results / 主要结果",
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
            "## Supported Claim / 支持的结论",
            "",
            f"- ZH: {row['claim_supported_zh']}",
            f"- EN: {row['claim_supported_en']}",
            "",
            "## Unsupported Claim / 不支持的结论",
            "",
            f"- ZH: {row['claim_not_supported_zh']}",
            f"- EN: {row['claim_not_supported_en']}",
            "",
            "## Overinterpretation Risk / 过度解读风险",
            "",
            f"- ZH: {row['overinterpretation_risk_zh']}",
            f"- EN: {row['overinterpretation_risk_en']}",
            "",
            "## Draft Grading / 草判分级",
            "",
            f"- Evidence level: `{row['evidence_level_draft']}`",
            f"- Endpoint class: `{row['endpoint_class_draft']}`",
            f"- Proxy credibility score: `{row['contribution_score_draft']}`",
            f"- Recommendation class: `{row['recommendation_class_draft']}`",
            f"- Medical supervision needed: `{row['medical_supervision_draft']}`",
            f"- Authority signal: {row['authority_signal_draft']}",
            "",
            "## Review Status / 复核状态",
            "",
            "Public draft. Needs human full-text review before formal recommendation or clinical interpretation.",
            "",
            "公开草稿。形成正式推荐或临床解释前，必须人工阅读全文复核。",
        ]
        (PAPERS / f"{slug(row['candidate_id'])}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def topic_summary_zh(rows: List[Dict[str, str]]) -> str:
    best = sorted(rows, key=rank_key)[0]
    return f"草稿总结：本主题已有 {len(rows)} 条 v0.3 记录，当前最高草判证据等级为 {best['evidence_level_draft']}，仍需全文复核后才能形成正式建议。"


def topic_summary_en(rows: List[Dict[str, str]]) -> str:
    best = sorted(rows, key=rank_key)[0]
    return f"Draft summary: this topic has {len(rows)} v0.3 records; the highest draft evidence level is {best['evidence_level_draft']}. Full-text review is required before formal advice."


def write_topic_pages(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    TOPIC_DIR.mkdir(parents=True, exist_ok=True)
    topic_meta = []
    for topic_id, topic_rows in sorted(grouped_by_topic(rows).items()):
        sorted_rows = sorted(topic_rows, key=rank_key)
        first = sorted_rows[0]
        lines = [
            f"# {first['topic_zh']} / {first['topic_en']}",
            "",
            f"> {DRAFT_NOTICE_ZH}",
            f"> {DRAFT_NOTICE_EN}",
            "",
            "## 一句话结论 / One-Sentence Conclusion",
            "",
            topic_summary_zh(sorted_rows),
            "",
            topic_summary_en(sorted_rows),
            "",
            "## 当前证据等级 / Current Evidence Level",
            "",
            f"- Highest draft evidence level: `{first['evidence_level_draft']}`",
            f"- Highest draft endpoint class: `{first['endpoint_class_draft']}`",
            "- Status: public draft, not fully reviewed",
            "",
            "## 我们知道什么 / What We Know",
            "",
        ]
        for row in sorted_rows[:12]:
            lines.append(f"- {row['claim_supported_zh']} / {row['claim_supported_en']}")
        lines.extend([
            "",
            "## 仍不确定什么 / What Remains Uncertain",
            "",
            "- 自动抽取结果仍需阅读全文确认研究设计、样本量、终点定义、效应量和偏倚风险。",
            "- Metadata-only records are useful for tracking, but cannot support effect claims.",
            "- Automated extraction still needs full-text confirmation of design, sample size, endpoint definition, effect size, and bias risk.",
            "",
            "## 不能这么说 / What Not To Claim",
            "",
        ])
        for row in sorted_rows[:12]:
            lines.append(f"- {row['claim_not_supported_zh']} / {row['claim_not_supported_en']}")
        lines.extend(["", "## 相关论文卡片 / Related Paper Cards", ""])
        for row in sorted_rows:
            lines.append(f"- [{row['title_en']}](../papers/{slug(row['candidate_id'])}.md) ({row['year']}, {row['source']})")
        lines.extend([
            "",
            "## 发布边界 / Publication Boundary",
            "",
            "本页可以作为公开草稿展示，但不能作为医疗建议、补剂/药物建议或个体化风险管理建议。",
            "",
            "This page may be shown as a public draft, but it is not medical advice, supplement/drug advice, or personalized risk management guidance.",
        ])
        (TOPIC_DIR / f"{topic_id}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        topic_meta.append({
            "topic_id": topic_id,
            "title_zh": first["topic_zh"],
            "title_en": first["topic_en"],
            "scope": "Public draft topic generated from v0.3 600-record shortlist; full-text review required.",
            "evidence_summary_zh": topic_summary_zh(sorted_rows),
            "evidence_summary_en": topic_summary_en(sorted_rows),
            "status": "public_draft_not_fully_reviewed",
            "paper_count": str(len(sorted_rows)),
            "last_checked": str(date.today()),
        })
    return topic_meta


def write_analysis(matrix: List[Dict[str, str]]) -> None:
    rows = sorted(matrix, key=lambda row: ({"A": 0, "B": 1, "C": 2, "D": 3, "E": 4}.get(row["evidence_level"], 9), row["topic"]))
    lines = [
        "# 长寿抗衰证据排行 / Longevity Evidence Ranking",
        "",
        f"> {DRAFT_NOTICE_ZH}",
        f"> {DRAFT_NOTICE_EN}",
        "",
        "| Rank | Topic | Evidence | Endpoint | Recommendation | Medical supervision | Summary |",
        "|---:|---|---|---|---|---|---|",
    ]
    for i, row in enumerate(rows[:120], start=1):
        lines.append(f"| {i} | {row['topic']} | {row['evidence_level']} | {row['endpoint_class']} | {row['recommendation_class']} | {row['medical_supervision']} | {row['zh_summary']} |")
    lines.extend([
        "",
        "## 解释边界 / Interpretation Boundary",
        "",
        "- Strong Action: lifestyle or prevention topics with human evidence, still not individualized medical advice.",
        "- Medical Action: requires clinician evaluation or monitoring.",
        "- Monitor: frontier or lower-certainty evidence; not a public recommendation.",
        "- 所有条目仍处于公开草稿阶段，正式建议需要人工全文复核。",
    ])
    ANALYSIS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_recommendations(matrix: List[Dict[str, str]]) -> None:
    strong = [row for row in matrix if row["recommendation_class"] == "Strong Action"]
    medical = [row for row in matrix if row["recommendation_class"] == "Medical Action"]
    monitor = [row for row in matrix if row["recommendation_class"] == "Monitor"]
    lines = [
        "# 普通读者建议边界 / Boundaries for General Readers",
        "",
        f"> {DRAFT_NOTICE_ZH}",
        f"> {DRAFT_NOTICE_EN}",
        "",
        "本页不是医疗建议，不提供药物、补剂、剂量或治疗方案。它只说明哪些主题在证据图谱中更值得优先复核。",
        "",
        "This page is not medical advice and does not provide drugs, supplements, dosages, or treatment plans.",
        "",
        "## 可作为健康行为优先复核的方向 / Higher-Priority Health Behavior Topics",
        "",
    ]
    for row in strong[:20]:
        lines.append(f"- {row['topic']}: {row['claim_supported']}")
    lines.extend(["", "## 需要医生评估或监测 / Requires Clinician Evaluation", ""])
    for row in medical[:20]:
        lines.append(f"- {row['topic']}: {row['claim_supported']}")
    lines.extend(["", "## 只观察，不建议自行实践 / Monitor Only", ""])
    for row in monitor[:30]:
        lines.append(f"- {row['topic']}: {row['claim_supported']}")
    lines.extend([
        "",
        "## 禁止性边界 / Do Not Overclaim",
        "",
        "- 不把动物寿命实验写成人类延寿已证实。",
        "- 不把 biomarker 改善写成临床逆龄。",
        "- 不从单篇摘要或题录推出剂量、处方或治疗建议。",
        "- Do not present animal lifespan studies as proven human lifespan extension.",
        "- Do not present biomarker changes as clinical rejuvenation.",
        "- Do not infer dosage, prescription, or treatment advice from one abstract or metadata record.",
    ])
    RECOMMENDATIONS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_status(findings: List[Dict[str, str]], matrix: List[Dict[str, str]], topics: List[Dict[str, str]]) -> None:
    lines = [
        "# Current Output Status / 当前输出状态",
        "",
        f"Date / 日期: {date.today()}",
        "",
        "## Production Draft Assets / 可发布草稿资产",
        "",
        "- Candidate pool: 938 unique records.",
        f"- Finding extraction layer: {len(findings)} v0.3 finding records.",
        f"- Shortlist: {len(findings)} records for v0.3 public draft.",
        f"- Topic drafts: {len(topics)} public draft topic pages.",
        f"- Paper-card drafts: {len(findings)} public draft paper pages.",
        f"- Evidence matrix: {len(matrix)} cautious draft inclusion records.",
        "",
        "## Public Caveat / 公开警示",
        "",
        f"- {DRAFT_NOTICE_ZH}",
        f"- {DRAFT_NOTICE_EN}",
        "",
        "## Feishu Sync Targets / 飞书同步目标",
        "",
        f"- 候选文献: 938 unique candidates; {len(findings)} finding records include result/conclusion fields.",
        f"- 主题库: {len(topics)} public draft topic records.",
        f"- 文献总表: {len(matrix)} cautious draft inclusion records.",
        "- 发布日志: record GitHub commit and Feishu sync status.",
    ]
    STATUS_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix-limit", type=int, default=300)
    args = parser.parse_args()
    rows = read_rows(FINDINGS)
    if len(rows) < 600:
        raise SystemExit(f"Expected at least 600 finding rows, found {len(rows)}.")
    rows = rows[:600]
    clean_generated_pages()
    shortlist = build_shortlist(rows)
    write_csv(SHORTLIST, shortlist, list(shortlist[0].keys()))
    topics = write_topic_pages(rows)
    write_csv(TOPICS, topics, ["topic_id", "title_zh", "title_en", "scope", "evidence_summary_zh", "evidence_summary_en", "status", "paper_count", "last_checked"])
    write_paper_pages(rows)
    matrix = matrix_rows(rows, args.matrix_limit)
    write_csv(MATRIX, matrix, MATRIX_FIELDS)
    write_analysis(matrix)
    write_recommendations(matrix)
    write_status(rows, matrix, topics)
    print(f"Wrote {len(shortlist)} shortlist rows, {len(topics)} topic pages, {len(rows)} paper pages, and {len(matrix)} evidence matrix rows.")


if __name__ == "__main__":
    main()
