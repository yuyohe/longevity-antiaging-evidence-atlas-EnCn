"""Build the explicit November public release; never runs a publisher."""
from __future__ import annotations
import base64
import csv
import hashlib
import html
import io
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/maintenance_2026_11'
PRIVATE=ROOT/'build/private-content/maintenance-2026-11-01'
STAGE=PRIVATE/'public-staging'
ASSETS=ROOT/'docs/assets/ingredients-2026-11'
CARDS=ROOT/'content/cards/ingredients-2026-11'
DATE='2026-11-01'
REPO='https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn'
PUBLIC=[]
E=html.escape

def write(path,content):
    path=ROOT/path if isinstance(path,str) else path
    path.parent.mkdir(parents=True,exist_ok=True)
    if isinstance(content,bytes): path.write_bytes(content)
    else: path.write_text(content,encoding='utf-8')
    rel=path.relative_to(ROOT).as_posix()
    if not rel.startswith('build/'): PUBLIC.append(rel)

def csv_bytes(rows,fields):
    stream=io.StringIO(newline='')
    w=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(rows)
    return ('\ufeff'+stream.getvalue()).encode('utf-8')

def load_rows(raw):
    reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    return list(reader),reader.fieldnames

def backup(rel):
    src=ROOT/rel; dst=PRIVATE/'backup'/rel
    if src.exists() and not dst.exists():
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)

def sources_links(c):
    return [(f'PMID {i}',f'https://pubmed.ncbi.nlm.nih.gov/{i}/') for i in c['sources']]+[(f'DOI {i}',f'https://doi.org/{i}') for i in c.get('doi_sources',[])]

def corrections(raw,rel,log):
    rows,fields=load_rows(raw)
    for row in rows:
        key=row.get('pmid') or row.get('supplement_id') or row.get('id')
        updates={}
        if rel=='data/skin_beauty_findings.csv' and key=='16029679': updates={'intervention_type':'topical'}
        if rel=='data/evidence_findings.csv' and key=='33888596':
            updates={'pmcid':'PMC8550608','topic_id':'nad-nmn-nr-aging','topic_zh':'NAD/NMN/NR','topic_en':'NAD/NMN/NR','intervention_or_exposure_draft':'oral nicotinamide mononucleotide (NMN)'}
        if rel in ('data/candidate_sources.csv','data/literature_library.csv') and key=='33888596': updates={'pmcid':'PMC8550608'}
        if rel=='data/supplement_matrix.csv' and key in ('collagen-peptides','collagen-type-ii'):
            old=row.get('scoring_note_en','')
            level=row.get('final_evidence_level')
            if level: updates={'scoring_note_en':re.sub(r'final level [A-F]\.',f'final level {level}.',old)}
        for field,value in updates.items():
            if field in fields and row.get(field)!=value:
                log.append({'file':rel,'key':key,'field':field,'old':row.get(field,''),'new':value,'reason':'confirmed identity/route or bilingual legacy-field consistency; no automatic grade promotion','source':'PMID 16029679 / 33888596; editorial-v1 scope audit','date':DATE})
                row[field]=value
    return csv_bytes(rows,fields)

def candidate_merge(raw,metadata,rel):
    rows,fields=load_rows(raw)
    idfield='library_id' if rel.endswith('literature_library.csv') else 'id'
    seen={r.get(idfield) for r in rows}
    for r in metadata:
        sid='pubmed-'+r['pmid'] if r.get('pmid') else 'crossref-nmn-24week-2026'
        if sid in seen: continue
        row={k:'' for k in fields}
        row.update({idfield:sid,'title_en':r['title_en'],'year':r['year'],'pmid':r.get('pmid',''),'pmcid':r.get('pmcid',''),'doi':r['doi'],'url':r['url'],'source':'PubMed' if r.get('pmid') else 'Crossref','query':'bounded_ingredient_maintenance_2026_11','include_status':'retracted_excluded' if 'Retracted Publication' in r.get('publication_types',[]) else 'candidate_metadata_pending_full_appraisal','last_checked':DATE})
        rows.append(row);seen.add(sid)
    return csv_bytes(rows,fields)

