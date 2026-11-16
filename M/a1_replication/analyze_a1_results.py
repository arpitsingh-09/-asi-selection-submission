#!/usr/bin/env python3
"""Run the registered clustered paired bootstrap on saved supplementary A1 scores."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS_PATH = HERE / "A1_SCORING_RESULTS_V1.json"
OUTPUT_PATH = HERE / "A1_STATISTICAL_RESULTS_V1.json"
REPORT_PATH = HERE / "A1_STATISTICAL_FINDINGS_V1.md"
SEED = 20261113
DRAWS = 2000
COORDINATES = ("Y", "density", "N", "yours")
FOCAL_ORDER = ("2512.23709v3", "2610.29385v1")
COVERAGE_CONDITIONS = ("coverage_25", "coverage_50", "coverage_75", "coverage_100")


class AnalysisError(ValueError):
    pass


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _validate_results(results: dict[str, Any]) -> dict[str, dict[str, dict[str, float]]]:
    if results.get("schema") != "M-A1-scoring-results-v1":
        raise AnalysisError("Unexpected scoring-results schema")
    if results.get("run_status") != "completed":
        raise AnalysisError("Scoring results are not complete")
    if results.get("controls", {}).get("empty") != "undefined; no numeric score":
        raise AnalysisError("Empty-pool score must remain undefined")
    if results.get("controls", {}).get("same_topic_decoy") != "unavailable; not scored":
        raise AnalysisError("Same-topic decoy must remain unavailable")

    by_focal: dict[str, dict[str, dict[str, float]]] = {}
    seen_targets = set()
    for row in results.get("scoring_targets", []):
        focal_id = row.get("focal_paper_id")
        condition = row.get("condition")
        if focal_id not in FOCAL_ORDER:
            raise AnalysisError(f"Unexpected focal paper: {focal_id}")
        if condition in {"empty", "same_topic_decoy"}:
            raise AnalysisError(f"Undefined or unavailable condition was scored: {condition}")
        if row.get("status") != "scored" or row.get("result", {}).get("status") != "scored":
            raise AnalysisError(f"Missing successful score: {row.get('target_id')}")
        target_id = row.get("target_id")
        if not target_id or target_id in seen_targets:
            raise AnalysisError(f"Missing or duplicated target ID: {target_id}")
        seen_targets.add(target_id)
        if condition in by_focal.setdefault(focal_id, {}):
            raise AnalysisError(f"Duplicate focal/condition pair: {focal_id}/{condition}")
        scores = row["result"].get("scores")
        if not isinstance(scores, dict) or set(scores) != set(COORDINATES):
            raise AnalysisError(f"Incomplete score coordinates: {focal_id}/{condition}")
        normalized = {}
        for coordinate in COORDINATES:
            value = scores[coordinate]
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not np.isfinite(value)
            ):
                raise AnalysisError(f"Invalid {coordinate} score for {focal_id}/{condition}")
            normalized[coordinate] = float(value)
        by_focal[focal_id][condition] = normalized

    expected_conditions = {
        "baseline", *COVERAGE_CONDITIONS, "concentrated", "distributed", "shuffled"
    }
    if tuple(by_focal) != FOCAL_ORDER:
        raise AnalysisError("Focal papers are missing or out of registered order")
    for focal_id in FOCAL_ORDER:
        if set(by_focal[focal_id]) != expected_conditions:
            missing = sorted(expected_conditions - set(by_focal[focal_id]))
            extra = sorted(set(by_focal[focal_id]) - expected_conditions)
            raise AnalysisError(f"Incomplete conditions for {focal_id}: missing={missing}, extra={extra}")
    if len(seen_targets) != 16:
        raise AnalysisError(f"Expected 16 unique nonempty targets, found {len(seen_targets)}")
    return by_focal


def _bootstrap_summary(values: np.ndarray, draws: np.ndarray) -> dict[str, Any]:
    if values.ndim != 1 or len(values) != draws.shape[1]:
        raise AnalysisError("Bootstrap values must contain one value per focal cluster")
    point = float(np.mean(values))
    samples = np.mean(values[draws], axis=1)
    if not np.isfinite(samples).all():
        raise AnalysisError("Non-finite bootstrap replicate")
    return {
        "estimate": point,
        "ci_95_percentile": [
            float(np.percentile(samples, 2.5)),
            float(np.percentile(samples, 97.5)),
        ],
        "valid_replicates": int(len(samples)),
        "undefined_replicates": 0,
    }


def analyze(results: dict[str, Any], *, draws_count: int = DRAWS, seed: int = SEED) -> dict[str, Any]:
    if draws_count != DRAWS or seed != SEED:
        raise AnalysisError("Registered bootstrap requires 2,000 draws and PCG64 seed 20261113")
    by_focal = _validate_results(results)
    rng = np.random.Generator(np.random.PCG64(seed))
    # One shared cluster-index matrix preserves all conditions within a focal
    # and makes every registered comparison use identical bootstrap draws.
    bootstrap_indices = rng.integers(0, len(FOCAL_ORDER), size=(draws_count, len(FOCAL_ORDER)))

    comparisons: dict[str, Any] = {}
    coverage_axioms: dict[str, Any] = {}
    concentration_axioms: dict[str, Any] = {}
    for coordinate in COORDINATES:
        steps = [
            ("baseline", "coverage_25"),
            ("coverage_25", "coverage_50"),
            ("coverage_50", "coverage_75"),
            ("coverage_75", "coverage_100"),
        ]
        step_results = []
        paper_deltas: dict[str, list[float]] = {focal: [] for focal in FOCAL_ORDER}
        for left, right in steps:
            deltas = np.array([
                by_focal[focal][left][coordinate] - by_focal[focal][right][coordinate]
                for focal in FOCAL_ORDER
            ], dtype=np.float64)
            passed = deltas > 0.0
            for index, focal in enumerate(FOCAL_ORDER):
                paper_deltas[focal].append(float(deltas[index]))
            step_results.append({
                "comparison": f"{left}_minus_{right}",
                "direction": "positive means strict novelty decrease; ties fail",
                "per_paper_delta": {
                    focal: float(deltas[index]) for index, focal in enumerate(FOCAL_ORDER)
                },
                "mean_paired_delta": _bootstrap_summary(deltas, bootstrap_indices),
                "strict_pass_fraction": _bootstrap_summary(
                    passed.astype(np.float64), bootstrap_indices
                ),
            })

        # A focal cluster passes the partial-coverage axiom only when every
        # registered ordered transition is a strict decrease.
        coverage_passes = np.array([
            all(delta > 0.0 for delta in paper_deltas[focal])
            for focal in FOCAL_ORDER
        ], dtype=np.float64)
        coverage_axioms[coordinate] = {
            "definition": (
                "Per-focal pass iff baseline>25%>50%>75%>100% strictly "
                "for this coordinate."
            ),
            "per_paper_signed_deltas": {
                focal: paper_deltas[focal] for focal in FOCAL_ORDER
            },
            "per_paper_pass": {
                focal: bool(coverage_passes[index])
                for index, focal in enumerate(FOCAL_ORDER)
            },
            "strict_axiom_pass_fraction": _bootstrap_summary(
                coverage_passes, bootstrap_indices
            ),
        }
        comparisons[coordinate] = {"partial_coverage_steps": step_results}

        concentration_deltas = np.array([
            by_focal[focal]["distributed"][coordinate]
            - by_focal[focal]["concentrated"][coordinate]
            for focal in FOCAL_ORDER
        ], dtype=np.float64)
        concentration_passes = (concentration_deltas > 0.0).astype(np.float64)
        concentration_axioms[coordinate] = {
            "definition": (
                "Per-focal pass iff distributed score minus concentrated score "
                "is strictly positive."
            ),
            "direction": "distributed_minus_concentrated; positive is preregistered direction",
            "per_paper_signed_deltas": {
                focal: float(concentration_deltas[index])
                for index, focal in enumerate(FOCAL_ORDER)
            },
            "per_paper_pass": {
                focal: bool(concentration_passes[index])
                for index, focal in enumerate(FOCAL_ORDER)
            },
            "mean_paired_delta": _bootstrap_summary(
                concentration_deltas, bootstrap_indices
            ),
            "strict_axiom_pass_fraction": _bootstrap_summary(
                concentration_passes, bootstrap_indices
            ),
        }

    controls: dict[str, Any] = {}
    for coordinate in COORDINATES:
        deltas = np.array([
            by_focal[focal]["shuffled"][coordinate]
            - by_focal[focal]["baseline"][coordinate]
            for focal in FOCAL_ORDER
        ], dtype=np.float64)
        controls[coordinate] = {
            "comparison": "shuffled_minus_original",
            "interpretation": "diagnostic only; no directional pass criterion",
            "per_paper_delta": {
                focal: float(deltas[index]) for index, focal in enumerate(FOCAL_ORDER)
            },
            "mean_paired_delta": _bootstrap_summary(deltas, bootstrap_indices),
        }

    qualifying_coordinates = [
        coordinate for coordinate in COORDINATES
        if coverage_axioms[coordinate]["strict_axiom_pass_fraction"]["ci_95_percentile"][0] >= 0.80
        and concentration_axioms[coordinate]["strict_axiom_pass_fraction"]["ci_95_percentile"][0] >= 0.80
    ]
    return {
        "schema": "M-A1-statistical-results-v1",
        "source_results_schema": results["schema"],
        "authorization_commit": results["authorization_commit"],
        "sample": {
            "focal_paper_ids": list(FOCAL_ORDER),
            "independent_focal_clusters_n": len(FOCAL_ORDER),
            "scored_targets_n": len(results["scoring_targets"]),
            "coordinates": list(COORDINATES),
            "conditions_per_focal": 8,
            "complete_paired_comparisons": True,
        },
        "bootstrap": {
            "method": "paired percentile cluster bootstrap",
            "cluster_unit": "focal paper",
            "draws": draws_count,
            "bit_generator": "NumPy PCG64",
            "seed": seed,
            "sampling": (
                "For each draw, sample n=2 focal papers with replacement; "
                "retain all their conditions and comparisons together."
            ),
            "ci": "two-sided 95% percentile interval (2.5th and 97.5th percentiles)",
            "shared_draws_across_comparisons": True,
            "undefined_replicates": 0,
            "undefined_replicate_fraction": 0.0,
            "undefinedness_blocks_analysis": False,
        },
        "partial_coverage": {
            "comparisons": ["baseline→25%", "25%→50%", "50%→75%", "75%→100%"],
            "effect_sign": "left score minus right score; positive is strict novelty decrease",
            "coordinate_results": comparisons,
            "registered_axiom_pass_fraction": coverage_axioms,
        },
        "concentration": {
            "comparison": "distributed minus concentrated",
            "effect_sign": "positive means concentrated < distributed",
            "coordinate_results": concentration_axioms,
        },
        "diagnostic_controls": {
            "original_vs_shuffled": controls,
            "empty_pool": {
                "status": "undefined",
                "numeric_score": None,
                "included_in_numeric_analysis": False,
            },
            "same_topic_decoy": {
                "status": "unavailable",
                "numeric_score": None,
                "included_in_numeric_analysis": False,
            },
        },
        "registered_pass_assessment": {
            "rule": (
                "At least one same coordinate must have a lower 95% CI bound "
                ">=0.80 for both partial-coverage and concentration strict "
                "axiom pass fractions."
            ),
            "qualifying_coordinates": qualifying_coordinates,
            "criterion_met": bool(qualifying_coordinates),
            "interpretation": (
                "A numerical criterion result with only two clusters is not "
                "confirmatory evidence."
            ),
        },
        "limitations": [
            "This is an exposed supplementary partial replication, not the original registered A1 evaluation.",
            "The same-topic decoy condition is unavailable; no decoy effect is estimable.",
            "Empty-pool scores are undefined and were not imputed.",
            "n=2 independent focal-paper clusters makes inferential conclusions extremely limited.",
        ],
    }


def _findings_markdown(statistics: dict[str, Any]) -> str:
    coverage = statistics["partial_coverage"]["registered_axiom_pass_fraction"]
    concentration = statistics["concentration"]["coordinate_results"]
    lines = [
        "# Supplementary A1 statistical findings",
        "",
        "Analysis uses only the saved A1 score results; no scoring or model inference was run.",
        "",
        f"- Focal-paper clusters: **n={statistics['sample']['independent_focal_clusters_n']}**",
        f"- Scored nonempty targets: **{statistics['sample']['scored_targets_n']}**",
        "- Bootstrap: paired focal-paper cluster percentile, 2,000 draws, NumPy PCG64 seed `20261113`.",
        "- Every bootstrap draw retains each sampled focal paper's full set of conditions.",
        "- Empty pool: **undefined**. Same-topic decoy: **unavailable**.",
        "- **n=2 makes inferential conclusions extremely limited**; intervals are highly discrete and unstable.",
        "",
        "## Registered axiom pass fractions",
        "",
        "Intervals are 95% percentile cluster-bootstrap CIs. Coverage pass requires all four ordered decreases for that paper and coordinate.",
        "",
        "| Coordinate | Coverage strict pass fraction (95% CI) | Concentration strict pass fraction (95% CI) |",
        "|---|---:|---:|",
    ]
    for coordinate in COORDINATES:
        cov = coverage[coordinate]["strict_axiom_pass_fraction"]
        con = concentration[coordinate]["strict_axiom_pass_fraction"]
        lines.append(
            f"| {coordinate} | {cov['estimate']:.3f} "
            f"[{cov['ci_95_percentile'][0]:.3f}, {cov['ci_95_percentile'][1]:.3f}] "
            f"| {con['estimate']:.3f} "
            f"[{con['ci_95_percentile'][0]:.3f}, "
            f"{con['ci_95_percentile'][1]:.3f}] |"
        )
    lines.extend([
        "",
        f"Registered numerical threshold met: **{statistics['registered_pass_assessment']['criterion_met']}** "
        f"(qualifying coordinates: {', '.join(statistics['registered_pass_assessment']['qualifying_coordinates']) or 'none'}).",
        "",
        "## Mean paired score effects",
        "",
        "Effects are signed in the preregistered direction; positive values indicate the expected reduction.",
        "",
        "| Coordinate | Coverage comparison | Mean paired delta (95% CI) |",
        "|---|---|---:|",
    ])
    for coordinate in COORDINATES:
        for step in statistics["partial_coverage"]["coordinate_results"][coordinate]["partial_coverage_steps"]:
            effect = step["mean_paired_delta"]
            lines.append(
                f"| {coordinate} | {step['comparison']} | {effect['estimate']:.6f} "
                f"[{effect['ci_95_percentile'][0]:.6f}, {effect['ci_95_percentile'][1]:.6f}] |"
            )
    lines.extend([
        "",
        "| Coordinate | Concentration comparison | Mean paired delta (95% CI) |",
        "|---|---|---:|",
    ])
    for coordinate in COORDINATES:
        effect = concentration[coordinate]["mean_paired_delta"]
        lines.append(
            f"| {coordinate} | distributed − concentrated | {effect['estimate']:.6f} "
            f"[{effect['ci_95_percentile'][0]:.6f}, {effect['ci_95_percentile'][1]:.6f}] |"
        )
    lines.extend([
        "",
        "Original-versus-shuffled results are reported separately as diagnostics in the JSON; they have no registered directional pass criterion. These analyses cover the amended partial evaluation only and do not establish completion of the full control set or original A1.",
        "",
    ])
    return "\n".join(lines)


def run() -> tuple[dict[str, Any], str]:
    if OUTPUT_PATH.exists() or REPORT_PATH.exists():
        raise AnalysisError("Refusing to overwrite existing versioned statistical outputs")
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    statistics = analyze(results)
    statistics["provenance"] = {
        "input_results_file": RESULTS_PATH.name,
        "input_results_sha256": _sha256(RESULTS_PATH),
        "input_result_target_count": len(results["scoring_targets"]),
        "replication_registration": "PREREG_REPLICATION.md",
        "replication_registration_sha256": _sha256(HERE / "PREREG_REPLICATION.md"),
        "amendment": "AMENDMENT_003_PARTIAL_CONTROLS.md",
        "amendment_sha256": _sha256(HERE / "AMENDMENT_003_PARTIAL_CONTROLS.md"),
        "analysis_code": Path(__file__).name,
        "analysis_code_sha256": _sha256(Path(__file__).resolve()),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "model_inference_run": False,
        "novelty_scoring_run": False,
    }
    report = _findings_markdown(statistics)
    OUTPUT_PATH.write_text(json.dumps(statistics, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                           encoding="utf-8")
    REPORT_PATH.write_text(report, encoding="utf-8")
    return statistics, report


if __name__ == "__main__":
    run()
