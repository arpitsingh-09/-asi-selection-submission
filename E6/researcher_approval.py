"""Explicit E6 decisions and artifact sign-off; read-only validation, no approval defaults."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = ROOT / 'E6/RESEARCHER_APPROVAL.json'
SCHEMA = 'e6-researcher-approval-v1'
CONFIGURATION_PATHS = (
    'E6/config.json', 'E6/protocol.md', 'E6/PREREG.md',
    'E6/configured_evaluators.py',
    'E6/prior_question_corpus.py',
    'E6/prior_question_expansion.py',
    'E6/data/prior_question_corpus_v4.json',
    'E6/data/prior_question_expansion_v1/systematic_frame.json',
    'E6/data/prior_question_expansion_v1/source_question_reviews.json',
    'E6/data/prior_question_expansion_v1/source_index.json',
    'prompts/e6/17_prior_question_verbatim.txt',
    'E6/data/prior_question_corpus_v3.json',
    'E6/data/prior_question_sources_v1/index_v2.json',
    'E6/question_pipeline_config.json', 'E6/evaluation_config.json',
    'E6/literature_testbed_config.json',
    'prompts/e6/08_same_question.txt',
    'prompts/e6/09_target_extraction.txt',
    'prompts/e6/10_question_type.txt',
    'prompts/e6/15_reconstruction_similarity.txt',
    'prompts/e6/16_hypothesis_distinctness.txt',
    'E6/LITERATURE_REVIEW_GUIDE.md',
    'E6/LITERATURE_REVIEW_RECORD_SCHEMA.json',
    'E6/data/literature_selected_manifest_v1.json',
    'E6/data/literature_selection_approval_v1.json',
    'E6/data/literature_freeze_plan_v1.json',
    'E6/data/literature_sample_proposal_v1.json',
    'E6/data/hypobench_inductive_proposal_v1.json',
    'E6/data/literature_reference_selection_proposal_v1.json',
)

# A recommendation can be accepted only after its remaining operational details
# have explicit values. These are technical completeness checks, not scientific review.
# Hash plumbing, existing identifiers and output compatibility are implementation
# checks covered by final artifact sign-off, not three extra scientific choices.
RESEARCHER_DECISION_IDS = frozenset(set(range(1, 27)) - {6, 7, 17})
DETAILS = {
    1: ('directional_hypotheses', 'prospective_record_policy', 'governing_protocol'),
    2: (), 3: (), 4: ('task_text_by_testbed', 'source_field_allowlist'),
    5: ('sample_proposal_sha256',), 6: ('per_testbed_freeze_plan',), 7: (), 8: (),
    9: (), 10: ('run_order_algorithm',),
    11: ('transport_retry_policy', 'timeout_policy'),
    12: ('failed_cell_metric_values_by_outcome',), 13: (),
    14: ('task_leakage_audit_policy',), 15: ('assignment_cohorts',), 16: (),
    17: ('output_schema_contract',), 18: ('primary_outcomes_and_contrast_family',),
    19: ('rubric_prompt_and_hash', 'missing_annotation_policy'),
    20: ('corpus_path_and_hash', 'corpus_scope', 'binary_matcher_and_policy'),
    21: ('distinctness_prompt_and_hash',), 22: ('classification_prompt_and_hash',),
    23: (), 24: ('extraction_model_configuration', 'review_policy'),
    25: ('pre_outcome_error_review_plan',),
    26: ('bootstrap_statistic', 'rng_and_version', 'missingness_policy',
         'dependency_freeze_timing'),
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def file_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def concrete(value):
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value.strip().lower() not in {
            'pending', 'todo', 'tbd', 'unresolved', 'placeholder'}
    if isinstance(value, dict):
        return bool(value) and all(concrete(v) for v in value.values())
    if isinstance(value, list):
        return all(concrete(v) for v in value)
    return type(value) in (bool, int, float)


def nonempty_text(value):
    return isinstance(value, str) and concrete(value)


def valid_utc(value):
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return (parsed.utcoffset() is not None and parsed.utcoffset().total_seconds() == 0
                and parsed <= datetime.now(timezone.utc))
    except (AttributeError, TypeError, ValueError):
        return False


def decision_payload(row):
    return {key: row.get(key) for key in (
        'id', 'title', 'proposed_value', 'evidence', 'choice',
        'approved_value', 'resolved_details')}


def decision_errors(row, root=ROOT):
    errors = []
    prefix = f"decision {row.get('id')}"
    if row.get('status') != 'approved':
        return [prefix + ': explicit researcher approval required']
    if row.get('choice') not in ('accept_proposal', 'replacement'):
        errors.append(prefix + ': choice must be accept_proposal or replacement')
    if not concrete(row.get('approved_value')):
        errors.append(prefix + ': approved_value required')
    if row.get('choice') == 'accept_proposal' and row.get('approved_value') != row.get('proposed_value'):
        errors.append(prefix + ': accepted value differs from proposal')
    details = row.get('resolved_details')
    if not isinstance(details, dict):
        details = {}
    for key in DETAILS.get(row.get('id'), ()):
        value = details.get(key)
        if key == 'failed_cell_metric_values_by_outcome' and isinstance(value, dict):
            # A deliberate JSON null score is a policy value, not an unresolved
            # decision. All other missingness/denominator details remain required.
            value = dict(value)
            if ('missing_score' in value and value['missing_score'] is None
                    and value.get('imputation') == 'none'):
                value['missing_score'] = 'explicit_json_null'
        if not concrete(value):
            errors.append(prefix + ': unresolved detail ' + key)
    if not nonempty_text(row.get('approved_by')) or not valid_utc(row.get('approved_at_utc')):
        errors.append(prefix + ': researcher identity and valid UTC approval timestamp required')
    if row.get('approved_payload_sha256') != digest(decision_payload(row)):
        errors.append(prefix + ': approval does not bind current decision payload')
    evidence = row.get('evidence')
    if not isinstance(evidence, list) or not evidence:
        errors.append(prefix + ': supporting evidence required')
    else:
        for item in evidence:
            try:
                path = safe_path(root, item['path'])
                if file_digest(path) != item['file_sha256']:
                    errors.append(prefix + ': evidence changed: ' + item['path'])
            except (KeyError, TypeError, ValueError, OSError):
                errors.append(prefix + ': missing/invalid evidence')
    return errors


def safe_path(root, relative):
    if not isinstance(relative, str) or Path(relative).is_absolute():
        raise ValueError('artifact path must be repository-relative')
    path = (Path(root) / relative).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise ValueError('artifact path escapes repository')
    return path


def validate_approval_record(record, *, root=ROOT, required_ids=None, finalization=False):
    if not isinstance(record, dict) or record.get('schema_version') != SCHEMA:
        return ['researcher approval: unsupported or missing record']
    rows = record.get('decisions')
    if (not isinstance(rows, list) or len(rows) != 26
            or any(not isinstance(row, dict) or type(row.get('id')) is not int for row in rows)
            or sorted(row['id'] for row in rows) != list(range(1, 27))):
        return ['researcher approval: require exactly decisions 1 through 26, without duplicates']
    requested = set(range(1, 27)) if required_ids is None else set(required_ids)
    required = requested & RESEARCHER_DECISION_IDS
    if not requested <= set(range(1, 27)):
        return ['researcher approval: invalid required decision IDs']
    errors = []
    for row in rows:
        if row['id'] in required:
            errors.extend(decision_errors(row, root))
    if finalization:
        signoff = record.get('configuration_signoff')
        if not isinstance(signoff, dict):
            errors.append('researcher approval: configuration sign-off required')
        else:
            artifacts = signoff.get('artifacts')
            if not isinstance(artifacts, dict) or not set(CONFIGURATION_PATHS) <= set(artifacts):
                errors.append('researcher approval: configuration artifact hashes required')
            else:
                for relative, sha in artifacts.items():
                    try:
                        if file_digest(safe_path(root, relative)) != sha:
                            errors.append('researcher approval: signed artifact changed: ' + relative)
                    except (ValueError, OSError):
                        errors.append('researcher approval: signed artifact missing/invalid: ' + str(relative))
            if (not nonempty_text(signoff.get('approved_by'))
                    or not valid_utc(signoff.get('approved_at_utc'))
                    or signoff.get('approved_decisions_sha256') != digest(rows)):
                errors.append('researcher approval: configuration sign-off must bind all decisions and reviewer')
    return errors


def configuration_artifact_hashes(*, root=ROOT, extra_paths=()):
    """Compute final sign-off hashes without approving, finalizing or writing.

    Run after final edits and approved source freeze. Missing required artifacts
    fail closed. Include every additional source/review/runtime artifact used.
    """
    paths = tuple(dict.fromkeys((*CONFIGURATION_PATHS, *extra_paths)))
    return {relative: file_digest(safe_path(root, relative)) for relative in paths}


def load_approval_errors(root=ROOT, *, finalization=True):
    try:
        record = json.loads((Path(root) / 'E6/RESEARCHER_APPROVAL.json').read_text())
    except (OSError, ValueError):
        return ['researcher approval: cannot read E6/RESEARCHER_APPROVAL.json']
    return validate_approval_record(record, root=root, finalization=finalization)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', type=Path, default=RECORD_PATH)
    parser.add_argument('--finalization', action='store_true', help='also check configuration sign-off')
    args = parser.parse_args()
    try:
        errors = validate_approval_record(json.loads(args.record.read_text()), finalization=args.finalization)
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    print(json.dumps({'status': 'BLOCKED' if errors else 'APPROVALS_COMPLETE', 'errors': errors}, indent=2))
    return 2 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
