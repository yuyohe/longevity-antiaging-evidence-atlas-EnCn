"""Validate the fixed 2026-07 public release package."""

from __future__ import annotations

import csv
import os
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MONTH = "2026-07"
SNAPSHOT_DATE = os.environ.get("EVIDENCE_ATLAS_UPDATE_DATE", "2026-07-14")
BRAND_ZH = "宇多Yul细胞/yulcell"
BRAND_EN = "yulcell"
GITHUB_URL = "https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn"
EXPECTED_CANDIDATES = int(os.environ.get("EXPECTED_CANDIDATES", "15724"))
EXPECTED_FINDINGS = int(os.environ.get("EXPECTED_FINDINGS", "5600"))
EXPECTED_MATRIX = int(os.environ.get("EXPECTED_MATRIX_ROWS", "2800"))
EXPECTED_PUBLIC_TOTAL = EXPECTED_CANDIDATES * 2 + EXPECTED_FINDINGS * 2 + EXPECTED_MATRIX
EXPECTED_FULL_FILES = int(os.environ.get("EXPECTED_FEISHU_FULL_FILES", "5662"))
EXPECTED_LATE_ADDED = int(os.environ.get("EXPECTED_LATE_ADDED", "0"))
EXPECTED_LATE_SELECTED = int(os.environ.get("EXPECTED_LATE_SELECTED", "0"))
EXPECTED_LATE_TOPICS = int(os.environ.get("EXPECTED_LATE_TOPICS", "0"))
RELEASE_FILE = os.environ.get("EVIDENCE_ATLAS_RELEASE_FILE", "mid-july-2026-update.md")
REPORT_FILE = os.environ.get("EVIDENCE_ATLAS_PUBLIC_REPORT_FILE", "mid-july-public-update-2026-07.html")
DASHBOARD_FILE = os.environ.get("EVIDENCE_ATLAS_DASHBOARD_FILE", "yulcell-posting-asset-dashboard-2026-07-14.html")
RELEASE_EXPORT_NAME = os.environ.get("EVIDENCE_ATLAS_RELEASE_EXPORT_NAME", "001-2026-07中旬更新说明.md")

PUBLIC_TABLES = {
    "candidate-sources": (EXPECTED_CANDIDATES, "id"),
    "literature-library": (EXPECTED_CANDIDATES, "library_id"),
    "shortlist-sources": (EXPECTED_FINDINGS, "candidate_id"),
    "evidence-findings": (EXPECTED_FINDINGS, "finding_id"),
    "evidence-matrix": (EXPECTED_MATRIX, "paper_id"),
}

MAIN_IMAGES = [
    "heatmap-dashboard",
    "heatmap-topic-year",
    "heatmap-topic-evidence",
    "ingredient-card-wall",
    "evidence-yield-ingredients",
    "retraction-density",
    "topic-evidence-yield",
]

