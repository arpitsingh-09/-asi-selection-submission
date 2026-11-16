#!/usr/bin/env python3
"""Execute authorized A1 targets through the unchanged, locked E2 scorer."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any

from M.a1_replication import scoring_adapter


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "A1_SCORING_INPUT_MANIFEST_V1.json"
RESULTS_PATH = HERE / "A1_SCORING_RESULTS_V1.json"
EXPECTED_TARGETS = 16


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _write_results(path: Path, results: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(results, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def _numeric_scores(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and bool(value)
        and all(
            isinstance(score, (int, float))
            and not isinstance(score, bool)
            and math.isfinite(score)
            for score in value.values()
        )
    )


def _prepare() -> tuple[Any, dict[str, Any]]:
    from E2 import novelty

    manifest = scoring_adapter.prepare_scoring_inputs(novelty_module=novelty)
    if not MANIFEST_PATH.is_file():
        raise scoring_adapter.ScoringInputError("Versioned scoring-input manifest is missing")
    saved_manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if saved_manifest != manifest:
        raise scoring_adapter.ScoringInputError(
            "Current validated scoring inputs differ from the versioned scoring manifest"
        )
    if len(manifest.get("scoring_targets", [])) != EXPECTED_TARGETS:
        raise scoring_adapter.ScoringInputError(
            f"Expected {EXPECTED_TARGETS} targets, found "
            f"{len(manifest.get('scoring_targets', []))}"
        )
    target_ids = [target.get("target_id") for target in manifest["scoring_targets"]]
    if len(target_ids) != len(set(target_ids)) or any(not item for item in target_ids):
        raise scoring_adapter.ScoringInputError("Scoring target IDs are missing or duplicated")
    if any(
        target.get("condition") in {"empty", "same_topic_decoy"}
        for target in manifest["scoring_targets"]
    ):
        raise scoring_adapter.ScoringInputError(
            "Manifest includes an empty or unavailable decoy scoring target"
        )

    from M.a1_replication import controls

    # Verify the exact locked local artifacts before any target is scored.
    cache_root = Path(os.environ.get(
        "HF_HUB_CACHE", Path.home() / ".cache" / "huggingface" / "hub"
    ))
    controls._verify_e2_snapshot(cache_root)
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    return novelty, manifest


def _new_results(manifest: dict[str, Any]) -> dict[str, Any]:
    from M.a1_replication import controls

    return {
        "schema": "M-A1-scoring-results-v1",
        "authorization_commit": manifest["authorization_commit"],
        "created_at": _now(),
        "updated_at": _now(),
        "run_status": "running",
        "scoring_input_manifest_sha256": scoring_adapter._file_sha256(MANIFEST_PATH),
        "manipulation_inputs_sha256": manifest["manipulation_inputs_sha256"],
        "validation_report_sha256": manifest["validation_report_sha256"],
        "scoring_adapter_sha256": manifest["scoring_adapter_sha256"],
        "control_adapter_sha256": manifest["control_adapter_sha256"],
        "e2_novelty_sha256": manifest["e2_novelty_sha256"],
        "parameters": {
            "model_id": "specter2_base+proximity-adapter+cls-v1",
            "base_model": "allenai/specter2_base",
            "base_revision": controls.SPECTER2_BASE_REVISION,
            "adapter": "allenai/specter2",
            "adapter_revision": controls.SPECTER2_ADAPTER_REVISION,
            "max_length": 512,
            "rnd_p": 100,
            "rnd_q": 50,
            "y_weight": 0.75,
            "n_weight": 0.25,
            "active_adapter": "proximity",
            "cache_db": str(
                HERE / (
                    f"novelty_embeddings_{controls.SPECTER2_BASE_REVISION[:8]}_"
                    f"{controls.SPECTER2_ADAPTER_REVISION[:8]}.sqlite3"
                )
            ),
            "offline_mode": True,
        },
        "model_provenance": {
            "status": "local_snapshot_hashes_verified",
            "base_artifacts_sha256": {
                "config.json": "6d9d68ca2bfeca756fd807e7c81e8e9d3203d8a002dff19cc42b29edd48e8802",
                "pytorch_model.bin": "801eda968fad1752fe846a8e572bfdc25202be85544680dda4c99f4589646ebc",
                "tokenizer.json": "fcd3fffca5d8fcc0d5863406f5f491293c1e4658ed503f424a30324b70533c0d",
                "tokenizer_config.json": "afea6e85bb539b2c2de8847d92c2a3ae88334c280abbbdb3baaddc5fb7195242",
                "special_tokens_map.json": "b6d346be366a7d1d48332dbc9fdf3bf8960b5d879522b7799ddba59e76237ee3",
                "vocab.txt": "f0a650346e51ede8996710f79ba65d83fdb8da05b159f17037b74ba4e3a36c6f",
            },
            "adapter_artifacts_sha256": {
                "adapter_config.json": "1065ad610a661c5169f05d81040fe14429d2cc7ecdf83ed654dca4a62aaf9a8c",
                "pytorch_adapter.bin": "5b6105714f78b294daa7e2d181134df12f0acb7a4ec7c1e3c13e512c908db94a",
            },
            "inference_started_at": None,
            "inference_completed_at": None,
        },
        "controls": {
            "original": "included as baseline manipulation target",
            "shuffled": "included as two diagnostic scoring targets",
            "empty": "undefined; no numeric score",
            "same_topic_decoy": "unavailable; not scored",
        },
        "scoring_targets": [
            {
                **target,
                "status": "pending",
                "started_at": None,
                "completed_at": None,
                "result": None,
                "error": None,
            }
            for target in manifest["scoring_targets"]
        ],
    }


def _validate_resume(results: dict[str, Any], manifest: dict[str, Any]) -> None:
    expected_manifest_hash = scoring_adapter._file_sha256(MANIFEST_PATH)
    if results.get("schema") != "M-A1-scoring-results-v1":
        raise scoring_adapter.ScoringInputError("Existing results have an unexpected schema")
    if (
        results.get("scoring_input_manifest_sha256") != expected_manifest_hash
        or results.get("manipulation_inputs_sha256") != manifest["manipulation_inputs_sha256"]
        or results.get("scoring_adapter_sha256") != manifest["scoring_adapter_sha256"]
        or results.get("control_adapter_sha256") != manifest["control_adapter_sha256"]
        or results.get("e2_novelty_sha256") != manifest["e2_novelty_sha256"]
    ):
        raise scoring_adapter.ScoringInputError(
            "Existing results are bound to different inputs or scoring code"
        )
    if [
        row.get("target_id") for row in results.get("scoring_targets", [])
    ] != [
        row["target_id"] for row in manifest["scoring_targets"]
    ]:
        raise scoring_adapter.ScoringInputError("Existing result target order differs from manifest")

    interrupted = False
    for row in results["scoring_targets"]:
        if row.get("status") == "in_progress":
            row["status"] = "interrupted"
            row["error"] = {
                "type": "InterruptedRun",
                "message": "Prior process ended during this target; automatic retry is disabled.",
            }
            row["completed_at"] = _now()
            interrupted = True
        if row.get("status") == "scored":
            result = row.get("result")
            if (
                not isinstance(result, dict)
                or result.get("status") != "scored"
                or not _numeric_scores(result.get("scores"))
            ):
                raise scoring_adapter.ScoringInputError(
                    f"Completed target has invalid score data: {row.get('target_id')}"
                )
    if interrupted:
        results["updated_at"] = _now()
        _write_results(RESULTS_PATH, results)


def run(*, resume: bool = False) -> dict[str, Any]:
    novelty, manifest = _prepare()
    if RESULTS_PATH.exists():
        if not resume:
            raise scoring_adapter.ScoringInputError(
                f"Results already exist; use --resume to continue safely: {RESULTS_PATH}"
            )
        results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        _validate_resume(results, manifest)
    else:
        if resume:
            raise scoring_adapter.ScoringInputError(
                f"Cannot resume because results do not exist: {RESULTS_PATH}"
            )
        results = _new_results(manifest)
        _write_results(RESULTS_PATH, results)

    pending = [row for row in results["scoring_targets"] if row["status"] == "pending"]
    if not pending:
        results["run_status"] = (
            "completed" if all(row["status"] == "scored" for row in results["scoring_targets"])
            else "incomplete"
        )
        results["updated_at"] = _now()
        _write_results(RESULTS_PATH, results)
        return results

    results["model_provenance"]["inference_started_at"] = (
        results["model_provenance"]["inference_started_at"] or _now()
    )
    for row in pending:
        row["status"] = "in_progress"
        row["started_at"] = _now()
        results["updated_at"] = _now()
        _write_results(RESULTS_PATH, results)
        try:
            score = scoring_adapter.score_target(row)
            if (
                not isinstance(score, dict)
                or score.get("status") != "scored"
                or not _numeric_scores(score.get("scores"))
            ):
                raise scoring_adapter.ScoringInputError(
                    "E2 returned a missing, nonnumeric, or non-finite score"
                )
            model = novelty._MODEL
            if (
                model is None
                or "proximity" not in model.adapters_config
                or "proximity" not in str(model.active_adapters)
            ):
                raise scoring_adapter.ScoringInputError(
                    "E2 did not retain the registered active proximity adapter"
                )
            results["model_provenance"]["status"] = "loaded_and_used"
            results["model_provenance"]["loaded_model_id"] = (
                "specter2_base+proximity-adapter+cls-v1"
            )
            results["model_provenance"]["active_adapters_observed"] = str(
                model.active_adapters
            )
            results["model_provenance"]["proximity_adapter_configured"] = True
            row["result"] = score
            row["status"] = "scored"
            row["completed_at"] = _now()
            row["error"] = None
            results["updated_at"] = _now()
            _write_results(RESULTS_PATH, results)
        except Exception as exc:
            row["status"] = "failed"
            row["completed_at"] = _now()
            row["error"] = {"type": type(exc).__name__, "message": str(exc)}
            results["run_status"] = "failed"
            results["updated_at"] = _now()
            results["model_provenance"]["inference_completed_at"] = _now()
            _write_results(RESULTS_PATH, results)
            return results

    results["run_status"] = (
        "completed" if all(row["status"] == "scored" for row in results["scoring_targets"])
        else "incomplete"
    )
    results["updated_at"] = _now()
    results["model_provenance"]["inference_completed_at"] = _now()
    _write_results(RESULTS_PATH, results)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    try:
        results = run(resume=args.resume)
    except Exception as exc:
        print(f"Scoring stopped before a recorded target result: {type(exc).__name__}: {exc}")
        return 1

    scored = [row for row in results["scoring_targets"] if row["status"] == "scored"]
    failed = [row for row in results["scoring_targets"] if row["status"] == "failed"]
    interrupted = [row for row in results["scoring_targets"] if row["status"] == "interrupted"]
    print(f"Scored {len(scored)}/{len(results['scoring_targets'])} targets.")
    for row in scored:
        print(f"{row['target_id']} {row['focal_paper_id']} {row['condition']}: {row['result']['scores']}")
    for row in failed + interrupted:
        error = row.get("error") or {}
        print(f"{row['status'].upper()} {row['target_id']}: {error.get('type')}: {error.get('message')}")
    print(f"Results: {RESULTS_PATH}")
    return 0 if not failed and not interrupted and len(scored) == EXPECTED_TARGETS else 1


if __name__ == "__main__":
    raise SystemExit(main())
