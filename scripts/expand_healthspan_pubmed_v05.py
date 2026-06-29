from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CANDIDATES = DATA / "candidate_sources.csv"
FINDINGS = DATA / "evidence_findings.csv"
QUERY_LOG = DATA / "query_log.csv"
BUILD = ROOT / "build"
REPORT = BUILD / "healthspan_expansion_v05_report.json"
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TODAY = os.environ.get("EVIDENCE_ATLAS_UPDATE_DATE", "2026-04-29")

DRAFT_NOTICE_ZH = "草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。"
DRAFT_NOTICE_EN = "Draft status: automatically prepared; not fully reviewed; not medical advice."

CANDIDATE_FIELDS = [
    "id", "title_en", "title_zh", "year", "doi", "pmid", "pmcid", "url", "source", "query",
    "include_status", "notes", "last_checked",
]

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

HIGH_WEIGHT_JOURNALS = [
    "The New England journal of medicine",
    "Lancet",
    "JAMA",
    "BMJ",
    "Annals of internal medicine",
    "Nature medicine",
    "Science",
    "Nature",
    "Cell",
    "Circulation",
    "European heart journal",
    "Journal of the American College of Cardiology",
    "JAMA internal medicine",
    "JAMA cardiology",
    "Lancet public health",
    "Lancet diabetes & endocrinology",
    "Cochrane database of systematic reviews",
    "Nature aging",
    "Aging cell",
    "GeroScience",
    "Proceedings of the National Academy of Sciences of the United States of America",
    "Science translational medicine",
]

JOURNAL_QUERY = " OR ".join(f'"{journal}"[Journal]' for journal in HIGH_WEIGHT_JOURNALS)
DESIGN_QUERY = (
    '"systematic review"[Publication Type] OR "meta-analysis"[Publication Type] OR '
    '"randomized controlled trial"[Publication Type] OR cohort[Title/Abstract] OR '
    '"Mendelian randomization"[Title/Abstract] OR "umbrella review"[Title/Abstract]'
)

