import sys
import csv
import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from feishu_client import FeishuClient
from reader_annotations import EVIDENCE_GUIDE, NAVIGATION_HELP, VISUAL_NOTES, reader_legend_html
from sync_feishu_reader_annotations import HELP_PREFIX, description_text, help_update, stable_record_fields


class ReaderAnnotationTests(unittest.TestCase):
    def test_current_outputs_match_shared_notes(self):
        root = Path(__file__).resolve().parents[1]
        month = json.loads((root / "data/current_release.json").read_text(encoding="utf-8"))["EVIDENCE_ATLAS_ASSET_MONTH"]
        self.assertEqual((root / "content/public-reader/evidence-weight.md").read_text(encoding="utf-8").strip(), EVIDENCE_GUIDE.strip())
        with (root / f"data/feishu_reader_navigation_{month.replace('-', '_')}.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual([row["entry_id"] for row in rows], [f"R{i:03d}" for i in range(1, 15)])
        for row, notes in zip(rows, NAVIGATION_HELP):
            self.assertEqual(row["先看什么 / Start with"], notes[0])
            self.assertEqual(row["避免误读 / Do not infer"], notes[1])
        with (root / f"data/visual_heatmap_assets_{month.replace('-', '_')}.csv").open(encoding="utf-8-sig", newline="") as handle:
            visuals = list(csv.DictReader(handle))
        self.assertEqual(len(visuals), 7)
        for row in visuals:
            key = Path(row["local_path"]).name.removesuffix(f"-{month}.png")
            self.assertEqual(row["description"], VISUAL_NOTES[key])

    def test_fourteen_entries_and_seven_visuals(self):
        self.assertEqual(len(NAVIGATION_HELP), 14)
        self.assertEqual(len(VISUAL_NOTES), 7)
        self.assertTrue(all(len(note) <= 180 for note in VISUAL_NOTES.values()))
        self.assertTrue(all(a and b for a, b in NAVIGATION_HELP))

    def test_guide_separates_codes_and_review(self):
        for code in ("H1", "H2", "H3", "H4", "H5", "H6", "not_assessed", "PMCID", "标准 GRADE", "1/2 = 50%"):
            self.assertIn(code, EVIDENCE_GUIDE)
        self.assertIn("五张表", reader_legend_html())

    def test_help_is_idempotent_and_preserves_existing_notes(self):
        self.assertIsNone(help_update({"description": {"text": "用户原有说明"}}, "新说明"))
        self.assertIsNone(help_update({"description": {"text": HELP_PREFIX + "说明"}}, "说明"))
        self.assertEqual(help_update({"description": None}, "说明"), HELP_PREFIX + "说明")
        self.assertIsNone(help_update({"description": HELP_PREFIX + "说明"}, "说明"))
        self.assertIsNone(help_update({"description": "用户原有说明"}, "新说明"))
        self.assertEqual(description_text({"description": "text"}), "text")

    @patch("feishu_client.requests.put")
    def test_field_help_preserves_schema(self, put):
        put.return_value = Mock(status_code=200)
        put.return_value.json.return_value = {"code": 0, "data": {}}
        client = FeishuClient("test-id", "test-secret")
        client._headers = Mock(return_value={})
        field = {"field_id": "field1", "field_name": "grade", "type": 1,
                 "property": {}, "is_hidden": True, "ui_type": "Text",
                 "description": {"disable_sync": True, "text": "old"}}
        client.update_bitable_field_description("app", "table", field, "new")
        body = put.call_args.kwargs["json"]
        for name in ("field_name", "type", "property", "is_hidden", "ui_type"):
            self.assertEqual(body[name], field[name])
        self.assertEqual(body["description"], {"disable_sync": True, "text": "new"})
        self.assertEqual(field["description"]["text"], "old")

    def test_unsupported_field_type_is_rejected(self):
        client = FeishuClient("test-id", "test-secret")
        with self.assertRaises(ValueError):
            client.update_bitable_field_description("app", "table", {"type": 20}, "help")

    def test_attachment_comparison_ignores_only_transient_urls(self):
        before = {"图片": [{"file_token": "same", "name": "image.png", "size": 10, "tmp_url": "old"}], "说明": "note"}
        after = {"图片": [{"file_token": "same", "name": "image.png", "size": 10, "tmp_url": "new"}], "说明": "note"}
        self.assertEqual(stable_record_fields(before), stable_record_fields(after))
        after["图片"][0]["file_token"] = "changed"
        self.assertNotEqual(stable_record_fields(before), stable_record_fields(after))


if __name__ == "__main__":
    unittest.main()
