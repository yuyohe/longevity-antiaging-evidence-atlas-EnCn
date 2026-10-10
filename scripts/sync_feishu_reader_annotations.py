"""Add in-place field help and visual captions; never change evidence or permissions.

API schema: https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-field/update
Description model: larksuite/oapi-sdk-python, AppTableFieldDescription.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from feishu_client import FeishuClient
from reader_annotations import FIELD_HELP, VISUAL_NOTES

ROOT = Path(__file__).resolve().parents[1]
HELP_PREFIX = "宇多Yul细胞读表提示："
ASSET_HELP = {
    "literature_library": "找论文的目录，不是已验证结论。与候选表重叠，不能相加当论文数。 / Literature index, not validation.",
    "candidate_sources": "检索找到的来源，进入候选不等于确认功效。与文献库重叠。 / Search candidates, not efficacy.",
    "shortlist_sources": "优先检查的记录，不等于已读完全文或已证明有效。 / Prioritized review, not approval.",
    "evidence_findings": "自动或摘要整理的待复核笔记；发现不等于证实的人体功效。 / Draft extraction, not proven benefit.",
    "evidence_matrix": "有容量上限的比较层，不是全球研究全集或购买榜。 / Bounded comparison layer.",
    "heatmaps": "当前研究结构，先看说明列中的范围、分母、日期。颜色深不等于有效。 / Research structure, not efficacy.",
    "ingredient_cards": "场景级暂定汇总；健康寿命和皮肤用途分开看，不是购买清单。 / Provisional context summary.",
    "ingredient_wall": "50张成分卡的索引，不是成分排行。新图不等于评级重审。 / Visual index, not ranking.",
    "reader_navigation": "14个可选入口，先选自己的问题，不必逐项读完。 / Optional reader entries.",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def description_text(field: dict) -> str:
    description = field.get("description") or ""
    return description.get("text", "") if isinstance(description, dict) else str(description)


def help_update(field: dict, note: str) -> str | None:
    existing = description_text(field)
    desired = HELP_PREFIX + note
    if existing == desired or (existing and not existing.startswith(HELP_PREFIX)):
        return None
    return desired


def stable_record_fields(fields: dict) -> dict:
    """Signed attachment URLs may refresh; file identity and other fields must not."""
    result = dict(fields)
    for name, value in fields.items():
        if isinstance(value, list) and value and all(isinstance(item, dict) and "file_token" in item for item in value):
            result[name] = [{key: item[key] for key in item if key not in {"url", "tmp_url"}} for item in value]
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Default is read-only planning")
    args = parser.parse_args()
    config = json.loads((ROOT / "data/current_release.json").read_text(encoding="utf-8"))
    month = config["EVIDENCE_ATLAS_ASSET_MONTH"]
    load_dotenv(ROOT / ".env")
    client = FeishuClient()
    app = client.resolve_bitable_app_token(os.getenv("FEISHU_BITABLE_APP_TOKEN", ""),
                                          os.getenv("FEISHU_BITABLE_WIKI_NODE_TOKEN", ""))
    registry = read_rows(ROOT / "data/feishu_table_registry.csv")
    if len(registry) != 9 or len({row["table_id"] for row in registry}) != 9:
        raise RuntimeError("Expected nine stable tables")
    manifest = read_rows(ROOT / f"data/visual_heatmap_assets_{month.replace('-', '_')}.csv")
    notes = {row["asset_id"]: VISUAL_NOTES[Path(row["local_path"]).name.removesuffix(f"-{month}.png")]
             for row in manifest}
    receipt = {"date": config["EVIDENCE_ATLAS_UPDATE_DATE"], "apply": args.apply,
               "tables": [], "updated_fields": 0, "verified_fields": 0, "updated_captions": 0}
    for asset in registry:
        key, table_id = asset["asset_key"], asset["table_id"]
        before_fields = client.list_bitable_fields(app, table_id)
        expected = {}
        for field in before_fields:
            note = ASSET_HELP[key] if field.get("is_primary") else FIELD_HELP.get(field["field_name"])
            if not note or field["type"] not in (1, 17):
                continue
            description = help_update(field, note)
            if description:
                print(f"{'Updating' if args.apply else 'Would update'} {key}: {field['field_name']}", flush=True)
                if args.apply:
                    client.update_bitable_field_description(app, table_id, field, description)
                    receipt["updated_fields"] += 1
                expected[field["field_id"]] = description
            elif description_text(field).startswith(HELP_PREFIX):
                expected[field["field_id"]] = HELP_PREFIX + note
        after_fields = client.list_bitable_fields(app, table_id) if args.apply else before_fields
        if args.apply:
            actual = {field["field_id"]: field for field in after_fields}
            for old in before_fields:
                new = actual[old["field_id"]]
                for attribute in ("field_name", "type", "is_primary", "is_hidden", "property"):
                    if new.get(attribute) != old.get(attribute):
                        raise RuntimeError(f"Field schema changed: {key}/{old['field_name']}/{attribute}")
            for field_id, description in expected.items():
                if description_text(actual[field_id]) != description:
                    raise RuntimeError(f"Field help read-back mismatch: {key}/{actual[field_id]['field_name']}")
                receipt["verified_fields"] += 1
        table_receipt = {"asset": key, "help_fields": len(expected)}
        if key in {"heatmaps", "ingredient_wall"}:
            before = client.list_bitable_records(app, table_id)
            updates = []
            for record in before:
                fields = record.get("fields", {})
                note = notes.get(fields.get("asset_id", ""))
                if not note:
                    raise RuntimeError(f"Missing visual annotation: {key}")
                if fields.get("说明") != note:
                    updates.append({"record_id": record["record_id"], "fields": {"说明": note}})
            if args.apply and updates:
                client.batch_update_bitable_records(app, table_id, updates)
                receipt["updated_captions"] += len(updates)
            if args.apply:
                after = {record["record_id"]: record["fields"] for record in client.list_bitable_records(app, table_id)}
                if set(after) != {record["record_id"] for record in before}:
                    raise RuntimeError("Visual record set changed")
                for record in before:
                    expected_fields = {**record["fields"], "说明": notes[record["fields"]["asset_id"]]}
                    actual_fields = stable_record_fields(after[record["record_id"]])
                    expected_fields = stable_record_fields(expected_fields)
                    if actual_fields != expected_fields:
                        changed = sorted(name for name in set(actual_fields) | set(expected_fields)
                                         if actual_fields.get(name) != expected_fields.get(name))
                        raise RuntimeError(f"Visual fields changed unexpectedly: {key}/{changed}")
            table_receipt["captions"] = len(before)
        receipt["tables"].append(table_receipt)
    if args.apply:
        table = next(row for row in registry if row["asset_key"] == "reader_navigation")
        nav_source = {row["entry_id"]: row for row in read_rows(ROOT / f"data/feishu_reader_navigation_{month.replace('-', '_')}.csv")}
        nav_online = client.list_bitable_records(app, table["table_id"])
        if len(nav_online) != 14 or {r["fields"]["entry_id"] for r in nav_online} != set(nav_source):
            raise RuntimeError("Navigation must retain exactly fourteen entries")
        for record in nav_online:
            for field in ("先看什么 / Start with", "避免误读 / Do not infer"):
                if record["fields"].get(field) != nav_source[record["fields"]["entry_id"]][field]:
                    raise RuntimeError(f"Navigation annotation mismatch: {field}")
        receipt["verified_navigation_rows"] = len(nav_online)
        view_name = "普通读者图例 / Reader notes"
        views = client.list_bitable_views(app, table["table_id"])
        matching = [view for view in views if view["view_name"] == view_name]
        if len(matching) > 1:
            raise RuntimeError("Duplicate reader-note views")
        view = matching[0] if matching else client.create_bitable_view(app, table["table_id"], view_name)["data"]["view"]
        fields = client.list_bitable_fields(app, table["table_id"])
        visible = {"公开标题", "先看什么 / Start with", "避免误读 / Do not infer"}
        hidden = [field["field_id"] for field in fields if field["field_name"] not in visible]
        client.set_bitable_view_hidden_fields(app, table["table_id"], view["view_id"], hidden)
        table["url"] = table["url"].split("&view=")[0] + "&view=" + view["view_id"]
        with (ROOT / "data/feishu_table_registry.csv").open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(registry[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(registry)
        receipt["reader_view"] = {"id": view["view_id"], "name": view_name, "visible_columns": sorted(visible), "url": table["url"]}
    receipt["status"] = "passed" if args.apply else "planned"
    output = ROOT / f"output/reader-annotations-{receipt['date']}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
