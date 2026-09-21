"""Validate the bounded late-September 2026 public release and online evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from PIL import Image

import archive_public_snapshots as snapshot_archive
import curate_mid_august_2026 as curation


ROOT = Path(__file__).resolve().parents[1]
MONTH = "2026-09"
SNAPSHOT_DATE = "2026-09-21"
BRAND_ZH = "宇多Yul细胞/yulcell"
BRAND_EN = "yulcell"
GITHUB_URL = "https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn"
EXPECTED = {
    "candidate-sources": (11141, "id"),
    "literature-library": (11141, "library_id"),
    "shortlist-sources": (2339, "candidate_id"),
    "evidence-findings": (2339, "finding_id"),
    "evidence-matrix": (1500, "paper_id"),
}
EXPECTED_TOTAL = 28460
MAIN_IMAGES = {
    "heatmap-dashboard-2026-09.png",
    "heatmap-topic-year-2026-09.png",
    "heatmap-topic-evidence-2026-09.png",
    "ingredient-card-wall-2026-09.png",
    "evidence-yield-ingredients-2026-09.png",
    "retraction-density-2026-09.png",
    "topic-evidence-yield-2026-09.png",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_public_tables(errors: list[str]) -> None:
    total = 0
    for name, (expected_count, id_field) in EXPECTED.items():
        path = ROOT / "public-data" / f"{name}-{MONTH}.csv"
        rows = read_csv(path)
        total += len(rows)
        if len(rows) != expected_count:
            errors.append(f"{path.name}: expected {expected_count}, found {len(rows)}")
        identifiers = [row.get(id_field, "").strip() for row in rows]
        if any(not value for value in identifiers) or len(identifiers) != len(set(identifiers)):
            errors.append(f"{path.name}: blank or duplicate {id_field}")
        if any(
            row.get("品牌标识") != BRAND_ZH
            or row.get("Brand") != BRAND_EN
            or "yulcell" not in row.get("SEO关键词", "").lower()
            or row.get("GitHub公开入口") != GITHUB_URL
            for row in rows
        ):
            errors.append(f"{path.name}: incomplete brand or GitHub coverage")
    if total != EXPECTED_TOTAL:
        errors.append(f"public CSV total: expected {EXPECTED_TOTAL}, found {total}")


def validate_active_curation(errors: list[str]) -> None:
    candidates = read_csv(ROOT / "data" / "candidate_sources.csv")
    findings = read_csv(ROOT / "data" / "evidence_findings.csv")
    matrix = read_csv(ROOT / "data" / "evidence_matrix.csv")
    candidate_by_id = {row["id"]: row for row in candidates}

    def duplicate_count(rows: list[dict[str, str]], field: str, normalizer=lambda value: value.strip().lower()) -> int:
        values = [normalizer(row.get(field, "")) for row in rows if normalizer(row.get(field, ""))]
        return len(values) - len(set(values))

    for field in ["id", "pmid", "doi"]:
        if duplicate_count(candidates, field):
            errors.append(f"active candidates contain duplicate {field}")
    normalized_titles = [
        curation.normalize_title(row.get("title_en", ""))
        for row in candidates
        if len(curation.normalize_title(row.get("title_en", ""))) >= 24
    ]
    if len(normalized_titles) != len(set(normalized_titles)):
        errors.append("active candidates contain duplicate sufficiently specific normalized titles")

    rejected_types = {"protocol_or_registered_plan", "non_primary_commentary_or_correction"}
    rejected = [row for row in findings if row.get("study_type_draft") in rejected_types]
    if rejected:
        errors.append(f"active findings contain {len(rejected)} protocol/non-primary rows")
    rejected_by_current_policy = [row for row in findings if curation.finding_rejection_reason(row)]
    if rejected_by_current_policy:
        counts = Counter(curation.finding_rejection_reason(row) for row in rejected_by_current_policy)
        errors.append(f"active findings violate current curation policy: {dict(sorted(counts.items()))}")
    nonhuman_mismatches = [
        row for row in findings
        if row.get("species_draft") in {"mouse", "animal", "cell"}
        and row.get("topic_id") not in curation.PRECLINICAL_TOPICS
    ]
    if nonhuman_mismatches:
        errors.append(f"active findings contain {len(nonhuman_mismatches)} nonhuman/human-topic mismatches")

    doi_mismatches = []
    for row in findings:
        candidate = candidate_by_id.get(row.get("candidate_id", ""))
        if not candidate:
            errors.append(f"finding without active candidate: {row.get('candidate_id')}")
            continue
        if candidate.get("doi") and row.get("doi") and candidate["doi"].lower() != row["doi"].lower():
            doi_mismatches.append(row)
    if doi_mismatches:
        errors.append(f"candidate/finding DOI mismatches: {len(doi_mismatches)}")

    candidate_topics = Counter(curation.topic_for_candidate(row, {})["id"] for row in candidates if curation.topic_for_candidate(row, {}))
    finding_topics = Counter(row.get("topic_id", "") for row in findings)
    matrix_topics = Counter(row.get("topic", "") for row in matrix)
    if max(candidate_topics.values(), default=0) > 600:
        errors.append("candidate topic cap exceeds 600")
    if max(finding_topics.values(), default=0) > 200:
        errors.append("finding topic cap exceeds 200")
    if len(matrix) != 1500 or max(matrix_topics.values(), default=0) > 100:
        errors.append("matrix does not satisfy 1,500 total / 100 per-topic caps")

    queue = read_csv(ROOT / "data" / "core_review_queue.csv")
    queue_topics = Counter(row.get("topic_id", "") for row in queue)
    if len(queue) != 54 or max(queue_topics.values(), default=0) > 3:
        errors.append("core review queue does not satisfy 54 total / 3 per-topic caps")


def validate_metrics_and_retirements(errors: list[str]) -> None:
    metrics = json.loads((ROOT / "data" / "curation_release_metrics_2026_09_late.json").read_text(encoding="utf-8"))
    current_metrics = json.loads((ROOT / "data" / "curation_release_metrics_2026_09.json").read_text(encoding="utf-8"))
    if current_metrics != metrics:
        errors.append("current September metrics alias is not synchronized with late-September metrics")
    candidate_retired = read_csv(ROOT / "data" / "archive" / "candidate_retirement_2026-09-late.csv")
    finding_retired = read_csv(ROOT / "data" / "archive" / "finding_retirement_2026-09-late.csv")
    expected_metrics = {
        "release": "2026-09-late-curated",
        "date": SNAPSHOT_DATE,
        "search": {
            "date_window": "2026/09/14..2026/09/21",
            "queries": 20,
            "unique_pubmed_matches": 386,
            "new_rows": 379,
            "matched_existing": 7,
        },
        "before": {"candidate_records": 11132, "finding_records": 2291},
        "after": {
            "candidate_records": 11141,
            "finding_records": 2339,
            "recent_candidates_retained": 116,
            "recent_findings_retained": 62,
        },
    }
    for key in ["release", "date", "search", "before", "after"]:
        if metrics.get(key) != expected_metrics[key]:
            errors.append(f"late-September release metrics mismatch: {key}")
    if len(candidate_retired) != metrics["retired"]["candidate_decisions"]:
        errors.append("candidate retirement count differs from release metrics")
    if len(finding_retired) != metrics["retired"]["finding_decisions"]:
        errors.append("finding retirement count differs from release metrics")
    if dict(sorted(Counter(row["reason"] for row in candidate_retired).items())) != metrics["retired"]["candidate_reasons"]:
        errors.append("candidate retirement reasons differ from release metrics")
    if dict(sorted(Counter(row["reason"] for row in finding_retired).items())) != metrics["retired"]["finding_reasons"]:
        errors.append("finding retirement reasons differ from release metrics")

    repair = json.loads((ROOT / "data" / "pubmed_identifier_repair_report_2026_09.json").read_text(encoding="utf-8"))
    if repair.get("status") != "passed" or repair.get("pubmed_findings_checked") != 2339:
        errors.append("PubMed identifier repair did not pass for all findings")
    if repair.get("missing_official_summaries") or repair.get("title_mismatches"):
        errors.append("PubMed identifier repair has missing records or title mismatches")


def validate_visuals_and_reports(errors: list[str]) -> None:
    asset_dir = ROOT / "docs" / "assets" / "visual-assets" / MONTH
    found_main = {path.name for path in asset_dir.glob("*.png")}
    cards = sorted((asset_dir / "ingredient-cards").glob("*.png"))
    if found_main != MAIN_IMAGES or len(cards) != 50:
        errors.append(f"visual set mismatch: main={len(found_main)}, cards={len(cards)}")
    for path in [*(asset_dir / name for name in sorted(MAIN_IMAGES)), *cards]:
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                if image.width < 600 or image.height < 600:
                    errors.append(f"visual too small: {path.relative_to(ROOT)} {image.size}")
        except Exception as exc:
            errors.append(f"invalid PNG {path.relative_to(ROOT)}: {exc}")

    critical_files = [
        ROOT / "README.md",
        ROOT / "README.zh-CN.md",
        ROOT / "public-data" / "README.md",
        ROOT / "content" / "public-reader" / "late-september-2026-update.md",
        ROOT / "docs" / "feishu-public-assets-2026-09.md",
        ROOT / "docs" / "yulcell-brand-index.md",
        ROOT / "docs" / "data-retention-and-curation-policy.md",
    ]
    for path in critical_files:
        text = path.read_text(encoding="utf-8")
        if BRAND_ZH not in text:
            errors.append(f"{path.relative_to(ROOT)} lacks release identity marker")
        if "�" in text or "瀹囧" in text or re.search(r"\?{3,}", text):
            errors.append(f"{path.relative_to(ROOT)} contains mojibake/question-mark runs")

    report = (ROOT / "docs" / "late-september-public-update-2026-09.html").read_text(encoding="utf-8")
    dashboard = (ROOT / "docs" / "yulcell-posting-asset-dashboard-2026-09-21.html").read_text(encoding="utf-8")
    if report.count("data:image/png;base64,") != 57 or report.count("button type=\"button\" class=\"download\"") != 57:
        errors.append("self-contained report does not embed 57 downloadable PNGs")
    if dashboard.count("data:image/png;base64,") < 57:
        errors.append("posting dashboard embeds fewer than 57 PNGs")

    monthly = (ROOT / "content" / "public-reader" / "monthly-update-2026-09.md").read_text(encoding="utf-8")
    if "已满额主题以替换为主" not in monthly or "新增候选 0" in monthly or "findings 扩到" in monthly:
        errors.append("monthly update still uses expansion-only wording")


def validate_feishu(errors: list[str], *, require_online_audit: bool) -> None:
    manifest = read_csv(ROOT / "data" / "feishu_live_tables_2026_09.csv")
    registry = read_csv(ROOT / "data" / "feishu_table_registry.csv")
    navigation = read_csv(ROOT / "data" / "feishu_reader_navigation_2026_09.csv")
    if len(manifest) != 9 or len(registry) != 9 or len(navigation) != 14:
        errors.append("Feishu manifest/registry/navigation counts are not 9/9/14")
    table_ids = []
    manifest_counts = {}
    for row in manifest:
        table_id = parse_qs(urlparse(row.get("飞书链接", "")).query).get("table", [""])[0]
        table_ids.append(table_id)
        if row.get("状态") != "active" or row.get("更新月份") != MONTH:
            errors.append(f"inactive or wrong-month Feishu row: {row.get('表名')}")
        if not row.get("表名", "").startswith("宇多Yul细胞_当前") or re.search(r"_2026-\d{2}$", row.get("表名", "")):
            errors.append(f"Feishu table is not month-neutral: {row.get('表名')}")
        manifest_counts[row.get("表名", "")] = int(row.get("记录数", "0"))
    if len(table_ids) != len(set(table_ids)) or any(not re.fullmatch(r"tbl[A-Za-z0-9]+", value) for value in table_ids):
        errors.append("Feishu manifest has invalid or duplicate table IDs")
    registry_counts = {row.get("stable_name", ""): int(row.get("expected_rows", "0")) for row in registry}
    if manifest_counts != registry_counts:
        errors.append("Feishu manifest and stable registry expected counts differ")

    if require_online_audit:
        online_report = ROOT / "build" / "feishu_online_audit_2026_09.json"
        if not online_report.exists():
            errors.append("missing Feishu online audit report")
        else:
            audit = json.loads(online_report.read_text(encoding="utf-8"))
            if audit.get("status") != "passed" or len(audit.get("tables", [])) != 9:
                errors.append("Feishu online audit did not pass 9/9 tables")
            if audit.get("snapshot_date") != SNAPSHOT_DATE:
                errors.append("Feishu online audit has an outdated snapshot date")
            actual_counts = {row["table_name"]: row["actual_records"] for row in audit.get("tables", [])}
            if actual_counts != manifest_counts:
                errors.append("Feishu online audited counts differ from current manifest")


def validate_archives_and_automation(errors: list[str]) -> None:
    archive_dir = ROOT / "archive" / "public-data"
    checksum_lines = (archive_dir / "SHA256SUMS.txt").read_text(encoding="ascii").splitlines()
    expected_hashes = {line.split()[1]: line.split()[0] for line in checksum_lines if line.strip()}
    for label in ["2026-05", "2026-06", "2026-07", "2026-08-mid", "2026-08-end", "2026-09-mid"]:
        archive = archive_dir / f"public-data-{label}.zip"
        manifest = snapshot_archive.verify_archive(archive)
        if len(manifest) != 5 or expected_hashes.get(archive.name) != sha256(archive):
            errors.append(f"historical archive verification failed: {archive.name}")
        if label in {"2026-05", "2026-06", "2026-07"} and list((ROOT / "public-data").glob(f"*-{label}.csv")):
            errors.append(f"archived source CSVs still unpacked for {label}")
    for month in ["2026-08", "2026-09"]:
        if len(list((ROOT / "public-data").glob(f"*-{month}.csv"))) != 5:
            errors.append(f"current/previous snapshot does not have five unpacked CSVs: {month}")

    workflow = (ROOT / ".github" / "workflows" / "fetch-pubmed.yml").read_text(encoding="utf-8")
    if (
        "fetch_pubmed_intake.py" not in workflow
        or "gh pr create" not in workflow
        or re.search(r"git push\s+(?:origin\s+)?(?:main|HEAD:main)\b", workflow)
    ):
        errors.append("weekly PubMed workflow is not intake-PR-only")


def validate_feishu_packages(errors: list[str]) -> None:
    reader_files = list((ROOT / "build" / "feishu-public-reader").glob("*.md"))
    full_files = list((ROOT / "build" / "feishu-docs").glob("*.md"))
    if len(reader_files) != 15 or len(full_files) != 2401:
        errors.append(f"Feishu export package count mismatch: reader={len(reader_files)}, full={len(full_files)}")
    if not (ROOT / "build" / "feishu-public-reader" / "001-2026-09下旬精编更新说明.md").exists():
        errors.append("Feishu reader package lacks the late-September curated release guide")


def validate_refreshed_sources(errors: list[str]) -> None:
    findings = read_csv(ROOT / "data" / "evidence_findings.csv")
    sources = json.loads((ROOT / "data" / "sources.json").read_text(encoding="utf-8"))
    if {r["id"] for r in sources} != {r["candidate_id"] for r in findings}:
        errors.append("source index is not synchronized with active findings")
    matrix = read_csv(ROOT / "data" / "evidence_matrix.csv")
    if {r["id"] for r in sources if r["included"]} != {r["paper_id"] for r in matrix}:
        errors.append("source inclusion flags differ from the matrix")
    queries = read_csv(ROOT / "data" / "retraction_risk_queries_20y.csv")
    retractions = read_csv(ROOT / "data" / "retraction_risk_summary_20y.csv")
    if len(queries) != 117 or len(retractions) != 117 or any(r.get("error") for r in queries):
        errors.append("117-target retraction refresh is incomplete")
    if any(r["last_checked"] != SNAPSHOT_DATE for r in queries + retractions):
        errors.append("retraction source dates are outdated")
    if any(int(r["retrieved_publication_rows"]) != int(r["pubmed_retracted_count_20y"]) for r in retractions):
        errors.append("retracted publication detail coverage is incomplete")
    retracted_pmids = {r["pmid"] for r in read_csv(ROOT / "data" / "retracted_publications_20y.csv")}
    if retracted_pmids.intersection(r["pmid"] for r in findings):
        errors.append("known retracted publications remain in active findings")
    for card in read_csv(ROOT / "data" / "social_cards_top50_ingredients.csv"):
        if card["retraction_checked_date"] != SNAPSHOT_DATE or not card["evidence_review_date"]:
            errors.append(f"ingredient source-date mismatch: {card['card_id']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-only",
        action="store_true",
        help="Validate tracked GitHub assets without requiring ignored local Feishu audit/export artifacts.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    errors: list[str] = []
    validate_public_tables(errors)
    validate_active_curation(errors)
    validate_refreshed_sources(errors)
    validate_metrics_and_retirements(errors)
    validate_visuals_and_reports(errors)
    validate_feishu(errors, require_online_audit=not args.source_only)
    validate_archives_and_automation(errors)
    if not args.source_only:
        validate_feishu_packages(errors)
    if errors:
        print("September public release validation failed:")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)
    print("September public release validation passed.")
    scope = (
        "tracked Feishu manifests"
        if args.source_only
        else "9 audited Feishu tables and export packages"
    )
    print(
        "Validated: 28,460 public CSV rows, bounded active layers, 57 PNGs, "
        f"{scope}, identifier repair, and archives."
    )


if __name__ == "__main__":
    main()
