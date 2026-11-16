"""Prospectively frozen, bounded, cache-only Y/RND development extension."""
import os
for _k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_k]='1'
import argparse
from collections import Counter,defaultdict
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np
from cached_extensions import Cache,MODEL,text,norm
from manipulation_extensions import parse,select_pools

ROOT=Path(__file__).resolve().parent
PROTOCOL=ROOT/'TASK2_EXTENSION_52_PROTOCOL.md'
COHORT=ROOT/'analysis/task2_extension_52_cohort_v1.json'
SEED=20261113
MEASURES=('Y','density')


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def rows(p):
    with Path(p).open() as f:return [json.loads(line) for line in f if line.strip()]


def score(idea,pool):
    """Exact float32 conventions of novelty._rnd_score; no model imports.
    P=100/Q=50 capped to n/n-1, stable sorting, self excluded.
    """
    n=len(pool)
    if n<2:raise ValueError('RND requires two references')
    y=float(1-np.clip(np.einsum('ij,j->i',pool,idea),-1,1).max())
    # Original RND uses its own row-matrix einsum, preserve that operation order.
    query=1-np.clip(np.einsum('ik,jk->ij',idea.reshape(1,-1),pool),-1,1)[0]
    p=min(100,n);q=min(50,n-1)
    order=np.argsort(query,kind='stable')
    density=float(np.mean(query[order[:q]]))
    pairwise=1-np.clip(np.einsum('ik,jk->ij',pool,pool),-1,1)
    neighbors=[]
    for i in order[:p]:
        d=pairwise[i].copy();d[i]=np.inf
        neighbors.append(float(np.mean(d[np.argsort(d,kind='stable')[:q]])))
    return {'Y':y,'density':float(100*np.mean(np.asarray(neighbors,dtype=np.float64)<=density))}


def summarize(records,replicates=10000):
    ids=[r['paper_id'] for r in records]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate evaluated focal')
    rng=np.random.default_rng(SEED);result=[]
    for left,right in [('near','far'),('newer','older')]:
        for m in MEASURES:
            d=np.asarray([r['scores'][left][m]-r['scores'][right][m] for r in records])
            if not len(d) or not np.isfinite(d).all():raise ValueError('missing/nonfinite contrast')
            passed=d < -1e-8
            # Bound bootstrap memory and keep one index stream per contrast.
            rates=[];means=[]
            for start in range(0,replicates,250):
                ix=rng.integers(0,len(d),(min(250,replicates-start),len(d)))
                rates.extend(passed[ix].mean(1));means.extend(d[ix].mean(1))
            result.append({'left':left,'right':right,'measure':m,'valid':len(d),
                'passes':int(passed.sum()),'ties':int((np.abs(d)<=1e-8).sum()),
                'pass_rate':float(passed.mean()),'pass_rate_ci95':np.percentile(rates,[2.5,97.5]).tolist(),
                'mean_difference':float(d.mean()),'difference_ci95':np.percentile(means,[2.5,97.5]).tolist()})
    return result


def check_commit():
    rels=['E2/TASK2_EXTENSION_52_PROTOCOL.md','E2/analysis/task2_extension_52_cohort_v1.json',
          'E2/task2_cache_extension.py','E2/tests/test_task2_cache_extension.py']
    for rel in rels:
        committed=subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT.parent)
        if hashlib.sha256(committed).hexdigest()!=sha(ROOT.parent/rel):
            raise ValueError('preregistration/implementation must be committed unchanged: '+rel)
    return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT.parent,text=True).strip()


