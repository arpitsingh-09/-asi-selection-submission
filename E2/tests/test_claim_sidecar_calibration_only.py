"""Offline-only tests for the isolated calibration-only worker.

No torch model or real encoder is loaded; fake vectors exercise the gates.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

import numpy as np

E2_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(E2_ROOT))

import claim_sidecar as sidecar
import claim_sidecar_calibration_only as calibration


FIRST_CLAIMS = (
    'The outcomes of the U-Net architecture have been thoroughly tested and compared with 5-fold validation datasets.',
    'LIME and SHAP explanations reveal which terms influence the model predictions of dark patterns.',
    'BANG achieves absolute improvements of 14.01 and 5.24 in the overall scores of SQuAD 1.1 and XSum compared with semi-NAR strong baselines.',
    'Separated convolutional front-ends are proposed for prosodic and spectral features in Transformer-based ASR.',
)


class CalibrationOnlyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.original = self.root / 'original.sqlite3'
        self.controls = [
            {'text': f'control {i}', 'text_sha256': sidecar.text_hash(f'control {i}')}
            for i in range(3)
        ]
        with sqlite3.connect(self.original) as conn:
            conn.execute('CREATE TABLE embeddings(model_id TEXT,text_hash TEXT,text_value TEXT,vector_json TEXT,PRIMARY KEY(model_id,text_hash))')
            for control in self.controls:
                vector = self.vector(control['text'])
                control['normalized_float32_vector_sha256'] = hashlib.sha256(vector.astype('<f4').tobytes()).hexdigest()
                conn.execute('INSERT INTO embeddings VALUES(?,?,?,?)', (
                    sidecar.MODEL, control['text_sha256'], control['text'], json.dumps(vector.tolist()),
                ))

        self.claims = [{'paper_id': f'paper-{i}', 'claims': []} for i in range(52)]
        self.requests = []
        for i in range(93):
            paper_idx = i % 52
            claim = FIRST_CLAIMS[i] if i < 4 else f'synthetic request {i}'
            claim_idx = len(self.claims[paper_idx]['claims'])
            self.claims[paper_idx]['claims'].append({'claim': claim})
            self.requests.append({
                'text': claim,
                'text_sha256': sidecar.text_hash(claim),
                'model_id': sidecar.MODEL,
                'uses': [{'paper_id': f'paper-{paper_idx}', 'claim_index': claim_idx}],
            })
        self.assertEqual(tuple(r['text_sha256'] for r in self.requests[:4]), calibration.EXPECTED_FIRST_FOUR)

        def write(name, data, jsonl=False):
            path = self.root / name
            if jsonl:
                path.write_text(''.join(json.dumps(row) + '\n' for row in data))
            else:
                path.write_text(json.dumps(data))
            return path

        requests_path = write('requests.jsonl', self.requests, True)
        claims_path = write('claims.jsonl', self.claims, True)
        pools_path = write('pools.jsonl', [{'paper_id': f'paper-{i}'} for i in range(52)], True)
        controls_path = write('controls.json', self.controls)
        inventory = {'base_revision': sidecar.BASE_REV, 'adapter_revision': sidecar.ADAPTER_REV, 'assets': {}}
        inventory_path = write('inventory.json', inventory)
        self.plan = {
            'existing_cache': str(self.original),
            'existing_cache_sha256': sidecar.sha(self.original),
            'base_revision': sidecar.BASE_REV,
            'adapter_revision': sidecar.ADAPTER_REV,
            'unique_required_claim_texts': 93,
            'representation': {'model_id': sidecar.MODEL, 'dimension': 768, 'max_length': 512, 'dtype': 'float32'},
            'requests_path': str(requests_path),
            'requests_sha256': sidecar.sha(requests_path),
            'claim_source_path': str(claims_path),
            'claim_source_sha256': sidecar.sha(claims_path),
            'fixed_condition_pools_path': str(pools_path),
            'fixed_condition_pools_sha256': sidecar.sha(pools_path),
            'parity_controls_path': str(controls_path),
            'parity_controls_sha256': sidecar.sha(controls_path),
            'model_inventory_path': str(inventory_path),
            'model_inventory_sha256': sidecar.sha(inventory_path),
        }
        self.plan_path = write('plan.json', self.plan)
        self.folder = self.root / 'claim_sidecar_v1'
        sidecar.prepare(self.plan_path, self.folder)
        self._create_four_vectors()
        self.amendment = self.folder / 'amendment.md'
        self.amendment.write_text('**Status:** Approved for execution\n')
        self.auth = self.root / 'calibration_authorization.json'
        self._write_auth()
        self.original_sha = sidecar.sha(self.original)

    def tearDown(self):
        self.assertEqual(sidecar.sha(self.original), self.original_sha)
        self.tmp.cleanup()

    @staticmethod
    def vector(text):
        vector = np.zeros(sidecar.DIM, dtype=np.float32)
        vector[int(sidecar.text_hash(text)[:8], 16) % sidecar.DIM] = 1.0
        return vector

    def _create_four_vectors(self):
        manifest, _, allowed = sidecar.load(self.folder)
        parity = {'passed': True, 'controls': [
            {'text_sha256': r['text_sha256'], 'max_absolute_difference': 0.0} for r in self.controls
        ]}
        db = sidecar.Sidecar(
            self.folder / sidecar.SIDECAR,
            sidecar.binding(self.folder, manifest), allowed, manifest['model_key'],
            write=True, parity=parity,
        )
        db.put_batch([(r['text_sha256'], self.vector(r['text'])) for r in self.requests[:4]])
        db.close()

    def _write_auth(self):
        now = datetime.now(timezone.utc).isoformat()
        data = {
            'scope': 'calibration_only',
            'authorize_calibration_only': True,
            'amendment_approved': True,
            'e6_inactive_verified': True,
            'resource_headroom_verified': True,
            'manifest_sha256': sidecar.sha(self.folder / 'manifest.json'),
            'amendment_sha256': sidecar.sha(self.amendment),
            'driver_sha256': sidecar.sha(calibration.__file__),
            'authorization_source': 'synthetic offline test fixture',
            'e6_check_utc': now,
            'resource_check_utc': now,
        }
        self.auth.write_text(json.dumps(data))

    def encoder_factory(self):
        def factory(_inventory):
            return lambda texts: np.stack([self.vector(text) for text in texts])
        return factory

    def run_ok(self, output_name='calibration_only_test'):
        with patch.object(calibration.sidecar, 'cpu_factory', self.encoder_factory()):
            return calibration.run_calibration(
                self.folder, self.amendment, self.auth, self.folder / output_name,
            )

    def test_existing_vectors_are_read_only_and_never_overwritten(self):
        db = self.folder / sidecar.SIDECAR
        before = sidecar.sha(db)
        report = self.run_ok()
        self.assertEqual(report['persisted_vectors'], 0)
        self.assertEqual(report['new_vectors_generated'], 4)
        self.assertGreater(report['process_peak_rss_bytes'], 0)
        self.assertGreater(report['elapsed_seconds'], 0)
        self.assertEqual(report['exit_status'], 0)
        self.assertIn('entrypoint', report['invocation'])
        self.assertTrue(report['wall_clock_source'])
        self.assertEqual(sidecar.sha(db), before)
        self.assertEqual(report['sidecar_before'], report['sidecar_after'])
        with self.assertRaisesRegex(ValueError, 'refusing to reuse'):
            self.run_ok()
        self.assertEqual(sidecar.sha(db), before)

    def test_rejects_more_than_four_claims_before_encoder_factory(self):
        factory = Mock(side_effect=AssertionError('must not initialize encoder'))
        with patch.object(calibration.sidecar, 'cpu_factory', factory):
            with self.assertRaisesRegex(ValueError, 'exactly four claims'):
                calibration.run_calibration(
                    self.folder, self.amendment, self.auth,
                    self.folder / 'calibration_only_too_many', claim_count=5,
                )
        factory.assert_not_called()

    def test_frozen_hash_mismatch_stops_before_encoder(self):
        request_file = Path(self.plan['requests_path'])
        request_file.write_text(request_file.read_text() + '\n')
        factory = Mock(side_effect=AssertionError('must not initialize encoder'))
        with patch.object(calibration.sidecar, 'cpu_factory', factory):
            with self.assertRaisesRegex(ValueError, 'frozen sidecar binding changed'):
                calibration.run_calibration(
                    self.folder, self.amendment, self.auth,
                    self.folder / 'calibration_only_hash_failure',
                )
        factory.assert_not_called()

    def test_missing_authorization_stops_before_encoder(self):
        factory = Mock(side_effect=AssertionError('must not initialize encoder'))
        with patch.object(calibration.sidecar, 'cpu_factory', factory):
            with self.assertRaisesRegex(ValueError, 'authorization is required'):
                calibration.run_calibration(
                    self.folder, self.amendment, None,
                    self.folder / 'calibration_only_no_auth',
                )
        factory.assert_not_called()

    def test_failed_parity_creates_no_report_or_acceptance(self):
        output = self.folder / 'calibration_only_bad_parity'
        def bad_factory(_inventory):
            return lambda texts: np.stack([np.roll(self.vector(text), 1) for text in texts])
        with patch.object(calibration.sidecar, 'cpu_factory', bad_factory):
            with self.assertRaisesRegex(ValueError, 'parity failed'):
                calibration.run_calibration(
                    self.folder, self.amendment, self.auth, output,
                )
        self.assertFalse((output / 'calibration_report.json').exists())
        self.assertTrue((output / 'stderr.log').exists())
        self.assertIn('pinned encoder parity failed', (output / 'stderr.log').read_text())

    def test_approval_fields_and_output_path_are_required(self):
        data = json.loads(self.auth.read_text())
        data['scope'] = 'all_inference'
        self.auth.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'authorization mismatch: scope'):
            self.run_ok('calibration_only_wrong_scope')

        self._write_auth()
        data = json.loads(self.auth.read_text())
        data['authorize_inference'] = True
        self.auth.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'broader-scope fields'):
            self.run_ok('calibration_only_broad_auth')


if __name__ == '__main__':
    unittest.main()
