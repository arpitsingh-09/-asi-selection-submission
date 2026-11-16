"""Focused tests for shared per-input-set token-budget enforcement."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from token_budget import PerArmTokenBudget, TokenBudgetError


def fixture_tokens(text):
    return len(text.split())


class BoundedFixtureClient:
    def __init__(self, responses=None, ignore_limit=False):
        self.responses = list(responses or ["one"])
        self.ignore_limit = ignore_limit
        self.calls = []

    def call_with_token_limit(self, stage, prompt, *, max_output_tokens):
        self.calls.append((stage, prompt, max_output_tokens))
        response = self.responses.pop(0) if self.responses else "one"
        return {
            "raw_response": response,
            "adapter_metadata": {
                "done_reason": "stop",
                "requested_output_token_limit": max_output_tokens,
            },
        }


class ExactPromptCounter:
    tokenizer_id = "ollama-runner-prompt-eval-count:fixture"

    def __init__(self, count=2, output=1):
        self.count = count
        self.output = output
        self.calls = []

    def __call__(self, stage, prompt):
        self.calls.append((stage, prompt))
        return {
            "raw_response": "x" if self.output else "",
            "input_tokens": self.count, "output_tokens": self.output,
            "total_tokens": self.count + self.output,
            "token_count_preflight": {
                "method": "ollama_prompt_eval_count_with_num_predict_one",
                "requested_num_predict": 1,
                "bounded_probe_confirmed": self.output <= 1,
            },
        }


class ExactUsageClient:
    def __init__(self, prompt_tokens=2, output_tokens=4):
        self.prompt_tokens = prompt_tokens
        self.output_tokens = output_tokens
        self.calls = []

    def call_with_token_limit(self, stage, prompt, *, max_output_tokens):
        self.calls.append((stage, prompt, max_output_tokens))
        return {
            "raw_response": "answer", "input_tokens": self.prompt_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.prompt_tokens + self.output_tokens,
            "adapter_metadata": {"done": True, "done_reason": "stop"},
        }


class TokenBudgetTests(unittest.TestCase):
    def test_context_overflow_blocks_without_silently_shrinking_output_or_cap(self):
        client = ExactUsageClient(prompt_tokens=7000, output_tokens=2)
        client.generation_options = {'num_ctx': 8192, 'num_predict': 2048}
        ledger = PerArmTokenBudget('context-fixture', 8192, None,
                                   ExactPromptCounter(count=7000), budget_unit='generated_tokens')
        with self.assertRaisesRegex(TokenBudgetError, 'context'):
            ledger.invoke(client, 'D_generation', 'fixture prompt')
        self.assertFalse(client.calls)
        self.assertEqual(ledger.cap, 8192)
        self.assertEqual(ledger.arm_report('D')['tokens_used'], 1)
        self.assertEqual(ledger.blocked_calls[0]['status'], 'context_overflow')

    def test_context_guard_reserves_the_configured_output(self):
        client = ExactUsageClient(prompt_tokens=6144, output_tokens=2)
        client.generation_options = {'num_ctx': 8192, 'num_predict': 2048}
        ledger = PerArmTokenBudget('context-fixture', 8192, None,
                                   ExactPromptCounter(count=6144), budget_unit='generated_tokens')
        ledger.invoke(client, 'D_generation', 'fixture prompt')
        self.assertEqual(client.calls[0][2], 2048)
        self.assertEqual(ledger.arm_report('D')['tokens_used'], 3)

    def test_generated_budget_records_prompts_without_debiting_them(self):
        probe = ExactPromptCounter(count=100, output=1)
        ledger = PerArmTokenBudget('generated-unit', 10, None, probe, budget_unit='generated_tokens')
        client = ExactUsageClient(prompt_tokens=100, output_tokens=3)
        ledger.invoke(client, 'D_generation', 'long prompt')
        self.assertEqual(client.calls[0][2], 9)
        report = ledger.arm_report('D')
        self.assertEqual(report['tokens_used'], 4)
        self.assertEqual(report['prompt_tokens_recorded'], 200)
        self.assertEqual(report['budget_unit'], 'generated_tokens')

    def test_generated_budget_preflight_cannot_run_after_exhaustion(self):
        probe = ExactPromptCounter(count=100, output=1)
        ledger = PerArmTokenBudget('generated-unit', 1, None, probe, budget_unit='generated_tokens')
        client = ExactUsageClient(prompt_tokens=100, output_tokens=1)
        with self.assertRaises(TokenBudgetError):
            ledger.invoke(client, 'D_generation', 'prompt')
        with self.assertRaises(TokenBudgetError):
            ledger.invoke(client, 'D_generation', 'prompt')
        self.assertEqual(len(probe.calls), 1)
        self.assertFalse(client.calls)

    def test_generated_shared_calls_and_reuse_charge_only_output(self):
        ledger = PerArmTokenBudget('generated-unit', 10, fixture_tokens, budget_unit='generated_tokens')
        ledger.charge_preexisting_shared_calls([{'stage': 'candidate_generation',
                                                'input_tokens': 100, 'output_tokens': 3, 'total_tokens': 103}])
        self.assertEqual(ledger.arm_report('QH-sel')['tokens_used'], 3)
        self.assertEqual(ledger.arm_report('QH-rand')['tokens_used'], 3)
        ledger.invoke(BoundedFixtureClient(['one two']), 'qh_sel_ranking', 'many prompt tokens here')
        self.assertEqual(ledger.arm_report('QH-sel')['tokens_used'], 5)
        self.assertEqual(ledger.arm_report('QH-rand')['tokens_used'], 3)

    def test_generated_failed_preflight_with_unknown_usage_locks_arm(self):
        def failed_probe(stage, prompt):
            raise RuntimeError('fixture preflight connection lost')
        ledger = PerArmTokenBudget('generated-unit', 10, None, failed_probe, budget_unit='generated_tokens')
        with self.assertRaises(TokenBudgetError):
            ledger.invoke(ExactUsageClient(), 'D_generation', 'prompt')
        self.assertEqual(ledger.arm_report('D')['tokens_remaining'], 0)
        self.assertTrue(ledger.calls[-1]['usage_unavailable'])

    def test_generated_unknown_failure_usage_locks_arm(self):
        class FailingClient:
            def call_with_token_limit(self, *args, **kwargs):
                raise RuntimeError('fixture transport failure')
        ledger = PerArmTokenBudget('generated-unit', 10, fixture_tokens, budget_unit='generated_tokens')
        with self.assertRaises(RuntimeError):
            ledger.invoke(FailingClient(), 'D_generation', 'prompt')
        self.assertEqual(ledger.arm_report('D')['tokens_remaining'], 0)

    def test_all_seven_arms_and_shared_question_stages_are_debited(self):
        ledger = PerArmTokenBudget("paper-1", 100, fixture_tokens)
        client = BoundedFixtureClient()
        stages = (
            ("D_generation", "p"), ("QH_generation", "p"),
            ("candidate_generation", "p"),
            ("pairwise_deduplication_batch", "p"),
            ("qh_sel_ranking", "p"),
            ("QH-sel_hypothesis_generation", "p"),
            ("QH-rand_hypothesis_generation", "p"),
            ("HQ_generation", "p"), ("D-empty_generation", "p"),
            ("D-shuffled_generation", "p"),
        )
        for stage, prompt in stages:
            ledger.invoke(client, stage, prompt)
        reports = {arm: ledger.arm_report(arm) for arm in ledger.used}
        self.assertEqual(set(reports), {"D", "QH", "QH-sel", "QH-rand", "HQ", "D-empty", "D-shuffled"})
        for arm in ("D", "QH", "HQ", "D-empty", "D-shuffled"):
            self.assertEqual(reports[arm]["tokens_used"], 2)
        self.assertEqual(reports["QH-sel"]["tokens_used"], 8)
        self.assertEqual(reports["QH-rand"]["tokens_used"], 6)
        self.assertEqual(len(ledger.calls), 10)
        self.assertEqual(sum(row["total_tokens"] for row in ledger.calls), 20)

    def test_shared_stage_is_blocked_before_call_when_either_arm_lacks_budget(self):
        ledger = PerArmTokenBudget("paper-2", 5, fixture_tokens)
        client = BoundedFixtureClient(["one", "one"])
        ledger.invoke(client, "qh_sel_ranking", "p p")
        # QH-sel has used 3; QH-rand has used 0, but a shared-stage call must
        # fit within the smaller remaining budget for both arms.
        with self.assertRaisesRegex(TokenBudgetError, "cannot fit"):
            ledger.invoke(client, "candidate_generation", "p p p")
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(ledger.arm_report("QH-sel")["budget_status"], "blocked_before_call")
        self.assertEqual(ledger.arm_report("QH-rand")["budget_status"], "blocked_before_call")

    def test_retries_consume_budget_and_later_attempt_is_not_called(self):
        ledger = PerArmTokenBudget("paper-3", 7, fixture_tokens)
        client = BoundedFixtureClient(["bad output", "second output", "never"])
        # The first two invocations model a failed generation and its retry.
        ledger.invoke(client, "D_generation", "prompt")  # 1 + 2 tokens
        ledger.invoke(client, "D_generation", "prompt")  # 1 + 2 tokens
        with self.assertRaises(TokenBudgetError):
            ledger.invoke(client, "D_generation", "prompt")
        self.assertEqual(len(client.calls), 2)
        self.assertEqual(ledger.arm_report("D")["tokens_used"], 6)
        self.assertEqual(ledger.arm_report("D")["tokens_remaining"], 1)

    def test_request_that_reaches_backend_limit_is_recorded_as_incomplete(self):
        class LimitedClient(BoundedFixtureClient):
            def call_with_token_limit(self, stage, prompt, *, max_output_tokens):
                self.calls.append((stage, prompt, max_output_tokens))
                return {"raw_response": "partial output", "adapter_metadata": {"done_reason": "length"}}

        ledger = PerArmTokenBudget("paper-4", 20, fixture_tokens)
        with self.assertRaisesRegex(TokenBudgetError, "before confirmed completion"):
            ledger.invoke(LimitedClient(), "D_generation", "prompt")
        self.assertEqual(ledger.arm_report("D")["tokens_used"], 3)
        self.assertEqual(ledger.calls[0]["status"], "budget_limited_incomplete")

    def test_unconfigured_cap_or_tokenizer_fails_closed(self):
        for cap, tokenizer in ((None, fixture_tokens), (10, None)):
            with self.subTest(cap=cap, tokenizer=tokenizer):
                with self.assertRaises(TokenBudgetError):
                    PerArmTokenBudget("paper-5", cap, tokenizer)

    def test_reused_prep_requires_actual_usage_and_charges_both_selection_arms(self):
        ledger = PerArmTokenBudget("paper-6", 20, fixture_tokens)
        ledger.charge_preexisting_shared_calls([
            {"stage": "candidate_generation", "total_tokens": 4},
            {"stage": "pairwise_deduplication_batch", "total_tokens": 3},
        ])
        self.assertEqual(ledger.arm_report("QH-sel")["tokens_used"], 7)
        self.assertEqual(ledger.arm_report("QH-rand")["tokens_used"], 7)
        with self.assertRaisesRegex(TokenBudgetError, "lack exact token usage"):
            ledger.charge_preexisting_shared_calls([{"stage": "qh_sel_ranking"}])

    def test_exact_backend_counts_probe_and_generation_usage(self):
        counter = ExactPromptCounter()
        client = ExactUsageClient()
        ledger = PerArmTokenBudget("paper-exact", 30, None, model_prompt_counter=counter)
        result = ledger.invoke(client, "D_generation", "two words")
        self.assertEqual(counter.calls, [("D_generation", "two words")])
        self.assertEqual(client.calls[0][2], 25)  # cap less preflight and generation prompt
        self.assertEqual(result["total_tokens"], 6)
        self.assertEqual(ledger.arm_report("D")["tokens_used"], 9)
        self.assertEqual(ledger.calls[0]["stage"], "D_generation_token_count_preflight")
        self.assertEqual(ledger.calls[0]["total_tokens"], 3)

    def test_exact_backend_prompt_mismatch_fails_closed_and_is_charged(self):
        counter = ExactPromptCounter(count=2, output=0)
        client = ExactUsageClient(prompt_tokens=3, output_tokens=1)
        ledger = PerArmTokenBudget("paper-mismatch", 30, None, model_prompt_counter=counter)
        with self.assertRaisesRegex(TokenBudgetError, "preflight"):
            ledger.invoke(client, "D_generation", "prompt")
        self.assertEqual(ledger.calls[-1]["status"], "tokenizer_mismatch")
        self.assertEqual(ledger.arm_report("D")["tokens_used"], 6)

    def test_invalid_probe_usage_fails_before_generation(self):
        counter = ExactPromptCounter(count=2, output=2)
        client = ExactUsageClient()
        ledger = PerArmTokenBudget("paper-probe", 30, None, model_prompt_counter=counter)
        with self.assertRaisesRegex(TokenBudgetError, "one-token bounded probe"):
            ledger.invoke(client, "D_generation", "prompt")
        self.assertEqual(client.calls, [])
        self.assertEqual(ledger.arm_report("D")["tokens_used"], 4)


if __name__ == "__main__":
    unittest.main()
