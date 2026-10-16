"""Move superseded reader documents out of active folders, repairing local links."""

from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
import posixpath
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
REPO = "https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn"
ARCHIVE = "archive/reader-history"


def rewrite_target(target: str, old_source: str, new_source: str, moves: dict[str, str]) -> str:
    url = urlsplit(target)
    prefix = REPO + "/blob/main/"
    if target.startswith(prefix):
        tail = target[len(prefix):]
        path = urlsplit(tail).path
        return target.replace(prefix + path, prefix + moves[path], 1) if path in moves else target
    if url.scheme or url.netloc or not url.path or url.path.startswith("/"):
        return target
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(old_source), unquote(url.path)))
    if resolved.startswith("../"):
        return target
    new_target = moves.get(resolved, resolved)
    if old_source == new_source and new_target == resolved:
        return target
    relative = posixpath.relpath(new_target, posixpath.dirname(new_source))
    return urlunsplit(("", "", relative, url.query, url.fragment))


def rewrite_markdown(text: str, old_source: str, new_source: str, moves: dict[str, str]) -> str:
    def replace(match):
        image, label, target = match.groups()
        new = rewrite_target(target, old_source, new_source, moves)
        return f"{image}[{label}]({new})"
    return re.sub(r"(!?)\[([^\]]*)\]\(([^)\s]+)\)", replace, text)


class LinkEdits(HTMLParser):
    def __init__(self, text: str, old_source: str, new_source: str, moves: dict[str, str]):
        super().__init__(convert_charrefs=False)
        self.offsets = [0]
        for line in text.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        self.old_source, self.new_source, self.moves = old_source, new_source, moves
        self.edits: list[tuple[int, int, str]] = []

    def handle_starttag(self, tag, attrs):
        raw = self.get_starttag_text()
        updated = raw
        for name, value in attrs:
            if name not in {"href", "src"} or not value:
                continue
            new = rewrite_target(value, self.old_source, self.new_source, self.moves)
            if new != value:
                pattern = re.compile(rf"(\b{re.escape(name)}\s*=\s*)([\"'])(.*?)\2", re.IGNORECASE | re.DOTALL)
                updated = pattern.sub(lambda m: m[1] + m[2] + html.escape(new, quote=True) + m[2]
                                      if html.unescape(m[3]) == value else m[0], updated)
        if updated != raw:
            line, column = self.getpos()
            start = self.offsets[line - 1] + column
            self.edits.append((start, start + len(raw), updated))

    handle_startendtag = handle_starttag


def rewrite_html(text: str, old_source: str, new_source: str, moves: dict[str, str]) -> str:
    parser = LinkEdits(text, old_source, new_source, moves)
    parser.feed(text)
    for start, end, replacement in reversed(parser.edits):
        text = text[:start] + replacement + text[end:]
    return text


def history_plan(cfg: dict, root: Path = ROOT) -> dict[str, str]:
    month = cfg["EVIDENCE_ATLAS_ASSET_MONTH"]
    date = cfg["EVIDENCE_ATLAS_UPDATE_DATE"]
    protected = {
        f"docs/{cfg['EVIDENCE_ATLAS_PUBLIC_REPORT_FILE']}",
        f"docs/yulcell-posting-asset-dashboard-{date}.html",
        f"docs/research-heatmap-{month}.html", f"docs/monthly-update-{month}.html",
        f"docs/feishu-public-assets-{month}.md", f"docs/public-full-data-index-{month}.md",
        f"content/public-reader/{cfg['EVIDENCE_ATLAS_RELEASE_FILE']}",
        f"content/public-reader/monthly-update-{month}.md",
    }
    result = {}
    for directory in [root / "docs", root / "content/public-reader"]:
        for path in sorted(directory.iterdir()):
            relative = path.relative_to(root).as_posix()
            if not path.is_file() or path.suffix not in {".md", ".html"} or not re.search(r"20\d{2}", path.name):
                continue
            if relative in protected or date in path.name:
                continue
            result[relative] = f"{ARCHIVE}/{relative}"
    return result


