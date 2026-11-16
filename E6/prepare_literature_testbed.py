"""Read-only eligibility and completeness interfaces for E6 literature inputs.

This module validates externally assembled candidate records in memory. It does
not retrieve citations, sample papers, write datasets, extract annotations, or
freeze either exploratory or confirmatory data.
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.parse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from prepare_dataset import canonicalize_arxiv_id, canonicalize_records

MINIMUM_INPUT_SETS = 100
MINIMUM_REFERENCES = 10
REQUIRED_MANUAL_CHECKS = 20
REFERENCE_FIELD_HINTS = ("ref", "citation", "bibliograph")
ROOT = Path(__file__).resolve().parent
DEFAULT_DEVELOPMENT_MANIFEST = ROOT / "data" / "development_manifest_v2.json"
OPENALEX_WORK_ID_RE = re.compile(r"^W[0-9]+$", re.IGNORECASE)


def canonical_literature_reference_id(value: Any) -> str:
    """Canonicalize an arXiv ID or stable OpenAlex Work ID without fuzzy matching."""
    try:
        return canonicalize_arxiv_id(value)
    except (TypeError, ValueError):
        pass
    if not isinstance(value, str) or not value.strip():
        raise ValueError("reference paper_id must be an arXiv ID or OpenAlex Work ID")
    raw = value.strip()
    if raw.lower().startswith("openalex:"):
        raw = raw.split(":", 1)[1]
    elif "://" in raw:
        parsed = urllib.parse.urlparse(raw)
        if (parsed.hostname or "").lower() not in {"openalex.org", "www.openalex.org"}:
            raise ValueError("reference URL is not an OpenAlex Work URL")
        raw = parsed.path.strip("/").split("/")[-1]
    if OPENALEX_WORK_ID_RE.fullmatch(raw):
        return "openalex:" + raw.upper()
    raise ValueError("reference paper_id must be an exact arXiv or OpenAlex Work ID")


def parse_utc_datetime(value: Any) -> datetime | None:
    """Parse an ISO timestamp only when it includes a timezone/UTC offset."""
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def format_utc_datetime(value: datetime | None) -> str | None:
    """Render parsed timestamps in one stable UTC representation."""
    return value.isoformat().replace("+00:00", "Z") if value is not None else None


def _sha256_text(value: Any) -> str | None:
    """Hash exact UTF-8 text while leaving unavailable/non-text evidence unrepresented."""
    if not isinstance(value, str):
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


SOURCE_RECORD_HASH_SERIALIZATION = (
    "UTF-8 JSON via json.dumps(ensure_ascii=False, sort_keys=True, "
    "separators=(',', ':'), allow_nan=False)"
)


def _source_record_hash(source_record: Any) -> dict[str, Any]:
    """Hash a retained source record using stable compact JSON serialization."""
    if source_record is None:
        return {"status": "missing", "sha256": None}
    if not isinstance(source_record, Mapping):
        return {"status": "invalid", "sha256": None}
    try:
        canonical_json = json.dumps(
            dict(source_record), ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        )
    except (TypeError, ValueError):
        return {"status": "unserializable", "sha256": None}
    return {
        "status": "hashed",
        "sha256": hashlib.sha256(canonical_json.encode("utf-8")).hexdigest(),
    }


def validate_literature_input_set(
    candidate: Mapping[str, Any], generator_training_cutoff_utc: str | None,
    *, minimum_references: int = MINIMUM_REFERENCES,
) -> dict[str, Any]:
    """Check target date and >=10 unique reference papers with nonempty abstracts.

    Invalid references remain listed in the result. No target/reference is
    silently removed or substituted.
    """
    errors: list[str] = []
    if not isinstance(candidate, Mapping):
        return {"status": "invalid", "errors": ["candidate must be an object"]}
    if type(minimum_references) is not int or minimum_references < 1:
        return {"status": "invalid", "errors": ["minimum_references must be a positive integer"]}
    input_set_id = candidate.get("input_set_id")
    if not isinstance(input_set_id, str) or not input_set_id.strip():
        errors.append("input_set_id is required")
    if candidate.get("reference_links_verified") is not True:
        errors.append("target-to-reference citation links are not verified")
    if not isinstance(candidate.get("reference_link_provenance"), Mapping) or not candidate.get("reference_link_provenance"):
        errors.append("reference-link provenance is required")

    target = candidate.get("target")
    if not isinstance(target, Mapping):
        errors.append("target must be an object")
        target = {}
    target_id = target.get("paper_id")
    canonical_target_id = None
    try:
        canonical_target_id = canonicalize_arxiv_id(target_id)
    except (TypeError, ValueError):
        errors.append("target paper_id must be a valid arXiv ID")
    if not isinstance(target.get("abstract"), str) or not target.get("abstract", "").strip():
        errors.append("target abstract is missing or empty")

    cutoff = parse_utc_datetime(generator_training_cutoff_utc)
    target_date = parse_utc_datetime(target.get("published"))
    if generator_training_cutoff_utc is None:
        errors.append("generator training cutoff is unresolved")
    elif cutoff is None:
        errors.append("generator training cutoff is missing, invalid, or lacks timezone")
    if not target.get("published"):
        errors.append("target published timestamp is missing")
    elif target_date is None:
        errors.append("target published timestamp is invalid or lacks timezone")
    elif cutoff is not None and target_date <= cutoff:
        errors.append("target was not posted strictly after the generator training cutoff")

    references = candidate.get("references")
    if not isinstance(references, list):
        errors.append("references must be a list")
        references = []
    seen: set[str] = set()
    excluded_reference_ids: set[str] = set()
    excluded_values = candidate.get("excluded_reference_paper_ids", [])
    if not isinstance(excluded_values, (list, tuple, set)):
        errors.append("excluded_reference_paper_ids must be a sequence when supplied")
        excluded_values = []
    for value in excluded_values:
        try:
            excluded_reference_ids.add(canonicalize_arxiv_id(value))
        except (TypeError, ValueError):
            errors.append("excluded_reference_paper_ids contains an invalid arXiv ID")
    duplicate_reference_ids: list[str] = []
    invalid_references: list[dict[str, Any]] = []
    eligibility_errors_for_references: list[dict[str, Any]] = []
    valid_reference_ids: list[str] = []
    references_with_abstract: list[str] = []
    references_without_abstract: list[str] = []
    for index, ref in enumerate(references):
        if not isinstance(ref, Mapping):
            detail = {"index": index, "reason": "reference must be an object"}
            invalid_references.append(detail)
            eligibility_errors_for_references.append(detail)
            continue
        try:
            ref_id = canonical_literature_reference_id(ref.get("paper_id"))
        except (TypeError, ValueError) as exc:
            detail = {"index": index, "reason": f"invalid paper_id: {exc}"}
            invalid_references.append(detail)
            eligibility_errors_for_references.append(detail)
            continue
        is_arxiv_id = not ref_id.startswith("openalex:")
        if is_arxiv_id and ref_id == canonical_target_id:
            detail = {"index": index, "paper_id": ref_id,
                      "reason": "target paper cannot count as its own reference"}
            invalid_references.append(detail)
            eligibility_errors_for_references.append(detail)
            continue
        if is_arxiv_id and ref_id in excluded_reference_ids:
            detail = {"index": index, "paper_id": ref_id,
                      "reason": "reference is in an excluded development/test set"}
            invalid_references.append(detail)
            eligibility_errors_for_references.append(detail)
            continue
        if ref_id in seen:
            duplicate_reference_ids.append(ref_id)
            invalid_references.append({"index": index, "paper_id": ref_id,
                                       "reason": "duplicate canonical reference ID"})
            continue
        seen.add(ref_id)
        valid_reference_ids.append(ref_id)
        abstract = ref.get("abstract")
        if isinstance(abstract, str) and abstract.strip():
            references_with_abstract.append(ref_id)
        else:
            references_without_abstract.append(ref_id)
            invalid_references.append({"index": index, "paper_id": ref_id,
                                       "reason": "reference abstract is missing or empty"})

    if len(references_with_abstract) < minimum_references:
        errors.append(
            f"only {len(references_with_abstract)} unique references have abstracts; "
            f"at least {minimum_references} are required"
        )
    if eligibility_errors_for_references:
        errors.append(
            f"{len(eligibility_errors_for_references)} reference entries have invalid IDs, "
            "self-links, or excluded IDs"
        )

    return {
        "status": "eligible_candidate" if not errors else "ineligible_or_unresolved",
        "input_set_id": input_set_id,
        "target_paper_id": target_id,
        "canonical_target_paper_id": canonical_target_id,
        "target_published_utc": format_utc_datetime(target_date) or target.get("published"),
        "training_cutoff_utc": format_utc_datetime(cutoff) or generator_training_cutoff_utc,
        "target_post_cutoff": (
            target_date > cutoff if target_date is not None and cutoff is not None else None
        ),
        "reference_entry_count": len(references),
        "unique_valid_reference_id_count": len(valid_reference_ids),
        "unique_reference_with_abstract_count": len(references_with_abstract),
        "references_without_abstract_count": len(references_without_abstract),
        "references_without_abstract": references_without_abstract,
        "duplicate_reference_ids": duplicate_reference_ids,
        "invalid_references": invalid_references,
        "errors": errors,
    }


def build_candidate_input_set(
    input_set_id: str, target: Mapping[str, Any], references: Sequence[Mapping[str, Any]],
    generator_training_cutoff_utc: str | None, *, source_provenance: Mapping[str, Any],
    reference_links_verified: bool | None = None,
    reference_link_provenance: Mapping[str, Any] | None = None,
    excluded_reference_paper_ids: Sequence[str] = (),
) -> dict[str, Any]:
    """Construct an in-memory candidate while retaining source rows and audit status."""
    target_value = dict(target) if isinstance(target, Mapping) else target
    if isinstance(references, (list, tuple)):
        reference_values = [dict(row) if isinstance(row, Mapping) else row for row in references]
    else:
        reference_values = references
    candidate = {
        "input_set_id": input_set_id,
        "target": target_value,
        "references": reference_values,
        "reference_links_verified": reference_links_verified,
        "reference_link_provenance": (
            dict(reference_link_provenance)
            if isinstance(reference_link_provenance, Mapping) else reference_link_provenance
        ),
        "excluded_reference_paper_ids": list(excluded_reference_paper_ids),
        "provenance": dict(source_provenance) if isinstance(source_provenance, Mapping) else source_provenance,
        "exposure_status": "unverified; exclusion from E2 focal set is not proof of no prior exposure",
    }
    target_abstract = target_value.get("abstract") if isinstance(target_value, Mapping) else None
    reference_abstract_hashes = []
    if isinstance(reference_values, list):
        for index, reference in enumerate(reference_values):
            reference_id = None
            abstract = None
            if isinstance(reference, Mapping):
                abstract = reference.get("abstract")
                try:
                    reference_id = canonical_literature_reference_id(reference.get("paper_id"))
                except (TypeError, ValueError):
                    pass
            reference_abstract_hashes.append({
                "reference_index": index,
                "canonical_paper_id": reference_id,
                "abstract_sha256": _sha256_text(abstract),
            })
    candidate["evidence_hashes"] = {
        "algorithm": "sha256",
        "text_encoding": "utf-8",
        "target_abstract_sha256": _sha256_text(target_abstract),
        "reference_abstracts": reference_abstract_hashes,
    }
    reference_source_hashes = []
    if isinstance(reference_values, list):
        for index, reference in enumerate(reference_values):
            source_record = reference.get("source_record") if isinstance(reference, Mapping) else None
            source_hash = _source_record_hash(source_record)
            reference_id = None
            if isinstance(reference, Mapping):
                try:
                    reference_id = canonical_literature_reference_id(reference.get("paper_id"))
                except (TypeError, ValueError):
                    pass
            reference_source_hashes.append({
                "reference_index": index,
                "canonical_paper_id": reference_id,
                **source_hash,
            })
    candidate["source_record_hashes"] = {
        "serialization": SOURCE_RECORD_HASH_SERIALIZATION,
        "target": _source_record_hash(
            target_value.get("source_record") if isinstance(target_value, Mapping) else None
        ),
        "references": reference_source_hashes,
    }
    candidate["eligibility_audit"] = validate_literature_input_set(
        candidate, generator_training_cutoff_utc,
    )
    return candidate


def audit_candidate_input_sets(
    candidates: Sequence[Mapping[str, Any]], generator_training_cutoff_utc: str | None,
) -> dict[str, Any]:
    """Count complete candidates and describe reference overlap without resolving reuse policy."""
    audits = [validate_literature_input_set(row, generator_training_cutoff_utc) for row in candidates]
    raw_input_set_ids = [row.get("input_set_id") for row in candidates if isinstance(row, Mapping)]
    valid_input_set_ids = [value for value in raw_input_set_ids
                           if isinstance(value, str) and value.strip()]
    targets = []
    for row in candidates:
        target = row.get("target") if isinstance(row, Mapping) else None
        try:
            targets.append(canonicalize_arxiv_id(target.get("paper_id")))
        except (AttributeError, TypeError, ValueError):
            pass
    input_counts, target_counts = Counter(valid_input_set_ids), Counter(targets)
    duplicate_input_ids = sorted(key for key, count in input_counts.items() if count > 1)
    duplicate_target_ids = sorted(key for key, count in target_counts.items() if count > 1)
    eligible = [audit for audit in audits if audit["status"] == "eligible_candidate"]
    eligible_ids = {audit["input_set_id"] for audit in eligible
                    if isinstance(audit.get("input_set_id"), str)}
    eligible_targets = {audit["canonical_target_paper_id"] for audit in eligible
                        if audit.get("canonical_target_paper_id")}
    eligible_count = min(len(eligible_ids), len(eligible_targets))
    reference_uses: dict[str, set[str]] = defaultdict(set)
    for row in candidates:
        if not isinstance(row, Mapping):
            continue
        input_set_id = row.get("input_set_id")
        references = row.get("references")
        if not isinstance(input_set_id, str) or not input_set_id.strip() or not isinstance(references, list):
            continue
        for reference in references:
            if not isinstance(reference, Mapping):
                continue
            try:
                reference_id = canonical_literature_reference_id(reference.get("paper_id"))
            except (TypeError, ValueError):
                continue
            reference_uses[reference_id].add(input_set_id)
    reused_references = [
        {"paper_id": paper_id, "input_set_ids": sorted(input_set_ids)}
        for paper_id, input_set_ids in sorted(reference_uses.items())
        if len(input_set_ids) > 1
    ]
    return {
        "status": "minimum_met" if eligible_count >= MINIMUM_INPUT_SETS else "minimum_not_met",
        "read_only": True,
        "input_sets_selected": False,
        "input_sets_frozen": False,
        "candidate_input_set_count": len(candidates),
        "unique_input_set_id_count": len(input_counts),
        "invalid_input_set_id_count": len(raw_input_set_ids) - len(valid_input_set_ids),
        "eligible_candidate_input_set_count": eligible_count,
        "eligible_unique_input_set_id_count": len(eligible_ids),
        "eligible_unique_target_paper_count": len(eligible_targets),
        "minimum_required_input_sets": MINIMUM_INPUT_SETS,
        "candidate_target_paper_count": len(target_counts),
        "duplicate_input_set_ids": duplicate_input_ids,
        "duplicate_target_paper_ids": duplicate_target_ids,
        "reference_reuse_audit_status": "descriptive_only_policy_unresolved",
        "shared_reference_paper_count": len(reused_references),
        "shared_reference_papers": reused_references,
        "per_candidate_audits": audits,
    }


def audit_manual_check_coverage(review_records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Count explicitly completed checks without selecting cases or judging them."""
    completed = [row for row in review_records
                 if isinstance(row, Mapping) and row.get("manual_check_completed") is True
                 and isinstance(row.get("input_set_id"), str) and row["input_set_id"].strip()]
    completed_ids = sorted({row["input_set_id"] for row in completed})
    duplicates = sorted(key for key, count in Counter(
        row["input_set_id"] for row in completed
    ).items() if count > 1)
    return {
        "required_unique_cases": REQUIRED_MANUAL_CHECKS,
        "completed_review_records": len(completed),
        "completed_unique_input_sets": len(completed_ids),
        "duplicate_review_records_for_input_sets": duplicates,
        "manual_check_requirement_met": len(completed_ids) >= REQUIRED_MANUAL_CHECKS,
        "input_set_ids": completed_ids,
        "case_selection_and_adjudication_policy": "unresolved; no cases selected by this function",
    }


