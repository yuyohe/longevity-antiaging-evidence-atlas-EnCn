"""Build the v0.1 PubMed finding layer for publication drafts.

The output is intentionally conservative:
- it uses PubMed metadata/abstracts first;
- it records whether an open PMCID is available;
- all Chinese fields are draft interpretations that require review.
"""

from __future__ import annotations

import argparse
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

PUBLIC_DRAFT_NOTICE_ZH = "草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。"
PUBLIC_DRAFT_NOTICE_EN = "Draft status: automatically prepared; not fully reviewed; not medical advice."

TOPICS = [
    ("cardiorespiratory_fitness_mortality", "cardiorespiratory-fitness", "心肺适能与死亡风险", "Cardiorespiratory Fitness and Mortality", "fitness / VO2max"),
    ("resistance_training_mortality_sarcopenia", "resistance-training-muscle", "抗阻训练、肌肉与衰弱", "Resistance Training, Muscle, and Frailty", "resistance training / muscle"),
    ("physical_activity_longevity", "physical-activity-healthspan", "身体活动与健康寿命", "Physical Activity and Healthspan", "physical activity"),
    ("blood_pressure_mortality_aging", "blood-pressure-aging", "血压与健康寿命", "Blood Pressure and Healthspan", "blood pressure"),
    ("ldl_apob_cardiovascular_mortality", "ldl-apob-cardiovascular-risk", "LDL-C/apoB 与心血管风险", "LDL-C/apoB and Cardiovascular Risk", "LDL-C / apoB"),
    ("sleep_duration_mortality_aging", "sleep-aging", "睡眠与健康结局", "Sleep and Aging Outcomes", "sleep"),
    ("dietary_pattern_longevity", "dietary-pattern-longevity", "饮食模式与死亡风险", "Dietary Patterns and Longevity", "dietary pattern"),
    ("caloric_restriction_human_aging", "caloric-restriction-human", "热量限制与人体衰老", "Caloric Restriction in Humans", "caloric restriction"),
    ("intermittent_fasting_aging_human", "time-restricted-eating", "限时进食与代谢健康", "Time-Restricted Eating and Metabolic Health", "time-restricted eating / intermittent fasting"),
    ("glp1_obesity_cardiometabolic_outcomes", "glp1-weight-cardiometabolic", "GLP-1、减重与心代谢结局", "GLP-1, Weight Loss, and Cardiometabolic Outcomes", "GLP-1 / weight loss"),
    ("metformin_aging_longevity", "metformin-aging", "二甲双胍与衰老", "Metformin and Aging", "metformin"),
    ("rapamycin_mtor_aging", "rapamycin-mtor-aging", "雷帕霉素/mTOR 与衰老", "Rapamycin/mTOR and Aging", "rapamycin / mTOR"),
    ("senolytics_human_aging", "senolytics", "Senolytics 与细胞衰老", "Senolytics and Cellular Senescence", "senolytics"),
    ("nad_nmn_nr_human_aging", "nad-nmn-nr-aging", "NAD/NMN/NR 与衰老", "NAD/NMN/NR and Aging", "NAD / NMN / NR"),
    ("epigenetic_clocks_intervention", "epigenetic-clocks", "表观遗传时钟与干预", "Epigenetic Clocks and Interventions", "epigenetic clock"),
    ("itp_mouse_lifespan_interventions", "itp-mouse-lifespan", "ITP 小鼠寿命干预", "ITP Mouse Lifespan Interventions", "mouse lifespan intervention"),
    ("klotho_aging_human", "klotho-il11-aging", "Klotho / IL-11 与衰老", "Klotho / IL-11 and Aging", "Klotho / IL-11"),
    ("partial_reprogramming_aging", "partial-reprogramming", "部分重编程", "Partial Reprogramming", "partial reprogramming"),
    ("autophagy_mitophagy_longevity", "autophagy-mitophagy", "自噬/线粒体自噬", "Autophagy and Mitophagy", "autophagy / mitophagy"),
    ("microbiome_healthy_aging", "microbiome-inflammaging", "微生物组与炎症性衰老", "Microbiome and Inflammaging", "microbiome / inflammaging"),
]

TOPIC_BY_QUERY = {item[0]: item for item in TOPICS}

