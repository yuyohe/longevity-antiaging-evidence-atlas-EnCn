from __future__ import annotations

import base64
import csv
import html
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"
PUBLIC = ROOT / "public-data"
VISUALS = DOCS / "assets" / "visual-assets" / "2026-07"

BRAND = "宇多Yul细胞/yulcell"
REPO_URL = "https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn"
FREEZE_DATE = os.environ.get("EVIDENCE_ATLAS_UPDATE_DATE", "2026-07-14")
REVIEW_DATE = os.environ.get("EVIDENCE_ATLAS_REVIEW_DATE", FREEZE_DATE)
RELEASE_LABEL = os.environ.get("EVIDENCE_ATLAS_RELEASE_LABEL_FULL", "2026 年 7 月中旬")
RELEASE_SHORT = os.environ.get("EVIDENCE_ATLAS_RELEASE_LABEL", "7 月中旬")
RELEASE_FILE = os.environ.get("EVIDENCE_ATLAS_RELEASE_FILE", "mid-july-2026-update.md")
REPORT_FILE = os.environ.get("EVIDENCE_ATLAS_PUBLIC_REPORT_FILE", "mid-july-public-update-2026-07.html")
DASHBOARD_FILE = os.environ.get("EVIDENCE_ATLAS_DASHBOARD_FILE", "yulcell-posting-asset-dashboard-2026-07-14.html")
NAV_TABLE_NAME = os.environ.get("EVIDENCE_ATLAS_NAV_TABLE_NAME", "公开入口_7月中阅读导航_2026-07")
PREVIOUS_SNAPSHOT_DATE = os.environ.get("EVIDENCE_ATLAS_PREVIOUS_SNAPSHOT_DATE", "2026-06-29")
PREVIOUS_CANDIDATES = int(os.environ.get("EVIDENCE_ATLAS_PREVIOUS_CANDIDATES", "14273"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{name: row.get(name, "") for name in fieldnames} for row in rows])


def count_csv(path: Path) -> int:
    return len(read_csv(path))


def data_uri(path: Path) -> str:
    mime = "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def table_links() -> tuple[list[dict[str, str]], dict[str, str]]:
    path = DATA / "feishu_live_tables_2026_07.csv"
    rows = read_csv(path) if path.exists() else []
    active = [row for row in rows if row.get("状态", "").startswith("active")]
    return active, {row.get("表名", ""): row.get("飞书链接", "") for row in active}


