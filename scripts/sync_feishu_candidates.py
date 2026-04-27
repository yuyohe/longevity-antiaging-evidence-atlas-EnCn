"""Sync data/candidate_sources.csv to the Feishu 候选文献 table."""

from __future__ import annotations

import csv
import os
import time
import argparse
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

from candidate_utils import CANDIDATE_FIELDS
from feishu_client import FeishuClient, FeishuError

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "candidate_sources.csv"
PRIMARY_FIELD = "文本"
REVIEW_FIELDS = [
    "reviewer",
    "review_date",
    "journal",
    "journal_if",
    "journal_if_year",
    "journal_if_source",
    "endpoint_value_score",
    "study_design_score",
    "human_relevance_score",
    "scale_replication_score",
    "effect_actionability_score",
    "authority_signal_score",
    "atlas_coverage_score",
    "bilingual_explainability_score",
    "penalty_score",
    "contribution_score",
    "decision",
    "reviewer_notes",
]


def normalize(value: str) -> Any:
    if value is None:
        return ""
    return str(value).strip()


def ensure_fields(client: FeishuClient, app_token: str, table_id: str) -> None:
    existing = {field.get("field_name") for field in client.list_bitable_fields(app_token, table_id)}
    for field_name in [*CANDIDATE_FIELDS, *REVIEW_FIELDS]:
        if field_name in existing:
            continue
        client.create_bitable_text_field(app_token, table_id, field_name)
        existing.add(field_name)
        time.sleep(0.2)


def row_to_fields(row: Dict[str, str]) -> Dict[str, Any]:
    fields = {key: normalize(row.get(key, "")) for key in CANDIDATE_FIELDS}
    title = fields.get("title_en") or fields.get("id")
    if title:
        fields[PRIMARY_FIELD] = title[:250]
    return fields


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--update-existing", action="store_true", help="Update records already present in Feishu.")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    table_id = os.getenv("FEISHU_CANDIDATE_TABLE_ID", "")
    if not table_id:
        raise SystemExit("Missing FEISHU_CANDIDATE_TABLE_ID.")

    client = FeishuClient()
    app_token = client.resolve_bitable_app_token(
        app_token=os.getenv("FEISHU_BITABLE_APP_TOKEN", ""),
        wiki_node_token=os.getenv("FEISHU_BITABLE_WIKI_NODE_TOKEN", ""),
    )
    ensure_fields(client, app_token, table_id)

    existing = client.list_bitable_records(app_token, table_id)
    by_id: Dict[str, str] = {}
    for record in existing:
        fields = record.get("fields", {})
        candidate_id = fields.get("id")
        if candidate_id:
            by_id[str(candidate_id)] = record.get("record_id", "")

    created = 0
    updated = 0
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            candidate_id = (row.get("id") or "").strip()
            if not candidate_id:
                continue
            fields = row_to_fields(row)
            if candidate_id in by_id:
                if args.update_existing:
                    client.update_bitable_record(app_token, table_id, by_id[candidate_id], fields)
                    updated += 1
            else:
                client.create_bitable_record(app_token, table_id, fields)
                created += 1

    skipped = len(by_id) if not args.update_existing else 0
    print(f"Feishu candidate sync complete: created={created}, updated={updated}, skipped_existing={skipped}")


if __name__ == "__main__":
    try:
        main()
    except FeishuError as exc:
        raise SystemExit(f"Feishu candidate sync failed: {exc}") from exc
