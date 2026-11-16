import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import test_readiness as readiness
import run_confirmatory_test as runner

class PhaseGateTests(unittest.TestCase):
    def test_accuracy_defers_only_unused_scoring_gates(self):
        for name in ('frozen_protocol','researcher_approval','exact_runtime_evidence','committed_preregistration','seven_arms','TRAIN_TEST_sources_and_isolation','TRAIN_terminal_inventory'):
            self.assertTrue(readiness.gate_required_for_phase(name,'heldout_accuracy'))
        for name in readiness.DEFERRED_FOR_ACCURACY:
            self.assertFalse(readiness.gate_required_for_phase(name,'heldout_accuracy'))
            self.assertTrue(readiness.gate_required_for_phase(name,'full'))
    def test_invalid_phase_fails_closed(self):
        with self.assertRaises(ValueError):readiness.gate_required_for_phase('frozen_protocol','anything')
    def test_blocked_accuracy_phase_never_executes(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(sys,'argv',['runner','--phase','heldout_accuracy','--output-dir',str(Path(tmp)/'out')]),patch.object(runner,'readiness',return_value={'status':'BLOCKED','mandatory_blockers':['fixture source gate failed']}),patch.object(runner,'execute_heldout_accuracy',side_effect=AssertionError('TEST call')):
            self.assertEqual(runner.main(),2)
            self.assertFalse((Path(tmp)/'out').exists())
    def test_full_phase_still_requires_HDR(self):
        with patch.object(sys,'argv',['runner','--output-dir','unused']),patch.object(runner,'readiness',side_effect=AssertionError('readiness')):
            with self.assertRaises(SystemExit) as exc:runner.main()
            self.assertEqual(exc.exception.code,2)
    def test_accuracy_runner_has_no_literature_semantic_or_regeneration_callbacks(self):
        config=runner.read(runner.ROOT,'E6/config.json');evaluation=runner.read(runner.ROOT,'E6/evaluation_config.json')
        units=['fixture:TRAIN-SET:0000:checksum','fixture:TRAIN-SET:0007:checksum']
        context=SimpleNamespace(inputs=[SimpleNamespace(paper_id=u) for u in units])
        report={'evaluation_phase':'heldout_accuracy','status':'READY','deferred_scoring_gates':['fixture'],
            'jobs':[{'input_set_id':u,'generation_checkpoint':'fixture-checkpoint'} for u in units]}
        def read(root,path):
            if path=='E6/config.json':return config
            if path=='E6/evaluation_config.json':return evaluation
            return {}
        client=SimpleNamespace(_call=lambda *a: (_ for _ in ()).throw(AssertionError('model call')))
        result={'evaluations':{'D':{'status':'evaluated'},'QH':{'status':'blocked_generation_failed'}},'evaluation_status':'incomplete_required_metrics'}
        with tempfile.TemporaryDirectory() as tmp,patch.object(runner,'read',side_effect=read),patch.object(runner,'checked_checkpoint',return_value={}),patch('run_literature_extraction.verify_live_identity',return_value={'fixture':'offline'}),patch('execution_preparation.make_configured_gemma_client',return_value=client),patch('hypobench_policies.make_hypobench_prediction_policy',return_value=object()),patch('hypobench_policies.make_hypobench_recovery_policy',side_effect=AssertionError('semantic recovery')),patch('configured_evaluators.ConfiguredEvaluators',side_effect=AssertionError('semantic evaluator')),patch('inductive_execution.prepare_train_execution_context',return_value=context),patch('inductive_execution.evaluate_train_envelope',return_value=result) as evaluate,patch('inductive_execution.run_train_generation',side_effect=AssertionError('TRAIN retry')),patch('literature_execution.execute_literature_input_set',side_effect=AssertionError('literature execution')):
            runner.execute_heldout_accuracy(report,Path(tmp))
            self.assertEqual(evaluate.call_count,1)
            self.assertIsNone(evaluate.call_args.kwargs['hdr_inputs_by_arm'])
            summary=json.loads((Path(tmp)/'heldout_phase_summary.json').read_text())
            self.assertFalse(summary['full_evaluation_complete'])
            self.assertEqual(len(summary['generation_sets']),1)

if __name__=='__main__':unittest.main()
