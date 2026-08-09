"""Fetch a bounded PubMed intake queue without changing the active library."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv

import curate_mid_august_2026 as curation
import expand_healthspan_pubmed_v05 as base


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
QUERIES = ROOT / "queries" / "pubmed.json"
ACTIVE = DATA / "candidate_sources.csv"
INTAKE = DATA / "candidate_intake.csv"
REPORT = DATA / "candidate_intake_report.json"

FIELDS = [
    "intake_id",
    "candidate_id",
    "title_en",
    "year",
    "doi",
    "pmid",
    "url",
    "source",
    "query_name",
    "topic_id",
    "publication_window",
    "intake_score",
    "intake_status",
    "fetched_date",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def active_keys(rows: list[dict[str, str]]) -> set[str]:
    keys: set[str] = set()
    for row in rows:
        for key in curation.candidate_identity_keys(row):
            keys.add(key)
    return keys


def topic_for_query(name: str) -> dict[str, object] | None:
    probe = {"id": "probe", "query": name, "title_en": ""}
    return base.infer_topic(probe)


def score_title(title: str, topic_id: str, doi: str, year: str) -> int:
    score = 60 if curation.concept_match(topic_id, title) else 0
    if re.search(r"systematic review|meta-analysis|randomi[sz]ed|clinical trial|cohort|mendelian randomization", title, re.I):
        score += 25
    if re.search(r"mortality|cardiovascular|frailty|function|dementia|healthspan|lifespan", title, re.I):
        score += 15
    if doi:
        score += 3
    if year == str(date.today().year):
        score += 5
    return score


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lookback-days", type=int, default=14)
    parser.add_argument("--max-intake", type=int, default=300)
    parser.add_argument("--retmax-per-query", type=int, default=80)
    parser.add_argument("--end-date", default=date.today().isoformat())
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    base.query_specs(1)
    end = date.fromisoformat(args.end_date)
    start = end - timedelta(days=max(1, args.lookback_days - 1))
    start_text = start.strftime("%Y/%m/%d")
    end_text = end.strftime("%Y/%m/%d")
    window = f"{start_text}..{end_text}"

    known_keys = active_keys(read_csv(ACTIVE))
    queries = json.loads(QUERIES.read_text(encoding="utf-8"))
    by_pmid: dict[str, dict[str, str]] = {}
    query_counts: list[dict[str, object]] = []

    for query_spec in queries:
        name = str(query_spec["name"])
        topic = topic_for_query(name)
        if not topic:
            continue
        query = curation.recent_query(str(query_spec["query"]), start_text, end_text)
        pmids = base.esearch(query, min(args.retmax_per_query, int(query_spec.get("max_results", 80))), sort="pub_date")
        summaries = base.esummary(pmids)
        accepted = 0
        for pmid in pmids:
            item = summaries.get(pmid, {})
            if not item:
                continue
            title = base.clean(item.get("title", ""))
            topic_id = str(topic["id"])
            if not curation.concept_match(topic_id, title):
                continue
            if curation.LOW_VALUE_TITLE_RE.search(title):
                continue
            doi = base.doi_from_summary(item)
            candidate = {
                "id": f"pubmed-{pmid}",
                "title_en": title,
                "pmid": pmid,
                "doi": doi,
            }
            if any(key in known_keys for key in curation.candidate_identity_keys(candidate)):
                continue
            year = base.year_from_summary(item)
            intake_score = score_title(title, topic_id, doi, year)
            previous = by_pmid.get(pmid)
            if previous and int(previous["intake_score"]) >= intake_score:
                continue
            by_pmid[pmid] = {
                "intake_id": f"intake-pubmed-{pmid}",
                "candidate_id": f"pubmed-{pmid}",
                "title_en": title,
                "year": year,
                "doi": doi,
                "pmid": pmid,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "source": "PubMed",
                "query_name": name,
                "topic_id": topic_id,
                "publication_window": window,
                "intake_score": str(intake_score),
                "intake_status": "pending_human_review_not_in_active_library",
                "fetched_date": args.end_date,
            }
            accepted += 1
        query_counts.append({"query_name": name, "results": len(pmids), "title_matched_new": accepted})
        time.sleep(0.34)

    rows = sorted(
        by_pmid.values(),
        key=lambda row: (int(row["intake_score"]), row["year"], row["pmid"]),
        reverse=True,
    )[: args.max_intake]
    write_csv(INTAKE, rows)
    report = {
        "status": "pending_human_review",
        "fetched_date": args.end_date,
        "publication_window": window,
        "active_library_changed": False,
        "intake_cap": args.max_intake,
        "intake_rows": len(rows),
        "queries": query_counts,
        "policy": "The scheduled job may update only this bounded intake queue. Promotion requires a reviewed pull request and may replace, not expand, the active topic budget.",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True, indent=2))
    if not rows:
        print("No eligible intake rows.", file=sys.stderr)


if __name__ == "__main__":
    main()
