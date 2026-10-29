"""Build the reader-first entry pages without changing scientific records."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_registry() -> list[dict[str, str]]:
    with (ROOT / "data/feishu_table_registry.csv").open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def ordered_registry(rows: list[dict[str, str]], layout: dict) -> list[dict[str, str]]:
    by_key = {row["asset_key"]: row for row in rows}
    if set(by_key) != set(layout["asset_order"]) or len(rows) != len(by_key):
        raise ValueError("Reader layout must preserve every unique current asset")
    return [{**by_key[key], "stable_name": layout["table_names"][key]} for key in layout["asset_order"]]


def write_catalog(rows: list[dict[str, str]], cfg: dict, layout: dict) -> None:
    by_key = {row["asset_key"]: row for row in rows}
    meanings = {
        "reader_navigation": "项目是什么、看图入口和阅读说明 / Introduction and navigation",
        "heatmaps": "6张研究图；看研究分布与统计口径 / Six research charts",
        "ingredient_cards": "查50种成分的用途、暂定评级、误解与注意 / Fifty context-specific cards",
        "ingredient_wall": "把50张卡放在一起作索引，不是购买排行 / Visual index, not a ranking",
        "evidence_matrix": "在同一张表中比较研究 / Compare selected studies",
        "evidence_findings": "根据摘要等整理的研究笔记，全文待复核 / Draft notes, full-text review pending",
        "literature_library": "用题名、PMID、DOI追查论文 / Trace original publications",
        "candidate_sources": "保留检索词、抓取来源等技术记录 / Raw search provenance",
        "shortlist_sources": "优先检查哪些记录，不表示已经验证 / Review priorities, not approvals",
    }
    sections = []
    for title, keys in [
        ("先看介绍和图 / Introduction and Visuals", layout["asset_order"][:4]),
        ("查证据 / Evidence", ["evidence_matrix", "evidence_findings"]),
        ("找原文 / Sources", ["literature_library", "candidate_sources", "shortlist_sources"]),
    ]:
        lines = [f"## {title}", "", "| 内容 / Content | 打开后能看到什么 / Meaning | 记录数 / Rows |", "| --- | --- | ---: |"]
        lines += [f"| [{by_key[key]['stable_name']}]({by_key[key]['url']}) | {meanings[key]} | {int(by_key[key]['expected_rows']):,} |" for key in keys]
        sections.append("\n".join(lines))
    month = cfg["EVIDENCE_ATLAS_ASSET_MONTH"]
    text = f"""# 宇多Yul细胞/yulcell：当前内容目录 / Current Reader Catalog

这是运动、睡眠、饮食、补剂和抗衰研究的证据图谱。第一次来先看图，关心某个说法再查证据，需要核对时再找论文。

[项目介绍与图片](../README.md) · [读表说明](../content/public-reader/evidence-weight.md)

Evidence snapshot / 资料快照：{cfg['EVIDENCE_ATLAS_UPDATE_DATE']}。Organization / 分类整理：{layout['organized_on']}。

{chr(10).join(sections)}

文献目录、研究笔记和证据对照表的入口已指向简洁阅读视图，完整字段仍在原视图。`title_en/title_zh`是英文/中文题名，`conclusion_zh/zh_summary`是中文结论/摘要，`year`是发表年份，`PMID`是PubMed文献编号。中文题名留空表示尚未补写翻译。

The three reading views hide maintenance columns without removing data. Empty Chinese titles mean a translation has not yet been added.

五张资料表属于不同处理层，同一论文可能重复出现。总行数不能当成独立论文数；入选与草稿等级也不代表功效已经确认。

The five data layers overlap. Candidate inclusion and draft grades do not establish efficacy.

## GitHub 图片与文件 / Images and Files

- [本期图片](assets/visual-assets/{month}/)：7张主图和50张成分卡。
- [公开数据](../public-data/README.md)：需要分析或复核时再下载。
- [离线图文报告]({cfg['EVIDENCE_ATLAS_PUBLIC_REPORT_FILE']})：图片已内嵌，本地打开即可。
- [助理发帖面板](yulcell-posting-asset-dashboard-{cfg['EVIDENCE_ATLAS_UPDATE_DATE']}.html)：生成、下载图片。

## 历史与维护 / History and Maintenance

旧月份只放在[历史资料](../archive/README.md)，飞书侧栏归入“90 历史资料（旧月份）”。旧链接和独有资料保留，不与当前入口混排。核验记录见[当前状态](current-output-status.md)。

{layout['continuation_policy']}

