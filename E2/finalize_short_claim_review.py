"""Materialize source-reviewed revisions of the 23 remaining short sets only.
Original scored extractions, prior completions and frozen plans stay immutable.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from complete_claim_additions import records,sha


def revise(prior, decisions, raw, expected_ids, source_path, source_sha):
    byid={r['paper_id']:r for r in prior}
    if len(byid)!=len(prior):raise ValueError('duplicate focal IDs')
    ids=[d['paper_id'] for d in decisions]
    if len(ids)!=len(set(ids)) or set(ids)!=set(expected_ids):
        raise ValueError('review must cover exactly the pending IDs')
    source={}
    for number,r in enumerate(raw,1):
        pid=r['paper_id']
        if pid in source and any(source[pid][1][k]!=r[k] for k in ('title','abstract','published')):
            raise ValueError('conflicting source duplicate')
        if pid not in source or (pid in byid and r.get('pool')==byid[pid]['pool']):
            source[pid]=(number,r)
    out=copy.deepcopy(prior);targets={r['paper_id']:r for r in out};reviews=[]
    for d in decisions:
        pid=d['paper_id'];original=byid[pid]
        if len(original['claims'])>=4:raise ValueError('completed focal must not be revised')
        if d.get('human_review') is not False or not d.get('semantic_review'):
            raise ValueError('explicit AI review required')
        line,paper=source[pid]
        binding={'source':str(source_path),'source_line':line,'source_sha256':source_sha,
                 'abstract_sha256':hashlib.sha256(paper['abstract'].encode()).hexdigest()}
        decision=copy.deepcopy(d);decision.update(binding)
        row=targets[pid]
        if d['status']=='supported_count_complete':
            claims=d['claims']
            if not 4<=len(claims)<=10:raise ValueError('4-10 reviewed claims required')
            seen=set();bound=[]
            for c in claims:
                key=' '.join(c['claim'].casefold().split())
                if not key or key in seen:raise ValueError('empty/duplicate claim')
                seen.add(key)
                if not c['evidence'].strip() or c['evidence'] not in paper['abstract']:
                    raise ValueError('unsupported excerpt: '+pid)
                if c['kind'] not in ('method','result','background'):raise ValueError('claim kind required')
                start=paper['abstract'].index(c['evidence'])
                bound.append({**c,**binding,'evidence_start':start,'evidence_end':start+len(c['evidence']),
                    'reused_exact_prior_claim':any(c['claim']==old['claim'] and c['evidence']==old['evidence'] for old in original['claims'])})
            decision['claims']=bound
            row['claims']=[{'claim':c['claim'],'evidence':c['evidence']} for c in claims]
            row['claim_count']=len(claims)
            row['prior_claims_before_short_set_review']=copy.deepcopy(original['claims'])
            row['prior_audit_before_short_set_review']={k:v for k,v in original.items() if k.startswith('audit_')}
            row['audit_exact_evidence']=len(claims);row['audit_invalid_evidence']=0
        elif d['status']=='evidence_limited':
            if d.get('claims') is not None or not d.get('limitation'):
                raise ValueError('unresolved history must retain original claims with limitation')
        else:raise ValueError('unknown review status')
        row['short_set_semantic_review']=decision
        reviews.append(decision)
    # No previously complete focal may change, even in metadata.
    if any(targets[pid]!=r for pid,r in byid.items() if pid not in expected_ids):
        raise ValueError('unrelated prior focal changed')
    return out,reviews


def main(output):
    root=Path(__file__).resolve().parent
    prior_path=root/'analysis/claim_completion_v1/claims_future.jsonl'
    pending_path=root/'analysis/claim_completion_v1/remaining_short_sets.jsonl'
    raw_path=root/'data/raw_papers.jsonl';decision_path=output/'decisions.jsonl'
    protected=[prior_path,pending_path,raw_path,root/'data/claims_v8_selected.jsonl',
               root/'data/scoring_results.jsonl',root/'data/scoring_results.matmul_pilot.jsonl',
               root/'analysis/task3_execution_v1/plan.json']
    before={str(p):sha(p) for p in protected}
    prior=records(prior_path);pending=records(pending_path)
    if len(prior)!=300 or len(pending)!=23:raise ValueError('unexpected resume state')
    updated,reviews=revise(prior,records(decision_path),records(raw_path),
        {r['paper_id'] for r in pending},raw_path,before[str(raw_path)])
    completed=[r for r in reviews if r['status']=='supported_count_complete']
    limited=[r for r in reviews if r['status']=='evidence_limited']
    count_complete=sum(4<=len(r['claims'])<=10 for r in updated)
    accepted=[c for r in completed for c in r['claims']]
    summary={'reviewed_papers':23,'papers_completed_this_run':len(completed),
        'papers_still_incomplete':len(limited),'total_count_eligible_focal_papers':count_complete,
        'semantically_reviewed_complete_sets_this_run':len(completed),
        'accepted_claims_in_reviewed_complete_sets':len(accepted),
        'exact_prior_claims_reused':sum(c['reused_exact_prior_claim'] for c in accepted),
        'all_reviewed_claim_excerpts_exact':True,
        'background_claims_explicitly_labeled':sum(c['kind']=='background' for c in accepted),
        'human_review':False,'used_in_evaluation':False,'new_scores':0,
        'source_sha256':before,'decisions_sha256':sha(decision_path),
        'implementation_sha256':sha(Path(__file__)),
        'limits':['294 is count eligibility, not independent semantic certification of all inherited sets.',
                  'The six evidence-limited sets are not eligible for four-claim analyses.',
                  'Background assertions are explicitly labeled and not presented as new contributions.',
                  'No matching full text for the pending IDs found in inspected local source paths.']}
    names=['claims_future.jsonl','review.jsonl','remaining_short_sets.jsonl','summary.json']
    if any((output/n).exists() for n in names):raise FileExistsError('output already materialized')
    dump=lambda path,rows:path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    dump(output/names[0],updated);dump(output/names[1],reviews)
    dump(output/names[2],[{'paper_id':r['paper_id'],'title':next(x['title'] for x in updated if x['paper_id']==r['paper_id']),
        'reason':r['semantic_review'],'source':r['source'],'source_line':r['source_line']} for r in limited])
    if any(sha(p)!=before[str(p)] for p in protected):raise ValueError('protected source changed')
    summary['protected_source_hashes_unchanged']=True
    (output/names[3]).write_text(json.dumps(summary,indent=2)+'\n')
    print({k:v for k,v in summary.items() if k in ('papers_completed_this_run','papers_still_incomplete','total_count_eligible_focal_papers','accepted_claims_in_reviewed_complete_sets','exact_prior_claims_reused')})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    main(p.parse_args().output)
