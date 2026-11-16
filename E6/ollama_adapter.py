"""Local-only Ollama adapter for the injected E6 model-call interface.

The adapter returns model text unchanged. E6's existing pipeline remains
responsible for parsing JSON and validating arm-specific output structure.
"""

from __future__ import annotations

import hashlib
import json
import socket
import time
import urllib.error
import urllib.request
from typing import Any, Mapping

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "gemma3:12b"


class OllamaRequestError(RuntimeError):
    """Auditable local Ollama request failure."""

    def __init__(
        self, message: str, *, category: str, latency_seconds: float,
        model: str, stage: str, generation_settings: Mapping[str, Any],
        prompt_sha256: str, status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        super().__init__(message)
        self.category = category
        self.status_code = status_code
        self.response_body = response_body
        self.latency_seconds = latency_seconds
        self.model = model
        # Tokenization and prompt-template rendering are performed by the same
        # installed Ollama runner used for generation. The verifier binds this
        # runtime label to the local model/tag digest.
        self.tokenizer_id = f"ollama-runner-prompt-eval-count:{model}"
        self.tokenizer_id = f"ollama-runner-prompt-eval-count:{model}"
        self.stage = stage
        self.generation_settings = dict(generation_settings)
        self.prompt_sha256 = prompt_sha256

    @property
    def audit_metadata(self) -> dict[str, Any]:
        return {
            "backend": "ollama-local",
            "endpoint": OLLAMA_ENDPOINT,
            "model": self.model,
            "stage": self.stage,
            "generation_settings": self.generation_settings,
            "prompt_sha256": self.prompt_sha256,
            "http_status": self.status_code,
            "error_category": self.category,
            "error": str(self),
            "response_body": self.response_body,
            "latency_seconds": self.latency_seconds,
        }


class OllamaModelClient:
    """Callable `(stage, prompt)` client for E6, restricted to local Ollama.

    `generation_options` are passed through unchanged so the caller controls
    decoding and token budgets. The adapter only enables Ollama JSON mode;
    it does not choose temperature, seed, retries, or scientific policy.
    """

    # Independent stateless requests may be queued concurrently; the local
    # Ollama server controls actual parallelism. No multi-example prompt batch.
    supports_independent_parallel_requests = True

    def __init__(
        self, *, model: str = DEFAULT_MODEL, timeout_seconds: float = 600.0,
        generation_options: Mapping[str, Any] | None = None,
        preflight_context_limit: int | None = None,
    ) -> None:
        if not isinstance(model, str) or not model.strip():
            raise ValueError("model must be a nonempty local Ollama model name")
        if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be a positive number")
        if generation_options is not None and not isinstance(generation_options, Mapping):
            raise TypeError("generation_options must be a mapping")
        if preflight_context_limit is not None and (type(preflight_context_limit) is not int or preflight_context_limit < 1):
            raise ValueError("preflight_context_limit must be positive")
        self.preflight_context_limit = preflight_context_limit
        self.model = model
        self.timeout_seconds = float(timeout_seconds)
        self.generation_options = dict(generation_options or {})

    @property
    def model_configuration(self) -> dict[str, Any]:
        return {
            "backend": "ollama-local",
            "endpoint": OLLAMA_ENDPOINT,
            "model": self.model,
            "timeout_seconds": self.timeout_seconds,
            "format": "json",
            "stream": False,
            "generation_options": dict(self.generation_options),
        }

    def __call__(self, stage: str, prompt: str) -> dict[str, Any]:
        return self._call(stage, prompt, self.generation_options, None)

    def call_with_token_limit(
        self, stage: str, prompt: str, *, max_output_tokens: int,
    ) -> dict[str, Any]:
        """Call Ollama with a request-local hard output-token ceiling."""
        if type(max_output_tokens) is not int or max_output_tokens < 1:
            raise ValueError("max_output_tokens must be a positive integer")
        options = dict(self.generation_options)
        configured_limit = options.get("num_predict")
        options["num_predict"] = min(configured_limit, max_output_tokens) \
            if type(configured_limit) is int and configured_limit > 0 else max_output_tokens
        return self._call(stage, prompt, options, max_output_tokens)

    def count_prompt_tokens(self, stage: str, prompt: str) -> dict[str, Any]:
        """Ask the installed Ollama runner to count its fully rendered prompt.

        Ollama's own prompt_eval_count includes the GGUF tokenizer and any
        model template/special-token formatting. A one-token completion cap
        avoids Ollama-version-dependent `num_predict=0` semantics; the probe
        completion is discarded and its actual usage is charged to the budget.
        """
        options = dict(self.generation_options)
        # Conservatively refuse large raw input BEFORE a counting probe. This
        # byte admission guard is not a substitute for an independent tokenizer.
        if self.preflight_context_limit is not None and len(prompt.encode('utf-8')) + 8192 >= max(self.preflight_context_limit, 131072):
            raise ValueError("prompt exceeds conservative preflight admission allowance; independent offline tokenization or a revised approved context policy required")
        options["num_predict"] = 1
        if self.preflight_context_limit is not None:
            options["num_ctx"] = self.preflight_context_limit
        result = self._call(stage + "_token_count_preflight", prompt, options, 1)
        measured_prompt = result.get("input_tokens")
        if self.preflight_context_limit is not None and (type(measured_prompt) is not int or measured_prompt >= self.preflight_context_limit - 1):
            raise ValueError("counting preflight may have truncated the input; exact-count evidence unavailable")
        adapter_metadata = result.get("adapter_metadata", {})
        result["token_count_preflight"] = {
            "method": "ollama_prompt_eval_count_with_num_predict_one",
            "requested_num_predict": 1,
            "num_ctx": options.get("num_ctx"),
            "bounded_probe_confirmed": type(result.get("output_tokens")) is int
            and 0 <= result["output_tokens"] <= 1
            and type(result.get("input_tokens")) is int
            and result.get("total_tokens") == result.get("input_tokens") + result.get("output_tokens")
            and adapter_metadata.get("done") is True,
            "prompt_eval_count": result.get("input_tokens"),
            "eval_count": result.get("output_tokens"),
        }
        return result

    def _call(
        self, stage: str, prompt: str, options: Mapping[str, Any],
        requested_output_token_limit: int | None,
    ) -> dict[str, Any]:
        if not isinstance(stage, str) or not stage:
            raise ValueError("stage must be a nonempty string")
        if not isinstance(prompt, str):
            raise TypeError("prompt must be a string")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": dict(options),
        }
        request = urllib.request.Request(
            OLLAMA_ENDPOINT,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        generation_settings = {
            "format": "json", "stream": False,
            "options": dict(options),
        }
        started = time.monotonic()
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                status = response.getcode()
                body_bytes = response.read()
        except urllib.error.HTTPError as exc:
            elapsed = time.monotonic() - started
            body = _decode_body(exc.read())
            raise OllamaRequestError(
                f"local Ollama returned HTTP {exc.code}", category="http_error",
                latency_seconds=elapsed, status_code=exc.code, response_body=body,
                model=self.model, stage=stage, generation_settings=generation_settings,
                prompt_sha256=prompt_sha256,
            ) from exc
        except (TimeoutError, urllib.error.URLError, OSError) as exc:
            elapsed = time.monotonic() - started
            reason = getattr(exc, "reason", exc)
            category = "timeout" if any(
                isinstance(value, (TimeoutError, socket.timeout)) for value in (exc, reason)
            ) else "connection_error"
            raise OllamaRequestError(
                f"local Ollama {category}: {reason}", category=category,
                latency_seconds=elapsed, model=self.model, stage=stage,
                generation_settings=generation_settings, prompt_sha256=prompt_sha256,
            ) from exc

        elapsed = time.monotonic() - started
        body = _decode_body(body_bytes)
        try:
            result = json.loads(body)
        except json.JSONDecodeError as exc:
            raise OllamaRequestError(
                f"local Ollama returned malformed HTTP JSON: {exc}",
                category="malformed_http_json", latency_seconds=elapsed,
                status_code=status, response_body=body, model=self.model, stage=stage,
                generation_settings=generation_settings, prompt_sha256=prompt_sha256,
            ) from exc
        if not isinstance(result, Mapping):
            raise OllamaRequestError(
                "local Ollama response must be a JSON object", category="invalid_http_response",
                latency_seconds=elapsed, status_code=status, response_body=body,
                model=self.model, stage=stage, generation_settings=generation_settings,
                prompt_sha256=prompt_sha256,
            )
        raw = result.get("response")
        if not isinstance(raw, str):
            raise OllamaRequestError(
                "local Ollama response is missing string field 'response'",
                category="invalid_http_response", latency_seconds=elapsed,
                status_code=status, response_body=body,
                model=self.model, stage=stage, generation_settings=generation_settings,
                prompt_sha256=prompt_sha256,
            )

        input_tokens = _optional_nonnegative_int(result.get("prompt_eval_count"))
        output_tokens = _optional_nonnegative_int(result.get("eval_count"))
        metadata = {
            "backend": "ollama-local",
            "endpoint": OLLAMA_ENDPOINT,
            "stage": stage,
            "http_status": status,
            "model": result.get("model", self.model),
            "created_at": result.get("created_at"),
            "done_reason": result.get("done_reason"),
            "model_identity": {
                "requested_model": self.model,
                "reported_model": result.get("model"),
                "reported_created_at": result.get("created_at"),
            },
            "generation_settings": {
                "format": "json",
                "stream": False,
                "options": dict(options),
            },
            "prompt_sha256": prompt_sha256,
            "prompt_characters": len(prompt),
            "latency_seconds": elapsed,
            "prompt_eval_count": input_tokens,
            "eval_count": output_tokens,
            "total_tokens": (
                input_tokens + output_tokens
                if input_tokens is not None and output_tokens is not None else None
            ),
            "usage_metadata_available": input_tokens is not None or output_tokens is not None,
            "done": result.get("done"),
            "requested_output_token_limit": requested_output_token_limit,
        }
        return {
            "raw_response": raw,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": metadata["total_tokens"],
            "latency_seconds": elapsed,
            "http_status": status,
            "model": metadata["model"],
            "model_identity": metadata["model_identity"],
            "generation_settings": metadata["generation_settings"],
            "adapter_metadata": metadata,
        }


def _decode_body(body: bytes) -> str:
    return body.decode("utf-8", errors="replace")


def _optional_nonnegative_int(value: Any) -> int | None:
    if type(value) is int and value >= 0:
        return value
    return None
