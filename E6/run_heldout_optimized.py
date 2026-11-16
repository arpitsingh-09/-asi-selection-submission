"""Explicit held-out continuation with exact-request reuse and bounded transport.

Default prepares offline only. --execute is forbidden while any source launcher
holds its execution lock. No prior attempted request is ever reissued.
"""
import argparse
from contextlib import contextmanager
import hashlib
import fcntl
import json
import os
from pathlib import Path
import tempfile
import threading
from researcher_approval import ROOT, digest, file_digest
from run_literature_extraction import save, same_or_save
from hypobench_policies import make_hypobench_prediction_policy
from hdr_pipeline import checked_forms


class PriorAttemptUnavailable(RuntimeError):pass


class UnsafeContinuation(BaseException):
    """Abort outside prediction-invalid handling when integrity or resume is unsafe."""


def read(path):return json.loads(Path(path).read_text())


def request_key(model,stage,prompt,options,limit):
    return digest({'model':model,'stage':stage,'prompt':prompt,'options':options,'requested_limit':limit})


@contextmanager
def stopped_source(source):
    """Hold a read-only shared lock; active legacy launcher holds exclusive lock."""
    source=Path(source)
    with (source/'execution.lock').open('r') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_SH|fcntl.LOCK_NB)
        except BlockingIOError:raise ValueError('source TEST is still running/locked; do not start a second experiment')
        yield


