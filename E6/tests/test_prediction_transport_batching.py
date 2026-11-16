"""Parallel transport retains identical single-observation prediction payloads."""
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hypobench_policies import make_hypobench_prediction_policy
from evaluation import prepare_hypobench_data_explanation_input


class IndependentFixtureClient:
    model = 'gemma3:12b'
    generation_options = {'temperature': 0.0, 'seed': 2026}
    supports_independent_parallel_requests = True
    def __init__(self): self.calls = []
    def call_with_token_limit(self, stage, prompt, *, max_output_tokens):
        self.calls.append((stage, prompt, max_output_tokens))
        if 'observation-2' in prompt: raise RuntimeError('fixture technical failure')
        return {'raw_response': json.dumps({'predicted_label': 'class-a', 'supporting_hypothesis_ids': ['H1']}),
                'adapter_metadata': {'done_reason': 'stop'}}


class PredictionTransportBatchingTests(unittest.TestCase):
    def prepared(self):
        return [prepare_hypobench_data_explanation_input(f'fixture-{i}',
            {'task': 'Fixture task', 'observation': f'observation-{i}'}, [f'Fixture rule {j}' for j in range(6)],
            dataset_id='fixture', split='TEST', dataset_provenance={'fixture': True}) for i in range(4)]

    def test_parallel_matches_serial_prompts_order_errors_and_output_limits(self):
        serial_client, parallel_client = IndependentFixtureClient(), IndependentFixtureClient()
        serial = make_hypobench_prediction_policy(serial_client, ['class-a', 'class-b'])
        parallel = make_hypobench_prediction_policy(parallel_client, ['class-a', 'class-b'])
        left = serial.predict_many(self.prepared(), max_workers=1)
        right = parallel.predict_many(self.prepared(), max_workers=3)
        self.assertEqual(left, right)
        self.assertCountEqual(serial_client.calls, parallel_client.calls)
        self.assertEqual(len(right), 4)
        self.assertEqual(right[2]['prediction_status'], 'invalid_prediction')
        self.assertTrue(all(call[2] == 32 for call in parallel_client.calls))
        for _, prompt, _ in parallel_client.calls:
            self.assertEqual(sum(f'observation-{i}' in prompt for i in range(4)), 1)

    def test_unsupported_clients_fall_back_to_serial_requests(self):
        client = IndependentFixtureClient(); client.supports_independent_parallel_requests = False
        predictor = make_hypobench_prediction_policy(client, ['class-a'])
        self.assertEqual(len(predictor.predict_many(self.prepared(), max_workers=4)), 4)
        self.assertTrue(all(f'observation-{i}' in call[1] for i, call in enumerate(client.calls)))
