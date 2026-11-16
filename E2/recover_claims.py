"""Recover verbatim, excerpt-backed candidates from saved LLM extractions.
No new claims are generated. Original selected records are never overwritten.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


def norm(s): return ' '.join(s.casefold().split())

def candidates(record):
    for c in record.get('claims', []):
        yield c, 'claims'
    for r in record.get('rejected_claims', []):
        if isinstance(r,dict): yield r.get('candidate'), 'rejected_candidate'
    raw=record.get('raw_responses', [])
    if isinstance(record.get('raw_response'), str):raw=list(raw)+[record['raw_response']]
    for text in raw:
        if not isinstance(text,str):continue
        try:
            obj,_=json.JSONDecoder().raw_decode(text[text.index('{'):])
        except (ValueError,TypeError):continue
        if isinstance(obj,dict):
            for c in obj.get('claims',[]):yield c,'raw_response'


def recover(selected, raw, sources):
    short={r['paper_id']:r for r in selected if len(r['claims'])<4}
    available={pid:[] for pid in short};rejected=Counter()
    for source,line,record in sources:
        pid=record.get('paper_id')
        if pid not in short:continue
        for c,kind in candidates(record):
            if not isinstance(c,dict) or not isinstance(c.get('claim'),str) or not isinstance(c.get('evidence'),str):continue
            claim,evidence=c['claim'],c['evidence']
            if not claim.strip() or not evidence.strip() or evidence not in raw[pid]['abstract']:
                rejected['nonexact_or_empty_evidence']+=1;continue
            available[pid].append({'claim':claim,'evidence':evidence,'source':source,'line':line,'source_kind':kind})
    output=[]
    for pid,r in short.items():
        claim_keys={norm(c['claim']) for c in r['claims']};evidence_keys={norm(c['evidence']) for c in r['claims']}
        additions=[]
        for c in sorted(available[pid],key=lambda c:({'claims':0,'rejected_candidate':1,'raw_response':2}[c['source_kind']],c['source'],c['line'],c['claim'])):
            ck,ek=norm(c['claim']),norm(c['evidence'])
            if ck in claim_keys or ek in evidence_keys:continue
            claim_keys.add(ck);evidence_keys.add(ek);additions.append(c)
        chosen=additions[:max(0,4-len(r['claims']))]
        output.append({'pool':r['pool'],'paper_id':pid,'original_count':len(r['claims']),
            'original_claims':r['claims'],'recovered_additions':chosen,
            'all_additional_candidates':additions,'candidate_count':len(r['claims'])+len(chosen),
            'status':'evidence_backed_candidates_need_semantic_atomicity_review' if chosen else 'no_additional_exact_excerpt_found'})
    return output,dict(rejected)


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parent;data=root/'data'
    selected=[json.loads(l) for l in (data/'claims_v8_selected.jsonl').read_text().splitlines()]
    raw={r['paper_id']:r for r in map(json.loads,(data/'raw_papers.jsonl').read_text().splitlines())}
    sources=[];hashes={}
    for path in sorted(data.rglob('claims*.jsonl')):
        hashes[str(path.relative_to(root))]=hashlib.sha256(path.read_bytes()).hexdigest()
        for line,text in enumerate(path.read_text().splitlines(),1):
            try:r=json.loads(text)
            except ValueError:continue
            if isinstance(r,dict):sources.append((str(path.relative_to(root)),line,r))
    records,rejected=recover(selected,raw,sources)
    a.output.mkdir(parents=True,exist_ok=False)
    (a.output/'candidates.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in records))
    summary={'short_records':len(records),'papers_with_additions':sum(bool(r['recovered_additions']) for r in records),
             'additions':sum(len(r['recovered_additions']) for r in records),
             'candidate_sets_reaching_four':sum(r['candidate_count']>=4 for r in records),
             'still_below_four':sum(r['candidate_count']<4 for r in records),
             'not_human_validated':True,'rejected_occurrences':rejected,'source_sha256':hashes}
    (a.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)

if __name__=='__main__':main()
