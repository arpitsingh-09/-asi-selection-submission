# E1 Corrected Development Evaluation

## Protocol and limitations

- Dataset: `E1/contrast.jsonl` only.
- Held-out file `E1/test_item.jsonl` was not opened by this script.
- Confidence intervals are 95% percentile bootstrap intervals over items.
- The five embedding models are evaluated using cosine distance for identity metrics.
- Scope order is evaluated separately using unnormalized embedding norms: norm(W) < norm(A) < norm(N).
- The length-only baseline uses word count as a proxy for scope.
- The MS MARCO cross-encoder is a passage-relevance baseline, not a purpose-trained identity judge.
- Retrieval threshold metrics are hindsight-tuned on the development set and are optimistic.

## Embedding results

| Model | Near-miss error | Overlap shortcut | Low-overlap shortcut | Norm scope order | Length-only scope |
|---|---:|---:|---:|---:|---:|
| e5-base-v2 | 0.984 [0.951, 1.000] | 0.066 [0.016, 0.131] | 0.410 [0.279, 0.541] | 0.000 [0.000, 0.000] | 0.098 [0.033, 0.180] |
| bge-base-en-v1.5 | 0.984 [0.951, 1.000] | 0.082 [0.016, 0.164] | 0.344 [0.230, 0.459] | 0.000 [0.000, 0.000] | 0.098 [0.033, 0.180] |
| all-MiniLM-L6-v2 | 0.967 [0.918, 1.000] | 0.164 [0.082, 0.262] | 0.426 [0.311, 0.541] | 0.000 [0.000, 0.000] | 0.098 [0.033, 0.180] |
| specter2_base | 0.951 [0.885, 1.000] | 0.082 [0.016, 0.148] | 0.328 [0.213, 0.443] | 0.377 [0.262, 0.492] | 0.098 [0.033, 0.180] |
| Qwen3-Embedding-0.6B | 0.967 [0.918, 1.000] | 0.131 [0.049, 0.230] | 0.426 [0.311, 0.541] | 0.016 [0.000, 0.049] | 0.098 [0.033, 0.180] |

## Cross-encoder contrast results

```json
{
  "model_id": "cross-encoder/ms-marco-MiniLM-L-6-v2",
  "interpretation": "Passage-relevance baseline; not a purpose-trained or instruction-following research-question identity judge.",
  "n": 61,
  "near_miss_error": {
    "estimate": 0.9836065573770492,
    "ci95_item_bootstrap": [
      0.9508196721311475,
      1.0
    ],
    "n": 61
  },
  "overlap_shortcut": {
    "estimate": 0.09836065573770492,
    "ci95_item_bootstrap": [
      0.03278688524590164,
      0.18032786885245902
    ],
    "n": 61
  },
  "low_overlap_shortcut": {
    "estimate": 0.47540983606557374,
    "ci95_item_bootstrap": [
      0.36065573770491804,
      0.6065573770491803
    ],
    "n": 61
  },
  "by_type": {
    "constraint_flip": {
      "n": 16,
      "near_miss_error": {
        "estimate": 1.0,
        "ci95_item_bootstrap": [
          1.0,
          1.0
        ],
        "n": 16
      },
      "overlap_shortcut": {
        "estimate": 0.25,
        "ci95_item_bootstrap": [
          0.0625,
          0.5
        ],
        "n": 16
      },
      "low_overlap_shortcut": {
        "estimate": 0.625,
        "ci95_item_bootstrap": [
          0.375,
          0.8140624999999915
        ],
        "n": 16
      }
    },
    "direction_flip": {
      "n": 14,
      "near_miss_error": {
        "estimate": 1.0,
        "ci95_item_bootstrap": [
          1.0,
          1.0
        ],
        "n": 14
      },
      "overlap_shortcut": {
        "estimate": 0.07142857142857142,
        "ci95_item_bootstrap": [
          0.0,
          0.21428571428571427
        ],
        "n": 14
      },
      "low_overlap_shortcut": {
        "estimate": 0.42857142857142855,
        "ci95_item_bootstrap": [
          0.14285714285714285,
          0.7142857142857143
        ],
        "n": 14
      }
    },
    "goal_swap": {
      "n": 10,
      "near_miss_error": {
        "estimate": 0.9,
        "ci95_item_bootstrap": [
          0.7,
          1.0
        ],
        "n": 10
      },
      "overlap_shortcut": {
        "estimate": 0.0,
        "ci95_item_bootstrap": [
          0.0,
          0.0
        ],
        "n": 10
      },
      "low_overlap_shortcut": {
        "estimate": 0.7,
        "ci95_item_bootstrap": [
          0.4,
          1.0
        ],
        "n": 10
      }
    },
    "inquiry_change": {
      "n": 11,
      "near_miss_error": {
        "estimate": 1.0,
        "ci95_item_bootstrap": [
          1.0,
          1.0
        ],
        "n": 11
      },
      "overlap_shortcut": {
        "estimate": 0.0,
        "ci95_item_bootstrap": [
          0.0,
          0.0
        ],
        "n": 11
      },
      "low_overlap_shortcut": {
        "estimate": 0.36363636363636365,
        "ci95_item_bootstrap": [
          0.09090909090909091,
          0.6363636363636364
        ],
        "n": 11
      }
    },
    "role_swap": {
      "n": 10,
      "near_miss_error": {
        "estimate": 1.0,
        "ci95_item_bootstrap": [
          1.0,
          1.0
        ],
        "n": 10
      },
      "overlap_shortcut": {
        "estimate": 0.1,
        "ci95_item_bootstrap": [
          0.0,
          0.3
        ],
        "n": 10
      },
      "low_overlap_shortcut": {
        "estimate": 0.2,
        "ci95_item_bootstrap": [
          0.0,
          0.5
        ],
        "n": 10
      }
    }
  }
}
```

