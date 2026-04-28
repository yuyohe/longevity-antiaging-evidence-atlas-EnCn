"""Remove duplicate and blank records from the Feishu 候选文献 table."""

from __future__ import annotations

import argparse
import os
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv

from feishu_client import FeishuClient, FeishuError

ROOT = Path(__file__).resolve().parents[1]


def field_count(record: Dict) -> int:
    return sum(1 for value in record.get("fields", {}).values() if value not in ("", None, []))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Actually delete records. Without this, only prints a dry run.")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    table_id = os.getenv("FEISHU_CANDIDATE_TABLE_ID", "")
    if not table_id:
        raise SystemExit("Missing FEISHU_CANDIDATE_TABLE_ID.")

    client = FeishuClient()
    app_token = client.resolve_bitable_app_token(
        app_token=os.getenv("FEISHU_BITABLE_APP_TOKEN", ""),
        wiki_node_token=os.getenv("FEISHU_BITABLE_WIKI_NODE_TOKEN", ""),
    )

    records = client.list_bitable_records(app_token, table_id)
    by_id: Dict[str, List[Dict]] = defaultdict(list)
    blank_records: List[Dict] = []
    for record in records:
        candidate_id = str(record.get("fields", {}).get("id") or "").strip()
        if candidate_id:
            by_id[candidate_id].append(record)
        elif not record.get("fields"):
            blank_records.append(record)

    delete_ids: List[str] = []
    for grouped in by_id.values():
        if len(grouped) <= 1:
            continue
        keep = sorted(grouped, key=field_count, reverse=True)[0]
        for record in grouped:
            if record.get("record_id") != keep.get("record_id"):
                delete_ids.append(record.get("record_id", ""))

    delete_ids.extend(record.get("record_id", "") for record in blank_records)
    delete_ids = [record_id for record_id in delete_ids if record_id]

    print(f"records={len(records)} unique_ids={len(by_id)} duplicate_or_blank_to_delete={len(delete_ids)}")
    if not args.execute:
        print("Dry run only. Re-run with --execute to delete.")
        return

    deleted = 0
    for record_id in delete_ids:
        try:
            client.delete_bitable_record(app_token, table_id, record_id)
        except FeishuError as exc:
            if "RecordIdNotFound" not in str(exc):
                raise
            continue
        deleted += 1
        if deleted % 50 == 0:
            print(f"deleted={deleted}")
        time.sleep(0.03)
    print(f"Deleted {deleted} duplicate/blank records.")


if __name__ == "__main__":
    try:
        main()
    except FeishuError as exc:
        raise SystemExit(f"Cleanup failed: {exc}") from exc
