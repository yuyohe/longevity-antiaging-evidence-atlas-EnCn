"""Compute contribution scores for manually reviewed candidate rows."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCORES = ROOT / "data" / "candidate_review_scores.csv"

POSITIVE_COLUMNS = [
    "endpoint_value_score",
    "study_design_score",
    "human_relevance_score",
    "scale_replication_score",
    "effect_actionability_score",
    "authority_signal_score",
    "atlas_coverage_score",
    "bilingual_explainability_score",
]


def number(value: str) -> float:
    try:
        return float(str(value).strip() or 0)
    except ValueError:
        return 0.0


def decision(score: float) -> str:
    if score >= 85:
        return "high_priority_include"
    if score >= 70:
        return "shortlist"
    if score >= 50:
        return "candidate_hold"
    if score >= 30:
        return "low_priority"
    return "exclude_or_archive"


def main() -> None:
    with SCORES.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
        fieldnames = f.readline()
    if not rows:
        print("No reviewed candidate rows yet.")
        return

    output_fields = list(rows[0].keys())
    for required in ("contribution_score", "decision"):
        if required not in output_fields:
            output_fields.append(required)

    for row in rows:
        base = sum(number(row.get(column, "")) for column in POSITIVE_COLUMNS)
        penalty = abs(number(row.get("penalty_score", "")))
        total = max(0.0, min(100.0, base - penalty))
        row["contribution_score"] = str(round(total, 1))
        row["decision"] = decision(total)

    with SCORES.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Scored {len(rows)} reviewed rows.")


if __name__ == "__main__":
    main()
