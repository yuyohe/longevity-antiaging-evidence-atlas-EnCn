from __future__ import annotations

import csv
import json
import math
import os
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CONTENT = ROOT / "content"
CACHE = ROOT / "build" / "cache"
CACHE.mkdir(parents=True, exist_ok=True)

TODAY = os.environ.get("EVIDENCE_ATLAS_UPDATE_DATE", "2026-04-28")
METHOD_MD = CONTENT / "overview" / "evidence-scoring-v0-4.md"
METHOD_CSV = DATA / "scoring_policy_v0_4.csv"
SUMMARY_WINDOW_MD = CONTENT / "overview" / "public-summary.md"
QUALITY_DASHBOARD = CONTENT / "overview" / "evidence-quality-dashboard.md"


SCORING_COLUMNS = [
    "scoring_version",
    "design_score",
    "endpoint_value_score",
    "human_relevance_score",
    "source_depth_score",
    "authority_signal_score",
    "risk_adjustment_score",
    "quality_confidence_score",
    "influence_score",
    "journal_metric_source",
    "journal_metric_value",
    "journal_metric_note",
    "openalex_work_id",
    "openalex_cited_by_count",
    "icite_rcr",
    "risk_of_bias_tool",
    "risk_of_bias_rating",
    "amstar2_rating",
    "funding_conflict_risk",
    "industry_funding_risk",
    "confidence_cap_rule",
    "final_evidence_level",
    "scoring_note_zh",
    "scoring_note_en",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], preferred_fields: list[str] | None = None) -> None:
    fields: list[str] = []
    if preferred_fields:
        fields.extend(preferred_fields)
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def request_json(url: str, timeout: int = 20) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "longevity-evidence-atlas/0.4 (mailto:example@example.com)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def batch_icite(pmids: Iterable[str]) -> dict[str, dict]:
    cache_path = CACHE / "icite_rcr_cache.json"
    cache = load_json(cache_path)
    if os.environ.get("SCORING_FETCH_EXTERNAL", "0") != "1":
        return cache
    missing = [p for p in sorted(set(pmids)) if p and p not in cache]
    for start in range(0, len(missing), 900):
        batch = missing[start : start + 900]
        if not batch:
            continue
        url = "https://icite.od.nih.gov/api/pubs?pmids=" + ",".join(batch)
        try:
            data = request_json(url)
            for item in data.get("data", []):
                pmid = str(item.get("pmid", ""))
                if pmid:
                    cache[pmid] = item
        except Exception as exc:
            for pmid in batch:
                cache.setdefault(pmid, {"_error": str(exc)})
        time.sleep(0.25)
    save_json(cache_path, cache)
    return cache


def openalex_lookup(rows: list[dict[str, str]]) -> dict[str, dict]:
    cache_path = CACHE / "openalex_work_cache.json"
    cache = load_json(cache_path)
    if os.environ.get("SCORING_FETCH_EXTERNAL", "0") != "1":
        return cache
    targets: list[tuple[str, str]] = []
    for row in rows:
        key = row_key(row)
        if key in cache:
            continue
        doi = clean_doi(row.get("doi", ""))
        pmid = row.get("pmid", "")
        if doi:
            targets.append((key, f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi, safe='')}"))
        elif pmid:
            filt = urllib.parse.quote(f"ids.pmid:{pmid}")
            targets.append((key, f"https://api.openalex.org/works?filter={filt}&per-page=1"))
    for i, (key, url) in enumerate(targets, 1):
        try:
            data = request_json(url)
            if "results" in data:
                work = data.get("results", [{}])[0] if data.get("results") else {}
            else:
                work = data
            cache[key] = {
                "id": work.get("id", ""),
                "cited_by_count": work.get("cited_by_count", ""),
                "source": (work.get("primary_location") or {}).get("source") or {},
            }
        except Exception as exc:
            cache[key] = {"_error": str(exc)}
        if i % 20 == 0:
            save_json(cache_path, cache)
            time.sleep(0.25)
    save_json(cache_path, cache)
    return cache


def clean_doi(value: str) -> str:
    value = (value or "").strip()
    value = value.removeprefix("https://doi.org/").removeprefix("http://dx.doi.org/")
    return value


