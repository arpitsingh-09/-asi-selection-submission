#!/usr/bin/env python3
"""Local fail-closed E6 protocol/config validator; performs no inference."""

import argparse
import copy
import json
import subprocess
from pathlib import Path

CONFIG_PATH = Path(__file__).with_name("config.json")
PROTOCOL_PATH = Path(__file__).with_name("protocol.md")
ARMS = ("D", "QH", "QH-sel", "QH-rand", "HQ", "D-empty", "D-shuffled")
REQUIRED = (
    "protocol.approved_by", "protocol.approved_at_utc",
    "protocol.confirmatory_or_exploratory", "protocol.prospective_protocol_record",
    "dataset.source", "dataset.evidence_source", "dataset.experimental_unit",
    "dataset.source_sha256", "dataset.task_domain_construction",
    "dataset.task_domain_allowed_source_fields", "dataset.canonical_paper_id_rule",
    "dataset.arxiv_version_suffix_policy", "dataset.cross_category_membership_policy",
    "dataset.sample_size", "dataset.sampling_method", "dataset.stratification_dimensions",
    "dataset.selection_seed", "dataset.development_evaluation_split", "dataset.manifest_sha256",
    "generation.model", "generation.immutable_version_or_digest", "generation.backend",
    "generation.backend_version", "generation.temperature", "generation.top_p",
    "generation.max_output_tokens", "generation.context_limit",
    "generation.replicates_per_paper_arm", "generation.seed", "generation.random_seed_behavior",
    "candidate_generation.requested_candidate_count",
    "candidate_generation.candidate_generation_retries",
    "deduplication.duplicate_clustering_rule", "deduplication.adjudication_rule",
    "deduplication.fewer_than_three_unique_questions_policy",
    "selection_randomization.qh_sel.ranking_criteria",
    "selection_randomization.qh_sel.score_scale_and_anchors",
    "selection_randomization.qh_sel.selector_model_or_method",
    "selection_randomization.qh_sel.score_aggregation",
    "selection_randomization.qh_sel.tie_break_rule",
    "selection_randomization.qh_rand.sampler",
    "selection_randomization.qh_rand.master_seed",
    "selection_randomization.qh_rand.rng_and_version",
    "selection_randomization.qh_rand.per_input_seed_derivation",
    "selection_randomization.qh_rand.sampling_without_replacement",
    "controls.d_empty.evidence_removal_representation",
    "controls.d_empty.task_may_contain_paper_specific_evidence",
    "controls.d_shuffled.donor_matching_rule", "controls.d_shuffled.within_split_only",
    "controls.d_shuffled.assignment_seed", "controls.d_shuffled.number_of_assignments",
    "controls.d_shuffled.donor_reuse_policy",
    "inference_budget.estimand", "inference_budget.budget_policy",
    "inference_budget.equalize_calls_or_tokens",
    "inference_budget.count_selector_dedup_judge_calls",
    "inference_budget.per_call_accounting_method",
    "inference_budget.tokens_per_input_set_arm",
    "output.schema_approved",
    "failure_handling.max_attempts", "failure_handling.retryable_error_classes",
    "failure_handling.retry_prompt_policy", "failure_handling.timeout_retry_policy",
    "failure_handling.invalid_json_policy", "failure_handling.failed_cell_analysis_policy",
    "failure_handling.quality_based_regeneration_policy",
    "failure_handling.replacement_after_outcome_inspection",
    "evaluation_human_review.primary_outcome",
    "evaluation_human_review.secondary_outcomes",
    "evaluation_human_review.evaluate_questions",
    "evaluation_human_review.comparison_schedule",
    "evaluation_human_review.hypothesis_matching_and_aggregation",
    "evaluation_human_review.judge_model_and_version",
    "evaluation_human_review.judge_count",
    "evaluation_human_review.judge_context_for_controls",
    "evaluation_human_review.blind_arm_labels",
    "evaluation_human_review.randomize_and_balance_ab_order",
    "evaluation_human_review.human_review_scope",
    "evaluation_human_review.human_review_sample",
    "evaluation_human_review.human_reviewer_count",
    "evaluation_human_review.human_review_guide_version",
    "evaluation_human_review.adjudication_rule",
    "evaluation_human_review.inter_rater_reporting",
    "evaluation_human_review.target_extraction_used",
    "evaluation_human_review.composite_score_and_weights",
    "execution_replication.run_order_method",
    "execution_replication.replicates_per_paper_arm",
    "execution_replication.sample_size_rationale",
    "statistical_analysis.primary_contrasts",
    "statistical_analysis.statistical_model",
    "statistical_analysis.uncertainty_method",
    "statistical_analysis.multiplicity_method",
    "statistical_analysis.missing_data_rule",
    "statistical_analysis.sensitivity_analyses",
    "statistical_analysis.analysis_dependency_versions",
)
REQUIRED_KEYS = (
    "protocol.status", "protocol.execution_authorized", "dataset.frozen",
    "arms", "repository_facts", "prompt_contracts.arm_outputs",
)
POSITIVE_INTS = (
    "dataset.sample_size", "generation.max_output_tokens", "generation.context_limit",
    "generation.replicates_per_paper_arm", "candidate_generation.requested_candidate_count",
    "inference_budget.tokens_per_input_set_arm",
    "controls.d_shuffled.number_of_assignments", "failure_handling.max_attempts",
    "evaluation_human_review.judge_count", "evaluation_human_review.human_reviewer_count",
    "execution_replication.replicates_per_paper_arm",
)
NONNEGATIVE_INTS = ("candidate_generation.candidate_generation_retries", "generation.seed")
LIST_OF_STRINGS = (
    "dataset.task_domain_allowed_source_fields", "dataset.stratification_dimensions",
    "selection_randomization.qh_sel.ranking_criteria",
    "evaluation_human_review.secondary_outcomes",
    "evaluation_human_review.human_review_sample",
    "statistical_analysis.primary_contrasts",
    "statistical_analysis.sensitivity_analyses",
)
SHA_FIELDS = ("dataset.source_sha256", "dataset.manifest_sha256")
PREREGISTRATION_COMMITTED_PATHS = (
    "E6/PREREG.md",
    "E6/development_runtime_probe.py",
    "E6/inductive_execution.py",
    "E6/literature_execution.py",
    "E6/literature_finalization.py",
    "prompts/e6/15_reconstruction_similarity.txt",
    "prompts/e6/16_hypothesis_distinctness.txt",
    "E6/question_pipeline.py",
    "E6/evaluation.py",
    "E6/configured_evaluators.py",
    "E6/prior_question_corpus.py",
    "E6/prior_question_expansion.py",
    "E6/data/prior_question_corpus_v4.json",
    "E6/data/prior_question_expansion_v1/systematic_frame.json",
    "E6/data/prior_question_expansion_v1/source_question_reviews.json",
    "E6/data/prior_question_expansion_v1/source_index.json",
    "prompts/e6/17_prior_question_verbatim.txt",
    "E6/data/prior_question_corpus_v3.json",
    "E6/data/prior_question_sources_v1/index_v2.json",
    "E6/statistical_analysis.py",
    "E6/approval_configuration.py",
    "E6/STATISTICAL_ANALYSIS.md",
    "E6/researcher_approval.py",
    "E6/assignment_requirements.py",
    "E6/prepare_hypobench_inductive.py",
    "E6/execution_preparation.py",
    "E6/orchestrator.py",
    "E6/token_budget.py",
    "E6/ollama_adapter.py",
    "E6/hypobench_policies.py",
    "E6/config.json",
    "E6/RESEARCHER_APPROVAL.json",
    "E6/data/literature_freeze_plan_v1.json",
    "E6/protocol.md",
    "E6/evaluation_config.json",
    "E6/question_pipeline_config.json",
    "E6/literature_testbed_config.json",
    "E6/data/development_manifest_v2.json",
    "E6/data/hypobench_election_level2_test_manifest_v1.json",
    "E6/data/literature_citation_verified_manifest_v1.json",
    "E6/data/gemma3_local_verification_v1.json",
)


