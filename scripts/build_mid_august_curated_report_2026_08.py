"""Build the mid-August curated public guide, self-contained report, and Feishu indexes."""

from __future__ import annotations

import base64
import csv
import html
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"
PUBLIC_DATA = ROOT / "public-data"
PUBLIC_READER = ROOT / "content" / "public-reader"
VISUAL_DIR = DOCS / "assets" / "visual-assets" / "2026-08"
METRICS_PATH = DATA / "curation_release_metrics_2026_08.json"
REGISTRY_PATH = DATA / "feishu_table_registry.csv"
FINDINGS_PATH = PUBLIC_DATA / "evidence-findings-2026-08.csv"
TOPICS_PATH = DATA / "topics.csv"
REPAIR_PATH = DATA / "pubmed_identifier_repair_report_2026_08.json"

BRAND = "宇多Yul细胞/yulcell"
GITHUB = "https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn"
SNAPSHOT_DATE = "2026-08-09"
MONTH = "2026-08"
REPORT_FILE = "mid-august-public-update-2026-08.html"
RELEASE_FILE = "mid-august-2026-update.md"

MAIN_IMAGES = [
    ("heatmap-dashboard-2026-08.png", "热力图总览 / Heatmap dashboard", "先看全局，再进入单张图。颜色表示数量或结构，不表示治疗效果。"),
    ("heatmap-topic-year-2026-08.png", "主题与年份 / Topic by year", "看不同主题近年的研究数量。2026 年尚未结束，不能和完整年份直接比较。"),
    ("heatmap-topic-evidence-2026-08.png", "主题与证据等级 / Topic by evidence grade", "看草稿等级分布。A 级也不等于适合每个人使用。"),
    ("evidence-yield-ingredients-2026-08.png", "成分证据产出 / Ingredient evidence yield", "看哪些成分进入较高层级的比例，不是购买榜。"),
    ("retraction-density-2026-08.png", "撤稿密度观察 / Retraction watch", "用于提醒复核风险；不能因为一个领域撤稿多就否定全部研究。"),
    ("topic-evidence-yield-2026-08.png", "主题证据产出 / Topic evidence yield", "比较 20 个主题进入较高等级层的结构。"),
    ("ingredient-card-wall-2026-08.png", "50 成分总览 / 50-ingredient wall", "适合发帖总览；每张单卡仍要结合边界说明阅读。"),
]

FEATURED_PMIDS = ["42543470", "42219271", "42044540", "42217831", "42212393", "42545663"]
FEATURED_NOTES = {
    "42543470": "冠心病患者有氧加抗阻训练的系统综述与 Meta 分析；属于特定患者康复场景，不能直接外推到所有人。",
    "42219271": "2 型糖尿病人群 GLP-1 类治疗与心血管结局的网络 Meta 分析；药物问题必须由医生评估。",
    "42044540": "地中海饮食与肿瘤一级预防的系统综述；饮食模式证据不等于某一种补剂有效。",
    "42217831": "久坐、看电视时间与全因死亡风险的综述之综述；观察到关联不等于单篇研究证明因果。",
    "42212393": "取栓成功后强化与常规降压的一年结局；研究对象很特殊，不能套用为普通人的降压方案。",
    "42545663": "老年人运动获益是否达到临床意义的随机试验随访分析；仍需全文复核效果大小和适用人群。",
}

RETIREMENT_LABELS = {
    "duplicate_record": "重复记录",
    "non_result_publication_title": "题名显示不是结果论文",
    "topic_capacity_limit": "超过主题容量，保留优先级更高者",
    "unmapped_topic": "无法映射到当前 20 个主题",
    "candidate_retired_as_duplicate": "候选已作为重复项退出",
    "non_primary_commentary_or_correction": "评论、社论或勘误",
    "nonhuman_record_in_human_outcome_topic": "人体主题中的动物或细胞记录",
    "protocol_or_registered_plan": "方案论文或注册计划",
    "title_topic_signal_missing": "题名与分配主题没有直接关系",
}

