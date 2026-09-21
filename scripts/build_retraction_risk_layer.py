"""Build a retraction-risk layer for supplement, skin, and anti-aging claims.

Data source: PubMed E-utilities. The first version deliberately uses only
PubMed records tagged as "Retracted Publication" so the method is explainable
and repeatable without private databases.
"""

from __future__ import annotations

import csv
import json
import os
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CONTENT = ROOT / "content"
PUBLIC_READER = CONTENT / "public-reader"
OVERVIEW = CONTENT / "overview"
ANALYSIS = CONTENT / "analysis"
DOCS = ROOT / "docs"
CACHE = ROOT / "build" / "cache"
CACHE.mkdir(parents=True, exist_ok=True)

TODAY = os.environ.get("EVIDENCE_ATLAS_UPDATE_DATE", date.today().isoformat())
START_DATE = os.environ.get("RETRACTION_START_DATE", "2006/01/01")
END_DATE = os.environ.get("RETRACTION_END_DATE", TODAY.replace("-", "/"))
RETMAX = int(os.environ.get("RETRACTION_RETMAX", "300"))
FETCH_DETAILS = os.environ.get("RETRACTION_FETCH_DETAILS", "1") != "0"

SUMMARY_CSV = DATA / "retraction_risk_summary_20y.csv"
PUBLICATIONS_CSV = DATA / "retracted_publications_20y.csv"
QUERY_CSV = DATA / "retraction_risk_queries_20y.csv"

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
USER_AGENT = "longevity-evidence-atlas-retraction-layer/0.1"


SUPPLEMENT_CONTEXT = (
    '"dietary supplement"[Title/Abstract] OR "nutritional supplement"[Title/Abstract] '
    "OR supplement[Title] OR supplements[Title] OR supplementation[Title/Abstract] "
    "OR dietary[Title/Abstract] OR nutrition*[Title/Abstract] "
    "OR oral[Title/Abstract] OR intake[Title/Abstract] OR deficiency[Title/Abstract] "
    "OR diet[Title/Abstract] OR food[Title/Abstract] OR fortified[Title/Abstract] "
    "OR dose[Title/Abstract]"
)
SKIN_CONTEXT = (
    "skin[Title/Abstract] OR dermatolog*[Title/Abstract] OR photoaging[Title/Abstract] "
    "OR wrinkle*[Title/Abstract] OR pigment*[Title/Abstract] OR topical[Title/Abstract] "
    "OR sunscreen[Title/Abstract] OR barrier[Title/Abstract] OR cosmetic*[Title/Abstract]"
)
PDRN_CONTEXT = (
    "skin[Title/Abstract] OR dermatolog*[Title/Abstract] OR photoaging[Title/Abstract] "
    "OR wrinkle*[Title/Abstract] OR pigment*[Title/Abstract] OR topical[Title/Abstract] "
    "OR cosmetic*[Title/Abstract] OR filler[Title/Abstract] OR aesthetic*[Title/Abstract] "
    "OR rejuvenation[Title/Abstract] OR booster[Title/Abstract]"
)
ANTIAGING_CONTEXT = (
    "aging[Title/Abstract] OR ageing[Title/Abstract] OR longevity[Title/Abstract] "
    "OR healthspan[Title/Abstract] OR lifespan[Title/Abstract] OR senescence[Title/Abstract] "
    "OR age-related[Title/Abstract] OR anti-aging[Title/Abstract] OR anti-ageing[Title/Abstract]"
)


