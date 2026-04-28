"""Validate v0.1 public draft safety and completeness."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT_NOTICE_ZH = "草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。"
DRAFT_NOTICE_EN = "Draft status: automatically prepared; not fully reviewed; not medical advice."


def errors_for_markdown() -> list[str]:
    errors: list[str] = []
    for folder in [ROOT / "content" / "papers", ROOT / "content" / "topics"]:
        for path in folder.glob("*.md"):
            if path.name.startswith("_"):
                continue
            text = path.read_text(encoding="utf-8")
            if DRAFT_NOTICE_ZH not in text:
                errors.append(f"{path.relative_to(ROOT)} missing Chinese draft notice")
            if DRAFT_NOTICE_EN not in text:
                errors.append(f"{path.relative_to(ROOT)} missing English draft notice")
            if folder.name == "papers":
                for marker in ["Unsupported Claim", "Overinterpretation Risk", "Medical supervision needed"]:
                    if marker not in text:
                        errors.append(f"{path.relative_to(ROOT)} missing {marker}")
    return errors


def errors_for_data() -> list[str]:
    errors: list[str] = []
    findings = list(csv.DictReader((ROOT / "data" / "evidence_findings.csv").open(encoding="utf-8-sig")))
    shortlist = list(csv.DictReader((ROOT / "data" / "shortlist_sources.csv").open(encoding="utf-8-sig")))
    topics = list(csv.DictReader((ROOT / "data" / "topics.csv").open(encoding="utf-8-sig")))
    matrix = list(csv.DictReader((ROOT / "data" / "evidence_matrix.csv").open(encoding="utf-8-sig")))
    if len(findings) != 60:
        errors.append(f"expected 60 findings, found {len(findings)}")
    if len(shortlist) != 60:
        errors.append(f"expected 60 shortlist rows, found {len(shortlist)}")
    if len(topics) != 20:
        errors.append(f"expected 20 topics, found {len(topics)}")
    if not 20 <= len(matrix) <= 30:
        errors.append(f"expected 20-30 evidence matrix rows, found {len(matrix)}")
    for row in findings:
        for field in ["result_en", "result_zh", "conclusion_en", "conclusion_zh", "claim_not_supported_zh"]:
            if not row.get(field):
                errors.append(f"{row.get('candidate_id')} missing {field}")
    for row in matrix:
        for field in ["evidence_level", "endpoint_class", "recommendation_class"]:
            if not row.get(field):
                errors.append(f"{row.get('paper_id')} missing {field}")
    return errors


def main() -> None:
    errors = errors_for_data() + errors_for_markdown()
    if errors:
        print("Public draft validation failed:")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)
    print("Public draft validation passed.")


if __name__ == "__main__":
    main()