def navigation_rows(links: dict[str, str]) -> list[dict[str, str]]:
    nav_url = links.get(NAV_TABLE_NAME, "")
    heatmap_url = links.get("视觉资产_热力图图片_2026-07", "")
    cards_url = links.get("公开入口_前50成分单卡_2026-07", "")
    wall_url = links.get("视觉资产_成分卡片总览_2026-07", "")
    library_url = links.get("公开数据_全量文献候选库_2026-07", "")
    findings_url = links.get("公开数据_证据发现表_2026-07", "")
    matrix_url = links.get("公开数据_证据矩阵_2026-07", "")

    items = [
        ("R001", "01", "普通读者入口：从这里开始", "Start here", "第一次打开项目的人", "先弄清项目能回答什么、不能回答什么。", f"{REPO_URL}/blob/main/content/public-reader/start-here.md", nav_url, "阅读入口"),
        ("R002", "02", f"{RELEASE_LABEL}更新说明", "July update", "所有读者", "用几分钟看懂这次新增了什么。", f"{REPO_URL}/blob/main/content/public-reader/{RELEASE_FILE}", nav_url, "更新说明"),
        ("R003", "03", "15 条结论", "15 takeaways", "普通读者、学生", "先建立判断抗衰说法的基本框架。", f"{REPO_URL}/blob/main/content/public-reader/ten-takeaways.md", nav_url, "阅读入口"),
        ("R004", "04", "证据权重怎么看", "How evidence is weighted", "想学会判断证据的人", "分清人体结局、指标、动物和机制研究。", f"{REPO_URL}/blob/main/content/public-reader/evidence-weight.md", matrix_url, "方法说明"),
        ("R005", "05", "大众主题速读", "Topic guide", "关心运动、睡眠和代谢的人", "按主题读结论，不必先翻论文。", f"{REPO_URL}/blob/main/content/public-reader/topics.md", findings_url, "阅读入口"),
        ("R006", "06", "最常见 30 个补剂", "30 common supplements", "想查补剂的人", "先看常见误解和安全边界。", f"{REPO_URL}/blob/main/content/public-reader/supplements-top-30.md", cards_url, "补剂入口"),
        ("R007", "07", "护肤与外观抗老速读", "Skin and appearance guide", "关心防晒、皱纹和医美的人", "把皮肤改善和延长寿命分开看。", f"{REPO_URL}/blob/main/content/public-reader/skin.md", cards_url, "皮肤入口"),
        ("R008", "08", "哪些内容必须先问医生", "Ask a clinician first", "看到药物、医美或高剂量补剂的人", "识别不能自己照表行动的内容。", f"{REPO_URL}/blob/main/content/public-reader/doctor-first.md", nav_url, "安全边界"),
        ("R009", "09", "研究热力图", "Research heatmaps", "普通读者、内容团队", "看研究多不多，不把热度误当效果。", f"{REPO_URL}/blob/main/docs/research-heatmap-2026-07.html", heatmap_url, "视觉资产"),
        ("R010", "10", "前 50 个常见成分卡", "Top 50 ingredient cards", "普通读者、内容团队", "一张卡看一个成分的证据和提醒。", f"{REPO_URL}/tree/main/docs/assets/visual-assets/2026-07/ingredient-cards", cards_url, "视觉资产"),
        ("R011", "11", "公开全量 CSV 数据包", "Public CSV package", "研究者、维护者", "下载冻结数据进行复核；总行数不是互不重复论文数。", f"{REPO_URL}/tree/main/public-data", library_url, "公开数据"),
        ("R012", "12", "证据矩阵", "Evidence matrix", "研究者、编辑", f"查看进入矩阵的 {count_csv(PUBLIC / 'evidence-matrix-2026-07.csv'):,} 条记录。", f"{REPO_URL}/blob/main/public-data/evidence-matrix-2026-07.csv", matrix_url, "公开数据"),
        ("R013", "13", "发帖资产面板", "Posting asset dashboard", "内容团队、助理", "集中找图片、文案和下载入口。", f"{REPO_URL}/blob/main/docs/{DASHBOARD_FILE}", wall_url, "内容生产"),
        ("R014", "14", "飞书公开资产总索引", "Feishu public asset index", "所有读者", "按阅读、图片和研究数据三类找表。", f"{REPO_URL}/blob/main/docs/feishu-public-assets-2026-07.md", nav_url, "飞书入口"),
    ]

    fields = [
        "entry_id",
        "公开标题",
        "阅读顺序",
        "中文名称",
        "English title",
        "适合谁",
        "一句话说明",
        "GitHub链接",
        "飞书链接",
        "资产类型",
        "冻结日期",
        "复核日期",
        "品牌标识",
        "Brand",
        "SEO关键词",
        "状态",
    ]
    rows = []
    for entry_id, order, title_zh, title_en, audience, note, github_url, feishu_url, asset_type in items:
        rows.append(
            {
                "entry_id": entry_id,
                "公开标题": f"{BRAND} | {title_zh}",
                "阅读顺序": order,
                "中文名称": title_zh,
                "English title": title_en,
                "适合谁": audience,
                "一句话说明": note,
                "GitHub链接": github_url,
                "飞书链接": feishu_url,
                "资产类型": asset_type,
                "冻结日期": FREEZE_DATE,
                "复核日期": REVIEW_DATE,
                "品牌标识": BRAND,
                "Brand": "yulcell",
                "SEO关键词": "宇多Yul细胞/yulcell, yulcell, 长寿抗衰证据图谱, 健康寿命证据图谱",
                "状态": "公开",
            }
        )
    write_csv(DATA / "feishu_reader_navigation_2026_07.csv", rows, fields)
    return rows


