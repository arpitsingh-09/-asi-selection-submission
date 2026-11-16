#!/usr/bin/env python3
"""Seven-arm E6 orchestration with fail-closed protocol and provisional output."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from question_pipeline import (
    ModelCall,
    PipelineSettings,
    PipelineState,
    PipelineError,
    generate_d_empty,
    generate_d_shuffled,
    generate_direct_arm,
    generate_question_hypotheses,
    prepare_qh_selection_arms,
    selected_questions_for_arm,
)
from validate_protocol import (
    CONFIG_PATH, PROTOCOL_PATH, validate_config,
    validate_preregistration_git_commit,
)
from token_budget import PerArmTokenBudget, TokenBudgetError

ARMS = ("D", "QH", "QH-sel", "QH-rand", "HQ", "D-empty", "D-shuffled")
PROVISIONAL_SCHEMA_VERSION = "e6-provisional-envelope-v1"
ROOT = Path(__file__).resolve().parents[1]
PROMPT_SOURCES = {
    "D": "prompts/e6/01_generator_D.txt",
    "QH": "prompts/e6/02_generator_QH.txt",
    "QH-sel": "prompts/e6/03_generator_QH_sel.txt",
    "QH-rand": "prompts/e6/04_generator_QH_rand.txt",
    "HQ": "prompts/e6/05_generator_HQ.txt",
    "D-empty": "prompts/e6/06_generator_controls.txt",
    "D-shuffled": "prompts/e6/06_generator_controls.txt",
}


@dataclass(frozen=True)
class ExperimentInput:
    """One externally prepared paper input; contains no sampling behavior."""

    paper_id: str
    domain_and_task: str
    evidence: str
    provenance: Mapping[str, Any] = field(default_factory=dict)
    reference_evidence: tuple[str, ...] | None = None
    split: str | None = None


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_json(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return _sha256_text(encoded)


def _prompt_template_hash(relative_path: str) -> str | None:
    path = ROOT / relative_path
    return _sha256_text(path.read_text(encoding="utf-8")) if path.is_file() else None


def validate_current_protocol() -> list[str]:
    """Return current fail-closed protocol/config errors; no inference is performed."""
    with CONFIG_PATH.open(encoding="utf-8") as handle:
        config = json.load(handle)
    protocol_text = PROTOCOL_PATH.read_text(encoding="utf-8")
    return validate_config(config, protocol_text)


def _validate_development_profile_attestation(
    experiment_input: Any, attestation: Mapping[str, Any] | None,
    token_budget_per_arm: int | None,
) -> list[str]:
    """Permit only hash-bound development-manifest rows in profiling mode."""
    errors = []
    manifest_path = ROOT / "E6/data/development_manifest_v2.json"
    try:
        raw = manifest_path.read_bytes()
        manifest = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        return ["development profile manifest unavailable: " + str(exc)]
    if not isinstance(attestation, Mapping):
        return ["development profile requires an explicit local attestation"]
    actual_manifest_sha = hashlib.sha256(raw).hexdigest()
    if attestation.get("scope") != "e6_development_token_profile_only":
        errors.append("profile attestation scope is invalid")
    if attestation.get("manifest_sha256") != actual_manifest_sha:
        errors.append("profile attestation manifest hash is invalid")
    if attestation.get("task_sha256") != _sha256_text(
        getattr(experiment_input, "domain_and_task", "")
    ):
        errors.append("profile attestation task hash does not match input task")
    if attestation.get("task_matches_profile_constant") is not True:
        errors.append("profile task does not match its verified generic constant")
    if type(token_budget_per_arm) is not int or token_budget_per_arm < 1:
        errors.append("profile requires an explicit temporary positive per-arm ceiling")
    if (not isinstance(manifest, Mapping)
            or manifest.get("split") != "DEVELOPMENT"
            or manifest.get("status") != "development_only_prepared_not_frozen"):
        errors.append("profile source manifest is not the prepared DEVELOPMENT manifest")
        return errors
    if getattr(experiment_input, "split", None) != "DEVELOPMENT":
        errors.append("development profile accepts DEVELOPMENT inputs only")
    input_id = getattr(experiment_input, "paper_id", None)
    matches = [row for row in manifest.get("inputs", [])
               if isinstance(row, Mapping) and row.get("paper_id") == input_id]
    if len(matches) != 1:
        errors.append("profile input ID is not a unique member of the development manifest")
    else:
        record = matches[0]
        if record.get("abstract") != getattr(experiment_input, "evidence", None):
            errors.append("profile evidence does not match the manifest abstract")
        provenance = getattr(experiment_input, "provenance", {})
        if not isinstance(provenance, Mapping) or provenance.get(
            "source_record_sha256"
        ) != record.get("source_record_sha256"):
            errors.append("profile source-record provenance does not match manifest")
    return errors


def serialize_provisional_envelope(envelope: Mapping[str, Any]) -> str:
    """Serialize in memory while refusing to label the provisional schema approved."""
    if envelope.get("schema_version") != PROVISIONAL_SCHEMA_VERSION:
        raise PipelineError("unexpected E6 envelope schema version")
    if envelope.get("schema_status") != "provisional_unapproved":
        raise PipelineError("E6 output schema must remain provisional and unapproved")
    return json.dumps(envelope, ensure_ascii=False, sort_keys=True, indent=2)


def _normalize_client_reply(reply: Any) -> tuple[str, dict[str, Any], dict[str, Any]]:
    if isinstance(reply, str):
        return reply, {}, {}
    if not isinstance(reply, Mapping):
        raise PipelineError("model client must return text or a response mapping")
    raw = reply.get("raw_response", reply.get("text"))
    if not isinstance(raw, str):
        raise PipelineError("model response mapping needs raw_response or text")
    usage = reply.get("usage") if isinstance(reply.get("usage"), Mapping) else {}
    accounting = {
        "input_tokens": reply.get("input_tokens", usage.get("input_tokens")),
        "output_tokens": reply.get("output_tokens", usage.get("output_tokens")),
        "total_tokens": reply.get("total_tokens", usage.get("total_tokens")),
        "cost": reply.get("cost", reply.get("cost_usd")),
        "latency_seconds": reply.get("latency_seconds"),
    }
    if accounting["total_tokens"] is None and all(
        type(accounting[key]) is int for key in ("input_tokens", "output_tokens")
    ):
        accounting["total_tokens"] = accounting["input_tokens"] + accounting["output_tokens"]
    metadata = reply.get("adapter_metadata")
    return raw, accounting, dict(metadata) if isinstance(metadata, Mapping) else {}


def _safe_accounting_total(calls: list[dict[str, Any]], key: str) -> dict[str, Any]:
    values = [row.get(key) for row in calls]
    valid = [value for value in values if type(value) in (int, float) and math.isfinite(value)]
    return {"sum": sum(valid) if valid else None, "reported_count": len(valid)}


def _block_arm(state: PipelineState, arm: str, reason: str) -> None:
    state.errors.append({"stage": "orchestration", "arm": arm, "error": reason})
    state.hypothesis_generations.append({
        "arm": arm, "status": "blocked", "questions": [], "hypotheses": [],
        "parsed_output": None, "raw_response": None, "attempt_history": [],
        "retry_policy": None, "errors": [reason],
    })


def _arm_status(state: PipelineState) -> tuple[str, bool, list[str]]:
    results = [row for row in state.hypothesis_generations if row.get("arm")]
    if not results:
        return "failed", True, ["generation produced no output record"]
    result = results[-1]
    status = result.get("status", "failed")
    failures = list(result.get("errors") or [])
    missing = status != "ok" or not isinstance(result.get("hypotheses"), list) or len(result["hypotheses"]) != 6
    if missing and not failures:
        failures.append("six-hypothesis output missing or invalid")
    return ("succeeded" if status == "ok" and not missing else
            "blocked" if status == "blocked" else "failed"), missing, failures


def _question_state_snapshot(question_state: PipelineState | None) -> Any:
    return question_state.as_dict() if isinstance(question_state, PipelineState) else None


def ordered_arm_outputs(input_set_id, seed, method):
    """Shared preparation precedes output calls; no ordering default for final mode."""
    if method == "fixed_configured_arm_order_v1":
        return list(ARMS)
    if method == "sha256_seeded_arm_order_v1" and type(seed) is int:
        return sorted(ARMS, key=lambda arm: (_sha256_text(f"E6-ARM-ORDER-v1|{seed}|{input_set_id}|{arm}"), arm))
    raise ValueError("final arm-output run order is unresolved or unsupported")


def run_seven_arms(
    experiment_input: ExperimentInput,
    settings: PipelineSettings,
    model_client: ModelCall,
    model_configuration: Mapping[str, Any],
    *,
    execution_mode: str = "development",
    question_state: PipelineState | None = None,
    d_empty_task_evidence_check=None,
    d_shuffled_assignment: Mapping[str, Any] | None = None,
    d_shuffled_assignment_batch: Mapping[str, Any] | None = None,
    development_manifest_records=None,
    canonical_source_records=None,
    expected_manifest_sha256: str | None = None,
    expected_source_corpus_sha256: str | None = None,
    d_shuffled_assignment_check=None,
    retry_prompt_builder=None,
    token_budget_per_arm: int | None = None,
    token_counter=None,
    development_profile_attestation: Mapping[str, Any] | None = None,
    train_execution_context=None,
    literature_execution_context=None,
) -> dict[str, Any]:
    """Run all arm workflows through existing generators after protocol validation.

    The output shape is an engineering envelope and is explicitly provisional.
    Selected QH inputs and D-shuffled donors must be supplied externally. The
    current repository protocol fails the execution gate while unresolved.
    """
    arm_output_order = list(ARMS)
    execution_order_policy = "legacy_fixed_arm_order_v1"
    if execution_mode == "development_profile":
        protocol_errors = _validate_development_profile_attestation(
            experiment_input, development_profile_attestation, token_budget_per_arm,
        )
    else:
        protocol_errors = validate_current_protocol()

    if token_budget_per_arm is None:
        try:
            configured_budget = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            token_budget_per_arm = configured_budget.get("inference_budget", {}).get(
                "tokens_per_input_set_arm"
            )
        except (OSError, json.JSONDecodeError):
            token_budget_per_arm = None
    try:
        token_budget = PerArmTokenBudget(
            getattr(experiment_input, "paper_id", ""), token_budget_per_arm,
            token_counter,
            model_prompt_counter=getattr(model_client, "count_prompt_tokens", None),
            # Preserve historical DEVELOPMENT accounting; assignment governs final runs.
            budget_unit="generated_tokens" if execution_mode == "final" else "prompt_plus_generation_tokens",
        )
    except TokenBudgetError as exc:
        token_budget = None
        protocol_errors.append("token budget configuration: " + str(exc))

    # Keep development and final execution strictly separated.
    if execution_mode not in ("development", "development_profile", "final"):
        protocol_errors.append("execution_mode must be development, development_profile, or final")
    elif execution_mode == "final":
        if train_execution_context is not None and literature_execution_context is not None:
            protocol_errors.append("exactly one source-bound execution context is allowed")
        if train_execution_context is not None:
            try:
                from inductive_execution import validate_train_execution_context
                train_execution_context = validate_train_execution_context(train_execution_context, experiment_input)
            except Exception as exc:
                protocol_errors.append("TRAIN execution integration: " + str(exc))
        elif literature_execution_context is not None:
            try:
                from literature_execution import validate_literature_execution_context
                literature_execution_context = validate_literature_execution_context(literature_execution_context, experiment_input)
            except Exception as exc:
                protocol_errors.append("literature execution integration: " + str(exc))
        else:
            protocol_errors.append("final execution is disabled without a source-bound TRAIN or literature execution context")
        protocol_errors.extend(validate_preregistration_git_commit(ROOT))
        if (getattr(experiment_input, "provenance", {}).get("dataset_id") == "hypobench-synthetic-election-level2"
                and (getattr(experiment_input, "split", None) != "TRAIN"
                     or getattr(experiment_input, "provenance", {}).get("evidence_split") != "TRAIN")):
            protocol_errors.append("R44: final hypotheses must use TRAIN evidence; legacy TEST-row generation is transductive")
        options = getattr(model_client, "generation_options", {})
        if not isinstance(options, Mapping) or type(options.get("num_ctx")) is not int or type(options.get("num_predict")) is not int:
            protocol_errors.append("final Gemma execution requires explicit context and output limits")
        try:
            final_config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            gen = final_config.get("generation", {})
            execution_order_policy = final_config.get("execution_replication", {}).get("run_order_method")
            arm_output_order = ordered_arm_outputs(getattr(experiment_input, "paper_id", ""), gen.get("seed"), execution_order_policy)
            from development_runtime_probe import validate_runtime_evidence
            protocol_errors.extend(validate_runtime_evidence(final_config, root=ROOT))
            if train_execution_context is not None:
                from inductive_execution import validate_frozen_train_context
                validate_frozen_train_context(train_execution_context, final_config, root=ROOT)
            elif literature_execution_context is not None:
                from literature_execution import validate_frozen_literature_context
                validate_frozen_literature_context(literature_execution_context, final_config, root=ROOT)
            expected_options = {"num_ctx": gen.get("context_limit"),
                                "num_predict": gen.get("max_output_tokens"),
                                "temperature": gen.get("temperature"), "top_p": gen.get("top_p"), "seed": gen.get("seed")}
            if not isinstance(options, Mapping) or any(v is None or options.get(k) != v for k, v in expected_options.items()):
                protocol_errors.append("final runtime decoding/context/output options differ from frozen configuration")
            if getattr(model_client, "model", None) != gen.get("model"):
                protocol_errors.append("final runtime model differs from frozen configuration")
            if token_budget_per_arm != final_config.get("inference_budget", {}).get("tokens_per_input_set_arm"):
                protocol_errors.append("final generated-token cap override differs from frozen configuration")
        except (OSError, ValueError) as exc:
            protocol_errors.append("cannot verify final runtime against frozen configuration: " + str(exc))
        if not isinstance(options, Mapping) or getattr(model_client, "preflight_context_limit", None) != options.get("num_ctx"):
            protocol_errors.append("final Gemma count preflight must use the same verified context as generation")


    input_error = None
    if not isinstance(experiment_input, ExperimentInput):
        input_error = "experiment_input must be an ExperimentInput"
    elif not isinstance(experiment_input.paper_id, str) or not experiment_input.paper_id.strip():
        input_error = "paper_id is required"
    elif not isinstance(experiment_input.domain_and_task, str) or not experiment_input.domain_and_task.strip():
        input_error = "domain_and_task is required"
    elif not isinstance(experiment_input.evidence, str):
        input_error = "evidence must be a string"
    elif (
        execution_mode in ("development", "development_profile")
        and experiment_input.split not in (None, "DEVELOPMENT")
    ):
        input_error = "development modes accept only DEVELOPMENT split inputs"
    elif not isinstance(experiment_input.provenance, Mapping):
        input_error = "input provenance must be a mapping"
    elif experiment_input.reference_evidence is not None and (
        not isinstance(experiment_input.reference_evidence, (tuple, list))
        or any(not isinstance(item, str) for item in experiment_input.reference_evidence)
    ):
        input_error = "reference_evidence must be a sequence of strings when supplied"

    if input_error:
        protocol_errors = list(protocol_errors) + [input_error]
        original = experiment_input
        paper_id = getattr(original, "paper_id", "")
        task = getattr(original, "domain_and_task", "")
        evidence = getattr(original, "evidence", "")
        provenance = getattr(original, "provenance", {})
        experiment_input = ExperimentInput(
            paper_id=paper_id if isinstance(paper_id, str) else "",
            domain_and_task=task if isinstance(task, str) else "",
            evidence=evidence if isinstance(evidence, str) else "",
            provenance=dict(provenance) if isinstance(provenance, Mapping) else {},
            reference_evidence=getattr(original, "reference_evidence", None),
            split=getattr(original, "split", None),
        )

    envelope: dict[str, Any] = {
        "schema_version": PROVISIONAL_SCHEMA_VERSION,
        "schema_status": "provisional_unapproved",
        "experiment_status": "blocked",
        "execution_mode": execution_mode,
        "development_profile_only": execution_mode == "development_profile",
        "train_execution_context_sha256": getattr(train_execution_context, "context_sha256", None),
        "literature_execution_context_sha256": getattr(literature_execution_context, "context_sha256", None),
        "paper_id": getattr(experiment_input, "paper_id", None),
        "input_provenance": dict(experiment_input.provenance),
        "protocol_validation_errors": list(protocol_errors),
        "model_configuration": dict(model_configuration),
        "arms": {},
        "execution_manifest": [],
        "execution_arm_output_order": arm_output_order,
        "execution_order_policy": execution_order_policy,
        "shared_preparation_order": "before_arm_output_calls",
        "token_budget_configuration": {
            "tokens_per_arm": token_budget_per_arm,
            "tokenizer_id": getattr(token_counter, "tokenizer_id", None),
            "counting_scope": ("generated_tokens; prompt tokens recorded separately" if execution_mode == "final"
                               else "historical development: prompt plus generated response"),
            "configured": token_budget is not None,
        },
    }

    if protocol_errors:
        for arm in ARMS:
            state = PipelineState()
            _block_arm(state, arm, "protocol or input validation gate did not pass")
            entry = _build_arm_entry(
                experiment_input, arm, state, [], model_configuration,
                question_state, blocked=True, failure_information=list(protocol_errors),
            )
            envelope["arms"][arm] = entry
            envelope["execution_manifest"].append(entry["manifest"])
        envelope["call_accounting"] = {
            "call_count": 0,
            "input_tokens": {"sum": None, "reported_count": 0},
            "output_tokens": {"sum": None, "reported_count": 0},
            "total_tokens": {"sum": None, "reported_count": 0},
            "cost": {"sum": None, "reported_count": 0},
            "calls": [],
        }
        envelope["token_budget_accounting"] = {
            arm: (token_budget.arm_report(arm) if token_budget else {
                "input_set_id": envelope["paper_id"], "arm": arm,
                "budget_tokens": token_budget_per_arm, "tokens_used": None,
                "tokens_remaining": None, "within_budget": False,
                "budget_status": "unconfigured",
            }) for arm in ARMS
        }
        return envelope

    preparation_calls: list[dict[str, Any]] = []
    question_preparation_reused = False

    if question_state is not None:
        prepared_question_state = question_state

        if not isinstance(question_state, PipelineState):
            prepared_question_state = PipelineState()
            prepared_question_state.errors.append({
                "stage": "qh_selection_preparation",
                "error": "supplied question_state must be a PipelineState",
            })
        else:
            provenance = question_state.preparation_provenance
            expected_task_hash = _sha256_text(experiment_input.domain_and_task)
            expected_evidence_hash = _sha256_text(experiment_input.evidence)

            valid_state = (
                provenance.get("schema_version") == "e6-qh-selection-preparation-v1"
                and provenance.get("input_set_id") == experiment_input.paper_id
                and provenance.get("task_sha256") == expected_task_hash
                and provenance.get("evidence_sha256") == expected_evidence_hash
                and provenance.get("status") == "ok"
                and question_state.candidate_generation_complete is True
                and len(question_state.candidate_records) == 6
                and len(question_state.representatives) >= 3
                and question_state.selections.get("QH-sel", {}).get("status") == "ok"
                and question_state.selections.get("QH-rand", {}).get("status") == "ok"
                and len(question_state.selections.get("QH-sel", {}).get(
                    "selected_candidate_ids", []
                )) == 3
                and len(question_state.selections.get("QH-rand", {}).get(
                    "selected_candidate_ids", []
                )) == 3
            )

            if valid_state:
                try:
                    token_budget.charge_preexisting_shared_calls(question_state.model_calls)
                    question_preparation_reused = True
                    preparation_calls = list(question_state.model_calls)
                except TokenBudgetError as exc:
                    prepared_question_state.errors.append({
                        "stage": "qh_selection_preparation",
                        "error": "question-state reuse rejected by token budget: " + str(exc),
                    })
                    prepared_question_state.preparation_provenance["status"] = "token_budget_blocked"
            else:
                question_state.errors.append({
                    "stage": "qh_selection_preparation",
                    "error": (
                        "supplied question_state failed input provenance or "
                        "preparation completeness checks"
                    ),
                })
                question_state.preparation_provenance["status"] = "invalid_reuse"

    else:
        def preparation_client(stage, prompt):
            record = {
                "stage": stage,
                "prompt_sha256": _sha256_text(prompt),
                "prompt_characters": len(prompt),
                "status": "started",
            }
            try:
                reply = token_budget.invoke(model_client, stage, prompt)
                raw, accounting, metadata = _normalize_client_reply(reply)
                record.update(accounting)
                record["adapter_metadata"] = metadata
                record["status"] = "returned"
                preparation_calls.append(record)
                return raw
            except Exception as exc:
                record.update({"status": "failed", "error": str(exc)})
                error_metadata = getattr(exc, "audit_metadata", None)
                if isinstance(error_metadata, Mapping):
                    record["adapter_metadata"] = dict(error_metadata)
                    for key in ("input_tokens", "output_tokens", "total_tokens"):
                        if type(error_metadata.get(key)) is int:
                            record[key] = error_metadata[key]
                preparation_calls.append(record)
                raise

        prepared_question_state = prepare_qh_selection_arms(
            PipelineState(), settings, preparation_client,
            experiment_input.paper_id,
            experiment_input.domain_and_task,
            experiment_input.evidence,
        )

    all_call_records = list(preparation_calls)
    for arm in arm_output_order:
        state = PipelineState()
        arm_calls: list[dict[str, Any]] = []

        def tracked_call(stage: str, prompt: str) -> str:
            call_index = len(arm_calls) + 1
            call_record = {
                "stage": stage,
                "call_index": call_index,
                "prompt_sha256": _sha256_text(prompt),
                "prompt_characters": len(prompt),
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
                "cost": None,
                "latency_seconds": None,
                "status": "started",
            }
            try:
                reply = token_budget.invoke(model_client, stage, prompt)
                raw, accounting, adapter_metadata = _normalize_client_reply(reply)
                call_record.update(accounting)
                if adapter_metadata:
                    call_record["adapter_metadata"] = adapter_metadata
                call_record["status"] = "returned"
                arm_calls.append(call_record)
                return raw
            except Exception as exc:
                call_record.update({"status": "failed", "error": str(exc)})
                error_metadata = getattr(exc, "audit_metadata", None)
                if isinstance(error_metadata, Mapping):
                    call_record["adapter_metadata"] = dict(error_metadata)
                    call_record["latency_seconds"] = error_metadata.get("latency_seconds")
                    for key in ("input_tokens", "output_tokens", "total_tokens"):
                        if type(error_metadata.get(key)) is int:
                            call_record[key] = error_metadata[key]
                arm_calls.append(call_record)
                raise

        try:
            if arm in ("D", "QH", "HQ"):
                generate_direct_arm(
                    state, arm, tracked_call, experiment_input.domain_and_task,
                    experiment_input.evidence, settings,
                    retry_prompt_builder=retry_prompt_builder,
                )
            elif arm in ("QH-sel", "QH-rand"):
                if prepared_question_state.preparation_provenance.get("status") != "ok":
                    raise PipelineError(f"{arm} blocked because shared question preparation failed")
                selected = selected_questions_for_arm(prepared_question_state, arm)
                generate_question_hypotheses(
                    state, arm, selected, tracked_call, experiment_input.domain_and_task,
                    experiment_input.evidence, settings,
                    retry_prompt_builder=retry_prompt_builder,
                )
            elif execution_mode == "final" and literature_execution_context is not None and arm in ("D-empty", "D-shuffled"):
                from literature_execution import generate_literature_control
                generate_literature_control(state, arm, experiment_input, literature_execution_context,
                    tracked_call, settings, retry_prompt_builder)
            elif execution_mode == "final" and train_execution_context is not None and arm in ("D-empty", "D-shuffled"):
                from inductive_execution import generate_train_control
                generate_train_control(state, arm, experiment_input, train_execution_context,
                    tracked_call, settings, retry_prompt_builder)
            elif arm == "D-empty":
                generate_d_empty(
                    state, experiment_input.paper_id, experiment_input.domain_and_task,
                    tracked_call, settings, d_empty_task_evidence_check,
                    original_abstract=experiment_input.evidence,
                    reference_evidence=experiment_input.reference_evidence,
                    development_profile_only=execution_mode == "development_profile",
                    retry_prompt_builder=retry_prompt_builder,
                )
            else:  # D-shuffled: donor evidence/assignment are external.
                if (not development_manifest_records or not canonical_source_records
                        or not expected_manifest_sha256 or not expected_source_corpus_sha256):
                    raise PipelineError("D-shuffled requires verified development source records and expected hashes")
                if not isinstance(d_shuffled_assignment, Mapping):
                    raise PipelineError("D-shuffled requires externally assigned donor evidence and provenance")
                if not isinstance(d_shuffled_assignment_batch, Mapping):
                    raise PipelineError("D-shuffled requires a validated assignment batch")
                donor_id = d_shuffled_assignment.get(
                    "donor_paper_id", d_shuffled_assignment.get("donor_id"),
                )
                assignment_provenance = d_shuffled_assignment.get(
                    "assignment_provenance", d_shuffled_assignment,
                )
                matching_assignment = next((row for row in d_shuffled_assignment_batch.get("assignments", [])
                    if isinstance(row, Mapping) and row.get("recipient_id") == experiment_input.paper_id), None)
                if matching_assignment is None or dict(matching_assignment) != dict(assignment_provenance):
                    raise PipelineError("D-shuffled assignment row does not match recipient assignment")
                generate_d_shuffled(
                    state, experiment_input.paper_id,
                    donor_id,
                    experiment_input.domain_and_task,
                    d_shuffled_assignment.get("donor_evidence"),
                    assignment_provenance,
                    tracked_call, settings, d_shuffled_assignment_check,
                    recipient_split=experiment_input.split,
                    assignment_batch=d_shuffled_assignment_batch,
                    # Pass the complete recipient cohort: batch validation
                    # must verify coverage across all assigned recipients.
                    recipient_records=development_manifest_records,
                    development_records=development_manifest_records,
                    canonical_source_records=canonical_source_records,
                    expected_manifest_sha256=expected_manifest_sha256,
                    expected_source_corpus_sha256=expected_source_corpus_sha256,
                    retry_prompt_builder=retry_prompt_builder,
                )
        except Exception as exc:
            _block_arm(state, arm, str(exc))

        entry = _build_arm_entry(
            experiment_input, arm, state, arm_calls, model_configuration,
            prepared_question_state, blocked=False,
            failure_information=[row.get("error", "") for row in state.errors],
            shared_preparation_calls=(
                preparation_calls if arm in ("QH-sel", "QH-rand") else []
            ),
        )
        envelope["arms"][arm] = entry
        envelope["execution_manifest"].append(entry["manifest"])
        all_call_records.extend(arm_calls)
        entry["token_budget_accounting"] = token_budget.arm_report(arm)
        entry["manifest"]["token_budget_accounting"] = entry["token_budget_accounting"]

    statuses = [entry["execution_status"] for entry in envelope["arms"].values()]
    success_count = sum(status == "succeeded" for status in statuses)
    if success_count == len(ARMS):
        envelope["experiment_status"] = "completed"
    elif success_count:
        envelope["experiment_status"] = "partial_failure"
    else:
        envelope["experiment_status"] = "failed"
    envelope["call_accounting"] = {
        "call_count": len(all_call_records),
        "input_tokens": _safe_accounting_total(all_call_records, "input_tokens"),
        "output_tokens": _safe_accounting_total(all_call_records, "output_tokens"),
        "total_tokens": _safe_accounting_total(all_call_records, "total_tokens"),
        "cost": _safe_accounting_total(all_call_records, "cost"),
        "calls": all_call_records,
    }
    envelope["question_preparation"] = _question_state_snapshot(prepared_question_state)
    envelope["question_preparation_reused"] = question_preparation_reused
    envelope["token_budget_accounting"] = {
        arm: token_budget.arm_report(arm) for arm in ARMS
    }
    return envelope


def _build_arm_entry(
    experiment_input: ExperimentInput,
    arm: str,
    state: PipelineState,
    calls: list[dict[str, Any]],
    model_configuration: Mapping[str, Any],
    question_state: PipelineState | None,
    *,
    blocked: bool,
    failure_information: list[str],
    shared_preparation_calls: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    generation = next(
        (item for item in reversed(state.hypothesis_generations) if item.get("arm") == arm),
        None,
    )
    if blocked:
        status, missing = "blocked", True
    else:
        status, missing, inferred_failures = _arm_status(state)
        failure_information = [item for item in failure_information if item] + inferred_failures
    if arm == "D-empty":
        evidence = ""
    elif arm == "D-shuffled":
        evidence = (generation or {}).get("control_provenance", {}).get("evidence_input", "")
    else:
        evidence = experiment_input.evidence

    task_hash = _sha256_text(experiment_input.domain_and_task)
    evidence_hash = _sha256_text(evidence)
    input_payload: dict[str, Any] = {
        "paper_id": experiment_input.paper_id,
        "domain_and_task": experiment_input.domain_and_task,
        "provenance": dict(experiment_input.provenance),
    }
    donor_paper_id = None
    if generation and generation.get("control_provenance"):
        control = generation["control_provenance"]
        donor_paper_id = control.get("donor_paper_id")
        if "evidence_absence_check" in control:
            input_payload["evidence_absence_check"] = control["evidence_absence_check"]
        if donor_paper_id:
            input_payload["donor_paper_id"] = donor_paper_id
    if arm in ("QH-sel", "QH-rand") and isinstance(question_state, PipelineState):
        try:
            input_payload["selected_questions"] = selected_questions_for_arm(question_state, arm)
        except PipelineError:
            input_payload["selected_questions"] = None
    input_hash = _sha256_json(input_payload)
    prompt_hashes = [row["prompt_sha256"] for row in calls]
    prompt_template_hash = _prompt_template_hash(PROMPT_SOURCES[arm])
    manifest = {
        "paper_id": experiment_input.paper_id,
        "arm": arm,
        "input_provenance": dict(experiment_input.provenance),
        "input_sha256": input_hash,
        "task_sha256": task_hash,
        "evidence_sha256": evidence_hash,
        "prompt_version": PROMPT_SOURCES[arm],
        "prompt_template_sha256": prompt_template_hash,
        "prompt_sha256": prompt_hashes[0] if prompt_hashes else None,
        "prompt_sha256_by_call": prompt_hashes,
        "donor_paper_id": donor_paper_id,
        "model_configuration": dict(model_configuration),
        "execution_status": status,
        "output_reference": (
            f"inline:{experiment_input.paper_id}:{arm}"
            if generation and generation.get("status") != "blocked" else None
        ),
        "failure_information": failure_information,
        "missing_output": missing,
        "calls": calls,
    }
    artifacts: dict[str, Any] = {
        "generation": generation,
        "raw_responses": state.raw_responses,
        "errors": state.errors,
    }
    if arm in ("QH-sel", "QH-rand"):
        artifacts["question_selection_state"] = _question_state_snapshot(question_state)

    # Shared preparation is attributed to both question-first arms for
    # fully-loaded comparisons, but remains counted only once globally.
    shared_calls = list(shared_preparation_calls or [])
    fully_loaded_calls = list(calls) + shared_calls

    return {
        "arm": arm,
        "execution_status": status,
        "missing_output": missing,
        "output": generation,
        "output_reference": manifest["output_reference"],
        "intermediate_artifacts": artifacts,
        "call_accounting": {
            "call_count": len(calls),
            "input_tokens": _safe_accounting_total(calls, "input_tokens"),
            "output_tokens": _safe_accounting_total(calls, "output_tokens"),
            "total_tokens": _safe_accounting_total(calls, "total_tokens"),
            "cost": _safe_accounting_total(calls, "cost"),
            "calls": calls,
        },
        "shared_question_preparation_accounting": (
            {
                "accounting_scope": "shared_non_additive",
                "call_count": len(shared_calls),
                "input_tokens": _safe_accounting_total(shared_calls, "input_tokens"),
                "output_tokens": _safe_accounting_total(shared_calls, "output_tokens"),
                "total_tokens": _safe_accounting_total(shared_calls, "total_tokens"),
                "cost": _safe_accounting_total(shared_calls, "cost"),
                "calls": shared_calls,
            }
            if arm in ("QH-sel", "QH-rand") else None
        ),
        "fully_loaded_call_accounting": {
            "accounting_scope": "direct_plus_shared_preparation",
            "shared_cost_is_non_additive_across_arms": True,
            "call_count": len(fully_loaded_calls),
            "input_tokens": _safe_accounting_total(fully_loaded_calls, "input_tokens"),
            "output_tokens": _safe_accounting_total(fully_loaded_calls, "output_tokens"),
            "total_tokens": _safe_accounting_total(fully_loaded_calls, "total_tokens"),
            "cost": _safe_accounting_total(fully_loaded_calls, "cost"),
            "calls": fully_loaded_calls,
        },
        "manifest": manifest,
    }
