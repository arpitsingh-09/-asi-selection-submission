"""Fixed, auditable model-backed HypoBench prediction and recovery policies."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from evaluation import EvaluationError


ROOT = Path(__file__).resolve().parents[1]
PREDICTION_PROMPT = ROOT / "prompts/e6/13_hypobench_heldout_prediction.txt"
RECOVERY_PROMPT = ROOT / "prompts/e6/14_hypobench_hypothesis_recovery.txt"
PREDICTION_POLICY_ID = "e6-hypobench-generated-hypothesis-application-v1"
RECOVERY_POLICY_ID = "e6-hypobench-dataset-ground-truth-semantic-recovery-v1"
EVALUATOR_MODEL = "gemma3:12b"
EVALUATOR_MODEL_LAYER_DIGEST = (
    "sha256:13576eb6dd8d9d04b4da04d015ff343968628d3c2984195569d9d3585651d4f1"
)
EVALUATOR_SEED = 2026


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _render(path: Path, values: Mapping[str, str]) -> str:
    template = path.read_text(encoding="utf-8")
    for name, value in values.items():
        marker = "{{" + name + "}}"
        if template.count(marker) != 1:
            raise EvaluationError(f"prompt {path} must contain exactly one {marker}")
        template = template.replace(marker, value)
    if "{{" in template or "}}" in template:
        raise EvaluationError(f"prompt {path} contains unresolved placeholders")
    return template


def _strict_json_object(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, str):
        raise EvaluationError("model response must be a JSON string")

    def no_duplicate_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise EvaluationError(f"duplicate JSON key {key!r}")
            result[key] = value
        return result

    try:
        value = json.loads(raw, object_pairs_hook=no_duplicate_keys)
    except (json.JSONDecodeError, TypeError) as exc:
        raise EvaluationError(f"model response is not valid strict JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise EvaluationError("model response must be a JSON object")
    return value


def _client_settings(model_client: Any) -> dict[str, Any]:
    model = getattr(model_client, "model", None)
    options = getattr(model_client, "generation_options", None)
    if model != EVALUATOR_MODEL or not isinstance(options, Mapping):
        raise EvaluationError(f"HypoBench policy requires configured {EVALUATOR_MODEL} client")
    if options.get("temperature") != 0.0 or options.get("seed") != EVALUATOR_SEED:
        raise EvaluationError("HypoBench policy requires temperature=0 and seed=2026")
    return {"model": model, "model_layer_digest": EVALUATOR_MODEL_LAYER_DIGEST,
            "generation_options": dict(options)}


def make_hypobench_prediction_policy(
    model_client: Any, allowed_labels: Sequence[str], *, max_output_tokens: int = 32,
):
    """Create deterministic label-blind predictor; malformed output is invalid."""
    settings = _client_settings(model_client)
    if isinstance(allowed_labels, (str, bytes)) or not isinstance(allowed_labels, Sequence) \
            or not allowed_labels or any(not isinstance(value, str) or not value.strip()
                                         for value in allowed_labels):
        raise EvaluationError("allowed_labels must be a nonempty sequence of strings")
    labels = list(allowed_labels)
    if len(labels) != len(set(labels)):
        raise EvaluationError("allowed_labels must be unique")
    if type(max_output_tokens) is not int or max_output_tokens < 1:
        raise EvaluationError("max_output_tokens must be a positive integer")

    def predict(prepared: Mapping[str, Any]) -> dict[str, Any]:
        invalid_reason = None
        prompt = None
        reply = None
        try:
            if not isinstance(prepared, Mapping) or not isinstance(
                prepared.get("evaluation_input"), Mapping
            ):
                raise EvaluationError("prepared HypoBench evaluation input is invalid")
            input_data = prepared["evaluation_input"]
            observation = input_data.get("benchmark_record")
            hypotheses = input_data.get("generated_explanations")
            if not isinstance(observation, Mapping) or not isinstance(
                observation.get("task"), str
            ) or not isinstance(observation.get("observation"), str):
                raise EvaluationError("prediction input requires task and observation only")
            if isinstance(hypotheses, (str, bytes)) or not isinstance(hypotheses, Sequence) \
                    or len(hypotheses) != 6 or any(
                        not isinstance(item, str) or not item.strip() for item in hypotheses
                    ):
                raise EvaluationError("prediction input requires exactly six generated hypotheses")
            hypothesis_rows = [
                {"hypothesis_id": f"H{index + 1}", "text": text}
                for index, text in enumerate(hypotheses)
            ]
            prompt = _render(PREDICTION_PROMPT, {
                "TASK": observation["task"],
                "OBSERVATION": observation["observation"],
                "HYPOTHESES_JSON": json.dumps(hypothesis_rows, ensure_ascii=False),
                "ALLOWED_LABELS_JSON": json.dumps(labels, ensure_ascii=False),
            })
            caller = getattr(model_client, "call_with_token_limit", None)
            if not callable(caller):
                raise EvaluationError("HypoBench prediction model must enforce num_predict")
            reply = caller("hypobench_heldout_prediction", prompt,
                           max_output_tokens=max_output_tokens)
            raw = reply.get("raw_response") if isinstance(reply, Mapping) else reply
            parsed = _strict_json_object(raw)
            if set(parsed) != {"predicted_label", "supporting_hypothesis_ids"}:
                raise EvaluationError("prediction JSON has missing or extra fields")
            predicted = parsed["predicted_label"]
            support = parsed["supporting_hypothesis_ids"]
            if not isinstance(predicted, str) or predicted not in labels:
                raise EvaluationError("prediction label is missing or outside the declared label set")
            if isinstance(support, (str, bytes)) or not isinstance(support, list) or not support \
                    or any(not isinstance(value, str)
                           or value not in {f"H{i}" for i in range(1, 7)} for value in support) \
                    or len(set(support)) != len(support):
                raise EvaluationError("prediction must cite one or more supplied hypothesis IDs")
            prediction = predicted
            status = "valid"
        except Exception as exc:
            prediction = None
            status = "invalid_prediction"
            invalid_reason = str(exc)
            raw = reply.get("raw_response") if isinstance(reply, Mapping) else reply
            parsed = None
            support = []
        adapter = reply.get("adapter_metadata", {}) if isinstance(reply, Mapping) else {}
        return {
            "predicted_labels": [prediction],
            "prediction_status": status,
            "invalid_reason": invalid_reason,
            "supporting_hypothesis_ids": support,
            "raw_response": raw,
            "prediction_provenance": {
                "policy_id": PREDICTION_POLICY_ID,
                "prompt_path": str(PREDICTION_PROMPT.relative_to(ROOT)),
                "prompt_sha256": None if prompt is None else _sha256_text(prompt),
                "model_settings": settings,
                "max_output_tokens": max_output_tokens,
                "temperature": 0.0,
                "seed": EVALUATOR_SEED,
                "heldout_label_in_prediction_input": False,
                "backend_usage": {
                    key: adapter.get(key) for key in (
                        "prompt_eval_count", "eval_count", "total_tokens", "done_reason",
                    )
                },
            },
        }

    def predict_many(prepared_inputs, *, max_workers=1):
        # Transport batching only. Each example retains the exact same single-
        # observation prompt, decoding, output cap, error policy and seed.
        if type(max_workers) is not int or not 1 <= max_workers <= 4:
            raise EvaluationError("prediction concurrency must be 1 through 4")
        if max_workers == 1 or not getattr(model_client, 'supports_independent_parallel_requests', False):
            return [predict(item) for item in prepared_inputs]
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            return list(executor.map(predict, prepared_inputs))

    predict.predict_many = predict_many
    predict.policy_identity = {"policy_id": PREDICTION_POLICY_ID, "model_settings": settings,
                               "max_output_tokens": max_output_tokens,
                               "prompt_template_sha256": _sha256_text(PREDICTION_PROMPT.read_text()),
                               "policy_implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    return predict


def make_hypobench_recovery_policy(
    model_client: Any, *, max_output_tokens: int = 512,
):
    """Create one fixed-prompt judge returning the complete 6-by-14 verdict matrix."""
    settings = _client_settings(model_client)
    if type(max_output_tokens) is not int or max_output_tokens < 1:
        raise EvaluationError("max_output_tokens must be a positive integer")

    def judge(generated: Sequence[str], planted: Sequence[str]) -> dict[str, Any]:
        if len(generated) != 6 or len(planted) != 14:
            raise EvaluationError("recovery judge requires six generated and 14 planted hypotheses")
        generated_rows = [{"hypothesis_id": f"H{i + 1}", "text": text}
                          for i, text in enumerate(generated)]
        planted_rows = [{"ground_truth_id": f"GT{i + 1}", "text": text}
                        for i, text in enumerate(planted)]
        prompt = _render(RECOVERY_PROMPT, {
            "GENERATED_HYPOTHESES_JSON": json.dumps(generated_rows, ensure_ascii=False),
            "PLANTED_HYPOTHESES_JSON": json.dumps(planted_rows, ensure_ascii=False),
        })
        caller = getattr(model_client, "call_with_token_limit", None)
        if not callable(caller):
            raise EvaluationError("HypoBench recovery judge must enforce num_predict")
        reply = caller("hypobench_dataset_level_recovery", prompt,
                       max_output_tokens=max_output_tokens)
        raw = reply.get("raw_response") if isinstance(reply, Mapping) else reply
        parse_error = None
        disagreement_count = 0
        invalid_cell_count = 0
        try:
            parsed = _strict_json_object(raw)
            if set(parsed) != {"generated_first", "planted_first"}:
                raise EvaluationError("recovery JSON must contain both comparison-order matrices")
            first, second = parsed["generated_first"], parsed["planted_first"]
            if not isinstance(first, list) or not isinstance(second, list):
                raise EvaluationError("recovery order results must be matrices")
            verdicts = {"MATCH", "NO_MATCH", "AMBIGUOUS"}
            matrix = []
            for row_index in range(6):
                first_row = first[row_index] if row_index < len(first) and isinstance(first[row_index], list) else []
                second_row = second[row_index] if row_index < len(second) and isinstance(second[row_index], list) else []
                invalid_cell_count += max(0, len(first_row) - 14)
                invalid_cell_count += max(0, len(second_row) - 14)
                combined_row = []
                for column_index in range(14):
                    left = first_row[column_index] if column_index < len(first_row) else None
                    right = second_row[column_index] if column_index < len(second_row) else None
                    if not isinstance(left, str) or left not in verdicts \
                            or not isinstance(right, str) or right not in verdicts:
                        invalid_cell_count += 1
                        combined_row.append("AMBIGUOUS")
                    elif left == right:
                        combined_row.append(left)
                    else:
                        disagreement_count += 1
                        combined_row.append("AMBIGUOUS")
                matrix.append(combined_row)
            invalid_cell_count += max(0, len(first) - 6) * 14
            invalid_cell_count += max(0, len(second) - 6) * 14
        except EvaluationError as exc:
            matrix = []
            parse_error = str(exc)
        adapter = reply.get("adapter_metadata", {}) if isinstance(reply, Mapping) else {}
        return {
            "judgments": matrix,
            "raw_response": raw,
            "invalid_response_reason": parse_error,
            "invalid_judgment_cell_count": invalid_cell_count,
            "order_disagreement_cell_count": disagreement_count,
            "prediction_provenance": {
                "policy_id": RECOVERY_POLICY_ID,
                "prompt_path": str(RECOVERY_PROMPT.relative_to(ROOT)),
                "prompt_sha256": _sha256_text(prompt),
                "model_settings": settings,
                "max_output_tokens": max_output_tokens,
                "temperature": 0.0,
                "seed": EVALUATOR_SEED,
                "blinded_to_arm_identity": True,
                "backend_usage": {
                    key: adapter.get(key) for key in (
                        "prompt_eval_count", "eval_count", "total_tokens", "done_reason",
                    )
                },
            },
        }

    return judge


def create_local_hypobench_evaluators(allowed_labels: Sequence[str], *, context_limit: int,
                                      prediction_output_tokens: int, recovery_output_tokens: int):
    """Build configured local evaluation callbacks; performs no inference here."""
    from ollama_adapter import OllamaModelClient

    if type(context_limit) is not int or context_limit < 1:
        raise EvaluationError("explicit evaluator context required")
    if any(type(value) is not int or not 0 < value < context_limit for value in (prediction_output_tokens, recovery_output_tokens)):
        raise EvaluationError("explicit evaluator output limits must fit context")
    client = OllamaModelClient(
        model=EVALUATOR_MODEL,
        generation_options={"temperature": 0.0, "seed": EVALUATOR_SEED, "num_ctx": context_limit},
        preflight_context_limit=context_limit,
    )
    return {
        "client": client,
        "prediction_policy": make_hypobench_prediction_policy(client, allowed_labels, max_output_tokens=prediction_output_tokens),
        "recovery_policy": make_hypobench_recovery_policy(client, max_output_tokens=recovery_output_tokens),
    }