def row_key(row: dict[str, str]) -> str:
    return row.get("pmid") or clean_doi(row.get("doi", "")) or row.get("candidate_id") or row.get("finding_id") or row.get("supplement_id", "")


def design_score(study_type: str) -> int:
    s = (study_type or "").lower()
    if "systematic_review" in s or "meta_analysis" in s or "meta-analysis" in s:
        return 34
    if "randomized" in s or "clinical_trial" in s or "clinical trial" in s:
        return 29
    if "cohort" in s:
        return 24
    if "observational" in s or "human_or_mixed" in s:
        return 18
    if "animal" in s or "preclinical" in s:
        return 11
    if "mechanistic" in s or "cell" in s:
        return 8
    if "review" in s:
        return 14
    return 7


def endpoint_score(endpoint: str, domain: str) -> int:
    e = (endpoint or "").upper()
    if e in {"H1", "L1"}:
        return 25
    if e in {"H2", "L2"}:
        return 20
    if e in {"H3"}:
        return 14
    if e in {"H4", "H5"}:
        return 9
    if e == "S1":
        return 15
    if e == "S2":
        return 8
    return 5 if domain != "supplement" else 7


def human_score(species: str, study: str, domain: str) -> int:
    s = f"{species} {study}".lower()
    if "human" in s or "clinical" in s or "cohort" in s or "randomized" in s:
        return 15
    if "animal" in s or "mouse" in s or "mice" in s:
        return 6
    if "cell" in s or "mechanistic" in s:
        return 3
    return 9 if domain == "skin" else 6


def source_depth_score(depth: str, row: dict[str, str]) -> int:
    d = (depth or "").lower()
    if "open_pmc" in d or row.get("pmcid"):
        return 10
    if "abstract" in d:
        return 7
    if row.get("pmid") or row.get("doi"):
        return 5
    return 1


def authority_score(row: dict[str, str], icite: dict, openalex: dict) -> tuple[int, int, str, str, str, str, str]:
    pmid = row.get("pmid", "")
    ic = icite.get(pmid, {}) if pmid else {}
    rcr = ic.get("relative_citation_ratio", "")
    oa = openalex.get(row_key(row), {})
    cited = oa.get("cited_by_count", "")
    work_id = oa.get("id", "")
    points = 0
    influence = 0
    try:
        rcr_float = float(rcr)
        if rcr_float >= 5:
            points += 10
        elif rcr_float >= 2:
            points += 8
        elif rcr_float >= 1:
            points += 5
        else:
            points += 1
        influence += min(15, int(math.log1p(max(rcr_float, 0)) * 7))
    except Exception:
        rcr = ""
    try:
        cited_int = int(cited)
        if cited_int >= 500:
            points += 8
        elif cited_int >= 100:
            points += 6
        elif cited_int >= 25:
            points += 4
        elif cited_int > 0:
            points += 2
        influence += min(15, int(math.log1p(max(cited_int, 0)) * 3))
    except Exception:
        cited = ""
    if row.get("doi"):
        points += 2
    if row.get("pmid"):
        points += 2
    if row.get("pmcid"):
        points += 2
    source = "NIH_iCite_RCR; OpenAlex_cited_by_count"
    value = f"RCR={rcr or 'NA'}; cited_by={cited or 'NA'}"
    note = "JCR IF not auto-imported; journal-level IF is intentionally separated from article-level citation signals."
    return min(20, points), min(30, influence), source, value, note, str(work_id or ""), str(cited or "")


