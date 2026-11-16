"""Summarize saved experiments and local source metadata; never performs inference."""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from human_check import normalize, resolve, historical, MEASURES, SEED

ROOT=Path(__file__).resolve().parent

def rows(path):
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--benchmark',type=Path,required=True)
    parser.add_argument('--history',type=Path,required=True)
    args=parser.parse_args()
    import pyarrow.parquet as pq
    bench=[normalize(r) for r in pq.read_table(args.benchmark).to_pylist()]
    out=ROOT/'analysis'; out.mkdir(exist_ok=True)
    def save(name,data):
        (out/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    originals={n:hashlib.sha256((ROOT/'data'/n).read_bytes()).hexdigest()
               for n in ('scoring_results.jsonl','scoring_results.matmul_pilot.jsonl')}
    history,excluded=historical(args.history,bench)
    mappings=resolve(bench,[])
    save('benchmark_audit.json',{'source':str(args.benchmark),'sha256':hashlib.sha256(args.benchmark.read_bytes()).hexdigest(),
         'records':len(bench),'labels':dict(Counter(r['label'] for r in bench)),
         'schema':'cached parquet has top-level metadata fields; normalizer also validates nested metadata',
         'mappings':mappings,'publication_dates_available':sum(bool(r.get('published')) for r in bench),
         'post_cutoff_status':'UNVERIFIED: no item-level dates or documented E2 encoder cutoff',
         'historical_eligible_after_exclusions':dict(Counter(r['year'] for r in history)),
         'excluded_history':excluded,
         'task3_blockers':['No saved benchmark novelty predictions for four measures',
           'No provenance-verified abstract-only historical/test embedding matrices',
           'No verified item-level post-cutoff publication dates',
           'TASK3_PROTOCOL is retrospective, not prospective preregistration; no held-out evaluation executed']})
    with (out/'historical_manifest.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=['forum_id','year','title','mean_rating','review_count'],lineterminator='\n');w.writeheader()
        w.writerows({k:r[k] for k in w.fieldnames} for r in history)
    pools=list(csv.DictReader((ROOT/'data/pool_manifest.csv').open()))
    focals=list(csv.DictReader((ROOT/'data/focal_papers.csv').open()))
    claims=rows(ROOT/'data/claims_v8_selected.jsonl'); plan=rows(ROOT/'data/manipulation_plan.jsonl')
    scores=rows(ROOT/'data/scoring_results.jsonl'); byid={}
    for r in scores:
        if r['case_id'] in byid:raise ValueError('duplicate score case')
        byid[r['case_id']]=r
    groups=defaultdict(dict)
    for p in plan:
        groups[(p['pool'],p['focal_paper_id'])][p['manipulation']]=p
    contrasts=[('exact_copy','baseline','strict_decrease')]
    contrasts += [(f'coverage_{p}','baseline','nonincrease') for p in (25,50,75,100)]
    contrasts += [(f'coverage_{b}',f'coverage_{a}','nonincrease') for a,b in [(25,50),(50,75),(75,100)]]
    contrasts += [('concentrated','distributed','strict_decrease')]
    rates=[]; rng=np.random.default_rng(SEED)
    for left,right,rule in contrasts:
        for measure in MEASURES:
            successes=[]; missing=0
            for g in groups.values():
                pair=[byid.get(g.get(k,{}).get('case_id')) for k in (left,right)]
                if any(r is None or r['status']!='ok' or not np.isfinite(r['scores'][measure]) for r in pair):missing+=1;continue
                a,b=[r['scores'][measure] for r in pair]
                successes.append(a<=b+1e-8 if rule=='nonincrease' else a<b-1e-8)
            v=np.array(successes,float)
            ci=np.percentile(rng.choice(v,(10000,len(v))).mean(1),[2.5,97.5]).tolist() if len(v) else None
            rates.append({'condition':left,'reference':right,'measure':measure,'criterion':rule,
                'passes':int(v.sum()),'valid':len(v),'missing_or_invalid':missing,'rate':float(v.mean()) if len(v) else None,
                'ci95':ci,'interpretation':'descriptive lower-concentration rate; original N equality prediction was incorrect' if left=='concentrated' else 'directional pass rate'})
    save('saved_results_report.json',{'scoring_sha256':originals,'status_counts':dict(Counter(r['status'] for r in scores)),
        'unique_pool_sizes':{p:len({r['paper_id'] for r in pools if r['pool']==p}) for p in {r['pool'] for r in pools}},
        'focals_per_pool':dict(Counter(r['pool'] for r in focals)),
        'claim_counts':dict(Counter(len(r['claims']) for r in claims)),
        'conditions':dict(Counter(r['manipulation'] for r in plan)),
        'focal_in_pool_cases':sum(p['focal_paper_id'] in p['pool_ids'] for p in plan),
        'unique_focal_papers':len({p['focal_paper_id'] for p in plan}),
        'seed':SEED,'bootstrap_replicates':10000,'rates':rates,
        'limitations':['Paper-level bootstrap pooled across the three fixed subfields; no claim of independent corpus samples',
        'Strict comparisons use fixed numerical tolerance 1e-8; equality fails strict decrease',
        'Partial coverage inserts synthetic papers, not claims into nearest existing papers',
        'Paraphrased-copy, near/far and older/newer not scored; no pass rates available',
        'Original predictions retrospective relative to git; density concentration prediction was uncertain']})
    assert originals=={n:hashlib.sha256((ROOT/'data'/n).read_bytes()).hexdigest() for n in originals}
    print('Wrote offline reports; preserved scoring hashes:',originals)

if __name__=='__main__':main()
