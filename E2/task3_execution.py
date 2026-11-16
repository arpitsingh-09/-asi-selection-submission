"""Prepared Task 3 commands. No inference/evaluation runs without explicit gates.

status is read-only. embed requires future authorization; defaults to limit=0.
export checks complete bound vectors but does not evaluate. evaluate additionally
requires complete supplied claims, eligibility evidence and evaluation approval.
"""
import os
for _name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_name]='1'
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false',CUDA_VISIBLE_DEVICES='')
import argparse
import hashlib
import json
import sqlite3
import subprocess
from pathlib import Path
import numpy as np
from task3_eligibility import validate_review
from task3_plan import sha_file,sha_text,jsonl,dump,materialize,parse_date,validate_claims


def load_plan(folder):
    folder=Path(folder).resolve();p=json.loads((folder/'plan.json').read_text())
    if p.get('format')==1 and not p.get('code_sha256'):raise ValueError('execution code fingerprints required')
    for path,fingerprint in p.get('code_sha256',{}).items():
        if sha_file(path)!=fingerprint:raise ValueError('execution code changed: '+path)
    for name,key in [('embedding_items.jsonl','items_sha256'),('history_targets.jsonl','targets_sha256'),('claim_requests.jsonl','claim_requests_sha256')]:
        if sha_file(folder/name)!=p[key]:raise ValueError('plan artifact changed: '+name)
    if p['claims_sha256'] and sha_file(folder/'supplied_claims.jsonl')!=p['claims_sha256']:raise ValueError('supplied claims changed')
    if sha_file(p['protocol_path'])!=p['protocol_sha256']:raise ValueError('protocol changed')
    if sha_file(p['benchmark_path'])!=p['sources']['test']['sha256']:raise ValueError('benchmark changed')
    return p,list(jsonl(folder/'embedding_items.jsonl'))

def model_key(plan):
    payload={'provenance':plan['provenance'],'assets':plan['model_inventory']['assets'],
        'execution_code':plan.get('code_sha256',{})}
    return sha_text(json.dumps(payload,sort_keys=True))

def authorize(folder,plan,path,operation):
    if path is None:raise ValueError('explicit future authorization file required')
    auth=json.loads(Path(path).read_text())
    if not auth.get('authorize_'+operation):raise ValueError(operation+' is not authorized')
    if auth.get('plan_sha256')!=sha_file(Path(folder)/'plan.json') or auth.get('protocol_sha256')!=plan['protocol_sha256']:
        raise ValueError('authorization fingerprint mismatch')
    # The user must authorize a concrete frozen plan; the code never enables flags.
    if not auth.get('authorization_source'):raise ValueError('authorization source required')
    root=Path(__file__).resolve().parent
    committed=subprocess.check_output(['git','show','HEAD:E2/TASK3_EXECUTION_PROTOCOL.md'],cwd=root)
    if hashlib.sha256(committed).hexdigest()!=plan['protocol_sha256']:raise ValueError('execution protocol must be committed unchanged')
    if operation=='evaluation':
        if not auth.get('preregistration_verified') or not auth.get('post_cutoff_verified'):raise ValueError('preregistration/eligibility not verified')
        review=auth.get('eligibility_review_path')
        if not review or sha_file(review)!=auth.get('eligibility_review_sha256'):raise ValueError('eligibility evidence missing/changed')
        rows=json.loads(Path(review).read_text())['records'];bench=list(jsonl(plan['benchmark_path']))
        validate_review(rows,bench,auth['encoder_cutoff'],
            plan['model_inventory']['release_evidence']['conservative_weights_existence_bound'],
            list(jsonl(Path(folder)/'history_targets.jsonl')))
    return auth

def open_cache(folder,write=False):
    path=Path(folder)/'task3_vectors.sqlite3'
    if not path.exists() and not write:return None
    connection=sqlite3.connect(path if write else path.resolve().as_uri()+'?mode=ro',uri=not write)
    if write:
        connection.execute('CREATE TABLE IF NOT EXISTS vectors(model_key TEXT,text_sha256 TEXT,checksum TEXT,vector BLOB,PRIMARY KEY(model_key,text_sha256))')
    return connection

def vector(connection,key,text_hash,dimension=768):
    if connection is None:return None
    row=connection.execute('SELECT checksum,vector FROM vectors WHERE model_key=? AND text_sha256=?',(key,text_hash)).fetchone()
    if row is None:return None
    checksum,blob=row
    if len(blob)!=dimension*4 or hashlib.sha256(blob).hexdigest()!=checksum:raise ValueError('cached embedding corruption')
    v=np.frombuffer(blob,dtype='<f4')
    if not np.isfinite(v).all() or np.linalg.norm(v)==0:raise ValueError('invalid cached embedding')
    return v