def risk_adjustment(row: dict[str, str], domain: str) -> tuple[int, str, str, str, str, str]:
    text = " ".join(str(v) for v in row.values()).lower()
    study = (row.get("study_type_draft") or row.get("study_type") or "").lower()
    topic = row.get("topic_id", "")
    commercial = row.get("commercial_overclaim_risk", "")
    risk = 0
    funding_risk = "not_assessed"
    industry_risk = "not_assessed"
    if "industry" in text or "sponsor" in text or commercial == "high":
        risk -= 8
        industry_risk = "possible_or_high"
    elif commercial == "medium":
        risk -= 3
        industry_risk = "possible"
    if "metadata_only" in text:
        risk -= 12
    if "abstract_only" in text:
        risk -= 4
    if domain == "skin" and topic in {"oral-collagen-peptides", "polyphenols-skin-photoprotection"}:
        risk -= 8
        industry_risk = "high_commercial_overclaim_risk"
    if domain == "supplement" and row.get("commercial_overclaim_risk") == "high":
        risk -= 8
        industry_risk = "high_commercial_overclaim_risk"
    if "systematic_review" in study or "meta_analysis" in study:
        tool, rob, amstar = "AMSTAR 2", "not_assessed_public_draft", "not_assessed_public_draft"
    elif "randomized" in study or "clinical" in study:
        tool, rob, amstar = "Cochrane RoB 2", "not_assessed_public_draft", "not_applicable"
    elif "cohort" in study or "observational" in study:
        tool, rob, amstar = "ROBINS-I", "not_assessed_public_draft", "not_applicable"
    else:
        tool, rob, amstar = "domain_screen", "not_assessed_public_draft", "not_applicable"
    if industry_risk == "not_assessed":
        funding_risk = "not_assessed_public_draft"
    else:
        funding_risk = industry_risk
    return risk, tool, rob, amstar, funding_risk, industry_risk


def level_from_score(score: int, cap: str) -> str:
    raw = "A" if score >= 82 else "B" if score >= 66 else "C" if score >= 48 else "D" if score >= 30 else "E"
    order = ["A", "B", "C", "D", "E"]
    return order[max(order.index(raw), order.index(cap))] if cap in order else raw


def confidence_cap(row: dict[str, str], domain: str) -> str:
    study = (row.get("study_type_draft") or row.get("study_type") or "").lower()
    endpoint = (row.get("endpoint_class_draft") or row.get("endpoint_class") or "").upper()
    depth = (row.get("evidence_source_depth") or "").lower()
    topic = row.get("topic_id", "")
    if "metadata_only" in depth:
        return "D"
    if "animal" in study or "preclinical" in study or "mechanistic" in study or endpoint in {"S2", "M", "H6"}:
        return "D"
    if domain == "skin":
        if topic in {"oral-collagen-peptides", "polyphenols-skin-photoprotection", "hyaluronic-acid-ceramides-hydration"}:
            return "B"
        if endpoint == "S1" and ("systematic_review" in study or "meta_analysis" in study):
            return "B"
    if domain == "supplement":
        if row.get("commercial_overclaim_risk") == "high" or row.get("skin_endpoint_class") in {"S1", "S2", "M"}:
            return "B"
    return "A"


def score_row(row: dict[str, str], domain: str, icite: dict, openalex: dict) -> dict[str, str]:
    study = row.get("study_type_draft") or row.get("study_type") or row.get("category", "")
    endpoint = row.get("endpoint_class_draft") or row.get("endpoint_class") or row.get("longevity_endpoint_class") or row.get("skin_endpoint_class") or ""
    species = row.get("species_draft") or row.get("species") or ""
    depth = row.get("evidence_source_depth") or row.get("source", "")
    ds = design_score(study)
    es = endpoint_score(endpoint, domain)
    hs = human_score(species, study, domain)
    ss = source_depth_score(depth, row)
    auth, influence, metric_source, metric_value, metric_note, work_id, cited = authority_score(row, icite, openalex)
    risk, rob_tool, rob_rating, amstar, funding, industry = risk_adjustment(row, domain)
    score = max(0, min(100, ds + es + hs + ss + auth + risk))
    cap = confidence_cap(row, domain)
    final = level_from_score(score, cap)
    row.update({
        "scoring_version": "v0.4_GRADE_RoB_AMSTAR_bibliometrics",
        "design_score": str(ds),
        "endpoint_value_score": str(es),
        "human_relevance_score": str(hs),
        "source_depth_score": str(ss),
        "authority_signal_score": str(auth),
        "risk_adjustment_score": str(risk),
        "quality_confidence_score": str(score),
        "influence_score": str(influence),
        "journal_metric_source": metric_source,
        "journal_metric_value": metric_value,
        "journal_metric_note": metric_note,
        "openalex_work_id": work_id,
        "openalex_cited_by_count": cited,
        "icite_rcr": metric_value.split("RCR=")[-1].split(";")[0].replace("NA", ""),
        "risk_of_bias_tool": rob_tool,
        "risk_of_bias_rating": rob_rating,
        "amstar2_rating": amstar,
        "funding_conflict_risk": funding,
        "industry_funding_risk": industry,
        "confidence_cap_rule": f"max_level_{cap}",
        "final_evidence_level": final,
        "scoring_note_zh": f"v0.4 综合评分：研究设计、终点价值、人类相关性、来源深度、RCR/OpenAlex 引用信号和风险扣分；当前上限规则为 max_level_{cap}，最终等级 {final}。",
        "scoring_note_en": f"v0.4 hybrid score using design, endpoint value, human relevance, source depth, RCR/OpenAlex signals, and risk adjustments; cap rule max_level_{cap}; final level {final}.",
    })
    return row


