"""Create blank evidence-request templates and validate returned evidence rows."""
import argparse,csv,json
from pathlib import Path
from .training import rows

REVIEW_FIELDS=('outcome_id','paper_id','factor','value','definition','review_source_url','version_id','public_at','archived_evidence_url','evidence_quote','verifier_id','verified_at')
HUMAN_FIELDS=('candidate_id','question_id','source_paper_id','question_identity_yes_no','paraphrase_same_question_yes_no','near_miss_distinct_yes_no','decoy_same_topic_yes_no','reviewer_id','independent_of_author','evidence_source','evidence_locator','rationale','reviewed_at')
def prepare(root='.',out='M/data/evidence_collection_v1'):
 root=Path(root);out=root/out if not Path(out).is_absolute() else Path(out);out.mkdir(parents=True,exist_ok=False)
 reviews=rows(root/'M/data/ingestion_v2/review_outcomes.jsonl')
 with (out/'review_version_dates.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=REVIEW_FIELDS);w.writeheader()
  for r in reviews:w.writerow({'outcome_id':r.get('outcome_id'),'paper_id':r.get('paper_id'),'factor':r.get('factor'),'value':r.get('value'),'definition':r.get('definition'),'review_source_url':'','version_id':r.get('outcome_id'),'public_at':'','archived_evidence_url':'','evidence_quote':'','verifier_id':'','verified_at':''})
 ledger=rows(root/'M/data/i1_prospective_v1/eligibility_ledger.jsonl')
 with (out/'human_question_decoy_reviews.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=HUMAN_FIELDS);w.writeheader()
  for r in ledger:w.writerow({'candidate_id':r['question_id'],'question_id':r['question_id'],'source_paper_id':','.join(r.get('input_ids') or []),**{k:'' for k in HUMAN_FIELDS[3:]}})
 (out/'README.md').write_text('# Evidence collection templates\n\nBlank fields require external source evidence or independent human review. Do not infer public dates from record version timestamps. For each review version, provide an archived source showing that exact value and its public timestamp. Human reviewers must be independent of question authors and cite evidence locators.\n')
 return out
def validate_review_row(r):
 for k in ('outcome_id','paper_id','factor','version_id','public_at','archived_evidence_url','evidence_quote','verifier_id','verified_at'):
  if not str(r.get(k,'')).strip():raise ValueError('missing '+k)
 if r['factor'] not in ('peer_review','later_community_use'):raise ValueError('unsupported factor')
 if not r['archived_evidence_url'].startswith(('https://','http://')):raise ValueError('evidence URL required')
 if 'T' not in r['public_at']:raise ValueError('public_at must include timestamp')
 return True
def validate_human_row(r):
 for k in HUMAN_FIELDS:
  if not str(r.get(k,'')).strip():raise ValueError('missing '+k)
 if r['independent_of_author']!='YES':raise ValueError('independent reviewer required')
 for k in HUMAN_FIELDS[3:7]:
  if r[k] not in ('YES','NO'):raise ValueError('explicit YES/NO required: '+k)
 for k in ('evidence_source','evidence_locator','rationale'): 
  if not r[k].strip():raise ValueError('traceable evidence and rationale required')
 return True
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--out',default='M/data/evidence_collection_v1');a=p.parse_args();print(prepare(a.root,a.out))
