"""Extract first-pass PubMed abstract findings for candidate records.

This creates a review queue, not final evidence claims. Chinese fields are
structured as draft summaries that must be manually checked before publication.
"""

from __future__ import annotations

import csv
import os
import re
import time
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "data" / "candidate_sources.csv"
FINDINGS = ROOT / "data" / "evidence_findings.csv"
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

FINDING_FIELDS = [
    "finding_id",
    "candidate_id",
    "pmid",
    "doi",
    "source",
    "query",
    "title_en",
    "title_zh",
    "journal",
    "year",
    "study_type_draft",
    "species_draft",
    "population_draft",
    "intervention_or_exposure_draft",
    "comparator_draft",
    "endpoint_draft",
    "result_en",
    "result_zh",
    "conclusion_en",
    "conclusion_zh",
    "evidence_level_draft",
    "endpoint_class_draft",
    "translation_status",
    "review_status",
    "last_checked",
]

PRIORITY_QUERIES = [
    "cardiorespiratory_fitness_mortality",
    "resistance_training_mortality_sarcopenia",
    "physical_activity_longevity",
    "blood_pressure_mortality_aging",
    "ldl_apob_cardiovascular_mortality",
    "sleep_duration_mortality_aging",
    "dietary_pattern_longevity",
    "caloric_restriction_human_aging",
    "intermittent_fasting_aging_human",
    "glp1_obesity_cardiometabolic_outcomes",
    "metformin_aging_longevity",
    "rapamycin_mtor_aging",
    "senolytics_human_aging",
    "nad_nmn_nr_human_aging",
    "epigenetic_clocks_intervention",
]

QUERY_ZH = {
    "cardiorespiratory_fitness_mortality": "心肺适能与死亡风险",
    "resistance_training_mortality_sarcopenia": "抗阻训练、肌肉与衰弱/死亡风险",
    "physical_activity_longevity": "身体活动与健康寿命",
    "blood_pressure_mortality_aging": "血压与心血管/死亡风险",
    "ldl_apob_cardiovascular_mortality": "LDL-C/apoB 与心血管风险",
    "sleep_duration_mortality_aging": "睡眠与健康结局",
    "dietary_pattern_longevity": "饮食模式与死亡风险",
    "caloric_restriction_human_aging": "热量限制与人体衰老指标",
    "intermittent_fasting_aging_human": "限时进食/间歇性禁食与代谢健康",
    "glp1_obesity_cardiometabolic_outcomes": "GLP-1/减重与心代谢结局",
    "metformin_aging_longevity": "二甲双胍与衰老/健康寿命",
    "rapamycin_mtor_aging": "雷帕霉素/mTOR 与衰老",
    "senolytics_human_aging": "Senolytics 与细胞衰老",
    "nad_nmn_nr_human_aging": "NAD/NMN/NR 与衰老",
    "epigenetic_clocks_intervention": "表观遗传时钟与干预",
}


def request_xml(endpoint: str, params: Dict[str, str]) -> ET.Element:
    params = dict(params)
    params["retmode"] = "xml"
    email = os.getenv("NCBI_EMAIL")
    api_key = os.getenv("NCBI_API_KEY")
    if email:
        params["email"] = email
    if api_key:
        params["api_key"] = api_key
    url = f"{BASE}/{endpoint}?{urlencode(params)}"
    resp = requests.get(url, timeout=45)
    resp.raise_for_status()
    return ET.fromstring(resp.content)


def text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return " ".join("".join(element.itertext()).split())


def abstract_sections(article: ET.Element) -> Dict[str, str]:
    sections: Dict[str, List[str]] = {}
    for abstract_text in article.findall(".//Abstract/AbstractText"):
        label = abstract_text.attrib.get("Label") or abstract_text.attrib.get("NlmCategory") or "ABSTRACT"
        sections.setdefault(label.upper(), []).append(text(abstract_text))
    return {key: " ".join(value).strip() for key, value in sections.items()}


def publication_types(article: ET.Element) -> List[str]:
    return [text(item) for item in article.findall(".//PublicationTypeList/PublicationType") if text(item)]


def classify_study(pub_types: List[str], abstract: str) -> str:
    joined = " ".join(pub_types).lower() + " " + abstract.lower()
    if "meta-analysis" in joined or "systematic review" in joined:
        return "systematic_review_or_meta_analysis"
    if "randomized" in joined or "randomised" in joined or "clinical trial" in joined:
        return "human_randomized_or_clinical_trial"
    if "cohort" in joined:
        return "human_cohort"
    if "mice" in joined or "mouse" in joined or "murine" in joined:
        return "animal_study"
    return "needs_classification"


def classify_endpoint(query: str, abstract: str) -> str:
    lower = f"{query} {abstract}".lower()
    if any(term in lower for term in ["mortality", "death", "mace", "stroke", "cancer incidence"]):
        return "H1"
    if any(term in lower for term in ["vo2", "frailty", "grip strength", "cognition", "falls", "ahi"]):
        return "H2"
    if any(term in lower for term in ["ldl", "apob", "blood pressure", "hba1c", "waist", "glucose"]):
        return "H3"
    if "clock" in lower or "methylation age" in lower:
        return "H5"
    return "H4"


