import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evaluation import ARMS
from execution_preparation import export_generation_records, write_jsonl_exclusive, prepare_execution_plan, prepare_literature_reference_proposal, literature_reference_inputs
from orchestrator import ExperimentInput


def envelope():
    return {'paper_id': 'fixture-id', 'model_configuration': {'model': 'fixture-model', 'generation_options': {'seed': 2026}},
            'arms': {arm: {'execution_status': 'succeeded', 'output': {'hypotheses': [
                {'text': f'Fixture {i}', 'hypothesis_id': f'{arm}:{i}', 'question_text': None} for i in range(6)]}}
                for arm in ARMS},
            'token_budget_accounting': {arm: {'budget_unit': 'generated_tokens', 'tokens_used': 100} for arm in ARMS}}


class ExecutionPreparationTests(unittest.TestCase):
    def test_gemma_client_preparation_maps_explicit_limits_without_inference(self):
        from execution_preparation import make_configured_gemma_client
        from unittest.mock import patch
        config = {'generation': {'model': 'gemma3:12b', 'context_limit': 32768,
                  'max_output_tokens': 2048, 'temperature': 0, 'top_p': 1, 'seed': 2026,
                  'verified_context_length_model_metadata': 131072}}
        with patch('ollama_adapter.urllib.request.urlopen') as request:
            client = make_configured_gemma_client(config, seed=2026)
            request.assert_not_called()
        self.assertEqual(client.generation_options['num_ctx'], 32768)
        self.assertEqual(client.generation_options['num_predict'], 2048)
        self.assertEqual(client.preflight_context_limit, 32768)
        with self.assertRaises(ValueError): make_configured_gemma_client(config, seed=49)
        config['generation']['context_limit'] = None
        with self.assertRaises(ValueError): make_configured_gemma_client(config, seed=2026)

    def test_assignment_schema_arm_mapping_and_nonadditive_cost_scope(self):
        rows, failures = export_generation_records(envelope(), testbed='data', seed=2026)
        self.assertEqual(len(rows), 42); self.assertFalse(failures)
        self.assertEqual({r['arm'] for r in rows}, {'D', 'QH', 'QH_sel', 'QH_rand', 'HQ', 'D_empty', 'D_shuffled'})
        self.assertTrue(all(r['rq'] is None and r['tokens_generated'] == 100 for r in rows))
        self.assertTrue(all('non_additive' in r['token_accounting_scope'] for r in rows))

    def test_export_seed_must_match_real_configuration(self):
        with self.assertRaisesRegex(ValueError, 'seed'):
            export_generation_records(envelope(), testbed='data', seed=49)
        value = envelope(); value['model_configuration'].pop('generation_options')
        with self.assertRaisesRegex(ValueError, 'seed'):
            export_generation_records(value, testbed='data', seed=2026)

    def test_feasibility_counts_are_not_claimed_as_exact_tokens(self):
        from token_feasibility import build_token_feasibility
        row = ExperimentInput(paper_id='fixture', domain_and_task='Fixture task', evidence='Fixture evidence')
        report = build_token_feasibility([row], generated_cap=8192, per_call_output_limit=2048,
                                         context_limit=32768, metadata_context_limit=131072)
        self.assertFalse(report['exact_token_count_available_offline'])
        self.assertEqual(report['maximum_requested_outputs_plus_one_token_probes']['QH-sel'], 8196)
        self.assertEqual(report['generated_cap'], 8192)
        self.assertTrue(all(r['exact_prompt_tokens'] is None for r in report['fixed_initial_prompt_lengths']))

    def test_failed_cells_retained_separately_without_fabricated_hypotheses(self):
        value = envelope(); value['arms']['D'] = {'execution_status': 'failed', 'missing_output': True}
        rows, failures = export_generation_records(value, testbed='literature', seed=2026)
        self.assertEqual(len(rows), 36); self.assertEqual(failures[0]['arm'], 'D')
        value = envelope(); value['token_budget_accounting']['D']['budget_unit'] = 'prompt_plus_generation_tokens'
        with self.assertRaises(ValueError): export_generation_records(value, testbed='data', seed=2026)

    def test_reference_selection_is_proposal_only_and_never_leaks_target(self):
        from test_prepare_literature_sample_proposal import candidate_manifest
        from prepare_literature_sample_proposal import build_literature_sample_proposal
        candidate = candidate_manifest()
        sample = build_literature_sample_proposal(candidate, sample_size=100, seed=2026)
        proposal = prepare_literature_reference_proposal(candidate, sample, references_per_set=10)
        inputs = literature_reference_inputs(candidate, sample, proposal, task='Explicit fixture task')
        self.assertFalse(proposal['frozen'])
        self.assertEqual(len(inputs), 100)
        self.assertTrue(all(len(row.reference_evidence) == 10 for row in inputs))
        self.assertTrue(all('Target-only answer' not in row.evidence for row in inputs))
        proposal['selections'][0]['reference_ids'].reverse()
        with self.assertRaises(ValueError):
            literature_reference_inputs(candidate, sample, proposal, task='Explicit fixture task')

    def test_exclusive_output_and_transductive_plan_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'fixture.jsonl'
            write_jsonl_exclusive(path, [{'fixture': True}])
            with self.assertRaises(FileExistsError): write_jsonl_exclusive(path, [])
            self.assertEqual(json.loads(path.read_text()), {'fixture': True})
            row = ExperimentInput(paper_id='test-row', domain_and_task='task', evidence='text', split='TEST')
            with self.assertRaisesRegex(ValueError, 'TRAIN'):
                prepare_execution_plan([row], testbed='data', source_artifacts=[], seed=2026, root=directory)
