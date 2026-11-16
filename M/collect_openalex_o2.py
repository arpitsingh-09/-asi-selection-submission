"""Collect source-bound OpenAlex citation/date evidence for the frozen O2 IDs.

This collector never changes the lock or scores a model. It caches raw API
responses and writes a derived seed-overlap/outcome audit under a new directory.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = "https://api.openalex.org/works"
SELECT = "id,doi,title,publication_date,ids,referenced_works,cited_by_count,cited_by_api_url,updated_date"
CITING_SELECT = "id,doi,title,publication_date,ids,referenced_works,updated_date"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def rows(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def fetch(params: dict, raw_dir: Path, stem: str, receipts: list):
    url = API + "?" + urlencode(params, safe=":,|*")
    request = Request(url, headers={"User-Agent": "ASI-Lab-M-O2-evidence/1.0"})
    with urlopen(request, timeout=60) as response:
        body = response.read()
    acquired = stamp()
    path = raw_dir / f"{stem}.json"
    with path.open("xb") as handle:
        handle.write(body)
    receipts.append({"path": str(path), "url": url, "acquired_at_utc": acquired, "sha256": sha(body)})
    return json.loads(body)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="M/data/openalex_o2_v1")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    out = Path(args.out)
    out = out if out.is_absolute() else root / out
    out.mkdir(parents=True, exist_ok=False)
    raw_dir = out / "raw"
    raw_dir.mkdir()

    frozen_path = root / "M/frozen/O2_test_list.json"
    manifest_path = root / "M/data/manifests_v2/test.jsonl"
    frozen = json.loads(frozen_path.read_text())
    frozen_qids = set(frozen["question_ids"])
    manifest_rows = [r for r in rows(manifest_path) if r.get("question_id") in frozen_qids]
    by_qid = {r["question_id"]: r for r in manifest_rows}
    if set(by_qid) != frozen_qids:
        raise ValueError("O2 frozen question IDs do not map exactly to manifest rows")

    paper_rows = {}
    for question_id in sorted(frozen_qids):
        row = by_qid[question_id]
        paper_id = str(row["paper_id"])
        base_id = paper_id.rsplit("v", 1)[0] if paper_id.rsplit("v", 1)[-1].isdigit() else paper_id
        doi = f"10.48550/arxiv.{base_id}".lower()
        item = paper_rows.setdefault(paper_id, {"paper_id": paper_id, "doi": doi, "question_ids": [], "manifest_rows": []})
        item["question_ids"].append(question_id)
        item["manifest_rows"].append({
            "question_id": question_id,
            "title": row.get("title"),
            "published": row.get("published"),
            "available_at": row.get("available_at"),
            # O2 seed IDs are the explicitly supplied input set R, not every
            # item in the paper's complete bibliography.
            "input_paper_ids": row.get("input_paper_ids"),
        })

    papers = sorted(paper_rows.values(), key=lambda item: item["paper_id"])
    if not papers or len(papers) > 100:
        raise ValueError("O2 paper batch must contain 1–100 exact frozen IDs")
    doi_values = "|".join(item["doi"] for item in papers)
    receipts = []
    response = fetch({"filter": f"doi:{doi_values}", "select": SELECT, "per-page": 100}, raw_dir, "works_batch_001", receipts)
    matched = response.get("results", [])
    by_doi = {str(r.get("doi", "")).removeprefix("https://doi.org/").lower(): r for r in matched}

    enriched = []
    for item in papers:
        work = by_doi.get(item["doi"])
        enriched.append({**item, "openalex_match": work, "identity_status": "EXACT_DOI_MATCH" if work else "NO_EXACT_OPENALEX_MATCH"})

    # O2 requires identical explicitly supplied input sets R (at least three
    # paper IDs), not identical complete bibliographies or partial overlap.
    # Missing/empty R is not inferred from OpenAlex references.
    groups = {}
    for item in enriched:
        work = item.get("openalex_match")
        input_sets = [
            tuple(sorted(set(row.get("input_paper_ids") or [])))
            for row in item["manifest_rows"]
        ]
        seeds = input_sets[0] if input_sets and all(value == input_sets[0] for value in input_sets) else ()
        if len(seeds) >= 3 and work.get("publication_date"):
            groups.setdefault(seeds, []).append(item)
    pairs = []
    for seeds, group in groups.items():
        for i, left in enumerate(group):
            for right in group[i + 1:]:
                from datetime import date
                days = abs((date.fromisoformat(left["openalex_match"]["publication_date"]) - date.fromisoformat(right["openalex_match"]["publication_date"])).days)
                if days <= 365:
                    pairs.append({"paper_a": left["paper_id"], "paper_b": right["paper_id"], "seed_ids": list(seeds), "paper_a_date": left["openalex_match"]["publication_date"], "paper_b_date": right["openalex_match"]["publication_date"], "days_apart": days})

    citing_by_id = {}
    citing_records = {}
    # Query one resolved work at a time: the free API rejects some large OR
    # citation filters, while this also binds each response to one target.
    for item in enriched:
        work = item.get("openalex_match")
        if not work or not work.get("publication_date") or not work.get("cited_by_count"):
            continue
        target_id = work["id"].rsplit("/", 1)[-1]
        cursor = "*"
        page = 0
        target_citations = []
        while cursor:
            page += 1
            response = fetch({"filter": f"referenced_works:{target_id},from_publication_date:{work['publication_date']}", "select": CITING_SELECT, "per-page": 100, "cursor": cursor}, raw_dir, f"citing_{target_id}_{page:03d}", receipts)
            for citing in response.get("results", []):
                citing_records[citing.get("id")] = citing
                for target in citing.get("referenced_works", []):
                    if target.rsplit("/", 1)[-1] == target_id:
                        target_citations.append({"id": citing.get("id"), "doi": citing.get("doi"), "title": citing.get("title"), "publication_date": citing.get("publication_date")})
            cursor = response.get("meta", {}).get("next_cursor")
            if cursor:
                time.sleep(0.1)
        citing_by_id[target_id] = target_citations

    by_paper = {item["paper_id"]: item for item in enriched}
    outcome_pairs = []
    for pair in pairs:
        counts = {}
        evidence = {}
        for key in ("paper_a", "paper_b"):
            item = by_paper[key]
            openalex_id = item["openalex_match"]["id"].rsplit("/", 1)[-1]
            pose_date = item["openalex_match"]["publication_date"]
            citations = [c for c in citing_by_id.get(openalex_id, []) if c.get("publication_date") and c["publication_date"] > pose_date]
            counts[key] = len(citations)
            evidence[key] = citations
        label = (counts["paper_a"] > counts["paper_b"]) - (counts["paper_a"] < counts["paper_b"])
        outcome_pairs.append({**pair, "dated_later_citation_counts": counts, "label_outcome": label, "citation_evidence": evidence, "observed_at": stamp(), "label_source": "OpenAlex cited-work records; see raw response hashes"})

    paper_outcomes = []
    for item in enriched:
        work = item.get("openalex_match")
        if not work:
            continue
        openalex_id = work["id"].rsplit("/", 1)[-1]
        pose_date = work.get("publication_date")
        later = [c for c in citing_by_id.get(openalex_id, []) if pose_date and c.get("publication_date") and c["publication_date"] > pose_date]
        paper_outcomes.append({"paper_id": item["paper_id"], "openalex_id": work["id"], "publication_date": pose_date, "later_citing_work_count": len(later), "later_citing_works": later, "observed_at": stamp()})

    with (out / "paper_evidence.jsonl").open("x") as handle:
        for item in enriched:
            handle.write(json.dumps(item, sort_keys=True) + "\n")
    if pairs:
        with (out / "seed_pairs.jsonl").open("x") as handle:
            for item in pairs:
                handle.write(json.dumps(item, sort_keys=True) + "\n")
        with (out / "dated_outcomes.jsonl").open("x") as handle:
            for item in outcome_pairs:
                handle.write(json.dumps(item, sort_keys=True) + "\n")
    if citing_records:
        with (out / "citing_papers.jsonl").open("x") as handle:
            for item in citing_records.values():
                handle.write(json.dumps({"id": item.get("id"), "doi": item.get("doi"), "title": item.get("title"), "publication_date": item.get("publication_date"), "referenced_works": item.get("referenced_works")}, sort_keys=True) + "\n")
    if paper_outcomes:
        with (out / "paper_outcomes.jsonl").open("x") as handle:
            for item in paper_outcomes:
                handle.write(json.dumps(item, sort_keys=True) + "\n")

    result = {
        "schema": "M-openalex-o2-evidence-v1",
        "status": "EVIDENCE_ONLY_NOT_SCORED",
        "frozen_o2_test_list_sha256": sha(frozen_path.read_bytes()),
        "frozen_question_ids": len(frozen_qids),
        "unique_frozen_paper_ids": len(papers),
        "exact_openalex_identity_matches": sum(bool(x.get("openalex_match")) for x in enriched),
        "candidate_pairs_matching_identical_seed_and_365_day_rules": len(pairs),
        "non_tied_dated_outcome_pairs": sum(x["label_outcome"] != 0 for x in outcome_pairs),
        "citing_works_with_dates": sum(bool(x.get("publication_date")) for x in citing_records.values()),
        "papers_with_later_citing_work_dates": sum(x["later_citing_work_count"] > 0 for x in paper_outcomes),
        "raw_responses": receipts,
        "paper_evidence_sha256": sha((out / "paper_evidence.jsonl").read_bytes()),
        "paper_outcomes_sha256": sha((out / "paper_outcomes.jsonl").read_bytes()) if (out / "paper_outcomes.jsonl").exists() else None,
        "citing_papers_sha256": sha((out / "citing_papers.jsonl").read_bytes()) if (out / "citing_papers.jsonl").exists() else None,
        "seed_pairs_sha256": sha((out / "seed_pairs.jsonl").read_bytes()) if (out / "seed_pairs.jsonl").exists() else None,
        "dated_outcomes_sha256": sha((out / "dated_outcomes.jsonl").read_bytes()) if (out / "dated_outcomes.jsonl").exists() else None,
        "registered_evaluation_run": False,
        "remaining_registered_gates": [
            "M frozen configuration has no quality/outcome model predictions or frozen semantic baseline artifacts.",
            "Question identity, input-control validity, and independently verified same-topic controls remain separately mandatory under M/EVALUATION.md."
        ]
    }
    with (out / "manifest.json").open("x") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({k: result[k] for k in ("status", "frozen_question_ids", "unique_frozen_paper_ids", "exact_openalex_identity_matches", "candidate_pairs_matching_identical_seed_and_365_day_rules", "non_tied_dated_outcome_pairs", "registered_evaluation_run")}, indent=2))


if __name__ == "__main__":
    main()
