# Main Problem Git history evidence

## Source and bundle

- Original repository: `/Users/arpit/asi-selection`
- Source ref bundled: `refs/heads/main`
- Bundle: [`main_problem_git_history.bundle`](main_problem_git_history.bundle)
- Bundle size: 31,841,481 bytes
- Bundle SHA-256: `2bae02603112398b289f9cfe9f4de62fb93227e51bd31e1bf04e0d25521fc51d`
- Verification: `git bundle verify` reports the bundle is okay, contains
  `refs/heads/main` at `a1dececb3929909bfc92de0e8b2b1defd3070917`, and records a
  complete history with no missing prerequisites.
- The submission checkout at `/Users/arpit/ASI_Intern_Submission` did not
  contain the historical commit objects before this bundle was created.

The bundle was created from the original repository's existing `main` ref. It
contains the complete history reachable from that ref, including unrelated
project history as ancestors/commits; no replacement commits or timestamp edits
were made. The source repository's working tree may contain uncommitted files;
Git bundles preserve committed objects and refs, not uncommitted changes.

## Relevant committed records

All dates below are the commit object's author and committer timestamps,
respectively. In these records they are identical. Parent IDs are included to
show the committed ancestry. Each path is present in the listed commit.

| Commit | Parent | Author / committer date (Asia/Kolkata offset) | Subject | Relevant path |
|---|---|---|---|---|
| `6e21dfea2719db1e67e0e9a8a8b3861ab3ec10a1` | `8445bb9679394f617dae0e63f8224b297d762250` | `2026-11-13T18:36:04+05:30` | Implement M shared space, temporal training and preregistered core battery | `M/PREREG.md` |
| `59a9d405fd29364d8db5ba9a15a75c3ef921097e` | `6e21dfea2719db1e67e0e9a8a8b3861ab3ec10a1` | `2026-11-13T18:43:21+05:30` | Add source-bound M outcome recovery and cache-only baseline adapters | `M/amendments/2026-11-13-stage4-evidence.md`; `M/amendments/stage4_evidence_lock.json` |
| `de7cbef7f38fde540a1168317a78328f5d7a7266` | `59a9d405fd29364d8db5ba9a15a75c3ef921097e` | `2026-11-13T18:49:22+05:30` | Preregister bounded S1 baseline encoding and independent human review workflow | `M/amendments/2026-11-13-S1-independent-review.md`; `M/amendments/S1_encoder_preparation_lock.json` |
| `098d5a0281421be3cc85477c8a50fd84a78a307b` | `7ab117ec72e32d813bff775513f140f497ace58c` | `2026-11-13T19:31:36+05:30` | Preregister deterministic generated-question cohort preparation | `M/amendments/2026-11-13-generated-question-cohort.md` |
| `281595fac1280a855cd67d71cf7f357e0a440d0e` | `71ac90c2961595db1e26e6ab2c5bf3a986e56f96` | `2026-11-14T17:56:03+05:30` | Register supplementary A1 replication | `M/a1_replication/PREREG_REPLICATION.md` |
| `a87b631bc1b4237e950cbaf8abe4e1e4524cc652` | `76c084a0679a52973542df43aa87866dbd1be782` | `2026-11-15T08:17:41+05:30` | Register separate prospective grounding V2 generation | `M/prospective_grounding/PREREG_V2.md` |
| `e18ace5121c49eb1f94cd3c0c7c40c912643e3e8` | `0280c39e89a8f7d35afc2a713a4c7da4b2619f3a` | `2026-11-15T23:23:48+05:30` | Freeze exploratory supplementary S1 preregistration | `M/supplementary_s1_e1_exploratory/PREREG.md` |

The six later records listed after the original preregistration are reachable
from the bundled `main` ref. The original preregistration commit is also an
ancestor of that ref. Commit IDs, parent links, paths, and timestamps were
queried from the original repository before bundling.

## What this supports

The bundle preserves the Git commit objects and parent graph for the original
Main Problem preregistration and the listed amendment/preregistration records.
Its SHA-256 identifies these exact bundle bytes. A reviewer can independently
verify the bundle and inspect the commits without access to the original local
repository.

## What this does not prove

Git commit author and committer timestamps are metadata supplied when a commit
is created. The bundle preserves them but does not independently authenticate
the wall-clock time, author identity, or when the commits became public. The
bundle is not signed by an external timestamp authority, and a successful
`git bundle verify` proves Git object/ref integrity and prerequisite
availability, not that the recorded chronology is externally attested.
Therefore it supports the repository's internal R2 chronology evidence, but
does not alone prove public availability or independently trusted timestamps.

The bundle also cannot establish that a preregistration was scientifically
followed, that labels/reviews are genuine, or that any experiment passed. The
A1 registration commit (`281595fac1280a855cd67d71cf7f357e0a440d0e`) is timestamped
2026-11-14 17:56:03 +05:30; the saved A1 result records inference start at
2026-11-14 16:42:20Z (22:12:20 +05:30), so the Git timestamp precedes inference
by about 4 hours 16 minutes. However, the committed A1 registration text retains
a status sentence saying it was “not committed or authorized”; the separate
scoring authorization exists, but the stale sentence is an unresolved
documentation inconsistency. A dated non-overwriting reconciliation is in
[`a1_replication/A1_PREREG_STATUS_CLARIFICATION_2026-11-19.md`](a1_replication/A1_PREREG_STATUS_CLARIFICATION_2026-11-19.md).
Do not silently treat the sentence as corrected or infer external timestamp
authenticity from the bundle.
