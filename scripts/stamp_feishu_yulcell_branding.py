"""Stamp yulcell brand metadata onto existing Feishu Bitable assets."""

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
DATA = ROOT / "data"
DEFAULT_TABLES_CSV = DATA / "feishu_live_tables_2026_05.csv"
REPORT_CSV = DATA / "feishu_yulcell_branding_2026_06.csv"
TEXT_FIELD = 1

BRAND_NAME = os.getenv("PUBLIC_BRAND_NAME", "宇多Yul细胞/yulcell")
BRAND_EN = os.getenv("PUBLIC_BRAND_EN", "yulcell")
BRAND_PROJECT = os.getenv("PUBLIC_BRAND_PROJECT", "Longevity Anti-Aging Evidence Atlas EnCn")
BRAND_GITHUB_URL = os.getenv(
    "PUBLIC_BRAND_GITHUB_URL",
    "https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn",
)
BRAND_SEO_KEYWORDS = os.getenv(
    "PUBLIC_BRAND_SEO_KEYWORDS",
    "宇多Yul细胞/yulcell, yulcell, 宇多Yul细胞, 长寿抗衰证据图谱, 健康寿命证据图谱, 抗衰证据库, longevity anti-aging evidence atlas, healthspan evidence atlas",
)
BRAND_FIELDS = {
    "品牌标识": BRAND_NAME,
    "Brand": BRAND_EN,
    "SEO关键词": BRAND_SEO_KEYWORDS,
    "资产归属": f"{BRAND_NAME} | {BRAND_PROJECT}",
    "GitHub公开入口": BRAND_GITHUB_URL,
}


def chunks(items: list[Any], size: int) -> list[list[Any]]:
    return [items[start : start + size] for start in range(0, len(items), size)]


def read_tables(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    tables: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        table_id = (row.get("table_id") or "").strip()
        status = (row.get("状态") or row.get("status") or "").strip()
        if not table_id or table_id in seen or not status.startswith("active"):
            continue
        seen.add(table_id)
        tables.append(row)
    return tables


def write_report(rows: list[dict[str, Any]]) -> None:
    REPORT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "sync_id",
        "table_name",
        "table_id",
        "url",
        "rows",
        "created_fields",
        "records_needing_update",
        "updated_records",
        "status",
    ]
    with REPORT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def ensure_brand_fields(client: FeishuClient, app_token: str, table_id: str, dry_run: bool) -> list[str]:
    existing = {field.get("field_name") for field in client.list_bitable_fields(app_token, table_id)}
    created: list[str] = []
    for field_name in BRAND_FIELDS:
        if field_name in existing:
            continue
        created.append(field_name)
        if not dry_run:
            client.create_bitable_field(app_token, table_id, field_name, TEXT_FIELD)
            time.sleep(0.15)
    return created


def needs_brand_update(fields: dict[str, Any]) -> bool:
    return any(str(fields.get(name, "")).strip() != value for name, value in BRAND_FIELDS.items())


def stamp_table(
    client: FeishuClient,
    app_token: str,
    table: dict[str, str],
    batch_size: int,
    dry_run: bool,
) -> dict[str, Any]:
    table_id = (table.get("table_id") or "").strip()
    table_name = (table.get("表名") or table.get("asset_group") or table_id).strip()
    created_fields = ensure_brand_fields(client, app_token, table_id, dry_run=dry_run)
    records = client.list_bitable_records(app_token, table_id)
    updates = [
        {"record_id": record.get("record_id", ""), "fields": dict(BRAND_FIELDS)}
        for record in records
        if record.get("record_id") and needs_brand_update(record.get("fields", {}))
    ]

    updated = 0
    if not dry_run:
        for batch in chunks(updates, batch_size):
            client.batch_update_bitable_records(app_token, table_id, batch)
            updated += len(batch)
            print(f"{table_name}: branded {updated}/{len(updates)}")
            time.sleep(0.25)

    return {
        "sync_id": table.get("sync_id", ""),
        "table_name": table_name,
        "table_id": table_id,
        "url": table.get("飞书链接") or table.get("url") or "",
        "rows": len(records),
        "created_fields": ",".join(created_fields),
        "records_needing_update": len(updates),
        "updated_records": 0 if dry_run else updated,
        "status": "dry_run" if dry_run else "branded",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tables-csv", default=str(DEFAULT_TABLES_CSV))
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    client = FeishuClient()
    app_token = client.resolve_bitable_app_token(
        app_token=os.getenv("FEISHU_BITABLE_APP_TOKEN", ""),
        wiki_node_token=os.getenv("FEISHU_BITABLE_WIKI_NODE_TOKEN", ""),
    )

    reports: list[dict[str, Any]] = []
    for table in read_tables(Path(args.tables_csv)):
        reports.append(
            stamp_table(
                client=client,
                app_token=app_token,
                table=table,
                batch_size=args.batch_size,
                dry_run=args.dry_run,
            )
        )
    write_report(reports)
    print(f"wrote {REPORT_CSV}")


if __name__ == "__main__":
    try:
        main()
    except FeishuError as exc:
        raise SystemExit(f"Feishu branding failed: {exc}") from exc
