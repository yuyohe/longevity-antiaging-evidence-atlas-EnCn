"""Explicit, idempotent November upserts into the original verified Feishu Base."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time
import requests
from dotenv import load_dotenv
from feishu_client import FeishuClient

ROOT=Path(__file__).resolve().parents[1]
PRIVATE=ROOT/'build/private-content/maintenance-2026-11-01'
STAGE=PRIVATE/'public-staging'
DATA=STAGE/'data/maintenance_2026_11'
VERSION='2026-11-01/editorial-v1'
WIKI='WriBw4TXZiOsjQkJWk8ctL1xnVg'
DOMAIN='https://ucngl3rlrux2.feishu.cn/wiki/'+WIKI
REPO='https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn'
TARGETS={'cards':('tbliLsUC2T8lXHla','02 成分卡片（50种）'),'heatmap':('tblASMHdK01yuvjL','01 研究热力图'),'home':('tbljh1Xmkn6RYWPD','00 从这里开始（项目介绍）'),'sources':('tblIPdcBJPH6UkAE','20 文献来源（目录）'),'candidates':('tblWoc9k5UIsKq4J','21 检索来源（原始）'),'findings':('tblgAIsjA1UR4jLr','11 研究笔记（待复核）')}

def api(client,method,path,**kwargs):
    resp=requests.request(method,client.base_url+'/open-apis/bitable/v1/'+path,headers=client._headers(),timeout=40,**kwargs)
    return client._json(resp)

def select(client,app,tid,key,keys):
    result=[]
    for start in range(0,len(keys),35):
        group=keys[start:start+35]
        terms=[f'CurrentValue.[{key}]="{v}"' for v in group]
        expression=terms[0] if len(terms)==1 else 'OR('+','.join(terms)+')'
        page=None
        while True:
            params={'filter':expression,'page_size':500}
            if page:params['page_token']=page
            data=api(client,'GET',f'apps/{app}/tables/{tid}/records',params=params)['data']
            result+=data.get('items',[])
            page=data.get('page_token')
            if not data.get('has_more'):break
    return result

def upsert(client,app,tid,key,rows,events,preserve_status=False):
    keys=[str(r[key]) for r in rows]
    existing=select(client,app,tid,key,keys)
    by_key={str(r['fields'].get(key,'')):r for r in existing}
    assert len(by_key)==len(existing),'Duplicate stable IDs; stop instead of guessing'
    create=[];update=[]
    for row in rows:
        item=dict(row);k=str(row[key])
        if k in by_key:
            old=by_key[k]['fields']
            if preserve_status:
                # Existing metadata and inclusion decisions are not replaced by an intake refresh.
                for field in list(item):
                    if old.get(field) and field not in (key,'last_checked'):
                        item.pop(field,None)
                if str(row.get('pmid',''))=='33888596':item['pmcid']='PMC8550608'
            changed={field:value for field,value in item.items() if old.get(field)!=value}
            if changed:update.append({'record_id':by_key[k]['record_id'],'fields':changed})
        else:create.append({'fields':item})
    for label,payload in [('update',update),('create',create)]:
        for start in range(0,len(payload),100):
            part=payload[start:start+100]
            if not part:continue
            try:
                if label=='update':client.batch_update_bitable_records(app,tid,part)
                else:client.batch_create_bitable_records(app,tid,part)
            except Exception:
                # Unknown write outcomes are inspected once; never retry a blind POST.
                seen=select(client,app,tid,key,keys)
                (PRIVATE/'unknown_write_outcome.json').write_text(json.dumps({'table_id':tid,'operation':label,'observed_keys':[r['fields'].get(key) for r in seen],'pending_keys':keys},ensure_ascii=False,indent=2),encoding='utf-8')
                raise
            events.append({'table_id':tid,'operation':label,'records':len(part)})
            (PRIVATE/'feishu_write_journal.json').write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf-8')
    return select(client,app,tid,key,keys)

def upload(client,app,path,cache):
    sha=hashlib.sha256(path.read_bytes()).hexdigest()
    if sha in cache:return cache[sha]
    token=client.upload_bitable_file(app,path)
    cache[sha]=token
    (PRIVATE/'upload_token_cache.json').write_text(json.dumps(cache,indent=2),encoding='utf-8')
    return token

def gallery(client,app,tid,fields,name,route=None):
    views=client.list_bitable_views(app,tid)
    matches=[v for v in views if v['view_name']==name]
    if matches:vid=matches[0]['view_id']
    else:
        res=client.create_bitable_view(app,tid,name,'gallery')
        vid=res['data']['view']['view_id'] if 'view' in res['data'] else res['data']['view_id']
    conditions=[{'field_id':fields['版本'],'operator':'is','value':json.dumps([VERSION],ensure_ascii=False)}]
    if route:conditions.append({'field_id':fields['途径'],'operator':'is','value':json.dumps([route],ensure_ascii=False)})
    api(client,'PATCH',f'apps/{app}/tables/{tid}/views/{vid}',json={'property':{'filter_info':{'conjunction':'and','conditions':conditions}}})
    actual=api(client,'GET',f'apps/{app}/tables/{tid}/records',params={'view_id':vid,'page_size':100})['data'].get('items',[])
    expected=10 if route else 20
    assert len(actual)==expected,(name,len(actual),expected)
    assert all(r['fields'].get('版本')==VERSION for r in actual)
    return {'name':name,'view_id':vid,'records':len(actual),'url':DOMAIN+'?table='+tid+'&view='+vid}

def main(apply=False):
    load_dotenv(ROOT/'.env')
    client=FeishuClient()
    app=client.resolve_bitable_app_token(app_token=os.getenv('FEISHU_BITABLE_APP_TOKEN',''),wiki_node_token=os.getenv('FEISHU_BITABLE_WIKI_NODE_TOKEN',''))
    node=client.get_wiki_node(WIKI)['data']['node']
    assert node['obj_type']=='bitable' and node['obj_token']==app,'Original wiki mismatch'
    tables={t['table_id']:t['name'] for t in client.list_bitable_tables(app)}
    for kind,(tid,name) in TARGETS.items():assert tables.get(tid)==name,(kind,tid,'target changed or unavailable')
    print('original active target names and wiki verified',flush=True)
    if not apply:
        print('NMN active finding matches',len(select(client,app,TARGETS['findings'][0],'pmid',['33888596'])))
        return
    gh=json.loads((PRIVATE/'github_receipt.json').read_text(encoding='utf-8'))
    assert gh.get('remote_verified') and gh.get('sha') and gh.get('publication_category')=='november_cards_and_maintenance','Publish verified November GitHub source first'
    for item in json.loads((PRIVATE/'public_manifest.json').read_text(encoding='utf-8')):
        assert hashlib.sha256((STAGE/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
    cards=json.loads((DATA/'ingredient_cards.json').read_text(encoding='utf-8'))['cards']
    import csv
    with (DATA/'candidate_sources_increment.csv').open(encoding='utf-8-sig') as stream:
        candidates=list(csv.DictReader(stream))
    backup={'cards':client.list_bitable_records(app,TARGETS['cards'][0]),'heatmap':client.list_bitable_records(app,TARGETS['heatmap'][0]),'home':client.list_bitable_records(app,TARGETS['home'][0]),'candidates':select(client,app,TARGETS['candidates'][0],'id',[r['id'] for r in candidates]),'sources':select(client,app,TARGETS['sources'][0],'library_id',[r['id'] for r in candidates])}
    backup_path=PRIVATE/'feishu_before_sync.json'
    if not backup_path.exists():backup_path.write_text(json.dumps(backup,ensure_ascii=False,indent=2),encoding='utf-8')
    print('original table records backed up; starting scoped upserts',flush=True)
    cache=json.loads((PRIVATE/'upload_token_cache.json').read_text()) if (PRIVATE/'upload_token_cache.json').exists() else {}
    events=json.loads((PRIVATE/'feishu_write_journal.json').read_text(encoding='utf-8')) if (PRIVATE/'feishu_write_journal.json').exists() else []
    tid=TARGETS['cards'][0]
    fields={r['field_name']:r['field_id'] for r in client.list_bitable_fields(app,tid)}
    for field in ['途径','用途','适合谁','预期效果','证据等级','来源','版本']:
        if field not in fields:
            client.create_bitable_text_field(app,tid,field)
            events.append({'table_id':tid,'operation':'add_text_field','field':field})
    fields={r['field_name']:r['field_id'] for r in client.list_bitable_fields(app,tid)}
    payload=[]
    for number,c in enumerate(cards,1):
        token=upload(client,app,STAGE/'docs/assets/ingredients-2026-11'/(c['id']+'.png'),cache)
        src='; '.join([f'https://pubmed.ncbi.nlm.nih.gov/{i}/' for i in c['sources']]+['https://doi.org/'+d for d in c.get('doi_sources',[])])
        payload.append({'card_id':c['id'],'成分':c['name'],'英文名':c['en'],'卡片图':[{'file_token':token}],'一句话':c['conclusion'],'注意':c['risks'],'途径':'外用' if c['route']=='topical' else '口服','用途':c['endpoint'],'适合谁':c['recommendation'],'预期效果':c['expected_effect'],'证据等级':c['grade']+'（'+c['grade_reason']+'）','来源':src,'版本':VERSION,'更新月份':'2026-11','评级资料日期':'2026-11-01','图片更新日期':'2026-11-01','GitHub公开入口':REPO+'/blob/main/content/cards/ingredients-2026-11/'+c['id']+'.md','品牌标识':'宇多Yul细胞/yulcell','Brand':'yulcell'})
        if number%4==0:print('card images available',number,'/20',flush=True)
    readback=upsert(client,app,tid,'card_id',payload,events)
    for intended in payload:
        actual=next(r['fields'] for r in readback if r['fields'].get('card_id')==intended['card_id'])
        for field in ('成分','英文名','途径','用途','一句话','适合谁','预期效果','证据等级','注意','来源','版本','更新月份','评级资料日期','图片更新日期','GitHub公开入口'):
            assert actual.get(field)==intended[field],(intended['card_id'],field)
        assert actual.get('卡片图') and actual['卡片图'][0]['file_token']==intended['卡片图'][0]['file_token']
    card_receipt={'status':'cards_verified_other_steps_pending','github_source_commit':gh['sha'],'table_id':tid,'cards':[{'card_id':r['fields']['card_id'],'record_id':r['record_id']} for r in readback],'writes':[e for e in events if e.get('table_id')==tid]}
    (PRIVATE/'feishu_cards_receipt.json').write_text(json.dumps(card_receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print('20 cards verified field-by-field',flush=True)
    views=[gallery(client,app,tid,fields,'11月｜外用10项','外用'),gallery(client,app,tid,fields,'11月｜口服10项','口服'),gallery(client,app,tid,fields,'11月｜本期20项')]
    lead=upload(client,app,STAGE/'docs/assets/ingredients-2026-11/00-ingredient-guide.png',cache)
    heat=TARGETS['heatmap'][0]
    heat_records=client.list_bitable_records(app,heat)
    first=next(r for r in heat_records if r['fields'].get('asset_id')=='H001')
    old_images=[{'file_token':v['file_token']} for v in first['fields'].get('图片',[]) if v['file_token']!=lead]
    heat_payload={'asset_id':'H001','标题':'00 抗衰成分推荐｜按当前研究证据强度分级','图片':[{'file_token':lead}]+old_images,'说明':'先看外用10项与口服10项，再看原研究热力图。证据等级表示结论把握，也可对应未见获益。原热力图保留为后续附件。','GitHub公开入口':REPO+'/blob/main/content/cards/ingredients-2026-11/index.md','更新月份':'2026-11'}
    verified=upsert(client,app,heat,'asset_id',[heat_payload],events)
    assert verified[0]['fields']['图片'][0]['file_token']==lead
    for r in heat_records:
        if r['fields'].get('asset_id') in ('H005','H006'):
            text='历史主题分级栏代理，仅作旧版记录；A/B栏个数不是优质研究比例。新入口按具体途径与终点评级。'
            upsert(client,app,heat,'asset_id',[{'asset_id':r['fields']['asset_id'],'标题':'历史代理图（非优质研究比例） '+r['fields'].get('asset_id',''),'说明':text}],events)
    home=TARGETS['home'][0]
    home_row={'entry_id':'NOV26-START','公开标题':'00 抗衰成分推荐｜外用10项、口服10项','阅读顺序':'00','中文名称':'抗衰成分推荐｜按当前研究证据强度分级','English title':'Ingredient evidence cards: 10 topical and 10 oral','适合谁':'先查成分、用途、效果和风险的读者','一句话说明':'按具体用途看证据，等级高也可能对应未见获益。','GitHub链接':REPO+'/blob/main/content/cards/ingredients-2026-11/index.md','飞书链接':views[2]['url'],'资产类型':'成分资料卡','冻结日期':'2026-11-01','复核日期':'2026-11-01','品牌标识':'宇多Yul细胞/yulcell','Brand':'yulcell','状态':'公开'}
    upsert(client,app,home,'entry_id',[home_row],events)
    # Metadata only: preserve prior inclusion decisions and notes on existing rows.
    trimmed=lambda v: str(v) if len(str(v))<=250 else str(v)[:232]+' [完整题名见GitHub]'
    cand_rows=[];source_rows=[]
    for row in candidates:
        item={k:trimmed(v) for k,v in row.items()}
        if item.get('include_status')!='retracted_excluded':item['include_status']='candidate_metadata_pending_full_appraisal'
        item.update({'公开标题':trimmed(row['id']+' | '+row['title_en']),'品牌标识':'宇多Yul细胞/yulcell','Brand':'yulcell','GitHub公开入口':REPO+'/blob/main/data/maintenance_2026_11/source_metadata.json'})
        cand_rows.append(item)
        source={k:v for k,v in item.items() if k in ('公开标题','品牌标识','Brand','GitHub公开入口','title_en','title_zh','year','source','pmid','pmcid','doi','url','query','include_status','last_checked')}
        source['library_id']=row['id'];source_rows.append(source)
    candidate_read=upsert(client,app,TARGETS['candidates'][0],'id',cand_rows,events,preserve_status=True)
    source_read=upsert(client,app,TARGETS['sources'][0],'library_id',source_rows,events,preserve_status=True)
    assert len(candidate_read)==len(candidates) and len(source_read)==len(candidates)
    with (DATA/'candidate_sources_merged.csv').open(encoding='utf-8-sig') as stream:
        canonical={r['id']:r for r in csv.DictReader(stream)}
    metadata_checks=[]
    for rows,key in ((candidate_read,'id'),(source_read,'library_id')):
        for intended in candidates:
            actual=next(r['fields'] for r in rows if r['fields'].get(key)==intended['id'])
            for field in ('pmid','doi','year'):
                assert str(actual.get(field,''))==str(canonical[intended['id']].get(field,'')),(intended['id'],field,'metadata mismatch')
        metadata_checks.append({'key':key,'records':len(rows),'fields':['pmid','doi','year']})
    # Confirmed NMN identity repair only; no new grade and no guessed insertion.
    found=select(client,app,TARGETS['findings'][0],'pmid',['33888596'])
    repairs=[]
    for rec in found:
        old=rec['fields'];new={}
        if old.get('pmcid')!='PMC8550608':new['pmcid']='PMC8550608'
        if old.get('topic_id')=='rapamycin-mtor-aging':new.update({'topic_id':'nad-nmn-nr-aging','topic_zh':'NAD/NMN/NR','topic_en':'NAD/NMN/NR'})
        if new:
            client.update_bitable_record(app,TARGETS['findings'][0],rec['record_id'],new)
            repairs.append({'pmid':'33888596','fields':list(new)})
    cards_all=client.list_bitable_records(app,tid)
    receipt={'date':'2026-11-01','version':VERSION,'github_source_commit':gh['sha'],'cards':{'table_id':tid,'verified_new_cards':20,'total_records':len(cards_all),'stable_ids':[c['id'] for c in cards],'records':[{'card_id':r['fields']['card_id'],'record_id':r['record_id']} for r in readback],'created':sum(e.get('records',0) for e in events if e.get('table_id')==tid and e.get('operation')=='create'),'updated':sum(e.get('records',0) for e in events if e.get('table_id')==tid and e.get('operation')=='update'),'exact_fields_checked':['成分','英文名','途径','用途','一句话','适合谁','预期效果','证据等级','注意','来源','版本','卡片图','GitHub公开入口','更新月份','评级资料日期','图片更新日期']},'views':views,'heatmap':{'table_id':heat,'first_record':'H001','guide_first_attachment_verified':True,'original_heatmap_attachments_retained':len(old_images)},'home':{'table_id':home,'entry_id':'NOV26-START'},'candidate_metadata':{'table_id':TARGETS['candidates'][0],'matched_records':len(candidate_read)},'source_metadata':{'table_id':TARGETS['sources'][0],'matched_records':len(source_read)},'metadata_checks':metadata_checks,'nmn_repairs':repairs,'writes':events,'sharing_permissions_changed':False,'tables_created':0,'rows_deleted':0}
    (PRIVATE/'feishu_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');a=p.parse_args();main(a.apply)