## Retrieval results

```json
{
  "retrieval_embedding_model": "e5-base-v2",
  "cross_encoder_model": "cross-encoder/ms-marco-MiniLM-L-6-v2",
  "candidate_pool_size": 427,
  "top_k": 10,
  "number_of_queries": 61,
  "known_target_pairs": 244,
  "known_positive_pairs": 122,
  "positive_retrieval_recall_before_cross_encoder": 0.8360655737704918,
  "cross_encoder_top10_pipeline": {
    "threshold_hindsight": -10.400358200073242,
    "metrics": {
      "precision": 0.504950495049505,
      "recall": 0.8360655737704918,
      "f1": 0.6296296296296297,
      "tp": 102,
      "fp": 100,
      "fn": 20,
      "tn": 22
    }
  },
  "cosine_threshold_baseline_hindsight": {
    "threshold_hindsight": 0.16765598118799052,
    "metrics": {
      "precision": 0.5104602510460251,
      "recall": 1.0,
      "f1": 0.6759002770083102,
      "tp": 122,
      "fp": 117,
      "fn": 0,
      "tn": 5
    }
  },
  "threshold_warning": "Both thresholds were chosen with hindsight on the same development items. These are optimistic descriptive comparisons, not held-out estimates.",
  "evaluation_scope_warning": "Precision/recall are computed on the four known target variants (B, B_min, C, C_tilde) per query. This is a targeted contrast set, not a fully labelled pool of every retrieved text."
}
```

## Interpretation cautions

1. A high near-miss error rate means the model places C closer to A than B under this constructed test; it does not establish general failure on all research questions.
2. Embedding norms may reflect length, pooling, or model-specific scaling rather than scope. The length-flipped subset is therefore important.
3. **Unit-normalization limitation:** If embeddings are L2-normalized before their norms are measured, their norms are approximately 1 by construction. Norm-based scope ordering is then not measurable and should be reported as N/A, not interpreted as zero accuracy. This limitation applies only where unit normalization is actually used at the point of measurement; the reported metrics should not be relabeled without verifying the implementation.
4. The cross-encoder is a relevance baseline. Its scores are not calibrated probabilities of question identity.
5. The retrieval metrics cover the four hand-constructed target variants per query, not a fully annotated set of every candidate in the pool.
6. Inspect the source papers and all manually edited items before claiming the dataset is semantically valid.


## Task 3: Comparing Predictions with Experimental Results

Before evaluating the models, I predicted that Qwen3-Embedding-0.6B would rank the near-miss question C closer to the original question A than the faithful paraphrase B on approximately 60% of items. I also expected general-purpose embedding models to make this error on roughly 40–70% of items.

The observed results were substantially worse than predicted. Qwen3-Embedding-0.6B had a near-miss error rate of 96.7%. E5 and BGE each reached 98.4%, MiniLM reached 96.7%, and SPECTER2 reached 95.1%. The cross-encoder's error rate was 98.4%.

My prediction underestimated the frequency of near-miss errors by a large margin. The difficulty was widespread across the evaluated models rather than an occasional weakness.

These results suggest that semantic similarity is not equivalent to research-question identity. Two questions may discuss similar concepts while asking fundamentally different things. Embedding models can capture shared subject matter without reliably distinguishing changes in research direction, constraints, goals, or relationships between entities.

