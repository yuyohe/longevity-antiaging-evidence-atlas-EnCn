from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import repair_pubmed_article_ids_2026_08 as repair  # noqa: E402


class PubMedIdentifierRepairTests(unittest.TestCase):
    def test_systolic_abbreviation_matches_without_merging_diastolic(self) -> None:
        self.assertEqual(repair.normalize_title("Long-term SBP time in target"),
                         repair.normalize_title("Long-term systolic blood pressure time in target"))
        self.assertNotEqual(repair.normalize_title("SBP control"), repair.normalize_title("DBP control"))

    def test_standard_medical_abbreviations_do_not_create_title_conflicts(self) -> None:
        expanded = (
            "Comorbid Insomnia is Associated with Enhanced Blood Pressure Reduction with CPAP Therapy "
            "in Patients with Obstructive Sleep Apnea: A Prospective Cohort Study."
        )
        abbreviated = (
            "Comorbid Insomnia Is Associated With Enhanced BP Reduction With CPAP Therapy "
            "in Patients With OSA: A Prospective Cohort Study."
        )
        self.assertEqual(repair.normalize_title(expanded), repair.normalize_title(abbreviated))


if __name__ == "__main__":
    unittest.main()