def build_feishu_index(active_tables: list[dict[str, str]]) -> None:
    snapshot_candidates = count_csv(PUBLIC / "candidate-sources-2026-07.csv")
    previous_candidates = PREVIOUS_CANDIDATES
    added_since_previous = max(0, snapshot_candidates - previous_candidates)
    lines = [
        f"# 飞书公开资产索引（{RELEASE_LABEL}） / Feishu Public Assets",
        "",
        f"**品牌 / Brand：** {BRAND}<br>",
        f"**冻结日期 / Snapshot date：** {FREEZE_DATE}<br>",
        f"**复核日期 / Last reviewed：** {REVIEW_DATE}",
        "",
        "这页把飞书多维表格分成三类：先读什么、图片在哪里、研究数据在哪里。第一次打开项目的人先看“阅读导航”，不必直接进入上万条文献表。",
        "",
        "This page groups the Feishu Bitable assets into reading, visual, and research layers. New readers should start with the reading navigation rather than the full literature tables.",
        "",
        "## 最短阅读路线 / Shortest Route",
        "",
    ]
    nav = next((row for row in active_tables if row.get("表名") == NAV_TABLE_NAME), None)
    heatmap = next((row for row in active_tables if row.get("表名") == "视觉资产_热力图图片_2026-07"), None)
    cards = next((row for row in active_tables if row.get("表名") == "公开入口_前50成分单卡_2026-07"), None)
    for label, row, note in [
        ("1. 阅读导航 / Reading navigation", nav, "先选你真正想看的内容。"),
        ("2. 热力图 / Heatmaps", heatmap, "看研究热度和证据分布，不当效果排行榜。"),
        ("3. 成分卡 / Ingredient cards", cards, "查常见补剂与成分的证据边界。"),
    ]:
        if row:
            lines.append(f"- [{label}]({row.get('飞书链接', '')})：{note}")
    if not nav:
        lines.append("- 阅读导航表正在同步；可先从 GitHub 普通读者入口开始。")

    lines.extend(
        [
            "",
            "## 全部多维表格 / All Bitable Tables",
            "",
            "| 类别 | 表名 | 记录数 | 状态 | 入口 |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for row in active_tables:
        category = row.get("类别", "")
        name = row.get("表名", "")
        count = row.get("记录数", "")
        status = row.get("状态", "")
        url = row.get("飞书链接", "")
        lines.append(f"| {category} | {name} | {count} | {status} | [打开飞书]({url}) |")

    lines.extend(
        [
            "",
            "## 两个数字为什么不同 / Why Two Candidate Counts Differ",
            "",
            f"- {snapshot_candidates:,} 条：{FREEZE_DATE} 公开冻结快照，GitHub 与飞书 2026-07 表保持一致，便于复核和引用。",
            f"- {previous_candidates:,} 条：{PREVIOUS_SNAPSHOT_DATE} 历史冻结快照，用来计算本轮新增 {added_since_previous:,} 条候选。",
            f"- 工作候选库会继续自动增长；后续新增不倒灌进 {RELEASE_SHORT}冻结快照，而是进入下一次发布。",
            "",
            "## 使用边界 / Boundary",
            "",
            "这些多维表格是证据导航和内容复核资产，不是购买清单、处方、剂量方案、诊断工具或医美操作建议。飞书页面能否被搜索引擎收录，还取决于对应文档和多维表格的公开分享权限。",
            "",
            f"GitHub source of truth: [{REPO_URL}]({REPO_URL})",
            "",
        ]
    )
    (DOCS / "feishu-public-assets-2026-07.md").write_text("\n".join(lines), encoding="utf-8")


def build_html(active_tables: list[dict[str, str]], links: dict[str, str]) -> None:
    snapshot_candidates = count_csv(PUBLIC / "candidate-sources-2026-07.csv")
    previous_candidates = PREVIOUS_CANDIDATES
    literature = count_csv(PUBLIC / "literature-library-2026-07.csv")
    findings = count_csv(PUBLIC / "evidence-findings-2026-07.csv")
    shortlist = count_csv(PUBLIC / "shortlist-sources-2026-07.csv")
    matrix = count_csv(PUBLIC / "evidence-matrix-2026-07.csv")
    public_total = snapshot_candidates + literature + findings + shortlist + matrix
    added_since_previous = max(0, snapshot_candidates - previous_candidates)
    visual_count = len(list(VISUALS.glob("*.png"))) + len(list((VISUALS / "ingredient-cards").glob("*.png")))

    images = {
        "dashboard": data_uri(VISUALS / "heatmap-dashboard-2026-07.png"),
        "yield": data_uri(VISUALS / "topic-evidence-yield-2026-07.png"),
        "retractions": data_uri(VISUALS / "retraction-density-2026-07.png"),
        "cards": data_uri(VISUALS / "ingredient-card-wall-2026-07.png"),
    }
    nav_url = links.get(NAV_TABLE_NAME, f"{REPO_URL}/blob/main/docs/feishu-public-assets-2026-07.md")
    summary_text = (
        f"{BRAND} {RELEASE_LABEL}证据图谱：公开冻结候选文献 {snapshot_candidates:,} 条、"
        f"证据发现 {findings:,} 条、证据矩阵 {matrix:,} 条、公开 CSV {public_total:,} 行，"
        f"以及 {visual_count} 张图片资产。候选文献不等于已证实结论，药物、医美和高剂量补剂仍需专业评估。"
    )

    html_text = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <link rel="icon" href="data:,">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="宇多Yul细胞/yulcell {RELEASE_LABEL}长寿抗衰证据图谱公开更新，含 GitHub、飞书多维表格、热力图和公开数据包。">
  <meta name="keywords" content="宇多Yul细胞/yulcell,yulcell,长寿抗衰证据图谱,健康寿命证据图谱,longevity evidence atlas">
  <title>宇多Yul细胞/yulcell | {RELEASE_LABEL}公开更新</title>
  <style>
    :root {{ --ink:#182126; --muted:#5d6a70; --paper:#ffffff; --wash:#f2f5f4; --teal:#176f73; --teal-soft:#dceced; --coral:#b74c3c; --line:#ccd5d4; --max:1160px; }}
    * {{ box-sizing:border-box; }}
    html {{ scroll-behavior:smooth; }}
    body {{ margin:0; color:var(--ink); background:var(--paper); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif; line-height:1.7; letter-spacing:0; }}
    a {{ color:var(--teal); text-underline-offset:3px; }}
    button, a.action {{ min-height:44px; font:inherit; }}
    .hero {{ background:#12252a; color:#fff; padding:54px 24px 46px; border-bottom:6px solid var(--teal); }}
    .hero-inner {{ max-width:var(--max); margin:0 auto; }}
    .brand {{ margin:0 0 18px; font-size:18px; font-weight:700; color:#a9d6d7; }}
    h1 {{ max-width:820px; margin:0; font-size:clamp(38px,6vw,72px); line-height:1.08; letter-spacing:0; }}
    .lede {{ max-width:760px; margin:22px 0 0; font-size:20px; color:#d7e3e4; }}
    .actions {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:28px; }}
    .action, .copy-button {{ display:inline-flex; align-items:center; justify-content:center; padding:10px 15px; border:1px solid #9bc9cb; border-radius:6px; background:transparent; color:#fff; text-decoration:none; cursor:pointer; }}
    .action.primary {{ background:#d9eeef; color:#12383b; border-color:#d9eeef; font-weight:700; }}
    .copy-button:hover, .action:hover {{ background:#fff; color:#153f42; }}
    .subnav {{ position:sticky; top:0; z-index:20; background:rgba(255,255,255,.96); border-bottom:1px solid var(--line); overflow:auto; }}
    .subnav-inner {{ max-width:var(--max); margin:0 auto; display:flex; gap:24px; padding:11px 24px; white-space:nowrap; }}
    .subnav a {{ color:var(--ink); text-decoration:none; font-size:14px; font-weight:650; }}
    .band {{ padding:58px 24px; }}
    .band.alt {{ background:var(--wash); }}
    .inner {{ max-width:var(--max); margin:0 auto; }}
    .eyebrow {{ color:var(--teal); font-weight:750; margin:0 0 6px; }}
    h2 {{ margin:0 0 18px; font-size:34px; line-height:1.2; letter-spacing:0; }}
    h3 {{ margin:28px 0 8px; font-size:22px; letter-spacing:0; }}
    .intro {{ max-width:780px; color:var(--muted); font-size:18px; }}
    .stats {{ display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); border-top:1px solid var(--line); border-bottom:1px solid var(--line); margin-top:32px; }}
    .stat {{ padding:24px 18px; border-right:1px solid var(--line); min-width:0; }}
    .stat:last-child {{ border-right:0; }}
    .stat strong {{ display:block; font-size:34px; color:var(--teal); line-height:1.15; overflow-wrap:anywhere; }}
    .stat span {{ display:block; margin-top:6px; color:var(--muted); font-size:14px; }}
    .pipeline {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:0; margin-top:30px; border-top:1px solid var(--line); }}
    .stage {{ padding:25px 24px 12px 0; border-bottom:1px solid var(--line); }}
    .stage + .stage {{ padding-left:24px; border-left:1px solid var(--line); }}
    .stage b {{ display:block; color:var(--teal); font-size:15px; }}
    .stage strong {{ display:block; margin:7px 0; font-size:25px; }}
    .stage p {{ margin:0; color:var(--muted); }}
    .freeze-note {{ margin:30px 0 0; padding:18px 20px; border-left:5px solid var(--coral); background:#fff6f3; }}
    .figure {{ margin:32px 0 0; }}
    .figure button {{ display:block; width:100%; padding:0; border:0; background:transparent; cursor:zoom-in; text-align:left; }}
    .figure img {{ display:block; width:100%; height:auto; border:1px solid var(--line); }}
    .figure figcaption {{ margin-top:12px; color:var(--muted); font-size:14px; }}
    .split {{ display:grid; grid-template-columns:1fr 1fr; gap:38px; align-items:start; }}
    .plain-table {{ width:100%; border-collapse:collapse; margin-top:20px; }}
    .plain-table th, .plain-table td {{ padding:12px 10px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
    .plain-table th {{ color:var(--muted); font-size:13px; }}
    .route {{ display:grid; grid-template-columns:150px 1fr; gap:0; border-top:1px solid var(--line); }}
    .route dt, .route dd {{ margin:0; padding:16px 0; border-bottom:1px solid var(--line); }}
    .route dt {{ font-weight:750; color:var(--teal); }}
    .route dd {{ color:var(--muted); }}
    .boundary {{ border-left:5px solid var(--coral); padding-left:22px; }}
    footer {{ padding:34px 24px; background:#12252a; color:#d7e3e4; }}
    footer .inner {{ display:flex; justify-content:space-between; gap:30px; flex-wrap:wrap; }}
    footer a {{ color:#a9d6d7; }}
    .reveal {{ opacity:1; transform:none; }}
    .reveal.visible {{ animation:reveal-in .45s ease both; }}
    @keyframes reveal-in {{ from {{ opacity:.72; transform:translateY(8px); }} to {{ opacity:1; transform:none; }} }}
    dialog {{ width:min(94vw,1280px); max-height:92vh; border:0; border-radius:6px; padding:12px; background:#fff; }}
    dialog::backdrop {{ background:rgba(10,20,23,.82); }}
    dialog img {{ display:block; max-width:100%; max-height:84vh; margin:auto; }}
    .close {{ position:absolute; top:14px; right:14px; width:44px; height:44px; border:1px solid var(--line); border-radius:50%; background:#fff; color:var(--ink); font-size:28px; cursor:pointer; }}
    @media (max-width:800px) {{
      .hero {{ padding:38px 20px 34px; }}
      h1 {{ font-size:42px; }}
      .lede {{ font-size:17px; }}
      .band {{ padding:42px 20px; }}
      h2 {{ font-size:29px; }}
      .stats {{ grid-template-columns:1fr 1fr; }}
      .stat {{ border-bottom:1px solid var(--line); }}
      .stat:nth-child(even) {{ border-right:0; }}
      .pipeline, .split {{ grid-template-columns:1fr; }}
      .stage + .stage {{ padding-left:0; border-left:0; }}
      .route {{ grid-template-columns:1fr; }}
      .route dt {{ padding-bottom:4px; border-bottom:0; }}
      .route dd {{ padding-top:0; }}
    }}
    @media (prefers-reduced-motion:reduce) {{ html {{ scroll-behavior:auto; }} .reveal.visible {{ animation:none; }} }}
  </style>
</head>
<body>
  <header class="hero">
    <div class="hero-inner">
      <p class="brand">{esc(BRAND)} · Longevity Anti-Aging Evidence Atlas</p>
      <h1>{RELEASE_LABEL}<br>公开更新</h1>
      <p class="lede">把 {snapshot_candidates:,} 条候选资料、{findings:,} 条证据发现和 {visual_count} 张图片，整理成普通读者也能顺着读下去的证据地图。</p>
      <div class="actions">
        <a class="action primary" href="{esc(REPO_URL)}/blob/main/content/public-reader/{RELEASE_FILE}">先读普通版说明</a>
        <a class="action" href="{esc(nav_url)}">打开飞书导航</a>
        <button class="copy-button" id="copy-summary" type="button">复制 {RELEASE_SHORT}摘要</button>
      </div>
    </div>
  </header>
  <nav class="subnav" aria-label="页面目录"><div class="subnav-inner">
    <a href="#summary">更新总览</a><a href="#pipeline">三个数据层</a><a href="#visuals">图片怎么看</a><a href="#access">公开入口</a><a href="#boundary">使用边界</a>
  </div></nav>

  <main>
    <section class="band" id="summary"><div class="inner reveal">
      <p class="eyebrow">30 秒看完 / 30-second summary</p>
      <h2>这次更新的重点不是“论文更多”，而是“读起来更清楚”</h2>
      <p class="intro">{RELEASE_SHORT}版补充了近期候选文献，扩大证据发现和证据矩阵，重做热力图与成分卡，并把 GitHub 和飞书入口放到同一条阅读路线中。新增候选只是等待复核的资料，不代表结论已经被证明。</p>
      <div class="stats">
        <div class="stat"><strong>{snapshot_candidates:,}</strong><span>候选文献冻结快照</span></div>
        <div class="stat"><strong>{findings:,}</strong><span>证据发现</span></div>
        <div class="stat"><strong>{matrix:,}</strong><span>证据矩阵</span></div>
        <div class="stat"><strong>{public_total:,}</strong><span>公开 CSV 总行数</span></div>
        <div class="stat"><strong>{visual_count}</strong><span>公开图片资产</span></div>
      </div>
      <div class="freeze-note"><strong>数字口径：</strong>{snapshot_candidates:,} 条是 {FREEZE_DATE} 的公开冻结快照；相对 {PREVIOUS_SNAPSHOT_DATE} 的 {previous_candidates:,} 条，新增 {added_since_previous:,} 条。后续自动检索会进入下一轮发布，不会倒灌修改这份 {RELEASE_SHORT}快照。</div>
      <div class="freeze-note"><strong>分类保护：</strong>研究方案和评论、社论、勘误等非原始研究最高为 E；系统先分清人体与动物，再判断随机设计。自动分层仍不能替代人工全文复核。</div>
    </div></section>

    <section class="band alt" id="pipeline"><div class="inner reveal">
      <p class="eyebrow">先分清三个数据层</p>
      <h2>候选文献、证据发现、证据矩阵不是同一件事</h2>
      <div class="pipeline">
        <div class="stage"><b>第一层</b><strong>{snapshot_candidates:,} 条候选文献</strong><p>像图书馆刚收到的新书。先收进来，可能相关，但还不能直接拿来下结论。</p></div>
        <div class="stage"><b>第二层</b><strong>{findings:,} 条证据发现</strong><p>像读书笔记。开始记录研究对象、研究设计、终点和可能被夸大的地方。</p></div>
        <div class="stage"><b>第三层</b><strong>{matrix:,} 条证据矩阵</strong><p>像整理好的地图。适合按主题、人体相关性、终点和证据等级比较。</p></div>
      </div>
      <p class="intro" style="margin-top:28px">最重要的一句：进入候选库，不等于有效；进入矩阵，也不等于每个人都应该行动。</p>
    </div></section>

    <section class="band" id="visuals"><div class="inner reveal">
      <p class="eyebrow">图片不是排行榜</p>
      <h2>热力图回答“研究在哪里”，不回答“什么一定最有效”</h2>
      <p class="intro">颜色越深通常表示进入矩阵的研究更多。它能帮助读者发现研究集中区，但不能替代研究质量、真实健康结局和安全边界。</p>
      <figure class="figure"><button type="button" class="zoom" data-image="dashboard" title="放大热力图总览"><img src="{images['dashboard']}" alt="2020 至 2026 年主题研究热力图和 A 到 E 证据等级热力图"></button><figcaption>热力图总览：2026 年尚未结束，不能直接和完整年度比较。点击图片可放大。</figcaption></figure>
    </div></section>

    <section class="band alt"><div class="inner reveal split">
      <div>
        <p class="eyebrow">证据产出率</p>
        <h2>研究多，不一定高等级证据多</h2>
        <p class="intro">同样是 A/B 级证据，A 级占比越高，越接近高质量人体或系统评价证据。但这个比例仍然不是个人行动建议。</p>
        <figure class="figure"><button type="button" class="zoom" data-image="yield" title="放大证据产出率图片"><img src="{images['yield']}" alt="各主题 A 级证据占比图"></button><figcaption>主题证据产出率：用于比较证据结构，不用于比较产品。</figcaption></figure>
      </div>
      <div>
        <p class="eyebrow">撤稿风险</p>
        <h2>论文数量多，也要看风险信号</h2>
        <p class="intro">撤稿密度是复核提醒，不是某个成分“有效”或“无效”的最终判决。它提醒编辑不要只拿单篇论文做宣传。</p>
        <figure class="figure"><button type="button" class="zoom" data-image="retractions" title="放大撤稿密度图片"><img src="{images['retractions']}" alt="撤稿密度观察图"></button><figcaption>撤稿密度：要同时看发表分母、撤稿数量和具体原因。</figcaption></figure>
      </div>
    </div></section>

    <section class="band"><div class="inner reveal">
      <p class="eyebrow">给普通读者和内容团队</p>
      <h2>50 张成分卡把重点压缩到一页</h2>
      <p class="intro">每张卡只回答几个问题：它是什么、证据大概在哪一层、最容易被怎么夸大、什么情况下要先问专业人员。卡片方便入门，完整判断仍要回到证据表和原始文献。</p>
      <figure class="figure"><button type="button" class="zoom" data-image="cards" title="放大前 50 成分卡片墙"><img src="{images['cards']}" alt="前 50 个常见补剂和成分卡片墙"></button><figcaption>前 50 个常见成分卡片墙；单张高清图可在 GitHub 或飞书成分卡表中打开。</figcaption></figure>
    </div></section>

    <section class="band alt" id="access"><div class="inner reveal">
      <p class="eyebrow">公开入口 / Public access</p>
      <h2>按你的目的进入，不必从上万条表格开始</h2>
      <dl class="route">
        <dt>第一次看</dt><dd><a href="{REPO_URL}/blob/main/content/public-reader/start-here.md">普通读者入口</a> → <a href="{REPO_URL}/blob/main/content/public-reader/ten-takeaways.md">15 条结论</a> → <a href="{REPO_URL}/blob/main/content/public-reader/evidence-weight.md">证据权重</a></dd>
        <dt>想看图片</dt><dd><a href="{links.get('视觉资产_热力图图片_2026-07', '')}">飞书热力图</a> · <a href="{links.get('公开入口_前50成分单卡_2026-07', '')}">飞书 50 张成分卡</a> · <a href="{REPO_URL}/tree/main/docs/assets/visual-assets/2026-07">GitHub 图片目录</a></dd>
        <dt>想查数据</dt><dd><a href="{REPO_URL}/tree/main/public-data">GitHub 公开 CSV 包</a> · <a href="{links.get('公开数据_证据矩阵_2026-07', '')}">飞书证据矩阵</a> · <a href="{links.get('公开数据_全量文献候选库_2026-07', '')}">飞书候选文献库</a></dd>
        <dt>要做内容</dt><dd><a href="{REPO_URL}/blob/main/docs/{DASHBOARD_FILE}">自包含发帖面板</a> · <a href="{REPO_URL}/blob/main/docs/feishu-public-assets-2026-07.md">飞书公开资产索引</a></dd>
      </dl>
      <p class="intro" style="margin-top:28px">当前飞书公开索引记录 {len(active_tables)} 张 active 表。飞书能否被外部搜索引擎收录，仍取决于对应页面的公开分享权限。</p>
    </div></section>

    <section class="band" id="boundary"><div class="inner reveal">
      <div class="boundary">
        <p class="eyebrow">最后保留这条边界</p>
        <h2>这是一张证据地图，不是购买清单</h2>
        <p class="intro">不要把候选文献当成定论，不要把指标改善说成返老还童，不要把动物延寿说成人类延寿。药物、注射、医美、高剂量或长期补剂、慢病指标和个人方案，需要医生或合格专业人员评估。</p>
      </div>
    </div></section>
  </main>

  <footer><div class="inner"><div><strong>{esc(BRAND)}</strong><br>{RELEASE_LABEL}长寿抗衰与健康寿命证据图谱</div><div><a href="{REPO_URL}">GitHub</a> · <a href="{esc(nav_url)}">Feishu</a> · 冻结 {FREEZE_DATE} · 复核 {REVIEW_DATE}</div></div></footer>

  <dialog id="lightbox"><button class="close" type="button" title="关闭原图" aria-label="关闭原图">×</button><img alt="放大的证据图"></dialog>
  <script>
    const SUMMARY = {json.dumps(summary_text, ensure_ascii=False)};
    const IMAGES = {{ dashboard:{json.dumps(images['dashboard'])}, yield:{json.dumps(images['yield'])}, retractions:{json.dumps(images['retractions'])}, cards:{json.dumps(images['cards'])} }};
    const copyButton = document.getElementById('copy-summary');
    copyButton.addEventListener('click', async () => {{
      await navigator.clipboard.writeText(SUMMARY);
      const old = copyButton.textContent;
      copyButton.textContent = '已复制';
      setTimeout(() => copyButton.textContent = old, 1600);
    }});
    const dialog = document.getElementById('lightbox');
    const dialogImage = dialog.querySelector('img');
    document.querySelectorAll('.zoom').forEach(button => button.addEventListener('click', () => {{
      dialogImage.src = IMAGES[button.dataset.image];
      dialogImage.alt = button.querySelector('img').alt;
      dialog.showModal();
    }}));
    dialog.querySelector('.close').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => {{ if (event.target === dialog) dialog.close(); }});
    if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {{
      const observer = new IntersectionObserver(entries => entries.forEach(entry => {{ if (entry.isIntersecting) entry.target.classList.add('visible'); }}), {{ threshold:0.08 }});
      document.querySelectorAll('.reveal').forEach(node => observer.observe(node));
    }} else {{ document.querySelectorAll('.reveal').forEach(node => node.classList.add('visible')); }}
  </script>
</body>
</html>
'''
    (DOCS / REPORT_FILE).write_text(html_text, encoding="utf-8")


def main() -> None:
    active_tables, links = table_links()
    navigation_rows(links)
    build_feishu_index(active_tables)
    build_html(active_tables, links)
    print("built data/feishu_reader_navigation_2026_07.csv")
    print("built docs/feishu-public-assets-2026-07.md")
    print(f"built docs/{REPORT_FILE}")


if __name__ == "__main__":
    main()
