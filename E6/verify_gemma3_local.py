#!/usr/bin/env python3
"""Development-only local verification for the proposed E6 Gemma generator.

Run from a normal Mac Terminal with Ollama already running and gemma3:12b
installed. This script makes two small local requests, writes no files, does
not download models, and does not run the E6 experiment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from ollama_adapter import OllamaModelClient

OLLAMA_BASE = "http://127.0.0.1:11434"
MODEL = "gemma3:12b"
DIGEST_HEX_RE = re.compile(r"^[0-9a-fA-F]{64}$")


class DigestMismatchError(ValueError):
    def __init__(self, diagnostic: Mapping[str, Any]):
        self.diagnostic = dict(diagnostic)
        super().__init__(str(self.diagnostic.get("failure_reason", "digest verification failed")))


def _sha256_hex(value: Any, field_name: str, *, allow_prefix: bool) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} is missing; expected a SHA-256 digest")
    digest = value
    if allow_prefix and digest.startswith("sha256:"):
        digest = digest[len("sha256:"):]
    if not DIGEST_HEX_RE.fullmatch(digest):
        expected = "64 hexadecimal characters (optionally prefixed with sha256:)" \
            if allow_prefix else "64 hexadecimal characters without a prefix"
        raise ValueError(f"{field_name} is invalid; expected {expected}")
    return digest.lower()


def _request_json(path: str, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        OLLAMA_BASE + path, data=data,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="GET" if payload is None else "POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            value = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Ollama local verification request {path} failed: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"Ollama {path} response must be a JSON object")
    return value


def local_model_row(tags: Mapping[str, Any], model: str = MODEL) -> dict[str, Any]:
    models = tags.get("models")
    if not isinstance(models, list):
        raise ValueError("/api/tags response lacks models list")
    matches = [row for row in models if isinstance(row, dict)
               and row.get("name", row.get("model")) == model]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one installed model named {model}")
    row = matches[0]
    digest = row.get("digest")
    # Ollama 0.40.15 /api/tags serializes this field as bare 64-character
    # hexadecimal. It is the tag/manifest digest, not an individual layer hash.
    _sha256_hex(digest, f"/api/tags models[{model!r}].digest", allow_prefix=True)
    return row


def verify_api_tag_digest(
    row: Mapping[str, Any], *, api_manifest_sha256: str,
    api_manifest_path: str,
    installed_manifest_sha256: str,
    installed_model_layer_digest: str,
    inventory_manifest_sha256: str,
    inventory_model_layer_digest: str,
    source_manifest_layer_digest: str | None = None,
    source_manifest_blob_sha256: str | None = None,
    installed_manifest_path: str | None = None,
) -> dict[str, Any]:
    """Match /api/tags only to the manifest representation selected for that tag."""
    actual = _sha256_hex(
        row.get("digest"), "/api/tags model digest", allow_prefix=True,
    )
    api_manifest = _sha256_hex(
        api_manifest_sha256, "Ollama-selected local tag manifest SHA-256", allow_prefix=False,
    )
    installed_manifest = _sha256_hex(
        installed_manifest_sha256, "installed manifest SHA-256", allow_prefix=False,
    )
    installed_layer = _sha256_hex(
        installed_model_layer_digest, "installed model-layer digest", allow_prefix=True,
    )
    inventory_manifest = _sha256_hex(
        inventory_manifest_sha256, "recorded inventory manifest SHA-256", allow_prefix=False,
    )
    inventory_layer = _sha256_hex(
        inventory_model_layer_digest, "recorded inventory model-layer digest", allow_prefix=True,
    )
    source_layer = None if source_manifest_layer_digest is None else _sha256_hex(
        source_manifest_layer_digest, "embedded source-manifest layer digest", allow_prefix=True,
    )
    source_blob = None if source_manifest_blob_sha256 is None else _sha256_hex(
        source_manifest_blob_sha256, "embedded source-manifest blob SHA-256", allow_prefix=False,
    )
    # The tag path can be a v2 symlink to a manifest blob while a legacy named
    # manifest remains installed alongside it. Ollama 0.40.15 prefers v2.
    source_manifest_matches = source_layer is not None and source_blob is not None \
        and source_layer == source_blob
    match_kind = "ollama_selected_tag_manifest_bytes" if actual == api_manifest else None
    diagnostic = {
        "api_tags_digest_raw": row["digest"],
        "api_tags_digest_type": "ollama_model_tag_manifest_digest_bare_sha256_hex",
        "api_tags_digest_source": "GET /api/tags models[].digest",
        "api_tags_digest_sha256": actual,
        "api_tags_compared_artifact_type": "sha256_of_ollama_selected_tag_manifest_bytes",
        "ollama_selected_tag_manifest_path": api_manifest_path,
        "ollama_selected_tag_manifest_sha256": api_manifest,
        "legacy_named_manifest_path": installed_manifest_path,
        "legacy_named_manifest_sha256": installed_manifest,
        "installed_model_layer_digest": "sha256:" + installed_layer,
        "embedded_source_manifest_layer_digest": (
            None if source_layer is None else "sha256:" + source_layer
        ),
        "embedded_source_manifest_blob_sha256": source_blob,
        "recorded_inventory_manifest_sha256": inventory_manifest,
        "recorded_inventory_model_layer_digest": "sha256:" + inventory_layer,
        "api_tags_digest_match_kind": match_kind,
        "api_tags_matches_verified_manifest_artifact": match_kind is not None,
        "api_tags_matches_ollama_selected_tag_manifest": actual == api_manifest,
        "api_tags_matches_legacy_named_manifest": actual == installed_manifest,
        "api_tags_matches_embedded_source_manifest": (
            source_manifest_matches and actual == source_blob
        ),
        "installed_manifest_matches_recorded_inventory": installed_manifest == inventory_manifest,
        "installed_model_layer_matches_recorded_inventory": installed_layer == inventory_layer,
    }
    if match_kind is None:
        if actual == installed_layer:
            failure = "API digest matches model weight layer, not an accepted manifest artifact"
        else:
            failure = "API digest differs from the locally resolved Ollama tag manifest bytes"
        diagnostic["failure_reason"] = failure
        raise DigestMismatchError(diagnostic)
    if installed_manifest != inventory_manifest or installed_layer != inventory_layer:
        diagnostic["failure_reason"] = (
            "installed manifest or model-layer digest differs from the recorded E6 inventory; "
            "live API and file hashes are shown separately"
        )
        raise DigestMismatchError(diagnostic)
    if source_layer is not None and not source_manifest_matches:
        diagnostic["failure_reason"] = (
            "embedded source-manifest layer digest does not match its local blob SHA-256"
        )
        raise DigestMismatchError(diagnostic)
    return diagnostic


def inspect_local_manifest(model: str = MODEL) -> dict[str, Any]:
    """Resolve v2-before-legacy tag metadata and verify every digest from bytes."""
    configured_root = os.environ.get("OLLAMA_MODELS") or str(Path.home() / ".ollama/models")
    model_root = Path(configured_root).expanduser()
    if model != MODEL:
        raise ValueError(f"no local manifest path mapping is defined for {model}")
    v2_path = model_root / "manifests-v2/ollama.com/library/gemma3/12b"
    legacy_path = model_root / "manifests/registry.ollama.ai/library/gemma3/12b"
    if v2_path.exists() or v2_path.is_symlink():
        api_manifest_path = v2_path
        api_representation = "ollama_manifests_v2_tag_target_bytes"
    elif legacy_path.is_file():
        api_manifest_path = legacy_path
        api_representation = "legacy_named_manifest_file_bytes"
    else:
        raise ValueError(
            f"cannot locate Ollama tag manifest at {v2_path} or {legacy_path}; "
            "check OLLAMA_MODELS for the model store used by this Terminal"
        )

    try:
        api_raw = api_manifest_path.read_bytes()
    except OSError as exc:
        raise ValueError(f"cannot read selected Ollama tag manifest at {api_manifest_path}: {exc}") from exc
    api_manifest_sha = hashlib.sha256(api_raw).hexdigest()
    api_symlink_digest = None
    if api_manifest_path.is_symlink():
        target = api_manifest_path.resolve(strict=True)
        blobs_root = (model_root / "blobs").resolve(strict=True)
        if target.parent != blobs_root or not target.name.startswith("sha256-"):
            raise ValueError(f"Ollama v2 tag symlink points outside its expected blob store: {target}")
        api_symlink_digest = _sha256_hex(
            target.name[len("sha256-"):], "Ollama v2 tag symlink blob digest", allow_prefix=False,
        )
        if api_manifest_sha != api_symlink_digest:
            raise ValueError(
                "Ollama v2 tag manifest hash does not match its symlink blob digest: "
                f"bytes sha256:{api_manifest_sha}, target sha256:{api_symlink_digest}"
            )
    try:
        api_manifest = json.loads(api_raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"selected Ollama tag manifest is not valid UTF-8 JSON: {api_manifest_path}") from exc
    if not isinstance(api_manifest, Mapping):
        raise ValueError(f"selected Ollama tag manifest must be a JSON object: {api_manifest_path}")
    api_layers = api_manifest.get("layers")
    if not isinstance(api_layers, list):
        raise ValueError(f"selected Ollama tag manifest lacks a layers list: {api_manifest_path}")
    model_layers = [layer for layer in api_layers if isinstance(layer, Mapping)
                    and layer.get("mediaType") == "application/vnd.ollama.image.model"]
    if len(model_layers) != 1:
        raise ValueError(
            f"expected one model weight layer in selected tag manifest, found {len(model_layers)}"
        )
    layer_digest = _sha256_hex(
        model_layers[0].get("digest"), "installed manifest model-layer digest", allow_prefix=True,
    )
    source_layers = [layer for layer in api_layers if isinstance(layer, Mapping)
                     and layer.get("mediaType") == "application/vnd.docker.distribution.manifest.v2+json"]
    source_manifest = None
    if len(source_layers) > 1:
        raise ValueError("installed manifest has multiple distribution-manifest layers; digest source is ambiguous")
    if source_layers:
        source_layer = source_layers[0]
        source_digest = _sha256_hex(
            source_layer.get("digest"), "installed embedded source-manifest layer digest", allow_prefix=True,
        )
        source_blob_path = model_root / "blobs" / ("sha256-" + source_digest)
        try:
            source_blob = source_blob_path.read_bytes()
        except OSError as exc:
            raise ValueError(
                f"cannot read embedded source-manifest blob at {source_blob_path}"
            ) from exc
        actual_source_blob_sha = hashlib.sha256(source_blob).hexdigest()
        if actual_source_blob_sha != source_digest:
            raise ValueError(
                "embedded source-manifest blob hash mismatch: manifest references "
                f"sha256:{source_digest}, local bytes hash to sha256:{actual_source_blob_sha}"
            )
        declared_size = source_layer.get("size")
        if type(declared_size) is int and declared_size != len(source_blob):
            raise ValueError(
                "embedded source-manifest blob size mismatch: manifest declares "
                f"{declared_size} bytes, local blob has {len(source_blob)}"
            )
        try:
            source_json = json.loads(source_blob.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("embedded source-manifest blob is not valid UTF-8 JSON") from exc
        if not isinstance(source_json, Mapping) or source_json.get("mediaType") != \
                "application/vnd.docker.distribution.manifest.v2+json":
            raise ValueError("embedded source-manifest blob has an unexpected mediaType")
        source_manifest = {
            "layer_digest": "sha256:" + source_digest,
            "blob_sha256": actual_source_blob_sha,
            "blob_size_bytes": len(source_blob),
            "blob_path": str(source_blob_path),
        }
    # Keep legacy manifest provenance separate; in this store the Ollama v2
    # symlink shadows it for /api/tags name resolution.
    legacy_manifest_sha = None
    if legacy_path.is_file():
        legacy_manifest_sha = hashlib.sha256(legacy_path.read_bytes()).hexdigest()
        legacy_json = json.loads(legacy_path.read_text(encoding="utf-8"))
        if not isinstance(legacy_json, Mapping):
            raise ValueError(f"legacy named manifest must be a JSON object: {legacy_path}")
        legacy_layers = legacy_json.get("layers")
        if not isinstance(legacy_layers, list):
            raise ValueError(f"legacy named manifest lacks a layers list: {legacy_path}")
        legacy_source_layers = [layer for layer in legacy_layers if isinstance(layer, Mapping)
                                and layer.get("mediaType") == "application/vnd.docker.distribution.manifest.v2+json"]
        if legacy_source_layers:
            if len(legacy_source_layers) != 1:
                raise ValueError("legacy named manifest has multiple embedded source-manifest layers")
            legacy_source_digest = _sha256_hex(
                legacy_source_layers[0].get("digest"),
                "legacy embedded source-manifest layer digest", allow_prefix=True,
            )
            if source_manifest is not None and legacy_source_digest != \
                    _sha256_hex(source_manifest["layer_digest"], "selected source layer", allow_prefix=True):
                raise ValueError("legacy and selected manifests reference different source manifests")
            if source_manifest is None:
                source_blob_path = model_root / "blobs" / ("sha256-" + legacy_source_digest)
                try:
                    source_blob = source_blob_path.read_bytes()
                except OSError as exc:
                    raise ValueError(f"cannot read legacy source-manifest blob at {source_blob_path}") from exc
                source_blob_sha = hashlib.sha256(source_blob).hexdigest()
                if source_blob_sha != legacy_source_digest:
                    raise ValueError("legacy source-manifest blob does not match its referenced SHA-256")
                source_manifest = {
                    "layer_digest": "sha256:" + legacy_source_digest,
                    "blob_sha256": source_blob_sha,
                    "blob_size_bytes": len(source_blob),
                    "blob_path": str(source_blob_path),
                }
    else:
        legacy_path = None
    return {
        "manifest_path": None if legacy_path is None else str(legacy_path),
        "manifest_sha256": legacy_manifest_sha or api_manifest_sha,
        "manifest_hash_method": "SHA-256 over exact local manifest-file bytes",
        "api_manifest_path": str(api_manifest_path),
        "api_manifest_sha256": api_manifest_sha,
        "api_manifest_representation": api_representation,
        "api_manifest_symlink_blob_sha256": api_symlink_digest,
        "model_layer_digest": "sha256:" + layer_digest,
        "model_layer_media_type": "application/vnd.ollama.image.model",
        "embedded_source_manifest": source_manifest,
    }


def expected_local_model_metadata(model: str = MODEL) -> dict[str, str]:
    """Load the established digest expectations recorded in E6 config."""
    config_path = Path(__file__).with_name("config.json")
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        audit = config["local_model_inventory_audit"]
        matches = [item for item in audit["models"] if item.get("tag") == model]
        if len(matches) != 1:
            raise ValueError(f"expected exactly one configured inventory row for {model}")
        item = matches[0]
        return {
            "manifest_sha256": item["manifest_sha256"],
            "model_layer_digest": item["model_layer_digest"],
        }
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ValueError(f"cannot load expected local digest metadata from {config_path}: {exc}") from exc


def tokenizer_metadata_summary(show: Mapping[str, Any]) -> dict[str, Any]:
    info = show.get("model_info")
    if not isinstance(info, Mapping):
        raise ValueError("/api/show response lacks model_info")
    fields = {key: value for key, value in info.items()
              if isinstance(key, str) and key.startswith("tokenizer.ggml.")}
    if not fields:
        raise ValueError("/api/show response contains no tokenizer.ggml metadata")
    serialized = json.dumps(fields, sort_keys=True, ensure_ascii=False,
                            separators=(",", ":")).encode("utf-8")
    tokens = fields.get("tokenizer.ggml.tokens")
    merges = fields.get("tokenizer.ggml.merges")
    return {
        "metadata_sha256": hashlib.sha256(serialized).hexdigest(),
        "model": fields.get("tokenizer.ggml.model"),
        "pre": fields.get("tokenizer.ggml.pre"),
        "vocabulary_size": len(tokens) if isinstance(tokens, list) else None,
        "merge_count": len(merges) if isinstance(merges, list) else None,
        "metadata_fields": sorted(fields),
        "metadata_fingerprint_is_not_a_token_count": True,
        "tokenization_delegated_to": "installed Ollama llama.cpp runner for this GGUF model",
    }


def output_limit_result(reply: Mapping[str, Any], requested_limit: int) -> dict[str, Any]:
    metadata = reply.get("adapter_metadata")
    metadata = metadata if isinstance(metadata, Mapping) else {}
    output_count = reply.get("output_tokens")
    reason = metadata.get("done_reason")
    reached = reason in {"length", "max_tokens", "token_limit"} or output_count == requested_limit
    return {
        "requested_num_predict": requested_limit,
        "backend_eval_count": output_count,
        "done_reason": reason,
        "honored_under_limit_pressure": (
            type(output_count) is int and output_count <= requested_limit and reached
        ),
    }


def run_verification(probe_output_limit: int) -> dict[str, Any]:
    if type(probe_output_limit) is not int or probe_output_limit < 1:
        raise ValueError("probe_output_limit must be a positive integer")
    version = _request_json("/api/version")
    tags = _request_json("/api/tags")
    model_row = local_model_row(tags)
    expected_digests = expected_local_model_metadata()
    installed_manifest = inspect_local_manifest()
    digest_verification = verify_api_tag_digest(
        model_row,
        api_manifest_sha256=installed_manifest["api_manifest_sha256"],
        api_manifest_path=installed_manifest["api_manifest_path"],
        installed_manifest_sha256=installed_manifest["manifest_sha256"],
        installed_model_layer_digest=installed_manifest["model_layer_digest"],
        inventory_manifest_sha256=expected_digests["manifest_sha256"],
        inventory_model_layer_digest=expected_digests["model_layer_digest"],
        source_manifest_layer_digest=(
            None if installed_manifest["embedded_source_manifest"] is None else
            installed_manifest["embedded_source_manifest"]["layer_digest"]
        ),
        source_manifest_blob_sha256=(
            None if installed_manifest["embedded_source_manifest"] is None else
            installed_manifest["embedded_source_manifest"]["blob_sha256"]
        ),
        installed_manifest_path=installed_manifest["manifest_path"],
    )
    show = _request_json("/api/show", {"model": MODEL, "verbose": True})
    tokenizer = tokenizer_metadata_summary(show)

    client = OllamaModelClient(model=MODEL, generation_options={"temperature": 0.0})
    smoke_prompt = (
        'Return a JSON object with exactly one key "result" and value "E6 READY".'
    )
    prompt_preflight = client.count_prompt_tokens("E6_development_smoke", smoke_prompt)
    count_preflight = prompt_preflight.get("token_count_preflight", {})
    exact_counter_available = (
        type(prompt_preflight.get("input_tokens")) is int
        and type(prompt_preflight.get("output_tokens")) is int
        and count_preflight.get("bounded_probe_confirmed") is True
        and count_preflight.get("requested_num_predict") == 1
        and count_preflight.get("method") == "ollama_prompt_eval_count_with_num_predict_one"
    )
    smoke = client("E6_development_smoke", smoke_prompt)
    try:
        smoke_json = json.loads(smoke["raw_response"])
    except (KeyError, json.JSONDecodeError) as exc:
        raise RuntimeError("development smoke response was not valid JSON") from exc
    if smoke_json != {"result": "E6 READY"}:
        raise RuntimeError("development smoke response did not match the required JSON result")
    tokenizer_accounting_consistent = (
        exact_counter_available
        and smoke.get("input_tokens") == prompt_preflight.get("input_tokens")
        and type(smoke.get("output_tokens")) is int
        and smoke.get("total_tokens") == smoke.get("input_tokens", 0) + smoke.get("output_tokens", 0)
    )

    limited = client.call_with_token_limit(
        "E6_development_output_limit_probe",
        'Return a JSON object with key "items" and an array of 256 distinct short strings. '
        "Continue until all 256 are present.",
        max_output_tokens=probe_output_limit,
    )
    limit_check = output_limit_result(limited, probe_output_limit)
    if not limit_check["honored_under_limit_pressure"]:
        raise RuntimeError(
            "output-limit probe was inconclusive or exceeded num_predict: "
            + json.dumps(limit_check, sort_keys=True)
        )

    try:
        e6_config = json.loads(Path(__file__).with_name("config.json").read_text(encoding="utf-8"))
        budget_cap = e6_config.get("inference_budget", {}).get("tokens_per_input_set_arm")
        protocol = e6_config.get("protocol", {})
        execution_gate_open = protocol.get("execution_authorized") is True
    except (OSError, json.JSONDecodeError):
        budget_cap = None
        execution_gate_open = False
    budget_ready = (
        exact_counter_available and tokenizer_accounting_consistent
        and limit_check["honored_under_limit_pressure"]
        and type(budget_cap) is int and budget_cap > 0
        and execution_gate_open
    )

    return {
        "scope": "development_only_no_experiment",
        "model": MODEL,
        "ollama_version": version.get("version"),
        "digest_verification": digest_verification,
        "installed_manifest": installed_manifest,
        "ollama_model_size_bytes": model_row.get("size"),
        "model_details": model_row.get("details"),
        "tokenizer": tokenizer,
        "tokenizer_counter_id": (
            f"ollama-runner:{digest_verification['api_tags_digest_sha256']}:{tokenizer['metadata_sha256']}"
        ),
        "prompt_token_count_preflight": {
            "input_tokens": prompt_preflight.get("input_tokens"),
            "output_tokens": prompt_preflight.get("output_tokens"),
            "requested_num_predict": count_preflight.get("requested_num_predict"),
            "bounded_probe_confirmed": count_preflight.get("bounded_probe_confirmed"),
            "method": count_preflight.get("method"),
            "rendering": "same Ollama /api/generate JSON-mode model template, tokenizer, and special-token path as generation; one-token probe completion is discarded",
        },
        "smoke": {
            "passed": True,
            "result": smoke_json["result"],
            "prompt_eval_count": smoke.get("input_tokens"),
            "eval_count": smoke.get("output_tokens"),
            "done_reason": smoke.get("adapter_metadata", {}).get("done_reason"),
        },
        "output_limit_probe": limit_check,
        "exact_token_counter_available": exact_counter_available,
        "tokenizer_accounting_consistent_with_e6_preflight": tokenizer_accounting_consistent,
        "tokenizer_accounting_note": (
            "PerArmTokenBudget charges the bounded one-token prompt-evaluation probe "
            "(including its actual eval_count) and the generation prompt_eval_count/eval_count "
            "separately; prompt counts must agree."
        ),
        "configured_arm_token_cap": budget_cap,
        "protocol_execution_gate_open": execution_gate_open,
        "e6_ready_for_budgeted_execution": budget_ready,
    }


def _write_verification_report_exclusive(path: Path, report: Mapping[str, Any]) -> None:
    """Persist actual output once; never overwrite previous verification evidence."""
    target = Path(path).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--probe-output-limit", type=int, required=True,
        help="temporary development probe ceiling; choose a small positive value (not an E6 experimental cap)",
    )
    parser.add_argument(
        "--output", type=Path, required=True,
        help="new JSON report path; existing files are never overwritten",
    )
    args = parser.parse_args(argv)
    output_path = args.output.expanduser()
    if output_path.exists():
        parser.error(f"verification output already exists; choose a new path: {output_path}")
    report: dict[str, Any]
    try:
        result = run_verification(args.probe_output_limit)
        runtime_checks_passed = bool(
            isinstance(result.get("digest_verification"), Mapping)
            and result["digest_verification"].get("api_tags_matches_verified_manifest_artifact") is True
            and result.get("exact_token_counter_available") is True
            and result.get("tokenizer_accounting_consistent_with_e6_preflight") is True
            and isinstance(result.get("smoke"), Mapping)
            and result["smoke"].get("passed") is True
            and isinstance(result.get("output_limit_probe"), Mapping)
            and result["output_limit_probe"].get("honored_under_limit_pressure") is True
        )
        report = {
            "verification_status": "verified_local_runtime" if runtime_checks_passed else "partial",
            "verification_timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "scope": "development_only_no_experiment",
            "probe_output_limit": args.probe_output_limit,
            **result,
            "tokenizer_metadata_fingerprint_sha256": (
                result.get("tokenizer", {}).get("metadata_sha256")
                if isinstance(result.get("tokenizer"), Mapping) else None
            ),
            "e6_ready_for_budgeted_execution": result.get("e6_ready_for_budgeted_execution") is True,
        }
    except DigestMismatchError as exc:
        report = {
            "verification_status": "failed",
            "verification_timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "scope": "development_only_no_experiment",
            "error": str(exc),
            "digest_diagnostic": exc.diagnostic,
            "exact_token_counter_available": False,
            "tokenizer_accounting_consistent_with_e6_preflight": False,
            "e6_ready_for_budgeted_execution": False,
        }
    except Exception as exc:
        report = {
            "verification_status": "failed",
            "verification_timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "scope": "development_only_no_experiment",
            "probe_output_limit": args.probe_output_limit,
            "error": str(exc),
            "exact_token_counter_available": False,
            "tokenizer_accounting_consistent_with_e6_preflight": False,
            "e6_ready_for_budgeted_execution": False,
        }
    report["report_path"] = str(output_path)
    try:
        _write_verification_report_exclusive(output_path, report)
    except FileExistsError:
        parser.error(f"verification output appeared during run; report not overwritten: {output_path}")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 2 if report.get("verification_status") == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
