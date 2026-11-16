"""Validate existing generated questions for prospective I1 eligibility only."""
import argparse,csv,hashlib,json
from pathlib import Path
from .training import rows
from .schema import date

def prepare(root='.',out='M/data/i1_prospective_v1'):
 root=Path(root);out=root/out if not Path(out).is_absolute() else Path(out);out.mkdir(parents=True,exist_ok=False)
 base=root/'M/data/generated_questions_v1'; qs=rows(base/'generated_questions.jsonl'); decoys={x['question_id']:x for x in rows(base/'decoy_questions_v2.jsonl')}
 vec=json.loads((root/'M/data/s1_review_v3/minilm_vectors.json').read_text()); quality=json.loads((root/'M/results/quality_v2/validation_results.json').read_text())
 items=[]
 for q in qs:
  b=[]; stamp=q.get('generated_at'); validstamp=False
  try: date(stamp);validstamp=True
  except Exception: b.append('generation_timestamp_missing_or_invalid')
  refs=q.get('R',[]); inputs_ok=bool(refs)
  if len({p.get('paper_id') for p in refs})!=len(refs):inputs_ok=False;b.append('duplicate_or_missing_input_ids')
  for p in refs:
   try:
    if not p.get('paper_id') or not p.get('url') or not p.get('source_record') or date(p['updated'])>=date(stamp):inputs_ok=False;b.append('input_identity_provenance_or_precedence_unverified')
   except Exception:inputs_ok=False;b.append('input_date_missing_or_invalid')
  c=q.get('controls',{});d=decoys.get(q['question_id'],{}).get('decoy')
  if not c.get('empty_input_ids')==[]:b.append('empty_control_missing')
  if not c.get('shuffled_input_ids'):b.append('shuffled_control_missing')
  if not d or decoys[q['question_id']].get('status')!='GENERATED_DEC0Y_PENDING_HUMAN_REVIEW':b.append('same_topic_decoy_unverified_or_missing')
  b.append('frozen_I1_contrast_pair_annotations_not_present_for_generated_questions')
  b.append('independent_human_question_and_paraphrase_verification_missing')
  if not any(x.get('question_id')==q['question_id'] for x in vec.get('records',[])):b.append('exact_frozen_encoder_vector_missing')
  if any(v.get('status')!='fitted' for v in quality.get('heads',{}).values()) or not quality.get('heads'):b.append('both_Q_heads_and_frozen_normalization_unavailable')
  items.append({'question_id':q['question_id'],'question':q.get('question'),'generation_timestamp':stamp if validstamp else None,'timestamp_verified_from_generation_record':validstamp,'input_ids':[p.get('paper_id') for p in refs] if inputs_ok else None,'input_versions_verified':inputs_ok,'temporal_precedence_verified':inputs_ok and validstamp,'required_conditions':['original','empty','shuffled','decoy'],'independent_human_verification':False,'eligible':False,'blockers':sorted(set(b))})
 h=hashlib.sha256((base/'generated_questions.jsonl').read_bytes()).hexdigest()
 report={'schema':'M-I1-prospective-readiness-v1','candidates_examined':len(items),'verified_timestamps':sum(x['timestamp_verified_from_generation_record'] for x in items),'verified_input_sets':sum(x['input_versions_verified'] for x in items),'temporally_eligible_candidates':sum(x['temporal_precedence_verified'] for x in items),'fully_I1_eligible_candidates':0,'source_sha256':h,'evaluation_run':False,'global_blockers':['Generated candidates lack frozen I1 paraphrase/near-miss contrast labels and independent human verification.','Both registered Q heads and frozen normalization are unavailable.','Same-topic decoy judgments remain unverified.']}
 (out/'eligibility_ledger.jsonl').write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in items));(out/'eligibility_report.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--out',default='M/data/i1_prospective_v1');a=p.parse_args();print(json.dumps(prepare(a.root,a.out),indent=2))
