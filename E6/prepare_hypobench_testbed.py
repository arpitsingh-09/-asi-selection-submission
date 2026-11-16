"""Prepare the repository's documented HypoBench Election Level 2 test split.

The benchmark's planted hypotheses are dataset-level. Each row has a held-out
classification label, but the source does not assign one planted hypothesis to
each row. Those two forms of truth remain separate in this manifest.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from orchestrator import ExperimentInput
from evaluation import (
    EvaluationError,
    aggregate_hypobench_heldout_accuracy,
    aggregate_hypobench_dataset_level_recovery,
    prepare_hypobench_data_explanation_input,
    score_hypobench_heldout_predictions,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_DIR = REPOSITORY_ROOT / "data/HypoBench-datasets/synthetic/election/level2"
DATASET_ID = "hypobench-synthetic-election-level2"
SOURCE_DATASET_PATH = "synthetic/election/level2"
SPLIT_FILES = {
    "TRAIN": "synthetic_election_train_level2.json",
    "VALIDATION": "synthetic_election_val_level2.json",
    "TEST": "synthetic_election_test_level2.json",
}
GT_FILE = "gt_hypotheses_level2.json"
METADATA_FILE = "metadata.json"
CONFIG_FILE = "config.yaml"


class HypoBenchPreparationError(ValueError):
    """HypoBench source data is absent, malformed, or internally inconsistent."""


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False,
                         separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(encoded)


def _read_json(path: Path, label: str) -> tuple[Any, str]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HypoBenchPreparationError(f"cannot read {label} at {path}: {exc}") from exc
    return value, _sha256_bytes(raw)


def _columnar_rows(value: Any, *, split: str) -> list[dict[str, Any]]:
    if not isinstance(value, Mapping) or not value:
        raise HypoBenchPreparationError(f"HypoBench {split} data must be a nonempty columnar object")
    if any(not isinstance(column, list) for column in value.values()):
        raise HypoBenchPreparationError(f"HypoBench {split} columns must all be arrays")
    lengths = {len(column) for column in value.values()}
    if len(lengths) != 1:
        raise HypoBenchPreparationError(f"HypoBench {split} columns have unequal lengths")
    return [{key: column[index] for key, column in value.items()}
            for index in range(next(iter(lengths)))]


def prepare_hypobench_election_level2_testbed(
    dataset_dir: str | Path = DEFAULT_DATASET_DIR,
) -> dict[str, Any]:
    """Build a deterministic test manifest from the unmodified HypoBench files."""
    root = Path(dataset_dir)
    metadata, metadata_sha = _read_json(root / METADATA_FILE, "dataset metadata")
    ground_truth, ground_truth_sha = _read_json(root / GT_FILE, "planted hypotheses")
    if not isinstance(metadata, Mapping):
        raise HypoBenchPreparationError("HypoBench metadata must be an object")
    metadata_ground_truth = metadata.get("ground_truth_hypotheses")
    if not isinstance(ground_truth, list) or not ground_truth or any(
        not isinstance(item, str) or not item.strip() for item in ground_truth
    ):
        raise HypoBenchPreparationError("ground-truth file must contain nonempty hypothesis strings")
    if metadata_ground_truth != ground_truth:
        raise HypoBenchPreparationError(
            "metadata ground_truth_hypotheses differs from the dedicated planted-hypothesis file"
        )
    task_description = metadata.get("task_description")
    if not isinstance(task_description, str) or not task_description.strip():
        raise HypoBenchPreparationError("metadata task_description is missing")
    labels = metadata.get("labels")
    if not isinstance(labels, list) or not labels or any(
        not isinstance(label, str) or not label.strip() for label in labels
    ):
        raise HypoBenchPreparationError("metadata labels must be a list of nonempty strings")

    split_hashes: dict[str, str] = {}
    split_records: dict[str, list[dict[str, Any]]] = {}
    for split, filename in SPLIT_FILES.items():
        source, source_sha = _read_json(root / filename, f"{split} split")
        rows = _columnar_rows(source, split=split)
        split_hashes[split] = source_sha
        split_records[split] = rows
        for index, row in enumerate(rows):
            if not isinstance(row.get("text"), str) or not row["text"].strip():
                raise HypoBenchPreparationError(f"{split} row {index} has missing or invalid text")
            if not isinstance(row.get("label"), str) or not row["label"].strip():
                raise HypoBenchPreparationError(f"{split} row {index} has missing or invalid label")
            if row["label"] not in labels:
                raise HypoBenchPreparationError(f"{split} row {index} label is absent from metadata")

    # A row's rendered observation must not be shared across the official splits.
    text_sets = {split: {row["text"] for row in rows}
                 for split, rows in split_records.items()}
    for left, right in (("TRAIN", "VALIDATION"), ("TRAIN", "TEST"), ("VALIDATION", "TEST")):
        overlap = text_sets[left] & text_sets[right]
        if overlap:
            raise HypoBenchPreparationError(
                f"HypoBench split isolation failed: {len(overlap)} text observations overlap "
                f"between {left} and {right}"
            )

    config_path = root / CONFIG_FILE
    try:
        config_bytes = config_path.read_bytes()
    except OSError as exc:
        raise HypoBenchPreparationError(f"cannot read dataset configuration at {config_path}: {exc}") from exc
    records = []
    for index, source_record in enumerate(split_records["TEST"]):
        row_sha = _canonical_hash(source_record)
        records.append({
            "input_set_id": f"{DATASET_ID}:TEST:{index:04d}:{row_sha[:12]}",
            "dataset_id": DATASET_ID,
            "split": "TEST",
            "source_record_index": index,
            "source_record_sha256": row_sha,
            "evidence": source_record["text"],
            "heldout_label": {
                "field": "label", "value": source_record["label"],
                "evaluation_only": True,
            },
            "ground_truth_set_id": DATASET_ID + ":dataset-planted-hypotheses",
            "source_record": source_record,
        })

    provenance = {
        "source_dataset_path": SOURCE_DATASET_PATH,
        "source_dataset_url": "https://github.com/ChicagoHAI/hypothesis-generation/tree/main/data/HypoBench-datasets/synthetic/election/level2",
        "dataset_metadata_file": METADATA_FILE,
        "dataset_metadata_sha256": metadata_sha,
        "source_split_file": SPLIT_FILES["TEST"],
        "source_split_sha256": split_hashes["TEST"],
        "source_split_hash_basis": "SHA-256 of exact source file bytes",
        "source_row_hash_basis": "SHA-256 of canonical JSON source row including all original fields",
        "source_configuration_file": CONFIG_FILE,
        "source_configuration_sha256": _sha256_bytes(config_bytes),
        "heldout_label_field": "label",
        "split_file_hashes": split_hashes,
        "split_row_counts": {split: len(rows) for split, rows in split_records.items()},
    }
    dataset_ground_truth = {
        "ground_truth_set_id": DATASET_ID + ":dataset-planted-hypotheses",
        "scope": "dataset_level",
        "source_file": GT_FILE,
        "source_file_sha256": ground_truth_sha,
        "hypotheses": ground_truth,
        "row_level_hypothesis_assignment": None,
        "row_level_assignment_status": "not_provided_by_source",
    }
    manifest: dict[str, Any] = {
        "schema_version": "e6-hypobench-testbed-manifest-v1",
        "selection_status": "selected_test_split_pending_protocol_approval",
        "dataset_id": DATASET_ID,
        "source_dataset_path": SOURCE_DATASET_PATH,
        "task_description": task_description,
        "split": "TEST",
        "split_is_held_out": True,
        "generation_input_fields": ["text"],
        "evaluation_only_fields": ["label"],
        "declared_label_classes": labels,
        "observed_test_label_classes": sorted({row["label"] for row in split_records["TEST"]}),
        "provenance": provenance,
        "dataset_ground_truth": dataset_ground_truth,
        "record_count": len(records),
        "records": records,
    }
    manifest["manifest_sha256"] = _canonical_hash(manifest)
    return manifest


def to_orchestrator_inputs(manifest: Mapping[str, Any]) -> list[ExperimentInput]:
    """Convert rows to generator inputs; held-out labels are not returned."""
    if not isinstance(manifest, Mapping) or manifest.get("schema_version") != (
        "e6-hypobench-testbed-manifest-v1"
    ) or manifest.get("split") != "TEST":
        raise HypoBenchPreparationError("a validated HypoBench TEST manifest is required")
    rows = manifest.get("records")
    if not isinstance(rows, list) or manifest.get("record_count") != len(rows):
        raise HypoBenchPreparationError("HypoBench manifest rows/count are invalid")
    if _canonical_hash({key: value for key, value in manifest.items()
                        if key != "manifest_sha256"}) != manifest.get("manifest_sha256"):
        raise HypoBenchPreparationError("HypoBench manifest hash mismatch")
    output = []
    seen_ids: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping) or row.get("split") != "TEST":
            raise HypoBenchPreparationError("HypoBench manifest contains a non-TEST row")
        source = row.get("source_record")
        if not isinstance(source, Mapping) or _canonical_hash(source) != row.get(
            "source_record_sha256"
        ):
            raise HypoBenchPreparationError("HypoBench row source hash mismatch")
        expected_id = f"{DATASET_ID}:TEST:{row.get('source_record_index', -1):04d}:" \
            f"{row['source_record_sha256'][:12]}"
        if row.get("dataset_id") != DATASET_ID or row.get("input_set_id") != expected_id:
            raise HypoBenchPreparationError("HypoBench row identity does not match its source provenance")
        if row["input_set_id"] in seen_ids:
            raise HypoBenchPreparationError("HypoBench manifest contains duplicate input_set_id values")
        seen_ids.add(row["input_set_id"])
        heldout = row.get("heldout_label")
        if row.get("evidence") != source.get("text") or not isinstance(heldout, Mapping) \
                or heldout.get("field") != "label" or heldout.get("value") != source.get("label") \
                or heldout.get("evaluation_only") is not True:
            raise HypoBenchPreparationError("HypoBench evidence or held-out label mapping is invalid")
        input_record = ExperimentInput(
            paper_id=row["input_set_id"],
            domain_and_task=manifest["task_description"],
            evidence=row["evidence"],
            split="TEST",
            provenance={
                "dataset_id": manifest["dataset_id"],
                "split": "TEST",
                "source_record_index": row["source_record_index"],
                "source_record_sha256": row["source_record_sha256"],
                "source_split_sha256": manifest["provenance"]["source_split_sha256"],
            },
        )
        output.append(input_record)
    return output


def score_hypobench_testbed_predictions(
    manifest: Mapping[str, Any], prediction_records: list[Mapping[str, Any]],
) -> dict[str, Any]:
    """Aggregate one arm's predictions in manifest order, counting missing as invalid."""
    if not isinstance(manifest, Mapping) or manifest.get("schema_version") != (
        "e6-hypobench-testbed-manifest-v1"
    ) or manifest.get("split") != "TEST":
        raise HypoBenchPreparationError("a HypoBench TEST manifest is required")
    if _canonical_hash({key: value for key, value in manifest.items()
                        if key != "manifest_sha256"}) != manifest.get("manifest_sha256"):
        raise HypoBenchPreparationError("HypoBench manifest hash mismatch")
    if not isinstance(prediction_records, list):
        raise HypoBenchPreparationError("prediction_records must be a list")
    predictions_by_id = {}
    for result in prediction_records:
        if not isinstance(result, Mapping) or not isinstance(result.get("input_set_id"), str):
            raise HypoBenchPreparationError("each prediction record needs an input_set_id")
        input_set_id = result["input_set_id"]
        if input_set_id in predictions_by_id:
            raise HypoBenchPreparationError("prediction records contain a duplicate input_set_id")
        if "predicted_label" in result:
            predictions_by_id[input_set_id] = result["predicted_label"]
        else:
            raw_output = result.get("raw_output")
            labels = raw_output.get("predicted_labels") if isinstance(raw_output, Mapping) else None
            predictions_by_id[input_set_id] = (
                labels[0] if isinstance(labels, list) and len(labels) == 1 else None
            )
    manifest_rows = manifest["records"]
    manifest_ids = [row["input_set_id"] for row in manifest_rows]
    extra = set(predictions_by_id) - set(manifest_ids)
    if extra:
        raise HypoBenchPreparationError("prediction records contain IDs outside the test manifest")
    true_labels = [row["heldout_label"]["value"] for row in manifest_rows]
    predicted_labels = [predictions_by_id.get(input_set_id) for input_set_id in manifest_ids]
    return aggregate_hypobench_heldout_accuracy(
        manifest_ids, true_labels, predicted_labels,
        valid_labels=manifest["declared_label_classes"],
        dataset_provenance={
            "dataset_id": manifest["dataset_id"], "split": "TEST",
            "manifest_sha256": manifest["manifest_sha256"],
            "source_split_sha256": manifest["provenance"]["source_split_sha256"],
        },
    )


