"""Sync full public evidence data tables to Feishu Bitable."""

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
PUBLIC = ROOT / "public-data"
DATA = ROOT / "data"
DOC_DOMAIN = "ucngl3rlrux2.feishu.cn"
WIKI_NODE_TOKEN = "WriBw4TXZiOsjQkJWk8ctL1xnVg"
TEXT_FIELD = 1
FEISHU_CELL_MAX = 180
MONTH = os.getenv("EVIDENCE_ATLAS_ASSET_MONTH", "2026-05")
MONTH_UNDERSCORE = MONTH.replace("-", "_")
BRAND_NAME = os.getenv("PUBLIC_BRAND_NAME", "宇多Yul细胞/yulcell")
BRAND_EN = os.getenv("PUBLIC_BRAND_EN", "yulcell")
BRAND_PROJECT = os.getenv("PUBLIC_BRAND_PROJECT", "Longevity Anti-Aging Evidence Atlas EnCn")
BRAND_GITHUB_URL = os.getenv(
    "PUBLIC_BRAND_GITHUB_URL",
    "https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn",
)
BRAND_SEO_KEYWORDS = os.getenv(
    "PUBLIC_BRAND_SEO_KEYWORDS",
    "宇多Yul细胞/yulcell, yulcell, 宇多Yul细胞, 长寿抗衰证据图谱, 健康寿命证据图谱, longevity anti-aging evidence atlas",
)
BRAND_FIELDS = {
    "品牌标识": BRAND_NAME,
    "Brand": BRAND_EN,
    "SEO关键词": BRAND_SEO_KEYWORDS,
    "资产归属": f"{BRAND_NAME} | {BRAND_PROJECT}",
    "GitHub公开入口": BRAND_GITHUB_URL,
}