ALIASES: dict[str, list[str]] = {
    "omega-3": ["omega-3", "omega 3", "fish oil", "eicosapentaenoic acid", "docosahexaenoic acid"],
    "collagen-peptides": ["collagen peptide", "collagen peptides", "oral collagen", "hydrolyzed collagen"],
    "protein-eaa": ["essential amino acid", "essential amino acids"],
    "calcium-magnesium": ["calcium", "magnesium"],
    "coq10": ["coenzyme Q10", "CoQ10", "ubiquinone"],
    "probiotics": ["probiotic", "probiotics", "Lactobacillus", "Bifidobacterium"],
    "nmn": ["NMN", "nicotinamide mononucleotide"],
    "nr": ["nicotinamide riboside"],
    "nad-precursors": ["NAD precursor", "NAD precursors", "nicotinamide riboside", "nicotinamide mononucleotide"],
    "green-tea-catechins": ["green tea catechin", "green tea catechins", "EGCG", "epigallocatechin gallate"],
    "hyaluronic-acid": ["hyaluronic acid", "hyaluronan"],
    "vitamin-b12": ["vitamin B12", "cobalamin"],
    "vitamin-k2": ["vitamin K2", "menaquinone"],
    "psyllium": ["psyllium", "soluble fiber", "soluble fibre"],
    "beta-glucan": ["beta glucan", "beta-glucan"],
    "prebiotic-mix": ["prebiotic", "prebiotics"],
    "beta-carotene": ["beta carotene", "beta-carotene"],
    "alpha-lipoic-acid": ["alpha lipoic acid", "alpha-lipoic acid"],
    "nac": ["N-acetylcysteine", "N acetylcysteine", "NAC"],
    "l-carnitine": ["L-carnitine", "levocarnitine"],
    "acetyl-l-carnitine": ["acetyl-L-carnitine", "acetyl carnitine"],
    "collagen-type-ii": ["type II collagen", "undenatured type II collagen"],
    "msm": ["methylsulfonylmethane", "MSM"],
    "lions-mane": ["lion's mane", "Hericium erinaceus"],
    "red-yeast-rice": ["red yeast rice", "Monascus"],
    "d-mannose": ["D-mannose", "mannose"],
    "peppermint-oil": ["peppermint oil", "Mentha piperita"],
    "beetroot": ["beetroot", "dietary nitrate", "nitrate"],
    "cocoa-flavanols": ["cocoa flavanol", "cocoa flavanols", "cocoa polyphenol"],
    "olive-leaf": ["olive leaf", "oleuropein"],
    "black-seed-oil": ["black seed oil", "Nigella sativa"],
    "evening-primrose-oil": ["evening primrose oil"],
    "borage-oil": ["borage oil"],
    "cla": ["conjugated linoleic acid", "CLA"],
    "mct-oil": ["MCT oil", "medium chain triglyceride", "medium-chain triglyceride"],
    "sam-e": ["S-adenosylmethionine", "SAM-e"],
    "l-theanine": ["L-theanine", "theanine"],
    "5-htp": ["5-HTP", "5 hydroxytryptophan", "5-hydroxytryptophan"],
}

SKIN_TARGETS = [
    ("skin-sunscreen", "皮肤外用", "防晒", "Sunscreen", ["sunscreen", "photoprotection", "sun protection"], SKIN_CONTEXT),
    ("skin-retinoids", "皮肤外用", "维A酸/视黄醇", "Retinoids", ["retinoid", "retinoids", "retinol", "tretinoin"], SKIN_CONTEXT),
    ("skin-niacinamide", "皮肤外用", "烟酰胺", "Niacinamide", ["niacinamide", "nicotinamide"], SKIN_CONTEXT),
    ("skin-topical-vitamin-c", "皮肤外用", "外用维C", "Topical Vitamin C", ["vitamin C", "ascorbic acid"], SKIN_CONTEXT),
    ("skin-hyaluronic-acid", "皮肤外用", "透明质酸", "Hyaluronic Acid", ["hyaluronic acid", "hyaluronan"], SKIN_CONTEXT),
    ("skin-ceramides", "皮肤外用", "神经酰胺", "Ceramides", ["ceramide", "ceramides"], SKIN_CONTEXT),
    ("skin-polyphenols", "皮肤外用", "多酚/抗氧化剂", "Polyphenols", ["polyphenol", "polyphenols", "antioxidant"], SKIN_CONTEXT),
    ("skin-energy-devices", "皮肤外用", "医美能量设备", "Energy Devices", ["laser resurfacing", "microneedling", "chemical peel", "radiofrequency"], SKIN_CONTEXT),
    (
        "skin-pdrn-polynucleotide",
        "皮肤外用",
        "PDRN/PN/Skin Booster",
        "PDRN / Polynucleotide / Skin Booster",
        [
            "PDRN",
            "polydeoxyribonucleotide",
            "polydeoxyribonucleotides",
            "polynucleotide",
            "polynucleotides",
            "polynucleotide filler",
            "PN-HPT",
            "skin booster",
            "skin boosters",
        ],
        PDRN_CONTEXT,
    ),
]

ANTIAGING_TARGETS = [
    ("antiaging-metformin", "抗衰前沿", "二甲双胍", "Metformin", ["metformin"], ANTIAGING_CONTEXT),
    ("antiaging-rapamycin", "抗衰前沿", "雷帕霉素/mTOR", "Rapamycin", ["rapamycin", "sirolimus", "mTOR"], ANTIAGING_CONTEXT),
    ("antiaging-senolytics", "抗衰前沿", "Senolytics", "Senolytics", ["senolytic", "senolytics", "dasatinib", "quercetin"], ANTIAGING_CONTEXT),
    ("antiaging-nad", "抗衰前沿", "NAD/NMN/NR", "NAD/NMN/NR", ["NAD", "NMN", "nicotinamide mononucleotide", "nicotinamide riboside"], ANTIAGING_CONTEXT),
    ("antiaging-resveratrol", "抗衰前沿", "白藜芦醇", "Resveratrol", ["resveratrol"], ANTIAGING_CONTEXT),
    ("antiaging-epigenetic-clocks", "抗衰前沿", "表观遗传时钟", "Epigenetic Clocks", ["epigenetic clock", "DNA methylation age", "biological age"], ANTIAGING_CONTEXT),
    ("antiaging-telomere", "抗衰前沿", "端粒", "Telomere", ["telomere", "telomerase"], ANTIAGING_CONTEXT),
    ("antiaging-autophagy", "抗衰前沿", "自噬/线粒体自噬", "Autophagy/Mitophagy", ["autophagy", "mitophagy"], ANTIAGING_CONTEXT),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in fields} for row in rows])


