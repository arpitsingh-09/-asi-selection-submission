# E2 Test Suite Report — Version 1

**Date:** 2026-10-27  
**Scope:** Automated implementation tests for E2 novelty scoring.

## 1. Test execution

Command: `.venv/bin/python -m unittest discover -s E2/tests -p 'test_*.py' -v`

Result: **31 tests passed, 0 failures, 0 errors.**

Reported runtime: 0.007 seconds.

## 2. Test coverage

| Test module | Tests passed |
|---|---:|
| test_axioms.py | 6 |
| test_eligibility.py | 16 |
| test_rnd.py | 5 |
| test_order_invariance_v1.py | 4 |
| **Total** | **31** |

The order-invariance tests check that reordering claims and comparison-pool papers preserves Y, N, the combined score (yours), and RND density in a controlled synthetic example. They also check that empty or invalid idea text and claims raise ValueError.

## 3. Limitations

- The order-invariance tests use mocked embeddings and a synthetic comparison pool.
- These tests establish selected implementation properties, not semantic validity or agreement with human novelty judgments.
- Passing implementation tests does not establish exact reproduction of the original RND method.
- The suite does not evaluate every experimental control listed in PREREG.md.
- The E2 protocol and predictions were documented retrospectively relative to the earlier implementation and scoring files. This report does not change that chronology.

## 4. Scoring and data integrity

The test run did not rerun the 2,400-case experiment.

No scoring-results files were intentionally modified by this test run. This report does not authorize scoring, data replacement, or changes to PREREG.md.

## 5. Warning

The test process emitted a nonfatal urllib3 NotOpenSSLWarning because Python uses LibreSSL. All 31 tests passed.
