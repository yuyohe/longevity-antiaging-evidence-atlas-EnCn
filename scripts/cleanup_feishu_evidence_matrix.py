from __future__ import annotations

import csv
import os
import time
from pathlib import Path

from dotenv import load_dotenv

from feishu_client import FeishuClient, FeishuError

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "data" / "evidence_matrix.csv"


def main() -> None:
    load_dotenv(ROOT / ".env")
    table_id = os.getenv("FEISHU_SOURCE_TABLE_ID", "")
    if not table_id:
        raise SystemExit("Missing FEISHU_SOURCE_TABLE_ID.")
    with MATRIX.open("r", encoding="utf-8-sig", newline="") as f:
        valid_ids = {row["paper_id"] for row in csv.DictReader(f) if row.get("paper_id")}

    client = FeishuClient()
    app_token = client.resolve_bitable_app_token(
        app_token=os.getenv("FEISHU_BITABLE_APP_TOKEN", ""),
        wiki_node_token=os.getenv("FEISHU_BITABLE_WIKI_NODE_TOKEN", ""),
    )
    records = client.list_bitable_records(app_token, table_id)
    seen: set[str] = set()
    delete_ids: list[str] = []
    keep = 0
    for record in records:
        record_id = record.get("record_id", "")
        fields = record.get("fields", {})
        paper_id = str(fields.get("paper_id") or "").strip()
        if not paper_id or paper_id not in valid_ids or paper_id in seen:
            if record_id:
                delete_ids.append(record_id)
            continue
        seen.add(paper_id)
        keep += 1

    deleted = 0
    for record_id in delete_ids:
        client.delete_bitable_record(app_token, table_id, record_id)
        deleted += 1
        if deleted % 100 == 0:
            print(f"deleted={deleted}/{len(delete_ids)}")
        time.sleep(0.03)
    print(f"Evidence matrix cleanup complete: total={len(records)}, kept={keep}, deleted={deleted}, expected={len(valid_ids)}")


if __name__ == "__main__":
    try:
        main()
    except FeishuError as exc:
        raise SystemExit(f"Evidence matrix cleanup failed: {exc}") from exc