ASSET_DESCRIPTIONS = {
    "literature_library": "当前精编文献目录",
    "candidate_sources": "当前候选来源与检索记录",
    "shortlist_sources": "进入优先复核的短名单",
    "evidence_findings": "自动整理、待全文复核的证据发现",
    "evidence_matrix": "按主题、终点和等级筛选的矩阵",
    "heatmaps": "6 张研究图和证据产出图",
    "ingredient_cards": "50 张常见成分单卡",
    "ingredient_wall": "1 张 50 成分总览墙",
    "reader_navigation": "普通读者 14 步阅读入口",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def image_data_uri(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    output = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        output.append("| " + " | ".join(str(cell).replace("|", "\\|").replace("\n", " ") for cell in row) + " |")
    return "\n".join(output)


def registry_rows() -> list[dict[str, str]]:
    rows = read_csv(REGISTRY_PATH)
    if len(rows) != 9 or len({row["table_id"] for row in rows}) != 9:
        raise RuntimeError("Feishu registry must contain nine unique tables")
    return rows


def build_feishu_manifest(registry: list[dict[str, str]]) -> None:
    rows = [
        {
            "类别": row["category"],
            "表名": row["stable_name"],
            "飞书链接": row["url"],
            "说明": ASSET_DESCRIPTIONS[row["asset_key"]],
            "记录数": row["expected_rows"],
            "状态": row["status"],
            "更新月份": MONTH,
        }
        for row in registry
    ]
    write_csv(
        DATA / "feishu_live_tables_2026_08.csv",
        rows,
        ["类别", "表名", "飞书链接", "说明", "记录数", "状态", "更新月份"],
    )

    table_rows = "\n".join(
        f"| {row['类别']} | {row['表名']} | {int(row['记录数']):,} | {row['状态']} | [打开飞书]({row['飞书链接']}) |"
        for row in rows
    )
    by_key = {row["asset_key"]: row for row in registry}
    text = f"""# 飞书公开资产索引（2026 年 8 月中期精编） / Feishu Public Assets

**品牌 / Brand:** {BRAND}<br>
**冻结日期 / Snapshot date:** {SNAPSHOT_DATE}<br>
**表格策略 / Table policy:** 复用 9 张长期表，不再每月新建一组 / Reuse nine stable tables instead of creating monthly duplicates.

## 最短阅读路线 / Shortest Route

- [1. 当前阅读导航 / Reading navigation]({by_key['reader_navigation']['url']})：第一次打开先看这里。
- [2. 当前研究图 / Research visuals]({by_key['heatmaps']['url']})：看研究数量和证据结构，不当疗效榜。
- [3. 当前 50 成分卡 / Ingredient cards]({by_key['ingredient_cards']['url']})：查常见成分的证据边界。

## 全部多维表格 / All Bitable Tables

| 类别 | 稳定表名 | 记录数 | 状态 | 入口 |
| --- | --- | ---: | --- | --- |
{table_rows}

## 为什么数量变小 / Why the Counts Are Smaller

本次不是继续把自动检索结果塞进主库。候选库从 16,547 条精简为 11,079 条，findings 从 6,000 条精简为 2,966 条。重复项、方案论文、评论勘误、动物/人体边界错误、题名与主题不符及超过容量的低优先级记录退出当前层；完整原因保存在 GitHub 的 `data/archive/`。

The smaller counts reflect curation, not missing data. Retirement reasons are versioned on GitHub, and older snapshots remain recoverable.

## 使用边界 / Boundary

这些表用于证据导航和公开复核，不是购买清单、处方、剂量方案或诊断工具。飞书是否被搜索引擎收录仍取决于公开分享和搜索引擎抓取设置。

GitHub source of truth: [{GITHUB}]({GITHUB})
"""
    (DOCS / "feishu-public-assets-2026-08.md").write_text(text, encoding="utf-8")


def build_navigation(registry: list[dict[str, str]]) -> None:
    by_key = {row["asset_key"]: row for row in registry}
    specs = [
        ("普通读者入口：从这里开始", "Start here", "第一次打开项目的人", "先弄清项目能回答什么、不能回答什么。", "content/public-reader/start-here.md", "reader_navigation", "阅读入口"),
        ("2026 年 8 月中期精编说明", "Mid-August curated update", "所有读者", "先看这次为什么一边补文献、一边删噪声。", f"content/public-reader/{RELEASE_FILE}", "reader_navigation", "更新说明"),
        ("15 条结论", "15 takeaways", "普通读者、学生", "先建立判断抗衰说法的基本框架。", "content/public-reader/ten-takeaways.md", "reader_navigation", "阅读入口"),
        ("证据权重怎么看", "How evidence is weighted", "想学会判断证据的人", "分清人体结局、指标、动物和机制研究。", "content/public-reader/evidence-weight.md", "evidence_matrix", "方法说明"),
        ("大众主题速读", "Topic guide", "关心运动、睡眠和代谢的人", "按主题读结论，不必先翻论文。", "content/public-reader/topics.md", "evidence_findings", "阅读入口"),
        ("最常见 30 个补剂", "30 common supplements", "想查补剂的人", "先看常见误解和安全边界。", "content/public-reader/supplements-top-30.md", "ingredient_cards", "补剂入口"),
        ("护肤与外观抗老速读", "Skin and appearance guide", "关心防晒、皱纹和医美的人", "把皮肤改善和延长寿命分开看。", "content/public-reader/skin.md", "ingredient_cards", "皮肤入口"),
        ("哪些内容必须先问医生", "Doctor-first topics", "涉及药物和慢病的人", "药物、慢病和高风险干预先找专业人员。", "content/public-reader/doctor-first.md", "reader_navigation", "安全边界"),
        ("研究热力图", "Research heatmaps", "想看全局结构的人", "颜色深表示记录多，不表示干预更有效。", "content/public-reader/research-heatmap.md", "heatmaps", "视觉入口"),
        ("50 成分卡", "50 ingredient cards", "发帖和查成分的人", "每张卡都同时写证据和不能支持的说法。", "content/public-reader/ingredient-cards-top-50.md", "ingredient_cards", "视觉入口"),
        ("撤稿怎么看", "How to read retractions", "关注研究可靠性的人", "把撤稿当复核信号，不作简单好坏判断。", "content/public-reader/retractions.md", "heatmaps", "风险说明"),
        ("精编与归档规则", "Curation and retention policy", "想复核清理规则的人", "查看容量上限、退出理由和恢复方式。", "docs/data-retention-and-curation-policy.md", "reader_navigation", "方法说明"),
        ("公开 CSV 数据", "Public CSV data", "研究者、数据分析人员", "下载当前五张处理层表，并注意同一论文会跨层出现。", "public-data/README.md", "candidate_sources", "数据入口"),
        ("GitHub 项目首页", "GitHub repository", "所有读者", "查看版本历史、方法、报告和全部公开资产。", "README.md", "reader_navigation", "项目入口"),
    ]
    rows = []
    for index, (zh, en, audience, note, github_path, feishu_key, asset_type) in enumerate(specs, 1):
        rows.append(
            {
                "entry_id": f"R{index:03d}",
                "公开标题": f"{BRAND} | {zh}",
                "阅读顺序": f"{index:02d}",
                "中文名称": zh,
                "English title": en,
                "适合谁": audience,
                "一句话说明": note,
                "GitHub链接": f"{GITHUB}/blob/main/{github_path}",
                "飞书链接": by_key[feishu_key]["url"],
                "资产类型": asset_type,
                "冻结日期": SNAPSHOT_DATE,
                "复核日期": SNAPSHOT_DATE,
                "品牌标识": BRAND,
                "Brand": "yulcell",
                "SEO关键词": "宇多Yul细胞/yulcell, yulcell, 长寿抗衰证据图谱, 健康寿命证据图谱",
                "状态": "公开",
            }
        )
    write_csv(
        DATA / "feishu_reader_navigation_2026_08.csv",
        rows,
        list(rows[0]),
    )


def build_markdown(metrics: dict[str, Any], findings: list[dict[str, str]], topics: dict[str, dict[str, str]]) -> None:
    before = metrics["before"]
    after = metrics["after"]
    search = metrics["search"]
    retired = metrics["retired"]
    levels = Counter(row.get("final_evidence_level") or row.get("evidence_level_draft") or "未分级" for row in findings)
    by_pmid = {row.get("pmid", ""): row for row in findings}

    retirement_rows = []
    for reason, count in retired["candidate_reasons"].items():
        retirement_rows.append(["候选层", RETIREMENT_LABELS.get(reason, reason), f"{count:,}"])
    for reason, count in retired["finding_reasons"].items():
        retirement_rows.append(["findings", RETIREMENT_LABELS.get(reason, reason), f"{count:,}"])

    sample_rows = []
    for pmid in FEATURED_PMIDS:
        row = by_pmid.get(pmid)
        if not row:
            continue
        sample_rows.append(
            [
                f"[{pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)",
                topics.get(row["topic_id"], {}).get("title_zh", row["topic_id"]),
                row.get("study_type_draft", ""),
                row.get("final_evidence_level", ""),
                FEATURED_NOTES[pmid],
            ]
        )

    topic_rows = []
    for topic_id, count in metrics["candidate_topic_counts"].items():
        topic = topics.get(topic_id, {})
        topic_rows.append(
            [
                topic.get("title_zh", topic_id),
                topic.get("title_en", topic_id),
                f"{count:,}",
                f"{metrics['finding_topic_counts'].get(topic_id, 0):,}",
            ]
        )

    text = f"""# 宇多Yul细胞/yulcell：2026 年 8 月中期精编更新

**冻结日期 / Snapshot date:** {SNAPSHOT_DATE}<br>
**检索窗口 / Search window:** {search['date_window']}<br>
**本轮目标 / Goal:** 补进真正相关的新资料，同时清理重复、弱相关和放错层级的记录，让初中生也能看懂这张证据地图。

## 一句话结论 / One-Sentence Summary

这次不是“继续往里塞”。PubMed 检索找到 {search['unique_pubmed_matches']:,} 条匹配，其中 {search['new_rows']:,} 条是新候选；经过主题核对、去重和容量控制后，当前候选库从 {before['candidate_records']:,} 条精简为 {after['candidate_records']:,} 条，findings 从 {before['finding_records']:,} 条精简为 {after['finding_records']:,} 条。

This release adds recent PubMed records while deliberately shrinking the active library. Smaller counts mean less noise, not lost history.

## 先看懂四个数字 / Four Numbers to Understand First

| 数字 | 是什么 | 不是什么 |
| ---: | --- | --- |
| {after['candidate_records']:,} | 当前候选文献目录 | 不是 {after['candidate_records']:,} 个已证实结论 |
| {after['finding_records']:,} | 与主题直接相关、进入复核层的 findings | 不是全部完成全文人工复核 |
| 1,500 | 公开证据矩阵行数 | 不是论文总数 |
| 29,590 | 五张公开 CSV 的处理层行数总和 | 同一论文可跨层出现，不能当成独立论文数 |

## 本轮找到了什么 / What the Search Found

- 20 个固定主题，各运行一条有限窗口查询。
- PubMed 唯一匹配：{search['unique_pubmed_matches']:,} 条。
- 新候选：{search['new_rows']:,} 条；已在库中：{search['matched_existing']:,} 条。
- 最终保留近期候选：{after['recent_candidates_retained']:,} 条；其中进入 findings：{after['recent_findings_retained']:,} 条。
- 新记录仍是自动整理草稿，不能因为标成 A 或 B 就直接改成医学结论。

## 为什么要删 / Why Active Records Were Retired

{markdown_table(['层级', '退出原因', '决定数'], retirement_rows)}

“退出”只表示不再占用当前公开层的位置，不代表论文被否定。每条决定都保留在 `data/archive/`，旧完整快照可从 ZIP 和 Git 历史恢复。

## 容量规则 / Capacity Rules

- 候选层：每个主题最多 600 条。
- findings：每个主题最多 200 条，不为填满而凑数。
- 证据矩阵：总计最多 1,500 条，每主题最多 100 条。
- 核心人工复核队列：每主题最多 3 条，本版共 54 条。
- 每周自动检索只能生成有上限的 intake Pull Request，不能再直接把候选推入 `main`。

完整规则：[精编与归档规则](../../docs/data-retention-and-curation-policy.md)

## 近期文献举例 / Recent Examples

这些例子只是说明本轮覆盖了哪些问题，不是疗效推荐。题名和标识已与 NCBI PubMed 核对；结论仍需全文复核。

{markdown_table(['PMID', '主题', '研究类型草稿', '等级草稿', '怎么理解'], sample_rows)}

## 当前等级分布 / Current Draft Grades

| A | B | C | D | E |
| ---: | ---: | ---: | ---: | ---: |
| {levels.get('A', 0):,} | {levels.get('B', 0):,} | {levels.get('C', 0):,} | {levels.get('D', 0):,} | {levels.get('E', 0):,} |

等级是排序工具，不是处方。A 表示更值得优先复核，不代表“人人应该用”。

## 20 个主题的当前体量 / Active Size by Topic

{markdown_table(['主题', 'Topic', '候选', 'findings'], topic_rows)}

## 本轮修正的质量问题 / Quality Fixes

- 修正 PubMed XML 解析范围，参考文献 DOI/PMCID 不再覆盖论文本身的标识。
- 用 NCBI 官方 E-utilities 核对全部 {len(findings):,} 个 findings PMID：缺失 0，实质题名冲突 0。
- 修正 findings DOI 1,395 个、PMCID 1,814 个；修复后候选表与 findings DOI 不一致为 0。
- 方案论文、评论勘误、明确动物实验不再被自动抬进人体高等级层。

## 图片与公开资产 / Visuals and Public Assets

- [自包含图文报告 / Self-contained report](../../docs/{REPORT_FILE})
- [8 月研究图片 / August images](../../docs/assets/visual-assets/2026-08/)
- [飞书 9 张长期表 / Nine stable Feishu tables](../../docs/feishu-public-assets-2026-08.md)
- [公开 CSV / Public CSV package](../../public-data/README.md)
- [精编与归档规则 / Curation policy](../../docs/data-retention-and-curation-policy.md)

## 读者边界 / Reader Boundary

这张图谱用来帮助读者区分证据强弱，不提供个人诊断、处方、剂量、停药建议、医美操作或购买推荐。动物延寿不能写成人类延寿已经证实，指标改善不能写成返老还童，研究数量多也不能写成疗效更强。
"""
    (PUBLIC_READER / RELEASE_FILE).write_text(text, encoding="utf-8")


def figure_html(path: Path, title: str, note: str, css_class: str = "main-figure") -> str:
    uri = image_data_uri(path)
    return f"""
    <figure class="{css_class}">
      <img src="{uri}" alt="{esc(title)}" loading="lazy">
      <figcaption><strong>{esc(title)}</strong><span>{esc(note)}</span>
        <button type="button" class="download" data-name="{esc(path.name)}">下载 PNG / Download</button>
      </figcaption>
    </figure>"""


def build_html(metrics: dict[str, Any], findings: list[dict[str, str]], topics: dict[str, dict[str, str]], registry: list[dict[str, str]]) -> None:
    search = metrics["search"]
    before = metrics["before"]
    after = metrics["after"]
    retired = metrics["retired"]
    levels = Counter(row.get("final_evidence_level") or row.get("evidence_level_draft") or "未分级" for row in findings)
    by_pmid = {row.get("pmid", ""): row for row in findings}
    by_key = {row["asset_key"]: row for row in registry}

    main_figures = "\n".join(
        figure_html(VISUAL_DIR / filename, title, note)
        for filename, title, note in MAIN_IMAGES
    )
    card_figures = "\n".join(
        figure_html(path, path.stem, "证据边界卡 / Evidence boundary card", "card-figure")
        for path in sorted((VISUAL_DIR / "ingredient-cards").glob("*.png"))
    )
    sample_html = "".join(
        f"<tr><td><a href=\"https://pubmed.ncbi.nlm.nih.gov/{pmid}/\">{pmid}</a></td>"
        f"<td>{esc(topics.get(by_pmid[pmid]['topic_id'], {}).get('title_zh', by_pmid[pmid]['topic_id']))}</td>"
        f"<td>{esc(by_pmid[pmid].get('study_type_draft', ''))}</td>"
        f"<td><span class=\"grade grade-{esc(by_pmid[pmid].get('final_evidence_level', 'E'))}\">{esc(by_pmid[pmid].get('final_evidence_level', ''))}</span></td>"
        f"<td>{esc(FEATURED_NOTES[pmid])}</td></tr>"
        for pmid in FEATURED_PMIDS
        if pmid in by_pmid
    )
    reason_html = "".join(
        f"<tr><td>候选层</td><td>{esc(RETIREMENT_LABELS.get(reason, reason))}</td><td>{count:,}</td></tr>"
        for reason, count in retired["candidate_reasons"].items()
    ) + "".join(
        f"<tr><td>findings</td><td>{esc(RETIREMENT_LABELS.get(reason, reason))}</td><td>{count:,}</td></tr>"
        for reason, count in retired["finding_reasons"].items()
    )
    topic_html = "".join(
        f"<tr><td>{esc(topics.get(topic_id, {}).get('title_zh', topic_id))}</td>"
        f"<td>{esc(topics.get(topic_id, {}).get('title_en', topic_id))}</td>"
        f"<td>{candidate_count:,}</td><td>{metrics['finding_topic_counts'].get(topic_id, 0):,}</td></tr>"
        for topic_id, candidate_count in metrics["candidate_topic_counts"].items()
    )
    feishu_links = "".join(
        f"<li><a href=\"{esc(row['url'])}\">{esc(row['stable_name'])}</a><span>{int(row['expected_rows']):,} 条</span></li>"
        for row in registry
    )

    document = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <link rel="icon" href="data:,">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{BRAND} 2026 年 8 月中期长寿抗衰证据图谱精编更新，含 PubMed 新文献、清理规则、热力图、50 成分卡和 GitHub/飞书资产。">
  <meta name="keywords" content="宇多Yul细胞/yulcell,yulcell,长寿抗衰证据图谱,健康寿命证据图谱,longevity evidence atlas">
  <title>{BRAND} | 2026 年 8 月中期精编更新</title>
  <style>
    :root {{ --ink:#182027; --muted:#5b6670; --line:#d5dde3; --paper:#ffffff; --soft:#f4f7f8; --green:#176b4b; --blue:#235a9f; --coral:#b4473a; --gold:#8a650c; }}
    * {{ box-sizing:border-box; }}
    html {{ scroll-behavior:smooth; }}
    body {{ margin:0; color:var(--ink); background:var(--paper); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",Arial,sans-serif; line-height:1.68; }}
    a {{ color:var(--blue); }}
    header {{ background:#17232c; color:#fff; padding:44px 24px 38px; border-bottom:6px solid #2b8a66; }}
    header .inner, main > section > .inner, footer .inner {{ width:min(1120px, calc(100% - 40px)); margin:0 auto; }}
    .eyebrow {{ margin:0 0 10px; color:#8fd6bc; font-size:14px; font-weight:700; }}
    h1 {{ margin:0; font-size:38px; line-height:1.2; letter-spacing:0; }}
    .subtitle {{ max-width:850px; margin:14px 0 0; color:#dce7ec; font-size:18px; }}
    .meta {{ margin-top:18px; color:#aebdc6; font-size:14px; }}
    .quick-nav {{ display:flex; flex-wrap:wrap; gap:8px 18px; margin-top:22px; }}
    .quick-nav a {{ color:#fff; text-decoration-thickness:1px; text-underline-offset:4px; }}
    main > section {{ border-bottom:1px solid var(--line); padding:42px 0; }}
    main > section.alt {{ background:var(--soft); }}
    h2 {{ margin:0 0 18px; font-size:26px; line-height:1.3; letter-spacing:0; }}
    h3 {{ margin:28px 0 12px; font-size:19px; letter-spacing:0; }}
    p {{ margin:10px 0; }}
    .lead {{ font-size:18px; max-width:900px; }}
    .notice {{ border-left:5px solid var(--coral); padding:14px 16px; background:#fff6f4; max-width:940px; }}
    .metrics {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin-top:24px; }}
    .metric {{ min-height:118px; border:1px solid var(--line); border-radius:6px; padding:16px; background:#fff; }}
    .metric b {{ display:block; font-size:30px; color:var(--green); line-height:1.15; }}
    .metric span {{ display:block; margin-top:8px; color:var(--muted); font-size:14px; }}
    .metric.blue b {{ color:var(--blue); }} .metric.coral b {{ color:var(--coral); }} .metric.gold b {{ color:var(--gold); }}
    .table-wrap {{ overflow-x:auto; border:1px solid var(--line); border-radius:6px; background:#fff; }}
    table {{ width:100%; border-collapse:collapse; min-width:720px; font-size:14px; }}
    th,td {{ border-bottom:1px solid var(--line); padding:10px 12px; text-align:left; vertical-align:top; }}
    th {{ background:#edf2f4; }} tr:last-child td {{ border-bottom:0; }}
    .grade {{ display:inline-block; min-width:28px; text-align:center; padding:2px 7px; border-radius:4px; color:#fff; font-weight:700; }}
    .grade-A {{ background:var(--green); }} .grade-B {{ background:var(--blue); }} .grade-C {{ background:var(--gold); }} .grade-D,.grade-E {{ background:var(--coral); }}
    figure {{ margin:30px 0 0; }}
    figure img {{ display:block; width:100%; height:auto; border:1px solid var(--line); background:#fff; }}
    figcaption {{ display:grid; grid-template-columns:minmax(0,1fr) auto; gap:4px 18px; align-items:center; padding:11px 0; }}
    figcaption strong,figcaption span {{ display:block; }} figcaption span {{ color:var(--muted); font-size:14px; }}
    button.download {{ grid-column:2; grid-row:1 / span 2; border:1px solid #9aaab5; border-radius:4px; background:#fff; color:var(--ink); padding:8px 11px; cursor:pointer; font-weight:600; }}
    button.download:hover {{ border-color:var(--green); color:var(--green); }}
    details {{ margin-top:26px; }} summary {{ cursor:pointer; font-weight:700; font-size:18px; }}
    .card-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:16px; margin-top:18px; }}
    .card-figure {{ margin:0; border:1px solid var(--line); border-radius:6px; padding:8px; background:#fff; }}
    .card-figure img {{ border:0; }} .card-figure figcaption {{ display:block; padding:8px 2px 2px; }}
    .card-figure figcaption strong {{ font-size:13px; overflow-wrap:anywhere; }} .card-figure figcaption span {{ display:none; }}
    .card-figure button.download {{ width:100%; margin-top:7px; }}
    .asset-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:24px; }}
    .link-list {{ list-style:none; padding:0; margin:0; }} .link-list li {{ display:flex; justify-content:space-between; gap:12px; border-bottom:1px solid var(--line); padding:9px 0; }} .link-list span {{ color:var(--muted); white-space:nowrap; }}
    footer {{ padding:34px 0; background:#17232c; color:#dce7ec; }} footer a {{ color:#9fd8ff; }}
    @media (max-width:820px) {{ h1 {{ font-size:31px; }} .metrics {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} .card-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} .asset-grid {{ grid-template-columns:1fr; }} }}
    @media (max-width:520px) {{ header {{ padding:32px 0 28px; }} header .inner,main > section > .inner,footer .inner {{ width:min(100% - 28px,1120px); }} h1 {{ font-size:27px; }} h2 {{ font-size:23px; }} main > section {{ padding:32px 0; }} .metrics {{ grid-template-columns:1fr 1fr; }} .metric {{ min-height:108px; padding:13px; }} .metric b {{ font-size:25px; }} .card-grid {{ grid-template-columns:1fr; }} figcaption {{ display:block; }} button.download {{ width:100%; margin-top:9px; }} }}
  </style>
</head>
<body>
  <header>
    <div class="inner">
      <p class="eyebrow">2026-08 MID-MONTH CURATED RELEASE</p>
      <h1>宇多Yul细胞 / yulcell</h1>
      <p class="subtitle">长寿抗衰与健康寿命证据图谱：8 月中期精编更新。补进新资料，也清理重复和弱相关记录。</p>
      <p class="meta">冻结日期 {SNAPSHOT_DATE} · PubMed 窗口 {esc(search['date_window'])} · 双语公开资产</p>
      <nav class="quick-nav"><a href="#summary">先看结论</a><a href="#cleanup">为什么变小</a><a href="#new">近期文献</a><a href="#visuals">图片</a><a href="#assets">GitHub 与飞书</a></nav>
    </div>
  </header>
  <main>
    <section id="summary"><div class="inner">
      <h2>先说结论 / Summary First</h2>
      <p class="lead">这次更新不是继续堆数量。检索找到 <strong>{search['unique_pubmed_matches']:,}</strong> 条匹配，其中 <strong>{search['new_rows']:,}</strong> 条是新候选；清理后，当前候选库从 {before['candidate_records']:,} 条变为 {after['candidate_records']:,} 条，findings 从 {before['finding_records']:,} 条变为 {after['finding_records']:,} 条。</p>
      <p class="notice"><strong>为什么数字变小：</strong>重复、方案论文、评论勘误、动物/人体边界错误、题名与主题不符和超过容量的低优先级记录退出当前层。它们仍可从退出日志、旧快照和 Git 历史恢复。</p>
      <div class="metrics">
        <div class="metric"><b>{after['candidate_records']:,}</b><span>当前候选文献 / active candidates</span></div>
        <div class="metric blue"><b>{after['finding_records']:,}</b><span>当前 findings / review drafts</span></div>
        <div class="metric gold"><b>1,500</b><span>证据矩阵 / matrix rows</span></div>
        <div class="metric coral"><b>29,590</b><span>五层 CSV 总行数，不是论文数</span></div>
      </div>
    </div></section>

    <section id="cleanup" class="alt"><div class="inner">
      <h2>这次怎样做减法 / How the Library Was Curated</h2>
      <p>候选每主题最多 600 条，findings 每主题最多 200 条，矩阵总计最多 1,500 条、每主题最多 100 条。上限不是配额：合格记录少就少放，不为填表而凑数。</p>
      <div class="table-wrap"><table><thead><tr><th>层级</th><th>退出原因</th><th>决定数</th></tr></thead><tbody>{reason_html}</tbody></table></div>
      <p>候选退出决定 {retired['candidate_decisions']:,} 条，findings 退出决定 {retired['finding_decisions']:,} 条。一个记录可能先经过新检索，再因去重或容量规则退出，因此“决定数”不能简单当成净减少数。</p>
    </div></section>

    <section id="new"><div class="inner">
      <h2>近期文献 / Recent Literature</h2>
      <p>20 个主题共得到 {search['unique_pubmed_matches']:,} 个唯一 PubMed 匹配：新候选 {search['new_rows']:,} 条，已有记录 {search['matched_existing']:,} 条；最终保留近期候选 {after['recent_candidates_retained']:,} 条，其中 {after['recent_findings_retained']:,} 条进入 findings。</p>
      <p class="notice">下面只是检索覆盖示例，不是治疗推荐。所有等级仍是公开草稿，完整全文、偏倚风险和适用人群需要继续人工复核。</p>
      <div class="table-wrap"><table><thead><tr><th>PMID</th><th>主题</th><th>研究类型草稿</th><th>等级</th><th>怎么理解</th></tr></thead><tbody>{sample_html}</tbody></table></div>
      <h3>当前等级分布</h3>
      <div class="metrics">
        <div class="metric"><b>{levels.get('A',0):,}</b><span>A：优先复核，不是处方</span></div><div class="metric blue"><b>{levels.get('B',0):,}</b><span>B：中高置信候选</span></div><div class="metric gold"><b>{levels.get('C',0):,}</b><span>C：有信号、限制明显</span></div><div class="metric coral"><b>{levels.get('D',0)+levels.get('E',0):,}</b><span>D/E：早期、低置信或不足</span></div>
      </div>
    </div></section>

    <section class="alt"><div class="inner">
      <h2>20 个主题 / 20 Active Topics</h2>
      <div class="table-wrap"><table><thead><tr><th>主题</th><th>Topic</th><th>候选</th><th>findings</th></tr></thead><tbody>{topic_html}</tbody></table></div>
    </div></section>

    <section id="visuals"><div class="inner">
      <h2>更新图片 / Updated Visuals</h2>
      <p>本文件内嵌 7 张主图和 50 张单成分卡，可以离线打开。每张图下方都能直接下载 PNG。</p>
{main_figures}
      <details><summary>展开 50 张单成分卡 / Show 50 ingredient cards</summary><div class="card-grid">{card_figures}</div></details>
    </div></section>

    <section class="alt"><div class="inner">
      <h2>质量修正 / Quality Corrections</h2>
      <p>本轮发现并修正了 PubMed XML 标识范围问题：参考文献列表中的 DOI/PMCID 不再覆盖论文本身。全部 {len(findings):,} 个 findings PMID 已用 NCBI 官方 E-utilities 核对，缺失 0、实质题名冲突 0；修正 findings DOI 1,395 个、PMCID 1,814 个，修复后候选源表与 findings DOI 不一致为 0。</p>
      <p>自动分类也增加了明确动物实验、叙述性综述、方案论文和评论勘误的防误升规则。</p>
    </div></section>

    <section id="assets"><div class="inner">
      <h2>GitHub、飞书与数据 / Public Assets</h2>
      <div class="asset-grid">
        <div><h3>GitHub</h3><ul class="link-list">
          <li><a href="{GITHUB}">项目首页 / Repository</a></li>
          <li><a href="{GITHUB}/blob/main/content/public-reader/{RELEASE_FILE}">普通读者说明</a></li>
          <li><a href="{GITHUB}/tree/main/public-data">公开 CSV</a></li>
          <li><a href="{GITHUB}/blob/main/docs/data-retention-and-curation-policy.md">精编与归档规则</a></li>
        </ul></div>
        <div><h3>飞书 9 张长期表</h3><ul class="link-list">{feishu_links}</ul></div>
      </div>
      <p>飞书继续复用同一组长期表，不再每月新建一套。GitHub 是版本化源头；飞书是中文阅读、筛选和复核层。</p>
    </div></section>

    <section><div class="inner">
      <h2>不能从这份报告得出什么 / What This Report Does Not Prove</h2>
      <ul><li>动物延寿不等于人类延寿。</li><li>指标改善不等于返老还童。</li><li>论文多、热力图颜色深不等于干预有效。</li><li>A 级草稿不等于每个人都应该使用。</li><li>本项目不提供个人处方、剂量、诊断、医美操作或购买推荐。</li></ul>
    </div></section>
  </main>
  <footer><div class="inner"><strong>{BRAND}</strong><p>Longevity Anti-Aging & Healthspan Evidence Atlas EnCn · Snapshot {SNAPSHOT_DATE}</p><p><a href="{GITHUB}">{GITHUB}</a></p></div></footer>
  <script>
    document.addEventListener('click', function(event) {{
      const button = event.target.closest('button.download');
      if (!button) return;
      const figure = button.closest('figure');
      const image = figure ? figure.querySelector('img') : null;
      if (!image) return;
      const link = document.createElement('a');
      link.href = image.src;
      link.download = button.dataset.name || 'yulcell-asset.png';
      document.body.appendChild(link); link.click(); link.remove();
    }});
  </script>
</body>
</html>
"""
    (DOCS / REPORT_FILE).write_text(document, encoding="utf-8")


def main() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    repair = json.loads(REPAIR_PATH.read_text(encoding="utf-8"))
    if repair.get("status") != "passed" or repair.get("title_mismatches") != 0:
        raise RuntimeError("PubMed identifier repair must pass before public report generation")
    findings = read_csv(FINDINGS_PATH)
    topics = {row["topic_id"]: row for row in read_csv(TOPICS_PATH)}
    registry = registry_rows()
    card_count = len(list((VISUAL_DIR / "ingredient-cards").glob("*.png")))
    if len(findings) != metrics["after"]["finding_records"] or card_count != 50:
        raise RuntimeError("Release inputs do not match curated metrics")

    build_feishu_manifest(registry)
    build_navigation(registry)
    build_markdown(metrics, findings, topics)
    build_html(metrics, findings, topics, registry)
    print(f"wrote content/public-reader/{RELEASE_FILE}")
    print(f"wrote docs/{REPORT_FILE}")
    print("wrote 9-table Feishu manifest and 14-row reading navigation")


if __name__ == "__main__":
    main()
