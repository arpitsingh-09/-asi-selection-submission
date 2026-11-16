"""Prepare or explicitly execute frozen literature phases; never runs TEST.

Generation reuses literature_execution/run_seven_arms. Evaluation reuses
ConfiguredEvaluators and stays gated on actual validation and source reviews.
"""
import argparse
from contextlib import contextmanager
import fcntl
import json
from pathlib import Path
from researcher_approval import ROOT, digest, file_digest, safe_path
from run_literature_extraction import save, same_or_save, verify_execute_gates, verify_live_identity
from literature_execution import (prepare_literature_execution_context,
    validate_frozen_literature_context, execute_literature_input_set)
from finalize_literature_evidence import verify_bundle
from execution_preparation import make_configured_gemma_client
from question_pipeline import PipelineSettings
from evaluation import ARMS


def read(path):return json.loads(Path(path).read_text())


def prepare(root=ROOT):
    root=Path(root);config=read(root/'E6/config.json');lit=read(root/'E6/literature_testbed_config.json')
    evidence=root/'E6/data/literature_evidence_finalized_v1/evidence_bundle.json'
    verified=verify_bundle(evidence,root)
    candidate=read(safe_path(root,lit['candidate_manifest']['path']))
    sample=read(root/'E6/data/literature_sample_proposal_v1.json')
    references=read(safe_path(root,config['dataset']['literature_reference_selection_proposal']))
    context=prepare_literature_execution_context(candidate,sample,references,
        task=config['dataset']['task_text_by_testbed']['literature'])
    validate_frozen_literature_context(context,config,root=root)
    # Bind the exact saved target annotations, but never pass them to generation.
    manifest_path=safe_path(root,verified['review_bundle_paths']['extraction_manifest'])
    targets=read(manifest_path)['target_extractions']
    if len(targets)!=100 or len({r['input_set_id'] for r in targets})!=100:
        raise ValueError('100 unique verified extraction targets required')
    if {r['input_set_id'] for r in targets}!={r.paper_id for r in context.inputs}:
        raise ValueError('verified targets differ from generation cohort')
    paths=['E6/config.json','E6/evaluation_config.json','E6/RESEARCHER_APPROVAL.json','E6/PREREG.md',
        'E6/protocol.md','E6/question_pipeline_config.json','E6/literature_testbed_config.json',
        'E6/run_literature_experiment.py','E6/literature_execution.py','E6/orchestrator.py',
        'E6/question_pipeline.py','E6/token_budget.py','E6/ollama_adapter.py',
        'E6/execution_preparation.py','E6/configured_evaluators.py','E6/evaluation.py',
        'E6/prior_question_corpus.py','E6/run_literature_extraction.py',
        lit['candidate_manifest']['path'],'E6/data/literature_sample_proposal_v1.json',
        config['dataset']['literature_reference_selection_proposal'],
        config['dataset']['literature_selected_manifest'],str(evidence.relative_to(root)),
        str(manifest_path.relative_to(root))]
    paths += [str(p.relative_to(root)) for p in sorted((root/'prompts/e6').rglob('*.txt'))]
    plan={'schema_version':'e6-literature-seven-arm-plan-v1','context_sha256':context.context_sha256,
        'input_set_ids':[r.paper_id for r in context.inputs],'arms':list(ARMS),'planned_arm_cells':700,
        'verified_target_extractions':100,'seed':config['generation']['seed'],
        'generation_configuration':config['generation'],'generated_token_cap':config['inference_budget']['tokens_per_input_set_arm'],
        'file_hashes':{p:file_digest(root/p) for p in sorted(set(paths))},
        'retry_count':0,'TEST_access':False,'generation_evidence':'frozen cited-reference bundles only; target annotations excluded',
        'evaluation_blockers':['Actual independent evaluator validation remains required.',
            'Frozen reconstruction review_bundle_paths must bind genuine completed source reviews and adjudications.',
            'Attributed source-component annotations and their actual reviews must pass existing validators.']}
    plan['plan_sha256']=digest(plan)
    return config,context,plan


class CallJournalBlocked(BaseException):
    """Abort outside ordinary arm/evaluator error handling; never score corruption."""


class RecordedFailure(RuntimeError):
    def __init__(self,record):
        super().__init__(record['error']);self.audit_metadata=record.get('audit_metadata',{})


