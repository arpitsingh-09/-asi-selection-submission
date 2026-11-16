# Literature review — reviewer B

Complete this document privately. Send only your completed document to the coordinator. Do not open the other reviewer document or coordinator reports until both reviews are submitted. Separate files do not enforce access control; distribute only the assigned document.

20 cases, seven checks each (140 decisions). Edit only the review-response JSON blocks. Use true/false for judgments; null means unanswered. Enter your identity and completion time in UTC (YYYY-MM-DDTHH:MM:SSZ) for each case. Set manual_check_completed to true only after all checks.

For every check, fill check_evidence with a brief rationale and source quote/location (or an explicit absence finding). Record extraction_errors and corrections as lists; use [] only when actually none. Originals are preserved; corrections require a new annotation version and renewed review.

The displayed four fields are MODEL extractions, not human judgments. Problem/method/result sidecars are separately attributed annotations and currently pending. Missing components require false checks and an omission explanation; do not invent annotations. A negative review is complete but does not accept the case.

## Frozen review guide

# Literature target-extraction review guide v2 — Decision 24 procedure approved

Review the preserved source field and exact extraction, not generated arm outputs.
Record the target ID, source-text SHA-256, extraction SHA-256, this guide's file
SHA-256, reviewer identity and UTC completion time. Work independently before
comparing judgments. A software validator cannot establish reviewer independence.

Answer each check with true or false:

- `research_question_extraction_accurate`: the extracted question faithfully
  represents the source's research question; it adds no unsupported claim.
- `main_hypothesis_extraction_accurate`: the extracted hypothesis faithfully
  represents the main hypothesis supported by the source's stated research aim.
- `research_question_explicitness_accurate`: the extracted explicitness flag
  correctly distinguishes a question expressly stated from one inferred.
- `main_hypothesis_explicitness_accurate`: the analogous flag is correct for the
  main hypothesis.

A null extracted field is accurate only if that field cannot be supported by
this exact source. Do not infer unavailable full text from an abstract. Record
source quotations/locations and the reason for negative judgments in notes.
Null fields do not become usable nonempty references merely because the null is
accurate; apply the separately approved missing-annotation scoring policy.

The existing two-independent-reviewer procedure is retained: two independent reviewers for each of the 20 fixed
cases. An independent third adjudicator resolves any disagreement, records four
final Boolean judgments and a rationale, and binds the sorted reviewer records
by SHA-256. The adjudicator must differ from the case's reviewers. Matching
negative judgments are still negative. Corrections require a new version of the
annotation and renewed checks; never overwrite the original annotation or mark
all cases accepted merely to reach 20. Report disagreement and completion counts.

Decision 24 additionally requires checking the extracted problem, method and
result against original source evidence. Record Boolean
`problem_extraction_accurate`, `method_extraction_accurate` and
`result_extraction_accurate`, with source quotations/locations in reviewer_notes.
Do not infer a missing extracted method or result from the generated hypotheses.
If an extraction does not contain a required component, record the omission and
a negative check; do not synthesize text or mark the component verified.
Record `extraction_errors` and `corrections` as explicit lists (empty only if
actually none). Corrections must name the original annotation, corrected text and
source location; preserve original records and re-review corrected versions.
Disagreements on any of the seven checks require independent adjudication.
All 20 deterministic cases must be reviewed before literature scoring. Approval
of this procedure is not evidence of a completed extraction or human review.

## lit-2610.29455 — Omnilingual-MsASR: Benchmarking Multimodal, Multilingual, Long-Form Multi-Speaker ASR of Omni Large Language Models

Source field: abstract (full preserved evidence):

```text
Omni-modal large language models (LLMs) have achieved remarkable progress in audio and video understanding. However, existing models struggle with long-form, multi-speaker videos, especially in understanding the entire video and recognizing who says what and when. To characterize the capability limit of current omni LLMs and guide future model development, we introduce Omnilingual-MsASR, a multilingual, multimodal benchmark for long-form Multi-speaker Automatic Speech Recognition (MsASR) covering six languages, recordings up to 30 minutes, and scenarios with up to 20 speakers. Omnilingual-MsASR provides parallel audio and video inputs to evaluate models' cross-modal consistency and their ability to exploit complementary cues across modalities. Extensive evaluations of leading omni-modal LLMs reveal substantial performance bottlenecks, while their tcpWERs frequently exceed 100%. These findings highlight fine-grained temporal localization, speaker disambiguation, and cross-modal synergy as key challenges for future omni-modal foundation models. Our work is available at https://github.com/QwenLM/Omnilingua-Bench/tree/main/Omnilingua-MSpeaker.
```

Saved model extraction (not a human review):

```json
{
  "main_hypothesis": null,
  "main_hypothesis_explicit": false,
  "research_question": "What are the capability limits of current omni-modal LLMs when processing long-form, multi-speaker videos, particularly in understanding the entire video and recognizing who says what and when?",
  "research_question_explicit": true
}
```

Separate source-component annotations (pending values are not extracted facts):

```json
{
  "components": {
    "method": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "problem": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "result": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    }
  },
  "fixed_extraction_sha256": "040458721af829f0d6d82d489aa92af50de9568953c121b2ad5b41847509a371",
  "input_set_id": "lit-2610.29455",
  "status": "pending_actual_source_annotations",
  "target_source_field": "abstract",
  "target_source_text_sha256": "ac61c9c5aa5d66450e697e58182b4beefc82fda3895c69fdb348a15cac48e566"
}
```

Mechanical attention flags (not judgments): ["research_question: explicit=true but no literal span; paraphrase/explicitness requires review"]

Review response:

```review-response
{
  "corrections": null,
  "disagreement_categories": null,
  "extraction_errors": null,
  "extraction_sha256": "040458721af829f0d6d82d489aa92af50de9568953c121b2ad5b41847509a371",
  "input_set_id": "lit-2610.29455",
  "main_hypothesis_explicitness_accurate": null,
  "main_hypothesis_extraction_accurate": null,
  "manual_check_completed": false,
  "method_extraction_accurate": null,
  "packet_sha256": "857fa548824cf0b3a4ab47ae901672e619237139f20f04bf03665f3c88b2b2e5",
  "problem_extraction_accurate": null,
  "research_question_explicitness_accurate": null,
  "research_question_extraction_accurate": null,
  "result_extraction_accurate": null,
  "review_guide_sha256": "64df98ff7ca39d7c2afb26940f795d33811dafce5ce5eac38adb43fdf2e43953",
  "reviewed_at_utc": null,
  "reviewer_id": null,
  "reviewer_notes": null,
  "reviewer_slot": 2,
  "source_component_binding_instruction": "Bind completed attributed sidecar digest before final source-component judgments.",
  "source_component_sidecar_sha256": null,
  "source_quotes_and_locations": null,
  "target_source_text_sha256": "ac61c9c5aa5d66450e697e58182b4beefc82fda3895c69fdb348a15cac48e566",
  "check_evidence": {
    "research_question_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "research_question_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "problem_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "method_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "result_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    }
  }
}
```

## lit-2610.30097 — AtomicRL: Atomic Reinforcement Learning for Long-Horizon Robotic Manipulation

Source field: abstract (full preserved evidence):

```text
Vision-language-action (VLA) models have shown promise in robotic manipulation, but imitation learning (IL) alone often struggles to master complex long-horizon skills. Reinforcement learning (RL) offers an effective avenue for further improving VLA policies. However, existing VLA-RL methods typically suffer from delayed and biased credit assignment due to trajectory-level sparse rewards, while imbalanced subtask mastery creates bottlenecks that limit overall performance. To address these challenges, we propose AtomicRL, an RL post-training framework that leverages atomic task structures for reliable credit assignment and adaptive exploration. AtomicRL introduces Semantic-Aware Policy Optimization (SAPO), which uses semantic-aware gating to constrain TD residuals from failed atomic subtasks from propagating across task boundaries, mitigating credit contamination while preserving intra-subtask credit assignment and value bootstrapping. In addition, Bottleneck-Adaptive Target Exploration (BATE) dynamically coordinates task sampling and local exploration incentives based on the mastery of individual atomic subtasks, directing learning toward the remaining bottlenecks. Finally, we develop a Real2Sim2Real pipeline that bridges online RL in simulation with real-world deployment, facilitating practical transfer to physical robots. On LIBERO-LONG, AtomicRL achieves absolute performance gains of 3.6% and 4.0% over PPO across two VLA architectures. On CALVIN ABC-D, it improves full-task performance by up to 9.5% over PPO. Combined with the Real2Sim2Real pipeline, AtomicRL further improves real-world task performance by an average of 21.3%. These results demonstrate that AtomicRL effectively improves the learning efficiency and manipulation performance of VLA policies on long-horizon tasks.
```

Saved model extraction (not a human review):

```json
{
  "main_hypothesis": "AtomicRL, an RL post-training framework leveraging atomic task structures and incorporating Semantic-Aware Policy Optimization (SAPO) and Bottleneck-Adaptive Target Exploration (BATE), will improve the learning efficiency and manipulation performance of VLA policies on long-horizon tasks.",
  "main_hypothesis_explicit": false,
  "research_question": "How can reinforcement learning be improved to address challenges like delayed credit assignment and imbalanced subtask mastery in vision-language-action (VLA) models for robotic manipulation?",
  "research_question_explicit": false
}
```

Separate source-component annotations (pending values are not extracted facts):

```json
{
  "components": {
    "method": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "problem": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "result": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    }
  },
  "fixed_extraction_sha256": "3842cd8b86a91d49d89e0ba6878449f0f3305aa9048fb12ec9551251bdb07a2f",
  "input_set_id": "lit-2610.30097",
  "status": "pending_actual_source_annotations",
  "target_source_field": "abstract",
  "target_source_text_sha256": "04dac0bd89e2e80d72c2a3612f68c922d323a13941e922ab3b037b7c75aaeee5"
}
```

Mechanical attention flags (not judgments): []

Review response:

