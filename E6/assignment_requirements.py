"""Assignment-mandated values, separate from methodological recommendations.

Source: preserved E6/assignment_e6_excerpt_v1.txt (Experiment instructions and
E6, pp.27, 38-40). K=6/M=3 are an example there, not mandated numeric choices.
"""
from __future__ import annotations

CONFIG_VALUES = {
    'arms': ['D', 'QH', 'QH-sel', 'QH-rand', 'HQ', 'D-empty', 'D-shuffled'],
    'inference_budget.accounting_unit': 'generated_tokens',
    'inference_budget.prompt_tokens_recorded_separately': True,
    'inference_budget.equalize_calls_or_tokens': True,
    'inference_budget.count_selector_dedup_judge_calls': True,
    'controls.d_empty.task_may_contain_paper_specific_evidence': False,
    'controls.d_shuffled.self_donation_allowed': False,
    'evaluation_human_review.evaluate_questions': True,
    'evaluation_human_review.target_extraction_used': True,
    'evaluation_human_review.human_review_scope': 'Read 20 input sets end to end across all seven arms and write error analysis with real examples.',
    'evaluation_human_review.error_analysis_input_set_count': 20,
    'statistical_analysis.uncertainty_method': 'paired input-set bootstrap with 95% intervals for every headline number',
    'output.assignment_jsonl_required_fields': ['input_set_id', 'testbed', 'arm', 'rq', 'hypothesis', 'tokens_generated', 'model', 'seed'],
    'output.assignment_testbed_labels': ['literature', 'data'],
    'output.assignment_arm_labels': ['D', 'QH', 'QH_sel', 'QH_rand', 'HQ', 'D_empty', 'D_shuffled'],
    'output.assignment_record_unit': 'one generation per JSONL line',
    'reproducibility.preregister_predictions_before_evaluation': True,
    'reproducibility.one_page_memo_required': True,
}
LITERATURE_VALUES = {
    'assignment_requirements.minimum_literature_input_sets': 100,
    'assignment_requirements.minimum_reference_papers_per_input_set': 10,
    'assignment_requirements.target_must_be_posted_after_generator_training_cutoff': True,
    'assignment_requirements.reference_abstract_required': True,
    'assignment_requirements.target_reference_extraction_prompt': 'prompts/e6/09_target_extraction.txt',
    'assignment_requirements.manual_check_cases_required': 20,
}
EVALUATION_VALUES = {
    'reconstruction.best_similarity_metrics': ['research_question', 'main_hypothesis'],
    'reconstruction.required_judgments': ['best_similarity', 'same_question'],
    'question_type.required_distinctions': ['constructive', 'analytic'],
    'pairwise_judging.maximum_judges': 1,
    'pairwise_judging.comparison_orders': ['A_then_B', 'B_then_A'],
    'pairwise_judging.length_matching_required': True,
    'pairwise_judging.output_label': 'LLM judge output',
    'paired_bootstrap.resampling_unit': 'input_set',
    'paired_bootstrap.confidence_level': 0.95,
}


def get_path(value, dotted):
    for key in dotted.split('.'):
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def validate_mandated_values(value, expected):
    errors = []
    for path, required in expected.items():
        actual = get_path(value, path)
        if actual != required or type(actual) is not type(required):
            errors.append('assignment requirement: ' + path + ' must equal ' + repr(required))
    return errors
