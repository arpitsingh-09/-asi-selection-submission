"""Explicit fixed-prompt reference extraction; never seven-arm or TEST scoring.

Prepare/verify is offline. --execute makes only new reference-extraction calls.
Terminal success/failure and ambiguous interrupted requests are never retried.
"""
import argparse
import copy
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import subprocess
from researcher_approval import ROOT, digest, file_digest, safe_path, load_approval_errors
from literature_finalization import (extraction_source, verify_seal, require_approved_sample,
    validate_extracted_candidates)
from prepare_literature_sample_proposal import (verify_sample_proposal,
    build_literature_extraction_manifest, build_proposed_manual_review_worklist)
from evaluation import extract_reference_targets, TARGET_EXTRACTION_PROMPT
from execution_preparation import make_configured_gemma_client
from literature_source_components import component_form


def save(path,value):
    with Path(path).open('x') as h:
        json.dump(value,h,ensure_ascii=False,sort_keys=True,indent=2);h.flush();os.fsync(h.fileno())


def same_or_save(path,value):
    if path.exists():
        if json.loads(path.read_text())!=value:raise ValueError('existing artifact changed: '+str(path))
    else:save(path,value)


def prepare(root=ROOT):
    load=lambda p:json.loads(safe_path(root,p).read_text())
    config=load('E6/config.json');approval=load('E6/RESEARCHER_APPROVAL.json')
    literature=load('E6/literature_testbed_config.json')
    cp=literature['candidate_manifest']['path'];pp='E6/data/literature_sample_proposal_v1.json'
    candidate=load(cp);proposal=load(pp);selected=load(config['dataset']['literature_selected_manifest']);verify_seal(selected)
    require_approved_sample(approval,proposal,root)
    rows=verify_sample_proposal(candidate,proposal)
    if rows!=selected['input_sets']:raise ValueError('selected source sample changed')
    model=next(d for d in approval['decisions'] if d['id']==24)['resolved_details']['extraction_model_configuration']
    gen=config['generation']
    if any(model.get(k)!=gen.get(k) for k in ('model','temperature','top_p','seed','max_output_tokens','context_limit','immutable_version_or_digest')):raise ValueError('extraction model differs from frozen generation settings')
    source_files=(cp,pp,config['dataset']['literature_selected_manifest'],'E6/config.json','E6/RESEARCHER_APPROVAL.json','prompts/e6/09_target_extraction.txt')
    plan={'schema_version':'e6-fixed-literature-extraction-plan-v1','model_configuration':model,
        'input_set_ids':[r['input_set_id'] for r in rows],
        'source_file_hashes':{p:file_digest(safe_path(root,p)) for p in source_files},
        'implementation_file_hashes':{p:file_digest(root/p) for p in ('E6/run_literature_extraction.py','E6/literature_source_components.py')},
        'new_call_count_maximum':len(rows),'retry_count':0,'TEST_scoring':False,
        'note':'Reference annotations only; no arm-generation evidence, scoring or validation approval.'}
    plan['plan_sha256']=digest(plan)
    return config,approval,candidate,proposal,rows,plan


def run_one(row,model,client,directory,plan_id):
    directory.mkdir(parents=True,exist_ok=True)
    if directory.is_symlink():raise ValueError('symlink checkpoint directory prohibited')
    field,text=extraction_source(row)
    identity=digest({'source':row,'model':model,'plan':plan_id,'prompt_sha256':file_digest(TARGET_EXTRACTION_PROMPT)})
    checkpoint=directory/'extraction_checkpoint.json';started=directory/'request_started.json'
    response=directory/'response.json';failed=directory/'request_failed.json'
    if checkpoint.exists():
        saved=json.loads(checkpoint.read_text())
        if saved.get('identity')!=identity or saved.get('checkpoint_sha256')!=digest({k:v for k,v in saved.items() if k!='checkpoint_sha256'}):raise ValueError('extraction checkpoint changed')
        return saved['extracted_candidate']
    if started.exists():
        if json.loads(started.read_text()).get('identity')!=identity:raise ValueError('interrupted request source/policy changed')
        if not response.exists() and not failed.exists():raise ValueError('unresolved interrupted extraction; no retry permitted')
    elif response.exists() or failed.exists():raise ValueError('orphan response/failure without request record')
    def call(stage,prompt):
        if response.exists():
            saved=json.loads(response.read_text())
            if saved.get('identity')!=identity or saved.get('reply_sha256')!=digest(saved.get('reply')):raise ValueError('saved model reply changed')
            return saved['reply']
        if failed.exists():
            saved=json.loads(failed.read_text())
            if saved.get('identity')!=identity:raise ValueError('failure identity mismatch')
            raise RuntimeError(saved['error'])
        save(started,{'identity':identity,'stage':stage,'prompt':prompt,'prompt_sha256':__import__('hashlib').sha256(prompt.encode()).hexdigest(),
            'model_configuration':model,'client_configuration':client.model_configuration,
            'started_at_utc':datetime.now(timezone.utc).isoformat(),'content_attempt':1})
        try:
            reply=client.call_with_token_limit(stage,prompt,max_output_tokens=model['max_output_tokens'])
            save(response,{'identity':identity,'reply':reply,'reply_sha256':digest(reply),'finished_at_utc':datetime.now(timezone.utc).isoformat()})
            return reply
        except Exception as exc:
            save(failed,{'identity':identity,'error':str(exc),'audit_metadata':getattr(exc,'audit_metadata',{}),'finished_at_utc':datetime.now(timezone.utc).isoformat()})
            raise
    extraction=extract_reference_targets(row['input_set_id'],text,call,model_configuration=model)
    extracted=copy.deepcopy(row);extracted.update(target_extraction=extraction,target_extraction_source_field=field)
    saved={'identity':identity,'extracted_candidate':extracted};saved['checkpoint_sha256']=digest(saved);save(checkpoint,saved)
    return extracted