```review-response
{
  "corrections": null,
  "disagreement_categories": null,
  "extraction_errors": null,
  "extraction_sha256": "3842cd8b86a91d49d89e0ba6878449f0f3305aa9048fb12ec9551251bdb07a2f",
  "input_set_id": "lit-2610.30097",
  "main_hypothesis_explicitness_accurate": null,
  "main_hypothesis_extraction_accurate": null,
  "manual_check_completed": false,
  "method_extraction_accurate": null,
  "packet_sha256": "b201da21e7c1c040e8fcc18833e1c3b0a6b48d5a737d156760be1bf99fb654e8",
  "problem_extraction_accurate": null,
  "research_question_explicitness_accurate": null,
  "research_question_extraction_accurate": null,
  "result_extraction_accurate": null,
  "review_guide_sha256": "64df98ff7ca39d7c2afb26940f795d33811dafce5ce5eac38adb43fdf2e43953",
  "reviewed_at_utc": null,
  "reviewer_id": null,
  "reviewer_notes": null,
  "reviewer_slot": 2,
  "source_component_binding_instruction": "Bind completed attributed sidecar digest before final source-component judgments.",
  "source_component_sidecar_sha256": null,
  "source_quotes_and_locations": null,
  "target_source_text_sha256": "04dac0bd89e2e80d72c2a3612f68c922d323a13941e922ab3b037b7c75aaeee5",
  "check_evidence": {
    "research_question_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "research_question_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "problem_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "method_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "result_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    }
  }
}
```

## lit-2610.29196 — A Unified Evaluation Framework of Physical Adversarial Robustness in the Edge VLM Era

Source field: abstract (full preserved evidence):

```text
Recent advancements in Vision-Language Models (VLMs) enable end-to-end visual grounding via language prompts and generative decoding, demonstrating largely improved zero-shot and open-vocabulary detection capabilities. As a result, VLMs are rapidly being deployed at the edge in safety-critical real-world systems. However, the physical adversarial robustness of edge VLMs has not been systematically studied, and the fundamental differences in output with modern object detectors create methodological challenges for fair evaluation. To compare the two families directly, we evaluate every selected representative model on one outcome: whether an adversarial patch worn on a person evades detection of the model. We report this by introducing a unified metric, conditional attack success rate (cASR), counted only on images the model still localizes under a matched gray occluder, and partition every failure into omission (no box), substitution (a box on the patch), and displacement (a box on neither). We benchmark the physical adversarial vulnerability of compact grounding VLMs against a range of object detectors, and find that the VLMs can be as vulnerable as the detectors. We disclose that failure mode is largely associated with the output format of a model rather than its architecture family. Of the three, only omission is visible to a downstream system; displacement and substitution return confident, well-formed boxes, making them potentially more dangerous failures. Further, we find that, under distribution shift, VLMs that primarily failed by omission instead shift to failing more by displacement/substitution. Thus, a grounding VLM can inherit the detector's vulnerability while showing the possibility to adopt more dangerous failure modes. Our code and data are available at https://github.com/ericliang1/physical-adversarial-robustness.
```

Saved model extraction (not a human review):

```json
{
  "main_hypothesis": "VLMs can be as vulnerable to physical adversarial attacks as object detectors, and the failure mode is largely associated with the output format of a model rather than its architecture family.",
  "main_hypothesis_explicit": true,
  "research_question": "How does the physical adversarial robustness of edge Vision-Language Models (VLMs) compare to that of object detectors, and what are the failure modes associated with these models when subjected to physical adversarial attacks?",
  "research_question_explicit": true
}
```

Separate source-component annotations (pending values are not extracted facts):

```json
{
  "components": {
    "method": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "problem": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "result": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    }
  },
  "fixed_extraction_sha256": "1814fbf043c3f15f361a9adcfe781af1680e91afcd3eabc5b13885de9a27b683",
  "input_set_id": "lit-2610.29196",
  "status": "pending_actual_source_annotations",
  "target_source_field": "abstract",
  "target_source_text_sha256": "d47eb2b224a7f9f9169a66a539774eda291d0a8b3ae92b85a9a8f7112712e37b"
}
```

Mechanical attention flags (not judgments): ["research_question: explicit=true but no literal span; paraphrase/explicitness requires review", "main_hypothesis: explicit=true but no literal span; paraphrase/explicitness requires review"]

Review response:

```review-response
{
  "corrections": null,
  "disagreement_categories": null,
  "extraction_errors": null,
  "extraction_sha256": "1814fbf043c3f15f361a9adcfe781af1680e91afcd3eabc5b13885de9a27b683",
  "input_set_id": "lit-2610.29196",
  "main_hypothesis_explicitness_accurate": null,
  "main_hypothesis_extraction_accurate": null,
  "manual_check_completed": false,
  "method_extraction_accurate": null,
  "packet_sha256": "f880b97430e7be9034e498a52c0d9a8bea40219a30bc818f17fba5e9780dd2fe",
  "problem_extraction_accurate": null,
  "research_question_explicitness_accurate": null,
  "research_question_extraction_accurate": null,
  "result_extraction_accurate": null,
  "review_guide_sha256": "64df98ff7ca39d7c2afb26940f795d33811dafce5ce5eac38adb43fdf2e43953",
  "reviewed_at_utc": null,
  "reviewer_id": null,
  "reviewer_notes": null,
  "reviewer_slot": 2,
  "source_component_binding_instruction": "Bind completed attributed sidecar digest before final source-component judgments.",
  "source_component_sidecar_sha256": null,
  "source_quotes_and_locations": null,
  "target_source_text_sha256": "d47eb2b224a7f9f9169a66a539774eda291d0a8b3ae92b85a9a8f7112712e37b",
  "check_evidence": {
    "research_question_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "research_question_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "problem_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "method_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "result_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    }
  }
}
```

## lit-2512.24120 — Enhancing LLM-Based Neural Network Generation: Few-Shot Prompting and Efficient Validation for Automated Architecture Design

Source field: abstract (full preserved evidence):

```text
Automated neural network architecture design remains a significant challenge in computer vision. Task diversity and computational constraints require both effective architectures and efficient search methods. Large Language Models (LLMs) present a promising alternative to computationally intensive Neural Architecture Search (NAS), but their application to architecture generation in computer vision has not been systematically studied, particularly regarding prompt engineering and validation strategies. Building on the task-agnostic NNGPT/LEMUR framework, this work introduces and validates two key contributions for computer vision. First, we present Few-Shot Architecture Prompting (FSAP), the first systematic study of the number of supporting examples (n = 1, 2, 3, 4, 5, 6) for LLM-based architecture generation. We find that using n = 3 examples best balances architectural diversity and context focus for vision tasks. Second, we introduce Whitespace-Normalized Hash Validation, a lightweight deduplication method (less than 1 ms) that provides a 100x speedup over AST parsing and prevents redundant training of duplicate computer vision architectures. In large-scale experiments across seven computer vision benchmarks (MNIST, CIFAR-10, CIFAR-100, CelebA, ImageNette, SVHN, Places365), we generated 1,900 unique architectures. We also introduce a dataset-balanced evaluation methodology to address the challenge of comparing architectures across heterogeneous vision tasks. These contributions provide actionable guidelines for LLM-based architecture search in computer vision and establish rigorous evaluation practices, making automated design more accessible to researchers with limited computational resources.
```

Saved model extraction (not a human review):

```json
{
  "main_hypothesis": null,
  "main_hypothesis_explicit": false,
  "research_question": "How can Large Language Models (LLMs) be effectively applied to architecture generation in computer vision, particularly regarding prompt engineering and validation strategies?",
  "research_question_explicit": false
}
```

Separate source-component annotations (pending values are not extracted facts):

```json
{
  "components": {
    "method": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "problem": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "result": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    }
  },
  "fixed_extraction_sha256": "a0710cbab9257331cc8e40626744c278c75253ad54f5f922e3b4dad51923ac3c",
  "input_set_id": "lit-2512.24120",
  "status": "pending_actual_source_annotations",
  "target_source_field": "abstract",
  "target_source_text_sha256": "05d60f5d22862f9a630488a5009513736c9e9b9556bf824eea01831746092683"
}
```

Mechanical attention flags (not judgments): []

Review response:

```review-response
{
  "corrections": null,
  "disagreement_categories": null,
  "extraction_errors": null,
  "extraction_sha256": "a0710cbab9257331cc8e40626744c278c75253ad54f5f922e3b4dad51923ac3c",
  "input_set_id": "lit-2512.24120",
  "main_hypothesis_explicitness_accurate": null,
  "main_hypothesis_extraction_accurate": null,
  "manual_check_completed": false,
  "method_extraction_accurate": null,
  "packet_sha256": "f6bcd0784d363bf5895e202a6d5d2971968c081d421cc6b9ca679ee9fd945024",
  "problem_extraction_accurate": null,
  "research_question_explicitness_accurate": null,
  "research_question_extraction_accurate": null,
  "result_extraction_accurate": null,
  "review_guide_sha256": "64df98ff7ca39d7c2afb26940f795d33811dafce5ce5eac38adb43fdf2e43953",
  "reviewed_at_utc": null,
  "reviewer_id": null,
  "reviewer_notes": null,
  "reviewer_slot": 2,
  "source_component_binding_instruction": "Bind completed attributed sidecar digest before final source-component judgments.",
  "source_component_sidecar_sha256": null,
  "source_quotes_and_locations": null,
  "target_source_text_sha256": "05d60f5d22862f9a630488a5009513736c9e9b9556bf824eea01831746092683",
  "check_evidence": {
    "research_question_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "research_question_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "problem_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "method_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "result_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    }
  }
}
```

## lit-2610.29746 — LEAF-Mamba: Feature Adaptation and Fusion for Whole Slide Image Analysis

Source field: abstract (full preserved evidence):

```text
Whole slide image (WSI) analysis enables computational diagnosis and prognosis, but gigapixel images and limited annotations make slide-level learning challenging. Multiple instance learning addresses this task by aggregating patch representations from frozen pretrained encoders. Recently, Mamba has enabled efficient modeling of long patch sequences. However, task supervision alone does not explicitly constrain information recovery during feature adaptation, while Mamba couples local processing with long-range propagation rather than retaining separate representations for fusion. Motivated by these challenges, we introduce LEAF-Mamba, a framework that jointly addresses latent evidence adaptation and fusion for frozen-feature WSI analysis. A reconstruction-regularized adapter learns compact, task-specific representations while reconstructing the input features. Parallel Mamba and convolutional streams then capture long-range dependencies and sequence-local interactions, with an input-dependent gate modulating their joint representation before slide-level pooling. Experiments across feature extractors demonstrate improved average performance over strong MIL baselines in both diagnostic classification and survival prediction. Component analyses further support the contributions of adaptation and fusion. These findings highlight the value of jointly designing feature transformation and contextual aggregation to translate pretrained representations into effective slide-level predictions.
```

