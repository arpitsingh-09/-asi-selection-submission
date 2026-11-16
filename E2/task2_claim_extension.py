"""Gated N/custom-only evaluation of the frozen 52-paper Task 2 extension.
No model imports, vector writes, re-ranking, or recomputation of Y/density.
"""
import os
for _k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_k]='1'
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import types
import numpy as np
from claim_sidecar import Overlay,status as sidecar_status
from cached_extensions import text
from task2_cache_extension import sha,rows,select_fixed,summarize as paired_bootstrap

ROOT=Path(__file__).resolve().parent
PROTOCOL=ROOT/'TASK2_N_CUSTOM_52_PROTOCOL.md'
MANIFEST=ROOT/'analysis/task2_claim_extension_inputs_v1.json'
CONDITIONS=('near','far','older','newer')


def claim_scores(claim_vectors,pool_vectors,saved_y):
    c=np.asarray(claim_vectors,dtype=np.float32);p=np.asarray(pool_vectors,dtype=np.float32)
    if c.ndim!=2 or p.ndim!=2 or c.shape[1:]!=(768,) or p.shape[1:]!=(768,) or not len(c) or not len(p):
        raise ValueError('nonempty 768-dimensional claim/reference matrices required')
    if not np.isfinite(c).all() or not np.isfinite(p).all() or not np.isfinite(saved_y):
        raise ValueError('nonfinite score input')
    if not np.allclose(np.linalg.norm(c,axis=1),1,atol=1e-4) or not np.allclose(np.linalg.norm(p,axis=1),1,atol=1e-4):
        raise ValueError('unit vectors required')
    if not 0<=saved_y<=2:raise ValueError('saved Y outside cosine-distance range')
    similarity=np.clip(np.einsum('ik,jk->ij',c,p),-1,1)
    n=float(1-np.max(similarity,axis=1).mean())
    return {'N':n,'yours':.75*saved_y+.25*n}


def summarize(records,replicates=10000):
    # Reuse the exact bounded paired-bootstrap implementation with private labels;
    # do not mutate the original module globals or recompute either earlier score.
    scope=dict(paired_bootstrap.__globals__);scope['MEASURES']=('N','yours')
    fn=types.FunctionType(paired_bootstrap.__code__,scope,paired_bootstrap.__name__,paired_bootstrap.__defaults__)
    return fn(records,replicates)


def unique(records,label):
    byid={r['paper_id']:r for r in records}
    if len(byid)!=len(records):raise ValueError('duplicate '+label+' IDs')
    return byid


def validate_fixed(cohort,pools,saved,claims,raw,manifest_pools,expected_count=52):
    bycohort=unique(cohort,'cohort');bypool=unique(pools,'pool');byresult=unique(saved,'result');byclaims=unique(claims,'claim')
    if len(cohort)!=expected_count or set(bycohort)!=set(bypool) or set(bycohort)!=set(byresult):
        raise ValueError('exact frozen cohort/pool/result coverage required')
    specs=[]
    for r in cohort:
        pid=r['paper_id'];fixed=bypool[pid];old=byresult[pid]
        if pid not in byclaims or not 4<=len(byclaims[pid]['claims'])<=10:raise ValueError('count-ineligible focal')
        if fixed['pool']!=r['pool'] or old['pool']!=r['pool'] or byclaims[pid]['pool']!=r['pool'] or fixed['cutoff']!=r['cutoff']:
            raise ValueError('pool/cutoff source mismatch')
        _,k=select_fixed(r,raw,manifest_pools[r['pool']])
        if old['k']!=k or set(fixed['conditions'])!=set(CONDITIONS) or set(old['scores'])!=set(CONDITIONS):
            raise ValueError('saved condition/pair-size mismatch')
        for name,ids in fixed['conditions'].items():
            if len(ids)!=k or len(set(ids))!=k or not set(ids)<=set(r['cached_reference_ids']):
                raise ValueError('condition membership mismatch')
        for a,b in (('near','far'),('older','newer')):
            if set(fixed['conditions'][a])&set(fixed['conditions'][b]):raise ValueError('contrast pools overlap')
        specs.append({'paper_id':pid,'pool':r['pool'],'cutoff':r['cutoff'],
            'conditions':fixed['conditions'],'claims':[c['claim'].strip() for c in byclaims[pid]['claims']],
            'saved_Y':{name:old['scores'][name]['Y'] for name in CONDITIONS},'k':k})
    return specs


def compute_records(specs,overlay):
    """Resolve every vector before the first numerical score, fail on any gap."""
    ids=[s['paper_id'] for s in specs]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate evaluated focal')
    needed=set()
    for s in specs:
        needed.update(s['claims'])
        for texts in s['condition_texts'].values():needed.update(texts)
    vectors={t:overlay.get(t) for t in sorted(needed)}
    results=[]
    for s in specs:
        c=np.stack([vectors[t] for t in s['claims']])
        scores={name:claim_scores(c,np.stack([vectors[t] for t in s['condition_texts'][name]]),s['saved_Y'][name]) for name in CONDITIONS}
        results.append({'paper_id':s['paper_id'],'pool':s['pool'],'k':s['k'],
            'scores':scores,'reused_Y':s['saved_Y']})
    return results


