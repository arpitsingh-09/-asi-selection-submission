# E6 post-hoc analysis of saved artifacts

Date 2026-11-17. Saved artifacts only; no inference, scoring, held-out rerun, or network. Frozen protocols/results unchanged.

## Sources and reproduction

Exact counts, per-set denominators and source SHA-256 hashes: [`post_hoc_saved_metrics_2026-11-17.json`](post_hoc_saved_metrics_2026-11-17.json). Evaluation: `E6/runs/heldout_accuracy_optimized_v1/`; generations/tokens/questions: `E6/submission_v1/generations.jsonl`; frozen packets: `E6/data/error_analysis_memo_v2/packets/`; sample: `E6/data/error_analysis_memo_v2/analysis.json`. Diversity uses offline E5 `LexicalBaseline`; questions use saved `rq` fields. Full reading packet: [`reading_packet_2026-11-17.md`](reading_packet_2026-11-17.md).

Read-only saved-evaluation verification:
```sh
python3 E6/reproduce_saved_heldout_accuracy.py
```

## Saved held-out metrics

19/20 data sets, 125/140 cells; each present cell has 501 TEST assignments. Observed 62,625/70,140; 7,515 assignments in 15 cells are missing. No imputation.
Invalid 45,354/62,625 (72.42%); exact refusal-text matches 45,324/62,625 (72.37%); other invalid 30. Exact text is not independent cause verification.

| Arm | Cells | Correct/observed | Invalid/observed | Refusal/observed | Missing assignments |
|---|---:|---:|---:|---:|---:|
| D | 16/20 | 401/8016 | 6748 (84.18%) | 6747 (84.17%) | 2004 |
| QH | 19/20 | 282/9519 | 8020 (84.25%) | 8016 (84.21%) | 501 |
| QH-sel | 16/20 | 105/8016 | 7016 (87.52%) | 7014 (87.50%) | 2004 |
| QH-rand | 17/20 | 127/8517 | 7516 (88.25%) | 7515 (88.24%) | 1503 |
| HQ | 19/20 | 216/9519 | 8019 (84.24%) | 8016 (84.21%) | 501 |
| D-empty | 19/20 | 2641/9519 | 19 (0.20%) | 0 (0.00%) | 501 |
| D-shuffled | 19/20 | 770/9519 | 8016 (84.21%) | 8016 (84.21%) | 501 |

### Per-input-set coverage

Each present cell has 501 assignments; em dash means absent, not zero. Exact cell metrics are in JSON.

| Set suffix | Evaluated arms | Missing arms |
|---|---|---|
| 0000:4b44593d53e3 | D, QH, HQ, D-empty, D-shuffled | QH-sel, QH-rand |
| 0001:f4dd50eb316a | D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled | — |
| 0002:157cd742897d | QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled | D |
| 0003:2dd885278cb2 | D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled | — |
| 0004:56bffd79f9b2 | D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled | — |
| 0005:713a53afc564 | D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled | — |
| 0006:d2196c978877 | QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled | D |
| 0007:7834fee0c0ed | — | D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled |
| 0008:3ac85a345990 | D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled | — |
| 0009:f87672ddc715 | QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled | D |
| 0010:2bb41ec842c2 | D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled | — |
| 0011:a26c8c80a830 | D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled | — |
| 0012:389f9702d175 | D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled | — |
| 0013:cdb388bd85ad | D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled | — |
| 0014:c98fd1f5b397 | D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled | — |
| 0015:6949369dd111 | D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled | — |
| 0016:fe31c77d0598 | D, QH, HQ, D-empty, D-shuffled | QH-sel, QH-rand |
| 0017:1dec51397785 | D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled | — |
| 0018:b494f9ac8f33 | D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled | — |
| 0019:e7f02a62e08f | D, QH, QH-rand, HQ, D-empty, D-shuffled | QH-sel |

Missing cells: D 4/2,004 assignments; QH 1/501; QH-sel 4/2,004; QH-rand 3/1,503; HQ 1/501; D-empty 1/501; D-shuffled 1/501. All arms missing for 0007. Also QH-sel 0019; D 0009, 0002, 0006; QH-sel and QH-rand 0000 and 0016.

