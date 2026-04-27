"""Fetch PubMed candidate papers using NCBI E-utilities.

This is a lightweight starter script. It writes candidate rows to
`data/candidate_sources.csv` and logs searches to `data/query_log.csv`.

Usage:
    python scripts/fetch_pubmed.py
"""

from __future__ import annotations

import csv
import json
import os
import time
from datetime import date
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

from candidate_utils import CANDIDATE_FIELDS, ensure_csv_header, is_duplicate, load_candidate_keys, remember

ROOT = Path(__file__).resolve().parents[1]
QUERIES = ROOT / "queries" / "pubmed.json"
CANDIDATES = ROOT / "data" / "candidate_sources.csv"
QUERY_LOG = ROOT / "data" / "query_log.csv"
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def request_json(endpoint: str, params: Dict[str, str]) -> Dict:
    params = dict(params)
    params["retmode"] = "json"
    email = os.getenv("NCBI_EMAIL")
    api_key = os.getenv("NCBI_API_KEY")
    if email:
        params["email"] = email
    if api_key:
        params["api_key"] = api_key
    url = f"{BASE}/{endpoint}?{urlencode(params)}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def esearch(query: str, max_results: int) -> List[str]:
    data = request_json("esearch.fcgi", {"db": "pubmed", "term": query, "retmax": str(max_results), "sort": "pub+date"})
    return data.get("esearchresult", {}).get("idlist", [])


def esummary(pmids: List[str]) -> Dict:
    if not pmids:
        return {"result": {}}
    return request_json("esummary.fcgi", {"db": "pubmed", "id": ",".join(pmids)})


def main() -> None:
    load_dotenv(ROOT / ".env")
    queries = json.loads(QUERIES.read_text(encoding="utf-8"))

    log_fields = ["date", "source", "query", "result_count", "new_candidates", "included_count", "notes"]
    ensure_csv_header(CANDIDATES, CANDIDATE_FIELDS)
    ensure_csv_header(QUERY_LOG, log_fields)
    existing_keys = load_candidate_keys(CANDIDATES)

    with CANDIDATES.open("a", encoding="utf-8", newline="") as cf, QUERY_LOG.open("a", encoding="utf-8", newline="") as lf:
        cw = csv.DictWriter(cf, fieldnames=CANDIDATE_FIELDS)
        lw = csv.DictWriter(lf, fieldnames=log_fields)

        for q in queries:
            name = q["name"]
            query = q["query"]
            max_results = int(q.get("max_results", 20))
            pmids = esearch(query, max_results)
            summary = esummary(pmids)
            new_count = 0

            for pmid in pmids:
                item = summary.get("result", {}).get(pmid, {})
                title = item.get("title", "").strip()
                year = str(item.get("pubdate", "")[:4])
                doi = ""
                for aid in item.get("articleids", []):
                    if aid.get("idtype") == "doi":
                        doi = aid.get("value", "")
                row = {
                    "id": f"pubmed-{pmid}",
                    "title_en": title,
                    "title_zh": "",
                    "year": year,
                    "doi": doi,
                    "pmid": pmid,
                    "pmcid": "",
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "source": "PubMed",
                    "query": name,
                    "include_status": "needs_review",
                    "notes": "Fetched by scripts/fetch_pubmed.py",
                    "last_checked": str(date.today()),
                }
                if is_duplicate(row, existing_keys):
                    continue
                cw.writerow(row)
                remember(row, existing_keys)
                new_count += 1

            lw.writerow({
                "date": str(date.today()),
                "source": "PubMed",
                "query": query,
                "result_count": len(pmids),
                "new_candidates": new_count,
                "included_count": 0,
                "notes": name,
            })
            time.sleep(0.35)
            print(f"{name}: results={len(pmids)} new={new_count}")


if __name__ == "__main__":
    main()