def score_supplement(row: dict[str, str]) -> dict[str, str]:
    base = {"A": 78, "B": 64, "C": 48, "D": 32, "E": 20}.get(row.get("longevity_evidence_level"), 32)
    skin_base = {"A": 72, "B": 58, "C": 44, "D": 30, "E": 18}.get(row.get("skin_beauty_evidence_level"), 30)
    commercial = row.get("commercial_overclaim_risk")
    risk = -10 if commercial == "high" else -4 if commercial == "medium" else 0
    score = max(0, min(100, round((base + skin_base) / 2 + risk)))
    cap = confidence_cap(row, "supplement")
    final = level_from_score(score, cap)
    row.update({
        "scoring_version": "v0.4_GRADE_RoB_AMSTAR_bibliometrics",
        "design_score": "not_article_level",
        "endpoint_value_score": "mixed_longevity_skin",
        "human_relevance_score": "topic_level",
        "source_depth_score": "topic_level",
        "authority_signal_score": "pending_source_review",
        "risk_adjustment_score": str(risk),
        "quality_confidence_score": str(score),
        "influence_score": "pending_article_mapping",
        "journal_metric_source": "not_applicable_topic_level",
        "journal_metric_value": "",
        "journal_metric_note": "Supplement matrix is topic-level; article-level IF/RCR/citations belong in linked findings.",
        "openalex_work_id": "",
        "openalex_cited_by_count": "",
        "icite_rcr": "",
        "risk_of_bias_tool": "GRADE_topic_profile",
        "risk_of_bias_rating": "not_assessed_public_draft",
        "amstar2_rating": "not_applicable_topic_level",
        "funding_conflict_risk": "high_commercial_overclaim_risk" if commercial == "high" else "not_assessed_public_draft",
        "industry_funding_risk": "high_commercial_overclaim_risk" if commercial == "high" else "not_assessed_public_draft",
        "confidence_cap_rule": f"max_level_{cap}",
        "final_evidence_level": final,
        "scoring_note_zh": f"补剂矩阵为主题级评分，不能替代单篇研究复核；商业过度宣传风险为 {commercial}，最终综合等级 {final}。",
        "scoring_note_en": f"Topic-level supplement score; not a substitute for article-level review. Commercial overclaim risk={commercial}; final level {final}.",
    })
    if row.get("supplement_id") in {"collagen-peptides", "oral-collagen", "marine-collagen"} or "胶原" in row.get("name_zh", ""):
        row["skin_beauty_evidence_level"] = "C"
        row["quality_confidence_score"] = str(min(int(row["quality_confidence_score"]), 52))
        row["final_evidence_level"] = "C"
        row["confidence_cap_rule"] = "max_level_C_for_oral_collagen_soft_endpoints_and_commercial_overclaim"
        row["scoring_note_zh"] = "口服胶原按 v0.4 降级：以皮肤水分/弹性等软终点为主，研究异质性和商业过度宣传风险较高，公开总览不列为 A。"
    return row


def update_evidence_matrix(findings: list[dict[str, str]]) -> None:
    path = DATA / "evidence_matrix.csv"
    rows = read_csv(path)
    by_id = {r.get("candidate_id"): r for r in findings}
    for row in rows:
        src = by_id.get(row.get("paper_id"))
        if not src:
            continue
        row["evidence_level"] = src.get("final_evidence_level", row.get("evidence_level", ""))
        row["risk_of_bias"] = src.get("risk_of_bias_rating", row.get("risk_of_bias", ""))
        row["quality_confidence_score"] = src.get("quality_confidence_score", "")
        row["influence_score"] = src.get("influence_score", "")
        row["journal_metric_value"] = src.get("journal_metric_value", "")
        row["confidence_cap_rule"] = src.get("confidence_cap_rule", "")
        row["scoring_version"] = src.get("scoring_version", "")
        row["last_checked"] = TODAY
    write_csv(path, rows)


