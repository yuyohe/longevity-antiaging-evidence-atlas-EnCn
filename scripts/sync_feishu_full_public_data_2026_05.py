"""Sync full public evidence data tables to Feishu Bitable."""

from __future__ import annotations

import csv
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from feishu_client import FeishuClient, FeishuError


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public-data"
DATA = ROOT / "data"
DOC_DOMAIN = "ucngl3rlrux2.feishu.cn"
WIKI_NODE_TOKEN = "WriBw4TXZiOsjQkJWk8ctL1xnVg"
TEXT_FIELD = 1
FEISHU_CELL_MAX = 300


ASSETS = [
    {
        "asset_key": "literature_library",
        "table_name": "公开数据_全量文献候选库_2026-05",
        "csv": PUBLIC / "literature-library-2026-05.csv",
        "primary_key": "library_id",
        "title_fields": ["title_zh", "title_en", "library_id"],
    },
    {
        "asset_key": "candidate_sources",
        "table_name": "公开数据_候选来源原始表_2026-05",
        "csv": PUBLIC / "candidate-sources-2026-05.csv",
        "primary_key": "id",
        "title_fields": ["title_zh", "title_en", "id"],
    },
    {
        "asset_key": "shortlist_sources",
        "table_name": "公开数据_入选短名单_2026-05",
        "csv": PUBLIC / "shortlist-sources-2026-05.csv",
        "primary_key": "candidate_id",
        "title_fields": ["title_zh", "title_en", "candidate_id"],
    },
    {
        "asset_key": "evidence_findings",
        "table_name": "公开数据_证据发现表_2026-05",
        "csv": PUBLIC / "evidence-findings-2026-05.csv",
        "primary_key": "finding_id",
        "title_fields": ["title_zh", "title_en", "finding_id"],
    },
    {
        "asset_key": "evidence_matrix",
        "table_name": "公开数据_证据矩阵_2026-05",
        "csv": PUBLIC / "evidence-matrix-2026-05.csv",
        "primary_key": "paper_id",
        "title_fields": ["topic", "intervention_or_exposure", "paper_id"],
    },
]


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames or []


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def chunks(items: list[Any], size: int = 500):
    for start in range(0, len(items), size):
        yield items[start : start + size]


def table_url(table_id: str) -> str:
    domain = os.getenv("FEISHU_DOC_DOMAIN", DOC_DOMAIN)
    wiki_token = os.getenv("FEISHU_WIKI_ROOT_NODE_TOKEN", WIKI_NODE_TOKEN)
    return f"https://{domain}/wiki/{wiki_token}?table={table_id}"


def normalize(value: Any, max_len: int = FEISHU_CELL_MAX) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 12].rstrip() + " ...[完整见CSV]"


def public_title(row: dict[str, str], title_fields: list[str], primary_key: str) -> str:
    parts = [normalize(row.get(primary_key))]
    for field in title_fields:
        value = normalize(row.get(field))
        if value and value not in parts:
            parts.append(value)
            break
    return " | ".join(part for part in parts if part)[:120]


def ensure_table(client: FeishuClient, app_token: str, table_name: str, fieldnames: list[str]) -> str:
    for table in client.list_bitable_tables(app_token):
        if table.get("name") == table_name:
            return table.get("table_id", "")
    schema = [{"field_name": "公开标题", "type": TEXT_FIELD}]
    schema.extend({"field_name": name, "type": TEXT_FIELD} for name in fieldnames if name != "公开标题")
    created = client.create_bitable_table(app_token, table_name, "表格", schema)
    table_id = created.get("data", {}).get("table_id") or created.get("data", {}).get("table", {}).get("table_id", "")
    if table_id:
        return table_id
    for table in client.list_bitable_tables(app_token):
        if table.get("name") == table_name:
            return table.get("table_id", "")
    raise FeishuError(f"Failed to create table {table_name}: {created}")