The low-overlap shortcut results reinforce this concern: error rates ranged from 32.8% to 42.6% across the embedding models. Reducing lexical overlap alone did not reliably resolve the problem. SPECTER2 also behaved differently on the exploratory scope-ordering metric, achieving 37.7%, compared with 0–1.6% for the other embedding models. This difference is worth investigating, but it does not establish that SPECTER2 reliably understands research-question scope.

**Conclusion:** My initial expectations underestimated the severity of the near-miss problem. Evaluating research-question identity requires testing whether models preserve the actual question being asked, rather than relying on topical similarity or surface-level resemblance.

**Protocol limitation:** The repository documents that the evaluation protocol was recorded retrospectively relative to the development evaluation. Therefore, this comparison should not be presented as a fully preregistered prediction-versus-test result.

## SPECTER2 evaluation correction

**Correction date:** 2026-10-22

The original SPECTER2 run loaded `allenai/specter2_base` through
SentenceTransformers with automatically created mean pooling. That setup
did not use the intended SPECTER2 adapter and CLS-token representation.
Its SPECTER2 metrics should therefore be treated as superseded exploratory
results, not as the final SPECTER2 evaluation.

A separate evaluation was run on the same 61 development items using
`allenai/specter2_base` with the `allenai/specter2` proximity adapter and
the CLS-token representation. It used 2,000 item-level bootstrap resamples.
The original result files were preserved, and the other embedding models
were not rerun.

| Metric | Estimate | 95% item-bootstrap CI | n |
|---|---:|---:|---:|
| Near-miss error | 0.951 | [0.885, 1.000] | 61 |
| Overlap shortcut | 0.115 | [0.049, 0.197] | 61 |
| Low-overlap shortcut | 0.393 | [0.262, 0.508] | 61 |
| Norm-based scope ordering | 0.180 | [0.082, 0.279] | 61 |
| Length-only scope baseline | 0.098 | [0.033, 0.180] | 61 |
| Scope ordering on length-flipped items | 0.205 | [0.077, 0.333] | 39 |

*Note:* Confidence intervals are item-level bootstrap intervals. These results describe this constructed development
set; they do not establish general performance on all research questions.
Embedding-norm ordering is exploratory and is not assumed to measure scope
reliably. The proximity adapter is designed for scientific-paper similarity,
so its performance on these research-question comparisons should be
interpreted in that context.

Corrected machine-readable outputs are stored in
`E1/results_specter2_corrected/`. The held-out test file was not used.


## Task 4: Retrieval and Deduplication

This task examines whether embedding-based retrieval and a cross-encoder
can identify known related and contrasting question variants in the
development candidate pool. E5-base-v2 retrieved the top 10
candidates from a pool of 427 texts for each
of 61 queries.

### Retrieval results

Before cross-encoder reranking, recall of the known positive target pairs
was 0.836.

| Method | Precision | Recall | F1 | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|---:|---:|
| Cross-encoder top-10 pipeline | 0.505 | 0.836 | 0.630 | 102 | 100 | 20 | 22 |
| Cosine-threshold baseline | 0.510 | 1.000 | 0.676 | 122 | 117 | 0 | 5 |

### Threshold-free AUROC (exploratory)

On the 244 labelled target pairs (122 positive and 122 negative),
the cross-encoder achieved AUROC 0.5694 (95% query-bootstrap CI:
[0.5434, 0.5973]). Embedding similarity, represented by the negative
embedding distance, achieved AUROC 0.6047 (95% query-bootstrap CI:
[0.5830, 0.6302]). Confidence intervals were calculated using 2,000
bootstrap resamples of the 61 query IDs, retaining all target-pair
records associated with each sampled query.

These results indicate modest ranking discrimination on this
constructed development evaluation. The analysis is exploratory and
was not a preregistered prediction; it is not a held-out test estimate.
The labelled pairs are the known target variants, not an exhaustively
labelled candidate pool. AUROC therefore does not establish general
question-identity or deduplication performance.

### Interpretation and limitations

The cross-encoder pipeline achieved precision 0.505 and
recall 0.836 on the defined target-pair evaluation. The
cosine-threshold baseline achieved precision 0.510 and
recall 1.000. These figures describe this constructed
development comparison; they do not establish general deduplication
performance across an exhaustively labelled corpus.

Both thresholds were selected with hindsight on the same development
items, so the comparison is exploratory and optimistic. Precision and
recall were calculated over the four known target variants per query
(B, B_min, C, and C_tilde), not over a fully labelled set of every
retrieved candidate. The cross-encoder is a relevance baseline, not a
calibrated question-identity classifier.

Consequently, these results support a limited assessment of retrieval
and candidate filtering, not a claim that the system reliably deduplicates
all semantically equivalent research questions. Independent validation
with a separately labelled candidate pool would be needed to support
that broader claim.