def validate_preregistration_git_commit(repo_root=None):
    """Require finalized preregistration/config files to be committed verbatim.

    This read-only check deliberately fails until the researcher finalizes and
    commits the preregistration. It does not create a commit or modify files.
    """
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[1]
    prereg_path = root / "E6/PREREG.md"
    if not prereg_path.is_file():
        return ["preregistration Git gate: E6/PREREG.md is missing"]
    try:
        prereg_text = prereg_path.read_text(encoding="utf-8")
    except OSError as exc:
        return ["preregistration Git gate: cannot read E6/PREREG.md: " + str(exc)]
    if "**Preregistration status:** FINALIZED" not in prereg_text:
        return ["preregistration Git gate: document is not marked FINALIZED"]

    from researcher_approval import load_approval_errors
    errors = load_approval_errors(root, finalization=True)
    required_paths = list(PREREGISTRATION_COMMITTED_PATHS)
    try:
        approval = json.loads((root / "E6/RESEARCHER_APPROVAL.json").read_text())
        artifacts = approval.get("configuration_signoff", {}).get("artifacts", {})
        if isinstance(artifacts, dict):
            from researcher_approval import safe_path
            for relative in artifacts:
                safe_path(root, relative)
                if relative not in required_paths:
                    required_paths.append(relative)
    except (OSError, ValueError, AttributeError):
        pass  # approval validation above reports the missing or malformed record
    try:
        configuration = json.loads((root / "E6/config.json").read_text())
        runtime_path = configuration.get("generation", {}).get("development_runtime_probe_report")
        if runtime_path:
            from researcher_approval import safe_path
            safe_path(root, runtime_path)
            if runtime_path not in required_paths:
                required_paths.append(runtime_path)
    except (OSError, ValueError, AttributeError):
        pass
    for relative_path in required_paths:
        local_path = root / relative_path
        if not local_path.is_file():
            errors.append("preregistration Git gate: required file is missing: " + relative_path)
            continue
        try:
            committed = subprocess.run(
                ["git", "show", "HEAD:" + relative_path], cwd=str(root),
                check=False, capture_output=True,
            )
        except OSError as exc:
            errors.append("preregistration Git gate: git unavailable: " + str(exc))
            break
        if committed.returncode != 0:
            errors.append("preregistration Git gate: file is not in HEAD: " + relative_path)
            continue
        try:
            working_bytes = local_path.read_bytes()
        except OSError as exc:
            errors.append("preregistration Git gate: cannot read " + relative_path + ": " + str(exc))
            continue
        if committed.stdout != working_bytes:
            errors.append("preregistration Git gate: committed file differs from working tree: "
                          + relative_path)
    return errors


