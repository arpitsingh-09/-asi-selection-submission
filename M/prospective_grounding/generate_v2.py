"""One-shot V2 local Ollama generation; no evaluation code is called here."""
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

REPO_ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PREREG_PATH = HERE / "PREREG_V2.md"
OUTPUT_ROOT = HERE / "generated_v2"
REQUESTS_PATH = REPO_ROOT / "M/prospective_a1/generation_requests.jsonl"
SOURCE_MANIFEST_PATH = REPO_ROOT / "M/prospective_a1/source_manifest.json"
DATASET_PATH = REPO_ROOT / "E2/data/raw_papers.jsonl"
SEEDS = {"video_memorability": (4900, 4901), "image_enhancement": (4910, 4911)}
V1_PRESERVATION_SHA256 = {
    "M/PREREG.md": "d996104d87f35435f25f1160e38ba1e7f335a35b84234dd1f43aa37b87c82bdd",
    "M/prospective_grounding/PREREG_DRAFT.md": "28e686939bb8eb40c1431490c9f82159aa9de67be6cc7e77d3a1ccbbcb6a8a5f",
    "M/prospective_grounding/workflow.py": "bc4abd5f9f54813b17c55b40ba306fa08df26994e2930e86c90b7f77810656dc",
    "M/prospective_grounding/generate.py": "a833a209b5c4c502f669c5a1d0f4afca283464fd418351cdd82aba0d6bc5aaac",
    "M/prospective_grounding/tests/test_workflow_safeguards.py": "4de253a0806f2293a75bb4be76fa032ff7267c4ac5656ffc998a8f8788d3f244",
    "M/prospective_grounding/tests/test_generate_cli.py": "e257c1983f4480b909a5b1f7409e2a6eb1a9728638ceac8d79f564b77b78d174",
    "M/prospective_grounding/generated_v1/ONE_SHOT_CLAIM.json": "961ba729c6589412d2b75c4649c1c06678f496d1e6c9dc788e6cef19e2d92d2c",
    "M/prospective_grounding/generated_v1/run_20261115T023429_468521Z/run.json": "e6b28e15d38b0541775af10768b7cdc58f8e4167e23c5b76800fc3f4857ca31d",
    "M/prospective_grounding/generated_v1/run_20261115T023429_468521Z/attempts/01_video_memorability_primary.json": "8f12074f0cd4746a41d1c3bf56ee7455a466a76927b2f40ffca93d37fa812fbc",
}
MODEL_LAYER_DIGEST = "sha256:a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f"
MODEL_CONFIG_DIGEST = "sha256:05a61d37b08453e59290add468e3bb2f688e23a01e967fecb0e2fa41218cea76"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _ollama_models_root() -> Path:
    return Path(os.environ.get("OLLAMA_MODELS", "~/.ollama/models")).expanduser()


def verify_committed_protocol(repo_root: Path = REPO_ROOT) -> str:
    """Require V2 preregistration and executable to be committed unchanged."""
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_root, check=True,
                            capture_output=True, text=True).stdout.strip()
    for path in ("M/prospective_grounding/PREREG_V2.md",
                 "M/prospective_grounding/generate_v2.py"):
        committed = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=repo_root,
                                   check=True, capture_output=True).stdout
        if committed != (repo_root / path).read_bytes():
            raise RuntimeError(f"V2 protocol file is not committed byte-for-byte: {path}")
    return commit


def verify_v1_preserved(repo_root: Path = REPO_ROOT) -> None:
    for relative, expected in V1_PRESERVATION_SHA256.items():
        path = repo_root / relative
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError(f"V1 preservation hash mismatch: {relative}")