Saved model extraction (not a human review):

```json
{
  "main_hypothesis": "Jointly designing feature transformation and contextual aggregation will translate pretrained representations into effective slide-level predictions.",
  "main_hypothesis_explicit": false,
  "research_question": "How can latent evidence adaptation and fusion be jointly addressed to improve slide-level analysis using frozen-feature whole slide images?",
  "research_question_explicit": false
}
```

Separate source-component annotations (pending values are not extracted facts):

```json
{
  "components": {
    "method": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "problem": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "result": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    }
  },
  "fixed_extraction_sha256": "f342de5063fac466a8c5d23addafb49b3faeea011fa6cc023659b24c573431a3",
  "input_set_id": "lit-2610.29746",
  "status": "pending_actual_source_annotations",
  "target_source_field": "abstract",
  "target_source_text_sha256": "d9e79187f1c8851155a922fd788c086fb261806a17f9ade4b081844746d784e3"
}
```

Mechanical attention flags (not judgments): []

Review response:

```review-response
{
  "corrections": null,
  "disagreement_categories": null,
  "extraction_errors": null,
  "extraction_sha256": "f342de5063fac466a8c5d23addafb49b3faeea011fa6cc023659b24c573431a3",
  "input_set_id": "lit-2610.29746",
  "main_hypothesis_explicitness_accurate": null,
  "main_hypothesis_extraction_accurate": null,
  "manual_check_completed": false,
  "method_extraction_accurate": null,
  "packet_sha256": "600d57d50daa5a712c1dcd66c77d833088a2ff71c6878cbf9e21dea3863a9216",
  "problem_extraction_accurate": null,
  "research_question_explicitness_accurate": null,
  "research_question_extraction_accurate": null,
  "result_extraction_accurate": null,
  "review_guide_sha256": "64df98ff7ca39d7c2afb26940f795d33811dafce5ce5eac38adb43fdf2e43953",
  "reviewed_at_utc": null,
  "reviewer_id": null,
  "reviewer_notes": null,
  "reviewer_slot": 2,
  "source_component_binding_instruction": "Bind completed attributed sidecar digest before final source-component judgments.",
  "source_component_sidecar_sha256": null,
  "source_quotes_and_locations": null,
  "target_source_text_sha256": "d9e79187f1c8851155a922fd788c086fb261806a17f9ade4b081844746d784e3",
  "check_evidence": {
    "research_question_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "research_question_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "problem_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "method_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "result_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    }
  }
}
```

## lit-2610.30119 — Self-normalized Bernstein Inequalities for Regenerative Processes and Applications to Learning Without Independence

Source field: abstract (full preserved evidence):

```text
We prove a self-normalized Bernstein inequality for bounded functions of a regenerative process with independent, identically distributed marked cycles of finite mean length. The bound uses observed cycle lengths and retains explicit terms for truncation and the cycle ending after the observation horizon. Selecting a tuning parameter from a finite deterministic collection gives a version of Bernstein inequality where all terms are empirical but one, related to the tails of the regeneration times. We then study this term in many regimes: it turns out that it is of second-order in many cases of interest. This is important for applications in machine learning: we prove generalization error bounds for classification with non-i.i.d., regenerative data. These bounds can be used to define learning objectives: by minimizing the first-order term only in the bound, we define agnostic classifiers that still satisfy oracle inequalities. We also show that the bound on the average deviation provided by our results is minimax-optimal in the sample size and in the expected regeneration time. Finally, we combine the Bernstein inequality with a regenerative strong approximation to obtain a Gaussian approximation using an observable block variance estimator.
```

Saved model extraction (not a human review):

```json
{
  "main_hypothesis": "A self-normalized Bernstein inequality can be proven for bounded functions of a regenerative process with independent, identically distributed marked cycles of finite mean length, and this inequality can be used to derive generalization error bounds for classification with non-i.i.d., regenerative data.",
  "main_hypothesis_explicit": false,
  "research_question": "Can a self-normalized Bernstein inequality be proven for bounded functions of a regenerative process with independent, identically distributed marked cycles, and how can this be applied to machine learning?",
  "research_question_explicit": false
}
```

Separate source-component annotations (pending values are not extracted facts):

```json
{
  "components": {
    "method": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "problem": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "result": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    }
  },
  "fixed_extraction_sha256": "f9d13b7468263284c2a6246a6b2e76f1fb4aa41cb6ea49d4f0484705a22e221b",
  "input_set_id": "lit-2610.30119",
  "status": "pending_actual_source_annotations",
  "target_source_field": "abstract",
  "target_source_text_sha256": "7115da1f4a89e4faa7f1bcc3a7f1955354a8085db0f3b90b76f015625b8d2e89"
}
```

Mechanical attention flags (not judgments): []

Review response:

```review-response
{
  "corrections": null,
  "disagreement_categories": null,
  "extraction_errors": null,
  "extraction_sha256": "f9d13b7468263284c2a6246a6b2e76f1fb4aa41cb6ea49d4f0484705a22e221b",
  "input_set_id": "lit-2610.30119",
  "main_hypothesis_explicitness_accurate": null,
  "main_hypothesis_extraction_accurate": null,
  "manual_check_completed": false,
  "method_extraction_accurate": null,
  "packet_sha256": "49c353b1b981d6409edd92e8ac215b97680719c3a6c8796229d253abe991ef4c",
  "problem_extraction_accurate": null,
  "research_question_explicitness_accurate": null,
  "research_question_extraction_accurate": null,
  "result_extraction_accurate": null,
  "review_guide_sha256": "64df98ff7ca39d7c2afb26940f795d33811dafce5ce5eac38adb43fdf2e43953",
  "reviewed_at_utc": null,
  "reviewer_id": null,
  "reviewer_notes": null,
  "reviewer_slot": 2,
  "source_component_binding_instruction": "Bind completed attributed sidecar digest before final source-component judgments.",
  "source_component_sidecar_sha256": null,
  "source_quotes_and_locations": null,
  "target_source_text_sha256": "7115da1f4a89e4faa7f1bcc3a7f1955354a8085db0f3b90b76f015625b8d2e89",
  "check_evidence": {
    "research_question_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "research_question_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "problem_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "method_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "result_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    }
  }
}
```

## lit-2610.29246 — DepState-JEPA: Learning Depth-Grounded State Representation for Visual Perception and Manipulation

Source field: abstract (full preserved evidence):

```text
Predictive representations for robot manipulation should connect scene geometry with the state changes induced by actions. Our intuition is that understanding what an action will change starts with understanding where things are: complementary RGB and depth observations ground a common scene representation from which to infer those changes. Guided by this intuition, we introduce \textbf{DepState-JEPA}, a dual-stream RGB--Depth joint-embedding predictive architecture that connects spatial understanding with action-conditioned prediction through a shared latent state, \textbf{DepState}. Built on V-JEPA~2.1, the framework uses depth both as a complementary observation stream and to ground both modalities in metric 3D space, aggregating shared information into DepState while retaining modality-private features for decoding. Ray-conditioned readouts predict local features without target depth; after an action-conditioned transition, the same decoders predict future RGB and depth features using the predicted state and fixed initial private features. Robot-state readouts provide recursive proprioceptive inputs; object-trajectory supervision and calibrated forward kinematics shape state learning through motion targets and joint--TCP consistency. Comparisons show stronger RGB-encoder transfer after RGB-D adaptation, feature completion, conditioned visual forecasting, and manipulation success. Within-model ablations identify contributions from depth content, metric coordinates, and future-state matching, with additional control gains from FK regularization.
```

Saved model extraction (not a human review):

```json
{
  "main_hypothesis": "Connecting scene geometry with the state changes induced by actions can be achieved through a dual-stream RGB--Depth joint-embedding predictive architecture that connects spatial understanding with action-conditioned prediction through a shared latent state (DepState).",
  "main_hypothesis_explicit": false,
  "research_question": "How can scene geometry be connected with the state changes induced by actions in robot manipulation?",
  "research_question_explicit": false
}
```

Separate source-component annotations (pending values are not extracted facts):

```json
{
  "components": {
    "method": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "problem": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "result": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    }
  },
  "fixed_extraction_sha256": "99d106251e84e9cc81b55909b53b38c6a696a212082f7a0731c44f3c8c691498",
  "input_set_id": "lit-2610.29246",
  "status": "pending_actual_source_annotations",
  "target_source_field": "abstract",
  "target_source_text_sha256": "5bec2768715ac90188685a5d90e344c92a3dc39d1ecaf5d7c5a1baff69963f68"
}
```

Mechanical attention flags (not judgments): []

Review response:

```review-response
{
  "corrections": null,
  "disagreement_categories": null,
  "extraction_errors": null,
  "extraction_sha256": "99d106251e84e9cc81b55909b53b38c6a696a212082f7a0731c44f3c8c691498",
  "input_set_id": "lit-2610.29246",
  "main_hypothesis_explicitness_accurate": null,
  "main_hypothesis_extraction_accurate": null,
  "manual_check_completed": false,
  "method_extraction_accurate": null,
  "packet_sha256": "25187a9505b87cb4a444cddb4b751924bac9d9f987fd5348fbe25a5775fe08be",
  "problem_extraction_accurate": null,
  "research_question_explicitness_accurate": null,
  "research_question_extraction_accurate": null,
  "result_extraction_accurate": null,
  "review_guide_sha256": "64df98ff7ca39d7c2afb26940f795d33811dafce5ce5eac38adb43fdf2e43953",
  "reviewed_at_utc": null,
  "reviewer_id": null,
  "reviewer_notes": null,
  "reviewer_slot": 2,
  "source_component_binding_instruction": "Bind completed attributed sidecar digest before final source-component judgments.",
  "source_component_sidecar_sha256": null,
  "source_quotes_and_locations": null,
  "target_source_text_sha256": "5bec2768715ac90188685a5d90e344c92a3dc39d1ecaf5d7c5a1baff69963f68",
  "check_evidence": {
    "research_question_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "research_question_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "problem_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "method_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "result_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    }
  }
}
```

