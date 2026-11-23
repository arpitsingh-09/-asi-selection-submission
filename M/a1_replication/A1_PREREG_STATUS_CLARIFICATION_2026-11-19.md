# A1 supplementary preregistration status clarification

**Prepared:** 2026-11-19 (Asia/Kolkata)  
**Purpose:** Reconcile conflicting status text with the preserved Git and run
records. This is a post hoc evidence clarification, not a preregistration,
protocol amendment, authorization, or change to any existing result.

## Preserved records

The A1 supplementary registration at
[`PREREG_REPLICATION.md`](PREREG_REPLICATION.md) remains unchanged. Its first
paragraph says “registration text prepared for approval; not committed or
authorized for scoring.” The committed file itself contains that sentence.

The original Main Problem Git history is preserved in
[`../main_problem_git_history.bundle`](../main_problem_git_history.bundle),
SHA-256 `2bae02603112398b289f9cfe9f4de62fb93227e51bd31e1bf04e0d25521fc51d`.
That bundle verifies as a complete history. It records these relevant commits:

| Record | Commit and parent | Commit time (Asia/Kolkata) | Evidence |
|---|---|---|---|
| A1 supplementary registration | `281595fac1280a855cd67d71cf7f357e0a440d0e`, parent `71ac90c2961595db1e26e6ab2c5bf3a986e56f96` | 2026-11-14 17:56:03 | Commit adds `M/a1_replication/PREREG_REPLICATION.md`. The committed file includes the contradictory “not committed” status sentence. |
| Amendment 003 | `c73df33a663ce9e648b12524703fd2f255b8097d`, parent `c7be68dbf12566083cffc5cad8697121aeb581cc` | 2026-11-14 19:50:48 | Commit records `M/a1_replication/AMENDMENT_003_PARTIAL_CONTROLS.md`. |
| Scoring authorization | `42770a2db1d6978c52b8c95e288fa769df7bc10c`, parent `c73df33a663ce9e648b12524703fd2f255b8097d` | 2026-11-14 21:48:53 | Commit adds `M/a1_replication/A1_SCORING_AUTHORIZATION_2026-11-14.md`. The saved result names this commit in `authorization_commit`. |

The saved result `A1_SCORING_RESULTS_V1.json` records inference start at
`2026-11-14T16:42:20Z`, equivalent to 22:12:20 Asia/Kolkata, and records the
authorization commit above. The committed registration timestamp precedes
that inference timestamp by 4 hours, 16 minutes, 17 seconds. The authorization
commit precedes it by 23 minutes, 27 seconds. The Amendment 003 commit precedes
the authorization commit.

The current authorization file's SHA-256 is
`4d7a1bc5d83dfb6b89b8aaa26776bd5ea4ae41bb90e5879560a47fff3ea105e7`; its Git
blob ID matches the version in commit `42770a2db1d6978c52b8c95e288fa769df7bc10c`.
The current saved scoring-result SHA-256 is
`40f564c94801395fd327b1849d457515dab6e7d4f0901fb3960d91c9f358b4ff`.

## Reconciliation and limits

The sentence “not committed” conflicts with the existence of the registration
commit that contains it. The sentence “not authorized” describes the draft
state but conflicts with the later, separately committed scoring authorization
and its reference in the saved result. The Git/run records therefore support
this internal sequence: registration commit, Amendment 003 commit, scoring
authorization commit, then recorded inference. The inconsistent sentence is
preserved as written; this clarification does not silently reinterpret or
remove it.

This sequence is evidence of the repository's internal commit and run-record
chronology, not independent proof of wall-clock time, author identity, public
availability, or compliance with every preregistered scientific condition.
The A1 work remains an exposed supplementary partial replication, not original
A1 and not an independent confirmatory result. It does not change the frozen
Main Problem protocol or the 0/9 status of the original registered battery.
