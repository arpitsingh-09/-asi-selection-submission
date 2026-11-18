# ASI Selection Round: Submission

## Current requested scope (2026-11-18)

This package is consolidated in `/Users/arpit/ASI_Intern_Submission` at the
candidate’s request and contains T1–T5, E1, E2, E5, E6, and Main Problem M.
The scope amendment is retrospective and candidly records that the original
root preregistration selected E4 rather than E5. The E5 work has a separate
scoped preregistration and controlled-baseline run; the selection mismatch is
not hidden or represented as a timely original amendment.

The assignment PDF and extracted text are included at the repository root.
See each task’s `COMPLETION_REPORT.md`/`FINAL_REPORT.md`, where present, for
what is complete, partial, blocked, or exploratory. This is an evidence-led
working submission, not a claim that every rubric item is complete.

## Compute environment

The exact compute tier used for the original evaluation is not established by the available project records. The evaluation scripts select Apple MPS, CUDA, or CPU when available. Device selection does not establish the machine memory tier.

## Reproduce

Run commands from the repository root with the required Python dependencies installed.

1. Corrected development evaluation:
   python E1/eval_contrast_v2.py
   Reads E1/contrast.jsonl and writes corrected results under E1/results_v2/.

2. Corrected SPECTER2 evaluation:
   python E1/evaluate_specter2_corrected.py
   Uses the separate corrected SPECTER2 evaluation implementation and writes outputs under E1/results_specter2_corrected/.

3. Earlier evaluation pipeline:
   python E1/eval_contrast.py
   Writes outputs under E1/results/. Treat these as earlier results, not replacements for the corrected results.

4. Project integrity checks:
   python E1/verify_e1.py

## Dataset boundary

The evaluation scripts use E1/contrast.jsonl, the development dataset. Keep the frozen dataset unchanged. Do not use the held-out test file for development evaluation.


## Main Problem (`main/`)

The assignment-format report is [`main/REPORT.md`](main/REPORT.md). The package contains copied code, configs, and result JSON under `main/`; canonical runnable code and complete supporting evidence remain in `M/`. No original registered evaluation produced scores: the submitted ledger reports 0/9 complete. Do not interpret blocked receipts or software tests as experimental results.

Run these commands from the repository root. The status-ledger command writes into `M/results/stage5/`, so use a fresh checkout or backup when rebuilding it. It reads saved evidence and does not run inference, scoring, or training.

```sh
# Rebuild the registered blocked-status ledger and its Markdown summary.
OPENBLAS_NUM_THREADS=1 python3 -B M/results/stage5/build_report.py

# Run Main Problem software tests only; fixtures are not experimental evidence.
PYTHONPYCACHEPREFIX=/tmp/asi-m-pycache OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python3 -B -m unittest discover -s M/tests -p 'test_*.py'

# Verify supplementary A1 statistics in memory against saved scoring rows.
python3 -B -c 'import json,pathlib; from M.a1_replication.analyze_a1_results import analyze; p=pathlib.Path("M/a1_replication"); r=json.loads((p/"A1_SCORING_RESULTS_V1.json").read_text()); s=json.loads((p/"A1_STATISTICAL_RESULTS_V1.json").read_text()); assert {k:v for k,v in s.items() if k!="provenance"} == analyze(r)'

# Recompute the descriptive V2 reviewer-agreement comparison in memory.
python3 -B -c 'from M.prospective_grounding.exploratory_evidence.compare_review_responses import validate_and_compare; r, _, _ = validate_and_compare(); a=r["rating_agreement"]; b=r["association_agreement"]; assert (a["exact_agreement_n"],b["joint_decision_agreement_n"])==(17,6) and abs(a["cohen_kappa_unweighted"]-0.912)<0.0005 and abs(a["cohen_kappa_linear_weighted"]-0.927)<0.0005'
```

The supplementary S1 result is retained as [`main/results/S1_exploratory_results.json`](main/results/S1_exploratory_results.json) and is explicitly exposed, label-relative evidence. Its runner requires separate authorization and performs scoring; this packaging task did not rerun it. The grounding generation records are not a completed grounding evaluation. The compute tier for Main Problem model runs is not established by the saved records.


### Packaging and provenance notes

- `main/REPORT.md` renders to **7 pages** in the local Letter-size print check (RDoc Markdown conversion to text followed by the system PDF text printer; 612 × 792 pt), within the eight-page maximum. The assignment does not fix font or margins, so organizer-side pagination may differ.
- The root preregistration records E1/E2/E4, while tracked experiment deliverables include E1/E2/E5 and no E4 folder. E5 has a dated experiment preregistration, but no dated amendment changing the selected experiment set was found. Treat this selection discrepancy as unresolved; see the [dated retrospective clarification](PROVENANCE/experiment-selection-clarification-2026-11-16.md).
- Theory answer files for T1–T5 are present under `theory/`; `theory/T1.md` includes the T1 answer-sheet entries.
- Original Main Problem Git commit objects and the preregistration tree binding are preserved in `PROVENANCE/`; verify them with `python3 -B PROVENANCE/verify_original_git_history.py`. The commit timestamps are preserved as authored/committed fields, not independently trusted wall-clock attestations.
