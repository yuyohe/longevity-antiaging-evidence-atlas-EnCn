import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from archive_reader_history import history_plan, rewrite_html, rewrite_markdown, rewrite_target, verify_manifest
from build_reader_home import load_registry, ordered_registry


class ReaderLayoutTests(unittest.TestCase):
    def test_layout_preserves_all_current_assets(self):
        root = Path(__file__).resolve().parents[1]
        layout = json.loads((root / "data/reader_layout.json").read_text(encoding="utf-8"))
        before = load_registry()
        after = ordered_registry(before, layout)
        self.assertEqual({r["table_id"] for r in before}, {r["table_id"] for r in after})
        self.assertEqual([r["asset_key"] for r in after[:4]], ["reader_navigation", "heatmaps", "ingredient_cards", "ingredient_wall"])
        self.assertEqual(len(after), 9)
        self.assertTrue(all("2026-" not in r["stable_name"] for r in after))

    def test_bad_layout_is_rejected(self):
        with self.assertRaises(ValueError):
            ordered_registry([{"asset_key": "x"}], {"asset_order": []})

    def test_reader_history_manifest_matches_archived_files(self):
        self.assertGreater(verify_manifest(Path(__file__).resolve().parents[1]), 0)

    def test_relative_link_to_moved_file(self):
        moves = {"docs/old.md": "archive/reader-history/docs/old.md"}
        self.assertEqual(rewrite_target("old.md#section", "docs/current.md", "docs/current.md", moves), "../archive/reader-history/docs/old.md#section")

    def test_links_inside_moved_document(self):
        self.assertEqual(rewrite_target("../README.md", "docs/old.md", "archive/reader-history/docs/old.md", {}), "../../../README.md")

    def test_external_and_fragment_links_unchanged(self):
        for url in ["https://pubmed.ncbi.nlm.nih.gov/123/", "#part", "mailto:test@example.org", "data:image/png;base64,abc"]:
            self.assertEqual(rewrite_target(url, "docs/a.md", "archive/a.md", {}), url)

    def test_markdown_keeps_labels_and_images(self):
        moves = {"docs/old.md": "archive/old.md"}
        self.assertEqual(rewrite_markdown("[说明](old.md)", "docs/a.md", "docs/a.md", moves), "[说明](../archive/old.md)")
        self.assertEqual(rewrite_markdown("![图](image.png)", "docs/a.md", "archive/a.md", {}), "![图](../docs/image.png)")

    def test_html_repairs_only_real_link_attributes(self):
        text = '<!doctype html><a href="old.md?x=1&amp;y=2">说明</a><script>const value="old.md";</script>'
        result = rewrite_html(text, "docs/current.html", "docs/current.html", {"docs/old.md": "archive/old.md"})
        self.assertEqual(result, '<!doctype html><a href="../archive/old.md?x=1&amp;y=2">说明</a><script>const value="old.md";</script>')

    def test_archive_keeps_current_release_and_unversioned_guides(self):
        cfg = {"EVIDENCE_ATLAS_ASSET_MONTH": "2026-10", "EVIDENCE_ATLAS_UPDATE_DATE": "2026-10-10", "EVIDENCE_ATLAS_PUBLIC_REPORT_FILE": "current-2026-10.html", "EVIDENCE_ATLAS_RELEASE_FILE": "current-2026-10.md"}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            (root / "content/public-reader").mkdir(parents=True)
            for name in ["old-2026-06.html", "current-2026-10.html", "report-2026-10-10.md", "asset-catalog.md"]:
                (root / "docs" / name).touch()
            plan = history_plan(cfg, root)
            self.assertEqual(list(plan), ["docs/old-2026-06.html"])


if __name__ == "__main__":
    unittest.main()
