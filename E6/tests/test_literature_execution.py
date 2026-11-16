"""Literature execution: toy source fixtures, mock models and temporary gates only."""
import copy
from contextlib import ExitStack
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_prepare_literature_sample_proposal import candidate_manifest
from test_orchestrator import test_settings
from test_inductive_execution import TokenizedFixtureClient
from prepare_literature_sample_proposal import build_literature_sample_proposal, verify_sample_proposal
from execution_preparation import prepare_literature_reference_proposal
from literature_execution import (prepare_literature_execution_context, validate_literature_execution_context,
    run_literature_generation, execute_literature_input_set)
from researcher_approval import digest


class LiteratureExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate = candidate_manifest()
        cls.sample = build_literature_sample_proposal(cls.candidate, sample_size=100, seed=2026)
        cls.references = prepare_literature_reference_proposal(cls.candidate, cls.sample, references_per_set=10)
        cls.context = prepare_literature_execution_context(cls.candidate, cls.sample, cls.references,
                                                          task='Generate hypotheses from the supplied reference evidence.')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name); (self.repo / 'E6/data').mkdir(parents=True)
        self.config = {'generation': {'model': 'gemma3:12b', 'context_limit': 32768, 'max_output_tokens': 2048,
                                     'temperature': 0, 'top_p': 1, 'seed': 2026},
            'inference_budget': {'tokens_per_input_set_arm': 8192},
            'execution_replication': {'run_order_method': 'sha256_seeded_arm_order_v1'},
            'dataset': {'literature_reference_selection_proposal': 'references.json'},
            'controls': {'d_shuffled': {'donor_matching_rule': 'sha256_hash_ordered_derangement_no_reuse_v1',
                'within_split_only': True, 'assignment_seed': 2026, 'number_of_assignments': 1,
                'donor_reuse_policy': 'prohibited_within_assignment_batch', 'self_donation_allowed': False}}}
        files = {'E6/config.json': self.config, 'candidate.json': self.candidate,
            'E6/data/literature_sample_proposal_v1.json': self.sample, 'references.json': self.references,
            'E6/literature_testbed_config.json': {'candidate_manifest': {'path': 'candidate.json'}},
            'E6/RESEARCHER_APPROVAL.json': {'decisions': [{'id': 4, 'resolved_details': {
                'task_text_by_testbed': {'literature': self.context.task}}}]}}
        selected = {'input_sets_selected': True, 'input_sets_frozen': True,
            'sample_proposal_sha256': self.sample['proposal_sha256'],
            'candidate_manifest_sha256': self.candidate['manifest_sha256'],
            'selected_input_set_ids': [r.paper_id for r in self.context.inputs],
            'input_sets': verify_sample_proposal(self.candidate, self.sample)}
        selected['manifest_sha256'] = digest(selected)
        files['E6/data/literature_selected_manifest_v1.json'] = selected
        for relative, value in files.items(): (self.repo / relative).write_text(json.dumps(value))

    def gates(self):
        stack = ExitStack()
        stack.enter_context(patch('orchestrator.ROOT', self.repo))
        stack.enter_context(patch('orchestrator.CONFIG_PATH', self.repo / 'E6/config.json'))
        stack.enter_context(patch('orchestrator.validate_current_protocol', return_value=[]))
        stack.enter_context(patch('orchestrator.validate_preregistration_git_commit', return_value=[]))
        stack.enter_context(patch('validate_protocol.validate_preregistration_git_commit', return_value=[]))
        stack.enter_context(patch('development_runtime_probe.validate_runtime_evidence', return_value=[]))
        return stack

    def test_sample_ids_references_and_donors_are_deterministic(self):
        again = prepare_literature_execution_context(self.candidate, self.sample, self.references, task=self.context.task)
        self.assertEqual(again.context_sha256, self.context.context_sha256)
        self.assertEqual([r.paper_id for r in again.inputs], self.sample['proposed_input_set_ids'])
        self.assertTrue(all(len(r.reference_evidence) == 10 for r in again.inputs))
        self.assertTrue(all(k != v for k, v in again.donors.items()))
        self.assertEqual(len(set(again.donors.values())), 100)
        self.assertTrue(all('Target-only answer' not in r.evidence for r in again.inputs))

    def test_seven_arms_share_model_budget_and_recipient_evidence_except_controls(self):
        client = TokenizedFixtureClient(); row = self.context.inputs[0]
        with self.gates():
            result = run_literature_generation(self.context, row.paper_id, test_settings(), client, token_budget_per_arm=8192)
        self.assertEqual(result['protocol_validation_errors'], [])
        self.assertEqual(result['experiment_status'], 'completed')
        self.assertEqual(len(result['arms']), 7)
        for entry in result['arms'].values():
            self.assertEqual(entry['manifest']['model_configuration'], client.model_configuration)
            self.assertEqual(entry['token_budget_accounting']['budget_tokens'], 8192)
            self.assertEqual(entry['token_budget_accounting']['budget_unit'], 'generated_tokens')
        for stage, prompt in client.calls:
            self.assertNotIn('Target-only answer', prompt)
            if stage in ('D_generation', 'QH_generation', 'HQ_generation', 'candidate_generation',
                         'QH-sel_hypothesis_generation', 'QH-rand_hypothesis_generation'):
                self.assertIn(row.evidence, prompt)
        self.assertTrue(result['arms']['D-empty']['output']['control_provenance']['rendered_evidence_empty_verified'])
        shuffled = result['arms']['D-shuffled']['output']['control_provenance']
        self.assertEqual(shuffled['donor_id'], self.context.donors[row.paper_id])
        self.assertEqual(len(shuffled['donor_reference_ids']), 10)

    def test_real_pending_gates_block_every_model_call(self):
        client = TokenizedFixtureClient()
        result = run_literature_generation(self.context, self.context.inputs[0].paper_id, test_settings(), client,
                                           token_budget_per_arm=8192)
        self.assertEqual(result['experiment_status'], 'blocked'); self.assertFalse(client.calls)

    def test_tampered_context_or_unfrozen_sample_blocks(self):
        context = copy.deepcopy(self.context)
        context.donors[context.inputs[0].paper_id] = context.inputs[0].paper_id
        with self.assertRaises(ValueError): validate_literature_execution_context(context, context.inputs[0])
        selected_path = self.repo / 'E6/data/literature_selected_manifest_v1.json'
        selected = json.loads(selected_path.read_text()); selected['input_sets_frozen'] = False
        selected.pop('manifest_sha256'); selected['manifest_sha256'] = digest(selected)
        selected_path.write_text(json.dumps(selected))
        client = TokenizedFixtureClient()
        with self.gates():
            result = run_literature_generation(self.context, self.context.inputs[0].paper_id, test_settings(), client,
                                               token_budget_per_arm=8192)
        self.assertEqual(result['experiment_status'], 'blocked'); self.assertFalse(client.calls)

    def test_checkpoint_resume_exports_without_regeneration_and_rejects_changed_budget(self):
        client = TokenizedFixtureClient(); directory = self.repo / 'output'; input_id = self.context.inputs[0].paper_id
        with self.gates():
            first = execute_literature_input_set(self.context, input_id, test_settings(), client,
                checkpoint_dir=directory, token_budget_per_arm=8192)
            calls = len(client.calls)
            second = execute_literature_input_set(self.context, input_id, test_settings(), client,
                checkpoint_dir=directory, token_budget_per_arm=8192)
            self.assertEqual(first, second); self.assertEqual(len(client.calls), calls)
            with self.assertRaises(ValueError):
                execute_literature_input_set(self.context, input_id, test_settings(), client,
                    checkpoint_dir=directory, token_budget_per_arm=4096)
        self.assertEqual(len(first['generation_records']), 42); self.assertFalse(first['failed_cells'])
        self.assertTrue(all(r['testbed'] == 'literature' for r in first['generation_records']))

    def test_failed_arm_preserved_without_fabrication_and_corrupt_checkpoint_rejected(self):
        client = TokenizedFixtureClient(fail_stage='D_generation'); directory = self.repo / 'failures'
        input_id = self.context.inputs[0].paper_id
        with self.gates():
            result = execute_literature_input_set(self.context, input_id, test_settings(), client,
                checkpoint_dir=directory, token_budget_per_arm=8192)
            self.assertEqual(len(result['generation_records']), 36)
            self.assertEqual(result['failed_cells'][0]['arm'], 'D')
            checkpoint = next(directory.glob('*_literature_generation.json'))
            saved = json.loads(checkpoint.read_text()); saved['envelope']['paper_id'] = 'forged'
            checkpoint.write_text(json.dumps(saved)); calls = len(client.calls)
            with self.assertRaises(ValueError):
                execute_literature_input_set(self.context, input_id, test_settings(), client,
                    checkpoint_dir=directory, token_budget_per_arm=8192)
            self.assertEqual(len(client.calls), calls)