TOPICS: list[dict[str, Any]] = [
    {"id": "cardiorespiratory-fitness", "zh": "心肺适能与死亡风险", "en": "Cardiorespiratory Fitness and Mortality", "exposure": "fitness / VO2max", "base": '(cardiorespiratory fitness OR VO2max OR "VO2 max" OR "exercise capacity") AND (mortality OR "cardiovascular mortality" OR "all-cause mortality")'},
    {"id": "resistance-training-muscle", "zh": "抗阻训练、肌肉与衰弱", "en": "Resistance Training, Muscle, and Frailty", "exposure": "resistance training / muscle", "base": '("resistance training" OR "strength training" OR sarcopenia OR "muscle strength" OR frailty) AND (older adults OR aging OR mortality OR disability)'},
    {"id": "physical-activity-healthspan", "zh": "身体活动与健康寿命", "en": "Physical Activity and Healthspan", "exposure": "physical activity", "base": '("physical activity" OR exercise OR "sedentary behavior") AND (mortality OR longevity OR "healthy aging" OR healthspan)'},
    {"id": "blood-pressure-aging", "zh": "血压与健康寿命", "en": "Blood Pressure and Healthspan", "exposure": "blood pressure", "base": '("blood pressure" OR hypertension OR "systolic blood pressure") AND (mortality OR "cardiovascular disease" OR stroke OR dementia) AND (aging OR elderly OR "older adults")'},
    {"id": "ldl-apob-cardiovascular-risk", "zh": "LDL-C/apoB 与心血管风险", "en": "LDL-C/apoB and Cardiovascular Risk", "exposure": "LDL-C / apoB", "base": '("LDL cholesterol" OR LDL-C OR "apolipoprotein B" OR apoB) AND ("cardiovascular risk" OR mortality OR "major adverse cardiovascular events")'},
    {"id": "sleep-aging", "zh": "睡眠与健康结局", "en": "Sleep and Aging Outcomes", "exposure": "sleep", "base": '("sleep duration" OR insomnia OR "sleep quality" OR "sleep apnea") AND (mortality OR dementia OR "healthy aging" OR cardiovascular)'},
    {"id": "dietary-pattern-longevity", "zh": "饮食模式与死亡风险", "en": "Dietary Patterns and Mortality", "exposure": "dietary pattern", "base": '("Mediterranean diet" OR "dietary pattern" OR "diet quality" OR "ultra-processed food" OR "plant-based diet") AND (mortality OR longevity OR "healthy aging")'},
    {"id": "caloric-restriction-human", "zh": "热量限制与人体衰老", "en": "Caloric Restriction in Humans", "exposure": "caloric restriction", "base": '("caloric restriction" OR "calorie restriction" OR "dietary restriction") AND (aging OR "biological aging" OR "metabolic health") AND (human OR adults OR trial)'},
    {"id": "time-restricted-eating", "zh": "限时进食与代谢健康", "en": "Time-Restricted Eating and Metabolic Health", "exposure": "time-restricted eating / intermittent fasting", "base": '("time-restricted eating" OR "time restricted feeding" OR "intermittent fasting") AND (metabolic OR aging OR obesity OR mortality)'},
    {"id": "glp1-weight-cardiometabolic", "zh": "GLP-1、减重与心代谢结局", "en": "GLP-1, Weight Loss, and Cardiometabolic Outcomes", "exposure": "GLP-1 / weight loss", "base": '(semaglutide OR tirzepatide OR "GLP-1 receptor agonist" OR liraglutide) AND (mortality OR cardiovascular OR obesity OR "kidney outcomes")'},
    {"id": "metformin-aging", "zh": "二甲双胍与衰老", "en": "Metformin and Aging", "exposure": "metformin", "base": '(metformin) AND (aging OR longevity OR lifespan OR mortality OR "age-related disease" OR TAME)'},
    {"id": "rapamycin-mtor-aging", "zh": "雷帕霉素/mTOR 与衰老", "en": "Rapamycin/mTOR and Aging", "exposure": "rapamycin / mTOR", "base": '(rapamycin OR sirolimus OR "mTOR inhibitor") AND (aging OR longevity OR lifespan OR "immune aging")'},
    {"id": "senolytics", "zh": "Senolytics 清除衰老细胞", "en": "Senolytics", "exposure": "senolytics", "base": '(senolytic OR senolytics OR dasatinib OR quercetin OR fisetin) AND (aging OR frailty OR senescence OR fibrosis)'},
    {"id": "nad-nmn-nr-aging", "zh": "NAD/NMN/NR", "en": "NAD/NMN/NR", "exposure": "NAD / NMN / NR", "base": '("nicotinamide riboside" OR "nicotinamide mononucleotide" OR NMN OR "NAD precursor") AND (aging OR "older adults" OR metabolic OR mitochondrial)'},
    {"id": "epigenetic-clocks", "zh": "表观遗传时钟", "en": "Epigenetic Clocks", "exposure": "epigenetic clock", "base": '("epigenetic clock" OR "DNA methylation age" OR "biological age" OR "aging clock") AND (mortality OR disease OR intervention OR prediction)'},
    {"id": "itp-mouse-lifespan", "zh": "ITP 小鼠寿命干预", "en": "ITP Mouse Lifespan Interventions", "exposure": "mouse lifespan intervention", "base": '("Interventions Testing Program" OR ITP OR acarbose OR "17-alpha-estradiol" OR rapamycin) AND (mouse OR mice) AND (lifespan OR longevity)'},
    {"id": "klotho-il11-aging", "zh": "Klotho / IL-11", "en": "Klotho / IL-11", "exposure": "Klotho / IL-11", "base": '(Klotho OR "interleukin 11" OR IL-11) AND (aging OR frailty OR mortality OR lifespan OR inflammation)'},
    {"id": "partial-reprogramming", "zh": "部分重编程", "en": "Partial Reprogramming", "exposure": "partial reprogramming", "base": '("partial reprogramming" OR "Yamanaka factors" OR "cellular reprogramming") AND (aging OR rejuvenation OR lifespan)'},
    {"id": "autophagy-mitophagy", "zh": "自噬/线粒体自噬", "en": "Autophagy and Mitophagy", "exposure": "autophagy / mitophagy", "base": '(autophagy OR mitophagy OR "urolithin A" OR spermidine OR taurine OR GlyNAC) AND (aging OR longevity OR lifespan OR "older adults")'},
    {"id": "microbiome-inflammaging", "zh": "微生物组与炎症性衰老", "en": "Microbiome and Inflammaging", "exposure": "microbiome / inflammaging", "base": '(microbiome OR microbiota OR inflammaging OR "chronic inflammation" OR "immune aging") AND (aging OR frailty OR mortality OR longevity)'},
]

TOPIC_BY_QUERY: dict[str, dict[str, Any]] = {}


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def concise(value: str, max_chars: int = 900) -> str:
    value = clean(value)
    return value if len(value) <= max_chars else value[: max_chars - 3].rstrip() + "..."