def get_path(data, dotted):
    current = data
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def set_path(data, dotted, value):
    current = data
    parts = dotted.split(".")
    for part in parts[:-1]:
        current = current[part]
    current[parts[-1]] = value


def validate_config(data, protocol_text="", *, root=None):
    errors = []
    if not isinstance(data, dict):
        return ["$: config root must be a JSON object"]

    from assignment_requirements import CONFIG_VALUES, validate_mandated_values
    errors.extend(validate_mandated_values(data, CONFIG_VALUES))

    paths = set(REQUIRED) | set(REQUIRED_KEYS)
    for dotted in sorted(paths):
        exists, value = get_path(data, dotted)
        if not exists:
            errors.append(dotted + ": missing required key")
        elif dotted in REQUIRED and value is None:
            errors.append(dotted + ": unresolved null decision")
        elif dotted in REQUIRED and isinstance(value, str) and value.strip().upper() in {
            "", "TODO", "TBD", "UNRESOLVED", "PLACEHOLDER"
        }:
            errors.append(dotted + ": unresolved placeholder")

    if get_path(data, "protocol.status")[1] != "approved":
        errors.append("protocol.status: must be exactly approved")
    auth = get_path(data, "protocol.execution_authorized")[1]
    if type(auth) is not bool or auth is not True:
        errors.append("protocol.execution_authorized: must be Boolean true")
    frozen = get_path(data, "dataset.frozen")[1]
    if type(frozen) is not bool or frozen is not True:
        errors.append("dataset.frozen: must be Boolean true before execution")
    schema_approved = get_path(data, "output.schema_approved")[1]
    if type(schema_approved) is not bool or schema_approved is not True:
        errors.append("output.schema_approved: must be Boolean true")

    arms = data.get("arms")
    if not isinstance(arms, list) or tuple(arms) != ARMS:
        errors.append("arms: must match all seven arms in protocol order")

    candidate_count = get_path(data, "candidate_generation.requested_candidate_count")[1]
    dedup_count = get_path(data, "candidate_generation.existing_dedup_prompt_expected_count")[1]
    if type(dedup_count) is not int or dedup_count != 6:
        errors.append("candidate_generation.existing_dedup_prompt_expected_count: must match the existing six-candidate prompt contract")
    if candidate_count is not None and candidate_count != dedup_count:
        errors.append("candidate_generation.requested_candidate_count: must match dedup prompt input count or prompts must be reviewed and versioned")
    if get_path(data, "candidate_generation.shared_pool_for_qh_sel_and_qh_rand")[1] is not True:
        errors.append("candidate_generation.shared_pool_for_qh_sel_and_qh_rand: must be Boolean true")
    if get_path(data, "deduplication.pairwise_all_pairs")[1] is not True:
        errors.append("deduplication.pairwise_all_pairs: must be Boolean true")
    if get_path(data, "deduplication.expected_pair_count_if_six_candidates")[1] != 15:
        errors.append("deduplication.expected_pair_count_if_six_candidates: must equal 15")

    facts = data.get("repository_facts")
    if not isinstance(facts, dict):
        errors.append("repository_facts: must be an object")
    else:
        keys = ("raw_corpus_unique_paper_ids", "focal_exclusion_ids",
                "targeted_comparison_ids", "targeted_comparison_overlap_with_focal",
                "eligible_candidate_ids_after_union_exclusion")
        if any(type(facts.get(k)) is not int for k in keys):
            errors.append("repository_facts: all audited counts must be integers")
        else:
            raw = facts["raw_corpus_unique_paper_ids"]
            focal = facts["focal_exclusion_ids"]
            targeted = facts["targeted_comparison_ids"]
            overlap = facts["targeted_comparison_overlap_with_focal"]
            eligible = facts["eligible_candidate_ids_after_union_exclusion"]
            if raw != 2680 or focal != 300 or targeted != 15 or overlap != 15:
                errors.append("repository_facts: audited counts disagree with verified facts")
            if not 0 <= overlap <= min(targeted, focal):
                errors.append("repository_facts: invalid comparison/focal overlap")
            if eligible != raw - focal - (targeted - overlap):
                errors.append("repository_facts: arithmetic must satisfy raw - focal - comparison-only = eligible")

    contracts = data.get("prompt_contracts")
    if not isinstance(contracts, dict):
        errors.append("prompt_contracts: must be an object")
    else:
        if contracts.get("hypotheses_per_arm") != 6:
            errors.append("prompt_contracts.hypotheses_per_arm: must equal 6")
        if contracts.get("max_words_per_hypothesis") != 50:
            errors.append("prompt_contracts.max_words_per_hypothesis: must equal 50")
        outputs = contracts.get("arm_outputs")
        if not isinstance(outputs, dict) or set(outputs) != set(ARMS):
            errors.append("prompt_contracts.arm_outputs: must specify all seven arms")
        else:
            for arm, spec in outputs.items():
                if not isinstance(spec, dict) or spec.get("hypotheses") != 6:
                    errors.append("prompt_contracts.arm_outputs." + arm + ": must specify six hypotheses")
            for arm in ("QH", "QH-sel", "QH-rand"):
                spec = outputs.get(arm, {})
                if spec.get("questions") != 3 or spec.get("hypotheses_per_question") != 2:
                    errors.append("prompt_contracts.arm_outputs." + arm + ": expected three questions and two hypotheses each")
            if outputs.get("HQ", {}).get("questions") != 6:
                errors.append("prompt_contracts.arm_outputs.HQ: expected six linked questions")
            for arm in ("D", "D-empty", "D-shuffled"):
                if outputs.get(arm, {}).get("questions") != 0:
                    errors.append("prompt_contracts.arm_outputs." + arm + ": expected no generated questions")

    # Validate required decision types where values have been supplied.
    bool_paths = (
        "protocol.execution_authorized", "dataset.frozen", "output.schema_approved",
        "controls.d_empty.task_may_contain_paper_specific_evidence",
        "controls.d_shuffled.within_split_only", "controls.d_shuffled.self_donation_allowed",
        "candidate_generation.shared_pool_for_qh_sel_and_qh_rand",
        "deduplication.pairwise_all_pairs",
        "inference_budget.equalize_calls_or_tokens",
        "inference_budget.count_selector_dedup_judge_calls",
        "evaluation_human_review.evaluate_questions",
        "evaluation_human_review.blind_arm_labels",
        "evaluation_human_review.randomize_and_balance_ab_order",
        "evaluation_human_review.target_extraction_used",
        "failure_handling.replacement_after_outcome_inspection",
    )
    for dotted in bool_paths:
        exists, value = get_path(data, dotted)
        if exists and value is not None and type(value) is not bool:
            errors.append(dotted + ": must be a Boolean")

    string_paths = (
        "protocol.approved_by", "protocol.approved_at_utc",
        "protocol.confirmatory_or_exploratory", "protocol.prospective_protocol_record",
        "dataset.source", "dataset.evidence_source", "dataset.experimental_unit",
        "dataset.task_domain_construction", "dataset.canonical_paper_id_rule",
        "dataset.arxiv_version_suffix_policy", "dataset.cross_category_membership_policy",
        "dataset.sampling_method", "dataset.development_evaluation_split",
        "generation.model", "generation.immutable_version_or_digest",
        "generation.backend", "generation.backend_version",
        "generation.random_seed_behavior", "deduplication.duplicate_clustering_rule",
        "deduplication.adjudication_rule",
        "deduplication.fewer_than_three_unique_questions_policy",
        "selection_randomization.qh_sel.score_scale_and_anchors",
        "selection_randomization.qh_sel.selector_model_or_method",
        "selection_randomization.qh_sel.score_aggregation",
        "selection_randomization.qh_sel.tie_break_rule",
        "selection_randomization.qh_rand.sampler",
        "selection_randomization.qh_rand.rng_and_version",
        "selection_randomization.qh_rand.per_input_seed_derivation",
        "controls.d_empty.evidence_removal_representation",
        "controls.d_shuffled.donor_matching_rule",
        "controls.d_shuffled.donor_reuse_policy",
        "inference_budget.estimand", "inference_budget.budget_policy",
        "inference_budget.per_call_accounting_method",
        "output.schema_version", "failure_handling.retry_prompt_policy",
        "failure_handling.timeout_retry_policy", "failure_handling.invalid_json_policy",
        "failure_handling.quality_based_regeneration_policy",
        "evaluation_human_review.primary_outcome",
        "evaluation_human_review.comparison_schedule",
        "evaluation_human_review.hypothesis_matching_and_aggregation",
        "evaluation_human_review.judge_model_and_version",
        "evaluation_human_review.judge_context_for_controls",
        "evaluation_human_review.human_review_scope",
        "evaluation_human_review.human_review_guide_version",
        "evaluation_human_review.adjudication_rule",
        "evaluation_human_review.inter_rater_reporting",
        "execution_replication.run_order_method",
        "execution_replication.sample_size_rationale",
        "statistical_analysis.statistical_model",
        "statistical_analysis.uncertainty_method",
        "statistical_analysis.multiplicity_method",
        "statistical_analysis.missing_data_rule",
        "statistical_analysis.analysis_dependency_versions",
    )
    for dotted in string_paths:
        exists, value = get_path(data, dotted)
        if exists and value is not None and (not isinstance(value, str) or not value.strip()):
            errors.append(dotted + ": must be a nonempty string")

    int_paths = (
        "dataset.sample_size", "generation.max_output_tokens", "generation.context_limit",
        "generation.replicates_per_paper_arm", "candidate_generation.requested_candidate_count",
        "candidate_generation.candidate_generation_retries", "generation.seed",
        "controls.d_shuffled.number_of_assignments", "failure_handling.max_attempts",
        "evaluation_human_review.judge_count", "evaluation_human_review.human_reviewer_count",
        "execution_replication.replicates_per_paper_arm",
    )
    for dotted in int_paths:
        exists, value = get_path(data, dotted)
        if exists and value is not None and type(value) is not int:
            errors.append(dotted + ": must be an integer")
        elif exists and value is not None:
            minimum = 0 if dotted in NONNEGATIVE_INTS else 1
            if value < minimum:
                errors.append(dotted + ": outside allowed integer range")

    missingness = get_path(data, "failure_handling.failed_cell_analysis_policy")[1]
    if isinstance(missingness, dict):
        required = {"missing_score", "imputation", "arm_mean_denominator",
                    "comparison_denominator", "planned_denominator",
                    "invalid_TEST_prediction_policy", "questionless_arm_policy"}
        if (not required <= set(missingness) or missingness.get("missing_score") is not None
                or missingness.get("imputation") != "none"
                or any(not isinstance(missingness.get(k), str) or not missingness[k].strip()
                       for k in required - {"missing_score"})):
            errors.append("failure_handling.failed_cell_analysis_policy: incomplete explicit null/denominator policy")
    elif missingness is not None and (not isinstance(missingness, str) or not missingness.strip()):
        errors.append("failure_handling.failed_cell_analysis_policy: expected explicit policy object or text")

    context = get_path(data, "generation.context_limit")[1]
    output = get_path(data, "generation.max_output_tokens")[1]
    metadata_context = get_path(data, "generation.verified_context_length_model_metadata")[1]
    if type(context) is int and type(output) is int and output >= context:
        errors.append("generation.context_limit: must reserve space for prompt plus output")
    if type(context) is int and type(metadata_context) is int and context > metadata_context:
        errors.append("generation.context_limit: exceeds verified model metadata")
    if get_path(data, "dataset.data_generation_split")[1] != "TRAIN":
        errors.append("R44: dataset.data_generation_split must be TRAIN; TEST rows are evaluation-only")

    for dotted in ("generation.temperature", "generation.top_p"):
        exists, value = get_path(data, dotted)
        if exists and value is not None and type(value) not in (int, float):
            errors.append(dotted + ": must be numeric")
        elif exists and value is not None:
            if dotted.endswith("temperature") and not 0 <= value <= 2:
                errors.append(dotted + ": must be within [0, 2]")
            if dotted.endswith("top_p") and not 0 < value <= 1:
                errors.append(dotted + ": must be within (0, 1]")

    for dotted in LIST_OF_STRINGS:
        exists, value = get_path(data, dotted)
        if exists and value is not None and (
            not isinstance(value, list) or any(not isinstance(item, str) for item in value)
        ):
            errors.append(dotted + ": must be a list of strings")

    for dotted in SHA_FIELDS:
        exists, value = get_path(data, dotted)
        per_bed = data.get('dataset', {}).get('hash_schema') == 'per_testbed_artifact_files_v1'
        if per_bed:
            from researcher_approval import safe_path, file_digest
            key = dotted.split('.')[-1]
            paths = data['dataset'].get('artifact_paths', {}).get(key)
            if (not isinstance(value, dict) or set(value) != {'data', 'literature'}
                    or not isinstance(paths, dict) or set(paths) != {'data', 'literature'}):
                errors.append(dotted + ': require separate data/literature file hashes and paths')
                continue
            for bed in ('data', 'literature'):
                sha = value[bed]
                if (not isinstance(sha, str) or len(sha) != 64
                        or any(c not in '0123456789abcdefABCDEF' for c in sha)):
                    errors.append(dotted + '.' + bed + ': must be a 64-character hexadecimal SHA-256')
                    continue
                try:
                    actual = file_digest(safe_path(root or Path(__file__).resolve().parents[1], paths[bed]))
                    if actual != sha:
                        errors.append(dotted + '.' + bed + ': artifact file hash mismatch')
                except (OSError, ValueError, TypeError):
                    errors.append(dotted + '.' + bed + ': missing or invalid source artifact path')
        elif exists and value is not None and (
            not isinstance(value, str) or len(value) != 64
            or any(c not in "0123456789abcdefABCDEF" for c in value)
        ):
            errors.append(dotted + ": must be a 64-character hexadecimal SHA-256")

    marker = contract_marker(data)
    if marker not in protocol_text:
        errors.append("protocol.md: machine-checked contract marker disagrees with config.json")
    expected_rows = {
        "| D | Direct generation from task and abstract | Six hypotheses |",
        "| QH | Generate questions, then hypotheses in one response | Three questions, two hypotheses each, six total |",
        "| QH-sel | Select questions, then generate hypotheses | Three questions, two hypotheses each, six total |",
        "| QH-rand | Randomly select questions, then generate hypotheses | Three questions, two hypotheses each, six total |",
        "| HQ | Generate hypotheses first, then questions | Six hypotheses and six linked questions |",
        "| D-empty | Direct generation without substantive paper evidence | Six hypotheses |",
        "| D-shuffled | Recipient task with another paper's evidence | Six hypotheses |",
    }
    if not expected_rows.issubset(set(protocol_text.splitlines())):
        errors.append("protocol.md: arm table output contracts disagree with config.json")
    return errors


