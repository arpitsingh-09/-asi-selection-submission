"""Read-only supplementary calibration for the first four claim vectors.

This separate worker never writes embeddings or edits the frozen sidecar. A
real run requires an approved amendment plus a fresh, narrowly scoped
authorization bound to this file, the amendment, and the existing manifest.
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
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
import hashlib
from importlib.metadata import PackageNotFoundError, version as package_version
import json
import math
import platform
from pathlib import Path
import resource
import sqlite3
import sys
import time
import traceback
import uuid

import numpy as np

import claim_sidecar as sidecar


EXPECTED_FIRST_FOUR = (
    '0898df02c4eb78a67cb2b8b5d615e73fd94963f353ddd9ee6c15faac2d408fba',
    '0b38c37f6df3cf3dda2732030afc6287aacfc927172385b388fe495206b02678',
    '0c4bc6e27997c779d6eb5326880f9b50bc58ec604f46b45a38d0d0537829ed3f',
    '0cca22c3fb951b60aaa223cbc73e3fc671ffd973924f29df283ddd41a3b9780c',
)
MAX_CHECK_AGE_SECONDS = 600


def _now():
    return datetime.now(timezone.utc)


def _sha(path):
    return sidecar.sha(path)


def _json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def _validate_approval(amendment_path, authorization_path, manifest_path):
    if authorization_path is None:
        raise ValueError('fresh calibration-only authorization is required')
    amendment_path = Path(amendment_path).resolve()
    if not amendment_path.is_file():
        raise ValueError('approved calibration amendment is missing')
    amendment = amendment_path.read_text(encoding='utf-8')
    if '**Status:** Approved for execution' not in amendment:
        raise ValueError('calibration amendment is not approved for execution')

    auth_path = Path(authorization_path).resolve()
    auth = _json(auth_path)
    if not isinstance(auth, dict):
        raise ValueError('calibration-only authorization must be a JSON object')
    expected = {
        'scope': 'calibration_only',
        'authorize_calibration_only': True,
        'amendment_approved': True,
        'e6_inactive_verified': True,
        'resource_headroom_verified': True,
        'manifest_sha256': _sha(manifest_path),
        'amendment_sha256': _sha(amendment_path),
        'driver_sha256': _sha(Path(__file__)),
    }
    allowed_fields = set(expected) | {
        'authorization_source', 'e6_check_utc', 'resource_check_utc',
    }
    if set(auth) != allowed_fields:
        raise ValueError('calibration-only authorization has missing or broader-scope fields')
    for key, value in expected.items():
        actual = auth.get(key)
        if isinstance(value, bool):
            valid = type(actual) is bool and actual is value
        else:
            valid = actual == value
        if not valid:
            raise ValueError('calibration-only authorization mismatch: ' + key)
    if not isinstance(auth.get('authorization_source'), str) or not auth['authorization_source'].strip():
        raise ValueError('calibration-only authorization source is required')

    # Require both environmental checks to be recent, explicit UTC timestamps.
    now = _now()
    for key in ('e6_check_utc', 'resource_check_utc'):
        raw = auth.get(key)
        if not isinstance(raw, str) or not raw:
            raise ValueError('fresh calibration-only check timestamp required: ' + key)
        try:
            stamp = datetime.fromisoformat(raw.replace('Z', '+00:00'))
        except ValueError as exc:
            raise ValueError('invalid calibration-only timestamp: ' + key) from exc
        if stamp.tzinfo is None or (now - stamp.astimezone(timezone.utc)).total_seconds() > MAX_CHECK_AGE_SECONDS:
            raise ValueError('stale calibration-only check: ' + key)
        if (stamp.astimezone(timezone.utc) - now).total_seconds() > 30:
            raise ValueError('future calibration-only check timestamp: ' + key)
    return auth, amendment_path


def _output_directory(folder, output_dir):
    folder = Path(folder).resolve()
    output_dir = Path(output_dir).absolute()
    # resolve(strict=False) follows existing parent symlinks but does not create.
    resolved = output_dir.resolve(strict=False)
    if resolved.parent != folder or not resolved.name.startswith('calibration_only_'):
        raise ValueError('output must be a fresh calibration_only_* child of the sidecar folder')
    if resolved.exists():
        raise ValueError('refusing to reuse an existing calibration output path')
    return resolved


def _sidecar_snapshot(path, manifest, allowed):
    path = Path(path).resolve()
    if not path.is_file():
        raise ValueError('the existing four-vector sidecar is required')
    conn = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)
    try:
        conn.execute('PRAGMA query_only=ON')
        rows = conn.execute(
            'SELECT text_hash,text_value,model_key,checksum,vector FROM vectors ORDER BY text_hash'
        ).fetchall()
        metadata = dict(conn.execute('SELECT key,value FROM metadata'))
        if len(rows) != 4:
            raise ValueError('calibration is restricted to exactly four already-saved vectors')
        if metadata.get('binding') != sidecar.binding(path.parent, manifest):
            raise ValueError('existing sidecar binding does not match the frozen manifest')
        parity = json.loads(metadata.get('parity', '{}'))
        if parity.get('passed') is not True or len(parity.get('controls', [])) != 3:
            raise ValueError('existing sidecar parity provenance is missing or invalid')
        by_hash = {row[0]: row for row in rows}
        if set(by_hash) != set(EXPECTED_FIRST_FOUR):
            raise ValueError('sidecar rows are not exactly the frozen first four claim requests')
        for h, text_value, model_key, checksum, blob in rows:
            req = allowed.get(h)
            if req is None or text_value != req['text'] or model_key != manifest['model_key']:
                raise ValueError('existing vector request/model binding mismatch')
            if len(blob) != sidecar.DIM * 4 or hashlib.sha256(blob).hexdigest() != checksum:
                raise ValueError('existing vector checksum/size mismatch')
            vector = np.frombuffer(blob, dtype='<f4')
            sidecar.validate_vector(vector)
        return {
            'sqlite_sha256': _sha(path),
            'row_count': len(rows),
            'rows': [
                {'text_sha256': r[0], 'vector_sha256': r[3],
                 'vector_bytes': len(r[4])}
                for r in rows
            ],
        }
    finally:
        conn.close()


def _rss_bytes():
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Darwin reports bytes; Linux and the supported non-Darwin Unix target report KiB.
    return int(value if sys.platform == 'darwin' else value * 1024)


def _finite_positive(value):
    return isinstance(value, (int, float)) and math.isfinite(value) and value > 0


def _execute(folder, amendment_path, auth, output_dir, batch_size, invocation):
    manifest, plan, allowed = sidecar.load(folder)
    manifest_path = Path(folder) / 'manifest.json'
    manifest_hash = _sha(manifest_path)
    requests = sidecar.read_rows(plan['requests_path'])
    if tuple(r['text_sha256'] for r in requests[:4]) != EXPECTED_FIRST_FOUR:
        raise ValueError('frozen first-four request list mismatch')
    selected = requests[:4]
    if any(r['text_sha256'] not in allowed for r in selected):
        raise ValueError('calibration request is not in the frozen request set')
    if batch_size not in (1, 2):
        raise ValueError('calibration batch size must be 1 or 2')
    if output_dir.exists():
        raise ValueError('refusing to reuse an existing calibration output path')

    sidecar_path = Path(folder) / sidecar.SIDECAR
    pre_sidecar = _sidecar_snapshot(sidecar_path, manifest, allowed)
    original_path = Path(plan['existing_cache'])
    pre_original_sha = _sha(original_path)
    if pre_original_sha != plan['existing_cache_sha256']:
        raise ValueError('original embedding cache hash mismatch')
    run_id = str(uuid.uuid4())
    output_dir.mkdir(mode=0o700, parents=False, exist_ok=False)
    stdout_path = output_dir / 'stdout.log'
    stderr_path = output_dir / 'stderr.log'
    report_path = output_dir / 'calibration_report.json'

    try:
        with stdout_path.open('x', encoding='utf-8') as stdout_file, stderr_path.open('x', encoding='utf-8') as stderr_file:
            with redirect_stdout(stdout_file), redirect_stderr(stderr_file):
                try:
                    started_utc = _now()
                    total_start = time.monotonic_ns()
                    load_start = total_start
                    inv = _json(plan['model_inventory_path'])
                    # Always use the frozen production factory. Tests patch this
                    # module binding; callers cannot inject an alternate encoder.
                    encoder = sidecar.cpu_factory(inv)
                    load_end = time.monotonic_ns()

                    control_rows = _json(plan['parity_controls_path'])
                    if len(control_rows) != 3:
                        raise ValueError('exactly three frozen parity controls are required')
                    parity_start = time.monotonic_ns()
                    original = sidecar.Cache(original_path)
                    parity_results = []
                    try:
                        for control in control_rows:
                            if sidecar.text_hash(control['text']) != control['text_sha256']:
                                raise ValueError('parity control text hash mismatch')
                            expected = original.get(control['text'])
                            expected_hash = hashlib.sha256(expected.astype('<f4').tobytes()).hexdigest()
                            if expected_hash != control['normalized_float32_vector_sha256']:
                                raise ValueError('parity cache vector hash mismatch')
                            raw = np.asarray(encoder([control['text']]), dtype=np.float32)
                            if raw.shape != (1, sidecar.DIM):
                                raise ValueError('parity encoder alignment/shape mismatch')
                            got = sidecar.normalized(raw[0])
                            if not np.allclose(
                                got, expected, atol=manifest['parity_atol'], rtol=manifest['parity_rtol']
                            ):
                                raise ValueError('pinned encoder parity failed')
                            parity_results.append({
                                'text_sha256': control['text_sha256'],
                                'max_absolute_difference': float(np.abs(got - expected).max()),
                                'passed': True,
                            })
                    finally:
                        original.close()
                    parity_end = time.monotonic_ns()

                    claim_start = time.monotonic_ns()
                    claim_results = []
                    for start in range(0, 4, batch_size):
                        batch = selected[start:start + batch_size]
                        raw_batch = np.asarray(encoder([r['text'] for r in batch]), dtype=np.float32)
                        if raw_batch.shape != (len(batch), sidecar.DIM):
                            raise ValueError('claim encoder batch alignment/shape mismatch')
                        for request, raw in zip(batch, raw_batch):
                            computed = sidecar.normalized(raw)
                            claim_results.append((request, computed))
                    claim_end = time.monotonic_ns()

                    # Reopen with the frozen read-only validator; no writer is constructed.
                    saved_sidecar = sidecar.Sidecar(
                        sidecar_path, sidecar.binding(folder, manifest), allowed,
                        manifest['model_key'], write=False,
                    )
                    vector_checks = []
                    try:
                        for request, computed in claim_results:
                            saved = saved_sidecar.get_hash(request['text_sha256'])
                            if saved is None:
                                raise ValueError('saved calibration vector disappeared')
                            if not np.allclose(
                                computed, saved, atol=manifest['parity_atol'], rtol=manifest['parity_rtol']
                            ):
                                raise ValueError('recomputed vector differs from saved vector')
                            vector_checks.append({
                                'text_sha256': request['text_sha256'],
                                'saved_vector_sha256': hashlib.sha256(saved.astype('<f4').tobytes()).hexdigest(),
                                'recomputed_vector_sha256': hashlib.sha256(computed.astype('<f4').tobytes()).hexdigest(),
                                'max_absolute_difference': float(np.abs(computed - saved).max()),
                                'passed': True,
                            })
                    finally:
                        saved_sidecar.close()

                    post_sidecar = _sidecar_snapshot(sidecar_path, manifest, allowed)
                    post_original_sha = _sha(original_path)
                    if post_sidecar != pre_sidecar:
                        raise ValueError('sidecar changed during calibration-only run')
                    if post_original_sha != pre_original_sha:
                        raise ValueError('original embedding cache changed during calibration-only run')
                    if len(vector_checks) != 4 or len(parity_results) != 3:
                        raise ValueError('incomplete calibration checks')
                    total_end = time.monotonic_ns()
                    ended_utc = _now()
                    elapsed = (total_end - total_start) / 1e9
                    try:
                        torch_version = package_version('torch')
                    except PackageNotFoundError:
                        torch_version = None
                    try:
                        transformers_version = package_version('transformers')
                    except PackageNotFoundError:
                        transformers_version = None
                    try:
                        adapters_version = package_version('adapters')
                    except PackageNotFoundError:
                        adapters_version = None
                    peak_rss = _rss_bytes()
                    if not _finite_positive(elapsed) or peak_rss <= 0:
                        raise ValueError('invalid elapsed-time or peak-RSS measurement')
                    report = {
                        'format': 1,
                        'run_type': 'supplementary_calibration_only',
                        'run_id': run_id,
                        'invocation': invocation,
                        'exit_status': 0,
                        'started_at_utc': started_utc.isoformat(),
                        'ended_at_utc': ended_utc.isoformat(),
                        'wall_clock_source': 'datetime.now(timezone.utc)',
                        'manifest_sha256': manifest_hash,
                        'amendment_path': str(Path(amendment_path).resolve()),
                        'amendment_sha256': _sha(amendment_path),
                        'calibration_driver_path': str(Path(__file__).resolve()),
                        'calibration_driver_sha256': _sha(Path(__file__)),
                        'model_key': manifest['model_key'],
                        'model_id': sidecar.MODEL,
                        'base_revision': sidecar.BASE_REV,
                        'adapter_revision': sidecar.ADAPTER_REV,
                        'representation': {
                            'dimension': sidecar.DIM, 'dtype': 'float32',
                            'normalization': 'unit_L2', 'device': 'cpu',
                            'max_length': 512, 'batch_size': batch_size,
                        },
                        'python_version': platform.python_version(),
                        'numpy_version': np.__version__,
                        'torch_version': torch_version,
                        'transformers_version': transformers_version,
                        'adapters_version': adapters_version,
                        'platform': platform.platform(),
                        'process_id': os.getpid(),
                        'thread_environment': {
                            key: os.environ.get(key) for key in (
                                'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
                                'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS',
                            )
                        },
                        'timing_source': 'time.monotonic_ns',
                        'elapsed_seconds': elapsed,
                        'phase_seconds': {
                            'model_load': (load_end - load_start) / 1e9,
                            'parity': (parity_end - parity_start) / 1e9,
                            'four_claim_batch': (claim_end - claim_start) / 1e9,
                        },
                        'peak_rss_source': 'resource.getrusage(RUSAGE_SELF).ru_maxrss',
                        'process_peak_rss_bytes': peak_rss,
                        'peak_rss_unit_rule': 'Darwin ru_maxrss bytes; other supported Unix platforms converted from KiB',
                        'new_vectors_generated': 4,
                        'persisted_vectors': 0,
                        'claim_request_sha256': [r['text_sha256'] for r in selected],
                        'parity_controls': parity_results,
                        'claim_vector_comparisons': vector_checks,
                        'sidecar_before': pre_sidecar,
                        'sidecar_after': post_sidecar,
                        'original_cache_sha256_before': pre_original_sha,
                        'original_cache_sha256_after': post_original_sha,
                        'technical_checks_passed': True,
                        'human_accepted': False,
                        'output_directory': str(output_dir),
                    }
                    # Exclusive creation prevents replacing any prior report.
                    with report_path.open('x', encoding='utf-8') as f:
                        json.dump(report, f, indent=2, allow_nan=False)
                        f.write('\n')
                    print(json.dumps({'report_path': str(report_path), 'run_id': run_id}, indent=2))
                    return report
                except BaseException:
                    traceback.print_exc(file=sys.stderr)
                    raise
    except BaseException:
        # The fresh run directory and logs are retained; no success report is made.
        raise


def run_calibration(folder, amendment_path, authorization_path, output_dir,
                    claim_count=4, batch_size=2, device='cpu', dtype='float32'):
    if type(claim_count) is not int or claim_count != 4:
        raise ValueError('calibration-only driver is restricted to exactly four claims')
    if device != 'cpu' or dtype != 'float32':
        raise ValueError('calibration-only representation is fixed to CPU float32')
    if type(batch_size) is not int or batch_size not in (1, 2):
        raise ValueError('calibration batch size must be 1 or 2')
    folder = Path(folder).resolve()
    manifest_path = folder / 'manifest.json'
    manifest, _, _ = sidecar.load(folder)
    auth, approved_amendment = _validate_approval(
        amendment_path, authorization_path, manifest_path
    )
    out = _output_directory(folder, output_dir)
    invocation = {
        'entrypoint': 'run_calibration',
        'process_argv': [sys.argv[0], *sys.argv[1:]],
        'parameters': {
            'folder': str(folder),
            'amendment': str(approved_amendment),
            'authorization': str(Path(authorization_path).resolve()),
            'output_dir': str(out),
            'claim_count': claim_count,
            'batch_size': batch_size,
            'device': device,
            'dtype': dtype,
        },
    }
    return _execute(folder, approved_amendment, auth, out, batch_size, invocation)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('run',))
    parser.add_argument('--folder', type=Path, required=True)
    parser.add_argument('--amendment', type=Path, required=True)
    parser.add_argument('--authorization', type=Path, required=True)
    parser.add_argument('--claim-count', type=int, default=4)
    parser.add_argument('--batch-size', type=int, default=2)
    parser.add_argument('--device', choices=('cpu',), default='cpu')
    parser.add_argument('--dtype', choices=('float32',), default='float32')
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args(argv)
    run_calibration(
        args.folder, args.amendment, args.authorization, args.output_dir,
        args.claim_count, args.batch_size, args.device, args.dtype,
    )


if __name__ == '__main__':
    main()
