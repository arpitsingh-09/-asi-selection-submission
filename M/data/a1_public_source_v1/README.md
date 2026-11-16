---
license: mit
task_categories:
  - text-generation
  - question-answering
language:
  - en
size_categories:
  - 1K<n<10K
tags:
  - research-question-generation
  - scientific-reasoning
  - llm-evaluation
  - benchmark
  - arxiv
  - novelty
  - literature-review
pretty_name: RQ-Bench
configs:
  - config_name: questions
    data_files:
      - split: test
        path: rq_dataset.jsonl
---

# RQ-Bench: A Benchmark for Grounded Research Question Generation

**RQ-Bench** evaluates whether language models can read background literature and propose the same kinds of research questions that a human author actually went on to investigate.

Each example pairs a held-out research question (RQ) — distilled from a real arXiv paper (the *target paper*) — with the full text of the prior-work papers that the target paper cites as motivation. A model is shown only the cited references and must predict an RQ that is **specific**, **answerable**, and **grounded** in a gap that those references expose. Predictions are compared against the held-out ground-truth RQ.

- **Questions:** 1,434
- **Target (source) papers:** 746
- **Unique cited reference papers (with full text):** 1,375
- **CS subfields covered:** 13 (cs.RO, cs.CV, cs.CL, cs.LG, cs.AI, cs.SD, cs.IR, cs.CR, cs.IT, cs.SE, cs.DC, cs.NI, cs.HC)
- **Predominantly 2025–2026 target papers** (very low contamination risk for pre-2025 LLMs).

---

## Quick Start

RQ-Bench is **evaluation-only** — there is a single `test` split (no train/val). The held-out questions and their grounding metadata live in `rq_dataset.jsonl` (one question per line); the full text of every cited reference is shipped alongside as one JSON per arXiv id in `cited_papers/`.

```python
from datasets import load_dataset
import json, urllib.request

# 1. Load the held-out research questions + per-RQ "grounded_in_refs" metadata.
ds = load_dataset("declare-lab/rq-bench", split="test")
print(ds[0]["question"])
print([r["arxiv_id"] for r in ds[0]["grounded_in_refs"]])

# 2. Cited papers (full text by section) live alongside the questions
#    in `cited_papers/<arxiv_id>.json`. Load them on demand:
def load_cited(arxiv_id: str) -> dict:
    url = f"https://huggingface.co/datasets/declare-lab/rq-bench/resolve/main/cited_papers/{arxiv_id}.json"
    return json.loads(urllib.request.urlopen(url).read())

cited = load_cited(ds[0]["grounded_in_refs"][0]["arxiv_id"])
print(list(cited.keys()))  # arxiv_id, title, abstract, INTRODUCTION, ...
```

---

## Why this benchmark?

LLMs are increasingly being considered for roles beyond assistance in the scientific knowledge-creation process. Progress has been made on evaluating LLMs at **idea generation** given a topic, question, or background literature — but those evaluations all assess only the *final* idea. The capability that precedes idea generation in real research — **identifying the right research question** — is not directly evaluated by any existing benchmark.

RQ-Bench fills that gap. Each item asks a model to produce research questions from background literature, anchored to human-authored RQs distilled from recent arXiv papers.

The dataset was built with two properties in mind that make this evaluation meaningful:

1. **Author-grounded.** Each gold RQ is distilled from a real, recently published arXiv paper's own framing (problem statement, main idea, contributions) — not invented post-hoc.
2. **Reference-anchored.** Each RQ ships with the specific cited papers that motivated the gap, the verbatim quotes in the target paper that name the gap, and a description of how the target paper closes it — so models are scored against grounded evidence, not free-form taste.

In the original study using this benchmark, three findings emerged: (i) LLMs generally do not reproduce human-anchored RQs, (ii) they do not appear to produce more novel RQs than humans, and (iii) LLM judges self-contradict across evaluation settings, raising concerns about their reliability as judges for this task.

---

## Dataset Structure

The dataset has two parts:

```
rq-bench/
├── README.md
├── rq_dataset.jsonl           # 1,434 lines — one question record per line
└── cited_papers/              # 1,375 cited-reference papers, full text by section
    ├── 1011.0686.json
    ├── 1303.3679.json
    └── ...
```

### `rq_dataset.jsonl`

