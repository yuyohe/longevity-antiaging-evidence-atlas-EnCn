"""Push extracted finding fields back to Feishu 候选文献 records."""

from __future__ import annotations

import csv
import os
import time
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

from feishu_client import FeishuClient, FeishuError

ROOT = Path(__file__).resolve().parents[1]
FINDINGS = ROOT / "data" / "evidence_findings.csv"
FINDING_FIELDS = [
    "study_type_draft",
    "species_draft",
    "population_draft",
    "intervention_or_exposure_draft",
    "comparator_draft",
    "endpoint_draft",
    "result_en",
    "result_zh",
    "conclusion_en",
    "conclusion_zh",
    "evidence_level_draft",
    "endpoint_class_draft",
    "translation_status",
    "review_status",
]


def normalize(value: str) -> Any:
    if value is None:
        return ""
    return str(value).strip()


def ensure_fields(client: FeishuClient, app_token: str, table_id: str) -> None:
    existing = {field.get("field_name") for field in client.list_bitable_fields(app_token, table_id)}
    for field_name in FINDING_FIELDS:
        if field_name in existing:
            continue
        client.create_bitable_text_field(app_token, table_id, field_name)
        existing.add(field_name)
        time.sleep(0.2)


def main() -> None:
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
    by_candidate_id: Dict[str, str] = {}
    for record in existing:
        candidate_id = record.get("fields", {}).get("id")
        if candidate_id:
            by_candidate_id[str(candidate_id)] = record.get("record_id", "")

    updated = 0
    missing = 0
    with FINDINGS.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            candidate_id = row.get("candidate_id", "")
            record_id = by_candidate_id.get(candidate_id)
            if not record_id:
                missing += 1
                continue
            fields = {field: normalize(row.get(field, "")) for field in FINDING_FIELDS}
            client.update_bitable_record(app_token, table_id, record_id, fields)
            updated += 1
    print(f"Feishu candidate findings sync complete: updated={updated}, missing={missing}")


if __name__ == "__main__":
    try:
        main()
    except FeishuError as exc:
        raise SystemExit(f"Feishu findings sync failed: {exc}") from exc
