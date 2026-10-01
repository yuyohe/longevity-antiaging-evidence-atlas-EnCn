"""Archive superseded visual releases, verifying every byte before replacement."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ARCHIVES = ROOT / "archive/visual-releases"
MONTHS = ("2026-06", "2026-07", "2026-08", "2026-09")
PREVIOUS = {"late-september-public-update-2026-09.html", "yulcell-posting-asset-dashboard-2026-09-21.html"}
REPO = "https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn"


def repair_archived_links() -> None:
    index = json.loads((ROOT / "data/asset_archive_index.json").read_text(encoding="utf-8"))
    commit = index[0]["source_commit"]
    frozen = set(subprocess.check_output(["git", "ls-tree", "-r", "--name-only", commit], cwd=ROOT, text=True).splitlines())
    allowed = set()
    for row in index:
        allowed.update(item["path"] for item in verify_archive(ROOT / row["archive"])["files"])
    allowed.update(f"public-data/{name}-2026-08.csv" for name in
                   ["candidate-sources", "literature-library", "shortlist-sources", "evidence-findings", "evidence-matrix"])
    files = subprocess.check_output(["git", "ls-files", "-z", "--", "*.md"], cwd=ROOT).decode("utf-8").split("\0")
    changes = 0
    for relative in filter(None, files):
        path = ROOT / relative
        if not path.exists():
            continue
        original = path.read_text(encoding="utf-8-sig")

        def replace(match):
            nonlocal changes
            image, label, target = match.groups()
            url = urlsplit(target.strip("<>"))
            if url.scheme or url.netloc or not url.path:
                return match.group()
            resolved = (path.parent / unquote(url.path)).resolve()
            if resolved.exists() or not resolved.is_relative_to(ROOT.resolve()):
                return match.group()
            name = resolved.relative_to(ROOT.resolve()).as_posix()
            if name not in allowed or name not in frozen:
                return match.group()
            changes += 1
            base = "https://raw.githubusercontent.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn" if image else REPO + "/blob"
            return f"{image}[{label}]({base}/{commit}/{name})"

        updated = re.sub(r"(!?)\[([^\]]*)\]\(([^)]+)\)", replace, original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
    print(f"Repaired {changes} archived Markdown links to the frozen source commit")


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verify_archive(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        if archive.testzip():
            raise RuntimeError(f"Archive CRC failed: {path.name}")
        manifest = json.loads(archive.read("MANIFEST.json"))
        if set(archive.namelist()) != {r["path"] for r in manifest["files"]} | {"MANIFEST.json"}:
            raise RuntimeError("Archive member list differs from manifest")
        for row in manifest["files"]:
            payload = archive.read(row["path"])
            if len(payload) != row["bytes"] or digest(payload) != row["sha256"]:
                raise RuntimeError(f"Archive content mismatch: {row['path']}")
    return manifest


def candidates() -> dict[str, list[Path]]:
    groups = {month: [] for month in MONTHS}
    for path in (ROOT / "docs").glob("*.html"):
        match = re.search(r"2026-0[6-9]", path.name)
        if match and path.name not in PREVIOUS and path.stat().st_size > 1024 * 1024:
            groups[match.group()].append(path)
    for month in MONTHS[:-1]:
        groups[month].extend((ROOT / "docs/assets/visual-assets" / month).rglob("*.png"))
    return {month: sorted(paths) for month, paths in groups.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Archive and replace only verified historical files")
    parser.add_argument("--repair-links", action="store_true", help="Repair links to already archived files")
    args = parser.parse_args()
    if args.repair_links:
        repair_archived_links()
        return
    groups = candidates()
    if not args.apply:
        print(json.dumps({m: {"files": len(ps), "bytes": sum(p.stat().st_size for p in ps)}
                          for m, ps in groups.items()}, indent=2))
        return
    source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    ARCHIVES.mkdir(parents=True, exist_ok=True)
    for month, paths in groups.items():
        archive_path = ARCHIVES / f"visual-release-{month}.zip"
        if not paths:
            continue
        if archive_path.exists():
            raise RuntimeError(f"Refusing to overwrite historical archive: {archive_path.name}")
        records = []
        for path in paths:
            resolved = path.resolve()
            resolved.relative_to(ROOT.resolve())
            if path.is_symlink() or not path.is_file():
                raise RuntimeError(f"Unexpected source: {path}")
            records.append({"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
                            "sha256": digest(path.read_bytes())})
        manifest = {"month": month, "archived_on": "2026-10-01", "source_commit": source_commit, "files": records}
        temp = archive_path.with_suffix(".zip.tmp")
        with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for row in records:
                archive.writestr(row["path"], (ROOT / row["path"]).read_bytes())
            archive.writestr("MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        verify_archive(temp)
        temp.replace(archive_path)
        for path, row in zip(paths, records):
            if digest(path.read_bytes()) != row["sha256"]:
                raise RuntimeError(f"Source changed before retirement: {path.name}")
            if path.suffix == ".html":
                path.write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>宇多Yul细胞/yulcell 历史资产 / Archived Asset</title><style>body{{font:18px/1.8 system-ui,sans-serif;max-width:760px;margin:50px auto;padding:0 20px;color:#20262b}}a{{color:#126c58;overflow-wrap:anywhere}}</style><h1>历史版本 / Historical Release</h1><p>宇多Yul细胞/yulcell · {month}</p><p>此版本已归档，不是当前结论。完整原件与图片保留在校验后的 ZIP 中，未删除历史证据。This superseded version remains recoverable in the verified archive.</p><ul><li><a href="../archive/visual-releases/{archive_path.name}">完整历史文件包 / Original archive</a></li><li><a href="{REPO}/blob/{source_commit}/{row['path']}">冻结版本 / Frozen Git version</a></li><li><a href="asset-catalog.md">当前资产总目录 / Current asset catalog</a></li></ul></html>\n''', encoding="utf-8")
            else:
                path.unlink()
        print(f"Archived {month}: {len(records)} files verified")
    index = []
    for path in sorted(ARCHIVES.glob("visual-release-*.zip")):
        manifest = verify_archive(path)
        index.append({"month": manifest["month"], "archive": path.relative_to(ROOT).as_posix(),
                      "files": len(manifest["files"]), "original_bytes": sum(r["bytes"] for r in manifest["files"]),
                      "archive_bytes": path.stat().st_size, "sha256": digest(path.read_bytes()),
                      "source_commit": manifest["source_commit"]})
    (ROOT / "data/asset_archive_index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    (ARCHIVES / "SHA256SUMS.txt").write_text("".join(f"{r['sha256']}  {Path(r['archive']).name}\n" for r in index), encoding="ascii")
    for month in MONTHS[:-1]:
        directory = ROOT / "docs/assets/visual-assets" / month
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "README.md").write_text(f"# {month} 历史图片 / Historical Images\n\n宇多Yul细胞/yulcell 此期 57 张原图已完整归档。\n\n[下载校验后的历史包 / Download verified archive](../../../../archive/visual-releases/visual-release-{month}.zip)\n\n[当前资产目录 / Current assets](../../../asset-catalog.md)\n", encoding="utf-8")


if __name__ == "__main__":
    main()