若未登录时看不到当前表，请先用GitHub入口；本次整理不扩大分享或编辑权限。Old month tables are historical snapshots. This reorganization does not change access permissions.
"""
    (ROOT / "docs/asset-catalog.md").write_text(text, encoding="utf-8")
    (ROOT / f"docs/feishu-public-assets-{month}.md").write_text(text.replace("当前内容目录 / Current Reader Catalog", "飞书阅读目录 / Feishu Reader Catalog"), encoding="utf-8")


def main() -> None:
    cfg = json.loads((ROOT / "data/current_release.json").read_text(encoding="utf-8"))
    layout = json.loads((ROOT / "data/reader_layout.json").read_text(encoding="utf-8"))
    month = cfg["EVIDENCE_ATLAS_ASSET_MONTH"]
    snapshot = cfg["EVIDENCE_ATLAS_UPDATE_DATE"]
    rows = ordered_registry(load_registry(), layout)
    with (ROOT / "data/feishu_table_registry.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    by_key = {row["asset_key"]: row for row in rows}
    images = f"docs/assets/visual-assets/{month}"
    cards = sorted((ROOT / images / "ingredient-cards").glob("*.png"))
    if len(cards) != 50:
        raise RuntimeError("Expected fifty existing ingredient cards")
    examples = [path.relative_to(ROOT).as_posix() for path in cards[:2]]
    introduction = "这里整理运动、睡眠、饮食、补剂和抗衰技术的研究，帮你看清研究了谁、测了什么、结论能支持到哪一步。动物实验、化验指标和人体疾病结局分开呈现。"
    english = "An evidence guide to exercise, sleep, nutrition, supplements and aging research: who was studied, what was measured, and what the findings support. Animal experiments, biomarkers and human outcomes are kept separate."
    readme = f"""# 宇多Yul细胞/yulcell
## 长寿抗衰与健康寿命证据图谱 / Longevity & Healthspan Evidence Atlas

{introduction}

{english}

资料快照 / Evidence snapshot：{snapshot} · 分类整理 / Organization：{layout['organized_on']}

[本期六篇研究解读 / Six studies in this update](content/public-reader/{cfg['EVIDENCE_ATLAS_RELEASE_FILE']}) · [飞书阅读导航 / Feishu start here]({by_key['reader_navigation']['url']})

