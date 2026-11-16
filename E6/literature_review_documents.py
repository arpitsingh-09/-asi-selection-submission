"""Prepare separate human review documents and ingest them offline.

No inference; never overwrites original packets, review records, or settings.
Combined reports belong to the coordinator, not either reviewer.
"""
import argparse
import json
import re
from pathlib import Path
from researcher_approval import ROOT, digest, file_digest, nonempty_text, valid_utc
from finalize_literature_evidence import CATEGORIES, verify_bundle

CHECKS=tuple(CATEGORIES)
BINDINGS=('input_set_id','reviewer_slot','packet_sha256','extraction_sha256',
          'target_source_text_sha256','review_guide_sha256')


def load(path):
    return json.loads(Path(path).read_text())


def write_json(path,value):
    with Path(path).open('x') as handle:
        json.dump(value,handle,indent=2,ensure_ascii=False,sort_keys=True)


def prepare(source,output,root=ROOT):
    source=Path(source);output=Path(output)
    verify_bundle(source/'evidence_bundle.json',root)
    forms=load(source/'independent_review_forms.json')
    if len(forms)!=40:raise ValueError('40 original forms required')
    guide=(Path(root)/'E6/LITERATURE_REVIEW_GUIDE.md').read_text()
    output.mkdir(parents=True,exist_ok=False)
    for slot,name in ((1,'reviewer_A'),(2,'reviewer_B')):
        directory=output/name;directory.mkdir()
        lines=[f'# Literature review — reviewer {name[-1]}','',
            'Complete this document privately. Send only your completed document to the coordinator. Do not open the other reviewer document or coordinator reports until both reviews are submitted. Separate files do not enforce access control; distribute only the assigned document.','',
            '20 cases, seven checks each (140 decisions). Edit only the review-response JSON blocks. Use true/false for judgments; null means unanswered. Enter your identity and completion time in UTC (YYYY-MM-DDTHH:MM:SSZ) for each case. Set manual_check_completed to true only after all checks.','',
            'For every check, fill check_evidence with a brief rationale and source quote/location (or an explicit absence finding). Record extraction_errors and corrections as lists; use [] only when actually none. Originals are preserved; corrections require a new annotation version and renewed review.','',
            'The displayed four fields are MODEL extractions, not human judgments. Problem/method/result sidecars are separately attributed annotations and currently pending. Missing components require false checks and an omission explanation; do not invent annotations. A negative review is complete but does not accept the case.','',
            '## Frozen review guide','',guide.rstrip(),'']
        for form in (r for r in forms if r['reviewer_slot']==slot):
            packet=load(source/'packets'/(form['input_set_id']+'.json'))
            if digest({k:v for k,v in packet.items() if k!='packet_sha256'})!=form['packet_sha256']:
                raise ValueError('packet checksum mismatch')
            response=dict(form,check_evidence={key:{'rationale':None,'source_quote_or_location':None} for key in CHECKS})
            lines+=['## '+packet['input_set_id']+' — '+packet['target_title'],'',
                'Source field: '+packet['target_source_field']+' (full preserved evidence):','',
                '```text',packet['target_source_text'],'```','',
                'Saved model extraction (not a human review):','','```json',
                json.dumps(packet['actual_four_fields'],indent=2,ensure_ascii=False),'```','',
                'Separate source-component annotations (pending values are not extracted facts):','',
                '```json',json.dumps(packet['source_component_sidecar'],indent=2,ensure_ascii=False),'```','',
                'Mechanical attention flags (not judgments): '+json.dumps(packet['automatic_consistency_checks']['review_attention_flags']),'',
                'Review response:','','```review-response',json.dumps(response,indent=2,ensure_ascii=False),'```','']
        (directory/'review.md').write_text('\n'.join(lines))
    return {'documents':2,'cases_per_reviewer':20,'checks_per_reviewer':140,'human_reviews_pending':40}


