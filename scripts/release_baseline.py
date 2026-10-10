"""Read a verified baseline, including a previous release in the same month."""

import csv
import io
import zipfile
from pathlib import Path

import archive_public_snapshots as snapshots


def baseline_rows(root: Path, config: dict, asset: str) -> list[dict[str, str]]:
    month = config["EVIDENCE_ATLAS_BASELINE_MONTH"]
    filename = f"{asset.replace('_', '-')}-{month}.csv"
    archive_name = config.get("EVIDENCE_ATLAS_BASELINE_ARCHIVE")
    if archive_name:
        path = root / archive_name
        snapshots.verify_archive(path)
        with zipfile.ZipFile(path) as archive:
            payload = archive.read(filename).decode("utf-8-sig")
        return list(csv.DictReader(io.StringIO(payload)))
    with (root / "public-data" / filename).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))
