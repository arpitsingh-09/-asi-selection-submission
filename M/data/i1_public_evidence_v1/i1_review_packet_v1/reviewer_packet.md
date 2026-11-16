# I1 independent human review packet

**Purpose:** Judge the source/question relationship, proposed paraphrase and near-miss, and same-topic decoy. These are review questions, not model predictions or labels. Complete the two reviewer sheets independently; do not coordinate.

Packet SHA-256: `ae5d6de6530c3beeb911b6e034585335a297e6ceb3e40e3518983fcf99463e68`

## Decisions required

For each of the two candidates, each of two independent reviewers must provide:

- Reviewer code and UTC review date.
- `YES`, `NO`, or `UNCERTAIN` for question/input relationship validity.
- `YES`, `NO`, or `UNCERTAIN` for paraphrase equivalence.
- `YES`, `NO`, or `UNCERTAIN` for whether the near-miss is genuinely distinct.
- `YES`, `NO`, or `UNCERTAIN` for same-topic decoy validity.
- Source references with source ID, URL, exact locator and supporting quote, plus a rationale.

The existing reviewer CSVs have these answer fields blank. A candidate passes this human-review gate only when the two independent reviewers agree and all decisions are `YES`; disagreement or `UNCERTAIN` remains unresolved.

## Candidate mgen-v1-01

**Original question**

> How do the approaches in TiG-BEV: Multi-view BEV 3D Object Detection via Target Inner-Geometry Learning and TiGDistill-BEV: Multi-view BEV 3D Object Detection via Target Inner-Geometry Learning Distillation differ in their treatment of computer vision?

**Question/input papers** (generator links recorded; relationship not independently validated)

