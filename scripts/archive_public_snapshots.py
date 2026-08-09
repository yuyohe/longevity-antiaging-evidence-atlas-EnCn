"""Compress older public CSV snapshots and verify them before source removal."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DATA = ROOT / "public-data"
ARCHIVE_DIR = ROOT / "archive" / "public-data"
ASSET_NAMES = (
    "literature-library",
    "candidate-sources",
    "shortlist-sources",
    "evidence-findings",
    "evidence-matrix",
)
ZIP_TIMESTAMP = (2026, 8, 9, 0, 0, 0)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_rows(payload: bytes) -> int:
    text = payload.decode("utf-8-sig")
    return sum(1 for _ in csv.DictReader(io.StringIO(text)))


def manifest_bytes(month: str, source_payloads: dict[str, bytes]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=["snapshot", "file", "rows", "bytes", "sha256"],
        lineterminator="\n",
    )
    writer.writeheader()
    for name, payload in source_payloads.items():
        writer.writerow(
            {
                "snapshot": month,
                "file": name,
                "rows": csv_rows(payload),
                "bytes": len(payload),
                "sha256": sha256_bytes(payload),
            }
        )
    return output.getvalue().encode("utf-8")


def zip_entry(name: str, payload: bytes) -> tuple[zipfile.ZipInfo, bytes]:
    info = zipfile.ZipInfo(name, date_time=ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    info.create_system = 3
    return info, payload


def verify_archive(path: Path) -> list[dict[str, str]]:
    with zipfile.ZipFile(path) as archive:
        bad_member = archive.testzip()
        if bad_member:
            raise RuntimeError(f"CRC verification failed for {path.name}: {bad_member}")
        if "MANIFEST.csv" not in archive.namelist():
            raise RuntimeError(f"{path.name} is missing MANIFEST.csv")
        manifest = list(
            csv.DictReader(io.StringIO(archive.read("MANIFEST.csv").decode("utf-8")))
        )
        expected_names = {row["file"] for row in manifest}
        actual_names = set(archive.namelist()) - {"MANIFEST.csv"}
        if actual_names != expected_names:
            raise RuntimeError(f"{path.name} member list does not match its manifest")
        for row in manifest:
            payload = archive.read(row["file"])
            if str(len(payload)) != row["bytes"]:
                raise RuntimeError(f"{path.name}:{row['file']} byte count mismatch")
            if sha256_bytes(payload) != row["sha256"]:
                raise RuntimeError(f"{path.name}:{row['file']} SHA-256 mismatch")
            if csv_rows(payload) != int(row["rows"]):
                raise RuntimeError(f"{path.name}:{row['file']} CSV row count mismatch")
        return manifest


def build_archive(month: str) -> tuple[Path, list[dict[str, str]], list[Path]]:
    source_paths = [PUBLIC_DATA / f"{name}-{month}.csv" for name in ASSET_NAMES]
    archive_path = ARCHIVE_DIR / f"public-data-{month}.zip"
    existing_sources = [path for path in source_paths if path.exists()]

    if not existing_sources:
        if not archive_path.exists():
            raise FileNotFoundError(f"No source CSVs or archive found for {month}")
        return archive_path, verify_archive(archive_path), []
    if len(existing_sources) != len(source_paths):
        missing = ", ".join(path.name for path in source_paths if not path.exists())
        raise FileNotFoundError(f"Incomplete {month} snapshot; missing: {missing}")

    source_payloads = {path.name: path.read_bytes() for path in source_paths}
    temp_path = archive_path.with_suffix(".zip.tmp")
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(temp_path, "w", allowZip64=True) as archive:
        for name, payload in source_payloads.items():
            info, content = zip_entry(name, payload)
            archive.writestr(info, content, compresslevel=9)
        info, content = zip_entry("MANIFEST.csv", manifest_bytes(month, source_payloads))
        archive.writestr(info, content, compresslevel=9)
    os.replace(temp_path, archive_path)

    verified_manifest = verify_archive(archive_path)
    for row in verified_manifest:
        source = PUBLIC_DATA / row["file"]
        if sha256_file(source) != row["sha256"]:
            raise RuntimeError(f"Source verification failed before removal: {source.name}")
    return archive_path, verified_manifest, source_paths


def write_checksums(archives: list[Path]) -> None:
    lines = [f"{sha256_file(path)}  {path.name}" for path in sorted(archives)]
    (ARCHIVE_DIR / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="ascii")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("months", nargs="+", help="Snapshots to archive, for example 2026-05 2026-06")
    parser.add_argument(
        "--delete-source",
        action="store_true",
        help="Delete source CSVs only after archive CRC, byte, row-count, and SHA-256 verification.",
    )
    args = parser.parse_args()

    archives: list[Path] = []
    sources_to_delete: list[Path] = []
    for month in args.months:
        archive_path, manifest, sources = build_archive(month)
        archives.append(archive_path)
        sources_to_delete.extend(sources)
        print(
            f"verified {archive_path.relative_to(ROOT)}: "
            f"{len(manifest)} CSVs, {sum(int(row['rows']) for row in manifest):,} rows"
        )

    write_checksums(archives)
    if args.delete_source:
        for source in sources_to_delete:
            source.unlink()
        print(f"removed {len(sources_to_delete)} verified source CSVs")
    else:
        print("source CSVs retained; pass --delete-source after review")


if __name__ == "__main__":
    main()
