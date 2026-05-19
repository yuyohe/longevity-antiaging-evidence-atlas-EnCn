"""Build the full public data package for the May 2026 release."""

from __future__ import annotations

import csv
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PUBLIC = ROOT / "public-data"
DOCS = ROOT / "docs"
MONTH = "2026-05"


ASSETS = [
    {
        "asset_id": "full-001",
        "name": "全量文献候选库",
        "source": DATA / "literature_library.csv",
        "public_file": PUBLIC / "literature-library-2026-05.csv",
        "description": "超过 1 万条候选文献入口，含题名、年份、来源、PMID/DOI、检索词和纳入状态。",
    },
    {
        "asset_id": "full-002",
        "name": "候选来源原始表",
        "source": DATA / "candidate_sources.csv",
        "public_file": PUBLIC / "candidate-sources-2026-05.csv",
        "description": "原始候选来源表，保留抓取来源、检索词、备注和最近检查日期。",
    },
    {
        "asset_id": "full-003",
        "name": "入选短名单",
        "source": DATA / "shortlist_sources.csv",
        "public_file": PUBLIC / "shortlist-sources-2026-05.csv",
        "description": "从候选库里进入优先复核的 3000 条记录，含主题、证据草稿等级、期刊和评分字段。",
    },
    {
        "asset_id": "full-004",
        "name": "证据发现表",
        "source": DATA / "evidence_findings.csv",
        "public_file": PUBLIC / "evidence-findings-2026-05.csv",
        "description": "3000 条证据发现，含研究类型、终点、结论、过度解读风险和 0.5 评分字段。",
    },
    {
        "asset_id": "full-005",
        "name": "证据矩阵",
        "source": DATA / "evidence_matrix.csv",
        "public_file": PUBLIC / "evidence-matrix-2026-05.csv",
        "description": "1500 条入矩阵证据，适合按主题、证据等级、终点等级和行动性筛选。",
    },
]


def count_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return sum(1 for _ in csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for asset in ASSETS:
        shutil.copyfile(asset["source"], asset["public_file"])
        row_count = count_rows(asset["public_file"])
        rel_public = asset["public_file"].relative_to(ROOT).as_posix()
        rel_source = asset["source"].relative_to(ROOT).as_posix()
        rows.append(
            {
                "asset_id": asset["asset_id"],
                "资产名称": asset["name"],
                "公开文件": rel_public,
                "源文件": rel_source,
                "记录数": str(row_count),
                "说明": asset["description"],
                "公开状态": "对外公开",
                "更新月份": MONTH,
            }
        )

    write_csv(
        DATA / "public_full_asset_index_2026_05.csv",
        rows,
        ["asset_id", "资产名称", "公开文件", "源文件", "记录数", "说明", "公开状态", "更新月份"],
    )

    table = "\n".join(
        f"| {row['资产名称']} | {int(row['记录数']):,} | `{row['公开文件']}` | {row['说明']} |"
        for row in rows
    )
    total = sum(int(row["记录数"]) for row in rows)
    readme = f"""# 抗衰证据库公开全量数据包（{MONTH}）

这个目录是给外部读者和研究者下载、复核、二次分析用的公开数据包。它不只包含卡片和热力图，也包含底层候选文献、入选短名单、证据发现和证据矩阵。

| 数据表 | 记录数 | 文件 | 内容 |
| --- | ---: | --- | --- |
{table}

合计公开记录数：{total:,}。

说明：这些表是证据地图的资料层，不等于个人医疗建议。读者可以用 PMID、DOI、主题、证据等级、期刊和评分字段追溯每条记录。
"""
    (PUBLIC / "README.md").write_text(readme, encoding="utf-8")
    (DOCS / "public-full-data-index-2026-05.md").write_text(readme, encoding="utf-8")
    print(f"Built public full data package: {len(rows)} files, {total} rows")


if __name__ == "__main__":
    main()
