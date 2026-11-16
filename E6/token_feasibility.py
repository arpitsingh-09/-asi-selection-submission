"""Offline prompt-length evidence and budget algebra; never estimates exact tokens.

Dynamic selection/retry prompts require runtime exact counting. Character/byte
counts are descriptive and cannot establish a context-fit guarantee.
"""
from __future__ import annotations
from pathlib import Path
from question_pipeline import _read_prompt, _render, _control_prompt
from researcher_approval import digest


def build_token_feasibility(inputs, *, generated_cap, per_call_output_limit, context_limit,
                            metadata_context_limit):
    if any(type(v) is not int or v < 1 for v in (generated_cap, per_call_output_limit, context_limit, metadata_context_limit)):
        raise ValueError('explicit positive token/context limits required')
    if context_limit > metadata_context_limit:
        raise ValueError('proposed context exceeds verified model metadata')
    records = []
    for row in inputs:
        prompts = {}
        for arm, filename in [('D', '01_generator_D.txt'), ('QH', '02_generator_QH.txt'), ('HQ', '05_generator_HQ.txt')]:
            prompts[arm] = _render(_read_prompt('prompts/e6/' + filename), DOMAIN_AND_TASK=row.domain_and_task, EVIDENCE=row.evidence)
        prompts['candidate_generation'] = _render(_read_prompt('prompts/e6/07_question_candidate_generation.txt'),
            N_QUESTIONS='6', DOMAIN_AND_TASK=row.domain_and_task, EVIDENCE=row.evidence)
        prompts['D-empty'] = _control_prompt('D-empty', row.domain_and_task, '')
        for stage, prompt in prompts.items():
            records.append({'input_set_id': row.paper_id, 'stage': stage,
                            'characters': len(prompt), 'utf8_bytes': len(prompt.encode()),
                            'rendered_prompt_sha256': digest(prompt), 'exact_prompt_tokens': None})
    # One candidate call, one batch duplicate call, one rank call and one
    # selected-hypothesis call; QH-rand shares the first two but not ranking.
    calls = {'D': 1, 'QH': 1, 'HQ': 1, 'D-empty': 1, 'D-shuffled': 1, 'QH-sel': 4, 'QH-rand': 3}
    value = {'schema_version': 'e6-token-feasibility-v1', 'status': 'conditional_feasibility_not_runtime_certified',
             'generated_cap': generated_cap, 'per_call_output_limit': per_call_output_limit,
             'proposed_context_limit': context_limit, 'verified_metadata_context_limit': metadata_context_limit,
             'maximum_prompt_tokens_with_full_per_call_output': context_limit - per_call_output_limit,
             'single_attempt_stage_counts': calls,
             'maximum_requested_outputs_plus_one_token_probes': {arm: n * (per_call_output_limit + 1) for arm, n in calls.items()},
             'fixed_initial_prompt_lengths': records,
             'maximum_fixed_prompt_characters': max((r['characters'] for r in records), default=0),
             'maximum_fixed_prompt_utf8_bytes': max((r['utf8_bytes'] for r in records), default=0),
             'exact_token_count_available_offline': False,
             'dynamic_prompts': 'deduplication, ranking, selected-question generation, shuffled donors and retries require exact rendered-prompt checks at runtime',
             'conclusions': [
                 '8192 generated tokens is a workflow allowance, independent of context and prompt length.',
                 'At 2048 output tokens/call, QH-sel can request 8196 including four one-token probes. The controller must restrict the last call to remaining budget; no promise of completion.',
                 'An 8192 context permits at most 6144 exact prompt tokens when reserving 2048 output tokens.',
                 'The saved 32-token probe verifies neither 2048 output adequacy nor a context window of 8192 or 131072 in operation.',
                 'Repeated evidence prompts affect context and compute, not generated-token debits. Intermediate model OUTPUTS do consume the cap.',
                 'No numeric cap is changed or approved by this report.']}
    return dict(value, manifest_sha256=digest(value))