def ledger_merge(raw,metadata,used):
    entries=json.loads(raw.decode('utf-8'))
    by_pmid={str(r.get('pmid')):r for r in entries if r.get('pmid')}
    by_id={r.get('id'):r for r in entries}
    for r in metadata:
        pmid=r.get('pmid',''); sid='pubmed-'+pmid if pmid else 'crossref-nmn-24week-2026'
        if sid in by_id or pmid and pmid in by_pmid:
            if pmid=='33888596':
                item=by_id.get(sid) or by_pmid[pmid]
                item.update({'pmcid':'PMC8550608','doi':'10.1126/science.abe9985','identity_checked':DATE})
            continue
        types=r.get('publication_types',[])
        entries.append({'id':sid,'title_en':r['title_en'],'title_zh':'中文解释见本版成分卡；题名暂保留原文','year':r['year'],'journal':r.get('journal',''),'doi':r['doi'],'pmid':pmid,'pmcid':r.get('pmcid',''),'url':r['url'],'source_type':'metadata_record','study_type':'systematic_review_or_meta_analysis' if any(t in types for t in ('Systematic Review','Meta-Analysis')) else 'human_randomized_trial' if 'Randomized Controlled Trial' in types else 'needs_classification','species':'human' if pmid in used else 'needs_classification','endpoint_class':'','evidence_level':'','included':False,'last_checked':DATE,'exclusion_reason':'not_promoted_to_legacy_matrix; used only in scoped editorial cards or candidate queue','risk_of_bias':'not_formally_assessed','full_text_availability':r.get('full_text_availability','not_confirmed')})
    return json.dumps(entries,ensure_ascii=False,indent=2)+'\n'

def wrap(draw,text,font,width):
    lines=[];line=''
    for char in text:
        if char=='\n': lines.append(line);line='';continue
        if line and draw.textlength(line+char,font=font)>width:
            lines.append(line);line=char
        else: line+=char
    if line: lines.append(line)
    return lines

def card_png(card):
    from PIL import Image,ImageDraw,ImageFont
    im=Image.new('RGB',(1080,1440),'#ffffff');d=ImageDraw.Draw(im)
    font=lambda n,b=False:ImageFont.truetype('C:/Windows/Fonts/'+('msyhbd.ttc' if b else 'msyh.ttc'),n)
    accent='#126858' if card['route']=='topical' else '#385d91'
    d.rectangle((0,0,1080,16),fill=accent)
    d.text((70,58),'宇多Yul细胞 / yulcell',font=font(25),fill='#596669')
    d.text((70,117),'外用' if card['route']=='topical' else '口服',font=font(29,True),fill=accent)
    d.text((70,168),card['name'],font=font(48,True),fill='#202b2c')
    d.text((70,238),card['en'],font=font(25),fill='#5b6669')
    y=300
    for label,text in [('结论',card['conclusion']),('适合谁',card['recommendation']),('预期效果',card['expected_effect']),('证据等级',card['grade']+'（'+card['grade_reason']+'）'),('副作用与注意',card['risks'])]:
        d.text((70,y),label,font=font(27,True),fill=accent);y+=44
        for line in wrap(d,text,font(30),940):
            d.text((70,y),line,font=font(30),fill='#202b2c');y+=43
        y+=19
    assert y<1305,(card['id'],y,'card overflow')
    d.line((70,1310,1010,1310),fill='#d6dedc',width=2)
    d.text((70,1330),'资料截止 2026-11-01 · 编辑分档 v1 · '+card['id'],font=font(21),fill='#5b6669')
    sources='PMID '+', '.join(card['sources'])
    if card.get('doi_sources'): sources+='；另见来源页DOI'
    for j,line in enumerate(wrap(d,sources,font(19),940)[:2]): d.text((70,1368+j*24),line,font=font(19),fill='#5b6669')
    stream=io.BytesIO();im.save(stream,format='PNG',optimize=True)
    target=ASSETS/(card['id']+'.png');write(target,stream.getvalue())
    return target

def make_heatmap(plan,logs):
    os.environ['MPLCONFIGDIR']=str(PRIVATE/'matplotlib-cache')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import FontProperties
    fp=FontProperties(fname='C:/Windows/Fonts/msyh.ttc')
    vals=[]
    for c in plan['cards']:
        log=next(r for r in logs if r['card_id']==c['id'] and r['query_id'].endswith('-recent'))
        vals.append([log['match_count'] or 0,len(log['retrieved_pmids']),0])
    fig,ax=plt.subplots(figsize=(7,11),dpi=120)
    ax.imshow(vals,cmap='GnBu',aspect='auto',vmin=0,vmax=max(max(x) for x in vals))
    ax.set_yticks(range(20),[('外用 ' if c['route']=='topical' else '口服 ')+c['name'] for c in plan['cards']],fontproperties=fp,fontsize=9)
    ax.set_xticks(range(3),['检索命中','实际抽取','完成正式复核'],fontproperties=fp,fontsize=10)
    for y,row in enumerate(vals):
        for x,v in enumerate(row): ax.text(x,y,str(v),ha='center',va='center',fontsize=10,color='white' if v>9 else '#25343b')
    ax.set_title('11月初检索记录图',fontproperties=fp,pad=22,fontsize=17)
    fig.text(.05,.015,'2026-06-30至11-01；每方向最多抽取4条。颜色表示数量，不代表疗效。',fontproperties=fp,fontsize=9)
    fig.tight_layout(rect=(0,.03,1,1))
    stream=io.BytesIO();fig.savefig(stream,format='png',bbox_inches='tight');plt.close(fig)
    write(ASSETS/'november-search-map.png',stream.getvalue())
    return stream.getvalue()