## lit-2610.28836 — Sketch2Sim: an end-to-end modular framework for hand-drawn circuit analysis

Source field: abstract (full preserved evidence):

```text
This study proposes a sketch-to-simulation system to solve handwritten circuit diagrams. The system converts raw images into a Simulation Program with Integrated Circuit Emphasis (SPICE)-compatible netlist and automatically calculates the circuit's nodal voltages and currents. Another objective is to propose a holistic framework that benefits students and educators by enhancing the teaching and learning experience of electric circuits and expediting engineering design reviews. This article presents a multistage pipeline that converts raw photographs of handwritten electric circuits into executable SPICE-like netlists, providing a solution. A dataset of 1,000 hand-drawn Resistor-Inductor-Capacitor (RLC) circuits was curated and annotated for components, text regions, and character recognition. The proposed system decomposes a circuit diagram into three stages: (i) dual You Only Look Once (YOLO)-based detectors for components and text regions, (ii) a Convolutional Recurrent Neural Network (CRNN) with Connectionist Temporal Classification (CTC) and Optical Character Recognition (OCR)-based domain-aware symbol value extraction, and (iii) image processing with thresholding, skeletonization, and Density-Based Spatial Clustering of Applications with Noise (DBSCAN) to automatically identify nodes and map them with corresponding components. The proposed system produces the netlist and solves the circuit. The qualitative and quantitative ablation studies on modular stages, as well as end-to-end tests, demonstrate robust performance across various handwriting styles, lighting conditions, and clutter.This study serves as an interactive learning aid and practical tool for professionals, providing a comprehensive user interface (UI), enabling rapid digitization of circuit sketches for study, design, prototyping, or troubleshooting.
```

Saved model extraction (not a human review):

```json
{
  "main_hypothesis": null,
  "main_hypothesis_explicit": false,
  "research_question": "How can raw images of handwritten circuit diagrams be converted into executable SPICE-like netlists?",
  "research_question_explicit": true
}
```

Separate source-component annotations (pending values are not extracted facts):

```json
{
  "components": {
    "method": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "problem": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "result": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    }
  },
  "fixed_extraction_sha256": "9f85f10ec4dab580814c8882864da0e5d58b6b352c9a698367a9f02f9d566c44",
  "input_set_id": "lit-2610.28836",
  "status": "pending_actual_source_annotations",
  "target_source_field": "abstract",
  "target_source_text_sha256": "8b27197acecf25694ae1bc3a2a31f3ec3944488924a0ab295f51c923afc424da"
}
```

Mechanical attention flags (not judgments): ["research_question: explicit=true but no literal span; paraphrase/explicitness requires review"]

Review response:

```review-response
{
  "corrections": null,
  "disagreement_categories": null,
  "extraction_errors": null,
  "extraction_sha256": "9f85f10ec4dab580814c8882864da0e5d58b6b352c9a698367a9f02f9d566c44",
  "input_set_id": "lit-2610.28836",
  "main_hypothesis_explicitness_accurate": null,
  "main_hypothesis_extraction_accurate": null,
  "manual_check_completed": false,
  "method_extraction_accurate": null,
  "packet_sha256": "1624b977dd97214a7f1d1980958b2c593297e652c2a7df079bcdf050ba235ef0",
  "problem_extraction_accurate": null,
  "research_question_explicitness_accurate": null,
  "research_question_extraction_accurate": null,
  "result_extraction_accurate": null,
  "review_guide_sha256": "64df98ff7ca39d7c2afb26940f795d33811dafce5ce5eac38adb43fdf2e43953",
  "reviewed_at_utc": null,
  "reviewer_id": null,
  "reviewer_notes": null,
  "reviewer_slot": 2,
  "source_component_binding_instruction": "Bind completed attributed sidecar digest before final source-component judgments.",
  "source_component_sidecar_sha256": null,
  "source_quotes_and_locations": null,
  "target_source_text_sha256": "8b27197acecf25694ae1bc3a2a31f3ec3944488924a0ab295f51c923afc424da",
  "check_evidence": {
    "research_question_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "research_question_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "problem_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "method_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "result_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    }
  }
}
```

## lit-2512.24827 — Inter-Agent Relative Representations for Multi-Agent Option Discovery

Source field: abstract (full preserved evidence):

```text
Temporally extended actions improve the ability to explore and plan in single-agent settings. In multi-agent settings, the exponential growth of the joint state space with the number of agents makes coordinated behaviours even more valuable. Yet, this same exponential growth renders the design of multi-agent options particularly challenging. Existing multi-agent option discovery methods often sacrifice coordination by producing loosely coupled or fully independent behaviours. Toward addressing these limitations, we describe a novel approach for multi-agent option discovery. Specifically, we propose a joint-state abstraction that compresses the state space while preserving the information necessary to discover strongly coordinated behaviours. Our approach builds on the inductive bias that synchronisation over agent states provides a natural foundation for coordination in the absence of explicit objectives. We first approximate a fictitious state of maximal alignment with the team, the \textit{Fermat} state, and use it to define a measure of \textit{spreadness}, capturing team-level misalignment on each individual state dimension. Building on this representation, we then employ a neural graph Laplacian estimator to derive options that capture state synchronisation patterns between agents. We evaluate the resulting options across multiple scenarios in two simulated multi-agent domains, showing that they yield stronger downstream coordination capabilities compared to alternative option discovery methods.
```

Saved model extraction (not a human review):

```json
{
  "main_hypothesis": "A joint-state abstraction, built on the inductive bias that synchronisation over agent states provides a natural foundation for coordination, can be used to discover multi-agent options that yield stronger downstream coordination capabilities compared to alternative option discovery methods.",
  "main_hypothesis_explicit": false,
  "research_question": "How can multi-agent option discovery methods be improved to produce strongly coordinated behaviours, given the challenges posed by the exponential growth of the joint state space with the number of agents?",
  "research_question_explicit": false
}
```

Separate source-component annotations (pending values are not extracted facts):

```json
{
  "components": {
    "method": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "problem": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "result": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    }
  },
  "fixed_extraction_sha256": "10bd2b9ba13a5903c55e2a257c51d04ef6ac1c4118ef9c22db06170136fde80d",
  "input_set_id": "lit-2512.24827",
  "status": "pending_actual_source_annotations",
  "target_source_field": "abstract",
  "target_source_text_sha256": "8f092165fa8c70008343c43b66ca8b9a482b2ff5bc29e4da343812c6778e5488"
}
```

Mechanical attention flags (not judgments): []

Review response:

```review-response
{
  "corrections": null,
  "disagreement_categories": null,
  "extraction_errors": null,
  "extraction_sha256": "10bd2b9ba13a5903c55e2a257c51d04ef6ac1c4118ef9c22db06170136fde80d",
  "input_set_id": "lit-2512.24827",
  "main_hypothesis_explicitness_accurate": null,
  "main_hypothesis_extraction_accurate": null,
  "manual_check_completed": false,
  "method_extraction_accurate": null,
  "packet_sha256": "ce18c9d29d4dd20148ac4792be8e541b74b4fef22fc993488b7c5fb1fd52ca10",
  "problem_extraction_accurate": null,
  "research_question_explicitness_accurate": null,
  "research_question_extraction_accurate": null,
  "result_extraction_accurate": null,
  "review_guide_sha256": "64df98ff7ca39d7c2afb26940f795d33811dafce5ce5eac38adb43fdf2e43953",
  "reviewed_at_utc": null,
  "reviewer_id": null,
  "reviewer_notes": null,
  "reviewer_slot": 2,
  "source_component_binding_instruction": "Bind completed attributed sidecar digest before final source-component judgments.",
  "source_component_sidecar_sha256": null,
  "source_quotes_and_locations": null,
  "target_source_text_sha256": "8f092165fa8c70008343c43b66ca8b9a482b2ff5bc29e4da343812c6778e5488",
  "check_evidence": {
    "research_question_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "research_question_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "problem_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "method_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "result_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    }
  }
}
```

## lit-2610.29227 — Schrödinger-Bass Bridge Barycenter Models for Measure-Valued Data

Source field: abstract (full preserved evidence):

```text
Barycenter models, based on stochastic and deterministic optimal transport bridges between probability measures, have proven to be useful for supervised and unsupervised learning for (probability) measure-valued data. In this paper, we utilize the directional asymmetry and dual drift-diffusion control arising in the recently proposed Schrödinger-Bass Bridge (SBB) between two measures, and propose \textit{SBB-encoder}, \textit{SBB-decoder}, \textit{SBB-symmetric}, and \textit{SBB-Markovian} barycenter models. For each of these novel models, our first theoretical result establishes the existence of the SBB-barycenter under mild assumptions. Our second theoretical result characterizes the decoder SBB-barycenter of Gaussians where we show that for Gaussian input measures, the decoder formulation admits a Gaussian minimizer, reducing barycenter computation to a finite-dimensional optimization and yielding a compact algorithm. For general input measures, we derive a hybrid Wasserstein gradient particle descent scheme for all four formulations using the SBB dual representation. Finally, we utilize these algorithms for solving distributional-inverse/interpolation problems arising in the context of spatial images and single-cell RNA sequencing data, where we show that the SBB-decoder and Markovian barycenter allow us to interpolate between successive time points. Results show that our method outperforms existing barycenter models for measure interpolation and inference.
```

Saved model extraction (not a human review):

```json
{
  "main_hypothesis": "SBB-decoder and Markovian barycenter models will allow interpolation between successive time points and outperform existing barycenter models for measure interpolation and inference.",
  "main_hypothesis_explicit": true,
  "research_question": "Can barycenter models based on the Schrödinger-Bass Bridge (SBB) be developed and utilized to solve distributional-inverse/interpolation problems, and do these models outperform existing barycenter models for measure interpolation and inference?",
  "research_question_explicit": true
}
```

Separate source-component annotations (pending values are not extracted facts):

```json
{
  "components": {
    "method": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "problem": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "result": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    }
  },
  "fixed_extraction_sha256": "cdbbc81ee8c913dbc86762bb424878f2ce985fbcf949c35839b8281e9627aebf",
  "input_set_id": "lit-2610.29227",
  "status": "pending_actual_source_annotations",
  "target_source_field": "abstract",
  "target_source_text_sha256": "0033f35ae19f883b0e05b2e0204d7ffcf2d8111eda2a600344f0ff6e77d4640b"
}
```

