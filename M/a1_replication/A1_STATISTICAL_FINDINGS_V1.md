# Supplementary A1 statistical findings

Analysis uses only the saved A1 score results; no scoring or model inference was run.

- Focal-paper clusters: **n=2**
- Scored nonempty targets: **16**
- Bootstrap: paired focal-paper cluster percentile, 2,000 draws, NumPy PCG64 seed `20261113`.
- Every bootstrap draw retains each sampled focal paper's full set of conditions.
- Empty pool: **undefined**. Same-topic decoy: **unavailable**.
- **n=2 makes inferential conclusions extremely limited**; intervals are highly discrete and unstable.

## Registered axiom pass fractions

Intervals are 95% percentile cluster-bootstrap CIs. Coverage pass requires all four ordered decreases for that paper and coordinate.

| Coordinate | Coverage strict pass fraction (95% CI) | Concentration strict pass fraction (95% CI) |
|---|---:|---:|
| Y | 0.500 [0.000, 1.000] | 1.000 [1.000, 1.000] |
| density | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| N | 0.500 [0.000, 1.000] | 0.000 [0.000, 0.000] |
| yours | 0.500 [0.000, 1.000] | 0.000 [0.000, 0.000] |

Registered numerical threshold met: **False** (qualifying coordinates: none).

## Mean paired score effects

Effects are signed in the preregistered direction; positive values indicate the expected reduction.

| Coordinate | Coverage comparison | Mean paired delta (95% CI) |
|---|---|---:|
| Y | baseline_minus_coverage_25 | 0.025126 [0.014988, 0.035263] |
| Y | coverage_25_minus_coverage_50 | 0.000740 [-0.001748, 0.003227] |
| Y | coverage_50_minus_coverage_75 | 0.007104 [0.004944, 0.009265] |
| Y | coverage_75_minus_coverage_100 | 0.000787 [-0.001252, 0.002825] |
| density | baseline_minus_coverage_25 | 2.500000 [1.000000, 4.000000] |
| density | coverage_25_minus_coverage_50 | 0.500000 [0.000000, 1.000000] |
| density | coverage_50_minus_coverage_75 | 0.000000 [0.000000, 0.000000] |
| density | coverage_75_minus_coverage_100 | 0.000000 [0.000000, 0.000000] |
| N | baseline_minus_coverage_25 | 0.010061 [0.008485, 0.011636] |
| N | coverage_25_minus_coverage_50 | -0.000267 [-0.003046, 0.002512] |
| N | coverage_50_minus_coverage_75 | 0.001132 [-0.001530, 0.003794] |
| N | coverage_75_minus_coverage_100 | 0.000755 [-0.001175, 0.002684] |
| yours | baseline_minus_coverage_25 | 0.021359 [0.013363, 0.029356] |
| yours | coverage_25_minus_coverage_50 | 0.000488 [-0.002072, 0.003048] |
| yours | coverage_50_minus_coverage_75 | 0.005611 [0.003325, 0.007897] |
| yours | coverage_75_minus_coverage_100 | 0.000779 [-0.001233, 0.002790] |

| Coordinate | Concentration comparison | Mean paired delta (95% CI) |
|---|---|---:|
| Y | distributed − concentrated | 0.010803 [0.007569, 0.014037] |
| density | distributed − concentrated | -13.500000 [-19.000000, -8.000000] |
| N | distributed − concentrated | -0.057500 [-0.059443, -0.055556] |
| yours | distributed − concentrated | -0.006272 [-0.009184, -0.003361] |

Original-versus-shuffled results are reported separately as diagnostics in the JSON; they have no registered directional pass criterion. These analyses cover the amended partial evaluation only and do not establish completion of the full control set or original A1.
