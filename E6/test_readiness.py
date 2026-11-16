"""Offline, fail-closed pre-TEST gates and complete seven-arm schedule.

Never constructs a model client. Frozen files and prior runs are read-only.
An unresolved TRAIN set is a terminal missing unit, never a generation job.
"""
import argparse
import json
from pathlib import Path

from evaluation import ARMS
from researcher_approval import ROOT, digest, file_digest, load_approval_errors, safe_path
from validate_protocol import validate_config, validate_preregistration_git_commit
from development_runtime_probe import validate_runtime_evidence
from inductive_execution import (prepare_train_execution_context, validate_frozen_train_context,
                                require_final_authorization, bound_hdr_score)
from literature_execution import prepare_literature_execution_context, validate_frozen_literature_context
from execution_preparation import export_generation_records


def read(root, path):
    return json.loads(safe_path(root, path).read_text())


def checked_checkpoint(saved, context):
    if saved.get('checkpoint_sha256') != digest({k:v for k,v in saved.items() if k != 'checkpoint_sha256'}):
        raise ValueError('generation checkpoint checksum mismatch')
    if saved.get('context_sha256') != context.context_sha256:
        raise ValueError('generation checkpoint context mismatch')
    envelope = saved['envelope']
    if set(envelope.get('arms', {})) != set(ARMS):
        raise ValueError('generation checkpoint must retain all seven arms, including failures')
    return envelope


def required_evidence_gates(path, *, root=ROOT):
    """Consume source packets without mistaking pending forms for reviews/scores."""
    from prepare_required_evidence import validate_bundle
    bundle = validate_bundle(path, root=root)
    return {key: bundle[key] for key in (
        'literature_source_records_complete', 'literature_fixed_model_extractions_complete',
        'HDR_inputs_complete', 'HDR_inputs_required', 'scoring_ready', 'blockers')}


def literature_evidence_gates(path, *, root=ROOT):
    from finalize_literature_evidence import verify_bundle
    bundle = verify_bundle(path, root=root)
    return {key: bundle[key] for key in ('verified_extractions', 'review_packets_completed',
        'human_reviews_completed', 'human_reviews_required', 'annotations_usable', 'review_bundle_paths', 'blockers')}


DEFERRED_FOR_ACCURACY = frozenset({
    'validation_reconstruction', 'validation_already_asked', 'validation_diversity',
    'validation_question_type', 'literature_source_reviews', 'grounded_HDR_inputs',
    'literature_frozen_sources_and_donors', 'rubric_similarity', 'rubric_same_question',
    'rubric_distinctness', 'rubric_question_type',
})


def gate_required_for_phase(name, phase):
    if phase not in ('full', 'heldout_accuracy'):
        raise ValueError('explicit supported evaluation phase required')
    return phase == 'full' or name not in DEFERRED_FOR_ACCURACY


