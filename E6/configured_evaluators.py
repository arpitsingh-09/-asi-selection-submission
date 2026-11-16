"""Connect frozen evaluator configuration to existing E6 scoring interfaces.

Construction is offline. Every scoring entry point checks existing execution,
approval, runtime and Git gates before any client call. No default corpus or
validation evidence is supplied here.
"""
from copy import deepcopy
import json
from pathlib import Path

from evaluation import (EvaluationError, _hash_json, _render, _unpack_model_reply,
                        evaluate_literature_seven_arm_outputs,
                        evaluate_k6_hypothesis_diversity, classify_question, evaluation_record)
from hypobench_policies import _strict_json_object
from researcher_approval import ROOT, file_digest, safe_path, validate_approval_record


class ConfiguredEvaluators:
    def __init__(self, config, evaluation_config, approval, model_client, *, root=ROOT):
        self.config = deepcopy(config)
        self.evaluation = deepcopy(evaluation_config)
        self.approval = deepcopy(approval)
        self.client = model_client
        self.root = Path(root)
        self.calls = []

    def _require_execution(self, decision, section):
        from validate_protocol import validate_config, validate_preregistration_git_commit
        from development_runtime_probe import validate_runtime_evidence
        errors = validate_approval_record(self.approval, root=self.root,
                                          required_ids={decision}, finalization=True)
        errors += validate_config(self.config, (self.root / 'E6/protocol.md').read_text(), root=self.root)
        errors += validate_runtime_evidence(self.config, root=self.root)
        errors += validate_preregistration_git_commit(self.root)
        # The passed copies must be the current committed/signable configuration.
        for name, value in (('config.json', self.config), ('evaluation_config.json', self.evaluation),
                            ('RESEARCHER_APPROVAL.json', self.approval)):
            if json.loads((self.root / 'E6' / name).read_text()) != value:
                errors.append('evaluator configuration differs from frozen artifact: ' + name)
        if self.evaluation[section].get('validation_status') != 'validated':
            errors.append(section + ': actual evaluator validation is required before scoring')
        gen = self.config['generation']
        options = getattr(self.client, 'generation_options', {})
        if (getattr(self.client, 'model', None) != gen['model']
                or any(options.get(k) != gen[k] for k in ('temperature', 'top_p', 'seed'))
                or options.get('num_ctx') != gen['context_limit']
                or not callable(getattr(self.client, 'call_with_token_limit', None))):
            errors.append('evaluator client does not match approved model/decoding/context')
        if errors:
            raise EvaluationError('; '.join(errors))

    def _prompt(self, rubric):
        binding = self.evaluation['configured_rubrics'][rubric]
        path = safe_path(self.root, binding['path'])
        if file_digest(path) != binding['file_sha256']:
            raise EvaluationError('evaluator rubric hash mismatch: ' + rubric)
        return path.read_text()

    def _reply(self, stage, prompt):
        reply = self.client.call_with_token_limit(stage, prompt,
            max_output_tokens=self.config['generation']['max_output_tokens'])
        raw, metadata = _unpack_model_reply(reply)
        self.calls.append({'stage': stage, 'prompt': prompt, 'prompt_sha256': _hash_json(prompt),
                           'raw_output': raw, 'model_metadata': metadata})
        return reply

    def _scalar(self, rubric, values, key):
        prompt = _render(self._prompt(rubric), values)
        raw, _ = _unpack_model_reply(self._reply(rubric, prompt))
        result = _strict_json_object(raw)
        if set(result) != {key}:
            raise EvaluationError('evaluator reply must contain exactly ' + key)
        value = result[key]
        if key == 'similarity':
            if type(value) is not int or not 1 <= value <= 5:
                raise EvaluationError('similarity must be an integer from 1 through 5')
        elif type(value) is not bool:
            raise EvaluationError(key + ' is unavailable or is not Boolean; no numeric substitution')
        return value

    def score_literature(self, input_set_id, arm_outputs):
        self._require_execution(19, 'reconstruction')
        from literature_finalization import validate_review_bundle
        paths = self.evaluation['reconstruction'].get('review_bundle_paths')
        if not isinstance(paths, dict):
            raise EvaluationError('actual source-bound extraction/review bundle is required')
        keys = ('candidate', 'proposal', 'extraction_manifest', 'worklist', 'records', 'adjudications')
        if set(paths) != set(keys):
            raise EvaluationError('review bundle requires the six original source/review artifacts')
        bundle = {k: json.loads(safe_path(self.root, paths[k]).read_text()) for k in keys}
        review = validate_review_bundle(**bundle, approval=self.approval, root=self.root)
        if not review['annotations_usable']:
            raise EvaluationError('review corrections and renewed checks required before scoring')
        rows = bundle['extraction_manifest']['target_extractions']
        source = next((r for r in rows if r['input_set_id'] == input_set_id), None)
        if source is None:
            raise EvaluationError('literature target is outside the source-bound extraction manifest')
        start = len(self.calls)
        result = evaluate_literature_seven_arm_outputs(input_set_id, arm_outputs,
            source['target_extraction'],
            similarity_evaluator=lambda a, b: self._scalar('similarity',
                {'FIELD': 'research question or hypothesis', 'GENERATED': a, 'TARGET': b}, 'similarity'),
            same_question_evaluator=lambda a, b: self._scalar('same_question',
                {'TYPE_A': 'generated research question', 'TEXT_A': a,
                 'TYPE_B': 'source research question', 'TEXT_B': b}, 'same_question'),
            similarity_policy_id='e6-configured-similarity-v1',
            same_question_policy_id='e6-configured-same-question-v1',
            reference_provenance={'review_validation_sha256': review['manifest_sha256'],
                                  'source_record_sha256': _hash_json(source)})
        for record in result['records']:
            if record['stage'] == 'same_question_judgment':
                decisions = record.get('parsed_output')
                complete = (record['status'] == 'succeeded' and isinstance(decisions, list)
                            and bool(decisions) and all(type(d.get('same_question')) is bool
                                                       for d in decisions))
                planned = len(record['evaluation_input'].get('generated_questions', []))
                record['analysis_summary'] = {
                    'same_question_fraction': sum(d['same_question'] for d in decisions) / len(decisions)
                        if complete else None,
                    'included_denominator': len(decisions) if complete else 0,
                    'planned_denominator': planned,
                    'missing_policy': 'null unless all candidate judgments succeed'}
        result['configured_evaluator_calls'] = self.calls[start:]
        result['bundle_sha256'] = _hash_json({k: v for k, v in result.items() if k != 'bundle_sha256'})
        return result

    def score_diversity(self, input_set_id, hypotheses):
        self._require_execution(21, 'diversity')
        start = len(self.calls)
        result = evaluate_k6_hypothesis_diversity(input_set_id, hypotheses,
            lambda a, b: self._scalar('distinctness', {'HYPOTHESIS_A': a, 'HYPOTHESIS_B': b}, 'distinct'),
            lambda pairs: sum(p['distinct'] for p in pairs) / 15,
            policy_id='e6-configured-distinct-pair-proportion-v1',
            provenance={'rubric': self.evaluation['configured_rubrics']['distinctness']})
        result['configured_evaluator_calls'] = self.calls[start:]
        return result

    def score_question_type(self, input_set_id, question_id, question):
        self._require_execution(22, 'question_type')
        # The existing classifier owns the prompt; verify the same frozen file.
        self._prompt('question_type')
        return classify_question(input_set_id, question_id, question, self._reply,
            model_configuration={'model': self.config['generation']['model'],
                'generation_options': dict(self.client.generation_options)})

    def score_already_asked(self, input_set_id, generated_questions, matcher=None, *, evaluation_cutoff=None):
        self._require_execution(20, 'already_asked')
        from evaluation import evaluate_already_asked_rate
        from literature_finalization import verify_seal
        policy = self.evaluation['already_asked']
        # A source-supported historical cutoff is required for a TRAIN evidence
        # set. Approved abstention is an unavailable record, never a zero rate.
        if ':TRAIN-SET:' in input_set_id:
            from prior_question_corpus import precise_date
            generation_path = self.config['dataset']['data_generation_proposal']
            proposal_path = safe_path(self.root, generation_path)
            if file_digest(proposal_path) != self.config['dataset']['manifest_sha256']['data']:
                raise EvaluationError('HypoBench generation source hash mismatch')
            proposal = json.loads(proposal_path.read_text())
            if input_set_id not in {r['input_set_id'] for r in proposal['input_sets']}:
                raise EvaluationError('unknown HypoBench generation evidence set')
            expected = policy.get('evaluation_cutoffs_by_input_set', {}).get(input_set_id)
            proof = policy.get('hypobench_cutoff_evidence_by_input_set', {}).get(input_set_id)
            reason = 'no independently supported HypoBench historical cutoff'
            supported = False
            if expected and isinstance(proof, dict):
                try:
                    source_path = safe_path(self.root, proof['path'])
                    if file_digest(source_path) != proof['file_sha256'] or proof.get('independently_supported') is not True:
                        raise ValueError('cutoff provenance is not independently supported/hash-bound')
                    native = json.loads(source_path.read_text())
                    for key in proof['source_value_path']:
                        native = native[key]
                    precise_date(native)
                    if native != expected:
                        raise ValueError('historical cutoff differs from original source evidence')
                    supported = True
                except (ValueError, KeyError, TypeError, OSError) as exc:
                    reason += ': ' + str(exc)
            if not supported:
                return evaluation_record(stage='already_asked_rate', input_set_id=input_set_id,
                    evaluation_input={'generated_questions': deepcopy(generated_questions),
                                      'provided_cutoff': evaluation_cutoff},
                    provenance={'testbed': 'data', 'historical_cutoff_status': 'unavailable',
                                'planned_denominator': len(generated_questions),
                                'eligible_denominator': None, 'policy': 'Decision20 approved abstention'},
                    status='blocked', error=reason, parsed_output=None)
        binding = policy.get('reference_question_corpus')
        if not isinstance(binding, dict):
            raise EvaluationError('genuine independently sourced question corpus is absent')
        path = safe_path(self.root, binding['path'])
        if file_digest(path) != binding['file_sha256']:
            raise EvaluationError('prior-question corpus file hash mismatch')
        corpus = json.loads(path.read_text())
        verify_seal(corpus)
        questions = corpus.get('questions', [])
        if (corpus.get('corpus_frozen') is not True
                or corpus.get('independently_sourced') is not True or not questions
                or any(not r.get('source_records') or not isinstance(r.get('question'), str)
                       or not r['question'].strip() for r in questions)):
            raise EvaluationError('corpus is empty, unfrozen or lacks independent question provenance')
        identity = policy.get('semantic_matcher')
        if corpus.get('schema_version') in ('e6-temporal-prior-question-corpus-v1', 'e6-reviewed-temporal-prior-question-corpus-v1'):
            if corpus['schema_version'] == 'e6-reviewed-temporal-prior-question-corpus-v1':
                from prior_question_expansion import validate_reviewed_corpus as validate_corpus, make_temporal_matcher
            else:
                from prior_question_corpus import validate_corpus, make_temporal_matcher
            validate_corpus(corpus, root=self.root)
            expected_cutoff = policy.get('evaluation_cutoffs_by_input_set', {}).get(input_set_id)
            if evaluation_cutoff is None:
                evaluation_cutoff = expected_cutoff
            if not expected_cutoff or evaluation_cutoff != expected_cutoff:
                raise EvaluationError('explicit per-input-set evaluation cutoff must match frozen configuration')
            if not isinstance(identity, dict):
                raise EvaluationError('semantic identity and candidate-limit policy still require approval')
            connected = make_temporal_matcher(corpus, evaluation_cutoff=evaluation_cutoff,
                candidate_limit=identity.get('candidate_limit'),
                identity_policy_id=identity.get('identity_policy_id'), root=self.root,
                identity_evaluator=lambda a,b: self._scalar('same_question',
                    {'TYPE_A':'generated research question','TEXT_A':a,
                     'TYPE_B':'historical source research question','TEXT_B':b}, 'same_question'))
            expected_identity = dict(connected.policy_identity)
            if identity != {k:v for k,v in expected_identity.items() if k != 'evaluation_cutoff'}:
                raise EvaluationError('temporal matcher differs from approved corpus/retrieval/identity policy')
            if matcher is None:
                matcher = connected
            elif getattr(matcher, 'policy_identity', None) != expected_identity:
                raise EvaluationError('supplied semantic matcher differs from approved temporal identity')
        elif not identity or getattr(matcher, 'policy_identity', None) != identity:
            raise EvaluationError('explicit approved prior-question matcher is unresolved or mismatched')
        start = len(self.calls)
        result = evaluate_already_asked_rate(input_set_id, generated_questions,
            [r['question'] for r in questions], matcher,
            denominator_policy_id=policy.get('denominator_and_missing_reference_policy'),
            provenance={'corpus_file_sha256': binding['file_sha256'], 'matcher_identity': getattr(matcher, 'policy_identity', identity),
                        'evaluation_cutoff': evaluation_cutoff})
        result['candidate_retrieval_and_judgments'] = list(getattr(matcher, 'attempts', []))
        result['configured_evaluator_calls'] = self.calls[start:]
        return result