def ensure_fields(client: FeishuClient, app_token: str, table_id: str, fieldnames: list[str]) -> None:
    existing = {field.get("field_name") for field in client.list_bitable_fields(app_token, table_id)}
    for field in ["公开标题", *fieldnames]:
        if field in existing:
            continue
        client.create_bitable_text_field(app_token, table_id, field)
        existing.add(field)
        time.sleep(0.15)


def sync_asset(client: FeishuClient, app_token: str, asset: dict[str, Any]) -> dict[str, Any]:
    rows, fieldnames = read_csv(asset["csv"])
    if asset["primary_key"] not in fieldnames:
        raise FeishuError(f"{asset['csv']} missing primary key {asset['primary_key']}")
    table_id = ensure_table(client, app_token, asset["table_name"], fieldnames)
    ensure_fields(client, app_token, table_id, fieldnames)

    existing = client.list_bitable_records(app_token, table_id)
    by_key = {
        str(record.get("fields", {}).get(asset["primary_key"], "")): record.get("record_id", "")
        for record in existing
        if record.get("fields", {}).get(asset["primary_key"])
    }
    source_keys = {normalize(row.get(asset["primary_key"]), max_len=120) for row in rows if row.get(asset["primary_key"])}
    if source_keys and source_keys.issubset(set(by_key)) and len(by_key) >= len(source_keys):
        print(f"{asset['asset_key']}: already synced {len(source_keys)} records; skipped")
        return {
            "asset_group": asset["table_name"],
            "asset_key": asset["asset_key"],
            "table_id": table_id,
            "url": table_url(table_id),
            "rows": len(rows),
            "created": 0,
            "updated": 0,
            "status": "active",
        }

    create_payloads: list[dict[str, Any]] = []
    update_payloads: list[dict[str, Any]] = []
    for row in rows:
        key = normalize(row.get(asset["primary_key"]), max_len=120)
        if not key:
            continue
        fields = {field: normalize(row.get(field)) for field in fieldnames}
        fields["公开标题"] = public_title(row, asset["title_fields"], asset["primary_key"])
        payload = {"fields": fields}
        if key in by_key:
            update_payloads.append({"record_id": by_key[key], "fields": fields})
        else:
            create_payloads.append(payload)

    created = 0
    for batch in chunks(create_payloads):
        client.batch_create_bitable_records(app_token, table_id, batch)
        created += len(batch)
        print(f"{asset['asset_key']}: created {created}/{len(create_payloads)}")
        time.sleep(0.25)

    updated = 0
    for batch in chunks(update_payloads):
        client.batch_update_bitable_records(app_token, table_id, batch)
        updated += len(batch)
        print(f"{asset['asset_key']}: updated {updated}/{len(update_payloads)}")
        time.sleep(0.25)

    return {
        "asset_group": asset["table_name"],
        "asset_key": asset["asset_key"],
        "table_id": table_id,
        "url": table_url(table_id),
        "rows": len(rows),
        "created": created,
        "updated": updated,
        "status": "active",
    }


def main() -> None:
    load_dotenv(ROOT / ".env")
    client = FeishuClient()
    app_token = client.resolve_bitable_app_token(
        app_token=os.getenv("FEISHU_BITABLE_APP_TOKEN", ""),
        wiki_node_token=os.getenv("FEISHU_BITABLE_WIKI_NODE_TOKEN", ""),
    )

    synced: list[dict[str, Any]] = []
    for asset in ASSETS:
        synced.append(sync_asset(client, app_token, asset))

    write_csv(
        DATA / "feishu_full_public_data_links_2026_05.csv",
        synced,
        ["asset_group", "asset_key", "table_id", "url", "rows", "created", "updated", "status"],
    )
    print("wrote data/feishu_full_public_data_links_2026_05.csv")


if __name__ == "__main__":
    try:
        main()
    except FeishuError as exc:
        raise SystemExit(f"Feishu full public data sync failed: {exc}") from exc
