#!/usr/bin/env python3
"""Mockable E6 question pipeline with explicit policy gates.

Callers inject the model function. The QH-sel/QH-rand preparation contract is
implemented here; other unresolved settings still block their dependent stages.
Every raw response and candidate is retained.
"""

from __future__ import annotations

import itertools
import hashlib
import json
import re
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence, Union

from prepare_dataset import canonicalize_arxiv_id

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SETTINGS = Path(__file__).with_name("question_pipeline_config.json")
QH_CANDIDATE_COUNT = 6
QH_RAND_SEED = 2026
QH_RAND_PREFIX = "E6-QH-RAND-v1"
QH_SEL_RANKING_PROMPT = "prompts/e6/12_qh_sel_ranking.txt"
QH_SEL_WEIGHTS = {
    "novelty": 0.30,
    "specificity": 0.25,
    "scientific_significance": 0.25,
    "evidence_grounding": 0.20,
}
D_SHUFFLED_SEED = 2026
D_SHUFFLED_ALGORITHM = "sha256_hash_ordered_derangement_no_reuse_v1"
D_SHUFFLED_KEY_EXPRESSION = "E6-D-SHUFFLED-v1|2026|<recipient_id>|<donor_id>"


class PipelineError(ValueError):
    """Invalid input, response, or unresolved setting for a requested stage."""


@dataclass(frozen=True)
class PipelineSettings:
    candidate_count: int | None = None
    deduplication_threshold: float | None = None
    clustering_policy: str | None = None
    representative_selection_policy: str | None = None
    qh_sel_ranking_weights: Mapping[str, float] | None = None
    qh_sel_tie_break_policy: str | None = None
    random_seed: int | str | None = None
    random_sampler: str | None = None
    random_generator_and_version: str | None = None
    per_input_seed_derivation: str | None = None
    selected_hypothesis_max_attempts: int | None = None
    selected_hypothesis_retry_policy: str | None = None
    arm_hypothesis_max_attempts: int | None = None
    arm_hypothesis_retry_policy: str | None = None
    d_empty_task_evidence_policy: str | None = None
    d_shuffled_donor_constraints: Mapping[str, Any] | None = None
    d_shuffled_assignment_algorithm: str | None = None
    d_shuffled_assignment_seed: int | str | None = None
    d_shuffled_within_split_only: bool | None = None
    d_shuffled_donor_reuse_policy: str | None = None
    d_empty_evidence_fields: Sequence[str] | None = None
    selection_count: int = 3

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "PipelineSettings":
        return cls(
            candidate_count=value.get("candidate_count"),
            deduplication_threshold=value.get("deduplication_threshold"),
            clustering_policy=value.get("clustering_policy"),
            representative_selection_policy=value.get("representative_selection_policy"),
            qh_sel_ranking_weights=value.get("qh_sel_ranking_weights"),
            qh_sel_tie_break_policy=value.get("qh_sel_tie_break_policy"),
            random_seed=value.get("random_seed"),
            random_sampler=value.get("random_sampler"),
            random_generator_and_version=value.get("random_generator_and_version"),
            per_input_seed_derivation=value.get("per_input_seed_derivation"),
            selected_hypothesis_max_attempts=value.get("selected_hypothesis_max_attempts"),
            selected_hypothesis_retry_policy=value.get("selected_hypothesis_retry_policy"),
            arm_hypothesis_max_attempts=value.get("arm_hypothesis_max_attempts"),
            arm_hypothesis_retry_policy=value.get("arm_hypothesis_retry_policy"),
            d_empty_task_evidence_policy=value.get("d_empty_task_evidence_policy"),
            d_shuffled_donor_constraints=value.get("d_shuffled_donor_constraints"),
            d_shuffled_assignment_algorithm=value.get("d_shuffled_assignment_algorithm"),
            d_shuffled_assignment_seed=value.get("d_shuffled_assignment_seed"),
            d_shuffled_within_split_only=value.get("d_shuffled_within_split_only"),
            d_shuffled_donor_reuse_policy=value.get("d_shuffled_donor_reuse_policy"),
            d_empty_evidence_fields=value.get("d_empty_evidence_fields"),
            selection_count=value.get("selection_count", 3),
        )

    @classmethod
    def load(cls, path: Path = DEFAULT_SETTINGS) -> "PipelineSettings":
        with Path(path).open(encoding="utf-8") as handle:
            value = json.load(handle)
        if not isinstance(value, dict):
            raise PipelineError("question pipeline settings must be a JSON object")
        if value.get("status") != "unresolved":
            raise PipelineError("settings status must remain explicitly unresolved")
        return cls.from_mapping(value)

    def validate_candidate_generation(self) -> None:
        if type(self.candidate_count) is not int or self.candidate_count < 1:
            raise PipelineError("candidate_count is unresolved; supply an approved positive integer")

    def validate_selection_count(self) -> None:
        if type(self.selection_count) is not int or self.selection_count != 3:
            raise PipelineError("selection_count must match the existing three-question prompt contract")


@dataclass
class PipelineState:
    """Complete audit trail for candidate, pairwise, clustering, and selection stages."""

    candidate_records: list[dict[str, Any]] = field(default_factory=list)
    candidate_generation_complete: bool = False
    pairwise_records: list[dict[str, Any]] = field(default_factory=list)
    clusters: list[dict[str, Any]] = field(default_factory=list)
    representatives: list[str] = field(default_factory=list)
    ranking_result: dict[str, Any] | None = None
    selections: dict[str, Any] = field(default_factory=dict)
    hypothesis_generations: list[dict[str, Any]] = field(default_factory=list)
    raw_responses: list[dict[str, Any]] = field(default_factory=list)
    model_calls: list[dict[str, Any]] = field(default_factory=list)
    preparation_provenance: dict[str, Any] = field(default_factory=dict)
    errors: list[dict[str, Any]] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "failed" if self.errors else "ok"

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "candidate_generation_complete": self.candidate_generation_complete,
            "candidate_records": self.candidate_records,
            "pairwise_records": self.pairwise_records,
            "clusters": self.clusters,
            "representatives": self.representatives,
            "ranking_result": self.ranking_result,
            "selections": self.selections,
            "hypothesis_generations": self.hypothesis_generations,
            "raw_responses": self.raw_responses,
            "model_calls": self.model_calls,
            "preparation_provenance": self.preparation_provenance,
            "errors": self.errors,
        }


ModelCall = Callable[[str, str], str]
Clusterer = Callable[[Sequence[str], Sequence[Mapping[str, Any]]], Sequence[Sequence[str]]]
RepresentativeSelector = Callable[[Sequence[str], Sequence[Mapping[str, Any]]], str]
Ranker = Callable[[Sequence[Mapping[str, Any]], Mapping[str, float]], Mapping[str, Any]]
Sampler = Callable[[Sequence[str], int, Union[int, str]], Sequence[str]]
RetryPromptBuilder = Callable[[str, str, Sequence[str], int], str]
ResponseValidator = Callable[[Any], Any]
@dataclass(frozen=True)
class TrustedDEmptyAuditResult:
    """Typed audit attestation; it does not itself implement leakage detection."""

    trust_status: str
    auditor_id: str
    audit_id: str
    audit_complete: bool
    audit_scope: str
    leakage_check_performed: bool
    retained_task_leakage_detected: bool
    recipient_id: str
    scrubbed_task_sha256: str
    removed_fields: Any
    removed_evidence_sha256: Any
    rendered_evidence: str


class TrustedDEmptyEvidenceAuditor(ABC):
    """Explicit production trust boundary for an externally implemented auditor.

    Subclasses must be supplied by a trusted production integration. This
    interface makes no claim that a callback or fixture proves semantic
    leakage detection. Concrete integrations must bind the task and removed
    evidence to their independently validated source; TRAIN uses TrainTaskAuditor.
    """

    @abstractmethod
    def audit(
        self, recipient_id: str, retained_task_text: str,
        original_evidence: Mapping[str, Any], policy: str,
    ) -> TrustedDEmptyAuditResult:
        """Return an explicit trusted audit attestation for the exact inputs."""
        raise NotImplementedError


DonorAssignmentCheck = Callable[[str, str, Mapping[str, Any], Mapping[str, Any]], Mapping[str, Any]]


def _read_prompt(path: str) -> str:
    prompt_path = ROOT / path
    return prompt_path.read_text(encoding="utf-8")


def _render(template: str, **values: str) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    unresolved = re.findall(r"\{\{[^{}]+\}\}", rendered)
    if unresolved:
        raise PipelineError("unfilled prompt placeholders: " + ", ".join(unresolved))
    return rendered


