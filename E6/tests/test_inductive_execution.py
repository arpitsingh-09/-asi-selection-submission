"""Complete TRAIN pipeline tests with toy sources and mocked model/gates only."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from contextlib import ExitStack
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_inductive_preparation as preparation_fixtures
from test_orchestrator import MockClient, test_settings
from inductive_execution import (
    prepare_train_execution_context, validate_train_execution_context, run_train_generation,
    evaluate_train_envelope, bound_hdr_score, execute_train_input_set,
)
from researcher_approval import digest


class TokenizedFixtureClient(MockClient):
    model = 'gemma3:12b'
    generation_options = {'temperature': 0, 'top_p': 1, 'seed': 2026, 'num_ctx': 32768, 'num_predict': 2048}
    preflight_context_limit = 32768
    @property
    def model_configuration(self): return {'model': self.model, 'generation_options': self.generation_options}
    def count_prompt_tokens(self, stage, prompt):
        count = len(prompt.split())
        return {'raw_response': 'x', 'input_tokens': count, 'output_tokens': 1, 'total_tokens': count + 1,
                'token_count_preflight': {'method': 'ollama_prompt_eval_count_with_num_predict_one',
                    'requested_num_predict': 1, 'bounded_probe_confirmed': True}}
    def call_with_token_limit(self, stage, prompt, *, max_output_tokens):
        result = self(stage, prompt); raw = result['raw_response']
        inp, out = len(prompt.split()), len(raw.split())
        return {'raw_response': raw, 'input_tokens': inp, 'output_tokens': out, 'total_tokens': inp + out,
                'adapter_metadata': {'done': True, 'done_reason': 'stop'}}


class FixturePredictor:
    policy_identity = {'policy_id': 'fixture-only'}
    def __init__(self): self.calls = 0
    def predict_many(self, inputs, *, max_workers):
        self.calls += 1
        return [{'predicted_labels': ['class-a'], 'prediction_status': 'valid'} for _ in inputs]


class InductiveExecutionTests(unittest.TestCase):
    def setUp(self):
        preparation_fixtures.InductivePreparationTests.setUp(self)
        self.context = prepare_train_execution_context(self.proposal, self.test, dataset_dir=self.root)
        self.repo = self.root / 'repo'; (self.repo / 'E6').mkdir(parents=True)
        (self.repo / 'proposal.json').write_text(json.dumps(self.proposal))
        (self.repo / 'test.json').write_text(json.dumps(self.test))
        self.config = {'generation': {'model': 'gemma3:12b', 'context_limit': 32768,
                        'max_output_tokens': 2048, 'temperature': 0, 'top_p': 1, 'seed': 2026},
                       'inference_budget': {'tokens_per_input_set_arm': 8192},
                       'execution_replication': {'run_order_method': 'fixed_configured_arm_order_v1'},
                       'controls': {'d_shuffled': {'donor_matching_rule': 'sha256_hash_ordered_derangement_no_reuse_v1',
                            'within_split_only': True, 'assignment_seed': 2026, 'number_of_assignments': 1,
                            'donor_reuse_policy': 'prohibited_within_assignment_batch', 'self_donation_allowed': False}},
                       'dataset': {'data_generation_proposal': 'proposal.json', 'data_evaluation_manifest': 'test.json'}}
        (self.repo / 'E6/config.json').write_text(json.dumps(self.config))

    def mocked_generation(self):
        client = TokenizedFixtureClient()
        with ExitStack() as stack:
            stack.enter_context(patch('orchestrator.validate_current_protocol', return_value=[]))
            stack.enter_context(patch('orchestrator.validate_preregistration_git_commit', return_value=[]))
            stack.enter_context(patch('development_runtime_probe.validate_runtime_evidence', return_value=[]))
            stack.enter_context(patch('orchestrator.ROOT', self.repo))
            stack.enter_context(patch('orchestrator.CONFIG_PATH', self.repo / 'E6/config.json'))
            result = run_train_generation(self.context, self.context.inputs[0].paper_id, test_settings(), client,
                                          token_budget_per_arm=8192)
        return result, client

    def test_all_seven_arms_run_with_source_bound_train_controls(self):
        result, client = self.mocked_generation()
        self.assertEqual(result['protocol_validation_errors'], [])
        self.assertEqual(result['experiment_status'], 'completed')
        self.assertEqual(result['train_execution_context_sha256'], self.context.context_sha256)
        self.assertTrue(all(r['execution_status'] == 'succeeded' for r in result['arms'].values()))
        self.assertTrue(all(r['budget_unit'] == 'generated_tokens' for r in result['token_budget_accounting'].values()))
        donor_map = self.context.donors
        self.assertEqual(len(donor_map), len(set(donor_map.values())))
        self.assertTrue(all(k != v for k, v in donor_map.items()))
        empty = result['arms']['D-empty']['output']['control_provenance']
        self.assertTrue(empty['rendered_evidence_empty_verified'])
        self.assertNotIn('TEST fixture observation', '\n'.join(prompt for _, prompt in client.calls))

    def test_seeded_arm_output_order_is_explicit_and_reproducible(self):
        from orchestrator import ordered_arm_outputs
        method = 'sha256_seeded_arm_order_v1'
        self.config['execution_replication']['run_order_method'] = method
        (self.repo / 'E6/config.json').write_text(json.dumps(self.config))
        result, _ = self.mocked_generation()
        expected = ordered_arm_outputs(self.context.inputs[0].paper_id, 2026, method)
        self.assertEqual(result['experiment_status'], 'completed')
        self.assertEqual(result['execution_arm_output_order'], expected)
        self.assertEqual([row['arm'] for row in result['execution_manifest']], expected)
        self.assertEqual(result['shared_preparation_order'], 'before_arm_output_calls')

    def test_real_pending_gates_stop_before_any_model_call(self):
        client = TokenizedFixtureClient()
        result = run_train_generation(self.context, self.context.inputs[0].paper_id, test_settings(), client,
                                       token_budget_per_arm=8192)
        self.assertEqual(result['experiment_status'], 'blocked')
        self.assertFalse(client.calls)

    def test_tampered_input_or_derangement_rejected(self):
        forged = copy.deepcopy(self.context)
        forged.donors[next(iter(forged.donors))] = next(iter(forged.donors))
        with self.assertRaises(ValueError): validate_train_execution_context(forged, forged.inputs[0])
        from inductive_execution import validate_frozen_train_context
        altered_policy = copy.deepcopy(self.config)
        altered_policy['controls']['d_shuffled']['assignment_seed'] = 49
        with self.assertRaisesRegex(ValueError, 'frozen policy'):
            validate_frozen_train_context(self.context, altered_policy, root=self.repo)
        from dataclasses import replace
        with self.assertRaises(ValueError):
            validate_train_execution_context(self.context, replace(self.context.inputs[0], evidence='forged'))

    def test_prediction_hdr_and_export_pipeline_checkpoints_without_repeating_calls(self):
        envelope, _ = self.mocked_generation()
        predictor = FixturePredictor()
        directory = self.root / 'checkpoints'
        with patch('inductive_execution.require_final_authorization'):
            result = evaluate_train_envelope(self.context, envelope, predictor, batch_size=2,
                                             checkpoint_dir=directory)
            calls = predictor.calls
            again = evaluate_train_envelope(self.context, envelope, predictor, batch_size=2,
                                            checkpoint_dir=directory)
        self.assertEqual(result, again); self.assertEqual(predictor.calls, calls)
        self.assertEqual(calls, 21)  # seven arms, ceil(5 toy TEST examples / 2)
        self.assertEqual(len(result['generation_records']), 42)
        self.assertFalse(result['failed_cells'])
        self.assertTrue(all(r['hdr']['status'].startswith('blocked_missing') for r in result['evaluations'].values()))
        self.assertTrue(all(r['heldout']['evaluation_row_count'] == 5 for r in result['evaluations'].values()))

    def test_adding_real_hdr_inputs_reuses_predictions_and_preserves_prior_summary(self):
        envelope, _ = self.mocked_generation(); predictor = FixturePredictor()
        directory = self.root / 'hdr-checkpoints'
        with patch('inductive_execution.require_final_authorization'):
            evaluate_train_envelope(self.context, envelope, predictor, batch_size=2, checkpoint_dir=directory)
            calls = predictor.calls
            hypotheses = [r['text'] for r in envelope['arms']['D']['output']['hypotheses']]
            mapping = {'f1': {'ground_truth_indices': [0], 'source_texts': ['Fixture planted rule']}}
            hdr = {'D': {'generation_input_set_id': envelope['paper_id'], 'arm': 'D',
                'hypotheses_sha256': digest(hypotheses), 'reference_feature_ids': ['f1'],
                'discovered_feature_ids': ['f1'], 'relationship_scores': {'f1': 1}, 'feature_mapping': mapping,
                'provenance': {'feature_mapping_sha256': digest(mapping), 'judge_provenance': 'fixture-only',
                    'ground_truth_source_sha256': self.test['dataset_ground_truth']['source_file_sha256']}}}
            result = evaluate_train_envelope(self.context, envelope, predictor, batch_size=2,
                                             checkpoint_dir=directory, hdr_inputs_by_arm=hdr)
        self.assertEqual(predictor.calls, calls)
        self.assertEqual(result['evaluations']['D']['hdr']['status'], 'scored')
        self.assertEqual(len(list(directory.glob('*_evaluation.json'))), 2)

    def test_hdr_input_cannot_be_reused_for_a_different_arm_or_output(self):
        hypotheses = [f'Fixture {i}' for i in range(6)]
        mapping = {'f1': {'ground_truth_indices': [0], 'source_texts': ['Fixture planted rule']}}
        payload = {'generation_input_set_id': self.context.inputs[0].paper_id, 'arm': 'D',
            'hypotheses_sha256': digest(hypotheses), 'reference_feature_ids': ['f1'],
            'discovered_feature_ids': ['f1'], 'relationship_scores': {'f1': 1}, 'feature_mapping': mapping,
            'provenance': {'feature_mapping_sha256': digest(mapping), 'judge_provenance': 'fixture-only',
                'ground_truth_source_sha256': self.test['dataset_ground_truth']['source_file_sha256']}}
        result = bound_hdr_score(self.context, self.context.inputs[0].paper_id, 'D', hypotheses, payload)
        self.assertEqual(result['hypothesis_discovery_rate'], 1)
        with self.assertRaises(ValueError):
            bound_hdr_score(self.context, self.context.inputs[0].paper_id, 'QH', hypotheses, payload)

    def test_unified_pipeline_stops_at_real_pending_gates(self):
        predictor, client = FixturePredictor(), TokenizedFixtureClient()
        result = execute_train_input_set(self.context, self.context.inputs[0].paper_id, test_settings(),
            client, predictor, batch_size=2, token_budget_per_arm=8192)
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(predictor.calls, 0); self.assertFalse(client.calls)

    def test_unified_pipeline_resumes_generation_and_prediction_checkpoints(self):
        envelope, client = self.mocked_generation()
        predictor = FixturePredictor(); directory = self.root / 'unified-checkpoints'
        with patch('inductive_execution.run_train_generation', return_value=envelope) as generate, \
             patch('inductive_execution.require_final_authorization'):
            first = execute_train_input_set(self.context, self.context.inputs[0].paper_id, test_settings(),
                client, predictor, batch_size=2, checkpoint_dir=directory, token_budget_per_arm=8192)
            calls = predictor.calls
            second = execute_train_input_set(self.context, self.context.inputs[0].paper_id, test_settings(),
                client, predictor, batch_size=2, checkpoint_dir=directory, token_budget_per_arm=8192)
        self.assertEqual(generate.call_count, 1)
        self.assertEqual(predictor.calls, calls)
        self.assertEqual(first, second)
        self.assertEqual(first['status'], 'incomplete_required_metrics')  # no fabricated HDR inputs

    def test_corrupted_generation_checkpoint_stops_before_prediction(self):
        envelope, client = self.mocked_generation(); predictor = FixturePredictor()
        directory = self.root / 'corrupt-generation'
        with patch('inductive_execution.run_train_generation', return_value=envelope), \
             patch('inductive_execution.require_final_authorization'):
            execute_train_input_set(self.context, self.context.inputs[0].paper_id, test_settings(),
                client, predictor, batch_size=2, checkpoint_dir=directory, token_budget_per_arm=8192)
            calls = predictor.calls
            checkpoint = next(directory.glob('*_generation_envelope.json'))
            payload = json.loads(checkpoint.read_text())
            payload['envelope']['paper_id'] = 'altered'
            checkpoint.write_text(json.dumps(payload))
            with self.assertRaisesRegex(ValueError, 'checkpoint'):
                execute_train_input_set(self.context, self.context.inputs[0].paper_id, test_settings(),
                    client, predictor, batch_size=2, checkpoint_dir=directory, token_budget_per_arm=8192)
        self.assertEqual(predictor.calls, calls)

    def test_pending_evaluation_gates_invoke_no_predictor(self):
        envelope, _ = self.mocked_generation(); predictor = FixturePredictor()
        with self.assertRaises((ValueError, OSError)):
            evaluate_train_envelope(self.context, envelope, predictor, batch_size=2)
        self.assertEqual(predictor.calls, 0)