class ExactRequestCache:
    def __init__(self,client,directory,*,unresolved_policy='block'):
        if unresolved_policy not in ('block','retain-invalid'):raise ValueError('explicit unresolved policy required')
        self.client=client;self.directory=Path(directory);self.directory.mkdir(parents=True,exist_ok=True)
        self.policy=unresolved_policy;self.guard=threading.Lock();self.locks={}
        self.original=client._call;self.executed=0;self.reused=0;self.retained_invalid=0
    def request(self,stage,prompt,options,limit):
        return {'model':self.client.model,'stage':stage,'prompt':prompt,'options':dict(options),'requested_limit':limit}
    def lock_for(self,key):
        with self.guard:return self.locks.setdefault(key,threading.Lock())
    def import_source(self,source):
        """Only call while stopped_source is held. Raw replies, including invalid JSON, are preserved."""
        source=Path(source);calls=source/'calls';inventory=[]
        for started in sorted(calls.glob('*.started.json'),key=lambda p:(p.stat().st_mtime_ns,p.name)):
            old=read(started)
            request=self.request(old['stage'],old['prompt'],old['options'],old['requested_limit'])
            if request['stage']!='hypobench_heldout_prediction':raise ValueError('foreign source request stage')
            expected=dict(self.client.generation_options);expected['num_predict']=min(expected['num_predict'],32)
            if request['options']!=expected or request['requested_limit']!=32:raise ValueError('source decoding/cap differs from frozen prediction policy')
            key=digest(request);finished=started.with_name(started.name.replace('.started.json','.finished.json'))
            failed=started.with_name(started.name.replace('.started.json','.failed.json'))
            if finished.exists() and failed.exists():raise ValueError('conflicting prior terminal markers')
            terminal=None
            if finished.exists():
                reply=read(finished)['reply'];metadata=reply.get('adapter_metadata',{})
                import hashlib
                if (reply.get('model')!=self.client.model or metadata.get('model')!=self.client.model
                    or metadata.get('prompt_sha256')!=hashlib.sha256(request['prompt'].encode()).hexdigest()
                    or metadata.get('generation_settings',{}).get('options')!=request['options']
                    or metadata.get('requested_output_token_limit')!=32
                    or metadata.get('http_status')!=200 or metadata.get('done') is not True):
                    raise ValueError('prior reply does not bind exact model/prompt/decoding/completion')
                terminal={'status':'finished','reply':reply,'reply_sha256':digest(reply)}
            elif failed.exists():terminal={'status':'failed','error':read(failed).get('error','prior attempted request failed'),'audit_metadata':read(failed).get('audit_metadata',{})}
            elif self.policy=='block':raise ValueError('unresolved prior attempted call; no retry: '+str(started))
            else:terminal={'status':'unresolved_retained_invalid','error':'explicitly retained missing prior response; never reissued'}
            origin={'started_path':str(started.resolve()),'started_sha256':file_digest(started)}
            if finished.exists():origin.update(terminal_path=str(finished.resolve()),terminal_sha256=file_digest(finished))
            if failed.exists():origin.update(terminal_path=str(failed.resolve()),terminal_sha256=file_digest(failed))
            path=self.directory/(key+'.json')
            entry={'request':request,'terminal':terminal,'origin':origin};entry['entry_sha256']=digest(entry)
            if path.exists():
                prior=self.load(path,request)
                # Different outputs for one deterministic request invalidate reuse.
                if prior['terminal']['status']!=terminal['status'] or (terminal['status']=='finished' and prior['terminal']['reply'].get('raw_response')!=terminal['reply'].get('raw_response')):
                    raise ValueError('conflicting prior responses/attempt states for identical request')
            else:save(path,entry)
            inventory.append({'request_key':key,**origin,'status':terminal['status']})
        # Terminal records without request intent cannot be safely imported.
        for path in list(calls.glob('*.finished.json'))+list(calls.glob('*.failed.json')):
            if not path.with_name(path.name.rsplit('.',2)[0]+'.started.json').exists():raise ValueError('orphan prior call record')
        return inventory
    def load(self,path,request):
        entry=read(path)
        if entry.get('entry_sha256')!=digest({k:v for k,v in entry.items() if k!='entry_sha256'}) or entry.get('request')!=request:
            raise ValueError('request cache integrity/binding mismatch')
        terminal=entry['terminal']
        if terminal['status']=='finished' and terminal.get('reply_sha256')!=digest(terminal.get('reply')):raise ValueError('cached reply checksum mismatch')
        return entry
    def __call__(self,stage,prompt,options,limit):
        request=self.request(stage,prompt,options,limit);key=digest(request);path=self.directory/(key+'.json')
        with self.lock_for(key):
            if path.exists():
                try:entry=self.load(path,request)
                except (ValueError,KeyError,TypeError) as exc:raise UnsafeContinuation(str(exc)) from exc
                terminal=entry['terminal']
                if terminal['status']=='finished':
                    with self.guard:self.reused+=1
                    return terminal['reply']
                if terminal['status'] in ('failed','unresolved_retained_invalid'):
                    with self.guard:self.retained_invalid+=1
                    raise PriorAttemptUnavailable(terminal['error'])
                raise UnsafeContinuation('unresolved optimized-run call; never reissued')
            started=self.directory/(key+'.started.json')
            if started.exists():
                try:
                    if read(started)!=request:raise ValueError('optimized attempt marker binding mismatch')
                except (ValueError,KeyError,TypeError,OSError) as exc:raise UnsafeContinuation(str(exc)) from exc
                if self.policy!='retain-invalid':raise UnsafeContinuation('unresolved optimized-run call; never reissued')
                entry={'request':request,'terminal':{'status':'unresolved_retained_invalid',
                    'error':'explicitly retained missing optimized response; never reissued'},
                    'origin':{'started_path':str(started.resolve()),'started_sha256':file_digest(started)}}
                entry['entry_sha256']=digest(entry);save(path,entry)
                with self.guard:self.retained_invalid+=1
                raise PriorAttemptUnavailable(entry['terminal']['error'])
            save(started,request)
            try:
                with self.guard:self.executed+=1
                reply=self.original(stage,prompt,options,limit)
                terminal={'status':'finished','reply':reply,'reply_sha256':digest(reply)}
            except Exception as exc:
                terminal={'status':'failed','error':str(exc),'audit_metadata':getattr(exc,'audit_metadata',{})}
                entry={'request':request,'terminal':terminal,'origin':{'kind':'new_request'}};entry['entry_sha256']=digest(entry);save(path,entry)
                raise
            entry={'request':request,'terminal':terminal,'origin':{'kind':'new_request'}};entry['entry_sha256']=digest(entry);save(path,entry)
            return reply


