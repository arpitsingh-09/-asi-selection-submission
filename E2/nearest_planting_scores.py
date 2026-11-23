"""Score the four frozen nearest-planting conditions against their unmodified pools."""
import argparse
import json
import os
from pathlib import Path
import tempfile

from nearest_planting_vectors import AREA, CACHE, DATABASE, PLANS, ROOT, inputs
from cached_extensions import Cache, calculate, text
from claim_sidecar import Sidecar, sha, text_hash
import numpy as np


def score(output, authorized_database_hash):
    if output.exists():
        raise FileExistsError(output)
    allowed, binding, model_key = inputs()
    if not DATABASE.is_file() or sha(DATABASE) != authorized_database_hash:
        raise ValueError('supply the SHA-256 of the finished planting database')
    raw_path = ROOT / 'data/raw_papers.jsonl'
    claims_path = ROOT / 'data/claims_v8_selected.jsonl'
    if sha(raw_path) != '98036e1d99139a7fa4938362ab45f97fc12f21a91182c0ce5d22ee5be7d0c662' or sha(claims_path) != '2266fe8e086ebd1ca2bdea1db0e4eccd241a2fc8f1d1282b9e9c5fcb37ec723d':
        raise ValueError('paper or claim source changed')
    raw = {r['paper_id']: r for r in map(json.loads, raw_path.read_text().splitlines())}
    claims = {r['paper_id']: r['claims'] for r in map(json.loads, claims_path.read_text().splitlines())}
    database = Sidecar(DATABASE, binding, allowed, model_key)
    cache = Cache(CACHE)
    try:
        vectors = {key: database.get_hash(key) for key in allowed}
        if any(v is None for v in vectors.values()):
            raise ValueError('all 1304 planting vectors required')
        results = {}
        for plan in map(json.loads, PLANS.read_text().splitlines()):
            focal = plan['paper_id']
            idea = cache.get(text(raw[focal]))
            cv = np.stack([cache.get(c['claim'].strip()) for c in claims[focal]])
            reverse = {v: k for k, v in plan['replacement_map'].items()}
            ids = plan['pool_ids']
            original = [reverse.get(i, i) for i in ids]
            if focal not in results:
                baseline = calculate(idea, cv, np.stack([cache.get(text(raw[i])) for i in original]))
                results[focal] = {'paper_id': focal, 'pool': plan['pool'], 'original_ids': original,
                                  'baseline': baseline, 'conditions': {}}
            row = results[focal]
            if original != row['original_ids'] or plan['percent'] in row['conditions']:
                raise ValueError('unpaired or repeated condition')
            modified = {r['paper_id']: vectors[text_hash(text(r))] for r in plan['synthetic_papers']}
            pool = np.stack([modified[i] if i in modified else cache.get(text(raw[i])) for i in ids])
            row['conditions'][plan['percent']] = calculate(idea, cv, pool)
        if len(results) != 241 or any(set(r['conditions']) != {25,50,75,100} for r in results.values()):
            raise ValueError('incomplete set of contrasts')
    finally:
        cache.close()
        database.close()
    if sha(DATABASE) != authorized_database_hash:
        raise ValueError('planting database changed during evaluation')
    with tempfile.NamedTemporaryFile(mode='w', dir=output.parent, delete=False) as f:
        tmp = Path(f.name)
        try:
            for row in results.values():
                del row['original_ids']
                f.write(json.dumps(dict(row, planting_database_sha256=authorized_database_hash),
                                   allow_nan=False) + '\n')
            f.flush()
            os.fsync(f.fileno())
            os.link(tmp, output)
        finally:
            tmp.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--authorize-scoring-for-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    score(args.output, args.authorize_scoring_for_sha256)