def request_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(4):
        try:
            time.sleep(0.36)
            with urllib.request.urlopen(req, timeout=40) as resp:
                return resp.read().decode("utf-8")
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("PubMed request did not complete")


def term_clause(aliases: list[str]) -> str:
    parts = []
    for alias in aliases:
        alias = alias.strip()
        if not alias:
            continue
        escaped = alias.replace('"', "")
        parts.append(f'"{escaped}"[Title]')
    return " OR ".join(parts) or '"missing-term"[Title]'


def build_base_query(aliases: list[str], context: str) -> str:
    date_window = f'("{START_DATE}"[Date - Publication] : "{END_DATE}"[Date - Publication])'
    return f"({term_clause(aliases)}) AND ({context}) AND {date_window}"


def build_retraction_query(aliases: list[str], context: str) -> str:
    return f"{build_base_query(aliases, context)} AND \"Retracted Publication\"[Publication Type]"


def search_pubmed(query: str) -> tuple[int, list[str]]:
    params = {
        "db": "pubmed",
        "retmode": "json",
        "retmax": str(RETMAX),
        "term": query,
    }
    email = os.getenv("NCBI_EMAIL", "")
    api_key = os.getenv("NCBI_API_KEY", "")
    if email:
        params["email"] = email
    if api_key:
        params["api_key"] = api_key
    url = f"{EUTILS}/esearch.fcgi?" + urllib.parse.urlencode(params)
    data = json.loads(request_text(url))
    result = data.get("esearchresult", {})
    return int(result.get("count", 0)), result.get("idlist", [])


def search_pubmed_count(query: str) -> int:
    params = {
        "db": "pubmed",
        "retmode": "json",
        "retmax": "0",
        "term": query,
    }
    email = os.getenv("NCBI_EMAIL", "")
    api_key = os.getenv("NCBI_API_KEY", "")
    if email:
        params["email"] = email
    if api_key:
        params["api_key"] = api_key
    url = f"{EUTILS}/esearch.fcgi?" + urllib.parse.urlencode(params)
    data = json.loads(request_text(url))
    return int(data.get("esearchresult", {}).get("count", 0))


def fetch_pubmed(pmids: list[str]) -> list[dict[str, str]]:
    if not pmids or not FETCH_DETAILS:
        return []
    params = {"db": "pubmed", "retmode": "xml", "id": ",".join(pmids)}
    email = os.getenv("NCBI_EMAIL", "")
    api_key = os.getenv("NCBI_API_KEY", "")
    if email:
        params["email"] = email
    if api_key:
        params["api_key"] = api_key
    url = f"{EUTILS}/efetch.fcgi?" + urllib.parse.urlencode(params)
    root = ET.fromstring(request_text(url))
    out: list[dict[str, str]] = []
    for article in root.findall(".//PubmedArticle"):
        pmid = text(article.find(".//MedlineCitation/PMID"))
        title = " ".join("".join(article.find(".//ArticleTitle").itertext()).split()) if article.find(".//ArticleTitle") is not None else ""
        journal = text(article.find(".//Journal/Title"))
        year = article_year(article)
        pub_types = "; ".join(text(node) for node in article.findall(".//PublicationTypeList/PublicationType") if text(node))
        doi = ""
        pmcid = ""
        for aid in article.findall("./PubmedData/ArticleIdList/ArticleId"):
            if aid.attrib.get("IdType") == "doi":
                doi = text(aid)
            if aid.attrib.get("IdType") == "pmc":
                pmcid = text(aid)
        notices = []
        for cc in article.findall(".//CommentsCorrectionsList/CommentsCorrections"):
            ref_type = cc.attrib.get("RefType", "")
            ref_pmid = text(cc.find("PMID"))
            note = text(cc.find("Note"))
            if ref_type or ref_pmid or note:
                notices.append(f"{ref_type}:{ref_pmid}:{note}".strip(":"))
        out.append(
            {
                "pmid": pmid,
                "title": title,
                "journal": journal,
                "year": year,
                "publication_types": pub_types,
                "doi": doi,
                "pmcid": pmcid,
                "retraction_links": " | ".join(notices),
                "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
            }
        )
    return out