def verify_frozen_inputs(repo_root: Path = REPO_ROOT) -> tuple[dict, dict[str, dict]]:
    manifest_path = repo_root / "M/prospective_a1/source_manifest.json"
    dataset_path = repo_root / "E2/data/raw_papers.jsonl"
    requests_path = repo_root / "M/prospective_a1/generation_requests.jsonl"
    if sha256_file(manifest_path) != SOURCE_MANIFEST_SHA256:
        raise RuntimeError("source manifest hash differs from the frozen V1 source manifest")
    if sha256_file(dataset_path) != DATASET_SHA256:
        raise RuntimeError("dataset hash differs from the frozen V1 dataset")
    manifest = json.loads(manifest_path.read_text())
    requests = [json.loads(line) for line in requests_path.read_text().splitlines() if line.strip()]
    source_by_family = {item["input_set_id"]: item for item in manifest["input_sets"]}
    request_by_family = {item["request_id"].removeprefix("prospective-a1-"): item for item in requests}
    if set(source_by_family) != set(SEEDS) or set(request_by_family) != set(SEEDS):
        raise RuntimeError("V2 requires exactly the two frozen source families")
    for family, request in request_by_family.items():
        source = source_by_family[family]
        papers = request["input_records"]
        if request.get("status") != "PREPARED_NOT_GENERATED" or len(papers) != 3:
            raise RuntimeError(f"invalid prepared request for {family}")
        if [paper["paper_id"] for paper in papers] != source["paper_ids"]:
            raise RuntimeError(f"input IDs differ from frozen source manifest for {family}")
        for expected, actual in zip(source["records"], papers):
            for key in ("paper_id", "published_at", "available_at", "source_url", "source_locator",
                        "source_sha256", "source_file_sha256", "title", "abstract"):
                if expected.get(key) != actual.get(key):
                    raise RuntimeError(f"source provenance differs for {actual.get('paper_id')}: {key}")
            if hashlib.sha256(actual["abstract"].encode()).hexdigest() != expected["abstract_sha256"]:
                raise RuntimeError(f"abstract hash mismatch for {actual['paper_id']}")
        if hashlib.sha256(request["prompt"].encode()).hexdigest() != request.get("prompt_sha256"):
            raise RuntimeError(f"primary prompt hash mismatch for {family}")
        if prepare_generation_request(papers=papers)["prompt"] != request["prompt"]:
            raise RuntimeError(f"primary prompt differs from the frozen prepared prompt for {family}")
    return manifest, request_by_family


def verify_local_model(models_root: Path | None = None) -> dict:
    models_root = models_root or _ollama_models_root()
    path = models_root / "manifests/registry.ollama.ai/library/qwen3/8b"
    if not path.is_file():
        raise RuntimeError("local qwen3:8b manifest is missing")
    raw_manifest = path.read_bytes()
    manifest = json.loads(raw_manifest)
    config = manifest.get("config", {}).get("digest")
    layers = manifest.get("layers", [])
    digests = [item.get("digest") for item in layers]
    if config != MODEL_CONFIG_DIGEST or MODEL_LAYER_DIGEST not in digests or GENERATOR_MODEL_DIGEST not in digests:
        raise RuntimeError("local qwen3:8b manifest digest differs from V2 preregistration")
    for descriptor in [manifest["config"], *layers]:
        blob = models_root / "blobs" / descriptor["digest"].replace(":", "-")
        if not blob.is_file() or blob.stat().st_size != descriptor["size"]:
            raise RuntimeError(f"local model artifact blob missing or wrong-sized: {descriptor['digest']}")
        if descriptor["digest"] == GENERATOR_MODEL_DIGEST and \
                sha256_file(blob) != GENERATOR_MODEL_DIGEST.removeprefix("sha256:"):
            raise RuntimeError("qwen3:8b Ollama ID blob hash mismatch")
    request = urllib.request.Request("http://127.0.0.1:11434/api/tags", method="GET")
    with urllib.request.urlopen(request, timeout=8) as response:
        tags = json.loads(response.read())
    models = [model for model in tags.get("models", []) if model.get("name") == GENERATOR_MODEL_ID]
    if len(models) != 1 or models[0].get("digest") not in (
            GENERATOR_MODEL_DIGEST, GENERATOR_MODEL_DIGEST.removeprefix("sha256:")):
        raise RuntimeError("Ollama API digest differs from the preregistered qwen3:8b artifact")
    return {"model_id": GENERATOR_MODEL_ID, "model_digest": GENERATOR_MODEL_DIGEST,
            "model_layer_digest": MODEL_LAYER_DIGEST, "config_digest": MODEL_CONFIG_DIGEST}


