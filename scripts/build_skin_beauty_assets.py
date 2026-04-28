"""Build the skin/appearance aging atlas and supplement evidence matrix."""

from __future__ import annotations

import csv
import os
import time
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
DRAFT_NOTICE_ZH = "草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。"
DRAFT_NOTICE_EN = "Draft status: automatically prepared; not fully reviewed; not medical advice."

SKIN_FINDINGS = ROOT / "data" / "skin_beauty_findings.csv"
SKIN_TOPICS = ROOT / "data" / "skin_beauty_topics.csv"
SKIN_SUMMARY = ROOT / "data" / "skin_beauty_summary.csv"
SUPPLEMENTS = ROOT / "data" / "supplement_matrix.csv"
SKIN_MD = ROOT / "content" / "overview" / "skin-beauty-summary.md"
SUPPLEMENT_MD = ROOT / "content" / "overview" / "supplement-summary.md"
SKIN_TOPIC_DIR = ROOT / "content" / "skin-beauty-topics"

TOPICS: list[dict[str, Any]] = [
    {
        "topic_id": "sunscreen-photoaging-prevention",
        "title_zh": "防晒与光老化预防",
        "title_en": "Sunscreen and Photoaging Prevention",
        "query": '("sunscreen"[Title/Abstract] OR "sun protection"[Title/Abstract]) AND ("photoaging"[Title/Abstract] OR "skin aging"[Title/Abstract] OR wrinkle*[Title/Abstract])',
        "position": "防晒是外观抗老中最基础、最可转化的预防方向，主要目标是减少紫外线相关光老化和色素问题。",
        "boundary": "支持长期防晒作为皮肤健康基础；不支持把防晒写成逆龄治疗。",
        "intervention_type": "lifestyle_topical",
    },
    {
        "topic_id": "retinoids-photoaging",
        "title_zh": "维A酸/视黄醇类与光老化",
        "title_en": "Retinoids and Photoaging",
        "query": '("tretinoin"[Title/Abstract] OR retinoid*[Title/Abstract] OR retinol[Title/Abstract] OR retinaldehyde[Title/Abstract]) AND (photoaging[Title/Abstract] OR "skin aging"[Title/Abstract] OR wrinkle*[Title/Abstract])',
        "position": "外用维A酸类是光老化干预中研究较多的方向，核心终点是皱纹、粗糙、色素和真皮结构相关指标。",
        "boundary": "处方维A酸、孕期、敏感肌和皮肤病人群需要医生评估；不提供浓度和用法建议。",
        "intervention_type": "topical_prescription_or_cosmeceutical",
    },
    {
        "topic_id": "niacinamide-barrier-pigment",
        "title_zh": "烟酰胺与屏障/色素/炎症",
        "title_en": "Niacinamide for Barrier, Pigment, and Inflammation",
        "query": '(niacinamide[Title/Abstract] OR nicotinamide[Title/Abstract]) AND (skin[Title/Abstract] OR barrier[Title/Abstract] OR pigmentation[Title/Abstract] OR photoaging[Title/Abstract])',
        "position": "烟酰胺适合放在皮肤屏障、色素和炎症调节主题中，但不同浓度、配方和终点需要区分。",
        "boundary": "可讨论皮肤指标，不支持宣传为全身抗衰或延寿。",
        "intervention_type": "topical_or_oral",
    },
    {
        "topic_id": "topical-vitamin-c",
        "title_zh": "维C外用与色素/胶原",
        "title_en": "Topical Vitamin C",
        "query": '("vitamin C"[Title/Abstract] OR ascorbic[Title/Abstract]) AND (topical[Title/Abstract] OR skin[Title/Abstract] OR photoaging[Title/Abstract] OR collagen[Title/Abstract])',
        "position": "维C外用主要作为抗氧化、色素和胶原相关候选方向，证据受配方稳定性和研究设计影响较大。",
        "boundary": "不支持把外用维C写成可替代防晒、医美或疾病治疗。",
        "intervention_type": "topical_cosmeceutical",
    },
    {
        "topic_id": "oral-collagen-peptides",
        "title_zh": "口服胶原肽与皮肤弹性/水分",
        "title_en": "Oral Collagen Peptides",
        "query": '("collagen peptide"[Title/Abstract] OR "collagen peptides"[Title/Abstract] OR "hydrolyzed collagen"[Title/Abstract]) AND (skin[Title/Abstract] OR wrinkle*[Title/Abstract] OR elasticity[Title/Abstract] OR hydration[Title/Abstract])',
        "position": "口服胶原肽的人体随机试验较多，主要终点是水分、弹性和皱纹等皮肤外观指标。",
        "boundary": "只能讨论皮肤外观或仪器指标，不支持声称延寿或逆转衰老。",
        "intervention_type": "oral_supplement",
    },
    {
        "topic_id": "hyaluronic-acid-ceramides-hydration",
        "title_zh": "透明质酸、神经酰胺与皮肤水分屏障",
        "title_en": "Hyaluronic Acid, Ceramides, and Hydration",
        "query": '("hyaluronic acid"[Title/Abstract] OR ceramide*[Title/Abstract]) AND (skin[Title/Abstract] OR hydration[Title/Abstract] OR "transepidermal water loss"[Title/Abstract] OR barrier[Title/Abstract])',
        "position": "透明质酸和神经酰胺更适合评价皮肤水分、屏障和干燥相关终点。",
        "boundary": "支持屏障/保湿方向的证据整理，不支持宣传为系统性抗衰。",
        "intervention_type": "topical_or_oral",
    },
    {
        "topic_id": "polyphenols-skin-photoprotection",
        "title_zh": "多酚/抗氧化剂与皮肤光保护",
        "title_en": "Polyphenols and Skin Photoprotection",
        "query": '(polyphenol*[Title/Abstract] OR astaxanthin[Title/Abstract] OR "green tea"[Title/Abstract] OR catechin*[Title/Abstract] OR resveratrol[Title/Abstract]) AND (skin[Title/Abstract] OR photoprotection[Title/Abstract] OR photoaging[Title/Abstract])',
        "position": "多酚和抗氧化剂有一定光保护和皮肤指标研究，但商业化过度宣传风险较高。",
        "boundary": "不能替代防晒；不能把抗氧化机制直接写成抗老已证实。",
        "intervention_type": "oral_or_topical_supplement",
    },
    {
        "topic_id": "energy-devices-resurfacing",
        "title_zh": "医美能量设备和换肤类干预",
        "title_en": "Energy Devices, Peels, and Resurfacing",
        "query": '(laser[Title/Abstract] OR "intense pulsed light"[Title/Abstract] OR microneedling[Title/Abstract] OR peel[Title/Abstract] OR resurfacing[Title/Abstract]) AND (photoaging[Title/Abstract] OR wrinkle*[Title/Abstract] OR "skin aging"[Title/Abstract])',
        "position": "能量设备、微针和换肤类干预多属于专业医美或医疗美容场景，终点可见但风险和操作者依赖性高。",
        "boundary": "必须由合格专业人员评估；不提供设备、参数或疗程建议。",
        "intervention_type": "procedure_or_device",
    },
]

FINDING_FIELDS = [
    "finding_id", "candidate_id", "pmid", "doi", "source", "topic_id", "topic_zh", "topic_en",
    "title_en", "title_zh", "year", "journal", "study_type_draft", "intervention_type",
    "endpoint_class", "skin_endpoint", "result_en", "result_zh", "conclusion_en", "conclusion_zh",
    "evidence_level_draft", "evidence_source_depth", "supported_claim_zh", "unsupported_claim_zh",
    "safety_notes_zh", "medical_supervision_needed", "commercial_overclaim_risk", "status",
    "last_checked", "url",
]

