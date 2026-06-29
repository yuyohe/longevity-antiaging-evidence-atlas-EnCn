"""Validate skin beauty atlas and supplement matrix drafts."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT_NOTICE_ZH = "草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。"
DRAFT_NOTICE_EN = "Draft status: automatically prepared; not fully reviewed; not medical advice."


def read_csv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.open("r", encoding="utf-8-sig", newline="")))


def main() -> None:
    errors: list[str] = []
    findings = read_csv(ROOT / "data" / "skin_beauty_findings.csv")
    topics = read_csv(ROOT / "data" / "skin_beauty_topics.csv")
    summary = read_csv(ROOT / "data" / "skin_beauty_summary.csv")
    supplements = read_csv(ROOT / "data" / "supplement_matrix.csv")

    if len(topics) != 9:
        errors.append(f"expected 9 skin beauty topics, found {len(topics)}")
    if len(summary) != 9:
        errors.append(f"expected 9 skin beauty summary rows, found {len(summary)}")
    if len(findings) < 180:
        errors.append(f"expected at least 180 skin beauty findings, found {len(findings)}")
    if len(supplements) < 20:
        errors.append(f"expected at least 20 supplement rows, found {len(supplements)}")

    topic_counts: dict[str, int] = {}
    for row in findings:
        topic_counts[row.get("topic_id", "")] = topic_counts.get(row.get("topic_id", ""), 0) + 1
        for field in ["result_en", "result_zh", "unsupported_claim_zh", "safety_notes_zh", "endpoint_class"]:
            if not row.get(field):
                errors.append(f"{row.get('finding_id')} missing {field}")
        if row.get("endpoint_class") not in {"S1", "S2", "M"}:
            errors.append(f"{row.get('finding_id')} invalid endpoint_class {row.get('endpoint_class')}")
    for row in topics:
        if topic_counts.get(row.get("topic_id", ""), 0) < 20:
            errors.append(f"{row.get('topic_id')} has fewer than 20 findings")

    for row in supplements:
        for field in ["longevity_evidence_level", "skin_beauty_evidence_level", "supported_claim_zh", "unsupported_claim_zh", "safety_notes_zh"]:
            if not row.get(field):
                errors.append(f"{row.get('supplement_id')} missing {field}")

    for path in [
        ROOT / "content" / "overview" / "skin-beauty-summary.md",
        ROOT / "content" / "overview" / "supplement-summary.md",
        *[p for p in (ROOT / "content" / "skin-beauty-topics").glob("*.md")],
    ]:
        text = path.read_text(encoding="utf-8")
        if DRAFT_NOTICE_ZH not in text:
            errors.append(f"{path.relative_to(ROOT)} missing Chinese draft notice")
        if DRAFT_NOTICE_EN not in text:
            errors.append(f"{path.relative_to(ROOT)} missing English draft notice")
        if "延寿" in text and "不能" not in text and "不支持" not in text:
            errors.append(f"{path.relative_to(ROOT)} may overclaim longevity")

    if errors:
        print("Skin beauty validation failed:")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)
    print("Skin beauty validation passed.")


if __name__ == "__main__":
    main()
