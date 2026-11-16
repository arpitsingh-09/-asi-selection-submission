"""Build an approval-pending deterministic sample proposal from eligible literature candidates.

No network access or model calls are made. The proposal never marks a sample
selected or frozen; an approved decision must be recorded before execution.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from prepare_literature_testbed import (
    REQUIRED_MANUAL_CHECKS,
    MINIMUM_INPUT_SETS,
    validate_literature_input_set,
    extract_literature_target_annotations,
    build_manual_extraction_review_worklist,
    write_manifest_exclusive,
)
from prepare_dataset import canonicalize_arxiv_id
from citation_sources import normalize_openalex_work, openalex_record_matches_arxiv_id

ROOT = Path(__file__).resolve().parent
DEFAULT_CANDIDATE_MANIFEST = ROOT / "data/literature_citation_verified_manifest_v1.json"
DEFAULT_PROPOSAL_PATH = ROOT / "data/literature_sample_proposal_v1.json"
PROPOSAL_SCHEMA = "e6-literature-sample-proposal-v1"
SAMPLE_RULE_ID = "sha256_rank_input_set_id_v1"
SAMPLE_KEY_FORMAT = "E6-LITERATURE-SAMPLE-v1|{seed}|{input_set_id}"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _project_exclusion_ids() -> tuple[set[str], set[str], dict[str, str]]:
    repository = ROOT.parent
    focal_path = repository / "E2/data/focal_papers.csv"
    development_path = ROOT / "data/development_manifest_v2.json"
    try:
        with focal_path.open(encoding="utf-8", newline="") as handle:
            focal_raw = [row["paper_id"] for row in csv.DictReader(handle) if row.get("paper_id")]
        development = json.loads(development_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot verify current focal/development exclusions: {exc}") from exc
    focal = {canonicalize_arxiv_id(value) for value in focal_raw}
    reserved = development.get("reserved_development_ids", {}).get("paper_ids")
    if not isinstance(reserved, list):
        raise ValueError("development exclusion manifest lacks reserved paper IDs")
    development_ids = {canonicalize_arxiv_id(value) for value in reserved}
    hashes = {
        "focal_exclusion_file_sha256": hashlib.sha256(focal_path.read_bytes()).hexdigest(),
        "development_manifest_sha256": hashlib.sha256(
            development_path.read_bytes()
        ).hexdigest(),
    }
    return focal, development_ids, hashes


def validate_candidate_manifest(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Verify manifest integrity and independently recheck every candidate."""
    if not isinstance(manifest, Mapping):
        raise ValueError("candidate manifest must be an object")
    if manifest.get("schema_version") != "e6-literature-citation-verified-manifest-v1":
        raise ValueError("unsupported literature candidate manifest schema")
    supplied_hash = manifest.get("manifest_sha256")
    unsigned = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    if supplied_hash != canonical_hash(unsigned):
        raise ValueError("literature candidate manifest hash mismatch")
    rows = manifest.get("input_sets")
    if not isinstance(rows, list):
        raise ValueError("candidate manifest input_sets must be a list")
    if manifest.get("eligible_input_set_count") != len(rows):
        raise ValueError("candidate manifest count differs from input_sets")
    cutoff = manifest.get("generator_training_cutoff_utc")
    focal_ids, development_ids, _ = _project_exclusion_ids()
    ids: set[str] = set()
    targets: set[str] = set()
    valid = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise ValueError(f"candidate row {index} must be an object")
        audit = validate_literature_input_set(row, cutoff)
        if audit.get("status") != "eligible_candidate":
            raise ValueError(f"candidate row {index} fails eligibility: {audit.get('errors')}")
        input_id = row.get("input_set_id")
        target_id = (row.get("target") or {}).get("paper_id")
        if input_id in ids or target_id in targets:
            raise ValueError(f"candidate row {index} duplicates an input-set or target ID")
        ids.add(input_id)
        targets.add(target_id)
        canonical_target = canonicalize_arxiv_id(target_id)
        if canonical_target in focal_ids:
            raise ValueError(f"candidate row {index} is in the focal-paper exclusion")
        if canonical_target in development_ids:
            raise ValueError(f"candidate row {index} is reserved for development")
        if row.get("reference_links_verified") is not True:
            raise ValueError(f"candidate row {index} lacks verified citation edges")
        target_record = row.get("target", {}).get("openalex_target_record")
        if not isinstance(target_record, Mapping) or not openalex_record_matches_arxiv_id(
            target_record, target_id
        ):
            raise ValueError(f"candidate row {index} lacks an exact arXiv-matched target record")
        target_openalex_id = target_record.get("id")
        raw_edge_ids = target_record.get("referenced_works")
        if not isinstance(raw_edge_ids, list):
            raise ValueError(f"candidate row {index} target has no referenced_works list")
        expected_edges = {value for value in raw_edge_ids if isinstance(value, str)}
        if target_openalex_id in expected_edges:
            expected_edges.remove(target_openalex_id)
        edge_rows = row.get("citation_edges")
        if not isinstance(edge_rows, list):
            raise ValueError(f"candidate row {index} has no source citation-edge records")
        edge_by_id = {}
        for edge in edge_rows:
            if not isinstance(edge, Mapping):
                raise ValueError(f"candidate row {index} contains a malformed citation edge")
            edge_id = edge.get("openalex_id")
            if (edge.get("edge_verified") is not True
                    or edge.get("edge_source_field") != "referenced_works"
                    or edge.get("edge_source_target_openalex_id") != target_openalex_id):
                raise ValueError(f"candidate row {index} has an unverified citation edge")
            if not isinstance(edge_id, str) or edge_id in edge_by_id:
                raise ValueError(f"candidate row {index} has a missing/duplicate edge ID")
            edge_by_id[edge_id] = edge
        if set(edge_by_id) != expected_edges:
            raise ValueError(f"candidate row {index} edge records differ from target referenced_works")
        if not isinstance(row.get("reference_link_provenance"), Mapping) or (
            row["reference_link_provenance"].get("target_openalex_id") != target_openalex_id
            or row["reference_link_provenance"].get("edge_source_field") != "referenced_works"
        ):
            raise ValueError(f"candidate row {index} citation-link provenance does not bind to target")
        reference_ids = set()
        for reference in row.get("references", []):
            if not isinstance(reference, Mapping):
                raise ValueError(f"candidate row {index} has malformed reference metadata")
            openalex_id = reference.get("openalex_id")
            if openalex_id not in edge_by_id or openalex_id in reference_ids:
                raise ValueError(f"candidate row {index} reference is not a unique verified citation")
            edge = edge_by_id[openalex_id]
            source_record = reference.get("source_record")
            if not isinstance(source_record, Mapping) or source_record.get("id") != openalex_id:
                raise ValueError(f"candidate row {index} reference record ID mismatch")
            normalized = normalize_openalex_work(source_record)
            if normalized.get("abstract") != reference.get("abstract") or not reference.get("abstract"):
                raise ValueError(f"candidate row {index} reference abstract does not match source metadata")
            if (edge.get("abstract_available") is not True
                    or edge.get("source_record_sha256") != canonical_hash(source_record)
                    or edge.get("metadata_status") != "retrieved_with_abstract"):
                raise ValueError(f"candidate row {index} reference is not provenance-verified")
            retrieval = reference.get("metadata_retrieval_provenance")
            if (not isinstance(retrieval, Mapping) or not retrieval.get("request_url")
                    or not retrieval.get("retrieved_at_utc")
                    or not retrieval.get("response_sha256")):
                raise ValueError(f"candidate row {index} reference retrieval provenance is incomplete")
            reference_ids.add(openalex_id)
        valid.append(dict(row))
    if manifest.get("input_sets_selected") is not False or manifest.get("input_sets_frozen") is not False:
        raise ValueError("candidate pool must remain unselected and unfrozen")
    return valid


