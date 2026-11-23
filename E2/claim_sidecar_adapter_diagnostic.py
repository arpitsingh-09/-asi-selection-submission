"""Read-only adapter-activation diagnostic for the four frozen E2 claims.

This worker is separate from the frozen encoder and calibration driver. It
reuses their model loader and calibration checks, while recording the effective
adapter setup at every adapters forward-context entry. It never writes vectors.
"""
import os

for _name in (
    'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
    'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS',
):
    os.environ[_name] = '1'
os.environ.update(
    HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
    TOKENIZERS_PARALLELISM='false', CUDA_VISIBLE_DEVICES='',
)

import argparse
from datetime import datetime, timezone
import inspect
import json
from pathlib import Path

import claim_sidecar as sidecar
import claim_sidecar_calibration_only as calibration


FIRST_FOUR = calibration.EXPECTED_FIRST_FOUR


def _sha(path):
    return sidecar.sha(path)


def _read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def _validate_auth(folder, amendment_path, auth_path):
    manifest_path = folder / 'manifest.json'
    amendment_path = Path(amendment_path).resolve()
    auth_path = Path(auth_path).resolve()
    amendment_text = amendment_path.read_text(encoding='utf-8')
    if '**Status:** Approved for execution' not in amendment_text:
        raise ValueError('diagnostic amendment is not approved for execution')
    auth = _read_json(auth_path)
    expected = {
        'scope': 'adapter_diagnostic_only',
        'authorize_adapter_diagnostic_only': True,
        'amendment_approved': True,
        'e6_inactive_verified': True,
        'resource_headroom_verified': True,
        'manifest_sha256': _sha(manifest_path),
        'amendment_sha256': _sha(amendment_path),
        'calibration_driver_sha256': _sha(Path(calibration.__file__)),
        'diagnostic_driver_sha256': _sha(Path(__file__)),
    }
    allowed_fields = set(expected) | {
        'authorization_source', 'e6_check_utc', 'resource_check_utc',
    }
    if not isinstance(auth, dict) or set(auth) != allowed_fields:
        raise ValueError('diagnostic authorization is missing fields or has broader scope')
    for key, value in expected.items():
        actual = auth.get(key)
        if type(value) is bool:
            valid = type(actual) is bool and actual is value
        else:
            valid = actual == value
        if not valid:
            raise ValueError('diagnostic authorization mismatch: ' + key)
    if not isinstance(auth.get('authorization_source'), str) or not auth['authorization_source'].strip():
        raise ValueError('diagnostic authorization source is required')
    return auth, amendment_path


def _freshness(auth):
    now = datetime.now(timezone.utc)
    for key in ('e6_check_utc', 'resource_check_utc'):
        raw = auth.get(key)
        try:
            stamp = datetime.fromisoformat(raw.replace('Z', '+00:00'))
        except (AttributeError, ValueError) as exc:
            raise ValueError('invalid diagnostic check timestamp: ' + key) from exc
        if stamp.tzinfo is None:
            raise ValueError('timezone-aware diagnostic timestamp required: ' + key)
        age = (now - stamp.astimezone(timezone.utc)).total_seconds()
        if age > calibration.MAX_CHECK_AGE_SECONDS or age < -30:
            raise ValueError('stale or future diagnostic check: ' + key)


def _active_names(model):
    active = getattr(model, 'active_adapters', None)
    if not active:
        from adapters.context import AdapterSetup
        active = AdapterSetup.get_context_adapter_setup()
    if not active:
        return []
    flatten = getattr(active, 'flatten', None)
    if not callable(flatten):
        raise ValueError('adapter setup does not expose a verifiable composition')
    return sorted(str(name) for name in flatten())