def readiness(root=ROOT, *, hdr_inputs=None, evidence_bundle=None, literature_components=None,
              literature_evidence=None, phase='full'):
    gate_required_for_phase('frozen_protocol', phase)
    root = Path(root)
    config = read(root, 'E6/config.json')
    evaluation = read(root, 'E6/evaluation_config.json')
    approval = read(root, 'E6/RESEARCHER_APPROVAL.json')
    blockers = []
    deferred = []
    gates = {}
    source_evidence = None
    completed_literature = None
    def gate(name, check):
        if not gate_required_for_phase(name, phase):
            gates[name] = 'DEFERRED_NOT_USED_IN_THIS_PHASE'
            deferred.append(name)
            return
        try:
            errors = check() or []
            if errors: raise ValueError('; '.join(errors))
            gates[name] = 'PASS'
        except (ValueError, OSError, KeyError, TypeError) as exc:
            gates[name] = 'BLOCKED'
            blockers.append({'gate': name, 'reason': str(exc)})
    if evidence_bundle is not None and phase == 'full':
        source_evidence = required_evidence_gates(evidence_bundle, root=root)
        gate('prepared_source_evidence_integrity', lambda: [])
        gate('prepared_evidence_scoring_completion', lambda: source_evidence['blockers'])
    literature_evidence = literature_evidence or root / 'E6/data/literature_evidence_finalized_v1/evidence_bundle.json'
    if phase == 'full' and Path(literature_evidence).exists():
        completed_literature = literature_evidence_gates(literature_evidence, root=root)
        gate('literature_extractions_and_review_packets_verified', lambda: [])
    gate('frozen_protocol', lambda: validate_config(config, (root/'E6/protocol.md').read_text(), root=root))
    gate('researcher_approval', lambda: load_approval_errors(root, finalization=True))
    gate('exact_runtime_evidence', lambda: validate_runtime_evidence(config, root=root))
    gate('committed_preregistration', lambda: validate_preregistration_git_commit(root))
    gate('seven_arms', lambda: [] if set(config['arms']) == set(ARMS) else ['seven-arm configuration mismatch'])
    for section in ('reconstruction', 'already_asked', 'diversity', 'question_type'):
        gate('validation_' + section, lambda section=section: [] if evaluation[section].get('validation_status') == 'validated'
             else ['Actual evaluator validation is required; frozen status: ' + str(evaluation[section].get('validation_status'))])
    def review():
        from literature_finalization import validate_review_bundle
        paths = evaluation['reconstruction'].get('review_bundle_paths')
        if paths is None and completed_literature is not None:
            paths = completed_literature['review_bundle_paths']
        keys = {'candidate','proposal','extraction_manifest','worklist','records','adjudications'}
        if not isinstance(paths, dict) or set(paths) != keys:
            raise ValueError('Missing source-bound extraction and actual review/adjudication bundle (Decision 24)')
        result = validate_review_bundle(**{k:read(root,v) for k,v in paths.items()}, approval=approval, root=root)
        if not result['annotations_usable']: raise ValueError('Source annotations not usable')
        from literature_source_components import validate_component_reviews
        component_path = literature_components or root / 'E6/data/literature_source_components_actual.json'
        sidecars = json.loads(Path(component_path).read_text())
        manifest = read(root, paths['extraction_manifest'])
        worklist = read(root, paths['worklist'])
        validate_component_reviews(manifest['target_extractions'], sidecars,
                                   read(root, paths['records']), worklist['selected_input_set_ids'])
    gate('literature_source_reviews', review)
    for name, binding in evaluation['configured_rubrics'].items():
        gate('rubric_' + name, lambda binding=binding: [] if file_digest(safe_path(root,binding['path'])) == binding['file_sha256'] else ['rubric hash mismatch'])
    proposal = read(root, config['dataset']['data_generation_proposal'])
    manifest = read(root, config['dataset']['data_evaluation_manifest'])
    context = prepare_train_execution_context(proposal, manifest)
    gate('TRAIN_TEST_sources_and_isolation', lambda: validate_frozen_train_context(context, config, root=root))
    lit_context = None
    if phase == 'full':
        literature = read(root, 'E6/literature_testbed_config.json')
        lit_context = prepare_literature_execution_context(read(root,literature['candidate_manifest']['path']),
            read(root,'E6/data/literature_sample_proposal_v1.json'),
            read(root,config['dataset']['literature_reference_selection_proposal']),
            task=config['dataset']['task_text_by_testbed']['literature'])
    gate('literature_frozen_sources_and_donors', lambda: validate_frozen_literature_context(lit_context,config,root=root))
    checkpoints = {}
    preserved = {}
    # Preserve histories as well as successful and partial-failure checkpoints.
    for directory in sorted((root/'E6/runs').glob('priority10_train*')):
        for path in sorted(directory.rglob('*')):
            if path.is_file() and path.suffix in ('.json','.jsonl'):
                relative = str(path.relative_to(root))
                preserved[relative] = file_digest(path)
                if path.name.endswith('_generation_envelope.json'):
                    saved = json.loads(path.read_text())
                    envelope = checked_checkpoint(saved, context)
                    unit = envelope['paper_id']
                    if unit in checkpoints: raise ValueError('duplicate TRAIN checkpoint: ' + unit)
                    require_final_authorization(context, envelope)
                    export_generation_records(envelope, testbed='data',seed=config['generation']['seed'])
                    checkpoints[unit] = (relative,envelope)
    jobs, hdr_worklist = [], []
    missing = []
    for row in context.inputs:
        unresolved = ':TRAIN-SET:0007:' in row.paper_id
        checkpoint, envelope = checkpoints.get(row.paper_id, (None,None))
        if unresolved and checkpoint: raise ValueError('0007 unexpectedly has a checkpoint; manual reconciliation required')
        if not unresolved and envelope is None: missing.append(row.paper_id)
        for arm in ARMS:
            entry = envelope['arms'][arm] if envelope else {}
            succeeded = entry.get('execution_status') == 'succeeded'
            job = {'testbed':'data','input_set_id':row.paper_id,'arm':arm,'generation_checkpoint':checkpoint,
                   'status':'ready_generation' if succeeded else 'terminal_missing_generation',
                   'generation_retry_allowed':False,'TEST_denominator':501,'prediction_output_tokens':32,
                   'recovery_output_tokens':512,'metrics':['TEST_accuracy'] if phase == 'heldout_accuracy' else ['TEST_accuracy','planted_recovery','HDR','diversity','question_type','already_asked'],
                   'already_asked_policy':'unavailable without independently supported historical cutoff'}
            if succeeded:
                hypotheses = [h['text'] for h in entry['output']['hypotheses']]
                payload = (hdr_inputs or {}).get(row.paper_id,{}).get(arm)
                result = bound_hdr_score(context,row.paper_id,arm,hypotheses,payload)
                if result['status'] != 'scored':
                    hdr_worklist.append({'generation_input_set_id':row.paper_id,'arm':arm,
                        'hypotheses_sha256':digest(hypotheses), 'hypotheses':hypotheses,
                        'ground_truth_source_sha256':manifest['dataset_ground_truth']['source_file_sha256'],
                        'required':'source-grounded feature_mapping, reference_feature_ids, discovered_feature_ids, relationship_scores and provenance; use bound_hdr_score schema'})
            jobs.append(job)
    gate('TRAIN_terminal_inventory', lambda: ['Missing terminal checkpoints: '+str(missing)] if missing else [])
    gate('grounded_HDR_inputs', lambda: [str(len(hdr_worklist))+' evaluable arm cells lack actual grounded feature mapping/relationship judgments'] if hdr_worklist else [])
    for row in (lit_context.inputs if lit_context is not None else ()):
        for arm in ARMS:
            jobs.append({'testbed':'literature','input_set_id':row.paper_id,'arm':arm,
                         'status':'generation_required','donor_id':lit_context.donors[row.paper_id] if arm=='D-shuffled' else None,
                         'metrics':['reconstruction','same_question','already_asked','diversity','question_type'],
                         'target_text_allowed_in_generation':False})
    result = {'schema_version':'e6-pre-test-readiness-v1','model_calls':0,
              'evaluation_phase': phase, 'deferred_scoring_gates': deferred,
              'full_evaluation_ready': phase == 'full' and not blockers,
              'prepared_source_evidence': source_evidence,
              'completed_literature_evidence': completed_literature,
              'status':'BLOCKED' if blockers else 'READY', 'gates':gates,'mandatory_blockers':blockers,
              'arms':list(ARMS),'planned_independent_units':{'data':20,'literature':100},
              'TEST_observations_per_evaluable_data_cell':501,'jobs':jobs,
              'terminal_missing_units':[r.paper_id for r in context.inputs if ':TRAIN-SET:0007:' in r.paper_id],
              'hdr_worklist':hdr_worklist,'preserved_artifact_file_hashes':preserved,
              'frozen_file_hashes':{str(p.relative_to(root)):file_digest(p) for p in (root/'E6/config.json', root/'E6/evaluation_config.json', root/'E6/PREREG.md')},
              'execution_policy':'No TEST execution until all mandatory gates pass. Never regenerate TRAIN; failed cells remain missing. New implementation must be committed locally before execution.'}
    result['manifest_sha256'] = digest(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--phase',choices=('full','heldout_accuracy'),default='full')
    parser.add_argument('--hdr-inputs',type=Path)
    parser.add_argument('--hdr-compilation',type=Path,
                        help='source-bound HDR compiler output; missing judgments remain blocked')
    parser.add_argument('--evidence-bundle',type=Path,
                        help='verify prepared sources; pending forms never pass scoring gates')
    parser.add_argument('--literature-components',type=Path,
                        help='actual attributed source-component sidecars for Decision 24')
    parser.add_argument('--literature-evidence',type=Path,
                        help='verified completed extraction/review packet bundle; never substitutes for human reviews')
    args = parser.parse_args()
    if args.hdr_inputs and args.hdr_compilation:
        parser.error('select --hdr-inputs or --hdr-compilation, not both')
    if args.hdr_compilation:
        from hdr_pipeline import load_compilation
        hdr_inputs = load_compilation(args.hdr_compilation)
    else:
        hdr_inputs = json.loads(args.hdr_inputs.read_text()) if args.hdr_inputs else None
    result = readiness(hdr_inputs=hdr_inputs,
                       evidence_bundle=args.evidence_bundle, literature_components=args.literature_components,
                       literature_evidence=args.literature_evidence, phase=args.phase)
    # Exclusive output preserves every previous readiness record.
    with args.output.open('x') as handle: json.dump(result,handle,indent=2,sort_keys=True)
    print(json.dumps({k:result[k] for k in ('status','model_calls','gates','mandatory_blockers')},indent=2))
    print('Schedule:',len(result['jobs']),'arm cells; HDR worklist:',len(result['hdr_worklist']))
    return 2 if result['status']=='BLOCKED' else 0

if __name__ == '__main__':
    raise SystemExit(main())
