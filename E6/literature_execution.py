"""Source-bound literature generation through the existing seven-arm orchestrator.

Preparation never authorizes inference. Final runs require frozen sources,
researcher/config/runtime/Git gates; annotations never enter generation inputs.
"""
from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path
from execution_preparation import literature_reference_inputs, export_generation_records, write_jsonl_exclusive
from prepare_literature_sample_proposal import verify_sample_proposal
from researcher_approval import digest, safe_path
from inductive_execution import deterministic_evidence_donors, text_hash
from question_pipeline import (TrustedDEmptyEvidenceAuditor, TrustedDEmptyAuditResult,
    generate_d_empty, _run_control_generation, _sha256_json)


@dataclass(frozen=True)
class LiteratureExecutionContext:
    candidate: dict
    sample: dict
    references: dict
    task: str
    inputs: tuple
    donors: dict
    context_sha256: str


def prepare_literature_execution_context(candidate, sample, references, *, task):
    if not isinstance(task, str) or not task.strip():
        raise ValueError('explicit common literature task required')
    rows = verify_sample_proposal(candidate, sample)
    if len(rows) != 100:
        raise ValueError('this execution integration requires the prepared 100-paper sample')
    if any(row['target'].get('abstract') and row['target']['abstract'] in task for row in rows):
        raise ValueError('target abstract must not be retained in the common task')
    inputs = tuple(literature_reference_inputs(candidate, sample, references, task=task))
    donors = deterministic_evidence_donors([row.paper_id for row in inputs])
    checksum = digest({'candidate': candidate['manifest_sha256'], 'sample': sample['proposal_sha256'],
        'references': references['manifest_sha256'], 'task': task, 'donors': donors,
        'inputs': [row.__dict__ for row in inputs]})
    return LiteratureExecutionContext(candidate, sample, references, task, inputs, donors, checksum)


def validate_literature_execution_context(context, experiment_input):
    if type(context) is not LiteratureExecutionContext:
        raise ValueError('typed literature context required')
    rebuilt = prepare_literature_execution_context(context.candidate, context.sample, context.references, task=context.task)
    if (context.context_sha256 != rebuilt.context_sha256 or context.inputs != rebuilt.inputs
            or context.donors != rebuilt.donors or experiment_input not in rebuilt.inputs):
        raise ValueError('literature source, input or donor context changed')
    return rebuilt


def validate_frozen_literature_context(context, config, *, root):
    from literature_finalization import verify_seal
    literature = json.loads((Path(root) / 'E6/literature_testbed_config.json').read_text())
    paths = [(literature['candidate_manifest']['path'], context.candidate),
             ('E6/data/literature_sample_proposal_v1.json', context.sample),
             (config['dataset']['literature_reference_selection_proposal'], context.references)]
    for relative, expected in paths:
        if json.loads(safe_path(root, relative).read_text()) != expected:
            raise ValueError('literature context differs from frozen source artifact: ' + relative)
    selected_path = literature.get('selected_manifest', {}).get('path', 'E6/data/literature_selected_manifest_v1.json')
    selected = json.loads(safe_path(root, selected_path).read_text())
    verify_seal(selected)
    if (selected.get('input_sets_selected') is not True or selected.get('input_sets_frozen') is not True
            or selected.get('sample_proposal_sha256') != context.sample['proposal_sha256']
            or selected.get('candidate_manifest_sha256') != context.candidate['manifest_sha256']
            or selected.get('selected_input_set_ids') != [row.paper_id for row in context.inputs]
            or selected.get('input_sets') != verify_sample_proposal(context.candidate, context.sample)):
        raise ValueError('selected literature manifest does not freeze this sample/source')
    approval = json.loads((Path(root) / 'E6/RESEARCHER_APPROVAL.json').read_text())
    task_decision = next(row for row in approval['decisions'] if row['id'] == 4)
    tasks = task_decision.get('resolved_details', {}).get('task_text_by_testbed')
    if not isinstance(tasks, dict) or tasks.get('literature') != context.task:
        raise ValueError('literature task differs from explicitly approved task text')
    implemented = {'donor_matching_rule': 'sha256_hash_ordered_derangement_no_reuse_v1',
        'within_split_only': True, 'assignment_seed': 2026, 'number_of_assignments': 1,
        'donor_reuse_policy': 'prohibited_within_assignment_batch', 'self_donation_allowed': False}
    if any(config.get('controls', {}).get('d_shuffled', {}).get(k) != v for k, v in implemented.items()):
        raise ValueError('literature donor implementation differs from frozen control policy')


