"""Fetch OpenAlex metadata for source-attested citation edges and build candidates.

The target work’s own ``referenced_works`` array is the sole edge source. This
module does not infer citations from titles, DOIs, or semantic similarity.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from acquire_literature_batches import (
    _canonical_hash,
    _write_json_exclusive,
    eligible_source_targets,
)
from citation_sources import openalex_record_matches_arxiv_id, normalize_openalex_work
from prepare_dataset import canonicalize_arxiv_id, canonicalize_records
from prepare_literature_testbed import (
    MINIMUM_REFERENCES,
    _source_record_hash,
    build_candidate_input_set,
    canonical_literature_reference_id,
    parse_utc_datetime,
    validate_literature_input_set,
)

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
CUTOFF_UTC = "2024-09-01T00:00:00Z"
REFERENCE_BATCH_SIZE = 100
REFERENCE_BATCH_SCHEMA = "e6-openalex-reference-metadata-batch-v1"
MANIFEST_SCHEMA = "e6-literature-citation-verified-manifest-v1"
OPENALEX_WORK_RE = re.compile(r"^https://openalex\.org/(W[0-9]+)$", re.IGNORECASE)


def _load_reference_batch(path: Path, *, run_sha256: str, batch_index: int,
                          target_ids: Sequence[str]) -> dict[str, Any]:
    try:
        batch = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"reference metadata batch is unreadable: {path}") from exc
    if not isinstance(batch, dict) or batch.get("schema_version") != REFERENCE_BATCH_SCHEMA:
        raise ValueError(f"unsupported reference metadata batch: {path}")
    if batch.get("run_sha256") != run_sha256 or batch.get("batch_index") != batch_index:
        raise ValueError(f"reference batch provenance mismatch: {path}")
    if batch.get("target_ids") != list(target_ids):
        raise ValueError(f"reference batch IDs differ from current deterministic order: {path}")
    unsigned = {key: value for key, value in batch.items() if key != "batch_sha256"}
    if batch.get("batch_sha256") != _canonical_hash(unsigned):
        raise ValueError(f"reference metadata batch hash mismatch: {path}")
    if not isinstance(batch.get("acquisition_result"), Mapping):
        raise ValueError(f"reference metadata batch payload missing: {path}")
    return batch


def canonical_openalex_work_id(value: Any) -> str:
    """Accept only exact OpenAlex Work URLs/IDs; return the canonical URL."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("citation edge must contain an OpenAlex Work ID")
    raw = value.strip()
    if re.fullmatch(r"W[0-9]+", raw, re.IGNORECASE):
        raw = "https://openalex.org/" + raw
    match = OPENALEX_WORK_RE.fullmatch(raw)
    if not match:
        raise ValueError("citation edge is not an exact OpenAlex Work ID")
    return "https://openalex.org/" + match.group(1).upper()