def read_responses(path):
    blocks=re.findall(r'^```review-response\n(.*?)\n```\s*$',Path(path).read_text(),re.M|re.S)
    if len(blocks)!=20:raise ValueError('document must contain exactly 20 review-response blocks')
    return [json.loads(block) for block in blocks]


def ingest(source,reviewer_a,reviewer_b, *, components=None, adjudications=None):
    source=Path(source)
    verify_bundle(source/'evidence_bundle.json')
    originals=load(source/'independent_review_forms.json')
    expected={(r['reviewer_slot'],r['input_set_id']):r for r in originals}
    supplied_components=load(components) if components is not None else []
    sidecars={row['input_set_id']:row for row in supplied_components}
    if len(sidecars)!=len(supplied_components):raise ValueError('duplicate source-component sidecars')
    bundle_evidence=load(source/'evidence_bundle.json')
    extracted=load(ROOT/bundle_evidence['review_bundle_paths']['extraction_manifest'])['target_extractions']
    extracted_by_id={row['input_set_id']:row for row in extracted}
    if set(sidecars)-set(extracted_by_id):raise ValueError('foreign source-component sidecar')
    records=[];issues=[];seen=set();complete={};check_count=0
    for slot,path in ((1,reviewer_a),(2,reviewer_b)):
        for row in read_responses(path):
            key=(slot,row.get('input_set_id'))
            if key not in expected or key in seen:raise ValueError('foreign or duplicate review case')
            seen.add(key);base=expected[key]
            if any(row.get(k)!=base[k] for k in BINDINGS):raise ValueError('review binding changed')
            errors=[]
            if not nonempty_text(row.get('reviewer_id')):errors.append('reviewer identity missing')
            if not valid_utc(row.get('reviewed_at_utc')):errors.append('UTC completion time missing')
            if row.get('manual_check_completed') is not True:errors.append('manual completion not confirmed')
            for field in CHECKS:
                evidence=row.get('check_evidence',{}).get(field,{})
                answered=(type(row.get(field)) is bool and nonempty_text(evidence.get('rationale'))
                          and nonempty_text(evidence.get('source_quote_or_location')))
                check_count+=answered
                if not answered:errors.append(field+': Boolean judgment and source-grounded rationale required')
            if not nonempty_text(row.get('reviewer_notes')):errors.append('source notes missing')
            for field in ('extraction_errors','corrections'):
                if not isinstance(row.get(field),list):errors.append(field+': explicit list required')
            # Blank sidecars cannot support positive component judgments.
            packet=load(source/'packets'/(row['input_set_id']+'.json'))
            sidecar=sidecars.get(row['input_set_id'],packet['source_component_sidecar'])
            if row['input_set_id'] in sidecars:
                from literature_source_components import validate_components
                try:validate_components(extracted_by_id[row['input_set_id']],sidecar)
                except ValueError as exc:errors.append(str(exc))
            for component in ('problem','method','result'):
                if row.get(component+'_extraction_accurate') is True:
                    if not nonempty_text(sidecar['components'][component].get('text')):
                        errors.append(component+': missing annotation cannot pass; prepare a new source-bound version')
                    if row.get('source_component_sidecar_sha256')!=digest(sidecar):
                        errors.append(component+': sidecar digest required')
            records.append(row)
            if errors:issues.append({'input_set_id':key[1],'reviewer_slot':slot,'errors':errors})
            else:complete[key]=row
    disagreements=[];matching_negative=[]
    for unit in dict.fromkeys(r['input_set_id'] for r in originals):
        pair=[complete.get((slot,unit)) for slot in (1,2)]
        if not all(pair):continue
        if pair[0]['reviewer_id'].strip()==pair[1]['reviewer_id'].strip():
            raise ValueError('two distinct independent reviewer identities required')
        disputed=[k for k in CHECKS if pair[0][k]!=pair[1][k]]
        if disputed:
            disagreements.append({'input_set_id':unit,'disputed_checks':disputed,
                'review_records_sha256':digest(sorted(pair,key=lambda r:r['reviewer_id'])),
                'adjudicator_id':None,'adjudicated_at_utc':None,'rationale':None,
                'reviewer_ids':[r['reviewer_id'] for r in pair],**{k:None for k in CHECKS}})
        elif not all(pair[0][k] for k in CHECKS):matching_negative.append(unit)
    final_validation=None;final_blockers=[]
    if len(complete)!=40:final_blockers.append('40 complete independent source reviews required')
    else:
        from literature_finalization import validate_review_bundle
        from literature_source_components import validate_component_reviews
        try:
            paths=bundle_evidence['review_bundle_paths']
            bundle={key:load(ROOT/paths[key]) for key in ('candidate','proposal','extraction_manifest','worklist')}
            final_validation=validate_review_bundle(**bundle,records=records,
                adjudications=load(adjudications) if adjudications is not None else [],
                approval=load(ROOT/'E6/RESEARCHER_APPROVAL.json'),root=ROOT)
            if not final_validation['annotations_usable']:final_blockers.append('negative final checks require correction and renewed review')
            if components is None:final_blockers.append('completed attributed component sidecars required')
            else:validate_component_reviews(extracted,supplied_components,records,bundle['worklist']['selected_input_set_ids'])
        except (ValueError,OSError,KeyError,TypeError) as exc:final_blockers.append(str(exc))
    usable=final_validation is not None and final_validation['annotations_usable'] and not final_blockers
    return {'status':'validated_source_reviews' if usable else 'blocked_missing_or_unaccepted_source_reviews',
            'final_validation':final_validation,'scoring_blockers':final_blockers,
            'human_reviews_completed':len(complete),'human_reviews_pending':40-len(complete),
            'checks_with_judgment_and_evidence':check_count,'checks_pending':280-check_count,
            'issues':issues,'records':records,'adjudication_required':disagreements,
            'matching_negative_cases_require_correction':matching_negative,
            'annotations_usable':usable,'model_calls':0,
            'note':'Coordinator-only report. Identity and independence cannot be authenticated by software. Use existing validate_review_records / validate_review_bundle for final adjudications; matching negatives remain negative. Positive source-component checks require a separately prepared attributed sidecar and renewed source-bound review.'}


