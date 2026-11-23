# E2 claim-sidecar calibration review packet

Prepared for human assessment. This packet is not a calibration review, does not accept calibration, and does not authorize additional inference. No scoring was rerun and no vectors were generated during this inspection.

## Frozen identity and saved state

- Manifest: `E2/analysis/claim_sidecar_v1/manifest.json`
- Manifest SHA-256: `a33e042bc0defaa72f658e421dc3e2ad8f0ad3fbcdf4c04b250604353d50998f`
- Authorization: `E2/analysis/claim_sidecar_v1/authorization.2026-11-18.json` (SHA-256 `e8ff09b9c105bf4c47b19bbff9f28743e59cab9118ca71d7e0e3da3a6471af90`). Its calibration review path and SHA-256 are both `null`.
- Supplementary run authorization: `E2/analysis/claim_sidecar_v1/calibration_authorization.2026-11-18.json` (SHA-256 `f61310a7531aae44575140bef4f1e07f87e6eb82aadc6a1c991aa0b54ce9f187`); it was bound to the manifest, approved amendment, and driver at the successful run start.
- Existing vectors: `4/93`; these rows pre-existed this inspection.
- Request list SHA-256: `0b595cc10d020ecb757b36762d834c7d4cef1ffc45f6131884efd039fe4acb43`.
- Claim-source file SHA-256: `98a4244c8389284b87f171372eafe58326ea444256226f089e429d165d3f8410`.
- Stored parity metadata: passed `True`, `3` controls; maximum absolute differences `[0.0, 1.1920928955078125e-07, 0.0]`.
- Saved parity metadata does not include encoder elapsed time or process peak RSS.
- Supplementary calibration report: `E2/analysis/claim_sidecar_v1/calibration_only_2026-11-18_terminal_retry/calibration_report.json`, SHA-256 `dbc20c4bc2dfaba335c1d254eda9f77fa2d6d11c095cb57300ceea9ef31df013`. It records 2.221 seconds and 775,028,736 bytes process peak RSS, four transient vectors, three passing parity controls, exact saved-vector matches, and unchanged sidecar/cache hashes.
- The supplementary report is not yet linked through a human review JSON. The captured stdout includes an adapter-activation warning; see `CALIBRATION_REVIEW_SUPPLEMENT_2026-11-18.md` and `CALIBRATION_ADAPTER_WARNING_ASSESSMENT_2026-11-18.md`. The warning's effect is unresolved, so this packet does not accept the calibration.

## Four saved claims and source evidence

### 1. 2401.00237v1 — A Novel Approach for Defect Detection of Wind Turbine Blade Using Virtual Reality and Deep Learning

- Claim index `3`; request SHA-256 `0898df02c4eb78a67cb2b8b5d615e73fd94963f353ddd9ee6c15faac2d408fba`.
- Exact vector text: “The outcomes of the U-Net architecture have been thoroughly tested and compared with 5-fold validation datasets.”
- Row text/hash binding valid: **True**.
- Vector checksum valid: **True**; bytes `3072`; L2 norm `1.0000000431`.
- Source evidence: “The outcomes of U-Net architecture have been thoroughly tested and compared with 5-fold validation datasets.”
- Claim source `E2/analysis/claim_completion_v2/claims_future.jsonl`, paper `2401.00237v1`, claim index `3`; audit status `review_required_claim_count`; `human_review=not recorded`.
- Human check: does the cited evidence support this exact claim, including its qualifiers/numbers, and is this the intended claim text? Enter no decision here until reviewed.

### 2. 2401.04119v1 — Why is the User Interface a Dark Pattern? : Explainable Auto-Detection and its Analysis

- Claim index `3`; request SHA-256 `0b38c37f6df3cf3dda2732030afc6287aacfc927172385b388fe495206b02678`.
- Exact vector text: “LIME and SHAP explanations reveal which terms influence the model predictions of dark patterns.”
- Row text/hash binding valid: **True**.
- Vector checksum valid: **True**; bytes `3072`; L2 norm `1.0000000007`.
- Source evidence: “Then, we applied post-hoc explanation techniques, including local interpretable model agnostic explanation (LIME) and Shapley additive explanations (SHAP), to the trained model, which revealed which terms influence each prediction as a dark pattern.”
- Claim source `E2/analysis/claim_completion_v2/claims_future.jsonl`, paper `2401.04119v1`, claim index `3`; audit status `needs_manual_review`; `human_review=not recorded`.
- Human check: does the cited evidence support this exact claim, including its qualifiers/numbers, and is this the intended claim text? Enter no decision here until reviewed.

