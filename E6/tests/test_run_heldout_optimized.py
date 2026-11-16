"""Offline fixture requests only. Never touches the active held-out run."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import fcntl
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import run_heldout_optimized as r
from hypobench_policies import make_hypobench_prediction_policy
from evaluation import prepare_hypobench_data_explanation_input

class Client:
    model='gemma3:12b'
    generation_options={'temperature':0,'top_p':1,'seed':2026,'num_ctx':32768,'num_predict':2048}
    supports_independent_parallel_requests=True
    def __init__(self,fail=False):self.calls=[];self.fail=fail
    def _call(self,stage,prompt,options,limit):
        self.calls.append((stage,prompt,dict(options),limit))
        if self.fail:raise RuntimeError('fixture failed')
        return {'model':self.model,'raw_response':json.dumps({'predicted_label':'class-a','supporting_hypothesis_ids':['H1']}),
            'adapter_metadata':{'model':self.model,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),
                'generation_settings':{'options':options},'requested_output_token_limit':limit,'http_status':200,'done':True}}
    def call_with_token_limit(self,stage,prompt,*,max_output_tokens):
        options=dict(self.generation_options,num_predict=max_output_tokens)
        return self._call(stage,prompt,options,max_output_tokens)

def prepared():
    return prepare_hypobench_data_explanation_input('fixture-row',{'task':'Fixture task','observation':'Fixture TEST text'},
        [f'Fixture hypothesis {i}' for i in range(6)],dataset_id='fixture',split='TEST',dataset_provenance={'fixture':True})

class OptimizedTests(unittest.TestCase):
    def progress_fixture(self,root):
        plan={'source_hashes':{'E6/run_heldout_optimized.py':'current-runner'},'context':'frozen'}
        plan['plan_sha256']=r.digest(plan)
        binding={'plan':plan,'source':'source','workers':1,'unresolved_policy':'retain-invalid'}
        r.save(root/'run_binding.json',binding)
        return binding

    def test_partial_summary_atomically_merges_resumed_progress(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);binding=self.progress_fixture(root);path=root/'heldout_phase_summary.json'
            prior={'evaluation_phase':'heldout_accuracy','full_evaluation_complete':False,
                   'generation_sets':[{'generation_input_set_id':'set-0','evaluated_arms':['arm-0']}],
                   'new_requests_this_invocation':12}
            r.save(path,prior);before=path.read_bytes()
            incoming={'evaluation_phase':'heldout_accuracy','full_evaluation_complete':False,
                      'generation_sets':[{'generation_input_set_id':'set-0','evaluated_arms':['arm-1']}],
                      'new_requests_this_invocation':20}
            result=r.atomic_progress_update(path,incoming,binding=binding,kind='summary')
            merged=next(x for x in result['generation_sets'] if x['generation_input_set_id']=='set-0')
            self.assertEqual(set(merged['evaluated_arms']),{'arm-0','arm-1'})
            self.assertEqual(result['progress_history'][0]['new_requests_this_invocation'],12)
            self.assertNotEqual(path.read_bytes(),before)
            self.assertEqual(json.loads(path.read_text()),result)

    def test_completed_summary_cannot_be_downgraded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);binding=self.progress_fixture(root);path=root/'heldout_phase_summary.json'
            prior={'evaluation_phase':'heldout_accuracy','full_evaluation_complete':True,
                   'generation_sets':[{'generation_input_set_id':f'set-{i}','evaluated_arms':[f'arm-{i}']}
                                      for i in range(125)]}
            r.save(path,prior);before=path.read_bytes()
            result=r.atomic_progress_update(path,dict(prior,full_evaluation_complete=False),binding=binding,kind='summary')
            self.assertEqual(result,prior);self.assertEqual(path.read_bytes(),before)

    def test_progress_update_rejects_mismatched_run_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);binding=self.progress_fixture(root);path=root/'heldout_phase_summary.json'
            prior={'evaluation_phase':'heldout_accuracy','full_evaluation_complete':False,'generation_sets':[]}
            r.save(path,prior);changed=dict(binding,workers=2)
            with self.assertRaises(ValueError):
                r.atomic_progress_update(path,prior,binding=changed,kind='summary')
            self.assertEqual(json.loads(path.read_text()),prior)

    def test_immutable_outputs_keep_same_or_save_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'immutable.json';r.save(path,{'frozen':True});before=path.read_bytes()
            with self.assertRaisesRegex(ValueError,'existing artifact changed'):
                r.same_or_save(path,{'frozen':False})
            self.assertEqual(path.read_bytes(),before)

    def source(self,root,client,status='finished'):
        source=root/'source';(source/'calls').mkdir(parents=True);(source/'execution.lock').touch()
        request={'stage':'hypobench_heldout_prediction','prompt':'fixture prompt','options':dict(client.generation_options,num_predict=32),'requested_limit':32}
        (source/'calls/fixture.started.json').write_text(json.dumps(request))
        if status=='finished':
            reply=client._call(request['stage'],request['prompt'],request['options'],32)
            (source/'calls/fixture.finished.json').write_text(json.dumps({'reply':reply}))
        elif status=='failed':(source/'calls/fixture.failed.json').write_text(json.dumps({'error':'fixture failed'}))
        return source,request
    def test_active_source_lock_prevents_continuation(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp);(source/'execution.lock').touch()
            with (source/'execution.lock').open('r') as old:
                fcntl.flock(old,fcntl.LOCK_EX|fcntl.LOCK_NB)
                with self.assertRaisesRegex(ValueError,'still running'):
                    with r.stopped_source(source):self.fail('entered active source')
    def test_source_response_reused_without_backend_and_keeps_raw_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);client=Client();source,q=self.source(root,client)
            cache=r.ExactRequestCache(client,root/'cache')
            with r.stopped_source(source):inventory=cache.import_source(source)
            before=len(client.calls);reply=cache(q['stage'],q['prompt'],q['options'],32)
            self.assertEqual(len(client.calls),before);self.assertEqual(cache.reused,1)
            self.assertEqual(reply,json.loads((source/'calls/fixture.finished.json').read_text())['reply'])
            self.assertEqual(inventory[0]['status'],'finished')
    def test_unresolved_source_blocks_or_is_explicitly_retained_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);client=Client();source,q=self.source(root,client,status='pending')
            with self.assertRaisesRegex(ValueError,'unresolved prior'):r.ExactRequestCache(client,root/'blocked').import_source(source)
            cache=r.ExactRequestCache(client,root/'retained',unresolved_policy='retain-invalid');cache.import_source(source)
            with self.assertRaises(r.PriorAttemptUnavailable):cache(q['stage'],q['prompt'],q['options'],32)
            self.assertEqual(client.calls,[])
    def test_failed_attempt_is_never_retried(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);client=Client();source,q=self.source(root,client,status='failed')
            cache=r.ExactRequestCache(client,root/'cache');cache.import_source(source)
            with self.assertRaises(r.PriorAttemptUnavailable):cache(q['stage'],q['prompt'],q['options'],32)
            self.assertEqual(client.calls,[])
    def test_parallel_identical_requests_singleflight_and_restart_reuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);client=Client();cache=r.ExactRequestCache(client,root);client._call=cache
            predictor=make_hypobench_prediction_policy(client,['class-a'])
            results=predictor.predict_many([prepared()]*4,max_workers=4)
            self.assertEqual(len(client.calls),1);self.assertEqual(results,[results[0]]*4)
            baseline=Client();expected=make_hypobench_prediction_policy(baseline,['class-a'])(prepared())
            self.assertEqual(results[0],expected)
            fresh=Client();second=r.ExactRequestCache(fresh,root);fresh._call=second
            self.assertEqual(make_hypobench_prediction_policy(fresh,['class-a'])(prepared()),results[0])
            self.assertEqual(fresh.calls,[])
    def test_cache_key_requires_exact_prompt_settings_and_model(self):
        options={'seed':2026};base=r.request_key('m','stage','prompt',options,32)
        for other in (r.request_key('m','stage','changed',options,32),r.request_key('m2','stage','prompt',options,32),r.request_key('m','stage','prompt',{'seed':1},32),r.request_key('m','stage','prompt',options,31)):
            self.assertNotEqual(base,other)
    def test_interrupted_new_request_aborts_outside_invalid_prediction_handler(self):
        with tempfile.TemporaryDirectory() as tmp:
            client=Client();cache=r.ExactRequestCache(client,tmp);client._call=cache
            request=cache.request('hypobench_heldout_prediction','p',dict(client.generation_options,num_predict=32),32)
            (Path(tmp)/(r.digest(request)+'.started.json')).write_text(json.dumps(request))
            with self.assertRaises(r.UnsafeContinuation):cache(request['stage'],'p',request['options'],32)
            self.assertFalse(client.calls)
    def test_source_decoding_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);client=Client();source,q=self.source(root,client)
            path=source/'calls/fixture.started.json';q['options']['seed']=1;path.write_text(json.dumps(q))
            with self.assertRaisesRegex(ValueError,'decoding'):r.ExactRequestCache(client,root/'cache').import_source(source)
    def test_interrupted_optimized_retained_durably_without_retry_or_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);client=Client();cache=r.ExactRequestCache(client,root/'cache',unresolved_policy='retain-invalid')
            options=dict(client.generation_options,num_predict=32)
            reply=cache('hypobench_heldout_prediction','completed',options,32)
            request=cache.request('hypobench_heldout_prediction','interrupted',options,32)
            marker=cache.directory/(r.digest(request)+'.started.json');r.save(marker,request)
            checkpoint=root/'batch.json';r.save(checkpoint,{'results':[{'predicted_labels':['class-a']}]})
            before={p:p.read_bytes() for p in root.rglob('*.json')}
            client.calls.clear()
            for policy in ('retain-invalid','block','retain-invalid'):
                fresh=r.ExactRequestCache(client,cache.directory,unresolved_policy=policy)
                with self.assertRaises(r.PriorAttemptUnavailable):fresh(request['stage'],request['prompt'],options,32)
                self.assertEqual(fresh('hypobench_heldout_prediction','completed',options,32),reply)
                self.assertEqual(fresh.executed,0)
                self.assertEqual(fresh.reused,1)
            self.assertEqual(client.calls,[])
            for p,data in before.items():self.assertEqual(p.read_bytes(),data)
            terminal=r.read(marker.with_name(marker.name.replace('.started.json','.json')))
            self.assertEqual(terminal['terminal']['status'],'unresolved_retained_invalid')
            self.assertEqual(terminal['origin']['started_sha256'],r.file_digest(marker))
            cache.load(marker.with_name(marker.name.replace('.started.json','.json')),request)
    def test_corrupt_interrupted_marker_never_retried_or_retained(self):
        with tempfile.TemporaryDirectory() as tmp:
            client=Client();cache=r.ExactRequestCache(client,tmp,unresolved_policy='retain-invalid')
            request=cache.request('stage','p',{},32);key=r.digest(request)
            marker=Path(tmp)/(key+'.started.json');r.save(marker,dict(request,prompt='different'))
            with self.assertRaises(r.UnsafeContinuation):cache('stage','p',{},32)
            marker.write_text('{')
            with self.assertRaises(r.UnsafeContinuation):cache('stage','p',{},32)
            self.assertFalse((Path(tmp)/(key+'.json')).exists());self.assertFalse(client.calls)
    def test_new_failed_request_never_retried(self):
        with tempfile.TemporaryDirectory() as tmp:
            client=Client(fail=True);cache=r.ExactRequestCache(client,tmp,unresolved_policy='retain-invalid')
            with self.assertRaises(RuntimeError):cache('stage','p',{},32)
            fresh=r.ExactRequestCache(client,tmp,unresolved_policy='retain-invalid')
            with self.assertRaises(r.PriorAttemptUnavailable):fresh('stage','p',{},32)
            self.assertEqual(len(client.calls),1)
    def test_original_binding_accepts_only_runner_recovery_and_preserves_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'binding.json'
            plan={'source_hashes':{'E6/run_heldout_optimized.py':'f3cd84edc49fd1197800bc0a579cfb2b5ad9721ac3d6e414e338a42e28bb50b8','prompt':'frozen'},'context':'frozen'}
            plan['plan_sha256']=r.digest(plan)
            original={'plan':plan,'workers':1,'unresolved_policy':'retain-invalid'};r.save(path,original);before=path.read_bytes()
            updated=json.loads(json.dumps(original));updated['plan']['source_hashes']['E6/run_heldout_optimized.py']='recovery'
            def seal(binding):binding['plan']['plan_sha256']=r.digest({k:v for k,v in binding['plan'].items() if k!='plan_sha256'})
            seal(updated);r.check_run_binding(path,updated);self.assertEqual(path.read_bytes(),before)
            for field in ('workers','unresolved_policy'):
                changed=json.loads(json.dumps(updated));changed[field]='changed'
                with self.assertRaises(ValueError):r.check_run_binding(path,changed)
            updated['plan']['source_hashes']['prompt']='changed';seal(updated)
            with self.assertRaises(ValueError):r.check_run_binding(path,updated)
            self.assertEqual(path.read_bytes(),before)
    def test_cached_output_corruption_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            client=Client();cache=r.ExactRequestCache(client,tmp);options=dict(client.generation_options,num_predict=32)
            cache('hypobench_heldout_prediction','p',options,32)
            path=next(Path(tmp).glob('*.json'));path=next(p for p in Path(tmp).glob('*.json') if not p.name.endswith('.started.json'))
            entry=r.read(path);entry['terminal']['reply']['raw_response']='changed';path.write_text(json.dumps(entry))
            with self.assertRaises(r.UnsafeContinuation):cache('hypobench_heldout_prediction','p',options,32)
            self.assertEqual(len(client.calls),1)

if __name__=='__main__':unittest.main()