def load_source_edge_targets(
    reconciliation: Mapping[str, Any], raw_source_records: Sequence[Mapping[str, Any]], *,
    focal_exclusion_ids: Sequence[str], development_manifest: Mapping[str, Any],
    cutoff_utc: str = CUTOFF_UTC,
) -> tuple[list[dict[str, Any]], list[str], dict[str, Any]]:
    """Validate exact targets and extract their source-reported OpenAlex edges."""
    source_targets = eligible_source_targets(
        raw_source_records, focal_exclusion_ids=focal_exclusion_ids,
        development_manifest=development_manifest, cutoff_utc=cutoff_utc,
    )
    by_target = {canonicalize_arxiv_id(row["paper_id"]): row for row in source_targets}
    exact_rows: dict[str, Mapping[str, Any]] = {}
    for row in reconciliation.get("rows", []):
        if not isinstance(row, Mapping) or row.get("status") != "exact_match":
            continue
        target_id = canonicalize_arxiv_id(row.get("target_arxiv_id"))
        exact = row.get("exact_openalex_records")
        if target_id not in by_target or not isinstance(exact, list) or len(exact) != 1:
            continue
        work = exact[0]
        if not openalex_record_matches_arxiv_id(work, target_id):
            continue
        if target_id in exact_rows:
            raise ValueError(f"duplicate exact OpenAlex target record for {target_id}")
        exact_rows[target_id] = row

    targets = []
    all_reference_ids: set[str] = set()
    edge_map: dict[str, Any] = {}
    for target_id in sorted(exact_rows):
        row = exact_rows[target_id]
        work = row["exact_openalex_records"][0]
        e2_record = by_target[target_id]
        raw_edges = work.get("referenced_works")
        edge_ids = []
        invalid_edges = []
        if isinstance(raw_edges, list):
            seen = set()
            for index, value in enumerate(raw_edges):
                try:
                    openalex_id = canonical_openalex_work_id(value)
                except ValueError as exc:
                    invalid_edges.append({"index": index, "value": value, "reason": str(exc)})
                    continue
                if openalex_id in seen:
                    continue
                seen.add(openalex_id)
                edge_ids.append(openalex_id)
                all_reference_ids.add(openalex_id)
        target_openalex_id = canonical_openalex_work_id(work.get("id"))
        if target_openalex_id in edge_ids:
            edge_ids = [value for value in edge_ids if value != target_openalex_id]
            invalid_edges.append({"openalex_id": target_openalex_id,
                                  "reason": "target work cannot cite itself"})
        target_entry = {
            "input_set_id": "lit-" + target_id,
            "target_arxiv_id": target_id,
            "source_target_record": dict(e2_record),
            "target_openalex_record": dict(work),
            "target_openalex_id": target_openalex_id,
            "target_resolution_provenance": {
                "source": "OpenAlex",
                "request_url": row.get("request_url"),
                "retrieved_at_utc": row.get("retrieved_at_utc"),
                "http_status": row.get("http_status"),
                "raw_response_sha256": row.get("raw_response_sha256"),
                "target_record_sha256": _source_record_hash(work).get("sha256"),
            },
            "referenced_works_ids": edge_ids,
            "source_referenced_works_count": len(raw_edges) if isinstance(raw_edges, list) else None,
            "invalid_source_edges": invalid_edges,
        }
        targets.append(target_entry)
        edge_map[target_id] = edge_ids

    run_fingerprint = _canonical_hash({
        "cutoff_utc": cutoff_utc,
        "targets": [{"target_arxiv_id": row["target_arxiv_id"],
                     "target_openalex_record_sha256": row["target_resolution_provenance"][
                         "target_record_sha256"],
                     "referenced_works_ids": row["referenced_works_ids"]}
                    for row in targets],
        "excluded_focal_ids": sorted(canonicalize_arxiv_id(x) for x in focal_exclusion_ids),
        "development_manifest_sha256": _canonical_hash(development_manifest),
        "reference_batch_size": REFERENCE_BATCH_SIZE,
    })
    return targets, sorted(all_reference_ids), {
        "run_sha256": run_fingerprint,
        "source_exact_target_count": len(targets),
        "target_records_with_reference_lists": sum(bool(row["referenced_works_ids"])
                                                   for row in targets),
        "source_citation_edge_count": sum(len(row["referenced_works_ids"]) for row in targets),
        "unique_reference_openalex_id_count": len(all_reference_ids),
    }


