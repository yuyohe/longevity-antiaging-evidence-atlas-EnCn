import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/maintenance_2026_11_22"


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


class LateNovember(unittest.TestCase):
    def test_intake_preserves_every_prior_record(self):
        prior = rows(ROOT / "data/maintenance_2026_11/literature_library_merged.csv")
        current = rows(DATA / "literature-library.csv")
        new = rows(DATA / "new-candidates.csv")
        by_id = {r["library_id"]:r for r in current}
        self.assertEqual(len(current), len(by_id))
        for r in prior:
            expected = dict(r)
            if r["pmid"] in {"42848371","42454954"}:
                expected["last_checked"] = "2026-11-22"
            self.assertEqual(by_id[r["library_id"]],expected)
        self.assertEqual(set(by_id)-{r["library_id"] for r in prior},{r["id"] for r in new})
        for r in new:
            self.assertEqual(by_id[r["id"]]["in_evidence_matrix"], "false")
        for key in ("pmid","doi"):
            values = [r[key].lower() for r in current if r[key]]
            self.assertEqual(len(values),len(set(values)))

    def test_reported_counts_reconcile(self):
        stats = json.loads((DATA / "summary.json").read_text(encoding="utf-8"))
        hits = rows(DATA / "retrieval.csv")
        log = json.loads((DATA / "search.json").read_text(encoding="utf-8"))
        self.assertEqual({r["pmid"] for r in hits},{p for q in log.values() for p in q["pmids"]})
        self.assertEqual(len(hits),stats["unique_sampled_pmids"])
        self.assertEqual(sum(q["count"]>q["cap"] for q in log.values()),stats["capped_topic_queries"])
        self.assertNotIn("abstract",hits[0])
        self.assertEqual(stats["current"],stats["baseline"]+stats["new_candidates"])

    def test_retraction_originals_not_notices(self):
        rates = rows(DATA / "retraction-density.csv")
        cases = rows(DATA / "new-retraction-matches.csv")
        pmids = {p for r in rates for p in r["pmids"].split(";") if p}
        oldfile = ROOT / "data/retraction_risk_queries_20y.csv"
        old = {p for r in rows(oldfile) for p in r["retrieved_pmids"].split(";") if p}
        self.assertEqual(pmids-old, {r["pmid"] for r in cases})
        self.assertTrue(all(r["pmid"]!=r["notice_pmid"] for r in cases))
        for r in rates:
            self.assertAlmostEqual(float(r["per_1000"]),1000*int(r["retracted"])/int(r["denominator"]),places=2)