def prepare():
    """Validate split isolation and compute exact hypothesis/observation reuse potential."""
    from inductive_execution import prepare_train_execution_context
    config=read(ROOT/'E6/config.json');evaluation=read(ROOT/'E6/evaluation_config.json')
    context=prepare_train_execution_context(read(ROOT/config['dataset']['data_generation_proposal']),read(ROOT/config['dataset']['data_evaluation_manifest']))
    forms,missing=checked_forms()
    unique_hypotheses={tuple(f['hypotheses']) for f in forms}
    observations={r['evidence'] for r in context.test_manifest['records']}
    maximum=len(forms)*context.test_manifest['record_count'];unique=len(unique_hypotheses)*len(observations)
    files=['E6/run_heldout_optimized.py','E6/inductive_execution.py','E6/hypobench_policies.py',
        'E6/prepare_hypobench_inductive.py','E6/ollama_adapter.py','E6/config.json','E6/evaluation_config.json',
        'E6/PREREG.md','prompts/e6/13_hypobench_heldout_prediction.txt']
    plan={'schema_version':'e6-exact-request-heldout-v1','context_sha256':context.context_sha256,
        'policy':'identical model, rendered prompt, options and output cap only; no semantic cache',
        'planned_cells':140,'evaluable_cells':len(forms),'excluded_generation_cells':len(missing),
        'test_rows':context.test_manifest['record_count'],'prediction_assignments':maximum,
        'unique_hypothesis_sets':len(unique_hypotheses),'unique_test_observations':len(observations),
        'maximum_unique_requests':unique,'exact_reuse_assignments':maximum-unique,
        'ideal_request_count_speedup':maximum/unique,
        'source_hashes':{p:file_digest(ROOT/p) for p in files},
        'test_manifest_sha256':context.test_manifest['manifest_sha256'],'training_source_sha256':context.proposal['training_source_sha256'],
        'heldout_scope':'TRAIN/TEST text overlap rejected; TEST labels stripped from prediction input. Historical researcher TEST-label exposure remains disclosed in PREREG.',
        'new_inference_calls_this_preparation':0}
    plan['plan_sha256']=digest(plan)
    return config,evaluation,context,plan


def check_run_binding(path,binding):
    """Permit only this recovery implementation over the original frozen run plan."""
    if not path.exists():
        same_or_save(path,binding);return
    prior=read(path)
    if prior==binding:return
    legacy_hash='f3cd84edc49fd1197800bc0a579cfb2b5ad9721ac3d6e414e338a42e28bb50b8'
    compatible=read(path)
    if compatible['plan']['source_hashes']['E6/run_heldout_optimized.py']!=legacy_hash:
        raise ValueError('existing run implementation is not the supported recovery predecessor')
    compatible['plan']['source_hashes']['E6/run_heldout_optimized.py']=binding['plan']['source_hashes']['E6/run_heldout_optimized.py']
    compatible['plan']['plan_sha256']=digest({k:v for k,v in compatible['plan'].items() if k!='plan_sha256'})
    if prior['plan']['plan_sha256']!=digest({k:v for k,v in prior['plan'].items() if k!='plan_sha256'}) or compatible!=binding:
        raise ValueError('existing run binding changed beyond recovery implementation')


def _validated_progress(path,kind):
    if not path.exists():return None,None
    if not path.is_file():raise ValueError('progress artifact is not a regular file: '+str(path))
    raw=path.read_bytes();prior=json.loads(raw)
    if not isinstance(prior,dict):raise ValueError('progress artifact must contain a JSON object')
    if kind=='summary':
        if prior.get('evaluation_phase')!='heldout_accuracy' or not isinstance(prior.get('generation_sets'),list):
            raise ValueError('existing progress summary identity/schema mismatch')
        cells=set()
        for item in prior['generation_sets']:
            if (not isinstance(item,dict) or not isinstance(item.get('generation_input_set_id'),str)
                    or not isinstance(item.get('evaluated_arms'),list)
                    or not all(isinstance(arm,str) for arm in item['evaluated_arms'])):
                raise ValueError('existing progress summary cell identity/schema mismatch')
            for arm in item['evaluated_arms']:
                cell=(item['generation_input_set_id'],arm)
                if cell in cells:raise ValueError('duplicate cell in existing progress summary')
                cells.add(cell)
        if prior.get('full_evaluation_complete') is True and len(cells)!=125:
            raise ValueError('existing completed summary lacks all 125 evaluated cells')
    elif (prior.get('phase')!='heldout_accuracy' or prior.get('status')!='phase_completed'
          or type(prior.get('full_evaluation_complete')) is not bool):
        raise ValueError('existing completion marker identity/schema mismatch')
    return prior,hashlib.sha256(raw).hexdigest()


