"""Hard, per-input-set/per-arm token accounting for E6 generation workflows.

The cap and exact model tokenizer are injected. This module deliberately has
no default cap or tokenizer because either choice belongs in preregistration.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any


class TokenBudgetError(RuntimeError):
    """A generation stage could not safely continue within the configured cap."""

    def __init__(self, message: str, *, audit_metadata: Mapping[str, Any] | None = None):
        super().__init__(message)
        self.audit_metadata = dict(audit_metadata or {})


class PerArmTokenBudget:
    """Shared-cap controller; shared QH preparation can debit both QH arms."""

    def __init__(self, input_set_id: str, cap: int | None,
                 token_counter: Callable[[str], int] | None,
                 model_prompt_counter: Callable[[str, str], Mapping[str, Any]] | None = None,
                 budget_unit: str = "prompt_plus_generation_tokens"):
        if not isinstance(input_set_id, str) or not input_set_id.strip():
            raise TokenBudgetError("input_set_id is required for token budgeting")
        if type(cap) is not int or cap < 1:
            raise TokenBudgetError("a positive preregistered per-arm token cap is required")
        if not callable(token_counter) and not callable(model_prompt_counter):
            raise TokenBudgetError("an exact generator-model tokenizer is required")
        if budget_unit not in ("generated_tokens", "prompt_plus_generation_tokens"):
            raise TokenBudgetError("unsupported token budget unit")
        self.budget_unit = budget_unit
        self.input_set_id = input_set_id
        self.cap = cap
        self.token_counter = token_counter
        self.model_prompt_counter = model_prompt_counter
        self.used = {arm: 0 for arm in (
            "D", "QH", "QH-sel", "QH-rand", "HQ", "D-empty", "D-shuffled",
        )}
        self.calls: list[dict[str, Any]] = []
        self.blocked_calls: list[dict[str, Any]] = []

    def charge_preexisting_shared_calls(self, calls: Sequence[Mapping[str, Any]]) -> None:
        """Account only fully metered QH prep records before accepting reuse."""
        for row in calls:
            stage = row.get("stage")
            participants = self._participants(stage)
            total = row.get("total_tokens")
            if type(total) is not int or total < 0:
                raise TokenBudgetError(
                    "reused question-preparation calls lack exact token usage"
                )
            debit = row.get("output_tokens") if self.budget_unit == "generated_tokens" else total
            if type(debit) is not int or debit < 0:
                raise TokenBudgetError("reused preparation lacks generated-token usage")
            self._debit(participants, debit)
            self.calls.append({**dict(row), "budget_participants": list(participants),
                               "reused_preparation_call": True})

    @staticmethod
    def _participants(stage: Any) -> tuple[str, ...]:
        if stage in ("candidate_generation", "pairwise_deduplication",
                     "pairwise_deduplication_batch"):
            return ("QH-sel", "QH-rand")
        if stage == "qh_sel_ranking":
            return ("QH-sel",)
        if stage in ("D_generation", "QH_generation", "HQ_generation",
                     "D-empty_generation", "D-shuffled_generation"):
            return (stage.removesuffix("_generation"),)
        if isinstance(stage, str) and stage.endswith("_hypothesis_generation"):
            arm = stage.removesuffix("_hypothesis_generation")
            if arm in ("QH-sel", "QH-rand"):
                return (arm,)
        raise TokenBudgetError(f"unmapped token-budget stage: {stage!r}")

    def _debit(self, participants: Sequence[str], total: int) -> None:
        exceeded = [arm for arm in participants if self.used[arm] + total > self.cap]
        if exceeded:
            raise TokenBudgetError(
                "shared question preparation already exceeds the cap for " + ", ".join(exceeded)
            )
        for arm in participants:
            self.used[arm] += total

    def invoke(self, model_client: Any, stage: str, prompt: str) -> Mapping[str, Any]:
        participants = self._participants(stage)
        if self.budget_unit == "generated_tokens" and any(self.used[arm] >= self.cap for arm in participants):
            raise TokenBudgetError("generated-token budget exhausted before preflight")
        prompt_tokens = None
        if callable(self.model_prompt_counter):
            try:
                measured = self.model_prompt_counter(stage, prompt)
            except Exception as exc:
                metadata = getattr(exc, "audit_metadata", {})
                record = {
                    "input_set_id": self.input_set_id,
                    "stage": stage + "_token_count_preflight",
                    "budget_participants": list(participants),
                    "status": "token_count_preflight_failed",
                    "error": str(exc),
                }
                if isinstance(metadata, Mapping):
                    record.update({key: metadata[key] for key in (
                        "input_tokens", "output_tokens", "total_tokens", "adapter_metadata",
                    ) if key in metadata})
                if self.budget_unit == "generated_tokens":
                    self._charge_reply_usage(participants, 0, record)
                self.calls.append(record)
                raise TokenBudgetError(
                    "exact model prompt-token preflight failed: " + str(exc),
                    audit_metadata=record,
                ) from exc
            if not isinstance(measured, Mapping):
                raise TokenBudgetError("model prompt-token preflight must return usage metadata")
            prompt_tokens = measured.get("input_tokens")
            probe_output_tokens = measured.get("output_tokens")
            probe_raw = measured.get("raw_response")
            probe_total = measured.get("total_tokens")
            if type(prompt_tokens) is not int or prompt_tokens < 0:
                raise TokenBudgetError("model prompt-token preflight lacks exact prompt_eval_count")
            if type(probe_output_tokens) is not int or probe_output_tokens < 0:
                raise TokenBudgetError("model prompt-token preflight lacks exact eval_count")
            if type(probe_total) is not int or probe_total != prompt_tokens + probe_output_tokens:
                raise TokenBudgetError("model prompt-token preflight has inconsistent total token usage")
            probe_info = measured.get("token_count_preflight")
            probe_info = probe_info if isinstance(probe_info, Mapping) else {}
            probe_limit = probe_info.get("requested_num_predict")
            probe_method = probe_info.get("method")
            probe_valid = (
                probe_method == "ollama_prompt_eval_count_with_num_predict_one"
                and probe_limit == 1
                and probe_output_tokens <= 1
                and probe_info.get("bounded_probe_confirmed") is True
            )
            preflight_record = {
                "input_set_id": self.input_set_id,
                "stage": stage + "_token_count_preflight",
                "budget_participants": list(participants),
                "input_tokens": prompt_tokens,
                "output_tokens": probe_output_tokens,
                "total_tokens": probe_total,
                "status": "returned" if probe_valid else "invalid_bounded_preflight",
                "counts_toward_arm_budget": True,
                "count_method": "backend_model_tokenizer_prompt_eval_count",
                "probe_output_limit": probe_limit,
                "budget_unit": self.budget_unit,
                "budget_tokens_charged": probe_output_tokens if self.budget_unit == "generated_tokens" else probe_total,
            }
            for arm in participants:
                self.used[arm] += probe_output_tokens if self.budget_unit == "generated_tokens" else probe_total
            overrun_arms = [arm for arm in participants if self.used[arm] > self.cap]
            if overrun_arms:
                preflight_record["status"] = "preflight_budget_overrun"
                preflight_record["overrun_arms"] = overrun_arms
            self.calls.append(preflight_record)
            if overrun_arms:
                raise TokenBudgetError(
                    "prompt-token preflight itself exceeds the remaining arm budget",
                    audit_metadata=preflight_record,
                )
            if not probe_valid:
                raise TokenBudgetError(
                    "model token-count preflight was not verified as a one-token bounded probe",
                    audit_metadata=preflight_record,
                )
        else:
            prompt_tokens = self._count(prompt, "prompt")
        remaining = min(self.cap - self.used[arm] for arm in participants)
        output_limit = remaining if self.budget_unit == "generated_tokens" else remaining - prompt_tokens
        if output_limit < 1:
            blocked = {
                "input_set_id": self.input_set_id, "stage": stage,
                "participants": list(participants), "prompt_tokens": prompt_tokens,
                "remaining_before_call": remaining, "status": "blocked_before_call",
                "error": ("generated-token budget has no output token remaining" if self.budget_unit == "generated_tokens"
                          else "prompt plus at least one output token cannot fit in remaining budget"),
            }
            self.blocked_calls.append(blocked)
            raise TokenBudgetError(blocked["error"], audit_metadata=blocked)
        options = getattr(model_client, "generation_options", {})
        options = options if isinstance(options, Mapping) else {}
        configured_output = options.get("num_predict")
        if type(configured_output) is int and configured_output > 0:
            output_limit = min(output_limit, configured_output)
        context_limit = options.get("num_ctx")
        if type(context_limit) is int and context_limit > 0 and prompt_tokens + output_limit > context_limit:
            blocked = {
                "input_set_id": self.input_set_id, "stage": stage,
                "participants": list(participants), "status": "context_overflow",
                "prompt_tokens": prompt_tokens, "output_limit": output_limit,
                "context_limit": context_limit,
                "error": "exact prompt plus requested output exceeds context; no truncation or silent limit reduction",
            }
            self.blocked_calls.append(blocked)
            raise TokenBudgetError(blocked["error"], audit_metadata=blocked)
        bounded_call = getattr(model_client, "call_with_token_limit", None)
        if not callable(bounded_call):
            blocked = {
                "input_set_id": self.input_set_id, "stage": stage,
                "participants": list(participants), "prompt_tokens": prompt_tokens,
                "remaining_before_call": remaining, "status": "blocked_before_call",
                "error": "model backend must support a request-level output-token limit",
            }
            self.blocked_calls.append(blocked)
            raise TokenBudgetError(blocked["error"], audit_metadata=blocked)

        try:
            reply = bounded_call(stage, prompt, max_output_tokens=output_limit)
        except Exception as exc:
            metadata = getattr(exc, "audit_metadata", {})
            record = {
                "input_set_id": self.input_set_id, "stage": stage,
                "budget_participants": list(participants),
                "prompt_tokens_preflight": prompt_tokens,
                "output_token_limit": output_limit, "status": "backend_failed",
                "error": str(exc),
            }
            if isinstance(metadata, Mapping):
                record.update({key: metadata[key] for key in (
                    "input_tokens", "output_tokens", "total_tokens", "latency_seconds",
                    "adapter_metadata", "raw_response",
                ) if key in metadata})
            self._charge_reply_usage(participants, prompt_tokens, record)
            self.calls.append(record)
            raise

        if isinstance(reply, str):
            raw = reply
            result: dict[str, Any] = {"raw_response": raw}
        elif isinstance(reply, Mapping):
            raw = reply.get("raw_response", reply.get("text"))
            if not isinstance(raw, str):
                raise TokenBudgetError("bounded backend response lacks raw text")
            result = dict(reply)
        else:
            raise TokenBudgetError("bounded backend must return text or a response mapping")

        metadata = result.get("adapter_metadata")
        adapter = dict(metadata) if isinstance(metadata, Mapping) else {}
        reported_input = result.get("input_tokens", adapter.get("prompt_eval_count"))
        reported_output = result.get("output_tokens", adapter.get("eval_count"))
        mismatches = []
        if callable(self.model_prompt_counter):
            if (type(reported_input) is not int or type(reported_output) is not int
                    or reported_input < 0 or reported_output < 0):
                unavailable = {
                    "input_set_id": self.input_set_id, "stage": stage,
                    "budget_participants": list(participants),
                    "prompt_tokens_preflight": prompt_tokens,
                    "reported_prompt_eval_count": reported_input,
                    "reported_eval_count": reported_output,
                    "status": "generation_usage_unavailable",
                    "error": "exact backend usage is required; arm locked to prevent unmetered retries",
                }
                self.calls.append(unavailable)
                self.blocked_calls.append({
                    "input_set_id": self.input_set_id, "stage": stage,
                    "participants": list(participants),
                    "status": "generation_usage_unavailable",
                    "error": unavailable["error"],
                })
                for arm in participants:
                    self.used[arm] = self.cap
                raise TokenBudgetError(
                    "model backend lacks exact prompt_eval_count/eval_count required by token budget",
                    audit_metadata=unavailable,
                )
            if reported_input != prompt_tokens:
                mismatches.append(
                    "generation prompt_eval_count differs from exact rendered-prompt preflight"
                )
            actual_prompt_tokens = reported_input
            output_tokens = reported_output
        else:
            output_tokens = self._count(raw, "response")
            actual_prompt_tokens = prompt_tokens
            if type(reported_input) is int and reported_input != prompt_tokens:
                mismatches.append("backend prompt token count differs from configured tokenizer")
            if type(reported_output) is int and reported_output != output_tokens:
                mismatches.append("backend output token count differs from configured tokenizer")
        total_tokens = actual_prompt_tokens + output_tokens
        reported_total = result.get("total_tokens", adapter.get("total_tokens"))
        if type(reported_total) is int and reported_total != total_tokens:
            mismatches.append("backend total token count differs from configured tokenizer")

        record = {
            "input_set_id": self.input_set_id, "stage": stage,
            "budget_participants": list(participants),
            "input_tokens": actual_prompt_tokens, "output_tokens": output_tokens,
            "total_tokens": total_tokens, "prompt_tokens_preflight": prompt_tokens,
            "output_token_limit": output_limit, "remaining_before_call": remaining,
            "status": "returned", "reported_usage_mismatches": mismatches,
        }
        if adapter:
            record["adapter_metadata"] = adapter
        debit = output_tokens if self.budget_unit == "generated_tokens" else total_tokens
        record["budget_unit"] = self.budget_unit
        record["budget_tokens_charged"] = debit
        exceeded = [arm for arm in participants if self.used[arm] + debit > self.cap]
        for arm in participants:
            self.used[arm] += debit
        if exceeded:
            record["status"] = "backend_budget_overrun"
            record["overrun_arms"] = exceeded
        self.calls.append(record)
        result.update({
            "input_tokens": prompt_tokens, "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "adapter_metadata": {
                **adapter,
                "token_budget": {
                    "input_set_id": self.input_set_id,
                    "participants": list(participants), "cap": self.cap,
                    "remaining_before_call": remaining,
                    "prompt_tokens_preflight": prompt_tokens,
                    "output_token_limit": output_limit,
                    "tokenizer_id": getattr(
                        self.model_prompt_counter or self.token_counter,
                        "tokenizer_id", None,
                    ),
                    "preflight_count_charged_to_budget": callable(self.model_prompt_counter),
                },
            },
        })

        done_reason = adapter.get("done_reason")
        incomplete = (
            result.get("generation_complete") is False
            or adapter.get("done") is False
            or done_reason in {"length", "max_tokens", "token_limit"}
        )
        if mismatches:
            record["status"] = "tokenizer_mismatch"
            raise TokenBudgetError(
                "; ".join(mismatches),
                audit_metadata={**record, "raw_response": raw},
            )
        if exceeded:
            raise TokenBudgetError(
                "backend exceeded the request-level token budget despite the output cap",
                audit_metadata={**record, "raw_response": raw},
            )
        if incomplete:
            record["status"] = "budget_limited_incomplete"
            raise TokenBudgetError(
                "generation reached the request token limit before confirmed completion",
                audit_metadata={**record, "raw_response": raw},
            )
        return result

    def _count(self, text: str, name: str) -> int:
        try:
            value = self.token_counter(text)
        except Exception as exc:
            raise TokenBudgetError(f"exact {name} token counting failed: {exc}") from exc
        if type(value) is not int or value < 0:
            raise TokenBudgetError(f"exact {name} token count must be a nonnegative integer")
        return value

    def _charge_reply_usage(self, participants: Sequence[str], prompt_tokens: int,
                            record: dict[str, Any]) -> None:
        input_tokens = record.get("input_tokens")
        output_tokens = record.get("output_tokens")
        if type(input_tokens) is int and type(output_tokens) is int:
            total = input_tokens + output_tokens
        else:
            total_value = record.get("total_tokens")
            total = total_value if type(total_value) is int else 0
        if self.budget_unit == "generated_tokens":
            if type(output_tokens) is not int or output_tokens < 0:
                for arm in participants:
                    self.used[arm] = self.cap
                record["usage_unavailable"] = True
                return
            debit = output_tokens
        else:
            debit = total
        record["budget_unit"] = self.budget_unit
        record["budget_tokens_charged"] = debit
        if total or self.budget_unit == "generated_tokens":
            for arm in participants:
                self.used[arm] += debit
            record["total_tokens"] = total
            overrun = [arm for arm in participants if self.used[arm] > self.cap]
            if overrun:
                record["status"] = "backend_budget_overrun"
                record["overrun_arms"] = overrun
        else:
            record["usage_unavailable"] = True

    def arm_report(self, arm: str) -> dict[str, Any]:
        blocked = [row for row in self.blocked_calls if arm in row.get("participants", [])]
        status = (
            "blocked_before_call" if blocked else
            "cap_reached" if self.used[arm] >= self.cap else "within_budget"
        )
        return {
            "input_set_id": self.input_set_id, "arm": arm,
            "budget_unit": self.budget_unit,
            "prompt_tokens_recorded": sum(row.get("input_tokens", 0) for row in self.calls
                                          if arm in row.get("budget_participants", [])
                                          and type(row.get("input_tokens")) is int),
            "budget_tokens": self.cap, "tokens_used": self.used[arm],
            "tokens_remaining": self.cap - self.used[arm],
            "within_budget": self.used[arm] <= self.cap,
            "budget_status": status,
            "blocked_call_count": len(blocked),
            "blocked_calls": blocked,
        }
