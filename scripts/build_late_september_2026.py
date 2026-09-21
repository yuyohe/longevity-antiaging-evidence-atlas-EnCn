"""Rebuild the frozen September 21 release using the existing builders."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES = {
    "core": [
        ["apply_evidence_scoring_v04.py"],
        ["build_healthspan_outputs_v05.py", "--matrix-limit", "1500", "--matrix-per-topic-cap", "100"],
        ["implement_methods_ab.py"],
        ["build_reader_friendly_layer.py"],
        ["enhance_feishu_plain_language_fields.py"],
        ["build_easy_reader_layer.py"],
        ["build_public_full_data_package_2026_05.py"],
        ["build_monthly_update_2026_06.py"],
        ["build_index.py"],
    ],
    "visuals": [
        ["refresh_ingredient_card_sources.py"],
        ["build_evidence_yield_assets_2026_05.py"],
        ["build_visual_feishu_assets_2026_05.py"],
        ["build_mid_august_curated_report_2026_08.py"],
        ["build_posting_asset_dashboard_2026_06.py"],
    ],
    "exports": [["prepare_feishu_docs.py"]],
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=STAGES)
    args = parser.parse_args()
    env = dict(os.environ)
    env.update(json.loads((ROOT / "data/release_config_2026_09_late.json").read_text(encoding="utf-8")))
    shutil.copyfile(ROOT / env["EVIDENCE_ATLAS_CURATION_METRICS"], ROOT / "data/curation_release_metrics_2026_09.json")
    for command in STAGES[args.stage]:
        print(f"Running {command[0]}", flush=True)
        subprocess.run([sys.executable, "-u", "-X", "utf8", str(ROOT / "scripts" / command[0]), *command[1:]],
                       cwd=ROOT, env=env, check=True)


if __name__ == "__main__":
    main()
