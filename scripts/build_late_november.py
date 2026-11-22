"""Build the public 22 November snapshot from verified cached responses; no network."""
import csv
import json
import os
from collections import defaultdict
from pathlib import Path

from collect_late_november import ROOT, OLD, CACHE, dump, load

OUT = ROOT / "data/maintenance_2026_11_22"
PNG = ROOT / "docs/assets/maintenance-2026-11-22/retraction-density.png"
DAY = "2026-11-22"


def read(path, sep=","):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=sep))


def write(name, values):
    with (OUT / name).open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(values[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(values)


def index(rows, key):
    pairs = [(r[key].strip().lower(),r) for r in rows if r[key]]
    result = dict(pairs)
    assert len(result) == len(pairs), ("duplicate identifier", key)
    return result


def relevant(links):
    return sorted((el["type"],el["pmid"]) for el in links if any(k in el["type"] for k in
                  ("Retraction","Erratum","Concern","Corrected","Republished","Update")))


def run():
    log = load(CACHE / "search.json")
    assert len(log) == 59 and len(load(CACHE / "tracked.json")) == 7
    rec = load(CACHE / "pubmed-private.json")
    selected = index(read(OUT / "editorial.tsv", "\t"), "pmid")
    hits = defaultdict(list)
    for key, q in log.items():
        for pmid in q["pmids"]:
            hits[pmid].append(key)
    card_hits = {p for p, keys in hits.items() if any(k.startswith("NOV26-") for k in keys)}
    assert set(selected).issubset(hits) and card_hits.issubset(selected)
    dump(OUT / "search.json", log)
    write("retrieval.csv", [dict(pmid=p, doi=rec[p]["doi"], title_en=rec[p]["title"],
          journal=rec[p]["journal"], electronic_date=rec[p]["electronic_date"], issue_date=rec[p]["issue_date"],
          entrez_date=rec[p]["entrez_date"], matched_queries=";".join(keys),
          disposition=selected.get(p,{}).get("action","search_log_only_not_appraised"), url=rec[p]["url"])
          for p,keys in sorted(hits.items())])
    orig = read(OLD / "literature_library_merged.csv")
    candidates = read(OLD / "candidate_sources_merged.csv")
    by_p, by_d = index(candidates,"pmid"), index(candidates,"doi")
    by_l = index(orig,"library_id")
    assert set(by_l) == set(index(candidates, "id"))
    increment, existing = [], []
    for p,s in selected.items():
        if s["action"] != "candidate":
            continue
        r = rec[p]
        assert "Retracted Publication" not in r["types"] and not any("Concern" in n[0] or
               "Retraction" in n[0] for n in relevant(r["links"]))
        matched = {v["id"] for v in (by_p.get(p), by_d.get(r["doi"].lower())) if v}
        assert len(matched) <= 1
        if matched:
            key = matched.pop()
            assert by_l[key]["pmid"] == p and by_l[key]["doi"].lower() == r["doi"].lower()
            existing.append(key)
            by_l[key]["last_checked"] = DAY
            continue
        key = "pubmed-" + p
        assert key not in by_l
        core = dict(title_en=r["title"],title_zh=s["short_title_zh"],year=r["year"],
                    doi=r["doi"],pmid=p,pmcid=r["pmcid"],url=r["url"],source="PubMed",
                    query="late_nov_2026:"+hits[p][0],include_status="candidate_metadata_pending_full_appraisal",
                    last_checked=DAY)
        increment.append(dict(id=key, **core, notes=s["reason_zh"]))
        row = {k:"" for k in orig[0]}
        row.update(library_id=key, **core, in_healthspan_findings="false", in_evidence_matrix="false",
                   in_skin_beauty_findings="false")
        orig.append(row)
    for field in ("library_id","pmid","doi"):
        index(orig,field)
    write("new-candidates.csv", increment)
    write("literature-library.csv", orig)
    old = [v for v in load(OLD / "source_metadata.json") if v.get("pmid")]
    tracked = load(CACHE / "tracked.json")
    prev_checks = []
    for o in old:
        p = o["pmid"]
        prev, new = relevant(o["notices"]), relevant(rec[p]["links"])
        tagset = {"Retracted Publication","Retraction Notice","Expression of Concern"}
        prev_checks.append(dict(pmid=p, old_links=prev, current_links=new,
                 current_status_tags=sorted(tagset.intersection(rec[p]["types"])),
                 changed=prev != new or bool((set(o["publication_types"]) ^ set(rec[p]["types"])) & tagset)))
    extra = load(CACHE / "linked-private.json")
    dump(OUT / "source-checks.json", dict(baseline_pubmed=prev_checks, registries_and_dois=tracked,
          linked_records=[{k:r[k] for k in ("pmid","doi","title","links","url")} for r in extra],
          notice_sources=[{k:rec[p][k] for k in ("pmid","doi","title","links","url")}
                          for p,s in selected.items() if s["action"]=="notice"]))
    rates = load(CACHE / "retraction-refresh.json")
    assert len(rates)==117
    dump(OUT / "retraction-queries.json",rates)
    write("retraction-density.csv",[dict(target=k, topic_zh=r["name"], denominator=r["denominator"],
          retracted=r["retracted"], per_1000=round(1000*r["retracted"]/r["denominator"],2) if r["denominator"] else "",
          previous_denominator=r["old_denominator"],previous_retracted=r["old_retracted"],
          pmids=";".join(r["pmids"]), checked=DAY) for k,r in rates.items()])
    n = load(CACHE / "new-retractions-private.json")
    notices = {r["pmid"]:r for r in n["notices"]}
    intake_pmids = set(index(orig,"pmid"))
    details = []
    for r in n["originals"]:
        for link in r["links"]:
            if link["type"] != "RetractionIn" or not link["pmid"]:
                continue
            no = notices[link["pmid"]]
            details.append(dict(pmid=r["pmid"],title_en=r["title"],notice_pmid=no["pmid"],
                          notice_online_date=no["electronic_date"], notice_issue=no["issue_date"],
                          original_in_current_intake=r["pmid"] in intake_pmids, notice_url=no["url"]))
    write("new-retraction-matches.csv", details)
    new_ids={p for r in rates.values() for p in r["pmids"]}
    old_ids={p for r in rates.values() for p in r["old_pmids"]}
    assert {r["pmid"] for r in details} == new_ids - old_ids
    stats=dict(cutoff=DAY,base_commit="112fd91d92c2257b873ea52ce363107b070c6910",
               unique_sampled_pmids=len(hits),ingredient_unique=len(card_hits),topic_queries=38,
               card_queries=20,integrity_queries=1,capped_topic_queries=sum(q["count"]>q["cap"] for q in log.values()),
               selected_candidates=len(increment)+len(existing),new_candidates=len(increment),known_candidates=existing,
               baseline=len(candidates),current=len(orig),current_unique_pmids=len(intake_pmids),
               individual_decisions=len(selected),baseline_pubmed_checks=len(prev_checks),
               baseline_integrity_changes=sum(x["changed"] for x in prev_checks),tracked_fields_changed=sum(bool(x["changed"]) for x in tracked),
               formal_promotions=0,formal_grade_changes=0,retraction_topics=len(rates),
               old_unique_retracted=len(old_ids),current_unique_retracted=len(new_ids),
               current_retraction_matches=sum(v["retracted"] for v in rates.values()),
               new_unique_retraction_matches=len(new_ids-old_ids),dropped_retraction_matches=len(old_ids-new_ids),
               new_retracted_in_intake=len((new_ids-old_ids)&intake_pmids))
    dump(OUT / "summary.json",stats)
    chart(rates)
    print(json.dumps(stats,ensure_ascii=False))


def chart(rates):
    from PIL import Image, ImageDraw, ImageFont
    canvas = Image.new("RGB",(1080,1440),"#f8f9f5")
    d = ImageDraw.Draw(canvas)
    fonts = [os.getenv("ATLAS_CJK_FONT", "C:/Windows/Fonts/msyh.ttc"),
             os.getenv("ATLAS_CJK_BOLD", "C:/Windows/Fonts/msyhbd.ttc")]
    def label(x,y,text,size=32,bold=False,color="#163b37"):
        d.text((x,y),text,font=ImageFont.truetype(fonts[int(bold)],size),fill=color)
    label(64,60,"宇多 Yul 细胞  /  文献观察",27)
    label(60,137,"撤稿还是 4 篇，",76,True)
    label(60,235,"为什么比例变小了？",76,True)
    label(64,365,"PDRN、PN 填充与 Skin Booster 合并检索",34)
    label(64,424,"每 1,000 篇匹配记录中的撤稿篇数",29)
    r = rates["skin-pdrn-polynucleotide"]
    for y, date, num, den in [(523,"10 月 30 日",r["old_retracted"],r["old_denominator"]),
                                (790,"11 月 22 日",r["retracted"],r["denominator"])]:
        v = 1000*num/den
        label(65,y,date,34,True)
        label(406,y,f"{num} 篇 / {den} 篇",34)
        label(756,y-7,f"{v:.2f}‰",43,True)
        d.rectangle((66,y+84,1005,y+126),fill="#dbe7e2")
        d.rectangle((66,y+84,66+int(939*v/25),y+126),fill="#28766a")
        label(65,y+141,"0",24)
        label(923,y+141,"25‰",24)
    d.line((66,1050,1007,1050),fill="#a7b9b1",width=2)
    label(64,1095,"多收录了 11 篇，撤稿原文仍是同样的 4 篇。",34,True)
    label(64,1173,"含注射、填充及综述。不能单算作外用护肤品的撤稿率，",29)
    label(64,1227,"也不能用来估计产品风险。",29)
    label(64,1335,"PubMed · 2006-01-01 起 · 检索截止 2026-11-22",25)
    assert (r["old_retracted"],r["retracted"],r["old_denominator"],r["denominator"]) == (4,4,175,186)
    PNG.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(PNG,optimize=True)


if __name__=="__main__":
    run()
