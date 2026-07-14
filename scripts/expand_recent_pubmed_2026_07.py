from __future__ import annotations

import argparse
import csv
import json
import os
import time
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

import expand_healthspan_pubmed_v05 as base


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
BUILD = ROOT / "build"
REPORT = BUILD / "healthspan_recent_update_2026_07_report.json"
RECENT_TAG = "recent_update_2026_07"


def append_note(row: dict[str, str], note: str) -> bool:
    current = row.get("notes", "").strip()
    if note in current:
        return False
    row["notes"] = f"{current}; {note}".strip("; ")
    return True


def tag_july_ingest(rows: list[dict[str, str]], ingest_start: str) -> set[str]:
    tagged: set[str] = set()
    for row in rows:
        if row.get("last_checked", "") < ingest_start:
            continue
        append_note(row, f"{RECENT_TAG}; July ingest cohort starting {ingest_start}")
        if row.get("id"):
            tagged.add(row["id"])
    return tagged


def recent_query(query: str, start_date: str, end_date: str) -> str:
    return f'({query}) AND ("{start_date}"[Date - Publication] : "{end_date}"[Date - Publication])'


def expand_recent(
    start_date: str,
    end_date: str,
    ingest_start: str,
    retmax_per_topic_tier: int,
    run_date: str,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    existing = base.load_candidates()
    tagged_ids = tag_july_ingest(existing, ingest_start)
    by_id = {row.get("id", ""): dict(row) for row in existing if row.get("id")}
    preexisting_ids = set(by_id)
    pmid_to_id = {row.get("pmid", ""): row.get("id", "") for row in existing if row.get("pmid") and row.get("id")}
    logs: list[dict[str, str]] = []
    added_rows: list[dict[str, str]] = []
    matched_existing: set[str] = set()

    for spec in base.query_specs(retmax_per_topic_tier):
        query = recent_query(spec["query"], start_date, end_date)
        pmids = base.esearch(query, int(spec["max_results"]), sort="pub_date")
        summaries = base.esummary(pmids)
        new_for_query = 0
        tagged_for_query = 0
        for pmid in pmids:
            existing_id = pmid_to_id.get(pmid, "")
            if existing_id:
                row = by_id[existing_id]
                if append_note(row, f"{RECENT_TAG}; publication window {start_date}..{end_date}"):
                    tagged_for_query += 1
                tagged_ids.add(existing_id)
                if existing_id in preexisting_ids:
                    matched_existing.add(existing_id)
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
                "query": f"{spec['name']}__{RECENT_TAG}",
                "include_status": "needs_review",
                "notes": (
                    "Fetched by expand_recent_pubmed_2026_07.py; "
                    f"{RECENT_TAG}; publication-date window={start_date}..{end_date}; "
                    f"source_tier={spec['tier']}."
                ),
                "last_checked": run_date,
            }
            by_id[row["id"]] = row
            pmid_to_id[pmid] = row["id"]
            tagged_ids.add(row["id"])
            added_rows.append(row)
            new_for_query += 1
        logs.append(
            {
                "date": run_date,
                "source": "PubMed",
                "query": query,
                "result_count": str(len(pmids)),
                "new_candidates": str(new_for_query),
                "included_count": "0",
                "notes": f"{spec['name']}__{RECENT_TAG}; tagged_existing={tagged_for_query}",
            }
        )
        print(f"{spec['name']} recent={len(pmids)} new={new_for_query} tagged_existing={tagged_for_query}")
        time.sleep(0.34)

    rows = list(by_id.values())
    base.write_candidates(rows)
    base.append_query_log(logs)
    return rows, {
        "existing": len(existing),
        "added": len(added_rows),
        "tagged_existing_unique": len(matched_existing),
        "recent_tagged_total": len(tagged_ids),
        "total": len(rows),
        "date_window": f"{start_date}..{end_date}",
        "ingest_window_start": ingest_start,
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
    fields = list(base.CANDIDATE_FIELDS)
    with (DATA / "literature_library.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in fields} for row in candidates])


def select_candidates_with_recent_floor(
    rows: list[dict[str, str]],
    target: int,
    recent_floor_per_topic: int,
) -> list[dict[str, str]]:
    base.query_specs(1)
    by_topic: dict[str, list[tuple[int, dict[str, str], dict[str, Any]]]] = defaultdict(list)
    for row in rows:
        if row.get("source") != "PubMed" or not row.get("pmid"):
            continue
        topic = base.infer_topic(row)
        if not topic:
            continue
        by_topic[topic["id"]].append((base.pre_priority(row, topic), row, topic))

    per_topic = target // len(base.TOPICS)
    selected: list[dict[str, str]] = []
    used: set[str] = set()
    for topic in base.TOPICS:
        items = sorted(
            by_topic[topic["id"]],
            key=lambda item: (item[0], item[1].get("year", ""), item[1].get("pmid", "")),
            reverse=True,
        )
        recent_items = [item for item in items if RECENT_TAG in f"{item[1].get('query', '')} {item[1].get('notes', '')}"]
        chosen = recent_items[: min(recent_floor_per_topic, per_topic)]
        chosen_ids = {picked[1].get("id") for picked in chosen}
        for item in items:
            if len(chosen) >= per_topic:
                break
            if item[1].get("id") in chosen_ids:
                continue
            chosen.append(item)
            chosen_ids.add(item[1].get("id"))
        for _, row, mapped_topic in chosen:
            if row.get("id") in used:
                continue
            enriched = dict(row)
            enriched["_topic"] = mapped_topic
            selected.append(enriched)
            used.add(row["id"])

    if len(selected) < target:
        leftovers = [item for items in by_topic.values() for item in items]
        leftovers.sort(
            key=lambda item: (item[0], item[1].get("year", ""), item[1].get("pmid", "")),
            reverse=True,
        )
        for _, row, topic in leftovers:
            if row.get("id") in used:
                continue
            enriched = dict(row)
            enriched["_topic"] = topic
            selected.append(enriched)
            used.add(row["id"])
            if len(selected) >= target:
                break
    return selected[:target]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", default="2026/06/15")
    parser.add_argument("--end-date", default="2026/07/14")
    parser.add_argument("--ingest-start", default="2026-07-01")
    parser.add_argument("--target", type=int, default=5600)
    parser.add_argument("--retmax-per-topic-tier", type=int, default=260)
    parser.add_argument("--recent-floor-per-topic", type=int, default=25)
    parser.add_argument("--skip-fetch", action="store_true")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    run_date = os.environ.get("EVIDENCE_ATLAS_UPDATE_DATE", date.today().isoformat())
    base.TODAY = run_date
    BUILD.mkdir(exist_ok=True)

    if args.skip_fetch:
        rows = base.load_candidates()
        tagged_ids = tag_july_ingest(rows, args.ingest_start)
        base.write_candidates(rows)
        expansion: dict[str, Any] = {
            "existing": len(rows),
            "added": 0,
            "recent_tagged_total": len(tagged_ids),
            "total": len(rows),
            "date_window": f"{args.start_date}..{args.end_date}",
            "ingest_window_start": args.ingest_start,
            "skipped_fetch": True,
        }
    else:
        rows, expansion = expand_recent(
            args.start_date,
            args.end_date,
            args.ingest_start,
            args.retmax_per_topic_tier,
            run_date,
        )

    selected = select_candidates_with_recent_floor(rows, args.target, args.recent_floor_per_topic)
    if len(selected) < args.target:
        raise SystemExit(f"Only {len(selected)} topic-mapped PubMed candidates available; target={args.target}.")
    findings = base.build_findings(selected)
    sync_literature_library()

    topic_counts: dict[str, int] = defaultdict(int)
    recent_topic_counts: dict[str, int] = defaultdict(int)
    recent_selected = 0
    selected_notes = {item.get("id", ""): item.get("notes", "") for item in selected}
    for row in findings:
        topic_counts[row["topic_id"]] += 1
        if RECENT_TAG in f"{row.get('query', '')} {selected_notes.get(row.get('candidate_id', ''), '')}":
            recent_selected += 1
            recent_topic_counts[row["topic_id"]] += 1

    report = {
        "date": run_date,
        "target": args.target,
        "recent_floor_per_topic": args.recent_floor_per_topic,
        "candidate_expansion": expansion,
        "findings_written": len(findings),
        "recent_update_findings_selected": recent_selected,
        "topic_counts": dict(sorted(topic_counts.items())),
        "recent_topic_counts": dict(sorted(recent_topic_counts.items())),
        "query_policy": (
            "PubMed E-utilities with a publication-date window, plus the July ingest cohort. "
            "Each mapped topic reserves a floor for recent records before evidence-priority filling."
        ),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
