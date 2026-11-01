"""Focused contracts for the scoped November editorial release."""
import csv
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_november_cards as builder


class NovemberCardsTest(unittest.TestCase):
    def test_card_set_is_complete_and_claim_scoped(self):
        cards = json.loads((ROOT / 'data/maintenance_2026_11/ingredient_cards.json').read_text(encoding='utf-8'))['cards']
        self.assertEqual({c['id'] for c in cards}, {f'NOV26-{r}{i:02}' for r in ('T', 'O') for i in range(1, 11)})
        self.assertEqual(sum(c['route'] == 'topical' for c in cards), 10)
        self.assertEqual(sum(c['route'] == 'oral' for c in cards), 10)
        for card in cards:
            for key in ('conclusion', 'recommendation', 'expected_effect', 'grade_reason', 'risks', 'population', 'formulation', 'endpoint'):
                self.assertTrue(card[key], (card['id'], key))
            self.assertIn(card['grade'], {'B', 'C', 'D'})

    def test_new_intake_does_not_rewrite_existing_decisions(self):
        old = [{'id': 'pubmed-1', 'title_en': 'Old', 'include_status': 'excluded_manually', 'last_checked': '2026-10-30'}]
        metadata = [{'pmid': '1', 'title_en': 'Changed', 'year': '2026', 'doi': '10.1/a', 'url': 'https://example.test/a'},
                    {'pmid': '2', 'title_en': 'New', 'year': '2026', 'doi': '10.1/b', 'url': 'https://example.test/b'}]
        raw = builder.csv_bytes(old, list(old[0]))
        merged, _ = builder.load_rows(builder.candidate_merge(raw, metadata, 'data/candidate_sources.csv'))
        self.assertEqual(merged[0], old[0])
        self.assertEqual(merged[1]['id'], 'pubmed-2')
        self.assertEqual(len(builder.load_rows(builder.candidate_merge(builder.csv_bytes(merged, list(old[0])), metadata, 'data/candidate_sources.csv'))[0]), 2)

    def test_intake_keeps_legacy_snapshot_separate(self):
        with (ROOT / 'data/candidate_sources.csv').open(encoding='utf-8-sig') as stream:
            base = list(csv.DictReader(stream))
        with (ROOT / 'data/maintenance_2026_11/candidate_sources_merged.csv').open(encoding='utf-8-sig') as stream:
            merged = list(csv.DictReader(stream))
        by_id = {r['id']: r for r in merged}
        base_ids = {r['id'] for r in base}
        self.assertTrue(base_ids <= set(by_id))
        self.assertEqual(len(by_id), len(merged))
        for row in base:
            self.assertEqual(by_id[row['id']], row)
        self.assertTrue(all(r['include_status'] in ('candidate_metadata_pending_full_appraisal', 'retracted_excluded') for r in merged if r['id'] not in base_ids))


if __name__ == '__main__':
    unittest.main()