### Why comparisons do not establish superiority

Paired D−QH is +2.32 pp (16 complete pairs; 95% input-set bootstrap [0.00, 5.70]); QH-sel−QH-rand is −0.27 pp (16; [−0.79, 0.00]). Intervals touch zero. Invalid rates are imbalanced: D-empty 0.20% versus 84.18–88.25% for other arms. Accuracy is confounded by valid-response/serving differences; D-empty’s higher point estimate is not evidence of stronger reasoning. Missing cells, fixed test set, absent literature outcomes also limit inference. No model-superiority or cross-testbed novelty claim follows.

## Saved token usage

125 deduplicated successful workflow charges; 90,833 generated tokens. Shared preparation/probes/retries included; repeated six-hypothesis rows deduplicated. Failed/missing workflows may lack usage.

| Arm | Charges | Tokens | Mean/charge | Min–max |
|---|---:|---:|---:|---:|
| D | 16 | 3279 | 204.9 | 184–217 |
| QH | 19 | 7788 | 409.9 | 385–453 |
| QH-sel | 16 | 32725 | 2045.3 | 1941–2190 |
| QH-rand | 17 | 29092 | 1711.3 | 1586–1846 |
| HQ | 19 | 8742 | 460.1 | 424–504 |
| D-empty | 19 | 4921 | 259.0 | 259–259 |
| D-shuffled | 19 | 4286 | 225.6 | 209–239 |

## Hypothesis diversity — exploratory/post-hoc

Offline E5 function ran on 125 saved six-hypothesis groups. Lexical values are not semantic novelty/quality ratings; no inferential tests preregistered.

| Arm | Groups | Mean pairwise cosine distance | Mean Vendi |
|---|---:|---:|---:|
| D | 16 | 0.809 | 5.449 |
| D-empty | 19 | 0.792 | 5.362 |
| D-shuffled | 19 | 0.731 | 5.062 |
| HQ | 19 | 0.818 | 5.491 |
| QH | 19 | 0.742 | 4.933 |
| QH-rand | 17 | 0.787 | 5.271 |
| QH-sel | 16 | 0.802 | 5.352 |

Distinct-class/uncertainty proxies are not treated as validated labels.

## Question-type rules — exploratory/preparatory

Denominator 246 unique texts (750 generation rows; 324 without question; 270 unique set-arm-question occurrences). Counts {'analytic': 236, 'ambiguous': 9, 'other': 1}; 10 not classified analytic/constructive. No human review.

Constructive: explicit build/design/develop/create/construct/implement/optimize/improve/enable/propose/engineer/generate/deploy/formulate cue. Analytic: relationship/correlation/association/influence/effect/impact/cause/mechanism/explanation/comparison/prediction/difference/extent/why/how-do/which-factor cue. Other: viewpoint/argument/theme/pattern/kind/type without decisive cue. Both cue families or no decisive cue: ambiguous. Rules unvalidated for precision/recall.

### Twenty examples for manual verification

12 analytic, all 7 ambiguous, 1 other; no constructive examples. Provisional rules only.

