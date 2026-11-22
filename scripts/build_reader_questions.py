"""Render the public question pages and the two repository-home shortcuts."""
import argparse
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


def page(q, card, date):
    facts = "\n".join(f'- **{label}：** {q[key]}' for label, key in FIELDS)
    refs = "\n".join(
        f'- [{s["label"]} · PMID {s["pmid"]}](https://pubmed.ncbi.nlm.nih.gov/{s["pmid"]}/)'
        for s in q["sources"]
    )
    return f"""# {q["question"]}

{q["answer"]}

{facts}

<details>
<summary>研究数字、出处和成分卡评级 / Study details</summary>

{q["detail"]}

{refs}

[原成分卡：{card["name"]} · {card["grade"]} 级](../../cards/ingredients-2026-11/{card["id"]}.md) · [这个等级怎么评](../../../methodology/ingredient-card-grading-v1.md)。这是资料库给成分卡的评级，不是给这项试验打分。

**{q["question_en"]}** {q["english"]}

核对日期：{date}。

</details>

[返回：选一个想了解的问题](README.md)
"""


def outputs():
    data, cards = load()
    questions = data["questions"]
    out = {DEST / (q["slug"] + ".md"): page(q, cards[q["card"]], data["as_of"])
           for q in questions}
    out[DEST / "README.md"] = (
        "# 选一个想了解的问题 / Read by question\n\n"
        + menu(questions)
        + "\n\n每页先看参加研究的是谁、实际测到了什么、结论有多可靠。"
          "数字、论文和原成分卡在「研究数字、出处和成分卡评级」里。\n\n"
          "[看其他成分](../ingredient-cards-top-50.md) · [全部公开资料](../../../docs/full-library.md)"
        + f' · [在飞书看这五张卡（可能需登录）]({data["feishu_gallery_url"]})\n'
    )
    block = ("## 你想了解什么？ / Read by question\n\n"
             + menu(questions, "content/public-reader/questions/"))
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
