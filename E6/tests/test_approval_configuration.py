import copy
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from approval_configuration import prepare_analysis_configuration
from test_researcher_approval import approved_record, resign


class ApprovalConfigurationTests(unittest.TestCase):
    def settings(self):
        return dict(statistic='arithmetic_mean', interval_method='linear_percentile', confidence_level=.95,
            replicates=10000, seed=2026,
            random_generator_and_version='python.random.Random/MT19937; sha256(seed:replicate) streams',
            comparisons=[['QH-sel', 'QH-rand']], missing_policy='complete_pairs',
            multiplicity_method='unadjusted_marginal_intervals', analysis_dependency_versions='Python 3.9 fixture')

    def test_signed_replacement_maps_without_mutation_or_authorization(self):
        with tempfile.TemporaryDirectory() as root:
            record = approved_record(root)
            row = record['decisions'][25]
            row.update(choice='replacement', approved_value='explicit marginal interval plan')
            row['resolved_details']['analysis_settings'] = self.settings()
            resign(row)
            config = dict(protocol=dict(status='draft_unapproved'), statistical_analysis={})
            evaluation = dict(status='provisional_unapproved', paired_bootstrap={})
            before = copy.deepcopy((record, config, evaluation))
            c, e = prepare_analysis_configuration(record, config, evaluation, root=root)
            self.assertEqual((record, config, evaluation), before)
            self.assertEqual(c['protocol']['status'], 'draft_unapproved')
            self.assertNotIn('primary_contrasts', c['statistical_analysis'])
            self.assertEqual(e['paired_bootstrap']['replicates'], 10000)
            row['resolved_details']['analysis_settings']['multiplicity_method'] = 'Holm'
            resign(row)
            with self.assertRaises(ValueError):
                prepare_analysis_configuration(record, config, evaluation, root=root)

    def test_pending_and_incomplete_approvals_block(self):
        with tempfile.TemporaryDirectory() as root:
            record = approved_record(root)
            with self.assertRaises(ValueError):
                prepare_analysis_configuration(record, {}, {}, root=root)
            record['decisions'][25]['status'] = 'pending_researcher_approval'
            with self.assertRaises(ValueError):
                prepare_analysis_configuration(record, {}, {}, root=root)