FINDING_FIELDS = [
    "finding_id",
    "candidate_id",
    "pmid",
    "pmcid",
    "doi",
    "source",
    "query",
    "topic_id",
    "topic_zh",
    "topic_en",
    "title_en",
    "title_zh",
    "journal",
    "year",
    "publication_types",
    "study_type_draft",
    "species_draft",
    "population_draft",
    "intervention_or_exposure_draft",
    "comparator_draft",
    "endpoint_draft",
    "sample_size_draft",
    "result_en",
    "result_zh",
    "conclusion_en",
    "conclusion_zh",
    "claim_supported_zh",
    "claim_supported_en",
    "claim_not_supported_zh",
    "claim_not_supported_en",
    "overinterpretation_risk_zh",
    "overinterpretation_risk_en",
    "evidence_level_draft",
    "endpoint_class_draft",
    "authority_signal_draft",
    "contribution_score_draft",
    "recommendation_class_draft",
    "medical_supervision_draft",
    "evidence_source_depth",
    "draft_notice_zh",
    "draft_notice_en",
    "translation_status",
    "review_status",
    "last_checked",
]


def request_xml(endpoint: str, params: Dict[str, str]) -> ET.Element:
    params = dict(params)
    params["retmode"] = "xml"
    if os.getenv("NCBI_EMAIL"):
        params["email"] = os.getenv("NCBI_EMAIL")
    if os.getenv("NCBI_API_KEY"):
        params["api_key"] = os.getenv("NCBI_API_KEY")
    resp = requests.get(f"{BASE}/{endpoint}?{urlencode(params)}", timeout=45)
    resp.raise_for_status()
    return ET.fromstring(resp.content)


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return clean("".join(element.itertext()))


def concise(value: str, max_chars: int = 900) -> str:
    value = clean(value)
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 3].rstrip() + "..."


def abstract_sections(article: ET.Element) -> Dict[str, str]:
    sections: Dict[str, List[str]] = {}
    for abstract_text in article.findall(".//Abstract/AbstractText"):
        label = abstract_text.attrib.get("Label") or abstract_text.attrib.get("NlmCategory") or "ABSTRACT"
        sections.setdefault(label.upper(), []).append(text(abstract_text))
    return {key: clean(" ".join(value)) for key, value in sections.items()}


def article_ids(article: ET.Element) -> Dict[str, str]:
    ids: Dict[str, str] = {}
    for item in article.findall(".//ArticleIdList/ArticleId"):
        id_type = item.attrib.get("IdType", "").lower()
        if id_type:
            ids[id_type] = text(item)
    return ids


def publication_types(article: ET.Element) -> List[str]:
    return [text(item) for item in article.findall(".//PublicationTypeList/PublicationType") if text(item)]


def classify_study(pub_types: List[str], abstract: str) -> str:
    joined = f"{' '.join(pub_types)} {abstract}".lower()
    if "meta-analysis" in joined or "systematic review" in joined:
        return "systematic_review_or_meta_analysis"
    if "randomized" in joined or "randomised" in joined or "clinical trial" in joined:
        return "human_randomized_or_clinical_trial"
    if "cohort" in joined:
        return "human_cohort"
    if any(term in joined for term in ["mice", "mouse", "murine", "rats", "rodent"]):
        return "animal_study"
    if any(term in joined for term in ["cell", "in vitro", "organoid"]):
        return "mechanistic_or_cell_study"
    return "needs_classification"


def classify_species(study_type: str, abstract: str) -> str:
    lower = abstract.lower()
    if study_type.startswith("human") or any(term in lower for term in ["participants", "patients", "adults", "women", "men"]):
        return "human"
    if any(term in lower for term in ["mice", "mouse", "murine"]):
        return "mouse"
    if any(term in lower for term in ["rats", "rodent"]):
        return "animal"
    if "cell" in lower or "in vitro" in lower:
        return "cell"
    return "needs_review"


def classify_endpoint(query: str, abstract: str) -> str:
    lower = f"{query} {abstract}".lower()
    if any(term in lower for term in ["mortality", "death", "mace", "stroke", "cardiovascular event", "cancer incidence"]):
        return "H1"
    if any(term in lower for term in ["vo2", "frailty", "grip strength", "cognition", "falls", "ahi", "sarcopenia"]):
        return "H2"
    if any(term in lower for term in ["ldl", "apob", "blood pressure", "hba1c", "waist", "glucose", "body weight"]):
        return "H3"
    if "clock" in lower or "methylation age" in lower or "biological age" in lower:
        return "H5"
    if any(term in lower for term in ["lifespan", "survival"]) and any(term in lower for term in ["mouse", "mice"]):
        return "H6"
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


def recommendation(study_type: str, topic_id: str, level: str) -> str:
    if topic_id in {"metformin-aging", "rapamycin-mtor-aging", "senolytics", "nad-nmn-nr-aging", "glp1-weight-cardiometabolic"}:
        return "Medical Action" if topic_id == "glp1-weight-cardiometabolic" else "Monitor"
    if level in {"A", "B"} and study_type.startswith("human"):
        return "Strong Action"
    return "Monitor"


