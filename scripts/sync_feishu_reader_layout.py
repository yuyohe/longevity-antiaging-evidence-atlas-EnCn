"""Rename the nine current tables for readers, preserving IDs and all records."""

import argparse
import json
import os
from pathlib import Path

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
    for row in rows:
        if row["table_id"] not in before:
            raise RuntimeError("Missing registered table; will not create replacements")
        existing = before[row["table_id"]]["name"]
        if existing != row["stable_name"]:
            print(f"{existing} -> {row['stable_name']}", flush=True)
            if args.apply:
                client.update_bitable_table(app, row["table_id"], row["stable_name"])
            receipt["renamed"].append({"id": row["table_id"], "before": existing, "after": row["stable_name"]})
    if args.apply:
        after = {row["table_id"]: row for row in client.list_bitable_tables(app)}
        if set(before) != set(after):
            raise RuntimeError("Reorganization must not add or remove data tables")
        if any(after[row["table_id"]]["name"] != row["stable_name"] for row in rows):
            raise RuntimeError("Table name read-back mismatch")
        receipt["status"] = "passed"
    else:
        receipt["status"] = "planned"
    output = ROOT / f"output/reader-layout-{layout['organized_on']}.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
