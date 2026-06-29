"""Build retraction-density and evidence-yield assets.

The new public-facing metric layer has two parts:
- Retraction density: retractions per 1000 PubMed publications.
- Evidence yield: a topic-level proxy for whether publication volume turns into
  A/B-level evidence surfaces.

The evidence-yield metric is intentionally conservative. For ingredient cards,
we only have topic-level evidence grades for health and skin/beauty surfaces,
not a fully adjudicated count of high-quality articles. Therefore the output
labels it as a "topic-level proxy" and avoids claiming exact counts of good
papers.
"""

from __future__ import annotations

import csv
import math
import os
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "build" / "visual-assets"
UPDATE_MONTH = os.environ.get("EVIDENCE_ATLAS_ASSET_MONTH", "2026-05")
UPDATE_MONTH_UNDERSCORE = UPDATE_MONTH.replace("-", "_")
RUN_DATE = os.environ.get("EVIDENCE_ATLAS_UPDATE_DATE", "2026-05-19")
REPORT = ROOT / "build" / "private-content" / f"evidence-yield-retraction-report-{RUN_DATE}.html"

FONT_CANDIDATES = [
    Path(r"C:\Windows\Fonts\msyh.ttc"),
    Path(r"C:\Windows\Fonts\simhei.ttf"),
    Path(r"C:\Windows\Fonts\Deng.ttf"),
]
FONT_BOLD_CANDIDATES = [
    Path(r"C:\Windows\Fonts\msyhbd.ttc"),
    Path(r"C:\Windows\Fonts\simhei.ttf"),
    Path(r"C:\Windows\Fonts\msyh.ttc"),
]

INK = (31, 36, 44)
MUTED = (92, 102, 116)
LINE = (218, 224, 232)
PAPER = (250, 250, 248)
WHITE = (255, 255, 255)
TEAL = (23, 107, 124)
RED = (166, 69, 69)
AMBER = (151, 111, 31)
GREEN = (23, 114, 69)

GRADE_RANK = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}
GRADE_POINTS = {"A": 5, "B": 4, "C": 2, "D": 1, "E": 0}


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for path in (FONT_BOLD_CANDIDATES if bold else FONT_CANDIDATES):
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def grade(value: str) -> str:
    value = (value or "").strip().upper()
    return value[0] if value and value[0] in GRADE_RANK else "D"


def grade_label(value: str) -> str:
    return grade(value)


def best_grade(health: str, skin: str) -> str:
    grades = [grade(health), grade(skin)]
    return sorted(grades, key=lambda item: GRADE_RANK[item])[0]


def ab_surface_count(health: str, skin: str) -> int:
    return sum(1 for item in [grade(health), grade(skin)] if item in {"A", "B"})


def evidence_yield_label(total: int, ab_count: int, risk: str) -> str:
    if total >= 1000 and ab_count == 0:
        return "高发表低证据：容易凑热闹"
    if total >= 1000 and ab_count == 1:
        return "热度部分转化：要分场景"
    if total >= 1000 and ab_count == 2:
        return "研究多且证据面较强"
    if total < 1000 and ab_count >= 1:
        return "小分母但有较强信号"
    if risk == "高":
        return "小分母/早期且宣传风险高"
    return "小分母早期线索"


def evidence_yield_score(total: int, health: str, skin: str) -> float:
    """A compact 0-100 proxy: grade strength adjusted by publication volume.

    The log denominator prevents huge fields from winning just because there
    are many papers, while not over-rewarding very small fields.
    """

    points = max(GRADE_POINTS[grade(health)], GRADE_POINTS[grade(skin)])
    if total <= 0:
        return 0.0
    return round(min(100.0, points * 20 / max(1.0, math.log10(total + 10) / 2)), 1)


