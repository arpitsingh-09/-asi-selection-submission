"""Evaluation plumbing for E6.

No metric, comparison schedule, model, threshold, or statistical policy is
selected here. Callers must inject approved evaluators and preserve this
module's input/output/provenance records. This module never executes by itself.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import re
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
PAIRWISE_PROMPT = ROOT / "prompts/e6/11_judge_pairwise.txt"
QUESTION_TYPE_PROMPT = ROOT / "prompts/e6/10_question_type.txt"
TARGET_EXTRACTION_PROMPT = ROOT / "prompts/e6/09_target_extraction.txt"
ARMS = ("D", "QH", "QH-sel", "QH-rand", "HQ", "D-empty", "D-shuffled")


class EvaluationError(ValueError):
    """Invalid input, unavailable policy, or malformed evaluator response."""


def _hash_json(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _read_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _render(template: str, values: Mapping[str, str]) -> str:
    result = template
    for key, value in values.items():
        result = result.replace("{{" + key + "}}", value)
    remaining = re.findall(r"\{\{[A-Z0-9_]+\}\}", result)
    if remaining:
        raise EvaluationError("unfilled prompt placeholders: " + ", ".join(remaining))
    return result


def _parse_json(raw: str, stage: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw)
    except (TypeError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"{stage}: malformed JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise EvaluationError(f"{stage}: response must be a JSON object")
    return parsed


def _unpack_model_reply(reply: Any) -> tuple[str, dict[str, Any]]:
    if isinstance(reply, str):
        return reply, {}
    if not isinstance(reply, Mapping):
        raise EvaluationError("model client must return raw text or a response mapping")
    raw = reply.get("raw_response", reply.get("text"))
    if not isinstance(raw, str):
        raise EvaluationError("model response mapping must include raw_response or text")
    metadata = {key: value for key, value in reply.items() if key not in ("raw_response", "text")}
    return raw, metadata


def evaluation_record(
    *, stage: str, input_set_id: str, evaluation_input: Mapping[str, Any],
    provenance: Mapping[str, Any], raw_output: Any = None,
    parsed_output: Any = None, error: str | None = None,
    attempts: Sequence[Mapping[str, Any]] = (), status: str | None = None,
    model_response_metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Common audit wrapper retaining exact inputs, outputs, and attempts."""
    if not isinstance(input_set_id, str) or not input_set_id.strip():
        raise EvaluationError("input_set_id is required")
    if status is None:
        status = "failed" if error else "succeeded"
    if status not in ("succeeded", "failed", "blocked"):
        raise EvaluationError("invalid evaluation status")
    return {
        "schema_version": "e6-evaluation-provisional-v1",
        "schema_status": "provisional_unapproved",
        "stage": stage,
        "input_set_id": input_set_id,
        "evaluation_input": dict(evaluation_input),
        "evaluation_input_sha256": _hash_json(evaluation_input),
        "provenance": dict(provenance),
        "raw_output": raw_output,
        "parsed_output": parsed_output,
        "model_response_metadata": dict(model_response_metadata or {}),
        "attempts": [dict(a) for a in attempts],
        "error": error,
        "status": status,
    }


def _require_evaluator(evaluator: Callable[..., Any] | None, name: str):
    if not callable(evaluator):
        raise EvaluationError(f"{name} policy/evaluator is unresolved and must be injected")
    return evaluator


def _require_input_set_id(input_set_id: str) -> str:
    if not isinstance(input_set_id, str) or not input_set_id.strip():
        raise EvaluationError("input_set_id is required")
    return input_set_id


def evaluate_reconstruction(
    input_set_id: str, generated: Mapping[str, Any], reference: Mapping[str, Any],
    matcher: Callable[[Mapping[str, Any], Mapping[str, Any]], Any] | None,
    *, reference_provenance: Mapping[str, Any], policy_id: str | None,
) -> dict[str, Any]:
    """Score generated/reference question and hypothesis records via approved matcher."""
    scorer = _require_evaluator(matcher, "reconstruction matching")
    source = {"generated": dict(generated), "reference": dict(reference)}
    attempts: list[dict[str, Any]] = []
    try:
        raw = scorer(dict(generated), dict(reference))
        attempts.append({"attempt": 1, "status": "returned", "raw": raw})
        return evaluation_record(
            stage="reconstruction", input_set_id=input_set_id,
            evaluation_input=source,
            provenance={"reference": dict(reference_provenance), "policy_id": policy_id},
            raw_output=raw, parsed_output=raw, attempts=attempts,
        )
    except Exception as exc:
        attempts.append({"attempt": 1, "status": "failed", "error": str(exc)})
        return evaluation_record(
            stage="reconstruction", input_set_id=input_set_id,
            evaluation_input=source,
            provenance={"reference": dict(reference_provenance), "policy_id": policy_id},
            error=str(exc), attempts=attempts,
        )


def evaluate_reconstruction_best_similarity(
    input_set_id: str, generated_questions: Sequence[str], generated_hypotheses: Sequence[str],
    reference: Mapping[str, Any], similarity_evaluator: Callable[[str, str], Any] | None,
    *, reference_provenance: Mapping[str, Any], policy_id: str | None,
) -> dict[str, Any]:
    """Record each candidate similarity and the best match for each target field."""
    if not isinstance(reference, Mapping):
        raise EvaluationError("reference targets must be an object")
    scorer = _require_evaluator(similarity_evaluator, "reconstruction similarity")
    targets = {
        "research_question": reference.get("research_question"),
        "main_hypothesis": reference.get("main_hypothesis"),
    }
    candidates = {
        "research_question": list(generated_questions) if not isinstance(
            generated_questions, (str, bytes)
        ) else [],
        "main_hypothesis": list(generated_hypotheses) if not isinstance(
            generated_hypotheses, (str, bytes)
        ) else [],
    }
    _require_input_set_id(input_set_id)
    for field, target in targets.items():
        if not isinstance(target, str) or not target.strip():
            raise EvaluationError(f"reference {field} must be a nonempty string")
        if not candidates[field] or any(not isinstance(value, str) or not value.strip()
                                        for value in candidates[field]):
            raise EvaluationError(f"generated {field} candidates must be nonempty strings")
    inputs = {"generated_questions": candidates["research_question"],
              "generated_hypotheses": candidates["main_hypothesis"], "reference": dict(reference)}
    attempts = []
    scores: dict[str, list[float]] = {}
    try:
        for field, target in targets.items():
            scores[field] = []
            for index, candidate in enumerate(candidates[field]):
                value = scorer(candidate, target)
                if type(value) not in (int, float) or not math.isfinite(value):
                    raise EvaluationError("similarity evaluator must return a finite number")
                scores[field].append(float(value))
                attempts.append({"field": field, "candidate_index": index,
                                 "status": "returned", "similarity": float(value)})
        parsed = {
            "research_question": {"best_similarity": max(scores["research_question"]),
                                  "candidate_similarities": scores["research_question"]},
            "main_hypothesis": {"best_similarity": max(scores["main_hypothesis"]),
                                "candidate_similarities": scores["main_hypothesis"]},
        }
        return evaluation_record(
            stage="reconstruction_best_similarity", input_set_id=input_set_id,
            evaluation_input=inputs,
            provenance={"reference": dict(reference_provenance), "policy_id": policy_id,
                        "similarity_evaluator": "caller_supplied"},
            raw_output=scores, parsed_output=parsed, attempts=attempts,
        )
    except Exception as exc:
        attempts.append({"status": "failed", "error": str(exc)})
        return evaluation_record(
            stage="reconstruction_best_similarity", input_set_id=input_set_id,
            evaluation_input=inputs,
            provenance={"reference": dict(reference_provenance), "policy_id": policy_id,
                        "similarity_evaluator": "caller_supplied"},
            raw_output=scores or None, attempts=attempts, error=str(exc),
        )


def evaluate_same_question_judgments(
    input_set_id: str, generated_questions: Sequence[str], reference_question: str,
    same_question_evaluator: Callable[[str, str], Any] | None,
    *, reference_provenance: Mapping[str, Any], policy_id: str | None,
) -> dict[str, Any]:
    """Apply the configured same-question evaluator separately to each candidate."""
    _require_input_set_id(input_set_id)
    judge = _require_evaluator(same_question_evaluator, "same-question judgment")
    if not isinstance(reference_question, str) or not reference_question.strip():
        raise EvaluationError("reference_question is required")
    if isinstance(generated_questions, (str, bytes)) or not isinstance(
        generated_questions, Sequence
    ) or not generated_questions or any(
        not isinstance(value, str) or not value.strip() for value in generated_questions
    ):
        raise EvaluationError("generated_questions must contain nonempty strings")
    inputs = {"generated_questions": list(generated_questions),
              "reference_question": reference_question}
    decisions, attempts = [], []
    try:
        for index, question in enumerate(generated_questions):
            value = judge(question, reference_question)
            if type(value) is not bool:
                raise EvaluationError("same-question evaluator must return Boolean decisions")
            decisions.append({"candidate_index": index, "same_question": value})
            attempts.append({"candidate_index": index, "status": "returned", "same_question": value})
        return evaluation_record(
            stage="same_question_judgment", input_set_id=input_set_id,
            evaluation_input=inputs,
            provenance={"reference": dict(reference_provenance), "policy_id": policy_id,
                        "decision_source": "configured_evaluator"},
            raw_output=decisions, parsed_output=decisions, attempts=attempts,
        )
    except Exception as exc:
        attempts.append({"status": "failed", "error": str(exc)})
        return evaluation_record(
            stage="same_question_judgment", input_set_id=input_set_id,
            evaluation_input=inputs,
            provenance={"reference": dict(reference_provenance), "policy_id": policy_id,
                        "decision_source": "configured_evaluator"},
            raw_output=decisions or None, attempts=attempts, error=str(exc),
        )
