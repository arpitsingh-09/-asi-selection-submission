"""Validate and summarize development-only E6 token-usage profiles.

The profile uses only the ten rows in development_manifest_v2 and never
updates the preregistered token cap. Model execution is injected so callers
must explicitly provide their local development runner and trusted D-empty
leakage auditor. The resulting cap statistic is descriptive, not approval.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import statistics
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

ROOT = Path(__file__).resolve().parent
DEFAULT_MANIFEST = ROOT / "data/development_manifest_v2.json"
ARMS = ("D", "QH", "QH-sel", "QH-rand", "HQ", "D-empty", "D-shuffled")
SCHEMA = "e6-development-token-budget-profile-v1"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":"), allow_nan=False).encode("utf-8")
    return _sha256(raw)


def load_development_manifest(path: Path = DEFAULT_MANIFEST) -> tuple[dict[str, Any], str]:
    raw = Path(path).read_bytes()
    manifest = json.loads(raw)
    if (not isinstance(manifest, dict)
            or manifest.get("schema_version") != "e6-development-manifest-v2"
            or manifest.get("split") != "DEVELOPMENT"
            or manifest.get("status") != "development_only_prepared_not_frozen"):
        raise ValueError("profile requires the existing non-frozen DEVELOPMENT manifest v2")
    rows = manifest.get("inputs")
    if not isinstance(rows, list) or len(rows) != 10:
        raise ValueError("expected the ten existing development records")
    ids = [row.get("paper_id") for row in rows if isinstance(row, Mapping)]
    if len(ids) != 10 or len(set(ids)) != 10:
        raise ValueError("development manifest must contain ten unique paper IDs")
    for row in rows:
        if (not isinstance(row, Mapping) or row.get("split") != "DEVELOPMENT"
                or row.get("eligibility", {}).get("nonempty_abstract") is not True
                or not isinstance(row.get("abstract"), str) or not row["abstract"].strip()):
            raise ValueError("development record failed split or evidence validation")
    return manifest, _sha256(raw)


def build_profile_attestation(manifest_sha256: str, task_text: str, *,
                              task_matches_profile_constant: bool) -> dict[str, Any]:
    """Create the narrow attestation consumed by orchestrator profile mode."""
    if not isinstance(task_text, str) or not task_text.strip():
        raise ValueError("task_text must be nonempty")
    if len(manifest_sha256) != 64:
        raise ValueError("development manifest SHA-256 is required")
    return {
        "scope": "e6_development_token_profile_only",
        "manifest_sha256": manifest_sha256,
        "task_sha256": _sha256(task_text.encode("utf-8")),
        "task_matches_profile_constant": task_matches_profile_constant is True,
    }


def summarize_development_token_profile(
    manifest: Mapping[str, Any], envelopes: Sequence[Mapping[str, Any]], *,
    manifest_sha256: str, profile_cap: int,
) -> dict[str, Any]:
    """Summarize actual seven-arm usage without changing E6 configuration."""
    if type(profile_cap) is not int or profile_cap < 1:
        raise ValueError("profile_cap must be a positive temporary development ceiling")
    rows = manifest.get("inputs") if isinstance(manifest, Mapping) else None
    if not isinstance(rows, list):
        raise ValueError("development manifest has no input rows")
    allowed = {row["paper_id"] for row in rows if isinstance(row, Mapping)
               and row.get("split") == "DEVELOPMENT"}
    if not allowed:
        raise ValueError("development manifest has no DEVELOPMENT IDs")
    seen: set[str] = set()
    observed: dict[str, list[int]] = {arm: [] for arm in ARMS}
    uncensored: dict[str, list[int]] = {arm: [] for arm in ARMS}
    incomplete: list[dict[str, Any]] = []
    per_input_usage: list[dict[str, Any]] = []
    for index, envelope in enumerate(envelopes):
        if not isinstance(envelope, Mapping):
            raise ValueError(f"profile envelope {index} must be an object")
        input_id = envelope.get("paper_id")
        if input_id not in allowed or envelope.get("execution_mode") != "development_profile":
            raise ValueError(f"profile envelope {index} is not an authorized development profile row")
        if input_id in seen:
            raise ValueError(f"duplicate profile envelope for {input_id}")
        seen.add(input_id)
        accounting = envelope.get("token_budget_accounting")
        if not isinstance(accounting, Mapping) or set(accounting) != set(ARMS):
            raise ValueError(f"{input_id} lacks complete seven-arm token accounting")
        input_usage: dict[str, Any] = {"input_set_id": input_id, "arms": {}}
        for arm in ARMS:
            report = accounting[arm]
            used = report.get("tokens_used") if isinstance(report, Mapping) else None
            arm_results = envelope.get("arms")
            arm_result = arm_results.get(arm, {}) if isinstance(arm_results, Mapping) else {}
            if type(used) is int and used >= 0:
                observed[arm].append(used)
                if (report.get("budget_status") == "within_budget"
                        and report.get("blocked_call_count", 0) == 0
                        and isinstance(arm_result, Mapping)
                        and arm_result.get("execution_status") == "succeeded"):
                    uncensored[arm].append(used)
            else:
                incomplete.append({"input_set_id": input_id, "arm": arm,
                                   "status": report.get("budget_status") if isinstance(report, Mapping) else "missing",
                                   "tokens_used": used})
            if (isinstance(report, Mapping)
                    and (report.get("budget_status") != "within_budget"
                         or report.get("blocked_call_count", 0) > 0)):
                incomplete.append({"input_set_id": input_id, "arm": arm,
                                   "status": report.get("budget_status"),
                                   "tokens_used": used})
            call_log = envelope.get("call_accounting")
            calls = call_log.get("calls", []) if isinstance(call_log, Mapping) else []
            input_usage["arms"][arm] = {
                "tokens_used": used,
                "budget_tokens": report.get("budget_tokens") if isinstance(report, Mapping) else None,
                "budget_status": report.get("budget_status") if isinstance(report, Mapping) else "missing",
                "blocked_call_count": report.get("blocked_call_count") if isinstance(report, Mapping) else None,
                "execution_status": arm_result.get("execution_status") if isinstance(arm_result, Mapping) else "missing",
                "calls": [
                    {key: call.get(key) for key in (
                        "stage", "status", "input_tokens", "output_tokens", "total_tokens",
                        "prompt_sha256", "budget_participants", "requested_output_token_limit",
                    ) if key in call}
                    for call in calls
                    if isinstance(call, Mapping)
                    and arm in call.get("budget_participants", [])
                ] if isinstance(calls, list) else [],
            }
        per_input_usage.append(input_usage)
    summaries = {}
    for arm, values in observed.items():
        summaries[arm] = {
            "observed_input_count": len(values),
            "minimum_tokens": min(values) if values else None,
            "median_tokens": statistics.median(values) if values else None,
            "maximum_tokens": max(values) if values else None,
            "candidate_floor_from_observed_complete_runs": (
                max(uncensored[arm]) if uncensored[arm] else None
            ),
        }
    unsigned = {
        "schema_version": SCHEMA,
        "status": "development_profile_descriptive_pending_review",
        "approval_required": True,
        "confirmatory_experiment": False,
        "configured_e6_token_cap_changed": False,
        "development_manifest_sha256": manifest_sha256,
        "profile_ceiling_tokens_per_arm": profile_cap,
        "profiled_input_set_ids": sorted(seen),
        "per_input_usage": per_input_usage,
        "arms": summaries,
        "incomplete_arm_cells": incomplete,
        "candidate_floor_is_not_a_recommended_or_approved_cap": True,
        "profile_cap_exhaustion_count": sum(
            row.get("budget_status") == "cap_reached" or row.get("blocked_call_count", 0) > 0
            for env in envelopes
            for row in env.get("token_budget_accounting", {}).values()
            if isinstance(row, Mapping) and type(row.get("tokens_used")) is int
        ),
        "notes": [
            "Only DEVELOPMENT records may be supplied.",
            "Every arm call, preflight, retry and shared call must already be metered by the E6 controller.",
            "The observed maximum is descriptive and does not set the confirmatory cap.",
            "Any profile ceiling hit leaves that arm cell right-censored and unusable as a cap estimate.",
        ],
    }
    result = dict(unsigned)
    result["profile_sha256"] = _canonical_hash(unsigned)
    return result


def run_development_profile(
    *, task_text: str, profile_cap: int, runner: Callable[[Mapping[str, Any], str, int], Mapping[str, Any]],
    manifest_path: Path = DEFAULT_MANIFEST,
    limit: int | None = None, checkpoint_dir: Path | None = None,
) -> dict[str, Any]:
    """Invoke an explicitly injected local runner on the ten development rows."""
    if not isinstance(task_text, str) or not task_text.strip():
        raise ValueError("an explicit task_text is required; no task is invented by this tool")
    if not callable(runner):
        raise ValueError("a local development runner with exact token accounting is required")
    if type(profile_cap) is not int or profile_cap < 1:
        raise ValueError("profile_cap must be a positive temporary development ceiling")
    manifest, manifest_sha = load_development_manifest(manifest_path)
    if limit is not None and (type(limit) is not int or not 1 <= limit <= 10):
        raise ValueError("limit must be an integer from 1 to 10")
    if checkpoint_dir is not None:
        for index in range(1, len(manifest["inputs"][:limit]) + 1):
            checkpoint = Path(checkpoint_dir) / f"record_{index:02d}.json"
            if checkpoint.exists():
                raise FileExistsError(f"checkpoint already exists: {checkpoint}")
    envelopes = []
    for index, record in enumerate(manifest["inputs"][:limit], 1):
        envelope = runner(record, task_text, profile_cap)
        if not isinstance(envelope, Mapping):
            raise ValueError("development runner must return an auditable envelope")
        # Validate before persisting; each completed record survives a later failure.
        summarize_development_token_profile(
            manifest, [envelope], manifest_sha256=manifest_sha, profile_cap=profile_cap,
        )
        if checkpoint_dir is not None:
            write_exclusive(Path(checkpoint_dir) / f"record_{index:02d}.json", [dict(envelope)])
        envelopes.append(dict(envelope))
    return summarize_development_token_profile(
        manifest, envelopes, manifest_sha256=manifest_sha, profile_cap=profile_cap,
    )


def write_exclusive(path: Path, profile: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(profile, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--envelopes", type=Path,
                              help="JSON array of development_profile envelopes to summarize")
    source_group.add_argument("--runner", help="local module:callable implementing (record, task, cap) -> envelope")
    parser.add_argument("--limit", type=int, help="profile only the first N DEVELOPMENT rows (1-10)")
    parser.add_argument("--checkpoint-dir", type=Path, help="new directory for exclusive per-record envelopes")
    parser.add_argument("--task-file", type=Path,
                        help="explicit reviewed generic task text; required with --runner")
    parser.add_argument("--profile-cap", type=int, required=True,
                        help="temporary per-arm ceiling for this development profile only")
    parser.add_argument("--output", type=Path, required=True,
                        help="new versioned profile path; never overwrites")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args(argv)
    try:
        manifest, manifest_sha = load_development_manifest(args.manifest)
        if args.runner:
            if args.task_file is None:
                raise ValueError("--task-file is required with --runner")
            if ":" not in args.runner:
                raise ValueError("--runner must be module:callable")
            module_name, function_name = args.runner.split(":", 1)
            runner = getattr(importlib.import_module(module_name), function_name, None)
            if not callable(runner):
                raise ValueError("--runner target is not callable")
            task_text = args.task_file.read_text(encoding="utf-8").strip()
            profile = run_development_profile(
                task_text=task_text, profile_cap=args.profile_cap, runner=runner,
                manifest_path=args.manifest, limit=args.limit, checkpoint_dir=args.checkpoint_dir,
            )
        else:
            if args.limit is not None or args.checkpoint_dir is not None:
                raise ValueError("--limit and --checkpoint-dir require --runner")
            if args.task_file is not None:
                raise ValueError("--task-file is only valid with --runner")
            envelopes = json.loads(args.envelopes.read_text(encoding="utf-8"))
            if not isinstance(envelopes, list):
                raise ValueError("--envelopes must contain a JSON array")
            profile = summarize_development_token_profile(
                manifest, envelopes, manifest_sha256=manifest_sha, profile_cap=args.profile_cap,
            )
        write_exclusive(args.output, profile)
    except (OSError, ValueError, json.JSONDecodeError, FileExistsError) as exc:
        parser.error(str(exc))
    print(json.dumps({"output": str(args.output), "status": profile["status"],
                      "profiled_input_count": len(profile["profiled_input_set_ids"]),
                      "profile_sha256": profile["profile_sha256"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
