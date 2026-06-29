from __future__ import annotations

import argparse
import csv
import json
import os
import time
from collections import defaultdict
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

import expand_healthspan_pubmed_v05 as base


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
BUILD = ROOT / "build"
REPORT = BUILD / "healthspan_recent_update_2026_06_report.json"


def write_candidates(rows: list[dict[str, str]]) -> None:
    base.write_candidates(rows)


def recent_query(query: str, start_date: str, end_date: str) -> str:
    return f'({query}) AND ("{start_date}"[Date - Publication] : "{end_date}"[Date - Publication])'


def expand_recent(
    start_date: str,
    end_date: str,
    retmax_per_topic_tier: int,
    run_date: str,
) -> tuple[list[dict[str, str]], dict[str, object]]:
    existing = base.load_candidates()
    by_id = {row.get("id", ""): dict(row) for row in existing if row.get("id")}
    by_pmid = {row.get("pmid", "") for row in existing if row.get("pmid")}
    logs: list[dict[str, str]] = []
    added_rows: list[dict[str, str]] = []

    for spec in base.query_specs(retmax_per_topic_tier):
        q = recent_query(spec["query"], start_date, end_date)
        pmids = base.esearch(q, int(spec["max_results"]), sort="pub_date")
        summaries = base.esummary(pmids)
        new_for_query = 0
        for pmid in pmids:
            if pmid in by_pmid:
                continue
            item = summaries.get(pmid, {})
            if not item:
                continue
            row = {
                "id": f"pubmed-{pmid}",
                "title_en": base.clean(item.get("title", "")),
                "title_zh": "",
                "year": base.year_from_summary(item),
                "doi": base.doi_from_summary(item),
                "pmid": pmid,
                "pmcid": "",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "source": "PubMed",
                "query": f"{spec['name']}__recent_update_2026_06",
                "include_status": "needs_review",
                "notes": (
                    "Fetched by expand_recent_pubmed_2026_06.py; "
                    f"recent_update publication-date window={start_date}..{end_date}; "
                    f"source_tier={spec['tier']}."
                ),
                "last_checked": run_date,
            }
            by_id[row["id"]] = row
            by_pmid.add(pmid)
            added_rows.append(row)
            new_for_query += 1
        logs.append(
            {
                "date": run_date,
                "source": "PubMed",
                "query": q,
                "result_count": str(len(pmids)),
                "new_candidates": str(new_for_query),
                "included_count": "0",
                "notes": f"{spec['name']}__recent_update_2026_06",
            }
        )
        print(f"{spec['name']} recent={len(pmids)} new={new_for_query}")
        time.sleep(0.34)

    rows = list(by_id.values())
    write_candidates(rows)
    base.append_query_log(logs)
    return rows, {
        "existing": len(existing),
        "added": len(added_rows),
        "total": len(rows),
        "date_window": f"{start_date}..{end_date}",
        "added_sample": [
            {
                "id": row["id"],
                "pmid": row["pmid"],
                "year": row["year"],
                "title_en": row["title_en"],
                "query": row["query"],
            }
            for row in added_rows[:40]
        ],
    }


def sync_literature_library() -> None:
    candidates = base.load_candidates()
    fields = [
        "id",
        "title_en",
        "title_zh",
        "year",
        "doi",
        "pmid",
        "pmcid",
        "url",
        "source",
        "query",
        "include_status",
        "notes",
        "last_checked",
    ]
    with (DATA / "literature_library.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in fields} for row in candidates])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", default="2026/05/01")
    parser.add_argument("--end-date", default="2026/06/02")
    parser.add_argument("--target", type=int, default=3600)
    parser.add_argument("--retmax-per-topic-tier", type=int, default=180)
    parser.add_argument("--skip-fetch", action="store_true")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    run_date = os.environ.get("EVIDENCE_ATLAS_UPDATE_DATE", date.today().isoformat())
    base.TODAY = run_date
    BUILD.mkdir(exist_ok=True)

    if args.skip_fetch:
        rows = base.load_candidates()
        recent_count = sum(1 for row in rows if "recent_update_2026_06" in row.get("query", ""))
        expansion: dict[str, object] = {
            "existing": len(rows) - recent_count,
            "added": recent_count,
            "total": len(rows),
            "date_window": f"{args.start_date}..{args.end_date}",
            "skipped_fetch": True,
        }
    else:
        rows, expansion = expand_recent(args.start_date, args.end_date, args.retmax_per_topic_tier, run_date)

    selected = base.select_candidates(rows, args.target)
    if len(selected) < args.target:
        raise SystemExit(f"Only {len(selected)} topic-mapped PubMed candidates available; target={args.target}.")
    findings = base.build_findings(selected)
    sync_literature_library()

    topic_counts: dict[str, int] = defaultdict(int)
    recent_selected = 0
    for row in findings:
        topic_counts[row["topic_id"]] += 1
        if "recent_update" in row.get("query", ""):
            recent_selected += 1

    report = {
        "date": run_date,
        "target": args.target,
        "candidate_expansion": expansion,
        "findings_written": len(findings),
        "recent_update_findings_selected": recent_selected,
        "topic_counts": dict(sorted(topic_counts.items())),
        "query_policy": "PubMed E-utilities, publication-date window constrained recent update layered on v0.5 topic queries.",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
