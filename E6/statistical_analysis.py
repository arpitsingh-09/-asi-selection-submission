"""Offline, provisional analysis of existing E6 evaluations; never runs inference.

Callers declare comparisons, replicate count, seed and missing-cell policy.
Intervals are marginal percentile intervals, without multiplicity adjustment.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import random
from pathlib import Path
from statistics import fmean

from evaluation import ARMS, EvaluationError, _hash_json, paired_bootstrap_interval


def percentile_interval(draws, confidence_level):
    ordered = sorted(draws)
    def quantile(p):
        index = (len(ordered) - 1) * p
        lo = math.floor(index)
        hi = math.ceil(index)
        return ordered[lo] + (ordered[hi] - ordered[lo]) * (index - lo)
    return quantile((1 - confidence_level) / 2), quantile((1 + confidence_level) / 2)


def resample_ids(ids, size, replicate_index, seed):
    # Separate deterministic streams avoid dependence on comparison traversal order.
    key = hashlib.sha256(f'{seed}:{replicate_index}'.encode()).digest()
    rng = random.Random(int.from_bytes(key, 'big'))
    return [ids[rng.randrange(len(ids))] for _ in range(size)]


def _value_at(value, path):
    for key in path:
        if isinstance(value, dict) and 'status' in value and value['status'] not in (
            'succeeded', 'evaluated', 'scored'
        ):
            raise KeyError('nested metric did not succeed')
        value = value[key]
    return value


def evaluation_cells(sources, *, testbed, metric, value_path, stage=None, field=None):
    """Join native TRAIN summaries or literature evaluation records to arm cells.

    A metric path names an existing scalar; candidate/judge aggregation is never
    guessed. For same-question judgments the caller must supply a declared
    input-set summary, rather than treating individual questions as replications.
    """
    if testbed not in ('data', 'literature') or not metric or not value_path:
        raise EvaluationError('testbed, metric and explicit scalar value_path required')
    cells = []
    seen = set()
    for source in sources:
        unit = source.get('generation_input_set_id') if testbed == 'data' else source.get('input_set_id')
        if not isinstance(unit, str) or not unit.strip() or unit in seen:
            raise EvaluationError('unique independent input-set IDs required')
        seen.add(unit)
        if testbed == 'data' and ':TRAIN-SET:' not in unit:
            raise EvaluationError('data analysis requires TRAIN generation evidence sets, never TEST rows')
        hash_key = 'result_sha256' if testbed == 'data' else 'bundle_sha256'
        if hash_key in source and source[hash_key] != _hash_json({k: v for k, v in source.items() if k != hash_key}):
            raise EvaluationError('evaluation source hash mismatch')
        for arm in ARMS:
            if testbed == 'data':
                record = source.get('evaluations', {}).get(arm)
            else:
                matches = [r for r in source.get('records', [])
                           if r.get('provenance', {}).get('arm') == arm
                           and r.get('stage') == stage
                           and (field is None or r.get('evaluation_input', {}).get('field') == field)]
                if len(matches) > 1:
                    raise EvaluationError('ambiguous metric records; declare a unique stage/field')
                record = matches[0] if matches else None
                if record and record.get('input_set_id') != unit:
                    raise EvaluationError('literature record belongs to another input set')
            status, reason, value = 'missing', 'metric record absent', None
            if record is not None:
                status = record.get('status', 'missing')
                reason = record.get('error') or status
                if status in ('succeeded', 'evaluated'):
                    try:
                        value = _value_at(record, value_path)
                    except (KeyError, TypeError, IndexError):
                        reason = 'metric value absent'
                    if type(value) in (int, float) and math.isfinite(value):
                        status, reason = 'succeeded', None
                    else:
                        value, status = None, 'missing'
                else:
                    value = None
            cells.append(dict(input_set_id=unit, arm=arm, metric=metric,
                              value=value, status=status, reason=reason,
                              source_sha256=_hash_json(source), record=record))
    return cells


def analyze_evaluations(sources, *, testbed, metric, value_path, comparisons,
                        replicates, seed, missing_policy, stage=None, field=None):
    """Analyze arm means and declared paired mean differences at fixed 95%.

    ``block`` withholds any estimate with unavailable cells. Explicit
    ``complete_pairs`` uses available units per arm/contrast and reports every
    exclusion. It does not impute, retry or replace any observation.
    """
    if missing_policy not in ('block', 'complete_pairs'):
        raise EvaluationError('explicit missing_policy must be block or complete_pairs')
    if type(replicates) is not int or replicates < 1 or type(seed) is not int:
        raise EvaluationError('positive replicates and integer seed required')
    pairs = [tuple(pair) for pair in comparisons]
    if not pairs or len(set(pairs)) != len(pairs) or any(
        len(p) != 2 or p[0] == p[1] or any(a not in ARMS for a in p) for p in pairs
    ):
        raise EvaluationError('unique declared comparisons between known distinct arms required')
    sources = list(sources)
    cells = evaluation_cells(sources, testbed=testbed, metric=metric,
                             value_path=value_path, stage=stage, field=field)
    ids = sorted({c['input_set_id'] for c in cells})
    if not ids:
        raise EvaluationError('nonempty input-set cohort required')
    lookup = {(c['input_set_id'], c['arm']): c for c in cells}
    def estimate(arms):
        excluded = [dict(input_set_id=i, unavailable=[lookup[i, a] for a in arms
                    if lookup[i, a]['status'] != 'succeeded']) for i in ids
                    if any(lookup[i, a]['status'] != 'succeeded' for a in arms)]
        usable = [i for i in ids if all(lookup[i, a]['status'] == 'succeeded' for a in arms)]
        result = dict(exclusions=excluded, included_input_set_ids=usable,
                      expected_count=len(ids), included_count=len(usable),
                      excluded_count=len(excluded),
                      denominator=len(usable),
                      unavailable_fraction=len(excluded) / len(ids))
        if not usable or (excluded and missing_policy == 'block'):
            return dict(result, status='blocked_missing_observations', point_estimate=None, interval=None)
        values = {i: lookup[i, arms[0]]['value'] - (lookup[i, arms[1]]['value'] if len(arms) == 2 else 0)
                  for i in usable}
        interval = paired_bootstrap_interval(values, replicates=replicates,
            confidence_level=0.95, seed=seed, statistic=fmean,
            interval_estimator=percentile_interval, resample_input_set_ids=resample_ids,
            rng_name='python.random.Random/MT19937; sha256(seed:replicate) streams')
        return dict(result, status='scored', **{'bootstrap': interval,
                    'point_estimate': interval['point_estimate'], 'interval': interval['interval']})
    result = dict(schema_version='e6-statistical-analysis-v1', schema_status='provisional_unapproved',
        testbed=testbed, metric=metric, confidence_level=0.95,
        independent_unit='TRAIN generation evidence set' if testbed == 'data' else 'literature target paper',
        configuration=dict(value_path=list(value_path), stage=stage, field=field,
                           comparisons=[list(p) for p in pairs], replicates=replicates,
                           seed=seed, missing_policy=missing_policy,
                           statistic='arithmetic_mean', interval_method='linear_percentile',
                           multiplicity='unadjusted marginal intervals'),
        provenance=dict(source_sha256=[_hash_json(s) for s in sources],
                        sources=sources, python_version=platform.python_version(),
                        implementation_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                        evaluation_implementation_sha256=hashlib.sha256(Path(__file__).with_name('evaluation.py').read_bytes()).hexdigest()),
        cells=cells, arm_estimates={a: estimate((a,)) for a in ARMS},
        comparisons={f'{a}-minus-{b}': estimate((a, b)) for a, b in pairs})
    result['output_sha256'] = _hash_json(result)
    return result


def write_analysis_exclusive(path, result):
    if result.get('output_sha256') != _hash_json({k: v for k, v in result.items() if k != 'output_sha256'}):
        raise EvaluationError('analysis output hash mismatch')
    with Path(path).open('x', encoding='utf-8') as handle:
        json.dump(result, handle, sort_keys=True, ensure_ascii=False, allow_nan=False, indent=2)
        handle.write('\n')


def analyze_configured_evaluations(sources, *, config, evaluation_config,
                                   testbed, metric, value_path, stage=None, field=None):
    """Use active descriptive settings only; never activate proposed parameters.

    This offline adapter does not authorize inference or confer preregistration.
    Numeric bootstrap parameters must be explicitly set before analysis.
    """
    settings = evaluation_config['paired_bootstrap']
    analysis = config['statistical_analysis']
    if (settings.get('statistic') != 'arithmetic_mean'
            or settings.get('interval_method') != 'linear_percentile'
            or settings.get('confidence_level') != .95
            or settings.get('multiplicity_method') != 'unadjusted_marginal_intervals'
            or analysis.get('multiplicity_method') != 'unadjusted_marginal_intervals'
            or settings.get('missing_policy') != 'complete_pairs'
            or analysis.get('missing_data_rule') != 'complete_pairs'
            or settings.get('comparisons') != analysis.get('comparisons')
            or settings.get('random_generator_and_version') !=
               'python.random.Random/MT19937; sha256(seed:replicate) streams'):
        raise EvaluationError('active descriptive bootstrap configuration incomplete or inconsistent')
    return analyze_evaluations(sources, testbed=testbed, metric=metric,
        value_path=value_path, comparisons=settings['comparisons'],
        replicates=settings.get('replicates'), seed=settings.get('seed'),
        missing_policy='complete_pairs', stage=stage, field=field)
