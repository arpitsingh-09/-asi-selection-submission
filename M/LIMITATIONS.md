# Main Problem limitations and remaining evidence requirements

This document records limitations of the current implementation and evidence.
It does not amend the frozen protocol or authorize a registered run.

## Evidence and eligibility gaps

* **No registered outcomes:** all nine frozen evaluation cohorts remain
  ineligible, so there are no registered predictions, metrics, confidence
  intervals, or conclusions.
* **Supplementary A1 scope:** a separate exposed partial replication has a
  negative preregistered threshold result from only two focal-paper clusters.
  Its same-topic decoy condition was unavailable. It does not complete or
  replace original A1 and is too small for confirmatory inference; details are
  in [`FINAL_REPORT.md`](FINAL_REPORT.md).
* **Supplementary S1 scope:** a 60-question exploratory comparison used exposed
  E1 data and unverified author-intended labels. Its near-miss difference
  cleared the 0.02 margin (0.15; 95% CI [0.0667, 0.25]), but the
  minimal-paraphrase difference did not (0.00; 95% CI [0.00, 0.00]); therefore
  the overall two-category criterion failed. It does not complete original
  S1, which remains incomplete. Original A1 also remains incomplete: 80/80
  frozen candidates are ineligible. See [`FINAL_REPORT.md`](FINAL_REPORT.md).
* **Quality labels and trained Q heads:** the two targets are peer-review quality
  and later community use. Existing matching/review retrieval has not yielded
  exact-cohort, question-linked labels with a verified outcome definition,
  original source provenance, and an observation date inside the proper temporal
  split. In particular, 570 cached review values do not map to the frozen
  train/validation questions with qualifying dates. The later-community-use
  target also lacks qualifying dated outcome records. Neither factor has a
  fitted model. The software minimum for fitting is not a claim of adequate
  statistical power.
* **I1 independent judgments:** two independent reviewers still need to assess
  each candidate's question/input relationship, paraphrase equivalence, near-miss
  distinction, same-topic decoy validity, supporting evidence and review date.
  Empty templates are not annotations. The generated candidates are not
  established as original research questions with verified supplied inputs.
* **O2 supplied input sets:** the frozen O2 records have no original `R` input
  IDs. OpenAlex reference lists describe bibliographies and cannot recover what
  was explicitly supplied to a question. The cached 41 shared-reference pairs
  therefore do not meet O2's identical-seed-set condition; eligible pair count
  is zero. O2 remains unscored.
* **Other tests:** see the per-test blockers in [`RESULTS.md`](RESULTS.md) and
  the frozen prediction requirements in [`EVALUATION.md`](EVALUATION.md). These
  include missing independent alignment/near-miss judgments, dated expert or
  reviewer outcomes, complete source/question links, independently checked
  controls, quality-model artifacts, and/or task-specific baselines and model
  cutoffs. Existing data from E1/E2/E5 is not automatically eligible M evidence.

## Model and measurement limits

The default shared representation uses deterministic lexical hashing and a
rule-based facet extractor. It is not a trained semantic encoder and does not
establish semantic equivalence, entailment, novelty quality, or research quality.
The I and N readouts are proxies. G cannot infer that an answer is supported just
from topical similarity. Q values remain unavailable unless the two separately
trained heads load successfully. No default or fallback Q prediction is supplied.

Semantic B-Q/B-ABS baselines need exact compatible frozen embedding artifacts.
Missing semantic vectors are reported unavailable, not relabeled lexical scores.
The implemented TF-IDF and length baselines do not make a cohort or annotation
eligible. The descriptive diversity statistics in the development run do not
establish reliability, validity, or treatment sensitivity.

## Temporal and provenance limits

The frozen split rules are TRAIN through 2023, VALIDATION during 2024, a first-
half 2025 gap, and TEST from 2025-07-01 onward. Paper publication date alone
does not prove when a question was posed, when a text version became public, or
when a label/outcome became observable. Venue years and later citations cannot
be backdated as observation evidence. Data-file hashes prove byte integrity,
not source authenticity, human independence, or label correctness.

The available local fixtures and generated development records are not
substitutes for the frozen real cohorts. Synthetic results are useful only for
software testing. No frozen TEST records were scored in this work, and no TEST
labels were used for fitting.

## Reproduction and submission boundary

The 92 passing CPU tests cover code paths and fixture behavior, not the
scientific validity of the hypotheses. Reproducing them requires the same local
repository inputs and NumPy-capable Python environment. Existing raw evidence
and generated result files are preserved in the workspace; the development
result JSON files are each about 14 MB and are not needed to validate the code.
Review their source/license and packaging requirements before external
distribution. Do not edit `PREREG.md` or `frozen/` to remove a blocker. If a new
cohort/version is permitted, document and commit its prospective rules before
looking at evaluation outcomes.