def text(node: ET.Element | None) -> str:
    if node is None:
        return ""
    return "".join(node.itertext()).strip()


def article_year(article: ET.Element) -> str:
    for xpath in [".//JournalIssue/PubDate/Year", ".//ArticleDate/Year"]:
        value = text(article.find(xpath))
        if value:
            return value
    medline = text(article.find(".//JournalIssue/PubDate/MedlineDate"))
    match = re.search(r"(19|20)\d{2}", medline)
    return match.group(0) if match else ""


def supplement_targets() -> list[tuple[str, str, str, str, list[str], str]]:
    rows = read_csv(DATA / "supplement_matrix.csv")
    targets = []
    for row in rows:
        sid = row["supplement_id"]
        aliases = ALIASES.get(sid)
        if not aliases:
            aliases = []
            for part in re.split(r"/|,", row.get("name_en", "")):
                part = part.strip()
                if part and part.lower() not in {"protein", "extract", "mix"}:
                    aliases.append(part)
            if not aliases:
                aliases = [row.get("name_en", sid).replace("-", " ")]
        targets.append((sid, "口服/补剂", row["name_zh"], row["name_en"], aliases, SUPPLEMENT_CONTEXT))
    return targets


def all_targets() -> list[tuple[str, str, str, str, list[str], str]]:
    return supplement_targets() + SKIN_TARGETS + ANTIAGING_TARGETS


def risk_label(count: int) -> str:
    if count >= 50:
        return "高撤稿观察量"
    if count >= 10:
        return "中等撤稿观察量"
    if count >= 1:
        return "低撤稿观察量"
    return "未检出撤稿记录"


def reader_note(count: int) -> str:
    if count >= 50:
        return "这个主题相关撤稿记录较多，读到夸张宣传时要特别谨慎。"
    if count >= 10:
        return "这个主题有一定撤稿记录，不能只看单篇论文或营销摘要。"
    if count >= 1:
        return "这个主题检出过撤稿记录，说明仍需要看研究质量和复核状态。"
    return "这不等于完全没有问题，只表示本轮 PubMed 检索未发现匹配撤稿记录。"


def window_years() -> float:
    start = datetime.strptime(START_DATE.replace("/", "-"), "%Y-%m-%d").date()
    end = datetime.strptime(END_DATE.replace("/", "-"), "%Y-%m-%d").date()
    return max((end - start).days / 365.25, 1.0)


def rate_percent(retracted_count: int, total_count: int) -> str:
    if total_count <= 0:
        return ""
    return f"{retracted_count / total_count * 100:.3f}"


def rate_per_1000(retracted_count: int, total_count: int) -> str:
    if total_count <= 0:
        return ""
    return f"{retracted_count / total_count * 1000:.2f}"


def avg_per_year(total_count: int) -> str:
    return f"{total_count / window_years():.1f}"


def publication_volume_label(total_count: int) -> str:
    if total_count >= 1000:
        return "大分母"
    if total_count >= 200:
        return "中等分母"
    if total_count >= 50:
        return "小分母"
    if total_count > 0:
        return "很小分母"
    return "未检出分母"


def density_label(retracted_count: int, total_count: int) -> str:
    if retracted_count <= 0:
        return "未检出撤稿"
    if total_count < 20:
        return "分母太小，比例不稳"
    density = retracted_count / total_count * 1000
    if density >= 20 and retracted_count >= 3:
        return "高撤稿密度"
    if density >= 5 and retracted_count >= 2:
        return "中等撤稿密度"
    if retracted_count >= 10:
        return "数量型风险"
    return "低撤稿密度"


def denominator_note(retracted_count: int, total_count: int) -> str:
    if total_count <= 0:
        return "本轮没有检出可作为分母的相关发表。"
    density = rate_per_1000(retracted_count, total_count)
    if total_count < 20:
        return f"分母只有 {total_count} 篇，撤稿比例容易被单篇记录放大。"
    return f"同一口径下总发表 {total_count} 篇；每 1000 篇约 {density} 篇撤稿。"


