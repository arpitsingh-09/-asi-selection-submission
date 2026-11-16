"""Explicit TEST launcher. No inference unless fresh mandatory readiness passes.

TRAIN generation is never called. An interrupted model request blocks resume.
"""
import argparse
import fcntl
import json
import os
import subprocess
from pathlib import Path
from test_readiness import readiness, read, checked_checkpoint
from researcher_approval import ROOT, digest
from evaluation import ARMS, evaluate_hypobench_dataset_level_recovery


def save(path, value):
    with path.open('x') as handle:
        json.dump(value,handle,sort_keys=True,ensure_ascii=False)
        handle.flush()
        os.fsync(handle.fileno())


def journal(client, directory):
    """Write intent before each call; never repeat a possibly issued request."""
    original = client._call
    counter = 0
    def call(stage, prompt, options, requested_limit):
        nonlocal counter
        counter += 1
        identity = digest([counter,stage,prompt,options,requested_limit])
        prefix = directory / identity
        started = prefix.with_suffix('.started.json')
        finished = prefix.with_suffix('.finished.json')
        failed = prefix.with_suffix('.failed.json')
        if finished.exists(): return json.loads(finished.read_text())['reply']
        if failed.exists() or started.exists():
            raise RuntimeError('Unresolved/failed call is terminal; no retry: '+str(prefix))
        save(started,dict(stage=stage,prompt=prompt,options=options,requested_limit=requested_limit))
        try:
            reply = original(stage,prompt,options,requested_limit)
            save(finished,{'reply':reply})
            return reply
        except Exception as exc:
            save(failed,{'error':str(exc),'audit_metadata':getattr(exc,'audit_metadata',{})})
            raise
    client._call = call


def execute(report, hdr, output):
    from execution_preparation import make_configured_gemma_client
    from inductive_execution import prepare_train_execution_context, evaluate_train_envelope
    from literature_execution import prepare_literature_execution_context, execute_literature_input_set
    from configured_evaluators import ConfiguredEvaluators
    from hypobench_policies import make_hypobench_prediction_policy, make_hypobench_recovery_policy, RECOVERY_POLICY_ID
    from question_pipeline import PipelineSettings
    config=read(ROOT,'E6/config.json'); ev=read(ROOT,'E6/evaluation_config.json')
    client=make_configured_gemma_client(config,seed=config['generation']['seed'])
    calls=output/'calls';calls.mkdir(exist_ok=True);journal(client,calls)
    evaluator=ConfiguredEvaluators(config,ev,read(ROOT,'E6/RESEARCHER_APPROVAL.json'),client)
    context=prepare_train_execution_context(read(ROOT,config['dataset']['data_generation_proposal']),read(ROOT,config['dataset']['data_evaluation_manifest']))
    predictor=make_hypobench_prediction_policy(client,ev['hypobench']['dataset_and_split']['declared_label_classes'],max_output_tokens=ev['hypobench']['prediction_policy']['max_output_tokens'])
    recovery=make_hypobench_recovery_policy(client,max_output_tokens=ev['hypobench']['recovery_judgment_policy']['max_output_tokens'])
    lit=read(ROOT,'E6/literature_testbed_config.json')
    literature=prepare_literature_execution_context(read(ROOT,lit['candidate_manifest']['path']),read(ROOT,'E6/data/literature_sample_proposal_v1.json'),read(ROOT,config['dataset']['literature_reference_selection_proposal']),task=config['dataset']['task_text_by_testbed']['literature'])
    for bed, rows in (('data',context.inputs),('literature',literature.inputs)):
        for row in rows:
            folder=output/digest(row.paper_id)[:16];folder.mkdir(exist_ok=True)
            if bed=='data':
                job=next(j for j in report['jobs'] if j['input_set_id']==row.paper_id)
                if job['generation_checkpoint'] is None:
                    continue # terminal missing 0007; never invoke TRAIN generation
                envelope=checked_checkpoint(read(ROOT,job['generation_checkpoint']),context)
                evaluate_train_envelope(context,envelope,predictor,batch_size=1,max_workers=1,
                    hdr_inputs_by_arm=hdr.get(row.paper_id),checkpoint_dir=folder)
            else:
                result=execute_literature_input_set(literature,row.paper_id,PipelineSettings.load(),client,checkpoint_dir=folder)
                envelope=result['generation_envelope']
                path=folder/'reconstruction.json'
                if not path.exists(): save(path,evaluator.score_literature(row.paper_id,envelope['arms']))
            for arm in ARMS:
                entry=envelope['arms'][arm]
                if entry.get('execution_status')!='succeeded': continue
                hypotheses=entry['output']['hypotheses']
                texts=[h['text'] for h in hypotheses]
                path=folder/(arm+'_secondary.json')
                if path.exists(): continue
                result={'diversity':evaluator.score_diversity(row.paper_id,hypotheses),'question_types':[]}
                questions=[]
                for h in hypotheses:
                    text=h.get('question_text')
                    if text and text not in [q['question'] for q in questions]:
                        questions.append({'question_id':h['hypothesis_id'],'question':text})
                for q in questions:
                    result['question_types'].append(evaluator.score_question_type(row.paper_id,q['question_id'],q['question']))
                result['already_asked']=evaluator.score_already_asked(row.paper_id,questions) if questions else {'status':'not_applicable_questionless_arm'}
                if bed=='data':
                    result['planted_recovery']=evaluate_hypobench_dataset_level_recovery(row.paper_id,texts,context.test_manifest['dataset_ground_truth']['hypotheses'],recovery,dataset_provenance={'manifest_sha256':context.test_manifest['manifest_sha256']},policy_id=RECOVERY_POLICY_ID)
                save(path,result)