def _audited_forward_context(original_forward_context, current_call,
                             ledger, initialization_contexts):
    """Ignore adapter setup's internal contexts; check encoding forwards only."""
    def audited(model, context, *args, **kwargs):
        labels = current_call['labels']
        if labels is None:
            initialization_contexts.append({
                'context_index': len(initialization_contexts) + 1,
                'classification': 'adapter_initialization',
            })
            return original_forward_context(model, context, *args, **kwargs)

        names = _active_names(model)
        event = {
            'forward_index': len(ledger) + 1,
            'inputs': labels,
            'effective_active_adapters': names,
            'passed': names == ['proximity'],
        }
        ledger.append(event)
        if not event['passed']:
            raise RuntimeError(
                'adapter activation check failed during encoding forward: '
                + json.dumps(event, sort_keys=True)
            )
        return original_forward_context(model, context, *args, **kwargs)

    return audited


def _verify_post_load_activation(model, loader_state):
    names = _active_names(model)
    loader_state['post_load_active_adapters'] = names
    loader_state['post_load_activation_passed'] = names == ['proximity']
    if not loader_state['post_load_activation_passed']:
        raise RuntimeError(
            'proximity adapter is not active after model and adapter loading: '
            + json.dumps(names)
        )


def _verify_model_assets(inventory):
    if (inventory.get('base_revision') != sidecar.BASE_REV
            or inventory.get('adapter_revision') != sidecar.ADAPTER_REV):
        raise ValueError('frozen base or adapter revision mismatch')
    checks = []
    for path, info in inventory['assets'].items():
        actual = _sha(path)
        if actual != info['sha256']:
            raise ValueError('frozen model/adapter asset hash mismatch: ' + path)
        checks.append({'path': path, 'sha256': actual, 'passed': True})
    return checks


def _make_instrumented_factory(folder, ledger, initialization_contexts, loader_state):
    _, plan, _allowed = sidecar.load(folder)
    controls = _read_json(plan['parity_controls_path'])
    request_rows = sidecar.read_rows(plan['requests_path'])[:4]
    labels = {
        row['text_sha256']: {'kind': 'parity_control', 'text_sha256': row['text_sha256']}
        for row in controls
    }
    labels.update({
        row['text_sha256']: {'kind': 'claim', 'text_sha256': row['text_sha256']}
        for row in request_rows
    })
    if len(controls) != 3 or tuple(row['text_sha256'] for row in request_rows) != FIRST_FOUR:
        raise ValueError('diagnostic input set is not exactly three controls and four frozen claims')

    def factory(inventory):
        from adapters.model_mixin import ModelAdaptersMixin
        from task3_execution import batched_cpu_encoder

        asset_checks = _verify_model_assets(inventory)
        loader_state['model_id'] = sidecar.MODEL
        loader_state['base_revision'] = inventory['base_revision']
        loader_state['adapter_revision'] = inventory['adapter_revision']
        loader_state['model_asset_hash_checks'] = asset_checks

        # Patch only this process. The frozen loader still verifies model files,
        # loads the same pinned model/adapter, and returns its normal encoder.
        original_forward_context = ModelAdaptersMixin.forward_context
        current_call = {'labels': None}
        ModelAdaptersMixin.forward_context = _audited_forward_context(
            original_forward_context, current_call, ledger, initialization_contexts,
        )
        try:
            encoder = batched_cpu_encoder({'model_inventory': inventory})
            model = inspect.getclosurevars(encoder).nonlocals.get('model')
            if model is None or not hasattr(model, 'active_adapters'):
                raise RuntimeError('could not inspect loaded model adapter state')
            _verify_post_load_activation(model, loader_state)
        except BaseException:
            ModelAdaptersMixin.forward_context = original_forward_context
            raise

        def audited_encoder(texts):
            hashes = [sidecar.text_hash(text) for text in texts]
            if not hashes or any(h not in labels for h in hashes):
                raise ValueError('forward request is outside the three controls and four frozen claims')
            current_call['labels'] = [labels[h] for h in hashes]
            try:
                return encoder(texts)
            finally:
                current_call['labels'] = None

        # Keep patch active across all forward calls; calibration calls this
        # encoder serially, and the process exits after restoring the method.
        audited_encoder._restore_forward_context = lambda: setattr(
            ModelAdaptersMixin, 'forward_context', original_forward_context
        )
        return audited_encoder

    return factory