TOPIC_FIELDS = [
    "topic_id", "title_zh", "title_en", "scope", "current_public_position_zh", "evidence_level_top",
    "finding_count", "s1_count", "s2_count", "metadata_only_count", "reader_boundary_zh", "status",
    "last_checked", "github_topic_path",
]

SUPPLEMENT_FIELDS = [
    "supplement_id", "name_zh", "name_en", "category", "longevity_evidence_level",
    "skin_beauty_evidence_level", "longevity_endpoint_class", "skin_endpoint_class",
    "supported_claim_zh", "unsupported_claim_zh", "safety_notes_zh", "medical_supervision_needed",
    "commercial_overclaim_risk", "summary_zh", "summary_en", "status", "last_checked",
]


def clean(value: str) -> str:
    return " ".join((value or "").replace("\n", " ").replace("\r", " ").split())


def text(node: ET.Element | None) -> str:
    return clean("".join(node.itertext())) if node is not None else ""


def request(endpoint: str, params: dict[str, str]) -> requests.Response:
    params = dict(params)
    email = os.getenv("NCBI_EMAIL")
    api_key = os.getenv("NCBI_API_KEY")
    if email:
        params["email"] = email
    if api_key:
        params["api_key"] = api_key
    url = f"{BASE}/{endpoint}?{urlencode(params)}"
    resp = requests.get(url, timeout=45)
    resp.raise_for_status()
    return resp


def esearch(query: str, retmax: int = 35) -> list[str]:
    resp = request("esearch.fcgi", {"db": "pubmed", "term": query, "retmax": str(retmax), "retmode": "json", "sort": "relevance"})
    return resp.json().get("esearchresult", {}).get("idlist", [])