def put_vector(connection,key,text_hash,v):
    v=np.asarray(v,dtype='<f4')
    if v.shape!=(768,) or not np.isfinite(v).all() or np.linalg.norm(v)==0:raise ValueError('invalid generated CLS vector')
    blob=v.tobytes();checksum=hashlib.sha256(blob).hexdigest()
    # Existing valid vectors are immutable. Resume must never silently replace one.
    prior=vector(connection,key,text_hash)
    if prior is not None:
        if not np.array_equal(prior,v):raise ValueError('conflicting embedding for exact text/model')
        return
    connection.execute('INSERT INTO vectors VALUES(?,?,?,?)',(key,text_hash,checksum,blob))

def texts_for_items(folder,plan,items):
    abstract_items=[x for x in items if x['split']!='claim']
    mapped={x['key']:s for x,s in zip(abstract_items,materialize(abstract_items,plan['sources']))}
    if any(x['split']=='claim' for x in items):
        supplied={r['forum_id']:r for r in jsonl(Path(folder)/'supplied_claims.jsonl')}
        for x in items:
            if x['split']!='claim':continue
            text=supplied[x['forum_id']]['claims'][x['claim_index']]['claim']
            if sha_text(text)!=x['text_sha256']:raise ValueError('claim text hash mismatch')
            mapped[x['key']]=text
    return [mapped[x['key']] for x in items]

def batched_cpu_encoder(plan):
    # Fail before torch import/model load if scheduling isolation is unavailable.
    os.nice(15)
    for path,info in plan['model_inventory']['assets'].items():
        if sha_file(path)!=info['sha256']:raise ValueError('pinned model asset changed')
    import torch
    from transformers import AutoTokenizer
    from adapters import AutoAdapterModel
    torch.set_num_threads(1);torch.set_num_interop_threads(1)
    inv=plan['model_inventory'];base=inv['base_path'];adapter=inv['adapter_path']
    tokenizer=AutoTokenizer.from_pretrained(base,local_files_only=True,trust_remote_code=False)
    model=AutoAdapterModel.from_pretrained(base,local_files_only=True,trust_remote_code=False).to(device='cpu',dtype=torch.float32)
    model.load_adapter(adapter,load_as='proximity',set_active=True)
    model.set_active_adapters('proximity');model.requires_grad_(False);model.eval()
    def encode(texts):
        inputs=tokenizer(texts,truncation=True,padding=True,max_length=512,return_tensors='pt')
        with torch.inference_mode():return model(**inputs).last_hidden_state[:,0,:].float().cpu().numpy()
    return encode

def status(folder):
    plan,items=load_plan(folder);connection=open_cache(folder);key=model_key(plan)
    try:complete=sum(vector(connection,key,x['text_sha256']) is not None for x in items)
    finally:
        if connection is not None:connection.close()
    return {'history':plan['history_count'],'test':plan['test_count'],'required_items':len(items),'complete_items':complete,
        'claim_papers':plan['claim_papers'],'missing_claim_papers':plan['test_count']-plan['claim_papers'],
        'authorized_now':False,'status':'prepared_only','model_loaded':False}

def embed(folder,authorization,limit=0,batch_size=2,encoder_factory=batched_cpu_encoder):
    if limit<0 or batch_size<1 or batch_size>8:raise ValueError('bounded positive batch size (1-8) and nonnegative limit required')
    if limit==0:return status(folder)
    plan,items=load_plan(folder);authorize(folder,plan,authorization,'inference')
    key=model_key(plan);connection=open_cache(folder)
    try:
        missing=[];seen=set()
        for x in items:
            if x['text_sha256'] in seen or vector(connection,key,x['text_sha256']) is not None:continue
            seen.add(x['text_sha256']);missing.append(x)
    finally:
        if connection is not None:connection.close()
    selected=missing[:limit]
    if not selected:return status(folder)
    texts=texts_for_items(folder,plan,selected)
    # Length ordering reduces padding; IDs remain independently bound by hashes.
    order=sorted(range(len(selected)),key=lambda i:(len(texts[i].split()),selected[i]['key']))
    encode=encoder_factory(plan)
    connection=open_cache(folder,write=True)
    try:
        for start in range(0,len(order),batch_size):
            ids=order[start:start+batch_size];v=np.asarray(encode([texts[i] for i in ids]),dtype=np.float32)
            if v.shape!=(len(ids),768):raise ValueError('encoder batch alignment/shape')
            with connection:
                for i,row in zip(ids,v):put_vector(connection,key,selected[i]['text_sha256'],row)
    finally:connection.close()
    result=status(folder)
    result.update(model_loaded=True,inference_ran=True,new_unique_texts=len(selected),authorized_now=True,status='bounded_embedding_batch_completed')
    return result

