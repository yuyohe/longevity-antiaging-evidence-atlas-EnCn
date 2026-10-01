import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import expand_healthspan_pubmed_v05 as pubmed


class PubmedBatchingTests(unittest.TestCase):
    def test_summary_batches_cover_every_requested_id(self):
        ids = [str(i) for i in range(450)]
        sizes = []

        def response(endpoint, params):
            batch = params["id"].split(",")
            sizes.append(len(batch))
            return {"result": {pmid: {"uid": pmid} for pmid in batch}}

        with patch.object(pubmed, "request_json", side_effect=response), patch.object(pubmed.time, "sleep"):
            actual = pubmed.esummary(ids)
        self.assertEqual(sizes, [200, 200, 50])
        self.assertEqual(set(actual), set(ids))

    def test_missing_summary_fails_closed(self):
        with patch.object(pubmed, "request_json", return_value={"result": {}}):
            with self.assertRaises(RuntimeError):
                pubmed.esummary(["123"])

    def test_empty_input_does_not_query(self):
        with patch.object(pubmed, "request_json") as request:
            self.assertEqual(pubmed.esummary([]), {})
        request.assert_not_called()
