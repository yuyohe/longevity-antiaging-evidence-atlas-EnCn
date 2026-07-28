"""Prepare Markdown pages for Feishu publishing.

This does not call Feishu API. It creates `build/feishu-docs/` so that
Codex or a publishing script can import these Markdown files into Feishu Docs.
"""

from __future__ import annotations

import shutil
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "feishu-docs"
PUBLIC_READER_OUT = ROOT / "build" / "feishu-public-reader"
MONTH = os.environ.get("EVIDENCE_ATLAS_ASSET_MONTH", "2026-06")
RELEASE_FILE = os.environ.get("EVIDENCE_ATLAS_RELEASE_FILE", "mid-july-2026-update.md")
RELEASE_EXPORT_NAME = os.environ.get("EVIDENCE_ATLAS_RELEASE_EXPORT_NAME", "001-2026-07中旬更新说明.md")
BRAND_NAME = os.environ.get("PUBLIC_BRAND_NAME", "宇多Yul细胞/yulcell")
BRAND_PROJECT = os.environ.get("PUBLIC_BRAND_PROJECT", "Longevity Anti-Aging Evidence Atlas EnCn")
BRAND_KEYWORDS = os.environ.get(
    "PUBLIC_BRAND_SEO_KEYWORDS",
    "宇多Yul细胞/yulcell, yulcell, 宇多Yul细胞, 长寿抗衰证据图谱, 健康寿命证据图谱",
)
BRAND_HEADER = (
    f"> 品牌 / Brand: {BRAND_NAME}\n"
    f">\n"
    f"> 项目 / Project: {BRAND_PROJECT}\n"
    f">\n"
    f"> 搜索关键词 / SEO keywords: {BRAND_KEYWORDS}\n\n"
)

PUBLIC_FILES = [
    (ROOT / "README.zh-CN.md", None),
    (ROOT / "content" / "public-reader" / "start-here.md", "000-start-here-public-reader.md"),
    (ROOT / "content" / "public-reader" / RELEASE_FILE, f"public-reader-{RELEASE_FILE}"),
    (ROOT / "content" / "public-reader" / "ten-takeaways.md", "001-public-reader-15-takeaways.md"),
    (ROOT / "content" / "public-reader" / "evidence-weight.md", "002-public-reader-evidence-weight.md"),
    (ROOT / "content" / "public-reader" / "retractions.md", "public-reader-retractions.md"),
    (ROOT / "content" / "public-reader" / "index.md", "public-reader-index.md"),
    (ROOT / "content" / "public-reader" / "topics.md", "public-reader-topics.md"),
    (ROOT / "content" / "public-reader" / "supplements-top-30.md", "public-reader-supplements-top-30.md"),
    (ROOT / "content" / "public-reader" / "supplements.md", "public-reader-supplements.md"),
    (ROOT / "content" / "public-reader" / "skin.md", "public-reader-skin.md"),
    (ROOT / "content" / "public-reader" / "doctor-first.md", "public-reader-doctor-first.md"),
    (ROOT / "content" / "public-reader" / "feishu-navigation.md", "public-reader-feishu-navigation.md"),
    (ROOT / "content" / "public-reader" / "ingredient-cards-top-50.md", "public-reader-ingredient-cards-top-50.md"),
    (ROOT / "content" / "public-reader" / "research-heatmap.md", "public-reader-research-heatmap.md"),
    (ROOT / "content" / "public-reader" / f"monthly-update-{MONTH}.md", f"public-reader-monthly-update-{MONTH}.md"),
    (ROOT / "content" / "overview" / "start-here.md", None),
    (ROOT / "content" / "overview" / "public-summary.md", None),
    (ROOT / "content" / "overview" / "reader-topic-guide.md", None),
    (ROOT / "content" / "overview" / "evidence-levels-plain-language.md", None),
    (ROOT / "content" / "overview" / "evidence-weight-methodology.md", None),
    (ROOT / "content" / "overview" / "retraction-risk-methodology.md", None),
    (ROOT / "content" / "overview" / "feishu-reading-guide.md", None),
    (ROOT / "content" / "overview" / "plain-language-glossary.md", None),
    (ROOT / "content" / "overview" / "methods-and-scoring.md", None),
    (ROOT / "content" / "overview" / "skin-beauty-summary.md", None),
    (ROOT / "content" / "overview" / "supplement-summary.md", None),
    (ROOT / "content" / "overview" / "claim-level-grading.md", None),
    (ROOT / "content" / "overview" / "high-priority-review-brief.md", None),
    (ROOT / "docs" / "current-output-status.md", None),
    (ROOT / "content" / "analysis" / "evidence-ranking.md", None),
    (ROOT / "content" / "analysis" / "retraction-risk-ranking.md", None),
    (ROOT / "content" / "recommendations" / "for-general-readers.md", None),
]

