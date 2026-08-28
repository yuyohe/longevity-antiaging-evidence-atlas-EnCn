from __future__ import annotations

import base64
import csv
import json
import os
from datetime import date
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
BRAND = os.environ.get("PUBLIC_BRAND_NAME", "宇多Yul细胞/yulcell")
MONTH = os.environ.get("EVIDENCE_ATLAS_ASSET_MONTH", "2026-06")
MONTH_UNDERSCORE = MONTH.replace("-", "_")
RUN_DATE = os.environ.get("EVIDENCE_ATLAS_UPDATE_DATE", date.today().isoformat())
UPDATE_LABEL = os.environ.get(
    "EVIDENCE_ATLAS_UPDATE_LABEL",
    "2026 年 7 月中旬" if MONTH == "2026-07" else f"{MONTH} 更新",
)
RELEASE_FILE = os.environ.get("EVIDENCE_ATLAS_RELEASE_FILE", "mid-july-2026-update.md")
PUBLIC_REPORT_FILE = os.environ.get("EVIDENCE_ATLAS_PUBLIC_REPORT_FILE", "mid-july-public-update-2026-07.html")
BASELINE_LABEL = os.environ.get("EVIDENCE_ATLAS_BASELINE_LABEL", "6 月底冻结版")
BASELINE_DELTA = int(os.environ.get("EVIDENCE_ATLAS_BASELINE_DELTA", "1451" if MONTH == "2026-07" else "0"))
CURATION_METRICS_PATH = Path(
    os.environ.get(
        "EVIDENCE_ATLAS_CURATION_METRICS",
        ROOT / "data" / f"curation_release_metrics_{MONTH_UNDERSCORE}.json",
    )
)
if not CURATION_METRICS_PATH.is_absolute():
    CURATION_METRICS_PATH = ROOT / CURATION_METRICS_PATH
OUT = ROOT / "docs" / f"yulcell-posting-asset-dashboard-{RUN_DATE}.html"

MAIN_IMAGES = [
    ("heatmap-dashboard", "热力图总览", ROOT / "build" / "visual-assets" / f"heatmap-dashboard-{MONTH}.png"),
    ("heatmap-topic-year", "主题-年份热力图", ROOT / "build" / "visual-assets" / f"heatmap-topic-year-{MONTH}.png"),
    ("heatmap-topic-evidence", "主题-证据等级热力图", ROOT / "build" / "visual-assets" / f"heatmap-topic-evidence-{MONTH}.png"),
    ("ingredient-card-wall", "成分卡片墙", ROOT / "build" / "visual-assets" / f"ingredient-card-wall-{MONTH}.png"),
    ("evidence-yield-ingredients", "成分证据产出图", ROOT / "build" / "visual-assets" / f"evidence-yield-ingredients-{MONTH}.png"),
    ("retraction-density", "撤稿密度图", ROOT / "build" / "visual-assets" / f"retraction-density-{MONTH}.png"),
    ("topic-evidence-yield", "主题证据产出图", ROOT / "build" / "visual-assets" / f"topic-evidence-yield-{MONTH}.png"),
]

GITHUB_LINKS = [
    ("GitHub 仓库", "https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn"),
    ("GitHub README", "https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn/blob/main/README.md"),
    ("中文 README", "https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn/blob/main/README.zh-CN.md"),
    (f"{UPDATE_LABEL}读者说明", f"https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn/blob/main/content/public-reader/{RELEASE_FILE}"),
    (f"{UPDATE_LABEL}自包含报告", f"https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn/blob/main/docs/{PUBLIC_REPORT_FILE}"),
    ("品牌资产索引", "https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn/blob/main/docs/yulcell-brand-index.md"),
    ("公开数据说明", "https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn/blob/main/public-data/README.md"),
]