def build_literature_sample_proposal(
    candidate_manifest: Mapping[str, Any], *, sample_size: int, seed: int,
) -> dict[str, Any]:
    """Rank eligible candidates by a salted hash and return a pending proposal."""
    if type(sample_size) is not int or sample_size < MINIMUM_INPUT_SETS:
        raise ValueError(f"sample_size must be at least {MINIMUM_INPUT_SETS}")
    if type(seed) is not int or seed < 0:
        raise ValueError("seed must be a nonnegative integer")
    eligible = validate_candidate_manifest(candidate_manifest)
    if sample_size > len(eligible):
        raise ValueError(f"requested {sample_size} sets but only {len(eligible)} are eligible")
    ranked = []
    for row in eligible:
        key = SAMPLE_KEY_FORMAT.format(seed=seed, input_set_id=row["input_set_id"])
        rank = hashlib.sha256(key.encode("utf-8")).hexdigest()
        ranked.append((rank, row["input_set_id"], row))
    ranked.sort(key=lambda item: (item[0], item[1]))
    chosen = ranked[:sample_size]
    proposed_rows = [{
        "rank_index": index,
        "input_set_id": row["input_set_id"],
        "target_paper_id": row["target"]["paper_id"],
        "candidate_record_sha256": canonical_hash(row),
        "selection_key_sha256": rank,
    } for index, (rank, _, row) in enumerate(chosen, start=1)]
    unsigned = {
        "schema_version": PROPOSAL_SCHEMA,
        "proposal_status": "pending_researcher_approval",
        "approval_required": True,
        "sample_selected": False,
        "sample_frozen": False,
        "source_manifest_path": "E6/data/literature_citation_verified_manifest_v1.json",
        "source_manifest_sha256": candidate_manifest["manifest_sha256"],
        "exclusion_hashes": dict(_project_exclusion_ids()[2]),
        "source_eligible_candidate_count": len(eligible),
        "minimum_required_sample_size": MINIMUM_INPUT_SETS,
        "proposed_sample_size": sample_size,
        "selection_rule_id": SAMPLE_RULE_ID,
        "selection_key_format": SAMPLE_KEY_FORMAT,
        "selection_seed": seed,
        "selection_order": "ascending SHA-256 key, then input_set_id as deterministic collision tie-break",
        "stratification": "none; no repository-approved strata are configured",
        "proposed_sample": proposed_rows,
        "proposed_input_set_ids": [row["input_set_id"] for row in proposed_rows],
        "proposed_manual_review_input_set_ids": [
            row["input_set_id"] for row in proposed_rows[:REQUIRED_MANUAL_CHECKS]
        ],
        "manual_review_case_count": REQUIRED_MANUAL_CHECKS,
        "manual_review_status": "not_started; requires successful extractions and human checks",
        "decision_note": "Hash ranking is a recommendation only; it does not approve or freeze this sample.",
    }
    proposal = dict(unsigned)
    proposal["proposal_sha256"] = canonical_hash(unsigned)
    return proposal