def audit_raw_corpus(
    raw_rows: Sequence[Mapping[str, Any]], focal_ids: Iterable[str],
    generator_training_cutoff_utc: str | None,
) -> dict[str, Any]:
    """Metadata-only audit of corpus support for the literature-testbed rules."""
    safe_rows = [row for row in raw_rows if isinstance(row, Mapping)]
    invalid_raw_rows = len(raw_rows) - len(safe_rows)
    aggregated = canonicalize_records(safe_rows)
    papers = aggregated["papers"]
    raw_ids = set(papers)
    focal: set[str] = set()
    invalid_focal_ids: list[Any] = []
    for value in focal_ids:
        try:
            focal.add(canonicalize_arxiv_id(value))
        except (TypeError, ValueError):
            invalid_focal_ids.append(value)
    eligible_ids = raw_ids - focal
    reference_keys = sorted({
        key for row in safe_rows for key in row
        if isinstance(key, str) and any(hint in key.lower() for hint in REFERENCE_FIELD_HINTS)
    })
    reference_rows = [row for row in safe_rows if any(key in row for key in reference_keys)]
    valid_dates = {}
    missing_dates = 0
    invalid_dates = 0
    empty_abstract_ids = []
    for paper_id, entry in papers.items():
        row = entry["canonical_record"]
        if row is None:
            continue
        if not entry["has_nonempty_abstract"]:
            empty_abstract_ids.append(paper_id)
        value = row.get("published")
        parsed = parse_utc_datetime(value)
        if not value:
            missing_dates += 1
        elif parsed is None:
            invalid_dates += 1
        else:
            valid_dates[paper_id] = parsed
    cutoff = parse_utc_datetime(generator_training_cutoff_utc)
    post_cutoff_count = (
        sum(valid_dates[paper_id] > cutoff for paper_id in eligible_ids if paper_id in valid_dates)
        if cutoff is not None else None
    )
    return {
        "read_only": True,
        "sampled": False,
        "split_created": False,
        "dataset_frozen": False,
        "raw_record_count": len(raw_rows),
        "invalid_non_object_raw_row_count": invalid_raw_rows,
        "invalid_raw_record_count": invalid_raw_rows + len(aggregated["invalid_rows"]),
        "invalid_focal_id_count": len(invalid_focal_ids),
        "invalid_focal_ids": invalid_focal_ids,
        "unique_canonical_paper_count": len(raw_ids),
        "unique_excluded_focal_count_present": len(raw_ids & focal),
        "candidate_paper_count_after_focal_exclusion": len(eligible_ids),
        "outside_focal_exposure_status": "unverified; not evidence of never having been seen",
        "duplicate_canonical_id_group_count": len(aggregated["duplicate_id_groups"]),
        "duplicate_raw_row_excess": sum(papers[pid]["record_count"] - 1
                                         for pid in aggregated["duplicate_id_groups"]),
        "exact_duplicate_record_group_count": aggregated["exact_duplicate_record_groups"],
        "same_pool_duplicate_id_count": len(aggregated["same_pool_duplicate_ids"]),
        "conflicting_metadata_paper_count": sum(bool(p["conflicting_core_fields"]) for p in papers.values()),
        "canonical_papers_without_abstract_count": len(empty_abstract_ids),
        "missing_published_timestamp_count": missing_dates,
        "invalid_or_timezone_uncertain_published_timestamp_count": invalid_dates,
        "published_year_min": min((value.year for value in valid_dates.values()), default=None),
        "published_year_max": max((value.year for value in valid_dates.values()), default=None),
        "generator_training_cutoff_utc": format_utc_datetime(cutoff) or generator_training_cutoff_utc,
        "eligible_papers_post_cutoff_count": post_cutoff_count,
        "reference_like_fields": reference_keys,
        "records_with_reference_like_fields": len(reference_rows),
        "input_sets_constructable_from_embedded_references": 0 if not reference_rows else None,
        "minimum_100_input_sets_supported_by_embedded_reference_data": (
            False if not reference_rows else None
        ),
        "minimum_references_with_abstracts_required_per_input_set": MINIMUM_REFERENCES,
        "minimum_input_sets_required": MINIMUM_INPUT_SETS,
        "manual_extraction_checks_required": REQUIRED_MANUAL_CHECKS,
        "manual_extraction_checks_completed": 0,
        "references_not_embedded": not bool(reference_keys),
    }


