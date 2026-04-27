"""Lightweight repository linter."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SOURCE_KEYS = [
    "id", "title_en", "title_zh", "year", "study_type", "species",
    "endpoint_class", "included", "last_checked",
]

REQUIRED_MATRIX_COLUMNS = [
    "paper_id", "year", "topic", "study_type", "species", "primary_endpoint",
    "endpoint_class", "evidence_level", "recommendation_class", "zh_summary", "en_summary", "last_checked",
]


def lint_sources() -> list[str]:
    errors: list[str] = []
    path = ROOT / "data" / "sources.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    seen = set()
    for i, item in enumerate(data):
        for key in REQUIRED_SOURCE_KEYS:
            if key not in item:
                errors.append(f"sources.json[{i}] missing key: {key}")
        paper_id = item.get("id")
        if paper_id in seen:
            errors.append(f"Duplicate source id: {paper_id}")
        seen.add(paper_id)
    return errors


def lint_matrix() -> list[str]:
    errors: list[str] = []
    path = ROOT / "data" / "evidence_matrix.csv"
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        for col in REQUIRED_MATRIX_COLUMNS:
            if col not in fieldnames:
                errors.append(f"evidence_matrix.csv missing column: {col}")
        for row_no, row in enumerate(reader, start=2):
            if not row.get("paper_id"):
                errors.append(f"evidence_matrix.csv row {row_no}: missing paper_id")
            if row.get("evidence_level") not in {"A", "B", "C", "D", "E", "F", ""}:
                errors.append(f"evidence_matrix.csv row {row_no}: invalid evidence_level")
            if row.get("endpoint_class") not in {"H1", "H2", "H3", "H4", "H5", "H6", ""}:
                errors.append(f"evidence_matrix.csv row {row_no}: invalid endpoint_class")
    return errors


def lint_markdown_templates() -> list[str]:
    errors: list[str] = []
    for path in [ROOT / "AGENTS.md", ROOT / "DISCLAIMER.md", ROOT / "README.zh-CN.md"]:
        if not path.exists():
            errors.append(f"Missing required file: {path.relative_to(ROOT)}")
    return errors


def main() -> None:
    errors = []
    errors.extend(lint_sources())
    errors.extend(lint_matrix())
    errors.extend(lint_markdown_templates())

    if errors:
        print("Lint failed:")
        for err in errors:
            print(f"- {err}")
        sys.exit(1)
    print("Lint passed.")


if __name__ == "__main__":
    main()
