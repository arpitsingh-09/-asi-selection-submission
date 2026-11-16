"""Prepare/validate Task 3 execution manifests without importing an encoder."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime
from importlib.metadata import version
from pathlib import Path
from abstract_embeddings import BASE_REV,ADAPTER_REV,PROVENANCE
from human_check import normalize,title_key,value


def sha_file(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def sha_text(text):return hashlib.sha256(text.encode()).hexdigest()
def jsonl(path):
    with Path(path).open() as f:
        for line in f:
            if line.strip():yield json.loads(line)

def dump(path,obj):Path(path).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def write_rows(path,rows):Path(path).write_text(''.join(json.dumps(r,allow_nan=False)+'\n' for r in rows))
def parse_date(s):
    dt=datetime.fromisoformat(s.replace('Z','+00:00'))
    if dt.tzinfo is None:raise ValueError('timezone missing')
    return dt

def model_inventory(hub):
    base=hub/'models--allenai--specter2_base'/'snapshots'/BASE_REV
    adapter=hub/'models--allenai--specter2'/'snapshots'/ADAPTER_REV
    paths=[base/n for n in ('config.json','pytorch_model.bin','tokenizer.json','tokenizer_config.json','vocab.txt','special_tokens_map.json')]
    paths += [adapter/n for n in ('adapter_config.json','pytorch_adapter.bin','README.md')]
    assets={str(p):{'bytes':p.stat().st_size,'sha256':sha_file(p)} for p in paths}
    config=json.loads((base/'config.json').read_text());ac=json.loads((adapter/'adapter_config.json').read_text())
    if config['hidden_size']!=768 or config['max_position_embeddings']!=512 or ac['name']!='[PRX]':
        raise ValueError('unexpected pinned model architecture/adapter')
    return {'base_revision':BASE_REV,'adapter_revision':ADAPTER_REV,'base_path':str(base),'adapter_path':str(adapter),
        'assets':assets,'architecture':config,'adapter_config':ac,
        'dependencies':{k:version(k) for k in ('torch','transformers','adapters','numpy')},
        'release_evidence':{'type':'official_revision_commit_dates','commit_date':'2024-12-04',
            'sources':[f'https://huggingface.co/allenai/specter2_base/commit/{BASE_REV}',f'https://huggingface.co/allenai/specter2/commit/{ADAPTER_REV}'],
            'conservative_weights_existence_bound':'2024-12-31T23:59:59.999999+00:00',
            'exact_training_data_cutoff_known':False,'first_global_test_publication_verified':False,
            'interpretation':'Pinned weights existed by these commits; not an exact training-data cutoff or proof against earlier preprints.'}}

def materialize(items,sources):
    """Read each needed source once; return exact abstracts in item order.
    No title, rating, label or review text is returned to an embedding worker.
    """
    groups={}
    for item in items:groups.setdefault(item['source'],{})[item['forum_id']]=item
    texts={}
    for key,wanted in groups.items():
        source=sources[key];path=Path(source['path'])
        if sha_file(path)!=source['sha256']:raise ValueError('source file fingerprint changed: '+key)
        for r in jsonl(path):
            pid=r.get('forum_id') if source['kind']=='prepared_test' else r.get('id')
            if pid not in wanted:continue
            s=r['abstract'] if source['kind']=='prepared_test' else value(r['content']['abstract'])
            if not isinstance(s,str) or not s.strip() or sha_text(s)!=wanted[pid]['text_sha256']:
                raise ValueError('abstract binding mismatch: '+str(pid))
            if (key,pid) in texts:raise ValueError('duplicate source forum')
            texts[key,pid]=s
        if any((key,pid) not in texts for pid in wanted):raise ValueError('missing source abstract')
    return [texts[x['source'],x['forum_id']] for x in items]

def validate_claims(rows,benchmark):
    byid={r['forum_id']:r for r in benchmark};accepted={}
    for row in rows:
        pid=row.get('forum_id')
        if pid not in byid or pid in accepted:raise ValueError('unknown/duplicate claim forum')
        b=byid[pid]
        if row.get('abstract_sha256')!=sha_text(b['abstract']) or not row.get('provenance'):
            raise ValueError('claim source binding/provenance missing')
        claims=row.get('claims',[])
        if not 4<=len(claims)<=10:raise ValueError('4-10 supplied atomic claims required')
        seen=set()
        for c in claims:
            if not isinstance(c.get('claim'),str) or not c['claim'].strip() or not isinstance(c.get('evidence'),str) or not c['evidence'].strip() or c['evidence'] not in b['abstract']:
                raise ValueError('unsupported saved claim')
            k=' '.join(c['claim'].casefold().split())
            if k in seen:raise ValueError('duplicate claim text')
            seen.add(k)
        accepted[pid]=row
    return accepted

def prepare(output,claims_path=None):
    root=Path(__file__).resolve().parent;recovered=root/'analysis/recovered_inputs_v1'
    test=[normalize(r) for r in jsonl(recovered/'benchmark_inputs.jsonl')]
    if len(test)!=299 or len({r['forum_id'] for r in test})!=299:raise ValueError('299 distinct test forums required')
    for r in test:
        if not r['abstract'].strip() or r['label'] not in ('POSITIVE','NEGATIVE') or sha_text(r['abstract'])!=r['abstract_sha256']:
            raise ValueError('incomplete test record')
        parse_date(r['published'])
    summary=json.loads((recovered/'summary.json').read_text())
    ref_path=recovered/'reference_manifest.csv'
    if sha_file(ref_path)!=summary['reference_manifest_sha256'] or sha_file(recovered/'benchmark_inputs.jsonl')!=summary['benchmark_inputs_sha256']:
        raise ValueError('recovered input fingerprint changed')
    with ref_path.open() as f:refs=list(csv.DictReader(f))
    with (root/'analysis/historical_manifest.csv').open() as f:historical={r['forum_id']:r for r in csv.DictReader(f)}
    if len(refs)!=25186 or len(historical)!=25186 or len({r['forum_id'] for r in refs})!=25186 or {r['forum_id'] for r in refs}!=set(historical):raise ValueError('frozen history/reference mismatch')
    test_ids={r['forum_id'] for r in test};test_titles={title_key(r['title']) for r in test}
    earliest=min(parse_date(r['published']) for r in test)
    sources={};items=[];targets=[]
    for r in refs:
        pid=r['forum_id'];h=historical[pid];year=int(h['year'])
        if pid in test_ids or title_key(h['title']) in test_titles or parse_date(r['public_date'])>=earliest or year not in (2022,2023,2024,2025):
            raise ValueError('training leakage/chronology')
        if any(s in title_key(h['title']) for s in ('hotpate','conjuringsemanticsimilarity','counterfactualtechniquesforenhancingcustomerretention')):
            raise ValueError('overlap exclusion missing')
        key=f'history_{year}'
        if key not in sources:sources[key]={'path':r['source'],'kind':'openreview','sha256':sha_file(r['source'])}
        items.append({'key':pid,'forum_id':pid,'split':'history','source':key,'text_sha256':r['abstract_sha256']})
        targets.append({'forum_id':pid,'year':year,'title':h['title'],'review_count':int(h['review_count']),
            'mean_rating':float(h['mean_rating']),'published':r['public_date'],'venue':'ICLR',
            'abstract_sha256':r['abstract_sha256']})
    sources['test']={'path':str(recovered/'benchmark_inputs.jsonl'),'kind':'prepared_test','sha256':sha_file(recovered/'benchmark_inputs.jsonl')}
    for r in test:items.append({'key':r['forum_id'],'forum_id':r['forum_id'],'split':'test','source':'test','text_sha256':r['abstract_sha256']})
    texts=materialize(items,sources)  # binding validation only, not tokenization/model inference
    supplied=validate_claims(list(jsonl(claims_path)),test) if claims_path else {}
    requests=[];claim_items=[]
    for r in test:
        pid=r['forum_id'];requests.append({'forum_id':pid,'abstract_sha256':r['abstract_sha256'],'abstract':r['abstract'],
            'claims':supplied.get(pid,{}).get('claims',[]),'provenance':supplied.get(pid,{}).get('provenance'),
            'status':'supplied_source_bound_semantic_review_required' if pid in supplied else 'missing_saved_or_reviewed_claims'})
        for i,c in enumerate(supplied.get(pid,{}).get('claims',[])):
            claim_items.append({'key':f'claim:{pid}:{i}','forum_id':pid,'split':'claim','source':'claims',
                'claim_index':i,'text_sha256':sha_text(c['claim'])})
    inventory=model_inventory(Path.home()/'.cache/huggingface/hub')
    output.mkdir(parents=True,exist_ok=False)
    dump(output/'model_inventory.json',inventory);write_rows(output/'embedding_items.jsonl',items+claim_items)
    write_rows(output/'history_targets.jsonl',targets);write_rows(output/'claim_requests.jsonl',requests)
    if supplied:write_rows(output/'supplied_claims.jsonl',list(supplied.values()))
    protocol=root/'TASK3_EXECUTION_PROTOCOL.md'
    code={str(root/name):sha_file(root/name) for name in ('task3_plan.py','task3_eligibility.py','task3_execution.py','task3_novelty.py','human_check.py','abstract_embeddings.py','evaluate_human_check.py')}
    plan={'format':1,'code_sha256':code,'sources':sources,'provenance':PROVENANCE,'model_inventory':inventory,
        'protocol_path':str(protocol),'protocol_sha256':sha_file(protocol),
        'items_sha256':sha_file(output/'embedding_items.jsonl'),'targets_sha256':sha_file(output/'history_targets.jsonl'),
        'claim_requests_sha256':sha_file(output/'claim_requests.jsonl'),
        'benchmark_path':str(recovered/'benchmark_inputs.jsonl'),'reference_sha256':sha_file(ref_path),
        'history_count':len(refs),'test_count':len(test),'claim_papers':len(supplied),
        'claims_sha256':sha_file(output/'supplied_claims.jsonl') if supplied else None,
        'prior_test_exposure':True,'input_text_policy':'original_abstract_only_raw_CLS_for_ridge_unit_normalized_for_novelty',
        'resource_estimate':{'embedding_cpu_threads':1,'embedding_batch_size':2,'embedding_ram_gib':[2,4],
            'evaluation_ram_gib':[1,2],'raw_history_test_float32_bytes':(len(refs)+len(test))*768*4,
            'runtime':'Unmeasured. At 0.25/1/5 seconds per abstract: approximately 1.8/7.1/35.4 CPU hours, excluding claims and evaluation. Calibrate on an authorized small batch.'},
        'validated':{'required_test_fields':299,'labels':dict(Counter(r['label'] for r in test)),
            'historical_abstract_bindings':len(refs),'chronology':'public-release chronology only; first global publication unverified'},
        'status':'prepared_no_inference_or_evaluation_authorized'}
    dump(output/'plan.json',plan)
    auth={'plan_sha256':sha_file(output/'plan.json'),'protocol_sha256':plan['protocol_sha256'],
        'authorize_inference':False,'authorize_evaluation':False,'authorization_source':None,'preregistration_verified':False,
        'post_cutoff_verified':False,'eligibility_review_path':None,'eligibility_review_sha256':None,
        'encoder_cutoff':None,'note':'Preparation only. Future explicit authorization and eligibility evidence required; do not relabel prior exposure as blind.'}
    dump(output/'authorization.template.json',auth)
    print({'history':len(refs),'test':len(test),'claim_papers':len(supplied),'model_loaded':False,'vectors_generated':0})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--claims',type=Path)
    a=p.parse_args();prepare(a.output,a.claims)
