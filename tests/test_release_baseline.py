import tempfile
import unittest
import zipfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import archive_public_snapshots as snapshots
from release_baseline import baseline_rows


class BaselineTests(unittest.TestCase):
    def test_same_month_reads_frozen_archive_not_current_file(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "中文快照"
            root.mkdir()
            (root / "public-data").mkdir()
            name = "candidate-sources-2026-10.csv"
            payload = b"id,title\nold,original\n"
            (root / "public-data" / name).write_bytes(b"id,title\nnew,current\n")
            with zipfile.ZipFile(root / "baseline.zip", "w") as archive:
                archive.writestr(name, payload)
                archive.writestr("MANIFEST.csv", snapshots.manifest_bytes("2026-10-01", {name: payload}))
            config = {"EVIDENCE_ATLAS_BASELINE_MONTH": "2026-10", "EVIDENCE_ATLAS_BASELINE_ARCHIVE": "baseline.zip"}
            self.assertEqual(baseline_rows(root, config, "candidate_sources"), [{"id": "old", "title": "original"}])

    def test_corrupt_archive_fails_before_baseline_comparison(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            name = "candidate-sources-2026-10.csv"
            with zipfile.ZipFile(root / "baseline.zip", "w") as archive:
                archive.writestr(name, b"id\nchanged\n")
                archive.writestr("MANIFEST.csv", snapshots.manifest_bytes("2026-10-01", {name: b"id\nold\n"}))
            with self.assertRaises(RuntimeError):
                baseline_rows(root, {"EVIDENCE_ATLAS_BASELINE_MONTH": "2026-10", "EVIDENCE_ATLAS_BASELINE_ARCHIVE": "baseline.zip"}, "candidate_sources")


if __name__ == "__main__":
    unittest.main()
