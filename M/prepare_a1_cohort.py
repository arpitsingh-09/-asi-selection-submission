"""Validate existing generated-question records against frozen A1 cohort needs.

This prepares an eligibility receipt only; it does not score novelty or alter source data.
"""
import argparse, hashlib, json
from pathlib import Path
from .training import rows
from .schema import date

AXIOMS=('partial_coverage','concentration')
CONTROLS=('original','empty','shuffled','decoy')

def prepare(root='.', out='M/data/a1_preparation_v1'):
    root=Path(root); out=root/out if not Path(out).is_absolute() else Path(out); out.mkdir(parents=True,exist_ok=False)
    base=root/'M/data/generated_questions_v1'
    questions=rows(base/'generated_questions.jsonl')
    decoys=rows(base/'decoy_questions_v2.jsonl')
    decoy_by={r.get('question_id'):r for r in decoys}
    records=[]; exclusions={}
    for r in questions:
        missing=[]
        if not r.get('R') or not r.get('generated_at'): missing.append('missing_generation_inputs_or_timestamp')
        else:
            for paper in r['R']:
                try:
                    if date(paper['updated'])>=date(r['generated_at']): missing.append('input_not_strictly_preceding_question'); break
                except Exception: missing.append('invalid_input_date'); break
        c=r.get('controls',{})
        if not c.get('shuffled_input_ids'): missing.append('shuffled_control_missing')
        dr=decoy_by.get(r.get('question_id'))
        if not dr or not dr.get('decoy') or dr['status']!='GENERATED_DEC0Y_PENDING_HUMAN_REVIEW': missing.append('same_topic_decoy_unresolved_or_unverified')
        # A1 manipulation records and signed score predictions do not exist in these source rows.
        missing.extend(['partial_coverage_manipulation_and_scores_missing','concentration_manipulation_and_scores_missing','four-condition frozen predictions missing'])
        rec={'question_id':r.get('question_id'),'source_record_sha256':hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest(),'required_axioms':list(AXIOMS),'required_conditions':list(CONTROLS),'status':'BLOCKED','missing':sorted(set(missing))}
        records.append(rec)
        for reason in rec['missing']: exclusions[reason]=exclusions.get(reason,0)+1
    (out/'candidate_eligibility.jsonl').write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in records))
    report={'schema':'M-A1-preparation-v1','source_records':len(questions),'eligible_cohort_size':0,'eligible_records':0,'evaluation_run':False,'axioms':list(AXIOMS),'conditions':list(CONTROLS),'exclusions_by_reason':exclusions,'remaining_blockers':['All six decoy proposals lack human same-topic verification or are unresolved.','Neither required novelty manipulation is present as a frozen, provenance-bound record with predictions.','No four-condition predictions are frozen; evaluation authorization/cohort lock remains required.']}
    (out/'eligibility_report.json').write_text(json.dumps(report,indent=2)+'\n'); return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--out',default='M/data/a1_preparation_v1');a=p.parse_args();print(json.dumps(prepare(a.root,a.out),indent=2))
