"""Validate the configured current release without copying a monthly validator."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from PIL import Image

import archive_legacy_visuals as visual_archive
import archive_public_snapshots as csv_archive
import validate_public_release_2026_09 as shared

ROOT = Path(__file__).resolve().parents[1]
read_csv = shared.read_csv


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--config", type=Path, default=ROOT / "data/current_release.json")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    month = config["EVIDENCE_ATLAS_ASSET_MONTH"]
    key = month.replace("-", "_")
    date = config["EVIDENCE_ATLAS_UPDATE_DATE"]
    metrics = json.loads((ROOT / config["EVIDENCE_ATLAS_RELEASE_METRICS"]).read_text(encoding="utf-8"))
    nc, nf = metrics["after"]["candidate_records"], metrics["after"]["finding_records"]
    expected = {"candidate-sources": (nc, "id"), "literature-library": (nc, "library_id"),
                "shortlist-sources": (nf, "candidate_id"), "evidence-findings": (nf, "finding_id"),
                "evidence-matrix": (1500, "paper_id")}
    errors = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    shared.MONTH, shared.SNAPSHOT_DATE = month, date
    shared.EXPECTED, shared.EXPECTED_TOTAL = expected, 2 * nc + 2 * nf + 1500
    shared.validate_public_tables(errors)
    shared.validate_active_curation(errors)
    shared.validate_refreshed_sources(errors)
    require(metrics["date"] == date, "Metrics snapshot date is stale")
    for name, count, field in [("candidate_sources", nc, "candidate_records"), ("evidence_findings", nf, "finding_records")]:
        require(len(read_csv(ROOT / "data" / f"{name}.csv")) == count, f"Active count mismatch: {name}")
    for layer in ["candidate", "finding"]:
        rows = read_csv(ROOT / "data/archive" / f"{layer}_retirement_{month}.csv")
        require(len(rows) == metrics["retired"][f"{layer}_decisions"], f"Retirement count mismatch: {layer}")
        require(dict(sorted(Counter(r["reason"] for r in rows).items())) == metrics["retired"][f"{layer}_reasons"],
                f"Retirement reasons mismatch: {layer}")
    repair = json.loads((ROOT / config["EVIDENCE_ATLAS_IDENTIFIER_REPORT"]).read_text(encoding="utf-8"))
    require(repair.get("status") == "passed" and repair.get("pubmed_findings_checked") == nf,
            "Identifier repair does not cover all findings")
    require(not repair.get("missing_official_summaries") and not repair.get("title_mismatches"), "Identifier mismatch or missing summaries")

    main_names = {f"{name}-{month}.png" for name in ["heatmap-dashboard", "heatmap-topic-year", "heatmap-topic-evidence",
                  "ingredient-card-wall", "evidence-yield-ingredients", "retraction-density", "topic-evidence-yield"]}
    visual_dir = ROOT / "docs/assets/visual-assets" / month
    cards = list((visual_dir / "ingredient-cards").glob("*.png"))
    require({p.name for p in visual_dir.glob("*.png")} == main_names and len(cards) == 50, "57-image inventory mismatch")
    for path in [*(visual_dir / name for name in main_names), *cards]:
        with Image.open(path) as image:
            require(image.width >= 600 and image.height >= 600, f"Image too small: {path.name}")
            image.verify()
    report_path = ROOT / "docs" / config["EVIDENCE_ATLAS_PUBLIC_REPORT_FILE"]
    report = report_path.read_text(encoding="utf-8")
    dashboard_path = ROOT / "docs" / f"yulcell-posting-asset-dashboard-{date}.html"
    dashboard = dashboard_path.read_text(encoding="utf-8")
    require(report.count("data:image/png;base64,") == 57 and report.count('button type="button" class="download"') == 57,
            "Report must embed 57 individually downloadable images")
    require(dashboard.count("data:image/png;base64,") >= 57, "Posting panel lacks images")
    for path in [ROOT / "README.md", ROOT / "README.zh-CN.md", ROOT / "public-data/README.md",
                 ROOT / "docs/asset-catalog.md", ROOT / "docs/yulcell-brand-index.md",
                 ROOT / "docs/data-retention-and-curation-policy.md",
                 ROOT / "content/public-reader" / config["EVIDENCE_ATLAS_RELEASE_FILE"],
                 ROOT / "docs" / f"feishu-public-assets-{month}.md"]:
        text = path.read_text(encoding="utf-8")
        require(shared.BRAND_ZH in text, f"Missing brand: {path.name}")
        require(not ("�" in text or "瀹囧" in text or re.search(r"\?{3,}", text)), f"Broken Unicode: {path.name}")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if not target.startswith(("https:", "http:", "#", "mailto:")):
                require((path.parent / target.split("#")[0]).exists(), f"Broken current link: {path.name} -> {target}")
    notes = json.loads((ROOT / config["EVIDENCE_ATLAS_FEATURED_NOTES"]).read_text(encoding="utf-8"))
    findings_by_pmid = {r["pmid"]: r for r in read_csv(ROOT / "data/evidence_findings.csv")}
    for pmid in config["EVIDENCE_ATLAS_FEATURED_PMIDS"].split(","):
        require(pmid in findings_by_pmid and pmid in notes, f"Missing featured paper/note: {pmid}")
        require(notes[pmid]["checked_date"] == date and notes[pmid]["review_depth"].endswith("full_text_pending"),
                f"Featured provenance mismatch: {pmid}")
    for pmid in ["42782098", "41940793"]:
        row = findings_by_pmid.get(pmid, {})
        require(row.get("study_type_draft") != "human_randomized_or_clinical_trial", f"Secondary design mislabeled: {pmid}")
        require(row.get("final_evidence_level", "") in {"C", "D", "E"}, f"Secondary design overgraded: {pmid}")

    manifest = read_csv(ROOT / "data" / f"feishu_live_tables_{key}.csv")
    registry = read_csv(ROOT / "data/feishu_table_registry.csv")
    navigation = read_csv(ROOT / "data" / f"feishu_reader_navigation_{key}.csv")
    require((len(manifest), len(registry), len(navigation)) == (9, 9, 14), "Feishu inventory must remain 9/9/14")
    ids = [parse_qs(urlparse(r["飞书链接"]).query).get("table", [""])[0] for r in manifest]
    require(len(set(ids)) == 9 and all(re.fullmatch(r"tbl[A-Za-z0-9]+", v) for v in ids), "Invalid Feishu table IDs")
    require(set(ids) == {r["table_id"] for r in registry}, "Manifest/registry IDs differ")
    counts = {r["表名"]: int(r["记录数"]) for r in manifest}
    require(counts == {r["stable_name"]: int(r["expected_rows"]) for r in registry}, "Manifest/registry counts differ")
    for row in manifest:
        require(row["状态"] == "active" and row["更新月份"] == month and row["表名"].startswith("宇多Yul细胞_当前"),
                f"Stale Feishu manifest: {row['表名']}")
    if not args.source_only:
        audit = json.loads((ROOT / "build" / f"feishu_online_audit_{key}.json").read_text(encoding="utf-8"))
        require(audit.get("status") == "passed" and audit.get("snapshot_date") == date, "Online audit did not pass for this snapshot")
        require({r["table_name"]: r["actual_records"] for r in audit["tables"]} == counts, "Online audit counts differ")
        require(len(list((ROOT / "build/feishu-public-reader").glob("*.md"))) == 15, "Reader export count differs")
        require(len(list((ROOT / "build/feishu-docs").glob("*.md"))) == nf + 62, "Full export count differs")
        require((ROOT / "build/feishu-public-reader" / config["EVIDENCE_ATLAS_RELEASE_EXPORT_NAME"]).exists(), "Missing release export")

    for directory, verifier in [(ROOT / "archive/public-data", csv_archive.verify_archive),
                                (ROOT / "archive/visual-releases", visual_archive.verify_archive)]:
        hashes = {line.split()[1]: line.split()[0] for line in (directory / "SHA256SUMS.txt").read_text(encoding="ascii").splitlines() if line.strip()}
        require(set(hashes) == {p.name for p in directory.glob("*.zip")}, f"Archive inventory mismatch: {directory.name}")
        for filename, expected_hash in hashes.items():
            verifier(directory / filename)
            require(shared.sha256(directory / filename) == expected_hash, f"Archive hash mismatch: {filename}")
    year, number = map(int, month.split("-"))
    previous = f"{year if number > 1 else year - 1:04d}-{number - 1 if number > 1 else 12:02d}"
    csv_paths = list((ROOT / "public-data").glob("*.csv"))
    require(len(csv_paths) == 10, "Keep only current and previous five-table snapshots unpacked")
    for release_month in [month, previous]:
        require(len(list((ROOT / "public-data").glob(f"*-{release_month}.csv"))) == 5, f"Missing CSV snapshot: {release_month}")
    for file_key, metric_key in [("candidate-sources", "candidate_records"), ("evidence-findings", "finding_records")]:
        require(len(read_csv(ROOT / "public-data" / f"{file_key}-{previous}.csv")) == metrics["before"][metric_key], "Baseline count mismatch")
    index = json.loads((ROOT / "data/asset_archive_index.json").read_text(encoding="utf-8"))
    for row in index:
        archived = visual_archive.verify_archive(ROOT / row["archive"])
        require(len(archived["files"]) == row["files"] and shared.sha256(ROOT / row["archive"]) == row["sha256"], "Visual archive index mismatch")
    workflow = (ROOT / ".github/workflows/fetch-pubmed.yml").read_text(encoding="utf-8")
    require("fetch_pubmed_intake.py" in workflow and "gh pr create" in workflow and not re.search(r"git push\s+(?:origin\s+)?(?:main|HEAD:main)\b", workflow), "Weekly intake may bypass review")
    if errors:
        raise SystemExit("Current release validation failed:\n- " + "\n- ".join(errors))
    print(f"Current release passed: {shared.EXPECTED_TOTAL:,} public rows, 57 images, 9 stable tables, verified archives.")


if __name__ == "__main__":
    main()