def authority_signal(pub_types: List[str], ids: Dict[str, str], journal: str, evidence_source_depth: str) -> str:
    signals = []
    if "doi" in ids:
        signals.append("DOI")
    if "pmcid" in ids:
        signals.append("PMCID/open-access signal")
    if any("Meta-Analysis" in pt or "Systematic Review" in pt for pt in pub_types):
        signals.append("review-level publication type")
    if any("Clinical Trial" in pt or "Randomized" in pt for pt in pub_types):
        signals.append("trial publication type")
    if journal:
        signals.append("peer-reviewed journal metadata")
    if evidence_source_depth != "abstract_only":
        signals.append(evidence_source_depth)
    return "; ".join(signals) or "metadata_only"


def score(level: str, endpoint: str, species: str, authority: str) -> int:
    level_points = {"A": 35, "B": 30, "C": 22, "D": 14, "E": 8, "F": 0}.get(level, 8)
    endpoint_points = {"H1": 20, "H2": 16, "H3": 12, "H4": 8, "H5": 8, "H6": 5}.get(endpoint, 5)
    human_points = 15 if species == "human" else 5 if species in {"mouse", "animal"} else 3
    authority_points = min(10, 2 * len([part for part in authority.split(";") if part.strip()]))
    return min(100, level_points + endpoint_points + human_points + authority_points + 10)


def draft_zh_result(topic_zh: str, value_en: str) -> str:
    if not value_en:
        return f"中文草稿：该记录属于「{topic_zh}」主题；摘要中未解析出明确结果，需人工复核。"
    return f"中文草稿：该研究属于「{topic_zh}」主题；摘要结果显示：{value_en}"


def draft_zh_conclusion(topic_zh: str, value_en: str) -> str:
    if not value_en:
        return f"中文草稿：摘要未给出明确结论，不能据此形成正式建议。"
    return f"中文草稿：英文摘要结论为：{value_en}"


def conclusion_fallback(topic_en: str) -> str:
    return f"No separate conclusion section was parsed from the abstract for {topic_en}; full-text or manual abstract review is required before publication claims."


def support_claim(topic_zh: str, topic_en: str, level: str) -> tuple[str, str]:
    return (
        f"可支持：将「{topic_zh}」作为证据图谱中的候选主题，并按 {level} 级草判证据继续复核。",
        f"Supports treating {topic_en} as a candidate evidence topic with draft level {level}, pending full review.",
    )


def unsupported_claim(species: str, endpoint_class: str) -> tuple[str, str]:
    if species != "human":
        return ("不支持：不能把非人体结果直接解释为已证实的人类延寿作用。", "Does not support direct claims of proven human lifespan extension.")
    if endpoint_class not in {"H1", "H2"}:
        return ("不支持：不能把替代指标或 biomarker 改善直接解释为临床逆龄。", "Does not support interpreting surrogate or biomarker change as clinical rejuvenation.")
    return ("不支持：不能据单篇摘要给出剂量、处方或个人医疗建议。", "Does not support dosing, prescriptions, or individual medical advice from one abstract.")


def parse_articles(pmids: Iterable[str]) -> Dict[str, ET.Element]:
    root = request_xml("efetch.fcgi", {"db": "pubmed", "id": ",".join(pmids)})
    articles: Dict[str, ET.Element] = {}
    for article in root.findall(".//PubmedArticle"):
        pmid = text(article.find(".//PMID"))
        if pmid:
            articles[pmid] = article
    return articles


def selected_candidates(per_topic: int) -> List[Dict[str, str]]:
    with CANDIDATES.open("r", encoding="utf-8-sig", newline="") as f:
        rows = [row for row in csv.DictReader(f) if row.get("source") == "PubMed" and row.get("pmid")]
    selected: List[Dict[str, str]] = []
    for query, *_ in TOPICS:
        topic_rows = [row for row in rows if row.get("query") == query]
        selected.extend(topic_rows[:per_topic])
    return selected


