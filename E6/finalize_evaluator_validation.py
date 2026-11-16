"""Finalize saved TRAIN validation evidence offline; never calls a model.

Keeps frozen validation statuses unchanged. Logical controls are scored as such,
not treated as human reference labels or sufficient semantic validation.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from evaluation import _hash_json, _render
from hypobench_policies import _strict_json_object
from researcher_approval import ROOT, file_digest, safe_path
from validate_evaluators_train import build_cases, save

SECTIONS=('reconstruction','already_asked','diversity','question_type')


def require(condition, reason):
    if not condition:raise ValueError(reason)


def strict_equal(a,b):
    return type(a) is type(b) and a==b


def verify_response(case, result, started, config, evaluation, root):
    cid=case['case_id']
    require(started==case,cid+': started record differs from planned case')
    require(all(result.get(k)==v for k,v in case.items()),cid+': result differs from case')
    require(result.get('status')=='returned_valid',cid+': response not valid')
    require(len(result.get('calls',[]))==1,cid+': expected exactly one recorded call')
    call=result['calls'][0]
    binding=evaluation['configured_rubrics'][case['rubric']]
    prompt_path=safe_path(root,binding['path'])
    require(file_digest(prompt_path)==binding['file_sha256'],cid+': rubric hash mismatch')
    values={
        'similarity':{'FIELD':'main hypothesis','GENERATED':case['a'],'TARGET':case['b']},
        'same_question':{'TYPE_A':'generated research question','TEXT_A':case['a'],
            'TYPE_B':'TRAIN generated research question','TEXT_B':case['b']},
        'distinctness':{'HYPOTHESIS_A':case['a'],'HYPOTHESIS_B':case['b']},
        'question_type':{'QUESTION':case['a']},
    }[case['rubric']]
    prompt=_render(prompt_path.read_text(),values)
    require(call.get('prompt')==prompt,cid+': rendered prompt mismatch')
    require(call.get('prompt_sha256')==_hash_json(prompt),cid+': canonical prompt hash mismatch')
    stage='question_type_classification' if case['rubric']=='question_type' else case['rubric']
    require(call.get('stage')==stage,cid+': stage mismatch')
    metadata=call['model_metadata'];adapter=metadata['adapter_metadata']
    require(adapter.get('prompt_sha256')==hashlib.sha256(prompt.encode()).hexdigest(),cid+': backend prompt hash mismatch')
    require(metadata.get('model')==config['generation']['model'] and adapter.get('model')==config['generation']['model'],cid+': model mismatch')
    gen=config['generation']
    expected={'num_ctx':gen['context_limit'],'num_predict':gen['max_output_tokens'],
              'temperature':gen['temperature'],'top_p':gen['top_p'],'seed':gen['seed']}
    require(adapter['generation_settings']['options']==expected,cid+': frozen decoding mismatch')
    require(adapter.get('http_status')==200 and adapter.get('done') is True,cid+': backend completion missing')
    require(adapter.get('requested_output_token_limit')==gen['max_output_tokens'],cid+': request token limit mismatch')
    require(bool(adapter.get('created_at')),cid+': backend timestamp absent')
    for key in ('prompt_eval_count','eval_count'):
        require(type(adapter.get(key)) is int and adapter[key]>=0,cid+': token accounting absent')
    require(metadata.get('input_tokens')==adapter['prompt_eval_count'] and metadata.get('output_tokens')==adapter['eval_count'],cid+': usage disagreement')
    parsed=_strict_json_object(call['raw_output'])
    require(set(parsed)=={case['key']},cid+': response fields differ from rubric')
    value=parsed[case['key']]
    if case['key']=='similarity':require(type(value) is int and 1<=value<=5,cid+': invalid similarity')
    elif case['key'] in ('same_question','distinct'):require(type(value) is bool,cid+': invalid Boolean')
    else:require(value in ('constructive','analytic','other','ambiguous'),cid+': invalid category')
    require(strict_equal(value,result['prediction']),cid+': saved prediction differs from raw response')
    if case['rubric']=='question_type':
        record=result['evaluation_record']
        require(record.get('status')=='succeeded' and record.get('raw_output')==call['raw_output'],cid+': classifier record mismatch')
        require(record.get('parsed_output')==parsed,cid+': classifier parsed output mismatch')
    if case['expected'] is not None:
        require(case['a']==case['b'] and case['reference_kind']=='logical_identity_control',cid+': unsupported reference label')
        expected_value={'similarity':5,'same_question':True,'distinctness':False}[case['rubric']]
        require(strict_equal(case['expected'],expected_value),cid+': identity reference mismatch')
    return {'case_id':cid,'section':case['section'],'prediction':value,'expected':case['expected'],
            'reference_kind':case['reference_kind'],'prompt_tokens':adapter['prompt_eval_count'],
            'generated_tokens':adapter['eval_count'],'timestamp':adapter['created_at'],
            'raw_output':call['raw_output'],'rubric_path':binding['path']}


def metrics(rows):
    sections={}
    for section in SECTIONS:
        selected=[r for r in rows if r['section']==section]
        controls=[r for r in selected if r['expected'] is not None]
        correct=sum(strict_equal(r['prediction'],r['expected']) for r in controls)
        sections[section]={'status':'responses_verified_independent_validation_pending',
            'responses_verified':len(selected),'logical_identity_controls':len(controls),
            'logical_identity_correct':correct,'logical_identity_accuracy':correct/len(controls) if controls else None,
            'logical_identity_MAE':sum(abs(r['prediction']-r['expected']) for r in controls)/len(controls) if section=='reconstruction' and controls else None,
            'independent_human_reference_count':0,'independent_human_agreement':None,
            'remaining_pilot_judgments':[r['case_id'] for r in selected if r['expected'] is None],
            'prediction_counts':dict(Counter(str(r['prediction']) for r in selected)),
            'acceptance_threshold':None,'validated':False}
    return sections


def review_markdown(cases, rows, *, include_outputs):
    by_id={r['case_id']:r for r in rows}
    text=['# TRAIN evaluator pilot: '+('examples and model outputs' if include_outputs else 'independent label sheet'),'',
          'Ten independent judgments are required for this pilot. These are not existing human labels.',
          'Use the linked frozen rubric. Record a label, reviewer identity, date and short rationale.',
          'Prefer labeling the blind sheet before opening the model-output sheet; disclosure of model outputs can bias agreement.',
          'No passing threshold or adequacy decision is supplied by this sheet.','']
    for c in cases:
        if c['expected'] is not None:continue
        r=by_id[c['case_id']]
        text.extend(['## '+c['case_id'],'',f"Rubric: `{r['rubric_path']}`",'',
                     'A: '+c['a'],''])
        if c['b'] is not None:text.extend(['B: '+c['b'],''])
        text.extend(['Source: '+', '.join(f"`{s['unit']}` / `{s['hypothesis_id']}`" for s in c['sources']),''])
        if include_outputs:text.extend(['Evaluator response: `'+r['raw_output']+'`',''])
        text.extend(['Independent label: ______  Reviewer/date: ______','Rationale: ______',''])
    return '\n'.join(text)


def finalize(source, output, root=ROOT):
    source=Path(source);output=Path(output);root=Path(root)
    # Snapshot every input artifact, including calls and previous reports.
    before={p.name:file_digest(p) for p in sorted(source.iterdir()) if p.is_file()}
    load=lambda name:json.loads((source/name).read_text())
    provenance=load('provenance_started.json');cases=load('cases.json')
    require(cases==build_cases(root),'saved case selection differs from actual preserved TRAIN sources')
    require(len(cases)==16 and len({c['case_id'] for c in cases})==16,'16 unique cases required')
    require(file_digest(root/'E6/validate_evaluators_train.py')==provenance['implementation_sha256'],'validation implementation changed since execution')
    for relative,sha in provenance['preserved_file_hashes'].items():
        require(file_digest(safe_path(root,relative))==sha,'preserved artifact changed: '+relative)
    config=json.loads((root/'E6/config.json').read_text());evaluation=json.loads((root/'E6/evaluation_config.json').read_text())
    runtime=load('actual_runtime_identity.json');gen=config['generation']
    require(runtime['version']['version']==gen['backend_version'],'saved backend identity mismatch')
    probe=json.loads(safe_path(root,gen['development_runtime_probe_report']).read_text())
    require(runtime['tag']['digest'].removeprefix('sha256:')==probe['steps']['01_identity']['tag_digest'].removeprefix('sha256:'),'saved tag digest mismatch')
    require(runtime['tokenizer']['metadata_sha256']==gen['tokenizer_metadata_fingerprint_sha256'],'saved tokenizer mismatch')
    rows=[]
    require({p.name for p in source.glob('*_result.json')}=={c['case_id']+'_result.json' for c in cases},'missing or unexpected result files')
    for c in cases:
        rows.append(verify_response(c,load(c['case_id']+'_result.json'),load(c['case_id']+'_started.json'),config,evaluation,root))
    worklist=load('human_labels_required.json')
    require({r['case_id'] for r in worklist}=={c['case_id'] for c in cases if c['expected'] is None},'human worklist mismatch')
    require(all(r.get('label') is None and r.get('reviewer') is None for r in worklist),'human labels populated; explicit independent evidence ingestion needed')
    sections=metrics(rows)
    report={'schema_version':'e6-evaluator-validation-finalization-v1','validations_genuinely_completed':0,'total_validations':4,
        'saved_responses_verified':len(rows),'logical_identity_controls_correct':sum(strict_equal(r['prediction'],r['expected']) for r in rows if r['expected'] is not None),
        'logical_identity_controls_total':sum(r['expected'] is not None for r in rows),'sections':sections,
        'prompt_tokens':sum(r['prompt_tokens'] for r in rows),'generated_tokens':sum(r['generated_tokens'] for r in rows),
        'source_artifact_file_hashes':before,'verifier_implementation_sha256':file_digest(Path(__file__)),
        'frozen_validation_statuses':{k:evaluation[k]['validation_status'] for k in SECTIONS},
        'inference_calls_this_finalization':0,'minimum_independent_pilot_judgments':10,
        'mandatory_remaining':['Independent labels for 2 cross-text similarities, 2 cross-question equivalences, 2 hypothesis distinctness judgments and 4 question categories.',
            'Researcher assesses validation adequacy and missing category/score coverage; no frozen numeric acceptance threshold exists.',
            'Literature reconstruction requires separate source-bound extraction and Decision 24 independent source reviews; TRAIN controls cannot provide them.'],
        'limitations':['Logical identity controls are exact references, not independent human judgments.',
            'Historical semantic-matcher rubric checks do not establish temporal eligibility, retrieval recall or comprehensive literature coverage.',
            'Four question-type predictions do not establish accuracy or coverage of unobserved categories.',
            'This source snapshot verifies recorded provenance and integrity; it does not independently attest execution on the host.']}
    output.mkdir(parents=True,exist_ok=False)
    save(output/'verified_responses.json',rows);save(output/'validation_status.json',report)
    save(output/'human_review.json',[dict(r,evaluator_output=next(x['raw_output'] for x in rows if x['case_id']==r['case_id'])) for r in worklist])
    for name,expose in (('human_review_blind.md',False),('human_review_with_outputs.md',True)):
        with (output/name).open('x') as handle:handle.write(review_markdown(cases,rows,include_outputs=expose))
    require(before=={p.name:file_digest(p) for p in sorted(source.iterdir()) if p.is_file()},'saved run changed during finalization')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True);parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args();report=finalize(args.source,args.output_dir)
    print(json.dumps({k:report[k] for k in ('validations_genuinely_completed','saved_responses_verified','logical_identity_controls_correct','logical_identity_controls_total','minimum_independent_pilot_judgments','prompt_tokens','generated_tokens')},indent=2))

if __name__=='__main__':main()
