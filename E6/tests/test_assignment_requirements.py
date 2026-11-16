"""Original assignment constraints cannot be relaxed by a recommendation."""
import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from assignment_requirements import CONFIG_VALUES, EVALUATION_VALUES, LITERATURE_VALUES, validate_mandated_values
from validate_protocol import validate_config

E6 = Path(__file__).resolve().parents[1]


class AssignmentRequirementsTests(unittest.TestCase):
    def test_all_assignment_values_are_installed(self):
        for name, required in (('config.json', CONFIG_VALUES),
                               ('evaluation_config.json', EVALUATION_VALUES),
                               ('literature_testbed_config.json', LITERATURE_VALUES)):
            with self.subTest(name=name):
                self.assertEqual(validate_mandated_values(json.loads((E6 / name).read_text()), required), [])

    def test_approved_numeric_settings_leave_final_execution_gated(self):
        config = json.loads((E6 / 'config.json').read_text())
        self.assertEqual(config['inference_budget']['tokens_per_input_set_arm'], 8192)
        self.assertEqual(config['generation']['temperature'], 0)
        self.assertEqual(config['generation']['replicates_per_paper_arm'], 1)
        self.assertEqual(config['protocol']['status'], 'approved')
        self.assertTrue(config['protocol']['approved_by'])
        self.assertTrue(config['protocol']['execution_authorized'])
        self.assertIn('committed-artifact', config['protocol']['authorization_scope'])
        self.assertTrue(config['dataset']['frozen'])
        self.assertTrue(config['output']['schema_approved'])

    def test_applied_components_do_not_approve_remaining_methods(self):
        config = json.loads((E6 / 'config.json').read_text())
        approval = json.loads((E6 / 'RESEARCHER_APPROVAL.json').read_text())
        self.assertEqual(config['protocol']['governing_protocol']['model'], 'gemma3:12b')
        self.assertEqual(config['protocol']['governing_protocol']['supersedes'],
                         'E6/prior_protocol_2026-11-04.md')
        self.assertTrue((E6 / 'prior_protocol_2026-11-04.md').is_file())
        self.assertEqual(config['statistical_analysis']['missing_data_rule'], 'complete_pairs')
        self.assertEqual(config['statistical_analysis']['multiplicity_method'], 'unadjusted_marginal_intervals')
        self.assertIsNone(config['failure_handling']['failed_cell_analysis_policy']['missing_score'])
        for number in (1, 8, 12, 26):
            row = approval['decisions'][number - 1]
            self.assertIn('applied_components', row)
            self.assertEqual(row['status'], 'approved')
            self.assertTrue(row['approved_by'])
        for number in (20,):
            self.assertEqual(approval['decisions'][number - 1]['status'], 'approved')
        self.assertIsNotNone(approval['configuration_signoff'])

    def test_proposed_rubrics_have_real_hashes_without_approval(self):
        import hashlib
        config = json.loads((E6 / 'evaluation_config.json').read_text())
        rubrics = config['proposed_evaluator_rubrics']
        self.assertEqual(rubrics['status'], 'pending_researcher_confirmation')
        for value in rubrics['rubrics'].values():
            path = E6.parent / value['path']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), value['file_sha256'])
        self.assertIn('maximum integer 1', config['reconstruction']['matching_and_aggregation_policy'])
        self.assertEqual(config['reconstruction']['validation_status'], 'not_performed')
        self.assertIn('other', config['question_type']['categories'])

    def test_structured_null_policy_validates_without_imputing_scores(self):
        config = json.loads((E6 / 'config.json').read_text())
        protocol = (E6 / 'protocol.md').read_text()
        errors = validate_config(config, protocol)
        self.assertFalse(any('failed_cell_analysis_policy:' in error for error in errors))
        config['failure_handling']['failed_cell_analysis_policy']['missing_score'] = 0
        errors = validate_config(config, protocol)
        self.assertTrue(any('failed_cell_analysis_policy:' in error for error in errors))
        self.assertEqual(len(config['evaluation_human_review']['human_review_sample']), 20)

    def test_approved_predictions_have_no_invented_magnitudes_or_outcome_extensions(self):
        config = json.loads((E6 / 'config.json').read_text())
        approval = json.loads((E6 / 'RESEARCHER_APPROVAL.json').read_text())
        predictions = config['directional_hypotheses']
        self.assertEqual([(p['id'], p['left_arm'], p['right_arm']) for p in predictions],
                         [('H1', 'QH', 'D'), ('H2', 'QH-sel', 'QH-rand'), ('H3', 'QH', 'D-shuffled')])
        for prediction in predictions:
            self.assertEqual(prediction['direction'], '>')
            self.assertEqual(prediction['outcome'], 'main_hypothesis_best_similarity')
            self.assertEqual(prediction['testbed'], 'literature')
            self.assertEqual(prediction['expected_effect_size'], 'unspecified_by_researcher')
        self.assertEqual(approval['decisions'][0]['resolved_details']['directional_hypotheses'], predictions)
        evaluation = json.loads((E6 / 'evaluation_config.json').read_text())
        self.assertTrue(evaluation['diversity']['validation_required_before_scoring'])
        self.assertEqual(evaluation['diversity']['validation_status'], 'not_performed')
        self.assertEqual(evaluation['already_asked']['reference_question_corpus']['path'], 'E6/data/prior_question_corpus_v4.json')
        self.assertEqual(evaluation['already_asked']['semantic_matcher']['candidate_limit'],20)
        self.assertEqual(approval['decisions'][19]['status'], 'approved')
        self.assertIsNotNone(approval['configuration_signoff'])
        self.assertEqual(len(config['statistical_analysis']['comparisons']), 21)

    def test_per_testbed_hashes_are_separate_and_source_checked(self):
        config = json.loads((E6 / 'config.json').read_text())
        protocol = (E6 / 'protocol.md').read_text()
        self.assertEqual(set(config['dataset']['source_sha256']), {'data', 'literature'})
        self.assertEqual(set(config['dataset']['manifest_sha256']), {'data', 'literature'})
        self.assertFalse(any('artifact file hash mismatch' in e for e in validate_config(config, protocol)))
        config['dataset']['source_sha256']['data'] = '0' * 64
        self.assertTrue(any('dataset.source_sha256.data: artifact file hash mismatch' in e
                            for e in validate_config(config, protocol)))

    def test_wrong_budget_unit_and_missing_error_analysis_fail_gate(self):
        config = json.loads((E6 / 'config.json').read_text())
        altered = copy.deepcopy(config)
        altered['inference_budget']['accounting_unit'] = 'prompt_plus_generation_tokens'
        altered['evaluation_human_review']['error_analysis_input_set_count'] = 0
        errors = validate_config(altered)
        self.assertTrue(any('assignment requirement: inference_budget.accounting_unit' in e for e in errors))
        self.assertTrue(any('assignment requirement: evaluation_human_review.error_analysis_input_set_count' in e for e in errors))

    def test_classification_covers_every_original_group_without_claiming_approval(self):
        value = json.loads((E6 / 'DECISION_CLASSIFICATION.json').read_text())
        self.assertEqual([row['id'] for row in value['decisions']], list(range(1, 27)))
        self.assertEqual(value['previous_explicit_row_approvals_found'], 0)
        self.assertEqual(value['administrative_ids_without_separate_scientific_approval'], [6, 7, 17])
        for row in value['decisions']:
            self.assertTrue(all(row[key] for key in ('A', 'B', 'C')))
