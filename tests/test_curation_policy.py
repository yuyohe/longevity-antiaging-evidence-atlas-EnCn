from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import curate_mid_august_2026 as curation  # noqa: E402


class CurationPolicyTests(unittest.TestCase):
    def test_topic_concept_guard_rejects_mismatched_record(self) -> None:
        row = {
            "candidate_id": "pubmed-1",
            "topic_id": "epigenetic-clocks",
            "title_en": "Rabies post-exposure prophylaxis in travelers",
            "result_en": "A retrospective travel-clinic analysis.",
            "conclusion_en": "Follow-up was complete.",
            "study_type_draft": "human_cohort",
            "species_draft": "human",
            "review_status": "public_draft_not_fully_reviewed",
        }
        self.assertEqual(curation.finding_rejection_reason(row), "title_topic_signal_missing")

    def test_protocol_is_retired_from_active_findings(self) -> None:
        row = {
            "candidate_id": "pubmed-2",
            "topic_id": "time-restricted-eating",
            "title_en": "Protocol for a time-restricted eating trial",
            "result_en": "",
            "conclusion_en": "",
            "study_type_draft": "protocol_or_registered_plan",
            "species_draft": "human",
            "review_status": "public_draft_not_fully_reviewed",
        }
        self.assertEqual(curation.finding_rejection_reason(row), "protocol_or_registered_plan")

    def test_nonhuman_record_is_not_kept_in_human_outcome_topic(self) -> None:
        row = {
            "candidate_id": "pubmed-3",
            "topic_id": "blood-pressure-aging",
            "title_en": "Blood pressure intervention in mice",
            "result_en": "The mice had lower systolic blood pressure.",
            "conclusion_en": "",
            "study_type_draft": "animal_study",
            "species_draft": "mouse",
            "review_status": "public_draft_not_fully_reviewed",
        }
        self.assertEqual(
            curation.finding_rejection_reason(row),
            "nonhuman_record_in_human_outcome_topic",
        )

    def test_pubmed_duplicate_is_preferred_over_crossref(self) -> None:
        rows = [
            {
                "id": "crossref-1",
                "title_en": "Sleep duration and mortality in older adults",
                "doi": "10.1000/example",
                "pmid": "",
                "source": "Crossref",
            },
            {
                "id": "pubmed-1",
                "title_en": "Sleep duration and mortality in older adults",
                "doi": "10.1000/example",
                "pmid": "123",
                "source": "PubMed",
            },
        ]
        kept, retired = curation.dedupe_candidates(rows, set(), "2026-08-09")
        self.assertEqual([row["id"] for row in kept], ["pubmed-1"])
        self.assertEqual(retired[0]["duplicate_of"], "pubmed-1")

    def test_per_topic_finding_cap_is_enforced(self) -> None:
        rows = []
        for index in range(4):
            rows.append(
                {
                    "finding_id": f"finding-pubmed-{index}",
                    "candidate_id": f"pubmed-{index}",
                    "pmid": str(100 + index),
                    "topic_id": "sleep-aging",
                    "title_en": f"Sleep duration and mortality cohort {index}",
                    "result_en": "Sleep duration was associated with mortality.",
                    "conclusion_en": "",
                    "study_type_draft": "human_cohort",
                    "species_draft": "human",
                    "endpoint_class_draft": "H1",
                    "evidence_level_draft": "B",
                    "review_status": "public_draft_not_fully_reviewed",
                    "year": "2026",
                }
            )
        selected, retired, counts = curation.curate_findings(
            rows,
            {row["candidate_id"] for row in rows},
            set(),
            per_topic_cap=2,
            run_date="2026-08-09",
        )
        self.assertEqual(len(selected), 2)
        self.assertEqual(len(retired), 2)
        self.assertEqual(counts["sleep-aging"], 2)
        self.assertTrue(all(row["reason"] == "topic_capacity_limit" for row in retired))


if __name__ == "__main__":
    unittest.main()
