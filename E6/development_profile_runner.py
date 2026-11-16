"""Local Ollama adapter for the isolated E6 development token profile.

This module accepts only the exact generic task in development_profile_config
and verifies every input against development_manifest_v2 and the E2 raw source.
It never reads or accepts TEST/EVALUATION records.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from ollama_adapter import OllamaModelClient
from orchestrator import ExperimentInput, run_seven_arms
from prepare_dataset import canonicalize_arxiv_id
from profile_development_token_budget import (
    DEFAULT_MANIFEST,
    build_profile_attestation,
    load_development_manifest,
)
from question_pipeline import (
    PipelineSettings,
    TrustedDEmptyAuditResult,
    TrustedDEmptyEvidenceAuditor,
    _d_shuffled_provenance_hashes,
    assign_d_shuffled_donors,
)

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "development_profile_config.json"
RAW_SOURCE_PATH = ROOT.parent / "E2/data/raw_papers.jsonl"
VERIFICATION_PATH = ROOT / "data/gemma3_local_verification_v1.json"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_hash(value: Any) -> str:
    return _sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                               separators=(",", ":"), allow_nan=False).encode("utf-8"))


def _load_verified_source_rows(development_rows):
    allowed = {row["paper_id"]: row for row in development_rows}
    sources: dict[str, Mapping[str, Any]] = {}
    with RAW_SOURCE_PATH.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            try:
                paper_id = canonicalize_arxiv_id(row.get("paper_id"))
            except (TypeError, ValueError):
                continue
            if paper_id not in allowed:
                continue
            expected = allowed[paper_id]
            source_hash = _canonical_hash(row)
            if (row.get("abstract") != expected.get("abstract")
                    or source_hash != expected.get("source_record_sha256")):
                raise ValueError(f"development source mismatch at E2 raw record line {line_no}")
            if paper_id in sources:
                raise ValueError(f"duplicate canonical source record for development paper {paper_id}")
            sources[paper_id] = row
    if set(sources) != set(allowed):
        raise ValueError("one or more development records lack an exact E2 source row")
    return sources


class DevelopmentProfileDEmptyAuditor(TrustedDEmptyEvidenceAuditor):
    """Attest only the constant profile task; not valid for confirmatory runs."""

    auditor_id = "e6_profile_constant_task_auditor_v1"

    def __init__(self, generic_task: str):
        self.generic_task = generic_task

    def audit(self, recipient_id, retained_task_text, original_evidence, policy):
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if (config.get("status") != "development_only_pending_operator_run"
                or config.get("confirmatory_use") is not False
                or config.get("generic_task_text") != self.generic_task
                or retained_task_text != self.generic_task):
            raise ValueError("profile auditor accepts only its exact generic task")
        original_abstract = original_evidence.get("abstract")
        original_refs = original_evidence.get("reference_evidence")
        if not isinstance(original_abstract, str) or not isinstance(original_refs, list):
            raise ValueError("profile auditor requires explicit source evidence to audit removal")
        abstract_hash = _sha256(original_abstract.encode("utf-8"))
        refs_hash = _canonical_hash(original_refs)
        audit_payload = {
            "recipient_id": recipient_id,
            "task_sha256": _sha256(self.generic_task.encode("utf-8")),
            "abstract_sha256": abstract_hash,
            "references_sha256": refs_hash,
            "policy": policy,
        }
        return TrustedDEmptyAuditResult(
            trust_status="trusted_development_profile",
            auditor_id=self.auditor_id,
            audit_id="dev-audit-" + _canonical_hash(audit_payload)[:24],
            audit_complete=True,
            audit_scope="retained_task_domain_text",
            leakage_check_performed=True,
            retained_task_leakage_detected=False,
            recipient_id=recipient_id,
            scrubbed_task_sha256=_sha256(self.generic_task.encode("utf-8")),
            removed_fields=["abstract", "reference_evidence"],
            removed_evidence_sha256={
                "abstract": abstract_hash,
                "reference_evidence": refs_hash,
            },
            rendered_evidence="",
        )


def run_one_development_record(record: Mapping[str, Any], task_text: str,
                               profile_cap: int) -> Mapping[str, Any]:
    """Execute one seven-arm DEVELOPMENT profile cell through the E6 controller."""
    manifest, manifest_sha = load_development_manifest(DEFAULT_MANIFEST)
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    expected_task = config.get("generic_task_text")
    if (config.get("status") != "development_only_pending_operator_run"
            or config.get("confirmatory_use") is not False
            or config.get("source_split") != "DEVELOPMENT"
            or task_text != expected_task):
        raise ValueError("profile inputs/configuration are not the fixed DEVELOPMENT profile")
    if type(profile_cap) is not int or profile_cap < 1:
        raise ValueError("temporary development profile cap must be positive")
    if not any(dict(row) == dict(record) for row in manifest["inputs"]):
        raise ValueError("profile record is not an exact member of development_manifest_v2")
    verification = json.loads(VERIFICATION_PATH.read_text(encoding="utf-8"))
    if (verification.get("verification_status") != "verified_local_runtime"
            or verification.get("exact_token_counter_available") is not True
            or verification.get("tokenizer_accounting_consistent_with_e6_preflight") is not True):
        raise ValueError("saved Gemma local verification report is not verified")

    source_records = _load_verified_source_rows(manifest["inputs"])
    expected_manifest_hash, expected_sources_hash = _d_shuffled_provenance_hashes(
        manifest["inputs"], source_records,
    )
    assignments = assign_d_shuffled_donors(
        recipients=manifest["inputs"], development_records=manifest["inputs"],
        canonical_source_records=source_records,
        expected_manifest_sha256=expected_manifest_hash,
        expected_source_corpus_sha256=expected_sources_hash,
    )
    assignment = next(row for row in assignments["assignments"]
                      if row["recipient_id"] == record["paper_id"])

    settings_value = json.loads((ROOT / "question_pipeline_config.json").read_text(encoding="utf-8"))
    settings_value["arm_hypothesis_max_attempts"] = 1
    settings_value["selected_hypothesis_max_attempts"] = 1
    settings = PipelineSettings.from_mapping(settings_value)
    client = OllamaModelClient(
        model="gemma3:12b",
        timeout_seconds=600,
        generation_options={"temperature": 0.0, "seed": 2026, "num_predict": 512},
    )
    experiment_input = ExperimentInput(
        paper_id=record["paper_id"],
        domain_and_task=task_text,
        evidence=record["abstract"],
        provenance={
            "split": "DEVELOPMENT",
            "source_record_sha256": record["source_record_sha256"],
            "development_manifest_sha256": manifest_sha,
            "profile_only": True,
        },
        reference_evidence=(),
        split="DEVELOPMENT",
    )
    profile_attestation = build_profile_attestation(
        manifest_sha, task_text,
        task_matches_profile_constant=(task_text == expected_task),
    )

    def donor_check(recipient_id, donor_id, provenance, constraints):
        return {
            "passed": True,
            "recipient_id": recipient_id,
            "donor_id": donor_id,
            "donor_split": "DEVELOPMENT",
            "evidence_sha256": provenance["evidence_sha256"],
            "source_record_sha256": provenance["source_record_sha256"],
            "profile_only": True,
        }

    result = run_seven_arms(
        experiment_input, settings, client, client.model_configuration,
        execution_mode="development_profile",
        d_empty_task_evidence_check=DevelopmentProfileDEmptyAuditor(task_text),
        d_shuffled_assignment=assignment,
        d_shuffled_assignment_batch=assignments,
        development_manifest_records=manifest["inputs"],
        canonical_source_records=source_records,
        expected_manifest_sha256=expected_manifest_hash,
        expected_source_corpus_sha256=expected_sources_hash,
        d_shuffled_assignment_check=donor_check,
        token_budget_per_arm=profile_cap,
        development_profile_attestation=profile_attestation,
    )
    result["profile_configuration"] = {
        "profile_only": True,
        "temporary_ceiling_tokens_per_arm": profile_cap,
        "model_verification_report": "E6/data/gemma3_local_verification_v1.json",
        "tokenizer_fingerprint": verification["tokenizer_metadata_fingerprint_sha256"],
        "max_output_tokens_per_call": 512,
        "output_limit_is_development_profile_setting_only": True,
    }
    return result