### 3. 2012.15525v3 — BANG: Bridging Autoregressive and Non-autoregressive Generation with Large Scale Pretraining

- Claim index `3`; request SHA-256 `0c4bc6e27997c779d6eb5326880f9b50bc58ec604f46b45a38d0d0537829ed3f`.
- Exact vector text: “BANG achieves absolute improvements of 14.01 and 5.24 in the overall scores of SQuAD 1.1 and XSum compared with semi-NAR strong baselines.”
- Row text/hash binding valid: **True**.
- Vector checksum valid: **True**; bytes `3072`; L2 norm `0.9999999821`.
- Source evidence: “Compared with the semi-NAR strong baselines, BANG achieves absolute improvements of 14.01 and 5.24 in the overall scores of SQuAD 1.1 and XSum, respectively.”
- Claim source `E2/analysis/claim_completion_v2/claims_future.jsonl`, paper `2012.15525v3`, claim index `3`; audit status `needs_manual_review`; `human_review=not recorded`.
- Human check: does the cited evidence support this exact claim, including its qualifiers/numbers, and is this the intended claim text? Enter no decision here until reviewed.

### 4. 2112.11391v1 — Voice Quality and Pitch Features in Transformer-Based Speech Recognition

- Claim index `0`; request SHA-256 `0cca22c3fb951b60aaa223cbc73e3fc671ffd973924f29df283ddd41a3b9780c`.
- Exact vector text: “Separated convolutional front-ends are proposed for prosodic and spectral features in Transformer-based ASR.”
- Row text/hash binding valid: **True**.
- Vector checksum valid: **True**; bytes `3072`; L2 norm `1.0000001169`.
- Source evidence: “For doing so, we propose separated convolutional front-ends for prosodic and spectral features, showing that this architectural choice yields better results than simple concatenation of such pitch and voice quality features to mel-spectrogram filterbanks.”
- Claim source `E2/analysis/claim_completion_v2/claims_future.jsonl`, paper `2112.11391v1`, claim index `0`; audit status `review_required_claim_count`; `human_review=not recorded`.
- Human check: does the cited evidence support this exact claim, including its qualifiers/numbers, and is this the intended claim text? Enter no decision here until reviewed.

## Required calibration review schema and checks

The encoder gate in `E2/claim_sidecar.py` reads the review JSON named by `calibration_review_path` in the authorization JSON and verifies its SHA-256 against `calibration_review_sha256`. The review JSON must include:
- `manifest_sha256`: exact SHA-256 of the frozen manifest.
- `accepted`: literal `true`, supplied only after genuine human acceptance.
- `review_source`: nonempty attributable description of the review.
- `calibration_report_path`: separate calibration report path.
- `calibration_report_sha256`: matching SHA-256 of that report.

The separate calibration report must contain a matching `manifest_sha256`, `new_vectors_generated` from 1 through 4, exactly three `parity_controls`, and positive/nonzero `process_peak_rss_bytes`. The documented protocol additionally requires elapsed timing and all three fixed parity checks to pass at `atol=1e-5`, `rtol=1e-4`; parity records should identify each control text hash and maximum absolute difference. Review source claim support above as human judgment. Some claim-source audit statuses explicitly say manual review is needed; this packet does not resolve them.

## Human decision — intentionally blank

- Decision (`accept` / `reject`): ____________________
- Reviewer / attributable source: ____________________
- Review date: ____________________
- Per-claim support decisions and notes (1–4): ____________________
- Calibration report path and hash checked: ____________________
- Manifest hash confirmed: ____________________
- Timing, peak RSS, and three parity controls reviewed: ____________________

No acceptance is asserted here. A genuine report and review must be hash-bound through the existing authorization fields before any more vectors are generated.
