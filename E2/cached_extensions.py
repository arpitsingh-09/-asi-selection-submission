"""Frozen cache-only extension evaluator and nearest-paper plan writer.
Never loads a model, writes a cache, or changes the original scoring artifacts.
"""
import argparse
import csv
import hashlib
import json
import sqlite3
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from human_check import MEASURES, SEED
from manipulation_extensions import parse,select_pools,plant_nearest

MODEL='specter2_base+proximity-adapter+cls-v1'

def text(p):return p['title'].strip()+'\n\n'+p['abstract'].strip()
def norm(s):return ' '.join(s.casefold().split())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class Cache:
    def __init__(self,path):
        self.connection=sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True)
        self.memory={}
    def get(self,s):
        if s not in self.memory:
            h=hashlib.sha256(s.encode()).hexdigest()
            r=self.connection.execute('SELECT text_value,vector_json FROM embeddings WHERE model_id=? AND text_hash=?',(MODEL,h)).fetchone()
            if r is None:raise KeyError(h)
            if r[0]!=s:raise ValueError('cache text/hash binding mismatch')
            v=np.asarray(json.loads(r[1]),dtype=np.float32)
            if v.shape!=(768,) or not np.isfinite(v).all() or not np.isclose(np.linalg.norm(v),1,atol=1e-4):
                raise ValueError('invalid cached vector')
            self.memory[s]=v
        return self.memory[s]
    def close(self):self.connection.close()

def calculate(idea,claims,pool):
    """Same formulas as novelty.score; RND helper has no model/cache side effects."""
    from novelty import _rnd_score
    y=float(1-np.clip(np.einsum('ij,j->i',pool,idea),-1,1).max())
    n=float(1-np.clip(np.einsum('ik,jk->ij',claims,pool),-1,1).max(axis=1).mean())
    return {'Y':y,'N':n,'yours':.75*y+.25*n,'density':_rnd_score(idea,pool)}

def evaluate_paraphrase(idea, claims, prior_vectors, candidate_text, cache, review_status):
    """Future cache-only exact baseline pairing; missing vectors stay explicit.

    review_status is the recorded source status, never a new human judgment.
    Call only after a protocol/authorization check by the invoking workflow.
    """
    if review_status!='accepted':
        return {'status':'blocked_missing_meaning_preservation_review'}
    try: vector=cache.get(candidate_text)
    except KeyError as error:
        return {'status':'blocked_missing_candidate_embedding','text_hash':str(error)}
    baseline=calculate(idea,claims,prior_vectors)
    manipulated=calculate(idea,claims,np.vstack([prior_vectors,vector]))
    return {'status':'ok','baseline':baseline,'paraphrased_copy':manipulated,
        'difference':{m:manipulated[m]-baseline[m] for m in MEASURES}}