def atomic_progress_update(path,value,*,binding,kind):
    """Atomically update only the two resumable progress artifacts."""
    path=Path(path);expected={'heldout_phase_summary.json':'summary','launch_completed.json':'marker'}
    if expected.get(path.name)!=kind:raise ValueError('atomic progress update is restricted to heldout progress artifacts')
    binding_path=path.parent/'run_binding.json'
    check_run_binding(binding_path,binding)
    prior,prior_identity=_validated_progress(path,kind)
    if prior is not None and prior.get('full_evaluation_complete') is True and value.get('full_evaluation_complete') is not True:
        return prior
    if kind=='marker':
        summary_path=path.parent/'heldout_phase_summary.json'
        summary,_=_validated_progress(summary_path,'summary')
        if summary is None or summary.get('full_evaluation_complete') is not value.get('full_evaluation_complete'):
            raise ValueError('completion marker and summary disagree')
    if kind=='summary' and prior is not None:
        # Keep the historical progress snapshot while merging completed cells.
        prior_sets={x['generation_input_set_id']:x['evaluated_arms'] for x in prior['generation_sets']
                    if isinstance(x,dict) and isinstance(x.get('generation_input_set_id'),str)
                    and isinstance(x.get('evaluated_arms'),list)}
        merged={key:{'generation_input_set_id':key,'evaluated_arms':list(arms)}
                for key,arms in prior_sets.items()}
        for item in value.get('generation_sets',[]):
            key=item['generation_input_set_id'];target=merged.setdefault(key,{'generation_input_set_id':key,'evaluated_arms':[]})
            target['evaluated_arms']=list(dict.fromkeys(target['evaluated_arms']+item['evaluated_arms']))
        cells={(x['generation_input_set_id'],arm) for x in merged.values() for arm in x['evaluated_arms']}
        value=dict(value,generation_sets=list(merged.values()),
                   full_evaluation_complete=(len(cells)==125),
                   progress_history=prior.get('progress_history',[])+[
                       {k:v for k,v in prior.items() if k!='progress_history'}])
        if prior.get('full_evaluation_complete') is True and value['full_evaluation_complete'] is not True:
            return prior
    check_run_binding(binding_path,binding)
    current,current_identity=_validated_progress(path,kind)
    if current_identity!=prior_identity:raise ValueError('progress artifact changed during update')
    fd,temp_name=tempfile.mkstemp(prefix='.'+path.name+'.',suffix='.tmp',dir=path.parent)
    try:
        with os.fdopen(fd,'w') as handle:
            json.dump(value,handle,ensure_ascii=False,sort_keys=True,indent=2)
            handle.flush();os.fsync(handle.fileno())
        check_run_binding(binding_path,binding)
        current,current_identity=_validated_progress(path,kind)
        if current_identity!=prior_identity:raise ValueError('progress artifact changed during update')
        os.replace(temp_name,path)
        directory=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(directory)
        finally:os.close(directory)
    finally:
        if os.path.exists(temp_name):os.unlink(temp_name)
    return value