def contract_marker(data):
    facts = data["repository_facts"]
    prompt = data["prompt_contracts"]
    outputs = prompt["arm_outputs"]
    signature = ";".join(
        arm + ":" + str(outputs[arm]["questions"]) + "q"
        + str(outputs[arm]["hypotheses"]) + "h"
        + (str(outputs[arm]["hypotheses_per_question"])
           if outputs[arm]["hypotheses_per_question"] is not None else "")
        for arm in data["arms"]
    )
    return (
        "<!-- E6-CONTRACT status=" + data["protocol"]["status"]
        + " arms=" + ",".join(data["arms"])
        + " raw=" + str(facts["raw_corpus_unique_paper_ids"])
        + " focal=" + str(facts["focal_exclusion_ids"])
        + " targeted=" + str(facts["targeted_comparison_ids"])
        + " overlap=" + str(facts["targeted_comparison_overlap_with_focal"])
        + " eligible=" + str(facts["eligible_candidate_ids_after_union_exclusion"])
        + " hypotheses_per_arm=" + str(prompt["hypotheses_per_arm"])
        + " hypothesis_word_limit=" + str(prompt["max_words_per_hypothesis"])
        + " candidate_count=" + str(data["candidate_generation"]["requested_candidate_count"])
        + " dedup_prompt_count="
        + str(data["candidate_generation"]["existing_dedup_prompt_expected_count"])
        + " outputs=" + signature + " -->"
    )

