"""Sync data/evidence_matrix.csv to Feishu Base/Bitable.

Usage:
    export FEISHU_APP_ID=cli_xxx
    export FEISHU_APP_SECRET=xxx
    export FEISHU_BITABLE_APP_TOKEN=bascn_xxx
    export FEISHU_SOURCE_TABLE_ID=tblxxx
    python scripts/sync_feishu_bitable.py

Design:
- GitHub CSV is the source of truth.
- Feishu Base is the public/operational display layer.
- Upsert key: paper_id.
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

from feishu_client import FeishuClient, FeishuError

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "evidence_matrix.csv"
MAPPING_PATH = ROOT / "config" / "feishu_field_mapping.json"


def normalize_value(value: str) -> Any:
    if value is None:
        return ""
    value = str(value).strip()
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value == "":
        return ""
    return value


def load_mapping() -> Dict[str, str]:
    with MAPPING_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def row_to_fields(row: Dict[str, str], mapping: Dict[str, str]) -> Dict[str, Any]:
    fields: Dict[str, Any] = {}
    for csv_key, feishu_key in mapping.items():
        if csv_key in row:
            fields[feishu_key] = normalize_value(row[csv_key])
    return fields


def main() -> None:
    load_dotenv(ROOT / ".env")

    app_token = os.getenv("FEISHU_BITABLE_APP_TOKEN", "")
    table_id = os.getenv("FEISHU_SOURCE_TABLE_ID", "")
    if not app_token or not table_id:
        raise SystemExit("Missing FEISHU_BITABLE_APP_TOKEN or FEISHU_SOURCE_TABLE_ID.")

    mapping = load_mapping()
    client = FeishuClient()

    existing = client.list_bitable_records(app_token, table_id)
    by_paper_id: Dict[str, str] = {}
    paper_id_field = mapping.get("paper_id", "paper_id")
    for record in existing:
        fields = record.get("fields", {})
        paper_id = fields.get(paper_id_field)
        if paper_id:
            by_paper_id[str(paper_id)] = record.get("record_id", "")

    created = 0
    updated = 0

    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            paper_id = row.get("paper_id", "").strip()
            if not paper_id:
                continue
            fields = row_to_fields(row, mapping)
            if paper_id in by_paper_id:
                client.update_bitable_record(app_token, table_id, by_paper_id[paper_id], fields)
                updated += 1
            else:
                client.create_bitable_record(app_token, table_id, fields)
                created += 1

    print(f"Feishu sync complete: created={created}, updated={updated}")


if __name__ == "__main__":
    try:
        main()
    except FeishuError as exc:
        raise SystemExit(f"Feishu sync failed: {exc}") from exc