def execute_heldout_accuracy(report, output):
    """Only the frozen 501-row prediction policy; no other scoring callbacks."""
    from execution_preparation import make_configured_gemma_client
    from inductive_execution import prepare_train_execution_context, evaluate_train_envelope
    from hypobench_policies import make_hypobench_prediction_policy
    from run_literature_extraction import verify_live_identity
    if report.get('evaluation_phase') != 'heldout_accuracy' or report.get('status') != 'READY':
        raise ValueError('held-out accuracy phase authorization required')
    config=read(ROOT,'E6/config.json'); evaluation=read(ROOT,'E6/evaluation_config.json')
    # Read-only live identity checks precede construction/inference; no identity probe generation.
    save(output/'actual_runtime_identity.json',verify_live_identity(config))
    client=make_configured_gemma_client(config,seed=config['generation']['seed'])
    calls=output/'calls';calls.mkdir(exist_ok=True);journal(client,calls)
    predictor=make_hypobench_prediction_policy(client,
        evaluation['hypobench']['dataset_and_split']['declared_label_classes'],
        max_output_tokens=evaluation['hypobench']['prediction_policy']['max_output_tokens'])
    context=prepare_train_execution_context(read(ROOT,config['dataset']['data_generation_proposal']),
        read(ROOT,config['dataset']['data_evaluation_manifest']))
    results=[]
    for row in context.inputs:
        job=next(j for j in report['jobs'] if j['input_set_id']==row.paper_id)
        if ':TRAIN-SET:0007:' in row.paper_id or job['generation_checkpoint'] is None:
            continue
        envelope=checked_checkpoint(read(ROOT,job['generation_checkpoint']),context)
        folder=output/digest(row.paper_id)[:16];folder.mkdir(exist_ok=True)
        result=evaluate_train_envelope(context,envelope,predictor,batch_size=1,max_workers=1,
            hdr_inputs_by_arm=None,checkpoint_dir=folder)
        results.append({'generation_input_set_id':row.paper_id,
            'heldout_evaluable_arms':[arm for arm,value in result['evaluations'].items()
                if value.get('status')=='evaluated'],
            'full_metric_status':result['evaluation_status']})
    save(output/'heldout_phase_summary.json',{'evaluation_phase':'heldout_accuracy',
        'full_evaluation_complete':False,'generation_sets':results,
        'deferred_scoring_gates':report['deferred_scoring_gates'],
        'note':'Accuracy-only phase. HDR, literature and secondary metrics remain pending; missing generation is not zero.'})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--phase',choices=('full','heldout_accuracy'),default='full')
    parser.add_argument('--hdr-inputs',type=Path)
    args=parser.parse_args()
    if args.phase=='full' and args.hdr_inputs is None:
        parser.error('--hdr-inputs is required for the full evaluation')
    if args.phase=='heldout_accuracy' and args.hdr_inputs is not None:
        parser.error('HDR inputs are not consumed by the heldout_accuracy phase')
    hdr=json.loads(args.hdr_inputs.read_text()) if args.hdr_inputs else None
    report=readiness(hdr_inputs=hdr,phase=args.phase)
    if report['status']!='READY':
        print(json.dumps(report['mandatory_blockers'],indent=2));return 2
    # New launcher and readiness implementation must be reviewable in local HEAD.
    for name in ('E6/run_confirmatory_test.py','E6/test_readiness.py'):
        committed=subprocess.check_output(['git','show','HEAD:'+name],cwd=ROOT)
        if committed!=(ROOT/name).read_bytes(): raise ValueError('Commit exact TEST implementation locally before execution: '+name)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    with (args.output_dir/'execution.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        # Exclusive launch marker prevents a second invocation from reissuing any
        # request after a crash. Existing records require explicit reconciliation.
        save(args.output_dir/'launch_started.json',{'readiness_sha256':report['manifest_sha256']})
        if args.phase=='heldout_accuracy':
            execute_heldout_accuracy(report,args.output_dir)
        else:
            execute(report,hdr,args.output_dir)
        save(args.output_dir/'launch_completed.json',{'status':'phase_completed','phase':args.phase,
            'full_evaluation_complete':args.phase=='full'})
    return 0

if __name__=='__main__':raise SystemExit(main())