def acquire_openalex_reference_candidate(
    adapter: Any,
    target_response: Mapping[str, Any],
    target_record: Mapping[str, Any],
    *,
    input_set_id: str,
    generator_training_cutoff_utc: str | None,
    reference_links_verified: bool = False,
    reference_link_provenance: Mapping[str, Any] | None = None,
    excluded_reference_paper_ids: Sequence[str] = (),
) -> dict[str, Any]:
    """
    Retrieve reference metadata for one target.

    Development-only: does not select, freeze, or approve an input set.
    DOI/OpenAlex-only references are preserved but do not satisfy the
    existing arXiv-only eligibility validator.
    """
    from citation_sources import (
        fetch_openalex_works_batched,
        normalize_openalex_work,
        openalex_reference_records,
        openalex_record_matches_arxiv_id,
    )

    if not isinstance(target_response, Mapping):
        raise TypeError("target_response must be a mapping")

    if not isinstance(target_record, Mapping):
        raise TypeError("target_record must be a mapping")

    target_source_record = target_response.get("raw_response", target_response)
    identifiers = openalex_reference_records(target_response)
    openalex_ids = [row["openalex_id"] for row in identifiers]

    retrieval = fetch_openalex_works_batched(adapter, openalex_ids)

    reference_retrieval_by_id: dict[str, dict[str, Any]] = {}
    retrieval_responses = retrieval.get("responses", [])
    if isinstance(retrieval_responses, list):
        for batch_response in retrieval_responses:
            if not isinstance(batch_response, Mapping):
                continue
            body = batch_response.get("raw_response")
            results = body.get("results", []) if isinstance(body, Mapping) else []
            batch_provenance = {
                "source": batch_response.get("source", "OpenAlex"),
                "api_version": batch_response.get("api_version"),
                "request_url": batch_response.get("request_url"),
                "retrieved_at_utc": batch_response.get("retrieved_at_utc"),
                "http_status": batch_response.get("http_status"),
                "cache_hit": batch_response.get("cache_hit"),
                "response_sha256": _source_record_hash(body),
            }
            for result in results if isinstance(results, list) else []:
                if isinstance(result, Mapping) and isinstance(result.get("id"), str):
                    reference_retrieval_by_id[result["id"].rsplit("/", 1)[-1]] = batch_provenance

    references = []
    records_by_id = retrieval["records_by_openalex_id"]

    for identifier in identifiers:
        openalex_id = identifier["openalex_id"]
        source_record = records_by_id.get(openalex_id.rsplit("/", 1)[-1])

        if source_record is None:
            references.append({
                **identifier,
                "metadata_status": "not_retrieved",
                "missing_reason": "OpenAlex work record not returned",
            })
            continue

        normalized = normalize_openalex_work(source_record)
        source_ids = normalized.get("source_identifiers") or {}
        arxiv_id = normalized.get("arxiv_id")
        openalex_id = source_record.get("id")
        reference_paper_id = arxiv_id or canonical_literature_reference_id(openalex_id)
        retrieval_provenance = reference_retrieval_by_id.get(
            openalex_id.rsplit("/", 1)[-1] if isinstance(openalex_id, str) else "", {}
        )

        references.append({
            **identifier,
            **normalized,
            "paper_id": reference_paper_id,
            "doi": source_ids.get("doi"),
            "source_url": openalex_id,
            "metadata_retrieval_provenance": dict(retrieval_provenance),
            "metadata_status": (
                "retrieved_with_abstract"
                if normalized.get("abstract")
                else "retrieved_without_abstract"
            ),
        })

    candidate_target = dict(target_record)
    if "source_record" not in candidate_target and isinstance(target_source_record, Mapping):
        candidate_target["source_record"] = dict(target_source_record)

    candidate = build_candidate_input_set(
        input_set_id=input_set_id,
        target=candidate_target,
        references=references,
        generator_training_cutoff_utc=generator_training_cutoff_utc,
        source_provenance={
            "acquisition_status": "development_only",
            "target_metadata_source": "caller_supplied",
            "reference_metadata_source": "OpenAlex",
            "reference_edge_source": "OpenAlex referenced_works",
            "reference_count_reported_by_target": len(identifiers),
            "reference_records_retrieved": len(records_by_id),
            "missing_openalex_ids": retrieval["missing_openalex_ids"],
            "request_count": retrieval["request_count"],
            "target_edge_retrieval": {
                "source": target_response.get("source"),
                "api_version": target_response.get("api_version"),
                "request_url": target_response.get("request_url"),
                "retrieved_at_utc": target_response.get("retrieved_at_utc"),
                "http_status": target_response.get("http_status"),
                "edge_source_field": "referenced_works",
                "edge_status": "reported_by_source_not_independently_cross_checked",
            },
            "reference_metadata_batches": [
                {
                    "source": row.get("source"),
                    "api_version": row.get("api_version"),
                    "request_url": row.get("request_url"),
                    "retrieved_at_utc": row.get("retrieved_at_utc"),
                    "http_status": row.get("http_status"),
                    "cache_hit": row.get("cache_hit"),
                    "response_sha256": row.get("response_sha256"),
                }
                for row in retrieval_responses if isinstance(row, Mapping)
            ] if isinstance(retrieval_responses, list) else [],
            "dataset_selected": False,
            "dataset_frozen": False,
        },
        reference_links_verified=reference_links_verified,
        reference_link_provenance=reference_link_provenance,
        excluded_reference_paper_ids=excluded_reference_paper_ids,
    )
    candidate["source_record_hashes"]["openalex_target"] = _source_record_hash(
        target_response.get("raw_response")
    )

    return {
        "status": "development_only_not_frozen",
        "candidate": candidate,
        "retrieval": {
            "reference_identifier_count": len(identifiers),
            "metadata_retrieved_count": len(records_by_id),
            "missing_metadata_count": len(retrieval["missing_openalex_ids"]),
            "request_count": retrieval["request_count"],
        },
        "eligibility_audit": candidate["eligibility_audit"],
    }


