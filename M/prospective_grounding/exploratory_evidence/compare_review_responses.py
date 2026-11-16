"""Validate and compare the two preserved exploratory V2 review responses."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
EVIDENCE = HERE
RESPONSES = EVIDENCE / "review_responses"
OUTPUT = EVIDENCE / "analysis_2026-11-15"
PRIVATE_MAP = REPO_ROOT / "M/prospective_grounding/human_review_v2/private_mapping.json"
ANALYSIS_CODE = (REPO_ROOT / "M/prospective_grounding/exploratory_ai_reviews/"
                 "analysis_2026-11-15")
sys.path.insert(0, str(ANALYSIS_CODE))
from analyze_reviews import cohen_kappa  # noqa: E402: reuse existing metric implementation

SOURCES = {
    "reviewer_1": RESPONSES / "reviewer_1_completed_review_form.json",
    "reviewer_2": RESPONSES / "reviewer_2_AI_assisted_review.json",
}
ORIGINAL_DOWNLOADS = {
    "reviewer_1": Path("/Users/arpit/Downloads/completed_review_form.json"),
    "reviewer_2": Path("/Users/arpit/Downloads/reviewer_2_AI_assisted_review.json"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _yes_no(value: object) -> bool:
    if value not in ("yes", "no"):
        raise ValueError(f"expected yes/no decision, got {value!r}")
    return value == "yes"


def validate_and_compare() -> tuple[dict, list[dict], list[dict]]:
    mapping = json.loads(PRIVATE_MAP.read_text(encoding="utf-8"))
    qmap, dmap, cmap = mapping["questions"], mapping["documents"], mapping["collections"]
    question_ids = {v["v2_question_id"] for v in qmap.values()}
    paper_ids = set(dmap.values())
    paper_family = {paper: meta["family"] for meta in qmap.values()
                    for paper in meta["source_paper_ids"]}
    family_collection = {value["source_family"]: key for key, value in cmap.items()}
    expected_pairs = set()
    for qid in qmap:
        meta = qmap[qid]
        if meta["generation_kind"] == "decoy":
            papers = meta["source_paper_ids"]
        elif meta["generation_kind"] == "primary":
            papers = meta["source_paper_ids"]
        else:
            raise ValueError("unknown question kind in frozen private mapping")
        expected_pairs.update((meta["v2_question_id"], paper) for paper in papers)
    # The two primary questions also have cross-family shuffled control ratings.
    for meta in qmap.values():
        if meta["generation_kind"] == "primary":
            own = set(meta["source_paper_ids"])
            other = paper_ids - own
            expected_pairs.update((meta["v2_question_id"], paper) for paper in other)
    if len(expected_pairs) != 18:
        raise ValueError("frozen mapping does not define exactly 18 registered rating pairs")

    expected_associations = set()
    for blind_qid, meta in qmap.items():
        qid = meta["v2_question_id"]
        own_collection = next(k for k, v in cmap.items() if v["source_family"] == meta["family"])
        expected_associations.add((qid, meta["family"]))
        if meta["generation_kind"] == "primary":
            other_collection = next(k for k, v in cmap.items() if k != own_collection)
            expected_associations.add((qid, cmap[other_collection]["source_family"]))
    if len(expected_associations) != 6:
        raise ValueError("frozen mapping does not define exactly six association checks")

    identity = {
        "reviewer_1": {"code": "reviewer_1", "independence": "yes"},
        "reviewer_2": {"code": "reviewer_2", "independence": "no"},
    }
    ratings_by_reviewer, associations_by_reviewer, provenance = {}, {}, {}
    for reviewer, path in SOURCES.items():
        data = json.loads(path.read_text(encoding="utf-8"))
        if set(data) != {"reviewer_code", "review_date_utc", "independent_review_confirmed",
                         "paper_ratings", "association_checks"}:
            raise ValueError(f"{reviewer}: unexpected or missing top-level schema fields")
        if data["reviewer_code"] != identity[reviewer]["code"]:
            raise ValueError(f"{reviewer}: reviewer code does not match source designation")
        if data["review_date_utc"] != "2026-11-15":
            raise ValueError(f"{reviewer}: unexpected or missing review date")
        if data["independent_review_confirmed"] != identity[reviewer]["independence"]:
            raise ValueError(f"{reviewer}: independence declaration differs from expected disclosure")
        if not isinstance(data["paper_ratings"], list) or len(data["paper_ratings"]) != 18:
            raise ValueError(f"{reviewer}: expected exactly 18 paper ratings")
        ratings = {}
        for row in data["paper_ratings"]:
            if set(row) != {"question_id", "collection_id", "document_id", "rating_0_1_2", "evidence_note"}:
                raise ValueError(f"{reviewer}: invalid paper-rating row schema")
            if row["question_id"] not in qmap or row["document_id"] not in dmap or row["collection_id"] not in cmap:
                raise ValueError(f"{reviewer}: unknown blinded question, collection, or document ID")
            key = (qmap[row["question_id"]]["v2_question_id"], dmap[row["document_id"]])
            if key not in expected_pairs or key in ratings:
                raise ValueError(f"{reviewer}: unexpected or duplicate question-paper pair {key}")
            expected_collection = family_collection[paper_family[key[1]]]
            if row["collection_id"] != expected_collection:
                raise ValueError(f"{reviewer}: collection ID does not match the paper family for {key}")
            if str(row["rating_0_1_2"]) not in {"0", "1", "2"}:
                raise ValueError(f"{reviewer}: invalid 0/1/2 rating")
            if not isinstance(row["evidence_note"], str) or not row["evidence_note"].strip():
                raise ValueError(f"{reviewer}: missing rating evidence note")
            ratings[key] = int(row["rating_0_1_2"])
        if set(ratings) != expected_pairs:
            raise ValueError(f"{reviewer}: question-paper IDs do not cover registered pairs")
        if not isinstance(data["association_checks"], list) or len(data["association_checks"]) != 6:
            raise ValueError(f"{reviewer}: expected exactly six association checks")
        associations = {}
        for row in data["association_checks"]:
            if set(row) != {"question_id", "collection_id", "same_broad_topic",
                            "unsupported_by_supplied_papers", "evidence_note"}:
                raise ValueError(f"{reviewer}: invalid association-check row schema")
            if row["question_id"] not in qmap or row["collection_id"] not in cmap:
                raise ValueError(f"{reviewer}: unknown blinded question or collection ID")
            key = (qmap[row["question_id"]]["v2_question_id"],
                   cmap[row["collection_id"]]["source_family"])
            if key not in expected_associations or key in associations:
                raise ValueError(f"{reviewer}: unexpected or duplicate association {key}")
            if not isinstance(row["evidence_note"], str) or not row["evidence_note"].strip():
                raise ValueError(f"{reviewer}: missing association evidence note")
            associations[key] = {
                "same_broad_topic": _yes_no(row["same_broad_topic"]),
                "unsupported_by_supplied_papers": _yes_no(row["unsupported_by_supplied_papers"]),
            }
        if set(associations) != expected_associations:
            raise ValueError(f"{reviewer}: association IDs do not cover all registered checks")
        ratings_by_reviewer[reviewer] = ratings
        associations_by_reviewer[reviewer] = associations
        provenance[reviewer] = {
            "source_file": str(path.relative_to(REPO_ROOT)),
            "original_download_path": str(ORIGINAL_DOWNLOADS[reviewer]),
            "sha256": sha(path), "reviewer_code": data["reviewer_code"],
            "review_date_utc": data["review_date_utc"],
            "independent_review_confirmed": data["independent_review_confirmed"],
            "review_provenance": (
                "independence self-declared; no external identity/independence verification is in the supplied file"
                if reviewer == "reviewer_1" else
                "file designation and explicit declaration identify AI assistance; reviewer declares independence=false"
            ),
            "embedded_provenance_field": False,
            "validated_rating_rows": len(ratings), "validated_association_checks": len(associations),
        }

    keys = sorted(expected_pairs)
    left = [ratings_by_reviewer["reviewer_1"][key] for key in keys]
    right = [ratings_by_reviewer["reviewer_2"][key] for key in keys]
    rating_rows = [{"question_id": key[0], "paper_id": key[1],
                    "reviewer_1_rating": ratings_by_reviewer["reviewer_1"][key],
                    "reviewer_2_rating": ratings_by_reviewer["reviewer_2"][key],
                    "exact_agreement": ratings_by_reviewer["reviewer_1"][key] == ratings_by_reviewer["reviewer_2"][key]}
                   for key in keys]
    disagreements = [row for row in rating_rows if not row["exact_agreement"]]
    association_rows = []
    for key in sorted(expected_associations):
        a, b = associations_by_reviewer["reviewer_1"][key], associations_by_reviewer["reviewer_2"][key]
        association_rows.append({"question_id": key[0], "family": key[1], **{
            field: {"reviewer_1": a[field], "reviewer_2": b[field], "agreement": a[field] == b[field]}
            for field in ("same_broad_topic", "unsupported_by_supplied_papers")
        }})
    assoc_disagreements = [r for r in association_rows if not r["same_broad_topic"]["agreement"] or
                           not r["unsupported_by_supplied_papers"]["agreement"]]
    exact = sum(row["exact_agreement"] for row in rating_rows)
    result = {
        "status": "exploratory_only_no_preregistered_v2_scoring",
        "source_provenance": provenance,
        "validation": {"reviewer_1_rating_rows": 18, "reviewer_2_rating_rows": 18,
                       "reviewer_1_association_checks": 6, "reviewer_2_association_checks": 6,
                       "all_question_paper_ids_valid": True, "all_association_ids_valid": True,
                       "all_evidence_notes_nonempty": True, "dates_valid": True,
                       "reviewer_1_independence_verified_externally": False,
                       "reviewer_2_independence_confirmed": False},
        "rating_agreement": {"n": 18, "exact_agreement_n": exact, "exact_agreement": exact / 18,
                             "cohen_kappa_unweighted": cohen_kappa(left, right),
                             "cohen_kappa_linear_weighted": cohen_kappa(left, right, weighted=True),
                             "disagreement_count": len(disagreements)},
        "association_agreement": {
            "n": 6,
            "same_broad_topic_agreement_n": sum(r["same_broad_topic"]["agreement"] for r in association_rows),
            "unsupported_by_supplied_papers_agreement_n": sum(r["unsupported_by_supplied_papers"]["agreement"] for r in association_rows),
            "joint_decision_agreement_n": sum(all(r[f]["agreement"] for f in
                                                   ("same_broad_topic", "unsupported_by_supplied_papers")) for r in association_rows),
            "field_disagreement_count": sum(not r[f]["agreement"] for r in association_rows
                                             for f in ("same_broad_topic", "unsupported_by_supplied_papers")),
            "record_disagreements": len(assoc_disagreements)},
        "rating_disagreements": disagreements,
        "association_comparisons": association_rows,
        "association_disagreements": assoc_disagreements,
        "limitations": [
            "Reviewer 1's independence is self-declared and was not externally verified.",
            "Reviewer 2 explicitly declares independence=false; the supplied file is identified as AI-assisted.",
            "The responses are not two independent reviews and do not pass the V2 review gate.",
            "Kappa and agreement are descriptive only for 18 repeated question-paper pairs; they do not establish validity or reviewer correctness.",
            "No preregistered V2 scores were calculated.",
        ],
    }
    return result, rating_rows, association_rows


def write_outputs() -> dict:
    result, rating_rows, association_rows = validate_and_compare()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (OUTPUT / "rating_comparison.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rating_rows[0]))
        writer.writeheader(); writer.writerows(rating_rows)
    with (OUTPUT / "association_comparison.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["question_id", "family", "same_broad_topic_reviewer_1", "same_broad_topic_reviewer_2",
                  "same_broad_topic_agreement", "unsupported_reviewer_1", "unsupported_reviewer_2",
                  "unsupported_agreement"]
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader()
        for row in association_rows:
            writer.writerow({"question_id": row["question_id"], "family": row["family"],
                             "same_broad_topic_reviewer_1": row["same_broad_topic"]["reviewer_1"],
                             "same_broad_topic_reviewer_2": row["same_broad_topic"]["reviewer_2"],
                             "same_broad_topic_agreement": row["same_broad_topic"]["agreement"],
                             "unsupported_reviewer_1": row["unsupported_by_supplied_papers"]["reviewer_1"],
                             "unsupported_reviewer_2": row["unsupported_by_supplied_papers"]["reviewer_2"],
                             "unsupported_agreement": row["unsupported_by_supplied_papers"]["agreement"]})
    a = result["rating_agreement"]
    b = result["association_agreement"]
    lines = ["# Exploratory comparison of the two supplied review responses", "",
             "Both source JSON files are preserved unchanged in `../review_responses/`; SHA-256 hashes and declarations are recorded in `results.json`.",
             "Reviewer 1 (`reviewer_1`, 2026-11-15) declares independence, which was not externally verified. Reviewer 2 (`reviewer_2`, 2026-11-15) declares `independent_review_confirmed=no`; the source is identified as AI-assisted. The supplied JSON files contain no separate provenance field.",
             "", "## Validation and rating agreement", "",
             "Both files passed structural validation for all 18 registered question-paper IDs and all six association pairs. All ratings were 0/1/2 and all evidence notes were nonempty. This is exploratory validation only; the two-independent-review gate did not pass.",
             f"Exact rating agreement: **{a['exact_agreement_n']}/18 ({a['exact_agreement']:.1%})**. Unweighted Cohen's κ: **{a['cohen_kappa_unweighted']:.3f}**; linear-weighted κ: **{a['cohen_kappa_linear_weighted']:.3f}**. Rating disagreements: {a['disagreement_count']}.",
             "", "## Association checks", "",
             f"Same-topic decisions agreed on {b['same_broad_topic_agreement_n']}/6 checks. Unsupportedness decisions agreed on {b['unsupported_by_supplied_papers_agreement_n']}/6. Both decisions jointly agreed on {b['joint_decision_agreement_n']}/6 association records. There were {b['field_disagreement_count']} field-level disagreements across {b['record_disagreements']} records.", "",
             "The detailed disagreements are listed in `results.json` and the paired CSV files. Agreement and κ are descriptive for a small set of repeated pairs; they do not establish correctness, independent review, or model performance. No model inference or preregistered V2 scoring was run.", "",
             "Reproduce from the repository root with `python3 -m M.prospective_grounding.exploratory_evidence.compare_review_responses`.", ""]
    (OUTPUT / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(write_outputs(), indent=2))