Mechanical attention flags (not judgments): ["research_question: explicit=true but no literal span; paraphrase/explicitness requires review", "main_hypothesis: explicit=true but no literal span; paraphrase/explicitness requires review"]

Review response:

```review-response
{
  "corrections": null,
  "disagreement_categories": null,
  "extraction_errors": null,
  "extraction_sha256": "cdbbc81ee8c913dbc86762bb424878f2ce985fbcf949c35839b8281e9627aebf",
  "input_set_id": "lit-2610.29227",
  "main_hypothesis_explicitness_accurate": null,
  "main_hypothesis_extraction_accurate": null,
  "manual_check_completed": false,
  "method_extraction_accurate": null,
  "packet_sha256": "d9e2baa92e5aadc499ed767c1b0214c5b8890b6d388c51c0f4c93fccc00c6db5",
  "problem_extraction_accurate": null,
  "research_question_explicitness_accurate": null,
  "research_question_extraction_accurate": null,
  "result_extraction_accurate": null,
  "review_guide_sha256": "64df98ff7ca39d7c2afb26940f795d33811dafce5ce5eac38adb43fdf2e43953",
  "reviewed_at_utc": null,
  "reviewer_id": null,
  "reviewer_notes": null,
  "reviewer_slot": 2,
  "source_component_binding_instruction": "Bind completed attributed sidecar digest before final source-component judgments.",
  "source_component_sidecar_sha256": null,
  "source_quotes_and_locations": null,
  "target_source_text_sha256": "0033f35ae19f883b0e05b2e0204d7ffcf2d8111eda2a600344f0ff6e77d4640b",
  "check_evidence": {
    "research_question_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "research_question_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "problem_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "method_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "result_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    }
  }
}
```

## lit-2610.29302 — Compressing Onboard Language Models for Space Robots under a Behavioral-Fidelity Requirement

Source field: abstract (full preserved evidence):

```text
Language models are being explored as the interface through which space robots interpret operator commands and select among verified skills. Running them onboard calls for low-bit compression, and flight use adds requirements that generic post-training quantization leaves implicit: a fixed memory budget and storage format, a static artifact under configuration control, and behavior close to the full-precision model validated on the ground. We treat compression as a ground-segment step and study QSelect, which composes one static low-bit model from compatible AWQ, GPTQ, and AutoRound checkpoints by assigning each linear module to one quantizer family and scoring every substitution at the final next-token distribution. The default fidelity mode needs no labels or tuned thresholds and accepts a substitution only when the forward KL divergence from the BF16 reference decreases; an optional target-adapted mode adds answer likelihood on a small labeled set. On DeepSeek-R1-Distill-Qwen-7B, Llama-3.1-8B, and Llama-3.2-3B at 3 and 4 bits, composed models reach lower mean held-out perplexity than every single-family model in all six settings, and the fidelity mode lowers perplexity and KL further. In a matched scaffold, final-output scoring gives lower held-out KL than representation-similarity scoring in all 12 paired runs. With labels from training or development splits of the evaluated task families, the target-adapted mode raises 3-bit pooled accuracy on the two Llama models by 4.3 and 4.5 points over the best single-family model. At 3 bits, unquantized embedding and output layers make up 43-46% of the packed artifact. All evaluations use general-domain benchmarks on a ground GPU; space-domain tasks and flight hardware are left to future work.
```

Saved model extraction (not a human review):

```json
{
  "main_hypothesis": "Composing a low-bit model from multiple quantizer families (AWQ, GPTQ, and AutoRound) using a scoring method based on next-token distribution and KL divergence will result in a model with lower perplexity and improved accuracy compared to models using a single quantizer family.",
  "main_hypothesis_explicit": false,
  "research_question": "How can language models be effectively compressed and deployed on space robots, addressing the specific requirements of a fixed memory budget, storage format, and validated ground behavior?",
  "research_question_explicit": false
}
```

Separate source-component annotations (pending values are not extracted facts):

```json
{
  "components": {
    "method": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "problem": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "result": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    }
  },
  "fixed_extraction_sha256": "ce2f8c414a95ffde97b57a50e748bc3261ecffc6f2da374f54a736e4964cecdd",
  "input_set_id": "lit-2610.29302",
  "status": "pending_actual_source_annotations",
  "target_source_field": "abstract",
  "target_source_text_sha256": "e99103e91c134e511580f9249b24cfa8198169852e0a575582875e405b9d69fc"
}
```

Mechanical attention flags (not judgments): []

Review response:

```review-response
{
  "corrections": null,
  "disagreement_categories": null,
  "extraction_errors": null,
  "extraction_sha256": "ce2f8c414a95ffde97b57a50e748bc3261ecffc6f2da374f54a736e4964cecdd",
  "input_set_id": "lit-2610.29302",
  "main_hypothesis_explicitness_accurate": null,
  "main_hypothesis_extraction_accurate": null,
  "manual_check_completed": false,
  "method_extraction_accurate": null,
  "packet_sha256": "cfa7d0bfe8a7209fb63030fbccf16d74141f43615163fa3a319e26decb9dd5a9",
  "problem_extraction_accurate": null,
  "research_question_explicitness_accurate": null,
  "research_question_extraction_accurate": null,
  "result_extraction_accurate": null,
  "review_guide_sha256": "64df98ff7ca39d7c2afb26940f795d33811dafce5ce5eac38adb43fdf2e43953",
  "reviewed_at_utc": null,
  "reviewer_id": null,
  "reviewer_notes": null,
  "reviewer_slot": 2,
  "source_component_binding_instruction": "Bind completed attributed sidecar digest before final source-component judgments.",
  "source_component_sidecar_sha256": null,
  "source_quotes_and_locations": null,
  "target_source_text_sha256": "e99103e91c134e511580f9249b24cfa8198169852e0a575582875e405b9d69fc",
  "check_evidence": {
    "research_question_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "research_question_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "problem_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "method_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "result_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    }
  }
}
```

## lit-2610.29408 — LiveAct: Towards Real-Time Multi-Agent World Models with Heterogeneous Action Interfaces

Source field: abstract (full preserved evidence):

```text
Interactive video world models predict how an environment evolves under user actions, but most existing systems assume one controlled agent and one task-specific action interface. We study multi-agent video world modeling, where one model generates a joint visual future for multiple controlled agents while interpreting heterogeneous controls ranging from binary game buttons to continuous robot commands. This task presents two complementary challenges. First, every agent-indexed action stream must control its intended visual entity independently. Second, the model must adapt the meaning of each control variable across different tasks, where the same tensor dimension may denote an attack, steering command, or robot command. We introduce LiveAct, centered on a Heterogeneous Action Interface (HAI) whose two components mirror this decomposition. To support independent control, Agent-Aware Spatial Modulation uses language-driven spatial gates and agent-specific attention to bind each action stream to its intended visual agent. To accommodate heterogeneous controls, Schema-Guided Action Adaptation describes each control variable in language and modulates its semantic token with the synchronized numerical value. We further transfer the complete interface to a blockwise causal generator through teacher forcing and rollout-aware distribution matching, enabling efficient streaming generation while retaining agent-specific control and action semantics. We instantiate the formulation on six multi-agent sources spanning games and multi-robot manipulation, and evaluate visual quality, action following, agent attribution, and latency. Across games and robot manipulation, LiveAct reaches 0.898 and 0.942 agent-attribution accuracy without agent locations or identity crops, and the causal generator attains 17.70 FPS at $512\times 448$.
```

Saved model extraction (not a human review):

```json
{
  "main_hypothesis": null,
  "main_hypothesis_explicit": false,
  "research_question": "How can a model be developed to generate a joint visual future for multiple controlled agents while interpreting heterogeneous controls ranging from binary game buttons to continuous robot commands?",
  "research_question_explicit": false
}
```

Separate source-component annotations (pending values are not extracted facts):

```json
{
  "components": {
    "method": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "problem": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "result": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    }
  },
  "fixed_extraction_sha256": "7680134ffabf7d60b18461a5141b8f806b986f4459475e6dd45a4c5217f3c6df",
  "input_set_id": "lit-2610.29408",
  "status": "pending_actual_source_annotations",
  "target_source_field": "abstract",
  "target_source_text_sha256": "0cca218b5ee77468852f8af9916c3d4574d874498e8bcca7bf823a74ee5bf1fe"
}
```

Mechanical attention flags (not judgments): []

Review response:

```review-response
{
  "corrections": null,
  "disagreement_categories": null,
  "extraction_errors": null,
  "extraction_sha256": "7680134ffabf7d60b18461a5141b8f806b986f4459475e6dd45a4c5217f3c6df",
  "input_set_id": "lit-2610.29408",
  "main_hypothesis_explicitness_accurate": null,
  "main_hypothesis_extraction_accurate": null,
  "manual_check_completed": false,
  "method_extraction_accurate": null,
  "packet_sha256": "809c51f8a20ce5be8c3abc8bb230cc9074965a6e0a6f6d311fcc22a71a7990f2",
  "problem_extraction_accurate": null,
  "research_question_explicitness_accurate": null,
  "research_question_extraction_accurate": null,
  "result_extraction_accurate": null,
  "review_guide_sha256": "64df98ff7ca39d7c2afb26940f795d33811dafce5ce5eac38adb43fdf2e43953",
  "reviewed_at_utc": null,
  "reviewer_id": null,
  "reviewer_notes": null,
  "reviewer_slot": 2,
  "source_component_binding_instruction": "Bind completed attributed sidecar digest before final source-component judgments.",
  "source_component_sidecar_sha256": null,
  "source_quotes_and_locations": null,
  "target_source_text_sha256": "0cca218b5ee77468852f8af9916c3d4574d874498e8bcca7bf823a74ee5bf1fe",
  "check_evidence": {
    "research_question_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "research_question_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "problem_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "method_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "result_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    }
  }
}
```

## lit-2610.29439 — How Far Can Foundation Models Be Distilled for Efficient Jet Tagging?

Source field: abstract (full preserved evidence):