def select_fixed(record,raw,manifest_ids):
    pid=record['paper_id'];paper=raw[pid];ids=record['cached_reference_ids']
    if len(ids)!=len(set(ids)) or len(ids)!=record['eligible_cached_prior_count']:
        raise ValueError('duplicate/misaligned reference IDs')
    if record['cutoff']!=paper['published']:raise ValueError('cutoff binding')
    for qid in ids:
        q=raw[qid]
        if qid not in manifest_ids or qid==pid or parse(q['published'])>=parse(paper['published']) or norm(q['abstract'])==norm(paper['abstract']):
            raise ValueError('reference eligibility failure')
    k=min(100,len(ids)//2)
    if k<2 or k!=record['pair_size']:raise ValueError('pair size mismatch')
    return [raw[qid] for qid in ids],k


def run(output):
    commit=check_commit() # Before vector reads, ranking, scoring or bootstrap.
    cohort=json.loads(COHORT.read_text())
    before=cohort['source_sha256']
    for path,fingerprint in before.items():
        if sha(path)!=fingerprint:raise ValueError('frozen source changed: '+path)
    frozen=cohort['records']
    if len(frozen)!=52 or len({r['paper_id'] for r in frozen})!=52:raise ValueError('exact 52 required')
    readiness=json.loads(Path(cohort['readiness_path']).read_text())
    ready=[r for r in readiness['records'] if r['claim_independent_Y_density_ready']]
    if frozen!=ready:raise ValueError('readiness cohort changed')
    old=rows(ROOT/'analysis/cached_extensions_v1/results.jsonl')
    if len(old)!=241 or len({r['paper_id'] for r in old})!=241 or {r['paper_id'] for r in old}&{r['paper_id'] for r in frozen}:
        raise ValueError('old/new cohort coverage or overlap')
    raw={r['paper_id']:r for r in rows(ROOT/'data/raw_papers.jsonl')}
    claims={r['paper_id']:r for r in rows(ROOT/'analysis/claim_completion_v2/claims_future.jsonl')}
    pools=defaultdict(set)
    with (ROOT/'data/pool_manifest.csv').open() as f:
        for r in csv.DictReader(f):pools[r['pool']].add(r['paper_id'])
    output.mkdir(parents=True,exist_ok=False)
    cache=Cache(ROOT/'data/novelty_embeddings.sqlite3');results=[];plans=[]
    try:
        for r in frozen:
            pid=r['paper_id']
            if not 4<=len(claims[pid]['claims'])<=10:raise ValueError('claim eligibility changed')
            candidates,k=select_fixed(r,raw,pools[r['pool']])
            idea=cache.get(text(raw[pid]));pv=np.stack([cache.get(text(q)) for q in candidates])
            similarity=np.einsum('ij,j->i',pv,idea)
            chosen=select_pools(candidates,pid,r['cutoff'],{q['paper_id']:float(s) for q,s in zip(candidates,similarity)},k)
            lookup={q['paper_id']:i for i,q in enumerate(candidates)}
            for a,b in [('near','far'),('older','newer')]:
                if set(chosen[a])&set(chosen[b]) or len(chosen[a])!=len(chosen[b]):raise ValueError('pool contrast invariant')
            scores={condition:score(idea,pv[[lookup[q] for q in ids]]) for condition,ids in chosen.items()}
            results.append({'paper_id':pid,'pool':r['pool'],'k':k,'eligible_cached':len(candidates),'scores':scores})
            plans.append({'paper_id':pid,'pool':r['pool'],'cutoff':r['cutoff'],'conditions':chosen})
        # Exact-deduplicated future N/yours vector requirements. No cache writes.
        missing={};blocked=[]
        candidate_ids={r['paper_id'] for r in readiness['records']}
        ready_ids={r['paper_id'] for r in frozen}
        for pid in sorted(candidate_ids):
            for i,c in enumerate(claims[pid]['claims']):
                s=c['claim'].strip()
                try:cache.get(s);continue
                except KeyError:pass
                h=hashlib.sha256(s.encode()).hexdigest()
                request=missing.setdefault(h,{'text_sha256':h,'text':s,'model_id':MODEL,'uses':[]})
                request['uses'].append({'paper_id':pid,'claim_index':i,'currently_pool_ready':pid in ready_ids})
        requests=[v for _,v in sorted(missing.items()) if any(u['currently_pool_ready'] for u in v['uses'])]
        blocked=[v for _,v in sorted(missing.items()) if not any(u['currently_pool_ready'] for u in v['uses'])]
    finally:cache.close()
    # Same Y/density formulas, representation, pool construction and pass criterion;
    # descriptive aggregation only, with separate stage summaries retained.
    prior_summary=json.loads((ROOT/'analysis/cached_extensions_v1/summary.json').read_text())
    if prior_summary['protocol_sha256']!=sha(ROOT/'CONTINUATION_PROTOCOL.md') or prior_summary['records']!=241:
        raise ValueError('prior-method binding mismatch')
    combined=old+results
    report={'protocol_commit':commit,'protocol_sha256':sha(PROTOCOL),'cohort_sha256':sha(COHORT),
        'evaluated_new_focals':len(results),'previous_focals':241,'combined_Y_density_focals':len(combined),
        'new_per_pool':dict(Counter(r['pool'] for r in results)),
        'bootstrap':{'replicates':10000,'seed':SEED,'unit':'distinct focal paper','method':'paired-paper percentile 95%'},
        'new_rates':summarize(results),
        'previous_Y_density_rates':[r for r in prior_summary['rates'] if r['measure'] in MEASURES],
        'combined_descriptive_rates':summarize(combined),
        'combined_scope':'Y/density only. Compatible formulas, exact text/model, chronological pools, pair sizes, tie rule; heterogeneous selection stages. Descriptive pooled development results, not one prospectively registered cohort.',
        'N_yours_focals_evaluated':241,'new_embeddings_generated':0,'model_loaded':False,
        'minimum_missing_unique_claim_vectors_for_ready_52':len(requests),
        'additional_unique_claim_vectors_for_pool_blocked_focal':len(blocked),
        'source_sha256':before,
        'limitations':['Cohort selected for claim count and cache availability after earlier study exposure.',
            'Near selection uses the same geometry as scoring; not independent semantic validation.',
            'Temporal decrease is an empirical hypothesis, not a universal axiom.',
            'Six claim-incomplete and one insufficient-prior-cache focal remain excluded.',
            'Missing claim embeddings prevent new N/yours; planting/paraphrase require modified-paper vectors.']}
    if any(sha(p)!=h for p,h in before.items()):raise ValueError('protected source changed during evaluation')
    report['protected_source_hashes_unchanged']=True
    def dump(name,obj): (output/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
    def dump_rows(name,items): (output/name).write_text(''.join(json.dumps(r,allow_nan=False)+'\n' for r in items))
    dump_rows('results.jsonl',results);dump_rows('pool_plan.jsonl',plans)
    dump_rows('missing_claim_vectors.jsonl',requests);dump_rows('pool_blocked_claim_vectors.jsonl',blocked)
    dump('summary.json',report)
    print(json.dumps({k:report[k] for k in ('evaluated_new_focals','combined_Y_density_focals','minimum_missing_unique_claim_vectors_for_ready_52','additional_unique_claim_vectors_for_pool_blocked_focal')}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output)
