import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import archive_legacy_visuals as archives


class VisualArchiveTests(unittest.TestCase):
    def make_archive(self, directory, payload, checksum=None, extra=False):
        path = Path(directory) / "test.zip"
        manifest = {"files": [{"path": "docs/old.html", "bytes": len(payload),
                                "sha256": checksum or archives.digest(payload)}]}
        with zipfile.ZipFile(path, "w") as output:
            output.writestr("docs/old.html", payload)
            output.writestr("MANIFEST.json", json.dumps(manifest))
            if extra:
                output.writestr("unexpected.txt", "unexpected")
        return path

    def test_original_bytes_survive(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.make_archive(directory, b"original bytes")
            self.assertEqual(len(archives.verify_archive(path)["files"]), 1)

    def test_changed_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.make_archive(directory, b"changed", checksum="0" * 64)
            with self.assertRaises(RuntimeError):
                archives.verify_archive(path)

    def test_extra_members_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.make_archive(directory, b"original", extra=True)
            with self.assertRaises(RuntimeError):
                archives.verify_archive(path)
