# Export-only recovery — 2026-11-13

Initial protocol/data/numerical implementation committed as c0fd73c. Nineteen
unit tests passed. The first full controlled run calculated its results but
failed on JSON serialization of a NumPy scalar before saving any result row.
The empty partial output directory is preserved, not overwritten. No headline
outcomes were inspected; no claim of completed evaluation was made.

Commit a narrowly scoped export wrapper and two serialization tests before
retrying. Convert only NumPy scalar types to their equivalent Python scalar
values. Keep the original numerical function, source/code/data hashes,
thresholds, predictions, bootstrap and pass criteria unchanged. Do not edit
PREREG.md or the original frozen manifest. Use a fresh versioned output directory.
This is recovery of an unusable export, not a new tuned experiment. The wrapper
verifies its own committed manifest and then delegates to the original engine
with a private JSON-export binding; it does not mutate the original module.