def text(element: ET.Element | None) -> str:
    return "" if element is None else clean("".join(element.itertext()))


def request_json(endpoint: str, params: dict[str, str], timeout: int = 45, retries: int = 4) -> dict:
    params = dict(params)
    params["retmode"] = "json"
    if os.getenv("NCBI_EMAIL"):
        params["email"] = os.getenv("NCBI_EMAIL", "")
    if os.getenv("NCBI_API_KEY"):
        params["api_key"] = os.getenv("NCBI_API_KEY", "")
    url = f"{BASE}/{endpoint}?{urlencode(params)}"
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            last_exc = exc
            if attempt == retries - 1:
                raise
            time.sleep(1.2 * (attempt + 1))
    raise last_exc or RuntimeError(f"PubMed JSON request failed: {endpoint}")


def request_xml(endpoint: str, params: dict[str, str], timeout: int = 60, retries: int = 4) -> ET.Element:
    params = dict(params)
    params["retmode"] = "xml"
    if os.getenv("NCBI_EMAIL"):
        params["email"] = os.getenv("NCBI_EMAIL", "")
    if os.getenv("NCBI_API_KEY"):
        params["api_key"] = os.getenv("NCBI_API_KEY", "")
    url = f"{BASE}/{endpoint}?{urlencode(params)}"
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
            return ET.fromstring(resp.content)
        except (requests.RequestException, ET.ParseError) as exc:
            last_exc = exc
            if attempt == retries - 1:
                raise
            time.sleep(1.2 * (attempt + 1))
    raise last_exc or RuntimeError(f"PubMed XML request failed: {endpoint}")


def esearch(query: str, retmax: int, sort: str = "relevance") -> list[str]:
    data = request_json("esearch.fcgi", {"db": "pubmed", "term": query, "retmax": str(retmax), "sort": sort})
    return data.get("esearchresult", {}).get("idlist", [])


def esummary(pmids: list[str]) -> dict[str, dict]:
    if not pmids:
        return {}
    data = request_json("esummary.fcgi", {"db": "pubmed", "id": ",".join(pmids)})
    result = data.get("result", {})
    return {pmid: result.get(pmid, {}) for pmid in pmids}


def parse_articles(pmids: list[str]) -> dict[str, ET.Element]:
    if not pmids:
        return {}
    root = request_xml("efetch.fcgi", {"db": "pubmed", "id": ",".join(pmids)})
    out = {}
    for article in root.findall(".//PubmedArticle"):
        pmid = text(article.find(".//PMID"))
        if pmid:
            out[pmid] = article
    return out


def abstract_sections(article: ET.Element) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    for abstract_text in article.findall(".//Abstract/AbstractText"):
        label = abstract_text.attrib.get("Label") or abstract_text.attrib.get("NlmCategory") or "ABSTRACT"
        sections.setdefault(label.upper(), []).append(text(abstract_text))
    return {key: clean(" ".join(value)) for key, value in sections.items()}


def publication_types(article: ET.Element) -> list[str]:
    return [text(item) for item in article.findall(".//PublicationTypeList/PublicationType") if text(item)]


def article_ids(article: ET.Element) -> dict[str, str]:
    ids = {}
    for item in article.findall(".//ArticleIdList/ArticleId"):
        id_type = item.attrib.get("IdType", "").lower()
        if id_type:
            ids[id_type] = text(item)
    return ids


def journal_from_summary(item: dict) -> str:
    return clean(item.get("fulljournalname") or item.get("source") or "")


def doi_from_summary(item: dict) -> str:
    for aid in item.get("articleids", []):
        if aid.get("idtype") == "doi":
            return aid.get("value", "")
    return ""


def year_from_summary(item: dict) -> str:
    return str(item.get("pubdate", "")[:4])


def load_candidates() -> list[dict[str, str]]:
    if not CANDIDATES.exists():
        return []
    with CANDIDATES.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_candidates(rows: list[dict[str, str]]) -> None:
    with CANDIDATES.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CANDIDATE_FIELDS)
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in CANDIDATE_FIELDS} for row in rows])