def verify_execute_gates(config,root=ROOT):
    from validate_protocol import validate_config, validate_preregistration_git_commit
    from development_runtime_probe import validate_runtime_evidence
    errors=validate_config(config,(root/'E6/protocol.md').read_text(),root=root)
    errors+=load_approval_errors(root,finalization=True)+validate_preregistration_git_commit(root)+validate_runtime_evidence(config,root=root)
    if errors:raise ValueError('; '.join(errors))
    for name in ('E6/run_literature_extraction.py','E6/literature_source_components.py'):
        committed=subprocess.check_output(['git','show','HEAD:'+name],cwd=root)
        if committed!=(root/name).read_bytes():raise ValueError('Commit exact extraction implementation locally before execution: '+name)


def verify_live_identity(config):
    from verify_gemma3_local import _request_json, tokenizer_metadata_summary
    gen=config['generation'];runtime=_request_json('/api/version');tags=_request_json('/api/tags')
    tag=next(r for r in tags['models'] if r.get('name')==gen['model'] or r.get('model')==gen['model'])
    show=_request_json('/api/show',{'model':gen['model'],'verbose':True})
    probe=json.loads(safe_path(ROOT,gen['development_runtime_probe_report']).read_text())['steps']['01_identity']
    tokenizer=tokenizer_metadata_summary(show)
    if runtime['version']!=gen['backend_version'] or tag['digest'].removeprefix('sha256:')!=probe['tag_digest'].removeprefix('sha256:') or tokenizer['metadata_sha256']!=gen['tokenizer_metadata_fingerprint_sha256']:raise ValueError('live runtime/model/tokenizer mismatch')
    return {'version':runtime,'tag':tag,'tokenizer':tokenizer}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    config,approval,candidate,proposal,rows,plan=prepare()
    if not args.execute:
        args.output_dir.mkdir(parents=True,exist_ok=True);same_or_save(args.output_dir/'extraction_plan.json',plan)
        print(json.dumps({'status':'prepared_no_inference','source_targets':len(rows),'model_calls':0,'plan_sha256':plan['plan_sha256']}));return 0
    verify_execute_gates(config)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    with (args.output_dir/'execution.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        same_or_save(args.output_dir/'extraction_plan.json',plan)
        runtime=verify_live_identity(config)
        # Preserve an identity snapshot for each invocation; runtime timestamps can change.
        identity_path=args.output_dir/('runtime_'+digest(runtime)[:16]+'.json');same_or_save(identity_path,runtime)
        client=make_configured_gemma_client(config,seed=config['generation']['seed'])
        extracted=[]
        for row in rows:
            extracted.append(run_one(row,plan['model_configuration'],client,args.output_dir/digest(row['input_set_id'])[:16],plan['plan_sha256']))
        validate_extracted_candidates(candidate,proposal,extracted,plan['model_configuration'])
        manifest=build_literature_extraction_manifest(proposal,extracted,model_configuration=plan['model_configuration'])
        same_or_save(args.output_dir/'extraction_manifest.json',manifest)
        same_or_save(args.output_dir/'source_component_sidecars_pending.json',[component_form(r) for r in extracted])
        try:
            worklist=build_proposed_manual_review_worklist(extracted,proposal)
            same_or_save(args.output_dir/'review_worklist.json',worklist)
        except ValueError as exc:
            same_or_save(args.output_dir/'review_preparation_blocked.json',{'error':str(exc),'failed_extractions_preserved':True})
        print(json.dumps({'status':'extraction_complete_reviews_pending','succeeded':manifest['successful_extraction_count'],'failed':manifest['failed_extraction_count'],'TEST_scoring':False}))
    return 0

if __name__=='__main__':raise SystemExit(main())
