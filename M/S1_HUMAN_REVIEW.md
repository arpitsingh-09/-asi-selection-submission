# Independent S1 human verification

Canonical packet: `M/data/s1_review_v3/`. There are 122 pairs, no verified labels.
`annotation_manifest.jsonl` preserves original E1 assertions with exact-byte/field
provenance. `blind_review_template.jsonl` omits proposed relation/variant/task labels
and model outputs; human reviewers should receive this file, not the manifest.
Paper source context is included; dates shown are **paper dates**, not question dates.

1. Give separate copies of the template to two genuine humans independent of the
   original E1 author and each other. Do not send via tools without authorization.
2. Each reviewer fills `reviewer_id`, `reviewer_kind: human`,
   `independent_of_author: true`, `same_question: true/false`,
   `source_alignment_verified: true/false`, a concrete rationale and timezone-aware
   `reviewed_at`. Leave unknown judgments null; the importer retains them unresolved.
   Compare the scientific question, not wording overlap. Check source alignment in
   the provided abstract/paper. False alignment rejects eligibility, not the review.
3. Do not change pair IDs, text, hashes or source context. Work independently, without
   model predictions or the other human's answers. AI-generated judgments cannot
   fulfill this step. Attestations are auditable human responsibility; the importer
   cannot authenticate a person's identity.
4. Import actual completed files into a **new** directory:

```sh
.venv/bin/python -B -m M.s1_review import \
  --manifest M/data/s1_review_v3/annotation_manifest.jsonl \
  --reviews /path/reviewer_A.jsonl /path/reviewer_B.jsonl \
  --out M/data/s1_human_reviews_NEXT
```

Two distinct independent reviewers must agree and confirm alignment. Disagreements
stay unresolved; repeated votes by one reviewer do not create independence. Keep
review files permanently: imported votes bind their byte offsets and SHA-256s.
Do not edit reviewed sources after import. Annotation consensus alone does not
make an example temporally eligible.

Remaining metadata verification must source the authored question's creation and
availability dates, original earlier input IDs/versions, different shuffled inputs,
and a distinct independently verified same-topic decoy. A paper date or a local
file modification date does not prove question availability. The packet retains
source-ID associations but leaves original inputs and question dates null.

Offline B-Q preparation (no scoring):

```sh
.venv/bin/python -B -m M.s1_encoder \
  --requests M/data/s1_review_v3/embedding_requests.json \
  --out M/data/s1_review_v3/minilm_vectors.json
```

Only the pinned existing local MiniLM snapshot is allowed; exact misses, oversized
requests or truncation needs fail. New vectors never modify E1/E2 caches. This
solves vector availability, not training-cutoff evidence or human annotations.

After resolving all dependencies: freeze a new reviewed cohort, encoder/threshold
configuration and four-control prediction sources; commit the prospective lock;
then run the registered S1 statistics. Current real-run status is **BLOCKED**.
