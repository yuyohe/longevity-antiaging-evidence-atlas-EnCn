"""Append a GitHub/Feishu publishing event to Feishu 发布日志."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

from feishu_client import FeishuClient, FeishuError

ROOT = Path(__file__).resolve().parents[1]
TODAY = os.environ.get("EVIDENCE_ATLAS_UPDATE_DATE", "2026-04-29")


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
    changed_items = os.getenv(
        "FEISHU_PUBLISH_CHANGED_ITEMS",
        "Methods A/B implementation: full literature library, core review queue, PICO/PECO framework, claim-level grading, methodology appraisal plan, Feishu tables synced",
    )
    notes = os.getenv(
        "FEISHU_PUBLISH_NOTES",
        "Full literature library is visible in Feishu; A/B topic review workflow and claim-level grading tables are available for manual review and lock/downgrade decisions.",
    )
    client.create_bitable_record(
        app_token,
        table_id,
        {
            "publish_id": f"publish-{TODAY}-{commit or 'working'}",
            "date": TODAY,
            "target": "GitHub + Feishu Base + Feishu Docs package",
            "source_commit": commit,
            "changed_items": changed_items,
            "status": "success",
            "notes": notes,
        },
    )
    print("Feishu publish log synced.")


if __name__ == "__main__":
    try:
        main()
    except FeishuError as exc:
        raise SystemExit(f"Feishu publish log sync failed: {exc}") from exc
