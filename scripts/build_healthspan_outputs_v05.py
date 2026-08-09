from __future__ import annotations

import argparse
import csv
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CONTENT = ROOT / "content"
FINDINGS = DATA / "evidence_findings.csv"
SHORTLIST = DATA / "shortlist_sources.csv"
MATRIX = DATA / "evidence_matrix.csv"
TOPICS_CSV = DATA / "topics.csv"
PUBLIC_SUMMARY_CSV = DATA / "public_summary.csv"
PUBLIC_SUMMARY_MD = CONTENT / "overview" / "public-summary.md"
PAPERS = CONTENT / "papers"
TOPICS_DIR = CONTENT / "topics"
ANALYSIS = CONTENT / "analysis" / "evidence-ranking.md"
RECOMMENDATIONS = CONTENT / "recommendations" / "for-general-readers.md"
STATUS_DOC = ROOT / "docs" / "current-output-status.md"
TODAY = os.environ.get("EVIDENCE_ATLAS_UPDATE_DATE", "2026-04-29")
DRAFT_NOTICE_ZH = "草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。"
DRAFT_NOTICE_EN = "Draft status: automatically prepared; not fully reviewed; not medical advice."


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in fields} for row in rows])


def slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return value[:110] or "item"


def level_rank(row: dict[str, str]) -> tuple[int, int, int, int]:
    level = row.get("final_evidence_level") or row.get("evidence_level_draft") or "E"
    level_score = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4}.get(level, 5)
    endpoint_score = {"H1": 0, "H2": 1, "H3": 2, "H5": 3, "H4": 4, "H6": 5}.get(row.get("endpoint_class_draft", "H6"), 6)
    quality = -int(row.get("quality_confidence_score") or row.get("contribution_score_draft") or 0)
    influence = -safe_int(row.get("influence_score"))
    return level_score, endpoint_score, quality, influence


def safe_int(value: str) -> int:
    try:
        return int(float(value or 0))
    except Exception:
        return 0