def extract_reference_targets(
    input_set_id: str, target_paper_text: str,
    model_client: Callable[[str, str], Any], *, model_configuration: Mapping[str, Any],
) -> dict[str, Any]:
    """Extract reference question/hypothesis with the existing prompt, preserving raw reply.

    The extraction is a reference annotation interface, not validated gold truth;
    downstream use still requires an approved source and adjudication policy.
    """
    template = _read_prompt(TARGET_EXTRACTION_PROMPT)
    rendered = _render(template, {"TARGET_PAPER_TEXT": target_paper_text})
    attempts: list[dict[str, Any]] = []
    raw: str | None = None
    reply_metadata: dict[str, Any] = {}
    try:
        reply = model_client("reference_target_extraction", rendered)
        raw, reply_metadata = _unpack_model_reply(reply)
        parsed = _parse_json(raw, "reference target extraction")
        required_fields = {
            "research_question", "research_question_explicit",
            "main_hypothesis", "main_hypothesis_explicit",
        }
        if set(parsed) != required_fields:
            raise EvaluationError(
                "reference target extraction must return exactly the four documented fields"
            )
        for field in ("research_question", "main_hypothesis"):
            if parsed[field] is not None and (
                not isinstance(parsed[field], str) or not parsed[field].strip()
            ):
                raise EvaluationError(f"{field} must be a nonempty string or null")
        for field in ("research_question_explicit", "main_hypothesis_explicit"):
            if type(parsed.get(field)) is not bool:
                raise EvaluationError(f"{field} must be Boolean")
        attempts.append({"attempt": 1, "status": "returned", "raw": raw})
        return evaluation_record(
            stage="reference_target_extraction", input_set_id=input_set_id,
            evaluation_input={"target_paper_text": target_paper_text, "rendered_prompt": rendered},
            provenance={"prompt_path": str(TARGET_EXTRACTION_PROMPT.relative_to(ROOT)),
                        "prompt_sha256": hashlib.sha256(template.encode()).hexdigest(),
                        "model_configuration": dict(model_configuration),
                        "gold_truth_status": "requires independent validation"},
            raw_output=raw, parsed_output=parsed, attempts=attempts,
            model_response_metadata=reply_metadata,
        )
    except Exception as exc:
        attempts.append({"attempt": 1, "status": "failed", "raw": raw, "error": str(exc)})
        return evaluation_record(
            stage="reference_target_extraction", input_set_id=input_set_id,
            evaluation_input={"target_paper_text": target_paper_text, "rendered_prompt": rendered},
            provenance={"prompt_path": str(TARGET_EXTRACTION_PROMPT.relative_to(ROOT)),
                        "prompt_sha256": hashlib.sha256(template.encode()).hexdigest(),
                        "model_configuration": dict(model_configuration),
                        "gold_truth_status": "requires independent validation"},
            raw_output=raw, attempts=attempts, error=str(exc),
            model_response_metadata=reply_metadata,
        )


def _generated_texts(values: Any, field: str) -> list[str]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        return []
    output = []
    for row in values:
        value = row.get("text") if isinstance(row, Mapping) else row
        if isinstance(value, str) and value.strip():
            output.append(value)
    return output


def evaluate_literature_seven_arm_outputs(
    input_set_id: str, arm_outputs: Mapping[str, Any], target_extraction: Mapping[str, Any], *,
    similarity_evaluator: Callable[[str, str], Any] | None,
    same_question_evaluator: Callable[[str, str], Any] | None,
    similarity_policy_id: str | None, same_question_policy_id: str | None,
    reference_provenance: Mapping[str, Any],
) -> dict[str, Any]:
    """Evaluate literature reconstruction for all seven arm outputs.

    The caller injects the approved similarity and same-question policies.
    Missing target annotations, generated questions, or failed arms are stored
    as blocked metric records rather than omitted or replaced with scores.
    """
    _require_input_set_id(input_set_id)
    if not isinstance(arm_outputs, Mapping) or set(arm_outputs) != set(ARMS):
        raise EvaluationError("arm_outputs must contain exactly all seven E6 arms")
    if not isinstance(target_extraction, Mapping):
        raise EvaluationError("target_extraction must be an object")
    parsed_target = target_extraction.get("parsed_output", target_extraction)
    if not isinstance(parsed_target, Mapping):
        raise EvaluationError("target_extraction parsed_output must be an object")
    if not isinstance(reference_provenance, Mapping):
        raise EvaluationError("reference_provenance must be an object")

    records: list[dict[str, Any]] = []
    for arm in ARMS:
        arm_entry = arm_outputs[arm]
        if not isinstance(arm_entry, Mapping):
            raise EvaluationError(f"arm {arm} output must be an object")
        generation = arm_entry.get("output", arm_entry.get("generation", arm_entry))
        generation = generation if isinstance(generation, Mapping) else {}
        arm_status = arm_entry.get("execution_status", generation.get("status"))
        arm_provenance = {
            **dict(reference_provenance), "arm": arm,
            "arm_execution_status": arm_status,
            "arm_manifest": dict(arm_entry.get("manifest", {}))
            if isinstance(arm_entry.get("manifest"), Mapping) else {},
            "target_extraction_record_sha256": _hash_json(target_extraction),
        }
        questions = _generated_texts(generation.get("questions"), "questions")
        hypotheses = _generated_texts(generation.get("hypotheses"), "hypotheses")
        for field, candidates in (("research_question", questions),
                                  ("main_hypothesis", hypotheses)):
            target = parsed_target.get(field)
            available = (arm_status in ("succeeded", "ok") and
                         isinstance(target, str) and bool(target.strip()) and
                         bool(candidates) and callable(similarity_evaluator))
            inputs = {"arm": arm, "field": field, "candidates": candidates,
                      "reference": target}
            attempts = []
            scores = []
            error = None
            if not available:
                reasons = []
                if arm_status not in ("succeeded", "ok"):
                    reasons.append("arm generation did not succeed")
                if not isinstance(target, str) or not target.strip():
                    reasons.append(f"reference {field} is unavailable")
                if not candidates:
                    reasons.append(f"generated {field} candidates are unavailable")
                if not callable(similarity_evaluator):
                    reasons.append("similarity evaluator is unavailable")
                error = "; ".join(reasons)
            else:
                try:
                    for index, candidate in enumerate(candidates):
                        score = similarity_evaluator(candidate, target)
                        if type(score) not in (int, float) or not math.isfinite(score):
                            raise EvaluationError("similarity evaluator must return a finite number")
                        scores.append(float(score))
                        attempts.append({"candidate_index": index, "status": "returned",
                                         "similarity": float(score)})
                except Exception as exc:
                    error = str(exc)
                    attempts.append({"status": "failed", "error": error})
            parsed = ({"best_similarity": max(scores), "candidate_similarities": scores}
                      if scores and error is None else None)
            records.append(evaluation_record(
                stage="literature_reconstruction_similarity", input_set_id=input_set_id,
                evaluation_input=inputs, provenance={
                    **arm_provenance, "policy_id": similarity_policy_id,
                    "similarity_evaluator": "caller_supplied", "field_status":
                    "scored" if parsed is not None else "unavailable_or_failed",
                }, raw_output=scores or None, parsed_output=parsed, error=error,
                attempts=attempts, status=("succeeded" if parsed is not None else
                                           "failed" if available else "blocked"),
            ))

        reference_question = parsed_target.get("research_question")
        question_error = None
        question_record = None
        if arm_status not in ("succeeded", "ok"):
            question_error = "arm generation did not succeed"
        elif not isinstance(reference_question, str) or not reference_question.strip():
            question_error = "reference research_question is unavailable"
        elif not questions:
            question_error = "generated research_question candidates are unavailable"
        elif not callable(same_question_evaluator):
            question_error = "same-question evaluator is unavailable"
        else:
            question_record = evaluate_same_question_judgments(
                input_set_id, questions, reference_question, same_question_evaluator,
                reference_provenance=arm_provenance,
                policy_id=same_question_policy_id,
            )
        if question_record is None:
            question_record = evaluation_record(
                stage="same_question_judgment", input_set_id=input_set_id,
                evaluation_input={"arm": arm, "generated_questions": questions,
                                  "reference_question": reference_question},
                provenance={**arm_provenance, "policy_id": same_question_policy_id,
                            "decision_source": "configured_evaluator"},
                error=question_error, status="blocked",
            )
        question_record["provenance"]["arm"] = arm
        question_record["provenance"]["arm_manifest"] = arm_provenance["arm_manifest"]
        question_record["provenance"]["target_extraction_record_sha256"] = (
            arm_provenance["target_extraction_record_sha256"]
        )
        records.append(question_record)

    unsigned = {
        "schema_version": "e6-literature-evaluation-bundle-v1",
        "schema_status": "provisional_unapproved",
        "input_set_id": input_set_id,
        "arm_order": list(ARMS),
        "record_count": len(records),
        "records": records,
    }
    unsigned["bundle_sha256"] = _hash_json(unsigned)
    return unsigned


