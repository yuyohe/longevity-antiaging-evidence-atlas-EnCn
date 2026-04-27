"""Fetch candidate longevity-related clinical trials from ClinicalTrials.gov v2."""

from __future__ import annotations

import csv
import json
import time
from datetime import date
from pathlib import Path
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

from candidate_utils import append_rows, is_duplicate, load_candidate_keys, remember

ROOT = Path(__file__).resolve().parents[1]
QUERIES = ROOT / "queries" / "clinicaltrials.json"
CANDIDATES = ROOT / "data" / "candidate_sources.csv"
QUERY_LOG = ROOT / "data" / "query_log.csv"
BASE = "https://clinicaltrials.gov/api/v2/studies"


def module(study: Dict[str, Any], name: str) -> Dict[str, Any]:
    return study.get("protocolSection", {}).get(name, {})


def brief_title(study: Dict[str, Any]) -> str:
    ident = module(study, "identificationModule")
    return ident.get("briefTitle") or ident.get("officialTitle") or ""


def nct_id(study: Dict[str, Any]) -> str:
    return module(study, "identificationModule").get("nctId", "")


def start_year(study: Dict[str, Any]) -> str:
    status = module(study, "statusModule")
    start = status.get("startDateStruct", {}).get("date", "")
    return start[:4] if start else ""


def fetch_query(query: Dict[str, Any]) -> List[Dict[str, str]]:
    params = {
        "query.term": query["query"],
        "pageSize": int(query.get("max_results", 10)),
        "format": "json",
    }
    resp = requests.get(BASE, params=params, timeout=30)
    resp.raise_for_status()
    studies = resp.json().get("studies", [])
    rows: List[Dict[str, str]] = []
    for study in studies:
        nct = nct_id(study)
        title = brief_title(study).strip()
        if not nct or not title:
            continue
        design = module(study, "designModule")
        status = module(study, "statusModule")
        rows.append(
            {
                "id": f"clinicaltrials-{nct}",
                "title_en": title,
                "title_zh": "",
                "year": start_year(study),
                "doi": "",
                "pmid": "",
                "pmcid": "",
                "url": f"https://clinicaltrials.gov/study/{nct}",
                "source": "ClinicalTrials.gov",
                "query": query["name"],
                "include_status": "needs_review",
                "notes": " | ".join(
                    part
                    for part in [
                        status.get("overallStatus", ""),
                        design.get("studyType", ""),
                        "Fetched by scripts/fetch_clinical_trials.py",
                    ]
                    if part
                ),
                "last_checked": str(date.today()),
            }
        )
    return rows


def ensure_log_header() -> None:
    fields = ["date", "source", "query", "result_count", "new_candidates", "included_count", "notes"]
    if not QUERY_LOG.exists() or QUERY_LOG.stat().st_size == 0:
        with QUERY_LOG.open("w", encoding="utf-8", newline="") as f:
            csv.DictWriter(f, fieldnames=fields).writeheader()


def main() -> None:
    load_dotenv(ROOT / ".env")
    queries = json.loads(QUERIES.read_text(encoding="utf-8"))
    keys = load_candidate_keys(CANDIDATES)
    ensure_log_header()
    log_fields = ["date", "source", "query", "result_count", "new_candidates", "included_count", "notes"]

    with QUERY_LOG.open("a", encoding="utf-8", newline="") as lf:
        lw = csv.DictWriter(lf, fieldnames=log_fields)
        for query in queries:
            rows = fetch_query(query)
            new_rows: List[Dict[str, str]] = []
            for row in rows:
                if is_duplicate(row, keys):
                    continue
                new_rows.append(row)
                remember(row, keys)
            append_rows(CANDIDATES, new_rows)
            lw.writerow(
                {
                    "date": str(date.today()),
                    "source": "ClinicalTrials.gov",
                    "query": query["query"],
                    "result_count": len(rows),
                    "new_candidates": len(new_rows),
                    "included_count": 0,
                    "notes": query["name"],
                }
            )
            print(f"{query['name']}: results={len(rows)} new={len(new_rows)}")
            time.sleep(1.0)


if __name__ == "__main__":
    main()
