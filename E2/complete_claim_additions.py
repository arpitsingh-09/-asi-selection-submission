"""Validate and materialize new Codex-extracted claims separately from scored inputs.
No model, embedding cache, numerical scorer or original artifact is written.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def records(path):
    with Path(path).open() as f:
        return [json.loads(line) for line in f if line.strip()]


def merge(prior, additions, raw, raw_path, raw_sha):
    updated=copy.deepcopy(prior)
    byid={r['paper_id']:r for r in updated}
    source={}
    for number,r in enumerate(raw,1):
        pid=r['paper_id']
        if pid in source:
            old=source[pid][1]
            if any(old[k]!=r[k] for k in ('title','abstract','published')):
                raise ValueError('conflicting source duplicate: '+pid)
        if pid not in source or (pid in byid and r.get('pool')==byid[pid]['pool']):
            source[pid]=(number,r)
    if len(byid)!=len(prior):
        raise ValueError('duplicate focal ID')
    review=[]
    for a in additions:
        pid=a['paper_id']
        if pid not in byid or pid not in source or not 0<len(a['claim'].strip()):
            raise ValueError('unknown paper/empty claim')
        row=byid[pid];line,paper=source[pid]
        evidence=a['evidence']
        if not evidence.strip() or evidence not in paper['abstract']:
            raise ValueError('nonexact evidence: '+pid)
        normalized=lambda s:' '.join(s.casefold().split())
        if normalized(a['claim']) in {normalized(c['claim']) for c in row['claims']}:
            raise ValueError('duplicate claim: '+pid)
        if len(row['claims'])>=4:
            raise ValueError('only minimal additions to short sets allowed: '+pid)
        if not a.get('distinctness_review') or a.get('human_review') is not False:
            raise ValueError('explicit AI distinctness review required')
        binding={**a,'source':str(raw_path),'source_line':line,
                 'source_sha256':raw_sha,
                 'abstract_sha256':hashlib.sha256(paper['abstract'].encode()).hexdigest(),
                 'decision':'retained_for_future_use_not_scored'}
        row['claims'].append({'claim':a['claim'],'evidence':evidence})
        row['claim_count']=len(row['claims'])
        row.setdefault('new_extraction_review',[]).append(binding)
        review.append(binding)
    for row in updated:
        if row['paper_id'] in {a['paper_id'] for a in additions}:
            original=next(r for r in prior if r['paper_id']==row['paper_id'])
            row['inherited_audit_before_new_extraction']={k:v for k,v in original.items() if k.startswith('audit_')}
            abstract=source[row['paper_id']][1]['abstract']
            row['audit_exact_evidence']=sum(c['evidence'] in abstract for c in row['claims'])
            row['audit_invalid_evidence']=len(row['claims'])-row['audit_exact_evidence']
            row['new_extraction_status']='AI_source_support_and_distinctness_review_only_not_human_validated'
    return updated,review


def main(output):
    root=Path(__file__).resolve().parent
    prior_path=root/'analysis/shared_excerpt_recovery_v1/claims_future.jsonl'
    raw_path=root/'data/raw_papers.jsonl'
    protected=[root/'data/scoring_results.jsonl',root/'data/scoring_results.matmul_pilot.jsonl',
               root/'data/claims_v8_selected.jsonl',prior_path,raw_path,
               root/'analysis/task3_execution_v1/plan.json']
    before={str(p):sha(p) for p in protected}
    prior=records(prior_path);raw=records(raw_path)
    additions_path=output/'additions.jsonl'
    additions=records(additions_path)
    if len(prior)!=300:raise ValueError('expected 300 focal records')
    updated,review=merge(prior,additions,raw,raw_path,before[str(raw_path)])
    short=lambda rows:sum(len(r['claims'])<4 for r in rows)
    summary={
        'new_claims':len(review),'papers_with_additions':len({a['paper_id'] for a in additions}),
        'prior_short_sets':short(prior),'remaining_short_sets':short(updated),
        'newly_count_complete_sets':short(prior)-short(updated),
        'future_sets_with_4_to_10':sum(4<=len(r['claims'])<=10 for r in updated),
        'all_new_excerpts_exact':all(a['evidence'] in next(r['abstract'] for r in raw if r['paper_id']==a['paper_id']) for a in additions),
        'human_review':False,'used_in_evaluation':False,'new_numerical_scores':0,
        'generation':'New extraction by Codex language-model assistant in this session; not recovered historical output.',
        'source_sha256':before,'additions_sha256':sha(additions_path),
        'implementation_sha256':sha(Path(__file__)),
        'limitations':['Count completion does not validate all inherited claims or establish independent human review.',
                       'Old semantic/audit limitations and original scored claims remain unchanged.',
                       'New claim vectors are not generated; no Task 2 or Task 3 scores are asserted.'],
    }
    # Complete validation before creating any final artifact. Refuse overwrites.
    targets=[output/n for n in ('claims_future.jsonl','review.jsonl','remaining_short_sets.jsonl','summary.json')]
    if any(p.exists() for p in targets):raise FileExistsError('output already materialized')
    dump_rows=lambda p,rows:p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    dump_rows(targets[0],updated);dump_rows(targets[1],review)
    dump_rows(targets[2],[{'paper_id':r['paper_id'],'pool':r['pool'],'claim_count':len(r['claims']),
                         'title':r['title']} for r in updated if len(r['claims'])<4])
    if any(sha(p)!=before[str(p)] for p in protected):raise ValueError('protected source changed')
    summary['protected_sources_unchanged']=True
    targets[3].write_text(json.dumps(summary,indent=2)+'\n')
    print({k:v for k,v in summary.items() if k in ('new_claims','newly_count_complete_sets','remaining_short_sets','future_sets_with_4_to_10','all_new_excerpts_exact','protected_sources_unchanged')})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    main(p.parse_args().output)
