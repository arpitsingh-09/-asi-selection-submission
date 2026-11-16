"""Prepare blank independent I1 reviews and validate human-submitted sheets."""
import argparse,csv,json
from pathlib import Path
from .training import rows

FIELDS=('reviewer_id','question_matches_source','paraphrase_same_question','near_miss_distinct_question','evidence_note','reviewed_at')
def prepare(root='.',out='M/data/i1_human_review_v1'):
 root=Path(root);out=root/out if not Path(out).is_absolute() else Path(out);out.mkdir(parents=True,exist_ok=False)
 ledger=rows(root/'M/data/i1_evidence_v1/candidate_ledger.jsonl'); sheet=out/'review_sheet.csv'
 with sheet.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=('candidate_id','question_id','question_text','paraphrase_text','near_miss_text','source_paper_id','source_title','source_url','source_alignment_machine_status','machine_notes',*FIELDS));w.writeheader()
  for r in ledger:
   m=r.get('source_metadata') or {};w.writerow({'candidate_id':r['candidate_id'],'question_id':r['question_id'],'question_text':r['question_text'],'paraphrase_text':r['paraphrase_text'],'near_miss_text':r['near_miss_text'],'source_paper_id':r['source_paper_id'],'source_title':m.get('paper_title',''),'source_url':m.get('official_url',''),'source_alignment_machine_status':r['alignment_status'],'machine_notes':'; '.join(r['blockers']),**{k:'' for k in FIELDS}})
 return sheet
def import_reviews(sheet,ledger_path,out):
 ledger={r['candidate_id']:r for r in rows(ledger_path)}
 with Path(sheet).open(newline='') as f: reviews=list(csv.DictReader(f))
 seen=set();accepted=[]
 for r in reviews:
  cid=r.get('candidate_id','')
  if cid not in ledger:raise ValueError('unknown candidate ID')
  if cid in seen:raise ValueError('duplicate candidate review')
  seen.add(cid);base=ledger[cid]
  if r.get('question_id')!=base['question_id']:raise ValueError('candidate identity mismatch')
  if r.get('source_paper_id')!=base['source_paper_id']:raise ValueError('source paper mismatch')
  for k in ('reviewer_id','evidence_note','reviewed_at'):
   if not r.get(k,'').strip():raise ValueError('missing '+k)
  for k in ('question_matches_source','paraphrase_same_question','near_miss_distinct_question'):
   if r.get(k) not in ('YES','NO'):raise ValueError('review decision must be YES or NO: '+k)
  accepted.append({'candidate_id':cid,'question_id':base['question_id'],'reviewer_id':r['reviewer_id'],'decisions':{k:r[k] for k in ('question_matches_source','paraphrase_same_question','near_miss_distinct_question')},'evidence_note':r['evidence_note'],'reviewed_at':r['reviewed_at'],'independent_human_review':True,'machine_status_preserved':base['alignment_status']})
 if seen!=set(ledger):raise ValueError('missing candidate reviews')
 Path(out).write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in accepted));return len(accepted)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--prepare',action='store_true');a=p.parse_args()
 if a.prepare:print(prepare(a.root))
