"""Recover independent saved claims previously hidden by excerpt deduplication.
Explicit AI review; preserves all prior artifacts and never generates claim text.
"""
import argparse,copy,hashlib,json
from pathlib import Path
from recover_claims import candidates,norm

CHOSEN={
 ('2112.14983v1','The system uses a combination of CNN and RNN to analyze facial expressions and emotions.'):
 'Adds the recurrent prediction component to the retained CNN landmark description; quoted source explicitly identifies both components.',
 ('2302.00595v1','The paper discusses the use of differentiable vector graphics and neural rendering in training deep reinforcement agents for painting images.'):
 'Adds a specific rendering/training mechanism absent from the retained survey scope and algorithm-range claims.',
 ('2412.20666v2','The proposed method outperforms classical methods and is on par with supervised learning approaches on real-world images.'):
 'Adds the real-image comparative result; retained result was only on synthetic images.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parent;data=root/'data'
    prior=root/'analysis/claim_review_v1/claims_future.jsonl'
    records=list(map(json.loads,prior.read_text().splitlines()));short={r['paper_id']:r for r in records if len(r['claims'])<4}
    raw={r['paper_id']:r for r in map(json.loads,(data/'raw_papers.jsonl').read_text().splitlines())}
    previous={(r['paper_id'],norm(c['claim'])) for r in map(json.loads,(root/'analysis/claim_recovery_v1/candidates.jsonl').read_text().splitlines()) for c in r['all_additional_candidates']}
    seen=set();found=[]
    for path in sorted(data.rglob('claims*.json*')):
        for line,text in enumerate(path.read_text().splitlines(),1):
            try:r=json.loads(text)
            except ValueError:continue
            if not isinstance(r,dict) or r.get('paper_id') not in short:continue
            pid=r['paper_id'];original={norm(c['claim']) for c in short[pid]['claims']}
            for c,kind in candidates(r):
                if not isinstance(c,dict) or not isinstance(c.get('claim'),str) or not isinstance(c.get('evidence'),str):continue
                key=(pid,norm(c['claim']))
                if key in seen or key in previous or key[1] in original or not c['evidence'] or c['evidence'] not in raw[pid]['abstract']:continue
                seen.add(key);found.append({'paper_id':pid,'claim':c['claim'],'evidence':c['evidence'],
                    'source':str(path.relative_to(root)),'line':line,'source_kind':kind,
                    'promote':(pid,c['claim']) in CHOSEN,'reviewer':'Codex AI','human_review':False,
                    'reason':CHOSEN.get((pid,c['claim']),'Not promoted: repeats/refines retained assertions or does not establish an independent atomic addition.')})
    selected={(r['paper_id'],r['claim']) for r in found if r['promote']}
    if selected!=set(CHOSEN):raise ValueError('chosen saved claims missing')
    updated=copy.deepcopy(records);byid={r['paper_id']:r for r in updated}
    for c in found:
        if not c['promote']:continue
        r=byid[c['paper_id']];r['claims'].append({'claim':c['claim'],'evidence':c['evidence']})
        r['shared_excerpt_review']={'reviewer':'Codex AI','human_review':False,'addition':c,
            'original_audit':{k:v for k,v in r.items() if k.startswith('audit_')}}
        r['claim_count']=len(r['claims']);r['audit_exact_evidence']=sum(x['evidence'] in raw[r['paper_id']]['abstract'] for x in r['claims'])
        r['audit_invalid_evidence']=len(r['claims'])-r['audit_exact_evidence']
    a.output.mkdir(parents=True,exist_ok=False)
    (a.output/'candidate_review.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in found))
    (a.output/'claims_future.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in updated))
    summary={'new_claims':len(selected),'newly_completed_sets':len(selected),'remaining_short_sets':sum(len(r['claims'])<4 for r in updated),
        'future_sets_with_4_to_10':sum(4<=len(r['claims'])<=10 for r in updated),'candidate_strings_reviewed':len(found),
        'prior_artifact_sha256':hashlib.sha256(prior.read_bytes()).hexdigest(),'human_review':False,'used_in_evaluation':False}
    (a.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)

if __name__=='__main__':main()