- **TiG-BEV: Multi-view BEV 3D Object Detection via Target Inner-Geometry Learning** — `2212.13979v1`; published `2022-12-28T17:53:43Z`; version updated `2022-12-28T17:53:43Z`; [https://arxiv.org/abs/2212.13979v1](https://arxiv.org/abs/2212.13979v1).
- **TiGDistill-BEV: Multi-view BEV 3D Object Detection via Target Inner-Geometry Learning Distillation** — `2412.20911v1`; published `2024-12-30T12:44:20Z`; version updated `2024-12-30T12:44:20Z`; [https://arxiv.org/abs/2412.20911v1](https://arxiv.org/abs/2412.20911v1).

**Paraphrase proposal** (unreviewed)

> In what ways do TiG-BEV and TiGDistill-BEV differ in how they address computer vision?

**Near-miss proposal** (unreviewed)

> Which of TiG-BEV and TiGDistill-BEV achieves stronger 3D object-detection performance on nuScenes?

**Shuffled-control papers**

- **Cascaded Convolutional Neural Network for Automatic Myocardial Infarction Segmentation from Delayed-Enhancement Cardiac MRI** — `2012.14128v1`; published `2020-12-28T07:41:10Z`; version updated `2020-12-28T07:41:10Z`; [https://arxiv.org/abs/2012.14128v1](https://arxiv.org/abs/2012.14128v1).
- **Cascaded Framework for Automatic Evaluation of Myocardial Infarction from Delayed-Enhancement Cardiac MRI** — `2012.14556v1`; published `2020-12-29T01:35:02Z`; version updated `2020-12-29T01:35:02Z`; [https://arxiv.org/abs/2012.14556v1](https://arxiv.org/abs/2012.14556v1).

**Same-topic decoy question** (category match only; semantic validity unverified)

> How do the approaches in Towards Unsupervised Deep Image Enhancement with Generative Adversarial Network and Unpaired Image Enhancement with Quality-Attention Generative Adversarial Network differ in their treatment of computer vision?

**Decoy papers**

- **Towards Unsupervised Deep Image Enhancement with Generative Adversarial Network** — `2012.15020v1`; published `2020-12-30T03:22:46Z`; version updated `2020-12-30T03:22:46Z`; [https://arxiv.org/abs/2012.15020v1](https://arxiv.org/abs/2012.15020v1).
- **Unpaired Image Enhancement with Quality-Attention Generative Adversarial Network** — `2012.15052v1`; published `2020-12-30T05:57:20Z`; version updated `2020-12-30T05:57:20Z`; [https://arxiv.org/abs/2012.15052v1](https://arxiv.org/abs/2012.15052v1).

**Reviewer response fields** — complete one row for this candidate in the assigned reviewer CSV:

`reviewer_code` · `review_date_utc` · `question_input_relationship_valid` · `paraphrase_equivalent` · `near_miss_distinct` · `same_topic_decoy_valid` · `evidence_references_json` · `rationale`

## Candidate mgen-v1-02

**Original question**

> How do the approaches in Cascaded Convolutional Neural Network for Automatic Myocardial Infarction Segmentation from Delayed-Enhancement Cardiac MRI and Cascaded Framework for Automatic Evaluation of Myocardial Infarction from Delayed-Enhancement Cardiac MRI differ in their treatment of computer vision?

**Question/input papers** (generator links recorded; relationship not independently validated)

- **Cascaded Convolutional Neural Network for Automatic Myocardial Infarction Segmentation from Delayed-Enhancement Cardiac MRI** — `2012.14128v1`; published `2020-12-28T07:41:10Z`; version updated `2020-12-28T07:41:10Z`; [https://arxiv.org/abs/2012.14128v1](https://arxiv.org/abs/2012.14128v1).
- **Cascaded Framework for Automatic Evaluation of Myocardial Infarction from Delayed-Enhancement Cardiac MRI** — `2012.14556v1`; published `2020-12-29T01:35:02Z`; version updated `2020-12-29T01:35:02Z`; [https://arxiv.org/abs/2012.14556v1](https://arxiv.org/abs/2012.14556v1).

**Paraphrase proposal** (unreviewed)

> In what ways do the two cited approaches differ in their computer-vision treatment of myocardial infarction?

**Near-miss proposal** (unreviewed)

> Which method more accurately identifies myocardial infarction in delayed-enhancement cardiac MRI?

**Shuffled-control papers**

- **Towards Unsupervised Deep Image Enhancement with Generative Adversarial Network** — `2012.15020v1`; published `2020-12-30T03:22:46Z`; version updated `2020-12-30T03:22:46Z`; [https://arxiv.org/abs/2012.15020v1](https://arxiv.org/abs/2012.15020v1).
- **Unpaired Image Enhancement with Quality-Attention Generative Adversarial Network** — `2012.15052v1`; published `2020-12-30T05:57:20Z`; version updated `2020-12-30T05:57:20Z`; [https://arxiv.org/abs/2012.15052v1](https://arxiv.org/abs/2012.15052v1).

**Same-topic decoy question** (category match only; semantic validity unverified)

> How do the approaches in TiG-BEV: Multi-view BEV 3D Object Detection via Target Inner-Geometry Learning and TiGDistill-BEV: Multi-view BEV 3D Object Detection via Target Inner-Geometry Learning Distillation differ in their treatment of computer vision?

**Decoy papers**

- **TiG-BEV: Multi-view BEV 3D Object Detection via Target Inner-Geometry Learning** — `2212.13979v1`; published `2022-12-28T17:53:43Z`; version updated `2022-12-28T17:53:43Z`; [https://arxiv.org/abs/2212.13979v1](https://arxiv.org/abs/2212.13979v1).
- **TiGDistill-BEV: Multi-view BEV 3D Object Detection via Target Inner-Geometry Learning Distillation** — `2412.20911v1`; published `2024-12-30T12:44:20Z`; version updated `2024-12-30T12:44:20Z`; [https://arxiv.org/abs/2412.20911v1](https://arxiv.org/abs/2412.20911v1).

**Additional existing decoy proposal:**

> {'evaluation_R': ['2012.14128v1', '2012.14556v1'], 'generated_at': '2026-11-13T14:31:04Z', 'generation_source_pair': [{'paper_id': '2212.13715v1', 'provenance': {'length': 2243, 'line': 406, 'line_sha256': '5578ef3de8e0faf7ad6abb8479e5207189762067a561a356c9ed8e704a3c12e7', 'offset': 731323, 'path': 'E2/data/raw_papers.jsonl'}, 'published': '2022-12-28T06:34:38Z', 'title': 'MyI-Net: Fully Automatic Detection and Quantification of Myocardial Infarction from Cardiovascular MRI Images', 'updated': '2022-12-28T06:34:38Z', 'url': 'https://arxiv.org/abs/2212.13715v1'}, {'paper_id': '2012.14564v1', 'provenance': {'length': 1781, 'line': 100, 'line_sha256': '498ea31e758db5b55b58504716e3ba9a6c32d01d84f06e8816ce51b7ee6d17a5', 'offset': 175774, 'path': 'E2/data/raw_papers.jsonl'}, 'published': '2020-12-29T01:54:09Z', 'title': 'Myocardial Segmentation of Cardiac MRI Sequences with Temporal Consistency for Coronary Artery Disease Diagnosis', 'updated': '2020-12-29T01:54:09Z', 'url': 'https://arxiv.org/abs/2012.14564v1'}], 'question': 'How do the approaches in MyI-Net: Fully Automatic Detection and Quantification of Myocardial Infarction from Cardiovascular MRI Images and Myocardial Segmentation of Cardiac MRI Sequences with Temporal Consistency for Coronary Artery Disease Diagnosis differ in their treatment of computer vision?', 'question_kind': 'generated', 'same_topic_status': 'PENDING_HUMAN_REVIEW', 'template': 'm_generated_question_v1', 'topic_label': 'computer vision', 'topic_rationale': 'Both source papers explicitly address myocardial infarction analysis from MRI; their segmentation/detection outputs differ but the clinical-imaging problem is closely matched.'}

**Reviewer response fields** — complete one row for this candidate in the assigned reviewer CSV:

`reviewer_code` · `review_date_utc` · `question_input_relationship_valid` · `paraphrase_equivalent` · `near_miss_distinct` · `same_topic_decoy_valid` · `evidence_references_json` · `rationale`

## Return files

Complete both separate files without changing `candidate_id`, `question_id`, `reviewer_slot`, or `packet_sha256`:

- `reviewer_1_template.csv` — reviewer slot 1
- `reviewer_2_template.csv` — reviewer slot 2

Then import both sheets:

```sh
python3 -m M.i1_evidence_packet import-reviews \
  --sheet M/data/i1_public_evidence_v1/i1_review_packet_v1/reviewer_1_template.csv \
  --sheet M/data/i1_public_evidence_v1/i1_review_packet_v1/reviewer_2_template.csv \
  --packet M/data/i1_public_evidence_v1/i1_review_packet_v1/packet.json \
  --out M/data/i1_public_evidence_v1/i1_review_packet_v1/completed_reviews.jsonl
```

Human review alone will not authorize I1 scoring: the evidence manifest separately requires fitted Q heads with frozen normalization, verified original input relationships, eligible controls and a prospective cohort/model lock.
