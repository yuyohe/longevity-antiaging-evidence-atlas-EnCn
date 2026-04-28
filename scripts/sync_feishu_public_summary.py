"""Sync data/public_summary.csv to a Feishu table named 对外总览."""

from __future__ import annotations

import argparse
import csv
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from feishu_client import FeishuClient, FeishuError

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "data" / "public_summary.csv"
TABLE_NAME = "对外总览"
PRIMARY_FIELD = "主题"


def normalize(value: str) -> Any:
    return "" if value is None else str(value).strip()


def ensure_table(client: FeishuClient, app_token: str, fieldnames: list[str]) -> str:
    for table in client.list_bitable_tables(app_token):
        if table.get("name") == TABLE_NAME:
            return table.get("table_id", "")
    fields = [{"field_name": PRIMARY_FIELD, "type": 1}]
    fields.extend({"field_name": name, "type": 1} for name in fieldnames if name != PRIMARY_FIELD)
    table = client.create_bitable_table(app_token, TABLE_NAME, "表格", fields)
    table_id = table.get("data", {}).get("table_id") or table.get("data", {}).get("table", {}).get("table_id", "")
    if not table_id:
        tables = client.list_bitable_tables(app_token)
        for item in tables:
            if item.get("name") == TABLE_NAME:
                return item.get("table_id", "")
        raise FeishuError(f"Failed to create or locate table {TABLE_NAME}: {table}")
    return table_id


def ensure_fields(client: FeishuClient, app_token: str, table_id: str, fieldnames: list[str]) -> None:
    existing = {field.get("field_name") for field in client.list_bitable_fields(app_token, table_id)}
    for field_name in [PRIMARY_FIELD, *fieldnames]:
        if field_name in existing:
            continue
        client.create_bitable_text_field(app_token, table_id, field_name)
        existing.add(field_name)
        time.sleep(0.2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delete-stale", action="store_true")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    with SUMMARY.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    client = FeishuClient()
    app_token = client.resolve_bitable_app_token(
        app_token=os.getenv("FEISHU_BITABLE_APP_TOKEN", ""),
        wiki_node_token=os.getenv("FEISHU_BITABLE_WIKI_NODE_TOKEN", ""),
    )
    table_id = os.getenv("FEISHU_PUBLIC_SUMMARY_TABLE_ID", "") or ensure_table(client, app_token, fieldnames)
    ensure_fields(client, app_token, table_id, fieldnames)

    existing = client.list_bitable_records(app_token, table_id)
    by_summary_id: dict[str, str] = {}
    blank_record_ids = []
    for record in existing:
        fields = record.get("fields", {})
        summary_id = fields.get("summary_id")
        if summary_id:
            by_summary_id[str(summary_id)] = record.get("record_id", "")
        elif not fields:
            blank_record_ids.append(record.get("record_id", ""))

    created = 0
    updated = 0
    seen = set()
    for row in rows:
        summary_id = row.get("summary_id", "")
        seen.add(summary_id)
        fields = {key: normalize(row.get(key, "")) for key in fieldnames}
        fields[PRIMARY_FIELD] = row.get("title_zh") or row.get("title_en") or summary_id
        if summary_id in by_summary_id:
            client.update_bitable_record(app_token, table_id, by_summary_id[summary_id], fields)
            updated += 1
        else:
            client.create_bitable_record(app_token, table_id, fields)
            created += 1

    deleted = 0
    if args.delete_stale:
        for summary_id, record_id in by_summary_id.items():
            if summary_id not in seen:
                client.delete_bitable_record(app_token, table_id, record_id)
                deleted += 1
        for record_id in blank_record_ids:
            if record_id:
                client.delete_bitable_record(app_token, table_id, record_id)
                deleted += 1

    print(f"Feishu public summary sync complete: table_id={table_id}, created={created}, updated={updated}, deleted_stale={deleted}")


if __name__ == "__main__":
    try:
        main()
    except FeishuError as exc:
        raise SystemExit(f"Feishu public summary sync failed: {exc}") from exc
