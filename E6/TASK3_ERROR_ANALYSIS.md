# E6 Task 3 — frozen 20-case error analysis

## Scope and interpretation

This report follows the unchanged sample in
[`data/error_analysis_memo_v2/analysis.json`](data/error_analysis_memo_v2/analysis.json):
10 HypoBench `TRAIN-SET` cases and 10 literature cases. Evidence links below
point to existing packets, generation records, and saved evaluation JSONs.
No generation, inference, scoring, review form completion, or sample change
was performed.

“Automatic evidence review” means checking saved records, schemas, and reported
counts. It does not mean semantic correctness was independently judged. The
packet status records 0/20 input sets and 0 arm cells reviewed by humans. No
independent human judgments are available. The reported held-out outcome for a
data case is the saved arm evaluation over the common 501-item HypoBench TEST
split associated with that TRAIN-set generation; it is not an evaluation of
the sampled TRAIN-set texts. Per-case invalid outputs are observable, but the
held-out records alone do not establish the cause of every invalid response.

## Case-by-case evidence

| Frozen case | Input/source evidence | Saved arm outputs | Saved evaluation outcome | Observable example / failure classification |
|---|---|---|---|---|
| Data 0019 — `hypobench-synthetic-election-level2:TRAIN-SET:0019:e7f02a62e08f` | 20 source observations in [packet](data/error_analysis_memo_v2/packets/data_3938323d60bba3b5.json). | [generation rows 715–750](submission_v1/generations.jsonl#L715-L750): D, QH, QH-rand, HQ, D-empty, D-shuffled; QH-sel missing (failed generation cell). | [saved evaluation](runs/heldout_accuracy_optimized_v1/3938323d60bba3b5/3938323d60bba3b5_5ea2934b0aa6189e_evaluation.json): six available arms; each non-D-empty arm has 0/501 correct and 501 invalid, while D-empty has 139/501 correct and 1 invalid. QH-sel unavailable. | D H1: “Tweets criticizing the Supreme Court favoring conservatives correlate with increased support for third-party candidates.” The output exists, but no human semantic judgment validates the claim. Observable failure: invalid held-out predictions in all available non-D-empty arms. |
| Data 0017 — `hypobench-synthetic-election-level2:TRAIN-SET:0017:1dec51397785` | 20 source observations in [packet](data/error_analysis_memo_v2/packets/data_8f9b6e0d6d660a93.json). | [generation rows 631–672](submission_v1/generations.jsonl#L631-L672): all seven arms, six hypotheses per arm. | [saved evaluation](runs/heldout_accuracy_optimized_v1/8f9b6e0d6d660a93/8f9b6e0d6d660a93_49e5d4e6ea0d054f_evaluation.json): every non-D-empty arm 0/501 correct, 501 invalid; D-empty 139/501, 1 invalid. | D H1: “Individuals expressing frustration with the two-party system are more likely to support third-party candidates.” This is a saved hypothesis, not an independently assessed error. Observable failure: invalid held-out predictions across six non-empty arms. |
| Data 0011 — `hypobench-synthetic-election-level2:TRAIN-SET:0011:a26c8c80a830` | 20 source observations in [packet](data/error_analysis_memo_v2/packets/data_133dd7a854d9398b.json). | [generation rows 391–432](submission_v1/generations.jsonl#L391-L432): all seven arms, six hypotheses per arm. | [saved evaluation](runs/heldout_accuracy_optimized_v1/133dd7a854d9398b/133dd7a854d9398b_3f821456dbfd9aa4_evaluation.json): every non-D-empty arm 0/501 correct, 501 invalid; D-empty 139/501, 1 invalid. | D H2 asserts debate-presence frustration is more frequent among likely Republican voters. In the saved 20 observations, four mention debate presence, split 2 Republican-labelled and 2 Democratic-labelled; that count does not support the asserted direction. This is an AI-assisted inspection of recorded labels, not independent human review. |
| Data 0013 — `hypobench-synthetic-election-level2:TRAIN-SET:0013:cdb388bd85ad` | 20 source observations in [packet](data/error_analysis_memo_v2/packets/data_7b17b034d8a45586.json). | [generation rows 475–516](submission_v1/generations.jsonl#L475-L516): all seven arms, six hypotheses per arm. | [saved evaluation](runs/heldout_accuracy_optimized_v1/7b17b034d8a45586/7b17b034d8a45586_ee3eac24c2d621f5_evaluation.json): every non-D-empty arm 0/501 correct, 501 invalid; D-empty 139/501, 1 invalid. | D H1 links criticism of conservative Supreme Court decisions with support for non-voting. The saved text is evidence of the generated claim only; semantic support was not human-coded. Observable failure: invalid held-out predictions across non-empty arms. |
| Data 0015 — `hypobench-synthetic-election-level2:TRAIN-SET:0015:6949369dd111` | 20 source observations in [packet](data/error_analysis_memo_v2/packets/data_15882043d59f01a1.json). | [generation rows 559–600](submission_v1/generations.jsonl#L559-L600): all seven arms, six hypotheses per arm. | [saved evaluation](runs/heldout_accuracy_optimized_v1/15882043d59f01a1/15882043d59f01a1_8610e09e557629e1_evaluation.json): every non-D-empty arm 0/501 correct, 501 invalid; D-empty 139/501, 1 invalid. | D H1 links non-voting protest with Republican identification. This directional claim is recorded; independent semantic validation is unavailable. Observable failure: invalid held-out predictions across non-empty arms. |
| Data 0014 — `hypobench-synthetic-election-level2:TRAIN-SET:0014:c98fd1f5b397` | 20 source observations in [packet](data/error_analysis_memo_v2/packets/data_958a03500045bc18.json). | [generation rows 517–558](submission_v1/generations.jsonl#L517-L558): all seven arms, six hypotheses per arm. | [saved evaluation](runs/heldout_accuracy_optimized_v1/958a03500045bc18/958a03500045bc18_2c98c89e675dfd6d_evaluation.json): every non-D-empty arm 0/501 correct, 501 invalid; D-empty 139/501, 1 invalid. | D H1 links frustration with third-party debate presence to Republican preference. No independent semantic coding is recorded. Observable failure: invalid held-out predictions across non-empty arms. |
| Data 0007 — `hypobench-synthetic-election-level2:TRAIN-SET:0007:7834fee0c0ed` | 20 source observations in [packet](data/error_analysis_memo_v2/packets/data_918152f5db2b6a0b.json). | No saved generation output; all seven cells are marked unresolved in the existing run records. | No saved per-set evaluation JSON. | No model output exists to classify. Failure category is unavailable evidence, not a model error. Do not retry this frozen cell. |
| Data 0012 — `hypobench-synthetic-election-level2:TRAIN-SET:0012:389f9702d175` | 20 source observations in [packet](data/error_analysis_memo_v2/packets/data_e7f52356f01b6284.json). | [generation rows 433–474](submission_v1/generations.jsonl#L433-L474): all seven arms, six hypotheses per arm. | [saved evaluation](runs/heldout_accuracy_optimized_v1/e7f52356f01b6284/e7f52356f01b6284_49bc70c955a26bf8_evaluation.json): every non-D-empty arm 0/501 correct, 501 invalid; D-empty 139/501, 1 invalid. | D H1 links debate-presence frustration to non-voting protest. The claim is observable in saved text but not independently judged. Observable failure: invalid held-out predictions across non-empty arms. |
| Data 0008 — `hypobench-synthetic-election-level2:TRAIN-SET:0008:3ac85a345990` | 20 source observations in [packet](data/error_analysis_memo_v2/packets/data_06f934aaaf59bfed.json). | [generation rows 271–312](submission_v1/generations.jsonl#L271-L312): all seven arms, six hypotheses per arm. | [saved evaluation](runs/heldout_accuracy_optimized_v1/06f934aaaf59bfed/06f934aaaf59bfed_c61e6943e00f636d_evaluation.json): every non-D-empty arm 0/501 correct, 501 invalid; D-empty 139/501, 1 invalid. | D H1 links frustration about debate presence to non-voting protest. No independent semantic judgment is available. Observable failure: invalid held-out predictions across non-empty arms. |
| Data 0009 — `hypobench-synthetic-election-level2:TRAIN-SET:0009:f87672ddc715` | 20 source observations in [packet](data/error_analysis_memo_v2/packets/data_366f9231e28f7bce.json). | [generation rows 313–348](submission_v1/generations.jsonl#L313-L348): QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled; D missing (failed generation cell). | [saved evaluation](runs/heldout_accuracy_optimized_v1/366f9231e28f7bce/366f9231e28f7bce_d67191de43f2416b_evaluation.json): six available arms each have 0/501 correct and 501 invalid, except D-empty 139/501 correct and 1 invalid. D unavailable. | QH H1: “Tweets explicitly endorsing a candidate are more likely to contain phrases associated with that candidate's party.” The claim is saved, not independently judged. Observable failure: invalid held-out predictions in available non-D-empty arms. |
| Literature `lit-2610.30103` | Target and 12 reference records in [packet](data/error_analysis_memo_v2/packets/literature_d494a62c5318b420.json); target title: “Did the Problem Actually Get Harder? Testing LLMs on Paired P and NP-Complete Problems Hardened by Adversarial Multi-Agent Rewriting.” | No saved generation rows for any arm. | No saved per-case evaluation; packet metrics are null. | Source record is present, but there is no generated response to inspect. Failure classification is unavailable; no model error can be inferred. |
| Literature `lit-2610.30099` | Target and 18 reference records in [packet](data/error_analysis_memo_v2/packets/literature_26ce0d8dc6652974.json); target title: “Differentially Private Sparse Reward Estimation with Preference Feedback.” | No saved generation rows for any arm. | No saved per-case evaluation; packet metrics are null. | Source record is present, but no arm output or outcome exists; no model error can be inferred. |
| Literature `lit-2610.29174` | Target and 10 reference records in [packet](data/error_analysis_memo_v2/packets/literature_0a2b1015c53619ab.json); target title: “LocalAgent: Collaborative Agentic Verification for Fine-Grained Instance-Level Consistency.” | No saved generation rows for any arm. | No saved per-case evaluation; packet metrics are null. | Source record is present, but no arm output or outcome exists; no model error can be inferred. |
| Literature `lit-2610.29439` | Target and 10 reference records in [packet](data/error_analysis_memo_v2/packets/literature_bed0b516a0c6fc6e.json); target title: “How Far Can Foundation Models Be Distilled for Efficient Jet Tagging?” | No saved generation rows for any arm. | No saved per-case evaluation; packet metrics are null. | Source record is present, but no arm output or outcome exists; no model error can be inferred. |
| Literature `lit-2610.29909` | Target and 11 reference records in [packet](data/error_analysis_memo_v2/packets/literature_66457e1f16e8053e.json); target title: “Tractable Inference with Kolmogorov-Arnold Networks.” | No saved generation rows for any arm. | No saved per-case evaluation; packet metrics are null. | Source record is present, but no arm output or outcome exists; no model error can be inferred. |
| Literature `lit-2610.29246` | Target and 26 reference records in [packet](data/error_analysis_memo_v2/packets/literature_98137d50b0720b36.json); target title: “DepState-JEPA: Learning Depth-Grounded State Representation for Visual Perception and Manipulation.” | No saved generation rows for any arm. | No saved per-case evaluation; packet metrics are null. | Source record is present, but no arm output or outcome exists; no model error can be inferred. |
| Literature `lit-2610.29517` | Target and 33 reference records in [packet](data/error_analysis_memo_v2/packets/literature_e65d31b014a08bce.json); target title: “AutoPhyX: Automatic Text-Condition Physics Property Generation.” | No saved generation rows for any arm. | No saved per-case evaluation; packet metrics are null. | Source record is present, but no arm output or outcome exists; no model error can be inferred. |
| Literature `lit-2610.29722` | Target and 17 reference records in [packet](data/error_analysis_memo_v2/packets/literature_37b40f0396493182.json); target title: “Retrieval Augmented Generation Compositionality.” | No saved generation rows for any arm. | No saved per-case evaluation; packet metrics are null. | Source record is present, but no arm output or outcome exists; no model error can be inferred. |
| Literature `lit-2610.30097` | Target and 32 reference records in [packet](data/error_analysis_memo_v2/packets/literature_d5fdf06ad61f2af4.json); target title: “AtomicRL: Atomic Reinforcement Learning for Long-Horizon Robotic Manipulation.” | No saved generation rows for any arm. | No saved per-case evaluation; packet metrics are null. | Source record is present, but no arm output or outcome exists; no model error can be inferred. |
| Literature `lit-2610.30105` | Target and 25 reference records in [packet](data/error_analysis_memo_v2/packets/literature_e34d5d54193089a7.json); target title: “Asymmetric On-Policy Distillation Learns In-Context Exploration.” | No saved generation rows for any arm. | No saved per-case evaluation; packet metrics are null. | Source record is present, but no arm output or outcome exists; no model error can be inferred. |

## Coverage and limitations

- **Seven cases have sufficient saved evidence for automatic, case-level
  generation/output availability review:** data sets 0017, 0011, 0013, 0015,
  0014, 0012, and 0008 (all seven arms plus associated 501-row outcome file).
- **Two data cases are partially analyzable:** 0019 (QH-sel missing) and 0009
  (D missing). The remaining saved arms and outcomes are reported above.
- **Eleven cases are blocked for output-based error analysis:** data 0007 has
  no generation or evaluation; all 10 literature cases have source packets but
  no generation rows or evaluations.
- **Independent human error analysis remains incomplete for all 20 cases.**
  Existing status is 0/20 sets and 0 coded arm cells. The examples above are
  record-based/automatic inspection; one directional comparison is AI-assisted
  and must not be represented as independent annotation.
- The repeated 0/501 and 501/501-invalid pattern for non-D-empty arms is a
  genuine saved evaluation outcome. It is an invalid-output/serving failure
  signal, not evidence that the generated scientific hypotheses are false.
  D-empty's 139/501 result and 1 invalid prediction are also recorded outcomes,
  not proof that the empty-input control is scientifically superior.
- Packet source evidence and reference metadata are not substitutes for missing
  literature arm outputs. Titles above identify source records only.

## Reproduction / verification

From the submission repository root, inspect the frozen sample and packet
status, then verify the saved held-out evaluation artifact hashes and aggregate
metrics using the existing read-only command:

```sh
python3 E6/reproduce_saved_heldout_accuracy.py
```

This command only checks saved artifacts and computes summaries; it does not
call a model, create generations, score new outputs, write results, or restart
the locked held-out evaluation. The raw records cited per case are
`E6/submission_v1/generations.jsonl`,
`E6/data/error_analysis_memo_v2/packets/*.json`, and the linked files under
`E6/runs/heldout_accuracy_optimized_v1/`.
