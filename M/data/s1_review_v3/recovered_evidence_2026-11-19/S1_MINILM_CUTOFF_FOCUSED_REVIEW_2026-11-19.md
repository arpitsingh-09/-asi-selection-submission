# S1 MiniLM cutoff source review — 2026-11-19

Scope: focused read-only review of public source material for the exact
encoder checkpoint in `S1_encoder_preparation_lock.json`. No model was loaded,
no vectors were generated, and no scoring or protocol change was made.

## Frozen encoder identity

The preparation lock pins
`sentence-transformers/all-MiniLM-L6-v2` revision
`1110a243fdf4706b3f48f1d95db1a4f5529b4d41` and records hashes for the model,
tokenizer, and configuration files. The exact-revision
[Hugging Face model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/blob/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/README.md)
says the checkpoint was fine-tuned on more than one billion sentence pairs,
lists the component datasets, and says it was developed during the Hugging Face
Community Week using JAX/Flax. The
[official Community Week announcement](https://discuss.huggingface.co/t/open-to-the-community-community-week-using-jax-flax-for-nlp-cv/7104)
dates the event to July 7–14, 2021.

The linked [base-model card](https://huggingface.co/nreimers/MiniLM-L6-H384-uncased)
describes the six-layer MiniLM model structure, but supplies no complete
pretraining-data snapshot or cutoff date.

## Decision

This is authoritative context about the model’s development event and named
training sources. It is **not** an explicit, artifact-bound training-data
cutoff: the sources do not identify the exact snapshots or collection dates of
all training corpora, and they do not state a cutoff for the base model’s
pretraining data. The event date alone cannot establish those missing facts.

Therefore the frozen amendment’s statement that the training-data cutoff is
unverified remains accurate. The cutoff requirement **does not pass**. This
review does not authorize substituting the event date, model revision date, or
repository upload date for a verified cutoff.

## Exact evidence still needed

An authoritative record from the model publisher or training authors must bind
the exact pinned weights (or their training run) to a declared training-data
cutoff and account for both the sentence-transformer fine-tuning corpora and
the base model’s pretraining. Without that record, the S1 encoder-cutoff gate
remains blocked.
