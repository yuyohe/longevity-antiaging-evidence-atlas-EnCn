"""Build visual Feishu assets for the May 2026 public reader layer.

Outputs:
- PNG heatmaps for topic/year and topic/evidence matrices.
- 50 PNG ingredient cards plus one overview wall.
- CSV manifests used by the Feishu visual sync script.
"""

from __future__ import annotations

import csv
import math
import os
import re
import shutil
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "build" / "visual-assets"
CARD_DIR = OUT_DIR / "ingredient-cards"
DATA_DIR = ROOT / "data"
UPDATE_MONTH = os.environ.get("EVIDENCE_ATLAS_ASSET_MONTH", "2026-05")
UPDATE_MONTH_UNDERSCORE = UPDATE_MONTH.replace("-", "_")
PUBLIC_DIR = ROOT / "docs" / "assets" / "visual-assets" / UPDATE_MONTH
PUBLIC_CARD_DIR = PUBLIC_DIR / "ingredient-cards"

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

CATEGORY_PALETTE = {
    "vitamin": ((44, 123, 182), (230, 241, 248)),
    "mineral": ((79, 93, 117), (234, 238, 244)),
    "protein": ((90, 111, 80), (238, 244, 234)),
    "fatty_acid": ((32, 121, 128), (228, 243, 244)),
    "sports_nutrition": ((127, 82, 60), (246, 237, 231)),
    "polyphenol": ((117, 87, 144), (241, 235, 246)),
    "amino_acid": ((98, 97, 45), (245, 244, 229)),
    "skin": ((160, 78, 93), (249, 235, 238)),
    "other": ((80, 92, 102), (238, 241, 244)),
}

GRADE_COLORS = {
    "A": ((23, 114, 69), (226, 243, 234)),
    "B": ((33, 105, 173), (228, 239, 250)),
    "C": ((151, 111, 31), (250, 242, 222)),
    "D": ((96, 105, 116), (238, 241, 244)),
    "E": ((166, 69, 69), (249, 232, 232)),
}


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = FONT_BOLD_CANDIDATES if bold else FONT_CANDIDATES
    for path in candidates:
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


def text_len(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
    max_lines: int | None = None,
) -> list[str]:
    text = " ".join((text or "").strip().split())
    if not text:
        return []
    lines: list[str] = []
    line = ""
    for ch in text:
        trial = f"{line}{ch}"
        if line and text_len(draw, trial, font) > max_width:
            lines.append(line.rstrip())
            line = ch.lstrip()
            if max_lines and len(lines) >= max_lines:
                break
        else:
            line = trial
    if line and (not max_lines or len(lines) < max_lines):
        lines.append(line.rstrip())

    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
    if max_lines and len(lines) == max_lines:
        remaining = text
        if "".join(lines) != remaining:
            last = lines[-1].rstrip()
            while last and text_len(draw, f"{last}...", font) > max_width:
                last = last[:-1]
            lines[-1] = f"{last}..."
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    max_width: int,
    line_gap: int = 8,
    max_lines: int | None = None,
) -> int:
    x, y = xy
    lines = wrap_text(draw, text, font, max_width, max_lines=max_lines)
    line_h = font.size + line_gap
    for i, line in enumerate(lines):
        draw.text((x, y + i * line_h), line, font=font, fill=fill)
    return y + len(lines) * line_h