class LiteratureTaskAuditor(TrustedDEmptyEvidenceAuditor):
    def __init__(self, context): self.context = context
    def audit(self, recipient_id, retained_task_text, original_evidence, policy):
        row = next((r for r in self.context.inputs if r.paper_id == recipient_id), None)
        if (row is None or retained_task_text != self.context.task
                or original_evidence.get('abstract') != row.evidence
                or original_evidence.get('reference_evidence') != list(row.reference_evidence)):
            raise ValueError('literature empty-control source/task mismatch')
        # Final source validation binds this common task to researcher-approved
        # text; this audit is structural, not automated semantic adjudication.
        return TrustedDEmptyAuditResult(trust_status='trusted_production',
            auditor_id='approved_common_literature_task_v1', audit_id=digest([self.context.context_sha256, recipient_id]),
            audit_complete=True, audit_scope='retained_task_domain_text', leakage_check_performed=True,
            retained_task_leakage_detected=False, recipient_id=recipient_id,
            scrubbed_task_sha256=text_hash(retained_task_text), removed_fields=['abstract', 'reference_evidence'],
            removed_evidence_sha256={'abstract': text_hash(row.evidence),
                                    'reference_evidence': _sha256_json(list(row.reference_evidence))}, rendered_evidence='')


def generate_literature_control(state, arm, experiment_input, context, model_call, settings, retry_prompt_builder=None):
    if arm == 'D-empty':
        return generate_d_empty(state, experiment_input.paper_id, experiment_input.domain_and_task,
            model_call, settings, LiteratureTaskAuditor(context), original_abstract=experiment_input.evidence,
            reference_evidence=experiment_input.reference_evidence, retry_prompt_builder=retry_prompt_builder)
    if arm != 'D-shuffled': raise ValueError('unknown literature control')
    donor_id = context.donors[experiment_input.paper_id]
    donor = next(row for row in context.inputs if row.paper_id == donor_id)
    provenance = {'source_kind': 'verified_cited_reference_bundle', 'recipient_id': experiment_input.paper_id,
        'donor_id': donor_id, 'donor_split': 'EVALUATION', 'seed': 2026,
        'evidence_sha256': text_hash(donor.evidence), 'context_sha256': context.context_sha256,
        'sample_proposal_sha256': context.sample['proposal_sha256'],
        'reference_selection_sha256': context.references['manifest_sha256'],
        'donor_reference_ids': next(row['reference_ids'] for row in context.references['selections'] if row['input_set_id'] == donor_id),
        'no_self_no_reuse_verified': donor_id != experiment_input.paper_id and len(set(context.donors.values())) == len(context.donors)}
    return _run_control_generation(state, arm, experiment_input.domain_and_task, donor.evidence,
                                   provenance, model_call, settings, retry_prompt_builder, None)


def run_literature_generation(context, input_set_id, settings, client, *, token_budget_per_arm=None):
    from orchestrator import run_seven_arms
    row = next((r for r in context.inputs if r.paper_id == input_set_id), None)
    if row is None: raise ValueError('unknown selected literature ID')
    return run_seven_arms(row, settings, client, client.model_configuration, execution_mode='final',
        literature_execution_context=context, token_budget_per_arm=token_budget_per_arm)