CRITICAL_TEXT_FILES = [
    ROOT / "README.md",
    ROOT / "README.zh-CN.md",
    ROOT / "content" / "public-reader" / "start-here.md",
    ROOT / "content" / "public-reader" / RELEASE_FILE,
    ROOT / "content" / "public-reader" / "feishu-navigation.md",
    ROOT / "docs" / "feishu-public-assets-2026-07.md",
    ROOT / "docs" / "public-full-data-index-2026-07.md",
    ROOT / "docs" / "yulcell-brand-index.md",
    ROOT / "public-data" / "README.md",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_public_tables(errors: list[str]) -> None:
    total = 0
    for name, (expected_count, id_field) in PUBLIC_TABLES.items():
        path = ROOT / "public-data" / f"{name}-{MONTH}.csv"
        if not path.exists():
            errors.append(f"missing public table: {path.relative_to(ROOT)}")
            continue
        rows = read_csv(path)
        total += len(rows)
        if len(rows) != expected_count:
            errors.append(f"{path.name}: expected {expected_count}, found {len(rows)}")
        identifiers = [row.get(id_field, "").strip() for row in rows]
        if any(not item for item in identifiers):
            errors.append(f"{path.name}: blank {id_field}")
        if len(identifiers) != len(set(identifiers)):
            errors.append(f"{path.name}: duplicate {id_field}")
        for line_number, row in enumerate(rows, 2):
            if row.get("品牌标识") != BRAND_ZH:
                errors.append(f"{path.name}:{line_number}: invalid 品牌标识")
                break
            if row.get("Brand") != BRAND_EN:
                errors.append(f"{path.name}:{line_number}: invalid Brand")
                break
            if "yulcell" not in row.get("SEO关键词", "").lower():
                errors.append(f"{path.name}:{line_number}: missing SEO keyword")
                break
            if row.get("GitHub公开入口") != GITHUB_URL:
                errors.append(f"{path.name}:{line_number}: invalid GitHub link")
                break
    if total != EXPECTED_PUBLIC_TOTAL:
        errors.append(f"public CSV total: expected {EXPECTED_PUBLIC_TOTAL}, found {total}")


def validate_visuals(errors: list[str]) -> None:
    asset_dir = ROOT / "docs" / "assets" / "visual-assets" / MONTH
    expected_main = {f"{name}-{MONTH}.png" for name in MAIN_IMAGES}
    found_main = {path.name for path in asset_dir.glob("*.png")}
    if found_main != expected_main:
        errors.append(f"main visual set mismatch: expected {len(expected_main)}, found {len(found_main)}")

    cards = sorted((asset_dir / "ingredient-cards").glob("*.png"))
    if len(cards) != 50:
        errors.append(f"expected 50 ingredient cards, found {len(cards)}")

    for path in [*(asset_dir / name for name in sorted(expected_main)), *cards]:
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                if image.width < 600 or image.height < 600:
                    errors.append(f"visual too small: {path.relative_to(ROOT)} {image.size}")
        except Exception as exc:  # pragma: no cover - release diagnostics
            errors.append(f"invalid PNG {path.relative_to(ROOT)}: {exc}")


def validate_feishu_manifest(errors: list[str]) -> None:
    path = ROOT / "data" / "feishu_live_tables_2026_07.csv"
    rows = read_csv(path)
    if len(rows) != 9:
        errors.append(f"Feishu manifest: expected 9 tables, found {len(rows)}")
    table_ids: list[str] = []
    for row in rows:
        if row.get("状态") != "active":
            errors.append(f"Feishu table not active: {row.get('表名', '<blank>')}")
        if row.get("更新月份") != MONTH:
            errors.append(f"Feishu table has wrong month: {row.get('表名', '<blank>')}")
        url = row.get("飞书链接", "")
        table_id = parse_qs(urlparse(url).query).get("table", [""])[0]
        if not re.fullmatch(r"tbl[A-Za-z0-9]+", table_id):
            errors.append(f"invalid Feishu table URL: {url}")
        table_ids.append(table_id)
    if len(table_ids) != len(set(table_ids)):
        errors.append("Feishu manifest contains duplicate table IDs")

    navigation = read_csv(ROOT / "data" / "feishu_reader_navigation_2026_07.csv")
    if len(navigation) != 14:
        errors.append(f"Feishu navigation: expected 14 records, found {len(navigation)}")


def validate_text_and_html(errors: list[str]) -> None:
    required_markers = [
        BRAND_ZH,
        SNAPSHOT_DATE,
        f"{EXPECTED_CANDIDATES:,}",
        f"{EXPECTED_FINDINGS:,}",
        f"{EXPECTED_MATRIX:,}",
    ]
    broken_markers = ["�", "瀹囧", "缁嗚優"]
    for path in CRITICAL_TEXT_FILES:
        if not path.exists():
            errors.append(f"missing public text file: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in broken_markers:
            if marker in text:
                errors.append(f"{path.relative_to(ROOT)} contains mojibake marker {marker!r}")
        if re.search(r"\?{3,}", text):
            errors.append(f"{path.relative_to(ROOT)} contains a question-mark run")
    combined = "\n".join(path.read_text(encoding="utf-8") for path in CRITICAL_TEXT_FILES if path.exists())
    for marker in required_markers:
        if marker not in combined:
            errors.append(f"public entry files missing marker: {marker}")

    report = ROOT / "docs" / REPORT_FILE
    dashboard = ROOT / "docs" / DASHBOARD_FILE
    for path, minimum_embedded_pngs in [(report, 7), (dashboard, 57)]:
        if not path.exists():
            errors.append(f"missing self-contained HTML: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        if text.count("data:image/png;base64,") < minimum_embedded_pngs:
            errors.append(f"{path.name}: fewer than {minimum_embedded_pngs} embedded PNGs")
        for marker in [
            BRAND_ZH,
            SNAPSHOT_DATE,
            f"{EXPECTED_CANDIDATES:,}",
            f"{EXPECTED_FINDINGS:,}",
            f"{EXPECTED_MATRIX:,}",
            f"{EXPECTED_PUBLIC_TOTAL:,}",
        ]:
            if marker not in text:
                errors.append(f"{path.name}: missing marker {marker}")


def validate_feishu_packages(errors: list[str]) -> None:
    reader_files = list((ROOT / "build" / "feishu-public-reader").glob("*.md"))
    full_files = list((ROOT / "build" / "feishu-docs").glob("*.md"))
    if len(reader_files) != 15:
        errors.append(f"Feishu reader package: expected 15 files, found {len(reader_files)}")
    if len(full_files) != EXPECTED_FULL_FILES:
        errors.append(f"Feishu full package: expected {EXPECTED_FULL_FILES} files, found {len(full_files)}")
    expected_update = ROOT / "build" / "feishu-public-reader" / RELEASE_EXPORT_NAME
    if not expected_update.exists():
        errors.append(f"Feishu reader package is missing {RELEASE_EXPORT_NAME}")


def validate_study_design_guards(errors: list[str]) -> None:
    candidates = read_csv(ROOT / "data" / "candidate_sources.csv")
    findings = read_csv(ROOT / "data" / "evidence_findings.csv")
    protocols = [row for row in findings if row.get("study_type_draft") == "protocol_or_registered_plan"]
    if not protocols:
        errors.append("study-design guard: no protocol records found")
    if any(row.get("final_evidence_level") != "E" for row in protocols):
        errors.append("study-design guard: protocol record above level E")

    suspect_systematic = [
        row
        for row in findings
        if row.get("study_type_draft") == "systematic_review_or_meta_analysis"
        and not re.search(
            r"systematic review|meta-analysis|meta analysis|umbrella review",
            f"{row.get('title_en', '')} {row.get('publication_types', '')}",
            flags=re.IGNORECASE,
        )
    ]
    suspect_trials = [
        row
        for row in findings
        if row.get("study_type_draft") == "human_randomized_or_clinical_trial"
        and (
            re.search(
                r"published erratum|editorial|comment|letter|news|retracted publication|"
                r"retraction of publication|expression of concern",
                row.get("publication_types", ""),
                flags=re.IGNORECASE,
            )
            or re.search(
                r"^\s*(?:correction|corrigendum|erratum|editorial|comment(?:ary)?|reply|letter)\s*:",
                row.get("title_en", ""),
                flags=re.IGNORECASE,
            )
            or not re.search(
                r"randomized|randomised|controlled trial|clinical trial|randomly assigned",
                f"{row.get('title_en', '')} {row.get('publication_types', '')} {row.get('result_en', '')}",
                flags=re.IGNORECASE,
            )
        )
    ]
    animal_species_mismatches = [
        row
        for row in findings
        if row.get("study_type_draft") == "animal_study"
        and row.get("species_draft") not in {"animal", "mouse"}
    ]
    non_primary_above_e = [
        row
        for row in findings
        if row.get("study_type_draft") == "non_primary_commentary_or_correction"
        and row.get("final_evidence_level") != "E"
    ]
    if suspect_systematic:
        errors.append(f"study-design guard: {len(suspect_systematic)} suspect systematic-review classifications")
    if suspect_trials:
        errors.append(f"study-design guard: {len(suspect_trials)} suspect trial classifications")
    if animal_species_mismatches:
        errors.append(f"study-design guard: {len(animal_species_mismatches)} animal/species mismatches")
    if non_primary_above_e:
        errors.append(f"study-design guard: {len(non_primary_above_e)} non-primary records above level E")

    if EXPECTED_LATE_ADDED:
        late_candidates = [
            row
            for row in candidates
            if row.get("last_checked") == SNAPSHOT_DATE
            and "publication-date window=2026/07/15..2026/07/29" in row.get("notes", "")
        ]
        late_ids = {row.get("id", "") for row in late_candidates}
        late_findings = [row for row in findings if row.get("candidate_id", "") in late_ids]
        late_topics = {row.get("topic_id", "") for row in late_findings if row.get("topic_id")}
        if len(late_candidates) != EXPECTED_LATE_ADDED:
            errors.append(f"late-July candidates: expected {EXPECTED_LATE_ADDED}, found {len(late_candidates)}")
        if len(late_findings) != EXPECTED_LATE_SELECTED:
            errors.append(f"late-July selected findings: expected {EXPECTED_LATE_SELECTED}, found {len(late_findings)}")
        if len(late_topics) != EXPECTED_LATE_TOPICS:
            errors.append(f"late-July topic coverage: expected {EXPECTED_LATE_TOPICS}, found {len(late_topics)}")


def main() -> None:
    errors: list[str] = []
    validate_public_tables(errors)
    validate_visuals(errors)
    validate_feishu_manifest(errors)
    validate_text_and_html(errors)
    validate_feishu_packages(errors)
    validate_study_design_guards(errors)
    if errors:
        print("July public release validation failed:")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)
    print("July public release validation passed.")
    print(
        f"Validated: {EXPECTED_PUBLIC_TOTAL:,} CSV rows, 57 PNGs, 9 Feishu tables, "
        f"15 reader files, {EXPECTED_FULL_FILES:,} full files."
    )


if __name__ == "__main__":
    main()