ASSETS = [
    {
        "asset_key": "literature_library",
        "table_name": f"公开数据_全量文献候选库_{MONTH}",
        "csv": PUBLIC / f"literature-library-{MONTH}.csv",
        "primary_key": "library_id",
        "title_fields": ["title_zh", "title_en", "library_id"],
    },
    {
        "asset_key": "candidate_sources",
        "table_name": f"公开数据_候选来源原始表_{MONTH}",
        "csv": PUBLIC / f"candidate-sources-{MONTH}.csv",
        "primary_key": "id",
        "title_fields": ["title_zh", "title_en", "id"],
    },
    {
        "asset_key": "shortlist_sources",
        "table_name": f"公开数据_入选短名单_{MONTH}",
        "csv": PUBLIC / f"shortlist-sources-{MONTH}.csv",
        "primary_key": "candidate_id",
        "title_fields": ["title_zh", "title_en", "candidate_id"],
    },
    {
        "asset_key": "evidence_findings",
        "table_name": f"公开数据_证据发现表_{MONTH}",
        "csv": PUBLIC / f"evidence-findings-{MONTH}.csv",
        "primary_key": "finding_id",
        "title_fields": ["title_zh", "title_en", "finding_id"],
    },
    {
        "asset_key": "evidence_matrix",
        "table_name": f"公开数据_证据矩阵_{MONTH}",
        "csv": PUBLIC / f"evidence-matrix-{MONTH}.csv",
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


def chunks(items: list[Any], size: int = 100):
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


def branded_public_title(row: dict[str, str], title_fields: list[str], primary_key: str) -> str:
    return normalize(f"{BRAND_NAME} | {public_title(row, title_fields, primary_key)}", max_len=120)


def record_has_brand(record: dict[str, Any]) -> bool:
    fields = record.get("fields", {})
    return all(str(fields.get(name, "")).strip() == value for name, value in BRAND_FIELDS.items())


def ensure_table(client: FeishuClient, app_token: str, table_name: str, fieldnames: list[str]) -> str:
    for table in client.list_bitable_tables(app_token):
        if table.get("name") == table_name:
            return table.get("table_id", "")
    schema = [{"field_name": "公开标题", "type": TEXT_FIELD}]
    schema.extend({"field_name": name, "type": TEXT_FIELD} for name in BRAND_FIELDS)
    schema.extend(
        {"field_name": name, "type": TEXT_FIELD}
        for name in fieldnames
        if name != "公开标题" and name not in BRAND_FIELDS
    )
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
    for field in ["公开标题", *BRAND_FIELDS, *fieldnames]:
        if field in existing:
            continue
        client.create_bitable_text_field(app_token, table_id, field)
        existing.add(field)
        time.sleep(0.15)


def sync_asset(
    client: FeishuClient,
    app_token: str,
    asset: dict[str, Any],
    delete_stale_records: bool = False,
    force_update: bool = False,
    only_keys: set[str] | None = None,
) -> dict[str, Any]:
    rows, fieldnames = read_csv(asset["csv"])
    if asset["primary_key"] not in fieldnames:
        raise FeishuError(f"{asset['csv']} missing primary key {asset['primary_key']}")
    table_id = ensure_table(client, app_token, asset["table_name"], fieldnames)
    ensure_fields(client, app_token, table_id, fieldnames)

    existing = client.list_bitable_records(
        app_token,
        table_id,
        field_names=[asset["primary_key"], *BRAND_FIELDS],
    )
    by_key: dict[str, str] = {}
    record_by_key: dict[str, dict[str, Any]] = {}
    stale_record_ids: list[str] = []
    for record in existing:
        key = normalize(record.get("fields", {}).get(asset["primary_key"], ""), max_len=120)
        record_id = str(record.get("record_id", ""))
        if not key or key in by_key:
            if record_id:
                stale_record_ids.append(record_id)
            continue
        by_key[key] = record_id
        record_by_key[key] = record

    source_keys = {normalize(row.get(asset["primary_key"]), max_len=120) for row in rows if row.get(asset["primary_key"])}
    stale_record_ids.extend(
        record_id
        for key, record_id in by_key.items()
        if key not in source_keys and record_id
    )
    stale_record_ids = list(dict.fromkeys(stale_record_ids))
    if stale_record_ids and not delete_stale_records:
        print(
            f"{asset['asset_key']}: found {len(stale_record_ids)} stale or duplicate records; "
            "rerun with --delete-stale-records to remove them"
        )
    if stale_record_ids and delete_stale_records:
        for index, record_id in enumerate(stale_record_ids, 1):
            client.delete_bitable_record(app_token, table_id, record_id)
            if index % 50 == 0 or index == len(stale_record_ids):
                print(f"{asset['asset_key']}: deleted stale {index}/{len(stale_record_ids)}")

    if (
        not force_update
        and source_keys
        and source_keys.issubset(set(by_key))
        and all(record_has_brand(record_by_key[key]) for key in source_keys)
    ):
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

    rows_to_sync = rows
    if only_keys is not None:
        rows_to_sync = [
            row
            for row in rows
            if normalize(row.get(asset["primary_key"]), max_len=120) in only_keys
        ]
        missing_requested_keys = only_keys - {
            normalize(row.get(asset["primary_key"]), max_len=120)
            for row in rows_to_sync
        }
        if missing_requested_keys:
            print(
                f"{asset['asset_key']}: {len(missing_requested_keys)} requested keys are absent "
                "from the current source and will only be handled by stale cleanup"
            )

    create_payloads: list[dict[str, Any]] = []
    update_payloads: list[dict[str, Any]] = []
    for row in rows_to_sync:
        key = normalize(row.get(asset["primary_key"]), max_len=120)
        if not key:
            continue
        fields = {field: normalize(row.get(field)) for field in fieldnames}
        fields.update(BRAND_FIELDS)
        fields["公开标题"] = branded_public_title(row, asset["title_fields"], asset["primary_key"])
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--delete-stale-records", action="store_true")
    parser.add_argument("--force-update", action="store_true")
    parser.add_argument(
        "--asset",
        action="append",
        choices=[asset["asset_key"] for asset in ASSETS],
        help="Sync only the selected asset key. Repeat to select multiple assets.",
    )
    parser.add_argument(
        "--keys-file",
        type=Path,
        help="UTF-8 file with one primary-key value per line; requires exactly one --asset.",
    )
    args = parser.parse_args()
    if args.keys_file and (not args.asset or len(set(args.asset)) != 1):
        parser.error("--keys-file requires exactly one --asset")
    only_keys = None
    if args.keys_file:
        only_keys = {
            line.strip()
            for line in args.keys_file.read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        }

    load_dotenv(ROOT / ".env")
    client = FeishuClient()
    app_token = client.resolve_bitable_app_token(
        app_token=os.getenv("FEISHU_BITABLE_APP_TOKEN", ""),
        wiki_node_token=os.getenv("FEISHU_BITABLE_WIKI_NODE_TOKEN", ""),
    )

    selected_assets = [
        asset
        for asset in ASSETS
        if not args.asset or asset["asset_key"] in args.asset
    ]
    synced: list[dict[str, Any]] = []
    for asset in selected_assets:
        synced.append(
            sync_asset(
                client,
                app_token,
                asset,
                delete_stale_records=args.delete_stale_records,
                force_update=args.force_update,
                only_keys=only_keys,
            )
        )

    links_path = DATA / f"feishu_full_public_data_links_{MONTH_UNDERSCORE}.csv"
    output_rows = synced
    if args.asset and links_path.exists():
        previous_rows, _ = read_csv(links_path)
        merged = {row.get("asset_key", ""): row for row in previous_rows}
        merged.update({row["asset_key"]: row for row in synced})
        output_rows = [
            merged[asset["asset_key"]]
            for asset in ASSETS
            if asset["asset_key"] in merged
        ]

    write_csv(
        links_path,
        output_rows,
        ["asset_group", "asset_key", "table_id", "url", "rows", "created", "updated", "status"],
    )
    print(f"wrote data/feishu_full_public_data_links_{MONTH_UNDERSCORE}.csv")


if __name__ == "__main__":
    try:
        main()
    except FeishuError as exc:
        raise SystemExit(f"Feishu full public data sync failed: {exc}") from exc