| 你想做什么 / Your question | 从哪里看 / Open |
| --- | --- |
| 先看图，了解有哪些研究 / See the research | [热力图](#一先看图--visuals) · [成分卡片](content/public-reader/ingredient-cards-top-50.md) |
| 查某个说法有多少支持 / Check a claim | [主题解读](content/public-reader/topics.md) · [补剂速查](content/public-reader/supplements-top-30.md) |
| 找到论文原文 / Trace a source | [文献来源与数据说明](public-data/README.md) |

## 一、先看图 / Visuals

### 研究热力图 / Research Heatmap

看当前收录的研究分布。颜色深表示记录多，不表示效果更好；0 表示当前集合没有记录，不代表没有相关研究。

Counts in the selected matrix, not an efficacy ranking.

![研究热力图]({images}/heatmap-dashboard-{month}.png)

[图例与统计范围](content/public-reader/research-heatmap.md) · [飞书看图]({by_key['heatmaps']['url']})

### 成分卡片 / Ingredient Cards

每张卡分别写健康寿命、皮肤用途、常见误解和注意事项。先看适用场景与限制，再看暂定等级。

Each card distinguishes healthspan and skin contexts and includes limitations.

<a href="{examples[0]}"><img src="{examples[0]}" width="350" alt="成分卡片示例一"></a>
<a href="{examples[1]}"><img src="{examples[1]}" width="350" alt="成分卡片示例二"></a>

[查看全部50张卡](content/public-reader/ingredient-cards-top-50.md) · [一张图看50种成分]({images}/ingredient-card-wall-{month}.png) · [飞书查成分]({by_key['ingredient_cards']['url']})

## 二、查证据 / Evidence

| 想了解 / Topic | 阅读入口 / Open |
| --- | --- |
| 运动、睡眠、饮食和代谢 | [大众主题速读](content/public-reader/topics.md) |
| NMN、鱼油、胶原蛋白等补剂 | [常见补剂](content/public-reader/supplements-top-30.md) |
| 防晒、皱纹、屏障和医美 | [皮肤与外观](content/public-reader/skin.md) |
| A/B、H1至H6、全文待复核是什么意思 | [读表与缩写说明](content/public-reader/evidence-weight.md) |
| 比较不同研究 | [飞书证据对照表]({by_key['evidence_matrix']['url']}) |

等级是项目草稿排序，研究笔记仍可能等待全文复核。图片制作日期不代表评级重新确认；不能据此自行用药、停药或购买补剂。

Grades and notes are provisional. New images do not imply revalidated evidence. This atlas does not provide personal medical or purchase advice.

## 三、找原文 / Sources

[文献来源目录]({by_key['literature_library']['url']}) · [公开数据与字段说明](public-data/README.md) · [全部当前入口](docs/asset-catalog.md)

五张数据表是不同处理层，同一论文可能重复出现，总行数不是独立论文数。查具体文献时用 PMID 或 DOI。

The five data layers overlap. Use PMID or DOI to trace individual papers.

<details>
<summary>更新记录、历史资料与维护 / Updates, Archives and Maintenance</summary>

- [最近一次文献更新](content/public-reader/{cfg['EVIDENCE_ATLAS_RELEASE_FILE']})
- [历史版本统一入口](archive/README.md)
- [维护与分表规则](docs/data-retention-and-curation-policy.md)
- [核验状态](docs/current-output-status.md)
- [中文说明](README.zh-CN.md) · [更新日志](CHANGELOG.md)

GitHub保存版本；飞书用于看图、筛选和复核。HTML报告可下载后离线打开，图片已内嵌，不需要本地网站。

GitHub preserves versions; Feishu supports browsing and review. Downloaded HTML reports work offline without a server.

</details>
"""
    (ROOT / "README.md").write_text(readme, encoding="utf-8")
    chinese = f"""# 宇多Yul细胞/yulcell：怎么阅读这个项目

{introduction}

## 从哪里开始 / Where to Start

1. [看热力图](content/public-reader/research-heatmap.md)：了解当前研究分布。
2. [查成分卡](content/public-reader/ingredient-cards-top-50.md)：先看用途、误解和限制。
3. [按主题读证据](content/public-reader/topics.md)：再查运动、睡眠、饮食等问题。
4. [找论文来源](public-data/README.md)：需要核对原文时再进入资料层。

[项目首页](README.md)直接展示热力图和两张真实成分卡。[全部当前入口](docs/asset-catalog.md)按看图、查证据、找原文分类；旧月份统一放在[历史资料](archive/README.md)。

## 读之前记住 / Reading Limits

- A/B 是项目草稿排序，不表示人人有效或值得购买。
- “研究笔记”“优先复核”不代表已完成全文检查。
- 颜色深表示记录多；成分图的两个用途场景不是论文有效率。
- 五层数据会重复收录同一论文，不能把行数当作独立论文总数。
- 新图不等于评级重新确认。[完整读表说明](content/public-reader/evidence-weight.md)。

资料快照：{snapshot}。分类整理：{layout['organized_on']}。[本期更新内容](content/public-reader/{cfg['EVIDENCE_ATLAS_RELEASE_FILE']})。

English: start with the [bilingual homepage](README.md). Current evidence, source material and historical releases have separate entry points.
"""
    (ROOT / "README.zh-CN.md").write_text(chinese, encoding="utf-8")
    start = f"""# 从这里开始：这是什么？ / Start Here

**宇多Yul细胞/yulcell · 长寿抗衰与健康寿命证据图谱**

{introduction}

{english}

## 选一个入口 / Choose an Entry

| 你现在想看什么 | 打开 | 能看到什么 |
| --- | --- | --- |
| 我先看看这是什么 | [项目首页](../../README.md) | 热力图、成分卡和简单说明 |
| 我想看整个研究分布 | [研究热力图](research-heatmap.md) | 当前矩阵的主题、年份和草稿等级 |
| 我想查一种成分 | [50种成分卡](ingredient-cards-top-50.md) | 健康寿命、皮肤用途、误解与注意 |
| 我关心运动、睡眠或饮食 | [主题速读](topics.md) | 研究对象、发现和不能外推的结论 |
| 我关心补剂 | [常见30种补剂](supplements-top-30.md) | 暂定证据和安全边界 |
| 我看不懂缩写和数字 | [读表说明](evidence-weight.md) | A/B、H1至H6、草稿状态与百分比 |
| 我要核对论文 | [文献来源](../../public-data/README.md) | PMID、DOI和各层资料的区别 |

## 一个例子 / An Example

一篇研究写“某个化验指标改善”，这里只能先记为指标变化。还要检查研究了谁、有没有对照、随访多久，才能判断它能支持什么。不能直接改写成“人变年轻了”。

五张资料表是不同处理层，同一论文可以跨层出现。“找到”“入选”“整理成笔记”都不等于已证实功效。

No individual prescriptions, dosing, stopping medication or purchase recommendations are provided. Draft grades and biomarkers do not establish human lifespan extension.

[全部当前入口](../../docs/asset-catalog.md) · [飞书阅读入口]({by_key['reader_navigation']['url']}) · [历史资料](../../archive/README.md)

资料快照：{snapshot}；阅读分类整理：{layout['organized_on']}。[本期文献与资产更新]({cfg['EVIDENCE_ATLAS_RELEASE_FILE']})。
"""
    (ROOT / "content/public-reader/start-here.md").write_text(start, encoding="utf-8")
    write_catalog(rows, cfg, layout)
    print("Built reader-first homepages and ordered nine-asset registry")


if __name__ == "__main__":
    main()
