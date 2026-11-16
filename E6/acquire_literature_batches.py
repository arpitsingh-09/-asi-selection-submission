"""Resumable, append-only OpenAlex literature acquisition batches.

This prepares provisional candidates only. The existing literature eligibility
validator remains authoritative, including its requirement for verified
target-to-reference links.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from prepare_dataset import canonicalize_arxiv_id, canonicalize_records
from prepare_literature_testbed import (
    acquire_openalex_candidate_pool_from_e2,
    parse_utc_datetime,
    validate_literature_input_set,
)

BATCH_SIZE = 50
TARGET_ELIGIBLE_CANDIDATES = 120
BATCH_SCHEMA = "e6-openalex-literature-batch-v1"


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def eligible_source_targets(
    raw_source_records: Sequence[Mapping[str, Any]], *,
    focal_exclusion_ids: Iterable[str], development_manifest: Mapping[str, Any],
    cutoff_utc: str,
) -> list[dict[str, Any]]:
    """Return unique, nonexcluded, abstract-bearing E2 target records after cutoff."""
    cutoff = parse_utc_datetime(cutoff_utc)
    if cutoff is None:
        raise ValueError("cutoff_utc must be a timezone-aware ISO timestamp")
    reserved = development_manifest.get("reserved_development_ids")
    reserved_ids = reserved.get("paper_ids") if isinstance(reserved, Mapping) else None
    if not isinstance(reserved_ids, list):
        raise ValueError("development manifest lacks reserved development IDs")
    excluded = {canonicalize_arxiv_id(value) for value in focal_exclusion_ids}
    excluded.update(canonicalize_arxiv_id(value) for value in reserved_ids)

    aggregated = canonicalize_records(raw_source_records)
    targets: list[tuple[str, dict[str, Any]]] = []
    for paper_id, entry in aggregated["papers"].items():
        if paper_id in excluded:
            continue
        source = entry.get("canonical_record")
        if not isinstance(source, Mapping) or not isinstance(source.get("abstract"), str) \
                or not source["abstract"].strip():
            continue
        published = parse_utc_datetime(source.get("published"))
        if published is None or published <= cutoff:
            continue
        targets.append((paper_id, dict(source)))
    targets.sort(key=lambda item: item[0])
    return [record for _, record in targets]


def _write_json_exclusive(path: Path, value: Mapping[str, Any]) -> None:
    """Atomically create a JSON artifact without replacing an existing file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                         allow_nan=False) + "\n"
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=".e6-literature-batch-", suffix=".tmp", delete=False,
        ) as handle:
            temp_name = handle.name
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temp_name, path)
    except FileExistsError as exc:
        raise FileExistsError(f"refusing to overwrite completed batch: {path}") from exc
    finally:
        if temp_name is not None:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass


def _batch_digest(batch: Mapping[str, Any]) -> str:
    unsigned = {key: value for key, value in batch.items() if key != "batch_sha256"}
    return _canonical_hash(unsigned)


def _load_batch(path: Path, *, run_sha256: str, batch_index: int,
                target_ids: Sequence[str]) -> dict[str, Any]:
    try:
        batch = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"completed batch is unreadable: {path}") from exc
    if not isinstance(batch, dict) or batch.get("schema_version") != BATCH_SCHEMA:
        raise ValueError(f"unsupported batch artifact: {path}")
    if batch.get("run_sha256") != run_sha256 or batch.get("batch_index") != batch_index:
        raise ValueError(f"batch provenance does not match this acquisition: {path}")
    if batch.get("target_ids") != list(target_ids):
        raise ValueError(f"batch target order differs from deterministic source order: {path}")
    if batch.get("batch_sha256") != _batch_digest(batch):
        raise ValueError(f"batch content hash is invalid: {path}")
    if not isinstance(batch.get("acquisition_result"), Mapping):
        raise ValueError(f"batch acquisition result is missing: {path}")
    return batch


def _batch_counts(result: Mapping[str, Any], cutoff_utc: str) -> dict[str, int]:
    attempts = result.get("attempts", [])
    candidates = result.get("candidates", [])
    successful = sum(row.get("status") == "provisional_candidate_acquired"
                     for row in attempts if isinstance(row, Mapping))
    failures = sum(row.get("status") == "retrieval_failed"
                   for row in attempts if isinstance(row, Mapping))
    with_ten_abstracts = 0
    eligible = 0
    for row in candidates if isinstance(candidates, list) else []:
        if not isinstance(row, Mapping):
            continue
        audit = validate_literature_input_set(row, cutoff_utc)
        if audit.get("unique_reference_with_abstract_count", 0) >= 10:
            with_ten_abstracts += 1
        if audit.get("status") == "eligible_candidate":
            eligible += 1
    return {
        "targets_processed": len(attempts),
        "successful_openalex_matches": successful,
        "retrieval_failures": failures,
        "candidates_with_10_abstract_references": with_ten_abstracts,
        "genuinely_eligible_candidates": eligible,
    }


