"""Repair DOI/PMCID fields from official PubMed summaries after XML path audit."""

from __future__ import annotations

import csv
import difflib
import json
import os
import re
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

import expand_healthspan_pubmed_v05 as pubmed


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
BUILD = ROOT / "build"
CANDIDATES = DATA / "candidate_sources.csv"
FINDINGS = DATA / "evidence_findings.csv"
REPORT = DATA / "pubmed_identifier_repair_report_2026_08.json"
CACHE = BUILD / "pubmed_identifier_summary_cache_2026_08.json"


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), reader.fieldnames or []


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in fields} for row in rows])


def normalize_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def article_ids(summary: dict[str, Any]) -> dict[str, str]:
    return {
        str(item.get("idtype", "")).lower(): str(item.get("value", "")).strip()
        for item in summary.get("articleids", [])
        if item.get("idtype") and item.get("value")
    }


def main() -> None:
    load_dotenv(ROOT / ".env")
    candidates, candidate_fields = read_csv(CANDIDATES)
    findings, finding_fields = read_csv(FINDINGS)
    candidates_by_id = {row.get("id", ""): row for row in candidates if row.get("id")}
    pubmed_rows = [row for row in findings if row.get("source") == "PubMed" and row.get("pmid")]
    pmids = list(dict.fromkeys(row["pmid"] for row in pubmed_rows))

    BUILD.mkdir(parents=True, exist_ok=True)
    if CACHE.exists():
        summaries = json.loads(CACHE.read_text(encoding="utf-8"))
        print(f"loaded_cached_pubmed_summaries={len(summaries)}")
    else:
        summaries: dict[str, dict[str, Any]] = {}
        delay = 0.12 if os.getenv("NCBI_API_KEY") else 0.36
        for start in range(0, len(pmids), 200):
            batch = pmids[start : start + 200]
            summaries.update(pubmed.esummary(batch))
            print(f"official_pubmed_summaries={min(start + len(batch), len(pmids))}/{len(pmids)}")
            time.sleep(delay)
        CACHE.write_text(json.dumps(summaries, ensure_ascii=False), encoding="utf-8")

    missing = [pmid for pmid in pmids if not summaries.get(pmid)]
    title_mismatches: list[dict[str, str]] = []
    accepted_title_variants = 0
    for row in pubmed_rows:
        summary = summaries.get(row["pmid"], {})
        official_title = pubmed.clean(summary.get("title", ""))
        if official_title and normalize_title(official_title) != normalize_title(row.get("title_en", "")):
            ratio = difflib.SequenceMatcher(
                None,
                normalize_title(official_title),
                normalize_title(row.get("title_en", "")),
            ).ratio()
            if ratio >= 0.97:
                accepted_title_variants += 1
            else:
                title_mismatches.append(
                    {
                        "pmid": row["pmid"],
                        "finding_title": row.get("title_en", ""),
                        "official_title": official_title,
                    }
                )
    if missing or title_mismatches:
        print(json.dumps(title_mismatches[:10], ensure_ascii=False, indent=2))
        raise RuntimeError(
            f"Identifier repair stopped before writes: missing={len(missing)}, "
            f"title_mismatches={len(title_mismatches)}"
        )

    finding_doi_corrected = 0
    finding_pmcid_corrected = 0
    candidate_doi_corrected = 0
    candidate_pmcid_corrected = 0
    for row in pubmed_rows:
        ids = article_ids(summaries[row["pmid"]])
        official_doi = ids.get("doi", "")
        official_pmcid = ids.get("pmc", "")
        if row.get("doi", "").lower() != official_doi.lower():
            finding_doi_corrected += 1
        if row.get("pmcid", "").upper() != official_pmcid.upper():
            finding_pmcid_corrected += 1
        row["doi"] = official_doi
        row["pmcid"] = official_pmcid
        if row.get("evidence_source_depth") != "metadata_only":
            row["evidence_source_depth"] = (
                "abstract_plus_open_pmc_available" if official_pmcid else "abstract_only"
            )

        candidate = candidates_by_id.get(row.get("candidate_id", ""))
        if candidate:
            if candidate.get("doi", "").lower() != official_doi.lower():
                candidate_doi_corrected += 1
            if candidate.get("pmcid", "").upper() != official_pmcid.upper():
                candidate_pmcid_corrected += 1
            candidate["doi"] = official_doi
            candidate["pmcid"] = official_pmcid
            row["authority_signal_draft"] = pubmed.authority_signal(
                candidate,
                ids,
                [part.strip() for part in row.get("publication_types", "").split(";") if part.strip()],
                row.get("journal", ""),
                row.get("evidence_source_depth", "abstract_only"),
            )

    write_csv(CANDIDATES, candidates, candidate_fields)
    write_csv(FINDINGS, findings, finding_fields)
    report = {
        "date": os.getenv("EVIDENCE_ATLAS_UPDATE_DATE", "2026-08-09"),
        "official_source": "NCBI PubMed E-utilities esummary",
        "pubmed_findings_checked": len(pubmed_rows),
        "unique_pmids_checked": len(pmids),
        "missing_official_summaries": len(missing),
        "title_mismatches": len(title_mismatches),
        "accepted_minor_title_variants": accepted_title_variants,
        "finding_doi_corrected": finding_doi_corrected,
        "finding_pmcid_corrected": finding_pmcid_corrected,
        "candidate_doi_corrected": candidate_doi_corrected,
        "candidate_pmcid_corrected": candidate_pmcid_corrected,
        "status": "passed",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
