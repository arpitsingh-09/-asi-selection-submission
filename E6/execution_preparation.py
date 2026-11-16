"""Priority 10 offline execution planning and mandatory JSONL export.

No model client is constructed, inference is never enabled, and output files use
exclusive creation. Scientific choices must already be supplied by the caller.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from evaluation import ARMS
from researcher_approval import digest, file_digest, safe_path

ARM_LABELS = {'QH-sel': 'QH_sel', 'QH-rand': 'QH_rand', 'D-empty': 'D_empty', 'D-shuffled': 'D_shuffled'}


def make_configured_gemma_client(config, *, seed):
    """Construct only; unresolved choices fail and no request is sent."""
    from ollama_adapter import OllamaModelClient
    gen = config.get('generation', {})
    context, output = gen.get('context_limit'), gen.get('max_output_tokens')
    metadata_context = gen.get('verified_context_length_model_metadata')
    if (gen.get('model') != 'gemma3:12b' or type(seed) is not int or seed != gen.get('seed')
            or type(context) is not int or type(output) is not int
            or type(metadata_context) is not int or not 0 < output < context <= metadata_context
            or gen.get('temperature') is None or gen.get('top_p') is None):
        raise ValueError('explicit consistent Gemma settings required; no defaults or approval inferred')
    return OllamaModelClient(model=gen['model'], generation_options={
        'temperature': gen['temperature'], 'top_p': gen['top_p'], 'seed': seed,
        'num_ctx': context, 'num_predict': output}, preflight_context_limit=context)


def prepare_execution_plan(inputs, *, testbed, source_artifacts, seed, root):
    if testbed not in ('literature', 'data') or type(seed) is not int:
        raise ValueError('assignment testbed and explicit seed required')
    ids = [row.paper_id for row in inputs]
    if not ids or len(set(ids)) != len(ids):
        raise ValueError('nonempty unique input IDs required')
    if testbed == 'data' and any(row.split != 'TRAIN' or row.provenance.get('evidence_split') != 'TRAIN' for row in inputs):
        raise ValueError('R44 execution plan requires TRAIN evidence inputs')
    artifacts = {path: file_digest(safe_path(root, path)) for path in source_artifacts}
    if not artifacts:
        raise ValueError('source artifact hashes required')
    value = {'schema_version': 'e6-execution-plan-v1', 'status': 'preparation_only_not_authorized',
             'testbed': testbed, 'seed': seed, 'execution_authorized': False,
             'input_set_ids': ids, 'arms': list(ARMS), 'generation_cell_count': len(ids) * 7,
             'source_artifact_file_hashes': artifacts,
             'input_hashes': {row.paper_id: digest({'task': row.domain_and_task, 'evidence': row.evidence,
                                                   'references': row.reference_evidence}) for row in inputs},
             'note': 'Plans do not implement or approve arm scheduling, donors, run order or evaluation; final runtime stays blocked.'}
    return dict(value, manifest_sha256=digest(value))


def export_generation_records(envelope, *, testbed, seed):
    if testbed not in ('literature', 'data') or type(seed) is not int:
        raise ValueError('explicit assignment testbed and integer seed required')
    if not isinstance(envelope, dict) or set(envelope.get('arms', {})) != set(ARMS):
        raise ValueError('complete seven-arm envelope required')
    input_id = envelope.get('paper_id')
    if not isinstance(input_id, str) or not input_id.strip():
        raise ValueError('stable input ID required')
    model_config = envelope.get('model_configuration', {})
    actual_seed = model_config.get('generation_options', {}).get('seed')
    if type(actual_seed) is not int or actual_seed != seed:
        raise ValueError('export seed differs from actual generation configuration')
    model = model_config.get('model')
    if not isinstance(model, str) or not model.strip():
        raise ValueError('actual model identity required')
    rows, failures = [], []
    for arm in ARMS:
        entry = envelope['arms'][arm]
        output = entry.get('output')
        hypotheses = output.get('hypotheses') if isinstance(output, dict) else None
        if (entry.get('execution_status') != 'succeeded' or not isinstance(hypotheses, list)
                or len(hypotheses) != 6):
            failures.append({'input_set_id': input_id, 'testbed': testbed, 'arm': ARM_LABELS.get(arm, arm),
                             'status': entry.get('execution_status'), 'missing_output': entry.get('missing_output'),
                             'errors': entry.get('failure_information', entry.get('intermediate_artifacts', {}).get('errors', []))})
            continue
        accounting = envelope.get('token_budget_accounting', {}).get(arm, {})
        if accounting.get('budget_unit') != 'generated_tokens' or type(accounting.get('tokens_used')) is not int:
            raise ValueError('export requires exact generated-token arm accounting, not historical total-token units')
        tokens = accounting['tokens_used']
        if tokens < 0:
            raise ValueError('generated tokens must be nonnegative')
        hypothesis_ids = [item.get('hypothesis_id') for item in hypotheses if isinstance(item, dict)]
        if len(hypothesis_ids) != 6 or any(not isinstance(i, str) or not i for i in hypothesis_ids) or len(set(hypothesis_ids)) != 6:
            raise ValueError('six unique stable hypothesis IDs required')
        for item in hypotheses:
            if not isinstance(item, dict) or not isinstance(item.get('text'), str) or not item['text'].strip():
                raise ValueError('cannot export malformed hypothesis text')
            question = item.get('question_text')
            if question is not None and (not isinstance(question, str) or not question.strip()):
                raise ValueError('question must be text or null')
            rows.append({'input_set_id': input_id, 'testbed': testbed, 'arm': ARM_LABELS.get(arm, arm),
                         'rq': question, 'hypothesis': item['text'], 'tokens_generated': tokens,
                         'model': model, 'seed': seed, 'hypothesis_id': item.get('hypothesis_id'),
                         'token_accounting_scope': 'input_set_arm_workflow_total_non_additive',
                         'token_accounting_id': f'{input_id}:{arm}',
                         'note': 'Cost includes shared preparation/probes/retries and repeats across six hypothesis records; do not sum these costs.'})
    return rows, failures


def write_jsonl_exclusive(path, records):
    payload = ''.join(json.dumps(row, ensure_ascii=False, sort_keys=True, allow_nan=False) + '\n' for row in records)
    with Path(path).open('x', encoding='utf-8') as handle:
        handle.write(payload)


def main():
    parser = argparse.ArgumentParser(description='Offline mandatory E6 export; no inference')
    parser.add_argument('--envelope', type=Path, required=True)
    parser.add_argument('--testbed', choices=('literature', 'data'), required=True)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--failures-output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.resolve() == args.failures_output.resolve() or args.output.exists() or args.failures_output.exists():
            raise ValueError('distinct new output paths required')
        rows, failures = export_generation_records(json.loads(args.envelope.read_text()), testbed=args.testbed, seed=args.seed)
        write_jsonl_exclusive(args.output, rows)
        write_jsonl_exclusive(args.failures_output, failures)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps({'generations': len(rows), 'failed_cells': len(failures), 'inference_executed': False}))
    return 0


def prepare_literature_reference_proposal(candidate, sample, *, references_per_set):
    from prepare_literature_sample_proposal import verify_sample_proposal
    if type(references_per_set) is not int or references_per_set < 10:
        raise ValueError('at least ten references required')
    originals = verify_sample_proposal(candidate, sample)
    selections = []
    for row in originals:
        references = row['references'][:references_per_set]
        if len(references) != references_per_set:
            raise ValueError('insufficient source references')
        selections.append({'input_set_id': row['input_set_id'], 'candidate_record_sha256': digest(row),
                           'reference_ids': [r['paper_id'] for r in references],
                           'reference_record_hashes': [digest(r) for r in references]})
    value = {'schema_version': 'e6-literature-reference-selection-proposal-v1',
             'status': 'pending_researcher_approval', 'frozen': False,
             'sample_proposal_sha256': sample['proposal_sha256'],
             'references_per_set': references_per_set, 'selection_policy': 'first references in preserved verified manifest order',
             'note': 'Proposed evidence subset only; source candidate manifest and sample are unchanged. No BGE relevance ranking or target text supplied to generation.',
             'selections': selections}
    return dict(value, manifest_sha256=digest(value))


def literature_reference_inputs(candidate, sample, reference_proposal, *, task):
    from prepare_literature_sample_proposal import verify_sample_proposal
    from orchestrator import ExperimentInput
    if not isinstance(task, str) or not task.strip():
        raise ValueError('explicit task text required')
    if reference_proposal != prepare_literature_reference_proposal(candidate, sample,
            references_per_set=reference_proposal.get('references_per_set')):
        raise ValueError('reference selection differs from source and deterministic proposal')
    originals = verify_sample_proposal(candidate, sample)
    count = reference_proposal['references_per_set']
    return [ExperimentInput(paper_id=row['input_set_id'], domain_and_task=task,
             evidence='\n\n'.join(r['abstract'] for r in row['references'][:count]),
             reference_evidence=tuple(r['abstract'] for r in row['references'][:count]), split='EVALUATION',
             provenance={'reference_selection_proposal_sha256': reference_proposal['manifest_sha256'],
                         'status': 'pending_researcher_approval'}) for row in originals]


if __name__ == '__main__':
    raise SystemExit(main())