@contextmanager
def durable_calls(client,directory,identity):
    """Journal every backend call, including token probes. Replay replies, never requests."""
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    # Fail before orchestration: ordinary model exceptions are caught as arm failures.
    for path in directory.glob('*.started.json'):
        prefix=path.name.removesuffix('.started.json')
        if not (directory/(prefix+'.finished.json')).exists() and not (directory/(prefix+'.failed.json')).exists():
            raise ValueError('unresolved attempted call; no retry: '+str(path))
    for path in directory.glob('*.started.json'):
        request=read(path)
        if request.get('identity')!=identity:raise ValueError('journal source/plan changed')
        prefix=path.name.removesuffix('.started.json')
        finished=directory/(prefix+'.finished.json');failed=directory/(prefix+'.failed.json')
        if finished.exists() and failed.exists():raise ValueError('conflicting terminal call records')
        terminal=read(finished if finished.exists() else failed)
        if terminal.get('request_sha256')!=digest(request):raise ValueError('terminal request integrity mismatch')
        if finished.exists() and terminal.get('reply_sha256')!=digest(terminal.get('reply')):
            raise ValueError('saved reply integrity mismatch')
    for path in list(directory.glob('*.finished.json'))+list(directory.glob('*.failed.json')):
        prefix=path.name.rsplit('.',2)[0]
        if not (directory/(prefix+'.started.json')).exists():raise ValueError('orphan terminal call record')
    original=client._call;counter=0
    def call(stage,prompt,options,requested_limit):
        nonlocal counter
        counter+=1;prefix=directory/f'{counter:06d}'
        request={'identity':identity,'ordinal':counter,'stage':stage,'prompt':prompt,
            'options':options,'requested_limit':requested_limit}
        start=prefix.with_suffix('.started.json');finished=prefix.with_suffix('.finished.json');failed=prefix.with_suffix('.failed.json')
        if start.exists():
            if read(start)!=request:raise CallJournalBlocked('saved call sequence/source/settings changed')
            if finished.exists() and failed.exists():raise CallJournalBlocked('conflicting terminal call records')
            if finished.exists():
                saved=read(finished)
                if saved.get('request_sha256')!=digest(request) or saved.get('reply_sha256')!=digest(saved.get('reply')):
                    raise CallJournalBlocked('saved reply integrity mismatch')
                return saved['reply']
            if failed.exists():
                saved=read(failed)
                if saved.get('request_sha256')!=digest(request):raise CallJournalBlocked('saved failure binding changed')
                raise RecordedFailure(saved)
            raise CallJournalBlocked('unresolved attempted call; no retry')
        if finished.exists() or failed.exists():raise CallJournalBlocked('orphan terminal call record')
        save(start,request)
        try:reply=original(stage,prompt,options,requested_limit)
        except Exception as exc:
            save(failed,{'request_sha256':digest(request),'error':str(exc),'audit_metadata':getattr(exc,'audit_metadata',{})})
            raise
        save(finished,{'request_sha256':digest(request),'reply':reply,'reply_sha256':digest(reply)})
        return reply
    client._call=call
    try:yield
    finally:client._call=original


def evaluation_gates(config,evaluation,approval,client,components):
    from configured_evaluators import ConfiguredEvaluators
    from literature_finalization import validate_review_bundle
    from literature_source_components import validate_component_reviews
    evaluator=ConfiguredEvaluators(config,evaluation,approval,client)
    for decision,section in ((19,'reconstruction'),(20,'already_asked'),(21,'diversity'),(22,'question_type')):
        evaluator._require_execution(decision,section)
    paths=evaluation['reconstruction'].get('review_bundle_paths')
    if not isinstance(paths,dict):raise ValueError('genuine frozen literature review bundle required')
    bundle={k:read(safe_path(ROOT,p)) for k,p in paths.items()}
    validation=validate_review_bundle(**bundle,approval=approval,root=ROOT)
    if not validation['annotations_usable']:raise ValueError('source review corrections required')
    if components is None:raise ValueError('actual source-component sidecars required')
    validate_component_reviews(bundle['extraction_manifest']['target_extractions'],read(components),
        bundle['records'],bundle['worklist']['selected_input_set_ids'])
    return evaluator


