"""Render the public question pages and the two repository-home shortcuts."""
import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/reader_questions.json"
CARDS = ROOT / "data/maintenance_2026_11/ingredient_cards.json"
DEST = ROOT / "content/public-reader/questions"
START, END = "<!-- reader-questions:start -->", "<!-- reader-questions:end -->"
FIELDS = (("研究了谁", "who"), ("测到了什么", "measured"), ("有多大把握", "confidence"))


def load():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    cards = json.loads(CARDS.read_text(encoding="utf-8"))
    return data, {card["id"]: card for card in cards["cards"]}


def menu(questions, prefix=""):
    return "\n".join(f'- [{q["question"]}]({prefix}{q["slug"]}.md)' for q in questions)


def page(q, card, date, group, bibliography):
    facts = "\n".join(f'- **{label}：** {q[key]}' for label, key in FIELDS)
    refs = "\n".join(
        f'- [{s["label"]} · PMID {s["pmid"]}](https://pubmed.ncbi.nlm.nih.gov/{s["pmid"]}/)'
        for s in q["sources"]
    )
    notes = []
    for s in q["sources"]:
        meta = bibliography[s["pmid"]]
        for pmid in filter(None, meta["errata_pmids"].split(";")):
            notes.append(f'[期刊更正 · PMID {pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)')
        if meta["source_set"].startswith("reader supplement"):
            notes.append("本题补充核对的参考文献，未纳入原评分矩阵。")
    if card:
        notes.append(f'[原成分卡：{card["name"]} · {card["grade"]} 级](../../cards/ingredients-2026-11/{card["id"]}.md) · '
                     '[成分卡评级方法](../../../methodology/ingredient-card-grading-v1.md)')
    extra = "\n\n".join(notes)
    if extra:
        refs += "\n\n" + extra
    return f"""# {q["question"]}

{q["answer"]}

{facts}

<details>
<summary>研究数字和出处 / Study details</summary>

{q["detail"]}

{refs}

**{q["question_en"]}** {q["english"]}

核对日期：{date}。

</details>

[同类问题：{group["zh"]}](groups/{group["id"]}.md) · [全部 50 个问题](README.md)
"""


def outputs():
    data, cards = load()
    questions = data["questions"]
    groups = {g["id"]: g for g in data["groups"]}
    with (ROOT / "data/reader-question-sources.csv").open(encoding="utf-8", newline="") as handle:
        bibliography = {s["pmid"]: s for s in csv.DictReader(handle)}
    out = {DEST / (q["slug"] + ".md"): page(q, cards[q["card"]] if q.get("card") else None,
                                             data["as_of"], groups[q["group"]], bibliography)
           for q in questions}
    nav, all_links = [], []
    for gid, g in groups.items():
        items = [q for q in questions if q["group"] == gid]
        nav.append(f'- [{g["zh"]} · {len(items)} 题](groups/{gid}.md)：{g["examples"]}')
        all_links.append(f'### {g["zh"]}\n\n' + menu(items))
        out[DEST / "groups" / (gid + ".md")] = (f'# {g["zh"]} / {g["en"]}\n\n' + menu(items, "../")
              + f'\n\n[全部 50 个问题](../README.md) · [飞书分类画册（可能需登录）]({g["feishu"]})\n')
    out[DEST / "README.md"] = ("# 选一个想了解的问题 / Read by question\n\n"
        + "50 个问题，按你想改善的事来找。\n\n" + "\n".join(nav)
        + "\n\n<details>\n<summary>展开全部 50 个问题</summary>\n\n" + "\n\n".join(all_links)
        + "\n\n</details>\n\n[这些问题怎么选的](../../../docs/reader-question-selection.md)"
          " · [全部论文出处](../../../data/reader-question-sources.csv)"
        + f' · [飞书问题画册（可能需登录）]({data["feishu_gallery_url"]})\n')
    prefix = "content/public-reader/questions/"
    by_slug = {q["slug"]: q for q in questions}
    block = ("## 你想了解什么？ / Read by question\n\n"
             + f'**[按主题找：50 个健康问题]({prefix}README.md)**\n\n'
             + " · ".join(f'[{g["zh"]}]({prefix}groups/{g["id"]}.md)' for g in groups.values())
             + "\n\n" + menu([by_slug[s] for s in ("wrinkles","protein","coffee")], prefix))
    for name in ("README.md", "README.zh-CN.md"):
        path = ROOT / name
        old = path.read_text(encoding="utf-8")
        if old.count(START) != 1 or old.count(END) != 1:
            raise ValueError(f"Expected one marked navigation block in {name}")
        before, _, rest = old.partition(START)
        _, _, after = rest.partition(END)
        out[path] = before + START + "\n" + block + "\n" + END + after
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for path, body in outputs().items():
        if path.exists() and path.read_text(encoding="utf-8") == body:
            continue
        if args.check:
            stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8", newline="\n") as file:
                file.write(body)
    if stale:
        parser.exit(1, "Stale reader pages: " + ", ".join(stale) + "\n")


if __name__ == "__main__":
    main()
