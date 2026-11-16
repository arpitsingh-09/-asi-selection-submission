"""Run the preregistered exposed-E1 supplementary S1-style comparison."""

from __future__ import annotations

import argparse
import ast
import csv
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any

import numpy as np


LABEL = "EXPLORATORY — EXPOSED E1 DATA — UNVERIFIED AUTHOR-INTENDED LABELS"
PREREG_COMMIT = "e18ace5121c49eb1f94cd3c0c7c40c912643e3e8"
PREREG_PATH = "M/supplementary_s1_e1_exploratory/PREREG.md"
PREREG_SHA256 = "6bd1a61037073185d78d6cc942aed99bfdb5452b50fe331f9f92b61efbce9671"
CONTRASTS_SHA256 = "57f95f7690746d3b22670434410c4ce80894b42f0f8dc504cac58f7d9cdaedcc"
AUDIT_SHA256 = "45786a684a0c5bb5abfa12c74e9aed5e1cdb111f6a9b933fcdb09c1a77615218"
COHORT_SHA256 = "af485191ba1464153c6d2812e77e1bd54f06db32f12ba5ab99751393778b727e"
CONFIG_SHA256 = "9fb1a8e94b08d99167d54cb12cb86357eadf073ef6d0c3d5cea3e5dbd5d19a36"
IDENTITY_FUNCTION_SHA256 = "e2975a9ff3bc63d093c6cb364be14a24efbe47f8c0c1a89475284d285925a870"
E5_MODEL_ID = "intfloat/e5-base-v2"
E5_REVISION = "f52bf8ec8c7124536f0efb74aca902b2995e5bcd"
E5_ARTIFACT_SHA256 = {
    "config.json": "01cc39aa39538a8179aa131c8a16adc03b506c92009f091502e4eb0c702f5f78",
    "model.safetensors": "d0d559c47d5f71b1d280b13b62a2657f3e3bc70c0786f9ab91a36545e6a8f693",
    "tokenizer.json": "d241a60d5e8f04cc1b2b3e9ef7a4921b27bf526d9f6050ab90f9267a1f9e5c66",
    "modules.json": "c6e29747481e8b5dd2b58401966aeac910de39092f90cda9a704b1545f902b04",
    "sentence_bert_config.json": "948201d8329907aae938fa62f9ceeed53f5694dacc2b87b9f3b78b37ee986529",
    "1_Pooling/config.json": "f586ab6c734af7b8d14d898bfa7faa886f23b46f86dd1730514309893af13d75",
    "tokenizer_config.json": "ae83fa6ca0333117ff12606020af925d648667ef70d92ff7f27d781ba0ca4544",
    "special_tokens_map.json": "b6d346be366a7d1d48332dbc9fdf3bf8960b5d879522b7799ddba59e76237ee3",
    "vocab.txt": "07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3",
}
IDENTITY_THRESHOLD = 0.65
BQ_THRESHOLD = 0.65
BOOTSTRAP_DRAWS = 2000
BOOTSTRAP_SEED = 20261113
COMPARISON_MARGIN = 0.02
DATE_CUTOFF = "2025-07-01"


