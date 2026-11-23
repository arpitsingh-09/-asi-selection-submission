# Frozen Main quality-label recovery audit

**Date:** 2026-11-19  
**Status:** additive source audit only; no labels imported into the frozen manifests, no model fit, no predictions, and no evaluation run.

## Scope and inputs

The audit used the current frozen-v2 quality candidates and the local official OpenReview exports in `/Users/arpit/Downloads/iclr_task3_baseline/data/iclr_{2022,2023,2024,2025}/`. It searched every paper record in the four years for exact normalized frozen question text in the abstract, then checked title and note identity. It did not use fuzzy author-only matches as paper links.

| Input | SHA-256 | Rows |
|---|---|---:|
| `M/data/manifests_v2/train.jsonl` | `ba18f9b3cd2c781379ac4a98c71c66359a2940c78163388b392ced125af34329` | 25 rows / 20 unique paper IDs |
| `M/data/manifests_v2/validation.jsonl` | `a4854b7144724bc28b3b6c2ca0fd0c3b1d57ac6373d029c0dcec40c25f76f842` | 2 rows / 2 unique paper IDs |

The full paper export search found one exact frozen question passage in an OpenReview submission abstract: the TRAIN record `2212.14034v1:abstract-question:0`, “Cramming: Training a Language Model on a Single GPU in One Day.” No exact frozen question passage matched an ICLR 2022–2025 paper abstract for the other TRAIN or either VALIDATION candidate. Same-author or related-title results were not accepted as identity evidence.

## Recovered TRAIN candidate: Cramming

The ICLR 2023 submission note is `gUL6zYN4Uaf`, invitation `ICLR.cc/2023/Conference/-/Blind_Submission`. The local paper export’s line 1149 has SHA-256 `c20024ca106143dc1418a2b99842d728c985c5078481ec1904e1bbbecd037d37`; the complete export has SHA-256 `6fb56c1ab5734285cc7a25bcc4b32762d8cae68bfcb55acf98b7830a5e2cf199`. Its `odate` is `2022-09-29T16:15:00Z`, and the current abstract contains the frozen interrogative passage (abstract SHA-256 `d40ce57441ce3229ab4347a8ed395822627b4eec57e01adebccdf0c54424c086`). OpenReview defines `odate` as the time a note first becomes public.

The ICLR 2023 official calendar schedules “Paper Reviews Released” at `2022-11-05T01:00:00Z`. The local review export contains four `Official_Review` notes on that forum. Three notes have true modification times before the release event and carry current numeric recommendation values 5, 5, and 6; the fourth carries 6 but was modified on `2022-11-22T13:02:41.410Z`, after public release. The post-release-modified note is excluded from any release-time value summary because its value at release cannot be recovered from this snapshot.

The review export’s full-file SHA-256 is `b3ad35ce8c570d1cf91657c46fdc724a78768484fdc7b026562da9de41efd134`. Row bindings for the four note records are:

| Review note | Export line | Record SHA-256 | Current value | True modification time | Release-time handling |
|---|---:|---|---:|---|---|
| `VpEkt6zLidI` | 30607 | `6009832934d42ad1b6e2ea428f64a8e0b6386f4c4017c820d23764ed8c4789d4` | 5 | 2022-10-25 07:22:37.189 UTC | unchanged before release |
| `O8d9Km8oLKg` | 38011 | `24e2ac158f652579cf44a3344291ac6959b91e465366f91b38418741af3e84b3` | 6 | 2022-11-22 13:02:41.410 UTC | exclude: modified after release |
| `LcmGfQxOYO3` | 40420 | `e0567a20cc2b0abf31406d2f569d69f74538c0c9244b6c55b7a430306f581027` | 5 | 2022-10-25 06:27:29.276 UTC | unchanged before release |
| `JJy5zDi_UNr` | 42622 | `9da1fb8539bf74008853fa25637a3981b5ee0c47fba805843da7e61c85c2a305` | 6 | 2022-10-26 13:58:15.709 UTC | unchanged before release |