class OllamaV2Generator:
    """Single-call Ollama adapter with thinking explicitly disabled."""
    def __init__(self, opener=None):
        self.opener = opener or urllib.request.urlopen
        self.last_response = None
        self.last_call_started_at = None

    def __call__(self, *, prompt: str, model_id: str, parameters: dict, seed: int) -> str:
        self.last_call_started_at = utc_now()
        self.last_response = None
        payload = {"model": model_id, "prompt": prompt, "stream": False, "think": False,
                   "options": {**parameters, "seed": seed}}
        request = urllib.request.Request(
            "http://127.0.0.1:11434/api/generate",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST")
        try:
            with self.opener(request, timeout=1800) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            self.last_response = {"http_status": exc.code,
                                  "raw_http_body_utf8": raw.decode("utf-8", errors="replace")}
            raise
        parsed = json.loads(raw)
        self.last_response = {"raw_http_body_utf8": raw.decode("utf-8", errors="replace"), "parsed": parsed}
        if parsed.get("model") != model_id or not isinstance(parsed.get("response"), str) or not parsed["response"].strip():
            raise RuntimeError("Ollama returned an empty or invalid response; V2 stops without retry")
        return parsed["response"]


def make_plan(requests_by_family: dict) -> list[dict]:
    plan = []
    for family in ("video_memorability", "image_enhancement"):
        request = requests_by_family[family]
        primary_seed, decoy_seed = SEEDS[family]
        plan.append({"family": family, "kind": "primary", "seed": primary_seed, "request": request})
        decoy = prepare_decoy_request(papers=request["input_records"], model_id=GENERATOR_MODEL_ID,
                                      model_digest=GENERATOR_MODEL_DIGEST,
                                      parameters=GENERATOR_PARAMETERS, seed=decoy_seed)
        plan.append({"family": family, "kind": "decoy", "seed": decoy_seed,
                     "request": {**decoy, "input_records": request["input_records"]}})
    if [item["seed"] for item in plan] != [4900, 4901, 4910, 4911]:
        raise RuntimeError("V2 seed schedule mismatch")
    return plan


def _write_json(path: Path, record: dict, *, replace: bool = False) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("x", encoding="utf-8") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    if not replace and path.exists():
        temporary.unlink()
        raise FileExistsError(path)
    temporary.replace(path)


def _claim_output(output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    if any(output_root.iterdir()):
        raise RuntimeError("generated_v2 is already claimed or contains outputs; refusing overwrite/retry")
    claim = output_root / "ONE_SHOT_CLAIM.json"
    try:
        fd = os.open(claim, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise RuntimeError("V2 output already has a one-shot claim") from exc
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump({"claimed_at": utc_now()}, stream)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def run_once(*, repo_root: Path = REPO_ROOT, output_root: Path = OUTPUT_ROOT,
             models_root: Path | None = None, generator=None) -> Path:
    commit = verify_committed_protocol(repo_root)
    verify_v1_preserved(repo_root)
    manifest, requests = verify_frozen_inputs(repo_root)
    model = verify_local_model(models_root)
    plan = make_plan(requests)  # Fix and hash all four prompts before inference.
    _claim_output(output_root)
    run_dir = output_root / f"run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')}"
    run_dir.mkdir(exist_ok=False)
    (run_dir / "attempts").mkdir()
    run = {"status": "IN_PROGRESS", "protocol_commit": commit, "started_at": utc_now(),
           "v1_failure_reference": "generated_v1/run_20261115T023429_468521Z/attempts/01_video_memorability_primary.json",
           "source_manifest_sha256": SOURCE_MANIFEST_SHA256, "dataset_sha256": DATASET_SHA256,
           "model": model, "parameters": GENERATOR_PARAMETERS, "think": False,
           "seeds": [4900, 4901, 4910, 4911],
           "prompts": [{"family": item["family"], "kind": item["kind"], "seed": item["seed"],
                        "prompt": item["request"]["prompt"],
                        "prompt_sha256": item["request"]["prompt_sha256"],
                        "input_ids": [paper["paper_id"] for paper in item["request"]["input_records"]]}
                       for item in plan], "attempts": []}
    _write_json(run_dir / "run.json", run)
    generator = generator or OllamaV2Generator()
    for index, item in enumerate(plan, 1):
        family, kind, seed, request = item["family"], item["kind"], item["seed"], item["request"]
        papers = request["input_records"]
        name = f"{index:02d}_{family}_{kind}.json"
        path = run_dir / "attempts" / name
        attempt = {"status": "STARTED", "family": family, "kind": kind, "seed": seed,
                   "question_id": f"{'primary' if kind == 'primary' else 'decoy'}-{family}-v2",
                   "model_id": GENERATOR_MODEL_ID, "model_digest": GENERATOR_MODEL_DIGEST,
                   "parameters": GENERATOR_PARAMETERS, "think": False,
                   "input_ids": [paper["paper_id"] for paper in papers], "input_records": papers,
                   "prompt": request["prompt"], "prompt_sha256": request["prompt_sha256"],
                   "source_manifest_sha256": SOURCE_MANIFEST_SHA256, "dataset_sha256": DATASET_SHA256,
                   "attempt_started_at": utc_now(), "raw_model_output": None, "ollama_response": None}
        _write_json(path, attempt)
        try:
            if kind == "primary":
                record = generate_record(papers=papers, model_id=GENERATOR_MODEL_ID,
                                         parameters=GENERATOR_PARAMETERS, seed=seed, generator=generator)
            else:
                record = generate_decoy_record(papers=papers, model_id=GENERATOR_MODEL_ID,
                                               model_digest=GENERATOR_MODEL_DIGEST,
                                               parameters=GENERATOR_PARAMETERS, seed=seed, generator=generator)
            if record.get("prompt") != request["prompt"] or record.get("prompt_sha256") != request["prompt_sha256"]:
                raise RuntimeError("generation helper prompt differs from the pre-frozen V2 prompt")
            record.update({"question_id": attempt["question_id"],
                           "generated_at": generator.last_call_started_at or record.get("generated_at"),
                           "generation_call_started_at": generator.last_call_started_at,
                           "raw_model_output": generator.last_response["parsed"]["response"],
                           "ollama_response": generator.last_response, "family": family,
                           "model_digest": GENERATOR_MODEL_DIGEST, "think": False,
                           "source_manifest_sha256": SOURCE_MANIFEST_SHA256,
                           "dataset_sha256": DATASET_SHA256})
            validate_question(record)
            attempt.update(record)
            attempt["status"] = "SUCCEEDED"
            _write_json(path, attempt, replace=True)
        except BaseException as exc:
            attempt.update({"status": "FAILED", "generation_call_started_at": generator.last_call_started_at,
                            "error_type": type(exc).__name__, "error": str(exc),
                            "ollama_response": generator.last_response})
            _write_json(path, attempt, replace=True)
            run["status"] = "FAILED_STOPPED_NO_RETRY"
            run["failed_attempt"] = name
            run["attempts"].append(name)
            _write_json(run_dir / "run.json", run, replace=True)
            raise
        run["attempts"].append(name)
        _write_json(run_dir / "run.json", run, replace=True)
    run["status"] = "COMPLETE_4_OF_4"
    run["completed_at"] = utc_now()
    _write_json(run_dir / "run_complete.json", run)
    return run_dir


def main() -> int:
    try:
        print(f"V2 generation complete: {run_once()}")
    except Exception as exc:
        print(f"V2 generation stopped: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