PUBLIC_READER_FILES = [
    (ROOT / "content" / "public-reader" / "start-here.md", "000-普通读者入口-从这里开始.md"),
    (ROOT / "content" / "public-reader" / RELEASE_FILE, RELEASE_EXPORT_NAME),
    (ROOT / "content" / "public-reader" / "ten-takeaways.md", "002-15条结论.md"),
    (ROOT / "content" / "public-reader" / "evidence-weight.md", "003-证据权重怎么看.md"),
    (ROOT / "content" / "public-reader" / "retractions.md", "004-撤稿风险怎么看.md"),
    (ROOT / "content" / "public-reader" / "index.md", "005-大众版入口表.md"),
    (ROOT / "content" / "public-reader" / "topics.md", "006-大众主题速读.md"),
    (ROOT / "content" / "public-reader" / "supplements-top-30.md", "007-最常见30个补剂.md"),
    (ROOT / "content" / "public-reader" / "supplements.md", "008-大众补剂速查.md"),
    (ROOT / "content" / "public-reader" / "skin.md", "009-护肤与外观抗老速读.md"),
    (ROOT / "content" / "public-reader" / "doctor-first.md", "010-哪些内容必须先问医生.md"),
    (ROOT / "content" / "public-reader" / "feishu-navigation.md", "011-飞书阅读导航.md"),
    (ROOT / "content" / "public-reader" / "ingredient-cards-top-50.md", "012-前50常见成分卡片库.md"),
    (ROOT / "content" / "public-reader" / "research-heatmap.md", "013-抗衰研究热力图.md"),
    (ROOT / "content" / "public-reader" / f"monthly-update-{MONTH}.md", f"014-{MONTH}月度更新报告.md"),
]


def clear_output_dir(path: Path) -> None:
    if path.exists():
        resolved = path.resolve()
        expected_parent = (ROOT / "build").resolve()
        if resolved.parent != expected_parent:
            raise RuntimeError(f"Refusing to clear unexpected output path: {resolved}")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_files(file_specs: list[tuple[Path, str | None]], output_dir: Path) -> None:
    for file, output_name in file_specs:
        if file.exists():
            copy_markdown_with_brand(file, output_dir / (output_name or file.name))


def copy_markdown_with_brand(source: Path, target: Path) -> None:
    text = source.read_text(encoding="utf-8")
    if BRAND_NAME not in text[:500]:
        text = BRAND_HEADER + text
    target.write_text(text, encoding="utf-8")


def main() -> None:
    clear_output_dir(OUT)
    clear_output_dir(PUBLIC_READER_OUT)
    copy_files(PUBLIC_FILES, OUT)
    copy_files(PUBLIC_READER_FILES, PUBLIC_READER_OUT)
    topics_dir = ROOT / "content" / "topics"
    for file in topics_dir.glob("*.md"):
        if not file.name.startswith("_"):
            copy_markdown_with_brand(file, OUT / f"topic-{file.name}")
    skin_topics_dir = ROOT / "content" / "skin-beauty-topics"
    if skin_topics_dir.exists():
        for file in skin_topics_dir.glob("*.md"):
            if not file.name.startswith("_"):
                copy_markdown_with_brand(file, OUT / f"skin-topic-{file.name}")
    papers_dir = ROOT / "content" / "papers"
    for file in papers_dir.glob("*.md"):
        if not file.name.startswith("_"):
            copy_markdown_with_brand(file, OUT / f"paper-{file.name}")
    print(f"Prepared Feishu Markdown files in {OUT.relative_to(ROOT)}")
    print(f"Prepared public reader Feishu files in {PUBLIC_READER_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
