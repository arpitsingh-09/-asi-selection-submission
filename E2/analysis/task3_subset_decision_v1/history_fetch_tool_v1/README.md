# OpenReview history retrieval helper

Read-only helper for obtaining the 28 queued OpenReview note revision histories when run from a network-enabled environment. It saves raw responses and hashes to a new directory and will fail if that directory already exists. It does not make eligibility decisions.

From a network-enabled macOS Terminal:

```sh
python3 /Users/arpit/ASI_Intern_Submission/E2/analysis/task3_subset_decision_v1/history_fetch_tool_v1/fetch_openreview_history.py \
  --queue /Users/arpit/ASI_Intern_Submission/E2/analysis/task3_subset_decision_v1/first_release_review_queue.csv \
  --output /Users/arpit/ASI_Intern_Submission/E2/analysis/task3_subset_decision_v1/openreview_history_fetch_2026-11-19
```

Review `manifest.json` and each paper's `record.json`. Any row with `status: error`, missing edits, or inconsistent API data remains unresolved. Do not treat a successful fetch by itself as proof of first global publication.
