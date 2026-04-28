"""Append a GitHub/Feishu publishing event to Feishu 发布日志."""

from __future__ import annotations

import os
import subprocess
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from feishu_client import FeishuClient, FeishuError

ROOT = Path(__file__).resolve().parents[1]


def git_commit() -> str:
    for git in ["git", r"C:\Program Files\Git\cmd\git.exe"]:
        try:
            return subprocess.check_output([git, "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
        except Exception:
            continue
    return ""


def main() -> None:
    load_dotenv(ROOT / ".env")
    table_id = os.getenv("FEISHU_PUBLISH_LOG_TABLE_ID", "")
    if not table_id:
        raise SystemExit("Missing FEISHU_PUBLISH_LOG_TABLE_ID.")
    client = FeishuClient()
    app_token = client.resolve_bitable_app_token(
        app_token=os.getenv("FEISHU_BITABLE_APP_TOKEN", ""),
        wiki_node_token=os.getenv("FEISHU_BITABLE_WIKI_NODE_TOKEN", ""),
    )
    fields = ["publish_id", "date", "target", "source_commit", "changed_items", "status", "notes"]
    existing_fields = {field.get("field_name") for field in client.list_bitable_fields(app_token, table_id)}
    for field in fields:
        if field not in existing_fields:
            client.create_bitable_text_field(app_token, table_id, field)

    commit = git_commit()
    client.create_bitable_record(
        app_token,
        table_id,
        {
            "publish_id": f"publish-{date.today()}-{commit or 'working'}",
            "date": str(date.today()),
            "target": "GitHub + Feishu Base + Feishu Docs package",
            "source_commit": commit,
            "changed_items": "v0.1 public draft: 60 findings, 20 topics, 60 paper cards, 30 evidence matrix rows",
            "status": "success",
            "notes": "Draft publication package generated; Feishu Docs API publishing not enabled, Markdown package prepared.",
        },
    )
    print("Feishu publish log synced.")


if __name__ == "__main__":
    try:
        main()
    except FeishuError as exc:
        raise SystemExit(f"Feishu publish log sync failed: {exc}") from exc