def acquire_openalex_candidate_for_e2_record(
    adapter: Any, e2_source_record: Mapping[str, Any], *, input_set_id: str,
    generator_training_cutoff_utc: str | None,
    excluded_reference_paper_ids: Sequence[str] = (),
) -> dict[str, Any]:
    """Resolve one existing E2 arXiv record in OpenAlex and acquire its references.

    OpenAlex matches are retained only when exactly one candidate carries the
    exact canonical arXiv identifier. Ambiguous/no matches remain unresolved.
    The candidate remains provisional because source-edge verification policy,
    model cutoff, and dataset selection are not established here.
    """
    if not isinstance(e2_source_record, Mapping):
        raise ValueError("E2 source record must be an object")
    from citation_sources import openalex_record_matches_arxiv_id

    raw_id = e2_source_record.get("paper_id")
    try:
        canonical_id = canonicalize_arxiv_id(raw_id)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"E2 source record has invalid paper_id: {exc}") from exc
    resolution = adapter.resolve_by_arxiv_external_id(canonical_id)
    if not isinstance(resolution, Mapping):
        raise ValueError("OpenAlex arXiv resolution must return an object")
    matches = []
    for row in resolution.get("candidate_matches", []):
        if not isinstance(row, Mapping):
            continue
        if openalex_record_matches_arxiv_id(row, canonical_id):
            matches.append(dict(row))
    if len(matches) != 1:
        return {
            "status": "unresolved_openalex_target_match",
            "input_set_id": input_set_id,
            "canonical_target_paper_id": canonical_id,
            "exact_match_count": len(matches),
            "candidate_matches": [dict(row) for row in resolution.get("candidate_matches", [])
                                  if isinstance(row, Mapping)],
            "resolution_provenance": {
                "source": resolution.get("source", "OpenAlex"),
                "api_version": resolution.get("api_version"),
                "request_url": resolution.get("request_url"),
                "retrieved_at_utc": resolution.get("retrieved_at_utc"),
                "http_status": resolution.get("http_status"),
                "match_method": resolution.get("match_method"),
                "automatic_match_selected": False,
            },
        }

    openalex_target = matches[0]
    target_response = {
        "source": resolution.get("source", "OpenAlex"),
        "api_version": resolution.get("api_version"),
        "request_url": resolution.get("request_url"),
        "retrieved_at_utc": resolution.get("retrieved_at_utc"),
        "http_status": resolution.get("http_status"),
        "raw_response": openalex_target,
    }
    target_record = {
        **dict(e2_source_record),
        "source_record": dict(e2_source_record),
        "source_url": e2_source_record.get("paper_url"),
        "target_metadata_provenance": {
            "source": e2_source_record.get("source"),
            "source_url": e2_source_record.get("paper_url"),
            "retrieved_at_utc": e2_source_record.get("retrieved_at_utc"),
            "source_record_sha256": _source_record_hash(e2_source_record).get("sha256"),
        },
        "openalex_target_record": openalex_target,
        "openalex_target_source_url": openalex_target.get("id"),
        "openalex_target_resolution": {
            "source": resolution.get("source", "OpenAlex"),
            "api_version": resolution.get("api_version"),
            "request_url": resolution.get("request_url"),
            "retrieved_at_utc": resolution.get("retrieved_at_utc"),
            "http_status": resolution.get("http_status"),
            "match_method": resolution.get("match_method"),
            "automatic_match_selected": False,
            "exact_canonical_arxiv_match_count": 1,
        },
    }
    acquired = acquire_openalex_reference_candidate(
        adapter, target_response, target_record,
        input_set_id=input_set_id,
        generator_training_cutoff_utc=generator_training_cutoff_utc,
        reference_links_verified=False,
        reference_link_provenance={
            "source": "OpenAlex",
            "source_field": "referenced_works",
            "status": "source_reported_not_independently_cross_checked",
            "target_openalex_id": openalex_target.get("id"),
            "retrieved_at_utc": resolution.get("retrieved_at_utc"),
            "request_url": resolution.get("request_url"),
        },
        excluded_reference_paper_ids=excluded_reference_paper_ids,
    )
    acquired.update({
        "status": "provisional_candidate_acquired",
        "target_resolution_provenance": target_record["openalex_target_resolution"],
    })
    return acquired