def export_validated(report,source,output,adjudications,components):
    """Export raw records for the existing scoring bundle; never edit configuration."""
    if report.get('annotations_usable') is not True or report.get('status')!='validated_source_reviews':
        raise ValueError('source scoring blocked: '+ '; '.join(report.get('scoring_blockers',[])))
    source=Path(source);output=Path(output).resolve()
    relative=output.relative_to(Path(ROOT).resolve())
    output.mkdir(parents=True,exist_ok=False)
    write_json(output/'actual_review_records.json',report['records'])
    write_json(output/'actual_adjudications.json',load(adjudications) if adjudications is not None else [])
    write_json(output/'source_components.json',load(components))
    paths=load(source/'evidence_bundle.json')['review_bundle_paths']
    paths=dict(paths,records=str(relative/'actual_review_records.json'),adjudications=str(relative/'actual_adjudications.json'))
    write_json(output/'review_bundle_paths.json',paths)
    write_json(output/'review_validation.json',report['final_validation'])
    return paths


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=ROOT/'E6/data/literature_evidence_finalized_v1')
    sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('prepare');a.add_argument('--output-dir',type=Path,required=True)
    a=sub.add_parser('ingest');a.add_argument('--reviewer-a',type=Path,required=True);a.add_argument('--reviewer-b',type=Path,required=True);a.add_argument('--output',type=Path,required=True);a.add_argument('--components',type=Path);a.add_argument('--adjudications',type=Path);a.add_argument('--export-dir',type=Path)
    args=p.parse_args()
    if args.command=='prepare':result=prepare(args.source,args.output_dir)
    else:
        result=ingest(args.source,args.reviewer_a,args.reviewer_b,components=args.components,adjudications=args.adjudications)
        write_json(args.output,result)
        if args.export_dir:export_validated(result,args.source,args.export_dir,args.adjudications,args.components)
        result={k:v for k,v in result.items() if k not in ('records','issues','adjudication_required')}
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