def verify_sample_proposal(
    candidate_manifest: Mapping[str, Any], proposal: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Resolve proposal IDs to source candidates while verifying both hashes."""
    if not isinstance(proposal, Mapping) or proposal.get("schema_version") != PROPOSAL_SCHEMA:
        raise ValueError("unsupported sample proposal")
    unsigned = {key: value for key, value in proposal.items() if key != "proposal_sha256"}
    if proposal.get("proposal_sha256") != canonical_hash(unsigned):
        raise ValueError("sample proposal hash mismatch")
    expected = build_literature_sample_proposal(
        candidate_manifest, sample_size=proposal.get("proposed_sample_size"),
        seed=proposal.get("selection_seed"),
    )
    # Legacy v1 proposals predate exclusion_hashes. Candidate validation above
    # still applies today's exact exclusions; preserve that original artifact.
    if "exclusion_hashes" not in proposal:
        expected.pop("exclusion_hashes")
        expected["proposal_sha256"] = canonical_hash({
            key: value for key, value in expected.items() if key != "proposal_sha256"})
    if dict(proposal) != expected:
        raise ValueError("sample proposal differs from deterministic sampling and review policy")
    candidates = validate_candidate_manifest(candidate_manifest)
    if proposal.get("source_manifest_sha256") != candidate_manifest.get("manifest_sha256"):
        raise ValueError("sample proposal points to a different candidate manifest")
    by_id = {row["input_set_id"]: row for row in candidates}
    output = []
    for item in proposal.get("proposed_sample", []):
        if not isinstance(item, Mapping):
            raise ValueError("sample proposal row must be an object")
        input_id = item.get("input_set_id")
        row = by_id.get(input_id)
        if row is None or canonical_hash(row) != item.get("candidate_record_sha256"):
            raise ValueError(f"proposed candidate missing or changed: {input_id}")
        output.append(dict(row))
    if [row["input_set_id"] for row in output] != proposal.get("proposed_input_set_ids"):
        raise ValueError("proposal ID order does not match proposed sample rows")
    if proposal.get("sample_selected") is not False or proposal.get("sample_frozen") is not False:
        raise ValueError("proposal must not claim selection or freeze")
    return output


def extract_proposed_literature_sample(
    candidate_manifest: Mapping[str, Any], proposal: Mapping[str, Any], model_client: Any, *,
    model_configuration: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Run existing fixed-prompt extraction only when explicitly called by a caller."""
    candidates = verify_sample_proposal(candidate_manifest, proposal)
    return extract_literature_target_annotations(
        candidates, model_client, model_configuration=model_configuration,
    )


def build_literature_extraction_manifest(
    proposal: Mapping[str, Any], extracted_candidates: Sequence[Mapping[str, Any]], *,
    model_configuration: Mapping[str, Any],
) -> dict[str, Any]:
    """Package real caller-produced extractions without treating them as gold truth."""
    if not isinstance(proposal, Mapping) or proposal.get("schema_version") != PROPOSAL_SCHEMA:
        raise ValueError("unsupported sample proposal")
    proposal_unsigned = {key: value for key, value in proposal.items()
                         if key != "proposal_sha256"}
    if proposal.get("proposal_sha256") != canonical_hash(proposal_unsigned):
        raise ValueError("sample proposal hash mismatch")
    if proposal.get("sample_selected") is not False or proposal.get("sample_frozen") is not False:
        raise ValueError("extraction packaging accepts only an unfrozen proposal")
    if not isinstance(model_configuration, Mapping):
        raise ValueError("model_configuration must be an object")
    expected_ids = proposal.get("proposed_input_set_ids") if isinstance(proposal, Mapping) else None
    if (not isinstance(expected_ids, list) or not expected_ids
            or len(set(expected_ids)) != len(expected_ids)):
        raise ValueError("sample proposal must contain proposed_input_set_ids")
    if not isinstance(extracted_candidates, Sequence) or isinstance(extracted_candidates, (str, bytes)):
        raise ValueError("extracted_candidates must be a sequence")
    by_id = {}
    for row in extracted_candidates:
        if not isinstance(row, Mapping):
            raise ValueError("each extracted candidate must be an object")
        input_id = row.get("input_set_id")
        if input_id in by_id:
            raise ValueError(f"duplicate extracted input_set_id: {input_id}")
        if not isinstance(row.get("target_extraction"), Mapping):
            raise ValueError(f"{input_id} is missing target_extraction")
        by_id[input_id] = dict(row)
    if set(by_id) != set(expected_ids):
        raise ValueError("extraction candidate IDs must exactly match the proposed sample")
    rows = [by_id[input_id] for input_id in expected_ids]
    unsigned = {
        "schema_version": "e6-literature-target-extraction-manifest-v1",
        "status": "pending_manual_validation",
        "approval_required": True,
        "sample_proposal_sha256": proposal.get("proposal_sha256"),
        "candidate_manifest_sha256": proposal.get("source_manifest_sha256"),
        "proposed_input_set_ids": list(expected_ids),
        "model_configuration": dict(model_configuration),
        "target_extractions": rows,
        "successful_extraction_count": sum(
            row["target_extraction"].get("status") == "succeeded" for row in rows
        ),
        "failed_extraction_count": sum(
            row["target_extraction"].get("status") != "succeeded" for row in rows
        ),
        "manual_validation_status": "not_started",
        "target_extractions_are_gold_truth": False,
    }
    output = dict(unsigned)
    output["manifest_sha256"] = canonical_hash(unsigned)
    return output


def build_proposed_manual_review_worklist(
    extracted_candidates: Sequence[Mapping[str, Any]], proposal: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the existing human-review form for the proposal's first 20 ranked cases."""
    if not isinstance(proposal, Mapping) or proposal.get("schema_version") != PROPOSAL_SCHEMA:
        raise ValueError("unsupported sample proposal")
    proposal_unsigned = {key: value for key, value in proposal.items()
                         if key != "proposal_sha256"}
    if proposal.get("proposal_sha256") != canonical_hash(proposal_unsigned):
        raise ValueError("sample proposal hash mismatch")
    expected_sample_ids = proposal.get("proposed_input_set_ids")
    ids = proposal.get("proposed_manual_review_input_set_ids")
    if (not isinstance(expected_sample_ids, list)
            or not isinstance(ids, list)
            or ids != expected_sample_ids[:REQUIRED_MANUAL_CHECKS]
            or len(ids) != REQUIRED_MANUAL_CHECKS):
        raise ValueError("proposal must identify exactly 20 pending manual review cases")
    extracted_ids = [row.get("input_set_id") for row in extracted_candidates
                     if isinstance(row, Mapping)]
    if (len(extracted_ids) != len(expected_sample_ids)
            or set(extracted_ids) != set(expected_sample_ids)):
        raise ValueError("manual-review extractions must exactly match the proposed sample")
    worklist = build_manual_extraction_review_worklist(extracted_candidates, ids)
    worklist["case_selection_and_adjudication_policy"] = (
        "proposed hash-rank prefix from pending literature sample; researcher approval required"
    )
    worklist["selection_proposal_sha256"] = proposal.get("proposal_sha256")
    worklist["status"] = "pending_manual_review_and_policy_approval"
    unsigned = {key: value for key, value in worklist.items() if key != "worklist_sha256"}
    worklist["worklist_sha256"] = canonical_hash(unsigned)
    return worklist


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-manifest", type=Path, default=DEFAULT_CANDIDATE_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_PROPOSAL_PATH)
    parser.add_argument("--sample-size", type=int, default=100)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(args.candidate_manifest.read_text(encoding="utf-8"))
        proposal = build_literature_sample_proposal(
            manifest, sample_size=args.sample_size, seed=args.seed,
        )
        write_manifest_exclusive(args.output, proposal)
    except (OSError, json.JSONDecodeError, ValueError, FileExistsError) as exc:
        parser.error(str(exc))
    print(json.dumps({"proposal_path": str(args.output),
                      "proposal_status": proposal["proposal_status"],
                      "proposed_sample_size": proposal["proposed_sample_size"],
                      "eligible_candidate_count": proposal["source_eligible_candidate_count"],
                      "proposal_sha256": proposal["proposal_sha256"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
