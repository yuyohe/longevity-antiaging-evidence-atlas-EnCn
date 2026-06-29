from __future__ import annotations

import csv
import html
import json
import os
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"
CONTENT = ROOT / "content"
BUILD = ROOT / "build"

MONTH = os.environ.get("EVIDENCE_ATLAS_ASSET_MONTH", "2026-06")
MONTH_UNDERSCORE = MONTH.replace("-", "_")
RUN_DATE = os.environ.get("EVIDENCE_ATLAS_UPDATE_DATE", date.today().isoformat())
RECENT_REPORT = BUILD / "healthspan_recent_update_2026_06_report.json"
BRAND_NAME = os.environ.get("PUBLIC_BRAND_NAME", "宇多Yul细胞/yulcell")
BRAND_KEYWORDS = os.environ.get(
    "PUBLIC_BRAND_SEO_KEYWORDS",
    "宇多Yul细胞/yulcell, yulcell, 宇多Yul细胞, 长寿抗衰证据图谱, 健康寿命证据图谱",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in fields} for row in rows])


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value))


def safe_int(value: object) -> int:
    try:
        return int(float(str(value or "0")))
    except Exception:
        return 0


def md_table(headers: list[str], rows: list[list[object]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return "\n".join(out)


def html_table(headers: list[str], rows: list[list[object]]) -> str:
    head = "".join(f"<th>{esc(header)}</th>" for header in headers)
    body = "\n".join(
        "<tr>" + "".join(f"<td>{esc(cell)}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def heat_color(value: int, max_value: int) -> str:
    if value <= 0 or max_value <= 0:
        return "#f6f8fa"
    ratio = min(1.0, value / max_value)
    r = int(238 - 150 * ratio)
    g = int(246 - 80 * ratio)
    b = int(243 - 96 * ratio)
    return f"rgb({r},{g},{b})"


def recent_report() -> dict:
    if RECENT_REPORT.exists():
        return json.loads(RECENT_REPORT.read_text(encoding="utf-8"))
    return {}


def build_heatmap_tables() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    matrix = read_csv(DATA / "evidence_matrix.csv")
    years = list(range(2020, 2027))
    by_topic_year: dict[str, Counter[int]] = defaultdict(Counter)
    by_topic_level: dict[str, Counter[str]] = defaultdict(Counter)
    for row in matrix:
        topic = row.get("topic", "未分类")
        year = safe_int(row.get("year"))
        if year in years:
            by_topic_year[topic][year] += 1
        by_topic_level[topic][row.get("evidence_level", "") or "未分级"] += 1

    topic_year_rows: list[dict[str, str]] = []
    for topic, counts in by_topic_year.items():
        row = {"topic": topic}
        total = 0
        for year in years:
            value = counts[year]
            row[str(year)] = str(value)
            total += value
        row["total_2020_2026"] = str(total)
        topic_year_rows.append(row)
    topic_year_rows.sort(key=lambda row: safe_int(row["total_2020_2026"]), reverse=True)

    topic_evidence_rows: list[dict[str, str]] = []
    for topic, counts in by_topic_level.items():
        row = {"topic": topic}
        total = 0
        for level in ["A", "B", "C", "D", "E"]:
            value = counts[level]
            row[level] = str(value)
            total += value
        row["total"] = str(total)
        topic_evidence_rows.append(row)
    topic_evidence_rows.sort(key=lambda row: safe_int(row["total"]), reverse=True)

    year_fields = ["topic", *[str(year) for year in years], "total_2020_2026"]
    evidence_fields = ["topic", "A", "B", "C", "D", "E", "total"]
    write_csv(DATA / "research_heatmap_topic_year.csv", topic_year_rows, year_fields)
    write_csv(DATA / f"research_heatmap_topic_year_{MONTH_UNDERSCORE}.csv", topic_year_rows, year_fields)
    write_csv(DATA / "research_heatmap_topic_evidence.csv", topic_evidence_rows, evidence_fields)
    write_csv(DATA / f"research_heatmap_topic_evidence_{MONTH_UNDERSCORE}.csv", topic_evidence_rows, evidence_fields)
    return topic_year_rows, topic_evidence_rows


def build_heatmap_html(topic_year_rows: list[dict[str, str]], topic_evidence_rows: list[dict[str, str]]) -> None:
    years = [str(year) for year in range(2020, 2027)]
    max_value = max([safe_int(row.get(year)) for row in topic_year_rows for year in years] or [0])
    year_rows = []
    for row in topic_year_rows[:24]:
        cells = "".join(
            f'<td style="background:{heat_color(safe_int(row.get(year)), max_value)}">{safe_int(row.get(year))}</td>'
            for year in years
        )
        year_rows.append(f"<tr><th>{esc(row['topic'])}</th>{cells}<td>{safe_int(row['total_2020_2026'])}</td></tr>")

    evidence_rows = []
    for row in topic_evidence_rows[:24]:
        evidence_rows.append(
            "<tr>"
            f"<th>{esc(row['topic'])}</th>"
            f"<td>{safe_int(row['A'])}</td><td>{safe_int(row['B'])}</td>"
            f"<td>{safe_int(row['C'])}</td><td>{safe_int(row['D'])}</td>"
            f"<td>{safe_int(row['E'])}</td><td>{safe_int(row['total'])}</td>"
            "</tr>"
        )

    html_text = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>抗衰研究热力图 {MONTH}</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif; background: #f6f8fa; color: #1f2933; line-height: 1.7; }}
    header {{ background: #183044; color: white; padding: 40px 24px; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px 20px 54px; }}
    section {{ background: white; border: 1px solid #d9e1ea; border-radius: 8px; padding: 22px; margin: 16px 0; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border: 1px solid #d9e1ea; padding: 8px 9px; text-align: center; }}
    th:first-child, td:first-child {{ text-align: left; }}
    .note {{ background: #eef6f2; border-left: 4px solid #1f7a5a; padding: 12px 14px; border-radius: 6px; }}
  </style>
</head>
<body>
  <header>
    <h1>抗衰研究热力图</h1>
    <p>品牌：{esc(BRAND_NAME)}。{MONTH} 更新。颜色越深，表示该年份进入证据矩阵的研究越多。2026 年尚未结束，不能和全年直接比较。</p>
  </header>
  <main>
    <section>
      <h2>主题 × 年份</h2>
      <div class="note">这张图看研究活跃度，不是有效性排序。近期文献需要人工复核后才能改变公开结论等级。</div>
      <table><thead><tr><th>主题</th>{"".join(f"<th>{year}</th>" for year in years)}<th>合计</th></tr></thead><tbody>{"".join(year_rows)}</tbody></table>
    </section>
    <section>
      <h2>主题 × 证据等级</h2>
      <table><thead><tr><th>主题</th><th>A</th><th>B</th><th>C</th><th>D</th><th>E</th><th>合计</th></tr></thead><tbody>{"".join(evidence_rows)}</tbody></table>
    </section>
  </main>
</body>
</html>
"""
    (DOCS / f"research-heatmap-{MONTH}.html").write_text(html_text, encoding="utf-8")

    md_rows = [
        [row["topic"], *[row.get(str(year), "0") for year in range(2020, 2027)], row["total_2020_2026"]]
        for row in topic_year_rows[:20]
    ]
    md_text = f"""# 抗衰研究热力图

品牌：{BRAND_NAME}

颜色版 HTML：`docs/research-heatmap-{MONTH}.html`

这张图看研究活跃度，不是有效性排序。2026 年还没有结束，不能和 2025 全年直接比较。

{md_table(["主题", "2020", "2021", "2022", "2023", "2024", "2025", "2026", "合计"], md_rows)}

## 数据文件

- `data/research_heatmap_topic_year_{MONTH_UNDERSCORE}.csv`
- `data/research_heatmap_topic_evidence_{MONTH_UNDERSCORE}.csv`
"""
    (CONTENT / "public-reader" / "research-heatmap.md").write_text(md_text, encoding="utf-8")
    (BUILD / "feishu-public-reader").mkdir(parents=True, exist_ok=True)
    (BUILD / "feishu-public-reader" / "012-抗衰研究热力图.md").write_text(md_text, encoding="utf-8")


def build_public_asset_index(counts: dict[str, int]) -> None:
    rows = [
        ["asset-001", "前 50 常见成分卡片库", "公开阅读资产", "content/cards/ingredients-top-50/index.md", "build/feishu-public-reader/011-前50常见成分卡片库.md", "让普通读者快速理解常见成分", "可公开"],
        ["asset-002", "抗衰研究热力图", "公开阅读资产", f"docs/research-heatmap-{MONTH}.html", "build/feishu-public-reader/012-抗衰研究热力图.md", "展示不同方向研究活跃度", "可公开"],
        ["asset-003", f"{MONTH} 月度更新报告", "公开阅读资产", f"docs/monthly-update-{MONTH}.html", f"build/feishu-public-reader/013-{MONTH}月度更新报告.md", "解释本月新增资产和维护范围", "可公开"],
        ["asset-004", "全量文献候选库", "公开全量数据", f"public-data/literature-library-{MONTH}.csv", "", f"{counts['literature_library']} 条候选文献入口", "可公开"],
        ["asset-005", "候选来源原始表", "公开全量数据", f"public-data/candidate-sources-{MONTH}.csv", "", f"{counts['candidate_sources']} 条原始候选来源", "可公开"],
        ["asset-006", "入选短名单", "公开全量数据", f"public-data/shortlist-sources-{MONTH}.csv", "", f"{counts['shortlist_sources']} 条优先复核记录", "可公开"],
        ["asset-007", "证据发现表", "公开全量数据", f"public-data/evidence-findings-{MONTH}.csv", "", f"{counts['evidence_findings']} 条证据发现", "可公开"],
        ["asset-008", "证据矩阵", "公开全量数据", f"public-data/evidence-matrix-{MONTH}.csv", "", f"{counts['evidence_matrix']} 条矩阵记录", "可公开"],
        ["asset-009", "成分证据含金量", "公开数据资产", f"data/evidence_yield_metrics_{MONTH_UNDERSCORE}.csv", "", "前 50 成分的证据产出代理指标", "可公开"],
        ["asset-010", "主题证据产出率", "公开数据资产", f"data/topic_evidence_yield_metrics_{MONTH_UNDERSCORE}.csv", "", "主题级证据产出代理指标", "可公开"],
        ["asset-011", "撤稿密度", "公开数据资产", "data/retraction_risk_summary_20y.csv", "", f"{counts['retraction_targets']} 个撤稿风险观察目标", "可公开"],
    ]
    fields = ["asset_id", "资产名称", "资产类型", "GitHub路径", "飞书导入文件", "主要用途", "公开状态", "更新月份"]
    asset_rows = []
    for row in rows:
        record = dict(zip(fields, [*row, MONTH]))
        record["品牌标识"] = BRAND_NAME
        record["SEO关键词"] = BRAND_KEYWORDS
        asset_rows.append(record)
    write_csv(
        DATA / f"public_asset_index_{MONTH_UNDERSCORE}.csv",
        asset_rows,
        [*fields, "品牌标识", "SEO关键词"],
    )


def build_monthly_report(topic_year_rows: list[dict[str, str]], topic_evidence_rows: list[dict[str, str]]) -> None:
    candidates = read_csv(DATA / "candidate_sources.csv")
    literature = read_csv(DATA / "literature_library.csv")
    findings = read_csv(DATA / "evidence_findings.csv")
    matrix = read_csv(DATA / "evidence_matrix.csv")
    shortlist = read_csv(DATA / "shortlist_sources.csv")
    skin = read_csv(DATA / "skin_beauty_summary.csv")
    supplements = read_csv(DATA / "supplement_matrix.csv")
    retractions = read_csv(DATA / "retraction_risk_summary_20y.csv")
    recent = recent_report()
    expansion = recent.get("candidate_expansion", {})
    date_window = str(expansion.get("date_window") or "2026/05/01..2026/06/18").replace("..", " 至 ")
    recent_bucket_total = safe_int(expansion.get("added"))
    recent_selected = safe_int(recent.get("recent_update_findings_selected"))

    counts = {
        "candidate_sources": len(candidates),
        "literature_library": len(literature),
        "evidence_findings": len(findings),
        "evidence_matrix": len(matrix),
        "shortlist_sources": len(shortlist),
        "skin_topics": len(skin),
        "supplements": len(supplements),
        "retraction_targets": len(retractions),
    }
    midmonth_candidate_base = safe_int(os.environ.get("MIDMONTH_CANDIDATE_BASE", "13720"))
    recent_added_since_midmonth = max(0, len(candidates) - midmonth_candidate_base)
    public_recent_added = recent_added_since_midmonth or recent_bucket_total
    build_public_asset_index(counts)

    matrix_levels = Counter(row.get("evidence_level", "") for row in matrix)
    top_recent_rows = []
    sample_rows = list(expansion.get("added_sample", [])[:12])
    if not sample_rows:
        sample_rows = [
            row
            for row in candidates
            if row.get("last_checked") == RUN_DATE and "recent_update_2026_06" in row.get("query", "")
        ][:12]
    for row in sample_rows:
        top_recent_rows.append([row.get("pmid", ""), row.get("year", ""), row.get("title_en", "")[:120], row.get("query", "")])

    report_rows = [
        {
            "section_id": "report-001",
            "板块": "本月一句话",
            "内容": f"本月按 {date_window} 的 PubMed 近期窗口更新文献候选；相对 6 月中本地版新增候选 {public_recent_added} 条，并把健康寿命发现扩到 {len(findings)} 条、证据矩阵扩到 {len(matrix)} 条。",
            "是否公开": "是",
            "GitHub路径": f"docs/monthly-update-{MONTH}.html",
            "飞书导入文件": f"build/feishu-public-reader/013-{MONTH}月度更新报告.md",
            "更新月份": MONTH,
        },
        {
            "section_id": "report-002",
            "板块": "近期文献",
            "内容": f"相对 6 月中本地版新增候选 {public_recent_added} 条；6 月 recent_update 标签累计 {recent_bucket_total} 条；进入 {len(findings)} 条 findings 的 recent_update 记录 {recent_selected} 条。新增记录仍是自动草稿，不能直接改变医学结论。",
            "是否公开": "是",
            "GitHub路径": "build/healthspan_recent_update_2026_06_report.json",
            "飞书导入文件": f"build/feishu-public-reader/013-{MONTH}月度更新报告.md",
            "更新月份": MONTH,
        },
        {
            "section_id": "report-003",
            "板块": "资产规模",
            "内容": f"候选文献 {len(candidates)}；证据发现 {len(findings)}；证据矩阵 {len(matrix)}；皮肤/外观主题 {len(skin)}；补剂条目 {len(supplements)}；撤稿观察目标 {len(retractions)}。",
            "是否公开": "是",
            "GitHub路径": f"data/public_asset_index_{MONTH_UNDERSCORE}.csv",
            "飞书导入文件": f"build/feishu-public-reader/013-{MONTH}月度更新报告.md",
            "更新月份": MONTH,
        },
        {
            "section_id": "report-004",
            "板块": "热力图",
            "内容": "研究热力图和证据等级热力图已按最新 evidence_matrix 重建。热力图表示研究活跃度和证据分布，不是有效性排行榜。",
            "是否公开": "是",
            "GitHub路径": f"docs/research-heatmap-{MONTH}.html",
            "飞书导入文件": "build/feishu-public-reader/012-抗衰研究热力图.md",
            "更新月份": MONTH,
        },
        {
            "section_id": "report-005",
            "板块": "边界",
            "内容": "近期文献仅进入候选和草稿层；药物、慢病、医美、注射、剂量和个人方案继续保持医生/专业评估边界。",
            "是否公开": "是",
            "GitHub路径": "content/public-reader/doctor-first.md",
            "飞书导入文件": "build/feishu-public-reader/009-哪些内容必须先问医生.md",
            "更新月份": MONTH,
        },
    ]
    write_csv(
        DATA / f"monthly_update_report_{MONTH_UNDERSCORE}.csv",
        report_rows,
        ["section_id", "板块", "内容", "是否公开", "GitHub路径", "飞书导入文件", "更新月份"],
    )

    stat_html = "".join(
        f"<div class=\"stat\"><b>{value:,}</b><span>{label}</span></div>"
        for label, value in [
            ("候选文献", len(candidates)),
            ("证据发现", len(findings)),
            ("证据矩阵", len(matrix)),
            ("月底新增候选", public_recent_added),
            ("近期入选 findings", recent_selected),
            ("撤稿观察目标", len(retractions)),
        ]
    )
    level_text = "；".join(f"{level or '未分级'}：{count}" for level, count in sorted(matrix_levels.items()))
    top_topics = [
        [row["topic"], row["total_2020_2026"], row.get("2025", "0"), row.get("2026", "0")]
        for row in topic_year_rows[:10]
    ]
    recent_table = md_table(["PMID", "年份", "题名", "查询层"], top_recent_rows) if top_recent_rows else "本轮没有新增近期候选样例。"

    html_report = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{MONTH} 抗衰证据库月度更新报告</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif; background: #f6f8fa; color: #1f2933; line-height: 1.72; }}
    header {{ background: #14202b; color: white; padding: 42px 24px; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px 20px 56px; }}
    section {{ background: white; border: 1px solid #d9e1ea; border-radius: 8px; padding: 24px; margin: 16px 0; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; }}
    .stat {{ border: 1px solid #d9e1ea; border-radius: 8px; padding: 14px; background: #fbfcfd; }}
    .stat b {{ display: block; font-size: 30px; color: #176b4b; }}
    .stat span {{ color: #596775; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border: 1px solid #d9e1ea; padding: 8px 9px; text-align: left; vertical-align: top; }}
    .note {{ background: #eef6f2; border-left: 4px solid #1f7a5a; padding: 12px 14px; border-radius: 6px; }}
  </style>
</head>
<body>
  <header>
    <h1>{MONTH} 抗衰证据库月度更新报告</h1>
    <p>品牌：{esc(BRAND_NAME)}。生成日期：{RUN_DATE}。本轮重点是近期文献增量、证据矩阵扩容和视觉资产更新。</p>
  </header>
  <main>
    <section>
      <h2>本月一句话</h2>
      <p class="note">按 {esc(date_window)} 的 PubMed 近期窗口补充候选文献；相对 6 月中本地版新增候选 {public_recent_added} 条，并将健康寿命 findings 扩到 {len(findings)} 条、证据矩阵扩到 {len(matrix)} 条。近期文献仍是草稿层，不直接改变医学结论。</p>
    </section>
    <section>
      <h2>资产规模</h2>
      <div class="grid">{stat_html}</div>
    </section>
    <section>
      <h2>近期文献更新</h2>
      <p>相对 6 月中本地版新增候选：{public_recent_added} 条；6 月 recent_update 标签累计：{recent_bucket_total} 条；进入本轮 findings 的 recent_update 记录：{recent_selected} 条。</p>
      <p>检索窗口：{esc(expansion.get("date_window", "2026/05/01..2026/06/02"))}。数据源为 PubMed E-utilities。</p>
    </section>
    <section>
      <h2>证据矩阵等级分布</h2>
      <p>{esc(level_text)}</p>
    </section>
    <section>
      <h2>研究热力图观察</h2>
      <p>颜色版见 <code>docs/research-heatmap-{MONTH}.html</code>。2026 年尚未结束，不能与 2025 全年直接比较。</p>
      {html_table(["主题", "2020-2026 合计", "2025", "2026"], top_topics)}
    </section>
    <section>
      <h2>边界</h2>
      <p>本项目继续只做证据导航，不给个人剂量、诊断、处方替代、注射医美操作建议。近期文献需要人工全文复核后，才适合调整公开叙述。</p>
    </section>
  </main>
</body>
</html>
"""
    (DOCS / f"monthly-update-{MONTH}.html").write_text(html_report, encoding="utf-8")

    md_report = f"""# {MONTH} 抗衰证据库月度更新报告

品牌：{BRAND_NAME}

生成日期：{RUN_DATE}

## 本月一句话

按 {date_window} 的 PubMed 近期窗口补充候选文献；相对 6 月中本地版新增候选 {public_recent_added} 条，并将健康寿命 findings 扩到 {len(findings)} 条、证据矩阵扩到 {len(matrix)} 条。近期文献仍是草稿层，不直接改变医学结论。

## 资产规模

- 候选文献：{len(candidates):,}
- 证据发现：{len(findings):,}
- 证据矩阵：{len(matrix):,}
- 月底新增候选：{public_recent_added:,}
- 6 月 recent_update 标签累计：{recent_bucket_total:,}
- 近期入选 findings：{recent_selected:,}
- 皮肤/外观主题：{len(skin):,}
- 补剂条目：{len(supplements):,}
- 撤稿观察目标：{len(retractions):,}

## 近期文献样例

{recent_table}

## 研究热力图

- HTML：`docs/research-heatmap-{MONTH}.html`
- 年份数据：`data/research_heatmap_topic_year_{MONTH_UNDERSCORE}.csv`
- 证据等级数据：`data/research_heatmap_topic_evidence_{MONTH_UNDERSCORE}.csv`

## 边界

本项目继续只做证据导航，不给个人剂量、诊断、处方替代、注射医美操作建议。近期文献需要人工全文复核后，才适合调整公开叙述。
"""
    (CONTENT / "public-reader" / f"monthly-update-{MONTH}.md").write_text(md_report, encoding="utf-8")
    (BUILD / "feishu-public-reader" / f"013-{MONTH}月度更新报告.md").write_text(md_report, encoding="utf-8")


def main() -> None:
    topic_year_rows, topic_evidence_rows = build_heatmap_tables()
    build_heatmap_html(topic_year_rows, topic_evidence_rows)
    build_monthly_report(topic_year_rows, topic_evidence_rows)
    print(f"Built monthly update assets for {MONTH}")


if __name__ == "__main__":
    main()