def load_inputs(manifest_path=MANIFEST):
    manifest_path=Path(manifest_path).resolve();m=json.loads(manifest_path.read_text())
    if m.get('format')!=1 or m.get('cohort_count')!=52:raise ValueError('unsupported frozen claim extension')
    if m.get('numpy_version')!=np.__version__:raise ValueError('frozen NumPy version changed')
    for path,h in {**m['source_sha256'],**m['code_sha256']}.items():
        if sha(path)!=h:raise ValueError('frozen evaluation binding changed: '+path)
    cohort=json.loads(Path(m['cohort_path']).read_text())['records']
    if [r['paper_id'] for r in cohort]!=m['focal_ids']:raise ValueError('frozen focal order changed')
    prior=rows(m['previous_241_path'])
    if len(prior)!=241 or len(unique(prior,'prior result'))!=241 or set(m['focal_ids'])&{r['paper_id'] for r in prior}:
        raise ValueError('previous/new cohort overlap or mismatch')
    raw={}
    for r in rows(m['raw_path']):
        if r['paper_id'] in raw and any(r[k]!=raw[r['paper_id']][k] for k in ('title','abstract','published')):
            raise ValueError('conflicting raw source duplicate')
        raw[r['paper_id']]=r
    pools={}
    with Path(m['pool_manifest_path']).open() as f:
        for r in csv.DictReader(f):pools.setdefault(r['pool'],set()).add(r['paper_id'])
    specs=validate_fixed(cohort,rows(m['fixed_pools_path']),rows(m['saved_Y_density_path']),rows(m['claims_path']),raw,pools)
    for s in specs:s['condition_texts']={name:[text(raw[pid]) for pid in ids] for name,ids in s['conditions'].items()}
    return m,specs


def check_committed():
    rels=['E2/TASK2_N_CUSTOM_52_PROTOCOL.md','E2/analysis/task2_claim_extension_inputs_v1.json',
          'E2/task2_claim_extension.py','E2/tests/test_task2_claim_extension.py']
    for rel in rels:
        data=subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT.parent)
        if hashlib.sha256(data).hexdigest()!=sha(ROOT.parent/rel):raise ValueError('N/custom protocol/code must be committed unchanged')
    return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT.parent,text=True).strip()


def authorize(manifest_path,m,auth_path):
    if auth_path is None:raise ValueError('future explicit evaluation authorization required')
    a=json.loads(Path(auth_path).read_text())
    if a.get('authorize_evaluation') is not True or not isinstance(a.get('authorization_source'),str) or not a['authorization_source'].strip():
        raise ValueError('N/custom evaluation not authorized')
    if a.get('manifest_sha256')!=sha(manifest_path) or a.get('protocol_sha256')!=sha(PROTOCOL):
        raise ValueError('evaluation authorization binding mismatch')
    database=Path(m['sidecar_folder'])/'claim_vectors_v1.sqlite3'
    if not database.exists() or a.get('sidecar_sha256')!=sha(database):raise ValueError('complete sidecar authorization missing/changed')
    return a,database


def status(manifest_path=MANIFEST):
    m,_=load_inputs(manifest_path)
    readiness=sidecar_status(m['sidecar_folder'])
    return {'cohort_focals':52,'required_claim_vectors':93,'complete_claim_vectors':readiness['complete_vectors'],
            'missing_claim_vectors':readiness['missing_vectors'],'authorize_evaluation':False,
            'real_scores_computed':0,'model_loaded':False}


def evaluate(output,auth_path=None,manifest_path=MANIFEST):
    if Path(manifest_path).resolve()!=MANIFEST.resolve():raise ValueError('only the preregistered manifest may evaluate')
    if Path(output).exists():raise FileExistsError('evaluation output already exists')
    commit=check_committed()
    m,specs=load_inputs(manifest_path)
    a,database=authorize(manifest_path,m,auth_path)
    readiness=sidecar_status(m['sidecar_folder'])
    if readiness['complete_vectors']!=93:raise ValueError('all 93 claim vectors required before scoring')
    # No output files or score calculation until all required inputs are resolved.
    with Overlay(m['sidecar_folder']) as overlay:records=compute_records(specs,overlay)
    report={'protocol_commit':commit,'protocol_sha256':sha(PROTOCOL),'manifest_sha256':sha(manifest_path),
        'sidecar_sha256':sha(database),'source_sha256':m['source_sha256'],
        'new_focals':52,'new_per_pool':dict(Counter(r['pool'] for r in records)),
        'new_rates':summarize(records),'previous_N_custom_focals':241,'N_custom_focals_after_this_run':293,
        'previous_results_recomputed':False,'Y_density_recomputed':False,'new_embeddings_generated':0,
        'bootstrap':{'unit':'distinct focal paper','replicates':10000,'seed':20261113,'interval':'95% percentile'},
        'scope':'New N/yours stage only; no pooled numerical N/custom estimate across claim-extraction stages.',
        'authorization_source':a['authorization_source']}
    # A completed future run must not race a vector writer or changed source.
    for path,h in {**m['source_sha256'],**m['code_sha256']}.items():
        if sha(path)!=h:raise ValueError('input changed during evaluation')
    if sha(database)!=a['sidecar_sha256']:raise ValueError('sidecar changed during evaluation')
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    for name,obj in [('results.jsonl',records),('summary.json',report)]:
        with (output/name).open('x') as f:
            if name.endswith('.jsonl'):
                for r in obj:f.write(json.dumps(r,allow_nan=False)+'\n')
            else:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('status');a.add_argument('--manifest',type=Path,default=MANIFEST)
    a=sub.add_parser('evaluate');a.add_argument('--manifest',type=Path,default=MANIFEST)
    a.add_argument('--authorization',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    result=status(a.manifest) if a.command=='status' else evaluate(a.output,a.authorization,a.manifest)
    print(json.dumps(result,indent=2,allow_nan=False))
