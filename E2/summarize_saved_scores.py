#!/usr/bin/env python3
"""Read-only summaries of E2 saved scores; never imports novelty or scores."""
import csv, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1] if Path(__file__).parent.name == 'E2' else Path('/Users/arpit/asi-selection')
DATA = ROOT / 'E2' / 'data'
REPORT = ROOT / 'E2' / 'analysis' / 'saved_results_report.json'
SEED = 20261113
REPS = 10000
METHODS = ('Y', 'N', 'yours', 'density')
TOL = 1e-8

def load_jsonl(path):
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    baseline_report = json.loads(REPORT.read_text())
    files = ('scoring_results.jsonl', 'scoring_results.matmul_pilot.jsonl')
    hashes = {name: sha(DATA / name) for name in files}
    for name, expected in baseline_report['scoring_sha256'].items():
        if hashes[name] != expected:
            raise SystemExit(f'SHA256 mismatch: {name}')
    plans = load_jsonl(DATA / 'manipulation_plan.jsonl')
    results = load_jsonl(DATA / 'scoring_results.jsonl')
    if len(plans) != 2400 or len(results) != 2400:
        raise SystemExit('Expected exactly 2,400 plan and saved score records')
    plan_by_id = {x['case_id']: x for x in plans}
    result_by_id = {x['case_id']: x for x in results}
    if len(plan_by_id) != 2400 or len(result_by_id) != 2400 or set(plan_by_id) != set(result_by_id):
        raise SystemExit('Duplicate or unmatched case IDs')
    if any(x['status'] != 'ok' for x in results):
        raise SystemExit('Unexpected non-ok saved score')
    groups = defaultdict(dict)
    for row in plans:
        groups[(row['pool'], row['focal_paper_id'])][row['manipulation']] = row['case_id']
    if len(groups) != 300 or any(len(x) != 8 for x in groups.values()):
        raise SystemExit('Expected 300 focal groups with 8 conditions each')
    pool_counts = Counter(pool for pool, _ in groups)
    if set(pool_counts.values()) != {100}:
        raise SystemExit('Expected exactly 100 focal papers per fixed pool')
    for rid, row in result_by_id.items():
        if set(row['scores']) != set(METHODS):
            raise SystemExit(f'Unexpected methods in {rid}')
        if not all(np.isfinite(float(v)) for v in row['scores'].values()):
            raise SystemExit(f'Non-finite saved score in {rid}')

    contrasts = [
        ('exact_copy', 'baseline', 'decrease'),
        ('coverage_25', 'baseline', 'nonincrease'),
        ('coverage_50', 'baseline', 'nonincrease'),
        ('coverage_75', 'baseline', 'nonincrease'),
        ('coverage_100', 'baseline', 'nonincrease'),
        ('coverage_50', 'coverage_25', 'nonincrease'),
        ('coverage_75', 'coverage_50', 'nonincrease'),
        ('coverage_100', 'coverage_75', 'nonincrease'),
        ('concentrated', 'distributed', 'method_specific'),
    ]
    rng = np.random.default_rng(SEED)
    def summarize(unit_groups, left, right, rule, method):
        delta = np.asarray([
            result_by_id[g[left]]['scores'][method] - result_by_id[g[right]]['scores'][method]
            for g in unit_groups
        ], dtype=float)
        if rule == 'method_specific':
            actual = {'Y': delta < -TOL, 'N': delta > TOL,
                      'yours': delta < -TOL, 'density': delta < -TOL}[method]
            label = {'Y': 'lower', 'N': 'higher (T2-derived)',
                     'yours': 'lower (registered prediction)',
                     'density': 'lower (descriptive; direction uncertain)'}[method]
        elif rule == 'decrease':
            actual, label = delta < -TOL, 'lower'
        else:
            actual, label = delta <= TOL, 'non-increase'
        indices = rng.integers(0, len(delta), size=(REPS, len(delta)))
        rates = actual.astype(float)
        rate_ci = np.percentile(rates[indices].mean(axis=1), (2.5, 97.5))
        delta_ci = np.percentile(delta[indices].mean(axis=1), (2.5, 97.5))
        return {
            'criterion': label, 'n': len(delta), 'passes': int(actual.sum()),
            'rate': float(actual.mean()), 'rate_ci95': rate_ci.tolist(),
            'mean_left': float(np.mean([result_by_id[g[left]]['scores'][method] for g in unit_groups])),
            'mean_right': float(np.mean([result_by_id[g[right]]['scores'][method] for g in unit_groups])),
            'mean_delta': float(delta.mean()), 'mean_delta_ci95': delta_ci.tolist(),
            'less_equal_greater': [int((delta < -TOL).sum()), int((np.abs(delta) <= TOL).sum()), int((delta > TOL).sum())]
        }
    out = {
        'scope': 'saved-result descriptive analysis; no new scoring',
        'source_paths': ['E2/data/manipulation_plan.jsonl', 'E2/data/scoring_results.jsonl', 'E2/analysis/saved_results_report.json'],
        'sha256': hashes, 'records': len(results), 'score_values': len(results) * 4,
        'status_counts': dict(Counter(x['status'] for x in results)),
        'condition_counts': dict(Counter(x['manipulation'] for x in plans)),
        'pools': dict(pool_counts), 'focal_groups': len(groups), 'conditions_per_focal': 8,
        'bootstrap': {'unit': 'paired focal paper, resampled within each fixed pool', 'replicates': REPS, 'seed': SEED, 'interval': 'percentile 95%', 'tolerance': TOL},
        'contrast_definitions': [{'condition': a, 'reference': b, 'rule': c} for a,b,c in contrasts],
        'overall': {}, 'per_pool': {},
    }
    all_groups = list(groups.values())
    def add_results(dest, sample):
        for left, right, rule in contrasts:
            key = f'{left}_vs_{right}'
            dest[key] = {m: summarize(sample, left, right, rule, m) for m in METHODS}
    add_results(out['overall'], all_groups)
    for pool in sorted(pool_counts):
        sample = [g for (p, _), g in groups.items() if p == pool]
        out['per_pool'][pool] = {}
        add_results(out['per_pool'][pool], sample)
    json.dump(out, __import__('sys').stdout, indent=2, allow_nan=False)
    print()

if __name__ == '__main__':
    main()
