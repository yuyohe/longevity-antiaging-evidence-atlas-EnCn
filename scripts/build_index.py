"""Build a lightweight Markdown index for public draft review."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"


def main() -> None:
    BUILD.mkdir(exist_ok=True)
    matrix = ROOT / "data" / "evidence_matrix.csv"
    out = BUILD / "index.md"
    lines = ["# 长寿抗衰与健康寿命证据图谱索引", ""]
    lines.append("> 草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。")
    lines.append("> Draft status: automatically prepared; not fully reviewed; not medical advice.")
    lines.append("")
    lines.append("## Evidence Matrix")
    lines.append("")
    lines.append("| paper_id | topic | evidence | endpoint | recommendation | zh_summary |")
    lines.append("|---|---|---|---|---|---|")
    with matrix.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            lines.append(
                f"| {row.get('paper_id','')} | {row.get('topic','')} | {row.get('evidence_level','')} | "
                f"{row.get('endpoint_class','')} | {row.get('recommendation_class','')} | {row.get('zh_summary','')} |"
            )
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with (ROOT / "data" / "evidence_findings.csv").open(encoding="utf-8-sig", newline="") as handle:
        findings = list(csv.DictReader(handle))
    with matrix.open(encoding="utf-8-sig", newline="") as handle:
        included_ids = {row["paper_id"] for row in csv.DictReader(handle)}
    sources = [{
        "id": row["candidate_id"], "title_en": row["title_en"], "title_zh": row["title_zh"],
        "year": row["year"], "doi": row["doi"], "pmid": row["pmid"], "pmcid": row["pmcid"],
        "url": f"https://pubmed.ncbi.nlm.nih.gov/{row['pmid']}/",
        "study_type": row["study_type_draft"], "species": row["species_draft"],
        "endpoint_class": row["endpoint_class_draft"], "evidence_level": row["final_evidence_level"],
        "included": row["candidate_id"] in included_ids,
        "review_status": row["review_status"], "last_checked": row["last_checked"],
    } for row in findings]
    (ROOT / "data" / "sources.json").write_text(json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT)}")
    print(f"Wrote {len(sources)} active source records")


if __name__ == "__main__":
    main()