def draw_round_rect(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    radius: int,
    fill: tuple[int, int, int],
    outline: tuple[int, int, int] | None = None,
    width: int = 1,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def evidence_grade(value: str) -> str:
    match = re.match(r"\s*([A-E])", value or "")
    return match.group(1) if match else "D"


def draw_chip(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    label: str,
    value: str,
    width: int,
    height: int,
) -> None:
    grade = evidence_grade(value)
    ink, bg = GRADE_COLORS.get(grade, GRADE_COLORS["D"])
    draw_round_rect(draw, (x, y, x + width, y + height), 18, bg, outline=(220, 226, 232))
    label_font = load_font(24)
    value_font = load_font(34, bold=True)
    draw.text((x + 22, y + 14), label, font=label_font, fill=MUTED)
    draw.text((x + 22, y + 48), value or "未分级", font=value_font, fill=ink)


def risk_color(risk: str) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    if risk == "高":
        return (159, 65, 65), (250, 232, 232)
    if risk == "中":
        return (151, 111, 31), (250, 242, 222)
    return (23, 114, 69), (226, 243, 234)


def safe_filename(value: str) -> str:
    value = re.sub(r"[\\/:*?\"<>|]+", "-", value)
    value = re.sub(r"\s+", "-", value.strip())
    return value[:80] or "card"


def category_style(category: str) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    return CATEGORY_PALETTE.get(category, CATEGORY_PALETTE["other"])


def draw_section(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    title: str,
    body: str,
    max_width: int,
    accent: tuple[int, int, int],
    max_lines: int,
) -> int:
    title_font = load_font(30, bold=True)
    body_font = load_font(31)
    draw.rectangle((x, y + 4, x + 8, y + 40), fill=accent)
    draw.text((x + 22, y), title, font=title_font, fill=INK)
    y += 48
    y = draw_wrapped(draw, (x, y), body, body_font, INK, max_width, line_gap=10, max_lines=max_lines)
    return y + 26


def make_ingredient_card(row: dict[str, str]) -> Path:
    CARD_DIR.mkdir(parents=True, exist_ok=True)
    w, h = 900, 1180
    img = Image.new("RGB", (w, h), PAPER)
    draw = ImageDraw.Draw(img)

    accent, bg = category_style(row.get("category", ""))
    draw.rectangle((0, 0, w, 18), fill=accent)
    draw_round_rect(draw, (34, 36, w - 34, h - 36), 22, WHITE, outline=LINE, width=2)

    top_y = 70
    small_font = load_font(25)
    title_font = load_font(58, bold=True)
    en_font = load_font(30)

    draw.text((70, top_y), row["card_id"], font=small_font, fill=accent)
    risk_ink, risk_bg = risk_color(row.get("commercial_overclaim_risk", "中"))
    draw_round_rect(draw, (690, top_y - 4, 830, top_y + 42), 18, risk_bg, outline=None)
    draw.text((716, top_y + 4), f"宣传风险 {row.get('commercial_overclaim_risk', '中')}", font=load_font(22, bold=True), fill=risk_ink)

    title_y = top_y + 48
    title_lines = wrap_text(draw, row["name_zh"], title_font, 760, max_lines=2)
    for i, line in enumerate(title_lines):
        draw.text((70, title_y + i * 68), line, font=title_font, fill=INK)
    en_y = title_y + max(1, len(title_lines)) * 70
    draw_wrapped(draw, (70, en_y), row.get("name_en", ""), en_font, MUTED, 760, max_lines=2)

    chip_y = en_y + 92
    draw_chip(draw, 70, chip_y, "健康证据", row.get("health_evidence", ""), 230, 100)
    draw_chip(draw, 320, chip_y, "皮肤证据", row.get("skin_evidence", ""), 230, 100)
    draw_round_rect(draw, (570, chip_y, 830, chip_y + 100), 18, bg, outline=(220, 226, 232))
    draw.text((594, chip_y + 14), "撤稿/发表", font=load_font(24), fill=MUTED)
    rate = row.get("retractions_per_1000_publications", "0")
    draw.text((594, chip_y + 48), f"{rate}/千篇", font=load_font(34, bold=True), fill=accent)

    y = chip_y + 138
    max_width = 760
    y = draw_section(draw, 70, y, "一句话", row.get("one_sentence", ""), max_width, accent, 3)
    y = draw_section(draw, 70, y, "常见误解", row.get("common_misunderstanding", ""), max_width, accent, 3)
    y = draw_section(draw, 70, y, "注意", row.get("attention", ""), max_width, accent, 3)

    retraction = row.get("retraction_note", "")
    if y < 1020:
        y = draw_section(draw, 70, y, "撤稿记录", retraction, max_width, accent, 2)

    footer = f"更新 {UPDATE_MONTH} | 只做证据导航，不给个人剂量、诊断或处方替代"
    draw.text((70, h - 90), footer, font=load_font(23), fill=MUTED)

    path = CARD_DIR / f"{row['card_id']}-{safe_filename(row['name_zh'])}.png"
    img.save(path, optimize=True, quality=95)
    return path


def gradient_color(value: int, max_value: int) -> tuple[int, int, int]:
    if max_value <= 0:
        return (239, 244, 246)
    t = math.sqrt(max(0, value) / max_value)
    low = (230, 243, 244)
    high = (19, 104, 124)
    return tuple(int(low[i] + (high[i] - low[i]) * t) for i in range(3))


def draw_heatmap(
    rows: list[dict[str, str]],
    columns: list[str],
    title: str,
    subtitle: str,
    output: Path,
    value_suffix: str = "",
) -> Path:
    row_h = 68
    cell_w = 145 if len(columns) > 5 else 170
    left = 430
    top = 190
    right_pad = 80
    bottom_pad = 120
    width = left + len(columns) * cell_w + right_pad
    height = top + (len(rows) + 1) * row_h + bottom_pad
    img = Image.new("RGB", (width, height), PAPER)
    draw = ImageDraw.Draw(img)
    title_font = load_font(46, bold=True)
    subtitle_font = load_font(26)
    label_font = load_font(25)
    header_font = load_font(26, bold=True)
    value_font = load_font(25, bold=True)

    draw.text((60, 48), title, font=title_font, fill=INK)
    draw_wrapped(draw, (60, 108), subtitle, subtitle_font, MUTED, width - 120, max_lines=2)

    values = [
        int(float(row.get(col, "0") or 0))
        for row in rows
        for col in columns
    ]
    max_value = max(values) if values else 0

    for c, col in enumerate(columns):
        x = left + c * cell_w
        draw.text((x + 22, top - 48), col, font=header_font, fill=INK)
    draw.line((60, top - 12, width - 60, top - 12), fill=LINE, width=2)

    for r, row in enumerate(rows):
        y = top + r * row_h
        label = row.get("topic", "")
        label_lines = wrap_text(draw, label, label_font, left - 95, max_lines=2)
        for i, line in enumerate(label_lines):
            draw.text((60, y + 14 + i * 27), line, font=label_font, fill=INK)
        for c, col in enumerate(columns):
            value = int(float(row.get(col, "0") or 0))
            x = left + c * cell_w
            color = gradient_color(value, max_value)
            draw.rectangle((x, y, x + cell_w - 8, y + row_h - 8), fill=color)
            fill = WHITE if value > max_value * 0.45 else INK
            text = f"{value}{value_suffix}"
            tw = text_len(draw, text, value_font)
            draw.text((x + (cell_w - 8 - tw) / 2, y + 20), text, font=value_font, fill=fill)

    legend_y = height - 80
    draw.text((60, legend_y), "颜色越深，数量越多", font=load_font(24), fill=MUTED)
    for i in range(8):
        color = gradient_color(i, 7)
        draw.rectangle((300 + i * 46, legend_y + 2, 338 + i * 46, legend_y + 28), fill=color)
    draw.text((700, legend_y), "2026 年尚未结束，后续会继续更新。", font=load_font(24), fill=MUTED)
    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output, optimize=True, quality=95)
    return output