def build_metrics() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, str]]]:
    cards = read_csv(DATA / "social_cards_top50_ingredients.csv")
    retractions = read_csv(DATA / "retraction_risk_summary_20y.csv")
    by_target = {row.get("target_id", ""): row for row in retractions}
    by_name = {row.get("name_zh", ""): row for row in retractions}

    ingredient_rows: list[dict[str, Any]] = []
    for row in cards:
        target_id = row.get("source_id") or ""
        ret = by_name.get(row["name_zh"], {})
        total = int(float(row.get("retraction_publications_20y") or ret.get("pubmed_total_count_20y") or 0))
        retracted = int(float(row.get("retraction_count_20y") or ret.get("pubmed_retracted_count_20y") or 0))
        per_1000 = float(row.get("retractions_per_1000_publications") or ret.get("retractions_per_1000_publications") or 0)
        health = row.get("health_evidence", "")
        skin = row.get("skin_evidence", "")
        ab_count = ab_surface_count(health, skin)
        pubs_per_ab = round(total / ab_count, 1) if ab_count else ""
        risk = row.get("commercial_overclaim_risk", "")
        label = evidence_yield_label(total, ab_count, risk)
        ingredient_rows.append(
            {
                "target_id": row["card_id"],
                "update_month": UPDATE_MONTH,
                "name_zh": row["name_zh"],
                "name_en": row.get("name_en", ""),
                "category": row.get("category", ""),
                "pubmed_total_count_20y": total,
                "pubmed_retracted_count_20y": retracted,
                "retractions_per_1000_publications": round(per_1000, 2),
                "health_evidence": health,
                "skin_evidence": skin,
                "best_evidence_grade": best_grade(health, skin),
                "ab_evidence_surface_count": ab_count,
                "ab_evidence_surface_share_percent": round(ab_count / 2 * 100, 1),
                "publications_per_ab_surface_proxy": pubs_per_ab,
                "evidence_yield_score_0_100": evidence_yield_score(total, health, skin),
                "evidence_yield_label": label,
                "commercial_overclaim_risk": risk,
                "reader_note": f"20年发表 {total} 篇；A/B 证据面 {ab_count}/2；每1000篇撤稿 {per_1000:.2f}。这是主题级代理，不是单篇高质量研究计数。",
                "last_checked": RUN_DATE,
            }
        )

    topic_rows = []
    for row in read_csv(DATA / "research_heatmap_topic_evidence.csv"):
        total = int(row.get("total") or 0)
        a = int(row.get("A") or 0)
        b = int(row.get("B") or 0)
        ab = a + b
        a_share = round(a / total * 100, 1) if total else 0
        ab_share = round(ab / total * 100, 1) if total else 0
        label = "A 级集中" if a_share >= 60 else ("A/B 混合" if a_share > 0 else "主要 B 级或待复核")
        topic_rows.append(
            {
                "topic_id": row["topic"],
                "update_month": UPDATE_MONTH,
                "topic": row["topic"],
                "total_evidence_items": total,
                "a_count": a,
                "b_count": b,
                "ab_count": ab,
                "a_share_percent": a_share,
                "ab_share_percent": ab_share,
                "items_per_a_evidence_proxy": round(total / a, 1) if a else "",
                "evidence_yield_label": label,
                "reader_note": "按本库证据等级表统计；用于展示高等级证据分布，不等同于全 PubMed 分母。",
                "last_checked": RUN_DATE,
            }
        )

    return ingredient_rows, topic_rows, retractions


def bar_color(value: float, high: float) -> tuple[int, int, int]:
    if high <= 0:
        return (220, 226, 232)
    t = min(1.0, value / high)
    low = (231, 242, 244)
    high_c = (23, 107, 124)
    return tuple(int(low[i] + (high_c[i] - low[i]) * math.sqrt(t)) for i in range(3))


def draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.ImageFont, width: int, fill=INK, max_lines: int = 2) -> None:
    x, y = xy
    lines = []
    current = ""
    for ch in text:
        if current and text_width(draw, current + ch, font) > width:
            lines.append(current)
            current = ch
            if len(lines) >= max_lines:
                break
        else:
            current += ch
    if current and len(lines) < max_lines:
        lines.append(current)
    for idx, line in enumerate(lines[:max_lines]):
        draw.text((x, y + idx * (font.size + 5)), line, font=font, fill=fill)


