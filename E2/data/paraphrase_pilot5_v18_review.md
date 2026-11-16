# E2 Paraphrase Pilot v18 — Manual Review Report

## Scope

- Dataset reviewed: `E2/data/paraphrase_pilot5_v18.jsonl`
- Records examined: 5
- Review basis: comparison of candidate titles and abstracts against their source titles and abstracts, with relevant earlier review notes.
- Review level: abstract-level semantic preservation.
- This report does not independently verify every claim against the full source papers.
- No scoring was run.
- The decisions below are proposed manual-review recommendations; JSONL review statuses remain unchanged pending explicit approval.

## Proposed paper-level decisions

### 1. 2012.14359v1 — ACCEPT recommended

The candidate preserves the general neurosymbolic method for online visual sensemaking, answer set programming (ASP), formal specification and implementation, modular hybrid-architecture framing, real-time perception and control, all three named benchmarks, the human-centred use case, commonsense interpolation, and the broader scope of diverse cognitive interaction settings.

The candidate title retains commonsense visual sensemaking, autonomous driving, and neurosymbolic online abduction.

### 2. 2012.14371v3 — ACCEPT recommended

The candidate preserves the Sequence Compatibility Kernel (SCK), Dynamics Compatibility Kernel (DCK), generalized SCK(+), subsequence-based local and global correlations, multimodal inputs, linearized descriptors, the three evaluation settings, and the higher-order feature-occurrence argument involving Eigenvalue Power Normalization (EPN).

The candidate retains the order-r tensor, Z*-dimensional features, binom(Z*,r) detectors, r-dimensional subspaces, and the claim that at least one higher-order occurrence is projected into a subspace. The theorem was checked against the paper text during the earlier review process. This report does not constitute a new independent mathematical proof.

### 3. 2012.13915v2 — ACCEPT recommended

The candidate preserves syntactic dependency of interest (SDOI), the SDOI-SAN component, syntax-guided self-attention, the combination with the original Transformer self-attention network in a dual-context architecture, application to typical Transformer encoders, and all three evaluation task categories: natural language inference, machine reading comprehension, and neural machine translation.

### 4. 2012.14271v3 — ACCEPT recommended, with priority caveat

The candidate preserves all four contributions: a multimodal context-aware translation framework, automatic parallel-corpus construction without manual labeling, a manga-translation benchmark, and a comprehensive fully automated translation system.

It retains the specific example of speaker gender and the claims that the framework is the first to incorporate context obtained from manga images and the system is the first comprehensive system for fully automated manga translation.

These priority claims are represented as claims made by the authors; this review does not independently establish historical priority.

### 5. 2012.14961v1 — ACCEPT recommended

The candidate preserves deep one-class anomaly detection, the potential association between learned representations and social bias, the goal of fair and correct predictions, Deep Fair SVDD, adversarial training to reduce association between sensitive attributes and learned representations, the distinction from regularizer- or constraint-based approaches, two fairness measures, reported fairness and anomaly-performance findings, and parameter, feature-visualization, and run-time analyses.

## Supplementary C8 lexical-overlap diagnostic

A reconstructed diagnostic was run on the five candidate abstracts. It lowercases alphabetic tokens, removes a simple stopword list, and measures the longest contiguous shared sequence of remaining tokens.

| Paper ID | Longest shared run |
|---|---:|
| 2012.14359v1 | 7 |
| 2012.14371v3 | 7 |
| 2012.13915v2 | 6 |
| 2012.14271v3 | 7 |
| 2012.14961v1 | 7 |

No candidate reached the reconstructed threshold of eight shared content words.

**Limitation:** This is a supplementary diagnostic, not the original C8 implementation and not evidence of semantic equivalence. Technical terminology, theorem wording, named components, and specific reported analyses can legitimately overlap.

## Authorization and integrity safeguards

- All five recommendations are pending explicit approval.
- The v18 JSONL records remain `manual_validation_status = not_reviewed`.
- The v18 JSONL records remain `scoring_authorized = false`.
- No scoring was run or authorized by this report.
- `scoring_results.jsonl` was not modified.
- Earlier v2–v17 files and review artifacts were not modified.
- The reconstructed C8 diagnostic does not replace semantic review.

## Recommended next action

Review and approve or revise each paper-level recommendation before recording final manual-validation decisions in the dataset. Keep scoring disabled until the project protocol and explicit authorization permit it.