def update_skin_summary(findings: list[dict[str, str]]) -> None:
    path = DATA / "skin_beauty_summary.csv"
    rows = read_csv(path)
    by_topic: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in findings:
        by_topic[row.get("topic_id", "")].append(row)
    for row in rows:
        items = by_topic.get(row["topic_id"], [])
        if items:
            levels = Counter(i.get("final_evidence_level") or i.get("evidence_level_draft") for i in items)
            row["evidence_level_top"] = next((lvl for lvl in ["A", "B", "C", "D", "E"] if levels.get(lvl)), "pending")
            row["quality_confidence_median"] = str(round(median_int(i.get("quality_confidence_score") for i in items)))
            row["confidence_cap_summary"] = "; ".join(sorted(set(i.get("confidence_cap_rule", "") for i in items if i.get("confidence_cap_rule"))))
            row["scoring_version"] = "v0.4_GRADE_RoB_AMSTAR_bibliometrics"
            if row["topic_id"] == "oral-collagen-peptides":
                row["current_public_position_zh"] = "口服胶原肽对皮肤水分、弹性等软终点有候选证据，但异质性、商业化和终点临床意义限制较大；公开等级下调为 C。"
                row["reader_boundary_zh"] = "不支持把口服胶原写成逆龄、延寿或替代均衡蛋白摄入；需要看研究质量和利益冲突。"
        row["last_checked"] = TODAY
    write_csv(path, rows)


def median_int(values: Iterable[str]) -> int:
    nums = sorted(int(v) for v in values if str(v).isdigit())
    if not nums:
        return 0
    mid = len(nums) // 2
    return nums[mid] if len(nums) % 2 else round((nums[mid - 1] + nums[mid]) / 2)


def update_public_summary(findings: list[dict[str, str]]) -> None:
    path = DATA / "public_summary.csv"
    rows = read_csv(path)
    by_topic: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in findings:
        by_topic[row.get("topic_id", "")].append(row)
    for row in rows:
        items = by_topic.get(row.get("topic_id", ""), [])
        if items:
            levels = Counter(i.get("final_evidence_level") or i.get("evidence_level_draft") for i in items)
            row["evidence_level_top"] = next((lvl for lvl in ["A", "B", "C", "D", "E"] if levels.get(lvl)), row.get("evidence_level_top", ""))
            row["quality_confidence_median"] = str(round(median_int(i.get("quality_confidence_score") for i in items)))
            row["scoring_version"] = "v0.4_GRADE_RoB_AMSTAR_bibliometrics"
            row["reader_boundary_zh"] = row.get("reader_boundary_zh", "") + " 等级已按 v0.4 综合评分重算；A 不等于个人处方建议。"
        row["last_checked"] = TODAY
    write_csv(path, rows)


