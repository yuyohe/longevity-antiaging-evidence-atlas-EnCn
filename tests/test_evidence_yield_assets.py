from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_evidence_yield_assets_2026_05 as assets  # noqa: E402


class EvidenceYieldAssetTests(unittest.TestCase):
    def test_new_month_manifest_starts_from_empty(self) -> None:
        previous_data = assets.DATA
        previous_month = assets.UPDATE_MONTH
        previous_month_underscore = assets.UPDATE_MONTH_UNDERSCORE
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                assets.DATA = Path(temp_dir)
                assets.UPDATE_MONTH = "2099-01"
                assets.UPDATE_MONTH_UNDERSCORE = "2099_01"
                paths = {
                    "retraction": ROOT / "build" / "visual-assets" / "retraction.png",
                    "ingredient": ROOT / "build" / "visual-assets" / "ingredient.png",
                    "topic": ROOT / "build" / "visual-assets" / "topic.png",
                }
                assets.update_heatmap_manifest(paths)
                manifest = assets.DATA / "visual_heatmap_assets_2099_01.csv"
                with manifest.open(encoding="utf-8-sig", newline="") as handle:
                    rows = list(csv.DictReader(handle))
                self.assertEqual([row["asset_id"] for row in rows], ["H004", "H005", "H006"])
        finally:
            assets.DATA = previous_data
            assets.UPDATE_MONTH = previous_month
            assets.UPDATE_MONTH_UNDERSCORE = previous_month_underscore


if __name__ == "__main__":
    unittest.main()