| # | Rule label | Set / arm | Question |
|---:|---|---|---|
| 1 | analytic | 0005:713a53afc564 / QH-sel | What is the relationship between frustration regarding the lack of third-party debate presence and the adoption of strategies such as promoting non-voting or advocating for third-party alternatives, and how does this relate to expressed political ideology? |
| 2 | analytic | 0012:389f9702d175 / QH-sel | What is the predictive power of consistently expressing views on specific policies (e.g., tax cuts for corporations, bipartisan infrastructure bills) in conjunction with endorsements of political candidates? |
| 3 | analytic | 0017:1dec51397785 / QH | How do reactions to specific political events (e.g., Supreme Court decisions, government shutdowns, infrastructure bills) influence the expression of political ideology and subsequent voting preference? |
| 4 | analytic | 0019:e7f02a62e08f / QH-rand | In what ways does the expression of support for bipartisan infrastructure bills influence a voter’s subsequent political endorsements and criticisms of mainstream political parties? |
| 5 | analytic | 0011:a26c8c80a830 / QH-sel | What is the relationship between condemnation of government shutdowns orchestrated by Republicans and the adoption of non-voting as a form of protest, and how does this relate to expressed opinions on universal healthcare and Second Amendment rights? |
| 6 | analytic | 0001:f4dd50eb316a / QH | Does the expression of frustration regarding the lack of third-party debate presence predict a specific voting preference, and if so, what is the relationship? |
| 7 | analytic | 0009:f87672ddc715 / HQ | To what extent does explicit condemnation of Republican-led government shutdowns predict voter preference for the Democratic candidate in the 2028 election? |
| 8 | analytic | 0013:cdb388bd85ad / QH-sel | How does the combination of stances on issues like universal healthcare, gun rights, and climate change policy, alongside criticism of mainstream parties, influence an individual’s likelihood of supporting a third-party candidate versus a major party candidate? |
| 9 | analytic | 0015:6949369dd111 / QH-sel | How do expressions of frustration regarding the lack of third-party debate presence influence voter alignment, specifically concerning the adoption of conservative or libertarian ideologies? |
| 10 | analytic | 0004:56bffd79f9b2 / QH-sel | What is the relationship between criticism of Supreme Court decisions (particularly those perceived as favoring conservatives) and subsequent political endorsements or voting preferences? |
| 11 | analytic | 0011:a26c8c80a830 / HQ | What is the relationship between the expression of support for universal healthcare and the frequency of criticism directed towards Supreme Court decisions perceived as conservative? |
| 12 | analytic | 0013:cdb388bd85ad / QH | To what extent does explicit criticism of mainstream political parties correlate with a voter's likely political affiliation? |
| 13 | ambiguous | 0017:1dec51397785 / HQ | Does the advocacy for universal healthcare consistently appear alongside expressions of support for broader social justice initiatives in online communication? |
| 14 | ambiguous | 0015:6949369dd111 / HQ | Does the expression of frustration over the absence of third-party debate presence serve as a reliable indicator of conservative values? |
| 15 | ambiguous | 0000:4b44593d53e3 / HQ | What specific arguments and reasoning do individuals employ when criticizing mainstream political parties and advocating for universal healthcare? |
| 16 | ambiguous | 0005:713a53afc564 / HQ | Under what circumstances and with what rationale do individuals endorse Democratic candidates while simultaneously defending Second Amendment rights? |
| 17 | ambiguous | 0006:d2196c978877 / HQ | Does the presence of language supporting gun rights reliably indicate an alignment with the defense of Second Amendment rights in online communication? |
| 18 | ambiguous | 0014:c98fd1f5b397 / HQ | What are the common ideological connections between advocating for libertarian policies and opposing corporate tax cuts among politically active individuals? |
| 19 | ambiguous | 0009:f87672ddc715 / HQ | Does the expression of approval for Biden's climate change policy reliably indicate a conservative voting preference in the 2028 election? |
| 20 | other | 0000:4b44593d53e3 / HQ | What are the common viewpoints and arguments used by individuals who express opinions on immigration reform and universal healthcare? |

## Frozen error-analysis packet

Frozen sample: 10 data + 10 literature cases. Seven data cases have all-arm generation/evaluation; two partial (0019 missing QH-sel, 0009 missing D); 0007 has none; all literature cases lack arm generations/evaluations. Human review remains 0/20 cases and 0 arm cells. The [packet](reading_packet_2026-11-17.md) includes source inputs, available outputs/questions/hypotheses and missing-arm markers; it is not itself human review.

## Limitations / incomplete requirements

- No missing values, literature outputs, human judgments, or causes inferred; refusal counts are exact-text matches only.
- Diversity/question labels are exploratory and unvalidated. Twenty examples and frozen cases still need manual review.
- Literature-arm evaluation, full held-out coverage, validated novelty evidence, HDR, and independent human error review remain incomplete. Protocol/status unchanged.
- Manual work: verify question examples and document decisions; conduct and record independent case review.
