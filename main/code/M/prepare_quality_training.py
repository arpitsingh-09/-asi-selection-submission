"""Prepare only provenance- and date-verified quality labels for train/validation."""
import argparse, json
from pathlib import Path
from .training import rows
from .schema import date
from .temporal import split_for
from .ingestion import verify_outcome

def prepare(root='.', out='M/data/quality_training_v1'):
    root=Path(root); out=root/out if not Path(out).is_absolute() else Path(out)
    out.mkdir(parents=True,exist_ok=False)
    reviews=rows(root/'M/data/ingestion_v2/review_outcomes.jsonl')
    manifests={s:rows(root/f'M/data/manifests_v1/{s}.jsonl') for s in ('train','validation')}
    by_paper={}
    for s,rs in manifests.items():
        for r in rs: by_paper.setdefault(r['paper_id'],[]).append((s,r))
    reasons={}; eligible={'train':[],'validation':[]}; mapped=[]
    for x in reviews:
        reason=None
        evidence=x.get('value_evidence') or x.get('source_record_evidence') or {}
        binding=evidence.get('binding',{})
        if x.get('source_type')=='M_DATED_QUALITY_LABEL':
            try: verify_outcome(x)
            except (KeyError, TypeError, ValueError): reason='invalid_dated_label_source_evidence'
        matches=by_paper.get(x.get('paper_id'),[])
        if reason is not None: pass
        elif not matches: reason='no_exact_question_paper_link'
        elif len(matches)!=1: reason='ambiguous_question_paper_link'
        elif not binding.get('record_sha256'): reason='missing_label_source_provenance'
        elif not x.get('observed_at'): reason='missing_verified_review_observation_date'
        elif x.get('usable_for_fitting') is not True: reason='source_receipt_marks_unusable'
        else:
            s,r=matches[0]
            try:
                observed=date(x['observed_at']); published=date(r['published'])
                if split_for(r['published'])!=s: reason='split_mismatch'
                elif observed<published: reason='review_precedes_question_publication'
                elif s=='train' and observed>=date('2024-01-01'): reason='train_label_after_cutoff'
                elif s=='validation' and observed>=date('2025-01-01'): reason='validation_label_after_cutoff'
            except Exception: reason='invalid_or_unverifiable_date'
            if reason is None:
                mapped.append({'question_id':r['question_id'],'paper_id':r['paper_id'],'split':s,'factor':x['factor'],'value':x['value'],'definition':x['definition'],'observed_at':x['observed_at'],'source_outcome_id':x['outcome_id'],'source_record_sha256':binding['record_sha256']})
                eligible[s].append(mapped[-1])
        if reason: reasons[reason]=reasons.get(reason,0)+1
    (out/'eligible_labels.jsonl').write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in mapped))
    report={'source_review_records_examined':len(reviews),'manifest_records':{s:len(v) for s,v in manifests.items()},'eligible_train':len(eligible['train']),'eligible_validation':len(eligible['validation']),'eligible_by_factor_split':{s:{f:sum(x['factor']==f for x in eligible[s]) for f in ('peer_review','later_community_use')} for s in eligible},'exclusions':reasons,'remaining_blockers':['No review record carries a verified public observed_at date; ingestion receipt reports 0 verified dates.','Question mapping requires exact paper ID present in train/validation manifest.','No later_community_use labels with dated provenance.'],'training_status':'BLOCKED_INELIGIBLE_LABELS' if not mapped else 'PREPARED_NOT_TRAINED'}
    (out/'eligibility_report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--out',default='M/data/quality_training_v1');a=p.parse_args();print(json.dumps(prepare(a.root,a.out),indent=2))
