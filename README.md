# ASI Selection Round: Submission

## Compute environment

The exact compute tier used for the original evaluation is not established by the available project records. The evaluation scripts select Apple MPS, CUDA, or CPU when available. Device selection does not establish the machine memory tier.

## Reproduce

Run commands from the repository root with the required Python dependencies installed.

1. Corrected development evaluation:
   python E1/eval_contrast_v2.py
   Reads E1/contrast.jsonl and writes corrected results under E1/results_v2/.

2. Corrected SPECTER2 evaluation:
   python E1/evaluate_specter2_corrected.py
   Uses the separate corrected SPECTER2 evaluation implementation and writes outputs under E1/results_specter2_corrected/.

3. Earlier evaluation pipeline:
   python E1/eval_contrast.py
   Writes outputs under E1/results/. Treat these as earlier results, not replacements for the corrected results.

4. Project integrity checks:
   python E1/verify_e1.py

## Dataset boundary

The evaluation scripts use E1/contrast.jsonl, the development dataset. Keep the frozen dataset unchanged. Do not use the held-out test file for development evaluation.