def evidence_level(study_type: str, endpoint_class: str) -> str:
    if study_type == "systematic_review_or_meta_analysis" and endpoint_class in {"H1", "H2"}:
        return "A"
    if study_type in {"human_randomized_or_clinical_trial", "human_cohort"} and endpoint_class in {"H1", "H2"}:
        return "B"
    if study_type.startswith("human"):
        return "C"
    if study_type == "animal_study":
        return "D"
    return "E"


def concise(value: str, max_chars: int = 900) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 3].rstrip() + "..."


def draft_zh(query: str, conclusion_en: str) -> str:
    topic = QUERY_ZH.get(query, query)
    if not conclusion_en:
        return f"中文初稿：该记录属于「{topic}」主题；摘要中未解析出明确结论，需要人工阅读全文复核。"
    return f"中文初稿：该研究属于「{topic}」主题；英文摘要结论显示：{conclusion_en}"


def load_existing_findings() -> set[str]:
    if not FINDINGS.exists() or FINDINGS.stat().st_size == 0:
        return set()
    with FINDINGS.open("r", encoding="utf-8-sig", newline="") as f:
        return {row.get("candidate_id", "") for row in csv.DictReader(f) if row.get("candidate_id")}


def ensure_header() -> None:
    if not FINDINGS.exists() or FINDINGS.stat().st_size == 0:
        with FINDINGS.open("w", encoding="utf-8", newline="") as f:
            csv.DictWriter(f, fieldnames=FINDING_FIELDS).writeheader()


def selected_candidates(limit: int) -> List[Dict[str, str]]:
    with CANDIDATES.open("r", encoding="utf-8-sig", newline="") as f:
        rows = [row for row in csv.DictReader(f) if row.get("source") == "PubMed" and row.get("pmid")]
    by_query: Dict[str, List[Dict[str, str]]] = {query: [] for query in PRIORITY_QUERIES}
    for row in rows:
        if row.get("query") in by_query:
            by_query[row["query"]].append(row)

    selected: List[Dict[str, str]] = []
    while len(selected) < limit:
        added = False
        for query in PRIORITY_QUERIES:
            if by_query[query]:
                selected.append(by_query[query].pop(0))
                added = True
                if len(selected) >= limit:
                    break
        if not added:
            break
    return selected


def parse_articles(pmids: Iterable[str]) -> Dict[str, ET.Element]:
    root = request_xml("efetch.fcgi", {"db": "pubmed", "id": ",".join(pmids)})
    articles: Dict[str, ET.Element] = {}
    for article in root.findall(".//PubmedArticle"):
        pmid = text(article.find(".//PMID"))
        if pmid:
            articles[pmid] = article
    return articles


def main() -> None:
    load_dotenv(ROOT / ".env")
    ensure_header()
    existing = load_existing_findings()
    candidates = [row for row in selected_candidates(limit=60) if row.get("id") not in existing]
    if not candidates:
        print("No new PubMed findings to enrich.")
        return

    created = 0
    with FINDINGS.open("a", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=FINDING_FIELDS)
        for start in range(0, len(candidates), 20):
            batch = candidates[start : start + 20]
            articles = parse_articles(row["pmid"] for row in batch)
            for row in batch:
                article = articles.get(row["pmid"])
                if article is None:
                    continue
                sections = abstract_sections(article)
                abstract = " ".join(sections.values())
                result_en = sections.get("RESULTS") or sections.get("RESULT") or sections.get("FINDINGS") or ""
                conclusion_en = sections.get("CONCLUSIONS") or sections.get("CONCLUSION") or sections.get("INTERPRETATION") or ""
                if not result_en:
                    result_en = abstract
                pub_types = publication_types(article)
                study_type = classify_study(pub_types, abstract)
                endpoint_class = classify_endpoint(row["query"], abstract)
                level = evidence_level(study_type, endpoint_class)
                journal = text(article.find(".//Journal/Title"))
                writer.writerow(
                    {
                        "finding_id": f"finding-{row['id']}",
                        "candidate_id": row["id"],
                        "pmid": row["pmid"],
                        "doi": row.get("doi", ""),
                        "source": row.get("source", ""),
                        "query": row.get("query", ""),
                        "title_en": row.get("title_en", ""),
                        "title_zh": "",
                        "journal": journal,
                        "year": row.get("year", ""),
                        "study_type_draft": study_type,
                        "species_draft": "human" if study_type.startswith("human") else "needs_review",
                        "population_draft": "",
                        "intervention_or_exposure_draft": QUERY_ZH.get(row.get("query", ""), row.get("query", "")),
                        "comparator_draft": "",
                        "endpoint_draft": endpoint_class,
                        "result_en": concise(result_en),
                        "result_zh": draft_zh(row.get("query", ""), concise(result_en, 500)),
                        "conclusion_en": concise(conclusion_en),
                        "conclusion_zh": draft_zh(row.get("query", ""), concise(conclusion_en, 500)),
                        "evidence_level_draft": level,
                        "endpoint_class_draft": endpoint_class,
                        "translation_status": "zh_draft_needs_review",
                        "review_status": "needs_manual_review",
                        "last_checked": str(date.today()),
                    }
                )
                created += 1
            time.sleep(0.35)
    print(f"Created {created} PubMed finding records.")


if __name__ == "__main__":
    main()