```text
Jet tagging is one of the most important applications of machine learning at the Large Hadron Collider. Recent models build in more physics knowledge or rely on large-scale pretraining, but the experiments place strict limits on their inference cost. Knowledge distillation can transfer their performance to small students that are cheap to run. We ask which properties of a teacher help the student, how small a student can get and how close it can come to the state of the art. On a jet tagging benchmark, we distil six teachers that differ in architecture, symmetry and pretraining, including two foundation models, into five small students. Every teacher improves every student, and the gain depends mainly on the strength of the teacher. We then shrink our two strongest distilled students, Transformer and L-GATr-slim, in width and in depth. With 20 thousand parameters, a distilled L-GATr-slim outperforms every published jet tagger trained from scratch at a fraction of the inference cost of every teacher. Even with two thousand parameters, it matches ParT, a model with a thousand times as many parameters. We also study what the students learn from their teachers. Our benchmark of inference cost shows that students of the same size can differ by almost an order of magnitude in speed. We release the code and the weights of all trained models.
```

Saved model extraction (not a human review):

```json
{
  "main_hypothesis": null,
  "main_hypothesis_explicit": false,
  "research_question": "Which properties of a teacher help the student, how small a student can get, and how close it can come to the state of the art?",
  "research_question_explicit": true
}
```

Separate source-component annotations (pending values are not extracted facts):

```json
{
  "components": {
    "method": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "problem": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "result": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    }
  },
  "fixed_extraction_sha256": "fc97030926d4150e52fc638b37e17ed39a92122d5e073169feaf414929dd5751",
  "input_set_id": "lit-2610.29439",
  "status": "pending_actual_source_annotations",
  "target_source_field": "abstract",
  "target_source_text_sha256": "c1706ecf9427c7d6474c82b9b4e9a41435344cc9592d01891bbd6ce203eb911a"
}
```

Mechanical attention flags (not judgments): ["research_question: explicit=true but no literal span; paraphrase/explicitness requires review"]

Review response:

```review-response
{
  "corrections": null,
  "disagreement_categories": null,
  "extraction_errors": null,
  "extraction_sha256": "fc97030926d4150e52fc638b37e17ed39a92122d5e073169feaf414929dd5751",
  "input_set_id": "lit-2610.29439",
  "main_hypothesis_explicitness_accurate": null,
  "main_hypothesis_extraction_accurate": null,
  "manual_check_completed": false,
  "method_extraction_accurate": null,
  "packet_sha256": "6e1167885c20d546f15ad548b38065d3652585876da25c509ee8b6b6d53b38cb",
  "problem_extraction_accurate": null,
  "research_question_explicitness_accurate": null,
  "research_question_extraction_accurate": null,
  "result_extraction_accurate": null,
  "review_guide_sha256": "64df98ff7ca39d7c2afb26940f795d33811dafce5ce5eac38adb43fdf2e43953",
  "reviewed_at_utc": null,
  "reviewer_id": null,
  "reviewer_notes": null,
  "reviewer_slot": 2,
  "source_component_binding_instruction": "Bind completed attributed sidecar digest before final source-component judgments.",
  "source_component_sidecar_sha256": null,
  "source_quotes_and_locations": null,
  "target_source_text_sha256": "c1706ecf9427c7d6474c82b9b4e9a41435344cc9592d01891bbd6ce203eb911a",
  "check_evidence": {
    "research_question_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "research_question_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "problem_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "method_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "result_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    }
  }
}
```

## lit-2610.29922 — Unintended Side Effects of Value Training in LLMs

Source field: abstract (full preserved evidence):

```text
As LLMs are increasingly deployed in value-sensitive contexts, aligning them with human values has emerged as a post-training objective in NLP, aimed at instilling additional values and guiding model behaviour. However, current evaluations remain narrow. Because values are interconnected, it is unclear how fine-tuning for specific values alters unrelated capabilities and behaviours. In this work, we adapt four instruction-tuned LLMs across individual Hofstede's value dimensions and evaluate them on both cross-value transfer and broader behaviours. We find that value-specific training produces unintended side effects on untrained values, risk preferences, social cognition, and safety traits. Consequently, we suggest that value alignment after post-training should incorporate broader behavioral evaluations, and we highlight the need to investigate where additional value training might best fit into the pipeline.
```

Saved model extraction (not a human review):

```json
{
  "main_hypothesis": "Value-specific training produces unintended side effects on untrained values, risk preferences, social cognition, and safety traits.",
  "main_hypothesis_explicit": true,
  "research_question": "How does fine-tuning LLMs for specific values alter unrelated capabilities and behaviors, given that values are interconnected?",
  "research_question_explicit": true
}
```

Separate source-component annotations (pending values are not extracted facts):

```json
{
  "components": {
    "method": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "problem": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "result": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    }
  },
  "fixed_extraction_sha256": "592cf3b6d212d3f7d9b4ff11003c8ea9d21ece96a4c1fda19a9c402ca4e400b5",
  "input_set_id": "lit-2610.29922",
  "status": "pending_actual_source_annotations",
  "target_source_field": "abstract",
  "target_source_text_sha256": "9c28b532fa57bc21bbf1e150ba39bb14a679423114948d2abfcf8d79e1756914"
}
```

Mechanical attention flags (not judgments): ["research_question: explicit=true but no literal span; paraphrase/explicitness requires review", "main_hypothesis: explicit=true but no literal span; paraphrase/explicitness requires review"]

Review response:

```review-response
{
  "corrections": null,
  "disagreement_categories": null,
  "extraction_errors": null,
  "extraction_sha256": "592cf3b6d212d3f7d9b4ff11003c8ea9d21ece96a4c1fda19a9c402ca4e400b5",
  "input_set_id": "lit-2610.29922",
  "main_hypothesis_explicitness_accurate": null,
  "main_hypothesis_extraction_accurate": null,
  "manual_check_completed": false,
  "method_extraction_accurate": null,
  "packet_sha256": "906d30209aa4e35b4188540c1be5cc5ebe91cda703472f3b00a18bbb44534c3a",
  "problem_extraction_accurate": null,
  "research_question_explicitness_accurate": null,
  "research_question_extraction_accurate": null,
  "result_extraction_accurate": null,
  "review_guide_sha256": "64df98ff7ca39d7c2afb26940f795d33811dafce5ce5eac38adb43fdf2e43953",
  "reviewed_at_utc": null,
  "reviewer_id": null,
  "reviewer_notes": null,
  "reviewer_slot": 2,
  "source_component_binding_instruction": "Bind completed attributed sidecar digest before final source-component judgments.",
  "source_component_sidecar_sha256": null,
  "source_quotes_and_locations": null,
  "target_source_text_sha256": "9c28b532fa57bc21bbf1e150ba39bb14a679423114948d2abfcf8d79e1756914",
  "check_evidence": {
    "research_question_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "research_question_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "problem_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "method_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "result_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    }
  }
}
```

## lit-2610.28500 — BitMTP: When Multi-Token Prediction Meets Low-Bit Large Language Models

Source field: abstract (full preserved evidence):

```text
For efficient deployment of large language models (LLMs), methods of ultra-low-bit backbones reduce weight storage, memory traffic, and linear-layer execution cost, while multi-token prediction (MTP) methods reduce sequential decoding steps by predicting multiple future tokens in parallel. Although complementary, the direct combination of these methods cannot accelerate decoding at comparable quality: masked drafting lacks intermediate token input supplied in next-token training, while wider computation and causal key-value (KV) updates can offset the savings from fewer steps. To address these challenges, we propose BitMTP, an algorithm-system co-design framework for efficient MTP on ultra-low-bit LLM backbones. A joint next-token prediction and MTP objective equips a single model with both autoregressive (AR) generation and block-causal drafting. Confidence-only decoding, speculative-only decoding, and hybrid decoding provide different quality-throughput operating points without using separate draft and verifier models. Accepted-prefix alignment keeps the committed prefix, materialized causal KV boundary, and CUDA Graph replay state consistent for continued generation. BitMTP uses this contract to select width-specialized low-bit execution and reuse captured graphs over shared KV storage. On NVIDIA H20, BitMTP with hybrid decoding achieves five-task mean speedups of 2.2x on BitNet b1.58-2B and 2.1-2.4x on 1.7B-4B Bonsai models at comparable task quality. On RTX 3090 and Jetson Orin, it further achieves up to 2.0x in five-task mean throughput and 3.3x on MBPP+, respectively. These results demonstrate that BitMTP accelerates ultra-low-bit LLM generation across backbones, model sizes, and GPU types. The source code is released at https://github.com/PolyU-VCLab/BitMTP
```

Saved model extraction (not a human review):

```json
{
  "main_hypothesis": "A joint next-token prediction and MTP objective, combined with confidence-only, speculative-only, and hybrid decoding, and accepted-prefix alignment, can accelerate ultra-low-bit LLM generation across backbones, model sizes, and GPU types.",
  "main_hypothesis_explicit": false,
  "research_question": "How can the complementary methods of ultra-low-bit backbones and multi-token prediction (MTP) be effectively combined to accelerate decoding of large language models without sacrificing quality?",
  "research_question_explicit": false
}
```

Separate source-component annotations (pending values are not extracted facts):

```json
{
  "components": {
    "method": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "problem": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "result": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    }
  },
  "fixed_extraction_sha256": "4d0730d0b1fee9950cc576c7ac520ebe1f1ae7e30cd211f76626b62a1fad820a",
  "input_set_id": "lit-2610.28500",
  "status": "pending_actual_source_annotations",
  "target_source_field": "abstract",
  "target_source_text_sha256": "ec3112a9dc6640ecb74fda3e34ba94db54afcf8eadbc9c237d2943ae2aef4c03"
}
```

Mechanical attention flags (not judgments): []

Review response:

