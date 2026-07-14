"""Read-only online audit for the 2026-07 Feishu Bitable release."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from dotenv import load_dotenv

from feishu_client import FeishuClient


ROOT = Path(__file__).resolve().parents[1]
BRAND_ZH = "宇多Yul细胞/yulcell"
BRAND_EN = "yulcell"
MONTH = "2026-07"
GITHUB_URL = "https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def table_id_from_url(url: str) -> str:
    return parse_qs(urlparse(url).query).get("table", [""])[0]


def text_value(value: object) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def audit_table(
    client: FeishuClient,
    app_token: str,
    manifest_row: dict[str, str],
    table_meta: dict[str, object],
) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    table_name = manifest_row["表名"]
    table_id = table_id_from_url(manifest_row["飞书链接"])
    expected_count = int(manifest_row["记录数"])

    if table_meta.get("name") != table_name:
        errors.append(f"{table_id}: expected name {table_name!r}, found {table_meta.get('name')!r}")

    fields = client.list_bitable_fields(app_token, table_id)
    field_names = [str(field.get("field_name", "")) for field in fields]
    for required in ["品牌标识", "Brand", "SEO关键词"]:
        if required not in field_names:
            errors.append(f"{table_name}: missing field {required}")

    records = client.list_bitable_records(app_token, table_id)
    if len(records) != expected_count:
        errors.append(f"{table_name}: expected {expected_count} records, found {len(records)}")

    primary_field = field_names[0] if field_names else ""
    primary_values: list[str] = []
    brand_coverage = 0
    github_coverage = 0
    attachment_coverage = 0
    broken_text_records = 0
    for item in records:
        values = item.get("fields", {})
        if not isinstance(values, dict):
            errors.append(f"{table_name}: record fields payload is not an object")
            continue
        primary_values.append(text_value(values.get(primary_field, "")).strip())
        if values.get("品牌标识") == BRAND_ZH and values.get("Brand") == BRAND_EN and "yulcell" in str(values.get("SEO关键词", "")).lower():
            brand_coverage += 1
        if values.get("GitHub公开入口") == GITHUB_URL or str(values.get("GitHub链接", "")).startswith(GITHUB_URL):
            github_coverage += 1
        if any(values.get(name) for name in ["图片", "卡片图", "总览图"]):
            attachment_coverage += 1
        serialized = json.dumps(values, ensure_ascii=False, sort_keys=True)
        if "�" in serialized or "瀹囧" in serialized or re.search(r"\?{3,}", serialized):
            broken_text_records += 1

    if brand_coverage != len(records):
        errors.append(f"{table_name}: brand coverage {brand_coverage}/{len(records)}")
    if any(not value for value in primary_values):
        errors.append(f"{table_name}: blank primary field {primary_field!r}")
    if len(primary_values) != len(set(primary_values)):
        errors.append(f"{table_name}: duplicate primary values in {primary_field!r}")
    if broken_text_records:
        errors.append(f"{table_name}: {broken_text_records} records contain mojibake/question-mark runs")

    category = manifest_row.get("类别", "")
    if category == "公开全量数据" and github_coverage != len(records):
        errors.append(f"{table_name}: GitHub link coverage {github_coverage}/{len(records)}")
    if category == "视觉资产" and attachment_coverage != len(records):
        errors.append(f"{table_name}: attachment coverage {attachment_coverage}/{len(records)}")
    if category == "阅读入口":
        for item in records:
            values = item.get("fields", {})
            if values.get("冻结日期") != "2026-07-14" or values.get("复核日期") != "2026-07-14":
                errors.append(f"{table_name}: navigation dates are not 2026-07-14")
                break

    result = {
        "table_id": table_id,
        "table_name": table_name,
        "expected_records": expected_count,
        "actual_records": len(records),
        "field_count": len(field_names),
        "primary_field": primary_field,
        "brand_coverage": brand_coverage,
        "github_link_coverage": github_coverage,
        "attachment_coverage": attachment_coverage,
        "broken_text_records": broken_text_records,
        "status": "passed" if not errors else "failed",
    }
    return result, errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data" / "feishu_live_tables_2026_07.csv")
    parser.add_argument("--report", type=Path, default=ROOT / "build" / "feishu_online_audit_2026_07.json")
    args = parser.parse_args()

    load_dotenv(args.env_file)
    client = FeishuClient()
    app_token = client.resolve_bitable_app_token(
        app_token=os.getenv("FEISHU_BITABLE_APP_TOKEN", ""),
        wiki_node_token=os.getenv("FEISHU_BITABLE_WIKI_NODE_TOKEN", ""),
    )
    manifest = read_csv(args.manifest)
    if len(manifest) != 9:
        raise RuntimeError(f"Expected 9 manifest rows, found {len(manifest)}")

    table_catalog = {str(item.get("table_id")): item for item in client.list_bitable_tables(app_token)}
    all_errors: list[str] = []
    results: list[dict[str, object]] = []
    for index, row in enumerate(manifest, 1):
        table_id = table_id_from_url(row["飞书链接"])
        metadata = table_catalog.get(table_id)
        if not metadata:
            all_errors.append(f"missing online table: {table_id}")
            continue
        result, errors = audit_table(client, app_token, row, metadata)
        results.append(result)
        all_errors.extend(errors)
        print(f"[{index}/9] {result['table_name']}: {result['actual_records']} records, {result['status']}")

    report = {
        "audit_version": "2026-07-release-v1",
        "audited_at_utc": datetime.now(timezone.utc).isoformat(),
        "snapshot_date": "2026-07-14",
        "manifest": str(args.manifest.resolve()),
        "tables": results,
        "errors": all_errors,
        "status": "passed" if not all_errors and len(results) == 9 else "failed",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if report["status"] != "passed":
        print("Feishu online audit failed:")
        for error in all_errors:
            print(f"- {error}")
        sys.exit(1)
    print("Feishu online audit passed: 9/9 tables, exact counts, full brand coverage, no mojibake.")


if __name__ == "__main__":
    main()
