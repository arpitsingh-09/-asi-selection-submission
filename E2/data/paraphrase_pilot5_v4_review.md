# E2 Paraphrase Pilot — V4 Semantic Review

## Scope
- Dataset reviewed: `E2/data/paraphrase_pilot5_v4.jsonl`
- Records reviewed: 5
- Review basis: source titles and abstracts supplied for manual comparison
- This is an abstract-level semantic review, not independent verification against full papers.
- No scoring is authorized by this report.

## Paper-level decisions

| Paper ID | Decision | Findings / required action |
|---|---|---|
| 2012.14359v1 | PASS_WITH_MINOR_REVISION | Restore the source's explicit claims that the method is fully implemented and the framework is generally usable in hybrid architectures. |
| 2012.14371v3 | PASS_WITH_MINOR_REVISION | Refine the description of EPN to better preserve the source's claim about spectral detection of higher-order occurrences. The mathematical theorem has not been independently checked against the full paper. |
| 2012.13915v2 | PASS | The motivation, SDOI-SAN component, dual-context architecture, Transformer encoders, and three evaluation task categories are preserved. |
| 2012.14271v3 | PASS_WITH_MINOR_REVISION | Restore the source's explicit claim that some speech-bubble text cannot be translated adequately without contextual information. The priority claims have not been independently verified. |
| 2012.14961v1 | PASS_WITH_MINOR_REVISION | Make explicit that Deep Fair SVDD is trained with an adversarial network to reduce the association between sensitive attributes and learned representations. |

## Required revisions

### 1. Paper 2012.14359v1
Suggested wording:
"It formalizes and fully implements a general neurosymbolic method for online visual sensemaking using answer set programming (ASP). The method combines established visual-computing techniques within a modular framework designed for general use in hybrid architectures supporting real-time perception and control."

### 2. Paper 2012.14371v3
Suggested wording:
"The work uses higher-order tensors and Eigenvalue Power Normalization (EPN) to characterize spectral detection of higher-order occurrences, distinguishing fine-grained feature relationships from simple feature counts."

This is a wording recommendation only; verify the technical theorem against the full paper before treating the candidate as fully validated.

### 3. Paper 2012.14271v3
Suggested wording:
"The framework enables translation of speech-bubble text that cannot be translated adequately without contextual information, such as text in other speech bubbles or information about the speaker's gender."

### 4. Paper 2012.14961v1
Suggested wording:
"The proposed Deep Fair SVDD architecture is trained with an adversarial network to reduce the association between sensitive attributes and learned representations, rather than incorporating fairness only through a regularizer or constraint."

## Status
- Paper 2012.13915v2: abstract-level PASS.
- Four other candidates: minor revisions recommended.
- V4 dataset: remains `not_reviewed`.
- Scoring: NOT AUTHORIZED.
- Do not modify or append to the existing main experiment results as part of this pilot review.
