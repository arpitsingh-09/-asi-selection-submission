import argparse
import json
import math
import sys
import time
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PLAN = ROOT / "data" / "manipulation_plan.jsonl"
OUTPUT = ROOT / "data" / "scoring_results.jsonl"

sys.path.insert(0, str(ROOT))
from novelty import score


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=None)
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error('--limit must be at least 1')

    with PLAN.open(encoding="utf-8") as f:
        cases = [json.loads(line) for line in f if line.strip()]

    completed = set()
    if OUTPUT.exists():
        with OUTPUT.open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("status") == "ok":
                    completed.add(record["case_id"])

    pending = [c for c in cases if c["case_id"] not in completed]

    print(f"Total planned cases: {len(cases)}")
    print(f"Already scored successfully: {len(completed)}")
    print(f"Cases remaining: {len(pending)}")
    if args.limit is not None:
        pending = pending[:args.limit]
        print(f"Pilot limit: {len(pending)} cases")
    print(f"Results file: {OUTPUT}")
    print("Starting scoring...")

    started = time.time()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("a", encoding="utf-8") as out:
        for i, case in enumerate(pending, 1):
            case_start = time.time()
            record = {
                "case_id": case["case_id"],
                "manipulation": case["manipulation"],
                "status": "error",
                "elapsed_seconds": None,
                "warnings": [],
            }

            try:
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    result = score(
                        idea_text=case["idea_text"],
                        claims=case["claims"],
                        pool_ids=case["pool_ids"],
                        t=case["t"],
                    )

                values = {
                    key: float(result[key])
                    for key in ("Y", "N", "density", "yours")
                }

                record["scores"] = values
                record["warnings"] = [
                    str(w.message) for w in caught
                ]

                if not all(math.isfinite(v) for v in values.values()):
                    record["status"] = "invalid_score"
                else:
                    record["status"] = "ok"

            except Exception as exc:
                record["error"] = f"{type(exc).__name__}: {exc}"

            record["elapsed_seconds"] = round(
                time.time() - case_start, 3
            )

            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            out.flush()

            if record["status"] == "ok":
                completed.add(case["case_id"])
                print(
                    f"[{i}/{len(pending)}] OK "
                    f"{case['case_id']} "
                    f"Y={record['scores']['Y']:.4f} "
                    f"N={record['scores']['N']:.4f} "
                    f"RND={record['scores']['density']:.4f} "
                    f"combined={record['scores']['yours']:.4f}"
                )
            else:
                print(
                    f"[{i}/{len(pending)}] "
                    f"{record['status'].upper()} "
                    f"{case['case_id']} "
                    f"{record.get('error', record.get('scores'))}"
                )

            if i % 25 == 0:
                print(
                    f"Progress: {i}/{len(pending)} this run; "
                    f"{len(completed)}/{len(cases)} successful overall; "
                    f"{time.time() - started:.1f}s elapsed"
                )

    print("\nScoring pass finished.")
    print(f"Successful unique cases: {len(completed)}/{len(cases)}")
    print(f"Elapsed time: {time.time() - started:.1f}s")
    print(f"Results saved to: {OUTPUT}")
    print("Inspect errors and warnings before interpreting results.")


if __name__ == "__main__":
    main()
