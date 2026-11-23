"""Encode only the frozen nearest-planting requests. Default is a read-only inventory."""
import argparse
import fcntl
import json
from pathlib import Path
import re
import shutil
import subprocess

from claim_sidecar import Cache, Sidecar, canonical, cpu_factory, normalized, sha, text_hash
from cached_extensions import MODEL, text
import numpy as np

ROOT = Path(__file__).resolve().parent
AREA = ROOT / 'analysis'
REQUESTS = AREA / 'nearest_planting_vector_requests_v1/requests.jsonl'
PLANS = AREA / 'cached_extensions_v1/nearest_planting_plan.jsonl'
OUTPUT = AREA / 'nearest_planting_vectors_v1'
DATABASE = OUTPUT / 'modified_papers.sqlite3'
INPUT_HASHES = {
    REQUESTS: 'e15e929318000061900141f5709d68c47bfbe624ee62b7cf3d3eb3a367e21cac',
    PLANS: '3d348128c57a8d996dff8116ed192bb61d15f8a501df64478e004629ec8e8877',
}
MODEL_MANIFEST = AREA / 'claim_sidecar_v1/manifest.json'
CACHE = ROOT / 'data/novelty_embeddings.sqlite3'
INVENTORY = AREA / 'task3_execution_v1/model_inventory.json'
CONTROLS = AREA / 'task2_extension_52_v1/future_encoder_parity_controls.json'


def inputs():
    if sha(MODEL_MANIFEST) != 'a33e042bc0defaa72f658e421dc3e2ad8f0ad3fbcdf4c04b250604353d50998f':
        raise ValueError('encoder manifest changed')
    model = json.loads(MODEL_MANIFEST.read_text())
    hashes = dict(INPUT_HASHES)
    for path, digest in (model['code_sha256'] | model['source_sha256']).items():
        rel = Path(path).relative_to('/Users/arpit/asi-selection/E2')
        hashes[ROOT / rel] = digest
    for path, digest in hashes.items():
        if sha(path) != digest:
            raise ValueError(f'frozen input changed: {path}')
    allowed = {row['text_sha256']: row for row in map(json.loads, REQUESTS.open())}
    expected = {text(p) for row in map(json.loads, PLANS.open()) for p in row['synthetic_papers']}
    if len(allowed) != 1304 or expected != {r['text'] for r in allowed.values()}:
        raise ValueError('incomplete planting requests')
    for key, row in allowed.items():
        if text_hash(row['text']) != key or row['model_id'] != MODEL:
            raise ValueError('invalid planting request')
    binding = canonical({'requests': sha(REQUESTS), 'plans': sha(PLANS), 'encoder': model['model_key']})
    return allowed, binding, model['model_key']


def host_check():
    processes = subprocess.check_output(['/bin/ps', '-Aww', '-o', 'command='], text=True)
    markers = ('/e6/', 'e6/', 'overnight_supervisor.py', 'run_heldout', 'run_e6')
    if not processes.strip() or any(word in processes.lower() for word in markers):
        raise RuntimeError('E6 process present or process list unavailable')
    pressure = subprocess.check_output(['/usr/bin/memory_pressure', '-Q'], text=True)
    free = re.search(r'System-wide memory free percentage:\s*(\d+)%', pressure)
    # Use macOS's memory pressure reading on the 16 GiB host.
    if free is None or int(free[1]) < 25 or shutil.disk_usage(AREA).free < 2**30:
        raise RuntimeError('insufficient available memory or disk')


def run(encode_requested, limit):
    allowed, binding, model_key = inputs()
    reader = Sidecar(DATABASE, binding, allowed, model_key)
    try:
        missing = [h for h in allowed if reader.get_hash(h) is None]
    finally:
        reader.close()
    if not encode_requested or not missing:
        return {'complete': len(allowed)-len(missing), 'missing': len(missing)}
    host_check()
    OUTPUT.mkdir(exist_ok=True)
    with (OUTPUT / 'writer.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        reader = Sidecar(DATABASE, binding, allowed, model_key)
        try:
            pending = [h for h in missing if reader.get_hash(h) is None][:limit]
        finally:
            reader.close()
        if not pending:
            return {'new_vectors': 0}
        encode = cpu_factory(json.loads(INVENTORY.read_text()))
        parity = []
        original = Cache(CACHE)
        try:
            for control in json.loads(CONTROLS.read_text()):
                expected = original.get(control['text'])
                got = normalized(encode([control['text']])[0])
                if not np.allclose(got, expected, atol=1e-5, rtol=1e-4):
                    raise ValueError('cached control parity failed')
                parity.append({'text_sha256': control['text_sha256'],
                               'max_abs_diff': float(np.abs(got-expected).max())})
        finally:
            original.close()
        writer = Sidecar(DATABASE, binding, allowed, model_key, write=True,
                         parity={'passed': True, 'controls': parity})
        try:
            for offset in range(0, len(pending), 2):
                if offset % 16 == 0:
                    host_check()
                keys = pending[offset:offset+2]
                raw = encode([allowed[h]['text'] for h in keys])
                if raw.shape != (len(keys), 768):
                    raise ValueError('encoder alignment failed')
                writer.put_batch([(h, normalized(v)) for h, v in zip(keys, raw)])
        finally:
            writer.close()
        return {'new_vectors': len(pending)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--authorize-planting-inference', action='store_true')
    parser.add_argument('--limit', type=int, default=1304)
    args = parser.parse_args()
    if not 1 <= args.limit <= 1304:
        parser.error('limit must be 1 through 1304')
    print(json.dumps(run(args.authorize_planting_inference, args.limit)))