def build() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    summary_rows: list[dict[str, str]] = []
    query_rows: list[dict[str, str]] = []
    pub_rows: list[dict[str, str]] = []
    details_cache: dict[str, dict[str, str]] = {}
    target_count = len(all_targets())
    for i, (target_id, domain, name_zh, name_en, aliases, context) in enumerate(all_targets(), 1):
        base_query = build_base_query(aliases, context)
        query = build_retraction_query(aliases, context)
        try:
            total_count = search_pubmed_count(base_query)
            count, pmids = search_pubmed(query)
        except Exception as exc:
            total_count, count, pmids = 0, 0, []
            error = str(exc)
        else:
            error = ""
        query_rows.append(
            {
                "target_id": target_id,
                "domain": domain,
                "name_zh": name_zh,
                "name_en": name_en,
                "aliases": "; ".join(aliases),
                "total_publication_query": base_query,
                "query": query,
                "pubmed_total_count_20y": str(total_count),
                "pubmed_retracted_count_20y": str(count),
                "retraction_rate_percent": rate_percent(count, total_count),
                "retractions_per_1000_publications": rate_per_1000(count, total_count),
                "retrieved_pmids": ";".join(pmids),
                "error": error,
                "last_checked": TODAY,
            }
        )
        fetched = fetch_pubmed(pmids)
        for item in fetched:
            details_cache.setdefault(item["pmid"], item)
            pub_rows.append(
                {
                    "target_id": target_id,
                    "domain": domain,
                    "name_zh": name_zh,
                    "name_en": name_en,
                    **item,
                    "last_checked": TODAY,
                }
            )
        years = [int(item["year"]) for item in fetched if item.get("year", "").isdigit()]
        summary_rows.append(
            {
                "target_id": target_id,
                "domain": domain,
                "name_zh": name_zh,
                "name_en": name_en,
                "pubmed_total_count_20y": str(total_count),
                "avg_publications_per_year_20y": avg_per_year(total_count),
                "pubmed_retracted_count_20y": str(count),
                "retraction_rate_percent": rate_percent(count, total_count),
                "retractions_per_1000_publications": rate_per_1000(count, total_count),
                "publication_volume_bucket": publication_volume_label(total_count),
                "normalized_risk_bucket": density_label(count, total_count),
                "retrieved_publication_rows": str(len(fetched)),
                "unique_pmids_retrieved": str(len(set(pmids))),
                "most_recent_retracted_year": str(max(years)) if years else "",
                "risk_bucket": risk_label(count),
                "reader_note_zh": reader_note(count),
                "denominator_note_zh": denominator_note(count, total_count),
                "query_scope_zh": "PubMed 近20年；分母为同一题名/语境检索下的总发表量，分子为其中 PubMed Retracted Publication。",
                "last_checked": TODAY,
            }
        )
        time.sleep(0.12 if os.getenv("NCBI_API_KEY") else 0.35)
        if i % 10 == 0:
            print(f"Retraction queries: {i}/{target_count}")
    summary_rows.sort(key=lambda r: (int(r["pubmed_retracted_count_20y"]), r["domain"], r["name_zh"]), reverse=True)
    pub_rows.sort(key=lambda r: (r["domain"], r["target_id"], r.get("year", ""), r.get("pmid", "")), reverse=True)
    return summary_rows, pub_rows, query_rows


def top_by_domain(rows: list[dict[str, str]], domain: str, limit: int = 12) -> list[dict[str, str]]:
    return [row for row in rows if row["domain"] == domain and int(row["pubmed_retracted_count_20y"]) > 0][:limit]


def density_value(row: dict[str, str]) -> float:
    try:
        return float(row.get("retractions_per_1000_publications", "") or 0)
    except ValueError:
        return 0.0


def total_value(row: dict[str, str]) -> int:
    try:
        return int(row.get("pubmed_total_count_20y", "") or 0)
    except ValueError:
        return 0


def top_by_density(rows: list[dict[str, str]], limit: int = 12, min_total: int = 20) -> list[dict[str, str]]:
    eligible = [
        row
        for row in rows
        if int(row.get("pubmed_retracted_count_20y", "0") or 0) > 0 and total_value(row) >= min_total
    ]
    eligible.sort(key=lambda row: (density_value(row), int(row["pubmed_retracted_count_20y"])), reverse=True)
    return eligible[:limit]


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(cell).replace("|", "/") for cell in row) + " |")
    return "\n".join(out)


