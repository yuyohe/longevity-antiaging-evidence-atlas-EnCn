"""Prepare Markdown pages for Feishu publishing.

This does not call Feishu API. It creates `build/feishu-docs/` so that
Codex or a publishing script can import these Markdown files into Feishu Docs.
"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "feishu-docs"

PUBLIC_FILES = [
    ROOT / "README.zh-CN.md",
    ROOT / "content" / "overview" / "public-summary.md",
    ROOT / "docs" / "current-output-status.md",
    ROOT / "content" / "analysis" / "evidence-ranking.md",
    ROOT / "content" / "recommendations" / "for-general-readers.md",
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for file in PUBLIC_FILES:
        if file.exists():
            shutil.copy2(file, OUT / file.name)
    topics_dir = ROOT / "content" / "topics"
    for file in topics_dir.glob("*.md"):
        if not file.name.startswith("_"):
            shutil.copy2(file, OUT / f"topic-{file.name}")
    papers_dir = ROOT / "content" / "papers"
    for file in papers_dir.glob("*.md"):
        if not file.name.startswith("_"):
            shutil.copy2(file, OUT / f"paper-{file.name}")
    print(f"Prepared Feishu Markdown files in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