def execute(config,evaluation,context,plan,source,output,workers,unresolved_policy):
    from test_readiness import readiness,checked_checkpoint
    from execution_preparation import make_configured_gemma_client
    from run_literature_extraction import verify_live_identity
    from inductive_execution import evaluate_train_envelope
    source=Path(source).resolve();output=Path(output).resolve()
    if source==output or source in output.parents or output in source.parents:raise ValueError('separate non-nested output directory required')
    if not 1<=workers<=4:raise ValueError('concurrency must be 1 through 4')
    # No identity request or model construction until the old launcher has stopped.
    with stopped_source(source):
        report=readiness(phase='heldout_accuracy')
        if report['status']!='READY':raise ValueError('heldout gates blocked: '+str(report['mandatory_blockers']))
        output.mkdir(parents=True,exist_ok=True)
        with (output/'execution.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            binding={'plan':plan,'source':str(source),'workers':workers,'unresolved_policy':unresolved_policy}
            check_run_binding(output/'run_binding.json',binding)
            runtime=verify_live_identity(config);prior_runtime=read(source/'actual_runtime_identity.json')
            if (runtime['version']['version']!=prior_runtime['version']['version']
                or runtime['tag']['digest']!=prior_runtime['tag']['digest']
                or runtime['tokenizer']['metadata_sha256']!=prior_runtime['tokenizer']['metadata_sha256']):
                raise ValueError('source runtime identity differs; reuse forbidden')
            same_or_save(output/('runtime_'+digest(runtime)[:16]+'.json'),runtime)
            same_or_save(output/'source_runtime_identity.json',prior_runtime)
            client=make_configured_gemma_client(config,seed=config['generation']['seed'])
            cache=ExactRequestCache(client,output/'request_cache',unresolved_policy=unresolved_policy)
            inventory=cache.import_source(source);same_or_save(output/'imported_attempts.json',inventory)
            client._call=cache
            predictor=make_hypobench_prediction_policy(client,evaluation['hypobench']['dataset_and_split']['declared_label_classes'],
                max_output_tokens=evaluation['hypobench']['prediction_policy']['max_output_tokens'])
            finished=[]
            for row in context.inputs:
                job=next(j for j in report['jobs'] if j['input_set_id']==row.paper_id)
                if ':TRAIN-SET:0007:' in row.paper_id or job['generation_checkpoint'] is None:continue
                envelope=checked_checkpoint(read(ROOT/job['generation_checkpoint']),context)
                result=evaluate_train_envelope(context,envelope,predictor,batch_size=4,max_workers=workers,
                    hdr_inputs_by_arm=None,checkpoint_dir=output/digest(row.paper_id)[:16])
                finished.append({'generation_input_set_id':row.paper_id,'evaluated_arms':[a for a,v in result['evaluations'].items() if v.get('status')=='evaluated']})
                print(json.dumps({'completed_sets':len(finished),'new_requests':cache.executed,'cache_hits':cache.reused,'retained_invalid_assignments':cache.retained_invalid}),flush=True)
            summary=atomic_progress_update(output/'heldout_phase_summary.json',{'evaluation_phase':'heldout_accuracy','generation_sets':finished,
                'full_evaluation_complete':False,'exact_request_reuse':True,'imported_attempts':len(inventory),
                'new_requests_this_invocation':cache.executed,'cache_hits_this_invocation':cache.reused,
                'retained_invalid_assignments_this_invocation':cache.retained_invalid,
                'cache_usage_note':'Backend usage on cache hits is historical provenance, not additional token expenditure.',
                'note':'All 501 rows remain in each evaluable denominator. Retained invalid prior attempts are incorrect, never retried. No claim that observations were historically unseen.'},
                binding=binding,kind='summary')
            atomic_progress_update(output/'launch_completed.json',{'status':'phase_completed','phase':'heldout_accuracy',
                'full_evaluation_complete':summary['full_evaluation_complete']},binding=binding,kind='marker')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True);parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--workers',type=int,choices=range(1,5),default=1)
    parser.add_argument('--unresolved-policy',choices=('block','retain-invalid'),default='block')
    parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    config,evaluation,context,plan=prepare()
    if not args.execute:
        print(json.dumps(plan,indent=2));return
    execute(config,evaluation,context,plan,args.source,args.output_dir,args.workers,args.unresolved_policy)

if __name__=='__main__':main()
