"""Source-bound TRAIN cohort integration; no execution at import or preparation.

Every real entry point retains protocol, researcher approval and Git gates.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Any
from researcher_approval import digest
from prepare_hypobench_inductive import inductive_generation_inputs
from prepare_hypobench_testbed import DEFAULT_DATASET_DIR
from question_pipeline import (
    TrustedDEmptyEvidenceAuditor, TrustedDEmptyAuditResult, generate_d_empty,
    _run_control_generation, _sha256_json,
)


def text_hash(value):
    return hashlib.sha256(value.encode()).hexdigest()


@dataclass(frozen=True)
class TrainExecutionContext:
    proposal: dict
    test_manifest: dict
    dataset_dir: Path
    inputs: tuple
    donors: dict
    context_sha256: str


def deterministic_evidence_donors(ids):
    ids = sorted(ids)
    if len(ids) < 2:
        raise ValueError('D-shuffled requires at least two distinct evidence sets')
    choices = {recipient: sorted((donor for donor in ids if donor != recipient),
                  key=lambda donor: (text_hash(f'E6-D-SHUFFLED-v1|2026|{recipient}|{donor}'), donor)) for recipient in ids}
    assignments = {}
    def assign(index, used):
        if index == len(ids): return True
        recipient = ids[index]
        for donor in choices[recipient]:
            if donor in used: continue
            assignments[recipient] = donor
            if assign(index + 1, used | {donor}): return True
        assignments.pop(recipient, None)
        return False
    if not assign(0, set()): raise ValueError('no complete evidence derangement')
    return assignments


def prepare_train_execution_context(proposal, test_manifest, *, dataset_dir=DEFAULT_DATASET_DIR):
    inputs = tuple(inductive_generation_inputs(proposal, test_manifest, dataset_dir=dataset_dir))
    assignments = deterministic_evidence_donors([row.paper_id for row in inputs])
    checksum = digest({'proposal_sha256': proposal['manifest_sha256'],
                       'test_manifest_sha256': test_manifest['manifest_sha256'],
                       'donors': assignments, 'inputs': [row.__dict__ for row in inputs]})
    return TrainExecutionContext(proposal, test_manifest, Path(dataset_dir), inputs, assignments, checksum)


def validate_train_execution_context(context, experiment_input):
    if type(context) is not TrainExecutionContext:
        raise ValueError('typed TRAIN execution context required')
    rebuilt = prepare_train_execution_context(context.proposal, context.test_manifest, dataset_dir=context.dataset_dir)
    if context.context_sha256 != rebuilt.context_sha256 or context.donors != rebuilt.donors or context.inputs != rebuilt.inputs:
        raise ValueError('TRAIN context/source/donor mapping changed')
    matching = next((row for row in rebuilt.inputs if row.paper_id == experiment_input.paper_id), None)
    if matching is None or matching != experiment_input:
        raise ValueError('generation input differs from actual TRAIN evidence cohort')
    return rebuilt


def validate_frozen_train_context(context, config, *, root):
    import json
    from researcher_approval import safe_path
    generation_path = config.get('dataset', {}).get('data_generation_proposal')
    evaluation_path = config.get('dataset', {}).get('data_evaluation_manifest')
    if not generation_path or not evaluation_path:
        raise ValueError('frozen TRAIN proposal and TEST evaluation manifest paths required')
    if json.loads(safe_path(root, generation_path).read_text()) != context.proposal:
        raise ValueError('TRAIN context differs from frozen proposal artifact')
    if json.loads(safe_path(root, evaluation_path).read_text()) != context.test_manifest:
        raise ValueError('TEST context differs from frozen evaluation artifact')
    implemented = {'donor_matching_rule': 'sha256_hash_ordered_derangement_no_reuse_v1',
                   'within_split_only': True, 'assignment_seed': 2026, 'number_of_assignments': 1,
                   'donor_reuse_policy': 'prohibited_within_assignment_batch', 'self_donation_allowed': False}
    frozen = config.get('controls', {}).get('d_shuffled', {})
    if any(frozen.get(key) != value for key, value in implemented.items()):
        raise ValueError('TRAIN donor implementation differs from frozen policy; adapt before execution')


class TrainTaskAuditor(TrustedDEmptyEvidenceAuditor):
    def __init__(self, context): self.context = context
    def audit(self, recipient_id, retained_task_text, original_evidence, policy):
        row = next((r for r in self.context.inputs if r.paper_id == recipient_id), None)
        if (row is None or retained_task_text != self.context.proposal['task_description']
                or original_evidence.get('abstract') != row.evidence
                or original_evidence.get('reference_evidence') != []):
            raise ValueError('task/evidence differs from source-bound generic TRAIN task')
        return TrustedDEmptyAuditResult(
            trust_status='trusted_production', auditor_id='e6_source_bound_train_task_v1',
            audit_id=digest({'context': self.context.context_sha256, 'recipient': recipient_id}),
            audit_complete=True, audit_scope='retained_task_domain_text', leakage_check_performed=True,
            retained_task_leakage_detected=False, recipient_id=recipient_id,
            scrubbed_task_sha256=text_hash(retained_task_text), removed_fields=['abstract', 'reference_evidence'],
            removed_evidence_sha256={'abstract': text_hash(row.evidence), 'reference_evidence': _sha256_json([])},
            rendered_evidence='')


def generate_train_control(state, arm, experiment_input, context, model_call, settings, retry_prompt_builder=None):
    if arm == 'D-empty':
        return generate_d_empty(state, experiment_input.paper_id, experiment_input.domain_and_task,
            model_call, settings, TrainTaskAuditor(context), original_abstract=experiment_input.evidence,
            reference_evidence=(), retry_prompt_builder=retry_prompt_builder)
    if arm != 'D-shuffled': raise ValueError('unknown TRAIN control')
    donor_id = context.donors[experiment_input.paper_id]
    donor = next(row for row in context.inputs if row.paper_id == donor_id)
    if donor_id == experiment_input.paper_id or donor.split != 'TRAIN':
        raise ValueError('invalid TRAIN donor')
    provenance = {'source_kind': 'TRAIN_evidence_cohort',
                  'control_interpretation': 'same-task evidence swap; different-mechanism corruption is not asserted',
                  'recipient_id': experiment_input.paper_id,
                  'donor_id': donor_id, 'donor_split': 'TRAIN', 'seed': 2026,
                  'context_sha256': context.context_sha256, 'evidence_sha256': text_hash(donor.evidence),
                  'source_proposal_sha256': context.proposal['manifest_sha256'],
                  'donor_source_row_ids': donor.provenance['source_row_ids'],
                  'no_self_no_reuse_verified': len(set(context.donors.values())) == len(context.donors)}
    return _run_control_generation(state, arm, experiment_input.domain_and_task, donor.evidence,
        provenance, model_call, settings, retry_prompt_builder, None)


def run_train_generation(context, input_set_id, settings, client, *, token_budget_per_arm=None):
    """Future authorized generation only; real gates run inside the orchestrator."""
    from orchestrator import run_seven_arms
    row = next((r for r in context.inputs if r.paper_id == input_set_id), None)
    if row is None: raise ValueError('unknown TRAIN input set')
    return run_seven_arms(row, settings, client, client.model_configuration,
        execution_mode='final', train_execution_context=context, token_budget_per_arm=token_budget_per_arm)


def require_final_authorization(context, envelope):
    from orchestrator import validate_current_protocol
    from validate_protocol import validate_preregistration_git_commit
    from researcher_approval import ROOT
    errors = validate_current_protocol() + validate_preregistration_git_commit(ROOT)
    import json
    from development_runtime_probe import validate_runtime_evidence
    config = json.loads((ROOT / 'E6/config.json').read_text())
    errors += validate_runtime_evidence(config, root=ROOT)
    validate_frozen_train_context(context, config, root=ROOT)
    if errors:
        raise ValueError('final evaluation blocked: ' + '; '.join(errors))
    from orchestrator import ordered_arm_outputs
    order_policy = config.get('execution_replication', {}).get('run_order_method')
    if (envelope.get('execution_order_policy') != order_policy
            or envelope.get('execution_arm_output_order') != ordered_arm_outputs(envelope.get('paper_id'), config.get('generation', {}).get('seed'), order_policy)):
        raise ValueError('generation checkpoint run order differs from frozen schedule')
    options = envelope.get('model_configuration', {}).get('generation_options', {})
    gen = config.get('generation', {})
    if (envelope.get('model_configuration', {}).get('model') != gen.get('model')
            or any(options.get(key) != gen.get(field) for key, field in (
                ('num_ctx', 'context_limit'), ('num_predict', 'max_output_tokens'),
                ('temperature', 'temperature'), ('top_p', 'top_p'), ('seed', 'seed')))
            or envelope.get('token_budget_configuration', {}).get('tokens_per_arm') != config.get('inference_budget', {}).get('tokens_per_input_set_arm')):
        raise ValueError('generation envelope differs from frozen runtime or generated-token budget')
    if envelope.get('execution_mode') != 'final':
        raise ValueError('only final-mode envelopes may enter confirmatory scoring')
    if envelope.get('protocol_validation_errors') or envelope.get('train_execution_context_sha256') != context.context_sha256:
        raise ValueError('generation envelope was blocked or does not bind TRAIN execution context')
    row = next((r for r in context.inputs if r.paper_id == envelope.get('paper_id')), None)
    if row is None: raise ValueError('envelope does not belong to TRAIN cohort')
    validate_train_execution_context(context, row)
    if envelope.get('input_provenance') != dict(row.provenance):
        raise ValueError('envelope provenance differs from source-bound TRAIN input')


def bound_hdr_score(context, input_id, arm, hypotheses, payload):
    """Join actual HDR inputs to this arm's output and original ground truth."""
    from prepare_hypobench_inductive import score_reference_hdr
    if payload is None:
        return {'status': 'blocked_missing_HDR_feature_mapping_or_judgments'}
    if (payload.get('generation_input_set_id') != input_id or payload.get('arm') != arm
            or payload.get('hypotheses_sha256') != digest(hypotheses)):
        raise ValueError('HDR judgments do not bind this cohort/arm/hypothesis set')
    provenance = payload.get('provenance', {})
    if provenance.get('ground_truth_source_sha256') != context.test_manifest['dataset_ground_truth']['source_file_sha256']:
        raise ValueError('HDR ground truth source differs from protected dataset')
    mapping = payload.get('feature_mapping')
    refs = payload.get('reference_feature_ids')
    if not isinstance(mapping, dict) or not isinstance(refs, list) or set(mapping) != set(refs) or digest(mapping) != provenance.get('feature_mapping_sha256'):
        raise ValueError('HDR feature mapping/provenance mismatch')
    truth = context.test_manifest['dataset_ground_truth']['hypotheses']
    for feature in mapping.values():
        indices = feature.get('ground_truth_indices') if isinstance(feature, dict) else None
        if not isinstance(indices, list) or not indices or any(type(i) is not int or not 0 <= i < len(truth) for i in indices):
            raise ValueError('HDR reference feature lacks source-ground-truth mapping')
        if feature.get('source_texts') != [truth[i] for i in indices]:
            raise ValueError('HDR mapping quotation differs from actual ground truth')
    score = score_reference_hdr(refs, payload.get('discovered_feature_ids'), payload.get('relationship_scores'), provenance=provenance)
    return {'status': 'scored', **score}


