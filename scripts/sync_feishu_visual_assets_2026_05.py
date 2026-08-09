"""Sync visual PNG assets to Feishu Bitable.

This replaces the previous public-table-only layer with image-based heatmaps
and ingredient cards. The old tables are deleted only when
--delete-old-public-tables is passed.
"""

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
DATA_DIR = ROOT / "data"
UPDATE_MONTH = os.environ.get("EVIDENCE_ATLAS_ASSET_MONTH", "2026-05")
UPDATE_MONTH_UNDERSCORE = UPDATE_MONTH.replace("-", "_")

TEXT_FIELD = 1
ATTACHMENT_FIELD = 17

DOC_DOMAIN = "ucngl3rlrux2.feishu.cn"
WIKI_NODE_TOKEN = "WriBw4TXZiOsjQkJWk8ctL1xnVg"
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
REGISTRY_PATH = DATA_DIR / "feishu_table_registry.csv"

OLD_PUBLIC_TABLES = {
    "tblEVNI9nsjU6oT3": "公开资产_索引_2026-05",
    "tblt6sfmnoTR7oe4": "公开资产_前50成分卡片_2026-05",
    "tbl193uCWbvFkZj3": "公开资产_研究热力图_主题年份_2026-05",
    "tblcsHGWOLHvCa1f": "公开资产_研究热力图_证据等级_2026-05",
    "tbl7SCAfeDDuWXv7": "公开资产_月度更新报告_2026-05",
    "tbl06WhmWYhb1IOi": "问答字段设计_2026-05",
    "tbl5in2mRl49uRef": "问答设计A_简单提问入口_2026-05",
    "tblso22SA6Fj7dv1": "问答设计B_研究复核版_2026-05",
    "tblbliMGDNuHX0i9": "问答设计C_公开FAQ候选_2026-05",
    "tblGEnLnoyw1DaWL": "同步链接_2026-05",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


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


def load_registry() -> dict[str, dict[str, str]]:
    return {row["asset_key"]: row for row in read_csv(REGISTRY_PATH) if row.get("asset_key")}


def load_token_cache(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    rows = read_csv(path)
    return {row["local_path"]: row["file_token"] for row in rows if row.get("local_path") and row.get("file_token")}


def save_token_cache(path: Path, cache: dict[str, str]) -> None:
    rows = [{"local_path": key, "file_token": value} for key, value in sorted(cache.items())]
    write_csv(path, rows, ["local_path", "file_token"])


def ensure_table(
    client: FeishuClient,
    app_token: str,
    table_name: str,
    primary_field: str,
    fields: dict[str, int],
    preferred_table_id: str,
    allow_create: bool,
) -> str:
    tables = client.list_bitable_tables(app_token)
    by_id = {str(table.get("table_id", "")): table for table in tables}
    if preferred_table_id:
        table = by_id.get(preferred_table_id)
        if not table:
            if not allow_create:
                raise FeishuError(f"Registered table is missing: {preferred_table_id} ({table_name})")
        else:
            if table.get("name") != table_name:
                client.update_bitable_table(app_token, preferred_table_id, table_name)
                print(f"renamed {preferred_table_id}: {table.get('name')} -> {table_name}")
            return preferred_table_id
    for table in tables:
        if table.get("name") == table_name:
            return str(table.get("table_id", ""))
    if not allow_create:
        raise FeishuError(f"No registered table for {table_name}; pass --allow-create only for a deliberate new asset")
    schema = [{"field_name": primary_field, "type": TEXT_FIELD}]
    for name, field_type in fields.items():
        if name == primary_field:
            continue
        schema.append({"field_name": name, "type": field_type})
    created = client.create_bitable_table(app_token, table_name, "表格", schema)
    table_id = created.get("data", {}).get("table_id") or created.get("data", {}).get("table", {}).get("table_id", "")
    if table_id:
        return table_id
    for table in client.list_bitable_tables(app_token):
        if table.get("name") == table_name:
            return table.get("table_id", "")
    raise FeishuError(f"Failed to create table {table_name}: {created}")


def ensure_fields(client: FeishuClient, app_token: str, table_id: str, fields: dict[str, int]) -> None:
    existing = {field.get("field_name"): field for field in client.list_bitable_fields(app_token, table_id)}
    for name, field_type in fields.items():
        if name in existing:
            continue
        client.create_bitable_field(app_token, table_id, name, field_type)
        time.sleep(0.25)


def upload_asset(client: FeishuClient, app_token: str, cache: dict[str, str], local_path: str) -> str:
    if local_path in cache:
        return cache[local_path]
    full_path = ROOT / local_path
    if not full_path.exists():
        raise FeishuError(f"Missing local asset: {local_path}")
    last_error: Exception | None = None
    for parent_type in ["bitable_file", "bitable_image"]:
        try:
            token = client.upload_bitable_file(app_token, full_path, parent_type=parent_type)
            cache[local_path] = token
            return token
        except Exception as exc:  # noqa: BLE001 - need fallback because Feishu parent_type varies by attachment use.
            last_error = exc
            time.sleep(0.5)
    raise FeishuError(f"Upload failed for {local_path}: {last_error}")


def upsert_records(
    client: FeishuClient,
    app_token: str,
    table_id: str,
    primary_field: str,
    records: list[dict[str, Any]],
    delete_stale_records: bool = False,
) -> tuple[int, int, int]:
    existing = client.list_bitable_records(
        app_token,
        table_id,
        field_names=[primary_field],
    )
    by_key: dict[str, str] = {}
    stale_record_ids: list[str] = []
    for record in existing:
        key = str(record.get("fields", {}).get(primary_field, "")).strip()
        record_id = str(record.get("record_id", ""))
        if not key or key in by_key:
            if record_id:
                stale_record_ids.append(record_id)
            continue
        by_key[key] = record_id

    source_keys = {str(fields.get(primary_field, "")).strip() for fields in records}
    stale_record_ids.extend(
        record_id
        for key, record_id in by_key.items()
        if key not in source_keys and record_id
    )
    stale_record_ids = list(dict.fromkeys(stale_record_ids))
    if stale_record_ids and not delete_stale_records:
        print(
            f"{primary_field}: found {len(stale_record_ids)} stale or duplicate records; "
            "rerun with --delete-stale-records to remove them"
        )
    if stale_record_ids and delete_stale_records:
        for batch in chunks(stale_record_ids, size=500):
            client.batch_delete_bitable_records(app_token, table_id, batch)
            time.sleep(0.25)

    create_payloads: list[dict[str, Any]] = []
    update_payloads: list[dict[str, Any]] = []
    for fields in records:
        key = str(fields.get(primary_field, ""))
        if key in by_key:
            update_payloads.append({"record_id": by_key[key], "fields": fields})
        else:
            create_payloads.append({"fields": fields})

    created = 0
    for batch in chunks(create_payloads):
        client.batch_create_bitable_records(app_token, table_id, batch)
        created += len(batch)
        time.sleep(0.3)

    updated = 0
    for batch in chunks(update_payloads):
        client.batch_update_bitable_records(app_token, table_id, batch)
        updated += len(batch)
        time.sleep(0.3)
    return created, updated, len(stale_record_ids) if delete_stale_records else 0


def attachment(token: str, name: str) -> list[dict[str, str]]:
    return [{"file_token": token, "name": name}]


def add_brand(fields: dict[str, Any]) -> dict[str, Any]:
    fields.update(BRAND_FIELDS)
    return fields


def add_brand_field_schema(fields: dict[str, int]) -> dict[str, int]:
    return {**fields, **{name: TEXT_FIELD for name in BRAND_FIELDS}}


def sync_heatmaps(
    client: FeishuClient,
    app_token: str,
    cache: dict[str, str],
    registry_row: dict[str, str],
    delete_stale_records: bool = False,
    allow_create: bool = False,
) -> tuple[str, int, int, int]:
    table_name = registry_row["stable_name"]
    fields = add_brand_field_schema({
        "标题": TEXT_FIELD,
        "asset_id": TEXT_FIELD,
        "类型": TEXT_FIELD,
        "图片": ATTACHMENT_FIELD,
        "说明": TEXT_FIELD,
        "数据来源": TEXT_FIELD,
        "本地路径": TEXT_FIELD,
        "更新月份": TEXT_FIELD,
    })
    table_id = ensure_table(
        client,
        app_token,
        table_name,
        "标题",
        fields,
        registry_row["table_id"],
        allow_create,
    )
    ensure_fields(client, app_token, table_id, fields)

    rows = []
    for row in read_csv(DATA_DIR / f"visual_heatmap_assets_{UPDATE_MONTH_UNDERSCORE}.csv"):
        if not row.get("asset_id", "").startswith("H"):
            continue
        local_path = row["local_path"]
        token = upload_asset(client, app_token, cache, local_path)
        rows.append(
            add_brand({
                "标题": row["title"],
                "asset_id": row["asset_id"],
                "类型": row["asset_type"],
                "图片": attachment(token, Path(local_path).name),
                "说明": row["description"],
                "数据来源": row["data_source"],
                "本地路径": local_path,
                "更新月份": row["update_month"],
            })
        )
    created, updated, deleted = upsert_records(
        client,
        app_token,
        table_id,
        "标题",
        rows,
        delete_stale_records=delete_stale_records,
    )
    try:
        client.create_bitable_view(app_token, table_id, "图片入口", view_type="gallery")
    except Exception:
        pass
    return table_id, created, updated, deleted


def sync_cards(
    client: FeishuClient,
    app_token: str,
    cache: dict[str, str],
    registry_row: dict[str, str],
    delete_stale_records: bool = False,
    allow_create: bool = False,
) -> tuple[str, int, int, int]:
    table_name = registry_row["stable_name"]
    fields = add_brand_field_schema({
        "成分": TEXT_FIELD,
        "card_id": TEXT_FIELD,
        "英文名": TEXT_FIELD,
        "卡片图": ATTACHMENT_FIELD,
        "健康证据": TEXT_FIELD,
        "皮肤证据": TEXT_FIELD,
        "商业宣传风险": TEXT_FIELD,
        "一句话": TEXT_FIELD,
        "常见误解": TEXT_FIELD,
        "注意": TEXT_FIELD,
        "撤稿记录": TEXT_FIELD,
        "本地路径": TEXT_FIELD,
        "更新月份": TEXT_FIELD,
    })
    table_id = ensure_table(
        client,
        app_token,
        table_name,
        "成分",
        fields,
        registry_row["table_id"],
        allow_create,
    )
    ensure_fields(client, app_token, table_id, fields)

    rows = []
    for row in read_csv(DATA_DIR / f"visual_ingredient_cards_{UPDATE_MONTH_UNDERSCORE}.csv"):
        local_path = row["local_path"]
        token = upload_asset(client, app_token, cache, local_path)
        rows.append(
            add_brand({
                "成分": f"{row['card_id']} {row['name_zh']}",
                "card_id": row["card_id"],
                "英文名": row["name_en"],
                "卡片图": attachment(token, Path(local_path).name),
                "健康证据": row["health_evidence"],
                "皮肤证据": row["skin_evidence"],
                "商业宣传风险": row["commercial_overclaim_risk"],
                "一句话": row["one_sentence"],
                "常见误解": row["common_misunderstanding"],
                "注意": row["attention"],
                "撤稿记录": row["retraction_note"],
                "本地路径": local_path,
                "更新月份": row["update_month"],
            })
        )
    created, updated, deleted = upsert_records(
        client,
        app_token,
        table_id,
        "成分",
        rows,
        delete_stale_records=delete_stale_records,
    )
    for view_name, view_type in [("单卡画廊", "gallery"), ("表格备查", "grid")]:
        try:
            client.create_bitable_view(app_token, table_id, view_name, view_type=view_type)
        except Exception:
            pass
    return table_id, created, updated, deleted


def sync_overview(
    client: FeishuClient,
    app_token: str,
    cache: dict[str, str],
    registry_row: dict[str, str],
    delete_stale_records: bool = False,
    allow_create: bool = False,
) -> tuple[str, int, int, int]:
    table_name = registry_row["stable_name"]
    fields = add_brand_field_schema({
        "标题": TEXT_FIELD,
        "asset_id": TEXT_FIELD,
        "总览图": ATTACHMENT_FIELD,
        "说明": TEXT_FIELD,
        "数据来源": TEXT_FIELD,
        "本地路径": TEXT_FIELD,
        "更新月份": TEXT_FIELD,
    })
    table_id = ensure_table(
        client,
        app_token,
        table_name,
        "标题",
        fields,
        registry_row["table_id"],
        allow_create,
    )
    ensure_fields(client, app_token, table_id, fields)

    heatmap_rows = read_csv(DATA_DIR / f"visual_heatmap_assets_{UPDATE_MONTH_UNDERSCORE}.csv")
    row = next(item for item in heatmap_rows if item["asset_id"] == "C000")
    token = upload_asset(client, app_token, cache, row["local_path"])
    records = [
        add_brand({
            "标题": row["title"],
            "asset_id": row["asset_id"],
            "总览图": attachment(token, Path(row["local_path"]).name),
            "说明": row["description"],
            "数据来源": row["data_source"],
            "本地路径": row["local_path"],
            "更新月份": row["update_month"],
        })
    ]
    created, updated, deleted = upsert_records(
        client,
        app_token,
        table_id,
        "标题",
        records,
        delete_stale_records=delete_stale_records,
    )
    try:
        client.create_bitable_view(app_token, table_id, "总览图片", view_type="gallery")
    except Exception:
        pass
    return table_id, created, updated, deleted


def delete_old_public_tables(client: FeishuClient, app_token: str) -> list[dict[str, str]]:
    tables = {table.get("table_id", ""): table.get("name", "") for table in client.list_bitable_tables(app_token)}
    results: list[dict[str, str]] = []
    for table_id, expected_name in OLD_PUBLIC_TABLES.items():
        actual_name = tables.get(table_id, "")
        if not actual_name:
            results.append({"table_id": table_id, "expected_name": expected_name, "status": "already_missing"})
            continue
        if actual_name != expected_name:
            results.append({"table_id": table_id, "expected_name": expected_name, "status": f"skipped_name_mismatch:{actual_name}"})
            continue
        client.delete_bitable_table(app_token, table_id)
        results.append({"table_id": table_id, "expected_name": expected_name, "status": "deleted"})
        time.sleep(0.5)
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delete-old-public-tables", action="store_true")
    parser.add_argument("--delete-stale-records", action="store_true")
    parser.add_argument(
        "--allow-create",
        action="store_true",
        help="Allow creation only when a registered table is genuinely missing.",
    )
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    client = FeishuClient()
    app_token = client.resolve_bitable_app_token(
        app_token=os.getenv("FEISHU_BITABLE_APP_TOKEN", ""),
        wiki_node_token=os.getenv("FEISHU_BITABLE_WIKI_NODE_TOKEN", ""),
    )

    cache_path = Path(
        os.environ.get(
            "FEISHU_VISUAL_TOKEN_CACHE",
            DATA_DIR / f"visual_feishu_file_tokens_{UPDATE_MONTH_UNDERSCORE}.csv",
        )
    )
    cache = load_token_cache(cache_path)
    registry = load_registry()

    synced: list[dict[str, Any]] = []
    for asset_key, fn in [
        ("heatmaps", sync_heatmaps),
        ("ingredient_cards", sync_cards),
        ("ingredient_wall", sync_overview),
    ]:
        registry_row = registry.get(asset_key)
        if not registry_row:
            raise FeishuError(f"Missing registry entry for {asset_key}")
        name = registry_row["stable_name"]
        table_id, created, updated, deleted = fn(
            client,
            app_token,
            cache,
            registry_row,
            delete_stale_records=args.delete_stale_records,
            allow_create=args.allow_create,
        )
        synced.append(
            {
                "asset_group": name,
                "table_id": table_id,
                "url": table_url(table_id),
                "created": created,
                "updated": updated,
                "deleted": deleted,
                "status": "active",
            }
        )
        print(
            f"synced {name}: table_id={table_id}, created={created}, "
            f"updated={updated}, deleted={deleted}"
        )
        save_token_cache(cache_path, cache)

    delete_results: list[dict[str, str]] = []
    if args.delete_old_public_tables:
        delete_results = delete_old_public_tables(client, app_token)

    write_csv(
        DATA_DIR / f"visual_feishu_links_{UPDATE_MONTH_UNDERSCORE}.csv",
        synced,
        ["asset_group", "table_id", "url", "created", "updated", "deleted", "status"],
    )
    write_csv(
        DATA_DIR / f"visual_feishu_deleted_old_tables_{UPDATE_MONTH_UNDERSCORE}.csv",
        delete_results,
        ["table_id", "expected_name", "status"],
    )
    print(f"wrote data/visual_feishu_links_{UPDATE_MONTH_UNDERSCORE}.csv")
    if delete_results:
        print(f"deleted_or_checked_old_tables={len(delete_results)}")


if __name__ == "__main__":
    try:
        main()
    except FeishuError as exc:
        raise SystemExit(f"Feishu visual sync failed: {exc}") from exc