def make_card_wall(card_paths: list[Path], output: Path) -> Path:
    thumb_w, thumb_h = 210, 275
    cols = 5
    gap = 24
    title_h = 130
    rows = math.ceil(len(card_paths) / cols)
    w = cols * thumb_w + (cols + 1) * gap
    h = title_h + rows * thumb_h + (rows + 1) * gap
    img = Image.new("RGB", (w, h), PAPER)
    draw = ImageDraw.Draw(img)
    draw.text((gap, 32), "前 50 个常见成分卡片总览", font=load_font(42, bold=True), fill=INK)
    draw.text((gap, 84), "每张小图都可单独放进飞书画廊视图或社交媒体卡片。", font=load_font(25), fill=MUTED)

    for idx, path in enumerate(card_paths):
        r = idx // cols
        c = idx % cols
        x = gap + c * (thumb_w + gap)
        y = title_h + gap + r * (thumb_h + gap)
        with Image.open(path) as card:
            thumb = card.resize((thumb_w, thumb_h))
        img.paste(thumb, (x, y))
        draw.rectangle((x, y, x + thumb_w, y + thumb_h), outline=LINE, width=1)
    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output, optimize=True, quality=95)
    return output


def make_combined_dashboard(paths: list[Path], output: Path) -> Path:
    opened = [Image.open(path).convert("RGB") for path in paths]
    max_w = max(img.width for img in opened)
    margin = 34
    total_h = margin + sum(int(img.height * max_w / img.width) + margin for img in opened)
    canvas = Image.new("RGB", (max_w + margin * 2, total_h), PAPER)
    y = margin
    for img in opened:
        scaled_h = int(img.height * max_w / img.width)
        resized = img.resize((max_w, scaled_h))
        canvas.paste(resized, (margin, y))
        y += scaled_h + margin
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, optimize=True, quality=95)
    for img in opened:
        img.close()
    return output


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CARD_DIR.mkdir(parents=True, exist_ok=True)

    ingredient_rows = read_csv(DATA_DIR / "social_cards_top50_ingredients.csv")
    ingredient_rows = sorted(ingredient_rows, key=lambda row: row.get("card_id", ""))
    card_paths = [make_ingredient_card(row) for row in ingredient_rows]

    topic_year_rows = read_csv(DATA_DIR / "research_heatmap_topic_year.csv")
    topic_year_rows = sorted(topic_year_rows, key=lambda row: int(row.get("total_2020_2026", "0") or 0), reverse=True)
    years = ["2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    topic_year_path = draw_heatmap(
        topic_year_rows,
        years,
        "研究热力图：哪些抗衰主题这几年更热",
        "按主题统计 2020-2026 年候选文献数量。深色不是“更有效”，只是研究更多。",
        OUT_DIR / f"heatmap-topic-year-{UPDATE_MONTH}.png",
    )

    evidence_rows = read_csv(DATA_DIR / "research_heatmap_topic_evidence.csv")
    evidence_rows = sorted(evidence_rows, key=lambda row: int(row.get("total", "0") or 0), reverse=True)
    evidence_path = draw_heatmap(
        evidence_rows,
        ["A", "B", "C", "D", "E"],
        "证据热力图：哪些主题更接近高等级证据",
        "A/B 代表更靠近人体临床与系统评价，C/D/E 代表证据还更早期或不稳定。",
        OUT_DIR / f"heatmap-topic-evidence-{UPDATE_MONTH}.png",
    )

    wall_path = make_card_wall(card_paths, OUT_DIR / f"ingredient-card-wall-{UPDATE_MONTH}.png")
    dashboard_path = make_combined_dashboard(
        [topic_year_path, evidence_path],
        OUT_DIR / f"heatmap-dashboard-{UPDATE_MONTH}.png",
    )

    card_manifest: list[dict[str, Any]] = []
    by_id = {row["card_id"]: row for row in ingredient_rows}
    for path in card_paths:
        card_id = path.name.split("-", 1)[0]
        row = by_id[card_id]
        card_manifest.append(
            {
                "card_id": row["card_id"],
                "update_month": UPDATE_MONTH,
                "name_zh": row["name_zh"],
                "name_en": row.get("name_en", ""),
                "category": row.get("category", ""),
                "health_evidence": row.get("health_evidence", ""),
                "skin_evidence": row.get("skin_evidence", ""),
                "commercial_overclaim_risk": row.get("commercial_overclaim_risk", ""),
                "one_sentence": row.get("one_sentence", ""),
                "common_misunderstanding": row.get("common_misunderstanding", ""),
                "attention": row.get("attention", ""),
                "retraction_note": row.get("retraction_note", ""),
                "local_path": str(path.relative_to(ROOT)).replace("\\", "/"),
            }
        )

    heatmap_manifest = [
        {
            "asset_id": "H001",
            "update_month": UPDATE_MONTH,
            "title": "研究热力图：主题 x 年份",
            "asset_type": "heatmap_png",
            "description": "按主题和年份显示候选文献数量，颜色越深数量越多。",
            "data_source": "data/research_heatmap_topic_year.csv",
            "local_path": str(topic_year_path.relative_to(ROOT)).replace("\\", "/"),
        },
        {
            "asset_id": "H002",
            "update_month": UPDATE_MONTH,
            "title": "证据热力图：主题 x 证据等级",
            "asset_type": "heatmap_png",
            "description": "按主题和证据等级显示文献数量，帮助读者看出哪些方向证据更成熟。",
            "data_source": "data/research_heatmap_topic_evidence.csv",
            "local_path": str(evidence_path.relative_to(ROOT)).replace("\\", "/"),
        },
        {
            "asset_id": "H003",
            "update_month": UPDATE_MONTH,
            "title": "热力图总览图",
            "asset_type": "dashboard_png",
            "description": "把研究热力图和证据热力图合并成一张长图，便于飞书和社媒展示。",
            "data_source": "data/research_heatmap_topic_year.csv; data/research_heatmap_topic_evidence.csv",
            "local_path": str(dashboard_path.relative_to(ROOT)).replace("\\", "/"),
        },
        {
            "asset_id": "H004",
            "update_month": UPDATE_MONTH,
            "title": "前 50 成分证据产出图",
            "asset_type": "evidence_yield_png",
            "description": "按统一代理指标展示常见成分的证据产出结构，不作为产品或疗效排行榜。",
            "data_source": f"data/evidence_yield_metrics_{UPDATE_MONTH_UNDERSCORE}.csv",
            "local_path": f"build/visual-assets/evidence-yield-ingredients-{UPDATE_MONTH}.png",
        },
        {
            "asset_id": "H005",
            "update_month": UPDATE_MONTH,
            "title": "撤稿密度观察图",
            "asset_type": "retraction_density_png",
            "description": "展示撤稿风险观察指标；撤稿密度是复核提醒，不单独判定有效或无效。",
            "data_source": "data/retraction_risk_summary_20y.csv",
            "local_path": f"build/visual-assets/retraction-density-{UPDATE_MONTH}.png",
        },
        {
            "asset_id": "H006",
            "update_month": UPDATE_MONTH,
            "title": "主题证据产出图",
            "asset_type": "topic_evidence_yield_png",
            "description": "比较各主题进入较高等级证据层的比例，不代表个人行动优先级。",
            "data_source": f"data/topic_evidence_yield_metrics_{UPDATE_MONTH_UNDERSCORE}.csv",
            "local_path": f"build/visual-assets/topic-evidence-yield-{UPDATE_MONTH}.png",
        },
        {
            "asset_id": "C000",
            "update_month": UPDATE_MONTH,
            "title": "前 50 成分卡片总览图",
            "asset_type": "card_wall_png",
            "description": "50 张成分卡片的总览墙，适合放在飞书入口页作为视觉索引。",
            "data_source": "data/social_cards_top50_ingredients.csv",
            "local_path": str(wall_path.relative_to(ROOT)).replace("\\", "/"),
        },
    ]

    write_csv(
        DATA_DIR / f"visual_ingredient_cards_{UPDATE_MONTH_UNDERSCORE}.csv",
        card_manifest,
        [
            "card_id",
            "update_month",
            "name_zh",
            "name_en",
            "category",
            "health_evidence",
            "skin_evidence",
            "commercial_overclaim_risk",
            "one_sentence",
            "common_misunderstanding",
            "attention",
            "retraction_note",
            "local_path",
        ],
    )
    write_csv(
        DATA_DIR / f"visual_heatmap_assets_{UPDATE_MONTH_UNDERSCORE}.csv",
        heatmap_manifest,
        [
            "asset_id",
            "update_month",
            "title",
            "asset_type",
            "description",
            "data_source",
            "local_path",
        ],
    )

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_CARD_DIR.mkdir(parents=True, exist_ok=True)
    public_main_assets = [
        topic_year_path,
        evidence_path,
        wall_path,
        dashboard_path,
        OUT_DIR / f"evidence-yield-ingredients-{UPDATE_MONTH}.png",
        OUT_DIR / f"retraction-density-{UPDATE_MONTH}.png",
        OUT_DIR / f"topic-evidence-yield-{UPDATE_MONTH}.png",
    ]
    for path in public_main_assets:
        if not path.exists():
            raise FileNotFoundError(f"Missing public visual asset: {path}")
        shutil.copy2(path, PUBLIC_DIR / path.name)
    for path in card_paths:
        shutil.copy2(path, PUBLIC_CARD_DIR / path.name)

    print(f"Generated {len(card_paths)} ingredient card PNGs")
    print(f"Published {len(public_main_assets) + len(card_paths)} PNGs to {PUBLIC_DIR.relative_to(ROOT)}")
    print(topic_year_path.relative_to(ROOT))
    print(evidence_path.relative_to(ROOT))
    print(wall_path.relative_to(ROOT))
    print(dashboard_path.relative_to(ROOT))


if __name__ == "__main__":
    main()