For the three unmodified notes, the current values were present before the official release event; the official event states reviews were released publicly. Their current reader lists include `everyone`. This yields a **candidate release-time training signal** of three reviewer values (mean `16/3`, about `5.333`), not a fitted label or an eligible training record yet.

### Why this candidate is still not admitted for fitting

1. The submission record’s current `tmdate` is in 2026, after its 2022 `odate`. The cached export has no note-edit/revision history binding the exact current abstract hash to the September 2022 public version. Thus the present snapshot shows the question text and the first-public date on one note, but does not prove that this exact abstract version was public at that date.
2. The current frozen manifest dates this question to the arXiv version on 2022-12-28, which is later than the ICLR review release. Using the earlier OpenReview submission date would require a separately versioned, source-bound manifest/amendment; this audit does not alter the frozen manifest or silently substitute dates.
3. The review notes have null per-note `odate` in the export. Their release time is supported by the official ICLR cohort release event plus the exact forum/invitation and pre-release `tmdate`, but the export does not preserve historical readers or per-note visibility edits.

Accordingly, these three values are preserved as **recovered candidate evidence**, not `eligible_labels.jsonl` entries. The fourth note remains excluded absent its historical edit value.

## VALIDATION result

Neither frozen validation question passage appears in the ICLR 2022–2025 submission abstracts searched. The export includes some same-author/related-topic work, but not the exact question text or a demonstrated exact paper-version link to these two frozen records. Those items are not joined to reviews. No 2024-observed, exact-question-linked validation rating was recovered.

For `2501.00457v1` (“Differentiable Prompt Learning for Vision Language Models”), the official IJCAI-25 proceedings paper contains the frozen question passage; the official arXiv v1 page dates that text to 2024-12-31. The local ICLR 2025 archive has an `ADAPT: Adaptive Prompt Tuning` submission by the same four authors, but its abstract does not contain the frozen question passage and describes adaptive prompt-token pruning. Same authorship is not an exact version binding, so that ICLR review is not joined to this record. For `2412.20895v1`, the existing local search hit is a DBLP CoRR record, not a conference review note; no exact ICLR review record or question-version link was recovered.

I also made one direct local request for the Cramming note's public edits (`notes/edits?note.id=gUL6zYN4Uaf`). DNS resolution failed with `[Errno 8] nodename nor servname provided, or not known`; the attempt is preserved in `OPENREVIEW_EDITS_FETCH_NEGATIVE_2026-11-19.json`. I did not retry or request other note histories. A focused indexed search for the Cramming/review note IDs and the two validation arXiv IDs/titles returned no exact OpenReview review or revision records. Their exact question text also does not occur in the local ICLR 2022–2025 paper abstracts.

## Gate and remaining work

**Recovered eligible labels:** 0 train, 0 validation, for both `peer_review` and `later_community_use`. **Quality heads remain unfit.** The recovery does not satisfy the model-training gate: `M/training.py` requires at least two dated training records and at least one dated validation record per factor, and the frozen validation split currently has no exact-linked public review evidence. The second factor also lacks an operationally defined, dated outcome source in the existing evidence record.

No existing result, authorization, manifest, protocol, or label file was changed. No training, inference, scoring, or heldout access occurred.

## Authoritative references

- OpenReview note fields: <https://docs.openreview.net/reference/api-v2/entities/note/fields> (`odate` is when a note first becomes public).
- ICLR 2023 official dates: <https://iclr.cc/Conferences/2023/Dates> (reviews released 2022-11-05 01:00 UTC).
- ICLR 2023 call for papers: <https://iclr.cc/Conferences/2023/CallForPapers> (reviews are publicly visible after release).
- Cramming OpenReview submission/PDF: <https://openreview.net/forum?id=gUL6zYN4Uaf>.
- DPL IJCAI-25 proceedings PDF: <https://www.ijcai.org/proceedings/2025/0606.pdf>.
- DPL arXiv v1: <https://arxiv.org/abs/2501.00457v1>.
- Compatible fine-tuning arXiv v1: <https://arxiv.org/abs/2412.20895v1>.