def draw_retraction_density(retractions: list[dict[str, str]]) -> Path:
    rows = sorted(
        retractions,
        key=lambda row: float(row.get("retractions_per_1000_publications") or 0),
        reverse=True,
    )[:20]
    width = 1500
    row_h = 54
    top = 170
    height = top + row_h * len(rows) + 120
    img = Image.new("RGB", (width, height), PAPER)
    draw = ImageDraw.Draw(img)
    title = load_font(46, True)
    sub = load_font(25)
    label = load_font(23)
    value_font = load_font(24, True)
    draw.text((56, 42), "撤稿密度图：每 1000 篇发表里有多少撤稿", font=title, fill=INK)
    draw.text((56, 104), "撤稿数必须看分母。小分母高密度，比单纯撤稿数量更值得前置提醒。", font=sub, fill=MUTED)
    max_value = max(float(row.get("retractions_per_1000_publications") or 0) for row in rows)
    bar_x = 420
    bar_w = 780
    for idx, row in enumerate(rows):
        y = top + idx * row_h
        name = row.get("name_zh", "")
        draw_wrapped(draw, (56, y + 7), name, label, 310)
        value = float(row.get("retractions_per_1000_publications") or 0)
        length = int(bar_w * value / max_value) if max_value else 0
        color = RED if "PDRN" in name or value >= 20 else bar_color(value, max_value)
        draw.rounded_rectangle((bar_x, y + 9, bar_x + length, y + 39), radius=8, fill=color)
        draw.rectangle((bar_x, y + 9, bar_x + bar_w, y + 39), outline=LINE, width=1)
        draw.text((bar_x + bar_w + 24, y + 7), f"{value:.2f}/千篇", font=value_font, fill=RED if value >= 20 else INK)
        draw.text((bar_x + bar_w + 180, y + 7), f"发表 {row.get('pubmed_total_count_20y')} | 撤稿 {row.get('pubmed_retracted_count_20y')}", font=label, fill=MUTED)
    draw.text((56, height - 62), "口径：PubMed 近 20 年；分子为 Retracted Publication；分母为同一检索语境下总发表量。", font=sub, fill=MUTED)
    path = OUT / f"retraction-density-{UPDATE_MONTH}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, optimize=True, quality=95)
    return path


def draw_evidence_yield_ingredients(rows: list[dict[str, Any]]) -> Path:
    selected = sorted(
        rows,
        key=lambda row: (
            -int(row["pubmed_total_count_20y"]),
            int(row["ab_evidence_surface_count"]),
            row["evidence_yield_score_0_100"],
        ),
    )[:24]
    width = 1580
    row_h = 58
    top = 185
    height = top + row_h * len(selected) + 120
    img = Image.new("RGB", (width, height), PAPER)
    draw = ImageDraw.Draw(img)
    title = load_font(46, True)
    sub = load_font(25)
    label = load_font(23)
    value = load_font(24, True)
    draw.text((56, 42), "证据含金量图：不是论文越多越靠谱", font=title, fill=INK)
    draw.text((56, 104), "看 20 年发表量、A/B 证据面和撤稿密度。高发表但 A/B 证据面少，就更像“热闹但不扎实”。", font=sub, fill=MUTED)
    headers = [("成分", 56), ("20年发表", 390), ("A/B证据面", 560), ("撤稿/千篇", 730), ("证据含金量", 900), ("判断", 1190)]
    for text, x in headers:
        draw.text((x, top - 44), text, font=value, fill=INK)
    for idx, row in enumerate(selected):
        y = top + idx * row_h
        draw.line((56, y - 8, width - 56, y - 8), fill=LINE, width=1)
        draw_wrapped(draw, (56, y), str(row["name_zh"]), label, 300, max_lines=1)
        draw.text((390, y), f"{int(row['pubmed_total_count_20y']):,}", font=value, fill=INK)
        ab = int(row["ab_evidence_surface_count"])
        ab_color = GREEN if ab == 2 else (TEAL if ab == 1 else RED)
        draw.rounded_rectangle((560, y - 2, 660, y + 34), radius=8, fill=(236, 245, 246), outline=LINE)
        draw.text((584, y), f"{ab}/2", font=value, fill=ab_color)
        retract = float(row["retractions_per_1000_publications"])
        draw.text((730, y), f"{retract:.2f}", font=value, fill=RED if retract >= 8 else INK)
        score = float(row["evidence_yield_score_0_100"])
        score_w = int(150 * score / 100)
        draw.rectangle((900, y + 8, 1050, y + 26), fill=(232, 238, 242))
        draw.rectangle((900, y + 8, 900 + score_w, y + 26), fill=bar_color(score, 100))
        draw.text((1068, y - 1), f"{score:.1f}", font=label, fill=MUTED)
        draw_wrapped(draw, (1190, y), str(row["evidence_yield_label"]), label, 310, max_lines=1)
    draw.text((56, height - 62), "说明：A/B证据面是健康寿命与皮肤美容两个场景的主题级代理；不是单篇高质量研究精确计数。", font=sub, fill=MUTED)
    path = OUT / f"evidence-yield-ingredients-{UPDATE_MONTH}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, optimize=True, quality=95)
    return path


