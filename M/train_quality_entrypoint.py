"""Eligibility-gated entry point for the registered two-factor quality fit."""
import argparse
import json
from pathlib import Path

from .quality import FACTORS
from .schema import LeakageError, date
from .training import rows, run, validate_record


def _inspect_split(records, split):
    """Validate provenance and count labels usable by the publication-time fit."""
    counts = {factor: 0 for factor in FACTORS}
    for record in records:
        if record.get("split") != split:
            raise LeakageError(f"{split} manifest contains a record from another split")
        validate_record(record)
        # The frozen training pipeline fits Phi at publication time. A later
        # version of the question cannot be used as if it existed at posing.
        if date(record["available_at"]) != date(record["published"]):
            continue
        for factor in FACTORS:
            label = (record.get("labels") or {}).get(factor)
            if label is None:
                continue
            if label.get("verified") is not True:
                raise ValueError(f"{split} {factor} label is not independently verified")
            if not label.get("source") or not label.get("evidence_sha256"):
                raise ValueError(f"{split} {factor} label lacks source evidence")
            counts[factor] += 1
    return counts


def _write_status(out, result):
    output = Path(out)
    output.mkdir(parents=True, exist_ok=False)
    with (output / "training_status.json").open("x") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")


def train_if_eligible(train_path, validation_path, eligibility_report, out):
    report = json.loads(Path(eligibility_report).read_text())
    train = rows(train_path)
    validation = rows(validation_path)
    counts = {
        "train": _inspect_split(train, "train"),
        "validation": _inspect_split(validation, "validation"),
    }
    report_counts = report.get("eligible_by_factor_split")
    if report_counts is not None:
        mismatches = [
            f"{split}.{factor}: report={report_counts.get(split, {}).get(factor, 0)}, "
            f"records={counts[split][factor]}"
            for split in counts
            for factor in FACTORS
            if report_counts.get(split, {}).get(factor, 0) != counts[split][factor]
        ]
    else:
        mismatches = []

    reported_train = report.get("eligible_train", 0)
    reported_validation = report.get("eligible_validation", 0)
    actual_train = sum(value > 0 for value in counts["train"].values())
    actual_validation = sum(value > 0 for value in counts["validation"].values())
    reasons = []
    if mismatches:
        reasons.append("eligibility report does not match verified manifest labels")
    if reported_train <= 0 or reported_validation <= 0:
        reasons.append("eligibility report has no eligible labels in both partitions")
    if actual_train == 0 or actual_validation == 0:
        reasons.append("no verified dated labels in both train and validation records")
    for factor in FACTORS:
        if counts["train"][factor] < 2:
            reasons.append(f"{factor}: need at least 2 publication-time TRAIN labels")
        if counts["validation"][factor] < 1:
            reasons.append(f"{factor}: need at least 1 publication-time VALIDATION label")

    if reasons:
        result = {
            "status": "BLOCKED_INELIGIBLE_LABELS",
            "heldout_evaluated": False,
            "reported_eligible_train": reported_train,
            "reported_eligible_validation": reported_validation,
            "verified_publication_time_labels": counts,
            "reason": "; ".join(dict.fromkeys(reasons)),
        }
        _write_status(out, result)
        return result

    result = run(train_path, validation_path, out)
    fitted = all(
        result.get("heads", {}).get(factor, {}).get("status") == "fitted"
        for factor in FACTORS
    )
    result["status"] = "TRAINED" if fitted else "BLOCKED_INELIGIBLE_LABELS"
    result["verified_publication_time_labels"] = counts
    with (Path(out) / "training_status.json").open("x") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", required=True)
    parser.add_argument("--validation", required=True)
    parser.add_argument("--eligibility-report", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    print(json.dumps(train_if_eligible(args.train, args.validation, args.eligibility_report, args.out), indent=2))
