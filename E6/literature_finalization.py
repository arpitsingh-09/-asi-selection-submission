"""Offline preparation, approved deterministic freeze, and source-bound review validation.

No network or model client is constructed here. Extraction calls are available
only through the existing explicit caller-injected interface.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

from researcher_approval import ROOT, digest, file_digest, concrete, nonempty_text, valid_utc, validate_approval_record
from prepare_literature_sample_proposal import (
    verify_sample_proposal, build_literature_extraction_manifest,
    build_proposed_manual_review_worklist,
)
from prepare_literature_testbed import write_manifest_exclusive
from evaluation import TARGET_EXTRACTION_PROMPT

CANDIDATE = ROOT / 'E6/data/literature_citation_verified_manifest_v1.json'
PROPOSAL = ROOT / 'E6/data/literature_sample_proposal_v1.json'
PLAN = ROOT / 'E6/data/literature_freeze_plan_v1.json'
SELECTED_PATH = 'E6/data/literature_selected_manifest_v1.json'
SOURCE_CONTENT_CHECK_FIELDS = ('problem_extraction_accurate', 'method_extraction_accurate', 'result_extraction_accurate')
CHECK_FIELDS = (
    'research_question_extraction_accurate', 'main_hypothesis_extraction_accurate',
    'research_question_explicitness_accurate', 'main_hypothesis_explicitness_accurate',
)


def seal(value, key='manifest_sha256'):
    return dict(copy.deepcopy(value), **{key: digest(value)})


def verify_seal(value, key='manifest_sha256'):
    if not isinstance(value, dict) or value.get(key) != digest({k: v for k, v in value.items() if k != key}):
        raise ValueError('artifact hash mismatch: ' + key)


def extraction_source(row):
    target = row['target']
    field = 'full_text' if isinstance(target.get('full_text'), str) and target['full_text'].strip() else 'abstract'
    text = target.get(field)
    if not isinstance(text, str) or not text.strip():
        raise ValueError('missing extraction source: ' + row['input_set_id'])
    return field, text


def build_freeze_plan(candidate, proposal):
    rows = verify_sample_proposal(candidate, proposal)
    template = TARGET_EXTRACTION_PROMPT.read_text()
    jobs = []
    for row in rows:
        field, text = extraction_source(row)
        jobs.append({
            'input_set_id': row['input_set_id'], 'candidate_record_sha256': digest(row),
            'target_source_field': field,
            'target_source_text_sha256': hashlib.sha256(text.encode()).hexdigest(),
            'rendered_prompt_sha256': hashlib.sha256(template.replace('{{TARGET_PAPER_TEXT}}', text).encode()).hexdigest(),
            'execution_status': 'not_started',
        })
    return seal({
        'schema_version': 'e6-literature-freeze-plan-v1', 'status': 'pending_researcher_approval',
        'sample_selected': False, 'sample_frozen': False,
        'candidate_manifest_sha256': candidate['manifest_sha256'],
        'sample_proposal_sha256': proposal['proposal_sha256'],
        'selected_manifest_path_after_approval': SELECTED_PATH,
        'proposed_input_set_ids': proposal['proposed_input_set_ids'],
        'proposed_manual_review_input_set_ids': proposal['proposed_manual_review_input_set_ids'],
        'selected_candidate_record_hashes': [digest(row) for row in rows],
        'extraction_prompt_path': 'prompts/e6/09_target_extraction.txt',
        'extraction_prompt_file_sha256': file_digest(TARGET_EXTRACTION_PROMPT),
        'extraction_jobs': jobs, 'extractions_completed': 0, 'human_reviews_completed': 0,
    })


def require_approved_sample(record, proposal, root=ROOT):
    errors = validate_approval_record(record, root=root, required_ids=(2, 5, 6, 7, 24))
    if errors:
        raise ValueError('; '.join(errors))
    by_id = {row['id']: row for row in record['decisions']}
    # This implementation supports the documented proposal. Replacements must
    # get an implementation rather than silently reusing the original sampler.
    if any(by_id[number]['choice'] != 'accept_proposal' for number in (2, 5)):
        raise ValueError('replacement scope/sampling/ID policy requires an adapted freeze implementation')
    selection = by_id[5]
    if selection['resolved_details']['sample_proposal_sha256'] != proposal['proposal_sha256']:
        raise ValueError('approved sample proposal hash does not match')


def build_frozen_literature_manifest(candidate, proposal, plan, approval, *, root=ROOT):
    """Future explicit freeze operation. Not called by preparation or validation."""
    require_approved_sample(approval, proposal, root)
    expected = build_freeze_plan(candidate, proposal)
    if plan != expected:
        raise ValueError('freeze plan differs from current sources, sample or prompt')
    rows = verify_sample_proposal(candidate, proposal)
    return seal({
        'schema_version': 'e6-literature-selected-manifest-v1',
        'input_sets_selected': True, 'input_sets_frozen': True,
        'candidate_manifest_sha256': candidate['manifest_sha256'],
        'sample_proposal_sha256': proposal['proposal_sha256'],
        'freeze_plan_sha256': plan['manifest_sha256'],
        'approval_record_sha256': digest(approval),
        'selected_input_set_ids': proposal['proposed_input_set_ids'],
        'manual_review_input_set_ids': proposal['proposed_manual_review_input_set_ids'],
        'input_sets': rows,
        'target_annotations_validated': False,
        'note': 'Frozen source selection only; no generation or scoring authorization.',
    })


def validate_extracted_candidates(candidate, proposal, extracted, model_configuration):
    """Bind all 100 real extraction records to unchanged sources and exact prompts."""
    originals = verify_sample_proposal(candidate, proposal)
    if not isinstance(extracted, list) or len(extracted) != len(originals):
        raise ValueError('extractions must cover the exact proposed sample')
    by_id = {row.get('input_set_id'): row for row in extracted if isinstance(row, dict)}
    if len(by_id) != len(originals) or set(by_id) != {r['input_set_id'] for r in originals}:
        raise ValueError('extractions contain missing, duplicate or foreign IDs')
    if not isinstance(model_configuration, dict) or not concrete(model_configuration):
        raise ValueError('explicit extraction model configuration required')
    template = TARGET_EXTRACTION_PROMPT.read_text()
    ordered = []
    for original in originals:
        row = by_id[original['input_set_id']]
        base = {key: value for key, value in row.items()
                if key not in ('target_extraction', 'target_extraction_source_field')}
        if base != original:
            raise ValueError('extracted candidate source changed: ' + original['input_set_id'])
        field, text = extraction_source(original)
        extraction = row.get('target_extraction')
        if not isinstance(extraction, dict):
            raise ValueError('missing target extraction')
        if (row.get('target_extraction_source_field') != field
                or extraction.get('stage') != 'reference_target_extraction'
                or extraction.get('input_set_id') != row['input_set_id']
                or extraction.get('evaluation_input') != {
                    'target_paper_text': text,
                    'rendered_prompt': template.replace('{{TARGET_PAPER_TEXT}}', text)}):
            raise ValueError('extraction source, input or prompt mismatch')
        provenance = extraction.get('provenance', {})
        if (provenance.get('prompt_path') != 'prompts/e6/09_target_extraction.txt'
                or provenance.get('prompt_sha256') != file_digest(TARGET_EXTRACTION_PROMPT)
                or provenance.get('model_configuration') != model_configuration):
            raise ValueError('extraction model or prompt provenance mismatch')
        if extraction.get('status') not in ('succeeded', 'failed'):
            raise ValueError('invalid extraction execution status')
        if extraction['status'] == 'succeeded':
            try:
                raw = json.loads(extraction['raw_output'])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError('successful extraction must preserve raw JSON output') from exc
            if raw != extraction.get('parsed_output') or not isinstance(raw, dict) or set(raw) != {
                'research_question', 'main_hypothesis', 'research_question_explicit', 'main_hypothesis_explicit'}:
                raise ValueError('parsed extraction differs from raw output/schema')
            for name in ('research_question', 'main_hypothesis'):
                if raw[name] is not None and (not isinstance(raw[name], str) or not raw[name].strip()):
                    raise ValueError('invalid extracted text field')
                if type(raw[name + '_explicit']) is not bool:
                    raise ValueError('extracted explicitness must be Boolean')
        ordered.append(copy.deepcopy(row))
    return ordered


def prepare_extraction_review(candidate, proposal, extracted, *, model_configuration):
    """Offline packaging of caller-produced annotations; does not approve them."""
    ordered = validate_extracted_candidates(candidate, proposal, extracted, model_configuration)
    manifest = build_literature_extraction_manifest(proposal, ordered, model_configuration=model_configuration)
    # Failure records remain in the manifest; reviews cannot be invented for failed cases.
    worklist = build_proposed_manual_review_worklist(ordered, proposal)
    return manifest, worklist


def review_policy_from_approval(approval, root=ROOT):
    errors = validate_approval_record(approval, root=root, required_ids=(24,))
    if errors:
        raise ValueError('; '.join(errors))
    decision = next(row for row in approval['decisions'] if row['id'] == 24)
    policy = decision['resolved_details']['review_policy']
    if (not isinstance(policy, dict) or type(policy.get('reviewer_count')) is not int
            or policy['reviewer_count'] < 1
            or policy.get('disagreement_policy') != 'independent_adjudicator'
            or not concrete(policy.get('guide_path')) or not concrete(policy.get('guide_sha256'))):
        raise ValueError('review policy requires reviewer_count, guide path/hash and independent_adjudicator')
    if decision['choice'] == 'accept_proposal' and policy['reviewer_count'] != 2:
        raise ValueError('accepted review proposal requires two independent reviewers')
    from researcher_approval import safe_path
    if file_digest(safe_path(root, policy['guide_path'])) != policy['guide_sha256']:
        raise ValueError('review guide hash mismatch')
    fields = policy.get('check_fields', list(CHECK_FIELDS))
    if (not isinstance(fields, list) or len(fields) != len(set(fields))
            or not set(CHECK_FIELDS) <= set(fields)
            or not set(fields) <= set(CHECK_FIELDS + SOURCE_CONTENT_CHECK_FIELDS)):
        raise ValueError('unsupported or incomplete review check fields')
    return policy


def validate_review_records(worklist, records, adjudications, approval, *, root=ROOT):
    """Require real source-bound human checks; a completed negative check is not acceptance."""
    verify_seal(worklist, 'worklist_sha256')
    policy = review_policy_from_approval(approval, root)
    check_fields = policy.get('check_fields', CHECK_FIELDS)
    ids = worklist.get('selected_input_set_ids')
    if not isinstance(ids, list) or len(ids) != 20 or len(set(ids)) != 20:
        raise ValueError('review requires exactly 20 distinct cases')
    forms = worklist.get('reviews')
    if not isinstance(forms, list) or [r.get('input_set_id') for r in forms] != ids:
        raise ValueError('review worklist cases differ from selected IDs')
    if not isinstance(records, list) or not isinstance(adjudications, list):
        raise ValueError('reviews and adjudications must be lists')
    expected = {row['input_set_id']: row for row in forms}
    grouped = {key: [] for key in ids}
    for row in records:
        if not isinstance(row, dict) or row.get('input_set_id') not in grouped:
            raise ValueError('foreign or malformed review case')
        base = expected[row['input_set_id']]
        text = base.get('target_source_text')
        if not isinstance(text, str) or hashlib.sha256(text.encode()).hexdigest() != base.get('target_source_text_sha256'):
            raise ValueError('worklist source text hash mismatch')
        if (row.get('extraction_sha256') != digest(base['target_extraction'])
                or row.get('target_source_text_sha256') != base['target_source_text_sha256']
                or row.get('review_guide_sha256') != policy['guide_sha256']):
            raise ValueError('review source, extraction or guide changed')
        if (not nonempty_text(row.get('reviewer_id')) or not valid_utc(row.get('reviewed_at_utc'))
                or row.get('manual_check_completed') is not True
                or any(type(row.get(key)) is not bool for key in check_fields)):
            raise ValueError('incomplete human review record')
        if policy.get('require_error_and_correction_records') and (
                not isinstance(row.get('extraction_errors'), list)
                or not isinstance(row.get('corrections'), list)
                or not nonempty_text(row.get('reviewer_notes'))):
            raise ValueError('review requires extraction errors, corrections and source notes')
        grouped[row['input_set_id']].append(row)
    adjudicated = {}
    for row in adjudications:
        if not isinstance(row, dict) or row.get('input_set_id') not in grouped or row['input_set_id'] in adjudicated:
            raise ValueError('duplicate, malformed or foreign adjudication')
        adjudicated[row['input_set_id']] = row
    accepted = []
    disagreement_ids = []
    for input_id, checks in grouped.items():
        if len(checks) != policy['reviewer_count'] or len({r['reviewer_id'] for r in checks}) != len(checks):
            raise ValueError('missing or duplicate independent reviewers: ' + input_id)
        disagree = any(len({r[key] for r in checks}) > 1 for key in check_fields)
        if disagree:
            disagreement_ids.append(input_id)
            final = adjudicated.pop(input_id, None)
            if (not isinstance(final, dict) or not nonempty_text(final.get('adjudicator_id'))
                    or final['adjudicator_id'] in {r['reviewer_id'] for r in checks}
                    or not valid_utc(final.get('adjudicated_at_utc')) or not concrete(final.get('rationale'))
                    or final.get('review_records_sha256') != digest(sorted(checks, key=lambda r: r['reviewer_id']))
                    or any(type(final.get(key)) is not bool for key in check_fields)):
                raise ValueError('disagreement requires independent source-bound adjudication: ' + input_id)
        else:
            final = checks[0]
        if all(final[key] for key in check_fields):
            accepted.append(input_id)
    if adjudicated:
        raise ValueError('unexpected adjudication without reviewer disagreement')
    return seal({'schema_version': 'e6-literature-review-validation-v1',
                 'review_worklist_sha256': worklist['worklist_sha256'],
                 'review_records_sha256': digest(records), 'adjudications_sha256': digest(adjudications),
                 'approval_record_sha256': digest(approval),
                 'completed_unique_cases': 20, 'accepted_input_set_ids': accepted,
                 'disagreement_input_set_ids': disagreement_ids,
                 'annotations_usable': len(accepted) == 20,
                 'note': 'Validation checks records, not human identity or scientific truth; negative checks require correction and renewed review.'})


def validate_review_bundle(candidate, proposal, extraction_manifest, worklist,
                           records, adjudications, approval, *, root=ROOT):
    """Entry point for complete validation against actual source and sample artifacts."""
    require_approved_sample(approval, proposal, root)
    verify_seal(extraction_manifest)
    model = extraction_manifest.get('model_configuration')
    ordered = validate_extracted_candidates(
        candidate, proposal, extraction_manifest.get('target_extractions'), model)
    decision = next(row for row in approval['decisions'] if row['id'] == 24)
    if model != decision['resolved_details']['extraction_model_configuration']:
        raise ValueError('extraction model configuration differs from researcher approval')
    expected_manifest = build_literature_extraction_manifest(
        proposal, ordered, model_configuration=model)
    if extraction_manifest != expected_manifest:
        raise ValueError('extraction manifest differs from source-bound records')
    if worklist != build_proposed_manual_review_worklist(ordered, proposal):
        raise ValueError('review worklist differs from extraction and deterministic review selection')
    return validate_review_records(worklist, records, adjudications, approval, root=root)


def freeze_approved_selection(candidate, proposal, plan, approval, output, *, root=ROOT):
    """Explicit source-selection freeze only; existing approvals are mandatory.

    Validates before any write and exclusively creates the selected manifest.
    Does not sign approvals, update config, finalize PREREG or run inference.
    """
    selected = build_frozen_literature_manifest(candidate, proposal, plan, approval, root=root)
    write_manifest_exclusive(Path(output), selected)
    return selected


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, default=CANDIDATE)
    parser.add_argument('--proposal', type=Path, default=PROPOSAL)
    parser.add_argument('--output', type=Path, required=True, help='new exclusive output path (freeze plan by default; selected manifest with explicit freeze flag)')
    parser.add_argument('--freeze-approved-selection', action='store_true',
                        help='freeze source selection only after explicit sample/review-policy approvals')
    parser.add_argument('--approval-record', type=Path, default=ROOT / 'E6/RESEARCHER_APPROVAL.json')
    parser.add_argument('--plan', type=Path, default=PLAN)
    args = parser.parse_args(argv)
    try:
        candidate = json.loads(args.candidate.read_text())
        proposal = json.loads(args.proposal.read_text())
        if args.freeze_approved_selection:
            selected = freeze_approved_selection(candidate, proposal,
                json.loads(args.plan.read_text()), json.loads(args.approval_record.read_text()), args.output)
            print(json.dumps({'status': 'source_selection_frozen_only',
                              'output': str(args.output), 'manifest_sha256': selected['manifest_sha256']}))
            return 0
        plan = build_freeze_plan(candidate, proposal)
        write_manifest_exclusive(args.output, plan)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.error(str(exc))
    print(json.dumps({'status': plan['status'], 'input_count': len(plan['extraction_jobs']),
                      'output': str(args.output), 'manifest_sha256': plan['manifest_sha256']}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