def execute_literature_input_set(context, input_set_id, settings, client, *, checkpoint_dir,
                                 token_budget_per_arm=None):
    """Gated generation and resumable export; target scoring is a separate interface."""
    from orchestrator import ROOT, validate_current_protocol, ordered_arm_outputs
    from validate_protocol import validate_preregistration_git_commit
    from development_runtime_probe import validate_runtime_evidence
    directory = Path(checkpoint_dir)
    stem = digest(input_set_id)[:16]
    checkpoint = directory / f'{stem}_literature_generation.json'
    if checkpoint.exists():
        saved = json.loads(checkpoint.read_text())
        if (saved.get('context_sha256') != context.context_sha256
                or saved.get('checkpoint_sha256') != digest({k: v for k, v in saved.items() if k != 'checkpoint_sha256'})):
            raise ValueError('literature generation checkpoint changed')
        envelope = saved['envelope']
        config = json.loads((ROOT / 'E6/config.json').read_text())
        errors = validate_current_protocol() + validate_preregistration_git_commit(ROOT) + validate_runtime_evidence(config, root=ROOT)
        if errors: raise ValueError('literature checkpoint replay blocked: ' + '; '.join(errors))
        row = next((r for r in context.inputs if r.paper_id == input_set_id), None)
        validate_literature_execution_context(context, row)
        validate_frozen_literature_context(context, config, root=ROOT)
        method = config['execution_replication']['run_order_method']
        cap = config['inference_budget']['tokens_per_input_set_arm']
        gen = config['generation']
        if (envelope.get('paper_id') != input_set_id or envelope.get('literature_execution_context_sha256') != context.context_sha256
                or envelope.get('input_provenance') != dict(row.provenance)
                or envelope.get('protocol_validation_errors') or envelope.get('execution_mode') != 'final'
                or envelope.get('model_configuration') != client.model_configuration
                or client.model != gen['model']
                or any(client.generation_options.get(k) != gen.get(v) for k, v in (
                    ('num_ctx', 'context_limit'), ('num_predict', 'max_output_tokens'),
                    ('temperature', 'temperature'), ('top_p', 'top_p'), ('seed', 'seed')))
                or client.preflight_context_limit != gen['context_limit']
                or envelope['token_budget_configuration']['tokens_per_arm'] != cap
                or (token_budget_per_arm is not None and token_budget_per_arm != cap)
                or envelope.get('execution_order_policy') != method
                or envelope.get('execution_arm_output_order') != ordered_arm_outputs(input_set_id, gen['seed'], method)):
            raise ValueError('literature checkpoint differs from frozen source/model/budget/schedule')
    else:
        envelope = run_literature_generation(context, input_set_id, settings, client,
                                             token_budget_per_arm=token_budget_per_arm)
        if envelope['experiment_status'] == 'blocked':
            return {'status': 'blocked', 'generation_envelope': envelope}
        directory.mkdir(parents=True, exist_ok=True)
        saved = {'context_sha256': context.context_sha256, 'envelope': envelope}
        saved['checkpoint_sha256'] = digest(saved)
        with checkpoint.open('x') as handle: json.dump(saved, handle, ensure_ascii=False, sort_keys=True)
    rows, failures = export_generation_records(envelope, testbed='literature', seed=client.generation_options['seed'])
    for path, records in ((directory / f'{stem}_generations.jsonl', rows), (directory / f'{stem}_failures.jsonl', failures)):
        if path.exists():
            if [json.loads(line) for line in path.read_text().splitlines() if line.strip()] != records:
                raise ValueError('existing literature export differs from checkpoint')
        else: write_jsonl_exclusive(path, records)
    return {'status': envelope['experiment_status'], 'generation_envelope': envelope,
            'generation_records': rows, 'failed_cells': failures,
            'scoring_status': 'separate approved target-extraction/evaluation interface; never inferred from generation'}
