"""Offline tests for adapter diagnostic gates; no model loading or inference."""
from pathlib import Path
import hashlib
import sys
import tempfile
import unittest
from unittest.mock import Mock

E2_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(E2_ROOT))

import claim_sidecar_adapter_diagnostic as diagnostic


class FakeComposition:
    def __init__(self, *names):
        self.names = names

    def flatten(self):
        return set(self.names)


class FakeModel:
    def __init__(self, active):
        self.active_adapters = active


class AdapterDiagnosticTests(unittest.TestCase):
    def test_exact_proximity_setup_is_reported(self):
        self.assertEqual(
            diagnostic._active_names(FakeModel(FakeComposition('proximity'))),
            ['proximity'],
        )

    def test_empty_setup_is_reported_as_empty(self):
        self.assertEqual(diagnostic._active_names(FakeModel(None)), [])

    def test_different_or_composed_setup_is_not_accepted(self):
        self.assertEqual(
            diagnostic._active_names(FakeModel(FakeComposition('other'))),
            ['other'],
        )
        self.assertEqual(
            diagnostic._active_names(FakeModel(FakeComposition('proximity', 'other'))),
            ['other', 'proximity'],
        )

    def test_initialization_context_is_classified_but_not_activation_checked(self):
        ledger = []
        initialization = []
        current_call = {'labels': None}
        original = Mock(return_value='initialized')
        audited = diagnostic._audited_forward_context(
            original, current_call, ledger, initialization,
        )

        # Adapter setup/reset can enter ForwardContext before activation is
        # finalized. That internal context is excluded from encoding evidence.
        result = audited(FakeModel(None), object())

        self.assertEqual(result, 'initialized')
        self.assertEqual(ledger, [])
        self.assertEqual(initialization, [{
            'context_index': 1,
            'classification': 'adapter_initialization',
        }])
        original.assert_called_once()

    def test_real_forward_checks_effective_proximity_adapter(self):
        ledger = []
        initialization = []
        current_call = {'labels': [{'kind': 'claim', 'text_sha256': 'abc'}]}
        original = Mock(return_value='encoded')
        audited = diagnostic._audited_forward_context(
            original, current_call, ledger, initialization,
        )

        result = audited(FakeModel(FakeComposition('proximity')), object())

        self.assertEqual(result, 'encoded')
        self.assertEqual(len(ledger), 1)
        self.assertEqual(ledger[0]['effective_active_adapters'], ['proximity'])
        self.assertTrue(ledger[0]['passed'])
        original.assert_called_once()

    def test_real_forward_with_wrong_adapter_fails_before_forward(self):
        ledger = []
        initialization = []
        current_call = {'labels': [{'kind': 'claim', 'text_sha256': 'abc'}]}
        original = Mock(return_value='must not encode')
        audited = diagnostic._audited_forward_context(
            original, current_call, ledger, initialization,
        )

        with self.assertRaisesRegex(RuntimeError, 'during encoding forward'):
            audited(FakeModel(FakeComposition('other')), object())

        self.assertEqual(len(ledger), 1)
        self.assertFalse(ledger[0]['passed'])
        original.assert_not_called()

    def test_post_load_adapter_identity_is_enforced(self):
        state = {}
        diagnostic._verify_post_load_activation(
            FakeModel(FakeComposition('proximity')), state,
        )
        self.assertEqual(state['post_load_active_adapters'], ['proximity'])
        self.assertTrue(state['post_load_activation_passed'])

        with self.assertRaisesRegex(RuntimeError, 'after model and adapter loading'):
            diagnostic._verify_post_load_activation(
                FakeModel(FakeComposition('other')), {},
            )

    def test_model_and_adapter_asset_hashes_are_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            asset = Path(tmp) / 'adapter.bin'
            asset.write_bytes(b'frozen adapter bytes')
            expected_hash = hashlib.sha256(asset.read_bytes()).hexdigest()
            inventory = {
                'base_revision': diagnostic.sidecar.BASE_REV,
                'adapter_revision': diagnostic.sidecar.ADAPTER_REV,
                'assets': {str(asset): {'sha256': expected_hash}},
            }

            checks = diagnostic._verify_model_assets(inventory)
            self.assertEqual(checks[0]['sha256'], expected_hash)
            self.assertTrue(checks[0]['passed'])

            asset.write_bytes(b'changed adapter bytes')
            with self.assertRaisesRegex(ValueError, 'asset hash mismatch'):
                diagnostic._verify_model_assets(inventory)


if __name__ == '__main__':
    unittest.main()
