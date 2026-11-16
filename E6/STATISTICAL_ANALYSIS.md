# Offline statistical integration

`statistical_analysis.analyze_evaluations` accepts existing evaluation artifacts;
it performs no inference, data acquisition, or protocol updates. Outputs remain
provisional. Call separately for each testbed and declared scalar metric.

Supply the frozen cohort's full list of source artifacts (including failed
units), an explicit list of comparisons, replicate count, seed, and
`missing_policy='block'` or explicitly chosen `'complete_pairs'`. The latter
reports exclusions separately for each arm and contrast. Missing cells never
become zeros. A wholly absent cohort unit must be supplied as an artifact with
its input-set ID and absent evaluations; it cannot be inferred from other units.

Native TRAIN evaluation summaries use `testbed='data'` and these value paths:

- Accuracy: `['heldout', 'heldout_accuracy', 'parsed_output', 'accuracy']`.
- HDR: `['hdr', 'hypothesis_discovery_rate']`.

Native literature bundles use `testbed='literature'`,
`stage='literature_reconstruction_similarity'`,
`field='research_question'` or `'main_hypothesis'`, and
`value_path=['parsed_output', 'best_similarity']`. Other evaluation record
stages can supply declared scalar input-set summaries through the same adapter.
Individual same-question candidates, hypotheses, judges and TEST rows must not
be passed as independent units. Their aggregation policy remains a caller
prerequisite; the adapter does not invent one.

Seven arm means and every supplied comparison receive fixed 95% percentile
intervals using arithmetic means, linear quantiles and paired input-set draws.
Use `list(itertools.combinations(ARMS, 2))` only when the declared family is all
21 pairs. Positive differences mean left minus right. Intervals are marginal,
unadjusted; this module does not choose primary contrasts or multiplicity policy.
A single available unit yields a degenerate interval, with its count reported.

Output includes original sources, source hashes, metric cells, explicit
exclusions, configuration, runtime and implementation hashes, and output hash.
`write_analysis_exclusive(path, result)` validates the hash and refuses overwrite.
The sampler records its deterministic SHA256-seeded Python MT19937 streams.
Repeated analysis of identical inputs/configuration in the same implementation
and runtime produces identical output. Retain the output runtime version for
reproduction. No results are synthesized to resolve pending approvals.

Current applied policy: failures remain null and configured contrasts use complete pairs with planned/included/excluded counts and unavailable fractions. `analyze_configured_evaluations` reads active config only; proposed numerical parameters are never used as defaults. Current replicate count, seed and RNG remain unresolved active values. All intervals are descriptive 95% marginal intervals; no adjusted significance claims are supported.
