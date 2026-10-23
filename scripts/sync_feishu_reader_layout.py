"""Maintain reader table names and concise views without altering records."""

import argparse
import csv
import json
import os
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from dotenv import load_dotenv

from build_reader_home import load_registry, ordered_registry
from feishu_client import FeishuClient

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    layout = json.loads((ROOT / "data/reader_layout.json").read_text(encoding="utf-8"))
    rows = ordered_registry(load_registry(), layout)
    load_dotenv(ROOT / ".env")
    client = FeishuClient()
    app = client.resolve_bitable_app_token(os.getenv("FEISHU_BITABLE_APP_TOKEN", ""), os.getenv("FEISHU_BITABLE_WIKI_NODE_TOKEN", ""))
    before = {row["table_id"]: row for row in client.list_bitable_tables(app)}
    receipt = {"date": layout["organized_on"], "applied": args.apply, "renamed": [], "total_tables_before": len(before)}
    receipt["reader_views"] = []
    for row in rows:
        if row["table_id"] not in before:
            raise RuntimeError("Missing registered table; will not create replacements")
        existing = before[row["table_id"]]["name"]
        if existing != row["stable_name"]:
            print(f"{existing} -> {row['stable_name']}", flush=True)
            if args.apply:
                client.update_bitable_table(app, row["table_id"], row["stable_name"])
            receipt["renamed"].append({"id": row["table_id"], "before": existing, "after": row["stable_name"]})
        spec = layout.get("reader_views", {}).get(row["asset_key"])
        if spec:
            fields = client.list_bitable_fields(app, row["table_id"])
            visible = set(spec["visible_fields"])
            if visible - {field["field_name"] for field in fields}:
                raise RuntimeError(f"Reader view references missing fields: {row['asset_key']}")
            views = client.list_bitable_views(app, row["table_id"])
            matches = [view for view in views if view["view_name"] == spec["name"]]
            if len(matches) > 1:
                raise RuntimeError("Duplicate reader views")
            if args.apply:
                view = matches[0] if matches else client.create_bitable_view(app, row["table_id"], spec["name"])["data"]["view"]
                hidden = [field["field_id"] for field in fields if field["field_name"] not in visible and not field.get("is_primary")]
                client.set_bitable_view_hidden_fields(app, row["table_id"], view["view_id"], hidden)
                after_views = client.list_bitable_views(app, row["table_id"])
                if not {v["view_id"] for v in views}.issubset({v["view_id"] for v in after_views}):
                    raise RuntimeError("Existing views must be preserved")
                url = urlsplit(row["url"])
                query = dict(parse_qsl(url.query))
                query["view"] = view["view_id"]
                row["url"] = urlunsplit((url.scheme, url.netloc, url.path, urlencode(query), url.fragment))
                receipt["reader_views"].append({"asset": row["asset_key"], "view_id": view["view_id"], "url": row["url"], "visible_fields": spec["visible_fields"]})
    if args.apply:
        after = {row["table_id"]: row for row in client.list_bitable_tables(app)}
        if set(before) != set(after):
            raise RuntimeError("Reorganization must not add or remove data tables")
        if any(after[row["table_id"]]["name"] != row["stable_name"] for row in rows):
            raise RuntimeError("Table name read-back mismatch")
        with (ROOT / "data/feishu_table_registry.csv").open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        receipt["status"] = "passed"
    else:
        receipt["status"] = "planned"
    output = ROOT / f"output/reader-layout-{layout['organized_on']}.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
