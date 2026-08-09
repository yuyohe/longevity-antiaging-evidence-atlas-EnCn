"""Build a bounded mid-August 2026 evidence-atlas release.

The historical pipeline treated discovery volume as progress. This release
uses fixed per-topic budgets and keeps retirement decisions in compact audit
logs. Full retired rows remain recoverable from Git history and prior public
snapshots.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from dotenv import load_dotenv

import expand_healthspan_pubmed_v05 as base


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
BUILD = ROOT / "build"
ARCHIVE = DATA / "archive"
RECENT_TAG = "curated_recent_update_2026_08"
REPORT = BUILD / "healthspan_recent_update_2026_08_report.json"
PUBLIC_REPORT = DATA / "curation_release_metrics_2026_08.json"

TOPIC_PATTERNS = {
    "cardiorespiratory-fitness": r"cardiorespiratory|\bvo2\b|oxygen uptake|exercise capacity|aerobic capacity",
    "resistance-training-muscle": r"resistance training|strength training|muscle strength|sarcopen|frailty|frail|grip strength|muscle mass|functional training",
    "physical-activity-healthspan": r"physical activ|exercise|sedentary|step count|walking|active lifestyle",
    "blood-pressure-aging": r"blood pressure|hypertension|systolic|diastolic|antihypertens",
    "ldl-apob-cardiovascular-risk": r"\bldl\b|ldl-c|apob|apolipoprotein b|cholesterol|lipid.lowering|statin|pcsk9",
    "sleep-aging": r"sleep|insomnia|circadian|apnea|chronotype",
    "dietary-pattern-longevity": r"diet|dietary|mediterranean|ultra.processed|plant.based|food pattern|nutrition",
    "caloric-restriction-human": r"calori[ec] restriction|dietary restriction|energy restriction|calorie-restricted",
    "time-restricted-eating": r"time.restricted|intermittent fasting|periodic fasting|fasting.mimicking|eating window",
    "glp1-weight-cardiometabolic": r"glp.?1|semaglutide|tirzepatide|liraglutide|dulaglutide|exenatide|retatrutide",
    "metformin-aging": r"metformin|tame trial",
    "rapamycin-mtor-aging": r"rapamycin|sirolimus|everolimus|\bmtor\b|mammalian target of rapamycin",
    "senolytics": r"senolytic|cellular senescence|senescent cell|dasatinib|fisetin|quercetin",
    "nad-nmn-nr-aging": r"nicotinamide riboside|nicotinamide mononucleotide|\bnmn\b|nad\+|nad precursor",
    "epigenetic-clocks": r"epigenetic clock|dna methylation age|biological age|aging clock|age acceleration",
    "itp-mouse-lifespan": r"interventions testing program|\bitp\b|acarbose|17.alpha.estradiol|mouse lifespan",
    "klotho-il11-aging": r"klotho|il.?11|interleukin.?11",
    "partial-reprogramming": r"partial reprogram|yamanaka|oskm|cellular reprogram",
    "autophagy-mitophagy": r"autophagy|mitophagy|urolithin|spermidine|taurine|glynac|glycine.*n.acetyl",
    "microbiome-inflammaging": r"microbiom|microbiota|inflammaging|immune aging|chronic inflammation|gut flora",
}
TOPIC_REGEX = {topic_id: re.compile(pattern, re.IGNORECASE) for topic_id, pattern in TOPIC_PATTERNS.items()}
TOPIC_BY_ID = {topic["id"]: topic for topic in base.TOPICS}

PRECLINICAL_TOPICS = {
    "itp-mouse-lifespan",
    "partial-reprogramming",
    "klotho-il11-aging",
    "rapamycin-mtor-aging",
    "senolytics",
    "autophagy-mitophagy",
    "microbiome-inflammaging",
    "nad-nmn-nr-aging",
}
RETIRED_STUDY_TYPES = {
    "protocol_or_registered_plan",
    "non_primary_commentary_or_correction",
}
LOW_VALUE_TITLE_RE = re.compile(
    r"^\s*(?:correction|corrigendum|erratum|editorial|comment(?:ary)?|reply|letter)\s*:|\b(?:study|review|trial) protocol\b",
    re.IGNORECASE,
)
GRADE_SCORE = {"A": 500, "B": 400, "C": 300, "D": 200, "E": 100}
STUDY_SCORE = {
    "systematic_review_or_meta_analysis": 90,
    "human_randomized_or_clinical_trial": 80,
    "human_mendelian_randomization": 70,
    "human_cohort": 65,
    "mixed_human_and_animal_study": 35,
    "narrative_review": 30,
    "metadata_only_needs_classification": 15,
    "animal_study": 10,
    "mechanistic_or_cell_study": 5,
}
ENDPOINT_SCORE = {"H1": 60, "H2": 50, "H3": 35, "H5": 20, "H4": 15, "H6": 10}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def csv_fields(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(next(csv.reader(handle)))


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in fieldnames} for row in rows])


def append_note(row: dict[str, str], note: str) -> None:
    current = row.get("notes", "").strip()
    if note not in current:
        row["notes"] = f"{current}; {note}".strip("; ")


def normalize_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def safe_int(value: str) -> int:
    try:
        return int(float(value or 0))
    except (TypeError, ValueError):
        return 0


def concept_match(topic_id: str, text: str) -> bool:
    matcher = TOPIC_REGEX.get(topic_id)
    return bool(matcher and matcher.search(text or ""))


def topic_for_candidate(row: dict[str, str], known_topics: dict[str, str] | None = None) -> dict[str, Any] | None:
    candidate_id = row.get("id", "")
    if known_topics and candidate_id in known_topics:
        return TOPIC_BY_ID.get(known_topics[candidate_id])
    inferred = base.infer_topic(row)
    if inferred:
        return inferred
    matches = [topic_id for topic_id in TOPIC_PATTERNS if concept_match(topic_id, row.get("title_en", ""))]
    if len(matches) == 1:
        return TOPIC_BY_ID[matches[0]]
    return None


def recent_query(query: str, start_date: str, end_date: str) -> str:
    return (
        f'({query}) AND ("{start_date}"[Date - Publication] : "{end_date}"[Date - Publication]) '
        "NOT (Editorial[Publication Type] OR Comment[Publication Type] OR Letter[Publication Type] "
        "OR Published Erratum[Publication Type] OR Retracted Publication[Publication Type])"
    )


def choose_recent_topic(title: str, topic_ids: list[str]) -> str:
    title_matches = [topic_id for topic_id in topic_ids if concept_match(topic_id, title)]
    if len(title_matches) == 1:
        return title_matches[0]
    if title_matches:
        return title_matches[0]
    return topic_ids[0]


def fetch_recent_candidates(
    existing: list[dict[str, str]],
    start_date: str,
    end_date: str,
    run_date: str,
    retmax_per_topic: int,
) -> tuple[list[dict[str, str]], set[str], dict[str, Any]]:
    by_id = {row["id"]: dict(row) for row in existing if row.get("id")}
    pmid_to_id = {row["pmid"]: row["id"] for row in existing if row.get("pmid") and row.get("id")}
    matched_topics: dict[str, list[str]] = defaultdict(list)
    summaries_by_pmid: dict[str, dict[str, Any]] = {}
    query_logs: list[dict[str, str]] = []

    for topic in base.TOPICS:
        query = recent_query(topic["base"], start_date, end_date)
        pmids = base.esearch(query, retmax_per_topic, sort="pub_date")
        summaries = base.esummary(pmids)
        new_for_query = 0
        for pmid in pmids:
            if topic["id"] not in matched_topics[pmid]:
                matched_topics[pmid].append(topic["id"])
            if pmid in summaries:
                summaries_by_pmid[pmid] = summaries[pmid]
            if pmid not in pmid_to_id:
                new_for_query += 1
        query_logs.append(
            {
                "date": run_date,
                "source": "PubMed",
                "query": query,
                "result_count": str(len(pmids)),
                "new_candidates": str(new_for_query),
                "included_count": "0",
                "notes": f"{topic['id']}__{RECENT_TAG}; bounded intake pending curation",
            }
        )
        print(f"recent_search {topic['id']}: results={len(pmids)} provisional_new={new_for_query}")
        time.sleep(0.34)

    discovered_ids: set[str] = set()
    new_rows = 0
    matched_existing = 0
    for pmid, topic_ids in matched_topics.items():
        existing_id = pmid_to_id.get(pmid, "")
        if existing_id:
            row = by_id[existing_id]
            append_note(
                row,
                f"{RECENT_TAG}; publication window {start_date}..{end_date}; matched_topics={','.join(topic_ids)}",
            )
            discovered_ids.add(existing_id)
            matched_existing += 1
            continue
        item = summaries_by_pmid.get(pmid, {})
        if not item:
            continue
        title = base.clean(item.get("title", ""))
        topic_id = choose_recent_topic(title, topic_ids)
        row = {
            "id": f"pubmed-{pmid}",
            "title_en": title,
            "title_zh": "",
            "year": base.year_from_summary(item),
            "doi": base.doi_from_summary(item),
            "pmid": pmid,
            "pmcid": "",
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "source": "PubMed",
            "query": f"{topic_id}__{RECENT_TAG}",
            "include_status": "intake_pending_curation",
            "notes": (
                f"Fetched by curate_mid_august_2026.py; {RECENT_TAG}; "
                f"publication window={start_date}..{end_date}; matched_topics={','.join(topic_ids)}."
            ),
            "last_checked": run_date,
        }
        by_id[row["id"]] = row
        pmid_to_id[pmid] = row["id"]
        discovered_ids.add(row["id"])
        new_rows += 1

    base.append_query_log(query_logs)
    return list(by_id.values()), discovered_ids, {
        "date_window": f"{start_date}..{end_date}",
        "queries": len(query_logs),
        "unique_pubmed_matches": len(matched_topics),
        "new_rows": new_rows,
        "matched_existing": matched_existing,
    }


def candidate_identity_keys(row: dict[str, str]) -> list[str]:
    keys = []
    if row.get("pmid"):
        keys.append(f"pmid:{row['pmid'].strip()}")
    if row.get("doi"):
        keys.append(f"doi:{row['doi'].strip().lower()}")
    normalized = normalize_title(row.get("title_en", ""))
    if len(normalized) >= 24:
        keys.append(f"title:{normalized}")
    return keys


def candidate_dedupe_score(row: dict[str, str], current_finding_ids: set[str]) -> tuple[int, int, int, int, str]:
    source_score = {"PubMed": 30, "ClinicalTrials.gov": 20, "Crossref": 10}.get(row.get("source", ""), 0)
    return (
        1 if row.get("id") in current_finding_ids else 0,
        source_score,
        1 if row.get("pmid") else 0,
        1 if row.get("doi") else 0,
        row.get("id", ""),
    )


def dedupe_candidates(
    rows: list[dict[str, str]], current_finding_ids: set[str], run_date: str
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    kept: list[dict[str, str]] = []
    retired: list[dict[str, str]] = []
    seen: dict[str, str] = {}
    ordered = sorted(rows, key=lambda row: candidate_dedupe_score(row, current_finding_ids), reverse=True)
    for row in ordered:
        keys = candidate_identity_keys(row)
        duplicate_of = next((seen[key] for key in keys if key in seen), "")
        if duplicate_of:
            retired.append(candidate_retirement(row, "duplicate_record", run_date, duplicate_of=duplicate_of))
            continue
        kept.append(dict(row))
        for key in keys:
            seen[key] = row.get("id", "")
    return kept, retired


def fetch_findings(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for start in range(0, len(rows), 100):
        batch = rows[start : start + 100]
        pmids = [row["pmid"] for row in batch if row.get("pmid")]
        articles = base.parse_articles(pmids)
        for index, row in enumerate(batch, start + 1):
            findings.append(base.finding_from_article(row, articles.get(row.get("pmid", "")), index))
        print(f"recent_finding_enrichment={min(start + len(batch), len(rows))}/{len(rows)}")
        time.sleep(0.34)
    return findings


def finding_rejection_reason(row: dict[str, str]) -> str:
    review_status = row.get("review_status", "")
    if review_status.startswith("reviewed_"):
        return ""
    study_type = row.get("study_type_draft", "")
    if study_type in RETIRED_STUDY_TYPES:
        return study_type
    topic_id = row.get("topic_id", "")
    if not concept_match(topic_id, row.get("title_en", "")):
        return "title_topic_signal_missing"
    if row.get("species_draft") in {"mouse", "animal", "cell"} and topic_id not in PRECLINICAL_TOPICS:
        return "nonhuman_record_in_human_outcome_topic"
    return ""


def finding_score(row: dict[str, str], discovered_ids: set[str]) -> tuple[int, int, int, int, int, str]:
    level = row.get("final_evidence_level") or row.get("evidence_level_draft") or "E"
    topic_id = row.get("topic_id", "")
    title_signal = 40 if concept_match(topic_id, row.get("title_en", "")) else 0
    body_signal = 20 if concept_match(topic_id, f"{row.get('result_en', '')} {row.get('conclusion_en', '')}") else 0
    recency = 20 if row.get("candidate_id") in discovered_ids else 0
    year = safe_int(row.get("year"))
    return (
        GRADE_SCORE.get(level, 0)
        + STUDY_SCORE.get(row.get("study_type_draft", ""), 0)
        + ENDPOINT_SCORE.get(row.get("endpoint_class_draft", ""), 0)
        + safe_int(row.get("quality_confidence_score") or row.get("contribution_score_draft"))
        + title_signal
        + body_signal
        + recency,
        1 if row.get("review_status", "").startswith("reviewed_") else 0,
        1 if row.get("evidence_source_depth") != "metadata_only" else 0,
        year,
        safe_int(row.get("pmid")),
        row.get("candidate_id", ""),
    )


def curate_findings(
    rows: list[dict[str, str]],
    valid_candidate_ids: set[str],
    discovered_ids: set[str],
    per_topic_cap: int,
    run_date: str,
) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, int]]:
    eligible: dict[str, list[dict[str, str]]] = defaultdict(list)
    retired: list[dict[str, str]] = []
    seen_candidates: set[str] = set()
    for row in rows:
        candidate_id = row.get("candidate_id", "")
        if not candidate_id or candidate_id in seen_candidates:
            retired.append(finding_retirement(row, "duplicate_finding", run_date))
            continue
        seen_candidates.add(candidate_id)
        if candidate_id not in valid_candidate_ids:
            retired.append(finding_retirement(row, "candidate_retired_as_duplicate", run_date))
            continue
        reason = finding_rejection_reason(row)
        if reason:
            retired.append(finding_retirement(row, reason, run_date))
            continue
        eligible[row.get("topic_id", "")].append(row)

    selected: list[dict[str, str]] = []
    for topic in base.TOPICS:
        items = sorted(
            eligible.get(topic["id"], []),
            key=lambda row: finding_score(row, discovered_ids),
            reverse=True,
        )
        selected.extend(items[:per_topic_cap])
        for row in items[per_topic_cap:]:
            retired.append(finding_retirement(row, "topic_capacity_limit", run_date))

    selected.sort(key=lambda row: (row.get("topic_id", ""), finding_score(row, discovered_ids)), reverse=True)
    topic_counts = Counter(row.get("topic_id", "") for row in selected)
    return selected, retired, dict(sorted(topic_counts.items()))


def candidate_score(
    row: dict[str, str], topic_id: str, selected_finding_ids: set[str], discovered_ids: set[str]
) -> tuple[int, int, int, int, str]:
    score = 0
    if row.get("id") in selected_finding_ids:
        score += 1_000
    if concept_match(topic_id, row.get("title_en", "")):
        score += 120
    query_text = f"{row.get('query', '')} {row.get('notes', '')}".lower()
    if "high_weight_journal" in query_text or "high-weight-journal" in query_text:
        score += 35
    if "high_design" in query_text:
        score += 25
    if row.get("id") in discovered_ids or "recent_update" in query_text:
        score += 20
    score += {"PubMed": 12, "ClinicalTrials.gov": 8, "Crossref": 4}.get(row.get("source", ""), 0)
    if row.get("pmid"):
        score += 5
    if row.get("doi"):
        score += 3
    year = safe_int(row.get("year"))
    if year >= 2024:
        score += 8
    elif year >= 2020:
        score += 5
    return score, 1 if row.get("id") in selected_finding_ids else 0, year, safe_int(row.get("pmid")), row.get("id", "")


def curate_candidates(
    rows: list[dict[str, str]],
    selected_findings: list[dict[str, str]],
    discovered_ids: set[str],
    per_topic_cap: int,
    run_date: str,
    finding_topics: dict[str, str],
) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, int]]:
    selected_finding_ids = {row.get("candidate_id", "") for row in selected_findings}
    by_topic: dict[str, list[dict[str, str]]] = defaultdict(list)
    retired: list[dict[str, str]] = []
    for row in rows:
        topic = topic_for_candidate(row, finding_topics)
        if not topic:
            retired.append(candidate_retirement(row, "unmapped_topic", run_date))
            continue
        if LOW_VALUE_TITLE_RE.search(row.get("title_en", "")) and row.get("id") not in selected_finding_ids:
            retired.append(candidate_retirement(row, "non_result_publication_title", run_date, topic_id=topic["id"]))
            continue
        enriched = dict(row)
        enriched["_topic_id"] = topic["id"]
        by_topic[topic["id"]].append(enriched)

    selected: list[dict[str, str]] = []
    for topic in base.TOPICS:
        items = sorted(
            by_topic.get(topic["id"], []),
            key=lambda row: candidate_score(row, topic["id"], selected_finding_ids, discovered_ids),
            reverse=True,
        )
        chosen = items[:per_topic_cap]
        selected.extend(chosen)
        for row in items[per_topic_cap:]:
            retired.append(candidate_retirement(row, "topic_capacity_limit", run_date, topic_id=topic["id"]))

    for row in selected:
        row["include_status"] = (
            "selected_finding_draft" if row.get("id") in selected_finding_ids else "active_candidate_needs_review"
        )
        row.pop("_topic_id", None)
    selected.sort(key=lambda row: row.get("id", ""))
    topic_counts = Counter(
        (topic_for_candidate(row, finding_topics) or {}).get("id", "unmapped") for row in selected
    )
    return selected, retired, dict(sorted(topic_counts.items()))


def candidate_retirement(
    row: dict[str, str],
    reason: str,
    run_date: str,
    duplicate_of: str = "",
    topic_id: str = "",
) -> dict[str, str]:
    return {
        "candidate_id": row.get("id", ""),
        "source": row.get("source", ""),
        "pmid": row.get("pmid", ""),
        "doi": row.get("doi", ""),
        "title_en": row.get("title_en", ""),
        "topic_id": topic_id,
        "previous_query": row.get("query", ""),
        "previous_status": row.get("include_status", ""),
        "decision": "retired_from_active_candidate_pool",
        "reason": reason,
        "duplicate_of": duplicate_of,
        "retired_date": run_date,
        "recovery_source": "Git history and prior public-data snapshots",
    }


def finding_retirement(row: dict[str, str], reason: str, run_date: str) -> dict[str, str]:
    return {
        "finding_id": row.get("finding_id", ""),
        "candidate_id": row.get("candidate_id", ""),
        "pmid": row.get("pmid", ""),
        "doi": row.get("doi", ""),
        "title_en": row.get("title_en", ""),
        "topic_id": row.get("topic_id", ""),
        "study_type": row.get("study_type_draft", ""),
        "species": row.get("species_draft", ""),
        "previous_level": row.get("final_evidence_level") or row.get("evidence_level_draft", ""),
        "decision": "retired_from_active_findings",
        "reason": reason,
        "retired_date": run_date,
        "recovery_source": "Git history and prior public-data snapshots",
    }


def retirement_reason_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    return dict(sorted(Counter(row.get("reason", "") for row in rows).items()))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", default="2026/07/30")
    parser.add_argument("--end-date", default="2026/08/09")
    parser.add_argument("--candidate-per-topic-cap", type=int, default=600)
    parser.add_argument("--finding-per-topic-cap", type=int, default=200)
    parser.add_argument("--retmax-per-topic", type=int, default=180)
    parser.add_argument("--skip-fetch", action="store_true")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    run_date = os.environ.get("EVIDENCE_ATLAS_UPDATE_DATE", date.today().isoformat())
    base.TODAY = run_date
    base.query_specs(1)
    BUILD.mkdir(parents=True, exist_ok=True)
    ARCHIVE.mkdir(parents=True, exist_ok=True)

    candidate_path = DATA / "candidate_sources.csv"
    finding_path = DATA / "evidence_findings.csv"
    candidates_before = read_csv(candidate_path)
    findings_before = read_csv(finding_path)
    candidate_fields = csv_fields(candidate_path)
    finding_fields = csv_fields(finding_path)
    current_finding_ids = {row.get("candidate_id", "") for row in findings_before}

    if args.skip_fetch:
        merged_candidates = candidates_before
        discovered_ids = {
            row.get("id", "")
            for row in merged_candidates
            if RECENT_TAG in f"{row.get('query', '')} {row.get('notes', '')}"
        }
        fetch_report: dict[str, Any] = {
            "date_window": f"{args.start_date}..{args.end_date}",
            "queries": 0,
            "unique_pubmed_matches": len(discovered_ids),
            "new_rows": 0,
            "matched_existing": len(discovered_ids),
            "skipped_fetch": True,
        }
    else:
        merged_candidates, discovered_ids, fetch_report = fetch_recent_candidates(
            candidates_before,
            args.start_date,
            args.end_date,
            run_date,
            args.retmax_per_topic,
        )

    deduped_candidates, duplicate_retirements = dedupe_candidates(
        merged_candidates, current_finding_ids, run_date
    )
    deduped_by_id = {row.get("id", ""): row for row in deduped_candidates}
    valid_candidate_ids = set(deduped_by_id)
    existing_finding_ids = {row.get("candidate_id", "") for row in findings_before}
    finding_topics = {
        row.get("candidate_id", ""): row.get("topic_id", "")
        for row in findings_before
        if row.get("candidate_id") and row.get("topic_id")
    }

    recent_to_enrich: list[dict[str, Any]] = []
    for candidate_id in sorted(discovered_ids):
        if candidate_id in existing_finding_ids or candidate_id not in deduped_by_id:
            continue
        row = dict(deduped_by_id[candidate_id])
        topic = topic_for_candidate(row, finding_topics)
        if not topic or not row.get("pmid"):
            continue
        row["_topic"] = topic
        recent_to_enrich.append(row)

    fresh_findings = fetch_findings(recent_to_enrich)
    combined_findings = findings_before + fresh_findings
    curated_findings, finding_retirements, finding_topic_counts = curate_findings(
        combined_findings,
        valid_candidate_ids,
        discovered_ids,
        args.finding_per_topic_cap,
        run_date,
    )
    selected_finding_topics = {
        row.get("candidate_id", ""): row.get("topic_id", "")
        for row in curated_findings
        if row.get("candidate_id") and row.get("topic_id")
    }
    finding_topics.update(selected_finding_topics)

    curated_candidates, capacity_retirements, candidate_topic_counts = curate_candidates(
        deduped_candidates,
        curated_findings,
        discovered_ids,
        args.candidate_per_topic_cap,
        run_date,
        finding_topics,
    )
    active_candidate_ids = {row.get("id", "") for row in curated_candidates}
    missing_finding_candidates = sorted(
        row.get("candidate_id", "")
        for row in curated_findings
        if row.get("candidate_id", "") not in active_candidate_ids
    )
    if missing_finding_candidates:
        raise SystemExit(
            "Curated findings reference candidates outside the active pool: "
            + ", ".join(missing_finding_candidates[:10])
        )

    write_csv(candidate_path, curated_candidates, candidate_fields)
    write_csv(finding_path, curated_findings, finding_fields)

    candidate_retirements = duplicate_retirements + capacity_retirements
    candidate_retirement_fields = [
        "candidate_id",
        "source",
        "pmid",
        "doi",
        "title_en",
        "topic_id",
        "previous_query",
        "previous_status",
        "decision",
        "reason",
        "duplicate_of",
        "retired_date",
        "recovery_source",
    ]
    finding_retirement_fields = [
        "finding_id",
        "candidate_id",
        "pmid",
        "doi",
        "title_en",
        "topic_id",
        "study_type",
        "species",
        "previous_level",
        "decision",
        "reason",
        "retired_date",
        "recovery_source",
    ]
    write_csv(
        ARCHIVE / "candidate_retirement_2026-08.csv",
        sorted(candidate_retirements, key=lambda row: row.get("candidate_id", "")),
        candidate_retirement_fields,
    )
    write_csv(
        ARCHIVE / "finding_retirement_2026-08.csv",
        sorted(finding_retirements, key=lambda row: row.get("finding_id", "")),
        finding_retirement_fields,
    )

    selected_recent_candidates = [row for row in curated_candidates if row.get("id") in discovered_ids]
    selected_recent_findings = [row for row in curated_findings if row.get("candidate_id") in discovered_ids]
    report = {
        "release": "2026-08-mid-curated",
        "date": run_date,
        "search": fetch_report,
        "capacity_policy": {
            "candidate_per_topic_cap": args.candidate_per_topic_cap,
            "finding_per_topic_cap": args.finding_per_topic_cap,
            "matrix_global_cap": 1500,
            "matrix_per_topic_cap": 100,
            "core_review_per_high_grade_topic": 3,
        },
        "before": {
            "candidate_records": len(candidates_before),
            "finding_records": len(findings_before),
        },
        "after": {
            "candidate_records": len(curated_candidates),
            "finding_records": len(curated_findings),
            "recent_candidates_retained": len(selected_recent_candidates),
            "recent_findings_retained": len(selected_recent_findings),
        },
        "retired": {
            "candidate_decisions": len(candidate_retirements),
            "candidate_reasons": retirement_reason_counts(candidate_retirements),
            "finding_decisions": len(finding_retirements),
            "finding_reasons": retirement_reason_counts(finding_retirements),
        },
        "candidate_topic_counts": candidate_topic_counts,
        "finding_topic_counts": finding_topic_counts,
        "recent_selected_examples": [
            {
                "candidate_id": row.get("candidate_id", ""),
                "pmid": row.get("pmid", ""),
                "topic_id": row.get("topic_id", ""),
                "title_en": row.get("title_en", ""),
                "study_type": row.get("study_type_draft", ""),
                "draft_level": row.get("evidence_level_draft", ""),
            }
            for row in sorted(
                selected_recent_findings,
                key=lambda row: finding_score(row, discovered_ids),
                reverse=True,
            )[:20]
        ],
        "notes": [
            "Discovery is not evidence of benefit.",
            "Retired rows remain recoverable from Git history and prior public snapshots.",
            "No protocol, commentary, correction, or title-topic mismatch is promoted into active findings.",
        ],
    }
    report_text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    REPORT.write_text(report_text, encoding="utf-8")
    PUBLIC_REPORT.write_text(report_text, encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
