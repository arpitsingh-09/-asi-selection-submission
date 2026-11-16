"""Deterministic metadata-only candidate/config locks. No prediction execution."""
import argparse
import hashlib
import json
from pathlib import Path
from .evaluation import TESTS,READOUTS,CONTROLS,SEED,DRAWS,MARGIN

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def freeze(root,out):
    root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=False)
    source=root/'M/data/manifests_v2/test.jsonl'
    rs=[json.loads(x) for x in source.read_text().splitlines() if x.strip()]
    candidates=[{'question_id':r['question_id'],'paper_id':r['paper_id'],'published':r['published'],
        'available_at':r['available_at'],'source_dataset':r['source_dataset'],
        'source_manifest_sha256':sha(source),'record_sha256':hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest(),
        'eligible':False,'blocker':'Missing verified question intent/availability, original input/control annotations and core-specific labels.'} for r in sorted(rs,key=lambda r:r['question_id'])]
    with (out/'heldout_candidates.jsonl').open('x') as f:
        for r in candidates:f.write(json.dumps(r,sort_keys=True)+'\n')
    for test in TESTS:dump(out/(test+'_test_list.json'),{'test':test,'status':'CANDIDATES_ONLY_BLOCKED','question_ids':[r['question_id'] for r in candidates],'manifest_sha256':sha(out/'heldout_candidates.jsonl'),'heldout_evaluated':False})
    files=sorted((root/'M').glob('*.py'))+[root/'E5/diversity.py',root/'E2/novelty.py',root/'E2/task3_novelty.py',root/'M/PREREG.md']
    config={'schema':'M-core-lock-v1','encoder':'E5 fixed 512-bin lexical hashing','quality_models':None,'semantic_baseline_cache':None,
        'feature_schema':'shared-phi-v1; q/meanR/residual/four-facets/seven-scalars','max_literature':128,'retrieval_k':3,
        'alpha_grid':[.1,1.,10.],'quality_fit_cap':128,'identity_threshold':.65,'controls':CONTROLS,'readouts':READOUTS,
        'seed':SEED,'bootstrap_draws':DRAWS,'improvement_margin':MARGIN,'real_execution_enabled':False,
        'train_end_exclusive':'2024-01-01','validation_end_exclusive':'2025-01-01','test_start':'2025-07-01',
        'file_hashes':{str(p.relative_to(root)):sha(p) for p in files},
        'partition_hashes':{s:sha(root/f'M/data/manifests_v2/{s}.jsonl') for s in ('train','validation','test')}}
    dump(out/'config.json',config)
    dump(out/'SHA256SUMS.json',{p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()})
    return {'candidate_count':len(candidates),'eligible_count':0,'real_evaluations':0}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--out',required=True);a=p.parse_args();print(json.dumps(freeze(a.root,a.out)))