```review-response
{
  "corrections": null,
  "disagreement_categories": null,
  "extraction_errors": null,
  "extraction_sha256": "4d0730d0b1fee9950cc576c7ac520ebe1f1ae7e30cd211f76626b62a1fad820a",
  "input_set_id": "lit-2610.28500",
  "main_hypothesis_explicitness_accurate": null,
  "main_hypothesis_extraction_accurate": null,
  "manual_check_completed": false,
  "method_extraction_accurate": null,
  "packet_sha256": "9e13635883cb5f2ae2a86978adcd3829a4a20776d1fc0154090766309c9364ba",
  "problem_extraction_accurate": null,
  "research_question_explicitness_accurate": null,
  "research_question_extraction_accurate": null,
  "result_extraction_accurate": null,
  "review_guide_sha256": "64df98ff7ca39d7c2afb26940f795d33811dafce5ce5eac38adb43fdf2e43953",
  "reviewed_at_utc": null,
  "reviewer_id": null,
  "reviewer_notes": null,
  "reviewer_slot": 2,
  "source_component_binding_instruction": "Bind completed attributed sidecar digest before final source-component judgments.",
  "source_component_sidecar_sha256": null,
  "source_quotes_and_locations": null,
  "target_source_text_sha256": "ec3112a9dc6640ecb74fda3e34ba94db54afcf8eadbc9c237d2943ae2aef4c03",
  "check_evidence": {
    "research_question_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "research_question_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "problem_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "method_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "result_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    }
  }
}
```

## lit-2610.28711 — Qwen-Audio-3.1-ASR Technical Report

Source field: abstract (full preserved evidence):

```text
We present Qwen-Audio-3.1-ASR, a family of audio-language models that builds upon its predecesor Qwen-Audio-3.0-ASR with improved speech recognition and expanded capabilities in speaker-diarized transcription and general audio understanding. The family retains support for 30 languages and 16 Chinese dialects, together with instruction-controlled capabilities including historical-context conditioning, hierarchical hotword customization, and native transcription polishing. Speaker-diarized ASR produces structured outputs containing speaker labels, timestamps, and recognized text, maintaining consistent speaker labels across turns and the representation of overlapping speech. The general audio understanding capabilities cover audio-, speech-, and music-captioning, temporal grounding and sound event detection, as well as audio question answering and multiple-choice reasoning. These tasks broaden the application scope from recognizing spoken words to interpreting speakers, acoustic events, and their temporal relations. To accommodate different deployment requirements, the family includes variants for asynchronous file transcription, low-latency streaming, interactive voice input, and non-streaming recognition, with speaker-diarized transcription and general audio understanding available in certain variants. Evaluations span conventional ASR, multilingual and dialectal speech, speaker-diarized transcription, and general audio understanding, demonstrating the capabilities of the Qwen-Audio-3.1-ASR family across transcription and broader audio analysis tasks.
```

Saved model extraction (not a human review):

```json
{
  "main_hypothesis": null,
  "main_hypothesis_explicit": false,
  "research_question": "How can audio-language models be improved to enhance speech recognition, speaker-diarized transcription, and general audio understanding?",
  "research_question_explicit": false
}
```

Separate source-component annotations (pending values are not extracted facts):

```json
{
  "components": {
    "method": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "problem": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "result": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    }
  },
  "fixed_extraction_sha256": "3c69014a1be611fb99bae2d44ed29aab606e28c09d14c42fe55c0a4e05e647b4",
  "input_set_id": "lit-2610.28711",
  "status": "pending_actual_source_annotations",
  "target_source_field": "abstract",
  "target_source_text_sha256": "6ea2f94febf758cf788ff1e511c38d0e5710de3778baff2092156951928a1ec7"
}
```

Mechanical attention flags (not judgments): []

Review response:

```review-response
{
  "corrections": null,
  "disagreement_categories": null,
  "extraction_errors": null,
  "extraction_sha256": "3c69014a1be611fb99bae2d44ed29aab606e28c09d14c42fe55c0a4e05e647b4",
  "input_set_id": "lit-2610.28711",
  "main_hypothesis_explicitness_accurate": null,
  "main_hypothesis_extraction_accurate": null,
  "manual_check_completed": false,
  "method_extraction_accurate": null,
  "packet_sha256": "062a16ffbf0e431bc1b0b2cef902f5ccdb547ef233b10809147bb70565c42bb5",
  "problem_extraction_accurate": null,
  "research_question_explicitness_accurate": null,
  "research_question_extraction_accurate": null,
  "result_extraction_accurate": null,
  "review_guide_sha256": "64df98ff7ca39d7c2afb26940f795d33811dafce5ce5eac38adb43fdf2e43953",
  "reviewed_at_utc": null,
  "reviewer_id": null,
  "reviewer_notes": null,
  "reviewer_slot": 2,
  "source_component_binding_instruction": "Bind completed attributed sidecar digest before final source-component judgments.",
  "source_component_sidecar_sha256": null,
  "source_quotes_and_locations": null,
  "target_source_text_sha256": "6ea2f94febf758cf788ff1e511c38d0e5710de3778baff2092156951928a1ec7",
  "check_evidence": {
    "research_question_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "research_question_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "problem_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "method_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "result_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    }
  }
}
```

## lit-2610.29110 — GRAM: Group-wise Rank-Aware Model Merging via Subspace Alignment

Source field: abstract (full preserved evidence):

```text
Merging different models into a single model is highly desirable for multi-task deployment, particularly in regulated domains like healthcare. In such settings, models are often locally fine-tuned due to strict data privacy policies, necessitating that aggregation operates exclusively on the fine-tuned weights. Existing methods apply a uniform merge across all tasks, ignoring the geometric relationships among their learned subspaces. When task updates occupy misaligned subspaces, projecting them onto a shared low-rank basis discards task-relevant directions, a failure mode named \emph{subspace interference}. Through this study, we show that the per-task projection error of a merged model is governed by the principal-angle alignment between each task and the shared subspace, so that grouping geometrically compatible tasks provably reduces this error within each group. Motivated by this observation, we propose \textbf{Group-wise Rank-Aware Model Merging (GRAM)}, which uses the principal-angle geometry of task vectors to decide which tasks should be merged together and then performs a standard SVD-based merge within each coalition; the pipeline requires only the fine-tuned weights at merge time. With only one additional model ($\nK{=}2$), GRAM significantly mitigates subspace interference and consistently outperforms prior merging methods across language understanding (GLUE with Flan-T5), 8-task CLIP vision, and medical instruction tuning (Qwen2-7B-Instruct with four English/Chinese medical LoRAs).
```

Saved model extraction (not a human review):

```json
{
  "main_hypothesis": "Grouping geometrically compatible tasks provably reduces the per-task projection error of a merged model.",
  "main_hypothesis_explicit": true,
  "research_question": "How can merging different models for multi-task deployment be improved, particularly when models are locally fine-tuned due to data privacy policies and existing methods apply a uniform merge that ignores geometric relationships among learned subspaces?",
  "research_question_explicit": false
}
```

Separate source-component annotations (pending values are not extracted facts):

```json
{
  "components": {
    "method": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "problem": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "result": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    }
  },
  "fixed_extraction_sha256": "ad5b5f2dbbc388c38bda8ad4bd9da36b257d5df39272de2bec82b496401aee8d",
  "input_set_id": "lit-2610.29110",
  "status": "pending_actual_source_annotations",
  "target_source_field": "abstract",
  "target_source_text_sha256": "6829ad1140bb52365ae479c4a4251582d37d489b586f1dbd6c360d8621c09eb1"
}
```

Mechanical attention flags (not judgments): ["main_hypothesis: explicit=true but no literal span; paraphrase/explicitness requires review"]

Review response:

```review-response
{
  "corrections": null,
  "disagreement_categories": null,
  "extraction_errors": null,
  "extraction_sha256": "ad5b5f2dbbc388c38bda8ad4bd9da36b257d5df39272de2bec82b496401aee8d",
  "input_set_id": "lit-2610.29110",
  "main_hypothesis_explicitness_accurate": null,
  "main_hypothesis_extraction_accurate": null,
  "manual_check_completed": false,
  "method_extraction_accurate": null,
  "packet_sha256": "c4018abede74da14d248ef7130dd696767fa42f95a0adbf1fa399361c6df3804",
  "problem_extraction_accurate": null,
  "research_question_explicitness_accurate": null,
  "research_question_extraction_accurate": null,
  "result_extraction_accurate": null,
  "review_guide_sha256": "64df98ff7ca39d7c2afb26940f795d33811dafce5ce5eac38adb43fdf2e43953",
  "reviewed_at_utc": null,
  "reviewer_id": null,
  "reviewer_notes": null,
  "reviewer_slot": 2,
  "source_component_binding_instruction": "Bind completed attributed sidecar digest before final source-component judgments.",
  "source_component_sidecar_sha256": null,
  "source_quotes_and_locations": null,
  "target_source_text_sha256": "6829ad1140bb52365ae479c4a4251582d37d489b586f1dbd6c360d8621c09eb1",
  "check_evidence": {
    "research_question_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "research_question_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "problem_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "method_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "result_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    }
  }
}
```

## lit-2610.29517 — AutoPhyX: Automatic Text-Condition Physics Property Generation

Source field: abstract (full preserved evidence):

```text
High-fidelity 4D physical simulation requires accurate physical parameter assignments that align with diverse material properties. Previous methods struggle with critical bottlenecks: they either rely on computationally intensive per-scene optimization or predict parameters from purely visual inputs. The latter suffers from inherent ambiguity, e.g., the inability to distinguish the stiffness of rubber from its appearance alone. To bridge this gap, we propose AutoPhyX, a text-conditioned framework for predicting spatially-varying physical properties. Since training robust feed-forward models requires fine-grained supervision, we first introduce a novel part-controllable data generation pipeline that decomposes complex 3D assets into semantically distinct components and pairs them with physically plausible, diverse parameters and corresponding text descriptions. Leveraging this dataset, AutoPhyX employs a cross-modal modulation mechanism where text features dynamically modulate visual features for precise physical grounding. By formulating property prediction within a voxel field, AutoPhyX ensures compatibility with diverse 3D representations, including meshes, point clouds, Gaussian Splatting, and NeRF. Experiments demonstrate that our method enables physically plausible, text-driven parameter assignment in a single forward pass. It achieves high accuracy and robust generalization to in-the-wild objects, paving the way for future physics-intensive embodied and robotic applications.
```

Saved model extraction (not a human review):

```json
{
  "main_hypothesis": "A text-conditioned framework (AutoPhyX) utilizing a novel part-controllable data generation pipeline and a cross-modal modulation mechanism can predict spatially-varying physical properties, enabling physically plausible, text-driven parameter assignment with high accuracy and robust generalization.",
  "main_hypothesis_explicit": false,
  "research_question": "How can physical parameters be predicted accurately and efficiently to enable high-fidelity 4D physical simulation, addressing the limitations of existing methods that rely on computationally intensive optimization or ambiguous visual inputs?",
  "research_question_explicit": false
}
```