def _record_error(state: PipelineState, stage: str, message: str, **details: Any) -> None:
    state.errors.append({"stage": stage, "error": message, **details})


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_json(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return _sha256_text(encoded)


def _audited_model_call(
    state: PipelineState, model_client: Callable[[str, str], Any],
    input_set_id: str,
) -> ModelCall:
    """Adapt the injected client to the text pipeline and retain call accounting."""
    def call(stage: str, prompt: str) -> str:
        started_utc = datetime.now(timezone.utc).isoformat()
        started = time.monotonic()
        record: dict[str, Any] = {
            "input_set_id": input_set_id,
            "stage": stage,
            "prompt_sha256": _sha256_text(prompt),
            "prompt_characters": len(prompt),
            "started_at_utc": started_utc,
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "cost": None,
            "latency_seconds": None,
            "status": "started",
        }
        try:
            reply = model_client(stage, prompt)
            if isinstance(reply, str):
                raw = reply
                metadata: Mapping[str, Any] = {}
                accounting: Mapping[str, Any] = {}
            elif isinstance(reply, Mapping):
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
                metadata_value = reply.get("adapter_metadata")
                metadata = metadata_value if isinstance(metadata_value, Mapping) else {}
                for key in ("model", "model_identity", "generation_settings", "http_status"):
                    if key in reply and key not in metadata:
                        metadata = {**metadata, key: reply[key]}
            else:
                raise PipelineError("model client must return text or a response mapping")

            record.update({key: accounting.get(key) for key in (
                "input_tokens", "output_tokens", "total_tokens", "cost", "latency_seconds",
            )})
            if record["latency_seconds"] is None:
                record["latency_seconds"] = time.monotonic() - started
            if record["total_tokens"] is None and all(
                type(record[key]) is int for key in ("input_tokens", "output_tokens")
            ):
                record["total_tokens"] = record["input_tokens"] + record["output_tokens"]
            record["adapter_metadata"] = dict(metadata)
            record["raw_response_sha256"] = _sha256_text(raw)
            record["status"] = "returned"
            state.model_calls.append(record)
            return raw
        except Exception as exc:
            record.update({"status": "failed", "error": str(exc)})
            error_metadata = getattr(exc, "audit_metadata", None)
            if isinstance(error_metadata, Mapping):
                record["adapter_metadata"] = dict(error_metadata)
                for key in ("input_tokens", "output_tokens", "total_tokens"):
                    if type(error_metadata.get(key)) is int:
                        record[key] = error_metadata[key]
                if record["latency_seconds"] is None:
                    record["latency_seconds"] = error_metadata.get("latency_seconds")
            elif record["latency_seconds"] is None:
                record["latency_seconds"] = time.monotonic() - started
            state.model_calls.append(record)
            raise
    return call


def _run_validated_generation(
    state: PipelineState,
    stage: str,
    prompt: str,
    model_call: ModelCall,
    max_attempts: int,
    retry_policy: str | None,
    retry_prompt_builder: RetryPromptBuilder | None,
    validator: ResponseValidator,
) -> dict[str, Any]:
    """Shared response/retry utility used by question and arm generators."""
    if type(max_attempts) is not int or max_attempts < 1:
        raise PipelineError("generation max_attempts is unresolved")
    if max_attempts > 1 and (not retry_policy or retry_prompt_builder is None):
        raise PipelineError("retry policy name and implementation are required for multiple attempts")

    attempts = []
    previous_raw = ""
    previous_errors: list[str] = []
    final_parsed = None
    final_output = None
    for number in range(1, max_attempts + 1):
        attempt = {
            "attempt": number, "prompt": None, "raw_response": None,
            "parsed_output": None, "normalized_output": None,
            "validation_errors": [],
        }
        try:
            current_prompt = prompt if number == 1 else retry_prompt_builder(
                prompt, previous_raw, previous_errors, number,
            )
            attempt["prompt"] = current_prompt
            raw = model_call(stage, current_prompt)
            previous_raw = raw
            attempt["raw_response"] = raw
            state.raw_responses.append({"stage": stage, "attempt": number, "raw": raw})
            parsed = json.loads(raw)
            attempt["parsed_output"] = parsed
            normalized = validator(parsed)
            attempt["normalized_output"] = normalized
            final_parsed = parsed
            final_output = normalized
            previous_errors = []
        except Exception as exc:
            message = str(exc)
            attempt["validation_errors"].append(message)
            previous_errors = [message]
            if attempt["raw_response"] is None:
                attempt["call_error"] = message
        attempts.append(attempt)
        if final_output is not None:
            break

    return {
        "status": "ok" if final_output is not None else "failed",
        "attempt_history": attempts,
        "parsed_output": final_parsed,
        "raw_response": attempts[-1]["raw_response"] if attempts else None,
        "normalized_output": final_output,
        "errors": [] if final_output is not None else previous_errors,
        "retry_policy": retry_policy,
    }


def generate_candidates(
    state: PipelineState,
    settings: PipelineSettings,
    model_call: ModelCall,
    domain_and_task: str,
    evidence: str,
    prompt_path: str = "prompts/e6/07_question_candidate_generation.txt",
) -> PipelineState:
    """Call the injected model and retain the full response and every returned item."""
    try:
        settings.validate_candidate_generation()
        prompt = _render(
            _read_prompt(prompt_path),
            N_QUESTIONS=str(settings.candidate_count),
            DOMAIN_AND_TASK=domain_and_task,
            EVIDENCE=evidence,
        )
        raw = model_call("candidate_generation", prompt)
        state.raw_responses.append({"stage": "candidate_generation", "raw": raw})
    except Exception as exc:
        _record_error(state, "candidate_generation", str(exc))
        return state

    try:
        parsed = json.loads(raw)
        question_items = parsed.get("questions") if isinstance(parsed, dict) else None
        if not isinstance(question_items, list):
            raise PipelineError("response must contain a questions array")
    except (json.JSONDecodeError, PipelineError) as exc:
        state.candidate_records.append({
            "candidate_id": None, "source_index": None, "text": None,
            "raw_item": raw, "validation_status": "invalid_response",
            "validation_errors": [str(exc)],
        })
        _record_error(state, "candidate_generation_parse", str(exc))
        return state

    seen_source_ids = set()
    for index, item in enumerate(question_items, start=1):
        issues = []
        text = item.get("text") if isinstance(item, dict) else None
        source_id = item.get("id") if isinstance(item, dict) else None
        if not isinstance(text, str) or not text.strip():
            issues.append("question text must be a nonempty string")
        if not isinstance(source_id, str) or not source_id.strip():
            issues.append("question id must be a nonempty string")
        elif source_id in seen_source_ids:
            issues.append("question id is duplicated")
        else:
            seen_source_ids.add(source_id)
        if source_id != f"Q{index}":
            issues.append("question ids must be consecutive beginning with Q1")
        state.candidate_records.append({
            "candidate_id": f"CQ{index}",
            "source_index": index,
            "source_id": source_id,
            "text": text,
            "raw_item": item,
            "validation_status": "invalid" if issues else "valid",
            "validation_errors": issues,
        })

    if len(question_items) != settings.candidate_count:
        _record_error(
            state, "candidate_generation_validation",
            "candidate count does not match configured count",
            expected=settings.candidate_count, observed=len(question_items),
        )
    invalid_count = sum(row["validation_status"] != "valid" for row in state.candidate_records)
    if invalid_count:
        _record_error(
            state, "candidate_generation_validation",
            "one or more candidate records are invalid", invalid_count=invalid_count,
        )
    state.candidate_generation_complete = (
        len(question_items) == settings.candidate_count and invalid_count == 0
    )
    return state


def _parse_pairwise(raw: str, threshold: float | None) -> tuple[bool, dict[str, Any]]:
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise PipelineError("pairwise response must be a JSON object")
    if type(parsed.get("same_question")) is bool:
        return parsed["same_question"], parsed
    similarity = parsed.get("similarity")
    if isinstance(similarity, (int, float)) and not isinstance(similarity, bool):
        if threshold is None:
            raise PipelineError("numeric similarity returned but deduplication_threshold is unresolved")
        if not isinstance(threshold, (int, float)) or isinstance(threshold, bool) or not 0 <= threshold <= 1:
            raise PipelineError("deduplication_threshold must be in [0, 1]")
        if not 0 <= similarity <= 1:
            raise PipelineError("similarity must be in [0, 1]")
        return similarity >= threshold, parsed
    raise PipelineError("response must contain Boolean same_question or numeric similarity")


def compare_candidates(
    state: PipelineState,
    settings: PipelineSettings,
    model_call: ModelCall,
    prompt_path: str = "prompts/e6/08_same_question.txt",
) -> PipelineState:
    """Compare every valid candidate pair, preserving failures and responses."""
    if not state.candidate_generation_complete:
        _record_error(state, "pairwise_deduplication", "candidate generation did not pass its output contract")
        return state
    valid = [row for row in state.candidate_records if row["validation_status"] == "valid"]
    if len(valid) != len(state.candidate_records):
        _record_error(state, "pairwise_deduplication", "invalid candidates retained; pairwise stage blocked")
        return state
    template = _read_prompt(prompt_path)
    for left, right in itertools.combinations(valid, 2):
        pair = {
            "question_a": left["candidate_id"], "question_b": right["candidate_id"],
            "text_a": left["text"], "text_b": right["text"],
        }
        raw = None
        try:
            prompt = _render(
                template, TYPE_A="research question", TEXT_A=left["text"],
                TYPE_B="research question", TEXT_B=right["text"],
            )
            raw = model_call("pairwise_deduplication", prompt)
            state.raw_responses.append({
                "stage": "pairwise_deduplication", "pair": [pair["question_a"], pair["question_b"]],
                "raw": raw,
            })
            duplicate, parsed = _parse_pairwise(raw, settings.deduplication_threshold)
            state.pairwise_records.append({
                **pair, "decision": "duplicate" if duplicate else "distinct",
                "parsed": parsed, "raw": raw, "status": "ok",
            })
        except Exception as exc:
            state.pairwise_records.append({
                **pair, "decision": None, "parsed": None, "raw": raw,
                "status": "failed", "error": str(exc),
            })
            _record_error(
                state, "pairwise_deduplication", str(exc),
                pair=[pair["question_a"], pair["question_b"]],
            )
    return state


def compare_candidates_batch(
    state: PipelineState,
    model_call: ModelCall,
    prompt_path: str = "prompts/e6/08_question_dedup.txt",
) -> PipelineState:
    """Request and strictly validate the complete pairwise table in one call."""
    valid = [row for row in state.candidate_records if row.get("validation_status") == "valid"]
    if not state.candidate_generation_complete or len(valid) != QH_CANDIDATE_COUNT:
        _record_error(
            state, "pairwise_deduplication_batch",
            "exactly six valid generated candidates are required",
            candidate_count=len(valid),
        )
        return state

    expected_pairs = list(itertools.combinations(
        [row["candidate_id"] for row in valid], 2,
    ))
    expected_pair_keys = {frozenset(pair) for pair in expected_pairs}
    candidate_payload = {
        "candidate_questions": [
            {"id": row["candidate_id"], "text": row["text"]} for row in valid
        ]
    }
    prompt = _read_prompt(prompt_path) + "\n\nCANDIDATE QUESTIONS\n" + json.dumps(
        candidate_payload, ensure_ascii=False, indent=2,
    )
    raw = None
    state.pairwise_records = []
    state.preparation_provenance["pairwise_deduplication"] = {
        "prompt_path": prompt_path,
        "prompt_sha256": _sha256_text(prompt),
        "candidate_pool_sha256": _sha256_json(candidate_payload["candidate_questions"]),
        "expected_pair_count": len(expected_pairs),
        "request_count": 1,
        "status": "started",
    }
    try:
        raw = model_call("pairwise_deduplication_batch", prompt)
        state.raw_responses.append({"stage": "pairwise_deduplication_batch", "raw": raw})
        parsed = json.loads(raw)
        if not isinstance(parsed, dict) or set(parsed) != {"pairwise_comparisons"}:
            raise PipelineError("batch deduplication response must contain only pairwise_comparisons")
        comparisons = parsed.get("pairwise_comparisons")
        if not isinstance(comparisons, list):
            raise PipelineError("pairwise_comparisons must be an array")
        observed: dict[frozenset[str], dict[str, Any]] = {}
        for index, item in enumerate(comparisons, start=1):
            if not isinstance(item, dict) or set(item) != {
                "question_a", "question_b", "is_duplicate", "reason",
            }:
                raise PipelineError(f"pairwise comparison {index} has an invalid structure")
            left, right = item["question_a"], item["question_b"]
            if not isinstance(left, str) or not isinstance(right, str) or left == right:
                raise PipelineError(f"pairwise comparison {index} must name two different question IDs")
            pair_key = frozenset((left, right))
            if pair_key not in expected_pair_keys:
                raise PipelineError(f"pairwise comparison {index} names an unknown or invalid pair")
            if pair_key in observed:
                raise PipelineError(f"pairwise pair {sorted(pair_key)} appears more than once")
            if type(item["is_duplicate"]) is not bool:
                raise PipelineError(f"pairwise decision {index} must be Boolean")
            if not isinstance(item["reason"], str) or not item["reason"].strip():
                raise PipelineError(f"pairwise comparison {index} needs a nonempty reason")
            observed[pair_key] = item

        missing = expected_pair_keys - set(observed)
        if missing:
            raise PipelineError(f"batch deduplication omitted {len(missing)} expected pairs")
        records = {row["candidate_id"]: row for row in valid}
        for left, right in expected_pairs:
            item = observed[frozenset((left, right))]
            state.pairwise_records.append({
                "question_a": left,
                "question_b": right,
                "text_a": records[left]["text"],
                "text_b": records[right]["text"],
                "decision": "duplicate" if item["is_duplicate"] else "distinct",
                "is_duplicate": item["is_duplicate"],
                "reason": item["reason"],
                "parsed": dict(item),
                "raw": raw,
                "status": "ok",
            })
        state.preparation_provenance["pairwise_deduplication"].update({
            "status": "ok",
            "observed_pair_count": len(observed),
            "pair_decisions_sha256": _sha256_json([
                {"question_a": row["question_a"], "question_b": row["question_b"],
                 "is_duplicate": row["is_duplicate"]}
                for row in state.pairwise_records
            ]),
        })
    except Exception as exc:
        state.preparation_provenance["pairwise_deduplication"].update({
            "status": "failed", "raw_response": raw, "error": str(exc),
        })
        _record_error(state, "pairwise_deduplication_batch", str(exc))
    return state


def cluster_candidates_complete_link(state: PipelineState) -> PipelineState:
    """Greedily form complete-link clusters in candidate order.

    Each candidate joins the earliest-created cluster only when it is marked a
    duplicate of every existing member. The first candidate in each cluster is
    its representative.
    """
    candidates = [row for row in state.candidate_records if row.get("validation_status") == "valid"]
    if not state.candidate_generation_complete or len(candidates) != QH_CANDIDATE_COUNT:
        _record_error(state, "clustering", "exactly six valid candidates are required")
        return state
    expected = {
        frozenset(pair)
        for pair in itertools.combinations([row["candidate_id"] for row in candidates], 2)
    }
    if (len(state.pairwise_records) != len(expected)
            or any(row.get("status") != "ok" or type(row.get("is_duplicate")) is not bool
                   for row in state.pairwise_records)):
        _record_error(state, "clustering", "complete validated pairwise decisions are required")
        return state
    decision_by_pair = {
        frozenset((row["question_a"], row["question_b"])): row["is_duplicate"]
        for row in state.pairwise_records
    }
    if set(decision_by_pair) != expected:
        _record_error(state, "clustering", "pairwise records must cover each expected pair exactly once")
        return state

    clusters: list[list[str]] = []
    for candidate in candidates:
        candidate_id = candidate["candidate_id"]
        compatible_cluster = next((cluster for cluster in clusters if all(
            decision_by_pair[frozenset((candidate_id, member))] for member in cluster
        )), None)
        if compatible_cluster is None:
            clusters.append([candidate_id])
        else:
            compatible_cluster.append(candidate_id)

    records_by_id = {row["candidate_id"]: row for row in candidates}
    state.clusters = [{
        "cluster_id": f"C{index}",
        "member_candidate_ids": list(members),
        "representative_candidate_id": members[0],
        "representative_policy": "earliest_candidate_generation_order",
        "clustering_policy": "complete_link_candidate_generation_order_v1",
    } for index, members in enumerate(clusters, start=1)]
    state.representatives = [members[0] for members in clusters]
    candidate_payload = [
        {"question_id": row["candidate_id"], "text": row["text"]} for row in candidates
    ]
    representative_payload = [
        {"question_id": candidate_id, "text": records_by_id[candidate_id]["text"]}
        for candidate_id in state.representatives
    ]
    state.preparation_provenance.update({
        "clustering": {
            "algorithm": "complete_link_candidate_generation_order_v1",
            "representative_rule": "earliest_candidate_generation_order",
            "clusters": state.clusters,
            "candidate_pool_sha256": _sha256_json(candidate_payload),
            "representative_pool_sha256": _sha256_json(representative_payload),
            "representative_ids": list(state.representatives),
            "status": "ok",
        }
    })
    return state


def select_qh_rand_sha256(
    representative_ids: Sequence[str], input_set_id: str,
) -> dict[str, Any]:
    """Select three representatives by the approved deterministic SHA256 key."""
    if not isinstance(input_set_id, str) or not input_set_id.strip():
        raise PipelineError("input_set_id is required for QH-rand SHA256 selection")
    ids = list(representative_ids)
    if len(ids) < 3:
        raise PipelineError("fewer than three representatives remain")
    if any(not isinstance(value, str) or not value for value in ids) or len(set(ids)) != len(ids):
        raise PipelineError("representative IDs must be unique nonempty strings")
    keyed = []
    for generation_order, question_id in enumerate(ids):
        key = f"{QH_RAND_PREFIX}|{QH_RAND_SEED}|{input_set_id}|{question_id}"
        keyed.append({
            "question_id": question_id,
            "generation_order": generation_order,
            "key": key,
            "key_sha256": _sha256_text(key),
        })
    keyed.sort(key=lambda row: (row["key_sha256"], row["generation_order"]))
    selected = keyed[:3]
    return {
        "status": "ok",
        "selected_candidate_ids": [row["question_id"] for row in selected],
        "seed": QH_RAND_SEED,
        "input_set_id": input_set_id,
        "sampler": "sha256_key_ascending_v1",
        "key_expression": f"{QH_RAND_PREFIX}|{QH_RAND_SEED}|<input_set_id>|<question_id>",
        "selection_keys": keyed,
    }


def _parse_qh_sel_scores(raw: str, representative_ids: Sequence[str]) -> list[dict[str, Any]]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PipelineError(f"QH-sel ranking returned malformed JSON: {exc}") from exc
    if not isinstance(parsed, dict) or set(parsed) != {"scores"}:
        raise PipelineError("QH-sel ranking response must contain only a scores array")
    score_rows = parsed["scores"]
    if not isinstance(score_rows, list):
        raise PipelineError("QH-sel scores must be an array")
    dimensions = tuple(QH_SEL_WEIGHTS)
    observed: dict[str, dict[str, Any]] = {}
    expected = set(representative_ids)
    for index, item in enumerate(score_rows, start=1):
        if not isinstance(item, dict) or set(item) != {"question_id", *dimensions}:
            raise PipelineError(f"QH-sel score row {index} has an invalid structure")
        question_id = item["question_id"]
        if not isinstance(question_id, str) or question_id not in expected:
            raise PipelineError(f"QH-sel score row {index} names an unknown representative")
        if question_id in observed:
            raise PipelineError(f"QH-sel representative {question_id} is scored more than once")
        for dimension in dimensions:
            value = item[dimension]
            if type(value) is not int or not 1 <= value <= 5:
                raise PipelineError(f"{dimension} score for {question_id} must be an integer from 1 to 5")
        observed[question_id] = dict(item)
    if set(observed) != expected:
        raise PipelineError("QH-sel ranking must score every representative exactly once")
    return [observed[question_id] for question_id in representative_ids]


def prepare_qh_selection_arms(
    state: PipelineState,
    settings: PipelineSettings,
    model_client: Callable[[str, str], Any],
    input_set_id: str,
    domain_and_task: str,
    evidence: str,
    *,
    ranking_prompt_path: str = QH_SEL_RANKING_PROMPT,
) -> PipelineState:
    """Build one audited pool shared by QH-sel and QH-rand, then select each."""
    if not isinstance(input_set_id, str) or not input_set_id.strip():
        _record_error(state, "qh_selection_preparation", "input_set_id is required")
        return state
    if not isinstance(domain_and_task, str) or not domain_and_task.strip():
        _record_error(state, "qh_selection_preparation", "domain_and_task is required")
        return state
    if not isinstance(evidence, str) or not evidence.strip():
        _record_error(state, "qh_selection_preparation", "nonempty evidence is required")
        return state
    if settings.candidate_count != QH_CANDIDATE_COUNT:
        _record_error(state, "qh_selection_preparation", "candidate_count must be exactly six")
        return state
    if settings.selection_count != 3:
        _record_error(state, "qh_selection_preparation", "selection_count must be exactly three")
        return state
    if dict(settings.qh_sel_ranking_weights or {}) != QH_SEL_WEIGHTS:
        _record_error(state, "qh_selection_preparation", "QH-sel ranking weights do not match the specified weights")
        return state
    if settings.qh_sel_tie_break_policy != "weighted_score_desc_then_generation_order":
        _record_error(state, "qh_selection_preparation", "QH-sel tie-break policy is unresolved or inconsistent")
        return state
    if settings.random_seed != QH_RAND_SEED:
        _record_error(state, "qh_selection_preparation", "QH-rand seed must be 2026")
        return state
    expected_derivation = "E6-QH-RAND-v1|2026|<input_set_id>|<question_id>"
    if (settings.random_sampler != "sha256_key_ascending_v1"
            or settings.random_generator_and_version != "SHA256"
            or settings.per_input_seed_derivation != expected_derivation):
        _record_error(state, "qh_selection_preparation", "QH-rand SHA256 selection settings are unresolved or inconsistent")
        return state

    state.preparation_provenance = {
        "schema_version": "e6-qh-selection-preparation-v1",
        "input_set_id": input_set_id,
        "task_sha256": _sha256_text(domain_and_task),
        "evidence_sha256": _sha256_text(evidence),
        "candidate_count": QH_CANDIDATE_COUNT,
        "selection_count": 3,
        "status": "started",
    }
    audited_call = _audited_model_call(state, model_client, input_set_id)
    generate_candidates(state, settings, audited_call, domain_and_task, evidence)
    if not state.candidate_generation_complete:
        state.preparation_provenance["status"] = "candidate_generation_failed"
        for arm in ("QH-sel", "QH-rand"):
            state.selections[arm] = {"status": "blocked_candidate_generation_failed"}
        return state

    candidates = [
        {"question_id": row["candidate_id"], "text": row["text"]}
        for row in state.candidate_records
    ]
    candidate_pool_hash = _sha256_json(candidates)
    state.preparation_provenance.update({
        "candidate_generation": {
            "candidate_ids": [row["candidate_id"] for row in state.candidate_records],
            "candidate_pool_sha256": candidate_pool_hash,
            "status": "ok",
        }
    })
    compare_candidates_batch(state, audited_call)
    if any(row.get("stage") == "pairwise_deduplication_batch" for row in state.errors):
        state.preparation_provenance["status"] = "pairwise_deduplication_failed"
        for arm in ("QH-sel", "QH-rand"):
            state.selections[arm] = {"status": "blocked_pairwise_deduplication_failed"}
        return state

    cluster_candidates_complete_link(state)
    if any(row.get("stage") == "clustering" for row in state.errors):
        state.preparation_provenance["status"] = "clustering_failed"
        for arm in ("QH-sel", "QH-rand"):
            state.selections[arm] = {"status": "blocked_clustering_failed"}
        return state
    representative_hash = state.preparation_provenance["clustering"]["representative_pool_sha256"]
    shared_pool_provenance = {
        "candidate_pool_sha256": candidate_pool_hash,
        "representative_pool_sha256": representative_hash,
        "candidate_ids": [row["candidate_id"] for row in state.candidate_records],
        "representative_ids": list(state.representatives),
    }
    if len(state.representatives) < 3:
        _record_error(state, "qh_selection", "fewer than three complete-link representatives remain")
        for arm in ("QH-sel", "QH-rand"):
            state.selections[arm] = {
                "status": "blocked_insufficient_representatives",
                "available": len(state.representatives),
                "required": 3,
                **shared_pool_provenance,
            }
        state.preparation_provenance["status"] = "blocked_insufficient_representatives"
        return state

    # QH-rand is selected from IDs and input_set_id alone; QH-sel scores do not
    # exist yet and cannot be observed by this selection function.
    random_selection = select_qh_rand_sha256(state.representatives, input_set_id)
    state.selections["QH-rand"] = {**random_selection, **shared_pool_provenance}

    representative_records = {
        row["candidate_id"]: row for row in state.candidate_records
    }
    ordered_representatives = [representative_records[cid] for cid in state.representatives]
    ranking_template = _read_prompt(ranking_prompt_path)
    ranking_prompt = _render(
        ranking_template,
        DOMAIN_AND_TASK=domain_and_task,
        EVIDENCE=evidence,
        REPRESENTATIVES=json.dumps([
            {"question_id": row["candidate_id"], "text": row["text"]}
            for row in ordered_representatives
        ], ensure_ascii=False, indent=2),
    )
    weights = dict(QH_SEL_WEIGHTS)

    def ranker(_rows, _weights):
        raw = audited_call("qh_sel_ranking", ranking_prompt)
        state.raw_responses.append({"stage": "qh_sel_ranking", "raw": raw})
        score_rows = _parse_qh_sel_scores(raw, state.representatives)
        generation_order = {cid: index for index, cid in enumerate(state.representatives)}
        scored = []
        for item in score_rows:
            weighted = sum(item[name] * weights[name] for name in weights)
            scored.append({**item, "weighted_score": weighted})
        ranked = sorted(
            scored,
            key=lambda row: (-row["weighted_score"], generation_order[row["question_id"]]),
        )
        return {
            "ordered_candidate_ids": [row["question_id"] for row in ranked],
            "scores": {row["question_id"]: row for row in ranked},
            "weights": weights,
            "tie_break_policy": "weighted_score_desc_then_generation_order",
            "prompt_path": ranking_prompt_path,
            "prompt_sha256": _sha256_text(ranking_prompt),
            "raw_response_sha256": _sha256_text(raw),
        }

    select_qh_sel(state, settings, ranker)
    if state.selections.get("QH-sel", {}).get("status") == "ok":
        state.selections["QH-sel"].update(shared_pool_provenance)
        state.selections["QH-sel"].update({
            "ranking_weights": weights,
            "tie_break_policy": "weighted_score_desc_then_generation_order",
        })
        state.preparation_provenance["qh_sel_ranking"] = {
            "weights": weights,
            "tie_break_policy": "weighted_score_desc_then_generation_order",
            "ranking_result": state.ranking_result,
            "status": "ok",
        }
    else:
        state.selections["QH-sel"] = {
            "status": "failed_ranking",
            **shared_pool_provenance,
            "errors": [row["error"] for row in state.errors if row.get("stage") == "qh_sel_ranking"],
        }
        state.preparation_provenance["qh_sel_ranking"] = {
            "status": "failed",
            "errors": state.selections["QH-sel"]["errors"],
        }

    state.preparation_provenance["qh_rand_selection"] = {
        "seed": QH_RAND_SEED,
        "key_expression": expected_derivation,
        "selected_ids": list(state.selections["QH-rand"]["selected_candidate_ids"]),
        "selection_keys": state.selections["QH-rand"]["selection_keys"],
        "status": "ok",
    }
    state.preparation_provenance["status"] = (
        "ok" if state.selections.get("QH-sel", {}).get("status") == "ok"
        else "partial_failure"
    )
    return state


def cluster_and_choose_representatives(
    state: PipelineState,
    settings: PipelineSettings,
    clusterer: Clusterer | None,
    representative_selector: RepresentativeSelector | None,
) -> PipelineState:
    """Policy interface: no clustering or representative rule is chosen here."""
    if not settings.clustering_policy:
        _record_error(state, "clustering", "clustering_policy is unresolved")
        return state
    if not settings.representative_selection_policy:
        _record_error(state, "representative_selection", "representative_selection_policy is unresolved")
        return state
    if clusterer is None or representative_selector is None:
        _record_error(state, "clustering", "policy implementations must be injected")
        return state
    if any(row["status"] != "ok" for row in state.pairwise_records):
        _record_error(state, "clustering", "pairwise comparisons contain failures")
        return state

    candidate_ids = [row["candidate_id"] for row in state.candidate_records]
    expected_pairs = {
        frozenset((left, right))
        for left, right in itertools.combinations(candidate_ids, 2)
    }
    observed_pairs = [
        frozenset((row.get("question_a"), row.get("question_b")))
        for row in state.pairwise_records
    ]
    if len(observed_pairs) != len(expected_pairs) or set(observed_pairs) != expected_pairs:
        _record_error(state, "clustering", "pairwise records must contain every unique candidate pair exactly once")
        return state

    try:
        clusters = [list(group) for group in clusterer(candidate_ids, state.pairwise_records)]
        flattened = [item for group in clusters for item in group]
        if not clusters or any(not group for group in clusters):
            raise PipelineError("clusterer must return nonempty groups")
        if len(flattened) != len(set(flattened)) or set(flattened) != set(candidate_ids):
            raise PipelineError("clusters must partition all candidate IDs exactly once")
        records = {row["candidate_id"]: row for row in state.candidate_records}
        selected = []
        for cluster_number, group in enumerate(clusters, start=1):
            representative = representative_selector(group, [records[cid] for cid in group])
            if representative not in group:
                raise PipelineError("representative must be a member of its cluster")
            state.clusters.append({
                "cluster_id": f"C{cluster_number}",
                "member_candidate_ids": list(group),
                "representative_candidate_id": representative,
                "policy": settings.clustering_policy,
                "representative_policy": settings.representative_selection_policy,
            })
            selected.append(representative)
        state.representatives = selected
    except Exception as exc:
        _record_error(state, "clustering_or_representative_selection", str(exc))
    return state


def select_qh_sel(
    state: PipelineState,
    settings: PipelineSettings,
    ranker: Ranker | None,
) -> PipelineState:
    """Delegate ranking and tie handling; the prompt set contains no ranking rubric."""
    if not settings.qh_sel_ranking_weights:
        _record_error(state, "qh_sel_ranking", "qh_sel_ranking_weights are unresolved")
        return state
    if not settings.qh_sel_tie_break_policy:
        _record_error(state, "qh_sel_ranking", "qh_sel_tie_break_policy is unresolved")
        return state
    if ranker is None:
        _record_error(state, "qh_sel_ranking", "ranking implementation must be injected")
        return state
    settings.validate_selection_count()
    if len(state.representatives) < settings.selection_count:
        state.selections["QH-sel"] = {
            "status": "blocked_insufficient_unique_questions",
            "available": len(state.representatives), "required": settings.selection_count,
        }
        _record_error(state, "qh_sel_ranking", "fewer than three representatives; policy unresolved")
        return state
    records = {row["candidate_id"]: row for row in state.candidate_records}
    try:
        result = dict(ranker([records[cid] for cid in state.representatives], settings.qh_sel_ranking_weights))
        state.ranking_result = result
        if isinstance(result.get("raw_response"), str):
            state.raw_responses.append({"stage": "qh_sel_ranking", "raw": result["raw_response"]})
        ordered = result.get("ordered_candidate_ids")
        if not isinstance(ordered, list) or len(ordered) != len(state.representatives):
            raise PipelineError("ranker must return a complete ordered_candidate_ids list")
        if len(set(ordered)) != len(ordered) or set(ordered) != set(state.representatives):
            raise PipelineError("ranker output must order every representative exactly once")
        state.selections["QH-sel"] = {
            "status": "ok", "selected_candidate_ids": ordered[:settings.selection_count],
            "ranking_result": result,
        }
    except Exception as exc:
        _record_error(state, "qh_sel_ranking", str(exc))
    return state


def select_qh_rand(
    state: PipelineState,
    settings: PipelineSettings,
    sampler: Sampler | None,
    sampler_name: str | None,
) -> PipelineState:
    """Delegate RNG and seed derivation; no random algorithm is selected here."""
    settings.validate_selection_count()
    if settings.random_seed is None or type(settings.random_seed) not in (int, str):
        _record_error(state, "qh_rand_selection", "random_seed is unresolved")
        return state
    if sampler is None or not sampler_name:
        _record_error(state, "qh_rand_selection", "random sampler and version must be injected")
        return state
    if len(state.representatives) < settings.selection_count:
        state.selections["QH-rand"] = {
            "status": "blocked_insufficient_unique_questions",
            "available": len(state.representatives), "required": settings.selection_count,
        }
        _record_error(state, "qh_rand_selection", "fewer than three representatives; policy unresolved")
        return state
    try:
        selected = list(sampler(state.representatives, settings.selection_count, settings.random_seed))
        if len(selected) != settings.selection_count or len(set(selected)) != len(selected):
            raise PipelineError("sampler must return the requested number of distinct candidates")
        if not set(selected).issubset(set(state.representatives)):
            raise PipelineError("sampler returned an unknown candidate ID")
    except Exception as exc:
        _record_error(state, "qh_rand_selection", str(exc))
        return state
    state.selections["QH-rand"] = {
        "status": "ok", "selected_candidate_ids": selected,
        "seed": settings.random_seed, "sampler": sampler_name,
    }
    return state


def selected_questions_for_arm(state: PipelineState, arm: str) -> list[dict[str, str]]:
    """Resolve selected candidate IDs back to retained question records."""
    if arm not in ("QH-sel", "QH-rand"):
        raise PipelineError("selected-question generation supports QH-sel and QH-rand")
    selection = state.selections.get(arm)
    if not isinstance(selection, dict) or selection.get("status") != "ok":
        raise PipelineError(f"{arm} has no successful question selection")
    selected_ids = selection.get("selected_candidate_ids")
    if not isinstance(selected_ids, list) or len(selected_ids) != 3 or len(set(selected_ids)) != 3:
        raise PipelineError(f"{arm} selection must contain exactly three distinct question IDs")
    records = {row.get("candidate_id"): row for row in state.candidate_records}
    questions = []
    for candidate_id in selected_ids:
        record = records.get(candidate_id)
        if not isinstance(record, dict) or record.get("validation_status") != "valid":
            raise PipelineError(f"selected question {candidate_id!r} is missing or invalid")
        questions.append({"question_id": candidate_id, "text": record["text"]})
    return questions


def _normalize_selected_questions(selected_questions: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    if not isinstance(selected_questions, Sequence) or isinstance(selected_questions, (str, bytes)):
        raise PipelineError("selected_questions must be a sequence of question objects")
    if len(selected_questions) != 3:
        raise PipelineError("exactly three selected questions are required")
    normalized = []
    seen = set()
    for index, item in enumerate(selected_questions, start=1):
        if not isinstance(item, Mapping):
            raise PipelineError(f"selected question {index} must be an object")
        question_id = item.get("question_id", item.get("candidate_id", item.get("id")))
        text = item.get("text")
        if not isinstance(question_id, str) or not question_id.strip():
            raise PipelineError(f"selected question {index} needs a nonempty stable ID")
        if question_id in seen:
            raise PipelineError(f"selected question ID {question_id!r} is duplicated")
        if not isinstance(text, str) or not text.strip():
            raise PipelineError(f"selected question {question_id!r} needs nonempty text")
        seen.add(question_id)
        normalized.append({"question_id": question_id, "text": text})
    return normalized


def _prompt_for_selected_hypotheses(
    arm: str,
    domain_and_task: str,
    evidence: str,
    selected_questions: Sequence[Mapping[str, str]],
    prompt_path: str | None,
) -> str:
    defaults = {
        "QH-sel": "prompts/e6/03_generator_QH_sel.txt",
        "QH-rand": "prompts/e6/04_generator_QH_rand.txt",
    }
    if arm not in defaults:
        raise PipelineError("selected-question generation supports QH-sel and QH-rand")
    template = _read_prompt(prompt_path or defaults[arm])
    # The QH-rand file includes authoring notes around the actual template.
    # Keep the existing prompt body intact while excluding those notes at runtime.
    if arm == "QH-rand" and prompt_path is None:
        start = template.find("ROLE\n")
        stop = template.find("\nSave with Cmd + S.")
        if start < 0 or stop < 0 or stop <= start:
            raise PipelineError("could not isolate the QH-rand prompt body")
        template = template[start:stop]
    selected_text = "\n".join(
        f"Q{index}: {item['text']}"
        for index, item in enumerate(selected_questions, start=1)
    )
    questions_block = json.dumps(
        {"questions": [
            {"id": item["question_id"], "text": item["text"]}
            for item in selected_questions
        ]},
        ensure_ascii=False,
        indent=2,
    )
    return _render(
        template,
        DOMAIN_AND_TASK=domain_and_task,
        EVIDENCE=evidence,
        SELECTED_QUESTIONS=selected_text,
        QUESTIONS_BLOCK=questions_block,
    )


def _normalize_hypothesis_response(
    parsed: Any,
    arm: str,
    selected_questions: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    if not isinstance(parsed, dict):
        raise PipelineError("response must be a JSON object")
    selected_by_id = {item["question_id"]: item for item in selected_questions}
    expected_hypothesis_ids = [f"H{i}" for i in range(1, 7)]
    normalized = []

    if isinstance(parsed.get("questions"), list):
        questions = parsed["questions"]
        if len(questions) != 3:
            raise PipelineError("response must include exactly three selected questions")
        seen_question_ids = set()
        observed_hypothesis_ids = []
        for question_index, (question_obj, selected) in enumerate(zip(questions, selected_questions), start=1):
            if not isinstance(question_obj, dict):
                raise PipelineError(f"question Q{question_index} must be an object")
            response_question_id = question_obj.get("id")
            if response_question_id != f"Q{question_index}" or response_question_id in seen_question_ids:
                raise PipelineError(f"invalid or duplicate question reference {response_question_id!r}")
            seen_question_ids.add(response_question_id)
            response_text = question_obj.get("text")
            if not isinstance(response_text, str) or " ".join(response_text.split()) != " ".join(selected["text"].split()):
                raise PipelineError(f"response question Q{question_index} does not match supplied selected question")
            hypotheses = question_obj.get("hypotheses")
            if not isinstance(hypotheses, list) or len(hypotheses) != 2:
                raise PipelineError(f"question Q{question_index} must have exactly two hypotheses")
            for hypothesis in hypotheses:
                if not isinstance(hypothesis, dict):
                    raise PipelineError(f"question Q{question_index} has a malformed hypothesis")
                hypothesis_id = hypothesis.get("id")
                text = hypothesis.get("text")
                if not isinstance(hypothesis_id, str) or not isinstance(text, str) or not text.strip():
                    raise PipelineError("hypotheses require nonempty IDs and text")
                observed_hypothesis_ids.append(hypothesis_id)
                if len(text.split()) > 50:
                    raise PipelineError(f"{hypothesis_id} exceeds the 50-word prompt contract")
                normalized.append({
                    "hypothesis_id": f"{arm}:{hypothesis_id}",
                    "source_hypothesis_id": hypothesis_id,
                    "question_id": selected["question_id"],
                    "question_text": selected["text"],
                    "text": text,
                })
        if observed_hypothesis_ids != expected_hypothesis_ids:
            raise PipelineError("hypothesis IDs must be unique and consecutive H1 through H6")
        return normalized

    hypotheses = parsed.get("hypotheses")
    if not isinstance(hypotheses, list) or len(hypotheses) != 6:
        raise PipelineError("response must contain exactly six hypotheses")
    observed_hypothesis_ids = []
    for item in hypotheses:
        if not isinstance(item, dict):
            raise PipelineError("each hypothesis must be an object")
        hypothesis_id = item.get("id")
        question_id = item.get("question_id")
        text = item.get("text")
        if not isinstance(hypothesis_id, str) or not isinstance(text, str) or not text.strip():
            raise PipelineError("hypotheses require nonempty IDs and text")
        if question_id not in selected_by_id:
            raise PipelineError(f"invalid question reference {question_id!r}")
        observed_hypothesis_ids.append(hypothesis_id)
        if len(text.split()) > 50:
            raise PipelineError(f"{hypothesis_id} exceeds the 50-word prompt contract")
        normalized.append({
            "hypothesis_id": f"{arm}:{hypothesis_id}",
            "source_hypothesis_id": hypothesis_id,
            "question_id": question_id,
            "question_text": selected_by_id[question_id]["text"],
            "text": text,
        })
    if observed_hypothesis_ids != expected_hypothesis_ids:
        raise PipelineError("hypothesis IDs must be unique and consecutive H1 through H6")
    counts = {qid: 0 for qid in selected_by_id}
    for item in normalized:
        counts[item["question_id"]] += 1
    if any(count != 2 for count in counts.values()):
        raise PipelineError("exactly two hypotheses must reference each selected question")
    return normalized


def generate_question_hypotheses(
    state: PipelineState,
    arm: str,
    selected_questions: Sequence[Mapping[str, Any]],
    model_call: ModelCall,
    domain_and_task: str,
    evidence: str,
    settings: PipelineSettings,
    retry_prompt_builder: RetryPromptBuilder | None = None,
    prompt_path: str | None = None,
) -> PipelineState:
    """Generate six linked hypotheses for preselected QH-sel or QH-rand inputs.

    Retry count and retry behavior must be explicitly supplied through settings
    and an injected retry prompt builder. The function never ranks or samples.
    """
    if arm not in ("QH-sel", "QH-rand"):
        _record_error(state, "selected_question_hypothesis_generation", "arm must be QH-sel or QH-rand")
        return state
    try:
        selected = _normalize_selected_questions(selected_questions)
        max_attempts = settings.selected_hypothesis_max_attempts
        if type(max_attempts) is not int or max_attempts < 1:
            raise PipelineError("selected_hypothesis_max_attempts is unresolved")
        if max_attempts > 1 and (retry_prompt_builder is None or not settings.selected_hypothesis_retry_policy):
            raise PipelineError("retry policy implementation and name are required for multiple attempts")
        prompt = _prompt_for_selected_hypotheses(
            arm, domain_and_task, evidence, selected, prompt_path,
        )
    except Exception as exc:
        _record_error(state, "selected_question_hypothesis_generation", str(exc), arm=arm)
        state.hypothesis_generations.append({
            "arm": arm, "status": "blocked", "selected_questions": list(selected_questions)
            if isinstance(selected_questions, Sequence) and not isinstance(selected_questions, (str, bytes)) else [],
            "attempt_history": [], "errors": [str(exc)],
        })
        return state
    generated = _run_validated_generation(
        state=state,
        stage=f"{arm}_hypothesis_generation",
        prompt=prompt,
        model_call=model_call,
        max_attempts=max_attempts,
        retry_policy=settings.selected_hypothesis_retry_policy,
        retry_prompt_builder=retry_prompt_builder,
        validator=lambda parsed: _normalize_hypothesis_response(parsed, arm, selected),
    )
    generation = {
        "arm": arm,
        "status": generated["status"],
        "selected_questions": selected,
        "hypotheses": generated["normalized_output"] or [],
        "parsed_output": generated["parsed_output"],
        "raw_response": generated["raw_response"],
        "attempt_history": generated["attempt_history"],
        "retry_policy": generated["retry_policy"],
        "errors": generated["errors"],
    }
    state.hypothesis_generations.append(generation)
    if generated["status"] != "ok":
        _record_error(
            state, "selected_question_hypothesis_generation",
            "all configured attempts failed validation or model call",
            arm=arm, attempts=len(generated["attempt_history"]),
        )
    return state


def _clean_hypothesis_text(value: Any, hypothesis_id: Any) -> str:
    if not isinstance(hypothesis_id, str) or not isinstance(value, str) or not value.strip():
        raise PipelineError("hypotheses require nonempty IDs and text")
    if len(value.split()) > 50:
        raise PipelineError(f"{hypothesis_id} exceeds the 50-word prompt contract")
    return value


def _stable_hypothesis(arm: str, hypothesis_id: str, text: str,
                       question_id: str | None = None,
                       question_text: str | None = None) -> dict[str, Any]:
    return {
        "hypothesis_id": f"{arm}:{hypothesis_id}",
        "source_hypothesis_id": hypothesis_id,
        "question_id": question_id,
        "question_text": question_text,
        "text": text,
    }


def _normalize_direct_output(parsed: Any) -> dict[str, Any]:
    if not isinstance(parsed, dict) or not isinstance(parsed.get("hypotheses"), list):
        raise PipelineError("D response must contain a hypotheses array")
    items = parsed["hypotheses"]
    if len(items) != 6:
        raise PipelineError("D response must contain exactly six hypotheses")
    expected = [f"H{i}" for i in range(1, 7)]
    observed = []
    hypotheses = []
    for item in items:
        if not isinstance(item, dict):
            raise PipelineError("each D hypothesis must be an object")
        hypothesis_id = item.get("id")
        text = _clean_hypothesis_text(item.get("text"), hypothesis_id)
        observed.append(hypothesis_id)
        hypotheses.append(_stable_hypothesis("D", hypothesis_id, text))
    if observed != expected:
        raise PipelineError("D hypothesis IDs must be unique and consecutive H1 through H6")
    return {"arm": "D", "questions": [], "hypotheses": hypotheses}


def _normalize_qh_output(parsed: Any) -> dict[str, Any]:
    if not isinstance(parsed, dict) or not isinstance(parsed.get("questions"), list):
        raise PipelineError("QH response must contain a questions array")
    if parsed.get("arm", "QH") != "QH":
        raise PipelineError("QH response arm identifier must be QH")
    questions_in = parsed["questions"]
    if len(questions_in) != 3:
        raise PipelineError("QH response must contain exactly three questions")
    hypotheses = []
    questions = []
    observed_hypotheses = []
    for question_index, question in enumerate(questions_in, start=1):
        expected_question_id = f"Q{question_index}"
        if not isinstance(question, dict) or question.get("id") != expected_question_id:
            raise PipelineError(f"QH question IDs must be unique and consecutive Q1 through Q3; expected {expected_question_id}")
        question_text = question.get("text")
        if not isinstance(question_text, str) or not question_text.strip():
            raise PipelineError(f"{expected_question_id} must have nonempty text")
        stable_question_id = f"QH:{expected_question_id}"
        questions.append({"question_id": stable_question_id, "source_question_id": expected_question_id,
                          "text": question_text})
        items = question.get("hypotheses")
        if not isinstance(items, list) or len(items) != 2:
            raise PipelineError(f"{expected_question_id} must contain exactly two hypotheses")
        for item in items:
            if not isinstance(item, dict):
                raise PipelineError(f"{expected_question_id} contains a malformed hypothesis")
            hypothesis_id = item.get("id")
            text = _clean_hypothesis_text(item.get("text"), hypothesis_id)
            observed_hypotheses.append(hypothesis_id)
            hypotheses.append(_stable_hypothesis(
                "QH", hypothesis_id, text, stable_question_id, question_text,
            ))
    if observed_hypotheses != [f"H{i}" for i in range(1, 7)]:
        raise PipelineError("QH hypothesis IDs must be unique and consecutive H1 through H6")
    return {"arm": "QH", "questions": questions, "hypotheses": hypotheses}


def _normalize_hq_output(parsed: Any) -> dict[str, Any]:
    if not isinstance(parsed, dict):
        raise PipelineError("HQ response must be a JSON object")
    hypotheses_in = parsed.get("hypotheses")
    questions_in = parsed.get("questions")
    if not isinstance(hypotheses_in, list) or len(hypotheses_in) != 6:
        raise PipelineError("HQ response must contain exactly six hypotheses")
    if not isinstance(questions_in, list) or len(questions_in) != 6:
        raise PipelineError("HQ response must contain exactly six linked questions")
    expected_hypothesis_ids = [f"H{i}" for i in range(1, 7)]
    hypotheses_by_id = {}
    for item in hypotheses_in:
        if not isinstance(item, dict):
            raise PipelineError("each HQ hypothesis must be an object")
        hypothesis_id = item.get("id")
        text = _clean_hypothesis_text(item.get("text"), hypothesis_id)
        if hypothesis_id in hypotheses_by_id:
            raise PipelineError(f"duplicate HQ hypothesis ID {hypothesis_id!r}")
        hypotheses_by_id[hypothesis_id] = text
    if list(hypotheses_by_id) != expected_hypothesis_ids:
        raise PipelineError("HQ hypothesis IDs must be unique and consecutive H1 through H6")

    questions_by_hypothesis = {}
    for item in questions_in:
        if not isinstance(item, dict):
            raise PipelineError("each HQ question must be an object")
        hypothesis_id = item.get("hypothesis_id")
        text = item.get("text")
        if hypothesis_id not in hypotheses_by_id:
            raise PipelineError(f"HQ question has invalid hypothesis reference {hypothesis_id!r}")
        if hypothesis_id in questions_by_hypothesis:
            raise PipelineError(f"duplicate HQ question reference {hypothesis_id!r}")
        if not isinstance(text, str) or not text.strip():
            raise PipelineError(f"HQ question linked to {hypothesis_id} needs nonempty text")
        questions_by_hypothesis[hypothesis_id] = text
    if set(questions_by_hypothesis) != set(expected_hypothesis_ids):
        raise PipelineError("HQ must have exactly one question for every hypothesis H1 through H6")

    hypotheses = []
    questions = []
    for index, hypothesis_id in enumerate(expected_hypothesis_ids, start=1):
        question_id = f"HQ:Q{index}"
        question_text = questions_by_hypothesis[hypothesis_id]
        hypotheses.append(_stable_hypothesis(
            "HQ", hypothesis_id, hypotheses_by_id[hypothesis_id], question_id, question_text,
        ))
        questions.append({
            "question_id": question_id,
            "source_hypothesis_id": hypothesis_id,
            "text": question_text,
        })
    return {"arm": "HQ", "questions": questions, "hypotheses": hypotheses}


def generate_direct_arm(
    state: PipelineState,
    arm: str,
    model_call: ModelCall,
    domain_and_task: str,
    evidence: str,
    settings: PipelineSettings,
    retry_prompt_builder: RetryPromptBuilder | None = None,
    prompt_path: str | None = None,
) -> PipelineState:
    """Implement prompt-driven D, QH, or HQ generation with shared retry logging."""
    prompt_paths = {
        "D": "prompts/e6/01_generator_D.txt",
        "QH": "prompts/e6/02_generator_QH.txt",
        "HQ": "prompts/e6/05_generator_HQ.txt",
    }
    validators = {"D": _normalize_direct_output, "QH": _normalize_qh_output, "HQ": _normalize_hq_output}
    stage = f"{arm}_generation"
    try:
        if arm not in prompt_paths:
            raise PipelineError("arm must be D, QH, or HQ")
        max_attempts = settings.arm_hypothesis_max_attempts
        if type(max_attempts) is not int or max_attempts < 1:
            raise PipelineError("arm_hypothesis_max_attempts is unresolved")
        if max_attempts > 1 and (retry_prompt_builder is None or not settings.arm_hypothesis_retry_policy):
            raise PipelineError("retry policy implementation and name are required for multiple attempts")
        prompt = _render(
            _read_prompt(prompt_path or prompt_paths[arm]),
            DOMAIN_AND_TASK=domain_and_task,
            EVIDENCE=evidence,
        )
    except Exception as exc:
        _record_error(state, stage, str(exc), arm=arm)
        state.hypothesis_generations.append({
            "arm": arm, "status": "blocked", "questions": [], "hypotheses": [],
            "attempt_history": [], "errors": [str(exc)],
        })
        return state

    generated = _run_validated_generation(
        state=state,
        stage=stage,
        prompt=prompt,
        model_call=model_call,
        max_attempts=max_attempts,
        retry_policy=settings.arm_hypothesis_retry_policy,
        retry_prompt_builder=retry_prompt_builder,
        validator=validators[arm],
    )
    normalized = generated["normalized_output"] or {"questions": [], "hypotheses": []}
    state.hypothesis_generations.append({
        "arm": arm,
        "status": generated["status"],
        "questions": normalized["questions"],
        "hypotheses": normalized["hypotheses"],
        "parsed_output": generated["parsed_output"],
        "raw_response": generated["raw_response"],
        "attempt_history": generated["attempt_history"],
        "retry_policy": generated["retry_policy"],
        "errors": generated["errors"],
    })
    if generated["status"] != "ok":
        _record_error(state, stage, "all configured attempts failed validation or model call",
                      arm=arm, attempts=len(generated["attempt_history"]))
    return state


def _normalize_control_output(parsed: Any, arm: str) -> dict[str, Any]:
    if not isinstance(parsed, dict):
        raise PipelineError("control response must be a JSON object")
    if parsed.get("arm") != arm:
        raise PipelineError(f"control response arm must be {arm}")
    if "questions" in parsed and parsed["questions"] not in (None, []):
        raise PipelineError("control response must not contain research questions")
    items = parsed.get("hypotheses")
    if not isinstance(items, list) or len(items) != 6:
        raise PipelineError("control response must contain exactly six hypotheses")
    hypotheses = []
    observed = []
    for item in items:
        if not isinstance(item, dict):
            raise PipelineError("each control hypothesis must be an object")
        hypothesis_id = item.get("id")
        text = _clean_hypothesis_text(item.get("text"), hypothesis_id)
        observed.append(hypothesis_id)
        hypotheses.append(_stable_hypothesis(arm, hypothesis_id, text))
    if observed != [f"H{i}" for i in range(1, 7)]:
        raise PipelineError("control hypothesis IDs must be unique and consecutive H1 through H6")
    return {"arm": arm, "questions": [], "hypotheses": hypotheses}


def _control_prompt(
    arm: str,
    domain_and_task: str,
    evidence: str,
    prompt_path: str | None = None,
) -> str:
    instructions = {
        "D-empty": (
            "No substantive research evidence is provided. Generate hypotheses using only the research domain and task. "
            "Do not pretend that supporting evidence was supplied."
        ),
        "D-shuffled": (
            "The supplied evidence belongs to a different research input. Generate hypotheses for the current research task "
            "using the supplied evidence as presented. Do not assume that the evidence belongs to the current task."
        ),
    }
    if arm not in instructions:
        raise PipelineError("control arm must be D-empty or D-shuffled")
    template = _read_prompt(prompt_path or "prompts/e6/06_generator_controls.txt")
    if prompt_path is None:
        start = template.find("ROLE\n")
        stop = template.find("\nStep 3 — Important control instructions")
        if start < 0 or stop < 0 or stop <= start:
            raise PipelineError("could not isolate the controls prompt body")
        template = template[start:stop]
    return _render(
        template,
        ARM_NAME=arm,
        DOMAIN_AND_TASK=domain_and_task,
        EVIDENCE=evidence,
        CONTROL_CONDITION_INSTRUCTIONS=instructions[arm],
    )


def _blocked_control_generation(
    state: PipelineState,
    arm: str,
    message: str,
    control_provenance: Mapping[str, Any],
) -> PipelineState:
    _record_error(state, f"{arm}_generation", message, arm=arm)
    state.hypothesis_generations.append({
        "arm": arm,
        "status": "blocked",
        "questions": [],
        "hypotheses": [],
        "control_provenance": dict(control_provenance),
        "parsed_output": None,
        "raw_response": None,
        "attempt_history": [],
        "retry_policy": None,
        "errors": [message],
    })
    return state


def _run_control_generation(
    state: PipelineState,
    arm: str,
    domain_and_task: str,
    evidence: str,
    control_provenance: Mapping[str, Any],
    model_call: ModelCall,
    settings: PipelineSettings,
    retry_prompt_builder: RetryPromptBuilder | None,
    prompt_path: str | None,
    rendered_prompt: str | None = None,
) -> PipelineState:
    try:
        if type(settings.arm_hypothesis_max_attempts) is not int or settings.arm_hypothesis_max_attempts < 1:
            raise PipelineError("arm_hypothesis_max_attempts is unresolved")
        if settings.arm_hypothesis_max_attempts > 1 and (
            retry_prompt_builder is None or not settings.arm_hypothesis_retry_policy
        ):
            raise PipelineError("retry policy implementation and name are required for multiple attempts")
        prompt = rendered_prompt if rendered_prompt is not None else _control_prompt(
            arm, domain_and_task, evidence, prompt_path,
        )
    except Exception as exc:
        return _blocked_control_generation(state, arm, str(exc), control_provenance)

    generated = _run_validated_generation(
        state=state,
        stage=f"{arm}_generation",
        prompt=prompt,
        model_call=model_call,
        max_attempts=settings.arm_hypothesis_max_attempts,
        retry_policy=settings.arm_hypothesis_retry_policy,
        retry_prompt_builder=retry_prompt_builder,
        validator=lambda parsed: _normalize_control_output(parsed, arm),
    )
    normalized = generated["normalized_output"] or {"questions": [], "hypotheses": []}
    state.hypothesis_generations.append({
        "arm": arm,
        "status": generated["status"],
        "questions": normalized["questions"],
        "hypotheses": normalized["hypotheses"],
        "control_provenance": dict(control_provenance),
        "parsed_output": generated["parsed_output"],
        "raw_response": generated["raw_response"],
        "attempt_history": generated["attempt_history"],
        "retry_policy": generated["retry_policy"],
        "errors": generated["errors"],
    })
    if generated["status"] != "ok":
        _record_error(state, f"{arm}_generation", "all configured attempts failed validation or model call",
                      arm=arm, attempts=len(generated["attempt_history"]))
    return state


def _control_prompt_evidence(prompt: str) -> str:
    """Extract the rendered control prompt evidence field without interpretation."""
    marker = "Evidence:\n"
    end_marker = "\n\nControl condition:"
    start = prompt.find(marker)
    end = prompt.find(end_marker, start + len(marker)) if start >= 0 else -1
    if start < 0 or end < 0:
        raise PipelineError("rendered control prompt has no auditable Evidence field")
    return prompt[start + len(marker):end]


def _canonical_source_record_hash(record: Mapping[str, Any]) -> str:
    encoded = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return _sha256_text(encoded)


def _d_shuffled_provenance_hashes(manifest_records, source_records):
    return (_sha256_json(list(manifest_records)),
            _sha256_json({key: source_records[key] for key in sorted(source_records)}))


def _canonical_evidence_hash(abstract: str, references: Sequence[str]) -> str:
    return _sha256_json({"abstract": abstract, "references": list(references)})


def _d_empty_audit_validation_errors(
    audit: Mapping[str, Any], recipient_id: str, retained_task_text: str,
    abstract_hash: str, reference_hash: str, *, development_profile_only: bool = False,
) -> list[str]:
    """Validate attestation structure and its binding to the supplied inputs."""
    errors = []
    expected_trust = "trusted_development_profile" if development_profile_only else "trusted_production"
    if audit.get("trust_status") != expected_trust:
        errors.append(
            "audit is not explicitly marked trusted production"
            if not development_profile_only else
            "audit is not explicitly marked trusted development profile"
        )
    for key in ("auditor_id", "audit_id"):
        if not isinstance(audit.get(key), str) or not audit[key].strip():
            errors.append(f"{key} must be a nonempty string")
    if audit.get("audit_complete") is not True:
        errors.append("audit_complete must be true")
    if audit.get("audit_scope") != "retained_task_domain_text":
        errors.append("audit_scope must cover the retained task/domain text")
    if audit.get("leakage_check_performed") is not True:
        errors.append("leakage_check_performed must be true")
    if audit.get("retained_task_leakage_detected") is not False:
        errors.append("retained task must be attested as free of retained paper-specific evidence")
    if audit.get("recipient_id") != recipient_id:
        errors.append("audit recipient ID does not match")
    if audit.get("scrubbed_task_sha256") != _sha256_text(retained_task_text):
        errors.append("scrubbed-task hash does not match")

    removed_fields = audit.get("removed_fields")
    expected_fields = ["abstract", "reference_evidence"]
    if type(removed_fields) is not list:
        errors.append("removed_fields must be an actual list")
    elif any(not isinstance(item, str) or not item.strip() for item in removed_fields):
        errors.append("every removed_fields entry must be a nonempty string")
    elif len(removed_fields) != len(set(removed_fields)):
        errors.append("removed_fields entries must be unique")
    elif set(removed_fields) != set(expected_fields) or len(removed_fields) != len(expected_fields):
        errors.append("removed_fields must contain exactly abstract and reference_evidence")

    expected_hashes = {
        "abstract": abstract_hash,
        "reference_evidence": reference_hash,
    }
    hashes = audit.get("removed_evidence_sha256")
    if not isinstance(hashes, Mapping) or dict(hashes) != expected_hashes:
        errors.append("removed evidence hashes do not match the original evidence")
    if audit.get("rendered_evidence") != "":
        errors.append("rendered evidence must be exactly empty")
    return errors


def assign_d_shuffled_donors(
    recipients: Sequence[Mapping[str, Any]],
    development_records: Sequence[Mapping[str, Any]],
    canonical_source_records: Mapping[str, Mapping[str, Any]],
    *, expected_manifest_sha256: str | None = None,
    expected_source_corpus_sha256: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic, no-reuse donor assignment batch from DEVELOPMENT only.

    Records must include manifest IDs/splits/abstract hashes/source-record hashes;
    canonical_source_records must map canonical IDs to the verified raw source rows.
    A deterministic backtracking search uses ascending SHA256 key order and avoids
    greedy dead ends that could leave a recipient with only itself as donor.
    """
    if not recipients or not development_records:
        raise PipelineError("recipient and development donor records are required")
    if not expected_manifest_sha256 or not expected_source_corpus_sha256:
        raise PipelineError("independently supplied manifest and source-corpus hashes are required")
    actual_manifest_hash, actual_source_hash = _d_shuffled_provenance_hashes(
        development_records, canonical_source_records)
    if actual_manifest_hash != expected_manifest_sha256:
        raise PipelineError("development manifest hash does not match independently supplied expected hash")
    if actual_source_hash != expected_source_corpus_sha256:
        raise PipelineError("source corpus hash does not match independently supplied expected hash")

    def validate_record(row: Mapping[str, Any], role: str) -> tuple[str, str, Mapping[str, Any]]:
        paper_id = row.get("paper_id")
        if not isinstance(paper_id, str):
            raise PipelineError(f"{role} paper_id is required")
        canonical_id = canonicalize_arxiv_id(paper_id)
        if canonical_id != paper_id:
            raise PipelineError(f"{role} ID must be canonical: {paper_id}")
        if row.get("split") != "DEVELOPMENT":
            raise PipelineError(f"{role} {paper_id} is not in the DEVELOPMENT split")
        eligibility = row.get("eligibility")
        if (not isinstance(eligibility, Mapping)
                or eligibility.get("nonempty_abstract") is not True
                or eligibility.get("metadata_conflict") is not False
                or eligibility.get("in_focal_exclusion_set") is not False):
            raise PipelineError(f"{role} {paper_id} lacks verified DEVELOPMENT eligibility fields")
        abstract = row.get("abstract")
        if not isinstance(abstract, str) or not abstract.strip():
            raise PipelineError(f"{role} {paper_id} has no nonempty abstract evidence")
        if row.get("abstract_sha256") != _sha256_text(abstract):
            raise PipelineError(f"{role} {paper_id} abstract hash does not match")
        source_record = canonical_source_records.get(canonical_id)
        if not isinstance(source_record, Mapping):
            raise PipelineError(f"canonical source record is missing for {role} {paper_id}")
        try:
            source_id = canonicalize_arxiv_id(source_record.get("paper_id"))
        except (TypeError, ValueError) as exc:
            raise PipelineError(f"canonical source record ID is invalid for {paper_id}") from exc
        if source_id != canonical_id:
            raise PipelineError(f"canonical source record ID mismatch for {paper_id}")
        if source_record.get("abstract") != abstract:
            raise PipelineError(f"{role} {paper_id} evidence differs from its canonical source record")
        source_hash = _canonical_source_record_hash(source_record)
        if row.get("source_record_sha256") != source_hash:
            raise PipelineError(f"{role} {paper_id} source-record hash does not match")
        return canonical_id, abstract, source_record

    recipient_by_id: dict[str, Mapping[str, Any]] = {}
    for recipient in recipients:
        recipient_id, _, _ = validate_record(recipient, "recipient")
        if recipient_id in recipient_by_id:
            raise PipelineError(f"duplicate recipient ID: {recipient_id}")
        recipient_by_id[recipient_id] = recipient
    donor_by_id: dict[str, tuple[Mapping[str, Any], str, Mapping[str, Any]]] = {}
    for donor in development_records:
        donor_id, abstract, source_record = validate_record(donor, "donor")
        if donor_id in donor_by_id:
            raise PipelineError(f"duplicate donor ID: {donor_id}")
        donor_by_id[donor_id] = (donor, abstract, source_record)

    recipient_ids = sorted(recipient_by_id)
    if not set(recipient_ids).issubset(donor_by_id):
        raise PipelineError("each recipient must be present in the DEVELOPMENT donor pool")
    batch_id = _sha256_text("\n".join(recipient_ids))
    keyed_candidates: dict[str, list[dict[str, str]]] = {}
    for recipient_id in recipient_ids:
        choices = []
        for donor_id in donor_by_id:
            if donor_id == recipient_id:
                continue
            key = f"E6-D-SHUFFLED-v1|{D_SHUFFLED_SEED}|{recipient_id}|{donor_id}"
            choices.append({"donor_id": donor_id, "key": key, "key_sha256": _sha256_text(key)})
        keyed_candidates[recipient_id] = sorted(choices, key=lambda row: (row["key_sha256"], row["donor_id"]))

    assignment_by_recipient: dict[str, dict[str, str]] = {}

    def find_assignment(index: int, used_donors: set[str]) -> bool:
        if index == len(recipient_ids):
            return True
        recipient_id = recipient_ids[index]
        for choice in keyed_candidates[recipient_id]:
            donor_id = choice["donor_id"]
            if donor_id in used_donors:
                continue
            assignment_by_recipient[recipient_id] = choice
            used_donors.add(donor_id)
            if find_assignment(index + 1, used_donors):
                return True
            used_donors.remove(donor_id)
            assignment_by_recipient.pop(recipient_id, None)
        return False

    if not find_assignment(0, set()):
        raise PipelineError("no no-self, no-reuse donor assignment exists for this batch")

    assignments = []
    for recipient_id in recipient_ids:
        choice = assignment_by_recipient[recipient_id]
        donor_row, donor_abstract, donor_source = donor_by_id[choice["donor_id"]]
        assignments.append({
            "recipient_id": recipient_id,
            "recipient_split": "DEVELOPMENT",
            "donor_id": choice["donor_id"],
            "donor_split": "DEVELOPMENT",
            "seed": D_SHUFFLED_SEED,
            "assignment_algorithm": D_SHUFFLED_ALGORITHM,
            "assignment_key": choice["key"],
            "assignment_key_sha256": choice["key_sha256"],
            "donor_evidence": donor_abstract,
            "evidence_sha256": _sha256_text(donor_abstract),
            "abstract_sha256": donor_row["abstract_sha256"],
            "source_record_sha256": donor_row["source_record_sha256"],
            "donor_source_version_ids": list(donor_row.get("source_version_ids", [])),
            "assignment_batch_id": batch_id,
            "source_verification": {
                "passed": True,
                "canonical_source_record_sha256": _canonical_source_record_hash(donor_source),
                "abstract_sha256": _sha256_text(donor_abstract),
            },
        })
    result = {
        "status": "ok",
        "split": "DEVELOPMENT",
        "seed": D_SHUFFLED_SEED,
        "assignment_algorithm": D_SHUFFLED_ALGORITHM,
        "key_expression": D_SHUFFLED_KEY_EXPRESSION,
        "assignment_batch_id": batch_id,
        "recipient_ids_canonical_order": recipient_ids,
        "donor_reuse_policy": "prohibited_within_assignment_batch",
        "manifest_sha256": actual_manifest_hash,
        "source_corpus_sha256": actual_source_hash,
        "assignments": assignments,
    }
    result["assignment_batch_sha256"] = _sha256_json([
        {key: row[key] for key in (
            "recipient_id", "recipient_split", "donor_id", "donor_split", "assignment_key_sha256",
            "evidence_sha256", "source_record_sha256",
        )}
        for row in assignments
    ])
    validate_d_shuffled_assignment_batch(
        result, recipients, development_records, canonical_source_records,
        expected_manifest_sha256=expected_manifest_sha256,
        expected_source_corpus_sha256=expected_source_corpus_sha256,
    )
    return result


def validate_d_shuffled_assignment_batch(
    batch: Mapping[str, Any],
    recipients: Sequence[Mapping[str, Any]],
    development_records: Sequence[Mapping[str, Any]],
    canonical_source_records: Mapping[str, Mapping[str, Any]],
    *, expected_manifest_sha256: str | None = None,
    expected_source_corpus_sha256: str | None = None,
) -> dict[str, Any]:
    """Independently validate batch completeness, split, provenance and no reuse."""
    if not isinstance(batch, Mapping) or batch.get("status") != "ok":
        raise PipelineError("D-shuffled assignment batch is missing or not successful")
    if not expected_manifest_sha256 or not expected_source_corpus_sha256:
        raise PipelineError("independently supplied manifest and source-corpus hashes are required")
    actual_manifest_hash, actual_source_hash = _d_shuffled_provenance_hashes(
        development_records, canonical_source_records)
    if actual_manifest_hash != expected_manifest_sha256 or batch.get("manifest_sha256") != expected_manifest_sha256:
        raise PipelineError("development manifest hash does not match independently supplied expected hash")
    if actual_source_hash != expected_source_corpus_sha256 or batch.get("source_corpus_sha256") != expected_source_corpus_sha256:
        raise PipelineError("source corpus hash does not match independently supplied expected hash")
    def canonical_id(value, role):
        if not isinstance(value, str):
            raise PipelineError(f"{role} paper ID is invalid")
        try:
            result = canonicalize_arxiv_id(value)
        except (TypeError, ValueError) as exc:
            raise PipelineError(f"{role} paper ID is invalid") from exc
        if result != value:
            raise PipelineError(f"{role} ID must be canonical: {value}")
        return result
    expected = sorted(canonical_id(row.get("paper_id"), "recipient") for row in recipients)
    if len(expected) != len(recipients) or len(set(expected)) != len(expected):
        raise PipelineError("recipient batch IDs must be complete and unique")
    if batch.get("split") != "DEVELOPMENT" or batch.get("seed") != D_SHUFFLED_SEED:
        raise PipelineError("D-shuffled batch split or master seed is invalid")
    if batch.get("assignment_algorithm") != D_SHUFFLED_ALGORITHM:
        raise PipelineError("D-shuffled batch assignment algorithm is invalid")
    if batch.get("key_expression") != D_SHUFFLED_KEY_EXPRESSION:
        raise PipelineError("D-shuffled batch key expression is invalid")
    if batch.get("recipient_ids_canonical_order") != expected:
        raise PipelineError("D-shuffled recipients are not recorded in canonical ID order")
    rows = batch.get("assignments")
    if not isinstance(rows, list) or len(rows) != len(expected):
        raise PipelineError("D-shuffled assignment batch does not cover every recipient exactly once")
    if [row.get("recipient_id") for row in rows if isinstance(row, Mapping)] != expected:
        raise PipelineError("D-shuffled assignment rows must follow canonical recipient order")
    recipient_ids = set(expected)
    donor_ids = [row.get("donor_id") for row in rows if isinstance(row, Mapping)]
    if len(donor_ids) != len(rows) or len(set(donor_ids)) != len(donor_ids):
        raise PipelineError("D-shuffled donor reuse is prohibited within a batch")
    donor_rows = {canonical_id(row.get("paper_id"), "donor"): row for row in development_records}
    recipient_by_id = {canonical_id(row.get("paper_id"), "recipient"): row for row in recipients}
    if any(paper_id not in donor_rows or dict(recipient_by_id[paper_id]) != dict(donor_rows[paper_id])
           for paper_id in expected):
        raise PipelineError("recipient records must bind to actual development-manifest records")
    batch_id = _sha256_text("\n".join(expected))
    if batch.get("assignment_batch_id") != batch_id:
        raise PipelineError("D-shuffled assignment batch ID does not match recipients")

    # Independently reproduce the deterministic no-self, no-reuse assignment.
    # This prevents a modified donor mapping from passing merely by recomputing
    # the public assignment and batch hashes.
    keyed_candidates: dict[str, list[dict[str, str]]] = {}
    for recipient_id in expected:
        choices = []
        for donor_id in donor_rows:
            if donor_id == recipient_id:
                continue
            key = (
                f"E6-D-SHUFFLED-v1|{D_SHUFFLED_SEED}|"
                f"{recipient_id}|{donor_id}"
            )
            choices.append({
                "donor_id": donor_id,
                "key": key,
                "key_sha256": _sha256_text(key),
            })
        keyed_candidates[recipient_id] = sorted(
            choices,
            key=lambda item: (item["key_sha256"], item["donor_id"]),
        )

    expected_assignment: dict[str, str] = {}

    def reproduce_assignment(index: int, used_donors: set[str]) -> bool:
        if index == len(expected):
            return True

        recipient_id = expected[index]
        for choice in keyed_candidates[recipient_id]:
            donor_id = choice["donor_id"]
            if donor_id in used_donors:
                continue

            expected_assignment[recipient_id] = donor_id
            used_donors.add(donor_id)

            if reproduce_assignment(index + 1, used_donors):
                return True

            used_donors.remove(donor_id)
            expected_assignment.pop(recipient_id, None)

        return False

    if not reproduce_assignment(0, set()):
        raise PipelineError(
            "no deterministic no-self, no-reuse donor assignment exists"
        )

    for row in rows:
        if not isinstance(row, Mapping):
            raise PipelineError("D-shuffled assignment row must be an object")
        required = {
            "recipient_id", "donor_id", "donor_split", "seed", "assignment_algorithm",
            "recipient_split",
            "assignment_key", "assignment_key_sha256", "donor_evidence", "evidence_sha256",
            "abstract_sha256", "source_record_sha256", "donor_source_version_ids",
            "assignment_batch_id", "source_verification",
        }
        if not required.issubset(row):
            raise PipelineError("D-shuffled assignment row is missing provenance fields")
        target_id, donor_id = row["recipient_id"], row["donor_id"]
        canonical_id(target_id, "assignment recipient")
        canonical_id(donor_id, "assignment donor")
        if target_id not in recipient_ids or donor_id not in donor_rows:
            raise PipelineError("D-shuffled assignment names an unknown recipient or donor")
        if target_id == donor_id:
            raise PipelineError("D-shuffled self-donation is prohibited")
        if expected_assignment.get(target_id) != donor_id:
            raise PipelineError(
                "D-shuffled donor mapping does not match the deterministic "
                "SHA256-ordered assignment"
            )
        if (row["recipient_split"] != "DEVELOPMENT" or recipient_by_id[target_id].get("split") != "DEVELOPMENT"
                or row["donor_split"] != "DEVELOPMENT" or donor_rows[donor_id].get("split") != "DEVELOPMENT"):
            raise PipelineError("D-shuffled donor must belong to the DEVELOPMENT split")
        key = f"E6-D-SHUFFLED-v1|{D_SHUFFLED_SEED}|{target_id}|{donor_id}"
        if (row["seed"] != D_SHUFFLED_SEED or row["assignment_algorithm"] != D_SHUFFLED_ALGORITHM
                or row["assignment_key"] != key or row["assignment_key_sha256"] != _sha256_text(key)):
            raise PipelineError("D-shuffled assignment key or seed provenance is inconsistent")
        donor = donor_rows[donor_id]
        donor_eligibility = donor.get("eligibility")
        if (not isinstance(donor_eligibility, Mapping)
                or donor_eligibility.get("nonempty_abstract") is not True
                or donor_eligibility.get("metadata_conflict") is not False
                or donor_eligibility.get("in_focal_exclusion_set") is not False):
            raise PipelineError("D-shuffled donor is not verified as eligible")
        if row["donor_evidence"] != donor.get("abstract"):
            raise PipelineError("D-shuffled donor evidence differs from eligible donor record")
        if row["evidence_sha256"] != _sha256_text(row["donor_evidence"]):
            raise PipelineError("D-shuffled donor evidence hash does not match")
        if (row["abstract_sha256"] != donor.get("abstract_sha256")
                or row["source_record_sha256"] != donor.get("source_record_sha256")
                or not isinstance(row["donor_source_version_ids"], list)
                or row["donor_source_version_ids"] != donor.get("source_version_ids")):
            raise PipelineError("D-shuffled donor source provenance does not match the manifest")
        source_record = canonical_source_records.get(donor_id)
        verification = row["source_verification"]
        if not isinstance(source_record, Mapping) or not isinstance(verification, Mapping):
            raise PipelineError("D-shuffled canonical source verification is missing")
        try:
            source_id = canonicalize_arxiv_id(source_record.get("paper_id"))
        except (TypeError, ValueError) as exc:
            raise PipelineError("D-shuffled canonical source record ID is invalid") from exc
        if (source_id != donor_id or source_record.get("abstract") != row["donor_evidence"]
                or verification.get("passed") is not True
                or verification.get("canonical_source_record_sha256") != _canonical_source_record_hash(source_record)
                or verification.get("canonical_source_record_sha256") != donor.get("source_record_sha256")
                or verification.get("abstract_sha256") != row["evidence_sha256"]):
            raise PipelineError("D-shuffled donor evidence/source record verification failed")
        if row["assignment_batch_id"] != batch_id:
            raise PipelineError("D-shuffled assignment row batch ID is inconsistent")
    expected_batch_hash = _sha256_json([
        {key: row[key] for key in (
            "recipient_id", "recipient_split", "donor_id", "donor_split", "assignment_key_sha256",
            "evidence_sha256", "source_record_sha256",
        )}
        for row in rows
    ])
    if batch.get("assignment_batch_sha256") != expected_batch_hash:
        raise PipelineError("D-shuffled assignment batch hash is inconsistent")
    return {"passed": True, "assignment_batch_id": batch_id, "recipient_count": len(expected),
            "donor_reuse_prohibited": True, "split": "DEVELOPMENT"}


def generate_d_empty(
    state: PipelineState,
    target_paper_id: str,
    domain_and_task: str,
    model_call: ModelCall,
    settings: PipelineSettings,
    task_evidence_check: TrustedDEmptyEvidenceAuditor | None,
    *,
    original_abstract: str | None = None,
    reference_evidence: Sequence[str] | None = None,
    retry_prompt_builder: RetryPromptBuilder | None = None,
    prompt_path: str | None = None,
    development_profile_only: bool = False,
) -> PipelineState:
    """Generate D-empty only after auditing removal of abstract and reference evidence."""
    original_references = list(reference_evidence) if isinstance(reference_evidence, Sequence) and not isinstance(
        reference_evidence, (str, bytes)
    ) else None
    abstract_hash = _sha256_text(original_abstract) if isinstance(original_abstract, str) else None
    reference_hash = _sha256_json(original_references) if original_references is not None else None
    provenance: dict[str, Any] = {
        "target_paper_id": target_paper_id,
        "recipient_id": target_paper_id,
        "domain_and_task_input": domain_and_task,
        "evidence_input": "",
        "task_sha256": hashlib.sha256(domain_and_task.encode("utf-8")).hexdigest()
        if isinstance(domain_and_task, str) else None,
        "evidence_sha256": hashlib.sha256(b"").hexdigest(),
        "evidence_absence_policy": settings.d_empty_task_evidence_policy,
        "original_evidence": {
            "abstract_sha256": abstract_hash,
            "reference_evidence_sha256": reference_hash,
            "reference_evidence_count": len(original_references) if original_references is not None else None,
        },
        "removed_fields": ["abstract", "reference_evidence"],
        "scrubbed_task_sha256": _sha256_text(domain_and_task)
        if isinstance(domain_and_task, str) else None,
        "evidence_absence_check": None,
    }
    if not isinstance(target_paper_id, str) or not target_paper_id.strip():
        return _blocked_control_generation(state, "D-empty", "target_paper_id is required", provenance)
    if not isinstance(domain_and_task, str) or not domain_and_task.strip():
        return _blocked_control_generation(state, "D-empty", "approved domain_and_task input is required", provenance)
    if not isinstance(original_abstract, str) or not original_abstract.strip():
        return _blocked_control_generation(state, "D-empty", "original abstract evidence is required for removal audit", provenance)
    if original_references is None or any(not isinstance(item, str) for item in original_references):
        return _blocked_control_generation(state, "D-empty", "explicit reference_evidence list is required for removal audit", provenance)
    if settings.d_empty_evidence_fields != ["abstract", "reference_evidence"]:
        return _blocked_control_generation(state, "D-empty", "D-empty removal fields are unresolved or inconsistent", provenance)
    if not settings.d_empty_task_evidence_policy:
        return _blocked_control_generation(state, "D-empty", "d_empty_task_evidence_policy is unresolved", provenance)
    if not issubclass(type(task_evidence_check), TrustedDEmptyEvidenceAuditor):
        return _blocked_control_generation(
            state, "D-empty",
            ("trusted development-profile D-empty auditor is not configured; callback fixtures and plain callbacks are not trusted"
             if development_profile_only else
             "trusted production D-empty auditor is not configured; callback fixtures and plain callbacks are not trusted"),
            provenance,
        )
    try:
        original_evidence_payload = {
            "abstract": original_abstract,
            "abstract_sha256": abstract_hash,
            "reference_evidence": original_references,
            "reference_evidence_sha256": reference_hash,
        }
        audit_result = task_evidence_check.audit(
            target_paper_id, domain_and_task, original_evidence_payload,
            settings.d_empty_task_evidence_policy,
        )
        if type(audit_result) is not TrustedDEmptyAuditResult:
            return _blocked_control_generation(
                state, "D-empty", "trusted auditor returned an untyped audit result", provenance,
            )
        audit = asdict(audit_result)
        provenance["evidence_absence_check"] = audit
        validation_errors = _d_empty_audit_validation_errors(
            audit, target_paper_id, domain_and_task, abstract_hash, reference_hash,
            development_profile_only=development_profile_only,
        )
        if validation_errors:
            provenance["audit_validation_errors"] = validation_errors
            return _blocked_control_generation(
                state, "D-empty", "trusted D-empty audit result is incomplete or inconsistent", provenance,
            )
    except Exception as exc:
        return _blocked_control_generation(state, "D-empty", f"task evidence audit failed: {exc}", provenance)
    try:
        rendered_prompt = _control_prompt("D-empty", domain_and_task, "", prompt_path)
        rendered_evidence = _control_prompt_evidence(rendered_prompt)
    except Exception as exc:
        return _blocked_control_generation(state, "D-empty", f"rendered evidence audit failed: {exc}", provenance)
    if rendered_evidence != "":
        return _blocked_control_generation(state, "D-empty", "rendered generator evidence is not exactly empty", provenance)
    provenance["rendered_evidence_sha256"] = _sha256_text(rendered_evidence)
    provenance["rendered_evidence_empty_verified"] = True
    return _run_control_generation(
        state, "D-empty", domain_and_task, "", provenance, model_call, settings,
        retry_prompt_builder, prompt_path, rendered_prompt=rendered_prompt,
    )


def generate_d_shuffled(
    state: PipelineState,
    target_paper_id: str,
    donor_paper_id: str,
    domain_and_task: str,
    donor_evidence: str,
    donor_assignment_provenance: Mapping[str, Any],
    model_call: ModelCall,
    settings: PipelineSettings,
    donor_assignment_check: DonorAssignmentCheck | None,
    *,
    recipient_split: str | None = None,
    assignment_batch: Mapping[str, Any] | None = None,
    recipient_records: Sequence[Mapping[str, Any]] | None = None,
    development_records: Sequence[Mapping[str, Any]] | None = None,
    canonical_source_records: Mapping[str, Mapping[str, Any]] | None = None,
    expected_manifest_sha256: str | None = None,
    expected_source_corpus_sha256: str | None = None,
    retry_prompt_builder: RetryPromptBuilder | None = None,
    prompt_path: str | None = None,
) -> PipelineState:
    """Generate D-shuffled output for an externally assigned and policy-checked donor."""
    provenance: dict[str, Any] = {
        "target_paper_id": target_paper_id,
        "donor_paper_id": donor_paper_id,
        "domain_and_task_input": domain_and_task,
        "task_sha256": hashlib.sha256(domain_and_task.encode("utf-8")).hexdigest()
        if isinstance(domain_and_task, str) else None,
        "evidence_input": donor_evidence,
        "evidence_sha256": hashlib.sha256(donor_evidence.encode("utf-8")).hexdigest()
        if isinstance(donor_evidence, str) else None,
        "assignment_provenance": dict(donor_assignment_provenance)
        if isinstance(donor_assignment_provenance, Mapping) else donor_assignment_provenance,
        "donor_constraints": settings.d_shuffled_donor_constraints,
        "assignment_algorithm_setting": settings.d_shuffled_assignment_algorithm,
        "assignment_seed_setting": settings.d_shuffled_assignment_seed,
        "within_split_only_setting": settings.d_shuffled_within_split_only,
        "donor_reuse_policy_setting": settings.d_shuffled_donor_reuse_policy,
        "donor_assignment_check": None,
    }
    if not isinstance(target_paper_id, str) or not target_paper_id.strip():
        return _blocked_control_generation(state, "D-shuffled", "target_paper_id is required", provenance)
    if not isinstance(donor_paper_id, str) or not donor_paper_id.strip():
        return _blocked_control_generation(state, "D-shuffled", "donor_paper_id is required", provenance)
    try:
        target_canonical = canonicalize_arxiv_id(target_paper_id)
        donor_canonical = canonicalize_arxiv_id(donor_paper_id)
    except (TypeError, ValueError):
        return _blocked_control_generation(state, "D-shuffled", "recipient or donor paper ID is invalid", provenance)
    if target_canonical != target_paper_id or donor_canonical != donor_paper_id:
        return _blocked_control_generation(state, "D-shuffled", "recipient and donor paper IDs must be canonical", provenance)
    if target_paper_id == donor_paper_id:
        return _blocked_control_generation(state, "D-shuffled", "donor and target paper IDs must differ", provenance)
    if not isinstance(domain_and_task, str) or not domain_and_task.strip():
        return _blocked_control_generation(state, "D-shuffled", "target domain_and_task input is required", provenance)
    if not isinstance(donor_evidence, str) or not donor_evidence.strip():
        return _blocked_control_generation(state, "D-shuffled", "donor evidence must be a nonempty string", provenance)
    if not isinstance(donor_assignment_provenance, Mapping) or not donor_assignment_provenance:
        return _blocked_control_generation(state, "D-shuffled", "external donor-assignment provenance is required", provenance)
    required_provenance = {
        "recipient_id", "recipient_split", "donor_id", "donor_split", "seed", "assignment_algorithm",
        "assignment_key", "assignment_key_sha256", "evidence_sha256", "abstract_sha256",
        "source_record_sha256", "donor_source_version_ids", "assignment_batch_id", "source_verification",
    }
    if not required_provenance.issubset(donor_assignment_provenance):
        return _blocked_control_generation(state, "D-shuffled", "donor assignment provenance is incomplete", provenance)
    if (not isinstance(assignment_batch, Mapping) or recipient_records is None
            or development_records is None or canonical_source_records is None
            or not expected_manifest_sha256 or not expected_source_corpus_sha256):
        return _blocked_control_generation(state, "D-shuffled", "independent validated batch and provenance records are required", provenance)
    try:
        validation = validate_d_shuffled_assignment_batch(
            assignment_batch, recipient_records, development_records, canonical_source_records,
            expected_manifest_sha256=expected_manifest_sha256,
            expected_source_corpus_sha256=expected_source_corpus_sha256,
        )
        provenance["assignment_batch_validation"] = validation
    except Exception as exc:
        return _blocked_control_generation(state, "D-shuffled", f"assignment batch validation failed: {exc}", provenance)
    if not any(row == dict(donor_assignment_provenance) for row in assignment_batch.get("assignments", [])):
        return _blocked_control_generation(state, "D-shuffled", "assignment is absent from validated batch", provenance)
    if recipient_split != "DEVELOPMENT":
        return _blocked_control_generation(state, "D-shuffled", "recipient split must be verified as DEVELOPMENT", provenance)
    if donor_assignment_provenance.get("recipient_id") != target_paper_id:
        return _blocked_control_generation(state, "D-shuffled", "assignment provenance target ID does not match", provenance)
    if donor_assignment_provenance.get("donor_id") != donor_paper_id:
        return _blocked_control_generation(state, "D-shuffled", "assignment provenance donor ID does not match", provenance)
    if donor_assignment_provenance.get("donor_split") != "DEVELOPMENT":
        return _blocked_control_generation(state, "D-shuffled", "donor split must be DEVELOPMENT", provenance)
    if donor_assignment_provenance.get("recipient_split") != recipient_split:
        return _blocked_control_generation(state, "D-shuffled", "recipient split provenance does not match", provenance)
    key = f"E6-D-SHUFFLED-v1|{D_SHUFFLED_SEED}|{target_paper_id}|{donor_paper_id}"
    if (donor_assignment_provenance.get("seed") != D_SHUFFLED_SEED
            or donor_assignment_provenance.get("assignment_algorithm") != D_SHUFFLED_ALGORITHM
            or donor_assignment_provenance.get("assignment_key") != key
            or donor_assignment_provenance.get("assignment_key_sha256") != _sha256_text(key)
            or donor_assignment_provenance.get("evidence_sha256") != _sha256_text(donor_evidence)):
        return _blocked_control_generation(state, "D-shuffled", "donor assignment hash/seed provenance is inconsistent", provenance)
    source_verification = donor_assignment_provenance.get("source_verification")
    if (not isinstance(source_verification, Mapping)
            or source_verification.get("passed") is not True
            or source_verification.get("canonical_source_record_sha256") != donor_assignment_provenance.get("source_record_sha256")
            or source_verification.get("abstract_sha256") != donor_assignment_provenance.get("abstract_sha256")
            or donor_assignment_provenance.get("abstract_sha256") != _sha256_text(donor_evidence)):
        return _blocked_control_generation(state, "D-shuffled", "donor source-record verification is incomplete or inconsistent", provenance)
    if not isinstance(settings.d_shuffled_donor_constraints, Mapping) or not settings.d_shuffled_donor_constraints:
        return _blocked_control_generation(state, "D-shuffled", "d_shuffled_donor_constraints are unresolved", provenance)
    if (settings.d_shuffled_assignment_algorithm != D_SHUFFLED_ALGORITHM
            or settings.d_shuffled_assignment_seed != D_SHUFFLED_SEED
            or settings.d_shuffled_within_split_only is not True
            or settings.d_shuffled_donor_reuse_policy != "prohibited_within_assignment_batch"):
        return _blocked_control_generation(state, "D-shuffled", "D-shuffled assignment policy settings are unresolved or inconsistent", provenance)
    if donor_assignment_check is None:
        return _blocked_control_generation(state, "D-shuffled", "donor-constraint validation must be injected", provenance)
    try:
        audit = dict(donor_assignment_check(
            target_paper_id, donor_paper_id, donor_assignment_provenance,
            settings.d_shuffled_donor_constraints,
        ))
        provenance["donor_assignment_check"] = audit
        if (audit.get("passed") is not True
                or audit.get("recipient_id") != target_paper_id
                or audit.get("donor_id") != donor_paper_id
                or audit.get("donor_split") != "DEVELOPMENT"
                or audit.get("evidence_sha256") != _sha256_text(donor_evidence)
                or audit.get("source_record_sha256") != donor_assignment_provenance.get("source_record_sha256")):
            return _blocked_control_generation(
                state, "D-shuffled", "donor assignment did not pass configured constraints", provenance,
            )
    except Exception as exc:
        return _blocked_control_generation(state, "D-shuffled", f"donor assignment check failed: {exc}", provenance)
    return _run_control_generation(
        state, "D-shuffled", domain_and_task, donor_evidence, provenance, model_call, settings,
        retry_prompt_builder, prompt_path,
    )

