"""Sync an arbitrary CSV file to a Feishu bitable table."""

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


def normalize(value: str) -> Any:
    return "" if value is None else str(value).strip()


def ensure_table(
    client: FeishuClient,
    app_token: str,
    table_name: str,
    primary_field: str,
    fieldnames: list[str],
    allow_create: bool,
) -> str:
    for table in client.list_bitable_tables(app_token):
        if table.get("name") == table_name:
            return table.get("table_id", "")
    if not allow_create:
        raise FeishuError(f"No existing table named {table_name}; pass --allow-create only for a deliberate new asset")
    fields = [{"field_name": primary_field, "type": 1}]
    fields.extend({"field_name": name, "type": 1} for name in fieldnames if name != primary_field)
    table = client.create_bitable_table(app_token, table_name, "表格", fields)
    table_id = table.get("data", {}).get("table_id") or table.get("data", {}).get("table", {}).get("table_id", "")
    if table_id:
        return table_id
    for table in client.list_bitable_tables(app_token):
        if table.get("name") == table_name:
            return table.get("table_id", "")
    raise FeishuError(f"Failed to create or locate table {table_name}: {table}")


def ensure_fields(client: FeishuClient, app_token: str, table_id: str, primary_field: str, fieldnames: list[str]) -> None:
    existing = {field.get("field_name") for field in client.list_bitable_fields(app_token, table_id)}
    for field_name in [primary_field, *fieldnames]:
        if field_name in existing:
            continue
        client.create_bitable_text_field(app_token, table_id, field_name)
        existing.add(field_name)
        time.sleep(0.2)


def chunks(items: list[Any], size: int = 500):
    for start in range(0, len(items), size):
        yield items[start : start + size]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="CSV path relative to repo root.")
    parser.add_argument("--table-name", required=True)
    parser.add_argument("--table-id", default="")
    parser.add_argument("--primary-key", required=True)
    parser.add_argument("--primary-field", default="文本")
    parser.add_argument("--table-id-env", default="")
    parser.add_argument("--delete-stale", action="store_true")
    parser.add_argument("--rename-existing", action="store_true")
    parser.add_argument("--allow-create", action="store_true")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    path = ROOT / args.csv
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    if args.primary_key not in fieldnames:
        raise SystemExit(f"{args.csv} missing primary key {args.primary_key}")

    client = FeishuClient()
    app_token = client.resolve_bitable_app_token(
        app_token=os.getenv("FEISHU_BITABLE_APP_TOKEN", ""),
        wiki_node_token=os.getenv("FEISHU_BITABLE_WIKI_NODE_TOKEN", ""),
    )
    table_id = args.table_id or (os.getenv(args.table_id_env, "") if args.table_id_env else "")
    if not table_id:
        table_id = ensure_table(
            client,
            app_token,
            args.table_name,
            args.primary_field,
            fieldnames,
            args.allow_create,
        )
    elif args.rename_existing:
        tables = {str(table.get("table_id", "")): table for table in client.list_bitable_tables(app_token)}
        table = tables.get(table_id)
        if not table:
            raise FeishuError(f"Registered table is missing: {table_id}")
        if table.get("name") != args.table_name:
            client.update_bitable_table(app_token, table_id, args.table_name)
            print(f"renamed {table_id}: {table.get('name')} -> {args.table_name}")
    ensure_fields(client, app_token, table_id, args.primary_field, fieldnames)

    existing = client.list_bitable_records(app_token, table_id)
    by_key: dict[str, str] = {}
    blank_record_ids: list[str] = []
    missing_key_record_ids: list[str] = []
    duplicate_record_ids: list[str] = []
    for record in existing:
        fields = record.get("fields", {})
        key = fields.get(args.primary_key)
        if key:
            normalized_key = str(key)
            if normalized_key in by_key:
                duplicate_record_ids.append(record.get("record_id", ""))
            else:
                by_key[normalized_key] = record.get("record_id", "")
        elif not fields:
            blank_record_ids.append(record.get("record_id", ""))
        else:
            missing_key_record_ids.append(record.get("record_id", ""))

    create_payloads: list[dict[str, Any]] = []
    update_payloads: list[dict[str, Any]] = []
    seen = set()
    for row in rows:
        key = row.get(args.primary_key, "")
        seen.add(key)
        fields = {field: normalize(row.get(field, "")) for field in fieldnames}
        fields[args.primary_field] = (
            normalize(row.get(args.primary_field, ""))
            or normalize(row.get("title_zh", ""))
            or normalize(row.get("name_zh", ""))
            or normalize(row.get(args.primary_key, ""))
        )
        if key in by_key:
            update_payloads.append({"record_id": by_key[key], "fields": fields})
        else:
            create_payloads.append({"fields": fields})

    created = 0
    for batch in chunks(create_payloads):
        client.batch_create_bitable_records(app_token, table_id, batch)
        created += len(batch)
        print(f"csv_created={created}/{len(create_payloads)}")
        time.sleep(0.2)

    updated = 0
    for batch in chunks(update_payloads):
        client.batch_update_bitable_records(app_token, table_id, batch)
        updated += len(batch)
        print(f"csv_updated={updated}/{len(update_payloads)}")
        time.sleep(0.2)

    deleted = 0
    if args.delete_stale:
        stale_record_ids: list[str] = []
        for key, record_id in by_key.items():
            if key not in seen:
                stale_record_ids.append(record_id)
        stale_record_ids.extend(blank_record_ids)
        stale_record_ids.extend(missing_key_record_ids)
        stale_record_ids.extend(duplicate_record_ids)
        stale_record_ids = list(dict.fromkeys(record_id for record_id in stale_record_ids if record_id))
        for batch in chunks(stale_record_ids):
            client.batch_delete_bitable_records(app_token, table_id, batch)
            deleted += len(batch)
            print(f"csv_deleted={deleted}/{len(stale_record_ids)}")
            time.sleep(0.2)

    print(f"Feishu CSV sync complete: table_name={args.table_name}, table_id={table_id}, created={created}, updated={updated}, deleted_stale={deleted}")


if __name__ == "__main__":
    try:
        main()
    except FeishuError as exc:
        raise SystemExit(f"Feishu CSV sync failed: {exc}") from exc