def _output_path(folder, output_dir):
    out = Path(output_dir).resolve(strict=False)
    if out.parent != folder or not out.name.startswith('adapter_diagnostic_'):
        raise ValueError('output must be a new adapter_diagnostic_* child directory')
    if out.exists():
        raise ValueError('refusing to reuse an existing diagnostic output path')
    return out


def run(folder, amendment, authorization, output_dir):
    folder = Path(folder).resolve()
    if not folder.is_dir():
        raise ValueError('sidecar folder is missing')
    manifest_path = folder / 'manifest.json'
    _, plan, _allowed = sidecar.load(folder)
    auth, approved_amendment = _validate_auth(folder, amendment, authorization)
    _freshness(auth)
    out = _output_path(folder, output_dir)
    ledger = []
    initialization_contexts = []
    loader_state = {}
    factory = _make_instrumented_factory(
        folder, ledger, initialization_contexts, loader_state,
    )
    invocation = {
        'entrypoint': 'adapter_diagnostic.run',
        'claim_count': 4,
        'parity_control_count': 3,
        'batch_size': 1,
        'device': 'cpu',
        'dtype': 'float32',
        'output_dir': str(out),
    }

    # The base worker provides read-only DB checks, exact frozen-input checks,
    # parity/vector comparisons, fresh-path handling and genuine metrics.
    original_factory = sidecar.cpu_factory
    completed = False
    error = None
    encoder_holder = []
    original_instrumented_factory = factory

    def tracked_factory(inventory):
        encoder = original_instrumented_factory(inventory)
        encoder_holder.append(encoder)
        return encoder

    sidecar.cpu_factory = tracked_factory
    try:
        report = calibration._execute(
            folder, approved_amendment, auth, out, batch_size=1,
            invocation=invocation,
        )
        completed = True
    except BaseException as exc:
        error = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        if encoder_holder:
            encoder_holder[0]._restore_forward_context()
        sidecar.cpu_factory = original_factory
        for cell in ledger:
            # Successful calibration must produce exactly three parity and
            # four claim forward contexts; failures preserve partial evidence.
            cell['passed'] = cell['effective_active_adapters'] == ['proximity']
        diagnostic = {
            'format': 1,
            'run_type': 'adapter_activation_diagnostic_only',
            'status': 'completed' if completed else 'failed',
            'error': error,
            'manifest_sha256': _sha(manifest_path),
            'amendment_path': str(approved_amendment),
            'amendment_sha256': _sha(approved_amendment),
            'diagnostic_driver_path': str(Path(__file__).resolve()),
            'diagnostic_driver_sha256': _sha(Path(__file__)),
            'calibration_driver_sha256': _sha(Path(calibration.__file__)),
            'authorization_path': str(Path(authorization).resolve()),
            'authorization_sha256': _sha(authorization),
            'calibration_report_path': str(out / 'calibration_report.json'),
            'calibration_report_sha256': (
                _sha(out / 'calibration_report.json')
                if (out / 'calibration_report.json').is_file() else None
            ),
            'sidecar_sha256': _sha(folder / sidecar.SIDECAR),
            'model_identity_and_hash_checks': loader_state,
            'initialization_context_count': len(initialization_contexts),
            'initialization_contexts': initialization_contexts,
            'expected_forward_contexts': 7,
            'observed_forward_contexts': len(ledger),
            'forward_contexts': ledger,
            'all_contexts_used_proximity': bool(ledger) and len(ledger) == 7 and all(
                event['passed'] for event in ledger
            ),
            'human_accepted': False,
        }
        if out.exists():
            report_path = out / 'adapter_activation_diagnostic.json'
            with report_path.open('x', encoding='utf-8') as handle:
                json.dump(diagnostic, handle, indent=2, allow_nan=False)
                handle.write('\n')
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder', type=Path, required=True)
    parser.add_argument('--amendment', type=Path, required=True)
    parser.add_argument('--authorization', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args(argv)
    run(args.folder, args.amendment, args.authorization, args.output_dir)


if __name__ == '__main__':
    main()