def write_docs(summary: list[dict[str, str]], publications: list[dict[str, str]]) -> None:
    oral = top_by_domain(summary, "口服/补剂", 15)
    skin = top_by_domain(summary, "皮肤外用", 10)
    anti = top_by_domain(summary, "抗衰前沿", 10)
    density_top = top_by_density(summary, 12)
    total_retraction_rows = len(publications)
    unique_retracted_pmids = len({row["pmid"] for row in publications if row.get("pmid")})
    top_oral = oral[0] if oral else {}
    top_anti = anti[0] if anti else {}
    top_skin = skin[0] if skin else {}
    pdrn = next((row for row in summary if row["target_id"] == "skin-pdrn-polynucleotide"), {})
    pdrn_publications = [row for row in publications if row.get("target_id") == "skin-pdrn-polynucleotide"]
    pdrn_section = ""
    if pdrn:
        pdrn_section = f"""
## PDRN/PN 专门观察

PDRN/PN 是本项目单独放大的美容主题，因为它同时出现在化妆品叙事、注射、skin booster、填充和导入类项目里。按本轮保守口径，PDRN/PN/Skin Booster 总发表量为 **{pdrn.get('pubmed_total_count_20y', '0')} 篇**，年均约 **{pdrn.get('avg_publications_per_year_20y', '')} 篇**，撤稿记录为 **{pdrn.get('pubmed_retracted_count_20y', '0')} 条**，每 1000 篇约 **{pdrn.get('retractions_per_1000_publications', '')}** 条撤稿。这个数量不是全库最高，但撤回文献触及医美填充、skin booster 分类和年轻化研究，传播风险比普通成分更高。

{md_table(["PMID", "年份", "期刊", "题名"], [[r["pmid"], r["year"], r["journal"], r["title"]] for r in pdrn_publications[:8]])}
"""

    public = f"""# 撤稿风险怎么看

这页回答一个问题：我们不仅看“有没有论文”，也看这个领域有没有撤稿记录。

## 一句话

论文被撤稿，意思是这篇论文后来被期刊或作者标记为不应继续当作可靠依据。撤稿不等于一个成分一定没用，也不等于所有相关研究都错了；它提醒我们：这个方向更需要看研究质量、复核状态和是否被夸大宣传。

## 我们这次怎么查

- 时间：{START_DATE} 到 {END_DATE}，按被撤稿论文的发表日期统计。
- 来源：PubMed。
- 只统计 PubMed 标记为 `Retracted Publication` 的记录。
- 目标成分或主题词必须出现在论文题名里；题名或摘要还要匹配到补剂、护肤或抗衰语境。
- 分母是同一口径下的 PubMed 总发表量；分子是其中被标记为撤稿的论文。
- 核心比较参数是“每 1000 篇相关发表中的撤稿数”，用来避免只看撤稿绝对数量。
- 不用论坛、广告文案、新闻稿来算撤稿。

## 我们的门槛

不是网上出现过的每个说法都会进入这里。先进入本项目的资产库，再做撤稿观察。

| 门槛 | 人话解释 |
| --- | --- |
| 先在资产库里 | 只看我们已经纳入的补剂、护肤和抗衰前沿主题 |
| 先看证据权重 | 人体相关性、研究设计、终点、样本、期刊和偏倚风险都要一起看 |
| 再查撤稿 | 在这个主题上额外查 PubMed 近 20 年撤稿记录 |
| 保守匹配 | 成分或主题词必须出现在论文题名里，减少误算 |
| 不当正向证据 | 被撤稿的论文只用来提醒风险，不用来支持购买或尝试 |

## 普通人怎么理解

| 看到什么 | 应该怎么想 |
| --- | --- |
| 某成分撤稿多 | 说明这个方向需要更谨慎，不代表它一定无效 |
| 某成分撤稿少 | 不代表绝对安全或一定有效，只表示本轮 PubMed 没查到很多撤稿 |
| 撤稿数高但总发表量也很大 | 说明要同时看撤稿密度，不能只按数量排序 |
| 总发表量很小但撤稿比例高 | 这是警示信号，但比例也可能不稳定 |
| 商家只拿单篇论文宣传 | 要看是否有人体研究、终点是否够硬、有没有撤稿或利益冲突 |
| 论文很多 | 论文多不等于证据强，还要看设计、终点、人群和复核 |

## 本轮谁撤稿记录最多

口服/补剂相关，本轮 PubMed 检索中撤稿记录最多的是：**{top_oral.get('name_zh','未检出')}**（{top_oral.get('pubmed_retracted_count_20y','0')} 条）。

抗衰前沿相关，本轮撤稿记录最多的是：**{top_anti.get('name_zh','未检出')}**（{top_anti.get('pubmed_retracted_count_20y','0')} 条）。

皮肤外用/医美相关，本轮撤稿记录最多的是：**{top_skin.get('name_zh','未检出')}**（{top_skin.get('pubmed_retracted_count_20y','0')} 条）。

{pdrn_section}

## 按撤稿密度看

撤稿密度 = 撤稿记录数 / 同口径总发表量 × 1000。分母小于 20 篇的主题暂不进入这张表，因为比例太容易被单篇记录放大。

{md_table(["主题", "领域", "总发表", "年均发表", "撤稿", "每1000篇撤稿", "密度判断"], [[r["name_zh"], r["domain"], r["pubmed_total_count_20y"], r["avg_publications_per_year_20y"], r["pubmed_retracted_count_20y"], r["retractions_per_1000_publications"], r["normalized_risk_bucket"]] for r in density_top])}

## 口服/补剂撤稿观察排行

{md_table(["成分", "英文", "总发表", "年均发表", "撤稿", "每1000篇撤稿", "怎么理解"], [[r["name_zh"], r["name_en"], r["pubmed_total_count_20y"], r["avg_publications_per_year_20y"], r["pubmed_retracted_count_20y"], r["retractions_per_1000_publications"], r["denominator_note_zh"]] for r in oral[:12]])}

## 抗衰前沿撤稿观察排行

{md_table(["主题", "英文", "总发表", "年均发表", "撤稿", "每1000篇撤稿", "怎么理解"], [[r["name_zh"], r["name_en"], r["pubmed_total_count_20y"], r["avg_publications_per_year_20y"], r["pubmed_retracted_count_20y"], r["retractions_per_1000_publications"], r["denominator_note_zh"]] for r in anti[:10]])}

## 护肤/外观撤稿观察排行

{md_table(["主题", "英文", "总发表", "年均发表", "撤稿", "每1000篇撤稿", "怎么理解"], [[r["name_zh"], r["name_en"], r["pubmed_total_count_20y"], r["avg_publications_per_year_20y"], r["pubmed_retracted_count_20y"], r["retractions_per_1000_publications"], r["denominator_note_zh"]] for r in skin[:10]])}

## 注意

- 撤稿数量会受研究热度影响。研究越多，可能被发现问题的机会也越多。
- PubMed 不是全世界所有撤稿的完整数据库，所以这页是观察层，不是最终裁判。
- 这页不提供购买、停用、剂量或治疗建议。
- 如果一个产品只靠“某篇论文”卖点宣传，先查证据等级和撤稿风险。
"""
    (PUBLIC_READER / "retractions.md").write_text(public.rstrip() + "\n", encoding="utf-8")

    methodology = f"""# 撤稿风险观察方法 / Retraction Risk Methodology

Last updated / 更新时间：{TODAY}

## 目的

本模块用于补充 v0.5 证据评分。v0.5 已经评价研究设计、终点、人群、来源深度、文章影响力、发表地/期刊层级和风险边界；撤稿风险层回答另一个问题：某个成分或主题在公开文献中是否出现过撤稿记录。

## 纳入门槛

一条记录进入本模块，需要同时满足：

1. 来源为 PubMed。
2. PubMed Publication Type 包含 `Retracted Publication`。
3. 被撤稿论文的发表日期在 {START_DATE} 到 {END_DATE}。
4. 成分或主题词必须匹配题名，题名或摘要再匹配本项目补剂、护肤、抗衰前沿语境。
5. 查询必须可复跑，查询式写入 `data/retraction_risk_queries_20y.csv`。

## 分母和归一化指标

撤稿记录数是分子，不能单独比较。每个目标还会记录同一检索口径下的 PubMed 总发表量作为分母。

| 字段 | 含义 |
| --- | --- |
| `pubmed_total_count_20y` | 同一题名/语境/时间窗下的总发表量 |
| `pubmed_retracted_count_20y` | 其中被 PubMed 标记为撤稿的论文数 |
| `retraction_rate_percent` | 撤稿数 / 总发表量 × 100% |
| `retractions_per_1000_publications` | 撤稿数 / 总发表量 × 1000 |
| `avg_publications_per_year_20y` | 近 20 年窗口内年均发表量 |
| `normalized_risk_bucket` | 综合分母和撤稿密度后的风险标签 |

## 输出文件

| 文件 | 作用 |
| --- | --- |
| `data/retraction_risk_summary_20y.csv` | 每个成分/主题的撤稿计数和读者解释 |
| `data/retracted_publications_20y.csv` | 匹配到的撤稿 PubMed 记录清单 |
| `data/retraction_risk_queries_20y.csv` | 每个成分/主题的 PubMed 查询式 |
| `content/public-reader/retractions.md` | 普通读者解释页 |
| `content/analysis/retraction-risk-ranking.md` | 研究维护用排行 |

## 解释边界

- 撤稿多不等于成分一定无效。
- 撤稿少不等于成分一定有效或安全。
- 被撤稿的论文不作为正向证据，只作为风险观察记录。
- 撤稿数量受研究热度、期刊审查、数据库覆盖范围影响。
- 本模块暂不使用非公开或需授权数据库；后续可接入 Retraction Watch Database 等更完整来源，但需要遵守其使用条款。

## 本轮规模

- 目标成分/主题：{len(summary)} 个。
- 匹配撤稿记录行：{total_retraction_rows} 行。
- 去重 PMID：{unique_retracted_pmids} 个。
"""
    (OVERVIEW / "retraction-risk-methodology.md").write_text(methodology.rstrip() + "\n", encoding="utf-8")

    ranking_lines = [
        "# 撤稿风险观察排行 / Retraction Risk Ranking",
        "",
        f"Last updated / 更新时间：{TODAY}",
        "",
        "数据源：PubMed `Retracted Publication`，近 20 年窗口。撤稿数不是有效性评分，只是风险观察信号。",
        "",
        "分母：同一题名/语境/时间窗下的 PubMed 总发表量。每 1000 篇撤稿数用于横向比较。",
        "",
        "| Rank | Domain | Name | English | Total records | Retracted records | Per 1000 | Density bucket | Note |",
        "|---:|---|---|---|---:|---:|---:|---|---|",
    ]
    for i, row in enumerate(summary[:80], 1):
        ranking_lines.append(
            f"| {i} | {row['domain']} | {row['name_zh']} | {row['name_en']} | {row['pubmed_total_count_20y']} | {row['pubmed_retracted_count_20y']} | {row['retractions_per_1000_publications']} | {row['normalized_risk_bucket']} | {row['denominator_note_zh']} |"
        )
    (ANALYSIS / "retraction-risk-ranking.md").write_text("\n".join(ranking_lines) + "\n", encoding="utf-8")

    report = f"""# 撤稿风险层实施报告

日期：{TODAY}

## 这次新增

- `data/retraction_risk_summary_20y.csv`
- `data/retracted_publications_20y.csv`
- `data/retraction_risk_queries_20y.csv`
- `content/public-reader/retractions.md`
- `content/overview/retraction-risk-methodology.md`
- `content/analysis/retraction-risk-ranking.md`

## 结果摘要

- 目标成分/主题：{len(summary)} 个。
- 匹配撤稿记录行：{total_retraction_rows} 行。
- 去重 PMID：{unique_retracted_pmids} 个。
- 口服/补剂最高：{top_oral.get('name_zh','未检出')}，{top_oral.get('pubmed_retracted_count_20y','0')} 条。
- 抗衰前沿最高：{top_anti.get('name_zh','未检出')}，{top_anti.get('pubmed_retracted_count_20y','0')} 条。
- 皮肤外用最高：{top_skin.get('name_zh','未检出')}，{top_skin.get('pubmed_retracted_count_20y','0')} 条。
- PDRN/PN/Skin Booster：{pdrn.get('pubmed_retracted_count_20y','0')} 条，已在普通读者撤稿页单独放大。

## 新增分母指标

- `pubmed_total_count_20y`：同一检索口径下的总发表量。
- `avg_publications_per_year_20y`：年均发表量，用来判断主题热度。
- `retractions_per_1000_publications`：每 1000 篇撤稿数，用来横向比较不同主题。
- `normalized_risk_bucket`：结合分母和撤稿密度后的标签。

## 发布建议

普通读者页可以作为创新点展示：我们不只看论文数量，也记录撤稿风险。对外表达必须保留边界：撤稿数是风险观察信号，不是成分有效性或安全性的最终判断。
"""
    (DOCS / f"retraction-risk-layer-report-{TODAY}.md").write_text(report.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    summary, publications, queries = build()
    failed = [row['target_id'] for row in queries if row.get('error')]
    incomplete = [row['target_id'] for row in summary if int(row['retrieved_publication_rows']) != int(row['pubmed_retracted_count_20y'])]
    if failed or incomplete:
        raise RuntimeError(f"Retraction refresh stopped before writes: failed={failed}, incomplete={incomplete}")
    write_csv(
        SUMMARY_CSV,
        summary,
        [
            "target_id",
            "domain",
            "name_zh",
            "name_en",
            "pubmed_total_count_20y",
            "avg_publications_per_year_20y",
            "pubmed_retracted_count_20y",
            "retraction_rate_percent",
            "retractions_per_1000_publications",
            "publication_volume_bucket",
            "normalized_risk_bucket",
            "retrieved_publication_rows",
            "unique_pmids_retrieved",
            "most_recent_retracted_year",
            "risk_bucket",
            "reader_note_zh",
            "denominator_note_zh",
            "query_scope_zh",
            "last_checked",
        ],
    )
    write_csv(
        PUBLICATIONS_CSV,
        publications,
        [
            "target_id",
            "domain",
            "name_zh",
            "name_en",
            "pmid",
            "title",
            "journal",
            "year",
            "publication_types",
            "doi",
            "pmcid",
            "retraction_links",
            "pubmed_url",
            "last_checked",
        ],
    )
    write_csv(
        QUERY_CSV,
        queries,
        [
            "target_id",
            "domain",
            "name_zh",
            "name_en",
            "aliases",
            "total_publication_query",
            "query",
            "pubmed_total_count_20y",
            "pubmed_retracted_count_20y",
            "retraction_rate_percent",
            "retractions_per_1000_publications",
            "retrieved_pmids",
            "error",
            "last_checked",
        ],
    )
    write_docs(summary, publications)
    print(
        "Retraction layer built: "
        f"targets={len(summary)}, publication_rows={len(publications)}, unique_pmids={len({r.get('pmid') for r in publications if r.get('pmid')})}"
    )


if __name__ == "__main__":
    main()