def retrieve_reference_metadata_batches(
    adapter: Any, reference_ids: Sequence[str], *, output_dir: str | Path,
    run_sha256: str, progress: Callable[[Mapping[str, Any]], None] | None = None,
    cached_records_by_openalex_id: Mapping[str, Mapping[str, Any]] | None = None,
    cached_provenance_by_openalex_id: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Fetch references in deterministic <=100-ID batches, atomically resumable.

    Exact-ID records already present in the acquisition inputs are reused before
    requesting the remaining IDs. This is safe only when callers provide the
    source record and its retrieval provenance under the same canonical ID.
    """
    if progress is None:
        progress = lambda _: None
    ordered_ids = sorted({canonical_openalex_work_id(value) for value in reference_ids})
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    records: dict[str, Mapping[str, Any]] = {}
    provenance: dict[str, Mapping[str, Any]] = {}
    cached_records = {
        canonical_openalex_work_id(key): value
        for key, value in (cached_records_by_openalex_id or {}).items()
    }
    cached_provenance = {
        canonical_openalex_work_id(key): value
        for key, value in (cached_provenance_by_openalex_id or {}).items()
    }
    batch_count = (len(ordered_ids) + REFERENCE_BATCH_SIZE - 1) // REFERENCE_BATCH_SIZE
    for batch_index in range(1, batch_count + 1):
        start = (batch_index - 1) * REFERENCE_BATCH_SIZE
        batch_ids = ordered_ids[start:start + REFERENCE_BATCH_SIZE]
        path = output / f"openalex_reference_metadata_batch_v1_{batch_index:04d}.json"
        if path.exists():
            batch = _load_reference_batch(path, run_sha256=run_sha256,
                                          batch_index=batch_index, target_ids=batch_ids)
        else:
            found: dict[str, Mapping[str, Any]] = {
                key: dict(cached_records[key]) for key in batch_ids if key in cached_records
            }
            fetch_ids = [key for key in batch_ids if key not in found]
            response = None
            raw: Mapping[str, Any] = {"results": []}
            if fetch_ids:
                response = adapter.get_works(fetch_ids, per_page=REFERENCE_BATCH_SIZE)
                response_raw = response.get("raw_response", {})
                raw = response_raw if isinstance(response_raw, Mapping) else {"results": []}
            result_rows = raw.get("results", []) if isinstance(raw, Mapping) else []
            for row in result_rows if isinstance(result_rows, list) else []:
                if not isinstance(row, Mapping):
                    continue
                try:
                    openalex_id = canonical_openalex_work_id(row.get("id"))
                except ValueError:
                    continue
                if openalex_id in batch_ids:
                    found[openalex_id] = dict(row)
            missing = [value for value in batch_ids if value not in found]
            request_provenance = {
                "source": response.get("source"),
                "api_version": response.get("api_version"),
                "request_url": response.get("request_url"),
                "retrieved_at_utc": response.get("retrieved_at_utc"),
                "http_status": response.get("http_status"),
                "cache_hit": response.get("cache_hit") is True,
                "response_sha256": _canonical_hash(raw),
            } if response else None
            per_record_provenance = {}
            for key in found:
                if key in cached_records:
                    source_provenance = cached_provenance.get(key)
                    if not isinstance(source_provenance, Mapping):
                        raise ValueError(f"cached reference record lacks provenance: {key}")
                    per_record_provenance[key] = dict(source_provenance)
                else:
                    per_record_provenance[key] = dict(request_provenance or {})
            artifact = {
                "schema_version": REFERENCE_BATCH_SCHEMA,
                "run_sha256": run_sha256,
                "batch_index": batch_index,
                "target_ids": batch_ids,
                "acquisition_result": {
                    "source": response.get("source") if response else "existing_exact_target_cache",
                    "api_version": response.get("api_version") if response else None,
                    "request_url": response.get("request_url") if response else None,
                    "retrieved_at_utc": response.get("retrieved_at_utc") if response else None,
                    "http_status": response.get("http_status") if response else None,
                    "cache_hit": bool(response and response.get("cache_hit") is True),
                    "response_sha256": _canonical_hash(raw),
                    "records": [found[key] for key in batch_ids if key in found],
                    "record_provenance_by_openalex_id": per_record_provenance,
                    "missing_openalex_ids": missing,
                },
                "counts": {"requested": len(batch_ids), "retrieved": len(found),
                           "missing": len(missing)},
            }
            artifact["batch_sha256"] = _canonical_hash(artifact)
            _write_json_exclusive(path, artifact)
            batch = artifact
        result = batch["acquisition_result"]
        batch_provenance = {
            key: result.get(key) for key in (
                "source", "api_version", "request_url", "retrieved_at_utc",
                "http_status", "cache_hit", "response_sha256",
            )
        }
        for row in result.get("records", []):
            openalex_id = canonical_openalex_work_id(row["id"])
            if openalex_id in records:
                raise ValueError(f"duplicate reference metadata across batches: {openalex_id}")
            records[openalex_id] = row
            record_provenance = result.get("record_provenance_by_openalex_id", {}).get(openalex_id)
            provenance[openalex_id] = dict(record_provenance or batch_provenance)
        progress({"batch_index": batch_index, "batch_count": batch_count,
                  "requested": len(batch_ids), "retrieved": len(result.get("records", [])),
                  "missing": len(result.get("missing_openalex_ids", [])),
                  "cache_hit": result.get("cache_hit") is True,
                  "reused_existing_records": sum(
                      key in cached_records for key in batch_ids
                  ) if not path.exists() else sum(
                      result.get("record_provenance_by_openalex_id", {}).get(key, {}).get(
                          "reuse_reason") is not None for key in batch_ids
                  )})
    return {"records_by_openalex_id": records, "provenance_by_openalex_id": provenance,
            "reference_id_count": len(ordered_ids), "batch_count": batch_count,
            "missing_openalex_ids": sorted(set(ordered_ids) - set(records))}


def cached_reference_records_from_targets(
    targets: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Mapping[str, Any]], dict[str, Mapping[str, Any]]]:
    """Reuse exact cached target records when another target cites that work."""
    records: dict[str, Mapping[str, Any]] = {}
    provenance: dict[str, Mapping[str, Any]] = {}
    for target in targets:
        record = target.get("target_openalex_record")
        if not isinstance(record, Mapping):
            continue
        work_id = canonical_openalex_work_id(record.get("id"))
        if work_id in records:
            if _canonical_hash(records[work_id]) != _canonical_hash(record):
                raise ValueError(f"conflicting exact OpenAlex records for {work_id}")
            continue
        source = target.get("target_resolution_provenance", {})
        if not isinstance(source, Mapping) or not source.get("request_url"):
            raise ValueError(f"cached target record lacks retrieval provenance: {work_id}")
        records[work_id] = dict(record)
        provenance[work_id] = {
            "source": "OpenAlex",
            "api_version": source.get("api_version"),
            "request_url": source.get("request_url"),
            "retrieved_at_utc": source.get("retrieved_at_utc"),
            "http_status": source.get("http_status"),
            "cache_hit": True,
            "response_sha256": source.get("raw_response_sha256"),
            "target_record_sha256": source.get("target_record_sha256"),
            "reuse_reason": "same_exact_work_id_was_already_retrieved_as_target",
        }
    return records, provenance


def build_verified_literature_manifest(
    targets: Sequence[Mapping[str, Any]], metadata: Mapping[str, Any], *,
    cutoff_utc: str, excluded_arxiv_ids: Sequence[str],
) -> dict[str, Any]:
    """Return a manifest whose input_sets contain eligible rows only."""
    records = metadata.get("records_by_openalex_id", {})
    retrieval_provenance = metadata.get("provenance_by_openalex_id", {})
    excluded = {canonicalize_arxiv_id(value) for value in excluded_arxiv_ids}
    input_sets = []
    audits = []
    for target in targets:
        target_id = target["target_arxiv_id"]
        source_target = dict(target["source_target_record"])
        source_hash = _source_record_hash(source_target).get("sha256")
        refs_for_input = []
        edge_records = []
        seen = set()
        for cited_id in target.get("referenced_works_ids", []):
            source_reference = records.get(cited_id)
            edge = {"openalex_id": cited_id, "edge_source_field": "referenced_works",
                    "edge_source_target_openalex_id": target.get("target_openalex_id"),
                    "edge_verified": True}
            if not isinstance(source_reference, Mapping):
                edge.update({"metadata_status": "not_retrieved", "abstract_available": False})
                edge_records.append(edge)
                continue
            normalized = normalize_openalex_work(source_reference)
            arxiv_id = normalized.get("arxiv_id")
            ref_id = arxiv_id or canonical_literature_reference_id(cited_id)
            if ref_id in seen:
                edge.update({"metadata_status": "duplicate_source_edge", "abstract_available": False})
                edge_records.append(edge)
                continue
            seen.add(ref_id)
            if arxiv_id and (arxiv_id in excluded or arxiv_id == target_id):
                edge.update({"metadata_status": "excluded_reference", "excluded_arxiv_id": arxiv_id,
                             "abstract_available": bool(normalized.get("abstract"))})
                edge_records.append(edge)
                continue
            abstract = normalized.get("abstract")
            edge.update({
                "paper_id": ref_id,
                "doi": (normalized.get("source_identifiers") or {}).get("doi"),
                "title": normalized.get("title"),
                "publication_date": normalized.get("publication_date"),
                "metadata_status": "retrieved_with_abstract" if abstract else "retrieved_without_abstract",
                "abstract_available": bool(abstract),
                "source_url": cited_id,
                "source_record_sha256": _source_record_hash(source_reference).get("sha256"),
                "metadata_retrieval_provenance": dict(retrieval_provenance.get(cited_id, {})),
            })
            edge_records.append(edge)
            if isinstance(abstract, str) and abstract.strip():
                refs_for_input.append({
                    "paper_id": ref_id, "openalex_id": cited_id,
                    "title": normalized.get("title"), "abstract": abstract,
                    "publication_date": normalized.get("publication_date"),
                    "source": "OpenAlex", "source_url": cited_id,
                    "source_record": dict(source_reference),
                    "metadata_retrieval_provenance": dict(retrieval_provenance.get(cited_id, {})),
                })

        target_openalex = dict(target["target_openalex_record"])
        target_openalex_hash = _source_record_hash(target_openalex).get("sha256")
        target_provenance = dict(target.get("target_resolution_provenance", {}))
        target_provenance.update({
            "target_source_record_sha256": source_hash,
            "target_openalex_record_sha256": target_openalex_hash,
            "referenced_works_ids_sha256": _canonical_hash(target.get("referenced_works_ids", [])),
        })
        candidate_target = dict(source_target)
        candidate_target.update({
            "source_record": dict(source_target),
            "target_metadata_provenance": {
                "source": source_target.get("source"),
                "source_url": source_target.get("paper_url"),
                "retrieved_at_utc": source_target.get("retrieved_at_utc"),
                "source_record_sha256": source_hash,
            },
            "openalex_target_record": target_openalex,
            "openalex_target_source_url": target.get("target_openalex_id"),
            "openalex_target_resolution": target_provenance,
        })
        reference_link_provenance = {
            "source": "OpenAlex",
            "status": "verified_from_target_work_referenced_works",
            "edge_source_field": "referenced_works",
            "target_openalex_id": target.get("target_openalex_id"),
            "target_openalex_record_sha256": target_openalex_hash,
            "target_resolution_request_url": target_provenance.get("request_url"),
            "target_resolution_retrieved_at_utc": target_provenance.get("retrieved_at_utc"),
            "source_edge_count": len(target.get("referenced_works_ids", [])),
            "source_edge_ids_sha256": _canonical_hash(target.get("referenced_works_ids", [])),
        }
        candidate = build_candidate_input_set(
            target["input_set_id"], candidate_target, refs_for_input, cutoff_utc,
            source_provenance={
                "acquisition_status": "source_attested_citation_edges",
                "target_metadata_source": source_target.get("source"),
                "reference_metadata_source": "OpenAlex",
                "reference_edge_source": "OpenAlex referenced_works",
                "target_reference_edge_count": len(target.get("referenced_works_ids", [])),
                "reference_abstract_count": len(refs_for_input),
                "excluded_reference_edge_count": sum(
                    row.get("metadata_status") == "excluded_reference" for row in edge_records
                ),
                "dataset_selected": False,
                "dataset_frozen": False,
            },
            reference_links_verified=True,
            reference_link_provenance=reference_link_provenance,
            excluded_reference_paper_ids=sorted(excluded),
        )
        candidate["citation_edges"] = edge_records
        candidate["citation_edge_count_source_reported"] = len(target.get("referenced_works_ids", []))
        candidate["split"] = "EVALUATION"
        candidate["eligibility_audit"] = validate_literature_input_set(candidate, cutoff_utc)
        audits.append({"input_set_id": target["input_set_id"],
                       "target_arxiv_id": target_id,
                       "status": candidate["eligibility_audit"]["status"],
                       "reference_abstract_count": candidate["eligibility_audit"][
                           "unique_reference_with_abstract_count"],
                       "errors": candidate["eligibility_audit"]["errors"]})
        if candidate["eligibility_audit"]["status"] == "eligible_candidate":
            input_sets.append(candidate)

    unsigned = {
        "schema_version": MANIFEST_SCHEMA,
        "status": "minimum_met" if len(input_sets) >= 100 else "minimum_not_met",
        "split": "EVALUATION",
        "generator_training_cutoff_utc": cutoff_utc,
        "minimum_required_input_sets": 100,
        "minimum_references_with_abstracts_per_input_set": MINIMUM_REFERENCES,
        "source_edge_policy": "only target OpenAlex referenced_works IDs; no inferred edges",
        "source_exact_target_count": len(targets),
        "eligible_input_set_count": len(input_sets),
        "input_sets_selected": False,
        "input_sets_frozen": False,
        "input_sets": input_sets,
        "candidate_audits": audits,
    }
    unsigned["manifest_sha256"] = _canonical_hash(unsigned)
    return unsigned


def _load_inputs() -> tuple[list[dict[str, Any]], list[str], Mapping[str, Any], Mapping[str, Any]]:
    import csv

    repository = ROOT.parent
    raw_rows = [json.loads(line) for line in
                (repository / "E2/data/raw_papers.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()]
    with (repository / "E2/data/focal_papers.csv").open(encoding="utf-8", newline="") as handle:
        focal = [row["paper_id"] for row in csv.DictReader(handle) if row.get("paper_id")]
    dev = json.loads((DATA / "development_manifest_v2.json").read_text(encoding="utf-8"))
    reconciliation = json.loads((DATA / "literature_openalex_cache_reconciliation_v1.json")
                                .read_text(encoding="utf-8"))
    return raw_rows, focal, dev, reconciliation


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    from citation_sources import JsonFileCache, OpenAlexAdapter

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-only", action="store_true",
                        help="build manifest from completed reference batch files without network")
    args = parser.parse_args(argv)
    raw_rows, focal, development, reconciliation = _load_inputs()
    targets, reference_ids, audit = load_source_edge_targets(
        reconciliation, raw_rows, focal_exclusion_ids=focal,
        development_manifest=development,
    )
    batch_dir = DATA / "openalex_reference_metadata_batches_v1"
    metadata: dict[str, Any]
    if args.prepare_only:
        metadata = load_reference_metadata_batch_files(
            batch_dir, reference_ids, run_sha256=audit["run_sha256"],
        )
    else:
        adapter = OpenAlexAdapter(
            cache=JsonFileCache(DATA / "openalex_literature_cache_v1"),
            max_attempts=3, timeout_seconds=15,
            progress_callback=print_request_progress,
        )
        try:
            cached_reference_records, cached_reference_provenance = (
                cached_reference_records_from_targets(targets)
            )
            metadata = retrieve_reference_metadata_batches(
                adapter, reference_ids, output_dir=batch_dir,
                run_sha256=audit["run_sha256"], progress=print_batch_progress,
                cached_records_by_openalex_id=cached_reference_records,
                cached_provenance_by_openalex_id=cached_reference_provenance,
            )
        except Exception as exc:
            if getattr(exc, "http_status", None) == 429:
                print("Reference metadata retrieval paused by HTTP 429. Retry-After: {} seconds. "
                      "Completed batch files and successful cache entries are preserved."
                      .format(getattr(exc, "retry_after_seconds", None)), flush=True)
                return 2
            raise
    if metadata.get("missing_batch_files"):
        print("Reference retrieval is incomplete: {} batches absent; rerun after access resumes."
              .format(len(metadata["missing_batch_files"])), flush=True)
        return 2
    excluded = list(focal) + list(
        development["reserved_development_ids"]["paper_ids"]
    )
    manifest = build_verified_literature_manifest(
        targets, metadata, cutoff_utc=CUTOFF_UTC, excluded_arxiv_ids=excluded,
    )
    output = DATA / "literature_citation_verified_manifest_v1.json"
    _write_json_exclusive(output, manifest)
    print(json.dumps({"manifest": str(output), **audit,
                      "eligible_input_set_count": manifest["eligible_input_set_count"],
                      "status": manifest["status"]}, indent=2))
    return 0 if manifest["eligible_input_set_count"] >= 100 else 2


def load_reference_metadata_batch_files(
    output_dir: str | Path, reference_ids: Sequence[str], *, run_sha256: str,
) -> dict[str, Any]:
    """Load complete batch artifacts for a no-network manifest rebuild."""
    output = Path(output_dir)
    ordered = sorted({canonical_openalex_work_id(value) for value in reference_ids})
    records: dict[str, Mapping[str, Any]] = {}
    provenance: dict[str, Mapping[str, Any]] = {}
    count = (len(ordered) + REFERENCE_BATCH_SIZE - 1) // REFERENCE_BATCH_SIZE
    missing_files = []
    for index in range(1, count + 1):
        ids = ordered[(index - 1) * REFERENCE_BATCH_SIZE:index * REFERENCE_BATCH_SIZE]
        path = output / f"openalex_reference_metadata_batch_v1_{index:04d}.json"
        if not path.exists():
            missing_files.append(str(path))
            continue
        batch = _load_reference_batch(path, run_sha256=run_sha256,
                                      batch_index=index, target_ids=ids)
        result = batch["acquisition_result"]
        prov = {key: result.get(key) for key in (
            "source", "api_version", "request_url", "retrieved_at_utc", "http_status",
            "cache_hit", "response_sha256",
        )}
        for row in result.get("records", []):
            work_id = canonical_openalex_work_id(row["id"])
            records[work_id] = row
            provenance[work_id] = prov
    return {"records_by_openalex_id": records, "provenance_by_openalex_id": provenance,
            "reference_id_count": len(ordered), "batch_count": count,
            "missing_batch_files": missing_files,
            "missing_openalex_ids": sorted(set(ordered) - set(records))}


def print_batch_progress(event: Mapping[str, Any]) -> None:
    print("Reference batch {batch_index}/{batch_count}: requested={requested}, retrieved={retrieved}, "
          "missing={missing}, cache_hit={cache_hit}, reused_existing_records={reused_existing_records}."
          .format(**event), flush=True)


def print_request_progress(event: Mapping[str, Any]) -> None:
    kind = event.get("event")
    if kind in {"cache_hit", "request", "retryable_response"}:
        print("OpenAlex {event}: {request_url}; status={http_status}; attempt={attempt}; wait={retry_after_seconds}."
              .format(event=kind, request_url=event.get("request_url"),
                      http_status=event.get("http_status"), attempt=event.get("attempt"),
                      retry_after_seconds=event.get("retry_after_seconds")), flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