One JSON object per line. Each line has the following fields:

| Field | Type | Description |
|---|---|---|
| `rq_id` | str | Stable identifier, format `<arxiv_id>_rq<index>` |
| `question` | str | The ground-truth research question (held out from the model) |
| `source_paper` | dict | Metadata for the **target** paper this RQ was distilled from |
| `source_paper.paper_id` | str | Semantic Scholar paper ID |
| `source_paper.arxiv_id` | str | arXiv identifier of the target paper |
| `source_paper.title` | str | Paper title |
| `source_paper.subfield` | str | arXiv CS subfield (e.g. `cs.CV`) |
| `source_paper.novelty_type` | str | `Methodological`, `Application`, or `Combinatorial` |
| `source_paper.main_idea.headline` | str | One-sentence statement of the paper's main idea |
| `source_paper.main_idea.contributions` | list[str] | Bullet contributions as claimed by the authors |
| `source_paper.problem` | str | Problem statement extracted from the paper |
| `source_paper.venue_info` | dict | `venue`, `venue_type`, `venue_id`, `year` |
| `grounded_in_refs` | list[dict] | The cited references that motivate this RQ |
| `grounded_in_refs[].arxiv_id` | str | arXiv id of the cited reference — corresponds to `cited_papers/<arxiv_id>.json` |
| `grounded_in_refs[].gaps` | list[dict] | One or more gaps the cited reference leaves open |
| `grounded_in_refs[].gaps[].limitation` | str | Concrete limitation/weakness of the cited reference |
| `grounded_in_refs[].gaps[].evidence_quote` | str | Verbatim quote from the target paper attesting the gap |
| `grounded_in_refs[].gaps[].evidence_source` | str | Section path in the target paper (e.g. `Introduction`) |
| `grounded_in_refs[].gaps[].target_relation` | str | How the target paper's idea addresses this gap |

### `cited_papers/<arxiv_id>.json`

One file per cited reference. Keys are the paper's section headers, values are the section bodies. The set of section keys varies by paper, but every file has at minimum:

| Field | Type | Description |
|---|---|---|
| `arxiv_id` | str | Matches the file name (e.g. `1011.0686`) |
| `title` | str | Paper title |
| `abstract` | str | Paper abstract |
| `<SECTION_NAME>` | str | Full text of a section (e.g. `INTRODUCTION`, `PRELIMINARIES`, `EXPERIMENTS`, …) |

Example:

```json
{
  "arxiv_id": "1011.0686",
  "title": "A reduction of imitation learning and structured prediction to no-regret online learning",
  "abstract": "Sequential prediction problems such as imitation learning...",
  "INTRODUCTION": "...",
  "PRELIMINARIES": "...",
  "DATASET AGGREGATION": "...",
  "THEORETICAL ANALYSIS": "...",
  "EXPERIMENTS": "...",
  "FUTURE WORK": "..."
}
```

---

## Worked example

A truncated row from `rq_dataset.jsonl` (pretty-printed for readability):

```json
{
  "rq_id": "2501.00732_rq0",
  "question": "How can error feedback and gradient tracking mechanisms be integrated into federated learning to mitigate the prediction performance degradation caused by high-ratio lossy gradient compression?",
  "source_paper": {
    "arxiv_id": "2501.00732",
    "title": "Gradient Compression and Correlation Driven Federated Learning for Wireless Traffic Prediction",
    "subfield": "cs.DC",
    "novelty_type": "Methodological",
    "main_idea": {
      "headline": "A novel federated learning algorithm integrates gradient compression and correlation-driven personalized aggregation...",
      "contributions": ["Introduces gradient sparsification...", "Incorporates error feedback...", "..."]
    },
    "problem": "While federated learning allows edge nodes to collaboratively train wireless traffic prediction models without sharing raw data, it still incurs heavy communication overhead...",
    "venue_info": {"venue": "IEEE TCCN", "year": 2025}
  },
  "grounded_in_refs": [
    {
      "arxiv_id": "1712.01887",
      "gaps": [{
        "limitation": "The lossy nature of gradient sparsification negatively impacts prediction performance...",
        "evidence_quote": "compression negatively influences prediction performance, especially when the compression ratio $\\gamma$ is large",
        "evidence_source": "Our Proposed Method > Local Update on the Client",
        "target_relation": "The target paper incorporates error feedback and gradient tracking techniques to compensate for the information loss..."
      }]
    }
  ]
}
```

