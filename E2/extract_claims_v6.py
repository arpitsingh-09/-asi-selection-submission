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
PROMPT_VERSION = "atomic-claims-v6"

DATA_DIR = Path("E2/data")
FOCAL_FILE = DATA_DIR / "focal_papers.csv"
PAPERS_FILE = DATA_DIR / "raw_papers.jsonl"
OUTPUT_FILE = DATA_DIR / "claims_v6_pilot3.jsonl"

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
You are extracting atomic scientific claims for a research novelty evaluation.

Use ONLY the paper title and abstract below. Do not use outside knowledge.
Do not infer findings or technical details that the abstract does not state.

Return exactly one valid JSON object with these two keys:
{{
  "claims": [
    {{
      "claim": "One concise, atomic scientific claim.",
      "evidence": "A verbatim supporting excerpt copied from the abstract."
    }}
  ],
  "limitations": ["A limitation of what can be established from the abstract."]
}}

CLAIM SELECTION RULES

1. Extract between 4 and 10 distinct scientific claims only if the abstract
   supports that many. Quality is more important than reaching four claims.
   If fewer are supported, return fewer and explain why in limitations.

2. A claim must express a specific scientific contribution, technical method,
   substantive finding, empirical result, or explicitly stated limitation
   of the research. Do not create claims just to summarize the abstract.

3. Exclude standalone administrative, bibliographic, or contextual details:
   author affiliations, publication details, code availability, and names of
   datasets or benchmarks used only to describe the experimental setup.

4. Do not treat background motivation, a research objective, or a hoped-for
   benefit as an established experimental finding. Preserve whether the
   abstract describes something as proposed, intended, evaluated, or found.

5. Do not split one contribution into multiple claims merely because the
   abstract describes its method, objective, motivation, and intended benefit
   in separate sentences. Merge statements that express the same core idea.

6. Keep claims distinct when they describe genuinely different contributions.
   For example, a method for estimating uncertainty and a separate method
   for generating explanations may be distinct technical contributions.

7. Include an evaluation result only when the abstract states a substantive
   result or comparison. Merely naming datasets, benchmarks, or experiments
   is not a scientific finding.

8. Do not invent numbers, comparisons, performance improvements, mechanisms,
   conclusions, or limitations. Do not strengthen a tentative author claim
   into a proven fact.

ADDITIONAL CLAIM-QUALITY CHECK

Before returning the JSON, review every candidate claim using these checks:

A. Contribution versus intention:
   If the abstract says a method is proposed with the objective of achieving
   an outcome, report the proposal or objective. Do not claim that the outcome
   was achieved unless the abstract reports supporting results.

B. Distinctness:
   Compare each candidate with all earlier candidates. If two claims describe
   the same core method, mechanism, objective, or finding, merge them into
   one precise claim. Different wording alone does not make claims distinct.

C. Substantive contribution:
   Do not count routine statements that experiments were conducted, a dataset
   was used, or a method was designed for a broad application as separate
   scientific contributions unless the abstract reports a specific substantive
   result or genuinely distinct technical contribution.

D. Evidence support:
   For each candidate, ask whether a reader could justify every material part
   of the claim using only its quoted evidence. If not, narrow the claim or
   choose a better supporting excerpt. Exact word matching alone is insufficient.

E. Conservative selection:
   Remove candidates that fail these checks. Return fewer claims rather than
   padding the list with background, intentions presented as findings,
   redundant paraphrases, or weak evaluation descriptions. Explain a genuine
   shortfall in limitations.

EVIDENCE RULES

9. Every claim must have evidence that directly supports the entire claim.

10. Each evidence value must be copied character-for-character from the
    abstract. It must be a complete, continuous substring of the abstract.
    Prefer a complete sentence or clause; do not paraphrase or repair it.

11. If a sentence supports only part of a claim, narrow the claim rather than
    making unsupported additions.

12. The same evidence excerpt may support more than one claim only when those
    claims express genuinely different contributions. Do not duplicate a
    claim or split the same contribution into overlapping paraphrases.

LIMITATIONS AND OUTPUT

13. If the abstract does not provide enough distinct scientific claims,
    return only the supported claims and explain the shortfall in limitations.
    Do not use dataset details, broad objectives, or duplicate claims to meet
    the minimum.

14. Limitations should describe what cannot be established from the available
    title and abstract. Do not imply that the full paper lacks information
    simply because the abstract omits it.