Separate source-component annotations (pending values are not extracted facts):

```json
{
  "components": {
    "method": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "problem": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "result": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    }
  },
  "fixed_extraction_sha256": "91cc03a63ce58677026d0f944c6133fb1421993ead9bde53cb09e1db13955229",
  "input_set_id": "lit-2610.29517",
  "status": "pending_actual_source_annotations",
  "target_source_field": "abstract",
  "target_source_text_sha256": "592cedd23b45f7f7451c08c99c716484eae8d9f3a21ee754b87011ea90581712"
}
```

Mechanical attention flags (not judgments): []

Review response:

```review-response
{
  "corrections": null,
  "disagreement_categories": null,
  "extraction_errors": null,
  "extraction_sha256": "91cc03a63ce58677026d0f944c6133fb1421993ead9bde53cb09e1db13955229",
  "input_set_id": "lit-2610.29517",
  "main_hypothesis_explicitness_accurate": null,
  "main_hypothesis_extraction_accurate": null,
  "manual_check_completed": false,
  "method_extraction_accurate": null,
  "packet_sha256": "fa42c64816bb66950a569fb51d443ab8cb9f8910c19155c0440ca3d111480ef1",
  "problem_extraction_accurate": null,
  "research_question_explicitness_accurate": null,
  "research_question_extraction_accurate": null,
  "result_extraction_accurate": null,
  "review_guide_sha256": "64df98ff7ca39d7c2afb26940f795d33811dafce5ce5eac38adb43fdf2e43953",
  "reviewed_at_utc": null,
  "reviewer_id": null,
  "reviewer_notes": null,
  "reviewer_slot": 2,
  "source_component_binding_instruction": "Bind completed attributed sidecar digest before final source-component judgments.",
  "source_component_sidecar_sha256": null,
  "source_quotes_and_locations": null,
  "target_source_text_sha256": "592cedd23b45f7f7451c08c99c716484eae8d9f3a21ee754b87011ea90581712",
  "check_evidence": {
    "research_question_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "research_question_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "problem_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "method_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "result_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    }
  }
}
```

## lit-2610.28974 — TEMPL: A Resource-Efficient and Transparent Model-Free Framework for Pseudo-Label Generation in Material CT Scans

Source field: abstract (full preserved evidence):

```text
The scarcity of large annotated datasets limits deep learning (DL) segmentation in material CT analysis. DL-based pseudo-labeling can help, but it is often computationally expensive and hard to interpret. We introduce a multi-stage, model-free framework that generates pseudo-labels directly from grayscale CT scans. It combines thresholding, morphological dilation, and a custom breadth-first search region-growing algorithm to produce polygonal annotations without pre-trained weights, labeled data, or a GPU. We compare it against the zero-shot Segment Anything Model (SAM), a fully supervised 3D U-Net, and classical baselines. On a dendrite dataset with ground truth, our method reaches 63.19% IoU versus 10.74% for zero-shot SAM, with four times the instance recall at 0.5 IoU (33.3% versus 8.3%). The supervised 3D U-Net serves as a reference ceiling that requires expert labels. On a silica sand specimen, YOLO models trained on our labels performed comparably to models trained on SAM labels in a qualitative comparison. Across 1,053 extracted grains, the median equivalent diameter was 163.8 micrometers, near the specimen's known 106 to 150 micrometers sieve range, compared with 219.5 micrometers for SAM, whose labels merge adjacent particles and add spurious detections. A sensitivity analysis shows a stable operating range for the key threshold and a sharp, predictable failure point linked to phase contrast. Our method needs 15s per image on a standard CPU versus 28s for SAM on a GPU. These results support our transparent approach as a tool for annotation bootstrapping and microstructural quantification in resource-limited settings.
```

Saved model extraction (not a human review):

```json
{
  "main_hypothesis": "The proposed multi-stage, model-free framework will generate pseudo-labels that perform comparably to or better than existing methods like zero-shot SAM and supervised 3D U-Net, particularly in resource-limited settings.",
  "main_hypothesis_explicit": false,
  "research_question": "Can a multi-stage, model-free framework generate pseudo-labels directly from grayscale CT scans to address the scarcity of large annotated datasets for deep learning segmentation in material CT analysis?",
  "research_question_explicit": false
}
```

Separate source-component annotations (pending values are not extracted facts):

```json
{
  "components": {
    "method": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "problem": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "result": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    }
  },
  "fixed_extraction_sha256": "c3eff8f4b777296f1beec300f6bbe26d1ba6374a94573f9ee9720ced8e8aecd4",
  "input_set_id": "lit-2610.28974",
  "status": "pending_actual_source_annotations",
  "target_source_field": "abstract",
  "target_source_text_sha256": "cef8b92a8767f163d38ead7331acb9befb5ab6d0fe2b252c49c5da9217b9a3e4"
}
```

Mechanical attention flags (not judgments): []

Review response:

```review-response
{
  "corrections": null,
  "disagreement_categories": null,
  "extraction_errors": null,
  "extraction_sha256": "c3eff8f4b777296f1beec300f6bbe26d1ba6374a94573f9ee9720ced8e8aecd4",
  "input_set_id": "lit-2610.28974",
  "main_hypothesis_explicitness_accurate": null,
  "main_hypothesis_extraction_accurate": null,
  "manual_check_completed": false,
  "method_extraction_accurate": null,
  "packet_sha256": "f32cdee44f583b8d0cb543badf998dcb9f07dd7758ea27c350b68ab12929e71d",
  "problem_extraction_accurate": null,
  "research_question_explicitness_accurate": null,
  "research_question_extraction_accurate": null,
  "result_extraction_accurate": null,
  "review_guide_sha256": "64df98ff7ca39d7c2afb26940f795d33811dafce5ce5eac38adb43fdf2e43953",
  "reviewed_at_utc": null,
  "reviewer_id": null,
  "reviewer_notes": null,
  "reviewer_slot": 2,
  "source_component_binding_instruction": "Bind completed attributed sidecar digest before final source-component judgments.",
  "source_component_sidecar_sha256": null,
  "source_quotes_and_locations": null,
  "target_source_text_sha256": "cef8b92a8767f163d38ead7331acb9befb5ab6d0fe2b252c49c5da9217b9a3e4",
  "check_evidence": {
    "research_question_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "research_question_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "problem_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "method_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "result_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    }
  }
}
```

## lit-2601.00086 — RIMRULE: Improving Tool-Using Language Agents via MDL-Guided Rule Learning

Source field: abstract (full preserved evidence):

```text
Large language models (LLMs) often struggle to use tools reliably in domain-specific settings, where APIs may be idiosyncratic, under-documented, or tailored to private workflows. This highlights the need for effective adaptation to task-specific tools. We propose RIMRULE, a neuro-symbolic approach for LLM adaptation based on dynamic rule injection. Compact, interpretable rules are distilled from failure traces and injected into the prompt during inference to improve task performance. These rules are proposed by the LLM itself and consolidated using a Minimum Description Length (MDL) objective that favors generality and conciseness. Each rule is stored in both natural language and a structured symbolic form, supporting efficient retrieval at inference time. Experiments on tool-use benchmarks show that this approach improves accuracy on both seen and unseen tools without modifying LLM weights. It outperforms prompting-based adaptation methods and complements finetuning. Moreover, rules learned from one LLM can be reused to improve others, including long reasoning LLMs, highlighting the portability of symbolic knowledge across architectures.
```

Saved model extraction (not a human review):

```json
{
  "main_hypothesis": "A neuro-symbolic approach, RIMRULE, based on dynamic rule injection, can improve LLM task performance by distilling compact, interpretable rules from failure traces and injecting them into the prompt during inference.",
  "main_hypothesis_explicit": false,
  "research_question": "How can large language models (LLMs) be effectively adapted to use tools reliably in domain-specific settings, where APIs are idiosyncratic, under-documented, or tailored to private workflows?",
  "research_question_explicit": false
}
```

Separate source-component annotations (pending values are not extracted facts):

```json
{
  "components": {
    "method": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "problem": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    },
    "result": {
      "annotated_at_utc": null,
      "annotator_id": null,
      "character_span": null,
      "source_quote": null,
      "text": null
    }
  },
  "fixed_extraction_sha256": "b2c9fc4323f0e2bcaee4c4ffbca923a513e17f995ce28367fbf7bd881a65b116",
  "input_set_id": "lit-2601.00086",
  "status": "pending_actual_source_annotations",
  "target_source_field": "abstract",
  "target_source_text_sha256": "5cd883a06ef408c558161a4bae8fc440114f478db22f26dc041757d657b9e4d0"
}
```

Mechanical attention flags (not judgments): []

Review response:

```review-response
{
  "corrections": null,
  "disagreement_categories": null,
  "extraction_errors": null,
  "extraction_sha256": "b2c9fc4323f0e2bcaee4c4ffbca923a513e17f995ce28367fbf7bd881a65b116",
  "input_set_id": "lit-2601.00086",
  "main_hypothesis_explicitness_accurate": null,
  "main_hypothesis_extraction_accurate": null,
  "manual_check_completed": false,
  "method_extraction_accurate": null,
  "packet_sha256": "03f08e011d850d0cb4b1109d546d8313a97f0286c2e1eb8f5823806401416204",
  "problem_extraction_accurate": null,
  "research_question_explicitness_accurate": null,
  "research_question_extraction_accurate": null,
  "result_extraction_accurate": null,
  "review_guide_sha256": "64df98ff7ca39d7c2afb26940f795d33811dafce5ce5eac38adb43fdf2e43953",
  "reviewed_at_utc": null,
  "reviewer_id": null,
  "reviewer_notes": null,
  "reviewer_slot": 2,
  "source_component_binding_instruction": "Bind completed attributed sidecar digest before final source-component judgments.",
  "source_component_sidecar_sha256": null,
  "source_quotes_and_locations": null,
  "target_source_text_sha256": "5cd883a06ef408c558161a4bae8fc440114f478db22f26dc041757d657b9e4d0",
  "check_evidence": {
    "research_question_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "research_question_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "main_hypothesis_explicitness_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "problem_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "method_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    },
    "result_extraction_accurate": {
      "rationale": null,
      "source_quote_or_location": null
    }
  }
}
```