def write_policy_docs() -> None:
    rows = [
        {"rule_id": "framework", "name_zh": "总框架", "name_en": "Framework", "description_zh": "采用 GRADE 思路作为公开结论置信度框架，并把 Cochrane RoB 2、ROBINS-I、AMSTAR 2 作为后续全文复核工具。", "weight_or_rule": "rule"},
        {"rule_id": "design", "name_zh": "研究设计", "name_en": "Study design", "description_zh": "系统综述/Meta 分析、随机试验、队列、观察、动物/机制按层级给基础分；但不能单独决定 A/B/C/D。", "weight_or_rule": "0-34"},
        {"rule_id": "endpoint", "name_zh": "终点价值", "name_en": "Endpoint value", "description_zh": "死亡、疾病事件、骨折等硬终点最高；皮肤皱纹/水分/弹性属于 S1 软临床/仪器终点，不能等同延寿。", "weight_or_rule": "0-25"},
        {"rule_id": "human", "name_zh": "人类相关性", "name_en": "Human relevance", "description_zh": "人体 RCT、队列、临床研究优先；动物、细胞和机制研究设置等级上限。", "weight_or_rule": "0-15"},
        {"rule_id": "source_depth", "name_zh": "来源深度", "name_en": "Source depth", "description_zh": "开放全文/PMC、摘要、仅题录分层；仅题录记录不能进入高等级。", "weight_or_rule": "0-10"},
        {"rule_id": "bibliometrics", "name_zh": "影响力信号", "name_en": "Influence signals", "description_zh": "自动使用 NIH iCite RCR 和 OpenAlex cited_by_count。JCR IF/CiteScore/SJR 若有授权数据，可后续导入；默认不伪造 IF。", "weight_or_rule": "0-20 plus influence_score"},
        {"rule_id": "risk", "name_zh": "风险扣分", "name_en": "Risk adjustments", "description_zh": "摘要级、仅题录、商业过度宣传、可能行业资助、软终点外推等会扣分。", "weight_or_rule": "-0 to -20"},
        {"rule_id": "cap", "name_zh": "等级上限", "name_en": "Confidence caps", "description_zh": "动物/机制最高 D；仅题录最高 D；皮肤软终点系统综述通常最高 B；口服胶原、抗氧化补剂等高商业风险主题最高 C/B。", "weight_or_rule": "hard cap"},
        {"rule_id": "final_level", "name_zh": "最终等级", "name_en": "Final level", "description_zh": "quality_confidence_score 先映射 A/B/C/D/E，再应用上限规则得到 final_evidence_level。", "weight_or_rule": "A>=82, B>=66, C>=48, D>=30, else E"},
        {"rule_id": "if_policy", "name_zh": "IF 使用政策", "name_en": "Impact factor policy", "description_zh": "IF 是期刊层指标，不作为单篇研究质量的直接替代；若后续导入 JCR IF，只进入 authority_signal_score，不覆盖 RoB/GRADE。", "weight_or_rule": "optional external import"},
        {"rule_id": "update", "name_zh": "更新时间", "name_en": "Update date", "description_zh": f"本轮评分和公开说明更新时间：{TODAY}。", "weight_or_rule": TODAY},
    ]
    write_csv(METHOD_CSV, rows, ["rule_id", "name_zh", "name_en", "description_zh", "weight_or_rule"])
    METHOD_MD.write_text(f"""# 证据评分方法 v0.4 / Evidence Scoring Method v0.4

草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。  
Draft status: automatically prepared; not fully reviewed; not medical advice.

Last updated / 更新时间：{TODAY}

## 我们为什么重做评分

旧版本主要用“研究类型 + 终点类型”直接映射 A/B/C/D，容易把一篇系统综述或 Meta 分析自动抬到 A。这个做法对死亡、疾病等硬终点仍然偏粗，对外观抗老、补剂、口服胶原这类高商业化主题尤其危险。

v0.4 改为混合框架：**GRADE 作为公开结论置信度框架，Cochrane RoB 2 / ROBINS-I / AMSTAR 2 作为全文复核工具，NIH iCite RCR 与 OpenAlex 引用数作为可公开获得的影响力信号**。JCR Impact Factor、CiteScore、SJR 可以后续导入，但不会被伪造，也不会单独决定单篇研究质量。

## 评分组成 / Score Components

| 维度 | 权重/规则 | 说明 |
|---|---:|---|
| 研究设计 / Study design | 0-34 | 系统综述、RCT、队列、观察、动物/机制分层。 |
| 终点价值 / Endpoint value | 0-25 | 死亡/疾病硬终点最高；皮肤水分、弹性、皱纹为 S1 软临床/仪器终点。 |
| 人类相关性 / Human relevance | 0-15 | 人体证据优先；动物/细胞证据设置上限。 |
| 来源深度 / Source depth | 0-10 | 开放全文/摘要/仅题录分层。 |
| 权威与影响力信号 / Authority signals | 0-20 | DOI、PMID、PMCID、NIH iCite RCR、OpenAlex cited_by_count。 |
| 风险扣分 / Risk adjustments | 0 到 -20 | 仅摘要、仅题录、商业过度宣传、可能行业资助、软终点外推等扣分。 |
| 等级上限 / Confidence caps | hard cap | 动物/机制最高 D；仅题录最高 D；皮肤软终点和高商业风险主题不能仅凭 Meta 分析进入 A。 |

## 公开等级解释 / Public Level Meaning

| 等级 | 含义 |
|---|---|
| A | 高置信候选方向。通常需要硬终点或强人体证据、较低风险、足够来源深度和影响力信号。不是个人处方。 |
| B | 中高置信候选方向。适合进入公开总览，但需要边界和分层。 |
| C | 有信号但限制明显。常见于软终点、样本较小、异质性高或商业化风险高的主题。 |
| D | 机制、动物、仅题录、摘要不足或结论外推风险高。 |
| E | 证据不足或当前不宜支持公开结论。 |

## IF 政策 / Impact Factor Policy

我们目前没有自动使用 JCR Impact Factor。原因有三点：

1. JCR IF 通常需要授权，不应从非授权网页抓取或伪造。
2. IF 是期刊层指标，不等于单篇论文质量。
3. 国际上 DORA、Leiden Manifesto 等负责任指标原则均反对用单一期刊指标替代研究质量评价。

如果后续导入 JCR IF、CiteScore 或 SJR，它们只会作为 `authority_signal_score` 的一部分，并且会被 RoB/GRADE、终点硬度、来源深度和上限规则约束。

## 关键修正：口服胶原 / Oral Collagen

口服胶原肽当前不再因为“有系统综述/Meta 分析 + S1 皮肤终点”自动显示为 A。v0.4 将其降为 C：主要理由是终点多为皮肤水分、弹性、皱纹评分等软终点，研究异质性和商业过度宣传风险较高，不能外推为逆龄、延寿或替代均衡蛋白摄入。

## 数据字段 / Data Fields

本轮新增字段包括：`quality_confidence_score`, `influence_score`, `journal_metric_source`, `journal_metric_value`, `openalex_cited_by_count`, `icite_rcr`, `risk_of_bias_tool`, `risk_of_bias_rating`, `amstar2_rating`, `funding_conflict_risk`, `industry_funding_risk`, `confidence_cap_rule`, `final_evidence_level`。
""", encoding="utf-8")