def draw_topic_yield(rows: list[dict[str, Any]]) -> Path:
    rows = sorted(rows, key=lambda row: float(row["a_share_percent"]), reverse=True)
    width = 1460
    row_h = 62
    top = 178
    height = top + row_h * len(rows) + 110
    img = Image.new("RGB", (width, height), PAPER)
    draw = ImageDraw.Draw(img)
    title = load_font(46, True)
    sub = load_font(25)
    label = load_font(23)
    value = load_font(24, True)
    draw.text((56, 42), "主题证据产出率：A 级证据占比", font=title, fill=INK)
    draw.text((56, 104), "同样是 A/B 级证据，A 级占比越高，越接近高质量人体/系统评价证据。", font=sub, fill=MUTED)
    for idx, row in enumerate(rows):
        y = top + idx * row_h
        draw.line((56, y - 8, width - 56, y - 8), fill=LINE, width=1)
        draw_wrapped(draw, (56, y), row["topic"], label, 390, max_lines=1)
        total = int(row["total_evidence_items"])
        a_share = float(row["a_share_percent"])
        bar_x = 500
        bar_w = 520
        draw.rectangle((bar_x, y + 9, bar_x + bar_w, y + 33), fill=(232, 238, 242))
        draw.rectangle((bar_x, y + 9, bar_x + int(bar_w * a_share / 100), y + 33), fill=bar_color(a_share, 100))
        draw.text((bar_x + bar_w + 24, y - 1), f"A {row['a_count']} / 总 {total}", font=value, fill=INK)
        draw.text((bar_x + bar_w + 220, y - 1), f"A占比 {a_share:.1f}%", font=value, fill=TEAL if a_share >= 50 else AMBER)
        draw.text((bar_x + bar_w + 390, y - 1), row["evidence_yield_label"], font=label, fill=MUTED)
    draw.text((56, height - 58), "说明：本图用本库证据等级表，不等同于全 PubMed 分母。", font=sub, fill=MUTED)
    path = OUT / f"topic-evidence-yield-{UPDATE_MONTH}.png"
    img.save(path, optimize=True, quality=95)
    return path


def update_heatmap_manifest(paths: dict[str, Path]) -> None:
    manifest_path = DATA / f"visual_heatmap_assets_{UPDATE_MONTH_UNDERSCORE}.csv"
    existing = read_csv(manifest_path)
    by_id = {row["asset_id"]: row for row in existing}
    new_rows = {
        "H004": {
            "asset_id": "H004",
            "update_month": UPDATE_MONTH,
            "title": "撤稿密度图：每1000篇发表撤稿数",
            "asset_type": "heatmap_png",
            "description": "按每1000篇发表撤稿数展示撤稿密度，强调要看分母。",
            "data_source": "data/retraction_risk_summary_20y.csv",
            "local_path": str(paths["retraction"].relative_to(ROOT)).replace("\\", "/"),
        },
        "H005": {
            "asset_id": "H005",
            "update_month": UPDATE_MONTH,
            "title": "成分证据含金量图",
            "asset_type": "heatmap_png",
            "description": "把20年发表量、A/B证据面、撤稿密度放在一起，识别高发表低证据主题。",
            "data_source": f"data/evidence_yield_metrics_{UPDATE_MONTH_UNDERSCORE}.csv",
            "local_path": str(paths["ingredient"].relative_to(ROOT)).replace("\\", "/"),
        },
        "H006": {
            "asset_id": "H006",
            "update_month": UPDATE_MONTH,
            "title": "主题证据产出率图",
            "asset_type": "heatmap_png",
            "description": "按A等级占比展示主题证据产出率。",
            "data_source": f"data/topic_evidence_yield_metrics_{UPDATE_MONTH_UNDERSCORE}.csv",
            "local_path": str(paths["topic"].relative_to(ROOT)).replace("\\", "/"),
        },
    }
    by_id.update(new_rows)
    rows = list(by_id.values())
    rows.sort(key=lambda row: row["asset_id"])
    write_csv(
        manifest_path,
        rows,
        ["asset_id", "update_month", "title", "asset_type", "description", "data_source", "local_path"],
    )


