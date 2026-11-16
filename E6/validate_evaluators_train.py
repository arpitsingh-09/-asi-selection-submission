"""TRAIN-only evaluator validation evidence; never authorizes TEST scoring.

No labels or passing thresholds are invented. Exact identity controls have
logical expected answers. Other pairs/classifications await human labels.
Uses original evaluator primitives, not confirmatory scoring entry points.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from researcher_approval import ROOT, digest, file_digest
from configured_evaluators import ConfiguredEvaluators
from execution_preparation import make_configured_gemma_client
from evaluation import classify_question
from verify_gemma3_local import _request_json, tokenizer_metadata_summary


def save(path, value):
    with path.open('x') as handle:
        json.dump(value,handle,ensure_ascii=False,sort_keys=True,indent=2)
        handle.flush()
        __import__('os').fsync(handle.fileno())


def build_cases(root=ROOT):
    paths=[]
    for directory in ('priority10_train_batch001','priority10_train_batch002'):
        paths.extend(sorted((root/'E6/runs'/directory).glob('*_generation_envelope.json')))
    pool=[]
    for path in paths:
        saved=json.loads(path.read_text())
        if saved['checkpoint_sha256']!=digest({k:v for k,v in saved.items() if k!='checkpoint_sha256'}):raise ValueError('TRAIN checkpoint checksum mismatch')
        envelope=saved['envelope']
        if ':TRAIN-SET:' not in envelope['paper_id'] or ':TRAIN-SET:0007:' in envelope['paper_id']:raise ValueError('TRAIN-only source required')
        entry=envelope['arms']['QH']
        if entry['execution_status']!='succeeded':continue
        hypotheses=entry['output']['hypotheses']
        seen=set()
        for h in hypotheses:
            question=h.get('question_text')
            if question and question not in seen:
                seen.add(question)
                pool.append(dict(unit=envelope['paper_id'],question=question,hypothesis=h['text'],
                    hypothesis_id=h['hypothesis_id'],source=str(path.relative_to(root)),source_file_sha256=file_digest(path)))
    if len(pool)<4:raise ValueError('four real TRAIN questions required')
    selected=sorted(pool,key=lambda r:digest([r['unit'],r['question']]))[:4]
    cases=[]
    for i,row in enumerate(selected):
        other=selected[(i+1)%len(selected)]
        for section,rubric,a,b,key,expected in (
            ('reconstruction','similarity',row['hypothesis'],row['hypothesis'] if i<2 else other['hypothesis'],'similarity',5 if i<2 else None),
            ('already_asked','same_question',row['question'],row['question'] if i<2 else other['question'],'same_question',True if i<2 else None),
            ('diversity','distinctness',row['hypothesis'],row['hypothesis'] if i<2 else other['hypothesis'],'distinct',False if i<2 else None),
            ('question_type','question_type',row['question'],None,'type',None)):
            cases.append(dict(case_id=f'{section}-{i+1:02d}',section=section,rubric=rubric,a=a,b=b,key=key,
                expected=expected,reference_kind='logical_identity_control' if expected is not None else 'human_reference_required',
                sources=[row] if i<2 or b is None else [row,other]))
    return cases


def summarize(cases, results):
    output={}
    for section in ('reconstruction','already_asked','diversity','question_type'):
        selected=[c for c in cases if c['section']==section]
        rows=[r for r in results if r['section']==section]
        controls=[r for r in rows if r['expected'] is not None]
        parsed=[r for r in rows if r['status']=='returned_valid']
        output[section]={'status':'incomplete_validation','planned_calls':len(selected),'attempted_calls':len(rows),
            'valid_response_count':len(parsed),'valid_response_rate':len(parsed)/len(selected),
            'logical_control_count':len(controls),'logical_control_correct':sum(r.get('prediction')==r['expected'] for r in controls),
            'human_reference_labels_required':[c['case_id'] for c in selected if c['expected'] is None],
            'human_agreement':None,'acceptance_threshold':None,
            'missing_acceptance_rule':'Frozen protocol supplies no numerical validation acceptance threshold; do not infer a pass from this pilot.'}
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args();out=args.output_dir
    out.mkdir(parents=True,exist_ok=False)
    config=json.loads((ROOT/'E6/config.json').read_text());ev=json.loads((ROOT/'E6/evaluation_config.json').read_text())
    cases=build_cases();save(out/'cases.json',cases)
    work=[{'case_id':c['case_id'],'section':c['section'],'a':c['a'],'b':c['b'],'allowed_labels':
           {'similarity':[1,2,3,4,5],'same_question':[True,False],'distinct':[True,False,None],'type':['constructive','analytic','other','ambiguous']}[c['key']],
           'label':None,'reviewer':None,'rationale':None,'sources':c['sources']} for c in cases if c['expected'] is None]
    save(out/'human_labels_required.json',work)
    files={c['sources'][0]['source'] for c in cases}|{'E6/config.json','E6/evaluation_config.json','E6/RESEARCHER_APPROVAL.json','E6/PREREG.md'}
    files.update(b['path'] for b in ev['configured_rubrics'].values())
    snapshot={p:file_digest(ROOT/p) for p in sorted(files)}
    results=[]
    provenance={'started_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'TRAIN-only development validation; no confirmatory TEST calls',
        'selection':'four actual QH questions sorted by SHA256(canonical [unit,question]) from preserved first two TRAIN checkpoints',
        'implementation_sha256':file_digest(Path(__file__)),'preserved_file_hashes':snapshot,
        'frozen_validation_statuses_modified':False,'semantic_labels_supplied_by_assistant':False,
        'limitations':['small operational pilot, not a preregistered validation sample','same-model evaluator, no independent human reference yet','no constructive/other/ambiguous coverage guaranteed','TRAIN similarity controls do not validate literature target extraction','no historical cutoff invented; binary identity rubric tested without claiming historical already-asked rates']}
    save(out/'provenance_started.json',provenance)
    try:
        runtime=_request_json('/api/version');tags=_request_json('/api/tags');show=_request_json('/api/show',{'model':config['generation']['model'],'verbose':True})
        tag=next(r for r in tags['models'] if r.get('name')==config['generation']['model'] or r.get('model')==config['generation']['model'])
        verified=json.loads((ROOT/config['generation']['development_runtime_probe_report']).read_text())['steps']['01_identity']
        if runtime['version']!=config['generation']['backend_version'] or tag['digest'].removeprefix('sha256:')!=verified['tag_digest'].removeprefix('sha256:') or tokenizer_metadata_summary(show)['metadata_sha256']!=config['generation']['tokenizer_metadata_fingerprint_sha256']:raise ValueError('runtime/model/tokenizer identity differs from frozen settings')
        save(out/'actual_runtime_identity.json',{'version':runtime,'tag':tag,'tokenizer':tokenizer_metadata_summary(show)})
        client=make_configured_gemma_client(config,seed=config['generation']['seed'])
        p=ConfiguredEvaluators(config,ev,json.loads((ROOT/'E6/RESEARCHER_APPROVAL.json').read_text()),client)
        for c in cases:
            save(out/(c['case_id']+'_started.json'),c)
            start=len(p.calls)
            r={**c,'status':'failed','prediction':None}
            try:
                if c['rubric']=='question_type':
                    p._prompt('question_type')
                    record=classify_question(c['sources'][0]['unit'],c['case_id'],c['a'],p._reply,model_configuration=client.model_configuration)
                    r['evaluation_record']=record
                    if record['status']!='succeeded':raise ValueError(str(record.get('error')))
                    prediction=record['parsed_output']['type']
                else:
                    values={'similarity':{'FIELD':'main hypothesis','GENERATED':c['a'],'TARGET':c['b']},
                            'same_question':{'TYPE_A':'generated research question','TEXT_A':c['a'],'TYPE_B':'TRAIN generated research question','TEXT_B':c['b']},
                            'distinctness':{'HYPOTHESIS_A':c['a'],'HYPOTHESIS_B':c['b']}}[c['rubric']]
                    prediction=p._scalar(c['rubric'],values,c['key'])
                r.update(status='returned_valid',prediction=prediction)
            except Exception as exc:r.update(error=str(exc),audit_metadata=getattr(exc,'audit_metadata',{}))
            r['calls']=p.calls[start:];save(out/(c['case_id']+'_result.json'),r);results.append(r)
            print(c['case_id'],r['status'],r['prediction'],flush=True)
    except Exception as exc:
        save(out/'execution_blocker.json',{'error':str(exc),'type':type(exc).__name__,'no_retry':True})
        print('Execution blocked:',exc,flush=True)
    unchanged=all(file_digest(ROOT/p)==sha for p,sha in snapshot.items())
    report={'validations_completed':0,'total_validations':4,'sections':summarize(cases,results),
            'preserved_sources_and_settings_unchanged':unchanged,'model_call_attempts':len(results),
            'human_action':'Label the 10 entries in human_labels_required.json using the frozen rubrics, record reviewer identity and rationale; independently define/authorize acceptance criteria and assess missing category coverage. Literature extraction/reviews remain separately required.',
            'TEST_calls':0,'TRAIN_generation_retries':0}
    save(out/'report.json',report)
    return 0 if len(results)==len(cases) and unchanged else 2

if __name__=='__main__':raise SystemExit(main())
