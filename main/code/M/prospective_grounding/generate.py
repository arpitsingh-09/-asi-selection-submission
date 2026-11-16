"""One-shot local Ollama generation for the preregistered grounding pilot.

Run from the repository root with: python3 -m M.prospective_grounding.generate
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.error
import urllib.request

from M.prospective_a1.workflow import generate_record, prepare_generation_request
from M.prospective_grounding.workflow import (
    DATASET_SHA256,
    GENERATOR_MODEL_DIGEST,
    GENERATOR_MODEL_ID,
    GENERATOR_PARAMETERS,
    SOURCE_MANIFEST_SHA256,
    generate_decoy_record,
    prepare_decoy_request,
    validate_question,
)

PREREG_COMMIT = "76c084a0679a52973542df43aa87866dbd1be782"
REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = Path(__file__).resolve().parent / "generated_v1"
REQUESTS_PATH = REPO_ROOT / "M/prospective_a1/generation_requests.jsonl"
SOURCE_MANIFEST_PATH = REPO_ROOT / "M/prospective_a1/source_manifest.json"
DATASET_PATH = REPO_ROOT / "E2/data/raw_papers.jsonl"
SEEDS = {"video_memorability": (4900, 4901), "image_enhancement": (4910, 4911)}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _ollama_models_root() -> Path:
    configured = os.environ.get("OLLAMA_MODELS")
    return Path(configured).expanduser() if configured else Path.home() / ".ollama/models"


def verify_preregistration(repo_root: Path = REPO_ROOT) -> None:
    if subprocess.run(["git", "rev-parse", "--verify", f"{PREREG_COMMIT}^{{commit}}"],
                      cwd=repo_root, check=True, capture_output=True, text=True).stdout.strip() != PREREG_COMMIT:
        raise RuntimeError("preregistration commit could not be resolved")
    for rel in ("prospective_grounding/PREREG_DRAFT.md", "prospective_grounding/workflow.py"):
        committed = subprocess.run(["git", "show", f"{PREREG_COMMIT}:M/{rel}"], cwd=repo_root,
                                   check=True, capture_output=True).stdout
        if committed != (repo_root / "M" / rel).read_bytes():
            raise RuntimeError(f"working preregistration file differs from frozen commit: {rel}")


def verify_frozen_inputs(repo_root: Path = REPO_ROOT) -> tuple[dict, dict[str, dict]]:
    manifest_path = repo_root / "M/prospective_a1/source_manifest.json"
    dataset_path = repo_root / "E2/data/raw_papers.jsonl"
    requests_path = repo_root / "M/prospective_a1/generation_requests.jsonl"
    if sha256_file(manifest_path) != SOURCE_MANIFEST_SHA256:
        raise RuntimeError("source manifest hash differs from preregistration")
    if sha256_file(dataset_path) != DATASET_SHA256:
        raise RuntimeError("dataset hash differs from preregistration")
    manifest = json.loads(manifest_path.read_text())
    requests = [json.loads(line) for line in requests_path.read_text().splitlines() if line.strip()]
    by_family = {item["input_set_id"]: item for item in manifest["input_sets"]}
    req_by_family = {item["request_id"].removeprefix("prospective-a1-"): item for item in requests}
    if set(by_family) != set(SEEDS) or set(req_by_family) != set(SEEDS):
        raise RuntimeError("prepared input families differ from the two preregistered families")
    for family, seeds in SEEDS.items():
        item, req = by_family[family], req_by_family[family]
        expected = item["records"]
        supplied = req["input_records"]
        if req.get("status") != "PREPARED_NOT_GENERATED":
            raise RuntimeError(f"request is not in its preregistered prepared state: {family}")
        if len(expected) != 3 or len(supplied) != 3:
            raise RuntimeError(f"family must have exactly three registered inputs: {family}")
        if [p["paper_id"] for p in supplied] != item["paper_ids"]:
            raise RuntimeError(f"request paper IDs differ from source manifest: {family}")
        for source, request_paper in zip(expected, supplied):
            if any(source.get(key) != request_paper.get(key) for key in (
                    "paper_id", "published_at", "available_at", "source_url", "source_locator",
                    "source_sha256", "source_file_sha256", "title", "abstract")):
                raise RuntimeError(f"request source provenance differs from manifest: {source['paper_id']}")
            if hashlib.sha256(request_paper["abstract"].encode()).hexdigest() != source["abstract_sha256"]:
                raise RuntimeError(f"abstract hash differs from source manifest: {source['paper_id']}")
        computed_prompt_hash = hashlib.sha256(req["prompt"].encode()).hexdigest()
        if req.get("prompt_sha256") != computed_prompt_hash:
            raise RuntimeError(f"prepared prompt hash mismatch: {family}")
        frozen_primary = prepare_generation_request(papers=supplied)
        if frozen_primary["prompt"] != req["prompt"]:
            raise RuntimeError(f"prepared primary prompt is not reproducible from its exact inputs: {family}")
    return manifest, req_by_family


def verify_local_model(models_root: Path | None = None) -> dict:
    """Verify the content-addressed Ollama manifest and its API-visible model digest."""
    models_root = models_root or _ollama_models_root()
    manifest_path = models_root / "manifests/registry.ollama.ai/library/qwen3/8b"
    if not manifest_path.is_file():
        raise RuntimeError("local qwen3:8b Ollama manifest is missing")
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    config = manifest.get("config", {}).get("digest")
    layer_digests = [item.get("digest") for item in manifest.get("layers", [])]
    if config != "sha256:05a61d37b08453e59290add468e3bb2f688e23a01e967fecb0e2fa41218cea76" or \
            "sha256:a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f" not in layer_digests or \
            GENERATOR_MODEL_DIGEST not in layer_digests:
        raise RuntimeError("local qwen3:8b manifest differs from preregistered artifact")
    for desc in [manifest["config"], *manifest["layers"]]:
        blob = models_root / "blobs" / desc["digest"].replace(":", "-")
        if not blob.is_file() or blob.stat().st_size != desc["size"]:
            raise RuntimeError(f"local Ollama artifact blob is missing or wrong-sized: {desc['digest']}")
        if desc["digest"] == GENERATOR_MODEL_DIGEST and sha256_file(blob) != GENERATOR_MODEL_DIGEST.removeprefix("sha256:"):
            raise RuntimeError("Ollama model ID blob content does not match the preregistered digest")

    request = urllib.request.Request("http://127.0.0.1:11434/api/tags", method="GET")
    with urllib.request.urlopen(request, timeout=8) as response:
        tags = json.loads(response.read())
    models = [item for item in tags.get("models", []) if item.get("name") == GENERATOR_MODEL_ID]
    if len(models) != 1 or models[0].get("digest") not in (
            GENERATOR_MODEL_DIGEST, GENERATOR_MODEL_DIGEST.removeprefix("sha256:")):
        raise RuntimeError("Ollama API does not report the exact preregistered qwen3:8b digest")
    return {"model_id": GENERATOR_MODEL_ID, "model_digest": GENERATOR_MODEL_DIGEST,
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "config_digest": config, "model_layer_digest": layer_digests[0]}


def make_plan(requests_by_family: dict) -> list[dict]:
    plan = []
    for family in ("video_memorability", "image_enhancement"):
        request = requests_by_family[family]
        primary_seed, decoy_seed = SEEDS[family]
        plan.append({"family": family, "kind": "primary", "seed": primary_seed,
                     "request": request})
        decoy_request = prepare_decoy_request(papers=request["input_records"], model_id=GENERATOR_MODEL_ID,
                                              model_digest=GENERATOR_MODEL_DIGEST,
                                              parameters=GENERATOR_PARAMETERS, seed=decoy_seed)
        plan.append({"family": family, "kind": "decoy", "seed": decoy_seed,
                     "request": {**decoy_request, "input_records": request["input_records"]}})
    if len(plan) != 4 or [item["seed"] for item in plan] != [4900, 4901, 4910, 4911]:
        raise RuntimeError("generation plan does not match the frozen four-seed schedule")
    return plan


def _write_json(path: Path, record: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("x", encoding="utf-8") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def _replace_json(path: Path, record: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("x", encoding="utf-8") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def _claim_one_shot(output_root: Path) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    if any(output_root.iterdir()):
        raise RuntimeError(f"output root is not empty; refusing retries or overwrite: {output_root}")
    lock_path = output_root / "ONE_SHOT_CLAIM.json"
    try:
        fd = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise RuntimeError("another or previous one-shot generation already claimed this output root") from exc
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump({"claimed_at": utc_now(), "prereg_commit": PREREG_COMMIT}, stream)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    return lock_path


class OllamaGenerator:
    def __init__(self):
        self.last_response = None
        self.last_call_started_at = None

    def __call__(self, *, prompt: str, model_id: str, parameters: dict, seed: int) -> str:
        self.last_call_started_at = utc_now()
        self.last_response = None
        body = {"model": model_id, "prompt": prompt, "stream": False,
                "options": {**parameters, "seed": seed}}
        request = urllib.request.Request(
            "http://127.0.0.1:11434/api/generate",
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=1800) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            raw_error = exc.read()
            self.last_response = {"http_status": exc.code,
                                  "raw_http_body_utf8": raw_error.decode("utf-8", errors="replace")}
            raise
        parsed = json.loads(raw)
        self.last_response = {"raw_http_body_utf8": raw.decode("utf-8", errors="replace"), "parsed": parsed}
        if parsed.get("model") != model_id or not isinstance(parsed.get("response"), str) or not parsed["response"].strip():
            raise RuntimeError("Ollama returned an invalid or empty generation response")
        return parsed["response"]


def _papers(request: dict) -> list[dict]:
    # Keep both manifest provenance and the exact prompt text prepared earlier.
    return request["input_records"]


def run_once(*, repo_root: Path = REPO_ROOT, output_root: Path = OUTPUT_ROOT,
             models_root: Path | None = None, generator=None) -> Path:
    verify_preregistration(repo_root)
    manifest, requests = verify_frozen_inputs(repo_root)
    model_provenance = verify_local_model(models_root)
    plan = make_plan(requests)
    _claim_one_shot(output_root)
    run_dir = output_root / f"run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')}"
    run_dir.mkdir(exist_ok=False)
    (run_dir / "attempts").mkdir()
    generator = generator or OllamaGenerator()
    run_record = {"status": "IN_PROGRESS", "created_at": utc_now(),
                  "prereg_commit": PREREG_COMMIT, "source_manifest_sha256": SOURCE_MANIFEST_SHA256,
                  "dataset_sha256": DATASET_SHA256, "model": model_provenance,
                  "generation_parameters": GENERATOR_PARAMETERS, "expected_seeds": [4900, 4901, 4910, 4911],
                  "input_families": {family: item["paper_ids"] for family, item in
                                      ((x["input_set_id"], x) for x in manifest["input_sets"])},
                  "prompts": [{"family": item["family"], "kind": item["kind"], "seed": item["seed"],
                               "prompt": item["request"]["prompt"],
                               "prompt_sha256": item["request"]["prompt_sha256"],
                               "input_ids": [p["paper_id"] for p in item["request"]["input_records"]]}
                              for item in plan],
                  "attempt_files": []}
    _write_json(run_dir / "run.json", run_record)

    for index, item in enumerate(plan, start=1):
        family, kind, seed, request = item["family"], item["kind"], item["seed"], item["request"]
        papers = _papers(request)
        filename = f"{index:02d}_{family}_{kind}.json"
        attempt_path = run_dir / "attempts" / filename
        attempt = {"status": "STARTED", "family": family, "kind": kind,
                   "question_id": f"{'primary' if kind == 'primary' else 'decoy'}-{family}",
                   "seed": seed, "model_id": GENERATOR_MODEL_ID, "model_digest": GENERATOR_MODEL_DIGEST,
                   "parameters": GENERATOR_PARAMETERS, "input_ids": [p["paper_id"] for p in papers],
                   "input_records": papers, "source_manifest_sha256": SOURCE_MANIFEST_SHA256,
                   "dataset_sha256": DATASET_SHA256, "prompt": request["prompt"],
                   "prompt_sha256": request["prompt_sha256"],
                   "attempt_started_at": utc_now(), "raw_model_output": None, "ollama_response": None}
        _write_json(attempt_path, attempt)
        try:
            if kind == "primary":
                record = generate_record(papers=papers, model_id=GENERATOR_MODEL_ID,
                                         parameters=GENERATOR_PARAMETERS, seed=seed, generator=generator)
            else:
                record = generate_decoy_record(papers=papers, model_id=GENERATOR_MODEL_ID,
                                               model_digest=GENERATOR_MODEL_DIGEST,
                                               parameters=GENERATOR_PARAMETERS, seed=seed, generator=generator)
            if record.get("prompt") != request["prompt"] or record.get("prompt_sha256") != request["prompt_sha256"]:
                raise RuntimeError("generation function prompt differs from the preregistered precomputed prompt")
            record.update({"question_id": attempt["question_id"], "model_digest": GENERATOR_MODEL_DIGEST,
                           "generated_at": generator.last_call_started_at or record.get("generated_at"),
                           "raw_model_output": generator.last_response["parsed"]["response"],
                           "ollama_response": generator.last_response})
            record["generation_call_started_at"] = generator.last_call_started_at
            record["family"] = family
            record["source_manifest_sha256"] = SOURCE_MANIFEST_SHA256
            record["dataset_sha256"] = DATASET_SHA256
            validate_question(record)
            attempt.update(record)
            attempt["status"] = "SUCCEEDED"
            _replace_json(attempt_path, attempt)
        except BaseException as exc:
            attempt.update({"status": "FAILED", "generation_call_started_at": generator.last_call_started_at,
                            "error_type": type(exc).__name__, "error": str(exc),
                            "ollama_response": generator.last_response})
            _replace_json(attempt_path, attempt)
            run_record["status"] = "FAILED_STOPPED_NO_RETRY"
            run_record["failed_attempt"] = filename
            run_record["attempt_files"].append(filename)
            _write_json(run_dir / "run.json", run_record)
            raise
        run_record["attempt_files"].append(filename)
        _replace_json(run_dir / "run.json", run_record)

    run_record["status"] = "COMPLETE_4_OF_4"
    run_record["completed_at"] = utc_now()
    _write_json(run_dir / "run_complete.json", run_record)
    return run_dir


def main() -> int:
    try:
        path = run_once()
    except Exception as exc:
        print(f"Generation stopped: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"Generation complete: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