def lead_png(cards):
    from PIL import Image,ImageDraw,ImageFont
    im=Image.new('RGB',(1200,1600),'white');d=ImageDraw.Draw(im)
    font=lambda n,b=False:ImageFont.truetype('C:/Windows/Fonts/'+('msyhbd.ttc' if b else 'msyh.ttc'),n)
    d.rectangle((0,0,1200,18),fill='#176d5c')
    d.text((70,70),'宇多Yul细胞 / yulcell',font=font(30),fill='#536266')
    d.text((70,140),'抗衰成分推荐',font=font(64,True),fill='#253135')
    d.text((70,235),'按当前研究证据强度分级',font=font(36),fill='#176d5c')
    y=315
    for line in ['等级表示对具体结论的把握。','高等级也可能对应未见获益；请同时看推荐条件。']:
        d.text((70,y),line,font=font(27),fill='#536266');y+=44
    for x,route,label in [(70,'topical','外用10项'),(645,'oral','口服10项')]:
        d.text((x,440),label,font=font(37,True),fill='#176d5c' if route=='topical' else '#385d91')
        for j,c in enumerate(c for c in cards if c['route']==route):
            y=525+j*88
            name=c['name'].replace('Omega-3／普通鱼油','普通鱼油 / Omega-3')
            d.text((x,y),name,font=font(29,True),fill='#253135')
            d.text((x,y+43),c['grade']+' · '+c['endpoint'],font=font(23),fill='#677374')
    d.line((70,1450,1130,1450),fill='#d1dcda',width=2)
    d.text((70,1480),'点开单卡查看结论、适用建议、预期效果和真实风险。',font=font(27),fill='#253135')
    d.text((70,1535),'资料截止 2026-11-01 · editorial-v1 · 本版未赋A',font=font(23),fill='#677374')
    stream=io.BytesIO();im.save(stream,format='PNG',optimize=True)
    write(ASSETS/'00-ingredient-guide.png',stream.getvalue())

def card_html(c):
    refs=' · '.join(f'<a href="{E(u)}">{E(t)}</a>' for t,u in sources_links(c))
    safety=' · '.join(f'<a href="{E(u)}">安全资料</a>' for u in c['safety_sources'])
    return f'''<article class="card" id="{c['id']}"><p class="route">{'外用' if c['route']=='topical' else '口服'} · {E(c['endpoint'])}</p><h3>{E(c['name'])}</h3><p class="english">{E(c['en'])}</p><p class="conclusion">{E(c['conclusion'])}</p><dl><dt>适合谁</dt><dd>{E(c['recommendation'])}</dd><dt>预期效果</dt><dd>{E(c['expected_effect'])}</dd><dt>证据等级</dt><dd class="grade">{c['grade']}（{E(c['grade_reason'])}）</dd><dt>副作用与注意</dt><dd>{E(c['risks'])}</dd></dl><p class="sources">{refs}{' · '+safety if safety else ''}<br>资料截止 2026-11-01</p></article>'''

def render_html(title,body):
    css='''*{box-sizing:border-box}body{margin:0;color:#243033;background:white;font:16px/1.8 "Microsoft YaHei",Arial,sans-serif;letter-spacing:0}header,main,footer,nav{max-width:1160px;margin:auto;padding:25px 28px}header{padding-top:38px}h1{font-size:30px;line-height:1.4;margin:8px 0 18px}h2{font-size:24px;margin:30px 0 15px}h3{font-size:23px;margin:6px 0}p{margin:8px 0 12px}a{color:#08645e;overflow-wrap:anywhere}nav{display:flex;flex-wrap:wrap;gap:20px;border-top:1px solid #d6dfdc;border-bottom:1px solid #d6dfdc;padding-top:12px;padding-bottom:12px}.cards{display:grid;grid-template-columns:1fr 1fr;gap:20px}.card{border:1px solid #d6dfdc;border-top:4px solid #42776c;border-radius:5px;padding:22px;min-width:0}.route,.english,.sources,.small{font-size:13px;color:#566667}.route{color:#287367}.conclusion{font-size:18px}.grade{color:#725526}dt{font-weight:700;font-size:13px;margin-top:12px}dd{margin:0;font-size:15px}.sources{border-top:1px solid #e0e7e4;padding-top:12px}.table-wrap{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid #d6dfdc;padding:10px;text-align:left;vertical-align:top}th{background:#edf4f0}code{font:12px Consolas,monospace;overflow-wrap:anywhere}.figure{max-width:720px;width:100%;height:auto;display:block;margin:20px auto}.notice{border-left:3px solid #44679b;background:#f3f6fa;padding:15px}footer{font-size:13px;color:#566667}@media(max-width:760px){header,main,nav,footer{padding-left:16px;padding-right:16px}h1{font-size:26px}.cards{grid-template-columns:1fr}.table-wrap table{min-width:640px}}'''
    return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)}</title><style>{css}</style></head><body>{body}</body></html>'