def execute(config,context,plan,output,phase,components=None):
    output=Path(output).resolve()
    if any('heldout' in part.lower() or part=='..' for part in output.parts):
        raise ValueError('literature output must be separate from held-out TEST')
    verify_execute_gates(config)
    output.mkdir(parents=True,exist_ok=True)
    with (output/'execution.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        same_or_save(output/'experiment_plan.json',plan)
        client=make_configured_gemma_client(config,seed=config['generation']['seed'])
        evaluator=None;evaluation_identity=None
        if phase=='evaluation':
            evaluation=read(ROOT/'E6/evaluation_config.json')
            evaluator=evaluation_gates(config,evaluation,read(ROOT/'E6/RESEARCHER_APPROVAL.json'),client,components)
            evaluation_identity=digest({'plan':plan['plan_sha256'],
                'review_files':{p:file_digest(safe_path(ROOT,p)) for p in evaluation['reconstruction']['review_bundle_paths'].values()},
                'components_sha256':file_digest(Path(components))})
        runtime=verify_live_identity(config)
        same_or_save(output/('runtime_'+digest(runtime)[:16]+'.json'),runtime)
        settings=PipelineSettings.load()
        for row in context.inputs:
            directory=output/digest(row.paper_id)[:16]
            directory.mkdir(exist_ok=True)
            # Both phases reuse and verify the same final envelope/export interface.
            checkpoint=directory/(digest(row.paper_id)[:16]+'_literature_generation.json')
            if phase=='evaluation' and not checkpoint.exists():raise ValueError('evaluation requires completed generation checkpoint')
            journal_id=digest([plan['plan_sha256'],row.paper_id,'generation'])
            with durable_calls(client,directory/'generation_calls',journal_id):
                result=execute_literature_input_set(context,row.paper_id,settings,client,
                    checkpoint_dir=directory,token_budget_per_arm=plan['generated_token_cap'])
            if result['status']=='blocked':raise ValueError('literature generation blocked by existing protocol gates')
            if phase=='evaluation':
                envelope=result['generation_envelope']
                # Replay all calls for the set so partial evaluation never reissues a request.
                # Existing completed results are compared, never silently replaced.
                evaluator.calls=[]
                with durable_calls(client,directory/'evaluation_calls',digest([evaluation_identity,row.paper_id,'evaluation'])):
                    reconstruction=evaluator.score_literature(row.paper_id,envelope['arms'])
                    secondary={}
                    for arm in ARMS:
                        entry=envelope['arms'][arm]
                        if entry.get('execution_status')!='succeeded':continue
                        hypotheses=entry['output']['hypotheses'];questions={}
                        for h in hypotheses:
                            if h.get('question_text'):questions.setdefault(h['question_text'],h['hypothesis_id'])
                        q=[{'question_id':qid,'question':text} for text,qid in questions.items()]
                        secondary[arm]={'diversity':evaluator.score_diversity(row.paper_id,hypotheses),
                            'question_types':[evaluator.score_question_type(row.paper_id,x['question_id'],x['question']) for x in q],
                            'already_asked':evaluator.score_already_asked(row.paper_id,q) if q else {'status':'not_applicable_questionless_arm'}}
                same_or_save(directory/'reconstruction.json',reconstruction)
                for arm,value in secondary.items():same_or_save(directory/(arm+'_secondary.json'),value)
            print(json.dumps({'input_set_id':row.paper_id,'phase':phase,'generation_status':result['status']}),flush=True)
        same_or_save(output/(phase+'_completed.json'),{'plan_sha256':plan['plan_sha256'],'input_sets':100,'phase':phase})


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--execute',action='store_true');p.add_argument('--phase',choices=('generation','evaluation'),default='generation')
    p.add_argument('--components',type=Path);args=p.parse_args()
    config,context,plan=prepare()
    if not args.execute:
        args.output_dir.mkdir(parents=True,exist_ok=True);same_or_save(args.output_dir/'experiment_plan.json',plan)
        print(json.dumps({'status':'prepared_no_inference','input_sets':100,'arm_cells':700,'model_calls':0,'evaluation_blockers':plan['evaluation_blockers']},indent=2));return
    execute(config,context,plan,args.output_dir,args.phase,args.components)

if __name__=='__main__':main()
