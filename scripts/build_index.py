"""Build a lightweight Markdown index for public draft review."""

from __future__ import annotations

import csv
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
    print(f"Wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