def aggregate_hypobench_testbed_recovery(
    manifest: Mapping[str, Any], per_input_recovery_records: list[Mapping[str, Any]],
) -> dict[str, Any]:
    if not isinstance(manifest, Mapping) or manifest.get("schema_version") != (
        "e6-hypobench-testbed-manifest-v1"
    ) or _canonical_hash({key: value for key, value in manifest.items()
                          if key != "manifest_sha256"}) != manifest.get("manifest_sha256"):
        raise HypoBenchPreparationError("a valid HypoBench E6 manifest is required")
    ids = [row["input_set_id"] for row in manifest["records"]]
    try:
        return aggregate_hypobench_dataset_level_recovery(
            ids, per_input_recovery_records,
            dataset_provenance={
                "dataset_id": manifest["dataset_id"], "split": "TEST",
                "manifest_sha256": manifest["manifest_sha256"],
                "ground_truth_set_id": manifest["dataset_ground_truth"]["ground_truth_set_id"],
                "ground_truth_source_sha256": manifest["dataset_ground_truth"]["source_file_sha256"],
            },
        )
    except EvaluationError as exc:
        raise HypoBenchPreparationError(f"cannot aggregate HypoBench recovery: {exc}") from exc


def prepare_hypobench_evaluation_input(
    manifest: Mapping[str, Any], row: Mapping[str, Any],
    generated_explanations: list[str],
) -> dict[str, Any]:
    """Prepare a row for E6 evaluation without passing its held-out label in."""
    if not isinstance(manifest, Mapping) or manifest.get("schema_version") != (
        "e6-hypobench-testbed-manifest-v1"
    ):
        raise HypoBenchPreparationError("a HypoBench E6 manifest is required")
    if _canonical_hash({key: value for key, value in manifest.items()
                        if key != "manifest_sha256"}) != manifest.get("manifest_sha256"):
        raise HypoBenchPreparationError("HypoBench manifest hash mismatch")
    if not isinstance(row, Mapping) or row not in manifest.get("records", []):
        raise HypoBenchPreparationError("row does not belong to this HypoBench manifest")
    if _canonical_hash(row.get("source_record")) != row.get("source_record_sha256") \
            or row.get("evidence") != row.get("source_record", {}).get("text") \
            or row.get("heldout_label", {}).get("value") != row.get("source_record", {}).get("label"):
        raise HypoBenchPreparationError("HypoBench row provenance or label mapping is invalid")
    try:
        return prepare_hypobench_data_explanation_input(
            row["input_set_id"],
            {"task": manifest["task_description"], "observation": row["evidence"]},
            generated_explanations,
            dataset_id=manifest["dataset_id"], split=row["split"],
            dataset_provenance={
                **dict(manifest["provenance"]),
                "source_record_index": row["source_record_index"],
                "source_record_sha256": row["source_record_sha256"],
                "ground_truth_set_id": row["ground_truth_set_id"],
                "planted_hypothesis_scope": "dataset_level",
                "planted_hypothesis_source_sha256": manifest[
                    "dataset_ground_truth"]["source_file_sha256"],
            },
        )
    except (KeyError, EvaluationError) as exc:
        raise HypoBenchPreparationError(f"cannot prepare HypoBench evaluation input: {exc}") from exc


def score_hypobench_evaluation_input(
    prepared_input: Mapping[str, Any], row: Mapping[str, Any],
    predicted_label: str,
) -> dict[str, Any]:
    """Apply E6's exact-match scorer to one explicit held-out row label."""
    if not isinstance(row, Mapping) or not isinstance(row.get("heldout_label"), Mapping):
        raise HypoBenchPreparationError("row lacks a separated held-out label")
    target = row["heldout_label"].get("value")
    if row["heldout_label"].get("evaluation_only") is not True:
        raise HypoBenchPreparationError("held-out row label is not marked evaluation-only")
    try:
        return score_hypobench_heldout_predictions(
            prepared_input, [target], [predicted_label],
        )
    except (EvaluationError, TypeError) as exc:
        raise HypoBenchPreparationError(f"cannot score HypoBench held-out prediction: {exc}") from exc


def write_manifest_new(path: str | Path, manifest: Mapping[str, Any]) -> Path:
    """Write a derived manifest only if the destination does not already exist."""
    destination = Path(path)
    if destination.exists():
        raise HypoBenchPreparationError(f"refusing to overwrite existing manifest: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")
    return destination
