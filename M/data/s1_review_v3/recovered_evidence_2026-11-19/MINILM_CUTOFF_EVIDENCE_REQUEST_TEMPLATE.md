# Request for authoritative MiniLM training-cutoff evidence

Please provide authoritative training-provenance documentation for the exact S1 encoder checkpoint:

- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Pinned revision: `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`

The record must identify the exact weights/revision and document both:

1. Fine-tuning dataset names, immutable snapshot/version identifiers, and the latest data date or cutoff included in fine-tuning.
2. The exact base-model checkpoint, pretraining dataset names and snapshots, and the pretraining cutoff.

Please include the author/publisher, date, primary source URL or signed source document, and enough detail to bind the statements to this exact revision. A model release date, paper publication date, or general training-period description does not establish the required cutoffs.

When received, preserve the response/document unchanged in the S1 recovered-evidence directory, calculate SHA-256, and add its source path, hash, scope, and requirements supported to the evidence handoff manifest. If the exact snapshots or cutoffs cannot be established, please state that limitation explicitly.
