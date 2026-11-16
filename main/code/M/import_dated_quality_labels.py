"""Import exact, dated quality observations from independently checked source rows.

This importer validates provenance declarations and exact source bytes. It does not
discover, infer, or create labels; the caller must provide already verified records.
"""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path

from .evidence import iter_bound, assertion, verify_assertion

FACTORS = {'peer_review', 'later_community_use'}


def _utc(value):
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() == timezone.utc.utcoffset(parsed)


def _validate_source(row):
    if row.get('schema') != 'M-dated-quality-label-source-v1':
        raise ValueError('unsupported dated quality-label source schema')
    for key in ('label_id', 'paper_id', 'definition', 'source_url', 'source_revision_id',
                'source_locator', 'source_quote', 'public_date_basis', 'verifier_code'):
        if not isinstance(row.get(key), str) or not row[key].strip():
            raise ValueError('missing required source field: ' + key)
    if row.get('factor') not in FACTORS:
        raise ValueError('unsupported quality factor')
    value = row.get('value')
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('quality value must be a finite number')
    if not _utc(row.get('observed_at')) or not _utc(row.get('public_at')) or not _utc(row.get('verified_at')):
        raise ValueError('observed_at, public_at and verified_at must be timezone-aware UTC timestamps')
    if row['observed_at'] != row['public_at']:
        raise ValueError('exact value public date must equal observed_at; no inferred dates allowed')
    if row.get('verification_status') != 'VERIFIED':
        raise ValueError('source row must be independently marked VERIFIED')


def verify_dated_outcome(outcome):
    if outcome.get('source_type') != 'M_DATED_QUALITY_LABEL':
        raise ValueError('not an imported dated quality label')
    verify_assertion(outcome['source_record_evidence'])
    source = outcome['source_record_evidence']['value']
    _validate_source(source)
    for key in ('outcome_id', 'paper_id', 'factor', 'value', 'definition', 'observed_at',
                'usable_for_fitting', 'source_url', 'source_revision_id', 'source_locator',
                'source_quote', 'verified_at', 'verifier_code'):
        if key == 'usable_for_fitting':
            continue
        source_key = {'outcome_id': 'label_id'}.get(key, key)
        if outcome.get(key) != source.get(source_key):
            raise ValueError('derived quality label disagrees with source row: ' + key)
    if outcome.get('usable_for_fitting') is not True:
        raise ValueError('source-verified label is not marked usable')
    return True


def import_labels(source_path, out_path):
    out_path = Path(out_path)
    if out_path.exists():
        raise FileExistsError(out_path)
    rows = []
    for row, binding in iter_bound(source_path):
        _validate_source(row)
        evidence = assertion(binding, [], row)
        rows.append({'source_type': 'M_DATED_QUALITY_LABEL', 'outcome_id': row['label_id'],
            'paper_id': row['paper_id'], 'factor': row['factor'], 'value': row['value'],
            'definition': row['definition'], 'observed_at': row['observed_at'],
            'observed_at_status': 'independently verified public availability of exact value',
            'record_version_timestamp': row['public_at'], 'usable_for_fitting': True,
            'source_url': row['source_url'], 'source_revision_id': row['source_revision_id'],
            'source_locator': row['source_locator'], 'source_quote': row['source_quote'],
            'verified_at': row['verified_at'], 'verifier_code': row['verifier_code'],
            'source_record_evidence': evidence})
    with out_path.open('x') as f:
        for item in rows:
            verify_dated_outcome(item)
            f.write(json.dumps(item, sort_keys=True, allow_nan=False) + '\n')
    return len(rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    print(import_labels(args.source, args.out))
