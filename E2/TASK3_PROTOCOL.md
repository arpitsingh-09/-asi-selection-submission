# E2 Task 3 — Human Check and Quality Baseline Protocol

## 1. Protocol status

Status: Retrospective protocol clarification, documented before Task 3
embedding inference and test scoring.

The ICLR 2026 benchmark records and labels were inspected before this
document was written. This document must not be described as a prospective
preregistration.

Purpose: Compare the discrimination performance of the E2 novelty measures
against a quality-only baseline on the ICLR 2026 human-labelled benchmark.

## 2. Evaluation benchmark

Dataset: allenai/novelty-judge-bench
Configuration: human-only_pointwise
Split: test
Expected sample size: 299
Positive labels: 154
Negative labels: 145

The dataset's operational label construction and use of AI-assisted
processing must be disclosed in the final report. In particular, the
benchmark's selection criteria use reviewer ratings and contribution
assessments. Consequently, the quality baseline is not independent of the
benchmark's label construction.

The benchmark records do not contain item-level publication timestamps.
Temporal separation is therefore established at the cohort level:
historical ICLR 2022–2025 training/validation data versus the ICLR 2026
test cohort. Do not claim item-level timestamp verification for the
benchmark.

## 3. Historical data

Source: OpenReview ICLR paper and review archive for 2022, 2023, 2024,
and 2025.

Eligible historical papers must:
- Have a non-empty abstract.
- Have at least two official reviews.
- Have valid numeric official-review ratings.

Verified eligible counts:
- ICLR 2022: 2,617
- ICLR 2023: 3,792
- ICLR 2024: 7,261
- ICLR 2025: 11,520
- Total before overlap exclusions: 25,190

All four years use the numeric rating anchors 1, 3, 5, 6, 8, and 10.
The original rating values will be retained; no conversion to acceptance
probabilities will be applied.

For each paper, the regression target is the arithmetic mean of its
official-review numeric ratings.

## 4. Historical overlap exclusions

Four historical records were identified as strong title/topic overlap
candidates with benchmark records:
- Hot PATE (ICLR 2024)
- Conjuring Semantic Similarity (ICLR 2025)
- Counterfactual Techniques for Enhancing Customer Retention (ICLR 2025)
- Hot PATE (ICLR 2025)

Exclude these four historical records from all ridge training and
validation folds. The matches are conservative overlap exclusions, not
confirmed duplicate-paper findings.

The audit found no exact benchmark-to-history forum-ID matches. The title
audit does not establish that every possible semantic near-duplicate has
been found; residual overlap risk must be disclosed.

## 5. Quality-only baseline

Task: Predict the mean official-review rating from a frozen abstract
embedding, without using benchmark labels or benchmark rating/contribution
fields as model inputs.

Embedding:
- Encoder: allenai/specter2_base
- Adapter: allenai/specter2, proximity adapter
- Representation: CLS token from the final hidden state
- Input: abstract only; do not include title, reviews, or benchmark labels
- Maximum token length: 512
- No encoder fine-tuning
- Do not reuse E2 title-plus-abstract novelty embeddings as baseline inputs
- Do not use or alter the existing E2 embedding cache for this baseline

Ridge regression:
- Target: mean numeric official-review rating per historical paper
- Standardise embedding features using training-fold statistics only
- Fit the ridge model using the standardised training features
- Fit all preprocessing only on the relevant training fold
- Do not use test labels, test ratings, or test contribution values for
  model fitting or hyperparameter selection

## 6. Chronological hyperparameter selection

Use expanding-window validation:

Fold 1:
- Train: ICLR 2022
- Validate: ICLR 2023

Fold 2:
- Train: ICLR 2022–2023
- Validate: ICLR 2024

Fold 3:
- Train: ICLR 2022–2024
- Validate: ICLR 2025

Apply the four overlap exclusions to both training and validation portions.

Predeclared ridge alpha grid:
0.0001, 0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000

Select alpha by the lowest pooled mean squared error across all available
out-of-time validation predictions from the three folds. Each validation
paper contributes one prediction. Do not select alpha using the ICLR 2026
test set.

After selecting alpha, refit the standardisation and ridge model on all
eligible ICLR 2022–2025 historical papers, excluding the four overlap
candidates. Use this final model to generate the ICLR 2026 quality-baseline
scores.

## 7. Novelty measures and evaluation

Evaluate the four E2 novelty measures:
- Y
- N
- yours
- density (RND)

Use the existing E2 implementation and its documented score orientation.
Before computing AUROC, verify whether higher values indicate greater
novelty for each measure. If a measure has the opposite orientation,
reverse its sign for AUROC and document the transformation. Do not tune
measure weights or thresholds on the test set.

Evaluate the quality baseline using its predicted mean review rating as
the score for the positive novelty class. Do not fit a classifier on the
benchmark.

Primary metric: AUROC.

Report:
- AUROC for each of the four novelty measures.
- AUROC for the quality-only baseline.
- Each novelty measure's AUROC minus the quality-baseline AUROC.

Uncertainty:
- Use 10,000 paired, class-stratified bootstrap replicates.
- Within each replicate, resample positive and negative test examples
  separately, preserving their original class counts.
- Use the same resampled examples for every measure and the baseline.
- Calculate AUROC and paired AUROC differences within each replicate.
- Report percentile 95% confidence intervals.
- Record the random seed used.

Do not interpret a confidence interval crossing zero as proof of equivalence.

## 8. Reporting limitations

The final report must disclose:
- The benchmark labels and records were inspected before this protocol
  clarification; this is not prospective preregistration.
- Benchmark selection is correlated with reviewer ratings and contribution
  assessments, which limits the independence of the quality-baseline
  comparison.
- The benchmark has no item-level timestamps in the inspected schema;
  temporal separation is cohort-level.
- The four overlap candidates were conservatively excluded, but the title
  audit cannot guarantee detection of all semantic near-duplicates.
- The benchmark's AI-assisted processing and operational label definition.
- Any missing records, failed embeddings, deviations, or implementation
  differences discovered during execution.

## 9. Execution boundary

This document records the analysis protocol only. It does not authorise
embedding inference, cache writes, model fitting, test scoring, or changes
to existing E2 files. Those operations require a separate explicit review
and approval.