def write_dashboard(longevity: list[dict[str, str]], skin: list[dict[str, str]], supplements: list[dict[str, str]]) -> None:
    def level_counts(rows: list[dict[str, str]]) -> str:
        c = Counter(r.get("final_evidence_level") or r.get("evidence_level_draft") for r in rows)
        return ", ".join(f"{k}:{c.get(k,0)}" for k in ["A", "B", "C", "D", "E"])
    collagen = [r for r in skin if r.get("topic_id") == "oral-collagen-peptides"]
    top_longevity = sorted(longevity, key=lambda r: int(r.get("quality_confidence_score") or 0), reverse=True)[:12]
    top_skin = sorted(skin, key=lambda r: int(r.get("quality_confidence_score") or 0), reverse=True)[:8]
    lines = [
        "# 证据质量总览 / Evidence Quality Dashboard",
        "",
        "草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。  ",
        "Draft status: automatically prepared; not fully reviewed; not medical advice.",
        "",
        f"Last updated / 更新时间：{TODAY}",
        "",
        "## 总览窗口 / Summary Window",
        "",
        f"- 健康寿命文献：{len(longevity)} 条；v0.4 等级分布：{level_counts(longevity)}。",
        f"- 外观抗老/皮肤文献：{len(skin)} 条；v0.4 等级分布：{level_counts(skin)}。",
        f"- 补剂证据矩阵：{len(supplements)} 个补剂/营养方向；v0.4 等级分布：{level_counts(supplements)}。",
        "- 对外阅读入口仍然是 `public-summary.md`，但每条记录现在可追踪到 v0.4 综合评分、影响力信号和上限规则。",
        "",
        "## 需要特别降温的结论 / Claims We Deliberately Downgrade",
        "",
        "- 皮肤美容指标改善不等于延寿、逆龄或疾病风险下降。",
        "- 口服胶原不列为 A。它属于软终点候选证据，当前公开等级为 C。",
        "- 补剂矩阵不提供剂量、品牌或购买建议。",
        "- 动物/细胞/机制证据不能直接写成人体健康寿命结论。",
        "",
        "## 口服胶原修正 / Oral Collagen Correction",
        "",
        f"- 口服胶原相关记录：{len(collagen)} 条。",
        f"- 修正后等级分布：{level_counts(collagen)}。",
        "- 公开表达：可能存在皮肤水分/弹性等候选信号，但临床意义、研究异质性、利益冲突和商业过度宣传风险必须显著标注。",
        "",
        "## 健康寿命高置信候选 / Higher-Confidence Longevity Candidates",
        "",
        "| 等级 | 分数 | 主题 | 年份 | 标题 |",
        "|---|---:|---|---:|---|",
    ]
    for r in top_longevity:
        lines.append(f"| {r.get('final_evidence_level')} | {r.get('quality_confidence_score')} | {r.get('topic_zh')} | {r.get('year')} | {safe_cell(r.get('title_en',''))} |")
    lines.extend([
        "",
        "## 皮肤/外观抗老高置信候选 / Higher-Confidence Skin Candidates",
        "",
        "| 等级 | 分数 | 主题 | 年份 | 标题 |",
        "|---|---:|---|---:|---|",
    ])
    for r in top_skin:
        lines.append(f"| {r.get('final_evidence_level')} | {r.get('quality_confidence_score')} | {r.get('topic_zh')} | {r.get('year')} | {safe_cell(r.get('title_en',''))} |")
    QUALITY_DASHBOARD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def safe_cell(text: str) -> str:
    return (text or "").replace("|", "/")[:120]


