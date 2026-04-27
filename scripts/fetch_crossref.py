"""Fetch candidate papers from Crossref.

Crossref is used here as a discovery layer, not as the final evidence source.
Rows are appended to data/candidate_sources.csv for later manual screening.
"""

from __future__ import annotations

import csv
import json
import time
from datetime import date
from pathlib import Path
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

from candidate_utils import CANDIDATE_FIELDS, append_rows, is_duplicate, load_candidate_keys, remember

ROOT = Path(__file__).resolve().parents[1]
QUERIES = ROOT / "queries" / "crossref.json"
CANDIDATES = ROOT / "data" / "candidate_sources.csv"
QUERY_LOG = ROOT / "data" / "query_log.csv"
BASE = "https://api.crossref.org/works"


def first(values: Any) -> str:
    if isinstance(values, list) and values:
        return str(values[0])
    if values is None:
        return ""
    return str(values)


def item_year(item: Dict[str, Any]) -> str:
    for key in ("published-print", "published-online", "published", "created"):
        parts = item.get(key, {}).get("date-parts", [])
        if parts and parts[0]:
            return str(parts[0][0])
    return ""


def fetch_query(query: Dict[str, Any]) -> List[Dict[str, str]]:
    params = {
        "query.bibliographic": query["query"],
        "rows": int(query.get("max_results", 20)),
        "select": "DOI,title,URL,published,published-print,published-online,created,type,container-title",
        "sort": "relevance",
    }
    resp = requests.get(BASE, params=params, timeout=30)
    resp.raise_for_status()
    items = resp.json().get("message", {}).get("items", [])
    rows: List[Dict[str, str]] = []
    for item in items:
        doi = str(item.get("DOI", "")).strip()
        url = item.get("URL", "")
        title = first(item.get("title")).strip()
        if not title:
            continue
        rows.append(
            {
                "id": f"crossref-{doi.lower()}" if doi else f"crossref-{abs(hash(url or title))}",
                "title_en": title,
                "title_zh": "",
                "year": item_year(item),
                "doi": doi,
                "pmid": "",
                "pmcid": "",
                "url": url,
                "source": "Crossref",
                "query": query["name"],
                "include_status": "needs_review",
                "notes": "Fetched by scripts/fetch_crossref.py",
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
                    "source": "Crossref",
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
