"""Split-isolation and fixed-hypothesis held-out scoring using synthetic fixtures."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare_hypobench_testbed import prepare_hypobench_election_level2_testbed, SPLIT_FILES
from prepare_hypobench_inductive import (
    prepare_inductive_proposal, validate_inductive_proposal, inductive_generation_inputs,
    heldout_prediction_jobs, score_inductive_predictions, score_reference_hdr,
)
from execution_preparation import prepare_execution_plan


class InductivePreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for split, count in [('TRAIN', 12), ('VALIDATION', 4), ('TEST', 5)]:
            data = {'text': [f'{split} fixture observation {i}' for i in range(count)],
                    'label': ['class-a' if i % 2 else 'class-b' for i in range(count)]}
            (self.root / SPLIT_FILES[split]).write_text(json.dumps(data))
        (self.root / 'metadata.json').write_text(json.dumps({'task_description': 'Fixture task',
            'labels': ['class-a', 'class-b'], 'ground_truth_hypotheses': ['Fixture planted rule']}))
        (self.root / 'gt_hypotheses_level2.json').write_text(json.dumps(['Fixture planted rule']))
        (self.root / 'config.yaml').write_text('task_name: fixture\n')
        self.test = prepare_hypobench_election_level2_testbed(self.root)
        self.proposal = prepare_inductive_proposal(self.test, input_set_count=3, observations_per_set=2,
                                                   seed=2026, dataset_dir=self.root)

    def test_deterministic_disjoint_training_evidence_and_no_test_generation(self):
        self.assertFalse(self.proposal['frozen'])
        ids = [r['source_row_index'] for cohort in self.proposal['input_sets'] for r in cohort['observations']]
        self.assertEqual(len(ids), len(set(ids)))
        inputs = inductive_generation_inputs(self.proposal, self.test, dataset_dir=self.root)
        for row in inputs:
            self.assertEqual(row.split, 'TRAIN')
            self.assertNotIn('TEST fixture', row.evidence)
            self.assertNotIn('planted', row.evidence)
            self.assertIn('observed_training_label', row.evidence)
        validate_inductive_proposal(self.proposal, self.test, dataset_dir=self.root)

    def test_fixed_hypotheses_reused_for_every_heldout_observation(self):
        hypotheses = [f'Fixture hypothesis {i}' for i in range(6)]
        input_id = self.proposal['input_sets'][0]['input_set_id']
        jobs = list(heldout_prediction_jobs(self.proposal, self.test, input_id, hypotheses, dataset_dir=self.root))
        self.assertEqual(len(jobs), 5)
        for job in jobs:
            prepared = job['prepared_input']['evaluation_input']
            self.assertEqual(prepared['generated_explanations'], hypotheses)
            self.assertNotIn('label', prepared['benchmark_record'])
            self.assertEqual(job['generation_input_set_id'], input_id)

    def test_missing_predictions_retained_and_mixed_cohorts_rejected(self):
        input_id = self.proposal['input_sets'][0]['input_set_id']
        result = score_inductive_predictions(self.proposal, self.test, input_id, 'D', [], dataset_dir=self.root)
        self.assertEqual(result['evaluation_row_count'], 5)
        with self.assertRaisesRegex(ValueError, 'mix'):
            score_inductive_predictions(self.proposal, self.test, input_id, 'D',
                [{'generation_input_set_id': 'other', 'arm': 'D'}], dataset_dir=self.root)

    def test_rehashed_foreign_test_rows_cannot_replace_protected_source(self):
        from researcher_approval import digest
        altered = copy.deepcopy(self.test)
        altered['records'][0]['source_record']['text'] = 'forged heldout text'
        altered.pop('manifest_sha256')
        altered['manifest_sha256'] = digest(altered)
        with self.assertRaises(ValueError):
            prepare_inductive_proposal(altered, input_set_count=3, observations_per_set=2,
                                        seed=2026, dataset_dir=self.root)

    def test_paper_hdr_is_not_reference_recall_and_requires_provenance(self):
        provenance = {'ground_truth_source_sha256': 'fixture', 'feature_mapping_sha256': 'fixture',
                      'judge_provenance': 'offline fixture'}
        result = score_reference_hdr(['f1', 'f2', 'f3', 'f4'], ['f1', 'f2'],
                                     {'f1': 1.0, 'f2': 0.5}, provenance=provenance)
        self.assertEqual(result['feature_discovery_rate'], 0.5)
        self.assertEqual(result['relationship_correctness'], 0.75)
        self.assertEqual(result['hypothesis_discovery_rate'], 0.375)
        with self.assertRaises(ValueError):
            score_reference_hdr(['f1'], ['f1'], {'f1': 1}, provenance={})
        with self.assertRaises(ValueError):
            score_reference_hdr(['f1'], ['f1'], {'f1': 2}, provenance=provenance)

    def test_changed_source_or_proposal_and_overallocation_rejected(self):
        altered = copy.deepcopy(self.proposal)
        altered['input_sets'][0]['observations'][0]['text'] = 'forged'
        with self.assertRaises(ValueError): validate_inductive_proposal(altered, self.test, dataset_dir=self.root)
        with self.assertRaises(ValueError):
            prepare_inductive_proposal(self.test, input_set_count=30, observations_per_set=2, seed=2026, dataset_dir=self.root)
        train = self.root / SPLIT_FILES['TRAIN']; train.write_text(train.read_text() + '\n')
        with self.assertRaisesRegex(ValueError, 'source'):
            validate_inductive_proposal(self.proposal, self.test, dataset_dir=self.root)