def setv(data, dotted, value):
    cur = data
    parts = dotted.split(".")
    for part in parts[:-1]:
        cur = cur[part]
    cur[parts[-1]] = value


def complete_fixture(source):
    """Build a valid synthetic fixture in memory only for gate tests."""
    data = copy.deepcopy(source)
    values = {
        "protocol.status": "approved",
        "protocol.approved_by": "SELF_TEST_ONLY",
        "protocol.approved_at_utc": "2000-01-01T00:00:00Z",
        "protocol.confirmatory_or_exploratory": "exploratory",
        "protocol.prospective_protocol_record": "SELF_TEST_ONLY",
        "protocol.execution_authorized": True,
        "dataset.source": "SELF_TEST_ONLY",
        "dataset.evidence_source": "abstract",
        "dataset.experimental_unit": "SELF_TEST_ONLY",
        "dataset.source_sha256": "a" * 64,
        "dataset.task_domain_construction": "SELF_TEST_ONLY",
        "dataset.task_domain_allowed_source_fields": ["title"],
        "dataset.canonical_paper_id_rule": "SELF_TEST_ONLY",
        "dataset.arxiv_version_suffix_policy": "SELF_TEST_ONLY",
        "dataset.cross_category_membership_policy": "SELF_TEST_ONLY",
        "dataset.sample_size": 1, "dataset.sampling_method": "SELF_TEST_ONLY",
        "dataset.stratification_dimensions": [], "dataset.selection_seed": 1,
        "dataset.development_evaluation_split": "SELF_TEST_ONLY",
        "dataset.manifest_sha256": "b" * 64, "dataset.frozen": True,
        "generation.model": "SELF_TEST_ONLY",
        "generation.immutable_version_or_digest": "SELF_TEST_ONLY",
        "generation.backend": "SELF_TEST_ONLY", "generation.backend_version": "SELF_TEST_ONLY",
        "generation.temperature": 0, "generation.top_p": 1, "generation.seed": 2026,
        "generation.max_output_tokens": 100, "generation.context_limit": 1000,
        "generation.replicates_per_paper_arm": 1,
        "inference_budget.tokens_per_input_set_arm": 1000,
        "generation.random_seed_behavior": "SELF_TEST_ONLY",
        "candidate_generation.requested_candidate_count": 6,
        "candidate_generation.candidate_generation_retries": 0,
        "deduplication.duplicate_clustering_rule": "SELF_TEST_ONLY",
        "deduplication.adjudication_rule": "SELF_TEST_ONLY",
        "deduplication.fewer_than_three_unique_questions_policy": "SELF_TEST_ONLY",
        "selection_randomization.qh_sel.ranking_criteria": ["SELF_TEST_ONLY"],
        "selection_randomization.qh_sel.score_scale_and_anchors": "SELF_TEST_ONLY",
        "selection_randomization.qh_sel.selector_model_or_method": "SELF_TEST_ONLY",
        "selection_randomization.qh_sel.score_aggregation": "SELF_TEST_ONLY",
        "selection_randomization.qh_sel.tie_break_rule": "SELF_TEST_ONLY",
        "selection_randomization.qh_rand.sampler": "SELF_TEST_ONLY",
        "selection_randomization.qh_rand.master_seed": 1,
        "selection_randomization.qh_rand.rng_and_version": "SELF_TEST_ONLY",
        "selection_randomization.qh_rand.per_input_seed_derivation": "SELF_TEST_ONLY",
        "selection_randomization.qh_rand.sampling_without_replacement": True,
        "controls.d_empty.evidence_removal_representation": "SELF_TEST_ONLY",
        "controls.d_empty.task_may_contain_paper_specific_evidence": False,
        "controls.d_shuffled.donor_matching_rule": "SELF_TEST_ONLY",
        "controls.d_shuffled.within_split_only": True,
        "controls.d_shuffled.assignment_seed": 1,
        "controls.d_shuffled.number_of_assignments": 1,
        "controls.d_shuffled.donor_reuse_policy": "SELF_TEST_ONLY",
        "inference_budget.estimand": "SELF_TEST_ONLY",
        "inference_budget.budget_policy": "SELF_TEST_ONLY",
        "inference_budget.equalize_calls_or_tokens": False,
        "inference_budget.count_selector_dedup_judge_calls": True,
        "inference_budget.per_call_accounting_method": "SELF_TEST_ONLY",
        "output.schema_approved": True,
        "failure_handling.max_attempts": 1,
        "failure_handling.retryable_error_classes": ["SELF_TEST_ONLY"],
        "failure_handling.retry_prompt_policy": "SELF_TEST_ONLY",
        "failure_handling.timeout_retry_policy": "SELF_TEST_ONLY",
        "failure_handling.invalid_json_policy": "SELF_TEST_ONLY",
        "failure_handling.failed_cell_analysis_policy": "SELF_TEST_ONLY",
        "failure_handling.quality_based_regeneration_policy": "SELF_TEST_ONLY",
        "failure_handling.replacement_after_outcome_inspection": False,
        "evaluation_human_review.primary_outcome": "SELF_TEST_ONLY",
        "evaluation_human_review.secondary_outcomes": ["SELF_TEST_ONLY"],
        "evaluation_human_review.evaluate_questions": False,
        "evaluation_human_review.comparison_schedule": "SELF_TEST_ONLY",
        "evaluation_human_review.hypothesis_matching_and_aggregation": "SELF_TEST_ONLY",
        "evaluation_human_review.judge_model_and_version": "SELF_TEST_ONLY",
        "evaluation_human_review.judge_count": 1,
        "evaluation_human_review.judge_context_for_controls": "SELF_TEST_ONLY",
        "evaluation_human_review.blind_arm_labels": True,
        "evaluation_human_review.randomize_and_balance_ab_order": True,
        "evaluation_human_review.human_review_scope": "SELF_TEST_ONLY",
        "evaluation_human_review.human_review_sample": ["SELF_TEST_ONLY"],
        "evaluation_human_review.human_reviewer_count": 1,
        "evaluation_human_review.human_review_guide_version": "SELF_TEST_ONLY",
        "evaluation_human_review.adjudication_rule": "SELF_TEST_ONLY",
        "evaluation_human_review.inter_rater_reporting": "SELF_TEST_ONLY",
        "evaluation_human_review.target_extraction_used": False,
        "evaluation_human_review.composite_score_and_weights": "SELF_TEST_ONLY",
        "execution_replication.run_order_method": "SELF_TEST_ONLY",
        "execution_replication.replicates_per_paper_arm": 1,
        "execution_replication.sample_size_rationale": "SELF_TEST_ONLY",
        "statistical_analysis.primary_contrasts": ["SELF_TEST_ONLY"],
        "statistical_analysis.statistical_model": "SELF_TEST_ONLY",
        "statistical_analysis.uncertainty_method": "SELF_TEST_ONLY",
        "statistical_analysis.multiplicity_method": "SELF_TEST_ONLY",
        "statistical_analysis.missing_data_rule": "SELF_TEST_ONLY",
        "statistical_analysis.sensitivity_analyses": ["SELF_TEST_ONLY"],
        "statistical_analysis.analysis_dependency_versions": "SELF_TEST_ONLY",
    }
    for dotted, value in values.items():
        setv(data, dotted, value)
    return data


