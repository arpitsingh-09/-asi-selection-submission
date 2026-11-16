#!/usr/bin/env python3

import argparse
import csv
import json
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

MODEL = "deepseek-r1:8b"
PROMPT_VERSION = "atomic-claims-v1"

DATA_DIR = Path("E2/data")
FOCAL_FILE = DATA_DIR / "focal_papers.csv"
PAPERS_FILE = DATA_DIR / "raw_papers.jsonl"
OUTPUT_FILE = DATA_DIR / "claims_pilot.jsonl"

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"


def load_papers():
    papers = {}

    with PAPERS_FILE.open(encoding="utf-8") as f:
        for line in f:
            paper = json.loads(line)
            key = (paper["pool"], paper["paper_id"])
            papers[key] = paper

    return papers


def extract_claims(title, abstract):
    """
    Extract candidate atomic claims, retry once on validation failures,
    and preserve raw responses and validation errors for audit.
    """
    base_prompt = f"""
You are extracting research claims for a scientific novelty evaluation.

Use ONLY the title and abstract below. Do not use outside knowledge.

Return one JSON object with exactly these keys:
{{
  "claims": [
    {{
      "claim": "One concise, atomic research claim.",
      "evidence": "A verbatim supporting excerpt copied from the abstract."
    }}
  ],
  "limitations": ["Any relevant limitation of the available abstract."]
}}

Requirements:
1. Extract 4 to 10 distinct atomic claims when the abstract supports them.
2. Every claim must be supported by its evidence excerpt.
3. Copy each evidence excerpt character-for-character from the abstract.
4. Every evidence excerpt must be a complete, continuous substring of the
   abstract. Prefer a complete sentence or clause; never cut a word or
   stop an excerpt halfway through a sentence.
5. Do not paraphrase, repair, or add words to an evidence excerpt.
6. Each claim should express one contribution, finding, method, or result.
6. Do not invent numerical results, comparisons, findings, or contributions.
7. Do not turn background motivation into a claimed research result.
8. Do not express the same contribution as multiple claims.
9. If fewer than four distinct claims are supported, return only those
   supported claims and explain why in "limitations".
10. Return valid JSON only, without Markdown fences.

TITLE:
{title}

ABSTRACT:
{abstract}
"""

    raw_responses = []
    validation_errors = []

    def call_model(prompt):
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "think": False,
            "options": {
                "temperature": 0,
                "num_predict": 1800,
            },
        }

        request = urllib.request.Request(
            OLLAMA_ENDPOINT,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=600) as response:
            result = json.loads(response.read().decode("utf-8"))

        generated = result.get("response", "")
        raw_responses.append(generated)
        return json.loads(generated)

    def validate(parsed):
        errors = []

        if not isinstance(parsed, dict):
            return None, ["Model response is not a JSON object"]

        claims = parsed.get("claims")
        limitations = parsed.get("limitations", [])

        if not isinstance(claims, list):
            return None, ["'claims' must be a list"]

        if not isinstance(limitations, list):
            errors.append("'limitations' must be a list")
            limitations = []

        if len(claims) > 10:
            errors.append(
                f"Maximum 10 claims allowed; received {len(claims)}"
            )
        elif len(claims) < 4:
            if not limitations or not any(
                isinstance(item, str) and item.strip()
                for item in limitations
            ):
                errors.append(
                    "Fewer than 4 claims returned without an explanation "
                    "in limitations"
                )

        seen = set()

        for index, item in enumerate(claims, start=1):
            if not isinstance(item, dict):
                errors.append(f"Claim {index} is not an object")
                continue

            claim = item.get("claim")
            evidence = item.get("evidence")

            if not isinstance(claim, str) or not claim.strip():
                errors.append(f"Claim {index} has no valid text")
                continue

            if not isinstance(evidence, str) or not evidence.strip():
                errors.append(f"Claim {index} has no evidence")
            elif evidence not in abstract:
                errors.append(
                    f"Claim {index} evidence is not an exact abstract excerpt"
                )

            normalized = " ".join(claim.lower().split())
            if normalized in seen:
                errors.append(f"Duplicate claim detected: {claim}")
            seen.add(normalized)

        if errors:
            return None, errors

        status = (
            "needs_manual_review"
            if len(claims) >= 4
            else "review_required_claim_count"
        )

        return {
            "claims": claims,
            "limitations": limitations,
            "status": status,
        }, []

    parsed = None

    for attempt in range(2):
        try:
            if attempt == 0:
                current_prompt = base_prompt
            else:
                current_prompt = base_prompt + """

Your previous response failed these validation checks:
""" + "\n".join(
                    f"- {error}" for error in validation_errors
                ) + """

Regenerate the complete JSON object. Correct every listed error.
Most importantly, each evidence value must be copied character-for-character
from the abstract. Do not invent evidence to reach a target claim count.
"""

            candidate = call_model(current_prompt)
            validated, errors = validate(candidate)

            if not errors:
                parsed = validated
                break

            validation_errors = errors

        except (ValueError, json.JSONDecodeError) as exc:
            validation_errors = [f"Invalid JSON or response: {exc}"]
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Could not contact Ollama: {exc}") from exc

    if parsed is not None:
        parsed["raw_responses"] = raw_responses
        parsed["validation_errors"] = []
        parsed["attempts"] = len(raw_responses)
        return parsed

    # Preserve candidates from the last response for inspection, but never
    # label invalid candidates as validated claims.
    last_candidate = {}
    if raw_responses:
        try:
            last_candidate = json.loads(raw_responses[-1])
        except (ValueError, json.JSONDecodeError):
            pass

    candidate_claims = (
        last_candidate.get("claims", [])
        if isinstance(last_candidate, dict)
        and isinstance(last_candidate.get("claims", []), list)
        else []
    )
    candidate_limitations = (
        last_candidate.get("limitations", [])
        if isinstance(last_candidate, dict)
        and isinstance(last_candidate.get("limitations", []), list)
        else []
    )

    return {
        "claims": candidate_claims,
        "limitations": candidate_limitations,
        "status": "needs_manual_review",
        "validation_errors": validation_errors,
        "raw_responses": raw_responses,
        "attempts": len(raw_responses),
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Number of focal-paper selections to process; default: 3",
    )
    parser.add_argument(
        "--output",
        default=str(OUTPUT_FILE),
        help="Output JSONL path",
    )
    args = parser.parse_args()

    if args.limit < 1:
        raise SystemExit("--limit must be at least 1")

    papers = load_papers()

    with FOCAL_FILE.open(newline="", encoding="utf-8") as f:
        focal = list(csv.DictReader(f))

    selected = focal[:args.limit]
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        raise SystemExit(
            f"Refusing to overwrite existing file: {output_path}"
        )

    counts = Counter()

    with output_path.open("w", encoding="utf-8") as out:
        for index, row in enumerate(selected, start=1):
            key = (row["pool"], row["paper_id"])
            paper = papers.get(key)

            if not paper:
                raise SystemExit(f"Paper missing from dataset: {key}")

            abstract = paper.get("abstract", "").strip()

            if not abstract:
                raise SystemExit(f"Missing abstract: {key}")

            print(
                f"[{index}/{len(selected)}] "
                f"{row['pool']} | {row['paper_id']} | "
                f"{row['title']}",
                flush=True,
            )

            record = {
                "pool": row["pool"],
                "paper_id": row["paper_id"],
                "published": row["published"],
                "title": row["title"],
                "model": MODEL,
                "prompt_version": PROMPT_VERSION,
                "source_text": "title_and_abstract",
                "extracted_at_utc": datetime.now(
                    timezone.utc
                ).isoformat(),
            }

            try:
                extracted = extract_claims(row["title"], abstract)
                record.update(extracted)
                counts[record["status"]] += 1

                print(
                    f"  Claims: {len(record['claims'])}; "
                    f"status: {record['status']}",
                    flush=True,
                )

            except Exception as exc:
                record["claims"] = []
                record["limitations"] = []
                record["status"] = "extraction_error"
                record["error"] = str(exc)
                counts["extraction_error"] += 1

                print(f"  ERROR: {exc}", flush=True)

            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            out.flush()

    print("\nPILOT COMPLETE")
    print(f"Output: {output_path}")
    print(f"Records: {sum(counts.values())}")
    print(f"Status counts: {dict(counts)}")
    print("All generated claims require human review.")


if __name__ == "__main__":
    main()
