"""Sync data/topics.csv to Feishu 主题库."""

from __future__ import annotations

import csv
import os
import time
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

from feishu_client import FeishuClient, FeishuError

ROOT = Path(__file__).resolve().parents[1]
TOPICS = ROOT / "data" / "topics.csv"
PRIMARY_FIELD = "文本"


def normalize(value: str) -> Any:
    return "" if value is None else str(value).strip()


def ensure_fields(client: FeishuClient, app_token: str, table_id: str, fieldnames: list[str]) -> None:
    existing = {field.get("field_name") for field in client.list_bitable_fields(app_token, table_id)}
    for field_name in fieldnames:
        if field_name in existing:
            continue
        client.create_bitable_text_field(app_token, table_id, field_name)
        existing.add(field_name)
        time.sleep(0.2)


def main() -> None:
    load_dotenv(ROOT / ".env")
    table_id = os.getenv("FEISHU_TOPIC_TABLE_ID", "")
    if not table_id:
        raise SystemExit("Missing FEISHU_TOPIC_TABLE_ID.")

    with TOPICS.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    client = FeishuClient()
    app_token = client.resolve_bitable_app_token(
        app_token=os.getenv("FEISHU_BITABLE_APP_TOKEN", ""),
        wiki_node_token=os.getenv("FEISHU_BITABLE_WIKI_NODE_TOKEN", ""),
    )
    ensure_fields(client, app_token, table_id, fieldnames)

    existing = client.list_bitable_records(app_token, table_id)
    by_topic_id: Dict[str, str] = {}
    for record in existing:
        topic_id = record.get("fields", {}).get("topic_id")
        if topic_id:
            by_topic_id[str(topic_id)] = record.get("record_id", "")

    created = 0
    updated = 0
    for row in rows:
        topic_id = row.get("topic_id", "")
        fields = {key: normalize(row.get(key, "")) for key in fieldnames}
        fields[PRIMARY_FIELD] = row.get("title_zh") or row.get("title_en") or topic_id
        if topic_id in by_topic_id:
            client.update_bitable_record(app_token, table_id, by_topic_id[topic_id], fields)
            updated += 1
        else:
            client.create_bitable_record(app_token, table_id, fields)
            created += 1
    print(f"Feishu topics sync complete: created={created}, updated={updated}")


if __name__ == "__main__":
    try:
        main()
    except FeishuError as exc:
        raise SystemExit(f"Feishu topics sync failed: {exc}") from exc
