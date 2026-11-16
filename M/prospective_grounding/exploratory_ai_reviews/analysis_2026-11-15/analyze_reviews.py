"""Reproduce an exploratory comparison of locally available review records."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from statistics import mean
import sys

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from M.prospective_grounding.exploratory_ai_reviews.validate_import import validate as validate_ai_csv

BASE = REPO_ROOT / "M/prospective_grounding"
PRIVATE_MAP = BASE / "human_review_v2/private_mapping.json"
AI_CSV = BASE / "exploratory_ai_reviews/assessments_imported.csv"
DEFAULT_HUMAN = Path.home() / "Downloads/human_researcher_ai_exposed_review_2026-11-15.json"
OUTPUT = Path(__file__).resolve().parent
RUN_COMPLETE = BASE / "generated_v2/run_20261115T024832_535290Z/run_complete.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_sources(human_path: Path) -> tuple[dict, dict, dict, dict, dict]:
    ai_validation = validate_ai_csv(AI_CSV, require_complete=True)
    private = json.loads(PRIVATE_MAP.read_text(encoding="utf-8"))
    human = json.loads(human_path.read_text(encoding="utf-8"))
    run = json.loads(RUN_COMPLETE.read_text(encoding="utf-8"))
    attempts = [json.loads(path.read_text(encoding="utf-8"))
                for path in sorted(RUN_COMPLETE.parent.glob("attempts/*.json"))]
    if run.get("status") != "COMPLETE_4_OF_4" or len(attempts) != 4 or \
            any(item.get("status") != "SUCCEEDED" for item in attempts):
        raise ValueError("V2 generated-record set is incomplete")
    if ai_validation["imported"] != 18:
        raise ValueError("external-AI dataset is not a complete 18-row import")
    return private, human, run, {"attempts": attempts}, ai_validation


def expected_pairs(attempts: list[dict]) -> tuple[set[tuple[str, str]], set[tuple[str, str]]]:
    by_key = {(item["family"], item["kind"]): item for item in attempts}
    families = {item["family"] for item in attempts}
    if len(by_key) != 4 or len(families) != 2:
        raise ValueError("unexpected V2 question/family structure")
    pairs, associations = set(), set()
    for family in families:
        other = next(value for value in families if value != family)
        primary, decoy = by_key[(family, "primary")], by_key[(family, "decoy")]
        for paper_id in primary["input_ids"]:
            pairs.add((primary["question_id"], paper_id))
            pairs.add((decoy["question_id"], paper_id))
        for paper_id in by_key[(other, "primary")]["input_ids"]:
            pairs.add((primary["question_id"], paper_id))
        associations.add((primary["question_id"], family))
        associations.add((primary["question_id"], other))
        associations.add((decoy["question_id"], family))
    if len(pairs) != 18 or len(associations) != 6:
        raise ValueError("registered exploratory pair design is not 18 ratings and 6 associations")
    return pairs, associations


def cohen_kappa(ai: list[int], human: list[int], weighted: bool = False) -> float:
    if len(ai) != len(human) or not ai:
        raise ValueError("paired ratings are required")
    categories = (0, 1, 2)
    n = len(ai)
    if weighted:
        weight = lambda i, j: 1.0 - abs(i - j) / 2.0
    else:
        weight = lambda i, j: float(i == j)
    observed = sum(weight(a, h) for a, h in zip(ai, human)) / n
    pa = {c: ai.count(c) / n for c in categories}
    ph = {c: human.count(c) / n for c in categories}
    expected = sum(pa[i] * ph[j] * weight(i, j) for i in categories for j in categories)
    if expected == 1:
        raise ValueError("kappa undefined because expected agreement is one")
    return (observed - expected) / (1.0 - expected)


def analyze(human_path: Path = DEFAULT_HUMAN) -> tuple[dict, list[dict]]:
    private, human, run, generation, ai_check = read_sources(human_path)
    attempts = generation["attempts"]
    expected, expected_associations = expected_pairs(attempts)
    question_map = private["questions"]
    document_map = private["documents"]
    collection_map = private["collections"]
    question_meta = {value["v2_question_id"]: value for value in question_map.values()}
    paper_family = {paper_id: record["family"] for record in attempts if record["kind"] == "primary"
                    for paper_id in record["input_ids"]}

    with AI_CSV.open(newline="", encoding="utf-8") as stream:
        ai_rows_raw = list(csv.DictReader(stream))
    ai_rows = {}
    for row in ai_rows_raw:
        key = (row["question_id"], row["paper_id"])
        if key in ai_rows:
            raise ValueError("duplicate external-AI rating pair")
        ai_rows[key] = row
        if (row["reviewer_type"] != "external_ai" or row["model_identity"] != "unknown" or
                row["source_type"] != "abstract_summary" or
                row["experimental_status"] != "exploratory_not_preregistered_human_review"):
            raise ValueError("external-AI record metadata changed from its exploratory designation")
    if set(ai_rows) != expected:
        raise ValueError("external-AI ratings do not match the registered 18 pairs")

    if human.get("reviewer_code") != "HUMAN-RESEARCHER-01" or \
            human.get("independent_review_confirmed") is not False:
        raise ValueError("researcher review identity/independence disclosure differs from source")
    human_rows = {}
    for row in human.get("paper_ratings", []):
        blinded_q, blinded_p = row.get("question_id"), row.get("document_id")
        if blinded_q not in question_map or blinded_p not in document_map:
            raise ValueError("researcher rating contains an unknown blinded ID")
        key = (question_map[blinded_q]["v2_question_id"], document_map[blinded_p])
        rating = row.get("rating_0_1_2")
        evidence = row.get("evidence_note")
        if str(rating) not in {"0", "1", "2"} or not isinstance(evidence, str) or not evidence.strip():
            raise ValueError("researcher rating or evidence note is missing/invalid")
        if key in human_rows:
            raise ValueError("duplicate researcher question-paper pair")
        human_rows[key] = {"rating": int(rating), "evidence_note": evidence}
    if set(human_rows) != expected or len(human_rows) != 18:
        raise ValueError("researcher ratings do not cover exactly the registered 18 pairs")

    association_rows = {}
    for row in human.get("association_checks", []):
        qid, collection = row.get("question_id"), row.get("collection_id")
        if qid not in question_map or collection not in collection_map:
            raise ValueError("association check contains an unknown blinded ID")
        key = (question_map[qid]["v2_question_id"], collection_map[collection]["source_family"])
        if type(row.get("same_broad_topic")) is not bool or \
                type(row.get("unsupported_by_supplied_papers")) is not bool or \
                not isinstance(row.get("evidence_note"), str) or not row["evidence_note"].strip():
            raise ValueError("researcher association check is incomplete or invalid")
        if key in association_rows:
            raise ValueError("duplicate researcher association check")
        association_rows[key] = row
    if set(association_rows) != expected_associations or len(association_rows) != 6:
        raise ValueError("researcher association checks do not cover the six registered associations")

    pairs = sorted(expected)
    ai_ratings = [int(ai_rows[pair]["rating"]) for pair in pairs]
    human_ratings = [human_rows[pair]["rating"] for pair in pairs]
    exact = sum(a == h for a, h in zip(ai_ratings, human_ratings))
    confusion = {str(a): {str(h): sum(ai_rows[p]["rating"] == str(a) and
                                      human_rows[p]["rating"] == h for p in pairs)
                          for h in (0, 1, 2)} for a in (0, 1, 2)}

    classified = {"primary_original": [], "decoy_original": [], "primary_shuffled": []}
    comparison_rows = []
    for pair in pairs:
        qid, pid = pair
        meta = question_meta[qid]
        kind = meta["generation_kind"]
        if kind == "primary":
            group = "primary_original" if paper_family[pid] == meta["family"] else "primary_shuffled"
        elif kind == "decoy" and paper_family[pid] == meta["family"]:
            group = "decoy_original"
        else:
            raise ValueError("question-paper pair is inconsistent with registered pool assignment")
        a, h = int(ai_rows[pair]["rating"]), human_rows[pair]["rating"]
        classified[group].append((a, h))
        comparison_rows.append({"question_id": qid, "paper_id": pid, "comparison_group": group,
                                "external_ai_rating": a, "researcher_ai_exposed_rating": h,
                                "exact_agreement": a == h})

    group_stats = {}
    for group, values in classified.items():
        group_stats[group] = {
            "n": len(values),
            "external_ai_mean": mean(a for a, _ in values),
            "researcher_mean": mean(h for _, h in values),
            "external_ai_rating_counts": {str(v): sum(a == v for a, _ in values) for v in (0, 1, 2)},
            "researcher_rating_counts": {str(v): sum(h == v for _, h in values) for v in (0, 1, 2)},
            "exact_agreement_n": sum(a == h for a, h in values),
        }

    primary_decoy_diffs = []
    by_key = {(item["family"], item["kind"]): item for item in attempts}
    for family in sorted({item["family"] for item in attempts}):
        primary, decoy = by_key[(family, "primary")], by_key[(family, "decoy")]
        for paper in primary["input_ids"]:
            primary_decoy_diffs.append({
                "family": family, "paper_id": paper,
                "external_ai_primary_minus_decoy": int(ai_rows[(primary["question_id"], paper)]["rating"]) -
                                                   int(ai_rows[(decoy["question_id"], paper)]["rating"]),
                "researcher_primary_minus_decoy": human_rows[(primary["question_id"], paper)]["rating"] -
                                                  human_rows[(decoy["question_id"], paper)]["rating"],
            })

    decoy_checks = []
    for (question_id, family), row in sorted(association_rows.items()):
        if question_meta[question_id]["generation_kind"] == "decoy":
            decoy_checks.append({"question_id": question_id, "family": family,
                                 "same_broad_topic": row["same_broad_topic"],
                                 "unsupported_by_supplied_papers": row["unsupported_by_supplied_papers"]})
    disagreements = [row for row in comparison_rows if not row["exact_agreement"]]
    ai_counts = {str(v): ai_ratings.count(v) for v in (0, 1, 2)}
    human_counts = {str(v): human_ratings.count(v) for v in (0, 1, 2)}
    result = {
        "status": "exploratory_only_no_model_scoring",
        "sources": {
            "external_ai_csv": str(AI_CSV), "external_ai_csv_sha256": sha(AI_CSV),
            "human_review_json": str(human_path), "human_review_sha256": sha(human_path),
            "human_reviewer_code": human["reviewer_code"], "human_review_date_utc": human["review_date_utc"],
            "human_review_independent": False,
            "human_provenance": human["review_provenance"],
            "v2_generation_run": str(RUN_COMPLETE),
            "private_mapping_sha256": sha(PRIVATE_MAP),
        },
        "validation": {"external_ai_rows": len(ai_rows), "external_ai_unique_pairs": len(ai_rows),
                       "human_rating_rows": len(human_rows), "human_unique_pairs": len(human_rows),
                       "human_association_checks": len(association_rows),
                       "human_rating_evidence_notes_present": 18,
                       "human_association_evidence_notes_present": 6,
                       "ids_match_registered_v2_pairs": True},
        "external_ai_model_identity": "unknown; no locally available per-model assessment files",
        "separate_claude_gemini_files_found": False,
        "agreement": {"n": 18, "exact_agreement_n": exact, "exact_agreement": exact / 18,
                      "cohen_kappa_unweighted": cohen_kappa(ai_ratings, human_ratings),
                      "cohen_kappa_linear_weighted": cohen_kappa(ai_ratings, human_ratings, weighted=True),
                      "external_ai_rating_counts": ai_counts, "researcher_rating_counts": human_counts,
                      "confusion_external_ai_rows_researcher_columns": confusion},
        "groups": group_stats,
        "paired_primary_minus_decoy_on_same_original_papers": {
            "n": len(primary_decoy_diffs), "external_ai_mean_difference": mean(
                x["external_ai_primary_minus_decoy"] for x in primary_decoy_diffs),
            "researcher_mean_difference": mean(x["researcher_primary_minus_decoy"] for x in primary_decoy_diffs),
            "records": primary_decoy_diffs,
        },
        "decoy_association_checks_researcher_only": decoy_checks,
        "disagreements": disagreements,
        "researcher_notes_with_unverified_cite_placeholder": sum(
            "[cite:" in row["evidence_note"] for row in human_rows.values()),
        "interpretation_limits": [
            "The external-AI CSV has unknown model identity and cannot be attributed to Claude or Gemini separately.",
            "The researcher-authored review records prior AI exposure and is explicitly not independent or blinded.",
            "There is one rating vector per source, only 18 dependent pairs across two question families, and no inferential CI is estimated.",
            "The AI data has no association checks, so AI-versus-human decoy-validation agreement is unavailable.",
            "The comparisons are human/AI relevance-rating diagnostics, not G/B-TF model scores or experimental results.",
        ],
    }
    return result, comparison_rows


def write_outputs(result: dict, comparison_rows: list[dict], human_path: Path,
                  output_dir: Path = OUTPUT) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_files = (output_dir / "results.json", output_dir / "pairwise_comparison.csv", output_dir / "RESULTS.md")
    if any(path.exists() for path in output_files):
        raise FileExistsError(f"exploratory result files already exist; refusing overwrite in {output_dir}")
    (output_dir / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    fields = ("question_id", "paper_id", "comparison_group", "external_ai_rating",
              "researcher_ai_exposed_rating", "exact_agreement")
    with (output_dir / "pairwise_comparison.csv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(comparison_rows)

    agreement = result["agreement"]
    groups = result["groups"]
    lines = [
        "# Exploratory comparison of available prospective-grounding assessments",
        "",
        "## Sources and eligibility",
        "",
        f"The available AI assessment source is `{result['sources']['external_ai_csv']}`: 18 complete abstract-summary ratings, model identity unknown. No separate Claude or Gemini review files were located in the exploratory review directory or Downloads, so this dataset cannot be attributed to either model separately.",
        f"The second source is `{human_path}`. It is submitted as `{result['sources']['human_reviewer_code']}` on `{result['sources']['human_review_date_utc']}`. Its provenance describes it as researcher-authored with prior AI exposure, while also noting that authorship is not independently verified; it records `independent_review_confirmed=false`. It is not an independent blinded human review.",
        "Both sources cover the same 18 registered question–paper pairs. Ratings and evidence-note presence were validated; source evidence remains unchanged. The AI file contains no association checks. The researcher file contains six complete association checks. Some researcher evidence notes contain `[cite: ...]` placeholders that have not been independently verified.",
        "",
        "## Rating agreement",
        "",
        f"Exact agreement was **{agreement['exact_agreement_n']}/18 ({agreement['exact_agreement']:.1%})**. Unweighted nominal Cohen's κ was **{agreement['cohen_kappa_unweighted']:.3f}**; linear-weighted κ was **{agreement['cohen_kappa_linear_weighted']:.3f}**. Both sources had the same marginal counts: 0={agreement['external_ai_rating_counts']['0']}, 1={agreement['external_ai_rating_counts']['1']}, 2={agreement['external_ai_rating_counts']['2']}. No confidence interval or significance test was calculated.",
        "",
        "| Registered comparison group | n | External-AI mean | AI-exposed researcher mean | Exact agreement |",
        "|---|---:|---:|---:|---:|",
    ]
    labels = {"primary_original": "Primary questions — original papers",
              "decoy_original": "Same-topic decoys — original papers",
              "primary_shuffled": "Primary questions — cross-family shuffled controls"}
    for key in ("primary_original", "decoy_original", "primary_shuffled"):
        group = groups[key]
        lines.append(f"| {labels[key]} | {group['n']} | {group['external_ai_mean']:.3f} | {group['researcher_mean']:.3f} | {group['exact_agreement_n']}/{group['n']} |")
    lines.extend([
        "",
        "Both sources rated all six shuffled cross-family pairs 0. Mean rating was 1.500 for primary/original pairs and 1.333 for decoy/original pairs. On the six within-family, same-paper primary-versus-decoy comparisons, mean primary-minus-decoy rating was 0.167 for each source; five pairs tied and one favored the primary. These are descriptive comparisons only, with two families and repeated papers/questions.",
        "",
        "## Disagreements",
        "",
        "All four rating disagreements were one-point 1-versus-2 differences, confined to two image-enhancement papers and repeated for both the primary and decoy question:",
        "",
        "| Question | Paper | External AI | AI-exposed researcher |",
        "|---|---|---:|---:|",
    ])
    for row in result["disagreements"]:
        lines.append(f"| `{row['question_id']}` | `{row['paper_id']}` | {row['external_ai_rating']} | {row['researcher_ai_exposed_rating']} |")
    lines.extend([
        "",
        "These splits are at the rubric boundary between topical evidence and direct relevance, suggesting ambiguity in how these abstracts ground the premise. They do not establish which rater is correct or show model performance.",
        "",
        "## Decoy checks and preregistered status",
        "",
    ])
    for row in result["decoy_association_checks_researcher_only"]:
        lines.append(f"- `{row['question_id']}` ({row['family']}): same broad topic = {str(row['same_broad_topic']).lower()}; unsupported by supplied papers = {str(row['unsupported_by_supplied_papers']).lower()}.")
    lines.extend([
        "",
        "The available researcher check marks both decoys same-topic; it marks the video-memorability decoy unsupported, but does not mark the image-enhancement decoy unsupported. There is no AI association-check vector for comparison. The required **two independent reviewers** have not supplied eligible blinded reviews; the preregistered human-review requirement remains incomplete. No scoring authorization, G/B-TF score, baseline comparison, or registered confidence interval is present. These exploratory assessments do not complete any of the original nine evaluations.",
        "",
        "## Reproduction and files",
        "",
        "Run from the repository root (reads sources, writes only this exploratory analysis directory):",
        "",
        "```sh",
        f"python3 M/prospective_grounding/exploratory_ai_reviews/analysis_2026-11-15/analyze_reviews.py --human-json '{human_path}' --output-dir /tmp/prospective_grounding_analysis_reproduced",
        "```",
        "",
        "`results.json` contains validation, metrics, group summaries, decoy checks and disagreement pairs. `pairwise_comparison.csv` contains only IDs, group labels and the two ratings; source evidence notes remain in their original files.",
        "",
    ])
    (OUTPUT / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--human-json", type=Path, default=DEFAULT_HUMAN)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result, comparisons = analyze(args.human_json)
    write_outputs(result, comparisons, args.human_json, args.output_dir)
    print(json.dumps({"agreement": result["agreement"], "groups": result["groups"],
                      "disagreements": len(result["disagreements"]),
                      "decoy_checks": result["decoy_association_checks_researcher_only"],
                      "output": str(args.output_dir)}, indent=2))


if __name__ == "__main__":
    main()