def grouped(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        out[row.get("topic_id", "")].append(row)
    return out


def clean_generated_pages() -> None:
    PAPERS.mkdir(parents=True, exist_ok=True)
    TOPICS_DIR.mkdir(parents=True, exist_ok=True)
    for pattern in ["pubmed-*.md", "crossref-*.md", "clinicaltrials-*.md"]:
        for path in PAPERS.glob(pattern):
            path.unlink()
    for path in TOPICS_DIR.glob("*.md"):
        if path.name != "_template.md":
            path.unlink()


def build_shortlist(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out = []
    for i, row in enumerate(sorted(rows, key=level_rank), start=1):
        out.append({
            "candidate_id": row["candidate_id"],
            "priority_rank": str(i),
            "topic_id": row["topic_id"],
            "topic_zh": row["topic_zh"],
            "topic_en": row["topic_en"],
            "title_en": row["title_en"],
            "title_zh": row["title_zh"],
            "year": row["year"],
            "journal": row["journal"],
            "source": row["source"],
            "pmid": row["pmid"],
            "pmcid": row.get("pmcid", ""),
            "doi": row["doi"],
            "evidence_level_draft": row["evidence_level_draft"],
            "final_evidence_level": row.get("final_evidence_level", ""),
            "endpoint_class_draft": row["endpoint_class_draft"],
            "quality_confidence_score": row.get("quality_confidence_score", ""),
            "influence_score": row.get("influence_score", ""),
            "confidence_cap_rule": row.get("confidence_cap_rule", ""),
            "evidence_source_depth": row["evidence_source_depth"],
            "reason_for_shortlist_zh": f"v0.5 短名单：{row['topic_zh']}；v0.4/v0.5 综合等级 {row.get('final_evidence_level') or row['evidence_level_draft']}，质量分 {row.get('quality_confidence_score','')}，终点 {row['endpoint_class_draft']}。公开前仍需人工全文复核。",
            "reason_for_shortlist_en": f"v0.5 shortlist: {row['topic_en']}; final level {row.get('final_evidence_level') or row['evidence_level_draft']}, quality score {row.get('quality_confidence_score','')}, endpoint {row['endpoint_class_draft']}. Human full-text review still required.",
            "review_status": row["review_status"],
        })
    return out


def build_matrix(rows: list[dict[str, str]], limit: int, per_topic_cap: int = 0) -> list[dict[str, str]]:
    out = []
    topic_counts: Counter[str] = Counter()
    for row in sorted(rows, key=level_rank):
        topic_id = row.get("topic_id", "")
        if per_topic_cap and topic_counts[topic_id] >= per_topic_cap:
            continue
        out.append({
            "paper_id": row["candidate_id"],
            "year": row["year"],
            "topic": row["topic_zh"],
            "intervention_or_exposure": row["intervention_or_exposure_draft"],
            "study_type": row["study_type_draft"],
            "species": row["species_draft"],
            "sample_size": row["sample_size_draft"],
            "primary_endpoint": row["endpoint_draft"],
            "endpoint_class": row["endpoint_class_draft"],
            "effect_size": "摘要级/题录级待复核",
            "evidence_level": row.get("final_evidence_level") or row["evidence_level_draft"],
            "risk_of_bias": row.get("risk_of_bias_rating") or "not_checked_public_draft",
            "actionability": "high" if row["recommendation_class_draft"] == "Strong Action" else "medium" if row["recommendation_class_draft"] == "Medical Action" else "low",
            "medical_supervision": row["medical_supervision_draft"],
            "recommendation_class": row["recommendation_class_draft"],
            "claim_supported": row["claim_supported_zh"],
            "claim_not_supported": row["claim_not_supported_zh"],
            "zh_summary": f"{DRAFT_NOTICE_ZH} {row['conclusion_zh']}",
            "en_summary": f"{DRAFT_NOTICE_EN} {row['conclusion_en']}",
            "last_checked": TODAY,
            "quality_confidence_score": row.get("quality_confidence_score", ""),
            "influence_score": row.get("influence_score", ""),
            "journal_metric_value": row.get("journal_metric_value", ""),
            "confidence_cap_rule": row.get("confidence_cap_rule", ""),
            "scoring_version": row.get("scoring_version", ""),
        })
        topic_counts[topic_id] += 1
        if len(out) >= limit:
            break
    return out


def write_paper_pages(rows: list[dict[str, str]]) -> None:
    for row in sorted(rows, key=level_rank):
        lines = [
            f"# {row['title_en']}",
            "",
            f"> {DRAFT_NOTICE_ZH}",
            f"> {DRAFT_NOTICE_EN}",
            "",
            "## Metadata / 元数据",
            "",
            f"- Candidate ID: `{row['candidate_id']}`",
            f"- Source: `{row['source']}`",
            f"- PMID: `{row['pmid']}`",
            f"- PMCID: `{row.get('pmcid','')}`",
            f"- DOI: `{row['doi']}`",
            f"- Year: {row['year']}",
            f"- Journal/Registry: {row['journal']}",
            f"- Topic: {row['topic_zh']} / {row['topic_en']}",
            f"- Evidence source depth: `{row['evidence_source_depth']}`",
            "",
            "## Study Design / 研究设计",
            "",
            f"- Draft study type: `{row['study_type_draft']}`",
            f"- Draft species/population: `{row['species_draft']}` / {row['population_draft']}",
            f"- Draft intervention or exposure: {row['intervention_or_exposure_draft']}",
            f"- Draft comparator: {row['comparator_draft']}",
            f"- Draft primary endpoint: {row['endpoint_draft']}",
            f"- Draft sample size: {row['sample_size_draft']}",
            "",
            "## Main Results / 主要结果",
            "",
            f"EN: {row['result_en']}",
            "",
            f"ZH draft: {row['result_zh']}",
            "",
            "## Conclusion Boundary / 结论边界",
            "",
            f"EN: {row['conclusion_en']}",
            "",
            f"ZH draft: {row['conclusion_zh']}",
            "",
            "## Supported Claim / 支持的结论",
            "",
            f"- ZH: {row['claim_supported_zh']}",
            f"- EN: {row['claim_supported_en']}",
            "",
            "## Unsupported Claim / 不支持的结论",
            "",
            f"- ZH: {row['claim_not_supported_zh']}",
            f"- EN: {row['claim_not_supported_en']}",
            "",
            "## Overinterpretation Risk / 过度解读风险",
            "",
            f"- ZH: {row['overinterpretation_risk_zh']}",
            f"- EN: {row['overinterpretation_risk_en']}",
            "",
            "## v0.4/v0.5 Scoring / 评分",
            "",
            f"- Draft evidence level: `{row['evidence_level_draft']}`",
            f"- Final evidence level: `{row.get('final_evidence_level','')}`",
            f"- Endpoint class: `{row['endpoint_class_draft']}`",
            f"- Quality confidence score: `{row.get('quality_confidence_score','')}`",
            f"- Influence score: `{row.get('influence_score','')}`",
            f"- Confidence cap rule: `{row.get('confidence_cap_rule','')}`",
            f"- Risk-of-bias tool: `{row.get('risk_of_bias_tool','')}`",
            f"- Medical supervision needed: `{row['medical_supervision_draft']}`",
            f"- Authority signal: {row['authority_signal_draft']}",
            "",
            "## Review Status / 复核状态",
            "",
            "Public draft. Needs human full-text review before formal recommendation or clinical interpretation.",
            "",
            "公开草稿。形成正式推荐或临床解释前，必须人工阅读全文复核。",
        ]
        (PAPERS / f"{slug(row['candidate_id'])}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def top_level(rows: list[dict[str, str]]) -> str:
    counts = Counter(row.get("final_evidence_level") or row.get("evidence_level_draft") for row in rows)
    for level in ["A", "B", "C", "D", "E"]:
        if counts.get(level):
            return level
    return "pending"


def median_quality(rows: list[dict[str, str]]) -> int:
    vals = sorted(safe_int(row.get("quality_confidence_score")) for row in rows if row.get("quality_confidence_score"))
    if not vals:
        return 0
    mid = len(vals) // 2
    return vals[mid] if len(vals) % 2 else round((vals[mid - 1] + vals[mid]) / 2)


def recommendation_boundary(topic_id: str) -> str:
    if topic_id in {"glp1-weight-cardiometabolic", "metformin-aging", "rapamycin-mtor-aging", "senolytics"}:
        return "medical_or_research_only"
    if topic_id in {"partial-reprogramming", "klotho-il11-aging", "itp-mouse-lifespan"}:
        return "research_only"
    if topic_id in {"nad-nmn-nr-aging", "epigenetic-clocks", "autophagy-mitophagy", "microbiome-inflammaging"}:
        return "do_not_overclaim"
    return "public_health_or_lifestyle_boundary"


def topic_position(topic_id: str, title_zh: str) -> tuple[str, str, str, str]:
    positions = {
        "cardiorespiratory-fitness": ("目前最值得优先关注的健康寿命指标之一；较高心肺适能与更低死亡和心血管风险高度相关。", "证据主要支持把心肺适能作为风险分层、运动干预和长期健康管理的核心指标。", "不同疾病人群、测试方式和干预强度之间仍需全文复核和分层。", "可作为生活方式优先方向；个体运动处方需结合年龄、疾病和医生评估。"),
        "physical-activity-healthspan": ("整体证据方向稳定：规律身体活动支持更好的健康结局和功能维持。", "活动量、减少久坐和功能维持具有稳定公共健康价值。", "最佳剂量、强度组合和慢病人群个体化方案仍需分层。", "支持行动方向，不等于给出单一万能运动处方。"),
        "resistance-training-muscle": ("肌肉量、力量和功能是健康寿命的关键支点；抗阻训练是高优先级主题。", "证据支持抗阻训练和综合运动对肌少、衰弱和功能下降的管理价值。", "训练模式、营养配合和不同风险人群仍需细分。", "可作为健康管理重点；高龄、骨质疏松或慢病人群需专业评估。"),
        "blood-pressure-aging": ("血压控制是心脑血管风险和健康寿命管理中证据最成熟的方向之一。", "硬终点、人群相关性和临床可行动性较强。", "不同年龄、虚弱状态和共病人群的目标值不能一刀切。", "支持监测和医学管理；不提供药物选择或剂量建议。"),
        "ldl-apob-cardiovascular-risk": ("动脉粥样硬化风险管理中的核心证据方向；apoB/LDL-C 是重要风险指标。", "遗传、队列和临床干预证据共同支持风险解释价值。", "个体治疗阈值和药物策略需结合总体风险。", "支持筛查和风险管理；药物治疗必须由医生决定。"),
        "dietary-pattern-longevity": ("饮食模式比单一补剂更适合作为对外健康建议框架。", "整体饮食质量、能量平衡和食物结构比单一成分更有解释力。", "不同文化和疾病背景下不能简单复制同一饮食方案。", "支持模式层面的建议，不支持神化单一食物或补剂。"),
        "sleep-aging": ("睡眠是认知、代谢、心血管和整体健康的重要基础变量。", "睡眠时长、质量和睡眠障碍与多类健康结局相关。", "因果方向和具体干预效果仍需区分。", "支持识别和管理睡眠问题；严重失眠、睡眠呼吸暂停需医疗评估。"),
        "glp1-weight-cardiometabolic": ("临床证据增长很快，主要价值在肥胖、糖代谢和心代谢风险管理。", "人体试验和真实世界研究显示体重、糖代谢和心血管相关收益。", "长期安全性、停药维持和非适应证使用边界仍需谨慎。", "这是医疗主题，不是普通抗衰保健建议；必须医生监督。"),
        "caloric-restriction-human": ("人体证据有价值但边界明显，不能直接等同于延寿已证实。", "更适合讨论代谢、风险因子和生物标志物改善。", "长期依从性、安全性、肌肉骨骼影响和真实寿命终点仍不充分。", "不建议盲目长期极端节食；需关注营养充足和个体风险。"),
        "time-restricted-eating": ("可作为代谢健康候选策略，但证据强度和适用人群仍不稳定。", "部分研究提示体重、胰岛素敏感性或进食行为改善。", "与热量减少的独立作用、长期效果和不良反应仍需复核。", "糖尿病、孕期、进食障碍或用药人群不应自行尝试。"),
    }
    return positions.get(topic_id, (f"{title_zh} 是重要候选方向，但公开结论必须区分成熟证据、机制线索和过度解读。", "当前证据可用于建立候选主题和复核优先级。", "终点硬度、人群外推、长期安全性和因果关系仍需全文复核。", "不支持把候选证据写成个人医疗、补剂或抗衰处方。"))


def write_topic_pages_and_topics(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    topics = []
    for topic_id, items in sorted(grouped(rows).items(), key=lambda kv: kv[0]):
        items = sorted(items, key=level_rank)
        first = items[0]
        position, know, uncertain, boundary = topic_position(topic_id, first["topic_zh"])
        lines = [
            f"# {first['topic_zh']} / {first['topic_en']}",
            "",
            f"> {DRAFT_NOTICE_ZH}",
            f"> {DRAFT_NOTICE_EN}",
            "",
            "## 一句话结论 / One-Sentence Conclusion",
            "",
            f"{position}",
            "",
            f"Draft summary: this topic now includes {len(items)} records; final public claims still require full-text review.",
            "",
            "## 当前证据等级 / Current Evidence Level",
            "",
            f"- Highest final evidence level: `{top_level(items)}`",
            f"- Median quality confidence score: `{median_quality(items)}`",
            "- Status: public draft, not fully reviewed",
            "",
            "## 我们知道什么 / What We Know",
            "",
            f"- {know}",
        ]
        for row in items[:8]:
            lines.append(f"- {row['claim_supported_zh']} / {row['claim_supported_en']}")
        lines.extend([
            "",
            "## 仍不确定什么 / What Remains Uncertain",
            "",
            f"- {uncertain}",
            "- 自动抽取结果仍需阅读全文确认研究设计、样本量、终点定义、效应量、偏倚风险和利益冲突。",
            "- Metadata-only or abstract-only records cannot support final effect claims.",
            "",
            "## 不能这么说 / What Not To Claim",
            "",
            f"- {boundary}",
        ])
        for row in items[:8]:
            lines.append(f"- {row['claim_not_supported_zh']} / {row['claim_not_supported_en']}")
        lines.extend(["", "## 相关论文卡片 / Related Paper Cards", ""])
        for row in items:
            lines.append(f"- [{row['title_en']}](../papers/{slug(row['candidate_id'])}.md) ({row['year']}, {row['journal']})")
        (TOPICS_DIR / f"{topic_id}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        topics.append({
            "topic_id": topic_id,
            "title_zh": first["topic_zh"],
            "title_en": first["topic_en"],
            "scope": "Public draft topic generated from v0.5 1800-record expansion; full-text review required.",
            "evidence_summary_zh": position,
            "evidence_summary_en": f"Public draft topic with {len(items)} records; full-text review required.",
            "status": "public_draft_not_fully_reviewed",
            "paper_count": str(len(items)),
            "last_checked": TODAY,
        })
    return topics


def build_public_summary(rows: list[dict[str, str]], matrix: list[dict[str, str]]) -> list[dict[str, str]]:
    by_topic = grouped(rows)
    matrix_by_topic: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in matrix:
        matrix_by_topic[row.get("topic", "")].append(row)
    out = []
    order = [
        "cardiorespiratory-fitness", "physical-activity-healthspan", "resistance-training-muscle",
        "blood-pressure-aging", "ldl-apob-cardiovascular-risk", "dietary-pattern-longevity",
        "sleep-aging", "glp1-weight-cardiometabolic", "caloric-restriction-human", "time-restricted-eating",
        "metformin-aging", "rapamycin-mtor-aging", "senolytics", "nad-nmn-nr-aging", "epigenetic-clocks",
        "itp-mouse-lifespan", "klotho-il11-aging", "partial-reprogramming", "autophagy-mitophagy", "microbiome-inflammaging",
    ]
    for i, topic_id in enumerate(order, 1):
        items = by_topic.get(topic_id, [])
        if not items:
            continue
        first = items[0]
        position, know, uncertain, boundary = topic_position(topic_id, first["topic_zh"])
        out.append({
            "summary_id": f"summary-{i:02d}-{topic_id}",
            "topic_id": topic_id,
            "title_zh": first["topic_zh"],
            "title_en": first["topic_en"],
            "current_public_position_zh": position,
            "current_public_position_en": f"Public draft position for {first['topic_en']}; see bilingual topic page for evidence boundaries.",
            "evidence_level_top": top_level(items),
            "recommendation_boundary": recommendation_boundary(topic_id),
            "finding_count": str(len(items)),
            "formal_matrix_count": str(sum(1 for m in matrix if m["topic"] == first["topic_zh"])),
            "pmc_or_abstract_count": str(sum(1 for r in items if r.get("evidence_source_depth") != "metadata_only")),
            "metadata_only_count": str(sum(1 for r in items if r.get("evidence_source_depth") == "metadata_only")),
            "what_we_know_zh": know,
            "what_remains_uncertain_zh": uncertain,
            "reader_boundary_zh": boundary,
            "github_topic_path": f"content/topics/{topic_id}.md",
            "status": "public_draft_not_fully_reviewed",
            "last_checked": TODAY,
            "domain": "longevity_healthspan",
            "entry_type": "topic_summary",
            "quality_confidence_median": str(median_quality(items)),
            "scoring_version": "v0.5_expanded_selection_plus_v0.4_scoring",
        })
    return out


def write_public_summary_md(summary_rows: list[dict[str, str]]) -> None:
    total_findings = sum(safe_int(r["finding_count"]) for r in summary_rows)
    total_matrix = sum(safe_int(r["formal_matrix_count"]) for r in summary_rows)
    lines = [
        "# 长寿抗衰与健康寿命证据图谱：公开总览 / Public Summary",
        "",
        f"> {DRAFT_NOTICE_ZH}",
        f"> {DRAFT_NOTICE_EN}",
        "",
        "## 总览窗口 / Summary Window",
        "",
        "这个页面是对外阅读的第一入口：先看我们认为哪些方向相对成熟、哪些方向仍然早期，再进入主题页、论文卡片和数据表。完整评分方法见 [证据评分方法 v0.4](evidence-scoring-v0-4.md)，质量仪表盘见 [证据质量总览](evidence-quality-dashboard.md)。",
        "",
        "## 图谱入口 / Atlas Entrypoints",
        "",
        "| 图谱 | 回答的问题 | 入口 |",
        "|---|---|---|",
        "| 健康寿命证据图谱 | 死亡、疾病、功能、代谢、药物、机制和健康寿命边界。 | [公开总览](public-summary.md) |",
        "| 外观抗老与皮肤健康证据图谱 | 光老化、皱纹、色斑、屏障、水分、医美和皮肤安全边界。 | [皮肤美容总览](skin-beauty-summary.md) |",
        "| 补剂证据矩阵 | 同一补剂对健康寿命和皮肤美容的证据强弱、不能宣传什么。 | [补剂矩阵](supplement-summary.md) |",
        "",
        "## 一句话说明",
        "",
        "这是一个中英双语、证据优先、可审计的长寿抗衰与健康寿命证据图谱。它不是药物、补剂或剂量推荐清单，而是把运动、心代谢、饮食、睡眠、药物、补剂和前沿 geroscience 技术按证据等级、终点价值和可转化边界重新整理。",
        "",
        "In short: this atlas separates mature healthspan evidence from early mechanistic or animal evidence, and makes the boundary visible before readers reach individual papers.",
        "",
        "## 当前版本说了什么",
        "",
        f"- 当前公开草稿覆盖 20 个健康寿命主题、{total_findings} 条 finding、{total_matrix} 条正式纳入候选记录。",
        "- 本轮扩容采用“高权重期刊优先 + 系统综述/Meta/RCT/队列/MR 优先 + 主题均衡”的策略。",
        "- 最稳健的方向仍主要集中在心肺适能、身体活动、抗阻训练、血压、LDL-C/apoB、饮食模式和睡眠等公共健康或临床风险管理主题。",
        "- 前沿药物、补剂和 geroscience 技术保留为研究方向，但不会被写成普通人可以自行执行的抗衰建议。",
        "",
        "## 不能这么说",
        "",
        "- 不能说某种药物、补剂或技术已经被证明可以让健康人延寿。",
        "- 不能把动物寿命实验直接写成人类延寿结论。",
        "- 不能把 biomarker 或表观遗传时钟改善直接写成“逆龄已证实”。",
        "- 不能根据单篇摘要给出剂量、处方或个人医疗建议。",
        "",
        "## 主题总览表",
        "",
        "| # | 主题 | 当前立场 | v0.4/v0.5 等级 | 记录数 | 中位质量分 | 边界 |",
        "|---:|---|---|---|---:|---:|---|",
    ]
    for i, row in enumerate(summary_rows, 1):
        lines.append(f"| {i} | [{row['title_zh']}](../topics/{row['topic_id']}.md)<br>{row['title_en']} | {row['current_public_position_zh']} | {row['evidence_level_top']} | {row['finding_count']} | {row.get('quality_confidence_median','')} | {row['reader_boundary_zh']} |")
    lines.extend([
        "",
        "## 证据等级和评分方法",
        "",
        "本项目使用 `v0.4_GRADE_RoB_AMSTAR_bibliometrics` 评分，并在 v0.5 扩容中加入高权重期刊/核心研究设计优先选取。公开等级综合研究设计、终点价值、人类相关性、来源深度、NIH iCite RCR、OpenAlex 引用数、偏倚风险工具、商业过度宣传风险和等级上限规则。",
        "",
        "- 方法全文：[证据评分方法 v0.4](evidence-scoring-v0-4.md)",
        "- 质量总览：[证据质量总览](evidence-quality-dashboard.md)",
        f"- 更新时间：{TODAY}",
        "",
        "特别说明：JCR Impact Factor 当前没有自动导入，也不会被伪造。IF 若后续由授权来源导入，只作为影响力信号之一，不替代 GRADE/RoB/AMSTAR 和终点硬度判断。",
        "",
        "## 内部管理方式",
        "",
        "- GitHub 是事实源：CSV、Markdown、方法学和脚本都从这里维护。",
        "- 飞书是展示和协作层：对外总览、主题库、候选文献、文献总表和发布日志用于筛选、复核和同步。",
        "- 正式发布前，应优先复核 `final_evidence_level=A/B`、终点较硬、`quality_confidence_score` 较高且偏倚风险已人工评估的记录。",
    ])
    PUBLIC_SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_analysis_and_recs(matrix: list[dict[str, str]]) -> None:
    rows = sorted(matrix, key=lambda row: ({"A": 0, "B": 1, "C": 2, "D": 3, "E": 4}.get(row["evidence_level"], 9), -safe_int(row.get("quality_confidence_score"))))
    lines = [
        "# 长寿抗衰证据排行 / Longevity Evidence Ranking",
        "",
        f"> {DRAFT_NOTICE_ZH}",
        f"> {DRAFT_NOTICE_EN}",
        "",
        "| Rank | Topic | Evidence | Quality | Endpoint | Recommendation | Medical supervision | Summary |",
        "|---:|---|---|---:|---|---|---|---|",
    ]
    for i, row in enumerate(rows[:180], 1):
        lines.append(f"| {i} | {row['topic']} | {row['evidence_level']} | {row.get('quality_confidence_score','')} | {row['endpoint_class']} | {row['recommendation_class']} | {row['medical_supervision']} | {row['zh_summary'][:240]} |")
    ANALYSIS.write_text("\n".join(lines) + "\n", encoding="utf-8")

    strong = [row for row in matrix if row["recommendation_class"] == "Strong Action"]
    medical = [row for row in matrix if row["recommendation_class"] == "Medical Action"]
    monitor = [row for row in matrix if row["recommendation_class"] == "Monitor"]
    rec_lines = [
        "# 普通读者建议边界 / Boundaries for General Readers",
        "",
        f"> {DRAFT_NOTICE_ZH}",
        f"> {DRAFT_NOTICE_EN}",
        "",
        "本页不是医疗建议，不提供药物、补剂、剂量或治疗方案。它只说明哪些主题在证据图谱中更值得优先复核。",
        "",
        "## 可作为健康行为优先复核的方向",
        "",
    ]
    for row in strong[:30]:
        rec_lines.append(f"- {row['topic']}: {row['claim_supported']}")
    rec_lines.extend(["", "## 需要医生评估或监督", ""])
    for row in medical[:30]:
        rec_lines.append(f"- {row['topic']}: {row['claim_supported']}")
    rec_lines.extend(["", "## 只观察，不建议自行实践", ""])
    for row in monitor[:50]:
        rec_lines.append(f"- {row['topic']}: {row['claim_supported']}")
    RECOMMENDATIONS.write_text("\n".join(rec_lines) + "\n", encoding="utf-8")


def write_status(rows: list[dict[str, str]], matrix: list[dict[str, str]], topics: list[dict[str, str]]) -> None:
    lines = [
        "# Current Output Status / 当前输出状态",
        "",
        f"Date / 日期: {TODAY}",
        "",
        "## Production Draft Assets / 可发布草稿资产",
        "",
        "- Candidate pool: expanded by v0.5 PubMed high-weight/high-design search.",
        f"- Finding extraction layer: {len(rows)} healthspan/longevity finding records.",
        f"- Topic drafts: {len(topics)} public draft topic pages.",
        f"- Paper-card drafts: {len(rows)} public draft paper pages.",
        f"- Evidence matrix: {len(matrix)} cautious draft inclusion records.",
        "",
        "## Public Caveat / 公开警示",
        "",
        f"- {DRAFT_NOTICE_ZH}",
        f"- {DRAFT_NOTICE_EN}",
    ]
    STATUS_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix-limit", type=int, default=900)
    parser.add_argument(
        "--matrix-per-topic-cap",
        type=int,
        default=0,
        help="Optional maximum rows per topic; zero keeps the historical global ranking behavior.",
    )
    args = parser.parse_args()
    rows = read_csv(FINDINGS)
    clean_generated_pages()
    shortlist = build_shortlist(rows)
    write_csv(SHORTLIST, shortlist, list(shortlist[0].keys()))
    matrix = build_matrix(rows, args.matrix_limit, args.matrix_per_topic_cap)
    write_csv(MATRIX, matrix, list(matrix[0].keys()))
    write_paper_pages(rows)
    topics = write_topic_pages_and_topics(rows)
    write_csv(TOPICS_CSV, topics, list(topics[0].keys()))
    summary = build_public_summary(rows, matrix)
    write_csv(PUBLIC_SUMMARY_CSV, summary, list(summary[0].keys()))
    write_public_summary_md(summary)
    write_analysis_and_recs(matrix)
    write_status(rows, matrix, topics)
    print(f"Wrote {len(rows)} paper pages, {len(topics)} topic pages, {len(matrix)} evidence matrix rows, and {len(summary)} summary rows.")


if __name__ == "__main__":
    main()
