"""Offline finalization of actual fixed-prompt extraction and Decision 24 packets.

No model client is constructed. Mechanical checks never supply human judgments.
The original raw output, four-field schema and frozen settings remain unchanged.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from researcher_approval import ROOT, digest, file_digest, valid_utc
from run_literature_extraction import prepare
from literature_finalization import validate_extracted_candidates, extraction_source, verify_seal
from literature_source_components import component_form
from prepare_literature_sample_proposal import build_proposed_manual_review_worklist, build_literature_extraction_manifest
from hypobench_policies import _strict_json_object
from evaluation import extract_reference_targets, TARGET_EXTRACTION_PROMPT


def require(value,message):
    if not value:raise ValueError(message)


def save(path,value):
    with Path(path).open('x') as h:json.dump(value,h,indent=2,sort_keys=True,ensure_ascii=False)


def valid_backend_utc(value):
    # Python 3.9 fromisoformat accepts only 3/6 fractional digits; Ollama emits
    # variable RFC3339 precision. Normalize solely for parsing, retaining raw data.
    if not isinstance(value,str):return False
    normalized=re.sub(r'\.(\d+)(?=Z$|\+00:00$)',
                      lambda m:'.'+(m.group(1)+'000000')[:6],value)
    return valid_utc(normalized)


def check_one(original,extracted,checkpoint,started,response,plan):
    unit=original['input_set_id'];field,text=extraction_source(original)
    model=plan['model_configuration'];prompt=TARGET_EXTRACTION_PROMPT.read_text().replace('{{TARGET_PAPER_TEXT}}',text)
    identity=digest({'source':original,'model':model,'plan':plan['plan_sha256'],'prompt_sha256':file_digest(TARGET_EXTRACTION_PROMPT)})
    require(checkpoint.get('identity')==identity,unit+': checkpoint identity mismatch')
    require(checkpoint.get('checkpoint_sha256')==digest({k:v for k,v in checkpoint.items() if k!='checkpoint_sha256'}),unit+': checkpoint checksum mismatch')
    require(checkpoint.get('extracted_candidate')==extracted,unit+': checkpoint differs from final extraction manifest')
    require(started.get('identity')==response.get('identity')==identity,unit+': request/reply identity mismatch')
    require(started.get('prompt')==prompt and started.get('prompt_sha256')==hashlib.sha256(prompt.encode()).hexdigest(),unit+': request prompt/source mismatch')
    require(started.get('stage')=='reference_target_extraction' and started.get('content_attempt')==1,unit+': stage/attempt mismatch')
    require(started.get('model_configuration')==model,unit+': frozen extraction model mismatch')
    require(valid_utc(started.get('started_at_utc')) and valid_utc(response.get('finished_at_utc')),unit+': request timestamps missing')
    reply=response['reply']
    require(response.get('reply_sha256')==digest(reply),unit+': saved response checksum mismatch')
    options={'num_ctx':model['context_limit'],'num_predict':model['max_output_tokens'],'seed':model['seed'],'temperature':model['temperature'],'top_p':model['top_p']}
    require(started['client_configuration']['generation_options']==options,unit+': client decoding mismatch')
    adapter=reply['adapter_metadata']
    require(reply.get('http_status')==adapter.get('http_status')==200 and adapter.get('done') is True,unit+': incomplete backend response')
    require(reply.get('model')==adapter.get('model')==model['model'],unit+': returned model mismatch')
    require(adapter.get('stage')=='reference_target_extraction' and adapter.get('prompt_sha256')==hashlib.sha256(prompt.encode()).hexdigest(),unit+': backend prompt/stage mismatch')
    require(adapter.get('generation_settings',{}).get('options')==options and adapter.get('requested_output_token_limit')==model['max_output_tokens'],unit+': backend decoding/token limit mismatch')
    require(valid_backend_utc(adapter.get('created_at')),unit+': backend timestamp missing')
    require(type(reply.get('input_tokens')) is int and type(reply.get('output_tokens')) is int and 0<=reply['output_tokens']<=model['max_output_tokens'],unit+': usage metadata invalid')
    require(reply['input_tokens']==adapter.get('prompt_eval_count') and reply['output_tokens']==adapter.get('eval_count') and reply.get('total_tokens')==reply['input_tokens']+reply['output_tokens'],unit+': usage metadata mismatch')
    parsed=_strict_json_object(reply['raw_response'])
    require(set(parsed)=={'research_question','main_hypothesis','research_question_explicit','main_hypothesis_explicit'},unit+': non-four-field schema')
    for name in ('research_question','main_hypothesis'):
        require(parsed[name] is None or (isinstance(parsed[name],str) and bool(parsed[name].strip())),unit+': invalid extracted text')
        require(type(parsed[name+'_explicit']) is bool,unit+': invalid explicitness flag')
    def replay(stage,rendered):
        require(stage==started['stage'] and rendered==started['prompt'],unit+': offline record replay mismatch')
        return reply
    reconstructed=extract_reference_targets(unit,text,replay,model_configuration=model)
    require(reconstructed==extracted['target_extraction'] and reconstructed['status']=='succeeded',unit+': raw response/extraction provenance disagreement')
    literal={};flags=[]
    for name in ('research_question','main_hypothesis'):
        value=parsed[name];spans=[]
        if value:
            start=text.find(value)
            while start>=0:
                spans.append([start,start+len(value)]);start=text.find(value,start+1)
        literal[name]={'value_present':value is not None,'verbatim_source_spans':spans,
            'semantic_support':'requires_independent_review'}
        if value is None and parsed[name+'_explicit']:flags.append(name+': null text with explicit=true')
        elif value and parsed[name+'_explicit'] and not spans:flags.append(name+': explicit=true but no literal span; paraphrase/explicitness requires review')
    return {'input_set_id':unit,'verified':True,'source_field':field,'source_text_sha256':hashlib.sha256(text.encode()).hexdigest(),
        'prompt_tokens':reply['input_tokens'],'generated_tokens':reply['output_tokens'],'automatic_checks':{
            'checkpoint_integrity':True,'frozen_source_binding':True,'request_and_response_provenance':True,'four_field_schema':True,
            'literal_source_checks':literal,'review_attention_flags':flags,
            'human_checks_completed':False}}


def verify_run(source,root=ROOT):
    source=Path(source).resolve();root=Path(root).resolve()
    read=lambda name:json.loads((source/name).read_text())
    config,approval,candidate,proposal,originals,plan=prepare(root)
    require(read('extraction_plan.json')==plan,'saved plan differs from frozen source/model/committed implementation')
    manifest=read('extraction_manifest.json');verify_seal(manifest)
    extracted=validate_extracted_candidates(candidate,proposal,manifest['target_extractions'],plan['model_configuration'])
    require(manifest==build_literature_extraction_manifest(proposal,extracted,model_configuration=plan['model_configuration']),'extraction manifest packaging mismatch')
    worklist=read('review_worklist.json')
    require(worklist==build_proposed_manual_review_worklist(extracted,proposal),'20-case review worklist differs from frozen sample')
    sidecars=read('source_component_sidecars_pending.json');by_sidecar={r['input_set_id']:r for r in sidecars}
    require(len(by_sidecar)==len(sidecars)==100,'100 unique source sidecars required')
    verified=[];files={str(p.relative_to(root)):file_digest(p) for p in sorted(source.rglob('*.json'))}
    require(len([p for p in source.iterdir() if p.is_dir()])==100,'unexpected/missing extraction checkpoint directories')
    for original,row in zip(originals,extracted):
        unit=original['input_set_id'];directory=source/digest(unit)[:16]
        require(not (directory/'request_failed.json').exists(),unit+': unexpected failure record')
        get=lambda name:json.loads((directory/name).read_text())
        verified.append(check_one(original,row,get('extraction_checkpoint.json'),get('request_started.json'),get('response.json'),plan))
        require(by_sidecar.get(unit)==component_form(row),unit+': pending sidecar differs from actual extraction/source binding')
    # Saved identity snapshot supports historical runtime provenance, not a new call.
    runtime_paths=list(source.glob('runtime_*.json'));require(bool(runtime_paths),'saved runtime identity absent')
    probe=json.loads((root/config['generation']['development_runtime_probe_report']).read_text())['steps']['01_identity']
    for path in runtime_paths:
        r=json.loads(path.read_text())
        require(r['version']['version']==config['generation']['backend_version'],'runtime backend mismatch')
        require(r['tag']['digest'].removeprefix('sha256:')==probe['tag_digest'].removeprefix('sha256:'),'runtime tag identity mismatch')
        require(r['tokenizer']['metadata_sha256']==config['generation']['tokenizer_metadata_fingerprint_sha256'],'runtime tokenizer mismatch')
    return {'config':config,'approval':approval,'candidate':candidate,'proposal':proposal,'manifest':manifest,
            'worklist':worklist,'sidecars':sidecars,'verified':verified,'source_file_hashes':files}


CATEGORIES={
 'research_question_extraction_accurate':['wrong_research_objective','unsupported_inference','scope_changed','question_missing_or_null_incorrect'],
 'main_hypothesis_extraction_accurate':['not_the_main_hypothesis','result_or_method_confused_with_hypothesis','unsupported_direction_or_relationship','hypothesis_missing_or_null_incorrect'],
 'research_question_explicitness_accurate':['explicit_vs_inferred_disagreement','source_evidence_insufficient'],
 'main_hypothesis_explicitness_accurate':['explicit_vs_inferred_disagreement','source_evidence_insufficient'],
 'problem_extraction_accurate':['source_component_missing','unsupported_component','incorrect_source_span','meaning_changed'],
 'method_extraction_accurate':['source_component_missing','unsupported_component','incorrect_source_span','meaning_changed'],
 'result_extraction_accurate':['source_component_missing','unsupported_component','incorrect_source_span','meaning_changed']}


def finalize(source,output,root=ROOT):
    root=Path(root).resolve();source=Path(source).resolve();output=Path(output).resolve();result=verify_run(source,root)
    policy=next(d for d in result['approval']['decisions'] if d['id']==24)['resolved_details']['review_policy']
    checks=policy['check_fields'];require(set(checks)==set(CATEGORIES),'unsupported source review checks')
    by_id={r['input_set_id']:r for r in result['manifest']['target_extractions']}
    by_sidecar={r['input_set_id']:r for r in result['sidecars']};by_check={r['input_set_id']:r for r in result['verified']}
    packets=[];forms=[];adjudications=[]
    for unit in result['worklist']['selected_input_set_ids']:
        row=by_id[unit];field,text=extraction_source(row);sidecar=by_sidecar[unit]
        packet={'input_set_id':unit,'target_title':row['target']['title'],'target_source_field':field,
            'target_source_text':text,'target_source_text_sha256':by_check[unit]['source_text_sha256'],
            'actual_extraction_record':row['target_extraction'],'actual_four_fields':row['target_extraction']['parsed_output'],
            'source_component_sidecar':sidecar,'source_component_sidecar_status':'pending_actual_annotations',
            'automatic_consistency_checks':by_check[unit]['automatic_checks'],
            'source_quote_blocks':[{'quote':text[start:start+400],'character_span':[start,min(start+400,len(text))],
                'semantic_role':'unclassified_exact_source_block'} for start in range(0,len(text),400)],
            'disagreement_categories':CATEGORIES,'human_review_complete':False}
        packet['packet_sha256']=digest(packet);packets.append(packet)
        for slot in (1,2):
            forms.append({'input_set_id':unit,'reviewer_slot':slot,'reviewer_id':None,'reviewed_at_utc':None,'manual_check_completed':False,
                'packet_sha256':packet['packet_sha256'],'extraction_sha256':digest(row['target_extraction']),
                'target_source_text_sha256':packet['target_source_text_sha256'],'review_guide_sha256':policy['guide_sha256'],
                'source_component_sidecar_sha256':None,'source_component_binding_instruction':'Bind completed attributed sidecar digest before final source-component judgments.',
                **{key:None for key in checks},'disagreement_categories':None,'source_quotes_and_locations':None,
                'reviewer_notes':None,'extraction_errors':None,'corrections':None})
        adjudications.append({'input_set_id':unit,'status':'conditional_on_genuine_independent_disagreement',
            'adjudicator_id':None,'adjudicated_at_utc':None,'review_records_sha256':None,'rationale':None,
            'disputed_checks':None,**{key:None for key in checks}})
    output.mkdir(parents=True,exist_ok=False);(output/'packets').mkdir()
    for packet in packets:save(output/'packets'/(packet['input_set_id']+'.json'),packet)
    save(output/'verified_extractions.json',result['verified']);save(output/'source_component_sidecars_pending.json',result['sidecars'])
    save(output/'independent_review_forms.json',forms);save(output/'conditional_adjudication_forms.json',adjudications)
    # These files are intentionally empty actual decision records, distinct from
    # pending forms. They cannot pass the existing frozen review validators.
    save(output/'actual_review_records.json',[]);save(output/'actual_adjudications.json',[])
    md=['# Twenty-case independent literature source review','',
        'Two reviewers work independently on all seven checks. Third-person adjudication only for genuine disagreements.',
        'Automatic literal-span checks do not establish semantic correctness or explicitness. All human decisions remain blank.',
        'Add attributed problem/method/result source annotations to the separate sidecar before source-component checks.',
        'Unsupported or missing components require negative checks, not invented annotations. Preserve originals and renew review after corrections.','']
    for packet in packets:
        md.extend(['## '+packet['input_set_id']+' — '+packet['target_title'],'',
            'Source quotation ('+packet['target_source_field']+'):','',packet['target_source_text'],'',
            'Actual fixed-prompt output:','', '```json',json.dumps(packet['actual_four_fields'],indent=2,ensure_ascii=False),'```','',
            'Mechanical review-attention flags: '+json.dumps(packet['automatic_consistency_checks']['review_attention_flags']),'',
            'Problem/method/result sidecar: actual annotation pending.','',
            *['- '+key+': reviewer 1 ______; reviewer 2 ______. Categories: '+', '.join(CATEGORIES[key]) for key in checks],'',
            'Actual source quotes/spans, errors/corrections, reviewer identities and UTC times: ______',''])
    (output/'review_sheet.md').write_text('\n'.join(md))
    report={'schema_version':'e6-verified-literature-evidence-v1','verified_extractions':len(result['verified']),
        'review_packets_completed':len(packets),'human_reviews_completed':0,'human_reviews_required':40,
        'required_check_decisions':280,'source_components_pending_for_review_cases':60,
        'adjudication_policy':'Independent third adjudicator only for actual disagreement; binds sorted reviewer records digest.',
        'review_bundle_paths':{'candidate':'E6/data/literature_citation_verified_manifest_v1.json','proposal':'E6/data/literature_sample_proposal_v1.json',
            'extraction_manifest':str((source/'extraction_manifest.json').relative_to(root)),
            'worklist':str((source/'review_worklist.json').relative_to(root)),
            'records':str((output/'actual_review_records.json').relative_to(root)),
            'adjudications':str((output/'actual_adjudications.json').relative_to(root))},
        'source_file_hashes':result['source_file_hashes'],
        'frozen_file_hashes':{p:file_digest(root/p) for p in ('E6/config.json','E6/evaluation_config.json','E6/PREREG.md','E6/RESEARCHER_APPROVAL.json','E6/LITERATURE_REVIEW_GUIDE.md')},
        'prepared_file_hashes':{str(p.relative_to(output)):file_digest(p) for p in sorted(output.rglob('*')) if p.is_file()},
        'implementation_sha256':file_digest(Path(__file__)),'model_calls':0,'TEST_evaluation':False,
        'automatic_verification_complete':True,'annotations_usable':False,
        'blockers':['40 independent source reviews, 280 seven-check Boolean decisions, and actual problem/method/result component annotations or honest unsupported/negative findings.',
            'Independent adjudication of actual disagreements, correction and renewed review for failed checks.',
            'Four evaluator semantic validations remain separate requirements.',
            'HDR reference-feature definition and 125 genuine cell judgments remain absent.'],
        'note':'Successful fixed-prompt extraction is not human-validated reference truth; null fields remain null.'}
    save(output/'evidence_bundle.json',report)
    verify_bundle(output/'evidence_bundle.json',root)
    return report


def verify_bundle(path,root=ROOT):
    path=Path(path);root=Path(root);r=json.loads(path.read_text())
    require(r.get('schema_version')=='e6-verified-literature-evidence-v1','unknown finalized literature bundle')
    for relative,sha in {**r['source_file_hashes'],**r['frozen_file_hashes']}.items():
        require(file_digest(root/relative)==sha,'saved/frozen literature source changed: '+relative)
    for relative,sha in r['prepared_file_hashes'].items():
        require(not Path(relative).is_absolute() and '..' not in Path(relative).parts,'foreign prepared artifact')
        require(file_digest(path.parent/relative)==sha,'prepared review artifact changed: '+relative)
    require(r.get('verified_extractions')==100 and r.get('review_packets_completed')==20,'incomplete literature evidence inventory')
    require(r.get('annotations_usable') is False,'automatic evidence bundle cannot authorize human validation')
    return r


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True)
    args=p.parse_args();r=finalize(args.source,args.output_dir)
    print(json.dumps({key:r[key] for key in ('verified_extractions','review_packets_completed','human_reviews_required','required_check_decisions','annotations_usable','model_calls')},indent=2))

if __name__=='__main__':main()
