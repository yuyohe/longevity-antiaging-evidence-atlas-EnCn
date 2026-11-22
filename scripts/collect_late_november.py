"""Read-only public surveillance for the 2026-11-22 atlas release.

Run explicitly; all working files (including abstracts) remain under build/.
No grades, write APIs, publication, or changes to previous snapshots here.
"""
import argparse
import csv
import datetime as dt
import json
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "data/maintenance_2026_11"
CACHE = ROOT / "build/private-content/maintenance-2026-11-22"
END = "2026/11/22"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
SESSION = requests.Session()
SESSION.headers["User-Agent"] = "YulCell-EvidenceAtlas/1 (public metadata surveillance)"
ALERT = ('(dietary supplements[mh] OR cosmetics[mh] OR nutraceutical* OR PDRN OR '
         'polydeoxyribonucleotide OR polynucleotide filler OR skin booster OR retinol OR '
         'collagen supplement OR nicotinamide mononucleotide OR nicotinamide riboside) AND '
         '("Retracted Publication"[pt] OR "Expression of Concern"[pt] OR retract*[ti] OR '
         '"expression of concern"[ti])')


def load(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def dump(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    temp = p.with_suffix(".partial")
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(p)


def get(url, params=None):
    for attempt in range(3):
        time.sleep(.40)
        r = SESSION.get(url, params=params, timeout=(12, 40))
        if r.status_code not in (429, 500, 502, 503, 504) or attempt == 2:
            r.raise_for_status()
            return r
        time.sleep(min(30, int(r.headers.get("Retry-After") or 2**(attempt + 1))))


def plans():
    broad = load(ROOT / "queries/pubmed.json")
    cards = load(OLD / "card_plan.json")["cards"]
    for r in broad:
        yield r["name"], "atlas", r["query"], "2026/10/31", r["max_results"]
    for r in cards:
        yield r["id"], "card", r["query"], "2026/11/02", 9999
    yield "integrity-alert", "alert", ALERT, "2026/11/02", 9999


def search():
    path = CACHE / "search.json"
    log = load(path) if path.exists() else {}
    for key, group, term, start, cap in plans():
        # The first batch used publication date. Entrez date catches late indexing;
        # bound both paths so a later rerun cannot import subsequently indexed records.
        edat = f'("{start}"[edat] : "{END}"[edat])'
        pdat = f'("{start}"[dp] : "{END}"[dp])'
        known = f'("1900/01/01"[edat] : "{END}"[edat])'
        expr = f"({term}) AND ({edat} OR ({pdat} AND {known}))"
        if key in log:
            assert log[key]["query"] == expr
            continue
        r = get(EUTILS + "esearch.fcgi", {"db":"pubmed", "term":expr, "retmode":"json",
                                          "sort":"pub date", "retmax":cap})
        obj = r.json()["esearchresult"]
        if obj.get("errorlist"):
            raise ValueError((key, obj["errorlist"]))
        n, ids = int(obj["count"]), obj["idlist"]
        assert len(ids) == min(n, cap) and len(ids) == len(set(ids))
        log[key] = dict(group=group, start=start, end=END, query=expr, cap=cap, count=n,
                        pmids=ids, warnings=obj.get("warninglist", {}), url=r.url)
        dump(path, log)
        print(key, n, len(ids), flush=True)
    return log


def txt(node):
    return "".join(node.itertext()).strip() if node is not None else ""


def date(el):
    if el is None:
        return ""
    return "-".join(filter(None, [el.findtext("Year"), el.findtext("Month"), el.findtext("Day")])) or el.findtext("MedlineDate", "")


def parse(node):
    article = node.find("MedlineCitation/Article")
    ids = {i.get("IdType"):txt(i) for i in node.findall("PubmedData/ArticleIdList/ArticleId")}
    issue = date(article.find("Journal/JournalIssue/PubDate"))
    electronic = date(article.find("ArticleDate"))
    pmid = node.findtext("MedlineCitation/PMID")
    return dict(pmid=pmid, doi=ids.get("doi",""), pmcid=ids.get("pmc",""),
                title=txt(article.find("ArticleTitle")), journal=txt(article.find("Journal/Title")),
                year=(re.search(r"(?:19|20)\d\d", issue or electronic).group() if issue or electronic else ""),
                issue_date=issue, electronic_date=electronic,
                entrez_date=date(node.find("PubmedData/History/PubMedPubDate[@PubStatus='entrez']")),
                types=[txt(i) for i in article.findall("PublicationTypeList/PublicationType")],
                links=[dict(type=i.get("RefType"), pmid=i.findtext("PMID","")) for i in
                       node.findall("MedlineCitation/CommentsCorrectionsList/CommentsCorrections")],
                abstract=" ".join(txt(i) for i in article.findall("Abstract/AbstractText")),
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/")


def fetch(log):
    prior = [r["pmid"] for r in load(OLD / "source_metadata.json") if r.get("pmid")]
    required = set(prior).union(*(v["pmids"] for v in log.values()))
    path = CACHE / "pubmed-private.json"
    recs = load(path) if path.exists() else {}
    missing = sorted(required - set(recs))
    for i in range(0, len(missing), 70):
        ids = missing[i:i+70]
        root = ET.fromstring(get(EUTILS + "efetch.fcgi", {"db":"pubmed", "retmode":"xml",
                                                          "id":",".join(ids)}).content)
        batch = [parse(n) for n in root.findall("PubmedArticle")]
        if {p["pmid"] for p in batch} != set(ids):
            raise ValueError(("missing metadata", sorted(set(ids) - {p["pmid"] for p in batch})))
        recs.update({p["pmid"]:p for p in batch})
        dump(path, recs)
    print("Fetched", len(required), "including baseline checks", flush=True)


def tracked():
    items = []
    for prev in load(OLD / "trial_registry_checks.json"):
        nct = prev["nct_id"]
        obj = get("https://clinicaltrials.gov/api/v2/studies/" + nct).json()
        protocol = obj["protocolSection"]
        assert protocol["identificationModule"]["nctId"] == nct
        status = protocol["statusModule"]
        result = dict(status=status.get("overallStatus"), results=bool(obj.get("hasResults")),
                      last_posted=status["lastUpdatePostDateStruct"]["date"],
                      primary_measures=[o["measure"] for o in protocol["outcomesModule"]["primaryOutcomes"]])
        before = dict(status=prev["status"]["overallStatus"], results=prev["has_results"],
                      last_posted=prev["status"]["lastUpdatePostDateStruct"]["date"],
                      primary_measures=[o["measure"] for o in prev["primary_outcomes"]])
        items.append(dict(id=nct, source="ClinicalTrials.gov", url="https://clinicaltrials.gov/study/"+nct,
                          fields=result, changed=[k for k in result if result[k] != before[k]]))
    for prev in load(OLD / "crossref_checks.json"):
        doi = prev["doi"]
        obj = get("https://api.crossref.org/works/" + doi).json()["message"]
        assert obj["DOI"].lower() == doi.lower()
        fields = dict(title=obj["title"], type=obj["type"], update_to=obj.get("update-to", []))
        items.append(dict(id=doi, source="Crossref", url="https://doi.org/"+doi, fields=fields,
                          changed=[k for k,v in fields.items() if v != prev[k]]))
    dump(CACHE / "tracked.json", items)


def retractions():
    """Repeat the frozen 117 denominator/numerator pairs; retain warnings and IDs."""
    path = CACHE / "retraction-refresh.json"
    results = load(path) if path.exists() else {}
    with (ROOT / "data/retraction_risk_queries_20y.csv").open(encoding="utf-8-sig", newline="") as f:
        previous = list(csv.DictReader(f))
    for idx, old in enumerate(previous, 1):
        key = old["target_id"]
        if key in results:
            continue
        def q(field, cap):
            expr = old[field]
            assert expr.count("2026/10/30") == 1
            expr = expr.replace("2026/10/30", END)
            data = get(EUTILS + "esearch.fcgi", {"db":"pubmed", "retmode":"json",
                                                 "retmax":cap, "term":expr}).json()["esearchresult"]
            # Some historic title synonyms do not occur in the index. Do not suppress
            # that fact, or count a malformed field or an API failure as zero.
            issues = data.get("errorlist", {})
            if any(v for k,v in issues.items() if k != "phrasesnotfound") or not data.get("querytranslation"):
                raise ValueError((key, issues))
            return expr, int(data["count"]), data.get("idlist", []), issues, data.get("warninglist", {})
        den, total, _, er1, w1 = q("total_publication_query", 0)
        num, n, ids, er2, w2 = q("query", 9999)
        assert n == len(set(ids)) and n <= total
        results[key] = dict(name=old["name_zh"], group=old["domain"], denominator=total, retracted=n,
                            pmids=ids, old_denominator=int(old["pubmed_total_count_20y"]),
                            old_retracted=int(old["pubmed_retracted_count_20y"]),
                            old_pmids=old["retrieved_pmids"].split(";") if old["retrieved_pmids"] else [],
                            denominator_query=den, numerator_query=num, warnings=[er1,w1,er2,w2])
        dump(path, results)
        if idx % 10 == 0:
            print("retraction query pairs", idx, "/", len(previous), flush=True)


def linked():
    """Resolve the DOI-only entry and verify the other end of three notice links."""
    base = load(CACHE / "pubmed-private.json")
    ids = {v["pmid"] for i in ("42804222", "42965647", "42725387")
           for v in base[i]["links"] if v["pmid"] and
           v["type"] in ("ErratumIn", "ErratumFor", "ExpressionOfConcernFor")}
    doi = "10.1038/s41514-026-00482-7"
    result = get(EUTILS + "esearch.fcgi", {"db":"pubmed", "retmode":"json",
                 "term":f'"{doi}"[aid] AND ("1900/01/01"[edat] : "{END}"[edat])'}).json()["esearchresult"]
    assert len(result["idlist"]) <= 1
    ids.update(result["idlist"])
    data = ET.fromstring(get(EUTILS+"efetch.fcgi", {"db":"pubmed","retmode":"xml","id":",".join(sorted(ids))}).content)
    recs = [parse(el) for el in data.findall("PubmedArticle")]
    assert {r["pmid"] for r in recs} == ids
    assert all(r["doi"].lower() == doi for r in recs if r["pmid"] in result["idlist"])
    dump(CACHE / "linked-private.json", recs)
    print([(r["pmid"],r["title"],r["links"]) for r in recs])


def new_retraction_links():
    pairs = load(CACHE / "retraction-refresh.json")
    old = {p for v in pairs.values() for p in v["old_pmids"]}
    now = {p for v in pairs.values() for p in v["pmids"]}
    def batch(ids):
        if not ids:
            return []
        data = ET.fromstring(get(EUTILS+"efetch.fcgi", {"db":"pubmed", "retmode":"xml",
                                  "id":",".join(sorted(ids))}).content)
        records = [parse(el) for el in data.findall("PubmedArticle")]
        assert {r["pmid"] for r in records} == ids
        return records
    originals = batch(now - old)
    assert all("Retracted Publication" in r["types"] for r in originals)
    notices = batch({l["pmid"] for r in originals for l in r["links"] if l["type"]=="RetractionIn" and l["pmid"]})
    dump(CACHE / "new-retractions-private.json", {"originals": originals, "notices": notices})


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=["collect", "retractions", "linked", "notices"])
    mode = p.parse_args().mode
    if mode == "retractions":
        retractions()
    elif mode == "linked":
        linked()
    elif mode == "notices":
        new_retraction_links()
    else:
        log = search()
        fetch(log)
        tracked()
        dump(CACHE / "finished.json", {"ended_utc":dt.datetime.now(dt.timezone.utc).isoformat()})
