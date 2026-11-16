# E6 research-agent memo — provisional submission snapshot

**Decision: pending verified outcome evaluation.** Whether questions-first decomposition helps, selection beats random choice, or controls degrade cannot be concluded from generation alone.

| Arm | Data accuracy | Literature hypothesis similarity | Data generated-token cost |
|---|---|---|---|
| D | pending | pending | 206 [202, 209] (n=19) |
| QH | pending | pending | 410 [402, 419] (n=19) |
| QH-sel | pending | pending | 2.05e+03 [2.02e+03, 2.08e+03] (n=19) |
| QH-rand | pending | pending | 1.71e+03 [1.68e+03, 1.74e+03] (n=19) |
| HQ | pending | pending | 460 [451, 469] (n=19) |
| D-empty | pending | pending | 259 [259, 259] (n=19) |
| D-shuffled | pending | pending | 226 [222, 229] (n=19) |

Entries are arithmetic means with descriptive 95% bootstrap intervals and available input-set counts; unavailable outcomes are pending. Costs include charged failed-arm work and shared preparation under the frozen per-arm accounting; do not sum shared costs across arms.

**Conditions and controls.** Paired differences (left minus right):

| Contrast | Data accuracy | Literature hypothesis similarity |
|---|---|---|
| QH − D | pending | pending |
| QH-sel − QH-rand | pending | pending |
| QH − D-shuffled | pending | pending |
| D − D-empty | pending | pending |

**Error analysis.** 0/20 fixed cases have attributed end-to-end reviews. Saved examples and failure records are provided for all seven arms; semantic error judgments remain pending. No most-common failure is claimed without completed coding.

**Scope and limits.** Testbeds remain separate. Failed generation and unresolved TRAIN set 0007 are missing, not zero. Literature reference extraction is not seven-arm experimental output. HDR, historical-question rates, diversity and question types remain pending where genuine scoring is unavailable.

**Method and cost.** One frozen model/decoding configuration, 8192 generated-token cap per set/arm, six hypotheses. Bootstrap: 10,000 input-set resamples, seed 2026, SHA256-seeded MT19937 streams, linear-percentile intervals; complete pairs for contrasts. Intervals are unadjusted and descriptive. See analysis.json and error review packets for provenance and denominators.

**Submission status.** Literature extraction: 100/100 verified, with 40 independent source reviews still pending. Evaluator pilot: 16/16 responses verified, 0/10 independent judgments. HDR: 0/125 scored. Held-out accuracy is running separately; its partial outputs are excluded. Literature seven-arm experiments and 20-case end-to-end human coding are incomplete. These gaps prevent a defensible benefit or deployment recommendation.