def run_self_tests(source):
    base = complete_fixture(source)
    # The self-tests use synthetic legacy hash strings, never real datasets.
    base['dataset'].pop('hash_schema', None)
    base['dataset'].pop('artifact_paths', None)
    text = contract_marker(base)
    cases = []

    def test(name, mutate, fragment):
        probe = copy.deepcopy(base)
        mutate(probe)
        errs = validate_config(probe, text)
        cases.append((name, any(fragment in e for e in errs), errs))

    probe = copy.deepcopy(base)
    del probe["dataset"]["sample_size"]
    errs = validate_config(probe, text)
    cases.append(("missing field", any("dataset.sample_size: missing required key" in e for e in errs), errs))

    test("null field", lambda x: setv(x, "generation.model", None),
         "generation.model: unresolved null decision")
    test("false execution authorization",
         lambda x: setv(x, "protocol.execution_authorized", False),
         "protocol.execution_authorized: must be Boolean true")
    test("unapproved status",
         lambda x: setv(x, "protocol.status", "draft_unapproved"),
         "protocol.status: must be exactly approved")
    test("invalid type", lambda x: setv(x, "dataset.sample_size", "10"),
         "dataset.sample_size: must be an integer")
    test("invalid numeric range", lambda x: setv(x, "generation.temperature", 3),
         "generation.temperature: must be within [0, 2]")
    test("invalid string type", lambda x: setv(x, "dataset.canonical_paper_id_rule", 7),
         "dataset.canonical_paper_id_rule: must be a nonempty string")
    test("invalid Boolean type", lambda x: setv(x, "evaluation_human_review.blind_arm_labels", "yes"),
         "evaluation_human_review.blind_arm_labels: must be a Boolean")
    test("dataset arithmetic inconsistency",
         lambda x: setv(x, "repository_facts.eligible_candidate_ids_after_union_exclusion", 2379),
         "arithmetic must satisfy raw - focal - comparison-only = eligible")
    bad_protocol = text.replace("eligible=2380", "eligible=2379")
    errs = validate_config(base, bad_protocol)
    cases.append(("protocol/config consistency",
                  any("marker disagrees" in e for e in errs), errs))

    for name, passed, errs in cases:
        print(("PASS" if passed else "FAIL") + ": " + name)
        if not passed:
            for error in errs:
                print("  " + error)
    return all(passed for _, passed, _ in cases)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--protocol", type=Path, default=PROTOCOL_PATH)
    parser.add_argument("--non-inference", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--precommit", action="store_true",
                        help="read-only local readiness checks without requiring HEAD; never authorizes execution")
    args = parser.parse_args()
    try:
        data = json.loads(args.config.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print("CONFIG ERROR: " + str(exc))
        return 2
    if args.self_test:
        passed = run_self_tests(data)
        print("Self-tests: " + ("PASS" if passed else "FAIL"))
        return 0 if passed else 1
    try:
        protocol_text = args.protocol.read_text(encoding="utf-8")
    except OSError as exc:
        print("PROTOCOL ERROR: " + str(exc))
        return 2
    print("Mode: " + ("non-inference; no model calls or experiment actions" if args.non_inference else "local-only"))
    errors = validate_config(data, protocol_text)
    from researcher_approval import load_approval_errors
    errors.extend(load_approval_errors(args.config.resolve().parent.parent, finalization=True))
    from development_runtime_probe import validate_runtime_evidence
    errors.extend(validate_runtime_evidence(data, root=args.config.resolve().parent.parent))
    if args.precommit:
        try:
            prereg = (args.config.resolve().parent / "PREREG.md").read_text()
            if "**Preregistration status:** FINALIZED" not in prereg:
                errors.append("precommit readiness: preregistration is not marked FINALIZED")
        except OSError:
            errors.append("precommit readiness: preregistration is missing")
    else:
        errors.extend(validate_preregistration_git_commit(args.config.resolve().parent.parent))
    if errors:
        print("Protocol gate: BLOCKED (" + str(len(errors)) + " unresolved/invalid item(s))")
        for error in errors:
            print("- " + error)
        print("Execution is blocked until decisions are resolved, protocol approved, dataset frozen, and execution authorized.")
        return 2
    print("Precommit readiness: COMPLETE; execution still requires the Git gate"
          if args.precommit else "Protocol gate: COMPLETE and authorized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
