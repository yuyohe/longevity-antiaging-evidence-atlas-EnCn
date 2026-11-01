"""Bounded November metadata maintenance. No publishing or automatic grading."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'maintenance_2026_11'
PRIVATE = ROOT / 'build' / 'private-content' / 'maintenance-2026-11-01'
DATE = '2026-11-01'

def request(url, xml=False):
    last=None
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'YulCell-EvidenceAtlas-Maintenance/2026-11 (public metadata only)'})
            raw=urllib.request.urlopen(req,timeout=35).read()
            return ET.fromstring(raw) if xml else json.loads(raw)
        except Exception as exc:
            last=exc
            time.sleep(1+attempt)
    raise RuntimeError(f'Public source request failed: {type(last).__name__}')

def search(query, retmax):
    url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'+urllib.parse.urlencode({'db':'pubmed','term':query,'retmode':'json','retmax':retmax,'sort':'pub date'})
    out=request(url)['esearchresult']
    return int(out['count']),out['idlist'],url

def text(node):
    return ''.join(node.itertext()).strip() if node is not None else ''

def fetch(ids):
    records=[]
    for start in range(0,len(ids),80):
        url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'+urllib.parse.urlencode({'db':'pubmed','id':','.join(ids[start:start+80]),'retmode':'xml'})
        tree=request(url,xml=True)
        for item in tree.findall('PubmedArticle'):
            article=item.find('MedlineCitation/Article')
            pmid=item.findtext('MedlineCitation/PMID')
            idmap={v.get('IdType'):v.text for v in item.findall('PubmedData/ArticleIdList/ArticleId')}
            types=[text(v) for v in article.findall('PublicationTypeList/PublicationType')]
            dates=[{v.tag:text(v) for v in d} for d in article.findall('ArticleDate')]
            year=article.findtext('Journal/JournalIssue/PubDate/Year') or article.findtext('Journal/JournalIssue/PubDate/MedlineDate','')[:4]
            records.append({'pmid':pmid,'doi':idmap.get('doi',''),'pmcid':idmap.get('pmc',''),'title_en':text(article.find('ArticleTitle')),'year':year,'journal':article.findtext('Journal/Title'),'publication_types':types,'publication_dates':dates,'url':f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/','abstract':[{ 'label':v.get('Label',''),'text':text(v)} for v in article.findall('Abstract/AbstractText')],'coi_statement':item.findtext('MedlineCitation/CoiStatement',''),'notices':[{'type':v.get('RefType'),'pmid':v.findtext('PMID'),'citation':v.findtext('RefSource')} for v in item.findall('MedlineCitation/CommentsCorrectionsList/CommentsCorrections')],'last_checked':DATE,'full_text_availability':'pmc_available_not_reviewed' if idmap.get('pmc') else 'not_confirmed','review_status':'metadata_and_abstract_checked_not_formal_appraisal'})
        time.sleep(.4)
    return records

def collect():
    DATA.mkdir(parents=True,exist_ok=True)
    PRIVATE.mkdir(parents=True,exist_ok=True)
    plan=json.loads((DATA/'card_plan.json').read_text(encoding='utf-8'))
    logpath=DATA/'search_log.json'
    log=json.loads(logpath.read_text(encoding='utf-8')) if logpath.exists() else []
    done={r['query_id'] for r in log if not r.get('error')}
    for card in plan['cards']:
        qid=card['id']+'-recent'
        if qid in done: continue
        query=f"({card['query']}) AND (\"2026/06/30\"[Date - Publication] : \"2026/11/01\"[Date - Publication])"
        try:
            count,ids,url=search(query,plan['retmax_per_query'])
            row={'query_id':qid,'card_id':card['id'],'query':query,'retrieved_at':DATE,'source':'PubMed','query_type':'recent_published','window':['2026-06-30','2026-11-01'],'retmax':plan['retmax_per_query'],'sort':'pub date','match_count':count,'retrieved_pmids':ids,'endpoint':url,'error':''}
        except Exception as exc:
            row={'query_id':qid,'card_id':card['id'],'query':query,'retrieved_at':DATE,'error':str(exc),'retrieved_pmids':[],'match_count':None}
        log.append(row)
        logpath.write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
        print(qid,row['match_count'],len(row['retrieved_pmids']),flush=True)
        time.sleep(.4)
    ids=sorted(set([v for r in log for v in r.get('retrieved_pmids',[])]+[v for c in plan['cards'] for v in c['anchors']]))
    cache=PRIVATE/'pubmed_records_with_abstracts.json'
    existing=json.loads(cache.read_text(encoding='utf-8')) if cache.exists() else []
    by_id={r['pmid']:r for r in existing}
    missing=[v for v in ids if v not in by_id]
    by_id.update({r['pmid']:r for r in fetch(missing)})
    records=[by_id[v] for v in ids if v in by_id]
    (PRIVATE/'pubmed_records_with_abstracts.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    public=[{k:v for k,v in r.items() if k not in ('abstract','coi_statement')} for r in records]
    (DATA/'source_metadata.json').write_text(json.dumps(public,ensure_ascii=False,indent=2),encoding='utf-8')
    print('unique source metadata',len(records),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['collect'])
    args=parser.parse_args()
    collect()