def append_query_log(rows: list[dict[str, str]]) -> None:
    fields = ["date", "source", "query", "result_count", "new_candidates", "included_count", "notes"]
    exists = QUERY_LOG.exists() and QUERY_LOG.stat().st_size > 0
    with QUERY_LOG.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def query_specs(retmax: int) -> list[dict[str, Any]]:
    specs = []
    for topic in TOPICS:
        topic_id = topic["id"]
        tiers = [
            ("high_weight_journal", f'({topic["base"]}) AND ({JOURNAL_QUERY})', max(30, retmax // 3), 35),
            ("high_design", f'({topic["base"]}) AND ({DESIGN_QUERY})', retmax, 25),
            ("recent_review_trial", f'({topic["base"]}) AND (review[Title/Abstract] OR trial[Title/Abstract] OR cohort[Title/Abstract] OR "systematic review"[Title/Abstract] OR "meta-analysis"[Title/Abstract])', retmax, 15),
        ]
        for tier, query, max_results, bonus in tiers:
            name = f"{topic_id}__{tier}"
            TOPIC_BY_QUERY[name] = topic
            specs.append({"name": name, "query": query, "max_results": max_results, "tier": tier, "bonus": bonus})
    return specs


def expand_candidates(retmax_per_topic_tier: int) -> tuple[list[dict[str, str]], dict[str, Any]]:
    existing = load_candidates()
    by_id = {row.get("id", ""): dict(row) for row in existing if row.get("id")}
    by_pmid = {row.get("pmid", "") for row in existing if row.get("pmid")}
    logs = []
    added = 0
    for spec in query_specs(retmax_per_topic_tier):
        pmids = esearch(spec["query"], int(spec["max_results"]))
        summaries = esummary(pmids)
        new_for_query = 0
        for pmid in pmids:
            if pmid in by_pmid:
                continue
            item = summaries.get(pmid, {})
            if not item:
                continue
            row = {
                "id": f"pubmed-{pmid}",
                "title_en": clean(item.get("title", "")),
                "title_zh": "",
                "year": year_from_summary(item),
                "doi": doi_from_summary(item),
                "pmid": pmid,
                "pmcid": "",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "source": "PubMed",
                "query": spec["name"],
                "include_status": "needs_review",
                "notes": f"Fetched by expand_healthspan_pubmed_v05.py; tier={spec['tier']}; high-weight-journal prioritized where available.",
                "last_checked": TODAY,
            }
            by_id[row["id"]] = row
            by_pmid.add(pmid)
            added += 1
            new_for_query += 1
        logs.append({
            "date": TODAY,
            "source": "PubMed",
            "query": spec["query"],
            "result_count": str(len(pmids)),
            "new_candidates": str(new_for_query),
            "included_count": "0",
            "notes": spec["name"],
        })
        print(f"{spec['name']}: results={len(pmids)} new={new_for_query}")
        time.sleep(0.34)
    rows = list(by_id.values())
    write_candidates(rows)
    append_query_log(logs)
    return rows, {"existing": len(existing), "added": added, "total": len(rows)}


def infer_topic(row: dict[str, str]) -> dict[str, Any] | None:
    q = row.get("query", "")
    if q in TOPIC_BY_QUERY:
        return TOPIC_BY_QUERY[q]
    for topic in TOPICS:
        if q.startswith(topic["id"] + "__"):
            return topic
    legacy = {
        "cardiorespiratory_fitness_mortality": "cardiorespiratory-fitness",
        "exercise_cardiorespiratory_fitness_longevity": "cardiorespiratory-fitness",
        "resistance_training_mortality_sarcopenia": "resistance-training-muscle",
        "resistance_training_sarcopenia_frailty": "resistance-training-muscle",
        "exercise_older_adults_frailty": "resistance-training-muscle",
        "physical_activity_longevity": "physical-activity-healthspan",
        "frailty_interventions_older_adults": "physical-activity-healthspan",
        "frailty_multidomain": "physical-activity-healthspan",
        "frailty_multidomain_interventions": "physical-activity-healthspan",
        "blood_pressure_mortality_aging": "blood-pressure-aging",
        "ldl_apob_cardiovascular_mortality": "ldl-apob-cardiovascular-risk",
        "sleep_duration_mortality_aging": "sleep-aging",
        "dietary_pattern_longevity": "dietary-pattern-longevity",
        "nutrition_dietary_restriction_aging": "dietary-pattern-longevity",
        "human_longevity_interventions_reviews": "dietary-pattern-longevity",
        "caloric_restriction_human_aging": "caloric-restriction-human",
        "caloric_restriction_aging": "caloric-restriction-human",
        "intermittent_fasting_aging_human": "time-restricted-eating",
        "time_restricted_eating_aging": "time-restricted-eating",
        "glp1_obesity_cardiometabolic_outcomes": "glp1-weight-cardiometabolic",
        "diabetes_obesity_longevity_outcomes": "glp1-weight-cardiometabolic",
        "obesity_weight_loss_mortality_aging": "glp1-weight-cardiometabolic",
        "metformin_aging_longevity": "metformin-aging",
        "metformin_aging": "metformin-aging",
        "rapamycin_mtor_aging": "rapamycin-mtor-aging",
        "rapamycin_aging": "rapamycin-mtor-aging",
        "geroprotectors_mtor_metformin_senolytics": "senolytics",
        "senolytics_human_aging": "senolytics",
        "senolytics_aging": "senolytics",
        "nad_nmn_nr_human_aging": "nad-nmn-nr-aging",
        "nad_precursors_aging_trials": "nad-nmn-nr-aging",
        "nad_nmn_nr_aging": "nad-nmn-nr-aging",
        "epigenetic_clocks_intervention": "epigenetic-clocks",
        "aging_clocks_disease_prediction": "epigenetic-clocks",
        "clinical_aging_biomarkers": "epigenetic-clocks",
        "biological_age_clock_trial": "epigenetic-clocks",
        "proteomic_metabolomic_aging_clocks": "epigenetic-clocks",
        "itp_mouse_lifespan_interventions": "itp-mouse-lifespan",
        "itp_mouse_lifespan_drugs": "itp-mouse-lifespan",
        "acarbose_lifespan_aging": "itp-mouse-lifespan",
        "klotho_aging_human": "klotho-il11-aging",
        "klotho_aging": "klotho-il11-aging",
        "il11_aging": "klotho-il11-aging",
        "partial_reprogramming_aging": "partial-reprogramming",
        "partial_reprogramming_rejuvenation": "partial-reprogramming",
        "autophagy_mitophagy_longevity": "autophagy-mitophagy",
        "urolithin_a_mitophagy_aging": "autophagy-mitophagy",
        "urolithin_a_aging": "autophagy-mitophagy",
        "spermidine_autophagy_aging": "autophagy-mitophagy",
        "spermidine_aging": "autophagy-mitophagy",
        "glynac_glutathione_aging": "autophagy-mitophagy",
        "taurine_aging_longevity": "autophagy-mitophagy",
        "taurine_aging": "autophagy-mitophagy",
        "nutraceuticals_aging_trials": "autophagy-mitophagy",
        "microbiome_healthy_aging": "microbiome-inflammaging",
        "inflammaging_interventions": "microbiome-inflammaging",
        "immune_inflammation_aging": "microbiome-inflammaging",
        "parabiosis_plasma_aging": "microbiome-inflammaging",
        "hearing_vision_social_isolation_aging": "microbiome-inflammaging",
        "dementia_prevention_lifestyle_aging": "microbiome-inflammaging",
        "smoking_alcohol_mortality_healthy_aging": "microbiome-inflammaging",
        "vaccination_older_adults_mortality": "microbiome-inflammaging",
        "sauna_heat_therapy_mortality": "microbiome-inflammaging",
    }
    topic_id = legacy.get(q)
    if topic_id:
        return next(t for t in TOPICS if t["id"] == topic_id)
    return None


def pre_priority(row: dict[str, str], topic: dict[str, Any]) -> int:
    text_blob = f"{row.get('title_en','')} {row.get('notes','')} {row.get('query','')}".lower()
    score = 0
    if "high_weight_journal" in row.get("query", "") or "high-weight-journal" in row.get("notes", ""):
        score += 35
    if "recent_update" in row.get("query", "") or "recent_update" in row.get("notes", ""):
        score += 18
    if any(term.lower() in text_blob for term in ["systematic review", "meta-analysis", "randomized", "clinical trial", "cohort", "mendelian randomization"]):
        score += 25
    try:
        year = int(row.get("year") or 0)
        if year >= 2020:
            score += 8
        elif year >= 2015:
            score += 4
    except Exception:
        pass
    if row.get("doi"):
        score += 3
    if row.get("pmid"):
        score += 3
    if topic["id"] in {"cardiorespiratory-fitness", "blood-pressure-aging", "ldl-apob-cardiovascular-risk", "physical-activity-healthspan"}:
        score += 3
    return score


def select_candidates(rows: list[dict[str, str]], target: int) -> list[dict[str, str]]:
    by_topic: dict[str, list[tuple[int, dict[str, str], dict[str, Any]]]] = defaultdict(list)
    for row in rows:
        if row.get("source") != "PubMed" or not row.get("pmid"):
            continue
        topic = infer_topic(row)
        if not topic:
            continue
        by_topic[topic["id"]].append((pre_priority(row, topic), row, topic))
    per_topic = target // len(TOPICS)
    selected = []
    used = set()
    for topic in TOPICS:
        items = sorted(by_topic[topic["id"]], key=lambda item: (item[0], item[1].get("year", "")), reverse=True)
        for _, row, t in items[:per_topic]:
            row = dict(row)
            row["_topic"] = t
            selected.append(row)
            used.add(row["id"])
    if len(selected) < target:
        leftovers = []
        for items in by_topic.values():
            leftovers.extend(items)
        leftovers.sort(key=lambda item: (item[0], item[1].get("year", "")), reverse=True)
        for _, row, topic in leftovers:
            if row["id"] in used:
                continue
            row = dict(row)
            row["_topic"] = topic
            selected.append(row)
            used.add(row["id"])
            if len(selected) >= target:
                break
    return selected[:target]


def classify_study(pub_types: list[str], body: str, source: str) -> str:
    joined = f"{' '.join(pub_types)} {body}".lower()
    if source == "ClinicalTrials.gov":
        return "registered_clinical_trial"
    if "meta-analysis" in joined or "systematic review" in joined or "umbrella review" in joined:
        return "systematic_review_or_meta_analysis"
    if "randomized" in joined or "randomised" in joined or "clinical trial" in joined:
        return "human_randomized_or_clinical_trial"
    if "mendelian randomization" in joined:
        return "human_mendelian_randomization"
    if "cohort" in joined or "prospective" in joined or "longitudinal" in joined:
        return "human_cohort"
    if any(term in joined for term in ["mice", "mouse", "murine", "rats", "rodent"]):
        return "animal_study"
    if any(term in joined for term in ["cell", "in vitro", "organoid"]):
        return "mechanistic_or_cell_study"
    if "review" in joined:
        return "narrative_review"
    return "metadata_only_needs_classification"


def classify_species(study_type: str, body: str) -> str:
    lower = body.lower()
    if study_type in {"registered_clinical_trial", "human_randomized_or_clinical_trial", "human_cohort", "human_mendelian_randomization"}:
        return "human"
    if any(term in lower for term in ["participants", "patients", "adults", "women", "men", "cohort"]):
        return "human"
    if any(term in lower for term in ["mice", "mouse", "murine"]):
        return "mouse"
    if any(term in lower for term in ["rats", "rodent"]):
        return "animal"
    if "cell" in lower or "in vitro" in lower:
        return "cell"
    return "needs_review"


def classify_endpoint(topic_id: str, body: str) -> str:
    lower = f"{topic_id} {body}".lower()
    if any(term in lower for term in ["mortality", "death", "mace", "stroke", "cardiovascular event", "fracture", "dementia incidence", "cancer incidence"]):
        return "H1"
    if any(term in lower for term in ["vo2", "frailty", "grip strength", "cognition", "falls", "sarcopenia", "disability", "quality of life"]):
        return "H2"
    if any(term in lower for term in ["ldl", "apob", "blood pressure", "hba1c", "waist", "glucose", "body weight", "obesity", "insulin"]):
        return "H3"
    if "clock" in lower or "methylation age" in lower or "biological age" in lower:
        return "H5"
    if any(term in lower for term in ["lifespan", "survival"]) and any(term in lower for term in ["mouse", "mice"]):
        return "H6"
    return "H4"


def evidence_level(study_type: str, endpoint_class: str) -> str:
    if study_type == "systematic_review_or_meta_analysis" and endpoint_class in {"H1", "H2"}:
        return "A"
    if study_type in {"human_randomized_or_clinical_trial", "human_cohort", "human_mendelian_randomization"} and endpoint_class in {"H1", "H2"}:
        return "B"
    if study_type in {"registered_clinical_trial", "human_randomized_or_clinical_trial", "human_cohort", "human_mendelian_randomization"}:
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


def authority_signal(row: dict[str, str], ids: dict[str, str], pub_types: list[str], journal: str, source_depth: str) -> str:
    signals = []
    if row.get("doi") or ids.get("doi"):
        signals.append("DOI")
    if row.get("pmid"):
        signals.append("PMID")
    if row.get("pmcid") or ids.get("pmc"):
        signals.append("PMCID/open-access signal")
    if any(journal.lower() == j.lower() for j in HIGH_WEIGHT_JOURNALS):
        signals.append("high-weight journal family signal")
    if any("Meta-Analysis" in pt or "Systematic Review" in pt for pt in pub_types):
        signals.append("review-level publication type")
    if any("Clinical Trial" in pt or "Randomized" in pt for pt in pub_types):
        signals.append("trial publication type")
    if journal:
        signals.append("peer-reviewed journal metadata")
    if source_depth != "abstract_only":
        signals.append(source_depth)
    return "; ".join(signals) or "metadata_only"


def draft_score(level: str, endpoint: str, species: str, authority: str) -> int:
    level_points = {"A": 35, "B": 30, "C": 22, "D": 14, "E": 8}.get(level, 8)
    endpoint_points = {"H1": 20, "H2": 16, "H3": 12, "H4": 8, "H5": 8, "H6": 5}.get(endpoint, 5)
    human_points = 15 if species == "human" else 5 if species in {"mouse", "animal"} else 3
    authority_points = min(14, 2 * len([part for part in authority.split(";") if part.strip()]))
    return min(100, level_points + endpoint_points + human_points + authority_points + 10)


def unsupported_claim(species: str, endpoint_class: str, metadata_only: bool) -> tuple[str, str]:
    if metadata_only:
        return ("不支持：仅凭题录/注册信息不能判断疗效、风险或临床意义。", "Does not support efficacy, risk, or clinical interpretation from metadata alone.")
    if species != "human":
        return ("不支持：不能把非人体结果直接解释为已证实的人类延寿作用。", "Does not support direct claims of proven human lifespan extension.")
    if endpoint_class not in {"H1", "H2"}:
        return ("不支持：不能把替代指标或 biomarker 改善直接解释为临床逆龄。", "Does not support interpreting surrogate or biomarker change as clinical rejuvenation.")
    return ("不支持：不能据单篇摘要给出剂量、处方或个人医疗建议。", "Does not support dosing, prescriptions, or individual medical advice from one abstract.")


def finding_from_article(row: dict[str, str], article: ET.Element | None, index: int) -> dict[str, str]:
    topic = row["_topic"]
    pub_types = []
    ids = {}
    journal = ""
    pmcid = row.get("pmcid", "")
    if article is not None:
        ids = article_ids(article)
        pub_types = publication_types(article)
        journal = text(article.find(".//Journal/Title")) or row.get("journal", "")
        sections = abstract_sections(article)
        body = clean(" ".join(sections.values()))
        result_en = sections.get("RESULTS") or sections.get("RESULT") or sections.get("FINDINGS") or body
        if not result_en:
            result_en = f"PubMed bibliographic record for {topic['en']}: {row.get('title_en','')}. No abstract result section was available; manual full-text review is required."
        conclusion_en = sections.get("CONCLUSIONS") or sections.get("CONCLUSION") or sections.get("INTERPRETATION") or f"No separate conclusion section was parsed from the abstract for {topic['en']}; full-text or manual abstract review is required before publication claims."
        pmcid = ids.get("pmc", pmcid)
        source_depth = "abstract_plus_open_pmc_available" if pmcid else "abstract_only"
        metadata_only = False
    else:
        body = row.get("title_en", "")
        journal = row.get("journal", "")
        result_en = f"Metadata-level record for {topic['en']}: {row.get('title_en','')}. Result extraction requires abstract or full-text retrieval."
        conclusion_en = f"Metadata-level candidate only; no result-level conclusion is available yet for {topic['en']}."
        source_depth = "metadata_only"
        metadata_only = True
    study = classify_study(pub_types, body, row.get("source", "PubMed"))
    species = classify_species(study, body)
    endpoint = classify_endpoint(topic["id"], body)
    level = evidence_level(study, endpoint)
    authority = authority_signal(row, ids, pub_types, journal, source_depth)
    contribution = draft_score(level, endpoint, species, authority)
    rec = recommendation(topic["id"], level, species)
    not_zh, not_en = unsupported_claim(species, endpoint, metadata_only)
    result_short = concise(result_en)
    conclusion_short = concise(conclusion_en)
    return {
        "finding_id": f"finding-{row['id']}",
        "candidate_id": row["id"],
        "pmid": row.get("pmid", ""),
        "pmcid": pmcid,
        "doi": ids.get("doi", row.get("doi", "")),
        "source": row.get("source", "PubMed"),
        "query": row.get("query", ""),
        "topic_id": topic["id"],
        "topic_zh": topic["zh"],
        "topic_en": topic["en"],
        "title_en": row.get("title_en", ""),
        "title_zh": row.get("title_zh", ""),
        "journal": journal,
        "year": row.get("year", ""),
        "publication_types": "; ".join(pub_types),
        "study_type_draft": study,
        "species_draft": species,
        "population_draft": "摘要级/题录级待复核 / abstract-or-metadata-level pending review",
        "intervention_or_exposure_draft": topic["exposure"],
        "comparator_draft": "摘要级/题录级待复核 / abstract-or-metadata-level pending review",
        "endpoint_draft": endpoint,
        "sample_size_draft": "摘要级/题录级待复核 / abstract-or-metadata-level pending review",
        "result_en": result_short,
        "result_zh": f"中文草稿：该研究属于「{topic['zh']}」主题；摘要/题录结果显示：{concise(result_en, 500)}",
        "conclusion_en": conclusion_short,
        "conclusion_zh": f"中文草稿：英文摘要结论为：{concise(conclusion_en, 500)}",
        "claim_supported_zh": f"可支持：将「{topic['zh']}」作为证据图谱中的候选主题，并按 {level} 级草判证据继续复核。",
        "claim_supported_en": f"Supports treating {topic['en']} as a candidate evidence topic with draft level {level}, pending full review.",
        "claim_not_supported_zh": not_zh,
        "claim_not_supported_en": not_en,
        "overinterpretation_risk_zh": "过度解读风险：自动抽取结果不能替代全文复核，不能直接转化为个人医疗建议。",
        "overinterpretation_risk_en": "Overinterpretation risk: automated extraction does not replace full-text review and cannot be converted into personal medical advice.",
        "evidence_level_draft": level,
        "endpoint_class_draft": endpoint,
        "authority_signal_draft": authority,
        "contribution_score_draft": str(contribution),
        "recommendation_class_draft": rec,
        "medical_supervision_draft": "true" if rec == "Medical Action" or topic["id"] in {"metformin-aging", "rapamycin-mtor-aging", "senolytics"} else "false",
        "evidence_source_depth": source_depth,
        "draft_notice_zh": DRAFT_NOTICE_ZH,
        "draft_notice_en": DRAFT_NOTICE_EN,
        "translation_status": "zh_draft_needs_review",
        "review_status": "public_draft_not_fully_reviewed",
        "last_checked": TODAY,
    }


def build_findings(selected: list[dict[str, str]]) -> list[dict[str, str]]:
    findings = []
    for start in range(0, len(selected), 100):
        batch = selected[start : start + 100]
        pmids = [row["pmid"] for row in batch if row.get("pmid")]
        articles = parse_articles(pmids)
        for i, row in enumerate(batch, start + 1):
            findings.append(finding_from_article(row, articles.get(row.get("pmid", "")), i))
        print(f"finding_enrichment={min(start + len(batch), len(selected))}/{len(selected)}")
        time.sleep(0.34)
    with FINDINGS.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FINDING_FIELDS)
        writer.writeheader()
        writer.writerows(findings)
    return findings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=1800)
    parser.add_argument("--retmax-per-topic-tier", type=int, default=140)
    parser.add_argument("--skip-fetch", action="store_true")
    args = parser.parse_args()
    load_dotenv(ROOT / ".env")
    BUILD.mkdir(exist_ok=True)
    if args.skip_fetch:
        rows = load_candidates()
        expansion = {"existing": len(rows), "added": 0, "total": len(rows), "skipped_fetch": True}
    else:
        rows, expansion = expand_candidates(args.retmax_per_topic_tier)
    selected = select_candidates(rows, args.target)
    if len(selected) < args.target:
        raise SystemExit(f"Only {len(selected)} topic-mapped PubMed candidates available; target={args.target}. Increase retmax or add queries.")
    findings = build_findings(selected)
    topic_counts = defaultdict(int)
    for row in findings:
        topic_counts[row["topic_id"]] += 1
    report = {
        "date": TODAY,
        "target": args.target,
        "candidate_expansion": expansion,
        "findings_written": len(findings),
        "topic_counts": dict(sorted(topic_counts.items())),
        "high_weight_journals": HIGH_WEIGHT_JOURNALS,
        "query_policy": "Prioritize high-weight journals, then systematic reviews/meta-analyses/RCTs/cohorts/Mendelian randomization, then broader recent review/trial/cohort records.",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