def render_report(ingredient_rows: list[dict[str, Any]], topic_rows: list[dict[str, Any]], retractions: list[dict[str, str]]) -> None:
    top_retract = sorted(retractions, key=lambda row: float(row.get("retractions_per_1000_publications") or 0), reverse=True)[:10]
    high_noise = [row for row in ingredient_rows if "高发表低证据" in row["evidence_yield_label"]][:12]
    links_path = DATA / f"evidence_yield_feishu_links_{UPDATE_MONTH_UNDERSCORE}.csv"
    links = read_csv(links_path) if links_path.exists() else []

    def row_table(headers: list[str], rows: list[list[Any]]) -> str:
        th = "".join(f"<th>{h}</th>" for h in headers)
        body = "\n".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
        return f"<table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>"

    link_rows = [
        [row["asset_group"], f'<a href="{row["url"]}" target="_blank">{row["table_id"]}</a>', row.get("status", "active")]
        for row in links
    ]
    retract_rows = [
        [row["name_zh"], row["pubmed_total_count_20y"], row["pubmed_retracted_count_20y"], row["retractions_per_1000_publications"], row["normalized_risk_bucket"]]
        for row in top_retract
    ]
    noise_rows = [
        [row["name_zh"], row["pubmed_total_count_20y"], row["health_evidence"], row["skin_evidence"], row["evidence_yield_label"]]
        for row in high_noise
    ]
    css = """
    body{margin:0;background:#fafaf8;color:#1f242c;font-family:"Microsoft YaHei","Segoe UI",Arial,sans-serif;line-height:1.65}
    main{max-width:1160px;margin:0 auto;padding:42px 28px 78px}h1{font-size:34px;margin:0 0 8px}h2{font-size:24px;margin:36px 0 14px;border-left:7px solid #176b7c;padding-left:12px}
    .muted{color:#5d6877}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.card{background:white;border:1px solid #d9e1e8;border-radius:10px;padding:16px}.card b{display:block;color:#176b7c;font-size:26px}
    table{width:100%;border-collapse:collapse;background:white;border:1px solid #d9e1e8;border-radius:10px;overflow:hidden;margin:12px 0 24px}th,td{border-bottom:1px solid #d9e1e8;padding:10px 12px;text-align:left;vertical-align:top}th{background:#edf5f6}tr:last-child td{border-bottom:none}
    img{max-width:100%;border:1px solid #d9e1e8;border-radius:10px;background:white}.two{display:grid;grid-template-columns:1fr 1fr;gap:18px}a{color:#145f70}@media(max-width:900px){.grid,.two{grid-template-columns:1fr}main{padding:28px 16px 60px}}
    """
    html = f"""<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>撤稿密度与证据含金量更新报告</title><style>{css}</style></head>
<body><main>
<h1>撤稿密度与证据含金量更新报告</h1>
<p class="muted">生成日期：{RUN_DATE}。用途：内部视频准备与公开资产说明。</p>
<div class="grid">
  <div class="card"><b>{len(ingredient_rows)}</b>个成分纳入证据含金量指标</div>
  <div class="card"><b>{len(retractions)}</b>个主题有撤稿密度记录</div>
  <div class="card"><b>{len(topic_rows)}</b>个抗衰主题有A/B证据产出率</div>
</div>
<h2>一、这次新增的两个指标</h2>
<p><b>撤稿密度</b>：每1000篇发表里有多少篇撤稿。它解决的是“不能只看撤稿数量，必须看分母”。</p>
<p><b>证据含金量/证据产出率</b>：把20年发表量、A/B证据面和证据等级放在一起。它解决的是“论文很多，不等于好证据多”。</p>
<p class="muted">注意：成分层面的 A/B 证据面是主题级代理，不是单篇高质量论文精确计数。</p>
<h2>二、已生成并同步的资产</h2>
{row_table(["资产表", "飞书链接", "状态"], link_rows)}
<h2>三、可以直接展示的图</h2>
<div class="two">
  <div><h3>撤稿密度图</h3><img src="../visual-assets/retraction-density-{UPDATE_MONTH}.png" alt="撤稿密度图"></div>
  <div><h3>证据含金量图</h3><img src="../visual-assets/evidence-yield-ingredients-{UPDATE_MONTH}.png" alt="证据含金量图"></div>
</div>
<h2>四、撤稿密度最高的主题</h2>
{row_table(["主题", "20年发表量", "撤稿数", "每1000篇撤稿", "风险"], retract_rows)}
<h2>五、高发表低证据的典型成分</h2>
{row_table(["成分", "20年发表量", "健康证据", "皮肤证据", "判断"], noise_rows)}
<h2>六、视频口播建议</h2>
<p>这次可以讲一句更有冲击力的话：<b>“抗衰不是看论文数量，论文越多，有时只是越热闹；要看这些论文有没有转化成 A/B 级证据，还要看撤稿密度。”</b></p>
<p>讲 PDRN 时用撤稿密度；讲益生菌、锌、辅酶Q10、姜黄素这类成分时，用证据含金量，提醒观众不要把研究热度当成购买理由。</p>
<h2>七、文件</h2>
<p>CSV：data/evidence_yield_metrics_{UPDATE_MONTH_UNDERSCORE}.csv；data/topic_evidence_yield_metrics_{UPDATE_MONTH_UNDERSCORE}.csv；data/retraction_risk_summary_20y.csv。</p>
<p>图片：build/visual-assets/retraction-density-{UPDATE_MONTH}.png；build/visual-assets/evidence-yield-ingredients-{UPDATE_MONTH}.png；build/visual-assets/topic-evidence-yield-{UPDATE_MONTH}.png。</p>
</main></body></html>"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(html, encoding="utf-8")


def main() -> None:
    ingredient_rows, topic_rows, retractions = build_metrics()
    write_csv(
        DATA / f"evidence_yield_metrics_{UPDATE_MONTH_UNDERSCORE}.csv",
        ingredient_rows,
        [
            "target_id",
            "update_month",
            "name_zh",
            "name_en",
            "category",
            "pubmed_total_count_20y",
            "pubmed_retracted_count_20y",
            "retractions_per_1000_publications",
            "health_evidence",
            "skin_evidence",
            "best_evidence_grade",
            "ab_evidence_surface_count",
            "ab_evidence_surface_share_percent",
            "publications_per_ab_surface_proxy",
            "evidence_yield_score_0_100",
            "evidence_yield_label",
            "commercial_overclaim_risk",
            "reader_note",
            "last_checked",
        ],
    )
    write_csv(
        DATA / f"topic_evidence_yield_metrics_{UPDATE_MONTH_UNDERSCORE}.csv",
        topic_rows,
        [
            "topic_id",
            "update_month",
            "topic",
            "total_evidence_items",
            "a_count",
            "b_count",
            "ab_count",
            "a_share_percent",
            "ab_share_percent",
            "items_per_a_evidence_proxy",
            "evidence_yield_label",
            "reader_note",
            "last_checked",
        ],
    )
    paths = {
        "retraction": draw_retraction_density(retractions),
        "ingredient": draw_evidence_yield_ingredients(ingredient_rows),
        "topic": draw_topic_yield(topic_rows),
    }
    update_heatmap_manifest(paths)
    render_report(ingredient_rows, topic_rows, retractions)
    print(DATA / f"evidence_yield_metrics_{UPDATE_MONTH_UNDERSCORE}.csv")
    print(DATA / f"topic_evidence_yield_metrics_{UPDATE_MONTH_UNDERSCORE}.csv")
    print(REPORT)


if __name__ == "__main__":
    main()