def finalize_manifest(root: Path = ROOT) -> int:
    """Freeze canonical LF copies and hash the originals from their Git commits."""
    path = root / ARCHIVE / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        archived = root / entry["archive_path"]
        text = archived.read_text(encoding="utf-8-sig")
        archived.write_text(text, encoding="utf-8", newline="\n")
        original = subprocess.check_output(["git", "show", f"{entry['source_commit']}:{entry['old_path']}"], cwd=root)
        entry["source_sha256"] = hashlib.sha256(original).hexdigest()
        entry["archived_sha256"] = hashlib.sha256(archived.read_bytes()).hexdigest()
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return len(manifest["files"])


def verify_manifest(root: Path = ROOT) -> int:
    archive_root = (root / ARCHIVE).resolve()
    manifest = json.loads((archive_root / "manifest.json").read_text(encoding="utf-8"))
    seen = set()
    for entry in manifest["files"]:
        archived = (root / entry["archive_path"]).resolve()
        if not archived.is_relative_to(archive_root) or archived in seen:
            raise ValueError("Unsafe or duplicate reader archive path")
        seen.add(archived)
        if hashlib.sha256(archived.read_bytes()).hexdigest() != entry["archived_sha256"]:
            raise ValueError(f"Reader archive checksum mismatch: {entry['archive_path']}")
        if not re.fullmatch(r"[0-9a-f]{40}", entry["source_commit"]) or not re.fullmatch(r"[0-9a-f]{64}", entry["source_sha256"]):
            raise ValueError("Reader archive lacks a frozen source reference")
    return len(seen)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    cfg = json.loads((ROOT / "data/current_release.json").read_text(encoding="utf-8"))
    moves = history_plan(cfg)
    print(json.dumps({"apply": args.apply, "files": len(moves), "moves": moves}, ensure_ascii=False, indent=2), flush=True)
    if not args.apply or not moves:
        return
    archive_root = (ROOT / ARCHIVE).resolve()
    if not archive_root.is_relative_to(ROOT.resolve()):
        raise RuntimeError("Archive escapes workspace")
    for old, new in moves.items():
        source, destination = (ROOT / old).resolve(), (ROOT / new).resolve()
        if not source.is_relative_to(ROOT.resolve()) or not destination.is_relative_to(archive_root):
            raise RuntimeError("Unsafe archive path")
        if destination.exists():
            raise RuntimeError(f"Archive already has a different entry: {new}")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    names = subprocess.check_output(["git", "ls-files", "-z", "--", "*.md", "*.html"], cwd=ROOT).decode("utf-8").split("\0")
    manifest = []
    changed = 0
    for old in filter(None, names):
        source = ROOT / old
        if not source.exists():
            continue
        new = moves.get(old, old)
        payload = source.read_bytes()
        text = payload.decode("utf-8-sig")
        transform = rewrite_html if source.suffix == ".html" else rewrite_markdown
        updated = transform(text, old, new, moves)
        if old != new:
            destination = ROOT / new
            destination.parent.mkdir(parents=True, exist_ok=True)
            source.replace(destination)
            if updated != text:
                destination.write_text(updated, encoding="utf-8", newline="\n")
            manifest.append({"old_path": old, "archive_path": new,
                             "source_commit": commit, "source_sha256": hashlib.sha256(payload).hexdigest(),
                             "archived_sha256": hashlib.sha256(destination.read_bytes()).hexdigest()})
        elif updated != text:
            source.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
    output = archive_root / "manifest.json"
    previous = json.loads(output.read_text(encoding="utf-8")) if output.exists() else {"files": []}
    previous["files"].extend(manifest)
    output.write_text(json.dumps(previous, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    finalize_manifest()
    previous = json.loads(output.read_text(encoding="utf-8"))
    for entry in previous["files"]:
        if hashlib.sha256((ROOT / entry["archive_path"]).read_bytes()).hexdigest() != entry["archived_sha256"]:
            raise RuntimeError("Archived file checksum mismatch")
    readme = "# 历史阅读文件 / Historical Reader Files\n\n这些是过去的月度报告与入口，不是当前结论。原始字节可从 manifest.json 中的 source_commit 恢复；归档副本修正相对链接并统一UTF-8与LF换行。\n\n[回到当前内容](../../docs/asset-catalog.md)\n\n" + "\n".join(f"- [{Path(entry['old_path']).name}]({posixpath.relpath(entry['archive_path'], ARCHIVE)})" for entry in previous["files"]) + "\n"
    (archive_root / "README.md").write_text(readme, encoding="utf-8")
    print(f"Archived {len(manifest)} reader files; repaired links in {changed} active files", flush=True)


if __name__ == "__main__":
    main()