def matrices(folder,plan,items):
    connection=open_cache(folder);key=model_key(plan);arrays={};ids={};hashes={}
    try:
        for split in ('history','test','claim'):
            chosen=[x for x in items if x['split']==split]
            vectors=[]
            for x in chosen:
                v=vector(connection,key,x['text_sha256'])
                if v is None:raise ValueError('incomplete embeddings: '+x['key'])
                vectors.append(v)
            arrays[split]=np.stack(vectors) if vectors else np.empty((0,768),np.float32)
            ids[split]=[x['key'] for x in chosen];hashes[split]=[x['text_sha256'] for x in chosen]
    finally:
        if connection is not None:connection.close()
    return arrays,ids,hashes

def export(folder,output):
    output=Path(output)
    if output.exists():raise ValueError('refusing to overwrite export')
    plan,items=load_plan(folder);arrays,ids,hashes=matrices(folder,plan,items)
    output.mkdir(parents=True)
    np.savez(output/'embeddings.npz',history_embeddings=arrays['history'],test_embeddings=arrays['test'],claim_embeddings=arrays['claim'])
    dump(output/'bindings.json',{'ids':ids,'text_sha256':hashes,'model_key':model_key(plan),
        'plan_sha256':sha_file(Path(folder)/'plan.json'),'matrix_sha256':sha_file(output/'embeddings.npz')})
    return {'exported':True,'history':len(ids['history']),'test':len(ids['test']),'claims':len(ids['claim'])}

def evaluate(folder,authorization,output):
    output=Path(output)
    predictions_path=output.with_name(output.name+'.predictions.json')
    if output.exists() or predictions_path.exists():raise ValueError('refusing to overwrite evaluation/predictions')
    plan,items=load_plan(folder);auth=authorize(folder,plan,authorization,'evaluation')
    if plan['claim_papers']!=plan['test_count']:raise ValueError('all benchmark claims required')
    bench=list(jsonl(plan['benchmark_path']));supplied=validate_claims(list(jsonl(Path(folder)/'supplied_claims.jsonl')),bench)
    arrays,ids,hashes=matrices(folder,plan,items)
    if ids['test']!=[r['forum_id'] for r in bench]:raise ValueError('test ordering mismatch')
    targets=list(jsonl(Path(folder)/'history_targets.jsonl'))
    if ids['history']!=[r['forum_id'] for r in targets]:raise ValueError('history ordering mismatch')
    claim_lookup={key:v for key,v in zip(ids['claim'],arrays['claim'])}
    claim_arrays=[np.stack([claim_lookup[f"claim:{r['forum_id']}:{i}"] for i in range(len(supplied[r['forum_id']]['claims']))]) for r in bench]
    from task3_novelty import novelty_scores
    scores=novelty_scores(arrays['test'],arrays['history'],claim_arrays)
    # Freeze label-independent prediction vectors before baseline fitting/metrics.
    with predictions_path.open('x') as f:
        json.dump({'test_ids':ids['test'],'scores':scores,'model_key':model_key(plan),
            'plan_sha256':sha_file(Path(folder)/'plan.json')},f,indent=2,allow_nan=False)
    bundle={'benchmark':bench,'history':targets,'history_ids':ids['history'],'test_ids':ids['test'],
        'test_abstract_sha256':hashes['test'],'history_abstract_sha256':hashes['history'],
        'embedding_provenance':plan['provenance'],'novelty_scores':scores,
        'authorization':{'prospective_preregistration_verified':auth['preregistration_verified'],
            'post_cutoff_verified':auth['post_cutoff_verified'],'encoder_cutoff':auth['encoder_cutoff'],'protocol_sha256':plan['protocol_sha256']}}
    from evaluate_human_check import evaluate as legacy_evaluate
    report=legacy_evaluate(bundle,{'history_embeddings':arrays['history'],'test_embeddings':arrays['test']},Path(plan['protocol_path']))
    report.update(plan_sha256=sha_file(Path(folder)/'plan.json'),prior_test_exposure=True,
        representation=plan['input_text_policy'],model_key=model_key(plan),
        predictions_sha256=sha_file(predictions_path))
    with output.open('x') as f:json.dump(report,f,indent=2,allow_nan=False)
    return {'evaluation_saved':str(output)}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['status','embed','export','evaluate'])
    p.add_argument('--plan',type=Path,required=True,help='directory containing plan.json')
    p.add_argument('--authorization',type=Path);p.add_argument('--limit',type=int,default=0)
    p.add_argument('--batch-size',type=int,default=2);p.add_argument('--output',type=Path)
    a=p.parse_args()
    if a.command=='status':result=status(a.plan)
    elif a.command=='embed':result=embed(a.plan,a.authorization,a.limit,a.batch_size)
    elif a.command=='export':
        if a.output is None:p.error('--output required')
        result=export(a.plan,a.output)
    else:
        if a.output is None:p.error('--output required')
        result=evaluate(a.plan,a.authorization,a.output)
    print(json.dumps(result,indent=2))
