"""Validate the paper register and explicit bindings to structured source records."""
import csv
import hashlib
import json
import re
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IDS = {f'h{i:03}' for i in range(1, 63)} - {'h028'}
FIELDS = 'question_id paper_id paper_version paper_sha256 paper_availability_date original_input_manifest_path availability_evidence_path evidence_status provenance_verification_status'.split()
STATUS = {'MISSING', 'PARTIAL', 'UNVERIFIED', 'VERIFIED'}


def source_matches(reference, binding):
    path = ROOT / reference
    if not reference or not path.is_file() or path.resolve() == (ROOT / 'E1_PAPER_INPUTS.csv').resolve():
        return False
    if path.suffix.lower() == '.csv':
        with path.open(newline='', encoding='utf-8') as stream:
            records = list(csv.DictReader(stream))
    elif path.suffix.lower() == '.jsonl':
        records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    elif path.suffix.lower() == '.json':
        data = json.loads(path.read_text())
        records = data if isinstance(data, list) else [data]
    else:
        return False
    return any(isinstance(row, dict) and all(row.get(k) == v for k, v in binding.items()) for row in records)


def validate():
    seen = set()
    verified = set()
    with (ROOT / 'E1_PAPER_INPUTS.csv').open(newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != FIELDS:
            raise ValueError('Unexpected register columns')
        for row in reader:
            key = tuple(row[k] for k in FIELDS[:3])
            if key in seen or key[0] not in IDS:
                raise ValueError(f'Duplicate or unknown record {key}')
            seen.add(key)
            digest = row['paper_sha256']
            if digest and not re.fullmatch('[a-fA-F0-9]{64}', digest):
                raise ValueError(f'Invalid SHA-256 for {key}')
            overall, provenance = (row[k] for k in FIELDS[-2:])
            if {overall, provenance} - STATUS:
                raise ValueError(f'Invalid status for {key}')
            binding = {k: row[k] for k in FIELDS[:4]}
            if provenance == 'VERIFIED' or overall == 'VERIFIED':
                if provenance != 'VERIFIED' or not all(binding.values()) or not source_matches(row['original_input_manifest_path'], binding):
                    raise ValueError(f'Missing original input binding for {key}')
                verified.add(key[0])
            if overall == 'VERIFIED':
                stamp = row['paper_availability_date']
                datetime.fromisoformat(stamp.replace('Z', '+00:00'))
                if not source_matches(row['availability_evidence_path'], dict(paper_id=key[1], paper_version=key[2], paper_sha256=digest, paper_availability_date=stamp)):
                    raise ValueError(f'Missing dated availability evidence for {key}')
    if {key[0] for key in seen} != IDS:
        raise ValueError('Incomplete question coverage')
    print(f'PASS: {len(seen)} rows, 61 questions, {len(verified)} questions with verified provenance')


if __name__ == '__main__':
    validate()
