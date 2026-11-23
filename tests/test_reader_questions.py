import csv
import re
import unittest
from pathlib import Path

from scripts import build_reader_questions as reader


class ReaderQuestions(unittest.TestCase):
    def test_website_links_match_each_question_and_group(self):
        data, _ = reader.load()
        pages = reader.outputs()
        for q in data["questions"]:
            md = pages[reader.DEST / (q["slug"] + ".md")]
            self.assertEqual(re.findall(r'\]\((https://yulcell\.cn/evidence/[^)]*)\)', md),
                             [reader.SITE + q["slug"] + "/"])
            self.assertIn(reader.CREDIT, md)
        for g in data["groups"]:
            self.assertIn(f'({reader.SITE}#yc-{g["id"]})', pages[reader.DEST / "groups" / (g["id"] + ".md")])
        for home in (reader.ROOT / "README.md", reader.ROOT / "README.zh-CN.md", reader.DEST / "README.md"):
            self.assertIn(f"({reader.SITE})", pages[home])

    def test_home_shortcuts_and_generated_pages(self):
        data, _ = reader.load()
        questions = data["questions"]
        self.assertEqual(len(questions), 50)
        self.assertEqual(len({q["question"] for q in questions}), 50)
        self.assertEqual(len({q["slug"] for q in questions}), len(questions))
        self.assertTrue({"wrinkles", "cholesterol", "strength", "memory", "fractures"} <= {q["slug"] for q in questions})
        for path, body in reader.outputs().items():
            with self.subTest(path=path):
                self.assertEqual(path.read_text(encoding="utf-8"), body)
                if path in (reader.ROOT / "README.md", reader.ROOT / "README.zh-CN.md"):
                    body = body.split(reader.START)[1].split(reader.END)[0]
                for ref in re.findall(r"\]\(([^)]+)\)", body):
                    if not ref.startswith(("https:", "#")):
                        self.assertTrue((path.parent / ref).resolve().is_file(), ref)
        hub = (reader.DEST / "README.md").read_text(encoding="utf-8")
        for q in questions:
            self.assertEqual(hub.count(f'[{q["question"]}]('), 1)
        for g in data["groups"]:
            link = "groups/" + g["id"] + ".md"
            for home in (reader.ROOT / "README.md", reader.ROOT / "README.zh-CN.md", reader.DEST / "README.md"):
                self.assertIn(link + ")", home.read_text(encoding="utf-8"))

    def test_topic_membership(self):
        data, _ = reader.load()
        groups = {g["id"]: g for g in data["groups"]}
        self.assertEqual(len(groups), 6)
        self.assertEqual(len({g["feishu"] for g in groups.values()}), 6)
        self.assertEqual({q["group"] for q in data["questions"]}, set(groups))
        for gid in groups:
            page = (reader.DEST / "groups" / (gid + ".md")).read_text(encoding="utf-8")
            listed = re.findall(r"\]\(\.\./([\w-]+)\.md\)", page)
            self.assertEqual([x for x in listed if x != "README"],
                             [q["slug"] for q in data["questions"] if q["group"] == gid])

    def test_first_screen_and_existing_sources(self):
        data, cards = reader.load()
        library = Path(reader.ROOT, "data/maintenance_2026_11_22/literature-library.csv")
        with library.open(encoding="utf-8-sig", newline="") as file:
            pmids = {row["pmid"] for row in csv.DictReader(file)}
        with (reader.ROOT / "data/reader-question-sources.csv").open(encoding="utf-8", newline="") as file:
            sources = {row["pmid"]: row for row in csv.DictReader(file)}
        self.assertEqual({s["pmid"] for q in data["questions"] for s in q["sources"]}, sources.keys())
        self.assertEqual(len(sources), 51)
        self.assertEqual({k for k, s in sources.items() if s["source_set"].startswith("reader supplement")},
                         sources.keys() - pmids)
        self.assertEqual(len(sources.keys() - pmids), 4)
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
                    self.assertIn(src["pmid"], sources)
                    self.assertIn("https://pubmed.ncbi.nlm.nih.gov/" + src["pmid"] + "/", fold)
                    for pid in filter(None, sources[src["pmid"]]["errata_pmids"].split(";")):
                        self.assertIn(f"https://pubmed.ncbi.nlm.nih.gov/{pid}/", fold)
                if q.get("card"):
                    self.assertIn(cards[q["card"]]["grade"] + " 级", fold)
                else:
                    self.assertNotIn("成分卡评级", fold)
                self.assertIn(q["english"], fold)
