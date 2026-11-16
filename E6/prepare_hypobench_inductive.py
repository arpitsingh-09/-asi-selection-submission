"""TRAIN-only hypothesis-generation proposals; TEST remains evaluation-only.

No model is constructed or called. Sampling parameters are supplied explicitly;
prepared proposals never authorize execution or freeze a methodology.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from collections import Counter
from prepare_hypobench_testbed import (
    DEFAULT_DATASET_DIR, DATASET_ID, SPLIT_FILES, _columnar_rows,
    to_orchestrator_inputs, prepare_hypobench_evaluation_input, prepare_hypobench_election_level2_testbed,
    score_hypobench_testbed_predictions,
)
from orchestrator import ExperimentInput
from researcher_approval import digest, file_digest


def prepare_inductive_proposal(test_manifest, *, input_set_count, observations_per_set, seed,
                               dataset_dir=DEFAULT_DATASET_DIR):
    if any(type(v) is not int or v < 1 for v in (input_set_count, observations_per_set)) or type(seed) is not int or seed < 0:
        raise ValueError('explicit positive input-set count/size and nonnegative seed required')
    # Validate original TEST source mapping, without exposing it to generation.
    to_orchestrator_inputs(test_manifest)
    root = Path(dataset_dir)
    if test_manifest != prepare_hypobench_election_level2_testbed(root):
        raise ValueError('evaluation manifest differs from actual protected source splits')
    train_file = root / SPLIT_FILES['TRAIN']
    rows = _columnar_rows(json.loads(train_file.read_text()), split='TRAIN')
    if file_digest(root / SPLIT_FILES['TEST']) != test_manifest['provenance']['source_split_sha256']:
        raise ValueError('TEST source differs from preserved evaluation manifest')
    source_sha = file_digest(train_file)
    if source_sha != test_manifest['provenance']['split_file_hashes']['TRAIN']:
        raise ValueError('TRAIN source differs from preserved benchmark split')
    if input_set_count * observations_per_set > len(rows):
        raise ValueError('requested non-overlapping evidence sets exceed TRAIN size')
    test_texts = {row['evidence'] for row in test_manifest['records']}
    if any(row['text'] in test_texts for row in rows):
        raise ValueError('TRAIN/TEST observation overlap')
    ranked = sorted(range(len(rows)), key=lambda i: (
        hashlib.sha256(f'E6-TRAIN-COHORT-v1|{seed}|{i}|{digest(rows[i])}'.encode()).hexdigest(), i))
    sets = []
    for index in range(input_set_count):
        indices = ranked[index * observations_per_set:(index + 1) * observations_per_set]
        # TRAIN labels are observed outcomes, unlike held-out TEST labels.
        observations = [{'source_row_index': i, 'source_record_sha256': digest(rows[i]),
                         'text': rows[i]['text'], 'observed_training_label': rows[i]['label']} for i in indices]
        identity = digest({'source_sha256': source_sha, 'indices': indices, 'seed': seed})
        sets.append({'input_set_id': f'{DATASET_ID}:TRAIN-SET:{index:04d}:{identity[:12]}',
                     'observations': observations})
    value = {'schema_version': 'e6-hypobench-inductive-proposal-v1',
             'status': 'pending_researcher_approval', 'frozen': False,
             'dataset_id': DATASET_ID, 'generation_split': 'TRAIN', 'evaluation_split': 'TEST',
             'task_description': test_manifest['task_description'],
             'input_set_count': input_set_count, 'observations_per_set': observations_per_set,
             'seed': seed, 'sampling': 'sha256-ranked TRAIN rows, disjoint fixed-size chunks, no stratification',
             'training_source_sha256': source_sha, 'training_source_path': str(train_file),
             'evaluation_manifest_sha256': test_manifest['manifest_sha256'],
             'evaluation_row_count': test_manifest['record_count'],
             'declared_label_classes': test_manifest['declared_label_classes'],
             'observed_training_label_counts': dict(Counter(row['label'] for row in rows)),
             'training_labels_are_observed_evidence': True,
             'test_observations_and_labels_available_to_generation': False,
             'hypotheses_reused_unchanged_across_test_rows': True,
             'statistical_unit': 'TRAIN evidence input set; shared TEST rows are not independent replications',
             'input_sets': sets,
             'prediction_calls_if_one_call_per_test_row': input_set_count * 7 * test_manifest['record_count']}
    return dict(value, manifest_sha256=digest(value))


def validate_inductive_proposal(proposal, test_manifest, *, dataset_dir=DEFAULT_DATASET_DIR):
    expected = prepare_inductive_proposal(test_manifest,
        input_set_count=proposal.get('input_set_count'), observations_per_set=proposal.get('observations_per_set'),
        seed=proposal.get('seed'), dataset_dir=dataset_dir)
    if proposal != expected:
        raise ValueError('inductive proposal differs from source rows, policy or evaluation manifest')


def inductive_generation_inputs(proposal, test_manifest, *, dataset_dir=DEFAULT_DATASET_DIR):
    validate_inductive_proposal(proposal, test_manifest, dataset_dir=dataset_dir)
    return [ExperimentInput(
        paper_id=row['input_set_id'], domain_and_task=proposal['task_description'],
        evidence=json.dumps([{'text': r['text'], 'observed_training_label': r['observed_training_label']}
                             for r in row['observations']], ensure_ascii=False),
        split='TRAIN', reference_evidence=(), provenance={'dataset_id': DATASET_ID, 'evidence_split': 'TRAIN',
            'proposal_sha256': proposal['manifest_sha256'], 'sampling_status': 'unapproved',
            'source_row_ids': [r['source_row_index'] for r in row['observations']],
            'source_split_sha256': proposal['training_source_sha256']}) for row in proposal['input_sets']]


def heldout_prediction_jobs(proposal, test_manifest, generation_input_set_id, hypotheses, *, dataset_dir=DEFAULT_DATASET_DIR):
    """Prepare label-blind jobs with the SAME six hypotheses for every TEST row."""
    validate_inductive_proposal(proposal, test_manifest, dataset_dir=dataset_dir)
    if generation_input_set_id not in {r['input_set_id'] for r in proposal['input_sets']}:
        raise ValueError('unknown generation input-set ID')
    if not isinstance(hypotheses, list) or len(hypotheses) != 6 or any(not isinstance(h, str) or not h.strip() for h in hypotheses):
        raise ValueError('exactly six fixed hypotheses required')
    from evaluation import prepare_hypobench_data_explanation_input
    # The manifest/source were validated once above. Avoid hashing the entire
    # TEST manifest again for each of its 501 rows.
    for row in test_manifest['records']:
        prepared = prepare_hypobench_data_explanation_input(
            row['input_set_id'], {'task': test_manifest['task_description'], 'observation': row['evidence']},
            list(hypotheses), dataset_id=test_manifest['dataset_id'], split='TEST',
            dataset_provenance={'manifest_sha256': test_manifest['manifest_sha256'],
                                'source_record_sha256': row['source_record_sha256'],
                                'generation_input_set_id': generation_input_set_id})
        yield {'generation_input_set_id': generation_input_set_id, 'evaluation_row_id': row['input_set_id'],
               'prepared_input': prepared}


def score_inductive_predictions(proposal, test_manifest, generation_input_set_id, arm, predictions, *, dataset_dir=DEFAULT_DATASET_DIR):
    """Score a fixed hypothesis set on all 501 TEST outcomes, not just its source row."""
    from evaluation import ARMS
    validate_inductive_proposal(proposal, test_manifest, dataset_dir=dataset_dir)
    if generation_input_set_id not in {row['input_set_id'] for row in proposal['input_sets']}:
        raise ValueError('unknown generation evidence set')
    if arm not in ARMS or not isinstance(generation_input_set_id, str) or ':TRAIN-SET:' not in generation_input_set_id:
        raise ValueError('TRAIN evidence-set ID and known arm required')
    # Each record names the cohort and arm to prevent pooling different generated sets.
    if any(r.get('generation_input_set_id') != generation_input_set_id or r.get('arm') != arm for r in predictions):
        raise ValueError('predictions mix generation cohorts or arms')
    result = score_hypobench_testbed_predictions(test_manifest, predictions)
    return {'generation_input_set_id': generation_input_set_id, 'arm': arm,
            'evaluation_row_count': test_manifest['record_count'], 'heldout_accuracy': result,
            'statistical_unit': 'generation evidence input set'}


def score_reference_hdr(reference_feature_ids, discovered_feature_ids, relationship_scores, *, provenance):
    """R44 HDR = feature discovery rate * mean relationship correctness.

    Reference features and judge scores must be real, provenance-bound inputs.
    The source's fourteen text hypotheses are NOT automatically fourteen features.
    """
    import math
    if (not isinstance(reference_feature_ids, list) or not reference_feature_ids
            or any(not isinstance(v, str) or not v.strip() for v in reference_feature_ids)
            or len(set(reference_feature_ids)) != len(reference_feature_ids)):
        raise ValueError('explicit unique source-grounded reference feature IDs required')
    if (not isinstance(discovered_feature_ids, list)
            or any(not isinstance(v, str) or not v.strip() for v in discovered_feature_ids)
            or len(set(discovered_feature_ids)) != len(discovered_feature_ids)):
        raise ValueError('explicit unique discovered feature IDs required')
    matched = sorted(set(reference_feature_ids) & set(discovered_feature_ids))
    if not isinstance(relationship_scores, dict) or set(relationship_scores) != set(matched):
        raise ValueError('relationship scores required for exactly the matched features')
    if any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1 for v in relationship_scores.values()):
        raise ValueError('relationship correctness must be finite scores in [0,1]')
    if (not isinstance(provenance, dict) or any(not provenance.get(key) for key in (
            'ground_truth_source_sha256', 'feature_mapping_sha256', 'judge_provenance'))):
        raise ValueError('ground-truth, feature-mapping and judge provenance required; cannot fabricate HDR')
    fdr = len(matched) / len(reference_feature_ids)
    rc = sum(relationship_scores.values()) / len(matched) if matched else 0.0
    return {'feature_discovery_rate': fdr, 'relationship_correctness': rc,
            'hypothesis_discovery_rate': fdr * rc, 'matched_feature_ids': matched,
            'provenance': provenance, 'not_equivalent_to': '14-reference hypothesis recall'}


def main():
    import argparse
    from prepare_literature_testbed import write_manifest_exclusive
    parser = argparse.ArgumentParser(description='Prepare TRAIN-only E6 proposal, no inference or freeze')
    parser.add_argument('--test-manifest', type=Path, default=Path(__file__).parent / 'data/hypobench_election_level2_test_manifest_v1.json')
    parser.add_argument('--input-set-count', type=int, required=True)
    parser.add_argument('--observations-per-set', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        proposal = prepare_inductive_proposal(json.loads(args.test_manifest.read_text()),
            input_set_count=args.input_set_count, observations_per_set=args.observations_per_set, seed=args.seed)
        write_manifest_exclusive(args.output, proposal)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps({'status': proposal['status'], 'manifest_sha256': proposal['manifest_sha256'],
                      'input_set_count': proposal['input_set_count'], 'inference_executed': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