def acquire_openalex_candidate_pool_from_e2(
    adapter: Any, raw_source_records: Sequence[Mapping[str, Any]], *,
    focal_exclusion_ids: Iterable[str], development_manifest: Mapping[str, Any] | None = None,
    generator_training_cutoff_utc: str | None, max_targets: int,
) -> dict[str, Any]:
    """Acquire a provisional OpenAlex citation pool from real E2 paper records.

    IDs are traversed in canonical order solely to make acquisition reproducible;
    this does not select or freeze an E6 evaluation sample. Focal and reserved
    development papers are excluded as targets and references. Candidate source
    records and all retrieval outcomes remain in the returned audit structure.
    """
    if type(max_targets) is not int or max_targets < 1:
        raise ValueError("max_targets must be a positive integer")
    if development_manifest is None:
        try:
            development_manifest = json.loads(DEFAULT_DEVELOPMENT_MANIFEST.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"cannot read E6 development manifest: {exc}") from exc
    reserved = development_manifest.get("reserved_development_ids") if isinstance(
        development_manifest, Mapping
    ) else None
    reserved_ids = reserved.get("paper_ids") if isinstance(reserved, Mapping) else None
    if not isinstance(reserved_ids, list):
        raise ValueError("development manifest is missing reserved development paper IDs")
    excluded_ids = {canonicalize_arxiv_id(value) for value in reserved_ids}
    excluded_ids.update(canonicalize_arxiv_id(value) for value in focal_exclusion_ids)
    aggregated = canonicalize_records(raw_source_records)
    targets = []
    for canonical_id, entry in aggregated["papers"].items():
        source = entry.get("canonical_record")
        if canonical_id in excluded_ids or not isinstance(source, Mapping):
            continue
        if not isinstance(source.get("abstract"), str) or not source["abstract"].strip():
            continue
        targets.append((canonical_id, dict(source)))
    targets.sort(key=lambda pair: pair[0])
    attempted = []
    acquired_candidates = []
    unresolved = []
    for canonical_id, source_record in targets[:max_targets]:
        input_set_id = "lit-" + canonical_id
        try:
            result = acquire_openalex_candidate_for_e2_record(
                adapter, source_record,
                input_set_id=input_set_id,
                generator_training_cutoff_utc=generator_training_cutoff_utc,
                excluded_reference_paper_ids=sorted(excluded_ids),
            )
        except Exception as exc:
            # A 429 applies to the whole API client/IP. Stop the current
            # acquisition instead of issuing the same blocked request for
            # every remaining target in this batch; successful responses are
            # already safely retained by the append-only URL cache.
            if getattr(exc, "http_status", None) == 429:
                raise
            attempted.append({"input_set_id": input_set_id, "paper_id": source_record.get("paper_id"),
                              "status": "retrieval_failed", "error": str(exc),
                              "attempt_history": getattr(exc, "attempts", [])})
            continue
        attempted.append({"input_set_id": input_set_id, "paper_id": source_record.get("paper_id"),
                          "status": result.get("status")})
        if result.get("status") == "provisional_candidate_acquired":
            acquired_candidates.append(result["candidate"])
        else:
            unresolved.append(result)
    return {
        "schema_version": "e6-literature-acquisition-pool-v1",
        "status": "provisional_not_selected_not_frozen",
        "source_corpus": "E2/data/raw_papers.jsonl",
        "candidate_target_count_after_exclusions": len(targets),
        "max_targets_requested": max_targets,
        "target_records_attempted": len(attempted),
        "candidates_acquired": len(acquired_candidates),
        "unresolved_target_matches": len(unresolved),
        "retrieval_failures": sum(row["status"] == "retrieval_failed" for row in attempted),
        "excluded_target_ids": sorted(excluded_ids),
        "attempts": attempted,
        "unresolved_matches": unresolved,
        "candidates": acquired_candidates,
    }


