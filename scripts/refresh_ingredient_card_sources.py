"""Refresh existing ingredient cards while retaining evidence-review dates."""

from __future__ import annotations

import csv
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    path = DATA / "social_cards_top50_ingredients.csv"
    cards = read_csv(path)
    retractions = {r["name_zh"]: r for r in read_csv(DATA / "retraction_risk_summary_20y.csv")
                   if r["domain"] == "口服/补剂"}
    supplements = {r["补剂"]: r for r in read_csv(DATA / "easy_reader_supplements.csv")}
    fields = list(cards[0])
    fields += [f for f in ("evidence_review_date", "retraction_checked_date", "visual_snapshot_date") if f not in fields]
    for card in cards:
        ret = retractions.get(card["name_zh"])
        source = supplements.get(card["name_zh"])
        if not ret or not source:
            raise RuntimeError(f"Missing source for card {card['card_id']}")
        card["evidence_review_date"] = card.get("evidence_review_date") or card["last_checked"]
        card["retraction_checked_date"] = ret["last_checked"]
        card["visual_snapshot_date"] = os.environ["EVIDENCE_ATLAS_UPDATE_DATE"]
        card["update_month"] = os.environ["EVIDENCE_ATLAS_ASSET_MONTH"]
        for dest, source_key in {
            "health_evidence": "健康证据", "skin_evidence": "皮肤证据",
            "one_sentence": "一句话总结", "common_misunderstanding": "常见误解",
            "attention": "注意", "commercial_overclaim_risk": "商业宣传风险",
        }.items():
            card[dest] = source[source_key]
        card["retraction_publications_20y"] = ret["pubmed_total_count_20y"]
        card["retraction_count_20y"] = ret["pubmed_retracted_count_20y"]
        card["retractions_per_1000_publications"] = ret["retractions_per_1000_publications"]
        card["retraction_note"] = ret["denominator_note_zh"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(cards)
    print(f"Refreshed sources for {len(cards)} cards; evidence-review dates preserved")


if __name__ == "__main__":
    main()