def efetch(pmids: list[str]) -> dict[str, ET.Element]:
    if not pmids:
        return {}
    resp = request("efetch.fcgi", {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"})
    root = ET.fromstring(resp.text)
    articles: dict[str, ET.Element] = {}
    for article in root.findall(".//PubmedArticle"):
        pmid = text(article.find(".//PMID"))
        if pmid:
            articles[pmid] = article
    return articles


def article_ids(article: ET.Element) -> dict[str, str]:
    ids: dict[str, str] = {}
    for aid in article.findall(".//ArticleIdList/ArticleId"):
        id_type = aid.attrib.get("IdType", "")
        if id_type:
            ids[id_type] = text(aid)
    return ids


def abstract(article: ET.Element) -> str:
    sections = [text(node) for node in article.findall(".//Abstract/AbstractText")]
    return clean(" ".join(section for section in sections if section))


def publication_types(article: ET.Element) -> list[str]:
    return [text(node) for node in article.findall(".//PublicationTypeList/PublicationType")]


def classify_study(pub_types: list[str], body: str, title: str) -> str:
    joined = f"{' '.join(pub_types)} {body} {title}".lower()
    if "meta-analysis" in joined or "systematic review" in joined:
        return "systematic_review_or_meta_analysis"
    if "randomized" in joined or "randomised" in joined or "clinical trial" in joined:
        return "randomized_or_clinical_trial"
    if "review" in joined:
        return "review"
    if "mouse" in joined or "mice" in joined or "cell" in joined or "in vitro" in joined:
        return "preclinical_or_mechanistic"
    return "human_or_mixed_observational"


def classify_endpoint(study: str, body: str, title: str) -> tuple[str, str]:
    joined = f"{body} {title}".lower()
    clinical_terms = ["wrinkle", "elasticity", "hydration", "transepidermal", "tewl", "pigmentation", "photoaging", "roughness", "erythema", "acne", "barrier"]
    mechanism_terms = ["collagen", "mmp", "fibroblast", "keratinocyte", "gene expression", "in vitro", "mouse", "mice"]
    if any(term in joined for term in clinical_terms) and study != "preclinical_or_mechanistic":
        endpoint = "S1"
    elif any(term in joined for term in mechanism_terms):
        endpoint = "S2"
    else:
        endpoint = "M"
    skin_endpoint = ", ".join(term for term in clinical_terms if term in joined)[:120] or "skin aging endpoint pending review"
    return endpoint, skin_endpoint


def evidence_level(study: str, endpoint: str) -> str:
    if endpoint == "S1" and study == "systematic_review_or_meta_analysis":
        return "A"
    if endpoint == "S1" and study == "randomized_or_clinical_trial":
        return "B"
    if endpoint in {"S1", "S2"} and study in {"review", "human_or_mixed_observational"}:
        return "C"
    return "D"


def needs_supervision(topic_id: str) -> str:
    return "true" if topic_id in {"retinoids-photoaging", "energy-devices-resurfacing"} else "false"


def overclaim_risk(topic_id: str, level: str) -> str:
    if topic_id in {"polyphenols-skin-photoprotection", "oral-collagen-peptides"}:
        return "high"
    if level in {"C", "D"}:
        return "medium"
    return "medium"


def finding_from_article(topic: dict[str, Any], pmid: str, article: ET.Element, index: int) -> dict[str, str]:
    ids = article_ids(article)
    title = text(article.find(".//ArticleTitle"))
    year = text(article.find(".//PubDate/Year")) or text(article.find(".//PubDate/MedlineDate"))[:4]
    journal = text(article.find(".//Journal/Title"))
    body = abstract(article)
    pub_types = publication_types(article)
    study = classify_study(pub_types, body, title)
    endpoint, skin_endpoint = classify_endpoint(study, body, title)
    level = evidence_level(study, endpoint)
    result = body or f"PubMed metadata-level skin/appearance aging candidate for {topic['title_en']}: {title}."
    source_depth = "abstract_only" if body else "metadata_only"
    if ids.get("pmc"):
        source_depth = "abstract_plus_open_pmc_available"
    return {
        "finding_id": f"skin-{topic['topic_id']}-{index:03d}",
        "candidate_id": f"pubmed-{pmid}",
        "pmid": pmid,
        "doi": ids.get("doi", ""),
        "source": "PubMed",
        "topic_id": topic["topic_id"],
        "topic_zh": topic["title_zh"],
        "topic_en": topic["title_en"],
        "title_en": title,
        "title_zh": "",
        "year": year,
        "journal": journal,
        "study_type_draft": study,
        "intervention_type": topic["intervention_type"],
        "endpoint_class": endpoint,
        "skin_endpoint": skin_endpoint,
        "result_en": result[:900],
        "result_zh": f"中文草稿：该记录属于「{topic['title_zh']}」主题，当前抽取到的英文摘要/题录结果为：{result[:420]}",
        "conclusion_en": f"Draft conclusion: this record can inform {topic['title_en']} but requires full-text review before public claims.",
        "conclusion_zh": f"中文草稿结论：该记录可作为「{topic['title_zh']}」的候选证据，但正式结论需要全文复核。",
        "evidence_level_draft": level,
        "evidence_source_depth": source_depth,
        "supported_claim_zh": f"可支持：将该记录作为「{topic['title_zh']}」的候选证据，并按 {endpoint} 皮肤终点继续复核。",
        "unsupported_claim_zh": "不支持：不能据此声称逆龄、延寿、替代治疗，或给出产品/剂量/疗程建议。",
        "safety_notes_zh": topic["boundary"],
        "medical_supervision_needed": needs_supervision(topic["topic_id"]),
        "commercial_overclaim_risk": overclaim_risk(topic["topic_id"], level),
        "status": "public_draft_not_fully_reviewed",
        "last_checked": str(date.today()),
        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
    }


def top_level(levels: Counter[str]) -> str:
    for level in ["A", "B", "C", "D"]:
        if levels.get(level):
            return level
    return "pending"


def build_skin_findings() -> list[dict[str, str]]:
    load_dotenv(ROOT / ".env")
    rows: list[dict[str, str]] = []
    seen_pmids: set[str] = set()
    for topic in TOPICS:
        pmids = [pmid for pmid in esearch(topic["query"], 40) if pmid not in seen_pmids]
        articles = efetch(pmids)
        count = 0
        for pmid in pmids:
            article = articles.get(pmid)
            if article is None:
                continue
            seen_pmids.add(pmid)
            count += 1
            rows.append(finding_from_article(topic, pmid, article, count))
            if count >= 20:
                break
        print(f"{topic['topic_id']}: selected={count}")
        time.sleep(0.35)
    return rows


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build_topic_rows(findings: list[dict[str, str]]) -> list[dict[str, str]]:
    by_topic: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in findings:
        by_topic[row["topic_id"]].append(row)
    rows: list[dict[str, str]] = []
    for topic in TOPICS:
        items = by_topic[topic["topic_id"]]
        levels = Counter(item["evidence_level_draft"] for item in items)
        endpoints = Counter(item["endpoint_class"] for item in items)
        depth = Counter(item["evidence_source_depth"] for item in items)
        rows.append({
            "topic_id": topic["topic_id"],
            "title_zh": topic["title_zh"],
            "title_en": topic["title_en"],
            "scope": "Skin and appearance aging public draft topic; not a longevity endpoint.",
            "current_public_position_zh": topic["position"],
            "evidence_level_top": top_level(levels),
            "finding_count": str(len(items)),
            "s1_count": str(endpoints.get("S1", 0)),
            "s2_count": str(endpoints.get("S2", 0)),
            "metadata_only_count": str(depth.get("metadata_only", 0)),
            "reader_boundary_zh": topic["boundary"],
            "status": "public_draft_not_fully_reviewed",
            "last_checked": str(date.today()),
            "github_topic_path": f"content/skin-beauty-topics/{topic['topic_id']}.md",
        })
    return rows


def supplement_rows() -> list[dict[str, str]]:
    raw = [
        ("vitamin-d", "维生素 D", "Vitamin D", "vitamin", "B", "D", "L1/L2", "M", "缺乏或高风险人群的骨骼、跌倒和部分健康结局管理更有意义。", "不支持健康人群普遍补充即可延寿或美容逆龄。", "过量可导致高钙血症；检测和补充策略宜结合医生建议。", "true", "medium"),
        ("vitamin-c", "维生素 C", "Vitamin C", "vitamin", "C", "C", "L2", "S1/S2", "可支持缺乏风险、饮食不足或外用皮肤抗氧化方向的候选证据。", "不支持高剂量口服维C延寿或替代防晒。", "高剂量可能增加胃肠不适和结石风险人群负担。", "false", "medium"),
        ("omega-3", "Omega-3", "Omega-3 Fatty Acids", "fatty_acid", "B", "C", "L1/L2", "S1/M", "部分心血管、甘油三酯和炎症相关场景有证据基础。", "不支持声称普通人补充即可延寿或全面抗炎抗老。", "抗凝药、手术前和高剂量使用需医疗评估。", "true", "medium"),
        ("collagen-peptides", "胶原蛋白/胶原肽", "Collagen Peptides", "protein", "D", "B", "M", "S1", "可支持皮肤水分、弹性和皱纹等外观终点的候选证据。", "不支持声称补胶原能直接变成年轻皮肤或延寿。", "注意过敏、蛋白来源和基础肾病人群。", "false", "high"),
        ("protein-eaa", "蛋白粉/必需氨基酸", "Protein / Essential Amino Acids", "protein", "B", "D", "L2", "M", "可支持肌肉、衰弱和营养不足相关健康寿命终点。", "不支持作为皮肤美容或延寿万能补剂。", "肾病、肝病和特殊疾病人群需医生/营养师评估。", "true", "medium"),
        ("creatine", "肌酸", "Creatine", "sports_nutrition", "B", "D", "L2", "M", "可支持力量、肌肉和老年功能相关候选证据。", "不支持声称抗衰逆龄或皮肤美容明确有效。", "肾病或多药人群需医疗评估。", "true", "medium"),
        ("calcium-magnesium", "钙/镁", "Calcium / Magnesium", "mineral", "B", "D", "L1/L2", "M", "特定缺乏、骨骼或膳食不足场景可有意义。", "不支持无差别补充来延寿或美容。", "钙补充与肾结石、心血管风险讨论需个体化；镁也需注意肾功能。", "true", "medium"),
        ("zinc", "锌", "Zinc", "mineral", "C", "C", "L2", "S1/M", "缺乏或特定皮肤炎症场景可作为候选证据。", "不支持长期高剂量用于抗老或提升免疫。", "长期过量可影响铜代谢和胃肠耐受。", "true", "medium"),
        ("coq10", "辅酶 Q10", "Coenzyme Q10", "mitochondrial", "C", "D", "L2/M", "M", "可作为线粒体、心血管和疲劳相关候选证据。", "不支持声称明确延寿或皮肤逆龄。", "与抗凝药和慢病用药需注意相互作用。", "true", "high"),
        ("melatonin", "褪黑素", "Melatonin", "sleep", "B", "D", "L2", "M", "可支持睡眠节律相关场景的候选证据。", "不支持把它作为长期抗衰或美容补剂。", "嗜睡、药物相互作用、孕期和儿童需谨慎。", "true", "medium"),
        ("probiotics", "益生菌", "Probiotics", "microbiome", "C", "C", "L2/M", "S1/M", "部分肠道、炎症和皮肤屏障/炎症场景有候选证据。", "不支持单一益生菌适用于所有人抗衰或美容。", "免疫抑制、重症或中心静脉置管人群需医疗评估。", "true", "high"),
        ("nmn", "NMN", "NMN", "nad_precursor", "C", "D", "L2/M", "M", "可作为 NAD 代谢和人体早期指标研究候选。", "不支持声称已证实延寿、逆龄或美容抗老。", "长期安全性和适用人群仍不清楚。", "false", "high"),
        ("nr", "NR", "Nicotinamide Riboside", "nad_precursor", "C", "D", "L2/M", "M", "可作为 NAD 前体和代谢指标研究候选。", "不支持声称已证实延寿或外观逆龄。", "长期净收益和特殊疾病人群安全性仍需复核。", "false", "high"),
        ("nad-precursors", "NAD 前体", "NAD Precursors", "nad_precursor", "C", "D", "L2/M", "M", "可作为机制和早期人体研究集合。", "不支持把 NAD 提升等同于延寿或抗老成功。", "不同前体不能混为同一效果。", "false", "high"),
        ("resveratrol", "白藜芦醇", "Resveratrol", "polyphenol", "C", "C", "L2/M", "S1/M", "可作为多酚、代谢和皮肤光保护候选证据。", "不支持红酒/白藜芦醇延寿或逆龄宣传。", "药物相互作用和剂量差异大。", "true", "high"),
        ("quercetin", "槲皮素", "Quercetin", "polyphenol", "D", "D", "M", "M", "可作为抗氧化、炎症和 senolytic 组合研究线索。", "不支持单独作为抗衰、清除衰老细胞或美容方案。", "与药物代谢相关相互作用需注意。", "true", "high"),
        ("curcumin", "姜黄素", "Curcumin", "polyphenol", "C", "D", "L2/M", "M", "可作为炎症和代谢相关候选证据。", "不支持声称抗癌、延寿或皮肤逆龄。", "胆道疾病、抗凝药和胃肠耐受需注意。", "true", "high"),
        ("green-tea-catechins", "绿茶儿茶素", "Green Tea Catechins", "polyphenol", "C", "C", "L2/M", "S1/M", "可作为代谢和皮肤光保护候选证据。", "不支持高浓缩提取物无风险或明确延寿。", "高剂量提取物有肝毒性报告，需谨慎。", "true", "high"),
        ("astaxanthin", "虾青素", "Astaxanthin", "antioxidant", "D", "C", "M", "S1/S2", "可作为皮肤光保护和抗氧化候选证据。", "不支持声称防晒替代、逆龄或延寿。", "长期高剂量和特殊人群安全性仍需复核。", "false", "high"),
        ("hyaluronic-acid", "透明质酸", "Hyaluronic Acid", "skin_hydration", "D", "B", "M", "S1", "可支持皮肤水分和屏障相关候选证据。", "不支持声称系统性抗衰或延寿。", "注射类属于医疗美容，不纳入口服/外用普通补剂结论。", "false", "medium"),
        ("ceramides", "神经酰胺", "Ceramides", "skin_barrier", "D", "B", "M", "S1", "可支持干燥、屏障和 TEWL 相关皮肤终点。", "不支持声称逆龄或治疗皮肤病。", "皮肤病治疗需医生评估。", "false", "medium"),
        ("niacinamide", "烟酰胺", "Niacinamide", "vitamin_b3", "C", "B", "L2/M", "S1", "可支持皮肤屏障、色素和炎症相关候选证据。", "不支持把烟酰胺写成延寿或全面抗衰。", "口服高剂量和肝病/慢病人群需谨慎。", "false", "medium"),
        ("vitamin-b12", "维生素 B12", "Vitamin B12", "vitamin", "B", "D", "L2", "M", "可支持缺乏、贫血和神经相关风险管理。", "不支持非缺乏人群补充即可延寿或美容。", "需结合缺乏风险、素食、胃肠疾病和用药情况。", "true", "medium"),
        ("folate", "叶酸", "Folate", "vitamin", "B", "D", "L1/L2", "M", "可支持孕前孕期和缺乏风险相关健康管理。", "不支持作为抗衰或美容补剂泛用。", "高剂量可能掩盖 B12 缺乏，需注意人群边界。", "true", "medium"),
        ("multivitamin", "复合维生素", "Multivitamin", "multi_nutrient", "C", "D", "L2/M", "M", "可作为饮食不足或特定人群营养补充候选。", "不支持替代健康饮食、延寿或美容逆龄。", "注意重复摄入脂溶性维生素和矿物质。", "false", "high"),
        ("vitamin-e", "维生素 E", "Vitamin E", "vitamin", "C", "C", "L2/M", "S2/M", "可作为抗氧化相关候选证据。", "不支持高剂量用于延寿、心血管预防或美容逆龄。", "高剂量可能增加出血风险，抗凝药人群需谨慎。", "true", "high"),
        ("vitamin-a", "维生素 A", "Vitamin A", "vitamin", "C", "C", "L2/M", "S2", "可支持缺乏相关视力、免疫和皮肤角化问题。", "不支持高剂量抗老或美容口服。", "脂溶性维生素，过量和孕期风险较高。", "true", "high"),
        ("vitamin-k2", "维生素 K2", "Vitamin K2", "vitamin", "C", "D", "L2/M", "M", "可作为骨骼和钙代谢相关候选证据。", "不支持声称软化血管、延寿或美容。", "华法林等抗凝药人群需医生评估。", "true", "high"),
        ("selenium", "硒", "Selenium", "mineral", "C", "D", "L2/M", "M", "可支持缺乏或甲状腺相关候选证据。", "不支持高剂量抗癌、延寿或美容。", "过量可导致硒中毒，安全窗较窄。", "true", "high"),
        ("iodine", "碘", "Iodine", "mineral", "B", "D", "L2", "M", "可支持缺乏和甲状腺健康管理。", "不支持抗衰或美容泛用。", "甲状腺疾病人群补充需医生评估。", "true", "medium"),
        ("iron", "铁", "Iron", "mineral", "B", "D", "L2", "M", "可支持缺铁和贫血相关健康管理。", "不支持无缺乏人群补铁抗老。", "过量铁有风险，需结合铁蛋白和医生评估。", "true", "medium"),
        ("copper", "铜", "Copper", "mineral", "C", "D", "L2/M", "M", "可支持明确缺乏相关候选证据。", "不支持作为美容或抗衰补剂泛用。", "过量有毒性，且与锌摄入存在平衡问题。", "true", "medium"),
        ("manganese", "锰", "Manganese", "mineral", "D", "D", "M", "M", "可作为微量元素缺乏风险线索。", "不支持抗衰或美容宣传。", "过量有神经毒性风险。", "true", "medium"),
        ("chromium", "铬", "Chromium", "mineral", "C", "D", "L2/M", "M", "可作为糖代谢相关候选证据。", "不支持减肥、控糖或延寿确定有效宣传。", "糖尿病用药人群需注意低血糖和相互作用。", "true", "high"),
        ("potassium", "钾", "Potassium", "mineral", "B", "D", "L2", "M", "可支持血压和膳食模式相关健康管理。", "不支持自行高剂量补钾抗衰。", "肾病、ACEI/ARB 或保钾利尿剂人群风险高。", "true", "medium"),
        ("electrolytes", "电解质", "Electrolytes", "mineral_mix", "C", "D", "L2/M", "M", "可支持出汗、运动或脱水场景。", "不支持日常抗衰或美容泛用。", "高血压、肾病和心衰人群需看钠钾负担。", "true", "medium"),
        ("psyllium", "车前子壳/可溶性纤维", "Psyllium / Soluble Fiber", "fiber", "B", "D", "L2", "M", "可支持 LDL-C、血糖和肠道规律相关终点。", "不支持直接延寿或美容逆龄。", "需注意饮水、吞咽困难和药物吸收间隔。", "false", "medium"),
        ("beta-glucan", "β-葡聚糖", "Beta-Glucan", "fiber", "B", "D", "L2", "M", "可支持胆固醇和免疫相关候选证据。", "不支持全面提升免疫或抗衰。", "过敏和胃肠耐受需注意。", "false", "medium"),
        ("inulin", "菊粉", "Inulin", "prebiotic", "C", "D", "L2/M", "M", "可作为益生元、肠道和代谢候选证据。", "不支持所有人群肠道抗老。", "易腹胀，肠易激人群需谨慎。", "false", "medium"),
        ("prebiotic-mix", "益生元复合物", "Prebiotic Mix", "prebiotic", "C", "D", "L2/M", "M", "可支持肠道菌群和代谢候选证据。", "不支持单独作为抗衰或美容方案。", "肠道敏感人群需关注耐受。", "false", "high"),
        ("lutein", "叶黄素", "Lutein", "carotenoid", "B", "C", "L1/L2", "S2/M", "可支持眼健康和黄斑相关证据。", "不支持延寿或皮肤逆龄。", "与综合配方和基础眼病状态有关。", "false", "medium"),
        ("zeaxanthin", "玉米黄质", "Zeaxanthin", "carotenoid", "B", "C", "L1/L2", "S2/M", "可支持眼健康和黄斑相关证据。", "不支持美容或延寿泛用宣传。", "常与叶黄素联用，需区分配方证据。", "false", "medium"),
        ("lycopene", "番茄红素", "Lycopene", "carotenoid", "C", "C", "L2/M", "S2/M", "可作为抗氧化和皮肤光保护候选证据。", "不支持抗癌、延寿或替代防晒。", "补剂证据不能替代富含蔬果的饮食模式。", "false", "high"),
        ("beta-carotene", "β-胡萝卜素", "Beta-Carotene", "carotenoid", "C", "C", "L2/M", "S2/M", "可作为维A来源和抗氧化候选证据。", "不支持吸烟者补充用于防癌或抗衰。", "吸烟者高剂量补充存在重要安全警示。", "true", "high"),
        ("alpha-lipoic-acid", "α-硫辛酸", "Alpha-Lipoic Acid", "antioxidant", "C", "D", "L2/M", "M", "可作为糖代谢和神经症状候选证据。", "不支持延寿或美容逆龄。", "糖尿病用药人群需注意低血糖风险。", "true", "high"),
        ("nac", "NAC/N-乙酰半胱氨酸", "N-Acetylcysteine", "antioxidant", "C", "D", "L2/M", "M", "可作为谷胱甘肽和呼吸/氧化应激相关候选证据。", "不支持作为通用抗衰补剂。", "哮喘、抗凝和药物相互作用需注意。", "true", "high"),
        ("glutathione", "谷胱甘肽", "Glutathione", "antioxidant", "D", "C", "M", "S1/M", "可作为色素和氧化应激候选证据。", "不支持美白、排毒或逆龄确定有效宣传。", "注射用途不属于普通补剂，存在医疗风险。", "true", "high"),
        ("glycine", "甘氨酸", "Glycine", "amino_acid", "C", "D", "L2/M", "M", "可作为睡眠、代谢和胶原相关候选证据。", "不支持延寿已证实。", "特殊疾病和多补剂组合需谨慎。", "false", "medium"),
        ("taurine", "牛磺酸", "Taurine", "amino_acid", "C", "D", "L2/M", "M", "可作为代谢、运动和心血管候选证据。", "不支持声称人类延寿已证实。", "能量饮料配方不能等同于牛磺酸单独证据。", "false", "high"),
        ("l-carnitine", "左旋肉碱", "L-Carnitine", "amino_acid_derivative", "C", "D", "L2/M", "M", "可作为脂代谢、疲劳和特定缺乏候选证据。", "不支持减肥或延寿确定有效。", "肾病、癫痫和 TMAO 风险讨论需复核。", "true", "high"),
        ("acetyl-l-carnitine", "乙酰左旋肉碱", "Acetyl-L-Carnitine", "amino_acid_derivative", "C", "D", "L2/M", "M", "可作为神经、疲劳和线粒体候选证据。", "不支持逆龄或认知增强确定有效。", "精神症状、癫痫和用药人群需谨慎。", "true", "high"),
        ("citrulline", "瓜氨酸", "Citrulline", "sports_nutrition", "C", "D", "L2/M", "M", "可作为运动表现和血流相关候选证据。", "不支持延寿或美容。", "低血压和硝酸酯类用药人群需谨慎。", "true", "medium"),
        ("arginine", "精氨酸", "Arginine", "sports_nutrition", "C", "D", "L2/M", "M", "可作为血流和运动相关候选证据。", "不支持抗衰或心血管治疗替代。", "疱疹、低血压和心血管病史人群需谨慎。", "true", "medium"),
        ("beta-alanine", "β-丙氨酸", "Beta-Alanine", "sports_nutrition", "C", "D", "L2", "M", "可支持部分运动表现相关证据。", "不支持延寿、美容或肌肉增长万能宣传。", "常见刺痛感，特殊疾病人群需谨慎。", "false", "medium"),
        ("hmb", "HMB", "HMB", "sports_nutrition", "C", "D", "L2", "M", "可作为肌肉保留和老年营养候选证据。", "不支持替代抗阻训练或延寿。", "肾病和多种蛋白补剂叠加需注意。", "true", "medium"),
        ("collagen-type-ii", "二型胶原", "Type II Collagen", "joint_support", "C", "D", "L2", "M", "可作为关节相关候选证据。", "不支持皮肤逆龄或延寿。", "自身免疫和过敏人群需谨慎。", "true", "medium"),
        ("glucosamine", "氨糖", "Glucosamine", "joint_support", "C", "D", "L2", "M", "可作为骨关节炎症状候选证据。", "不支持软骨再生、延寿或美容。", "糖尿病、贝类过敏和抗凝药人群需注意。", "true", "high"),
        ("chondroitin", "软骨素", "Chondroitin", "joint_support", "C", "D", "L2", "M", "可作为关节症状候选证据。", "不支持延寿或皮肤抗老。", "抗凝药人群需谨慎。", "true", "medium"),
        ("msm", "MSM", "Methylsulfonylmethane", "joint_support", "D", "D", "L2/M", "M", "可作为关节和炎症候选线索。", "不支持抗衰、美容或治疗确定有效。", "长期安全性和配方混杂需复核。", "false", "high"),
        ("boswellia", "乳香提取物", "Boswellia", "botanical", "C", "D", "L2/M", "M", "可作为关节和炎症候选证据。", "不支持治疗替代或延寿。", "与抗凝、胃肠耐受和产品质量有关。", "true", "high"),
        ("ashwagandha", "南非醉茄", "Ashwagandha", "botanical_adaptogen", "C", "D", "L2/M", "M", "可作为压力、睡眠和主观疲劳候选证据。", "不支持抗衰、增睾或治疗焦虑抑郁的确定宣传。", "肝损伤个案、甲状腺和孕期风险需注意。", "true", "high"),
        ("rhodiola", "红景天", "Rhodiola", "botanical_adaptogen", "D", "D", "L2/M", "M", "可作为疲劳和压力候选线索。", "不支持延寿或增强免疫确定有效。", "精神症状和用药相互作用需谨慎。", "true", "high"),
        ("ginseng", "人参", "Ginseng", "botanical", "C", "D", "L2/M", "M", "可作为疲劳、血糖和认知候选证据。", "不支持包治百病或延寿。", "血糖、血压、抗凝药和失眠风险需注意。", "true", "high"),
        ("maca", "玛咖", "Maca", "botanical", "D", "D", "M", "M", "可作为性健康和主观活力候选线索。", "不支持抗衰、增睾或美容确定有效。", "内分泌相关疾病人群需谨慎。", "false", "high"),
        ("ginkgo", "银杏", "Ginkgo", "botanical", "C", "D", "L2/M", "M", "可作为认知和循环相关候选证据。", "不支持预防痴呆、延寿或美容。", "抗凝药、手术前和出血风险人群需谨慎。", "true", "high"),
        ("bacopa", "婆罗米", "Bacopa", "botanical", "C", "D", "L2/M", "M", "可作为认知相关候选证据。", "不支持抗衰或治疗认知障碍。", "胃肠反应、镇静和药物相互作用需注意。", "true", "high"),
        ("lions-mane", "猴头菇", "Lion's Mane", "mushroom", "D", "D", "M", "M", "可作为神经和认知候选线索。", "不支持神经再生、延寿或美容确定有效。", "过敏、产品质量和证据不足需提示。", "false", "high"),
        ("berberine", "小檗碱", "Berberine", "botanical_alkaloid", "B", "D", "L2", "M", "可作为血糖、血脂和代谢候选证据。", "不支持替代降糖/降脂药或延寿。", "药物相互作用多，孕期和慢病用药人群需医生评估。", "true", "high"),
        ("cinnamon", "肉桂", "Cinnamon", "botanical", "C", "D", "L2/M", "M", "可作为血糖候选证据。", "不支持治疗糖尿病或延寿。", "香豆素、肝病和药物相互作用需注意。", "true", "high"),
        ("garlic-extract", "大蒜提取物", "Garlic Extract", "botanical", "C", "D", "L2/M", "M", "可作为血脂、血压和心血管风险候选证据。", "不支持替代降压/降脂治疗或延寿。", "抗凝药、手术前和胃肠反应需注意。", "true", "medium"),
        ("plant-sterols", "植物甾醇", "Plant Sterols", "lipid_lowering", "B", "D", "L2", "M", "可支持 LDL-C 降低相关证据。", "不支持直接降低死亡风险或美容。", "不替代总体饮食和医学降脂策略。", "false", "medium"),
        ("red-yeast-rice", "红曲米", "Red Yeast Rice", "lipid_lowering", "B", "D", "L2", "M", "可支持 LDL-C 相关候选证据。", "不支持作为安全天然替代他汀。", "含类他汀成分和污染风险，需医生评估。", "true", "high"),
        ("policosanol", "普利醇", "Policosanol", "lipid_lowering", "D", "D", "L2/M", "M", "可作为血脂候选线索。", "不支持降脂或延寿确定有效。", "证据不一致，不能替代标准治疗。", "true", "high"),
        ("milk-thistle", "水飞蓟", "Milk Thistle", "botanical", "C", "D", "L2/M", "M", "可作为肝功能相关候选证据。", "不支持护肝排毒、延寿或美容。", "肝病治疗需医生评估，注意药物相互作用。", "true", "high"),
        ("saw-palmetto", "锯棕榈", "Saw Palmetto", "botanical", "C", "D", "L2", "M", "可作为前列腺症状候选证据。", "不支持抗衰、增发或激素调节确定有效。", "前列腺症状需排除严重疾病。", "true", "high"),
        ("cranberry", "蔓越莓", "Cranberry", "botanical", "C", "D", "L2", "M", "可作为尿路感染复发预防候选证据。", "不支持抗衰、美容或治疗感染。", "抗凝药和肾结石风险人群需谨慎。", "true", "medium"),
        ("d-mannose", "D-甘露糖", "D-Mannose", "urogenital", "C", "D", "L2", "M", "可作为尿路感染复发预防候选证据。", "不支持治疗感染或抗衰。", "糖尿病和反复感染人群需医生评估。", "true", "medium"),
        ("peppermint-oil", "薄荷油", "Peppermint Oil", "botanical", "B", "D", "L2", "M", "可作为肠易激症状候选证据。", "不支持抗衰、美容或长期随意使用。", "胃食管反流、儿童和孕期需谨慎。", "true", "medium"),
        ("ginger", "姜", "Ginger", "botanical", "C", "D", "L2/M", "M", "可作为恶心、炎症和代谢候选证据。", "不支持延寿或美容逆龄。", "抗凝药和胃肠耐受需注意。", "true", "medium"),
        ("spirulina", "螺旋藻", "Spirulina", "algae", "D", "D", "M", "M", "可作为营养和代谢候选线索。", "不支持排毒、抗衰或美容确定有效。", "污染、免疫疾病和产品质量风险需提示。", "false", "high"),
        ("chlorella", "小球藻", "Chlorella", "algae", "D", "D", "M", "M", "可作为营养候选线索。", "不支持排毒、延寿或美容。", "污染、免疫疾病和抗凝药人群需谨慎。", "true", "high"),
        ("moringa", "辣木", "Moringa", "botanical", "D", "D", "M", "M", "可作为营养和代谢候选线索。", "不支持抗衰、降糖或美容确定有效。", "孕期、用药和产品质量需注意。", "false", "high"),
        ("wheatgrass", "小麦草", "Wheatgrass", "botanical", "D", "D", "M", "M", "可作为营养候选线索。", "不支持排毒、抗癌、延寿或美容。", "污染和过敏风险需提示。", "false", "high"),
        ("beetroot", "甜菜根", "Beetroot / Nitrate", "sports_nutrition", "B", "D", "L2", "M", "可支持血压和运动表现相关候选证据。", "不支持延寿或美容。", "低血压、肾结石风险和用药人群需谨慎。", "true", "medium"),
        ("cocoa-flavanols", "可可黄烷醇", "Cocoa Flavanols", "polyphenol", "C", "C", "L2/M", "S2/M", "可作为血管功能和皮肤光保护候选证据。", "不支持巧克力延寿或美容逆龄。", "糖脂负担和配方差异需区分。", "false", "high"),
        ("olive-leaf", "橄榄叶提取物", "Olive Leaf Extract", "botanical", "D", "D", "M", "M", "可作为血压、代谢和抗氧化候选线索。", "不支持替代降压药、延寿或美容。", "低血压和用药相互作用需注意。", "true", "high"),
        ("black-seed-oil", "黑种草籽油", "Black Seed Oil", "botanical_oil", "C", "D", "L2/M", "M", "可作为炎症和代谢候选证据。", "不支持治疗疾病、延寿或美容。", "药物相互作用、孕期和肝肾风险需注意。", "true", "high"),
        ("evening-primrose-oil", "月见草油", "Evening Primrose Oil", "fatty_acid", "C", "C", "L2/M", "S1/M", "可作为皮肤干燥、湿疹和女性健康候选证据。", "不支持抗衰或美容确定有效。", "抗凝药、癫痫和孕期需谨慎。", "true", "high"),
        ("borage-oil", "琉璃苣油", "Borage Oil", "fatty_acid", "C", "C", "L2/M", "S1/M", "可作为皮肤屏障和炎症候选证据。", "不支持抗衰或美容确定有效。", "需注意肝毒性污染物和抗凝风险。", "true", "high"),
        ("cla", "共轭亚油酸", "Conjugated Linoleic Acid", "fatty_acid", "D", "D", "L2/M", "M", "可作为体成分候选线索。", "不支持减脂、延寿或美容确定有效。", "可能影响胰岛素敏感性和血脂，需谨慎。", "true", "high"),
        ("mct-oil", "MCT 油", "MCT Oil", "fat", "C", "D", "L2/M", "M", "可作为能量代谢和特定饮食场景候选证据。", "不支持减肥、延寿或美容。", "胃肠反应和热量负担需注意。", "false", "high"),
        ("sam-e", "SAM-e", "S-Adenosylmethionine", "methylation", "C", "D", "L2/M", "M", "可作为情绪、关节和肝功能候选证据。", "不支持抗衰或美容。", "躁郁风险、抗抑郁药相互作用需医生评估。", "true", "high"),
        ("inositol", "肌醇", "Inositol", "metabolic", "C", "D", "L2/M", "M", "可作为 PCOS 和代谢候选证据。", "不支持抗衰、美容或所有女性泛用。", "糖代谢用药和孕期需评估。", "true", "medium"),
        ("phosphatidylserine", "磷脂酰丝氨酸", "Phosphatidylserine", "cognition", "D", "D", "M", "M", "可作为认知和压力候选线索。", "不支持预防痴呆或延寿。", "证据有限，产品来源和用药人群需注意。", "false", "high"),
        ("citicoline", "胞磷胆碱", "Citicoline", "cognition", "C", "D", "L2/M", "M", "可作为认知和神经恢复候选证据。", "不支持聪明药、延寿或美容。", "神经系统疾病和用药人群需医生评估。", "true", "high"),
        ("choline", "胆碱", "Choline", "nutrient", "C", "D", "L2/M", "M", "可作为营养和肝脂代谢候选证据。", "不支持延寿或美容。", "高摄入、TMAO 风险和鱼腥味副作用需注意。", "false", "medium"),
        ("l-theanine", "L-茶氨酸", "L-Theanine", "relaxation", "C", "D", "L2/M", "M", "可作为压力、睡眠和注意力候选证据。", "不支持抗衰或治疗焦虑失眠。", "镇静药物和驾驶安全需注意。", "false", "medium"),
        ("tryptophan", "色氨酸", "Tryptophan", "sleep_mood", "C", "D", "L2/M", "M", "可作为睡眠和情绪相关候选证据。", "不支持抗衰或美容。", "与抗抑郁药同用需注意血清素风险。", "true", "high"),
        ("5-htp", "5-HTP", "5-HTP", "sleep_mood", "C", "D", "L2/M", "M", "可作为睡眠和情绪候选线索。", "不支持治疗抑郁、减肥或抗衰。", "抗抑郁药同用风险较高，需医生评估。", "true", "high"),
        ("valerian", "缬草", "Valerian", "sleep_botanical", "C", "D", "L2/M", "M", "可作为睡眠候选证据。", "不支持长期治疗失眠或抗衰。", "镇静叠加、驾驶和肝脏安全需注意。", "true", "medium"),
        ("magnesium-glycinate", "甘氨酸镁", "Magnesium Glycinate", "mineral_form", "C", "D", "L2/M", "M", "可作为镁补充和睡眠/肌肉候选证据。", "不支持特定剂型必然优于所有镁或抗衰。", "肾功能不全人群需医生评估。", "true", "medium"),
        ("silica", "硅/二氧化硅", "Silica", "hair_skin_nails", "D", "D", "M", "M", "可作为头发、指甲和皮肤结构候选线索。", "不支持美容逆龄或胶原再生确定有效。", "证据有限，产品形态差异大。", "false", "high"),
        ("biotin", "生物素", "Biotin", "hair_skin_nails", "C", "D", "L2/M", "M", "可支持明确缺乏导致的头发/指甲问题。", "不支持非缺乏人群生发、美甲或抗衰。", "会干扰部分实验室检测，体检前需告知医生。", "true", "high"),
        ("paba", "PABA", "PABA", "skin_hair", "D", "D", "M", "M", "可作为历史性皮肤/头发候选线索。", "不支持防晒、抗白发或美容确定有效。", "安全性和有效性证据不足。", "false", "high"),
        ("horsetail", "木贼/问荆", "Horsetail", "botanical_skin_hair", "D", "D", "M", "M", "可作为头发、指甲和硅来源候选线索。", "不支持生发、强甲或抗衰。", "可能有硫胺素酶和污染风险，长期使用需谨慎。", "true", "high"),
        ("pomegranate", "石榴提取物", "Pomegranate Extract", "polyphenol", "C", "C", "L2/M", "S2/M", "可作为多酚、血管和皮肤光保护候选证据。", "不支持抗癌、延寿或替代防晒。", "药物相互作用和产品标准化需注意。", "true", "high"),
        ("grape-seed-extract", "葡萄籽提取物", "Grape Seed Extract", "polyphenol", "C", "C", "L2/M", "S2/M", "可作为血管、抗氧化和皮肤候选证据。", "不支持美白、延寿或逆龄确定有效。", "抗凝药和手术前需谨慎。", "true", "high"),
        ("pine-bark-extract", "松树皮提取物", "Pine Bark Extract", "polyphenol", "C", "C", "L2/M", "S1/M", "可作为血管和皮肤弹性候选证据。", "不支持延寿或美容逆龄确定有效。", "免疫疾病、抗凝药和产品差异需注意。", "true", "high"),
        ("spermidine", "亚精胺", "Spermidine", "autophagy", "C", "D", "L2/M", "M", "可作为自噬和流行病学候选证据。", "不支持人类延寿已证实或美容抗老。", "长期干预和适用人群仍需研究。", "false", "high"),
        ("fisetin", "漆黄素", "Fisetin", "senolytic_candidate", "D", "D", "M", "M", "可作为 senolytic 前沿候选线索。", "不支持清除衰老细胞、延寿或美容确定有效。", "人体证据不足，不应自行高剂量尝试。", "true", "high"),
        ("urolithin-a", "尿石素 A", "Urolithin A", "mitochondrial", "C", "D", "L2/M", "M", "可作为线粒体和肌肉功能候选证据。", "不支持延寿或美容逆龄已证实。", "长期安全性和真实临床终点仍需复核。", "false", "high"),
        ("ergothioneine", "麦角硫因", "Ergothioneine", "antioxidant", "D", "D", "M", "M", "可作为抗氧化和健康老化候选线索。", "不支持延寿、美容或抗氧化治疗确定有效。", "人体临床证据不足。", "false", "high"),
        ("apigenin", "芹菜素", "Apigenin", "polyphenol", "D", "D", "M", "M", "可作为睡眠、炎症和机制候选线索。", "不支持抗衰、抗癌或美容确定有效。", "药物相互作用和证据不足需提示。", "true", "high"),
        ("saffron", "藏红花", "Saffron", "botanical", "C", "D", "L2/M", "M", "可作为情绪和眼健康候选证据。", "不支持美容、延寿或治疗替代。", "孕期、高剂量和药物相互作用需谨慎。", "true", "high"),
        ("sea-buckthorn", "沙棘", "Sea Buckthorn", "botanical_oil", "C", "C", "L2/M", "S1/M", "可作为干眼、皮肤干燥和脂肪酸候选证据。", "不支持美容逆龄或延寿。", "抗凝药、胃肠耐受和产品差异需注意。", "true", "high"),
        ("royal-jelly", "蜂王浆", "Royal Jelly", "bee_product", "D", "D", "M", "M", "可作为代谢和皮肤候选线索。", "不支持抗衰、美容或激素调节确定有效。", "过敏和哮喘人群风险较高。", "true", "high"),
    ]
    raw = raw[:100]
    rows = []
    for item in raw:
        supplement_id, name_zh, name_en, category, longevity, skin, longevity_endpoint, skin_endpoint, supported, unsupported, safety, supervision, risk = item
        rows.append({
            "supplement_id": supplement_id,
            "name_zh": name_zh,
            "name_en": name_en,
            "category": category,
            "longevity_evidence_level": longevity,
            "skin_beauty_evidence_level": skin,
            "longevity_endpoint_class": longevity_endpoint,
            "skin_endpoint_class": skin_endpoint,
            "supported_claim_zh": supported,
            "unsupported_claim_zh": unsupported,
            "safety_notes_zh": safety,
            "medical_supervision_needed": supervision,
            "commercial_overclaim_risk": risk,
            "summary_zh": f"{name_zh}：健康寿命证据草判 {longevity}；皮肤美容证据草判 {skin}。{supported}",
            "summary_en": f"{name_en}: draft longevity evidence {longevity}; draft skin/beauty evidence {skin}. Not a dosing or product recommendation.",
            "status": "public_draft_not_fully_reviewed",
            "last_checked": str(date.today()),
        })
    return rows


def write_skin_topic_pages(topic_rows: list[dict[str, str]], findings: list[dict[str, str]]) -> None:
    SKIN_TOPIC_DIR.mkdir(parents=True, exist_ok=True)
    by_topic: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in findings:
        by_topic[row["topic_id"]].append(row)
    for topic in TOPICS:
        topic_id = topic["topic_id"]
        rows = by_topic[topic_id]
        lines = [
            f"# {topic['title_zh']} / {topic['title_en']}",
            "",
            f"> {DRAFT_NOTICE_ZH}",
            f"> {DRAFT_NOTICE_EN}",
            "",
            "## 当前立场",
            "",
            topic["position"],
            "",
            "## 读者边界",
            "",
            topic["boundary"],
            "",
            "## 候选证据",
            "",
            "| PMID | Year | Evidence | Endpoint | Study Type | Title |",
            "|---|---:|---|---|---|---|",
        ]
        for row in rows:
            title = row["title_en"].replace("|", " ")
            lines.append(f"| [{row['pmid']}]({row['url']}) | {row['year']} | {row['evidence_level_draft']} | {row['endpoint_class']} | {row['study_type_draft']} | {title} |")
        lines.extend([
            "",
            "## 不能这么说",
            "",
            "- 不能把皮肤水分、皱纹或仪器指标改善写成延寿。",
            "- 不能根据摘要给出产品、浓度、剂量或疗程。",
            "- 不能把机制研究直接写成临床美容效果已证实。",
        ])
        (SKIN_TOPIC_DIR / f"{topic_id}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_summary_pages(topic_rows: list[dict[str, str]], supplements: list[dict[str, str]]) -> None:
    SKIN_MD.parent.mkdir(parents=True, exist_ok=True)
    skin_lines = [
        "# 外观抗老与皮肤健康证据图谱 / Skin & Appearance Aging Evidence Atlas",
        "",
        f"> {DRAFT_NOTICE_ZH}",
        f"> {DRAFT_NOTICE_EN}",
        "",
        "## 一句话说明",
        "",
        "这是与健康寿命图谱并列的第二条证据轴：它只回答皮肤外观、屏障、光老化、皱纹、色斑、水分和安全性问题，不把美容终点写成延寿结论。",
        "",
        "## 当前能说什么",
        "",
        "- 防晒、维A酸类、口服胶原肽、神经酰胺/透明质酸等方向有较多皮肤终点研究线索。",
        "- 医美设备、换肤、处方维A酸等属于专业或医疗场景，需要医生或合格专业人员评估。",
        "- 多酚、抗氧化剂和部分补剂适合列为候选证据，但商业过度宣传风险较高。",
        "",
        "## 不能这么说",
        "",
        "- 不能把皱纹、水分、弹性或色斑改善写成延寿。",
        "- 不能提供产品、品牌、浓度、剂量或疗程推荐。",
        "- 不能把体外、动物或机制研究写成人体美容效果已证实。",
        "",
        "## 主题总览",
        "",
        "| # | 主题 | 当前立场 | Evidence | Findings | 边界 |",
        "|---:|---|---|---|---:|---|",
    ]
    for index, row in enumerate(topic_rows, start=1):
        skin_lines.append(
            f"| {index} | [{row['title_zh']}](../skin-beauty-topics/{row['topic_id']}.md)<br>{row['title_en']} | "
            f"{row['current_public_position_zh']} | {row['evidence_level_top']} | {row['finding_count']} | {row['reader_boundary_zh']} |"
        )
    skin_lines.extend([
        "",
        "## 热门补剂快速表",
        "",
        "| 补剂 | 健康寿命证据 | 皮肤美容证据 | 主要边界 |",
        "|---|---|---|---|",
    ])
    for row in supplements:
        skin_lines.append(f"| {row['name_zh']}<br>{row['name_en']} | {row['longevity_evidence_level']} | {row['skin_beauty_evidence_level']} | {row['unsupported_claim_zh']} |")
    SKIN_MD.write_text("\n".join(skin_lines) + "\n", encoding="utf-8")

    supplement_lines = [
        "# 补剂证据矩阵 / Supplement Evidence Matrix",
        "",
        f"> {DRAFT_NOTICE_ZH}",
        f"> {DRAFT_NOTICE_EN}",
        "",
        "本表同时展示同一种补剂对健康寿命/疾病风险和皮肤美容/外观抗老的证据草判。它不是购买清单、剂量建议或治疗建议。",
        "",
        "| 补剂 | 类型 | 健康寿命证据 | 皮肤美容证据 | 支持的说法 | 不支持的说法 | 安全边界 |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in supplements:
        supplement_lines.append(
            f"| {row['name_zh']}<br>{row['name_en']} | {row['category']} | {row['longevity_evidence_level']} / {row['longevity_endpoint_class']} | "
            f"{row['skin_beauty_evidence_level']} / {row['skin_endpoint_class']} | {row['supported_claim_zh']} | {row['unsupported_claim_zh']} | {row['safety_notes_zh']} |"
        )
    SUPPLEMENT_MD.write_text("\n".join(supplement_lines) + "\n", encoding="utf-8")


def patch_public_summary() -> None:
    path = ROOT / "content" / "overview" / "public-summary.md"
    text_body = path.read_text(encoding="utf-8") if path.exists() else ""
    marker = "## 图谱入口 / Atlas Entrypoints"
    block = "\n".join([
        marker,
        "",
        "| 图谱 | 回答的问题 | 入口 |",
        "|---|---|---|",
        "| 健康寿命证据图谱 | 死亡、疾病、功能、代谢、药物、机制和健康寿命边界。 | [公开总览](public-summary.md) |",
        "| 外观抗老与皮肤健康证据图谱 | 光老化、皱纹、色斑、屏障、水分、医美和皮肤安全边界。 | [皮肤美容总览](skin-beauty-summary.md) |",
        "| 补剂证据矩阵 | 同一补剂对健康寿命和皮肤美容的证据强弱、不能宣传什么。 | [补剂矩阵](supplement-summary.md) |",
        "",
    ])
    if marker in text_body:
        return
    lines = text_body.splitlines()
    if len(lines) > 4:
        lines = lines[:4] + ["", block] + lines[4:]
    else:
        lines.extend(["", block])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    findings = build_skin_findings()
    if len(findings) < 160:
        raise SystemExit(f"Expected at least 160 skin beauty findings, found {len(findings)}")
    topic_rows = build_topic_rows(findings)
    supplements = supplement_rows()
    write_csv(SKIN_FINDINGS, findings, FINDING_FIELDS)
    write_csv(SKIN_TOPICS, topic_rows, TOPIC_FIELDS)
    write_csv(SKIN_SUMMARY, topic_rows, TOPIC_FIELDS)
    write_csv(SUPPLEMENTS, supplements, SUPPLEMENT_FIELDS)
    write_skin_topic_pages(topic_rows, findings)
    write_summary_pages(topic_rows, supplements)
    patch_public_summary()
    print(f"Wrote {len(findings)} skin findings, {len(topic_rows)} skin topics, and {len(supplements)} supplement rows.")


if __name__ == "__main__":
    main()
