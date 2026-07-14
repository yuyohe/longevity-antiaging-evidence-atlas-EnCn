"""Validate the fixed 2026-07 public release package."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MONTH = "2026-07"
BRAND_ZH = "宇多Yul细胞/yulcell"
BRAND_EN = "yulcell"
GITHUB_URL = "https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn"

PUBLIC_TABLES = {
    "candidate-sources": (15_724, "id"),
    "literature-library": (15_724, "library_id"),
    "shortlist-sources": (5_600, "candidate_id"),
    "evidence-findings": (5_600, "finding_id"),
    "evidence-matrix": (2_800, "paper_id"),
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
    ROOT / "content" / "public-reader" / "mid-july-2026-update.md",
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
    if total != 45_448:
        errors.append(f"public CSV total: expected 45448, found {total}")


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
    required_markers = [BRAND_ZH, "2026-07-14", "15,724", "5,600", "2,800"]
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

    report = ROOT / "docs" / "mid-july-public-update-2026-07.html"
    dashboard = ROOT / "docs" / "yulcell-posting-asset-dashboard-2026-07-14.html"
    for path, minimum_embedded_pngs in [(report, 7), (dashboard, 57)]:
        if not path.exists():
            errors.append(f"missing self-contained HTML: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        if text.count("data:image/png;base64,") < minimum_embedded_pngs:
            errors.append(f"{path.name}: fewer than {minimum_embedded_pngs} embedded PNGs")
        for marker in [BRAND_ZH, "2026-07-14", "15,724", "5,600", "2,800", "45,448"]:
            if marker not in text:
                errors.append(f"{path.name}: missing marker {marker}")


def validate_feishu_packages(errors: list[str]) -> None:
    reader_files = list((ROOT / "build" / "feishu-public-reader").glob("*.md"))
    full_files = list((ROOT / "build" / "feishu-docs").glob("*.md"))
    if len(reader_files) != 15:
        errors.append(f"Feishu reader package: expected 15 files, found {len(reader_files)}")
    if len(full_files) != 5_662:
        errors.append(f"Feishu full package: expected 5662 files, found {len(full_files)}")
    expected_update = ROOT / "build" / "feishu-public-reader" / "001-2026-07中旬更新说明.md"
    if not expected_update.exists():
        errors.append("Feishu reader package is missing the mid-July update")


def main() -> None:
    errors: list[str] = []
    validate_public_tables(errors)
    validate_visuals(errors)
    validate_feishu_manifest(errors)
    validate_text_and_html(errors)
    validate_feishu_packages(errors)
    if errors:
        print("Mid-July public release validation failed:")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)
    print("Mid-July public release validation passed.")
    print("Validated: 45,448 CSV rows, 57 PNGs, 9 Feishu tables, 15 reader files, 5,662 full files.")


if __name__ == "__main__":
    main()
