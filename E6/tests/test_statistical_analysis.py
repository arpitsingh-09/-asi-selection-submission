"""Synthetic-only statistical integration tests."""
import itertools
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evaluation import ARMS, EvaluationError, evaluation_record
from statistical_analysis import analyze_evaluations, analyze_configured_evaluations, percentile_interval, write_analysis_exclusive


class StatisticalAnalysisTests(unittest.TestCase):
    def sources(self):
        return [dict(generation_input_set_id=f'x:TRAIN-SET:{i}', evaluations={
            a: dict(status='evaluated', heldout=dict(heldout_accuracy=dict(
                parsed_output=dict(accuracy=i / 10 + j / 100))), predictions=[{}] * 501)
            for j, a in enumerate(ARMS)}) for i in range(4)]

    def analyze(self, sources=None, **kwargs):
        options = dict(testbed='data', metric='accuracy',
                       value_path=['heldout', 'heldout_accuracy', 'parsed_output', 'accuracy'],
                       comparisons=list(itertools.combinations(ARMS, 2)),
                       replicates=100, seed=2026, missing_policy='block')
        options.update(kwargs)
        return analyze_evaluations(self.sources() if sources is None else sources, **options)

    def test_known_paired_effect_and_all_arms(self):
        result = self.analyze()
        self.assertEqual(len(result['comparisons']), 21)
        self.assertEqual(len(result['arm_estimates']), 7)
        for row in result['comparisons'].values():
            self.assertEqual(row['included_count'], 4)
            self.assertAlmostEqual(row['interval'][0], row['point_estimate'])
            self.assertAlmostEqual(row['interval'][1], row['point_estimate'])
            self.assertEqual(row['bootstrap']['confidence_level'], .95)
        self.assertLess(result['arm_estimates']['D']['interval'][0], .15)
        self.assertGreater(result['arm_estimates']['D']['interval'][1], .15)

    def test_reproducible_exclusive_provenance(self):
        result = self.analyze()
        self.assertEqual(result, self.analyze())
        self.assertEqual(result['provenance']['sources'], self.sources())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'analysis.json'
            write_analysis_exclusive(path, result)
            self.assertEqual(json.loads(path.read_text()), result)
            with self.assertRaises(FileExistsError):
                write_analysis_exclusive(path, result)
            result['metric'] = 'tampered'
            with self.assertRaises(EvaluationError):
                write_analysis_exclusive(path, result)

    def test_missing_failure_never_imputed(self):
        sources = self.sources()
        sources[0]['evaluations']['D'] = dict(status='blocked_generation_failed')
        del sources[1]['evaluations']['QH']
        sources[2]['evaluations']['HQ']['heldout'] = dict(status='failed')
        blocked = self.analyze(sources)
        self.assertIsNone(blocked['comparisons']['D-minus-QH']['point_estimate'])
        result = self.analyze(sources, missing_policy='complete_pairs')
        row = result['comparisons']['D-minus-QH']
        self.assertEqual(row['included_count'], 2)
        self.assertEqual(len(row['exclusions']), 2)
        self.assertEqual(row['denominator'], 2)
        self.assertEqual(row['expected_count'], 4)
        self.assertEqual(row['excluded_count'], 2)
        self.assertEqual(row['unavailable_fraction'], .5)
        self.assertIsNone(next(c for c in result['cells'] if c['input_set_id'] == 'x:TRAIN-SET:0' and c['arm'] == 'D')['value'])
        self.assertEqual(result['arm_estimates']['HQ']['included_count'], 3)
        for source in sources:
            source['evaluations']['D'] = dict(status='failed')
        self.assertIsNone(self.analyze(sources, missing_policy='complete_pairs')['arm_estimates']['D']['interval'])

    def test_literature_native_records(self):
        sources = [dict(input_set_id=f'paper:{i}', records=[evaluation_record(
            stage='literature_reconstruction_similarity', input_set_id=f'paper:{i}',
            evaluation_input=dict(field='main_hypothesis'), provenance=dict(arm=a),
            parsed_output=dict(best_similarity=.5 + i / 10)) for a in ARMS]) for i in range(3)]
        result = self.analyze(sources, testbed='literature', metric='hypothesis_similarity',
            stage='literature_reconstruction_similarity', field='main_hypothesis',
            value_path=['parsed_output', 'best_similarity'])
        self.assertEqual(result['independent_unit'], 'literature target paper')
        self.assertEqual(result['arm_estimates']['D']['included_count'], 3)
        sources[0]['records'].append(sources[0]['records'][0])
        with self.assertRaises(EvaluationError):
            self.analyze(sources, testbed='literature', stage='literature_reconstruction_similarity',
                         field='main_hypothesis', value_path=['parsed_output', 'best_similarity'])

    def test_invalid_units_config_and_hash(self):
        for overrides in (dict(seed=None), dict(replicates=0), dict(missing_policy='impute'),
                          dict(comparisons=[('D', 'unknown')])):
            with self.assertRaises(EvaluationError):
                self.analyze(**overrides)
        sources = self.sources()
        with self.assertRaises(EvaluationError):
            self.analyze(sources + sources[:1])
        sources[0]['generation_input_set_id'] = 'TEST:1'
        with self.assertRaises(EvaluationError):
            self.analyze(sources)
        sources = self.sources()
        sources[0]['result_sha256'] = 'bad'
        with self.assertRaises(EvaluationError):
            self.analyze(sources)

    def test_active_config_never_activates_proposals_and_rejects_holm(self):
        import copy
        root = Path(__file__).resolve().parents[1]
        config = json.loads((root / 'config.json').read_text())
        evaluation = json.loads((root / 'evaluation_config.json').read_text())
        kwargs = dict(config=config, evaluation_config=evaluation, testbed='data',
            metric='accuracy', value_path=['heldout', 'heldout_accuracy', 'parsed_output', 'accuracy'])
        self.assertEqual(evaluation['paired_bootstrap']['replicates'], 10000)
        self.assertEqual(evaluation['paired_bootstrap']['seed'], 2026)
        evaluation['paired_bootstrap']['replicates'] = None
        with self.assertRaises(EvaluationError):
            analyze_configured_evaluations(self.sources(), **kwargs)
        evaluation['paired_bootstrap'].update(replicates=25, seed=2026,
            random_generator_and_version='python.random.Random/MT19937; sha256(seed:replicate) streams')
        result = analyze_configured_evaluations(self.sources(), **kwargs)
        self.assertEqual(result['configuration']['missing_policy'], 'complete_pairs')
        self.assertEqual(result['confidence_level'], .95)
        self.assertEqual(len(result['comparisons']), 21)
        evaluation['paired_bootstrap']['multiplicity_method'] = 'Holm'
        with self.assertRaises(EvaluationError):
            analyze_configured_evaluations(self.sources(), **kwargs)

    def test_percentile_definition(self):
        self.assertEqual(percentile_interval(list(range(101)), .95), (2.500000000000002, 97.5))