class IntegrityError(RuntimeError):
    """A frozen input, selection, code, or model artifact did not match."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def verify_hash(path: Path, expected: str) -> str:
    actual = sha256_file(path)
    if actual != expected:
        raise IntegrityError(f"SHA-256 mismatch for {path}: expected {expected}, got {actual}")
    return actual


def identity_function_digest(path: Path) -> str:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    node = next(
        (n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "identity_scope"),
        None,
    )
    if node is None:
        raise IntegrityError("M identity_scope function is absent")
    segment = ast.get_source_segment(source, node)
    if segment is None:
        raise IntegrityError("cannot extract M identity_scope source")
    return sha256_bytes(segment.encode("utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise IntegrityError(f"invalid JSON at {path}:{line_number}: {exc}") from exc
            if not isinstance(record, dict):
                raise IntegrityError(f"non-object JSON at {path}:{line_number}")
            records.append(record)
    return records


def canonical_cohort_bytes(records: list[dict[str, Any]]) -> bytes:
    ordered = sorted(records, key=lambda r: r["id"])
    return "".join(
        f"{r['id']}\t{r['source_arxiv']}\t{r['source_publication_date']}\n" for r in ordered
    ).encode("utf-8")


def select_records(
    contrasts: list[dict[str, Any]], audit_rows: list[dict[str, str]]
) -> list[dict[str, Any]]:
    """Apply the frozen date/field selection; do not infer or substitute rows."""
    contrast_by_id: dict[str, dict[str, Any]] = {}
    for row in contrasts:
        item_id = row.get("id")
        if not item_id or item_id in contrast_by_id:
            raise IntegrityError(f"missing or duplicate E1 contrast id: {item_id!r}")
        contrast_by_id[item_id] = row

    audit_by_id: dict[str, dict[str, str]] = {}
    for row in audit_rows:
        item_id = row.get("item_id")
        if not item_id or item_id in audit_by_id:
            raise IntegrityError(f"missing or duplicate source-audit item_id: {item_id!r}")
        audit_by_id[item_id] = row

    selected = []
    for item_id, row in contrast_by_id.items():
        audit = audit_by_id.get(item_id)
        if audit is None:
            continue
        date_text = (audit.get("date") or "").strip()
        try:
            parsed_date = date.fromisoformat(date_text)
        except (TypeError, ValueError):
            continue
        if parsed_date.isoformat() != date_text or parsed_date.isoformat() < DATE_CUTOFF:
            continue
        required = ("A", "B", "B_min", "C", "source_arxiv")
        if not all(isinstance(row.get(key), str) and row[key].strip() for key in required):
            continue
        selected.append(
            {
                "id": item_id,
                "source_arxiv": row["source_arxiv"],
                "source_publication_date": parsed_date.isoformat(),
                "A": row["A"],
                "B": row["B"],
                "B_min": row["B_min"],
                "C": row["C"],
                "creator_author_code": row.get("author"),
                "second_reader_agrees": row.get("second_reader_agrees"),
            }
        )

    selected.sort(key=lambda r: r["id"])
    if len({r["source_arxiv"] for r in selected}) != len(selected):
        raise IntegrityError("selected records do not have one distinct source question each")
    return selected


def verify_prereg_table(prereg_path: Path, records: list[dict[str, Any]]) -> None:
    text = prereg_path.read_text(encoding="utf-8")
    table_rows = re.findall(r"^\| (h\d+) \| ([0-9.]+) \| (\d{4}-\d\d-\d\d) \|$", text, re.M)
    expected = [
        (r["id"], r["source_arxiv"], r["source_publication_date"])
        for r in records
    ]
    if table_rows != expected:
        raise IntegrityError("selected records do not exactly match the frozen preregistration table")
    if sha256_bytes(canonical_cohort_bytes(records)) != COHORT_SHA256:
        raise IntegrityError("selected cohort-list SHA-256 mismatch")


def author_intended_label(task: str) -> int:
    if task == "minimal_paraphrase":
        return 1
    if task == "near_miss":
        return 0
    raise ValueError(f"unsupported task: {task}")


def paired_cluster_bootstrap(
    identity_minimal: list[int],
    baseline_minimal: list[int],
    identity_near_miss: list[int],
    baseline_near_miss: list[int],
    draws: int = BOOTSTRAP_DRAWS,
    seed: int = BOOTSTRAP_SEED,
) -> dict[str, dict[str, Any]]:
    arrays = [
        np.asarray(x, dtype=np.float64)
        for x in (identity_minimal, baseline_minimal, identity_near_miss, baseline_near_miss)
    ]
    n = len(arrays[0])
    if n < 2 or any(a.ndim != 1 or len(a) != n for a in arrays):
        raise ValueError("paired bootstrap requires equal-length vectors for at least two questions")
    if draws != BOOTSTRAP_DRAWS or seed != BOOTSTRAP_SEED:
        raise ValueError("bootstrap draw count and seed are frozen by the preregistration")
    if any(not np.isin(a, [0.0, 1.0]).all() for a in arrays):
        raise ValueError("accuracy indicators must be binary")

    differences = {
        "minimal_paraphrase": arrays[0] - arrays[1],
        "near_miss": arrays[2] - arrays[3],
    }
    rng = np.random.Generator(np.random.PCG64(seed))
    indices = rng.integers(0, n, size=(draws, n))
    results = {}
    for task, diff in differences.items():
        samples = diff[indices].mean(axis=1)
        low, high = np.percentile(samples, [2.5, 97.5], method="linear")
        estimate = float(diff.mean())
        results[task] = {
            "estimate": estimate,
            "ci95_percentile": [float(low), float(high)],
            "draws": draws,
            "bootstrap_seed": seed,
            "margin": COMPARISON_MARGIN,
            "lower_ci_exceeds_margin": bool(float(low) > COMPARISON_MARGIN),
        }
    return results


def output_directory(path: Path) -> Path:
    """Create a new run directory only; existing paths are never overwritten."""
    path.mkdir(parents=True, exist_ok=False)
    return path


def load_frozen_e5(repo_root: Path, cache_root: Path | None = None):
    cache_root = cache_root or (Path.home() / ".cache/huggingface/hub")
    model_dir = cache_root / "models--intfloat--e5-base-v2"
    revision_ref = model_dir / "refs/main"
    if not revision_ref.is_file() or revision_ref.read_text().strip() != E5_REVISION:
        raise IntegrityError(f"cached E5 ref is not the frozen revision {E5_REVISION}")
    snapshot = model_dir / "snapshots" / E5_REVISION
    required = tuple(E5_ARTIFACT_SHA256)
    if any(not (snapshot / name).is_file() for name in required):
        raise IntegrityError("frozen E5 snapshot is incomplete in the local cache")
    artifacts = {name: sha256_file(snapshot / name) for name in required}
    if artifacts != E5_ARTIFACT_SHA256:
        raise IntegrityError("cached E5 artifact SHA-256 mismatch")

    # Import only during an explicitly invoked run; tests never instantiate a model.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError("sentence-transformers is required for the preregistered run") from exc
    model = SentenceTransformer(
        str(snapshot), device="cpu", local_files_only=True
    )
    return model, artifacts


def verify_frozen_inputs(repo_root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    prereg = repo_root / PREREG_PATH
    verify_hash(prereg, PREREG_SHA256)
    contrasts_path = repo_root / "E1/contrast.jsonl"
    audit_path = repo_root / "E1/results_v2/source_alignment_audit.csv"
    verify_hash(contrasts_path, CONTRASTS_SHA256)
    verify_hash(audit_path, AUDIT_SHA256)

    config_path = repo_root / "M/frozen/config.json"
    verify_hash(config_path, CONFIG_SHA256)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    encoders_path = repo_root / "M/encoders.py"
    encoder_hash = config["file_hashes"].get("M/encoders.py")
    if not encoder_hash:
        raise IntegrityError("frozen config does not bind M/encoders.py")
    verify_hash(encoders_path, encoder_hash)

    readouts_path = repo_root / "M/readouts.py"
    identity_digest = identity_function_digest(readouts_path)
    if identity_digest != IDENTITY_FUNCTION_SHA256:
        raise IntegrityError("M identity_scope differs from the preregistered readout")
    if config.get("identity_threshold") != IDENTITY_THRESHOLD:
        raise IntegrityError("M identity threshold differs from frozen 0.65")
    if config.get("encoder") != "E5 fixed 512-bin lexical hashing":
        raise IntegrityError("M identity representation differs from the frozen encoder")
    if config.get("improvement_margin") != COMPARISON_MARGIN:
        raise IntegrityError("comparison margin differs from the frozen 0.02 value")

    contrasts = read_jsonl(contrasts_path)
    with audit_path.open(encoding="utf-8", newline="") as stream:
        audit_rows = list(csv.DictReader(stream))
    selected = select_records(contrasts, audit_rows)
    if len(selected) != 60:
        raise IntegrityError(f"expected 60 selected records, found {len(selected)}")
    verify_prereg_table(prereg, selected)
    provenance = {
        "preregistration_commit": PREREG_COMMIT,
        "preregistration_sha256": PREREG_SHA256,
        "input_sha256": {
            "E1/contrast.jsonl": CONTRASTS_SHA256,
            "E1/results_v2/source_alignment_audit.csv": AUDIT_SHA256,
            "M/frozen/config.json": CONFIG_SHA256,
            "M/encoders.py": encoder_hash,
            "M/readouts.py_current_file": sha256_file(readouts_path),
            "M/readouts.py_frozen_config_file": config["file_hashes"].get("M/readouts.py"),
            "M/readouts.py_identity_scope_function": identity_digest,
        },
        "identity_scope_matches_frozen_function_digest": True,
        "readouts_module_file_changed_outside_identity_function": (
            sha256_file(readouts_path) != config["file_hashes"].get("M/readouts.py")
        ),
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "selection_sha256": COHORT_SHA256,
        "sample_count": len(selected),
        "unique_source_questions": len({r["source_arxiv"] for r in selected}),
        "date_cutoff": DATE_CUTOFF,
        "excluded_record_count": len(contrasts) - len(selected),
        "m_identity_threshold": IDENTITY_THRESHOLD,
        "b_q_threshold": BQ_THRESHOLD,
        "b_q_model": E5_MODEL_ID,
        "b_q_revision": E5_REVISION,
        "b_q_prefix": "query: ",
        "sentence_transformers_prompt_override": "",
        "embedding_normalization": "L2",
        "sentence_transformers_batch_size": 16,
        "show_progress_bar": False,
        "convert_to_numpy": True,
        "device": "cpu",
        "source_publication_date_min": min(r["source_publication_date"] for r in selected),
        "source_publication_date_max": max(r["source_publication_date"] for r in selected),
        "bootstrap": {
            "unit": "source question",
            "draws": BOOTSTRAP_DRAWS,
            "seed": BOOTSTRAP_SEED,
            "rng": "PCG64",
            "ci": "paired percentile 95%; linear empirical quantiles at 2.5% and 97.5%",
        },
        "comparison_margin": COMPARISON_MARGIN,
        "label_status": "unverified author-intended labels",
        "experiment_status": LABEL,
        "original_s1_completed": False,
        "results_overwritten": False,
    }
    return selected, provenance


def run(repo_root: Path, out_path: Path) -> Path:
    # Refuse an existing output before loading the encoder or computing predictions.
    if out_path.exists() or out_path.is_symlink():
        raise FileExistsError(f"refusing to overwrite existing output path: {out_path}")
    selected, provenance = verify_frozen_inputs(repo_root)

    model, model_artifact_hashes = load_frozen_e5(repo_root)
    texts = sorted({r[k] for r in selected for k in ("A", "B_min", "C")})
    prefixed = ["query: " + text for text in texts]
    vectors = model.encode(
        prefixed,
        batch_size=16,
        show_progress_bar=False,
        normalize_embeddings=True,
        convert_to_numpy=True,
        prompt="",
    )
    vectors = np.asarray(vectors, dtype=np.float64)
    if vectors.ndim != 2 or vectors.shape[0] != len(texts) or not np.isfinite(vectors).all():
        raise IntegrityError("E5 returned invalid or misaligned embeddings")
    norms = np.linalg.norm(vectors, axis=1)
    if not np.allclose(norms, 1.0, atol=1e-5, rtol=0):
        raise IntegrityError("E5 vectors are not L2 normalized")
    e5_vectors = dict(zip(texts, vectors))

    from M.encoders import HashEncoder
    from M.readouts import identity_scope
    from types import SimpleNamespace

    hash_encoder = HashEncoder()
    question_results = []
    task_correct = {
        "minimal_paraphrase": {"identity": [], "b_q": []},
        "near_miss": {"identity": [], "b_q": []},
    }
    for row in selected:
        pair_predictions = {}
        for task, variant_key in (("minimal_paraphrase", "B_min"), ("near_miss", "C")):
            original = row["A"]
            variant = row[variant_key]
            label = author_intended_label(task)
            left = SimpleNamespace(
                q=original,
                facets=(),
                question_vector=hash_encoder.encode(original),
                space_id=hash_encoder.space_id,
                feature_schema="shared-phi-v1",
            )
            right = SimpleNamespace(
                q=variant,
                facets=(),
                question_vector=hash_encoder.encode(variant),
                space_id=hash_encoder.space_id,
                feature_schema="shared-phi-v1",
            )
            identity_result = identity_scope(left, right)
            identity_prediction = int(identity_result["same_question"])
            bq_similarity = float(np.clip(np.dot(e5_vectors[original], e5_vectors[variant]), -1.0, 1.0))
            bq_prediction = int(bq_similarity >= BQ_THRESHOLD)
            task_correct[task]["identity"].append(int(identity_prediction == label))
            task_correct[task]["b_q"].append(int(bq_prediction == label))
            pair_predictions[task] = {
                "author_intended_label": label,
                "label_source": "E1 creator-intended assignment; unverified",
                "identity": {
                    "similarity": float(identity_result["score"]),
                    "prediction_same": identity_prediction,
                    "correct": int(identity_prediction == label),
                },
                "b_q": {
                    "cosine_similarity": bq_similarity,
                    "prediction_same": bq_prediction,
                    "correct": int(bq_prediction == label),
                },
            }
        question_results.append(
            {
                "e1_id": row["id"],
                "source_paper_id": row["source_arxiv"],
                "source_publication_date": row["source_publication_date"],
                "creator_author_code": row["creator_author_code"],
                "second_reader_agrees": row["second_reader_agrees"],
                "tasks": pair_predictions,
            }
        )

    bootstrap = paired_cluster_bootstrap(
        task_correct["minimal_paraphrase"]["identity"],
        task_correct["minimal_paraphrase"]["b_q"],
        task_correct["near_miss"]["identity"],
        task_correct["near_miss"]["b_q"],
    )
    metrics = {}
    for task, vals in task_correct.items():
        identity_accuracy = float(np.mean(vals["identity"]))
        bq_accuracy = float(np.mean(vals["b_q"]))
        metrics[task] = {
            "n_source_questions": len(selected),
            "label_counts": {
                "same": sum(1 for r in selected if author_intended_label(task) == 1),
                "different": sum(1 for r in selected if author_intended_label(task) == 0),
            },
            "identity_accuracy": identity_accuracy,
            "b_q_accuracy": bq_accuracy,
            "identity_minus_b_q_accuracy": bootstrap[task],
        }
    provenance["e5_model_artifact_sha256"] = model_artifact_hashes
    provenance["encoded_text_count"] = len(texts)
    payload = {
        "status_label": LABEL,
        "status": "EXPLORATORY_RESULT",
        "provenance": provenance,
        "metrics": metrics,
        "source_question_results": question_results,
        "interpretation_limits": [
            "Labels are unverified creator-intended assignments, not independent human judgments.",
            "E1 data and prior encoder results were exposed before this analysis.",
            "This does not complete original frozen S1.",
        ],
    }

    out_dir = output_directory(out_path)
    result_path = out_dir / "results.json"
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    fd = os.open(result_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "wb") as stream:
        stream.write(encoded)
    return result_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path, help="new, unused output directory")
    parser.add_argument(
        "--authorized",
        action="store_true",
        help="confirm the separate explicit authorization required by the preregistration",
    )
    args = parser.parse_args(argv)
    if not args.authorized:
        parser.error("execution requires the separate explicit authorization in the preregistration")
    repo_root = Path(__file__).resolve().parents[2]
    out_path = args.out if args.out.is_absolute() else repo_root / args.out
    try:
        result = run(repo_root, out_path)
    except Exception as exc:
        print(f"supplementary S1 aborted: {exc}", file=sys.stderr)
        return 2
    print(result.relative_to(repo_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
