"""Read independent pilot labels from the actual Markdown sheet; no inference."""
import argparse
from datetime import date
import json
import re
from pathlib import Path
from researcher_approval import file_digest


def concrete(text):
    return isinstance(text,str) and bool(text.strip()) and text.strip().lower() not in ('null','none','pending','todo','tbd','n/a') and not re.fullmatch(r'[_\s.\-]+',text.strip())


def label_value(section,text):
    text=text.strip().strip('`').lower()
    if section=='reconstruction':
        if re.fullmatch('[1-5]',text):return int(text)
    elif section=='diversity' and text=='null':return None
    elif section in ('already_asked','diversity'):
        if text in ('true','false'):return text=='true'
    elif text in ('constructive','analytic','other','ambiguous'):return text
    raise ValueError('missing or invalid rubric label')


def ingest(sheet,predictions):
    predictions_path=Path(predictions)
    text=Path(sheet).read_text();predictions=json.loads(predictions_path.read_text())
    required={r['case_id']:r for r in predictions if r['expected'] is None}
    sections=re.split(r'^## ([a-z_]+-\d+)\s*$',text,flags=re.M)
    found={};records=[];issues=[]
    for i in range(1,len(sections),2):
        cid,body=sections[i:i+2]
        if cid in found:raise ValueError('duplicate review case: '+cid)
        found[cid]=body
    if set(found)!=set(required):raise ValueError('review case IDs differ from required ten judgments')
    for cid,reference in required.items():
        body=found[cid];errors=[];label=None;reviewer=None;reviewed=None;rationale=None
        match=re.search(r'^Independent label:\s*(.*?)\s+Reviewer/date:\s*(.*?)\s*$',body,re.M)
        try:
            if not match:raise ValueError('missing label and Reviewer/date line')
            label=label_value(reference['section'],match.group(1))
        except ValueError as exc:errors.append(str(exc))
        if match:
            identity=match.group(2);dm=re.search(r'\b(\d{4}-\d{2}-\d{2})\b',identity)
            if dm:
                try:
                    reviewed=date.fromisoformat(dm.group(1))
                    if reviewed>date.today():raise ValueError('future review date')
                    reviewed=reviewed.isoformat()
                except ValueError:errors.append('invalid review date');reviewed=None
                reviewer=(identity[:dm.start()]+identity[dm.end():]).strip(' /|,;—-')
            if not concrete(reviewer):errors.append('missing real reviewer identifier')
            if reviewed is None:errors.append('missing valid review date')
        rationale_match=re.search(r'^Rationale:\s*(.*?)\s*$',body,re.M)
        rationale=rationale_match.group(1) if rationale_match else None
        if not concrete(rationale):errors.append('missing rationale')
        # Validate that actual examples were retained, not just the IDs.
        expected_source=json.loads((Path(sheet).parent/'human_review.json').read_text())
        case=next(r for r in expected_source if r['case_id']==cid)
        for key in ('a','b'):
            if case.get(key) is not None and (key.upper()+': '+case[key]) not in body:errors.append('review example '+key+' differs from evidence')
        record={'case_id':cid,'section':reference['section'],'label':label,'reviewer_id':reviewer,
            'review_date':reviewed,'rationale':rationale,'verified_fields_complete':not errors,
            'reviewer_identity_authenticated':False,'errors':errors}
        if not errors:record['agrees_with_evaluator']=type(label) is type(reference['prediction']) and label==reference['prediction']
        records.append(record)
    metrics={}
    for section in ('reconstruction','already_asked','diversity','question_type'):
        rows=[r for r in records if r['section']==section and r['verified_fields_complete']]
        metrics[section]={'verified_independent_labels':len(rows),'agreement_count':sum(r['agrees_with_evaluator'] for r in rows),
            'agreement_rate':sum(r['agrees_with_evaluator'] for r in rows)/len(rows) if rows else None,
            'MAE':sum(abs(r['label']-required[r['case_id']]['prediction']) for r in rows)/len(rows) if rows and section=='reconstruction' else None,
            'validation_complete':False,'acceptance_threshold':None}
    return {'human_labels_verified':sum(r['verified_fields_complete'] for r in records),'labels_required':10,
        'validations_genuinely_completed':0,'sections':metrics,'records':records,
        'review_sheet_file_sha256':file_digest(Path(sheet)),'verified_predictions_file_sha256':file_digest(predictions_path),
        'identity_limit':'Non-placeholder identifiers/dates/rationales can be checked; real-world identity and independence cannot be authenticated by this parser.',
        'status':'incomplete_missing_review_fields' if any(r['errors'] for r in records) else 'labels_recorded_researcher_adequacy_assessment_pending',
        'model_calls':0}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sheet',type=Path,required=True);p.add_argument('--predictions',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();report=ingest(args.sheet,args.predictions)
    with args.output.open('x') as h:json.dump(report,h,indent=2,sort_keys=True)
    print(json.dumps({k:report[k] for k in ('human_labels_verified','validations_genuinely_completed','status')},indent=2))

if __name__=='__main__':main()
