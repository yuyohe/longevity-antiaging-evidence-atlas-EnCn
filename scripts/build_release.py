"""Run the established build stages from one current-release configuration."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from build_late_september_2026 import STAGES

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=[*STAGES, "identifiers", "delta", "sync", "audit", "validate"])
    parser.add_argument("--config", type=Path, default=ROOT / "data/current_release.json")
    args = parser.parse_args()
    env = dict(os.environ)
    env.update(json.loads(args.config.read_text(encoding="utf-8")))
    month = env["EVIDENCE_ATLAS_ASSET_MONTH"]
    month_key = month.replace("-", "_")
    delta = ROOT / "output" / f"feishu-delta-{month}"
    env["FEISHU_VISUAL_TOKEN_CACHE"] = str(delta / f"visual_tokens_{month_key}.csv")
    sync_commands = [
        ["sync_feishu_full_public_data_2026_05.py", "--asset", key, "--keys-file", str(delta / f"{key}.txt"),
         "--delete-stale-records", "--force-update"]
        for key in ["literature_library", "candidate_sources", "shortlist_sources", "evidence_findings", "evidence_matrix"]
    ]
    sync_commands += [["sync_feishu_visual_assets_2026_05.py", "--delete-stale-records"],
                     ["sync_feishu_csv_table.py", "--csv", f"data/feishu_reader_navigation_{month_key}.csv",
                      "--table-id", "tbljh1Xmkn6RYWPD", "--table-name", "宇多Yul细胞_当前阅读导航",
                      "--primary-key", "entry_id", "--primary-field", "公开标题", "--delete-stale", "--rename-existing"]]
    commands = {
        **STAGES,
        "identifiers": [["repair_pubmed_article_ids_2026_08.py"]],
        "delta": [["prepare_feishu_delta.py"]],
        "sync": sync_commands,
        "audit": [["audit_feishu_public_release_2026_09.py"]],
        "validate": [["validate_public_release.py"]],
    }[args.stage]
    for command in commands:
        print(f"Running {command[0]}", flush=True)
        subprocess.run([sys.executable, "-u", "-X", "utf8", str(ROOT / "scripts" / command[0]), *command[1:]],
                       cwd=ROOT, env=env, check=True)


if __name__ == "__main__":
    main()
