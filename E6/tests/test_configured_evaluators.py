"""Offline fixtures only; no service access or real scoring."""
import copy
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from configured_evaluators import ConfiguredEvaluators
from evaluation import EvaluationError, evaluate_already_asked_rate

ROOT = Path(__file__).resolve().parents[2]


class FakeClient:
    model = 'gemma3:12b'
    generation_options = dict(temperature=0, top_p=1, seed=2026, num_ctx=32768)
    def __init__(self):
        self.calls = []
        self.raw = '{"similarity": 5}'
    def call_with_token_limit(self, stage, prompt, *, max_output_tokens):
        self.calls.append((stage, prompt, max_output_tokens))
        return dict(raw_response=self.raw, output_tokens=4)


class ConfiguredEvaluatorTests(unittest.TestCase):
    def policies(self):
        self.client = FakeClient()
        values = [json.loads((ROOT / 'E6' / n).read_text()) for n in
                  ('config.json', 'evaluation_config.json', 'RESEARCHER_APPROVAL.json')]
        return ConfiguredEvaluators(*values, self.client)

    def test_real_gates_block_all_scoring_before_any_call(self):
        p = self.policies()
        for invoke in (lambda: p.score_literature('paper', {}),
                       lambda: p.score_diversity('input', []),
                       lambda: p.score_question_type('input', 'q1', 'How?'),
                       lambda: p.score_already_asked('input', [], None)):
            with self.assertRaises(EvaluationError): invoke()
        self.assertEqual(self.client.calls, [])

    def test_fixture_scalar_rubrics_preserve_raw_outputs_and_reject_invalid_scores(self):
        p = self.policies()
        values = dict(FIELD='hypothesis', GENERATED='fixture generated', TARGET='fixture reference')
        self.assertEqual(p._scalar('similarity', values, 'similarity'), 5)
        self.assertEqual(p.calls[0]['raw_output'], '{"similarity": 5}')
        self.assertIn('fixture reference', self.client.calls[0][1])
        self.assertEqual(self.client.calls[0][2], 2048)
        for raw in ('{"similarity": 0}', '{"similarity": true}',
                    '{"similarity": 5, "extra": 1}', '{"similarity": 1, "similarity": 5}'):
            self.client.raw = raw
            with self.assertRaises(EvaluationError): p._scalar('similarity', values, 'similarity')
        self.client.raw = '{"distinct": null}'
        with self.assertRaises(EvaluationError):
            p._scalar('distinctness', {'HYPOTHESIS_A': 'fixture a', 'HYPOTHESIS_B': 'fixture b'}, 'distinct')

    def test_rubric_hash_mismatch_blocks_client_call(self):
        p = self.policies()
        p.evaluation['configured_rubrics']['similarity']['file_sha256'] = '0' * 64
        with self.assertRaises(EvaluationError):
            p._scalar('similarity', dict(FIELD='hypothesis', GENERATED='a', TARGET='b'), 'similarity')
        self.assertEqual(self.client.calls, [])

    def test_hypobench_without_supported_cutoff_is_unavailable_without_model_call(self):
        from unittest.mock import patch
        p=self.policies()
        proposal=json.loads((ROOT/p.config['dataset']['data_generation_proposal']).read_text())
        unit=proposal['input_sets'][0]['input_set_id']
        generated=[{'question_id':'fixture-q','question':'What causes a fixture outcome?'}]
        with patch.object(p,'_require_execution'):
            result=p.score_already_asked(unit,generated,evaluation_cutoff='2025-01-01')
        self.assertEqual(result['status'],'blocked')
        self.assertIsNone(result['parsed_output'])
        self.assertEqual(result['provenance']['historical_cutoff_status'],'unavailable')
        self.assertEqual(result['provenance']['planned_denominator'],1)
        self.assertIsNone(result['provenance']['eligible_denominator'])
        self.assertEqual(self.client.calls,[])

    def test_hash_mismatched_hypobench_cutoff_proof_never_becomes_a_date(self):
        from unittest.mock import patch
        p=self.policies()
        proposal=json.loads((ROOT/p.config['dataset']['data_generation_proposal']).read_text())
        unit=proposal['input_sets'][0]['input_set_id']
        policy=p.evaluation['already_asked']
        policy['evaluation_cutoffs_by_input_set'][unit]='2025-01-01'
        policy['hypobench_cutoff_evidence_by_input_set'][unit]={
            'path':p.config['dataset']['data_generation_proposal'],'file_sha256':'0'*64,
            'independently_supported':True,'source_value_path':['invented_field']}
        with patch.object(p,'_require_execution'):
            result=p.score_already_asked(unit,[])
        self.assertIsNone(result['parsed_output'])
        self.assertIn('provenance',result['error'])
        self.assertEqual(self.client.calls,[])

    def test_absent_prior_question_corpus_stays_null_and_never_invokes_matcher(self):
        calls = []
        result = evaluate_already_asked_rate('input', [{'question_id':'q1', 'question':'Fixture?'}], [],
            lambda *args: calls.append(args) or False, denominator_policy_id='fixture', provenance={})
        self.assertEqual(result['status'], 'blocked')
        self.assertIsNone(result['parsed_output'])
        self.assertEqual(calls, [])
