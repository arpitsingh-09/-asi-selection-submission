#!/usr/bin/env python3
"""Create deterministic, non-scoring manipulations for authorized A1 focals."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from M.a1_replication.controls import _digest, build_controls


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
COHORT_FILE = HERE / "cohort_manifest.json"
EXTRACTION_FILE = HERE / "claim_extraction_qwen3_v1.jsonl"
REVIEW_FILE = HERE / "A1_HUMAN_REVIEW_FORM_PAPERS_1_2.md"
INDEPENDENCE_FILE = HERE / "A1_REVIEWER_INDEPENDENCE_ADDENDUM.md"
AUTHORIZATION_FILE = HERE / "A1_SCORING_AUTHORIZATION_2026-11-14.md"
REGISTRATION_FILE = HERE / "PREREG_REPLICATION.md"
AMENDMENT_FILE = HERE / "AMENDMENT_003_PARTIAL_CONTROLS.md"
RAW_FILE = ROOT / "E2" / "data" / "raw_papers.jsonl"
POOL_FILE = ROOT / "E2" / "data" / "pool_manifest.csv"
OUTPUT_FILE = HERE / "A1_AUTHORIZED_MANIPULATIONS_V1.json"
REPORT_FILE = HERE / "A1_AUTHORIZED_MANIPULATIONS_VALIDATION_V1.json"

AUTHORIZED_IDS = ("2512.23709v3", "2610.29385v1")
COVERAGE_LEVELS = (25, 50, 75, 100)
MANIPULATION_SEED = "sha256:E2-manipulations-v1"
BOOTSTRAP_SEED = 20261113
REVIEWER_ID = "AS-01"
REVIEW_DATE = "2026-11-14"


class ReadinessError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_id(*parts: Any) -> str:
    value = "|".join(map(str, parts))
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:20]
    return f"e2synthetic:{digest}"


def parse_time(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ReadinessError(f"Missing publication timestamp: {value!r}")
    cleaned = value.strip()
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    result = datetime.fromisoformat(cleaned)
    if result.tzinfo is None:
        raise ReadinessError("Publication timestamps must include a timezone")
    return result.astimezone(timezone.utc)


def isoformat(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def read_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ReadinessError(f"Invalid JSON at {path}:{line_number}") from exc
    return records


def _one_checked_choice(line: str, field: str, choices: tuple[str, ...]) -> str:
    prefix = f"- {field}:"
    if not line.startswith(prefix):
        raise ReadinessError(f"Missing {field} decision")
    checked = re.findall(r"\[([x ])\]\s*([^[]+?)(?=\s+\[|$)", line[len(prefix):])
    selected = [label.strip() for mark, label in checked if mark == "x"]
    if len(selected) != 1 or selected[0] not in choices:
        raise ReadinessError(f"{field} must have exactly one valid human judgment")
    return selected[0]


def parse_review(review_text: str, extraction: dict, source: dict,
                 independence_text: str) -> list[dict]:
    if f"Reviewer ID/code: {REVIEWER_ID}" not in review_text:
        raise ReadinessError("Human review does not identify reviewer AS-01")
    if f"Review date: {REVIEW_DATE}" not in review_text:
        raise ReadinessError("Human review date does not match the authorized review")
    if REVIEWER_ID not in independence_text or "did not produce or contribute" not in independence_text:
        raise ReadinessError("Independent non-extractor attestation is missing")
    for paper_id in AUTHORIZED_IDS:
        if paper_id not in independence_text:
            raise ReadinessError(f"Independence attestation omits {paper_id}")

    section_matches = list(re.finditer(
        r"(?ms)^## Paper \d+ — .*?(?=^## Paper \d+ — |\Z)", review_text
    ))
    section = next(
        (match.group(0) for match in section_matches
         if f"- Paper ID: `{extraction['paper_id']}`" in match.group(0)),
        None,
    )
    if section is None:
        raise ReadinessError(f"No human review section for {extraction['paper_id']}")

    abstract_match = re.search(
        r"(?ms)^### Original abstract \(verbatim\)\s*\n\n(.*?)(?=^### Claim 1\s*$)",
        section,
    )
    if abstract_match is None:
        raise ReadinessError("Original abstract is missing from the review form")
    reviewed_abstract = re.sub(r"(?m)^> ?", "", abstract_match.group(1)).rstrip()
    if reviewed_abstract != source.get("abstract", "").rstrip():
        raise ReadinessError("Reviewed abstract differs from the original source abstract")

    extraction_claims = extraction["extractor_result"]["claims"]
    blocks = re.split(r"(?m)^### Claim (\d+)\s*$", section)[1:]
    if len(blocks) % 2:
        raise ReadinessError("Malformed claim review sections")
    decisions = []
    for offset in range(0, len(blocks), 2):
        claim_number = int(blocks[offset])
        body = blocks[offset + 1]
        claim_match = re.search(r"(?m)^\*\*Claim:\*\* (.+)$", body)
        evidence_match = re.search(
            r"(?m)^\*\*Supporting evidence excerpt:\*\* “(.*)”$", body
        )
        if claim_match is None or evidence_match is None:
            raise ReadinessError(f"Claim {claim_number} is missing claim or source excerpt")
        if claim_number != len(decisions) + 1 or claim_number > len(extraction_claims):
            raise ReadinessError("Review claim numbering/order differs from extraction")
        claim = claim_match.group(1)
        evidence = evidence_match.group(1)
        source_claim = extraction_claims[claim_number - 1]
        if claim != source_claim.get("claim") or evidence != source_claim.get("evidence"):
            raise ReadinessError(f"Claim {claim_number} differs from extraction evidence")
        if evidence not in source.get("abstract", ""):
            raise ReadinessError(f"Claim {claim_number} evidence is not in the original abstract")

        support_line = next(
            (line for line in body.splitlines() if line.startswith("- Semantic support:")),
            "",
        )
        atomicity_line = next(
            (line for line in body.splitlines() if line.startswith("- Atomicity:")),
            "",
        )
        support = _one_checked_choice(
            support_line, "Semantic support", ("Supported", "Unsupported", "Unclear")
        )
        atomicity = _one_checked_choice(
            atomicity_line, "Atomicity", ("Atomic", "Compound", "Unclear")
        )
        rationale_match = re.search(
            r"(?m)^- Rationale: (.+)$", body
        )
        if rationale_match is None or not rationale_match.group(1).strip():
            raise ReadinessError(f"Claim {claim_number} has no human rationale")
        decisions.append({
            "reviewer_id": REVIEWER_ID,
            "review_date": REVIEW_DATE,
            "claim_number": claim_number,
            "claim": claim,
            "evidence": evidence,
            "semantic_support": support,
            "atomicity": atomicity,
            "rationale": rationale_match.group(1).strip(),
        })

    if len(decisions) != len(extraction_claims):
        raise ReadinessError("Human review does not cover every extracted claim")
    retained = [
        row for row in decisions
        if row["semantic_support"] == "Supported" and row["atomicity"] == "Atomic"
    ]
    normalized = [" ".join(row["claim"].lower().split()) for row in retained]
    if len(normalized) != len(set(normalized)):
        raise ReadinessError("Retained human-approved claims are not distinct")
    if not 4 <= len(retained) <= 10:
        raise ReadinessError(
            f"{extraction['paper_id']} has {len(retained)} retained claims; expected 4–10"
        )
    return retained


def source_pool_ids(pool_name: str, focal_id: str, cutoff: datetime,
                    pool_ids_by_name: dict[str, set[str]],
                    papers: dict[str, dict]) -> list[str]:
    eligible = []
    for paper_id in sorted(pool_ids_by_name.get(pool_name, set()) - {focal_id}):
        paper = papers.get(paper_id)
        if paper is None:
            raise ReadinessError(f"Pool manifest references unknown paper {paper_id}")
        if not (paper.get("title") or paper.get("abstract")):
            continue
        if parse_time(paper.get("published")) < cutoff:
            eligible.append(paper_id)
    return eligible


def synthetic_record(focal: dict, condition: str, slot: str,
                     title: str, abstract: str, timestamp: str) -> dict:
    paper_id = stable_id(
        MANIPULATION_SEED, focal["pool"], focal["paper_id"], condition, slot
    )
    return {
        "paper_id": paper_id,
        "title": title,
        "abstract": abstract,
        "published": timestamp,
        "updated": timestamp,
        "authors": [],
        "categories": [],
        "primary_pool_category": focal["pool"],
        "paper_url": "",
        "source": "A1 supplementary synthetic manipulation; not a real publication",
        "pool": focal["pool"],
        "synthetic_manipulation": True,
        "synthetic_condition": condition,
        "synthetic_seed": MANIPULATION_SEED,
    }


def build_manipulations(focal: dict, claims: list[dict], original_ids: list[str],
                        controls: list[dict]) -> tuple[list[dict], list[dict]]:
    paper_id = focal["paper_id"]
    pool = focal["pool"]
    cutoff = parse_time(focal["published"])
    synthetic_time = isoformat(cutoff - timedelta(seconds=1))
    claim_texts = [row["claim"] for row in claims]
    source_claims = [
        {"claim_number": row["claim_number"], "claim": row["claim"],
         "evidence": row["evidence"]}
        for row in claims
    ]
    by_condition = {row["condition"]: row for row in controls}
    if "original" not in by_condition or by_condition["original"]["input_paper_ids"] != original_ids:
        raise ReadinessError("Original control does not match manipulation base pool")

    synthetic = []
    cases = []

    def add_case(condition: str, level: Optional[int], selected: list[int],
                 synthetic_rows: list[dict], metadata: dict) -> None:
        ids = [row["paper_id"] for row in synthetic_rows]
        case_id = stable_id("case-v1", pool, paper_id, condition, level or "")
        cases.append({
            "case_id": case_id,
            "pool": pool,
            "focal_paper_id": paper_id,
            "published": focal["published"],
            "t": focal["published"],
            "idea_text": f"{focal['title']}\n\n{focal['abstract']}",
            "claims": claim_texts,
            "source_claims": source_claims,
            "pool_ids": original_ids + ids,
            "manipulation": condition,
            "coverage_percent": level,
            "expected_direction": {
                "Y": "reference" if condition == "baseline" else "decrease",
                "N": "reference" if condition == "baseline" else "decrease",
                "yours": "reference" if condition == "baseline" else "decrease",
                "density": "reference" if condition == "baseline" else "decrease",
            },
            "metadata": {
                **metadata,
                "selected_claim_numbers": [claims[index]["claim_number"] for index in selected],
                "synthetic_paper_ids": ids,
            },
            "scoring_status": "not_scored",
            "control_record_id": by_condition["original"]["record_id"],
        })
        synthetic.extend(synthetic_rows)

    add_case("baseline", None, [], [], {
        "claim_selection": "none; unmanipulated original pool reference",
    })
    for percent in COVERAGE_LEVELS:
        count = max(1, math.ceil(len(claim_texts) * percent / 100))
        selected = list(range(count))
        planted = [claim_texts[index] for index in selected]
        record = synthetic_record(
            focal, f"coverage_{percent}", "planted",
            f"Synthetic prior work: {percent}% claim coverage",
            "\n".join(planted), synthetic_time,
        )
        add_case(f"coverage_{percent}", percent, selected, [record], {
            "planted_claim_count": count,
            "total_claim_count": len(claim_texts),
            "claim_selection": "first_n_in_human-approved extraction order",
        })

    concentrated = synthetic_record(
        focal, "concentrated", "all_claims",
        "Synthetic prior work: concentrated claim coverage",
        "\n".join(claim_texts), synthetic_time,
    )
    add_case("concentrated", None, list(range(len(claim_texts))), [concentrated], {
        "planted_claim_count": len(claim_texts),
    })

    distributed_rows = [
        synthetic_record(
            focal, "distributed", f"claim_{index + 1}",
            f"Synthetic prior work: claim {index + 1}", claim, synthetic_time,
        )
        for index, claim in enumerate(claim_texts)
    ]
    add_case("distributed", None, list(range(len(claim_texts))), distributed_rows, {
        "planted_claim_count": len(claim_texts),
        "claim_placement": "one claim per synthetic prior-work item",
    })
    return cases, synthetic


def validate_generated(focal_data: dict[str, dict], cases: list[dict],
                       synthetic: list[dict]) -> None:
    synthetic_by_id = {row["paper_id"]: row for row in synthetic}
    if len(synthetic_by_id) != len(synthetic):
        raise ReadinessError("Synthetic paper IDs are not unique")

    for paper_id in AUTHORIZED_IDS:
        focal_record = focal_data[paper_id]
        focal = focal_record["focal"]
        claims = focal_record["claims"]
        original_ids = focal_record["original_ids"]
        controls = focal_record["controls"]
        focal_cases = [row for row in cases if row["focal_paper_id"] == paper_id]
        expected_manipulations = [
            "baseline", "coverage_25", "coverage_50", "coverage_75",
            "coverage_100", "concentrated", "distributed",
        ]
        if [row["manipulation"] for row in focal_cases] != expected_manipulations:
            raise ReadinessError(f"Unexpected manipulation conditions for {paper_id}")

        control_by_condition = {row["condition"]: row for row in controls}
        if set(control_by_condition) != {"original", "empty", "shuffled", "same_topic_decoy"}:
            raise ReadinessError(f"Unexpected control conditions for {paper_id}")
        if control_by_condition["original"]["input_paper_ids"] != original_ids:
            raise ReadinessError(f"Original control IDs differ for {paper_id}")
        if control_by_condition["empty"].get("input_paper_ids") != [] or \
                control_by_condition["empty"].get("score_status") != "undefined":
            raise ReadinessError(f"Empty control is not explicitly undefined for {paper_id}")
        if control_by_condition["same_topic_decoy"].get("status") != "unavailable" or \
                "input_paper_ids" in control_by_condition["same_topic_decoy"] or \
                "question" in control_by_condition["same_topic_decoy"]:
            raise ReadinessError(f"Unavailable decoy contains fabricated data for {paper_id}")
        shuffled = control_by_condition["shuffled"]
        other_id = shuffled.get("shuffled_from_focal_paper_id")
        if other_id not in focal_data or other_id == paper_id:
            raise ReadinessError(f"Shuffled control lacks a distinct focal source for {paper_id}")
        other_pool = focal_data[other_id]["original_ids"]
        expected_shuffle = [
            source_id for source_id in other_pool
            if source_id != paper_id and
            parse_time(focal_data[other_id]["papers"][source_id]["published"])
            < parse_time(focal["published"])
        ]
        if shuffled.get("input_paper_ids") != expected_shuffle:
            raise ReadinessError(f"Shuffled IDs do not match the other focal's prior pool for {paper_id}")
        if set(shuffled["input_paper_ids"]) == set(original_ids):
            raise ReadinessError(f"Shuffled pool is not distinct for {paper_id}")

        for control in controls:
            if control.get("focal_paper_id") != paper_id or control.get("pair_id") != paper_id:
                raise ReadinessError(f"Control identity mismatch for {paper_id}")
            condition = control["condition"]
            if control.get("status") == "unavailable":
                identity = {
                    "focal_paper_id": paper_id,
                    "condition": condition,
                    "status": "unavailable",
                    "reason": control["reason"],
                }
            else:
                identity = {
                    "focal_paper_id": paper_id,
                    "condition": condition,
                    "question": control["question"],
                    "input_paper_ids": control["input_paper_ids"],
                }
                for metadata_key in (
                    "score_status", "score_reason", "shuffled_from_focal_paper_id",
                ):
                    if metadata_key in control:
                        identity[metadata_key] = control[metadata_key]
            if control.get("record_id") != "a1e2-" + _digest(identity):
                raise ReadinessError(f"Control record ID mismatch for {paper_id}/{condition}")
        original_control_id = control_by_condition["original"]["record_id"]
        claim_texts = [row["claim"] for row in claims]
        for case in focal_cases:
            if case["control_record_id"] != original_control_id:
                raise ReadinessError(f"Case baseline control identity mismatch for {paper_id}")
            level = case.get("coverage_percent")
            case_id = stable_id(
                "case-v1", focal["pool"], paper_id, case["manipulation"], level or ""
            )
            if case["case_id"] != case_id:
                raise ReadinessError(f"Case ID mismatch for {paper_id}/{case['manipulation']}")
            expected_claims = [
                {"claim_number": row["claim_number"], "claim": row["claim"],
                 "evidence": row["evidence"]}
                for row in claims
            ]
            if case["claims"] != claim_texts or case["source_claims"] != expected_claims:
                raise ReadinessError(f"Claim/source mapping mismatch for {paper_id}")
            if len(case["pool_ids"]) != len(set(case["pool_ids"])):
                raise ReadinessError(f"Duplicate pool IDs in {paper_id}/{case['manipulation']}")
            if not set(original_ids).issubset(case["pool_ids"]):
                raise ReadinessError(f"Original pool is missing from {paper_id}/{case['manipulation']}")

            name = case["manipulation"]
            selected = case["metadata"]["selected_claim_numbers"]
            synthetic_ids = case["metadata"]["synthetic_paper_ids"]
            if name == "baseline":
                expected_selected, expected_texts = [], []
            elif name.startswith("coverage_"):
                percent = int(name.removeprefix("coverage_"))
                count = max(1, math.ceil(len(claims) * percent / 100))
                expected_selected = [row["claim_number"] for row in claims[:count]]
                expected_texts = ["\n".join(row["claim"] for row in claims[:count])]
            elif name == "concentrated":
                expected_selected = [row["claim_number"] for row in claims]
                expected_texts = ["\n".join(claim_texts)]
            else:
                expected_selected = [row["claim_number"] for row in claims]
                expected_texts = claim_texts
            if selected != expected_selected:
                raise ReadinessError(f"Registered claim ordering mismatch for {paper_id}/{name}")
            if len(synthetic_ids) != len(expected_texts):
                raise ReadinessError(f"Synthetic item count mismatch for {paper_id}/{name}")
            if case["pool_ids"] != original_ids + synthetic_ids:
                raise ReadinessError(f"Manipulation pool identity mismatch for {paper_id}/{name}")
            cutoff = parse_time(focal["published"])
            for synthetic_index, (synthetic_id, expected_text) in enumerate(
                zip(synthetic_ids, expected_texts), 1
            ):
                record = synthetic_by_id.get(synthetic_id)
                if record is None or record.get("abstract") != expected_text:
                    raise ReadinessError(f"Synthetic claim text mismatch for {paper_id}/{name}")
                if record.get("pool") != focal["pool"] or not record.get("synthetic_manipulation"):
                    raise ReadinessError(f"Synthetic provenance mismatch for {paper_id}/{name}")
                expected_slot = (
                    "planted" if name.startswith("coverage_") else
                    "all_claims" if name == "concentrated" else
                    f"claim_{synthetic_index}"
                )
                expected_synthetic_id = stable_id(
                    MANIPULATION_SEED, focal["pool"], paper_id, name, expected_slot
                )
                if synthetic_id != expected_synthetic_id:
                    raise ReadinessError(f"Synthetic ID mismatch for {paper_id}/{name}")
                if parse_time(record["published"]) != cutoff - timedelta(seconds=1):
                    raise ReadinessError(f"Synthetic ordering timestamp mismatch for {paper_id}/{name}")
            for source_id in case["pool_ids"]:
                if source_id in synthetic_by_id:
                    source_time = parse_time(synthetic_by_id[source_id]["published"])
                else:
                    source_record = focal_record["papers"].get(source_id)
                    if source_record is None:
                        raise ReadinessError(f"Unknown source ID {source_id} in a case")
                    source_time = parse_time(source_record["published"])
                if source_time >= cutoff:
                    raise ReadinessError(f"Non-prior input {source_id} in {paper_id}/{name}")


def generate() -> tuple[dict, dict]:
    required = (
        COHORT_FILE, EXTRACTION_FILE, REVIEW_FILE, INDEPENDENCE_FILE,
        AUTHORIZATION_FILE, REGISTRATION_FILE, AMENDMENT_FILE, RAW_FILE, POOL_FILE,
    )
    for path in required:
        if not path.is_file():
            raise ReadinessError(f"Required input is missing: {path}")

    cohort = json.loads(COHORT_FILE.read_text(encoding="utf-8"))
    selected = {row["paper_id"]: row for row in cohort["selected_records"]}
    if any(paper_id not in selected for paper_id in AUTHORIZED_IDS):
        raise ReadinessError("An authorized focal is absent from the frozen cohort")
    excluded = set(cohort.get("previously_scored_focal_ids", []))
    if excluded.intersection(AUTHORIZED_IDS):
        raise ReadinessError("An authorized focal appears in prior scored IDs")

    extraction_rows = read_jsonl(EXTRACTION_FILE)
    extraction_by_id = {row["paper_id"]: row for row in extraction_rows}
    if any(paper_id not in extraction_by_id for paper_id in AUTHORIZED_IDS):
        raise ReadinessError("An authorized focal is absent from extraction output")
    review_text = REVIEW_FILE.read_text(encoding="utf-8")
    independence_text = INDEPENDENCE_FILE.read_text(encoding="utf-8")

    raw_rows = read_jsonl(RAW_FILE)
    papers: dict[str, dict] = {}
    for row in raw_rows:
        paper_id = row.get("paper_id")
        if not paper_id:
            raise ReadinessError("Raw source row lacks paper ID")
        previous = papers.get(paper_id)
        if previous is not None:
            fields = ("title", "abstract", "published", "updated", "paper_url")
            if any(previous.get(field) != row.get(field) for field in fields):
                raise ReadinessError(f"Conflicting source rows for {paper_id}")
            continue
        papers[paper_id] = row

    pool_ids_by_name: dict[str, set[str]] = {}
    with POOL_FILE.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            pool_ids_by_name.setdefault(row["pool"], set()).add(row["paper_id"])

    focal_data = {}
    all_controls = []
    all_cases = []
    all_synthetic = []
    original_by_focal = {}
    for paper_id in AUTHORIZED_IDS:
        source = papers.get(paper_id)
        focal_manifest = selected[paper_id]
        extraction = extraction_by_id[paper_id]
        if source is None:
            raise ReadinessError(f"Original source is missing for {paper_id}")
        if source.get("published") != focal_manifest.get("published"):
            raise ReadinessError(f"Focal timestamp differs from frozen cohort for {paper_id}")
        if hashlib.sha256(source.get("abstract", "").encode()).hexdigest() != focal_manifest.get("abstract_sha256"):
            raise ReadinessError(f"Source abstract hash differs from frozen cohort for {paper_id}")
        if extraction.get("cohort_manifest_sha256") != sha256_file(COHORT_FILE):
            raise ReadinessError(f"Extraction is not bound to the frozen cohort for {paper_id}")
        if extraction.get("abstract_sha256") != focal_manifest.get("abstract_sha256"):
            raise ReadinessError(f"Extraction abstract hash differs for {paper_id}")
        if not extraction.get("call_returned") or extraction.get("exception"):
            raise ReadinessError(f"Extraction did not complete successfully for {paper_id}")
        pool = extraction.get("pool") or source.get("pool")
        if not pool:
            raise ReadinessError(f"Source pool mapping is missing for {paper_id}")
        if extraction.get("accepted_claim_count") is None:
            raise ReadinessError(f"Extraction claim count is absent for {paper_id}")

        decisions = parse_review(review_text, extraction, source, independence_text)
        claims = [row for row in decisions
                  if row["semantic_support"] == "Supported" and row["atomicity"] == "Atomic"]
        focal = {
            "paper_id": paper_id,
            "pool": pool,
            "published": source["published"],
            "title": source["title"],
            "abstract": source["abstract"],
        }
        original_ids = source_pool_ids(
            pool, paper_id, parse_time(source["published"]), pool_ids_by_name, papers
        )
        if not original_ids:
            raise ReadinessError(f"Original eligible pool is empty for {paper_id}")
        original_by_focal[paper_id] = original_ids
        focal_data[paper_id] = {
            "focal": focal, "claims": claims, "original_ids": original_ids,
            "source": source, "extraction": extraction, "papers": papers,
            "source_ids": set(papers),
        }

    for paper_id in AUTHORIZED_IDS:
        current = focal_data[paper_id]
        other_instances = []
        for other_id in AUTHORIZED_IDS:
            if other_id == paper_id:
                continue
            other = focal_data[other_id]
            other_instances.append({
                "paper_id": other_id,
                "published": other["focal"]["published"],
                "question": f"{other['focal']['title']}\n\n{other['focal']['abstract']}",
                "input_paper_ids": original_by_focal[other_id],
            })
        controls = build_controls(
            focal=current["focal"],
            original_input_ids=current["original_ids"],
            papers=papers,
            other_instances=other_instances,
        )
        all_controls.extend(controls)
        cases, synthetic = build_manipulations(
            current["focal"], current["claims"], current["original_ids"], controls
        )
        all_cases.extend(cases)
        all_synthetic.extend(synthetic)
        current["controls"] = controls
        current["case_ids"] = [row["case_id"] for row in cases]
        current["synthetic_ids"] = [row["paper_id"] for row in synthetic]

    validate_generated(focal_data, all_cases, all_synthetic)

    inputs = {
        "schema": "M-A1-authorized-manipulation-inputs-v1",
        "authorization_commit": "42770a2db1d6978c52b8c95e288fa769df7bc10c",
        "authorization_record": AUTHORIZATION_FILE.name,
        "registration": REGISTRATION_FILE.name,
        "amendment": AMENDMENT_FILE.name,
        "review_form": REVIEW_FILE.name,
        "reviewer_independence_addendum": INDEPENDENCE_FILE.name,
        "reviewer_id": REVIEWER_ID,
        "review_date": REVIEW_DATE,
        "authorized_focals": list(AUTHORIZED_IDS),
        "condition_rules": {
            "partial_coverage_levels": list(COVERAGE_LEVELS),
            "coverage_selection": "ceil(n * percent / 100), minimum 1; first N retained claims in extraction order",
            "concentrated": "all retained claims in one synthetic prior-work item",
            "distributed": "one retained claim per synthetic prior-work item",
            "synthetic_id_seed": MANIPULATION_SEED,
            "bootstrap_seed_reserved_for_registered_analysis": BOOTSTRAP_SEED,
        },
        "focals": [
            {
                "paper_id": paper_id,
                "pool": focal_data[paper_id]["focal"]["pool"],
                "published": focal_data[paper_id]["focal"]["published"],
                "abstract_sha256": hashlib.sha256(
                    focal_data[paper_id]["source"]["abstract"].encode()
                ).hexdigest(),
                "human_approved_claims": [
                    {"claim_number": row["claim_number"], "claim": row["claim"],
                     "evidence": row["evidence"]}
                    for row in focal_data[paper_id]["claims"]
                ],
                "original_input_ids": focal_data[paper_id]["original_ids"],
                "control_records": focal_data[paper_id]["controls"],
                "case_ids": focal_data[paper_id]["case_ids"],
                "synthetic_paper_ids": focal_data[paper_id]["synthetic_ids"],
            }
            for paper_id in AUTHORIZED_IDS
        ],
        "manipulation_cases": all_cases,
        "synthetic_papers": all_synthetic,
        "scores_generated": False,
        "model_inference_run": False,
        "bootstrap_run": False,
    }
    inputs["input_sha256"] = {
        path.name: sha256_file(path)
        for path in (
            COHORT_FILE, EXTRACTION_FILE, REVIEW_FILE, INDEPENDENCE_FILE,
            AUTHORIZATION_FILE, REGISTRATION_FILE, AMENDMENT_FILE, RAW_FILE,
            POOL_FILE,
        )
    }

    condition_counts: dict[str, int] = {}
    for case in all_cases:
        condition = case["manipulation"]
        condition_counts[condition] = condition_counts.get(condition, 0) + 1
    control_counts: dict[str, int] = {}
    for control in all_controls:
        condition = control["condition"]
        control_counts[condition] = control_counts.get(condition, 0) + 1
    report = {
        "schema": "M-A1-authorized-manipulation-validation-v1",
        "inputs_file": OUTPUT_FILE.name,
        "inputs_sha256": hashlib.sha256(
            (json.dumps(inputs, ensure_ascii=False, indent=2) + "\n").encode()
        ).hexdigest(),
        "focal_results": [
            {
                "paper_id": paper_id,
                "reviewed_claims": len(focal_data[paper_id]["extraction"]["extractor_result"]["claims"]),
                "retained_supported_atomic_claims": len(focal_data[paper_id]["claims"]),
                "claim_numbers_in_extraction_order": [
                    row["claim_number"] for row in focal_data[paper_id]["claims"]
                ],
                "original_pool_count": len(focal_data[paper_id]["original_ids"]),
                "shuffled_pool_count": next(
                    len(row["input_paper_ids"]) for row in focal_data[paper_id]["controls"]
                    if row["condition"] == "shuffled"
                ),
                "case_count": len(focal_data[paper_id]["case_ids"]),
                "synthetic_paper_count": len(focal_data[paper_id]["synthetic_ids"]),
                "abstract_and_evidence_validation": "passed",
                "temporal_validation": "passed",
            }
            for paper_id in AUTHORIZED_IDS
        ],
        "manipulation_case_counts": dict(sorted(condition_counts.items())),
        "control_record_counts": dict(sorted(control_counts.items())),
        "empty_pool_status": "undefined; no score assigned",
        "decoy_status": "unavailable under Amendment 003; no substitute generated",
        "control_identity_validation": "passed",
        "synthetic_timestamp_validation": "passed: focal publication minus one second (intervention ordering only)",
        "case_id_validation": "passed",
        "scores_generated": False,
        "model_inference_run": False,
        "bootstrap_run": False,
        "validation_status": "passed",
    }
    return inputs, report


def main() -> None:
    if OUTPUT_FILE.exists() or REPORT_FILE.exists():
        raise SystemExit(
            "Refusing to overwrite existing manipulation inputs or validation report"
        )
    inputs, report = generate()
    OUTPUT_FILE.write_text(
        json.dumps(inputs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    REPORT_FILE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Generated {len(inputs['manipulation_cases'])} deterministic cases.")
    print(f"Validation report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