def ensure_parent() -> None:
    FINDINGS.parent.mkdir(parents=True, exist_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-topic", type=int, default=3)
    parser.add_argument("--force", action="store_true", help="Rebuild evidence_findings.csv from scratch.")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    ensure_parent()
    candidates = selected_candidates(args.per_topic)
    if args.force or not FINDINGS.exists():
        existing: set[str] = set()
        mode = "w"
    else:
        with FINDINGS.open("r", encoding="utf-8-sig", newline="") as f:
            existing = {row.get("candidate_id", "") for row in csv.DictReader(f) if row.get("candidate_id")}
        mode = "a"
    candidates = [row for row in candidates if row.get("id") not in existing]

    with FINDINGS.open(mode, encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=FINDING_FIELDS)
        if mode == "w":
            writer.writeheader()
        created = 0
        for start in range(0, len(candidates), 20):
            batch = candidates[start : start + 20]
            articles = parse_articles(row["pmid"] for row in batch)
            for row in batch:
                article = articles.get(row["pmid"])
                if article is None:
                    continue
                ids = article_ids(article)
                sections = abstract_sections(article)
                abstract = clean(" ".join(sections.values()))
                result_en = sections.get("RESULTS") or sections.get("RESULT") or sections.get("FINDINGS") or abstract
                conclusion_en = sections.get("CONCLUSIONS") or sections.get("CONCLUSION") or sections.get("INTERPRETATION") or ""
                pub_types = publication_types(article)
                study_type = classify_study(pub_types, abstract)
                species = classify_species(study_type, abstract)
                endpoint_class = classify_endpoint(row["query"], abstract)
                level = evidence_level(study_type, endpoint_class)
                topic_id, topic_zh, topic_en, exposure = TOPIC_BY_QUERY[row["query"]][1:]
                if not conclusion_en:
                    conclusion_en = conclusion_fallback(topic_en)
                pmcid = ids.get("pmc", row.get("pmcid", ""))
                evidence_source_depth = "abstract_plus_open_pmc_available" if pmcid else "abstract_only"
                journal = text(article.find(".//Journal/Title"))
                authority = authority_signal(pub_types, ids, journal, evidence_source_depth)
                contribution = score(level, endpoint_class, species, authority)
                rec = recommendation(study_type, topic_id, level)
                supported_zh, supported_en = support_claim(topic_zh, topic_en, level)
                not_zh, not_en = unsupported_claim(species, endpoint_class)
                writer.writerow(
                    {
                        "finding_id": f"finding-{row['id']}",
                        "candidate_id": row["id"],
                        "pmid": row["pmid"],
                        "pmcid": pmcid,
                        "doi": ids.get("doi", row.get("doi", "")),
                        "source": row.get("source", ""),
                        "query": row.get("query", ""),
                        "topic_id": topic_id,
                        "topic_zh": topic_zh,
                        "topic_en": topic_en,
                        "title_en": row.get("title_en", ""),
                        "title_zh": "",
                        "journal": journal,
                        "year": row.get("year", ""),
                        "publication_types": "; ".join(pub_types),
                        "study_type_draft": study_type,
                        "species_draft": species,
                        "population_draft": "摘要级待复核 / abstract-level pending review",
                        "intervention_or_exposure_draft": exposure,
                        "comparator_draft": "摘要级待复核 / abstract-level pending review",
                        "endpoint_draft": endpoint_class,
                        "sample_size_draft": "摘要级待复核 / abstract-level pending review",
                        "result_en": concise(result_en),
                        "result_zh": draft_zh_result(topic_zh, concise(result_en, 500)),
                        "conclusion_en": concise(conclusion_en),
                        "conclusion_zh": draft_zh_conclusion(topic_zh, concise(conclusion_en, 500)),
                        "claim_supported_zh": supported_zh,
                        "claim_supported_en": supported_en,
                        "claim_not_supported_zh": not_zh,
                        "claim_not_supported_en": not_en,
                        "overinterpretation_risk_zh": "过度解读风险：自动抽取结果不能替代全文复核，不能直接转化为个人医疗建议。",
                        "overinterpretation_risk_en": "Overinterpretation risk: automated extraction does not replace full-text review and cannot be converted into personal medical advice.",
                        "evidence_level_draft": level,
                        "endpoint_class_draft": endpoint_class,
                        "authority_signal_draft": authority,
                        "contribution_score_draft": str(contribution),
                        "recommendation_class_draft": rec,
                        "medical_supervision_draft": "true" if rec == "Medical Action" or topic_id in {"metformin-aging", "rapamycin-mtor-aging", "senolytics"} else "false",
                        "evidence_source_depth": evidence_source_depth,
                        "draft_notice_zh": PUBLIC_DRAFT_NOTICE_ZH,
                        "draft_notice_en": PUBLIC_DRAFT_NOTICE_EN,
                        "translation_status": "zh_draft_needs_review",
                        "review_status": "public_draft_not_fully_reviewed",
                        "last_checked": str(date.today()),
                    }
                )
                created += 1
            time.sleep(0.35)
    print(f"Created {created} PubMed finding records. total_target={len(TOPICS) * args.per_topic}")


if __name__ == "__main__":
    main()
