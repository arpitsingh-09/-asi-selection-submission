"""Prepare blank I1 contrast review records; proposals are never auto-verified."""
import argparse,csv,json
from pathlib import Path
from .training import rows

FIELDS=('reviewer_id','paraphrase_preserves_question','near_miss_changes_question','decoy_same_topic','evidence_note','reviewed_at')
DECOY_EVIDENCE=('decoy_evidence_source','decoy_evidence_locator','decoy_evidence_quote')
def prepare(root='.',out='M/data/i1_human_review_v1'):
 root=Path(root);out=root/out if not Path(out).is_absolute() else Path(out);out.mkdir(parents=True,exist_ok=True)
 qs=rows(root/'M/data/generated_questions_v1/generated_questions.jsonl'); ledger=rows(root/'M/data/i1_prospective_v1/eligibility_ledger.jsonl')
 li={x['question_id']:x for x in ledger}; path=out/'prospective_review.csv'
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=('question_id','question','inputs','decoy_question','decoy_status','contrast_status',*FIELDS,*DECOY_EVIDENCE));w.writeheader()
  for q in qs:
   l=li[q['question_id']]; dec=q.get('controls',{}).get('same_topic_decoy') or {}
   w.writerow({'question_id':q['question_id'],'question':q['question'],'inputs':json.dumps([p['paper_id'] for p in q['R']]),'decoy_question':dec.get('question',''),'decoy_status':'UNVERIFIED' if dec else 'MISSING','contrast_status':'NOT_PROVIDED','paraphrase_preserves_question':'','near_miss_changes_question':'','decoy_same_topic':'','reviewer_id':'','evidence_note':'','reviewed_at':'',**{k:'' for k in DECOY_EVIDENCE}})
 return path
def validate(sheet,expected_ids):
 with Path(sheet).open(newline='') as f:rs=list(csv.DictReader(f))
 ids=[r.get('question_id') for r in rs]
 if len(ids)!=len(set(ids)):raise ValueError('duplicate question review')
 if set(ids)!=set(expected_ids):raise ValueError('missing or unexpected question IDs')
 for r in rs:
  status=r.get('decoy_status','').strip()
  if status not in ('UNVERIFIED','MISSING','VERIFIED'):raise ValueError('unsupported decoy status')
  if status=='VERIFIED':
   if r.get('decoy_same_topic')!='YES':raise ValueError('verified decoy requires explicit YES decision')
   if any(not r.get(k,'').strip() for k in DECOY_EVIDENCE):raise ValueError('verified decoy requires source, locator, and evidence quote')
   if not r.get('reviewer_id','').strip() or not r.get('reviewed_at','').strip():raise ValueError('verified decoy requires reviewer identity and date')
  elif r.get('decoy_same_topic')=='YES':raise ValueError('YES decoy decision requires VERIFIED status')
  for k in FIELDS:
   if not r.get(k,'').strip():raise ValueError('incomplete human review field: '+k)
  for k in FIELDS[1:4]:
   if r[k] not in ('YES','NO'):raise ValueError('decision must be YES/NO')
 return len(rs)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');a=p.parse_args();print(prepare() if a.prepare else 'use prepare() or validate()')
