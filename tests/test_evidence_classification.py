from __future__ import annotations

import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import apply_evidence_scoring_v04 as scoring  # noqa: E402
import expand_healthspan_pubmed_v05 as expansion  # noqa: E402


class StudyClassificationTests(unittest.TestCase):
    def test_article_ids_ignore_reference_list_identifiers(self) -> None:
        article = ET.fromstring(
            """
            <PubmedArticle>
              <MedlineCitation><PMID>42543470</PMID></MedlineCitation>
              <PubmedData>
                <ArticleIdList>
                  <ArticleId IdType="pubmed">42543470</ArticleId>
                  <ArticleId IdType="doi">10.1186/main-article</ArticleId>
                  <ArticleId IdType="pmc">PMC13429572</ArticleId>
                </ArticleIdList>
                <ReferenceList><Reference><ArticleIdList>
                  <ArticleId IdType="doi">10.1000/cited-reference</ArticleId>
                  <ArticleId IdType="pmc">PMC0000001</ArticleId>
                </ArticleIdList></Reference></ReferenceList>
              </PubmedData>
            </PubmedArticle>
            """
        )
        self.assertEqual(
            expansion.article_ids(article),
            {
                "pubmed": "42543470",
                "doi": "10.1186/main-article",
                "pmc": "PMC13429572",
            },
        )

    def test_protocol_is_not_promoted_to_completed_review(self) -> None:
        study_type = expansion.classify_study(
            ["Systematic Review"],
            "The planned review will synthesize randomized trials.",
            "PubMed",
            "Systematic review protocol for healthy aging",
        )
        self.assertEqual(study_type, "protocol_or_registered_plan")

    def test_reference_to_randomized_trial_does_not_promote_unknown_design(self) -> None:
        body = "Background: a randomized controlled trial previously reported improved biomarkers."
        study_type = expansion.classify_study([], body, "PubMed", "Aging biomarker associations")
        self.assertEqual(study_type, "metadata_only_needs_classification")

    def test_explicit_random_assignment_is_recognized(self) -> None:
        body = "Methods: participants were randomly assigned to intervention or control groups."
        study_type = expansion.classify_study([], body, "PubMed", "Effects of an exercise program")
        self.assertEqual(study_type, "human_randomized_or_clinical_trial")

    def test_randomized_goat_experiment_is_not_a_human_trial(self) -> None:
        title = "Lycopene supplementation in heat-stressed goat kids"
        body = "Twenty-one goat kids were randomly allocated into three experimental groups."
        study_type = expansion.classify_study(["Journal Article"], body, "PubMed", title)
        self.assertEqual(study_type, "animal_study")
        self.assertEqual(expansion.classify_species(study_type, body, title), "animal")
        row = {
            "title_en": title,
            "publication_types": "Journal Article",
            "result_en": body,
            "conclusion_en": "",
            "study_type_draft": "human_randomized_or_clinical_trial",
        }
        self.assertEqual(scoring.normalized_study_type(row), "animal_study")
        self.assertEqual(scoring.normalized_species(row, "animal_study"), "animal")

    def test_correction_about_a_trial_is_not_the_trial(self) -> None:
        title = "Correction: Effects of lifestyle modification: a randomized controlled trial."
        study_type = expansion.classify_study(["Published Erratum"], "", "PubMed", title)
        self.assertEqual(study_type, "non_primary_commentary_or_correction")
        self.assertEqual(expansion.classify_species(study_type, "", title), "needs_review")

    def test_editorial_calling_for_a_trial_is_non_primary(self) -> None:
        row = {
            "title_en": "The time is ripe for a randomized trial of metformin.",
            "publication_types": "Editorial",
            "result_en": "",
            "conclusion_en": "",
            "study_type_draft": "human_randomized_or_clinical_trial",
        }
        self.assertEqual(scoring.normalized_study_type(row), "non_primary_commentary_or_correction")
        self.assertEqual(scoring.normalized_species(row, "non_primary_commentary_or_correction"), "needs_review")
        self.assertEqual(scoring.confidence_cap(row, "longevity"), "E")

    def test_cohort_design_takes_priority_over_cited_trial_language(self) -> None:
        row = {
            "title_en": "Prospective cohort study of sleep and mortality",
            "publication_types": "Journal Article",
            "result_en": "A randomized controlled trial previously examined a related biomarker.",
            "conclusion_en": "",
            "study_type_draft": "",
        }
        self.assertEqual(scoring.normalized_study_type(row), "human_cohort")

    def test_narrative_review_citing_mendelian_randomization_stays_a_review(self) -> None:
        title = "Insomnia and cardiovascular disease: a narrative review"
        body = "Mendelian randomization studies support a possible causal association."
        self.assertEqual(
            expansion.classify_study(["Journal Article", "Review"], body, "PubMed", title),
            "narrative_review",
        )
        row = {
            "title_en": title,
            "publication_types": "Journal Article; Review",
            "result_en": body,
            "conclusion_en": "Randomized treatment trials remain limited.",
            "study_type_draft": "human_mendelian_randomization",
        }
        self.assertEqual(scoring.normalized_study_type(row), "narrative_review")

    def test_mixed_mendelian_and_mouse_experiment_is_capped_as_animal(self) -> None:
        title = "Aerobic exercise improves cognition in sepsis-associated encephalopathy"
        body = (
            "Two-sample Mendelian randomization was followed by animal experiments. "
            "SAE mice exhibited impaired glucose uptake."
        )
        self.assertEqual(
            expansion.classify_study(["Journal Article"], body, "PubMed", title),
            "animal_study",
        )
        row = {
            "title_en": title,
            "publication_types": "Journal Article",
            "result_en": body,
            "conclusion_en": "The mice showed improved cognition.",
            "study_type_draft": "human_mendelian_randomization",
        }
        self.assertEqual(scoring.normalized_study_type(row), "animal_study")
        self.assertEqual(scoring.confidence_cap(row, "longevity"), "D")

    def test_mixed_animal_and_clinical_cohort_is_not_labeled_animal_only(self) -> None:
        title = "Metformin response: preclinical animal and clinical cohort study"
        body = "Animal experiments were followed by analysis in patients who received radiotherapy."
        study_type = expansion.classify_study(["Journal Article"], body, "PubMed", title)
        self.assertEqual(study_type, "mixed_human_and_animal_study")
        self.assertEqual(expansion.classify_species(study_type, body, title), "mixed_human_animal")
        row = {
            "title_en": title,
            "publication_types": "Journal Article",
            "result_en": body,
            "conclusion_en": "Animal and patient results were reported.",
            "study_type_draft": "animal_study",
            "species_draft": "animal",
        }
        self.assertEqual(scoring.normalized_study_type(row), "mixed_human_and_animal_study")
        self.assertEqual(scoring.normalized_species(row, "mixed_human_and_animal_study"), "mixed_human_animal")
        self.assertEqual(scoring.confidence_cap(row, "longevity"), "D")

    def test_weight_loss_review_is_not_promoted_by_background_mortality_wording(self) -> None:
        row = {
            "title_en": "Semaglutide for weight reduction: a systematic review",
            "result_en": "Background: obesity contributes to mortality. Mean body weight decreased.",
            "conclusion_en": "Semaglutide reduced body weight but increased gastrointestinal adverse events.",
            "endpoint_class_draft": "H1",
        }
        self.assertEqual(scoring.normalized_healthspan_endpoint(row), "H3")

    def test_protocol_confidence_is_capped_at_e(self) -> None:
        row = {
            "title_en": "Trial protocol for a longevity intervention",
            "publication_types": "Journal Article",
            "study_type_draft": "systematic_review_or_meta_analysis",
        }
        self.assertEqual(scoring.normalized_study_type(row), "protocol_or_registered_plan")
        self.assertEqual(scoring.confidence_cap(row, "longevity"), "E")


if __name__ == "__main__":
    unittest.main()