def extract_literature_target_annotations(
    candidates: Sequence[Mapping[str, Any]], model_client: Any,
    *, model_configuration: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Apply the fixed E6 target-extraction prompt to each supplied candidate.

    The prompt receives ``target.full_text`` when supplied, otherwise the
    preserved target abstract. The text field used is recorded with the result;
    the function never reconstructs or fabricates full text.
    """
    from evaluation import extract_reference_targets

    if isinstance(candidates, (str, bytes)) or not isinstance(candidates, Sequence):
        raise ValueError("candidates must be a sequence of candidate objects")
    if not isinstance(model_configuration, Mapping):
        raise ValueError("model_configuration must be an object")
    extracted: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, Mapping):
            raise ValueError(f"candidate {index} must be an object")
        input_set_id = candidate.get("input_set_id")
        if not isinstance(input_set_id, str) or not input_set_id.strip():
            raise ValueError(f"candidate {index} is missing input_set_id")
        if input_set_id in seen_ids:
            raise ValueError(f"duplicate input_set_id {input_set_id!r}")
        seen_ids.add(input_set_id)
        target = candidate.get("target")
        if not isinstance(target, Mapping):
            raise ValueError(f"candidate {index} is missing target record")
        if isinstance(target.get("full_text"), str) and target["full_text"].strip():
            text_field, target_text = "full_text", target["full_text"]
        elif isinstance(target.get("abstract"), str) and target["abstract"].strip():
            text_field, target_text = "abstract", target["abstract"]
        else:
            raise ValueError(f"candidate {index} has neither nonempty full_text nor abstract")
        record = dict(candidate)
        record["target_extraction"] = extract_reference_targets(
            input_set_id, target_text, model_client,
            model_configuration=dict(model_configuration),
        )
        record["target_extraction_source_field"] = text_field
        extracted.append(record)
    return extracted


def build_manual_extraction_review_worklist(
    candidates: Sequence[Mapping[str, Any]], selected_input_set_ids: Sequence[str],
) -> dict[str, Any]:
    """Create pending manual-check forms for 20 explicitly selected extractions.

    Selection is supplied by the caller because the repository's selection and
    adjudication policy is unresolved. No review is marked complete here.
    """
    if isinstance(selected_input_set_ids, (str, bytes)) or not isinstance(
        selected_input_set_ids, Sequence
    ):
        raise ValueError("selected_input_set_ids must be a sequence")
    ids = list(selected_input_set_ids)
    if len(ids) != REQUIRED_MANUAL_CHECKS or any(
        not isinstance(value, str) or not value.strip() for value in ids
    ) or len(set(ids)) != REQUIRED_MANUAL_CHECKS:
        raise ValueError("exactly 20 distinct nonempty input_set_ids are required")
    by_id = {
        row.get("input_set_id"): row for row in candidates if isinstance(row, Mapping)
    }
    missing = [value for value in ids if value not in by_id]
    if missing:
        raise ValueError("selected review input_set_ids are unavailable: " + ", ".join(missing))

    reviews = []
    for input_set_id in ids:
        candidate = by_id[input_set_id]
        extraction = candidate.get("target_extraction")
        if (not isinstance(extraction, Mapping) or extraction.get("status") != "succeeded"
                or not isinstance(extraction.get("parsed_output"), Mapping)):
            raise ValueError(f"{input_set_id} has no successful target extraction record")
        target = candidate.get("target")
        if not isinstance(target, Mapping):
            raise ValueError(f"{input_set_id} has no target record")
        source_field = candidate.get("target_extraction_source_field")
        source_text = target.get(source_field) if source_field in ("full_text", "abstract") else None
        if not isinstance(source_text, str) or not source_text.strip():
            raise ValueError(f"{input_set_id} has no preserved extraction source text")
        source_provenance = target.get("target_metadata_provenance")
        source_provenance = source_provenance if isinstance(source_provenance, Mapping) else {}
        source_url = source_provenance.get("source_url", target.get("paper_url"))
        reviews.append({
            "input_set_id": input_set_id,
            "target_paper_id": target.get("paper_id"),
            "target_title": target.get("title"),
            "target_published": target.get("published"),
            "target_source_url": source_url,
            "target_extraction_source_field": source_field,
            "target_source_text": source_text,
            "target_source_text_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
            "target_extraction": dict(extraction),
            "research_question_extraction_accurate": None,
            "main_hypothesis_extraction_accurate": None,
            "research_question_explicitness_accurate": None,
            "main_hypothesis_explicitness_accurate": None,
            "reviewer_id": None,
            "reviewed_at_utc": None,
            "reviewer_notes": None,
            "manual_check_completed": False,
        })
    worklist = {
        "schema_version": "e6-literature-extraction-review-v1",
        "status": "pending_manual_review",
        "required_unique_cases": REQUIRED_MANUAL_CHECKS,
        "completed_unique_cases": 0,
        "case_selection_and_adjudication_policy": "unresolved; IDs explicitly supplied by caller",
        "selected_input_set_ids": ids,
        "reviews": reviews,
    }
    canonical = json.dumps(worklist, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":"), allow_nan=False)
    worklist["worklist_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return worklist


def complete_manual_extraction_review(
    review_record: Mapping[str, Any], *, reviewer_id: str, reviewed_at_utc: str,
    research_question_extraction_accurate: bool,
    main_hypothesis_extraction_accurate: bool,
    research_question_explicitness_accurate: bool,
    main_hypothesis_explicitness_accurate: bool,
    reviewer_notes: str = "",
) -> dict[str, Any]:
    """Record a completed human check while retaining its source extraction."""
    if not isinstance(review_record, Mapping):
        raise ValueError("review_record must be an object")
    if not isinstance(review_record.get("input_set_id"), str) or not review_record["input_set_id"].strip():
        raise ValueError("review_record is missing input_set_id")
    if not isinstance(review_record.get("target_extraction"), Mapping):
        raise ValueError("review_record is missing target_extraction")
    if not isinstance(reviewer_id, str) or not reviewer_id.strip():
        raise ValueError("reviewer_id is required")
    if parse_utc_datetime(reviewed_at_utc) is None:
        raise ValueError("reviewed_at_utc must be an ISO timestamp with timezone")
    decisions = {
        "research_question_extraction_accurate": research_question_extraction_accurate,
        "main_hypothesis_extraction_accurate": main_hypothesis_extraction_accurate,
        "research_question_explicitness_accurate": research_question_explicitness_accurate,
        "main_hypothesis_explicitness_accurate": main_hypothesis_explicitness_accurate,
    }
    if any(type(value) is not bool for value in decisions.values()):
        raise ValueError("all manual extraction checks must be Boolean")
    if not isinstance(reviewer_notes, str):
        raise ValueError("reviewer_notes must be a string")
    completed = dict(review_record)
    completed.update(decisions)
    completed.update({
        "reviewer_id": reviewer_id,
        "reviewed_at_utc": format_utc_datetime(parse_utc_datetime(reviewed_at_utc)),
        "reviewer_notes": reviewer_notes,
        "manual_check_completed": True,
    })
    return completed


def build_orchestrator_input_manifest(
    candidates: Sequence[Mapping[str, Any]], generator_training_cutoff_utc: str | None,
    *, domain_and_task_by_input_set: Mapping[str, str],
    development_manifest: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a deterministic, unselected manifest matching ExperimentInput fields.

    Each candidate must already include verified references and a successful
    extraction. ``domain_and_task_by_input_set`` must be supplied explicitly;
    this function will not derive the model task from gold annotations.
    """
    if isinstance(candidates, (str, bytes)) or not isinstance(candidates, Sequence):
        raise ValueError("candidates must be a sequence")
    if not isinstance(domain_and_task_by_input_set, Mapping):
        raise ValueError("domain_and_task_by_input_set must be an object")
    if development_manifest is None:
        try:
            development_manifest = json.loads(DEFAULT_DEVELOPMENT_MANIFEST.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"cannot read E6 development manifest: {exc}") from exc
    reserved = development_manifest.get("reserved_development_ids") if isinstance(
        development_manifest, Mapping
    ) else None
    reserved_ids = reserved.get("paper_ids") if isinstance(reserved, Mapping) else None
    if not isinstance(reserved_ids, list):
        raise ValueError("development manifest is missing reserved development paper IDs")
    reserved_canonical = {canonicalize_arxiv_id(value) for value in reserved_ids}

    ids: set[str] = set()
    targets: set[str] = set()
    manifest_rows = []
    candidate_audits = []
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, Mapping):
            candidate_audits.append({"index": index, "status": "invalid", "errors": ["candidate must be an object"]})
            continue
        audit = validate_literature_input_set(candidate, generator_training_cutoff_utc)
        errors = list(audit.get("errors", []))
        input_set_id = candidate.get("input_set_id")
        target = candidate.get("target")
        canonical_target_id = audit.get("canonical_target_paper_id")
        if isinstance(input_set_id, str) and input_set_id in ids:
            errors.append("duplicate input_set_id")
        elif isinstance(input_set_id, str):
            ids.add(input_set_id)
        if canonical_target_id in targets:
            errors.append("duplicate target paper ID")
        elif canonical_target_id:
            targets.add(canonical_target_id)
        if canonical_target_id in reserved_canonical:
            errors.append("target paper is reserved for the E6 development manifest")

        extraction = candidate.get("target_extraction")
        parsed = extraction.get("parsed_output") if isinstance(extraction, Mapping) else None
        if not isinstance(extraction, Mapping) or extraction.get("status") != "succeeded":
            errors.append("successful fixed-prompt target extraction is required")
        else:
            from evaluation import TARGET_EXTRACTION_PROMPT
            extraction_input = extraction.get("evaluation_input")
            extraction_provenance = extraction.get("provenance")
            source_field = candidate.get("target_extraction_source_field")
            source_text = target.get(source_field) if isinstance(target, Mapping) and isinstance(
                source_field, str
            ) else None
            try:
                prompt_template = TARGET_EXTRACTION_PROMPT.read_text(encoding="utf-8")
            except OSError:
                prompt_template = None
            expected_prompt = (
                prompt_template.replace("{{TARGET_PAPER_TEXT}}", source_text)
                if isinstance(prompt_template, str) and isinstance(source_text, str) else None
            )
            if extraction.get("stage") != "reference_target_extraction":
                errors.append("target extraction stage does not match the fixed extraction interface")
            if not isinstance(extraction_input, Mapping) or extraction_input.get(
                "target_paper_text"
            ) != source_text or extraction_input.get("rendered_prompt") != expected_prompt:
                errors.append("target extraction input does not match the recorded source text and fixed prompt")
            if not isinstance(extraction_provenance, Mapping) or extraction_provenance.get(
                "prompt_path"
            ) != "prompts/e6/09_target_extraction.txt" or extraction_provenance.get(
                "prompt_sha256"
            ) != (hashlib.sha256(prompt_template.encode("utf-8")).hexdigest()
                  if isinstance(prompt_template, str) else None):
                errors.append("target extraction prompt provenance is missing or invalid")
        if not isinstance(parsed, Mapping):
            errors.append("parsed target extraction is missing")
            parsed = {}
        question = parsed.get("research_question")
        hypothesis = parsed.get("main_hypothesis")
        if question is not None and (not isinstance(question, str) or not question.strip()):
            errors.append("research_question must be a nonempty string or null")
        if hypothesis is not None and (not isinstance(hypothesis, str) or not hypothesis.strip()):
            errors.append("main_hypothesis must be a nonempty string or null")
        if type(parsed.get("research_question_explicit")) is not bool:
            errors.append("research_question_explicit must be Boolean")
        if type(parsed.get("main_hypothesis_explicit")) is not bool:
            errors.append("main_hypothesis_explicit must be Boolean")
        task = domain_and_task_by_input_set.get(input_set_id) if isinstance(input_set_id, str) else None
        if not isinstance(task, str) or not task.strip():
            errors.append("explicit orchestrator domain/task text is required")
        if not isinstance(question, str) or not question.strip():
            errors.append("a nonempty research_question is required for reference evaluation")
        if errors:
            candidate_audits.append({"input_set_id": input_set_id, "status": "blocked", "errors": errors})
            continue

        reference_evidence = [row["abstract"] for row in candidate["references"]]
        generation_evidence = "\n\n".join(reference_evidence)
        refs = [dict(row) for row in candidate["references"]]
        source_provenance = candidate.get("provenance")
        source_provenance = source_provenance if isinstance(source_provenance, Mapping) else {}
        reference_link_provenance = candidate.get("reference_link_provenance")
        reference_link_provenance = (
            reference_link_provenance if isinstance(reference_link_provenance, Mapping) else {}
        )
        source_hashes = candidate.get("source_record_hashes")
        source_hashes = source_hashes if isinstance(source_hashes, Mapping) else {}
        evidence_hashes = candidate.get("evidence_hashes")
        evidence_hashes = evidence_hashes if isinstance(evidence_hashes, Mapping) else {}
        provenance = {
            "input_set_id": input_set_id,
            "target_metadata_provenance": dict(target.get("target_metadata_provenance", {}))
            if isinstance(target.get("target_metadata_provenance"), Mapping) else {},
            "openalex_target_resolution": dict(target.get("openalex_target_resolution", {}))
            if isinstance(target.get("openalex_target_resolution"), Mapping) else {},
            "source_provenance": dict(source_provenance),
            "reference_link_provenance": dict(reference_link_provenance),
            "target_source_record_hash": source_hashes.get("target"),
            "reference_source_record_hashes": source_hashes.get("references"),
            "target_abstract_sha256": evidence_hashes.get("target_abstract_sha256"),
            "generation_evidence_source": "ordered cited-reference abstracts joined by two newlines",
            "target_abstract_is_generation_input": False,
            "reference_abstract_hashes": evidence_hashes.get("reference_abstracts"),
            "target_extraction_record_sha256": _source_record_hash(extraction).get("sha256"),
            "target_extraction_source_field": candidate.get("target_extraction_source_field"),
            "references": refs,
            "split": "EVALUATION",
            "dataset_status": "prepared_unselected_unfrozen",
        }
        experiment_input = {
            "paper_id": target.get("paper_id"),
            "domain_and_task": task,
            # The focal target's abstract is reserved for reference extraction;
            # generation receives only source-attested cited-reference abstracts.
            "evidence": generation_evidence,
            "provenance": provenance,
            "reference_evidence": reference_evidence,
            "split": "EVALUATION",
        }
        input_hash = hashlib.sha256(json.dumps(
            experiment_input, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")).hexdigest()
        manifest_rows.append({
            "input_set_id": input_set_id,
            "paper_id": target.get("paper_id"),
            "target_published": audit.get("target_published_utc"),
            "target_references": refs,
            "target_extraction": dict(extraction),
            "experiment_input": experiment_input,
            "experiment_input_sha256": input_hash,
            "eligibility_audit": audit,
        })
        candidate_audits.append({"input_set_id": input_set_id, "status": "ready", "errors": []})

    manifest = {
        "schema_version": "e6-literature-input-manifest-v1",
        "schema_status": "provisional_unapproved",
        "status": "minimum_met" if len(manifest_rows) >= MINIMUM_INPUT_SETS else "minimum_not_met",
        "split": "EVALUATION",
        "generator_training_cutoff_utc": format_utc_datetime(
            parse_utc_datetime(generator_training_cutoff_utc)
        ) or generator_training_cutoff_utc,
        "minimum_required_input_sets": MINIMUM_INPUT_SETS,
        "prepared_input_set_count": len(manifest_rows),
        "input_sets_selected": False,
        "input_sets_frozen": False,
        "candidate_audits": candidate_audits,
        "inputs": manifest_rows,
    }
    canonical_manifest = json.dumps(
        manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False,
    )
    manifest["manifest_sha256"] = hashlib.sha256(canonical_manifest.encode("utf-8")).hexdigest()
    return manifest


def write_manifest_exclusive(path: str | Path, manifest: Mapping[str, Any]) -> None:
    """Write a deterministic JSON manifest without replacing existing output."""
    destination = Path(path)
    payload = json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    try:
        with destination.open("x", encoding="utf-8") as handle:
            handle.write(payload)
    except FileExistsError as exc:
        raise FileExistsError(f"refusing to overwrite existing manifest: {destination}") from exc


def load_orchestrator_experiment_inputs(manifest: Mapping[str, Any]) -> list[Any]:
    """Validate a prepared manifest and convert rows to orchestrator inputs.

    The orchestrator's own final-mode protocol gate remains authoritative; this
    function only validates structure and hashes, and does not execute arms.
    """
    from orchestrator import ExperimentInput

    if not isinstance(manifest, Mapping) or manifest.get("schema_version") != (
        "e6-literature-input-manifest-v1"
    ):
        raise ValueError("unsupported literature input manifest")
    if manifest.get("schema_status") != "provisional_unapproved":
        raise ValueError("literature input manifest must remain provisional")
    supplied_hash = manifest.get("manifest_sha256")
    unsigned_manifest = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    canonical = json.dumps(
        unsigned_manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False,
    )
    actual_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    if supplied_hash != actual_hash:
        raise ValueError("literature input manifest hash is missing or invalid")
    rows = manifest.get("inputs")
    if not isinstance(rows, list) or manifest.get("prepared_input_set_count") != len(rows):
        raise ValueError("literature input manifest count does not match inputs")
    result = []
    seen_ids: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise ValueError(f"literature input manifest row {index} must be an object")
        experiment_input = row.get("experiment_input")
        if not isinstance(experiment_input, Mapping):
            raise ValueError(f"literature input manifest row {index} is missing experiment_input")
        input_hash = hashlib.sha256(json.dumps(
            experiment_input, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")).hexdigest()
        if row.get("experiment_input_sha256") != input_hash:
            raise ValueError(f"literature input manifest row {index} hash is invalid")
        paper_id = experiment_input.get("paper_id")
        task = experiment_input.get("domain_and_task")
        evidence = experiment_input.get("evidence")
        provenance = experiment_input.get("provenance")
        references = experiment_input.get("reference_evidence")
        split = experiment_input.get("split")
        if not isinstance(paper_id, str) or not paper_id.strip() or paper_id in seen_ids:
            raise ValueError(f"literature input manifest row {index} has missing or duplicate paper_id")
        seen_ids.add(paper_id)
        if not isinstance(task, str) or not task.strip():
            raise ValueError(f"literature input manifest row {index} is missing domain_and_task")
        if not isinstance(evidence, str) or not evidence.strip():
            raise ValueError(f"literature input manifest row {index} is missing target evidence")
        if not isinstance(provenance, Mapping) or not isinstance(references, list) or any(
            not isinstance(value, str) or not value.strip() for value in references
        ):
            raise ValueError(f"literature input manifest row {index} has invalid provenance/references")
        if split != "EVALUATION":
            raise ValueError(f"literature input manifest row {index} must use EVALUATION split")
        result.append(ExperimentInput(
            paper_id=paper_id,
            domain_and_task=task,
            evidence=evidence,
            provenance=dict(provenance),
            reference_evidence=tuple(references),
            split=split,
        ))
    return result
