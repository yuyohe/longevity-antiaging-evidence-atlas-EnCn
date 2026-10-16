"""Run the established build stages from one current-release configuration."""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from build_late_september_2026 import STAGES
from release_baseline import baseline_rows

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
    date = env["EVIDENCE_ATLAS_UPDATE_DATE"]
    delta = ROOT / "output" / f"feishu-delta-{date}"
    env["FEISHU_DELTA_DIR"] = str(delta)
    env["FEISHU_VISUAL_TOKEN_CACHE"] = str(delta / f"visual_tokens_{date}.csv")
    metrics = ROOT / env["EVIDENCE_ATLAS_CURATION_METRICS"]
    alias = ROOT / f"data/curation_release_metrics_{month_key}.json"
    if metrics.exists() and json.loads(metrics.read_text(encoding="utf-8"))["date"] != date:
        raise RuntimeError("Configuration and metrics dates differ; restore a frozen release before rebuilding historical assets")
    if args.stage == "core":
        notes = json.loads((ROOT / env["EVIDENCE_ATLAS_FEATURED_NOTES"]).read_text(encoding="utf-8"))
        for asset in ["candidate_sources", "evidence_findings"]:
            path = ROOT / "data" / f"{asset}.csv"
            with path.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                fields, rows = reader.fieldnames, list(reader)
            for row in rows:
                note = notes.get(row.get("pmid"))
                if not note or not note.get("paper_title_zh"):
                    continue
                if asset == "evidence_findings" and row.get("review_status", "").startswith("reviewed_"):
                    continue
                row["title_zh"] = note["paper_title_zh"]
                if asset == "evidence_findings":
                    row["result_zh"] = "摘要解读（全文待复核）：" + note["interpretation_zh"]
                    row["conclusion_zh"] = note["conclusion_zh"]
                    row["translation_status"] = "selected_abstract_interpretation_zh_full_text_pending"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
        release = json.loads(metrics.read_text(encoding="utf-8"))
        turnover = {}
        for asset, key in [("candidate_sources", "id"), ("evidence_findings", "finding_id")]:
            before = {row[key] for row in baseline_rows(ROOT, env, asset)}
            with (ROOT / "data" / f"{asset}.csv").open(encoding="utf-8-sig", newline="") as handle:
                after = {row[key] for row in csv.DictReader(handle)}
            turnover[asset] = {"before": len(before), "after": len(after),
                               "old_removed": len(before - after), "new_active": len(after - before),
                               "net_change": len(after) - len(before)}
        release["active_turnover"] = turnover
        metrics.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if metrics.exists() and metrics != alias:
        shutil.copyfile(metrics, alias)
    sync_commands = [
        ["sync_feishu_full_public_data_2026_05.py", "--asset", key, "--keys-file", str(delta / f"{key}.txt"),
         "--delete-stale-records", "--force-update"]
        for key in ["literature_library", "candidate_sources", "shortlist_sources", "evidence_findings", "evidence_matrix"]
    ]
    sync_commands += [["sync_feishu_visual_assets_2026_05.py", "--delete-stale-records"],
                     ["sync_feishu_csv_table.py", "--csv", f"data/feishu_reader_navigation_{month_key}.csv",
                      "--table-id", "tbljh1Xmkn6RYWPD", "--table-name", "宇多Yul细胞_当前阅读导航",
                      "--primary-key", "entry_id", "--primary-field", "公开标题", "--delete-stale", "--rename-existing"]]
    if (ROOT / "data/reader_layout.json").exists():
        layout = json.loads((ROOT / "data/reader_layout.json").read_text(encoding="utf-8"))
        nav_command = sync_commands[-1]
        nav_command[nav_command.index("--table-name") + 1] = layout["table_names"]["reader_navigation"]
    commands = {
        **STAGES,
        "identifiers": [["repair_pubmed_article_ids_2026_08.py"]],
        "delta": [["prepare_feishu_delta.py"]],
        "sync": sync_commands,
        "audit": [["audit_feishu_public_release_2026_09.py"]],
        "validate": [["validate_public_release.py", "--config", str(args.config)]],
    }[args.stage]
    for command in commands:
        print(f"Running {command[0]}", flush=True)
        subprocess.run([sys.executable, "-u", "-X", "utf8", str(ROOT / "scripts" / command[0]), *command[1:]],
                       cwd=ROOT, env=env, check=True)
        if args.stage == "core" and command[0] == "apply_evidence_scoring_v04.py":
            release = json.loads(metrics.read_text(encoding="utf-8"))
            with (ROOT / "data/evidence_findings.csv").open(encoding="utf-8-sig", newline="") as handle:
                findings = {row["candidate_id"]: row for row in csv.DictReader(handle)}
            for example in release.get("recent_selected_examples", []):
                row = findings[example["candidate_id"]]
                example.update(title_en=row["title_en"], study_type=row["study_type_draft"],
                               draft_level=row["final_evidence_level"])
            metrics.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if metrics != alias:
                shutil.copyfile(metrics, alias)


if __name__ == "__main__":
    main()