def summarize(records,replicates=10000):
    rng=np.random.default_rng(SEED);rows=[]
    for left,right in [('near','far'),('newer','older')]:
        for m in MEASURES:
            d=np.array([r['scores'][left][m]-r['scores'][right][m] for r in records])
            if not len(d):continue
            ix=rng.integers(0,len(d),(replicates,len(d)));passes=d<-1e-8
            rows.append({'left':left,'right':right,'measure':m,'valid':len(d),'passes':int(passes.sum()),
                'ties':int((np.abs(d)<=1e-8).sum()),'pass_rate':float(passes.mean()),
                'pass_rate_ci95':np.percentile(passes[ix].mean(1),[2.5,97.5]).tolist(),
                'mean_difference':float(d.mean()),'difference_ci95':np.percentile(d[ix].mean(1),[2.5,97.5]).tolist()})
    return rows

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parent;data=root/'data';protocol=root/'CONTINUATION_PROTOCOL.md'
    # Require the exact working protocol to have been committed before computation.
    import subprocess
    committed=subprocess.check_output(['git','show','HEAD:E2/CONTINUATION_PROTOCOL.md'],cwd=root).decode()
    if committed!=protocol.read_text():raise ValueError('protocol must be committed unchanged')
    files=['claims_v8_selected.jsonl','pool_manifest.csv','raw_papers.jsonl','novelty_embeddings.sqlite3',
           'scoring_results.jsonl','scoring_results.matmul_pilot.jsonl']
    before={n:sha(data/n) for n in files}
    raw={r['paper_id']:r for r in map(json.loads,(data/'raw_papers.jsonl').read_text().splitlines())}
    focals=list(map(json.loads,(data/'claims_v8_selected.jsonl').read_text().splitlines()))
    pools=defaultdict(set)
    with (data/'pool_manifest.csv').open() as f:
        for r in csv.DictReader(f):pools[r['pool']].add(r['paper_id'])
    a.output.mkdir(parents=True,exist_ok=False)
    cache=Cache(data/'novelty_embeddings.sqlite3');records=[];excluded=[];plans=[];nearest=[]
    try:
        for f in focals:
            pid=f['paper_id'];paper=raw[pid];claims=[c['claim'].strip() for c in f['claims']]
            if not 4<=len(claims)<=10:
                excluded.append({'paper_id':pid,'pool':f['pool'],'reason':'original_claim_count_outside_4_10'});continue
            candidates=[];missing=[]
            for candidate_id in sorted(pools[f['pool']]):
                q=raw[candidate_id]
                if candidate_id==pid or parse(q['published'])>=parse(paper['published']) or norm(q['abstract'])==norm(paper['abstract']):continue
                try:cache.get(text(q))
                except KeyError:missing.append(candidate_id);continue
                candidates.append(q)
            k=min(100,len(candidates)//2)
            if k<2:
                excluded.append({'paper_id':pid,'pool':f['pool'],'reason':'fewer_than_four_cached_prior_papers','eligible_cached':len(candidates)});continue
            try:
                idea=cache.get(text(paper)); cv=np.stack([cache.get(s) for s in claims])
            except KeyError as e:
                excluded.append({'paper_id':pid,'pool':f['pool'],'reason':'missing_focal_or_claim_embedding','hash':str(e)});continue
            pv=np.stack([cache.get(text(q)) for q in candidates]); similarities=np.einsum('ij,j->i',pv,idea)
            selected=select_pools(candidates,pid,paper['published'],{q['paper_id']:float(v) for q,v in zip(candidates,similarities)},k)
            lookup={q['paper_id']:i for i,q in enumerate(candidates)}
            scores={name:calculate(idea,cv,pv[[lookup[x] for x in ids]]) for name,ids in selected.items()}
            records.append({'paper_id':pid,'pool':f['pool'],'k':k,'eligible_cached':len(candidates),'missing_cached_prior_ids':missing,'scores':scores})
            plans.append({'paper_id':pid,'pool':f['pool'],'cutoff':paper['published'],'claim_source':'data/claims_v8_selected.jsonl','conditions':selected})
            claim_sim=np.einsum('ik,jk->ij',cv,pv)
            for percent in (25,50,75,100):
                replacements,mapping=plant_nearest(candidates,claims,claim_sim,percent,pid,paper['published'])
                ids=[mapping.get(q['paper_id'],q['paper_id']) for q in candidates]
                if len(ids)!=len(set(ids)) or set(mapping)&set(ids):raise ValueError('replacement invariant failed')
                nearest.append({'paper_id':pid,'pool':f['pool'],'cutoff':paper['published'],'percent':percent,
                    'pool_ids':ids,'replacement_map':mapping,'synthetic_papers':replacements,
                    'status':'planned_not_scored_modified_paper_embeddings_missing'})
        paraphrases=[]
        for r in map(json.loads,(data/'paraphrase_pilot5_v33.jsonl').read_text().splitlines()):
            try:cache.get(r['candidate_title'].strip()+'\n\n'+r['candidate_abstract'].strip());available=True
            except KeyError:available=False
            paraphrases.append({'paper_id':r['paper_id'],'pool':r['pool'],'candidate_title':r['candidate_title'],
                'candidate_abstract':r['candidate_abstract'],'source':'data/paraphrase_pilot5_v33.jsonl',
                'recorded_validation_status':r.get('manual_validation_status'),
                'original_scoring_authorized':r.get('scoring_authorized'),
                'embedding_available':available,'status':'blocked_missing_candidate_embedding' if not available else 'not_scored_pending_paired_evaluation','source_status_is_not_new_human_judgment':True})
    finally:cache.close()
    after={n:sha(data/n) for n in files}
    if before!=after:raise RuntimeError('protected source changed')
    def jsonl(name,items):
        (a.output/name).write_text(''.join(json.dumps(r,allow_nan=False)+'\n' for r in items))
    jsonl('results.jsonl',records);jsonl('pool_plan.jsonl',plans);jsonl('nearest_planting_plan.jsonl',nearest)
    jsonl('paraphrase_plan.jsonl',paraphrases)
    summary={'protocol_sha256':sha(protocol),'source_sha256':before,'source_hashes_unchanged':before==after,
        'records':len(records),'per_pool':dict(Counter(r['pool'] for r in records)),'excluded':excluded,
        'seed':SEED,'replicates':10000,'rates':summarize(records),'nearest_plans':len(nearest),
        'paraphrase_candidates':len(paraphrases),'paraphrase_cached':sum(r['embedding_available'] for r in paraphrases),
        'limitations':['Development results, not held-out human-check evaluation',
        'Original short claim records excluded; recovered candidates not used',
        'Available cached prior papers only; equal-size pairs may have k<100',
        'Near pool selected with same encoder as scores; this is a controlled response check',
        'No scored nearest planting or paraphrase; modified embeddings unavailable']}
    (a.output/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    print('Cached evaluation records:',len(records),'nearest plans:',len(nearest),'excluded:',len(excluded))

if __name__=='__main__':main()
