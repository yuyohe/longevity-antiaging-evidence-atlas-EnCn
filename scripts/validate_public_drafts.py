"""Validate public draft safety and completeness."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT_NOTICE_ZH = "草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。"
DRAFT_NOTICE_EN = "Draft status: automatically prepared; not fully reviewed; not medical advice."

EXPECTED_TOPICS = 20


def release_expectations() -> tuple[int, int, int]:
    metrics_path = Path(
        os.getenv(
            "RELEASE_METRICS_PATH",
            ROOT / "data" / "curation_release_metrics_2026_08.json",
        )
    )
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    findings = int(metrics["after"]["finding_records"])
    matrix = int(metrics["capacity_policy"]["matrix_global_cap"])
    return (
        int(os.getenv("EXPECTED_FINDINGS", findings)),
        int(os.getenv("MIN_MATRIX_ROWS", matrix)),
        int(os.getenv("MAX_MATRIX_ROWS", matrix)),
    )


EXPECTED_FINDINGS, MIN_MATRIX_ROWS, MAX_MATRIX_ROWS = release_expectations()


def read_csv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))


def errors_for_markdown() -> list[str]:
    errors: list[str] = []
    papers = [p for p in (ROOT / "content" / "papers").glob("*.md") if not p.name.startswith("_")]
    topics = [p for p in (ROOT / "content" / "topics").glob("*.md") if not p.name.startswith("_")]

    if len(papers) != EXPECTED_FINDINGS:
        errors.append(f"expected {EXPECTED_FINDINGS} paper pages, found {len(papers)}")
    if len(topics) != EXPECTED_TOPICS:
        errors.append(f"expected {EXPECTED_TOPICS} topic pages, found {len(topics)}")

    for path in papers + topics:
        text = path.read_text(encoding="utf-8")
        if DRAFT_NOTICE_ZH not in text:
            errors.append(f"{path.relative_to(ROOT)} missing Chinese draft notice")
        if DRAFT_NOTICE_EN not in text:
            errors.append(f"{path.relative_to(ROOT)} missing English draft notice")
        if path.parent.name == "papers":
            for marker in ["Unsupported Claim", "Overinterpretation Risk", "Medical supervision needed"]:
                if marker not in text:
                    errors.append(f"{path.relative_to(ROOT)} missing {marker}")
    return errors


def errors_for_data() -> list[str]:
    errors: list[str] = []
    findings = read_csv(ROOT / "data" / "evidence_findings.csv")
    shortlist = read_csv(ROOT / "data" / "shortlist_sources.csv")
    topics = read_csv(ROOT / "data" / "topics.csv")
    matrix = read_csv(ROOT / "data" / "evidence_matrix.csv")

    if len(findings) != EXPECTED_FINDINGS:
        errors.append(f"expected {EXPECTED_FINDINGS} findings, found {len(findings)}")
    if len(shortlist) != EXPECTED_FINDINGS:
        errors.append(f"expected {EXPECTED_FINDINGS} shortlist rows, found {len(shortlist)}")
    if len(topics) != EXPECTED_TOPICS:
        errors.append(f"expected {EXPECTED_TOPICS} topics, found {len(topics)}")
    if not MIN_MATRIX_ROWS <= len(matrix) <= MAX_MATRIX_ROWS:
        errors.append(f"expected {MIN_MATRIX_ROWS}-{MAX_MATRIX_ROWS} evidence matrix rows, found {len(matrix)}")

    finding_ids = [row.get("candidate_id", "") for row in findings]
    if len(finding_ids) != len(set(finding_ids)):
        errors.append("evidence_findings.csv contains duplicate candidate_id values")

    for row in findings:
        for field in [
            "result_en",
            "result_zh",
            "conclusion_en",
            "conclusion_zh",
            "claim_not_supported_zh",
            "evidence_source_depth",
            "contribution_score_draft",
        ]:
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