def refresh_public_summary_md() -> None:
    text = SUMMARY_WINDOW_MD.read_text(encoding="utf-8")
    marker = "## 证据等级和评分方法"
    insert = f"""## 证据等级和评分方法

本项目已升级到 `v0.4_GRADE_RoB_AMSTAR_bibliometrics`：公开等级不再只看研究类型，而是综合研究设计、终点价值、人类相关性、来源深度、NIH iCite RCR、OpenAlex 引用数、偏倚风险工具、商业过度宣传风险和等级上限规则。

- 方法全文：[证据评分方法 v0.4](evidence-scoring-v0-4.md)
- 质量总览：[证据质量总览](evidence-quality-dashboard.md)
- 更新时间：{TODAY}

特别说明：JCR Impact Factor 当前没有自动导入，也不会被伪造。IF 若后续由授权来源导入，只作为影响力信号之一，不替代 GRADE/RoB/AMSTAR 和终点硬度判断。

"""
    if marker in text:
        before = text.split(marker)[0].rstrip()
        after = text.split(marker, 1)[1]
        next_marker = "\n## "
        if next_marker in after:
            after = after[after.index(next_marker) + 1 :]
        else:
            after = ""
        text = before + "\n\n" + insert + after
    else:
        text = text.rstrip() + "\n\n" + insert
    SUMMARY_WINDOW_MD.write_text(text, encoding="utf-8")


def main() -> None:
    longevity_path = DATA / "evidence_findings.csv"
    skin_path = DATA / "skin_beauty_findings.csv"
    supplement_path = DATA / "supplement_matrix.csv"
    longevity = read_csv(longevity_path)
    skin = read_csv(skin_path)
    supplements = read_csv(supplement_path)
    article_rows = longevity + skin
    pmids = [r.get("pmid", "") for r in article_rows if r.get("pmid")]
    print(f"Loading bibliometrics for {len(pmids)} PMID-bearing records...")
    icite = batch_icite(pmids)
    print("Loading OpenAlex citation signals...")
    openalex = openalex_lookup(article_rows)
    print("Scoring longevity findings...")
    longevity = [score_row(dict(row), "longevity", icite, openalex) for row in longevity]
    print("Scoring skin findings...")
    skin = [score_row(dict(row), "skin", icite, openalex) for row in skin]
    print("Scoring supplement matrix...")
    supplements = [score_supplement(dict(row)) for row in supplements]
    write_csv(longevity_path, longevity)
    write_csv(skin_path, skin)
    write_csv(supplement_path, supplements)
    update_evidence_matrix(longevity)
    update_skin_summary(skin)
    update_public_summary(longevity)
    write_policy_docs()
    write_dashboard(longevity, skin, supplements)
    refresh_public_summary_md()
    print("Done: v0.4 scoring applied.")


if __name__ == "__main__":
    main()
