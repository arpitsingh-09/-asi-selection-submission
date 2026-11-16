"""Offline backend fixtures only; no Ollama or active TEST files."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import run_literature_experiment as r

class Client:
    def __init__(self,fail=False):self.calls=0;self.fail=fail
    def _call(self,stage,prompt,options,limit):
        self.calls+=1
        if self.fail:raise RuntimeError('fixture failure')
        return {'raw_response':'fixture reply','input_tokens':5,'output_tokens':1}

class JournalTests(unittest.TestCase):
    def test_completed_response_replay_and_new_call_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            first=Client()
            with r.durable_calls(first,tmp,'source'):
                expected=first._call('probe','p',{'num_predict':1},1)
            second=Client()
            with r.durable_calls(second,tmp,'source'):
                self.assertEqual(second._call('probe','p',{'num_predict':1},1),expected)
                second._call('generation','q',{'num_predict':20},20)
            self.assertEqual(first.calls,1);self.assertEqual(second.calls,1)
    def test_failed_call_replayed_without_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            first=Client(True)
            with r.durable_calls(first,tmp,'source'):
                with self.assertRaisesRegex(RuntimeError,'fixture failure'):first._call('generation','p',{},1)
            second=Client()
            with r.durable_calls(second,tmp,'source'):
                with self.assertRaises(r.RecordedFailure):second._call('generation','p',{},1)
            self.assertEqual(second.calls,0)
    def test_interrupted_request_blocks_before_client_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp,'000001.started.json').write_text('{}');client=Client()
            with self.assertRaisesRegex(ValueError,'unresolved attempted'):
                with r.durable_calls(client,tmp,'source'):self.fail('entered interrupted journal')
            self.assertEqual(client.calls,0)
    def test_divergent_sequence_aborts_outside_caught_model_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            client=Client()
            with r.durable_calls(client,tmp,'source'):client._call('generation','p',{},1)
            with self.assertRaises(r.CallJournalBlocked):
                with r.durable_calls(client,tmp,'source'):client._call('generation','changed',{},1)
            self.assertEqual(client.calls,1)
    def test_response_tampering_rejected_before_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            client=Client()
            with r.durable_calls(client,tmp,'source'):client._call('generation','p',{},1)
            path=Path(tmp,'000001.finished.json');record=r.read(path);record['reply']['raw_response']='tampered';path.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError,'integrity'):
                with r.durable_calls(client,tmp,'source'):pass
            self.assertEqual(client.calls,1)
    def test_real_plan_binds_100_targets_without_network_or_model(self):
        with patch('urllib.request.urlopen',side_effect=AssertionError('network prohibited')),patch.object(r,'make_configured_gemma_client',side_effect=AssertionError('client prohibited')):
            _,context,plan=r.prepare()
        self.assertEqual(len(context.inputs),100);self.assertEqual(plan['planned_arm_cells'],700)
        self.assertEqual(len(plan['arms']),7);self.assertEqual(plan['retry_count'],0)
        self.assertFalse(plan['TEST_access'])
    def test_evaluation_validation_blocks_before_any_request(self):
        from configured_evaluators import ConfiguredEvaluators
        config=r.read(r.ROOT/'E6/config.json');evaluation=r.read(r.ROOT/'E6/evaluation_config.json');approval=r.read(r.ROOT/'E6/RESEARCHER_APPROVAL.json')
        with patch.object(ConfiguredEvaluators,'_require_execution',side_effect=ValueError('missing genuine validation')):
            with self.assertRaisesRegex(ValueError,'missing genuine validation'):
                r.evaluation_gates(config,evaluation,approval,Client(),None)

if __name__=='__main__':unittest.main()
