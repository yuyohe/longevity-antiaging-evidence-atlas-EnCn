"""Build v0.3 finding records from the candidate pool.

v0.3 expands the public-draft evidence layer from 60 to 600 records.
PubMed records are enriched with E-utilities abstracts when possible.
Crossref and ClinicalTrials.gov records are kept as metadata-level findings.
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
    ("cardiorespiratory-fitness", "心肺适能与死亡风险", "Cardiorespiratory Fitness and Mortality", "fitness / VO2max", ["cardiorespiratory_fitness_mortality", "exercise_cardiorespiratory_fitness_longevity"]),
    ("resistance-training-muscle", "抗阻训练、肌肉与衰弱", "Resistance Training, Muscle, and Frailty", "resistance training / muscle", ["resistance_training_mortality_sarcopenia", "resistance_training_sarcopenia_frailty", "exercise_older_adults_frailty"]),
    ("physical-activity-healthspan", "身体活动与健康寿命", "Physical Activity and Healthspan", "physical activity", ["physical_activity_longevity", "frailty_interventions_older_adults", "frailty_multidomain", "frailty_multidomain_interventions"]),
    ("blood-pressure-aging", "血压与健康寿命", "Blood Pressure and Healthspan", "blood pressure", ["blood_pressure_mortality_aging", "mendelian_randomization_longevity_risk_factors"]),
    ("ldl-apob-cardiovascular-risk", "LDL-C/apoB 与心血管风险", "LDL-C/apoB and Cardiovascular Risk", "LDL-C / apoB", ["ldl_apob_cardiovascular_mortality", "mendelian_randomization_longevity_risk_factors"]),
    ("sleep-aging", "睡眠与健康结局", "Sleep and Aging Outcomes", "sleep", ["sleep_duration_mortality_aging"]),
    ("dietary-pattern-longevity", "饮食模式与死亡风险", "Dietary Patterns and Longevity", "dietary pattern", ["dietary_pattern_longevity", "nutrition_dietary_restriction_aging", "human_longevity_interventions_reviews"]),
    ("caloric-restriction-human", "热量限制与人体衰老", "Caloric Restriction in Humans", "caloric restriction", ["caloric_restriction_human_aging", "caloric_restriction_aging"]),
    ("time-restricted-eating", "限时进食与代谢健康", "Time-Restricted Eating and Metabolic Health", "time-restricted eating / intermittent fasting", ["intermittent_fasting_aging_human", "time_restricted_eating_aging"]),
    ("glp1-weight-cardiometabolic", "GLP-1、减重与心代谢结局", "GLP-1, Weight Loss, and Cardiometabolic Outcomes", "GLP-1 / weight loss", ["glp1_obesity_cardiometabolic_outcomes", "diabetes_obesity_longevity_outcomes", "obesity_weight_loss_mortality_aging"]),
    ("metformin-aging", "二甲双胍与衰老", "Metformin and Aging", "metformin", ["metformin_aging_longevity", "metformin_aging", "geroprotectors_mtor_metformin_senolytics"]),
    ("rapamycin-mtor-aging", "雷帕霉素/mTOR 与衰老", "Rapamycin/mTOR and Aging", "rapamycin / mTOR", ["rapamycin_mtor_aging", "rapamycin_aging", "geroprotectors_mtor_metformin_senolytics"]),
    ("senolytics", "Senolytics 与细胞衰老", "Senolytics and Cellular Senescence", "senolytics", ["senolytics_human_aging", "senolytics_aging", "geroprotectors_mtor_metformin_senolytics"]),
    ("nad-nmn-nr-aging", "NAD/NMN/NR 与衰老", "NAD/NMN/NR and Aging", "NAD / NMN / NR", ["nad_nmn_nr_human_aging", "nad_precursors_aging_trials", "nad_nmn_nr_aging"]),
    ("epigenetic-clocks", "表观遗传时钟与干预", "Epigenetic Clocks and Interventions", "epigenetic clock", ["epigenetic_clocks_intervention", "aging_clocks_disease_prediction", "clinical_aging_biomarkers", "biological_age_clock_trial", "proteomic_metabolomic_aging_clocks"]),
    ("itp-mouse-lifespan", "ITP 小鼠寿命干预", "ITP Mouse Lifespan Interventions", "mouse lifespan intervention", ["itp_mouse_lifespan_interventions", "itp_mouse_lifespan_drugs", "acarbose_lifespan_aging"]),
    ("klotho-il11-aging", "Klotho / IL-11 与衰老", "Klotho / IL-11 and Aging", "Klotho / IL-11", ["klotho_aging_human", "klotho_aging", "il11_aging"]),
    ("partial-reprogramming", "部分重编程", "Partial Reprogramming", "partial reprogramming", ["partial_reprogramming_aging", "partial_reprogramming_rejuvenation"]),
    ("autophagy-mitophagy", "自噬/线粒体自噬", "Autophagy and Mitophagy", "autophagy / mitophagy", ["autophagy_mitophagy_longevity", "urolithin_a_mitophagy_aging", "urolithin_a_aging", "spermidine_autophagy_aging", "spermidine_aging", "glynac_glutathione_aging", "taurine_aging_longevity", "taurine_aging", "nutraceuticals_aging_trials"]),
    ("microbiome-inflammaging", "微生物组与炎症性衰老", "Microbiome and Inflammaging", "microbiome / inflammaging", ["microbiome_healthy_aging", "inflammaging_interventions", "immune_inflammation_aging", "parabiosis_plasma_aging", "hearing_vision_social_isolation_aging", "dementia_prevention_lifestyle_aging", "smoking_alcohol_mortality_healthy_aging", "vaccination_older_adults_mortality", "sauna_heat_therapy_mortality"]),
]

QUERY_TO_TOPIC = {}
for topic in TOPICS:
    for query in topic[4]:
        QUERY_TO_TOPIC[query] = topic

FINDING_FIELDS = [
    "finding_id", "candidate_id", "pmid", "pmcid", "doi", "source", "query",
    "topic_id", "topic_zh", "topic_en", "title_en", "title_zh", "journal", "year",
    "publication_types", "study_type_draft", "species_draft", "population_draft",
    "intervention_or_exposure_draft", "comparator_draft", "endpoint_draft",
    "sample_size_draft", "result_en", "result_zh", "conclusion_en", "conclusion_zh",
    "claim_supported_zh", "claim_supported_en", "claim_not_supported_zh",
    "claim_not_supported_en", "overinterpretation_risk_zh", "overinterpretation_risk_en",
    "evidence_level_draft", "endpoint_class_draft", "authority_signal_draft",
    "contribution_score_draft", "recommendation_class_draft", "medical_supervision_draft",
    "evidence_source_depth", "draft_notice_zh", "draft_notice_en",
    "translation_status", "review_status", "last_checked",
]


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def concise(value: str, max_chars: int = 900) -> str:
    value = clean(value)
    return value if len(value) <= max_chars else value[: max_chars - 3].rstrip() + "..."


def text(element: ET.Element | None) -> str:
    return "" if element is None else clean("".join(element.itertext()))


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


def parse_articles(pmids: Iterable[str]) -> Dict[str, ET.Element]:
    pmids = [pmid for pmid in pmids if pmid]
    if not pmids:
        return {}
    root = request_xml("efetch.fcgi", {"db": "pubmed", "id": ",".join(pmids)})
    articles: Dict[str, ET.Element] = {}
    for article in root.findall(".//PubmedArticle"):
        pmid = text(article.find(".//PMID"))
        if pmid:
            articles[pmid] = article
    return articles


def abstract_sections(article: ET.Element) -> Dict[str, str]:
    sections: Dict[str, List[str]] = {}
    for abstract_text in article.findall(".//Abstract/AbstractText"):
        label = abstract_text.attrib.get("Label") or abstract_text.attrib.get("NlmCategory") or "ABSTRACT"
        sections.setdefault(label.upper(), []).append(text(abstract_text))
    return {key: clean(" ".join(value)) for key, value in sections.items()}


def publication_types(article: ET.Element) -> List[str]:
    return [text(item) for item in article.findall(".//PublicationTypeList/PublicationType") if text(item)]


def article_ids(article: ET.Element) -> Dict[str, str]:
    ids: Dict[str, str] = {}
    for item in article.findall(".//ArticleIdList/ArticleId"):
        id_type = item.attrib.get("IdType", "").lower()
        if id_type:
            ids[id_type] = text(item)
    return ids


def classify_study(pub_types: List[str], body: str, source: str) -> str:
    joined = f"{' '.join(pub_types)} {body}".lower()
    if source == "ClinicalTrials.gov":
        return "registered_clinical_trial"
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
    return "metadata_only_needs_classification"


def classify_species(study_type: str, body: str) -> str:
    lower = body.lower()
    if study_type in {"registered_clinical_trial", "human_randomized_or_clinical_trial", "human_cohort"}:
        return "human"
    if any(term in lower for term in ["participants", "patients", "adults", "women", "men"]):
        return "human"
    if any(term in lower for term in ["mice", "mouse", "murine"]):
        return "mouse"
    if any(term in lower for term in ["rats", "rodent"]):
        return "animal"
    if "cell" in lower or "in vitro" in lower:
        return "cell"
    return "needs_review"


def classify_endpoint(query: str, body: str) -> str:
    lower = f"{query} {body}".lower()
    if any(term in lower for term in ["mortality", "death", "mace", "stroke", "cardiovascular event", "cancer incidence"]):
        return "H1"
    if any(term in lower for term in ["vo2", "frailty", "grip strength", "cognition", "falls", "ahi", "sarcopenia"]):
        return "H2"
    if any(term in lower for term in ["ldl", "apob", "blood pressure", "hba1c", "waist", "glucose", "body weight", "obesity"]):
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
    if study_type in {"registered_clinical_trial", "human_randomized_or_clinical_trial", "human_cohort"}:
        return "C"
    if study_type == "animal_study":
        return "D"
    return "E"


def recommendation(topic_id: str, level: str, species: str) -> str:
    if topic_id in {"glp1-weight-cardiometabolic", "metformin-aging", "rapamycin-mtor-aging", "senolytics"}:
        return "Medical Action" if topic_id == "glp1-weight-cardiometabolic" else "Monitor"
    if level in {"A", "B"} and species == "human":
        return "Strong Action"
    return "Monitor"


def authority_signal(row: Dict[str, str], ids: Dict[str, str], pub_types: List[str], journal: str, source_depth: str) -> str:
    signals = []
    if row.get("doi") or ids.get("doi"):
        signals.append("DOI")
    if row.get("pmid"):
        signals.append("PMID")
    if row.get("pmcid") or ids.get("pmc"):
        signals.append("PMCID/open-access signal")
    if row.get("source") == "ClinicalTrials.gov":
        signals.append("trial registry")
    if row.get("source") == "Crossref":
        signals.append("Crossref metadata")
    if any("Meta-Analysis" in pt or "Systematic Review" in pt for pt in pub_types):
        signals.append("review-level publication type")
    if any("Clinical Trial" in pt or "Randomized" in pt for pt in pub_types):
        signals.append("trial publication type")
    if journal:
        signals.append("peer-reviewed journal metadata")
    if source_depth != "abstract_only":
        signals.append(source_depth)
    return "; ".join(signals) or "metadata_only"


def score(level: str, endpoint: str, species: str, authority: str) -> int:
    level_points = {"A": 35, "B": 30, "C": 22, "D": 14, "E": 8, "F": 0}.get(level, 8)
    endpoint_points = {"H1": 20, "H2": 16, "H3": 12, "H4": 8, "H5": 8, "H6": 5}.get(endpoint, 5)
    human_points = 15 if species == "human" else 5 if species in {"mouse", "animal"} else 3
    authority_points = min(10, 2 * len([part for part in authority.split(";") if part.strip()]))
    return min(100, level_points + endpoint_points + human_points + authority_points + 10)


def selected_candidates(target: int) -> List[Dict[str, str]]:
    rows = list(csv.DictReader(CANDIDATES.open("r", encoding="utf-8-sig", newline="")))
    used: set[str] = set()
    selected: List[Dict[str, str]] = []
    per_topic = max(1, target // len(TOPICS))
    for topic in TOPICS:
        topic_rows = [row for row in rows if row.get("query") in set(topic[4])]
        topic_rows.sort(key=lambda row: (0 if row.get("source") == "PubMed" else 1 if row.get("source") == "ClinicalTrials.gov" else 2, row.get("year", "")), reverse=False)
        for row in topic_rows:
            if len([r for r in selected if r.get("_topic_id") == topic[0]]) >= per_topic:
                break
            if row["id"] in used:
                continue
            row = dict(row)
            row["_topic_id"], row["_topic_zh"], row["_topic_en"], row["_exposure"] = topic[:4]
            selected.append(row)
            used.add(row["id"])
    if len(selected) < target:
        for row in rows:
            if row["id"] in used:
                continue
            topic = QUERY_TO_TOPIC.get(row.get("query"), TOPICS[-1])
            row = dict(row)
            row["_topic_id"], row["_topic_zh"], row["_topic_en"], row["_exposure"] = topic[:4]
            selected.append(row)
            used.add(row["id"])
            if len(selected) >= target:
                break
    return selected[:target]


def zh_result(topic_zh: str, value_en: str, metadata_only: bool) -> str:
    if metadata_only:
        return f"中文草稿：该记录属于「{topic_zh}」主题；当前只有题录/注册信息，尚未抽取到摘要级结果，需要后续补全文或摘要。"
    return f"中文草稿：该研究属于「{topic_zh}」主题；摘要结果显示：{value_en}"


def zh_conclusion(value_en: str, metadata_only: bool) -> str:
    if metadata_only:
        return "中文草稿：当前仅能确认该记录与主题相关，不能据此形成正式结论。"
    return f"中文草稿：英文摘要结论为：{value_en}"


def support_claim(topic_zh: str, topic_en: str, level: str) -> tuple[str, str]:
    return (
        f"可支持：将「{topic_zh}」作为证据图谱中的候选主题，并按 {level} 级草判证据继续复核。",
        f"Supports treating {topic_en} as a candidate evidence topic with draft level {level}, pending full review.",
    )


def unsupported_claim(species: str, endpoint_class: str, metadata_only: bool) -> tuple[str, str]:
    if metadata_only:
        return ("不支持：仅凭题录/注册信息不能判断疗效、风险或临床意义。", "Does not support efficacy, risk, or clinical interpretation from metadata alone.")
    if species != "human":
        return ("不支持：不能把非人体结果直接解释为已证实的人类延寿作用。", "Does not support direct claims of proven human lifespan extension.")
    if endpoint_class not in {"H1", "H2"}:
        return ("不支持：不能把替代指标或 biomarker 改善直接解释为临床逆龄。", "Does not support interpreting surrogate or biomarker change as clinical rejuvenation.")
    return ("不支持：不能据单篇摘要给出剂量、处方或个人医疗建议。", "Does not support dosing, prescriptions, or individual medical advice from one abstract.")


def finding_from_row(row: Dict[str, str], article: ET.Element | None) -> Dict[str, str]:
    pub_types: List[str] = []
    ids: Dict[str, str] = {}
    journal = ""
    pmcid = row.get("pmcid", "")
    if article is not None:
        ids = article_ids(article)
        pub_types = publication_types(article)
        journal = text(article.find(".//Journal/Title"))
        sections = abstract_sections(article)
        body = clean(" ".join(sections.values()))
        result_en = sections.get("RESULTS") or sections.get("RESULT") or sections.get("FINDINGS") or body
        if not result_en:
            result_en = (
                f"PubMed bibliographic record for {row['_topic_en']}: {row.get('title_en','')}. "
                "No abstract result section was available through E-utilities; result extraction requires manual full-text review."
            )
        conclusion_en = sections.get("CONCLUSIONS") or sections.get("CONCLUSION") or sections.get("INTERPRETATION") or f"No separate conclusion section was parsed from the abstract for {row['_topic_en']}; full-text or manual abstract review is required before publication claims."
        pmcid = ids.get("pmc", pmcid)
        source_depth = "abstract_plus_open_pmc_available" if pmcid else "abstract_only"
        metadata_only = False
    else:
        body = row.get("title_en", "")
        result_en = f"Metadata-level record for {row['_topic_en']}: {row.get('title_en','')}. Result extraction requires abstract or full-text retrieval."
        conclusion_en = f"Metadata-level candidate only; no result-level conclusion is available yet for {row['_topic_en']}."
        source_depth = "metadata_only"
        metadata_only = True
        if row.get("source") == "ClinicalTrials.gov":
            pub_types = ["ClinicalTrials.gov registry record"]
            journal = "ClinicalTrials.gov"
        elif row.get("source") == "Crossref":
            pub_types = ["Crossref bibliographic record"]
            journal = "Crossref"
    study = classify_study(pub_types, body, row.get("source", ""))
    species = classify_species(study, body)
    endpoint = classify_endpoint(row.get("query", ""), body)
    level = evidence_level(study, endpoint)
    authority = authority_signal(row, ids, pub_types, journal, source_depth)
    contribution = score(level, endpoint, species, authority)
    rec = recommendation(row["_topic_id"], level, species)
    supported_zh, supported_en = support_claim(row["_topic_zh"], row["_topic_en"], level)
    not_zh, not_en = unsupported_claim(species, endpoint, metadata_only)
    return {
        "finding_id": f"finding-{row['id']}",
        "candidate_id": row["id"],
        "pmid": row.get("pmid", ""),
        "pmcid": pmcid,
        "doi": ids.get("doi", row.get("doi", "")),
        "source": row.get("source", ""),
        "query": row.get("query", ""),
        "topic_id": row["_topic_id"],
        "topic_zh": row["_topic_zh"],
        "topic_en": row["_topic_en"],
        "title_en": row.get("title_en", ""),
        "title_zh": row.get("title_zh", ""),
        "journal": journal,
        "year": row.get("year", ""),
        "publication_types": "; ".join(pub_types),
        "study_type_draft": study,
        "species_draft": species,
        "population_draft": "摘要级/题录级待复核 / abstract-or-metadata-level pending review",
        "intervention_or_exposure_draft": row["_exposure"],
        "comparator_draft": "摘要级/题录级待复核 / abstract-or-metadata-level pending review",
        "endpoint_draft": endpoint,
        "sample_size_draft": "摘要级/题录级待复核 / abstract-or-metadata-level pending review",
        "result_en": concise(result_en),
        "result_zh": zh_result(row["_topic_zh"], concise(result_en, 500), metadata_only),
        "conclusion_en": concise(conclusion_en),
        "conclusion_zh": zh_conclusion(concise(conclusion_en, 500), metadata_only),
        "claim_supported_zh": supported_zh,
        "claim_supported_en": supported_en,
        "claim_not_supported_zh": not_zh,
        "claim_not_supported_en": not_en,
        "overinterpretation_risk_zh": "过度解读风险：自动抽取结果不能替代全文复核，不能直接转化为个人医疗建议。",
        "overinterpretation_risk_en": "Overinterpretation risk: automated extraction does not replace full-text review and cannot be converted into personal medical advice.",
        "evidence_level_draft": level,
        "endpoint_class_draft": endpoint,
        "authority_signal_draft": authority,
        "contribution_score_draft": str(contribution),
        "recommendation_class_draft": rec,
        "medical_supervision_draft": "true" if rec == "Medical Action" or row["_topic_id"] in {"metformin-aging", "rapamycin-mtor-aging", "senolytics"} else "false",
        "evidence_source_depth": source_depth,
        "draft_notice_zh": PUBLIC_DRAFT_NOTICE_ZH,
        "draft_notice_en": PUBLIC_DRAFT_NOTICE_EN,
        "translation_status": "zh_draft_needs_review",
        "review_status": "public_draft_not_fully_reviewed",
        "last_checked": str(date.today()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=600)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    load_dotenv(ROOT / ".env")
    rows = selected_candidates(args.target)
    if len(rows) < args.target:
        raise SystemExit(f"Only {len(rows)} candidates available for target={args.target}.")
    findings: List[Dict[str, str]] = []
    for start in range(0, len(rows), 50):
        batch = rows[start : start + 50]
        pubmed_rows = [row for row in batch if row.get("pmid")]
        articles = parse_articles(row.get("pmid", "") for row in pubmed_rows)
        for row in batch:
            findings.append(finding_from_row(row, articles.get(row.get("pmid", ""))))
        if pubmed_rows:
            time.sleep(0.35)
        print(f"processed={min(start + len(batch), len(rows))}/{len(rows)}")
    with FINDINGS.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FINDING_FIELDS)
        writer.writeheader()
        writer.writerows(findings)
    print(f"Wrote {len(findings)} finding records.")


if __name__ == "__main__":
    main()