def write_literature_evaluation_bundle_exclusive(
    path: str | Path, bundle: Mapping[str, Any],
) -> None:
    """Persist a validated literature evaluation bundle without overwriting."""
    if not isinstance(bundle, Mapping) or bundle.get("schema_version") != (
        "e6-literature-evaluation-bundle-v1"
    ) or bundle.get("schema_status") != "provisional_unapproved":
        raise EvaluationError("unsupported or nonprovisional literature evaluation bundle")
    records = bundle.get("records")
    if not isinstance(records, list) or bundle.get("record_count") != len(records):
        raise EvaluationError("literature evaluation bundle record count mismatch")
    unsigned = {key: value for key, value in bundle.items() if key != "bundle_sha256"}
    if bundle.get("bundle_sha256") != _hash_json(unsigned):
        raise EvaluationError("literature evaluation bundle hash mismatch")
    payload = json.dumps(bundle, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    try:
        with Path(path).open("x", encoding="utf-8") as handle:
            handle.write(payload)
    except FileExistsError as exc:
        raise FileExistsError(f"refusing to overwrite literature evaluation output: {path}") from exc


def evaluate_hypobench_recovery(
    input_set_id: str, benchmark_record: Mapping[str, Any],
    planted_hypothesis: str,
    recovery_judge: Callable[[Mapping[str, Any], str], Any] | None,
    *, dataset_provenance: Mapping[str, Any], policy_id: str | None,
) -> dict[str, Any]:
    """Interface for data-based HypoBench recovery; caller chooses dataset/split/policy."""
    if not isinstance(input_set_id, str) or not input_set_id.strip():
        raise EvaluationError("input_set_id is required for HypoBench recovery")
    if not isinstance(benchmark_record, Mapping) or not benchmark_record:
        raise EvaluationError("benchmark_record must be a nonempty object")
    if not isinstance(planted_hypothesis, str) or not planted_hypothesis.strip():
        raise EvaluationError("planted_hypothesis must be a nonempty caller-supplied string")
    if not isinstance(dataset_provenance, Mapping):
        raise EvaluationError("dataset_provenance must be an object")
    judge = _require_evaluator(recovery_judge, "HypoBench planted-hypothesis recovery")
    inputs = {"benchmark_record": dict(benchmark_record), "planted_hypothesis": planted_hypothesis}
    attempts: list[dict[str, Any]] = []
    try:
        raw = judge(dict(benchmark_record), planted_hypothesis)
        attempts.append({"attempt": 1, "status": "returned", "raw": raw})
        return evaluation_record(
            stage="hypobench_planted_hypothesis_recovery", input_set_id=input_set_id,
            evaluation_input=inputs,
            provenance={"dataset": dict(dataset_provenance), "policy_id": policy_id},
            raw_output=raw, parsed_output=raw, attempts=attempts,
        )
    except Exception as exc:
        attempts.append({"attempt": 1, "status": "failed", "error": str(exc)})
        return evaluation_record(
            stage="hypobench_planted_hypothesis_recovery", input_set_id=input_set_id,
            evaluation_input=inputs,
            provenance={"dataset": dict(dataset_provenance), "policy_id": policy_id},
            error=str(exc), attempts=attempts,
        )


def prepare_hypobench_data_explanation_input(
    input_set_id: str, benchmark_record: Mapping[str, Any],
    generated_explanations: Sequence[str], *, dataset_id: str, split: str,
    dataset_provenance: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate and preserve unscored data-explanation evaluation inputs.

    This prepares an auditable input envelope only. It does not identify planted
    hypotheses, call a judge, or calculate a score.
    """
    if not isinstance(input_set_id, str) or not input_set_id.strip():
        raise EvaluationError("input_set_id is required for data-explanation evaluation")
    if not isinstance(benchmark_record, Mapping) or not benchmark_record:
        raise EvaluationError("benchmark_record must be a nonempty object")
    if isinstance(generated_explanations, (str, bytes)) or not isinstance(
        generated_explanations, Sequence
    ) or not generated_explanations:
        raise EvaluationError("generated_explanations must be a nonempty sequence of strings")
    if any(not isinstance(text, str) or not text.strip() for text in generated_explanations):
        raise EvaluationError("each generated explanation must be a nonempty string")
    if not isinstance(dataset_id, str) or not dataset_id.strip():
        raise EvaluationError("dataset_id is required for data-explanation provenance")
    if not isinstance(split, str) or not split.strip():
        raise EvaluationError("split is required for data-explanation provenance")
    if not isinstance(dataset_provenance, Mapping) or not dataset_provenance:
        raise EvaluationError("dataset_provenance must be a nonempty object")

    evaluation_input = {
        "benchmark_record": dict(benchmark_record),
        "generated_explanations": list(generated_explanations),
    }
    return {
        "schema_version": "e6-hypobench-explanation-input-v1",
        "schema_status": "provisional_unapproved",
        "status": "input_ready_unscored",
        "input_set_id": input_set_id,
        "evaluation_input": evaluation_input,
        "evaluation_input_sha256": _hash_json(evaluation_input),
        "provenance": {
            "dataset_id": dataset_id,
            "split": split,
            "dataset": dict(dataset_provenance),
        },
        "scoring_status": "not_run",
    }


def prepare_hypobench_normalized_data_explanation_input(
    input_set_id: str, normalized_split: Mapping[str, Any],
    normalized_record: Mapping[str, Any], generated_explanations: Sequence[str],
) -> dict[str, Any]:
    """Prepare one caller-mapped normalized row for data-explanation evaluation.

    The source schemas differ across HypoBench datasets, so this adapter uses
    only ``evaluation_fields`` chosen by ``normalize_hypobench_evaluation_inputs``.
    It does not select fields, expose source labels as ground truth, or associate
    dataset-level planted hypotheses with individual rows.
    """
    if not isinstance(normalized_split, Mapping) or normalized_split.get("status") != (
        "normalized_unselected_unfrozen"
    ):
        raise EvaluationError("normalized HypoBench split is required")
    dataset_id, split = normalized_split.get("dataset_id"), normalized_split.get("split")
    provenance = normalized_split.get("provenance")
    if not isinstance(dataset_id, str) or not dataset_id.strip():
        raise EvaluationError("normalized HypoBench split is missing dataset_id")
    if not isinstance(split, str) or not split.strip():
        raise EvaluationError("normalized HypoBench split is missing split identity")
    if not isinstance(provenance, Mapping) or not provenance:
        raise EvaluationError("normalized HypoBench split is missing source provenance")
    if not isinstance(normalized_record, Mapping):
        raise EvaluationError("normalized HypoBench record must be an object")
    if normalized_record not in normalized_split.get("records", []):
        raise EvaluationError("normalized HypoBench record does not belong to the supplied split")
    fields = normalized_record.get("evaluation_fields")
    if not isinstance(fields, Mapping) or not fields:
        raise EvaluationError("normalized HypoBench record is missing evaluation_fields")
    if not isinstance(normalized_record.get("source_record_index"), int) or isinstance(
        normalized_record.get("source_record_index"), bool
    ):
        raise EvaluationError("normalized HypoBench record is missing a valid source row index")

    source_record = normalized_record.get("source_record")
    source_record_sha256 = _hash_json(source_record) if isinstance(source_record, Mapping) else None
    dataset_provenance = {
        **dict(provenance),
        "source_record_index": normalized_record["source_record_index"],
        "source_record_id": normalized_record.get("source_record_id"),
        "source_record_sha256": source_record_sha256,
        "field_mapping": dict(normalized_split.get("field_mapping", {})),
        "identifier_field": normalized_split.get("identifier_field"),
    }
    return prepare_hypobench_data_explanation_input(
        input_set_id, fields, generated_explanations,
        dataset_id=dataset_id, split=split, dataset_provenance=dataset_provenance,
    )


def evaluate_hypobench_data_explanation(
    prepared_input: Mapping[str, Any],
    explanation_evaluator: Callable[[Mapping[str, Any]], Any] | None,
    *, policy_id: str | None,
) -> dict[str, Any]:
    """Run a caller-supplied data-explanation evaluator through the audit wrapper.

    A metric/judge remains an injected policy. Without one, callers may retain
    the prepared input but cannot claim an evaluation result.
    """
    if not isinstance(prepared_input, Mapping) or prepared_input.get("schema_version") != (
        "e6-hypobench-explanation-input-v1"
    ):
        raise EvaluationError("prepared HypoBench data-explanation input is required")
    if prepared_input.get("status") != "input_ready_unscored" or prepared_input.get(
        "scoring_status"
    ) != "not_run":
        raise EvaluationError("HypoBench data-explanation input must be unscored")
    evaluation_input = prepared_input.get("evaluation_input")
    provenance = prepared_input.get("provenance")
    if not isinstance(evaluation_input, Mapping) or _hash_json(evaluation_input) != prepared_input.get(
        "evaluation_input_sha256"
    ):
        raise EvaluationError("prepared HypoBench input hash is missing or invalid")
    if not isinstance(provenance, Mapping) or not isinstance(
        provenance.get("dataset_id"), str
    ) or not isinstance(provenance.get("split"), str):
        raise EvaluationError("prepared HypoBench input is missing dataset provenance")
    input_set_id = prepared_input.get("input_set_id")
    if not isinstance(input_set_id, str) or not input_set_id.strip():
        raise EvaluationError("prepared HypoBench input is missing input_set_id")
    evaluator = _require_evaluator(explanation_evaluator, "HypoBench data-explanation")
    attempts: list[dict[str, Any]] = []
    try:
        raw = evaluator(dict(prepared_input))
        attempts.append({"attempt": 1, "status": "returned", "raw": raw})
        return evaluation_record(
            stage="hypobench_data_explanation", input_set_id=input_set_id,
            evaluation_input=dict(evaluation_input),
            provenance={"dataset": dict(provenance), "policy_id": policy_id},
            raw_output=raw, parsed_output=raw, attempts=attempts,
        )
    except Exception as exc:
        attempts.append({"attempt": 1, "status": "failed", "error": str(exc)})
        return evaluation_record(
            stage="hypobench_data_explanation", input_set_id=input_set_id,
            evaluation_input=dict(evaluation_input),
            provenance={"dataset": dict(provenance), "policy_id": policy_id},
            error=str(exc), attempts=attempts,
        )


def score_hypobench_heldout_predictions(
    prepared_input: Mapping[str, Any], true_labels: Sequence[str],
    predicted_labels: Sequence[Any], *, valid_labels: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Score held-out predictions; invalid predictions remain in the denominator.

    Labels must be mapped from the benchmark's source records by the caller;
    this function never infers a label field or a planted-hypothesis mapping.
    """
    if not isinstance(prepared_input, Mapping) or prepared_input.get("schema_version") != (
        "e6-hypobench-explanation-input-v1"
    ):
        raise EvaluationError("prepared HypoBench data-explanation input is required")
    if prepared_input.get("status") != "input_ready_unscored":
        raise EvaluationError("HypoBench input is not ready for held-out scoring")
    provenance = prepared_input.get("provenance")
    if not isinstance(provenance, Mapping) or not isinstance(
        provenance.get("dataset_id"), str
    ) or not isinstance(provenance.get("split"), str):
        raise EvaluationError("HypoBench dataset and split provenance are required")
    if _hash_json(prepared_input.get("evaluation_input")) != prepared_input.get(
        "evaluation_input_sha256"
    ):
        raise EvaluationError("prepared HypoBench input hash is missing or invalid")
    if isinstance(true_labels, (str, bytes)) or isinstance(predicted_labels, (str, bytes)):
        raise EvaluationError("held-out labels and predictions must be sequences")
    if not isinstance(true_labels, Sequence) or not isinstance(predicted_labels, Sequence):
        raise EvaluationError("held-out labels and predictions must be sequences")
    truth, predictions = list(true_labels), list(predicted_labels)
    if not truth or len(truth) != len(predictions):
        raise EvaluationError("held-out labels and predictions must be nonempty and length matched")
    if any(not isinstance(value, str) or not value.strip() for value in truth):
        raise EvaluationError("held-out true labels must be nonempty strings")
    allowed = None
    if valid_labels is not None:
        if isinstance(valid_labels, (str, bytes)) or not isinstance(valid_labels, Sequence) \
                or not valid_labels or any(not isinstance(value, str) or not value.strip()
                                           for value in valid_labels):
            raise EvaluationError("valid_labels must be a sequence of nonempty strings")
        allowed = set(valid_labels)
        if any(value not in allowed for value in truth):
            raise EvaluationError("held-out true label is outside the declared label set")
    is_valid = [
        isinstance(predicted, str) and bool(predicted.strip())
        and (allowed is None or predicted in allowed)
        for predicted in predictions
    ]
    correct = sum(actual == predicted for actual, predicted, valid
                  in zip(truth, predictions, is_valid) if valid)
    invalid_count = sum(not value for value in is_valid)
    parsed = {
        "correct": correct, "denominator": len(truth), "accuracy": correct / len(truth),
        "invalid_prediction_count": invalid_count,
        "invalid_prediction_policy": "count_as_incorrect_keep_in_fixed_denominator",
    }
    inputs = {"prepared_input_sha256": prepared_input["evaluation_input_sha256"],
              "true_labels": truth, "predicted_labels": predictions,
              "valid_labels": None if allowed is None else list(valid_labels)}
    return evaluation_record(
        stage="hypobench_heldout_accuracy",
        input_set_id=prepared_input["input_set_id"],
        evaluation_input=inputs,
        provenance={"dataset_id": provenance["dataset_id"], "split": provenance["split"],
                    "dataset": dict(provenance.get("dataset", {})),
                    "label_mapping": "caller_supplied_source_field",
                    "scoring_rule": "exact_label_match_accuracy"},
        raw_output=parsed, parsed_output=parsed,
    )


def aggregate_hypobench_heldout_accuracy(
    input_set_ids: Sequence[str], true_labels: Sequence[str],
    predicted_labels: Sequence[Any], *, valid_labels: Sequence[str],
    dataset_provenance: Mapping[str, Any],
) -> dict[str, Any]:
    """Compute fixed-denominator exact-match accuracy in supplied manifest order."""
    if isinstance(input_set_ids, (str, bytes)) or not isinstance(input_set_ids, Sequence) \
            or not input_set_ids or any(not isinstance(value, str) or not value.strip()
                                        for value in input_set_ids):
        raise EvaluationError("input_set_ids must be a nonempty sequence of IDs")
    if len(set(input_set_ids)) != len(input_set_ids):
        raise EvaluationError("input_set_ids must be unique")
    if not isinstance(dataset_provenance, Mapping) or not dataset_provenance:
        raise EvaluationError("dataset_provenance is required for held-out aggregation")
    if isinstance(true_labels, (str, bytes)) or isinstance(predicted_labels, (str, bytes)) \
            or not isinstance(true_labels, Sequence) or not isinstance(predicted_labels, Sequence):
        raise EvaluationError("held-out labels and predictions must be sequences")
    if len(input_set_ids) != len(true_labels) or len(true_labels) != len(predicted_labels):
        raise EvaluationError("IDs, held-out labels, and predictions must have equal fixed length")
    truth, predictions = list(true_labels), list(predicted_labels)
    if isinstance(valid_labels, (str, bytes)) or not isinstance(valid_labels, Sequence) \
            or not valid_labels or any(not isinstance(value, str) or not value.strip()
                                       for value in valid_labels):
        raise EvaluationError("valid_labels must be nonempty strings")
    allowed = set(valid_labels)
    if any(value not in allowed for value in truth):
        raise EvaluationError("held-out true label is outside the declared label set")
    valid = [isinstance(value, str) and bool(value.strip()) and value in allowed
             for value in predictions]
    correct = sum(actual == prediction for actual, prediction, is_valid
                  in zip(truth, predictions, valid) if is_valid)
    invalid_count = sum(not value for value in valid)
    summary = {
        "correct": correct,
        "denominator": len(input_set_ids),
        "accuracy": correct / len(input_set_ids),
        "invalid_prediction_count": invalid_count,
        "invalid_prediction_policy": "count_as_incorrect_keep_in_fixed_denominator",
        "aggregation_unit": "source_test_example_input_set",
        "aggregation_order": "manifest_input_set_order",
    }
    return evaluation_record(
        stage="hypobench_heldout_accuracy",
        input_set_id=str(dataset_provenance.get("dataset_id", "hypobench")) + ":TEST:aggregate",
        evaluation_input={
            "input_set_ids": list(input_set_ids), "true_labels": truth,
            "predicted_labels": predictions, "valid_labels": list(valid_labels),
            "dataset_provenance": dict(dataset_provenance),
        },
        provenance={**dict(dataset_provenance),
                    "scoring_rule": "exact_label_match_accuracy",
                    "prediction_policy_id": "e6-hypobench-generated-hypothesis-application-v1"},
        raw_output=summary, parsed_output=summary,
    )


def evaluate_hypobench_explanation_on_heldout(
    prepared_input: Mapping[str, Any], true_labels: Sequence[str],
    heldout_predictor: Callable[[Mapping[str, Any]], Any] | None,
    *, predictor_policy_id: str | None, valid_labels: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Run an injected held-out predictor for prepared explanations and score accuracy."""
    if not isinstance(prepared_input, Mapping):
        raise EvaluationError("prepared HypoBench input must be an object")
    predictor = _require_evaluator(heldout_predictor, "HypoBench held-out prediction")
    if not isinstance(predictor_policy_id, str) or not predictor_policy_id.strip():
        raise EvaluationError("held-out prediction policy_id is required")
    if not isinstance(prepared_input, Mapping) or not isinstance(
        prepared_input.get("evaluation_input"), Mapping
    ) or _hash_json(prepared_input.get("evaluation_input")) != prepared_input.get(
        "evaluation_input_sha256"
    ):
        raise EvaluationError("prepared HypoBench input hash is missing or invalid")
    if prepared_input.get("status") != "input_ready_unscored":
        raise EvaluationError("prepared HypoBench input is not ready for held-out scoring")
    prepared_provenance = prepared_input.get("provenance")
    if not isinstance(prepared_provenance, Mapping) or not isinstance(
        prepared_provenance.get("dataset_id"), str
    ) or not isinstance(prepared_provenance.get("split"), str):
        raise EvaluationError("prepared HypoBench input is missing dataset/split provenance")
    if not isinstance(prepared_input.get("input_set_id"), str) or not prepared_input[
        "input_set_id"
    ].strip():
        raise EvaluationError("prepared HypoBench input is missing input_set_id")
    if isinstance(true_labels, (str, bytes)) or not isinstance(true_labels, Sequence):
        raise EvaluationError("true_labels must be a sequence")
    if not true_labels or any(not isinstance(value, str) or not value.strip() for value in true_labels):
        raise EvaluationError("true_labels must contain nonempty strings")
    attempts = []
    raw = None
    try:
        raw = predictor(dict(prepared_input))
        if not isinstance(raw, Mapping) or not isinstance(raw.get("predicted_labels"), Sequence) or isinstance(
            raw.get("predicted_labels"), (str, bytes)
        ):
            raise EvaluationError("held-out predictor must return a predicted_labels sequence")
        scored = score_hypobench_heldout_predictions(
            prepared_input, true_labels, raw["predicted_labels"], valid_labels=valid_labels,
        )
        attempts.append({"attempt": 1, "status": "returned",
                         "predicted_label_count": len(raw["predicted_labels"])})
        return evaluation_record(
            stage="hypobench_data_explanation_heldout",
            input_set_id=prepared_input.get("input_set_id"),
            evaluation_input={**scored["evaluation_input"],
                              "prediction_output_sha256": _hash_json(raw)},
            provenance={
                **scored["provenance"], "prediction_policy_id": predictor_policy_id,
                **(dict(raw.get("prediction_provenance", {}))
                   if isinstance(raw.get("prediction_provenance"), Mapping) else {}),
            },
            raw_output=raw, parsed_output=scored["parsed_output"], attempts=attempts,
        )
    except Exception as exc:
        attempts.append({"attempt": 1, "status": "failed", "raw": raw, "error": str(exc)})
        return evaluation_record(
            stage="hypobench_data_explanation_heldout",
            input_set_id=prepared_input["input_set_id"],
            evaluation_input={"prepared_input": dict(prepared_input),
                              "true_labels": list(true_labels) if isinstance(true_labels, Sequence)
                              and not isinstance(true_labels, (str, bytes)) else true_labels},
            provenance={"prediction_policy_id": predictor_policy_id},
            raw_output=raw, attempts=attempts, error=str(exc),
        )


def evaluate_hypobench_dataset_level_recovery(
    input_set_id: str, generated_hypotheses: Sequence[str],
    planted_hypotheses: Sequence[str],
    recovery_judge: Callable[[Sequence[str], Sequence[str]], Any] | None,
    *, dataset_provenance: Mapping[str, Any], policy_id: str | None,
) -> dict[str, Any]:
    """Score one K=6 output against the dataset-level planted hypothesis set.

    A GT item is recovered if any generated hypothesis is MATCH. AMBIGUOUS
    pairs never count as recovered; if there is no MATCH but at least one
    AMBIGUOUS pair, that GT is reported as ambiguous. Invalid or missing cells
    are conservatively converted to AMBIGUOUS and remain in the 14-item
    denominator.
    """
    if not isinstance(input_set_id, str) or not input_set_id.strip():
        raise EvaluationError("input_set_id is required for HypoBench recovery")
    if isinstance(generated_hypotheses, (str, bytes)) or not isinstance(
        generated_hypotheses, Sequence
    ) or len(generated_hypotheses) != 6 or any(
        not isinstance(value, str) or not value.strip() for value in generated_hypotheses
    ):
        raise EvaluationError("planted recovery requires exactly six nonempty generated hypotheses")
    if isinstance(planted_hypotheses, (str, bytes)) or not isinstance(
        planted_hypotheses, Sequence
    ) or len(planted_hypotheses) != 14 or any(
        not isinstance(value, str) or not value.strip() for value in planted_hypotheses
    ):
        raise EvaluationError("planted recovery requires the 14 source-provided dataset hypotheses")
    if not isinstance(dataset_provenance, Mapping) or not dataset_provenance:
        raise EvaluationError("dataset provenance is required for planted recovery")
    judge = _require_evaluator(recovery_judge, "HypoBench dataset-level recovery")
    attempts = []
    try:
        raw = judge(list(generated_hypotheses), list(planted_hypotheses))
        judgments = raw.get("judgments") if isinstance(raw, Mapping) else raw
        valid_verdicts = {"MATCH", "NO_MATCH", "AMBIGUOUS"}
        parsed_matrix = []
        invalid_count = 0
        if not isinstance(judgments, Sequence) or isinstance(judgments, (str, bytes)):
            judgments = []
        reported_invalid = raw.get("invalid_judgment_cell_count", 0) \
            if isinstance(raw, Mapping) else 0
        if type(reported_invalid) is int and reported_invalid >= 0:
            invalid_count += reported_invalid
        else:
            invalid_count += 1
        for row_index in range(6):
            source_row = judgments[row_index] if row_index < len(judgments) else []
            if not isinstance(source_row, Sequence) or isinstance(source_row, (str, bytes)):
                source_row = []
            output_row = []
            for column_index in range(14):
                value = source_row[column_index] if column_index < len(source_row) else None
                if not isinstance(value, str) or value not in valid_verdicts:
                    value = "AMBIGUOUS"
                    invalid_count += 1
                output_row.append(value)
            invalid_count += max(0, len(source_row) - 14)
            parsed_matrix.append(output_row)
        invalid_count += max(0, len(judgments) - 6)
        per_ground_truth = []
        for gt_index in range(14):
            verdicts = [parsed_matrix[hyp_index][gt_index] for hyp_index in range(6)]
            if "MATCH" in verdicts:
                status = "recovered"
            elif "AMBIGUOUS" in verdicts:
                status = "ambiguous_unrecovered"
            else:
                status = "not_recovered"
            per_ground_truth.append({
                "ground_truth_id": f"GT{gt_index + 1}",
                "status": status,
                "matching_generated_hypothesis_ids": [
                    f"H{index + 1}" for index, value in enumerate(verdicts) if value == "MATCH"
                ],
            })
        recovered = sum(item["status"] == "recovered" for item in per_ground_truth)
        parsed = {
            "recovered_ground_truth_count": recovered,
            "ground_truth_denominator": 14,
            "recovery_recall": recovered / 14,
            "ambiguous_ground_truth_count": sum(
                item["status"] == "ambiguous_unrecovered" for item in per_ground_truth
            ),
            "invalid_judgment_cell_count": invalid_count,
            "order_disagreement_cell_count": (
                raw.get("order_disagreement_cell_count", 0)
                if isinstance(raw, Mapping) and type(raw.get("order_disagreement_cell_count", 0)) is int
                else 0
            ),
            "invalid_judgment_policy": "convert_to_ambiguous_and_not_recovered",
            "per_ground_truth": per_ground_truth,
            "judgment_matrix": parsed_matrix,
        }
        attempts.append({"attempt": 1, "status": "returned"})
        response_provenance = raw.get("prediction_provenance", {}) \
            if isinstance(raw, Mapping) else {}
        return evaluation_record(
            stage="hypobench_dataset_level_planted_recovery", input_set_id=input_set_id,
            evaluation_input={
                "generated_hypotheses": list(generated_hypotheses),
                "planted_hypotheses": list(planted_hypotheses),
                "matching_policy_id": policy_id,
            },
            provenance={"dataset": dict(dataset_provenance), "policy_id": policy_id,
                        "matching_unit": "generated_hypothesis_x_dataset_level_planted_hypothesis"},
            raw_output=raw, parsed_output=parsed, attempts=attempts,
            model_response_metadata=response_provenance,
            status="succeeded",
        )
    except Exception as exc:
        attempts.append({"attempt": 1, "status": "failed", "error": str(exc)})
        return evaluation_record(
            stage="hypobench_dataset_level_planted_recovery", input_set_id=input_set_id,
            evaluation_input={"generated_hypotheses": list(generated_hypotheses),
                              "planted_hypotheses": list(planted_hypotheses)},
            provenance={"dataset": dict(dataset_provenance), "policy_id": policy_id},
            attempts=attempts, error=str(exc),
        )


def aggregate_hypobench_dataset_level_recovery(
    input_set_ids: Sequence[str], per_input_results: Sequence[Mapping[str, Any]],
    *, dataset_provenance: Mapping[str, Any],
) -> dict[str, Any]:
    """Aggregate 14-item recovery recall over the fixed manifest order."""
    if isinstance(input_set_ids, (str, bytes)) or not isinstance(input_set_ids, Sequence) \
            or not input_set_ids or any(not isinstance(value, str) or not value.strip()
                                        for value in input_set_ids):
        raise EvaluationError("input_set_ids must be a nonempty sequence")
    if len(set(input_set_ids)) != len(input_set_ids):
        raise EvaluationError("input_set_ids must be unique")
    if isinstance(per_input_results, (str, bytes)) or not isinstance(
        per_input_results, Sequence
    ):
        raise EvaluationError("per_input_results must be a sequence")
    by_id = {}
    for result in per_input_results:
        if not isinstance(result, Mapping) or result.get("input_set_id") in by_id:
            raise EvaluationError("recovery result is invalid or duplicates an input set")
        by_id[result.get("input_set_id")] = result
    if set(by_id) != set(input_set_ids):
        raise EvaluationError("recovery results must cover exactly the input-set manifest")
    recalls = []
    total_ambiguous = 0
    total_invalid = 0
    total_order_disagreements = 0
    for input_set_id in input_set_ids:
        parsed = by_id[input_set_id].get("parsed_output")
        if not isinstance(parsed, Mapping) or parsed.get("ground_truth_denominator") != 14 \
                or type(parsed.get("recovered_ground_truth_count")) is not int:
            raise EvaluationError(f"recovery result for {input_set_id} is incomplete")
        recovered = parsed["recovered_ground_truth_count"]
        if not 0 <= recovered <= 14:
            raise EvaluationError(f"recovery count for {input_set_id} is out of range")
        recalls.append(recovered / 14)
        total_ambiguous += parsed.get("ambiguous_ground_truth_count", 0)
        total_invalid += parsed.get("invalid_judgment_cell_count", 0)
        total_order_disagreements += parsed.get("order_disagreement_cell_count", 0)
    summary = {
        "aggregation_unit": "input_set",
        "aggregation_order": "manifest_input_set_order",
        "input_set_count": len(recalls),
        "ground_truth_items_per_input_set": 14,
        "recovered_ground_truth_item_count": sum(
            by_id[item].get("parsed_output", {}).get("recovered_ground_truth_count", 0)
            for item in input_set_ids
        ),
        "ground_truth_item_opportunities": len(recalls) * 14,
        "macro_recovery_recall": sum(recalls) / len(recalls),
        "ambiguous_ground_truth_count_across_input_sets": total_ambiguous,
        "invalid_judgment_cells_across_input_sets": total_invalid,
        "order_disagreement_cells_across_input_sets": total_order_disagreements,
        "aggregation_rule": "arithmetic_mean_of_per_input_set_recovered_count_divided_by_14",
    }
    return evaluation_record(
        stage="hypobench_dataset_level_planted_recovery_aggregate",
        input_set_id=str(dataset_provenance.get("dataset_id", "hypobench")) + ":TEST:recovery-aggregate",
        evaluation_input={"input_set_ids": list(input_set_ids),
                          "per_input_recovery_record_hashes": [
                              _hash_json(by_id[item]) for item in input_set_ids
                          ], "dataset_provenance": dict(dataset_provenance)},
        provenance={**dict(dataset_provenance),
                    "policy_id": "e6-hypobench-dataset-ground-truth-semantic-recovery-v1"},
        raw_output=summary, parsed_output=summary,
    )


def load_hypobench_split(
    source_path: str | Path, *, dataset_id: str, split: str,
) -> dict[str, Any]:
    """Ingest an explicitly supplied HypoBench JSON/JSONL split without selecting it.

    JSON may be a list of record objects or an equal-length columnar object.
    JSONL must contain one record object per nonblank line. The source digest is
    over the exact file bytes; row values and ordering are preserved.
    """
    if not isinstance(dataset_id, str) or not dataset_id.strip():
        raise EvaluationError("dataset_id is required for HypoBench ingestion")
    if not isinstance(split, str) or not split.strip():
        raise EvaluationError("split is required for HypoBench ingestion")
    path = Path(source_path)
    try:
        source_bytes = path.read_bytes()
    except OSError as exc:
        raise EvaluationError(f"cannot read HypoBench split: {exc}") from exc
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()
    try:
        source_text = source_bytes.decode("utf-8")
        if path.suffix.lower() in (".jsonl", ".ndjson"):
            records = []
            for line_number, line in enumerate(source_text.splitlines(), start=1):
                if not line.strip():
                    continue
                value = json.loads(line)
                if not isinstance(value, Mapping):
                    raise EvaluationError(
                        f"HypoBench JSONL line {line_number} must be a record object"
                    )
                records.append(dict(value))
            source_format = "jsonl-records"
        else:
            value = json.loads(source_text)
            if isinstance(value, list):
                if any(not isinstance(row, Mapping) for row in value):
                    raise EvaluationError("HypoBench JSON record list must contain only objects")
                records = [dict(row) for row in value]
                source_format = "json-record-list"
            elif isinstance(value, Mapping) and value and all(
                isinstance(column, list) for column in value.values()
            ):
                lengths = {len(column) for column in value.values()}
                if len(lengths) != 1:
                    raise EvaluationError("HypoBench columnar JSON fields must have equal lengths")
                count = next(iter(lengths))
                records = [
                    {name: column[index] for name, column in value.items()}
                    for index in range(count)
                ]
                source_format = "json-columnar"
            else:
                raise EvaluationError(
                    "HypoBench JSON must be a record list or a nonempty columnar object"
                )
    except UnicodeDecodeError as exc:
        raise EvaluationError("HypoBench split must be UTF-8 JSON/JSONL") from exc
    except json.JSONDecodeError as exc:
        raise EvaluationError(f"HypoBench split contains malformed JSON: {exc}") from exc

    return {
        "status": "ingested_unselected_unfrozen",
        "dataset_id": dataset_id,
        "split": split,
        "records": records,
        "provenance": {
            "source_path": str(path),
            "source_format": source_format,
            "source_sha256": source_sha256,
            "source_hash_basis": "SHA-256 of exact file bytes",
            "record_count": len(records),
            "dataset_selected": False,
            "dataset_frozen": False,
        },
    }


def normalize_hypobench_evaluation_inputs(
    ingested_split: Mapping[str, Any], *, field_mapping: Mapping[str, str],
    identifier_field: str | None = None,
) -> dict[str, Any]:
    """Normalize caller-mapped fields without selecting a dataset or inferring labels.

    ``field_mapping`` maps normalized field names to exact source-record keys.
    Missing and null required values are errors; values are never synthesized.
    The complete original record and source-row index remain attached to each
    normalized input. Planted-hypothesis identification and scoring are separate.
    """
    if not isinstance(ingested_split, Mapping):
        raise EvaluationError("ingested HypoBench split must be an object")
    if ingested_split.get("status") != "ingested_unselected_unfrozen":
        raise EvaluationError("HypoBench input must come from an unselected, unfrozen ingestion")
    dataset_id, split = ingested_split.get("dataset_id"), ingested_split.get("split")
    if not isinstance(dataset_id, str) or not dataset_id.strip():
        raise EvaluationError("HypoBench ingestion is missing dataset_id")
    if not isinstance(split, str) or not split.strip():
        raise EvaluationError("HypoBench ingestion is missing split identity")
    if not isinstance(field_mapping, Mapping) or not field_mapping:
        raise EvaluationError("field_mapping must map at least one normalized field")
    if any(not isinstance(normalized, str) or not normalized.strip()
           or not isinstance(source, str) or not source.strip()
           for normalized, source in field_mapping.items()):
        raise EvaluationError("field_mapping names must be nonempty strings")
    records = ingested_split.get("records")
    if not isinstance(records, list):
        raise EvaluationError("ingested HypoBench records must be a list")
    source_provenance = ingested_split.get("provenance")
    if not isinstance(source_provenance, Mapping) or not source_provenance:
        raise EvaluationError("HypoBench source provenance is required")
    if identifier_field is not None and (
        not isinstance(identifier_field, str) or not identifier_field.strip()
    ):
        raise EvaluationError("identifier_field must be a nonempty string when supplied")

    normalized_records = []
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            raise EvaluationError(f"HypoBench source record {index} must be an object")
        normalized_fields = {}
        for normalized_name, source_name in field_mapping.items():
            if source_name not in record:
                raise EvaluationError(
                    f"HypoBench source record {index} is missing required field {source_name!r}"
                )
            value = record[source_name]
            if value is None:
                raise EvaluationError(
                    f"HypoBench source record {index} has null required field {source_name!r}"
                )
            normalized_fields[normalized_name] = value
        source_record_id = None
        if identifier_field is not None:
            if identifier_field not in record or record[identifier_field] is None:
                raise EvaluationError(
                    f"HypoBench source record {index} is missing identifier field {identifier_field!r}"
                )
            source_record_id = record[identifier_field]
        normalized_records.append({
            "source_record_index": index,
            "source_record_id": source_record_id,
            "evaluation_fields": normalized_fields,
            "source_record": dict(record),
        })

    return {
        "status": "normalized_unselected_unfrozen",
        "dataset_id": dataset_id,
        "split": split,
        "field_mapping": dict(field_mapping),
        "identifier_field": identifier_field,
        "records": normalized_records,
        "provenance": dict(source_provenance),
        "dataset_selected": False,
        "dataset_frozen": False,
    }


def summarize_binary_rate(
    input_set_id: str, stage: str, decisions: Sequence[Mapping[str, Any]],
    *, numerator_field: str, denominator_policy_id: str | None,
    provenance: Mapping[str, Any],
) -> dict[str, Any]:
    """Summarize already-adjudicated binary decisions without selecting a matcher."""
    if not isinstance(denominator_policy_id, str) or not denominator_policy_id.strip():
        raise EvaluationError("denominator policy is unresolved and must be supplied")
    copied = [dict(row) for row in decisions]
    if any(type(row.get(numerator_field)) is not bool for row in copied):
        raise EvaluationError(f"every decision needs Boolean {numerator_field}")
    successes = sum(row[numerator_field] for row in copied)
    value = successes / len(copied) if copied else None
    return evaluation_record(
        stage=stage, input_set_id=input_set_id,
        evaluation_input={"decisions": copied, "denominator_policy_id": denominator_policy_id},
        provenance=dict(provenance),
        raw_output={"successes": successes, "denominator": len(copied), "rate": value},
        parsed_output={"successes": successes, "denominator": len(copied), "rate": value},
        status="succeeded" if copied else "blocked",
        error=None if copied else "no eligible decisions under supplied denominator policy",
    )


def evaluate_already_asked_rate(
    input_set_id: str, generated_questions: Sequence[Mapping[str, Any]],
    reference_questions: Sequence[str],
    same_question_evaluator: Callable[[str, Sequence[str]], Any] | None,
    *, denominator_policy_id: str | None, provenance: Mapping[str, Any],
) -> dict[str, Any]:
    """Adjudicate each generated question against a supplied reference corpus.

    The evaluator owns retrieval, similarity thresholds, and same-question
    decisions. E2 novelty scores are not used as a substitute for this judgment.
    """
    _require_input_set_id(input_set_id)
    judge = _require_evaluator(same_question_evaluator, "already-asked matching")
    if not isinstance(denominator_policy_id, str) or not denominator_policy_id.strip():
        raise EvaluationError("denominator policy is unresolved and must be supplied")
    if isinstance(generated_questions, (str, bytes)) or not isinstance(
        generated_questions, Sequence
    ):
        raise EvaluationError("generated_questions must be a sequence of records")
    if isinstance(reference_questions, (str, bytes)) or not isinstance(
        reference_questions, Sequence
    ) or any(not isinstance(value, str) or not value.strip() for value in reference_questions):
        raise EvaluationError("reference_questions must be a sequence of nonempty strings")
    for index, row in enumerate(generated_questions):
        if not isinstance(row, Mapping) or not isinstance(row.get("question_id"), str) or not row[
            "question_id"
        ].strip() or not isinstance(row.get("question"), str) or not row["question"].strip():
            raise EvaluationError(f"generated question {index} requires question_id and question")
    corpus = list(reference_questions)
    if not corpus:
        return evaluation_record(
            stage="already_asked_rate", input_set_id=input_set_id,
            evaluation_input={"generated_questions": [dict(row) for row in generated_questions],
                              "reference_questions": [], "denominator_policy_id": denominator_policy_id},
            provenance=dict(provenance), status="blocked",
            error="genuine reference question corpus is absent; rate unavailable", parsed_output=None)
    decisions, attempts = [], []
    failures = []
    for index, row in enumerate(generated_questions):
        try:
            value = judge(row["question"], corpus)
            if type(value) is not bool:
                raise EvaluationError("already-asked evaluator must return Boolean decisions")
            decisions.append({"question_id": row["question_id"], "already_asked": value})
            attempts.append({"question_id": row["question_id"], "status": "returned", "raw": value})
        except Exception as exc:
            failures.append(str(exc))
            attempts.append({"question_id": row["question_id"], "status": "failed", "error": str(exc)})
    inputs = {"generated_questions": [dict(row) for row in generated_questions],
              "reference_questions": corpus,
              "denominator_policy_id": denominator_policy_id}
    source_provenance = {
        **dict(provenance), "reference_corpus_sha256": _hash_json(corpus),
        "same_question_evaluator": "caller_supplied",
    }
    if failures:
        return evaluation_record(
            stage="already_asked_rate", input_set_id=input_set_id,
            evaluation_input=inputs,
            provenance={**source_provenance, "denominator_policy_id": denominator_policy_id},
            raw_output={"decisions": decisions}, attempts=attempts,
            error="one or more already-asked judgments failed: " + "; ".join(failures),
            status="blocked",
        )
    result = summarize_binary_rate(
        input_set_id, "already_asked_rate", decisions,
        numerator_field="already_asked", denominator_policy_id=denominator_policy_id,
        provenance={**source_provenance, "judgment_attempts": attempts},
    )
    result["evaluation_input"] = inputs
    result["evaluation_input_sha256"] = _hash_json(inputs)
    result["attempts"] = attempts
    return result


def summarize_hypothesis_diversity(
    input_set_id: str, hypotheses: Sequence[Mapping[str, Any]],
    pair_decisions: Sequence[Mapping[str, Any]], *, distinct_field: str,
    policy_id: str | None, aggregate: Callable[[Sequence[Mapping[str, Any]]], Any] | None,
    provenance: Mapping[str, Any],
) -> dict[str, Any]:
    """Aggregate externally adjudicated pairs under an injected diversity policy."""
    input_rows = [dict(row) for row in hypotheses]
    pairs = [dict(row) for row in pair_decisions]
    if not policy_id:
        raise EvaluationError("hypothesis-diversity definition/policy_id is unresolved")
    aggregator = _require_evaluator(aggregate, "hypothesis-diversity aggregation")
    if any(type(row.get(distinct_field)) is not bool for row in pairs):
        raise EvaluationError(f"each pair needs Boolean {distinct_field}")
    value = aggregator(pairs)
    return evaluation_record(
        stage="hypothesis_diversity", input_set_id=input_set_id,
        evaluation_input={"hypotheses": input_rows, "pair_decisions": pairs},
        provenance={**dict(provenance), "policy_id": policy_id},
        raw_output=value, parsed_output=value,
    )


def evaluate_k6_hypothesis_diversity(
    input_set_id: str, hypotheses: Sequence[Mapping[str, Any]],
    pair_distinct_evaluator: Callable[[str, str], Any] | None,
    aggregate: Callable[[Sequence[Mapping[str, Any]]], Any] | None,
    *, policy_id: str | None, provenance: Mapping[str, Any],
) -> dict[str, Any]:
    """Adjudicate all 15 unordered pairs for exactly six hypotheses, then aggregate."""
    _require_input_set_id(input_set_id)
    if not isinstance(policy_id, str) or not policy_id.strip():
        raise EvaluationError("hypothesis-diversity definition/policy_id is unresolved")
    judge = _require_evaluator(pair_distinct_evaluator, "hypothesis-diversity pair judgment")
    aggregator = _require_evaluator(aggregate, "hypothesis-diversity aggregation")
    rows = list(hypotheses) if not isinstance(hypotheses, (str, bytes)) else []
    if len(rows) != 6 or any(not isinstance(row, Mapping) for row in rows):
        raise EvaluationError("K=6 diversity requires exactly six hypothesis records")
    normalized = []
    ids = set()
    for index, row in enumerate(rows):
        hypothesis_id, text_value = row.get("hypothesis_id", row.get("id")), row.get("text")
        if not isinstance(hypothesis_id, str) or not hypothesis_id.strip() or hypothesis_id in ids:
            raise EvaluationError(f"hypothesis {index} requires a unique nonempty ID")
        if not isinstance(text_value, str) or not text_value.strip():
            raise EvaluationError(f"hypothesis {index} requires nonempty text")
        ids.add(hypothesis_id)
        normalized.append({"hypothesis_id": hypothesis_id, "text": text_value})
    pairs, attempts = [], []
    try:
        for left_index in range(6):
            for right_index in range(left_index + 1, 6):
                left, right = normalized[left_index], normalized[right_index]
                distinct = judge(left["text"], right["text"])
                if type(distinct) is not bool:
                    raise EvaluationError("pair diversity evaluator must return Boolean decisions")
                pair = {"pair": [left["hypothesis_id"], right["hypothesis_id"],],
                        "distinct": distinct}
                pairs.append(pair)
                attempts.append({"pair": pair["pair"], "status": "returned", "distinct": distinct})
        aggregate_value = aggregator(pairs)
        parsed = {"K": 6, "pair_count": len(pairs), "pair_decisions": pairs,
                  "aggregate": aggregate_value}
        return evaluation_record(
            stage="hypothesis_diversity_k6", input_set_id=input_set_id,
            evaluation_input={"hypotheses": normalized},
            provenance={**dict(provenance), "policy_id": policy_id,
                        "pair_evaluator": "caller_supplied", "aggregate_policy": "caller_supplied"},
            raw_output={"pair_decisions": pairs, "aggregate": aggregate_value},
            parsed_output=parsed, attempts=attempts,
        )
    except Exception as exc:
        attempts.append({"status": "failed", "error": str(exc)})
        return evaluation_record(
            stage="hypothesis_diversity_k6", input_set_id=input_set_id,
            evaluation_input={"hypotheses": normalized},
            provenance={**dict(provenance), "policy_id": policy_id,
                        "pair_evaluator": "caller_supplied", "aggregate_policy": "caller_supplied"},
            raw_output={"pair_decisions": pairs} if pairs else None,
            attempts=attempts, error=str(exc),
        )


def classify_question(
    input_set_id: str, question_id: str, question: str,
    model_client: Callable[[str, str], Any], *, model_configuration: Mapping[str, Any],
) -> dict[str, Any]:
    """Call existing question-type prompt through injected client; tests use mocks only."""
    if not callable(model_client):
        raise EvaluationError("injected model_client is required")
    template = _read_prompt(QUESTION_TYPE_PROMPT)
    rendered = _render(template, {"QUESTION": question})
    attempts: list[dict[str, Any]] = []
    raw: str | None = None
    reply_metadata: dict[str, Any] = {}
    try:
        reply = model_client("question_type_classification", rendered)
        raw, reply_metadata = _unpack_model_reply(reply)
        parsed = _parse_json(raw, "question type")
        if parsed.get("type") not in ("constructive", "analytic", "other", "ambiguous"):
            raise EvaluationError("type must be constructive, analytic, other, or ambiguous")
        attempts.append({"attempt": 1, "status": "returned", "raw": raw})
        return evaluation_record(
            stage="question_type_classification", input_set_id=input_set_id,
            evaluation_input={"question_id": question_id, "question": question, "rendered_prompt": rendered},
            provenance={"prompt_path": str(QUESTION_TYPE_PROMPT.relative_to(ROOT)),
                        "prompt_sha256": hashlib.sha256(template.encode()).hexdigest(),
                        "model_configuration": dict(model_configuration)},
            raw_output=raw, parsed_output=parsed, attempts=attempts,
            model_response_metadata=reply_metadata,
        )
    except Exception as exc:
        attempts.append({"attempt": 1, "status": "failed", "raw": raw, "error": str(exc)})
        return evaluation_record(
            stage="question_type_classification", input_set_id=input_set_id,
            evaluation_input={"question_id": question_id, "question": question, "rendered_prompt": rendered},
            provenance={"prompt_path": str(QUESTION_TYPE_PROMPT.relative_to(ROOT)),
                        "prompt_sha256": hashlib.sha256(template.encode()).hexdigest(),
                        "model_configuration": dict(model_configuration)},
            raw_output=raw, attempts=attempts, error=str(exc),
            model_response_metadata=reply_metadata,
        )


def build_blinded_pairwise_presentations(
    comparisons: Sequence[Mapping[str, Any]],
    blind_labels: Mapping[str, str], *,
    length_matcher: Callable[[str, str], Mapping[str, Any]] | None = None,
    llm_judge: bool = True,
) -> list[dict[str, Any]]:
    """Create both A/B orders for externally selected pairs and supplied blind IDs.

    An LLM judge requires a caller-supplied length matcher. No truncation/padding
    method, label assignment, or comparison schedule is chosen here.
    """
    if llm_judge and not callable(length_matcher):
        raise EvaluationError("LLM judge use requires an approved/injected length matcher")
    rows: list[dict[str, Any]] = []
    for pair_index, item in enumerate(comparisons):
        left_id, right_id = item.get("left_id"), item.get("right_id")
        left, right = item.get("left_text"), item.get("right_text")
        if not all(isinstance(v, str) and v for v in (left_id, right_id, left, right)):
            raise EvaluationError("each pair requires two IDs and nonempty texts")
        if left_id == right_id or left_id not in blind_labels or right_id not in blind_labels:
            raise EvaluationError("pair IDs must differ and have supplied blind labels")
        if blind_labels[left_id] == blind_labels[right_id]:
            raise EvaluationError("blind labels must distinguish the compared items")
        match = dict(length_matcher(left, right)) if length_matcher else {
            "left_text": left, "right_text": right, "policy_id": "not_applicable_non_llm"
        }
        matched_left, matched_right = match.get("left_text"), match.get("right_text")
        if not isinstance(matched_left, str) or not isinstance(matched_right, str):
            raise EvaluationError("length matcher must return left_text and right_text strings")
        if llm_judge and (match.get("matched") is not True or not match.get("policy_id")):
            raise EvaluationError("LLM length matcher must record matched=true and a policy_id")
        for order, (a_id, a_text, b_id, b_text) in enumerate((
            (left_id, matched_left, right_id, matched_right),
            (right_id, matched_right, left_id, matched_left),
        ), start=1):
            rows.append({
                "input_set_id": item.get("input_set_id"),
                "pair_index": pair_index, "presentation_order_index": order,
                "item_a_blind_id": blind_labels[a_id], "item_b_blind_id": blind_labels[b_id],
                "item_a_text": a_text, "item_b_text": b_text,
                "source_item_ids": [a_id, b_id], "source_texts": [left, right],
                "length_matching": match,
                "provenance": dict(item.get("provenance") or {}),
            })
    return rows


def judge_blinded_presentations(
    presentations: Sequence[Mapping[str, Any]], model_client: Callable[[str, str], Any],
    *, domain_and_task: str, evidence: str, model_configuration: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Run the supplied pairwise prompt on mock or approved client and retain all replies."""
    template = _read_prompt(PAIRWISE_PROMPT)
    records = []
    for row in presentations:
        inp = dict(row)
        rendered = _render(template, {
            "DOMAIN_AND_TASK": domain_and_task, "EVIDENCE": evidence,
            "HYPOTHESIS_A": str(inp["item_a_text"]), "HYPOTHESIS_B": str(inp["item_b_text"]),
        })
        attempts: list[dict[str, Any]] = []
        raw: str | None = None
        reply_metadata: dict[str, Any] = {}
        try:
            reply = model_client("pairwise_hypothesis_judgment", rendered)
            raw, reply_metadata = _unpack_model_reply(reply)
            parsed = _parse_json(raw, "pairwise judge")
            if parsed.get("better") not in ("A", "B", "tie"):
                raise EvaluationError("better must be A, B, or tie")
            attempts.append({"attempt": 1, "status": "returned", "raw": raw})
            records.append(evaluation_record(
                stage="blinded_pairwise_judging", input_set_id=str(inp.get("input_set_id", "pairwise")),
                evaluation_input={**inp, "rendered_prompt": rendered},
                provenance={"prompt_path": str(PAIRWISE_PROMPT.relative_to(ROOT)),
                            "prompt_sha256": hashlib.sha256(template.encode()).hexdigest(),
                            "model_configuration": dict(model_configuration),
                            "output_kind": "llm_judge_output", "judge_count": 1},
                raw_output=raw, parsed_output=parsed, attempts=attempts,
                model_response_metadata=reply_metadata,
            ))
        except Exception as exc:
            attempts.append({"attempt": 1, "status": "failed", "raw": raw, "error": str(exc)})
            records.append(evaluation_record(
                stage="blinded_pairwise_judging", input_set_id=str(inp.get("input_set_id", "pairwise")),
                evaluation_input={**inp, "rendered_prompt": rendered},
                provenance={"prompt_path": str(PAIRWISE_PROMPT.relative_to(ROOT)),
                            "prompt_sha256": hashlib.sha256(template.encode()).hexdigest(),
                            "model_configuration": dict(model_configuration),
                            "output_kind": "llm_judge_output", "judge_count": 1},
                raw_output=raw, attempts=attempts, error=str(exc),
                model_response_metadata=reply_metadata,
            ))
    return records


def paired_bootstrap_interval(
    paired_differences: Mapping[str, float], *, replicates: int | None,
    confidence_level: float | None, seed: int | None,
    statistic: Callable[[Sequence[float]], float] | None,
    interval_estimator: Callable[[Sequence[float], float], tuple[float, float]] | None,
    resample_input_set_ids: Callable[[Sequence[str], int, int, int], Sequence[str]] | None,
    rng_name: str | None,
) -> dict[str, Any]:
    """Resample paired differences by input_set_id; all analytic choices are supplied."""
    if not paired_differences or any(not isinstance(k, str) or not k.strip() for k in paired_differences):
        raise EvaluationError("paired input_set_id values are required")
    values = list(paired_differences.values())
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in values):
        raise EvaluationError("paired differences must be finite numbers")
    if type(replicates) is not int or replicates < 1:
        raise EvaluationError("bootstrap replicates must be explicitly configured as a positive integer")
    if type(confidence_level) not in (int, float) or not 0 < confidence_level < 1:
        raise EvaluationError("confidence_level must be explicitly configured in (0, 1)")
    if type(seed) is not int:
        raise EvaluationError("bootstrap seed must be explicitly configured")
    stat = _require_evaluator(statistic, "bootstrap statistic")
    interval = _require_evaluator(interval_estimator, "bootstrap interval method")
    sampler = _require_evaluator(resample_input_set_ids, "bootstrap resampling RNG")
    if not rng_name:
        raise EvaluationError("random generator/version must be explicitly recorded")
    ids = list(paired_differences)
    draws = []
    for replicate_index in range(replicates):
        sampled_ids = list(sampler(ids, len(ids), replicate_index, seed))
        if len(sampled_ids) != len(ids) or any(sample_id not in paired_differences for sample_id in sampled_ids):
            raise EvaluationError("resampler must return input_set IDs with replacement at original sample size")
        sample = [paired_differences[sample_id] for sample_id in sampled_ids]
        result = stat(sample)
        if type(result) not in (int, float) or not math.isfinite(result):
            raise EvaluationError("bootstrap statistic must return a finite number")
        draws.append(float(result))
    point = stat(values)
    lower, upper = interval(draws, float(confidence_level))
    if (type(point) not in (int, float) or not math.isfinite(point)
            or type(lower) not in (int, float) or type(upper) not in (int, float)
            or not math.isfinite(lower) or not math.isfinite(upper) or lower > upper):
        raise EvaluationError("point estimate and interval bounds must be finite and ordered")
    return {
        "schema_version": "e6-evaluation-provisional-v1",
        "schema_status": "provisional_unapproved",
        "stage": "paired_bootstrap",
        "resampling_unit": "input_set",
        "input_set_ids": list(paired_differences),
        "paired_differences": dict(paired_differences),
        "point_estimate": point,
        "confidence_level": float(confidence_level),
        "interval": [lower, upper],
        "replicates": replicates,
        "seed": seed,
        "random_generator": rng_name,
        "statistic_id": getattr(statistic, "__name__", "injected"),
        "interval_method_id": getattr(interval_estimator, "__name__", "injected"),
    }


def paired_bootstrap_all_seven_arms(
    input_set_id: str, arm_values: Mapping[str, Mapping[str, float]], *,
    replicates: int, seed: int,
    statistic: Callable[[Sequence[float]], float] | None,
    interval_estimator: Callable[[Sequence[float], float], tuple[float, float]] | None,
    resample_input_set_ids: Callable[[Sequence[str], int, int, int], Sequence[str]] | None,
    rng_name: str | None,
) -> dict[str, Any]:
    """Compute paired 95% CIs for all 21 arm pairs under supplied policies."""
    if not isinstance(arm_values, Mapping) or set(arm_values) != set(ARMS):
        raise EvaluationError("arm_values must contain exactly all seven E6 arms")
    normalized = {}
    for arm in ARMS:
        values = arm_values[arm]
        if not isinstance(values, Mapping) or not values:
            raise EvaluationError(f"arm {arm} must map input_set_id to finite metric values")
        if any(not isinstance(key, str) or not key.strip() for key in values):
            raise EvaluationError(f"arm {arm} contains an invalid input_set_id")
        if any(type(value) not in (int, float) or not math.isfinite(value)
               for value in values.values()):
            raise EvaluationError(f"arm {arm} contains a non-finite metric value")
        normalized[arm] = dict(values)
    common_ids = set(normalized[ARMS[0]])
    if not common_ids or any(set(normalized[arm]) != common_ids for arm in ARMS[1:]):
        raise EvaluationError("all seven arms must have values for the same paired input_set_ids")
    ordered_ids = sorted(common_ids)

    comparisons = {}
    for left, right in itertools.combinations(ARMS, 2):
        paired_differences = {
            input_id: normalized[left][input_id] - normalized[right][input_id]
            for input_id in ordered_ids
        }
        comparisons[f"{left}-minus-{right}"] = paired_bootstrap_interval(
            paired_differences, replicates=replicates, confidence_level=0.95, seed=seed,
            statistic=statistic, interval_estimator=interval_estimator,
            resample_input_set_ids=resample_input_set_ids, rng_name=rng_name,
        )
    evaluation_input = {"arm_values": normalized, "paired_input_set_ids": ordered_ids}
    provenance = {
        "arms": list(ARMS), "comparison_count": 21,
        "resampling_unit": "input_set",
        "statistic": getattr(statistic, "__name__", "injected"),
        "interval_method": getattr(interval_estimator, "__name__", "injected"),
        "confidence_level": 0.95,
        "replicates": replicates, "seed": seed, "random_generator": rng_name,
    }
    return evaluation_record(
        stage="paired_bootstrap_all_seven_arms", input_set_id=input_set_id,
        evaluation_input=evaluation_input, provenance=provenance,
        raw_output=comparisons, parsed_output={"comparisons": comparisons},
    )


def make_synthetic_planted_recovery_fixture() -> dict[str, Any]:
    """Tiny synthetic known-answer fixture for tests only; never a research sample."""
    return {
        "input_set_id": "synthetic-fixture-only",
        "benchmark_record": {"task": "fixture task", "evidence": "fixture evidence"},
        "planted_hypothesis": "The fixture treatment increases the measured outcome.",
        "provenance": {"kind": "synthetic_test_fixture", "not_for_research": True},
    }
