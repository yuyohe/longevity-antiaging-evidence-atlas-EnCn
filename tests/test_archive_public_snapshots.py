from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import archive_public_snapshots as snapshots  # noqa: E402


class PublicSnapshotArchiveTests(unittest.TestCase):
    def test_same_month_label_is_used_for_archive_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            public_data = root / "public-data"
            archive_dir = root / "archive"
            public_data.mkdir()
            for name in snapshots.ASSET_NAMES:
                (public_data / f"{name}-2026-08.csv").write_text(
                    "id,title\n1,Example\n", encoding="utf-8"
                )

            with (
                patch.object(snapshots, "PUBLIC_DATA", public_data),
                patch.object(snapshots, "ARCHIVE_DIR", archive_dir),
            ):
                archive, manifest, sources = snapshots.build_archive(
                    "2026-08", "2026-08-mid"
                )

            self.assertEqual(archive.name, "public-data-2026-08-mid.zip")
            self.assertEqual(len(sources), 5)
            self.assertEqual({row["snapshot"] for row in manifest}, {"2026-08-mid"})
            self.assertEqual({int(row["rows"]) for row in manifest}, {1})

    def test_checksum_file_includes_every_existing_archive(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_dir = Path(temp_dir)
            (archive_dir / "public-data-2026-05.zip").write_bytes(b"may")
            (archive_dir / "public-data-2026-08-mid.zip").write_bytes(b"august")

            with patch.object(snapshots, "ARCHIVE_DIR", archive_dir):
                snapshots.write_checksums()

            lines = (archive_dir / "SHA256SUMS.txt").read_text(encoding="ascii").splitlines()
            self.assertEqual(len(lines), 2)
            self.assertTrue(lines[0].endswith("  public-data-2026-05.zip"))
            self.assertTrue(lines[1].endswith("  public-data-2026-08-mid.zip"))


if __name__ == "__main__":
    unittest.main()