def main():
    bundle=json.loads((DATA/'ingredient_cards.json').read_text(encoding='utf-8'))
    cards=bundle['cards']; assert len(cards)==20 and sum(c['route']=='oral' for c in cards)==10
    plan=json.loads((DATA/'card_plan.json').read_text(encoding='utf-8'))
    logs=json.loads((DATA/'search_log.json').read_text(encoding='utf-8'))
    metadata=json.loads((DATA/'source_metadata.json').read_text(encoding='utf-8'))
    by_id={r['pmid']:r for r in metadata}
    used={v for c in cards for v in c['sources']}
    assert used<=by_id.keys(),used-by_id.keys()
    assert not any('Retracted Publication' in by_id[i]['publication_types'] for i in used)
    nmndoi={'pmid':'','doi':'10.1038/s41514-026-00482-7','pmcid':'','title_en':'Sustained NAD+ augmentation by high-dose nicotinamide mononucleotide supplementation in older adults: a 24-week randomized, double-blind, placebo-controlled trial','year':'2026','journal':'npj Aging','publication_types':['Randomized Controlled Trial'],'publication_dates':[{'Year':'2026','Month':'09','Day':'25'}],'url':'https://doi.org/10.1038/s41514-026-00482-7','last_checked':DATE,'full_text_availability':'publisher_page_not_accessible; publisher_deposited_crossref_abstract_checked','review_status':'abstract_checked_not_formal_appraisal','notices':[]}
    metadata=[r for r in metadata if r.get('doi')!=nmndoi['doi']]+[nmndoi]
    write(DATA/'source_metadata.json',json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
    screening=[]
    recent={p for log in logs if log['query_id'].endswith('-recent') for p in log['retrieved_pmids']}
    delta=[log for log in logs if log['query_id'].endswith('-delta')]
    delta_ids={p for log in delta for p in log['retrieved_pmids']}
    existing={r['pmid'] for r in csv.DictReader((PRIVATE/'backup/data/candidate_sources.csv').open(encoding='utf-8-sig')) if r.get('pmid')}
    for r in metadata:
        retracted='Retracted Publication' in r.get('publication_types',[])
        status='retracted_excluded' if retracted else 'used_for_editorial_card_not_formal_grade' if r.get('pmid') in used or not r.get('pmid') else 'candidate_relevance_review_deferred'
        screening.append({'source_id':'pubmed-'+r['pmid'] if r.get('pmid') else 'crossref-nmn-24week-2026','pmid':r.get('pmid',''),'doi':r['doi'],'title_en':r['title_en'],'publication_year':r['year'],'checked_at':DATE,'in_recent_sample':r.get('pmid') in recent,'in_previous_local_candidates':r.get('pmid') in existing,'decision':status,'source_type':';'.join(r.get('publication_types',[])),'source_depth':r['full_text_availability'],'reason':'exact matching identity; retraction flags excluded; nonselected hits retained as candidates, not automatically graded'})
    write(DATA/'source_screening.csv',csv_bytes(screening,list(screening[0])))
    claimrows=[]
    for c in cards:
        row={k:c[k] for k in ('id','name','en','route','formulation','population','endpoint','grade','grade_reason','conclusion','recommendation','expected_effect','risks','review_note')}
        row.update({'grade_scheme':bundle['grading_version'],'full_appraisal':'not_completed','sources':';'.join(u for _,u in sources_links(c)),'cutoff':DATE})
        claimrows.append(row)
    write(DATA/'claim_matrix.csv',csv_bytes(claimrows,list(claimrows[0])))
    candidates=[]
    for r in metadata:
        candidates.append({'id':'pubmed-'+r['pmid'] if r.get('pmid') else 'crossref-nmn-24week-2026','title_en':r['title_en'],'title_zh':'','year':r['year'],'doi':r['doi'],'pmid':r.get('pmid',''),'pmcid':r.get('pmcid',''),'url':r['url'],'source':'PubMed' if r.get('pmid') else 'Crossref','query':'bounded_ingredient_maintenance_2026_11','include_status':'retracted_excluded' if 'Retracted Publication' in r.get('publication_types',[]) else 'needs_full_appraisal','notes':'Scoped metadata refresh; not formal RoB/GRADE','last_checked':DATE})
    write(DATA/'candidate_sources_increment.csv',csv_bytes(candidates,list(candidates[0])))
    for c in cards:
        image=card_png(c)
        refs='\n'.join(f'- [{t}]({u})' for t,u in sources_links(c))
        md=f"# {c['name']} / {c['en']}\n\n途径：{'外用' if c['route']=='topical' else '口服'}；用途：{c['endpoint']}；资料截止：{DATE}。\n\n![{c['name']}资料卡](../../../docs/assets/ingredients-2026-11/{c['id']}.png)\n\n## 结论\n{c['conclusion']}\n\n## 适合谁\n{c['recommendation']}\n\n## 预期效果\n{c['expected_effect']}\n\n## 证据等级\n{c['grade']}（{c['grade_reason']}）\n\n分档版本：ingredient-cards-editorial-v1；[规则](../../../methodology/ingredient-card-grading-v1.md)。\n\n## 副作用与注意\n{c['risks']}\n\n## 研究范围\n{c['formulation']}。人群：{c['population']}。{c['review_note']}\n\n## 来源\n{refs}\n"+''.join(f'\n- [安全资料]({u})' for u in c['safety_sources'])+'\n'
        write(CARDS/(c['id']+'.md'),md)
    heatmap=make_heatmap(plan,logs)
    lead_png(cards)
    overview_lines=['# 抗衰成分推荐｜按当前研究证据强度分级','',bundle['subtitle'],'','资料截止：2026-11-01；本次证据等级为 editorial-v1 编辑性概括。它与旧库自动 A–F 分档分开，未完成正式 GRADE，不将研究数量直接当作用强弱。','', '[证据等级规则](../../../methodology/ingredient-card-grading-v1.md) · [11月维护记录](../../../docs/november-maintenance-2026-11.md)','']
    for route,label in [('topical','外用10项'),('oral','口服10项')]:
        overview_lines+=['## '+label,'','| 成分 | 用途 | 证据等级 | 结论 |','| --- | --- | --- | --- |']
        overview_lines += [f"| [{c['name']}]({c['id']}.md) | {c['endpoint']} | {c['grade']}（{c['grade_reason']}） | {c['conclusion']} |" for c in cards if c['route']==route]
        overview_lines+=['']
    overview_lines+=['## 研究记录图','','![本轮有界检索记录](../../../docs/assets/ingredients-2026-11/november-search-map.png)','','每方向最多抽取4条最新记录；全部命中数和抽取数量分别保留。颜色表示检索与审核数量，不是成分效果排名。','']
    write(CARDS/'index.md','\n'.join(overview_lines))
    intro=f'<header><p class="small">宇多Yul细胞 / yulcell · 2026-11-01</p><h1>{E(bundle["title"])}</h1><p>{E(bundle["subtitle"])}</p><p>证据等级表示对本卡结论的把握，不代表效果大小或推荐顺序；高等级也可能对应未见获益。</p><p class="small">编辑分档 editorial-v1：A＝多项直接人体研究且关键效应、偏倚和一致性已完整核验（本版未赋A）；B＝有明确人体对照依据，适用范围或复核仍有限；C＝小样本、短期、组合配方或结果分歧；D＝缺足够直接人体证据。未完成正式GRADE，旧库等级另存。</p></header><nav><a href="#topical">外用10项</a><a href="#oral">口服10项</a><a href="#matrix">用途矩阵</a><a href="#research">研究记录</a><a href="{REPO}/blob/main/methodology/ingredient-card-grading-v1.md">评级方法</a></nav><main>'
    public_body=intro
    for route,label in [('topical','外用10项'),('oral','口服10项')]:
        public_body+=f'<h2 id="{route}">{label}</h2><div class="cards">'+''.join(card_html(c) for c in cards if c['route']==route)+'</div>'
    public_body+='<h2 id="matrix">先选用途，再看成分</h2><div class="table-wrap"><table><thead><tr><th>途径</th><th>成分</th><th>用途</th><th>证据等级</th></tr></thead><tbody>'+''.join(f'<tr><td>{"外用" if c["route"]=="topical" else "口服"}</td><td><a href="#{c["id"]}">{E(c["name"])}</a></td><td>{E(c["endpoint"])}</td><td>{c["grade"]}（{E(c["grade_reason"])}）</td></tr>' for c in cards)+'</tbody></table></div>'
    public_body+=f'<h2 id="research">11月初文献维护</h2><p>最新远端检索水位为2026-10-30。本次另查10月31日至11月1日的20个方向，去重命中{len(delta_ids)}个PMID；同时对6月30日以来做20个方向的有界回补核查，每方向最多抽取4条。回补与真正新增分别记录，另补核经典试验与关键遗漏。新来源停留在候选或编辑性解释层，没有批量升级旧库证据。</p><img class="figure" src="data:image/png;base64,{base64.b64encode(heatmap).decode()}" alt="20个方向的本轮命中、抽取和正式复核数量图"><p class="small">图为6月30日以来的回补样本：第一列是检索命中，第二列为有界抽取，第三列为本轮正式方法学复核数。0表示未完成正式复核，不表示零效果。</p></main><footer>资料截止2026-11-01。研究与风险资料供一般人了解；个人用药和疾病治疗由合格专业人员评估。</footer>'
    write('docs/ingredient-guide-2026-11.html',render_html(bundle['title'],public_body))
    write('docs/research-heatmap-2026-11.html',render_html(bundle['title'],public_body))
    catchup=[r for r in logs if r['query_id'].endswith('-recent')]
    remote_candidates=csv.DictReader(io.StringIO(subprocess.check_output(['git','show','origin/main:data/candidate_sources.csv'],cwd=ROOT).decode('utf-8-sig')))
    remote_pmids={r['pmid'] for r in remote_candidates if r.get('pmid')}
    counts={'queries':len(logs),'catchup_queries':len(catchup),'delta_queries':len(delta),'remote_previous_search_watermark':'2026-10-30','local_previous_search_watermark':'2026-06-29','query_match_sum_not_unique':sum(r['match_count'] or 0 for r in catchup),'sample_rows_sum':sum(len(r['retrieved_pmids']) for r in catchup),'unique_recent_sample':len(recent),'incremental_window':['2026-10-31','2026-11-01'],'incremental_match_sum':sum(r['match_count'] or 0 for r in delta),'incremental_unique_pmids':len(delta_ids),'incremental_new_vs_remote_pmids':len(delta_ids-remote_pmids),'source_metadata_records':len(metadata),'new_pmids_vs_remote_candidates':sum(bool(r.get('pmid')) and r['pmid'] not in remote_pmids for r in metadata),'new_pmids_vs_local':sum(bool(r.get('pmid')) and r['pmid'] not in existing for r in metadata),'formal_appraisals_completed':0,'cutoff':DATE}
    write(DATA/'maintenance_summary.json',json.dumps(counts,ensure_ascii=False,indent=2)+'\n')
    notes=f'''# 2026年11月初文献维护\n\n资料截止：{DATE}。\n\n- 主窗口：2026-06-30至2026-11-01（发表日期）；20个方向，每方向最多取最新4条。\n- 全部查询命中数相加为{counts['query_match_sum_not_unique']}，包含跨查询重复；实际抽取{counts['sample_rows_sum']}条命中、去重后{len(recent)}个PMID。不能把命中总数当新增独立论文数。\n- 本次来源元数据共{len(metadata)}条，含经典文献补核、纠正/撤稿核查及1条Crossref DOI来源。记录的“可获取全文”不等于“完成全文方法学复核”。\n- 正式RoB/GRADE完成数：0。20卡使用独立的editorial-v1编辑性证据等级，不改旧库A–F全库等级。\n\n## 本次改变读法的文献\n\n- PDRN（PMID42430369）：已有31人、28天的直接外用对照试验；缺空白基质臂、长期结果及独立重复，保留C。\n- NR（PMID42848371、42478598）：NAD上升与临床效果分开。NOPARK疾病人群未获益、部分终点更差；MCI试验也未改善主要认知终点。\n- NMN（DOI10.1038/s41514-026-00482-7）：出版社提交的Crossref摘要报告NAD代谢物升高，24周听力主要终点和身体功能未显著改善；原刊页面本轮不可完整访问，未冒称全文复核。\n- 肌酸（PMID42712402）：支持小幅肌力获益，肌肉量和身体功能仍不确定。探索性认知与血液指标不提升评级。\n- 神经酰胺（PMID42868105）：关键指标未见显著组间差异；不能把两组各自改善当成优效。\n- 维D（PMID42704968）：维D充足老年人未见骨折预防获益。\n- 镁（PMID42661485）：结果不一致，不支持把镁当常规失眠治疗。\n- 胶原（PMID40324552、42342959）：新综述的总体阳性与质量/资助亚组分歧同时保留，未自动提高等级。\n\n## 完整性与重复\n\n精确来源核对发现蛋白综述PMID28698222有关联纠正PMID32943392，纠正正文本轮未完整访问；本版不复用精确效果数值。旧镁综述的纠正PMID39702257涉及文本、检索计数与数据库名称，正文已核；并以2026综述作为更新依据。历史4条PN/skin booster相关撤稿记录仍有PubMed撤稿标记，涉及填充/注射及宽泛综述，不属于2026年新外用试验的同一支持集。旧4/149密度仍是2026-05-14快照，不能称11月最新PDRN外用撤稿率。\n\n同一注册号的论文/随访归同一母研究。VITAL鱼油与骨折研究不加总人数，NR/NMN注册记录不当额外试验，综述与其原始试验不重复加总。本版不计算未经完整关联核验的独立临床研究总量。\n\n## 可复核文件\n\n- `data/maintenance_2026_11/search_log.json`：检索式、命中量、抽取列表、窗口与截断。\n- `source_screening.csv`、`candidate_sources_increment.csv`：取回来源的候选/使用/撤稿排除状态。\n- `source_metadata.json`：题名、DOI/PMID、出版日期、核对日期、全文可得性和通知。\n- `trial_registry_checks.json`、`crossref_checks.json`：4个原注册号和3个重点DOI的核对。\n- `claim_matrix.csv`、`ingredient_cards.json`：本版20项，途径/人群/终点/制剂及评级规则分开。\n- `record_corrections.csv`：本次已确认修正的旧值、新值和依据。\n\n旧“证据含金量”使用健康/皮肤两个主题栏的A/B个数，不能称优质研究比例。新入口停用这种临床强度解释；历史图表保留并加历史代理标签。\n\n[打开20卡入口](../content/cards/ingredients-2026-11/index.md) · [评级规则](../methodology/ingredient-card-grading-v1.md)\n'''
    write('docs/november-maintenance-2026-11.md',notes)
    add=f'\n\n## 远端检索水位与真正增量\n\n发布基线origin/main的检索水位为2026-10-30；本地旧副本为2026-06-29。故另做2026-10-31至11-01的20个方向增量查询，命中去重{len(delta_ids)}个PMID，其中{len(delta_ids-remote_pmids)}个未见于远端候选表。六月以来的49个抽样PMID属于有界回补核查，不把它们全部称作11月新增。40个查询分为20个回补、20个真正增量；同一论文跨窗口只计一次。\n'
    write('docs/november-maintenance-2026-11.md',notes+add)
    # Preserve the original checkpoint and user changes; edit only confirmed fields locally.
    old_changes=DATA/'record_corrections.csv'
    change_log=list(csv.DictReader(old_changes.open(encoding='utf-8-sig'))) if old_changes.exists() else []
    changed_rels=['data/skin_beauty_findings.csv','data/evidence_findings.csv','data/supplement_matrix.csv','data/candidate_sources.csv','data/literature_library.csv']
    for rel in changed_rels:
        backup(rel); raw=(ROOT/rel).read_bytes(); updated=corrections(raw,rel,change_log)
        if rel in ('data/candidate_sources.csv','data/literature_library.csv'): updated=candidate_merge(updated,metadata,rel)
        write(rel,updated)
    backup('data/sources.json')
    write('data/sources.json',ledger_merge((ROOT/'data/sources.json').read_bytes(),metadata,used))
    write(DATA/'record_corrections.csv',csv_bytes(change_log,['file','key','field','old','new','reason','source','date']))
    # A scoped research page for each used article; no abstracts or copyrighted full text.
    for pmid in sorted(used):
        r=by_id[pmid]; related=[c for c in cards if pmid in c['sources']]
        types='; '.join(r['publication_types'])
        md=f"# {r['title_en']}\n\n中文一句话结论：{related[0]['conclusion']}\n\nEnglish one-sentence conclusion: This source informs the specific route and outcome described in the linked editorial card; formal appraisal remains pending.\n\n## Study design / 研究设计\n{types}。\n\n## Population / 样本和人群\n本版适用范围：{related[0]['population']}；原研究精确入组标准见来源，未重新抽取完整全文表。\n\n## Intervention / 干预与制剂\n{related[0]['formulation']}。研究条件不转为个人方案。\n\n## Comparator / 对照\n以原研究的安慰剂、基质或具体活性对照为准；本轮未重建全部试验臂。\n\n## Primary endpoint / 主要终点\n{related[0]['endpoint']}；主次终点及预设状态仍需正式复核。\n\n## Key results / 核心结果\n{related[0]['expected_effect']}\n\n## Appropriate interpretation / 适合怎么解读\n{related[0]['review_note']}\n\n## Overinterpretation / 不适合怎么解读\n不从本研究跨越给药途径、制剂、人群或终点外推。\n\n## Practical relevance / 对普通人的意义\n{related[0]['recommendation']}\n\n## Limitations / 局限性\n元数据与摘要复核；全文可得性：{r['full_text_availability']}。未完成逐结局RoB/GRADE。\n\n## Evidence grade / 证据等级\n具体claim的编辑性分档见[本版入口](../cards/ingredients-2026-11/index.md)；不赋单篇正式GRADE。\n\n## References / 参考文献\nPMID {pmid}；DOI {r['doi']}。{r['url']}\n\nPublication year: {r['year']}；metadata checked: {DATE}；species: human；legacy endpoint class: not assigned (new claim matrix retains actual endpoint)。\n"
        md=md.replace('../cards/ingredients-2026-11/index.md','../../cards/ingredients-2026-11/index.md')
        md+='\n\n草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。\nDraft status: automatically prepared; not fully reviewed; not medical advice.\n\nUnsupported Claim / Overinterpretation Risk: Do not infer unmeasured outcomes or transfer between routes.\nMedical supervision needed: See the linked condition-specific ingredient card.\n'
        write(f'content/papers/maintenance-2026-11/pubmed-{pmid}.md',md)
    # New source/claim topic entry without rebuilding unrelated topic pages.
    write('content/topics/maintenance-2026-11/ingredient-evidence.md','# 成分与具体用途的证据 / Ingredient-specific evidence\n\n[外用10项、口服10项](../../cards/ingredients-2026-11/index.md) · [11月维护](../../../docs/november-maintenance-2026-11.md)\n\n研究截止2026-11-01。版本editorial-v1；旧自动分档保留，不做字母直接换算。\n')
    for rel in ['README.md','README.zh-CN.md','content/public-reader/start-here.md','content/public-reader/index.md']:
        backup(rel); old=(ROOT/rel).read_text(encoding='utf-8')
        link='content/cards/ingredients-2026-11/index.md' if rel.startswith('README') else '../cards/ingredients-2026-11/index.md'
        notice=f'\n\n[抗衰成分推荐｜外用10项、口服10项（2026-11-01）]({link})\n\n'
        if 'ingredients-2026-11' not in old: old=old.split('\n',1)[0]+notice+old.split('\n',1)[1]
        write(rel,old)
    backup('CHANGELOG.md')
    old=(ROOT/'CHANGELOG.md').read_text(encoding='utf-8')
    changelog_entry='\n\n## 2026-11-01\n\n新增外用10项、口服10项成分资料卡；有界更新2026-06-30至11-01文献，补核关键试验、纠正与撤稿标记。采用独立editorial-v1分档，不批量升级旧库。修复确认的途径、主题和PMCID错误；公开检索/来源/变更账本。\n'
    if '## 2026-11-01' not in old: old=old.split('\n',1)[0]+changelog_entry+old.split('\n',1)[1]
    write('CHANGELOG.md',old)
    # Explicit staging. Existing public files use latest origin/main, not the dirty working copy.
    # Place the new guide before the existing October heatmap without changing its figures.
    heatmap_rel='docs/research-heatmap-2026-10.html'
    remote_heatmap=subprocess.check_output(['git','show','origin/main:'+heatmap_rel],cwd=ROOT).decode('utf-8')
    entry='<section><h2>抗衰成分推荐｜按当前研究证据强度分级</h2><p>外用10项、口服10项。证据等级表示具体结论的把握，高等级也可能对应未见获益。</p><p><a href="../content/cards/ingredients-2026-11/index.md">打开20张成分卡</a> · <a href="ingredient-guide-2026-11.html">图文阅读页</a> · <a href="../methodology/ingredient-card-grading-v1.md">本次A–D定义</a></p></section>'
    write(heatmap_rel,remote_heatmap.replace('<main>','<main>'+entry,1))
    new_paths=set(PUBLIC)|{p.relative_to(ROOT).as_posix() for p in DATA.glob('*') if p.is_file()}|{'scripts/maintain_november_2026.py','scripts/build_november_cards.py','methodology/ingredient-card-grading-v1.md'}
    existing_paths=set(changed_rels)|{'data/sources.json','README.md','README.zh-CN.md','CHANGELOG.md','content/public-reader/start-here.md','content/public-reader/index.md'}
    remote_log=[]
    for rel in sorted(new_paths):
        dst=STAGE/rel; dst.parent.mkdir(parents=True,exist_ok=True)
        if rel not in existing_paths:
            shutil.copyfile(ROOT/rel,dst);continue
        try: base=subprocess.check_output(['git','show','origin/main:'+rel],cwd=ROOT,stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError: continue
        if rel in changed_rels:
            result=corrections(base,rel,remote_log)
            if rel in ('data/candidate_sources.csv','data/literature_library.csv'): result=candidate_merge(result,metadata,rel)
        elif rel=='data/sources.json': result=ledger_merge(base,metadata,used).encode('utf-8')
        else:
            remote=base.decode('utf-8')
            if rel=='CHANGELOG.md': addition=changelog_entry
            else:
                link='content/cards/ingredients-2026-11/index.md' if rel.startswith('README') else '../cards/ingredients-2026-11/index.md'
                addition=f'\n\n[抗衰成分推荐｜外用10项、口服10项（2026-11-01）]({link})\n\n'
            result=(remote.split('\n',1)[0]+addition+remote.split('\n',1)[1]).encode('utf-8')
        dst.write_bytes(result)
    (PRIVATE/'remote_field_corrections.json').write_text(json.dumps(remote_log,ensure_ascii=False,indent=2),encoding='utf-8')
    files=[p for p in STAGE.rglob('*') if p.is_file()]
    manifest=[{'path':p.relative_to(STAGE).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
    assert all(not any(x in r['path'].lower() for x in ('private-content','.env','raw_pdf','raw_html','checkpoint')) for r in manifest)
    (PRIVATE/'public_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    report=public_body.replace('</main>',f'<h2>本轮维护回顾</h2><p>{len(cards)}张卡；主检索20个方向，去重抽取{len(recent)}个近期PMID，另有经典文献、纠正和DOI补核。正式方法学评级本轮未完成。发布状态见同目录release-receipt.json，不能由本地生成状态推断已上线。</p></main>')
    (PRIVATE/'11月初维护与20卡报告.html').write_text(render_html('11月初维护与20卡报告',report),encoding='utf-8')
    print(json.dumps({'cards':20,'recent_sample_unique':len(recent),'source_metadata':len(metadata),'public_files':len(manifest),'local_corrections':len(change_log),'remote_existing_field_corrections':len(remote_log),'private_report':str(PRIVATE/'11月初维护与20卡报告.html')},ensure_ascii=False))

if __name__=='__main__': main()
