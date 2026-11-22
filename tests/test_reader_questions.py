import csv
import re
import unittest
from pathlib import Path

from scripts import build_reader_questions as reader


class ReaderQuestions(unittest.TestCase):
    def test_home_shortcuts_and_generated_pages(self):
        data, _ = reader.load()
        questions = data["questions"]
        self.assertGreaterEqual(len(questions), 5)
        self.assertEqual(len({q["slug"] for q in questions}), len(questions))
        for path, body in reader.outputs().items():
            with self.subTest(path=path):
                self.assertEqual(path.read_text(encoding="utf-8"), body)
                if path in (reader.ROOT / "README.md", reader.ROOT / "README.zh-CN.md"):
                    body = body.split(reader.START)[1].split(reader.END)[0]
                for ref in re.findall(r"\]\(([^)]+)\)", body):
                    if not ref.startswith(("https:", "#")):
                        self.assertTrue((path.parent / ref).resolve().is_file(), ref)
        for home in (reader.ROOT / "README.md", reader.ROOT / "README.zh-CN.md", reader.DEST / "README.md"):
            body = home.read_text(encoding="utf-8")
            for q in questions:
                self.assertEqual(body.count(f'[{q["question"]}]('), 1, (home.name, q["slug"]))

    def test_first_screen_and_existing_sources(self):
        data, cards = reader.load()
        library = Path(reader.ROOT, "data/maintenance_2026_11_22/literature-library.csv")
        with library.open(encoding="utf-8-sig", newline="") as file:
            pmids = {row["pmid"] for row in csv.DictReader(file)}
        for q in data["questions"]:
            with self.subTest(question=q["slug"]):
                page = (reader.DEST / (q["slug"] + ".md")).read_text(encoding="utf-8")
                first, fold = page.split("<details>")
                self.assertTrue(first.startswith("# " + q["question"] + "\n\n" + q["answer"]))
                for label, key in reader.FIELDS:
                    self.assertIn(label, first)
                    self.assertIn(q[key], first)
                self.assertTrue(q["sources"])
                for src in q["sources"]:
                    self.assertIn(src["pmid"], pmids)
                    self.assertIn("https://pubmed.ncbi.nlm.nih.gov/" + src["pmid"] + "/", fold)
                self.assertIn(cards[q["card"]]["grade"] + " 级", fold)
                self.assertIn(q["english"], fold)