def reconcile_openalex_cache_offline(
    adapter: Any, raw_source_records: Sequence[Mapping[str, Any]], *,
    focal_exclusion_ids: Iterable[str], development_manifest: Mapping[str, Any],
    cutoff_utc: str, progress: Callable[[Mapping[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Resolve every eligible E2 target from cache only; never call the network."""
    targets = eligible_source_targets(
        raw_source_records, focal_exclusion_ids=focal_exclusion_ids,
        development_manifest=development_manifest, cutoff_utc=cutoff_utc,
    )
    rows = []
    counts = {"targets": len(targets), "cache_hits": 0, "cache_misses": 0,
              "exact_matches": 0, "empty_api_results": 0,
              "returned_but_unmatched": 0, "ambiguous_exact_matches": 0}
    from citation_sources import CitationCacheMiss, openalex_record_matches_arxiv_id

    for index, target in enumerate(targets, start=1):
        target_id = canonicalize_arxiv_id(target["paper_id"])
        try:
            response = adapter.resolve_by_arxiv_external_id(target_id)
        except CitationCacheMiss as exc:
            counts["cache_misses"] += 1
            row = {"target_arxiv_id": target_id, "status": "not_cached",
                   "request_url": exc.request_url}
        else:
            counts["cache_hits"] += int(response.get("cache_hit") is True)
            candidate_rows = response.get("candidate_matches", [])
            exact = [record for record in candidate_rows
                     if openalex_record_matches_arxiv_id(record, target_id)]
            raw = response.get("raw_response")
            api_results = raw.get("results", []) if isinstance(raw, Mapping) else []
            if len(exact) == 1:
                status = "exact_match"
                counts["exact_matches"] += 1
            elif len(exact) > 1:
                status = "ambiguous_exact_match"
                counts["ambiguous_exact_matches"] += 1
            elif not api_results:
                status = "empty_api_result"
                counts["empty_api_results"] += 1
            else:
                status = "returned_but_unmatched"
                counts["returned_but_unmatched"] += 1
            row = {
                "target_arxiv_id": target_id,
                "source_published": target.get("published"),
                "source_title": target.get("title"),
                "source_record_sha256": _canonical_hash(target),
                "status": status,
                "cache_hit": response.get("cache_hit") is True,
                "request_url": response.get("request_url"),
                "retrieved_at_utc": response.get("retrieved_at_utc"),
                "http_status": response.get("http_status"),
                "raw_response_sha256": _canonical_hash(raw),
                "api_result_count": len(api_results),
                "exact_openalex_records": exact,
            }
        rows.append(row)
        if progress is not None:
            progress({"index": index, "total": len(targets), "target_arxiv_id": target_id,
                      "status": row["status"], "cache_hit": row.get("cache_hit", False),
                      **counts})
    return {
        "schema_version": "e6-openalex-cache-reconciliation-v1",
        "status": "offline_cache_only",
        "cutoff_utc": cutoff_utc,
        "target_order": "ascending canonical arXiv ID after E2/focal/development/cutoff exclusions",
        "source_corpus": "E2/data/raw_papers.jsonl",
        "counts": counts,
        "rows": rows,
    }


def run_resumable_openalex_batches(
    adapter: Any, raw_source_records: Sequence[Mapping[str, Any]], *,
    focal_exclusion_ids: Iterable[str], development_manifest: Mapping[str, Any],
    cutoff_utc: str, output_dir: str | Path,
    progress: Callable[[Mapping[str, int]], None] | None = None,
    acquisition: Callable[..., Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Acquire in deterministic batches, reusing completed files and API cache.

    Only a completed batch is skipped on resume. An interrupted in-progress
    batch is retried; the append-only adapter cache reuses its successful API
    responses. The runner stops at 120 candidates accepted by the current
    strict eligibility validator, otherwise it exhausts the eligible targets.
    """
    if acquisition is None:
        acquisition = acquire_openalex_candidate_pool_from_e2
    if progress is None:
        progress = print_progress
    focal_exclusion_ids = sorted({canonicalize_arxiv_id(x) for x in focal_exclusion_ids})
    targets = eligible_source_targets(
        raw_source_records, focal_exclusion_ids=focal_exclusion_ids,
        development_manifest=development_manifest, cutoff_utc=cutoff_utc,
    )
    target_ids = [canonicalize_arxiv_id(row["paper_id"]) for row in targets]
    if len(target_ids) != len(set(target_ids)):
        raise ValueError("deterministic target source contains duplicate canonical IDs")
    run_sha = _canonical_hash({
        "matching_policy": "openalex-exact-arxiv-id-url-doi-v2",
        "cutoff_utc": cutoff_utc,
        "target_ids": target_ids,
        "target_record_hashes": [_canonical_hash(row) for row in targets],
        "focal_exclusion_ids": focal_exclusion_ids,
        "development_manifest_sha256": _canonical_hash(development_manifest),
        "batch_size": BATCH_SIZE,
    })
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    overall = {
        "targets_processed": 0,
        "successful_openalex_matches": 0,
        "retrieval_failures": 0,
        "candidates_with_10_abstract_references": 0,
        "genuinely_eligible_candidates": 0,
    }
    known_target_ids: set[str] = set()
    batch_count = (len(targets) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_index in range(1, batch_count + 1):
        start = (batch_index - 1) * BATCH_SIZE
        batch_targets = targets[start:start + BATCH_SIZE]
        batch_ids = target_ids[start:start + BATCH_SIZE]
        path = output / f"literature_openalex_batch_v1_{batch_index:04d}.json"
        if path.exists():
            batch = _load_batch(path, run_sha256=run_sha,
                                batch_index=batch_index, target_ids=batch_ids)
        else:
            try:
                result = acquisition(
                    adapter, batch_targets, focal_exclusion_ids=focal_exclusion_ids,
                    development_manifest=development_manifest,
                    generator_training_cutoff_utc=cutoff_utc,
                    max_targets=len(batch_targets),
                )
            except Exception as exc:
                if getattr(exc, "http_status", None) != 429:
                    raise
                retry_after = getattr(exc, "retry_after_seconds", None)
                pause = {"batch_index": batch_index, "batch_count": batch_count,
                         **overall, "status": "rate_limited_pause",
                         "retry_after_seconds": retry_after}
                progress(pause)
                return {"status": "rate_limited_pause", "batch_index": batch_index,
                        "run_sha256": run_sha, "retry_after_seconds": retry_after,
                        **overall, "output_dir": str(output),
                        "note": "successful requests remain in the append-only cache; rerun after Retry-After"}
            if not isinstance(result, Mapping):
                raise ValueError("acquisition callback must return an object")
            result = dict(result)
            candidate_ids = []
            for candidate in result.get("candidates", []):
                target = candidate.get("target") if isinstance(candidate, Mapping) else None
                if isinstance(candidate, Mapping) and isinstance(target, Mapping):
                    canonical_id = canonicalize_arxiv_id(target.get("paper_id"))
                    candidate_ids.append(canonical_id)
            if len(candidate_ids) != len(set(candidate_ids)):
                raise ValueError("acquisition batch contains duplicate target candidates")
            batch = {
                "schema_version": BATCH_SCHEMA,
                "run_sha256": run_sha,
                "batch_index": batch_index,
                "target_ids": batch_ids,
                "acquisition_result": result,
                "counts": _batch_counts(result, cutoff_utc),
            }
            batch["batch_sha256"] = _batch_digest(batch)
            _write_json_exclusive(path, batch)

        counts = batch.get("counts")
        if not isinstance(counts, Mapping):
            raise ValueError(f"batch counts missing: {path}")
        result = batch["acquisition_result"]
        for candidate in result.get("candidates", []):
            target = candidate.get("target") if isinstance(candidate, Mapping) else None
            if isinstance(target, Mapping):
                canonical_id = canonicalize_arxiv_id(target.get("paper_id"))
                if canonical_id in known_target_ids:
                    raise ValueError(f"duplicate target across completed batches: {canonical_id}")
                known_target_ids.add(canonical_id)
        for key in overall:
            overall[key] += int(counts[key])
        progress({"batch_index": batch_index, "batch_count": batch_count, **overall})
        if overall["genuinely_eligible_candidates"] >= TARGET_ELIGIBLE_CANDIDATES:
            return {"status": "target_met", "run_sha256": run_sha, **overall,
                    "batch_count": batch_index, "output_dir": str(output)}

    return {"status": "candidate_pool_exhausted", "run_sha256": run_sha, **overall,
            "batch_count": batch_count, "output_dir": str(output)}


def print_progress(counts: Mapping[str, int]) -> None:
    if counts.get("status") == "rate_limited_pause":
        print("Batch {batch_index}/{batch_count} paused for HTTP 429; Retry-After={retry_after_seconds}; "
              "completed targets={targets_processed}. Resume after the indicated delay."
              .format(**counts), flush=True)
        return
    print(
        "Batch {batch_index}/{batch_count}: targets processed={targets_processed}; "
        "successful OpenAlex matches={successful_openalex_matches}; "
        "retrieval failures={retrieval_failures}; candidates with >=10 abstract "
        "references={candidates_with_10_abstract_references}; "
        "genuinely_eligible={genuinely_eligible_candidates}."
        .format(**counts), flush=True,
    )


def print_cache_progress(event: Mapping[str, Any]) -> None:
    print("OpenAlex offline target {index}/{total}: status={status}; cache_hit={cache_hit}; "
          "target={target_arxiv_id}; cache hits={cache_hits}; misses={cache_misses}."
          .format(**event), flush=True)


def print_request_progress(event: Mapping[str, Any]) -> None:
    kind = event.get("event")
    if kind == "cache_hit":
        print("OpenAlex cache hit: {}".format(event.get("request_url")), flush=True)
    elif kind == "request":
        print("OpenAlex request attempt {}/{}: {}".format(
            event.get("attempt"), event.get("max_attempts"), event.get("request_url")
        ), flush=True)
    elif kind == "retryable_response":
        print("OpenAlex HTTP {}; retry wait {:.1f}s (attempt {}): {}".format(
            event.get("http_status"), event.get("retry_after_seconds", 0),
            event.get("attempt"), event.get("request_url")
        ), flush=True)


def main(argv: Sequence[str] | None = None) -> int:
    import argparse
    import csv

    from citation_sources import JsonFileCache, MemoryCache, OpenAlexAdapter
    from prepare_literature_testbed import acquire_openalex_candidate_pool_from_e2

    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--live-sample", type=int, choices=range(5, 11), metavar="N",
        help="freshly query N previously indexed exact-match examples; writes a separate sample artifact",
    )
    mode.add_argument("--offline-cache", action="store_true",
                      help="reconcile target lookups from cache only; no network fallback")
    args = parser.parse_args(argv)
    e6_root = Path(__file__).resolve().parent
    repository_root = e6_root.parent
    raw_path = repository_root / "E2/data/raw_papers.jsonl"
    raw_rows = [json.loads(line) for line in raw_path.read_text(encoding="utf-8").splitlines()
                if line.strip()]
    with (repository_root / "E2/data/focal_papers.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        focal_ids = [row["paper_id"] for row in csv.DictReader(handle) if row.get("paper_id")]
    development_manifest = json.loads(
        (e6_root / "data/development_manifest_v2.json").read_text(encoding="utf-8")
    )
    cache = e6_root / "data/openalex_literature_cache_v1"
    if args.offline_cache:
        output = e6_root / "data/literature_openalex_cache_reconciliation_v1.json"
        if output.exists():
            existing = json.loads(output.read_text(encoding="utf-8"))
            supplied = existing.get("reconciliation_sha256")
            unsigned = {key: value for key, value in existing.items()
                        if key != "reconciliation_sha256"}
            if supplied != _canonical_hash(unsigned):
                raise SystemExit(f"Existing offline report failed hash validation: {output}")
            print(json.dumps({"output": str(output), "reused_existing_report": True,
                              **existing.get("counts", {})}, indent=2))
            return 0
        adapter = OpenAlexAdapter(cache=JsonFileCache(cache), cache_only=True,
                                  progress_callback=None)
        result = reconcile_openalex_cache_offline(
            adapter, raw_rows, focal_exclusion_ids=focal_ids,
            development_manifest=development_manifest,
            cutoff_utc="2024-09-01T00:00:00Z",
            progress=lambda event: print_cache_progress(event),
        )
        result["reconciliation_sha256"] = _canonical_hash(result)
        _write_json_exclusive(output, result)
        print(json.dumps({"output": str(output), **result["counts"]}, indent=2))
        return 0
    if args.live_sample is not None:
        targets = eligible_source_targets(
            raw_rows, focal_exclusion_ids=focal_ids,
            development_manifest=development_manifest,
            cutoff_utc="2024-09-01T00:00:00Z",
        )
        known_exact_ids: set[str] = set()
        previous = e6_root / "data/literature_openalex_batches_v1"
        from citation_sources import openalex_record_matches_arxiv_id

        for batch_path in sorted(previous.glob("literature_openalex_batch_v1_*.json")):
            batch = json.loads(batch_path.read_text(encoding="utf-8"))
            result = batch.get("acquisition_result", {})
            for unresolved in result.get("unresolved_matches", []):
                requested = unresolved.get("canonical_target_paper_id")
                if any(openalex_record_matches_arxiv_id(row, requested)
                       for row in unresolved.get("candidate_matches", [])):
                    known_exact_ids.add(requested)
        selected = [row for row in targets
                    if canonicalize_arxiv_id(row.get("paper_id")) in known_exact_ids]
        if len(selected) < args.live_sample:
            raise SystemExit(
                f"only {len(selected)} cached exact-match examples are available; "
                "cannot run the requested live validation sample"
            )
        selected = selected[:args.live_sample]
        output = e6_root / "data" / (
            f"literature_openalex_live_sample_v2_{args.live_sample}.json"
        )
        if output.exists():
            raise SystemExit(f"Refusing to overwrite existing sample output: {output}")
        # No cache on this adapter: the sample exercises fresh API responses.
        adapter = OpenAlexAdapter(cache=MemoryCache(), max_attempts=1,
                                  progress_callback=print_request_progress)
        from citation_sources import openalex_record_matches_arxiv_id

        resolution_checks = []
        for target in selected:
            target_id = canonicalize_arxiv_id(target["paper_id"])
            resolution = adapter.resolve_by_arxiv_external_id(target_id)
            exact_matches = [row for row in resolution.get("candidate_matches", [])
                             if openalex_record_matches_arxiv_id(row, target_id)]
            resolution_checks.append({
                "target_arxiv_id": target_id,
                "http_status": resolution.get("http_status"),
                "exact_match_count": len(exact_matches),
                "request_url": resolution.get("request_url"),
                "retrieved_at_utc": resolution.get("retrieved_at_utc"),
                "raw_response_sha256": _canonical_hash(resolution.get("raw_response")),
            })
        sample_result = acquire_openalex_candidate_pool_from_e2(
            adapter, selected, focal_exclusion_ids=focal_ids,
            development_manifest=development_manifest,
            generator_training_cutoff_utc="2024-09-01T00:00:00Z",
            max_targets=len(selected),
        )
        successful = sum(row["exact_match_count"] == 1 for row in resolution_checks)
        with_10 = sum(
            isinstance(row.get("eligibility_audit"), Mapping)
            and row["eligibility_audit"].get("unique_reference_with_abstract_count", 0) >= 10
            for row in sample_result.get("candidates", [])
        )
        eligible = sum(
            row.get("eligibility_audit", {}).get("status") == "eligible_candidate"
            for row in sample_result.get("candidates", [])
        )
        _write_json_exclusive(output, {
            "schema_version": "e6-openalex-live-validation-sample-v2",
            "requested_sample_size": args.live_sample,
            "target_ids": [row["paper_id"] for row in selected],
            "resolution_checks": resolution_checks,
            "acquisition_result": sample_result,
            "summary": {"successful_exact_matches": successful,
                        "candidates_with_10_abstract_references": with_10,
                        "genuinely_eligible_candidates": eligible},
        })
        print(json.dumps({"output": str(output), "targets_requested": args.live_sample,
                          "successful_exact_matches": successful,
                          "candidates_with_10_abstract_references": with_10,
                          "genuinely_eligible_candidates": eligible}, indent=2))
        return 0 if successful == args.live_sample else 2

    output = e6_root / "data/literature_openalex_batches_v2"
    adapter = OpenAlexAdapter(cache=JsonFileCache(cache), max_attempts=3,
                              timeout_seconds=15,
                              progress_callback=print_request_progress)
    result = run_resumable_openalex_batches(
        adapter, raw_rows, focal_exclusion_ids=focal_ids,
        development_manifest=development_manifest,
        cutoff_utc="2024-09-01T00:00:00Z", output_dir=output,
    )
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["status"] == "target_met" else 2


if __name__ == "__main__":
    raise SystemExit(main())