At evaluation time, a model is shown the full text of `cited_papers/1712.01887.json` (and any other refs listed under `grounded_in_refs`), and must predict an RQ comparable to the held-out `question`.

---

## Statistics

| | Value |
|---|---|
| Research questions | **1,434** |
| Target (source) papers | **746** |
| Unique cited papers (referenced) | **1,375** |
| Cited-paper JSON files shipped | **1,375** (one per referenced ID) |
| CS subfields | **13** |
| Novelty types | **3** (Methodological / Application / Combinatorial) |

**Questions per subfield** (top): cs.RO 245 · cs.CV 222 · cs.CL 173 · cs.LG 162 · cs.AI 146 · cs.SD 115 · cs.IR 92 · cs.CR 75 · cs.IT 69 · cs.SE 67 · cs.DC 36 · cs.NI 19 · cs.HC 13.

**RQs per target paper:** 1 (229 papers), 2 (361), 3 (141), 4 (15); mean ≈ 1.92.

**Cited refs per RQ:** 1 (752), 2 (439), 3 (164), 4 (61), 5 (12), 6 (4), 7 (2); mean ≈ 1.72.

**Gaps per RQ** (summed across its cited refs): mean ≈ 2.20, max 11. Total gaps in the corpus: **3,151**.

**Question length:** mean 24.7 words, median 24, range 14–50.

**Cited-paper reuse:** the long tail dominates — 925 cited papers are referenced by exactly one RQ; a handful of foundational works (e.g. transformer/diffusion backbones) are referenced by 13–87 RQs.

---

## Intended uses

- **Benchmarking** RQ generation, scientific ideation, and literature-grounded reasoning models.
- **Fine-tuning / preference learning** for scientific assistants — the `(cited_papers, gaps, question)` triples give rich (positive) supervision and the `evidence_quote` / `target_relation` fields enable rationale-style training.
- **Studying citation-grounded gap analysis** — each RQ is anchored to specific quotes in the target paper that justify the gap, useful for evidence-attribution research.

## Out-of-scope uses

- Predicting the target paper's title, full method, or experimental results — the dataset only releases the *question* and the cited-paper context, not the answer.
- Tasks that require text outside the CS subfields listed above.
- Use as a training corpus for *summarization* of arXiv papers — section coverage is uneven by design (it is biased toward the parts of cited papers that matter for gap analysis).

---

## Limitations & known caveats

- **CS only.** All 13 subfields are arXiv CS categories; biomedical / physical-science questions are not represented.
- **Recency-skewed.** ~The target papers are from 2025-26. Older years are underrepresented.
- **Section schemas vary.** `cited_papers/*.json` keys are paper-specific section headers (`INTRODUCTION`, `Method`, `EXPERIMENTS`, …). Code that consumes the corpus should iterate over keys rather than assume a fixed list.
- **Author-distilled, not author-written.** Ground-truth RQs are extracted by an LLM-assisted pipeline from the target paper's own framing, not literally written by the authors as a "research question". They are faithful to the paper's stated motivation but should not be treated as a survey of every possible question the paper raises.
- **Gap text is extracted, not human-curated.** `evidence_quote` and `evidence_source` are taken verbatim from the target paper to keep grounding auditable, but the `limitation` and `target_relation` fields are model-generated paraphrases.

---

## License

Released under the **MIT License**. Section text in `cited_papers/` is excerpted from arXiv preprints owned by their respective authors and is included under the terms of arXiv's permitted re-use for non-commercial research. Please cite the original arXiv papers if you build on a particular cited reference.

## Maintainers

Deep Cognition and Language Research (DeCLaRe) Lab, Nanyang Technological University.
Issues, contributions, and pull requests welcome on the Hugging Face dataset page.

## Citation

```bibtex
@misc{sinhahajari2026limitsllmasjudgescientificnovelty,
      title={On the Limits of LLM-as-Judge for Scientific Novelty Assessment}, 
      author={Soumitra Sinhahajari and Navonil Majumder and Soujanya Poria},
      year={2026},
      eprint={2606.12071},
      archivePrefix={arXiv},
      primaryClass={cs.DL},
      url={https://arxiv.org/abs/2606.12071}, 
}
```