REPORT_LINKS = [
    (f"{UPDATE_LABEL}普通读者说明", ROOT / "content" / "public-reader" / RELEASE_FILE),
    (f"{UPDATE_LABEL}自包含报告", ROOT / "docs" / PUBLIC_REPORT_FILE),
    ("飞书公开资产索引", ROOT / "docs" / f"feishu-public-assets-{MONTH}.md"),
    ("月度更新 HTML", ROOT / "docs" / f"monthly-update-{MONTH}.html"),
    ("月度更新 Markdown", ROOT / "content" / "public-reader" / f"monthly-update-{MONTH}.md"),
    ("研究热力图 HTML", ROOT / "docs" / f"research-heatmap-{MONTH}.html"),
    ("本轮精编指标 JSON", CURATION_METRICS_PATH),
    ("飞书大众读者包", ROOT / "build" / "feishu-public-reader"),
    ("飞书全量 Markdown 包", ROOT / "build" / "feishu-docs"),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def count_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return sum(1 for _ in csv.DictReader(f))


def curation_metrics() -> dict[str, Any] | None:
    if not CURATION_METRICS_PATH.exists():
        return None
    return json.loads(CURATION_METRICS_PATH.read_text(encoding="utf-8"))


def data_url(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def image_record(image_id: str, title: str, path: Path) -> dict[str, object]:
    with Image.open(path) as image:
        width, height = image.size
    return {
        "id": image_id,
        "title": title,
        "filename": path.name,
        "localPath": str(path),
        "size": path.stat().st_size,
        "width": width,
        "height": height,
        "dataUrl": data_url(path),
    }


def local_link(label: str, path: Path, note: str = "") -> dict[str, str]:
    return {"label": label, "value": str(path), "note": note}


def public_tables() -> list[dict[str, str]]:
    specs = [
        ("候选来源原始表", ROOT / "public-data" / f"candidate-sources-{MONTH}.csv"),
        ("全量文献候选库", ROOT / "public-data" / f"literature-library-{MONTH}.csv"),
        ("入选短名单", ROOT / "public-data" / f"shortlist-sources-{MONTH}.csv"),
        ("证据发现表", ROOT / "public-data" / f"evidence-findings-{MONTH}.csv"),
        ("证据矩阵", ROOT / "public-data" / f"evidence-matrix-{MONTH}.csv"),
    ]
    return [local_link(label, path, f"{count_rows(path):,} rows") for label, path in specs]


def feishu_links() -> list[dict[str, str]]:
    current_files = [
        ROOT / "data" / f"feishu_live_tables_{MONTH_UNDERSCORE}.csv",
        ROOT / "data" / f"feishu_full_public_data_links_{MONTH_UNDERSCORE}.csv",
        ROOT / "data" / f"visual_feishu_links_{MONTH_UNDERSCORE}.csv",
    ]
    fallback_files = [ROOT / "data" / "feishu_live_tables_2026_05.csv"]
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for file in current_files:
        for row in read_csv(file):
            url = row.get("飞书链接") or row.get("url") or row.get("URL") or row.get("链接") or ""
            status = (row.get("状态") or row.get("status") or "active").strip()
            if not url or status not in {"active", "synced", "ok"}:
                continue
            if url in seen:
                continue
            seen.add(url)
            label = row.get("表名") or row.get("asset_group") or row.get("资产名称") or row.get("name") or file.stem
            note = row.get("说明") or row.get("类别") or row.get("asset_key") or file.name
            count = row.get("rows") or row.get("记录数") or ""
            if count:
                note = f"{note} · {count} rows"
            rows.append({"label": label, "value": url, "note": note})
    if rows:
        return rows
    for file in fallback_files:
        for row in read_csv(file):
            url = row.get("飞书链接") or row.get("url") or row.get("URL") or row.get("链接") or ""
            status = (row.get("状态") or row.get("status") or "active").strip()
            if not url or status not in {"active", "synced", "ok"} or url in seen:
                continue
            seen.add(url)
            label = row.get("表名") or row.get("asset_group") or row.get("资产名称") or row.get("name") or file.stem
            note = row.get("说明") or row.get("类别") or row.get("asset_key") or file.name
            rows.append({"label": label, "value": url, "note": note})
    return rows


def stats() -> list[dict[str, str]]:
    table_rows = {row["label"]: row["note"].split()[0] for row in public_tables()}
    public_row_total = sum(int(row["note"].split()[0].replace(",", "")) for row in public_tables())
    release = curation_metrics()
    intake_stats = (
        [
            {"value": f"{release['search']['new_rows']:,}", "label": "本轮 PubMed 新候选"},
            {"value": f"{release['after']['recent_candidates_retained']:,}", "label": "近期候选最终保留"},
        ]
        if release
        else [{"value": f"{BASELINE_DELTA:,}", "label": f"较 {BASELINE_LABEL}新增候选"}]
    )
    return [
        {"value": table_rows.get("全量文献候选库", "0"), "label": "候选文献库"},
        {"value": table_rows.get("证据发现表", "0"), "label": "evidence findings"},
        {"value": table_rows.get("证据矩阵", "0"), "label": "evidence matrix"},
        {"value": f"{public_row_total:,}", "label": "公开 CSV 总行数"},
        *intake_stats,
        {"value": "50", "label": "单成分卡"},
        {"value": "7", "label": "主图资产"},
    ]


def card_assets() -> list[dict[str, object]]:
    manifest = read_csv(ROOT / "data" / f"visual_ingredient_cards_{MONTH_UNDERSCORE}.csv")
    paths = [ROOT / row["local_path"] for row in manifest if row.get("local_path")]
    if not paths:
        paths = sorted((ROOT / "build" / "visual-assets" / "ingredient-cards").glob("*.png"))
    return [image_record(path.stem, path.stem, path) for path in paths]


def post_copy() -> str:
    values = {item["label"]: item["value"] for item in stats()}
    release = curation_metrics()
    if release:
        intake_lines = (
            f"- 本轮 PubMed 新候选：{release['search']['new_rows']:,} 条\n"
            f"- 近期候选最终保留：{release['after']['recent_candidates_retained']:,} 条"
        )
        curation_note = (
            f"本次不是继续堆数量：当前候选库从 {release['before']['candidate_records']:,} 条"
            f"调整为 {release['after']['candidate_records']:,} 条。已满额主题以替换为主，"
            "退出记录保留在日志、归档和 Git 历史中。"
        )
    else:
        intake_lines = f"- 相对 {BASELINE_LABEL}新增候选：{BASELINE_DELTA:,} 条"
        curation_note = ""
    return f"""宇多Yul细胞/yulcell {UPDATE_LABEL}抗衰证据图谱更新：

这次把 PubMed 近期窗口扩到 {RUN_DATE.replace("-", "/")}，并重新生成公开表格、飞书多维表格和图片资产。

{curation_note}

核心规模：
- 候选文献库：{values["候选文献库"]} 条
- evidence findings：{values["evidence findings"]} 条
- evidence matrix：{values["evidence matrix"]} 条
- 公开 CSV 数据包：{values["公开 CSV 总行数"]} 行
{intake_lines}
- 单成分卡：50 张
- 主图资产：7 张

怎么看：
- 热力图看研究活跃度和证据分布，不是有效性排行榜。
- 成分卡帮普通读者快速识别证据、误解和注意事项。
- 撤稿密度图提醒大家不要只看论文数量，也要看风险信号。

边界：
这些资料用于证据整理和内容创作，不是个人医疗建议、诊断、处方、剂量方案、医美操作建议或购买推荐。"""


HTML_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <link rel="icon" href="data:,">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>__BRAND__ __UPDATE_LABEL__发帖资产面板</title>
  <style>
    :root {
      --ink: #1f2933;
      --muted: #5e6b78;
      --line: #d8e0e7;
      --paper: #ffffff;
      --soft: #f3f7f6;
      --brand: #176b4b;
      --deep: #14232f;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
      color: var(--ink);
      background: #eef3f5;
      line-height: 1.65;
    }
    header {
      background: var(--deep);
      color: #fff;
      padding: 32px 24px 28px;
      border-bottom: 5px solid #75b79f;
    }
    header .wrap, main { max-width: 1240px; margin: 0 auto; }
    h1 { margin: 0 0 10px; font-size: 34px; line-height: 1.2; letter-spacing: 0; }
    h2 { margin: 0 0 14px; font-size: 23px; letter-spacing: 0; }
    h3 { margin: 0 0 8px; font-size: 17px; letter-spacing: 0; }
    p { margin: 0 0 12px; }
    main { padding: 22px 18px 52px; }
    section {
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 20px;
      margin: 16px 0;
    }
    .toolbar { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }
    button, a.button {
      border: 1px solid #b8c7d3;
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      padding: 9px 12px;
      font-size: 14px;
      cursor: pointer;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      min-height: 38px;
    }
    button.primary, a.button.primary { background: var(--brand); border-color: var(--brand); color: #fff; }
    button.secondary { background: #eef6f2; border-color: #bdd9cc; color: #174b39; }
    .notice {
      background: #eef6f2;
      border-left: 4px solid var(--brand);
      border-radius: 6px;
      padding: 12px;
      color: #153d2f;
    }
    .stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(155px, 1fr));
      gap: 10px;
      margin-top: 16px;
    }
    .stat {
      background: #f9fbfc;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
    }
    .stat b { display: block; font-size: 26px; color: var(--brand); line-height: 1.15; }
    .stat span { color: var(--muted); font-size: 13px; }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
      gap: 16px;
    }
    .asset {
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      background: #fbfcfd;
      display: flex;
      flex-direction: column;
      min-height: 100%;
    }
    .asset img {
      width: 100%;
      height: 260px;
      object-fit: contain;
      background: #fff;
      border-bottom: 1px solid var(--line);
    }
    .asset .body { padding: 12px; }
    .meta { color: var(--muted); font-size: 13px; word-break: break-all; }
    .card-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
    }
    .small-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 8px;
    }
    .small-card img {
      display: block;
      width: 100%;
      aspect-ratio: 4 / 5;
      object-fit: contain;
      background: #f8fafb;
      border-radius: 6px;
      border: 1px solid #edf1f4;
    }
    .small-card .name { margin-top: 7px; font-size: 13px; min-height: 34px; overflow-wrap: anywhere; }
    .table-scroll {
      width: 100%;
      max-width: 100%;
      overflow-x: auto;
      overscroll-behavior-inline: contain;
      -webkit-overflow-scrolling: touch;
    }
    .link-table { width: 100%; min-width: 680px; border-collapse: collapse; font-size: 14px; margin-bottom: 16px; }
    .link-table th, .link-table td {
      border: 1px solid var(--line);
      padding: 8px 9px;
      text-align: left;
      vertical-align: top;
    }
    .link-table code { overflow-wrap: anywhere; white-space: normal; }
    textarea {
      width: 100%;
      min-height: 230px;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      font: 14px/1.7 ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
      color: var(--ink);
      background: #fbfcfd;
    }
    details summary { cursor: pointer; font-weight: 700; }
    .toast {
      position: fixed;
      right: 18px;
      bottom: 18px;
      background: var(--deep);
      color: #fff;
      padding: 10px 12px;
      border-radius: 8px;
      opacity: 0;
      transform: translateY(8px);
      transition: opacity .18s ease, transform .18s ease;
      z-index: 20;
      max-width: min(420px, calc(100vw - 36px));
    }
    .toast.show { opacity: 1; transform: translateY(0); }
    @media (max-width: 640px) {
      h1 { font-size: 26px; }
      section { padding: 15px; }
      .asset img { height: 220px; }
      .link-table { font-size: 13px; }
    }
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <h1>__BRAND__ 发帖资产面板</h1>
      <p>__UPDATE_LABEL__更新，快照日期：__RUN_DATE__。本文件为自包含 HTML，图片已经内嵌，可离线打开。</p>
      <div class="toolbar">
        <button class="primary" id="posterBtn">生成总览海报 PNG</button>
        <button class="secondary" id="copyPostBtn">复制发帖文案</button>
        <button data-scroll="main-assets">查看主图</button>
        <button data-scroll="asset-links">查看资产链接</button>
      </div>
    </div>
  </header>

  <main>
    <section>
      <h2>本轮资产规模</h2>
      <div class="notice">这些图用于发帖和内部说明。它们展示研究活跃度、证据分布和撤稿风险，不构成个人医疗建议、用药建议、剂量建议、医美操作建议或购买建议。</div>
      <div id="stats" class="stats"></div>
    </section>

    <section id="main-assets">
      <h2>主图资产</h2>
      <div id="mainGrid" class="grid"></div>
    </section>

    <section>
      <details>
        <summary>展开 50 张单成分卡</summary>
        <p class="meta">每张卡都可单独下载 PNG；如果只需要发一张总览，优先使用“成分卡片墙”。</p>
        <div id="cardGrid" class="card-grid"></div>
      </details>
    </section>

    <section id="asset-links">
      <h2>GitHub 与表格资产链接</h2>
      <h3>GitHub 公开入口</h3>
      <div class="table-scroll"><table class="link-table" id="githubLinks"></table></div>
      <h3>飞书在线多维表格</h3>
      <div class="table-scroll"><table class="link-table" id="feishuLinks"></table></div>
      <h3>本地公开 CSV 表格</h3>
      <div class="table-scroll"><table class="link-table" id="tableLinks"></table></div>
      <h3>本地报告与飞书包</h3>
      <div class="table-scroll"><table class="link-table" id="reportLinks"></table></div>
    </section>

    <section>
      <h2>发帖文案</h2>
      <textarea id="postText"></textarea>
      <div class="toolbar">
        <button class="secondary" id="copyPostBtn2">复制文案</button>
        <button id="downloadTextBtn">下载文案 TXT</button>
      </div>
    </section>
  </main>

  <div id="toast" class="toast"></div>

  <script>
    const MAIN_ASSETS = __MAIN_ASSETS__;
    const CARD_ASSETS = __CARD_ASSETS__;
    const GITHUB_LINKS = __GITHUB_LINKS__;
    const TABLE_LINKS = __TABLE_LINKS__;
    const REPORT_LINKS = __REPORT_LINKS__;
    const FEISHU_LINKS = __FEISHU_LINKS__;
    const STATS = __STATS__;
    const POST_COPY = __POST_COPY__;

    function formatBytes(bytes) {
      const units = ["B", "KB", "MB"];
      let value = Number(bytes || 0);
      let index = 0;
      while (value >= 1024 && index < units.length - 1) {
        value /= 1024;
        index += 1;
      }
      return `${value.toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
    }

    function showToast(text) {
      const el = document.getElementById("toast");
      el.textContent = text;
      el.classList.add("show");
      window.setTimeout(() => el.classList.remove("show"), 1800);
    }

    async function copyText(text, label = "已复制") {
      try {
        await navigator.clipboard.writeText(text);
      } catch (err) {
        const ta = document.createElement("textarea");
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        ta.remove();
      }
      showToast(label);
    }

    function downloadDataUrl(dataUrl, filename) {
      const link = document.createElement("a");
      link.href = dataUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
    }

    function renderStats() {
      document.getElementById("stats").innerHTML = STATS.map(item => `
        <div class="stat"><b>${item.value}</b><span>${item.label}</span></div>
      `).join("");
    }

    function renderMainAssets() {
      const grid = document.getElementById("mainGrid");
      grid.innerHTML = MAIN_ASSETS.map(asset => `
        <article class="asset">
          <img src="${asset.dataUrl}" alt="${asset.title}">
          <div class="body">
            <h3>${asset.title}</h3>
            <p class="meta">${asset.filename} · ${asset.width}×${asset.height} · ${formatBytes(asset.size)}</p>
            <div class="toolbar">
              <button class="primary" data-download-main="${asset.id}">下载原图</button>
              <button data-copy-main="${asset.id}">复制路径</button>
              <button data-open-main="${asset.id}">新页打开</button>
            </div>
          </div>
        </article>
      `).join("");
    }

    function renderCards() {
      const grid = document.getElementById("cardGrid");
      grid.innerHTML = CARD_ASSETS.map(asset => `
        <div class="small-card">
          <img src="${asset.dataUrl}" alt="${asset.title}">
          <div class="name">${asset.title}</div>
          <div class="toolbar"><button data-download-card="${asset.id}">下载</button></div>
        </div>
      `).join("");
    }

    function renderLinkTable(id, rows) {
      const table = document.getElementById(id);
      const body = rows.map((row, index) => {
        const value = Array.isArray(row) ? row[1] : row.value;
        const label = Array.isArray(row) ? row[0] : row.label;
        const note = Array.isArray(row) ? "GitHub" : (row.note || "");
        const valueCell = /^https?:\/\//.test(value)
          ? `<a href="${value}" target="_blank" rel="noopener">${value}</a>`
          : `<code>${value}</code>`;
        return `<tr><td>${label}</td><td>${valueCell}</td><td>${note}</td><td><button data-copy-table="${id}:${index}">复制</button></td></tr>`;
      }).join("");
      table.innerHTML = `<thead><tr><th>资产</th><th>链接/路径</th><th>备注</th><th>操作</th></tr></thead><tbody>${body || "<tr><td colspan='4'>暂无链接，完成飞书同步后重新生成本页。</td></tr>"}</tbody>`;
    }

    function openImage(asset) {
      const win = window.open("", "_blank");
      if (!win) return;
      win.document.write(`<title>${asset.title}</title><body style="margin:0;background:#111;display:grid;place-items:center;min-height:100vh"><img src="${asset.dataUrl}" style="max-width:100%;height:auto;background:white"></body>`);
      win.document.close();
    }

    function loadImage(src) {
      return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = reject;
        img.src = src;
      });
    }

    function drawFitted(ctx, img, x, y, w, h) {
      const scale = Math.min(w / img.width, h / img.height);
      const nw = img.width * scale;
      const nh = img.height * scale;
      const ox = x + (w - nw) / 2;
      const oy = y + (h - nh) / 2;
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(x, y, w, h);
      ctx.drawImage(img, ox, oy, nw, nh);
      ctx.strokeStyle = "#d9e1ea";
      ctx.lineWidth = 2;
      ctx.strokeRect(x, y, w, h);
    }

    async function generatePoster() {
      const canvas = document.createElement("canvas");
      canvas.width = 1400;
      canvas.height = 1900;
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = "#f4f7f8";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "#14232f";
      ctx.fillRect(0, 0, canvas.width, 250);
      ctx.fillStyle = "#ffffff";
      ctx.font = "700 58px Microsoft YaHei, Arial";
      ctx.fillText("宇多Yul细胞/yulcell", 70, 92);
      ctx.font = "500 38px Microsoft YaHei, Arial";
      ctx.fillText("__UPDATE_LABEL__抗衰证据图谱更新", 70, 154);
      const newCandidates = STATS.find(item => item.label === "本轮 PubMed 新候选");
      const recentRetained = STATS.find(item => item.label === "近期候选最终保留");
      ctx.font = "24px Microsoft YaHei, Arial";
      ctx.fillText(`当前：候选文献 ${STATS[0].value} · findings ${STATS[1].value} · matrix ${STATS[2].value} · 成分卡 50`, 70, 194);
      if (newCandidates && recentRetained) {
        ctx.fillText(`本轮检索：新候选 ${newCandidates.value} · 近期最终保留 ${recentRetained.value} · 主动清理重复与弱相关记录`, 70, 226);
      }

      let sx = 70;
      for (const item of STATS.slice(0, 4)) {
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(sx, 285, 285, 118);
        ctx.strokeStyle = "#d9e1ea";
        ctx.strokeRect(sx, 285, 285, 118);
        ctx.fillStyle = "#176b4b";
        ctx.font = "700 42px Arial";
        ctx.fillText(item.value, sx + 24, 344);
        ctx.fillStyle = "#637083";
        ctx.font = "24px Microsoft YaHei, Arial";
        ctx.fillText(item.label, sx + 24, 380);
        sx += 315;
      }

      const picks = ["heatmap-topic-year", "heatmap-topic-evidence", "ingredient-card-wall", "evidence-yield-ingredients"];
      const imgs = await Promise.all(picks.map(id => loadImage(MAIN_ASSETS.find(a => a.id === id).dataUrl)));
      const boxes = [[70, 450, 610, 560], [720, 450, 610, 560], [70, 1060, 610, 560], [720, 1060, 610, 560]];
      imgs.forEach((img, index) => drawFitted(ctx, img, ...boxes[index]));

      ctx.fillStyle = "#202833";
      ctx.font = "26px Microsoft YaHei, Arial";
      ctx.fillText("说明：图片展示研究活跃度、证据分布与风险提示，不是个人医疗建议。", 70, 1706);
      ctx.fillStyle = "#637083";
      ctx.font = "22px Microsoft YaHei, Arial";
      ctx.fillText("GitHub: github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn", 70, 1750);
      ctx.fillText("生成日期：__RUN_DATE__", 70, 1786);
      downloadDataUrl(canvas.toDataURL("image/png"), "yulcell-__RUN_DATE__-posting-overview.png");
    }

    function downloadText() {
      const blob = new Blob([POST_COPY], { type: "text/plain;charset=utf-8" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "yulcell-__RUN_DATE__-post-copy.txt";
      document.body.appendChild(link);
      link.click();
      URL.revokeObjectURL(link.href);
      link.remove();
    }

    const tableSets = { githubLinks: GITHUB_LINKS, feishuLinks: FEISHU_LINKS, tableLinks: TABLE_LINKS, reportLinks: REPORT_LINKS };
    document.addEventListener("click", event => {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      const mainDownload = target.getAttribute("data-download-main");
      const mainCopy = target.getAttribute("data-copy-main");
      const mainOpen = target.getAttribute("data-open-main");
      const cardDownload = target.getAttribute("data-download-card");
      const copyTable = target.getAttribute("data-copy-table");
      const scrollId = target.getAttribute("data-scroll");
      if (mainDownload) {
        const asset = MAIN_ASSETS.find(item => item.id === mainDownload);
        if (asset) downloadDataUrl(asset.dataUrl, asset.filename);
      }
      if (mainCopy) {
        const asset = MAIN_ASSETS.find(item => item.id === mainCopy);
        if (asset) copyText(asset.localPath, "路径已复制");
      }
      if (mainOpen) {
        const asset = MAIN_ASSETS.find(item => item.id === mainOpen);
        if (asset) openImage(asset);
      }
      if (cardDownload) {
        const asset = CARD_ASSETS.find(item => item.id === cardDownload);
        if (asset) downloadDataUrl(asset.dataUrl, asset.filename);
      }
      if (copyTable) {
        const [tableId, rawIndex] = copyTable.split(":");
        const row = tableSets[tableId][Number(rawIndex)];
        const value = Array.isArray(row) ? row[1] : row.value;
        copyText(value, "已复制");
      }
      if (scrollId) document.getElementById(scrollId).scrollIntoView({ behavior: "smooth", block: "start" });
    });

    document.getElementById("posterBtn").addEventListener("click", generatePoster);
    document.getElementById("copyPostBtn").addEventListener("click", () => copyText(POST_COPY, "发帖文案已复制"));
    document.getElementById("copyPostBtn2").addEventListener("click", () => copyText(POST_COPY, "发帖文案已复制"));
    document.getElementById("downloadTextBtn").addEventListener("click", downloadText);
    document.getElementById("postText").value = POST_COPY;
    renderStats();
    renderMainAssets();
    renderCards();
    renderLinkTable("githubLinks", GITHUB_LINKS);
    renderLinkTable("feishuLinks", FEISHU_LINKS);
    renderLinkTable("tableLinks", TABLE_LINKS);
    renderLinkTable("reportLinks", REPORT_LINKS);
  </script>
</body>
</html>
"""


def build_html(main_assets: list[dict[str, object]], cards: list[dict[str, object]]) -> str:
    replacements = {
        "__BRAND__": BRAND,
        "__RUN_DATE__": RUN_DATE,
        "__UPDATE_LABEL__": UPDATE_LABEL,
        "__MAIN_ASSETS__": json.dumps(main_assets, ensure_ascii=False),
        "__CARD_ASSETS__": json.dumps(cards, ensure_ascii=False),
        "__GITHUB_LINKS__": json.dumps(GITHUB_LINKS, ensure_ascii=False),
        "__TABLE_LINKS__": json.dumps(public_tables(), ensure_ascii=False),
        "__REPORT_LINKS__": json.dumps([local_link(label, path) for label, path in REPORT_LINKS], ensure_ascii=False),
        "__FEISHU_LINKS__": json.dumps(feishu_links(), ensure_ascii=False),
        "__STATS__": json.dumps(stats(), ensure_ascii=False),
        "__POST_COPY__": json.dumps(post_copy(), ensure_ascii=False),
    }
    html = HTML_TEMPLATE
    for key, value in replacements.items():
        html = html.replace(key, value)
    return html


def main() -> None:
    main_assets = [image_record(*item) for item in MAIN_IMAGES]
    cards = card_assets()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build_html(main_assets, cards), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"Embedded main images: {len(main_assets)}")
    print(f"Embedded ingredient cards: {len(cards)}")
    print(f"Embedded Feishu links: {len(feishu_links())}")


if __name__ == "__main__":
    main()
