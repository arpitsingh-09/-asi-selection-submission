"""Validate returned six-question review package without auto-verifying anything."""
import csv,json,hashlib
from pathlib import Path
FIELDS=('question_same_as_intended','paraphrase_preserves_identity','near_miss_changes_identity','decoy_same_topic')
def import_reviews(sheet,source_jsonl,out):
 source={r['question_id']:r for r in (json.loads(x) for x in Path(source_jsonl).read_text().splitlines() if x.strip())}
 with Path(sheet).open(newline='') as f: rows=list(csv.DictReader(f))
 ids=[r.get('question_id','') for r in rows]
 if len(ids)!=len(set(ids)):raise ValueError('duplicate or conflicting candidate reviews')
 if set(ids)!=set(source):raise ValueError('missing or unexpected candidate IDs')
 accepted=[]
 for r in rows:
  q=source[r['question_id']]
  if r.get('question','')!=q.get('question') or r.get('original_inputs_json','')!=json.dumps(q.get('R',[]),ensure_ascii=False):raise ValueError('question or input identity mismatch')
  for k in FIELDS:
   if r.get(k) not in ('YES','NO'):raise ValueError('explicit human YES/NO required: '+k)
  for k in ('reviewer_id','independent_of_author','evidence_source','evidence_locator','rationale','reviewed_at'):
   if not r.get(k,'').strip():raise ValueError('missing traceable human evidence: '+k)
  if r['independent_of_author']!='YES':raise ValueError('independent reviewer required')
  if not r['evidence_source'].startswith(('https://','http://')):raise ValueError('unsupported evidence source; use traceable URL')
  if len(r['evidence_locator'])<3 or len(r['rationale'])<8:raise ValueError('unsupported evidence locator or rationale')
  status='VERIFIED' if r['decoy_same_topic']=='YES' else 'REJECTED' if r['decoy_same_topic']=='NO' else 'UNRESOLVED'
  accepted.append({'question_id':r['question_id'],'human_decisions':{k:r[k] for k in FIELDS},'reviewer_id':r['reviewer_id'],'reviewed_at':r['reviewed_at'],'evidence_source':r['evidence_source'],'evidence_locator':r['evidence_locator'],'rationale':r['rationale'],'decoy_human_status':status,'source_record_sha256':hashlib.sha256(json.dumps(q,sort_keys=True).encode()).hexdigest()})
 Path(out).write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in accepted));return len(accepted)
