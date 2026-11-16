#!/usr/bin/env python3
"""Recompute summaries from the locked, saved E6 accuracy outputs only.

This script does not import the generator, load a model, call a model-based
evaluator, write files, retry missing cells, or launch the held-out runner.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path

from statistical_analysis import analyze_evaluations

ROOT = Path(__file__).resolve().parent
RUN = ROOT / "runs/heldout_accuracy_optimized_v1"
ARMS = ("D", "QH", "QH-sel", "QH-rand", "HQ", "D-empty", "D-shuffled")


def hash_json(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def main():
    package = json.loads((RUN / "PACKAGING_MANIFEST.json").read_text())
    for entry in package["copied_files"]:
        path = RUN / entry["path"]
        assert path.stat().st_size == entry["bytes"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]

    test_manifest = json.loads(
        (ROOT / "data/hypobench_election_level2_test_manifest_v1.json").read_text()
    )
    test_ids = [row["input_set_id"] for row in test_manifest["records"]]
    assert len(test_ids) == 501 and len(set(test_ids)) == 501

    sources, seen = [], set()
    totals = Counter()
    for path in sorted(RUN.glob("*/*_evaluation.json")):
        row = json.loads(path.read_text())
        assert row["result_sha256"] == hash_json(
            {key: value for key, value in row.items() if key != "result_sha256"}
        )
        unit = row["generation_input_set_id"]
        seen.add(unit)
        for arm, cell in row["evaluations"].items():
            if cell.get("status") != "evaluated":
                continue
            record = cell["heldout"]["heldout_accuracy"]
            assert record["status"] == "succeeded"
            assert record["evaluation_input"]["input_set_ids"] == test_ids
            result = record["parsed_output"]
            assert result["denominator"] == 501
            assert result["correct"] == sum(
                actual == predicted
                for actual, predicted in zip(
                    record["evaluation_input"]["true_labels"],
                    record["evaluation_input"]["predicted_labels"],
                )
            )
            totals[(arm, "sets")] += 1
            totals[(arm, "correct")] += result["correct"]
            totals[(arm, "rows")] += result["denominator"]
            totals[(arm, "invalid")] += result["invalid_prediction_count"]
        sources.append(
            {"generation_input_set_id": unit, "evaluations": row["evaluations"]}
        )

    readiness = json.loads((ROOT / "data/heldout_accuracy_readiness_v1.json").read_text())
    planned = sorted(
        {
            job["input_set_id"]
            for job in readiness["jobs"]
            if ":TRAIN-SET:" in job.get("input_set_id", "")
        }
    )
    for unit in planned:
        if unit not in seen:
            sources.append(
                {"generation_input_set_id": unit, "evaluations": {a: {"status": "missing"} for a in ARMS}}
            )

    config = json.loads((ROOT / "evaluation_config.json").read_text())["paired_bootstrap"]
    summary = analyze_evaluations(
        sources,
        testbed="data",
        metric="heldout_accuracy",
        value_path=["heldout", "heldout_accuracy", "parsed_output", "accuracy"],
        comparisons=[tuple(pair) for pair in config["comparisons"]],
        replicates=config["replicates"],
        seed=config["seed"],
        missing_policy="complete_pairs",
    )

    print("Saved held-out accuracy; no generation or model scoring was run.")
    print("arm, sets, correct, assignments, invalid, accuracy, CI95")
    for arm, estimate in summary["arm_estimates"].items():
        print(
            arm,
            totals[(arm, "sets")],
            totals[(arm, "correct")],
            totals[(arm, "rows")],
            totals[(arm, "invalid")],
            f"{estimate['point_estimate']:.8f}",
            estimate["interval"],
        )
    print("paired contrast, complete sets, left-minus-right, CI95")
    for name, estimate in summary["comparisons"].items():
        print(name, estimate["included_count"], f"{estimate['point_estimate']:.8f}", estimate["interval"])

    token_cost = {}
    for path in sorted(RUN.glob("*/*_evaluation.json")):
        row = json.loads(path.read_text())
        for record in row.get("generation_records", []):
            key, value = record.get("token_accounting_id"), record.get("tokens_generated")
            if key and isinstance(value, int):
                assert key not in token_cost or token_cost[key] == value
                token_cost[key] = value
    print("distinct successful generation charges:", len(token_cost), sum(token_cost.values()))


if __name__ == "__main__":
    main()