15. Return valid JSON only, without Markdown fences or additional commentary.
    Use exactly the keys "claims" and "limitations".

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
                "num_predict": 2800,
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
        """Validate claims individually while preserving rejected candidates."""
        if not isinstance(parsed, dict):
            return None, ["Model response is not a JSON object"]

        claims = parsed.get("claims")
        limitations = parsed.get("limitations", [])

        if not isinstance(claims, list):
            return None, ["'claims' must be a list"]

        if not isinstance(limitations, list):
            return None, ["'limitations' must be a list"]

        accepted = []
        rejected = []
        claim_errors = []
        seen = set()

        for index, item in enumerate(claims, start=1):
            errors = []

            if not isinstance(item, dict):
                rejected.append({
                    "candidate": item,
                    "validation_errors": [
                        f"Claim {index} is not an object"
                    ],
                })
                claim_errors.append(
                    f"Claim {index} is not an object"
                )
                continue

            claim = item.get("claim")
            evidence = item.get("evidence")

            if not isinstance(claim, str) or not claim.strip():
                errors.append(f"Claim {index} has no valid text")

            if not isinstance(evidence, str) or not evidence.strip():
                errors.append(f"Claim {index} has no evidence")
            elif evidence not in abstract:
                errors.append(
                    f"Claim {index} evidence is not an exact abstract excerpt"
                )
            else:
                # An exact substring must also start and end at word
                # boundaries. Check every occurrence in the abstract.
                positions = []
                search_from = 0

                while True:
                    position = abstract.find(evidence, search_from)
                    if position == -1:
                        break
                    positions.append(position)
                    search_from = position + 1

                def valid_boundaries(position):
                    end_position = position + len(evidence)

                    starts_mid_word = (
                        position > 0
                        and evidence[0].isalnum()
                        and abstract[position - 1].isalnum()
                    )

                    ends_mid_word = (
                        end_position < len(abstract)
                        and evidence[-1].isalnum()
                        and abstract[end_position].isalnum()
                    )

                    return not starts_mid_word and not ends_mid_word

                if not any(valid_boundaries(p) for p in positions):
                    first = positions[0]
                    last = first + len(evidence)

                    if (
                        first > 0
                        and evidence[0].isalnum()
                        and abstract[first - 1].isalnum()
                    ):
                        errors.append(
                            f"Claim {index} evidence starts mid-word"
                        )

                    if (
                        last < len(abstract)
                        and evidence[-1].isalnum()
                        and abstract[last].isalnum()
                    ):
                        errors.append(
                            f"Claim {index} evidence ends mid-word"
                        )

            if isinstance(claim, str) and claim.strip():
                normalized = " ".join(claim.lower().split())

                if normalized in seen:
                    errors.append(f"Claim {index} is a duplicate")
                else:
                    seen.add(normalized)

            if errors:
                rejected.append({
                    "candidate": item,
                    "validation_errors": errors,
                })
                claim_errors.extend(errors)
            else:
                accepted.append(item)

        # Keep at most ten accepted claims. Any extras remain auditable.
        if len(accepted) > 10:
            extras = accepted[10:]
            accepted = accepted[:10]

            for item in extras:
                error = "Maximum of 10 accepted claims allowed"
                rejected.append({
                    "candidate": item,
                    "validation_errors": [error],
                })
                claim_errors.append(error)

        status = (
            "needs_manual_review"
            if rejected or len(accepted) >= 4
            else "review_required_claim_count"
        )

        return {
            "claims": accepted,
            "rejected_claims": rejected,
            "limitations": limitations,
            "status": status,
            "validation_errors": claim_errors,
            "attempts": 0,
        }, []


    best_result = None
    best_rank = (-1, float("-inf"))
    response_errors = []

    for attempt in range(2):
        try:
            if attempt == 0:
                current_prompt = base_prompt
            else:
                current_prompt = base_prompt + """

RETRY CORRECTION REQUIREMENTS:
The previous response contained claims with invalid evidence.
Regenerate the complete JSON object.

EVIDENCE REQUIREMENTS:
- Copy a complete clause or sentence exactly from the abstract.
- Preserve original spelling and punctuation.
- Never end an excerpt in the middle of a word.
- Do not include explanations or reasoning in evidence fields.
- Remove claims that cannot be supported by exact evidence.
- Distinguish proposed objectives from demonstrated results.
- Do not pad the claim count.

Return valid JSON with exactly the keys "claims" and "limitations".
Do not include Markdown or commentary.
"""

            candidate = call_model(current_prompt)
            validated, errors = validate(candidate)

            if errors or validated is None:
                response_errors.extend(errors)
                continue

            validated["attempts"] = len(raw_responses)

            # Prefer the response with the most accepted claims, then the
            # fewest rejected claims. Preserve the best attempt for review.
            rank = (
                len(validated["claims"]),
                -len(validated["rejected_claims"]),
            )

            if rank > best_rank:
                best_rank = rank
                best_result = validated

            # A complete response with no rejected claims needs no retry.
            if not validated["rejected_claims"]:
                break

        except (ValueError, json.JSONDecodeError) as exc:
            response_errors.append(f"Invalid JSON or response: {exc}")
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Could not contact Ollama: {exc}"
            ) from exc

    if best_result is not None:
        best_result["raw_responses"] = raw_responses
        best_result["attempts"] = len(raw_responses)
        best_result["validation_errors"] = (
            best_result["validation_errors"] + response_errors
        )
        return best_result

    # Neither response was usable JSON. Preserve raw output for diagnosis.
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
        "claims": [],
        "rejected_claims": [
            {
                "candidate": item,
                "validation_errors": [
                    "Response could not be parsed and validated"
                ],
            }
            for item in candidate_claims
        ],
        "unvalidated_candidate_claims": candidate_claims,
        "limitations": candidate_limitations,
        "status": "needs_manual_review",
        "validation_errors": response_errors or [
            "No response could be parsed and validated"
        ],
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