def evaluate_train_envelope(context, envelope, prediction_policy, *, batch_size,
                            max_workers=1, hdr_inputs_by_arm=None, checkpoint_dir=None):
    """Future gated evaluation, independent-row transport batches, HDR and export.

    No callback is invoked until the real approval/config/Git gates pass. TEST
    labels enter only the scorer. Checkpoints bind exact source/output/policy IDs.
    """
    import json
    from itertools import islice
    from prepare_hypobench_inductive import heldout_prediction_jobs, score_inductive_predictions
    from execution_preparation import export_generation_records, write_jsonl_exclusive
    from evaluation import ARMS
    require_final_authorization(context, envelope)
    if type(batch_size) is not int or batch_size < 1 or type(max_workers) is not int or not 1 <= max_workers <= 4:
        raise ValueError('positive batch size and concurrency 1 through 4 required')
    policy_identity = getattr(prediction_policy, 'policy_identity', None)
    if not isinstance(policy_identity, dict) or not policy_identity:
        raise ValueError('explicit frozen prediction policy identity required')
    input_id = envelope['paper_id']
    seed = envelope['model_configuration']['generation_options']['seed']
    generations, failures = export_generation_records(envelope, testbed='data', seed=seed)
    evaluations = {}
    directory = None
    pipeline_identity = digest({'context': context.context_sha256, 'envelope': digest(envelope),
                                'policy': policy_identity, 'hdr_inputs': hdr_inputs_by_arm,
                                'batch_size': batch_size,
                                'pipeline_implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    if checkpoint_dir is not None:
        directory = Path(checkpoint_dir)
        directory.mkdir(parents=True, exist_ok=True)
        summary_path = directory / f'{digest(input_id)[:16]}_{pipeline_identity[:16]}_evaluation.json'
        if summary_path.exists():
            completed = json.loads(summary_path.read_text())
            if (completed.get('pipeline_identity') != pipeline_identity
                    or completed.get('result_sha256') != digest({k: v for k, v in completed.items() if k != 'result_sha256'})):
                raise ValueError('completed evaluation artifact differs from source/output/policy/HDR inputs')
            return completed
    for arm in ARMS:
        entry = envelope['arms'][arm]
        if entry.get('execution_status') != 'succeeded':
            evaluations[arm] = {'status': 'blocked_generation_failed'}
            continue
        hypotheses = [r['text'] for r in entry['output']['hypotheses']]
        jobs = iter(heldout_prediction_jobs(context.proposal, context.test_manifest, input_id, hypotheses,
                                           dataset_dir=context.dataset_dir))
        predictions = []
        batch_index = 0
        while True:
            chunk = list(islice(jobs, batch_size))
            if not chunk: break
            identity = digest({'context': context.context_sha256, 'envelope': digest(envelope),
                'arm': arm, 'row_ids': [r['evaluation_row_id'] for r in chunk],
                'policy': policy_identity})
            path = None if directory is None else directory / f'{digest(input_id)[:16]}_{arm}_{batch_index:04d}.json'
            if path is not None and path.exists():
                saved = json.loads(path.read_text())
                if (saved.get('identity') != identity
                        or saved.get('checkpoint_sha256') != digest({k: v for k, v in saved.items() if k != 'checkpoint_sha256'})):
                    raise ValueError('prediction checkpoint source/output/policy changed')
                results = saved['results']
            else:
                prepared = [r['prepared_input'] for r in chunk]
                batch = getattr(prediction_policy, 'predict_many', None)
                results = batch(prepared, max_workers=max_workers) if callable(batch) else [prediction_policy(p) for p in prepared]
                if not isinstance(results, list) or len(results) != len(chunk):
                    raise ValueError('prediction transport batch lost or added evaluation examples')
                if path is not None:
                    saved = {'identity': identity, 'results': results}
                    saved['checkpoint_sha256'] = digest(saved)
                    with path.open('x') as handle: json.dump(saved, handle, sort_keys=True, ensure_ascii=False)
            for job, result in zip(chunk, results):
                labels = result.get('predicted_labels') if isinstance(result, dict) else None
                prediction = labels[0] if isinstance(labels, list) and len(labels) == 1 else None
                predictions.append({'generation_input_set_id': input_id, 'arm': arm,
                                    'input_set_id': job['evaluation_row_id'], 'predicted_label': prediction,
                                    'raw_output': result})
            batch_index += 1
        accuracy = score_inductive_predictions(context.proposal, context.test_manifest, input_id, arm,
                                                predictions, dataset_dir=context.dataset_dir)
        hdr_payload = (hdr_inputs_by_arm or {}).get(arm)
        evaluations[arm] = {'status': 'evaluated', 'heldout': accuracy,
                           'hdr': bound_hdr_score(context, input_id, arm, hypotheses, hdr_payload),
                           'predictions': predictions, 'prediction_policy_identity': policy_identity}
    result = {'generation_input_set_id': input_id, 'context_sha256': context.context_sha256,
              'evaluations': evaluations, 'generation_records': generations, 'failed_cells': failures,
              'pipeline_identity': pipeline_identity,
              'required_metrics_scope': 'TRAIN data utility accuracy and R44 HDR only; other E6 metrics require separate evaluation',
              'batch_semantics': 'independent single-observation prompts; batching never combines observations'}
    result['required_metrics_complete'] = all(row.get('status') == 'evaluated' and row.get('hdr', {}).get('status') == 'scored'
                                              for row in evaluations.values())
    result['evaluation_status'] = 'completed' if result['required_metrics_complete'] else 'incomplete_required_metrics'
    result['result_sha256'] = digest(result)
    if directory is not None:
        # Batch checkpoints survive interruptions; finalized exports never overwrite.
        stem = digest(input_id)[:16]
        for path, rows in ((directory / f'{stem}_generations.jsonl', generations),
                           (directory / f'{stem}_failures.jsonl', failures)):
            if path.exists():
                if [json.loads(line) for line in path.read_text().splitlines() if line.strip()] != rows:
                    raise ValueError('existing export differs from current envelope')
            else:
                write_jsonl_exclusive(path, rows)
        with summary_path.open('x') as handle:
            json.dump(result, handle, sort_keys=True, ensure_ascii=False)
    return result


def execute_train_input_set(context, input_set_id, settings, generation_client, prediction_policy, *,
                            batch_size, max_workers=1, hdr_inputs_by_arm=None, checkpoint_dir=None,
                            token_budget_per_arm=None):
    """One gated generation→held-out/HDR scoring→JSONL pipeline; never autostarts."""
    import json
    checkpoint = None
    if checkpoint_dir is not None:
        directory = Path(checkpoint_dir)
        directory.mkdir(parents=True, exist_ok=True)
        checkpoint = directory / f'{digest(input_set_id)[:16]}_generation_envelope.json'
    if checkpoint is not None and checkpoint.exists():
        saved_generation = json.loads(checkpoint.read_text())
        if (saved_generation.get('context_sha256') != context.context_sha256
                or saved_generation.get('checkpoint_sha256') != digest({k: v for k, v in saved_generation.items() if k != 'checkpoint_sha256'})):
            raise ValueError('generation checkpoint content/source changed')
        envelope = saved_generation['envelope']
        require_final_authorization(context, envelope)
        if token_budget_per_arm is not None and token_budget_per_arm != envelope.get('token_budget_configuration', {}).get('tokens_per_arm'):
            raise ValueError('generation checkpoint cap differs from requested cap')
        if envelope.get('model_configuration') != generation_client.model_configuration:
            raise ValueError('generation checkpoint model/decoding changed')
    else:
        envelope = run_train_generation(context, input_set_id, settings, generation_client,
                                        token_budget_per_arm=token_budget_per_arm)
        if envelope.get('experiment_status') == 'blocked':
            return {'status': 'blocked', 'generation_envelope': envelope}
        if checkpoint is not None:
            saved_generation = {'context_sha256': context.context_sha256, 'envelope': envelope}
            saved_generation['checkpoint_sha256'] = digest(saved_generation)
            with checkpoint.open('x') as handle: json.dump(saved_generation, handle, ensure_ascii=False, sort_keys=True)
    result = evaluate_train_envelope(context, envelope, prediction_policy, batch_size=batch_size,
        max_workers=max_workers, hdr_inputs_by_arm=hdr_inputs_by_arm, checkpoint_dir=checkpoint_dir)
    return {'status': result['evaluation_status'], 'generation_envelope': envelope, 'evaluation': result}
