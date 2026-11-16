# A1 partial-replication human-review shortlist

**Purpose:** prioritize claim review before any scoring. This is a working
shortlist, not a human review or approval. No reviewer decisions are prefilled.

**Prioritized papers:** 24  
**Claims requiring review:** 128 (all claims for these papers, not only AI-prioritized claims)  
**Prioritization rule:** at least four claims per paper are marked both
`supported` and `atomic` in the saved Copilot suggestions. This AI-derived
count is only a triage signal; it is not evidence, independent verification,
or a substitute for reviewing every claim below against the original abstract.

**Reviewer ID/code:** ____________________  **Review date:** ____________________

## Priority order

| Priority | Cohort order | Paper ID | Title | AI-suggested supported + atomic / claims |
|---:|---:|---|---|---:|
| 1 | 7 | `2512.23709v3` | Stream-DiffVSR: Low-Latency Streamable Video Super-Resolution via Auto-Regressive Diffusion | 9/9 |
| 2 | 8 | `2610.29385v1` | Parallelizable Probabilistic Latent Reasoning for Diverse Reasoning Trajectories | 7/9 |
| 3 | 9 | `2610.29361v1` | Seeing through Denoising: Frequency-guided One-step Denoising for Infrared Small Target Detection | 6/6 |
| 4 | 6 | `2610.29474v1` | Extending Affordance Segmentation for Wearable Robots to Multi-Object Images | 5/5 |
| 5 | 13 | `2512.23813v1` | StressRoBERTa: Cross-Condition Transfer Learning from Depression, Anxiety, and PTSD to Stress Detection | 5/5 |
| 6 | 22 | `2512.24289v1` | Automated Analysis of Sustainability Reports: Using Large Language Models for the Extraction and Prediction of EU Taxonomy-Compliant KPIs | 5/7 |
| 7 | 24 | `2512.23862v1` | Probing the Limits of Compressive Memory: A Study of Infini-Attention in Small-Scale Pretraining | 5/6 |
| 8 | 26 | `2512.24016v2` | FitControler: Toward Fit-Aware Virtual Try-On | 5/6 |
| 9 | 27 | `2512.24404v1` | Lifting Vision: Ground to Aerial Localization with Reasoning Guided Planning | 5/6 |
| 10 | 34 | `2512.23049v1` | Accelerating Language Model Workflows with Prompt Choreography | 5/5 |
| 11 | 3 | `2610.29559v1` | Certified Neural Approximation of Robust Nonlinear Model Predictive Control | 4/5 |
| 12 | 5 | `2512.24593v1` | 3D Semantic Segmentation for Post-Disaster Assessment | 4/4 |
| 13 | 10 | `2610.29527v1` | RCSD: Reinforcement and Continual Learning for Domain-Specific Speculative Decoding | 4/4 |
| 14 | 11 | `2610.29611v1` | Diff-IrisPAD: Modeling Bona Fide Iris Distributions for Unsupervised Presentation Attack Detection | 4/4 |
| 15 | 15 | `2610.29843v1` | Every Part Has Its Role: Part-of-Speech Effects in LLM Post-Training | 4/4 |
| 16 | 19 | `2610.29187v1` | A Decade of Learning-Based Control: From Theoretic Foundations to Practical Deployment | 4/4 |
| 17 | 25 | `2610.29441v1` | Sparsity Should Be ALLOTted by Output: Training-Free Allocation of Block-Sparse Attention for Video Diffusion Transformers | 4/6 |
| 18 | 28 | `2610.29090v1` | ReSeg: Retraining-free segmentation of abdominal organs via generalizable semantic representation learning | 4/4 |
| 19 | 31 | `2512.24780v2` | Gradient Descent as Implicit EM in Distance-Based Neural Models | 4/5 |
| 20 | 32 | `2512.24139v5` | Colorful Pinball: Density-Weighted Quantile Regression for Conditional Guarantee of Conformal Prediction | 4/4 |
| 21 | 33 | `2610.29531v1` | Phase Transitions in Learning Driven by Extremal Data | 4/6 |
| 22 | 38 | `2610.28941v1` | MINER: Modeling Inter- and Intra-Person Variance for Reidentification | 4/5 |
| 23 | 39 | `2610.29515v1` | BRIDGE: An Acceptance Gate to Block False Improvements in Model Updates, with a Retrospective Clinical Evaluation | 4/5 |
| 24 | 41 | `2610.28957v1` | Scan or Index? large Evidence Coverage, Answer Quality, and Cost in Long-Document RAG | 4/4 |

## Source abstracts and claim decisions

### 1. Stream-DiffVSR: Low-Latency Streamable Video Super-Resolution via Auto-Regressive Diffusion

- Cohort order: 7
- Paper ID: `2512.23709v3`
- Source: https://arxiv.org/abs/2512.23709v3
- Publication timestamp: 2025-12-29T18:59:57Z
- Copilot-priority count (triage only): 9/9

**Original abstract (verbatim):**

```text
Diffusion-based video super-resolution (VSR) methods deliver strong perceptual quality but are often unsuitable for latency-sensitive scenarios due to reliance on future frames and expensive multi-step denoising. We propose Stream-DiffVSR, a causally conditioned diffusion framework for efficient online VSR. Operating strictly on past frames, Stream-DiffVSR integrates a four-step distilled denoiser for fast inference, an Auto-regressive Temporal Guidance (ARTG) module that injects motion-aligned cues during latent denoising, and a lightweight temporal-aware decoder with a Temporal Processor Module (TPM) to enhance detail and temporal coherence. Unlike chunk-wise streaming inference, our strictly frame-by-frame causal design avoids sequence-level waiting, substantially reducing time-to-first-frame and end-to-end latency. Stream-DiffVSR processes 720p frames in 0.328 seconds on an RTX 4090 and consistently outperforms prior diffusion-based baselines. Compared with the online state-of-the-art TMP, it improves perceptual quality (LPIPS +0.095). Compared with prior diffusion-based VSR methods such as MGLD-VSR, it reduces per-frame runtime by over 130x. Moreover, Stream-DiffVSR substantially lowers time-to-first-frame for diffusion-based VSR, reducing initial delay from over 4600 seconds to 0.328 seconds, making diffusion-based VSR markedly more practical for low-latency online and streaming deployment. Project page: https://jamichss.github.io/stream-diffvsr-project-page/
```

#### Claim 1

**Claim (verbatim):**

```text
Stream-DiffVSR is a causally conditioned diffusion framework for efficient online video super-resolution.
```

**Evidence excerpt (verbatim):**

```text
We propose Stream-DiffVSR, a causally conditioned diffusion framework for efficient online VSR.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
Stream-DiffVSR integrates a four-step distilled denoiser for fast inference.
```

**Evidence excerpt (verbatim):**

```text
Stream-DiffVSR integrates a four-step distilled denoiser for fast inference,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
Stream-DiffVSR includes an Auto-regressive Temporal Guidance (ARTG) module that injects motion-aligned cues during latent denoising.
```

**Evidence excerpt (verbatim):**

```text
an Auto-regressive Temporal Guidance (ARTG) module that injects motion-aligned cues during latent denoising,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
Stream-DiffVSR employs a lightweight temporal-aware decoder with a Temporal Processor Module (TPM) to enhance detail and temporal coherence.
```

**Evidence excerpt (verbatim):**

```text
and a lightweight temporal-aware decoder with a Temporal Processor Module (TPM) to enhance detail and temporal coherence.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 5

**Claim (verbatim):**

```text
Stream-DiffVSR processes 720p frames in 0.328 seconds on an RTX 4090.
```

**Evidence excerpt (verbatim):**

```text
Stream-DiffVSR processes 720p frames in 0.328 seconds on an RTX 4090
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 6

**Claim (verbatim):**

```text
Stream-DiffVSR consistently outperforms prior diffusion-based baselines.
```

**Evidence excerpt (verbatim):**

```text
and consistently outperforms prior diffusion-based baselines.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 7

**Claim (verbatim):**

```text
Compared with the online state-of-the-art TMP, Stream-DiffVSR improves perceptual quality (LPIPS +0.095).
```

**Evidence excerpt (verbatim):**

```text
Compared with the online state-of-the-art TMP, it improves perceptual quality (LPIPS +0.095).
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 8

**Claim (verbatim):**

```text
Compared with prior diffusion-based VSR methods such as MGLD-VSR, Stream-DiffVSR reduces per-frame runtime by over 130x.
```

**Evidence excerpt (verbatim):**

```text
Compared with prior diffusion-based VSR methods such as MGLD-VSR, it reduces per-frame runtime by over 130x.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 9

**Claim (verbatim):**

```text
Stream-DiffVSR substantially lowers time-to-first-frame for diffusion-based VSR, reducing initial delay from over 4600 seconds to 0.328 seconds.
```

**Evidence excerpt (verbatim):**

```text
Moreover, Stream-DiffVSR substantially lowers time-to-first-frame for diffusion-based VSR, reducing initial delay from over 4600 seconds to 0.328 seconds,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 2. Parallelizable Probabilistic Latent Reasoning for Diverse Reasoning Trajectories

- Cohort order: 8
- Paper ID: `2610.29385v1`
- Source: https://arxiv.org/abs/2610.29385v1
- Publication timestamp: 2026-10-21T08:11:52Z
- Copilot-priority count (triage only): 7/9

**Original abstract (verbatim):**

```text
Language models relying on verbalized Chain-of-Thought (CoT) are constrained to token-by-token generation in the language space, where many tokens serve textual coherence rather than core reasoning. This entangles genuine differences in logical trajectories with superficial variations in verbalization. Moving reasoning into a compact, continuous latent space offers a promising alternative for efficiently representing and exploring diverse reasoning trajectories. However, current latent models remain largely deterministic, capturing only a single reasoning trajectory rather than modeling a distribution over multiple valid alternatives. While stochastic approaches parameterize distributions over latent reasoning steps, they frequently suffer from unstable optimization and limited empirical performance. Furthermore, their reliance on autoregressive latent prediction during training precludes effective parallelization, leading to prohibitively long training times. To overcome these bottlenecks, we propose Probabilistic Latent Reasoning Models (PLRM), a parallelizable variational framework for probabilistic latent reasoning. PLRM adopts a JEPA-style objective in which the posterior infers latent distributions in parallel from observed reasoning trajectories, while the prior learns to predict the subsequent latent distribution via teacher forcing. To model heterogeneous reasoning processes, we introduce a discrete strategy variable together with a mixture-based prior, allowing the model to preserve the Gaussian-mixture structure induced by multiple distinct reasoning trajectories rather than collapsing them into a single Gaussian. Across diverse benchmarks, PLRM achieves performance competitive with deterministic latent reasoning models on single-trajectory datasets while enabling efficient training and consistently outperforming competing stochastic baselines on multi-trajectory datasets.
```

#### Claim 1

**Claim (verbatim):**

```text
Language models relying on verbalized Chain-of-Thought (CoT) are constrained to token-by-token generation in the language space.
```

**Evidence excerpt (verbatim):**

```text
Language models relying on verbalized Chain-of-Thought (CoT) are constrained to token-by-token generation in the language space,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
Moving reasoning into a compact, continuous latent space offers a promising alternative for efficiently representing and exploring diverse reasoning trajectories.
```

**Evidence excerpt (verbatim):**

```text
Moving reasoning into a compact, continuous latent space offers a promising alternative for efficiently representing and exploring diverse reasoning trajectories.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
Current latent models remain largely deterministic, capturing only a single reasoning trajectory rather than modeling a distribution over multiple valid alternatives.
```

**Evidence excerpt (verbatim):**

```text
However, current latent models remain largely deterministic, capturing only a single reasoning trajectory rather than modeling a distribution over multiple valid alternatives.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
Stochastic approaches parameterize distributions over latent reasoning steps but frequently suffer from unstable optimization and limited empirical performance.
```

**Evidence excerpt (verbatim):**

```text
While stochastic approaches parameterize distributions over latent reasoning steps, they frequently suffer from unstable optimization and limited empirical performance.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 5

**Claim (verbatim):**

```text
PLRM adopts a JEPA-style objective in which the posterior infers latent distributions in parallel from observed reasoning trajectories.
```

**Evidence excerpt (verbatim):**

```text
PLRM adopts a JEPA-style objective in which the posterior infers latent distributions in parallel from observed reasoning trajectories,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 6

**Claim (verbatim):**

```text
PLRM introduces a discrete strategy variable together with a mixture-based prior to model heterogeneous reasoning processes.
```

**Evidence excerpt (verbatim):**

```text
To model heterogeneous reasoning processes, we introduce a discrete strategy variable together with a mixture-based prior,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 7

**Claim (verbatim):**

```text
PLRM preserves the Gaussian-mixture structure induced by multiple distinct reasoning trajectories rather than collapsing them into a single Gaussian.
```

**Evidence excerpt (verbatim):**

```text
allowing the model to preserve the Gaussian-mixture structure induced by multiple distinct reasoning trajectories rather than collapsing them into a single Gaussian.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 8

**Claim (verbatim):**

```text
PLRM achieves performance competitive with deterministic latent reasoning models on single-trajectory datasets.
```

**Evidence excerpt (verbatim):**

```text
Across diverse benchmarks, PLRM achieves performance competitive with deterministic latent reasoning models on single-trajectory datasets while enabling efficient training and consistently outperforming competing stochastic baselines on multi-trajectory datasets.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 9

**Claim (verbatim):**

```text
PLRM consistently outperforms competing stochastic baselines on multi-trajectory datasets.
```

**Evidence excerpt (verbatim):**

```text
Across diverse benchmarks, PLRM achieves performance competitive with deterministic latent reasoning models on single-trajectory datasets while enabling efficient training and consistently outperforming competing stochastic baselines on multi-trajectory datasets.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 3. Seeing through Denoising: Frequency-guided One-step Denoising for Infrared Small Target Detection

- Cohort order: 9
- Paper ID: `2610.29361v1`
- Source: https://arxiv.org/abs/2610.29361v1
- Publication timestamp: 2026-10-21T07:51:11Z
- Copilot-priority count (triage only): 6/6

**Original abstract (verbatim):**

```text
Infrared small target detection (IRSTD) is a challenging task due to the extremely small size of targets, low signal-to-noise ratios, and heavy background clutter in infrared imagery. While the progress of deep learning has advanced this field, existing methods primarily adopt discriminative paradigms that directly map images to target masks, overlooking the potential of generative modeling. In this paper, we propose DiffIRSTD, a novel generative framework that reformulates infrared small target detection as a background reconstruction problem. Instead of explicitly predicting target regions, we reinterpret small targets as noise-like signals and leverage a diffusion-based model to recover a clean, target-free background from a perturbed input image. The residual between the reconstructed background and the original image is then exploited to highlight candidate target regions, providing explicit cues for subsequent detection. To address the computational cost typically associated with diffusion sampling, we introduce a one-step denoising strategy that enables efficient background reconstruction while maintaining practical inference speed. Furthermore, we present a frequency-guided perception loss to preserve high-frequency background details and focus more on the reconstruction quality of target regions. More importantly, our DiffIRSTD operates as a plug-and-play framework, compatible with existing IRSTD models without increasing the computational complexity of detectors. Extensive experiments on IRSTD-1K, NUAA-SIRST, and NUDT-SIRST datasets demonstrate the superiority of our method, achieving state-of-the-art performance across three benchmarks.
```

#### Claim 1

**Claim (verbatim):**

```text
The paper proposes a novel generative framework for infrared small target detection that reformulates the task as a background reconstruction problem.
```

**Evidence excerpt (verbatim):**

```text
In this paper, we propose DiffIRSTD, a novel generative framework that reformulates infrared small target detection as a background reconstruction problem.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
The method reinterprets small targets as noise-like signals and uses a diffusion-based model to recover a clean, target-free background from a perturbed input image.
```

**Evidence excerpt (verbatim):**

```text
Instead of explicitly predicting target regions, we reinterpret small targets as noise-like signals and leverage a diffusion-based model to recover a clean, target-free background from a perturbed input image.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
The residual between the reconstructed background and the original image is used to highlight candidate target regions.
```

**Evidence excerpt (verbatim):**

```text
The residual between the reconstructed background and the original image is then exploited to highlight candidate target regions, providing explicit cues for subsequent detection.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
A frequency-guided perception loss is presented to preserve high-frequency background details and focus on the reconstruction quality of target regions.
```

**Evidence excerpt (verbatim):**

```text
Furthermore, we present a frequency-guided perception loss to preserve high-frequency background details and focus more on the reconstruction quality of target regions.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 5

**Claim (verbatim):**

```text
The proposed framework is compatible with existing IRSTD models without increasing the computational complexity of detectors.
```

**Evidence excerpt (verbatim):**

```text
More importantly, our DiffIRSTD operates as a plug-and-play framework, compatible with existing IRSTD models without increasing the computational complexity of detectors.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 6

**Claim (verbatim):**

```text
Extensive experiments on IRSTD-1K, NUAA-SIRST, and NUDT-SIRST datasets demonstrate the superiority of the method, achieving state-of-the-art performance across three benchmarks.
```

**Evidence excerpt (verbatim):**

```text
Extensive experiments on IRSTD-1K, NUAA-SIRST, and NUDT-SIRST datasets demonstrate the superiority of our method, achieving state-of-the-art performance across three benchmarks.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 4. Extending Affordance Segmentation for Wearable Robots to Multi-Object Images

- Cohort order: 6
- Paper ID: `2610.29474v1`
- Source: https://arxiv.org/abs/2610.29474v1
- Publication timestamp: 2026-10-21T09:30:14Z
- Copilot-priority count (triage only): 5/5

**Original abstract (verbatim):**

```text
This paper proposes a refinement to existing vision-based portable pipelines for the recognition of graspable object parts. Such pipelines can effectively support automatic grasp selection and preshaping in upper-limb prosthetic devices. However, realistic scenarios in which multiple objects are present still represent a challenge. The proposed method exploits a minor modification to the conventional hardware setup and a custom training approach to extend the applicability of vision-based pipelines. A laser pointer is introduced in the setup as an effective mechanism for object disambiguation. Accordingly, a suitable retraining of the deep convolutional neural networks supporting recognition of graspable parts is implemented. A mixed reality strategy allows the reuse of available high-quality segmentation masks to generate realistic images procedurally, extending the range of scenarios supported by the final device. Experimental results confirm that the proposed pipeline improves target disambiguation accuracy by up to 9% compared with existing solutions, while preserving the computational cost.
```

#### Claim 1

**Claim (verbatim):**

```text
The proposed method improves target disambiguation accuracy by up to 9% compared with existing solutions.
```

**Evidence excerpt (verbatim):**

```text
Experimental results confirm that the proposed pipeline improves target disambiguation accuracy by up to 9% compared with existing solutions
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
A laser pointer is introduced as an effective mechanism for object disambiguation in the hardware setup.
```

**Evidence excerpt (verbatim):**

```text
A laser pointer is introduced in the setup as an effective mechanism for object disambiguation.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
The method involves a minor modification to the conventional hardware setup.
```

**Evidence excerpt (verbatim):**

```text
The proposed method exploits a minor modification to the conventional hardware setup
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
A custom training approach is implemented to extend the applicability of vision-based pipelines.
```

**Evidence excerpt (verbatim):**

```text
and a custom training approach to extend the applicability of vision-based pipelines.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 5

**Claim (verbatim):**

```text
A mixed reality strategy allows the reuse of high-quality segmentation masks to generate realistic images procedurally.
```

**Evidence excerpt (verbatim):**

```text
A mixed reality strategy allows the reuse of available high-quality segmentation masks to generate realistic images procedurally
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 5. StressRoBERTa: Cross-Condition Transfer Learning from Depression, Anxiety, and PTSD to Stress Detection

- Cohort order: 13
- Paper ID: `2512.23813v1`
- Source: https://arxiv.org/abs/2512.23813v1
- Publication timestamp: 2025-12-29T19:16:14Z
- Copilot-priority count (triage only): 5/5

**Original abstract (verbatim):**

```text
The prevalence of chronic stress represents a significant public health concern, with social media platforms like Twitter serving as important venues for individuals to share their experiences. This paper introduces StressRoBERTa, a cross-condition transfer learning approach for automatic detection of self-reported chronic stress in English tweets. The investigation examines whether continual training on clinically related conditions (depression, anxiety, PTSD), disorders with high comorbidity with chronic stress, improves stress detection compared to general language models and broad mental health models. RoBERTa is continually trained on the Stress-SMHD corpus (108M words from users with self-reported diagnoses of depression, anxiety, and PTSD) and fine-tuned on the SMM4H 2022 Task 8 dataset. StressRoBERTa achieves 82% F1-score, outperforming the best shared task system (79% F1) by 3 percentage points. The results demonstrate that focused cross-condition transfer from stress-related disorders (+1% F1 over vanilla RoBERTa) provides stronger representations than general mental health training. Evaluation on Dreaddit (81% F1) further demonstrates transfer from clinical mental health contexts to situational stress discussions.
```

#### Claim 1

**Claim (verbatim):**

```text
StressRoBERTa is a cross-condition transfer learning approach for automatic detection of self-reported chronic stress in English tweets.
```

**Evidence excerpt (verbatim):**

```text
This paper introduces StressRoBERTa, a cross-condition transfer learning approach for automatic detection of self-reported chronic stress in English tweets.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
Continual training on clinically related conditions (depression, anxiety, PTSD) improves stress detection compared to general language models and broad mental health models.
```

**Evidence excerpt (verbatim):**

```text
The investigation examines whether continual training on clinically related conditions (depression, anxiety, PTSD), disorders with high comorbidity with chronic stress, improves stress detection compared to general language models and broad mental health models.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
StressRoBERTa achieves an F1-score of 82%, outperforming the best shared task system by 3 percentage points.
```

**Evidence excerpt (verbatim):**

```text
StressRoBERTa achieves 82% F1-score, outperforming the best shared task system (79% F1) by 3 percentage points.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
Focused cross-condition transfer from stress-related disorders provides stronger representations than general mental health training.
```

**Evidence excerpt (verbatim):**

```text
The results demonstrate that focused cross-condition transfer from stress-related disorders (+1% F1 over vanilla RoBERTa) provides stronger representations than general mental health training.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 5

**Claim (verbatim):**

```text
Evaluation on Dreaddit shows that transfer from clinical mental health contexts to situational stress discussions achieves an F1-score of 81%.
```

**Evidence excerpt (verbatim):**

```text
Evaluation on Dreaddit (81% F1) further demonstrates transfer from clinical mental health contexts to situational stress discussions.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 6. Automated Analysis of Sustainability Reports: Using Large Language Models for the Extraction and Prediction of EU Taxonomy-Compliant KPIs

- Cohort order: 22
- Paper ID: `2512.24289v1`
- Source: https://arxiv.org/abs/2512.24289v1
- Publication timestamp: 2025-12-30T15:28:03Z
- Copilot-priority count (triage only): 5/7

**Original abstract (verbatim):**

```text
The manual, resource-intensive process of complying with the EU Taxonomy presents a significant challenge for companies. While Large Language Models (LLMs) offer a path to automation, research is hindered by a lack of public benchmark datasets. To address this gap, we introduce a novel, structured dataset from 190 corporate reports, containing ground-truth economic activities and quantitative Key Performance Indicators (KPIs). We use this dataset to conduct the first systematic evaluation of LLMs on the core compliance workflow. Our results reveal a clear performance gap between qualitative and quantitative tasks. LLMs show moderate success in the qualitative task of identifying economic activities, with a multi-step agentic framework modestly enhancing precision. Conversely, the models comprehensively fail at the quantitative task of predicting financial KPIs in a zero-shot setting. We also discover a paradox, where concise metadata often yields superior performance to full, unstructured reports, and find that model confidence scores are poorly calibrated. We conclude that while LLMs are not ready for full automation, they can serve as powerful assistive tools for human experts. Our dataset provides a public benchmark for future research.
```

#### Claim 1

**Claim (verbatim):**

```text
A structured dataset containing ground-truth economic activities and quantitative Key Performance Indicators (KPIs) is introduced from 190 corporate reports.
```

**Evidence excerpt (verbatim):**

```text
To address this gap, we introduce a novel, structured dataset from 190 corporate reports, containing ground-truth economic activities and quantitative Key Performance Indicators (KPIs).
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
The first systematic evaluation of LLMs on the core compliance workflow is conducted using the introduced dataset.
```

**Evidence excerpt (verbatim):**

```text
We use this dataset to conduct the first systematic evaluation of LLMs on the core compliance workflow.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
LLMs show moderate success in the qualitative task of identifying economic activities, with a multi-step agentic framework modestly enhancing precision.
```

**Evidence excerpt (verbatim):**

```text
LLMs show moderate success in the qualitative task of identifying economic activities, with a multi-step agentic framework modestly enhancing precision.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
LLMs comprehensively fail at the quantitative task of predicting financial KPIs in a zero-shot setting.
```

**Evidence excerpt (verbatim):**

```text
Conversely, the models comprehensively fail at the quantitative task of predicting financial KPIs in a zero-shot setting.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 5

**Claim (verbatim):**

```text
A paradox is discovered where concise metadata often yields superior performance to full, unstructured reports.
```

**Evidence excerpt (verbatim):**

```text
We also discover a paradox, where concise metadata often yields superior performance to full, unstructured reports,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 6

**Claim (verbatim):**

```text
Model confidence scores are found to be poorly calibrated.
```

**Evidence excerpt (verbatim):**

```text
and find that model confidence scores are poorly calibrated.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 7

**Claim (verbatim):**

```text
LLMs are concluded to be not ready for full automation but can serve as powerful assistive tools for human experts.
```

**Evidence excerpt (verbatim):**

```text
We conclude that while LLMs are not ready for full automation, they can serve as powerful assistive tools for human experts.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 7. Probing the Limits of Compressive Memory: A Study of Infini-Attention in Small-Scale Pretraining

- Cohort order: 24
- Paper ID: `2512.23862v1`
- Source: https://arxiv.org/abs/2512.23862v1
- Publication timestamp: 2025-12-29T21:02:14Z
- Copilot-priority count (triage only): 5/6

**Original abstract (verbatim):**

```text
This study investigates small-scale pretraining for Small Language Models (SLMs) to enable efficient use of limited data and compute, improve accessibility in low-resource settings and reduce costs. To enhance long-context extrapolation in compact models, we focus on Infini-attention, which builds a compressed memory from past segments while preserving local attention. In our work, we conduct an empirical study using 300M-parameter LLaMA models pretrained with Infini-attention. The model demonstrates training stability and outperforms the baseline in long-context retrieval. We identify the balance factor as a key part of the model performance, and we found that retrieval accuracy drops with repeated memory compressions over long sequences. Even so, Infini-attention still effectively compensates for the SLM's limited parameters. Particularly, despite performance degradation at a 16,384-token context, the Infini-attention model achieves up to 31% higher accuracy than the baseline. Our findings suggest that achieving robust long-context capability in SLMs benefits from architectural memory like Infini-attention.
```

#### Claim 1

**Claim (verbatim):**

```text
Infini-attention enables compact models to maintain training stability and outperform baselines in long-context retrieval.
```

**Evidence excerpt (verbatim):**

```text
The model demonstrates training stability and outperforms the baseline in long-context retrieval.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
The balance factor is identified as a critical component influencing model performance.
```

**Evidence excerpt (verbatim):**

```text
We identify the balance factor as a key part of the model performance,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
Repeated memory compressions over long sequences lead to a decline in retrieval accuracy.
```

**Evidence excerpt (verbatim):**

```text
we found that retrieval accuracy drops with repeated memory compressions over long sequences.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
Infini-attention compensates for the limited parameters of Small Language Models (SLMs) in long-context tasks.
```

**Evidence excerpt (verbatim):**

```text
Infini-attention still effectively compensates for the SLM's limited parameters.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 5

**Claim (verbatim):**

```text
Infini-attention achieves up to 31% higher accuracy than the baseline in long-context retrieval tasks.
```

**Evidence excerpt (verbatim):**

```text
the Infini-attention model achieves up to 31% higher accuracy than the baseline.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 6

**Claim (verbatim):**

```text
Infini-attention contributes to achieving robust long-context capability in Small Language Models (SLMs).
```

**Evidence excerpt (verbatim):**

```text
Our findings suggest that achieving robust long-context capability in SLMs benefits from architectural memory like Infini-attention.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 8. FitControler: Toward Fit-Aware Virtual Try-On

- Cohort order: 26
- Paper ID: `2512.24016v2`
- Source: https://arxiv.org/abs/2512.24016v2
- Publication timestamp: 2025-12-30T06:31:19Z
- Copilot-priority count (triage only): 5/6

**Original abstract (verbatim):**

```text
Realistic virtual try-on (VTON) concerns not only faithful rendering of garment details but also coordination of the style. Prior art typically pursues the former, but neglects a key factor that shapes the holistic style -- garment fit. Garment fit delineates how a garment aligns with the body of a wearer and is a fundamental element in fashion design. In this work, we introduce fit-aware VTON and present FitControler, a learnable plug-in that can seamlessly integrate into modern VTON models to enable customized fit control. To achieve this, we highlight two challenges: i) how to delineate layouts of different fits and ii) how to render the garment that matches the layout. FitControler first features a fit-aware layout generator to redraw the body-garment layout conditioned on a set of delicately processed garment-agnostic representations, and a multi-scale fit injector is then used to deliver layout cues to enable layout-driven VTON. In particular, we build a fit-aware VTON dataset termed Fit4Men, including 13,000 body-garment pairs of different fits, covering both tops and bottoms, and featuring varying camera distances and body poses. Two fit consistency metrics are also introduced to assess the fitness of generations. Extensive experiments show that FitControler can work with various VTON models and achieve accurate fit control. Code and data will be released.
```

#### Claim 1

**Claim (verbatim):**

```text
FitControler is a learnable plug-in that can seamlessly integrate into modern VTON models to enable customized fit control.
```

**Evidence excerpt (verbatim):**

```text
we introduce fit-aware VTON and present FitControler, a learnable plug-in that can seamlessly integrate into modern VTON models to enable customized fit control.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
FitControler features a fit-aware layout generator to redraw the body-garment layout conditioned on a set of delicately processed garment-agnostic representations.
```

**Evidence excerpt (verbatim):**

```text
FitControler first features a fit-aware layout generator to redraw the body-garment layout conditioned on a set of delicately processed garment-agnostic representations,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
FitControler uses a multi-scale fit injector to deliver layout cues to enable layout-driven VTON.
```

**Evidence excerpt (verbatim):**

```text
and a multi-scale fit injector is then used to deliver layout cues to enable layout-driven VTON.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
A fit-aware VTON dataset termed Fit4Men is built, including 13,000 body-garment pairs of different fits, covering both tops and bottoms, and featuring varying camera distances and body poses.
```

**Evidence excerpt (verbatim):**

```text
we build a fit-aware VTON dataset termed Fit4Men, including 13,000 body-garment pairs of different fits, covering both tops and bottoms, and featuring varying camera distances and body poses.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 5

**Claim (verbatim):**

```text
Two fit consistency metrics are introduced to assess the fitness of generations.
```

**Evidence excerpt (verbatim):**

```text
Two fit consistency metrics are also introduced to assess the fitness of generations.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 6

**Claim (verbatim):**

```text
Extensive experiments show that FitControler can work with various VTON models and achieve accurate fit control.
```

**Evidence excerpt (verbatim):**

```text
Extensive experiments show that FitControler can work with various VTON models and achieve accurate fit control.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 9. Lifting Vision: Ground to Aerial Localization with Reasoning Guided Planning

- Cohort order: 27
- Paper ID: `2512.24404v1`
- Source: https://arxiv.org/abs/2512.24404v1
- Publication timestamp: 2025-12-30T18:36:39Z
- Copilot-priority count (triage only): 5/6

**Original abstract (verbatim):**

```text
Multimodal intelligence development recently show strong progress in visual understanding and high level reasoning. Though, most reasoning system still reply on textual information as the main medium for inference. This limit their effectiveness in spatial tasks such as visual navigation and geo-localization. This work discuss about the potential scope of this field and eventually propose an idea visual reasoning paradigm Geo-Consistent Visual Planning, our introduced framework called Visual Reasoning for Localization, or ViReLoc, which performs planning and localization using only visual representations. The proposed framework learns spatial dependencies and geometric relations that text based reasoning often suffer to understand. By encoding step by step inference in the visual domain and optimizing with reinforcement based objectives, ViReLoc plans routes between two given ground images. The system also integrates contrastive learning and adaptive feature interaction to align cross view perspectives and reduce viewpoint differences. Experiments across diverse navigation and localization scenarios show consistent improvements in spatial reasoning accuracy and cross view retrieval performance. These results establish visual reasoning as a strong complementary approach for navigation and localization, and show that such tasks can be performed without real time global positioning system data, leading to more secure navigation solutions.
```

#### Claim 1

**Claim (verbatim):**

```text
The proposed framework, ViReLoc, performs planning and localization using only visual representations.
```

**Evidence excerpt (verbatim):**

```text
The proposed framework learns spatial dependencies and geometric relations that text based reasoning often suffer to understand.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
ViReLoc encodes step by step inference in the visual domain and optimizes with reinforcement based objectives.
```

**Evidence excerpt (verbatim):**

```text
By encoding step by step inference in the visual domain and optimizing with reinforcement based objectives, ViReLoc plans routes between two given ground images.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
ViReLoc integrates contrastive learning and adaptive feature interaction to align cross view perspectives and reduce viewpoint differences.
```

**Evidence excerpt (verbatim):**

```text
The system also integrates contrastive learning and adaptive feature interaction to align cross view perspectives and reduce viewpoint differences.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
Experiments across diverse navigation and localization scenarios show consistent improvements in spatial reasoning accuracy and cross view retrieval performance.
```

**Evidence excerpt (verbatim):**

```text
Experiments across diverse navigation and localization scenarios show consistent improvements in spatial reasoning accuracy and cross view retrieval performance.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 5

**Claim (verbatim):**

```text
The results establish visual reasoning as a strong complementary approach for navigation and localization.
```

**Evidence excerpt (verbatim):**

```text
These results establish visual reasoning as a strong complementary approach for navigation and localization,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 6

**Claim (verbatim):**

```text
The proposed approach enables tasks to be performed without real time global positioning system data.
```

**Evidence excerpt (verbatim):**

```text
and show that such tasks can be performed without real time global positioning system data, leading to more secure navigation solutions.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 10. Accelerating Language Model Workflows with Prompt Choreography

- Cohort order: 34
- Paper ID: `2512.23049v1`
- Source: https://arxiv.org/abs/2512.23049v1
- Publication timestamp: 2025-12-28T19:21:11Z
- Copilot-priority count (triage only): 5/5

**Original abstract (verbatim):**

```text
Large language models are increasingly deployed in multi-agent workflows. We introduce Prompt Choreography, a framework that efficiently executes LLM workflows by maintaining a dynamic, global KV cache. Each LLM call can attend to an arbitrary, reordered subset of previously encoded messages. Parallel calls are supported. Though caching messages' encodings sometimes gives different results from re-encoding them in a new context, we show in diverse settings that fine-tuning the LLM to work with the cache can help it mimic the original results. Prompt Choreography significantly reduces per-message latency (2.0--6.2$\times$ faster time-to-first-token) and achieves substantial end-to-end speedups ($>$2.2$\times$) in some workflows dominated by redundant computation.
```

#### Claim 1

**Claim (verbatim):**

```text
Prompt Choreography introduces a framework that efficiently executes LLM workflows by maintaining a dynamic, global KV cache.
```

**Evidence excerpt (verbatim):**

```text
We introduce Prompt Choreography, a framework that efficiently executes LLM workflows by maintaining a dynamic, global KV cache.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
Each LLM call in Prompt Choreography can attend to an arbitrary, reordered subset of previously encoded messages.
```

**Evidence excerpt (verbatim):**

```text
Each LLM call can attend to an arbitrary, reordered subset of previously encoded messages.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
Prompt Chore, Choreography supports parallel calls in LLM workflows.
```

**Evidence excerpt (verbatim):**

```text
Parallel calls are supported.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
Caching messages' encodings sometimes gives different results from re-encoding them in a new context.
```

**Evidence excerpt (verbatim):**

```text
Though caching messages' encodings sometimes gives different results from re-encoding them in a new context, we show in diverse settings that fine-tuning the LLM to work with the cache can help it mimic the original results.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 5

**Claim (verbatim):**

```text
Fine-tuning the LLM to work with the cache can help it mimic the original results of re-encoding messages in a new context.
```

**Evidence excerpt (verbatim):**

```text
Though caching messages' encodings sometimes gives different results from re-encoding them in a new context, we show in diverse settings that fine-tuning the LLM to work with the cache can help it mimic the original results.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 11. Certified Neural Approximation of Robust Nonlinear Model Predictive Control

- Cohort order: 3
- Paper ID: `2610.29559v1`
- Source: https://arxiv.org/abs/2610.29559v1
- Publication timestamp: 2026-10-21T10:46:55Z
- Copilot-priority count (triage only): 4/5

**Original abstract (verbatim):**

```text
Model predictive control is a high-performance control method, but it incurs comparatively high online computational costs across many control tasks and is challenging to realize in low-level hardware settings. To address this, we present a framework for generating neural network controllers that provably inherit the safety and stability guarantees of a robust model predictive policy. In contrast to approaches based on post-verification or additional online safety filters, our method provides constructive, a priori design conditions that ensure preservation of recursive feasibility and stability before deployment. We treat the approximation error as a bounded input disturbance, which is addressed in the MPC design. This allows the neural network controller to directly inherit robustness from the underlying model predictive controller, which enables the transfer of guarantees to the approximation. The design process is an offline, constructive synthesis pipeline and can be implemented once Lipschitz bounds are specified. We further demonstrate in simulation that the learned controller reproduces the closed-loop behavior of the original controller while reducing online computation.
```

#### Claim 1

**Claim (verbatim):**

```text
A framework is presented for generating neural network controllers that provably inherit the safety and stability guarantees of a robust model predictive policy.
```

**Evidence excerpt (verbatim):**

```text
we present a framework for generating neural network controllers that provably inherit the safety and stability guarantees of a robust model predictive policy.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
The method provides constructive, a priori design conditions that ensure preservation of recursive feasibility and stability before deployment.
```

**Evidence excerpt (verbatim):**

```text
our method provides constructive, a priori design conditions that ensure preservation of recursive feasibility and stability before deployment.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
The approximation error is treated as a bounded input disturbance, which is addressed in the MPC design.
```

**Evidence excerpt (verbatim):**

```text
We treat the approximation error as a bounded input disturbance, which is addressed in the MPC design.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
The design process is an offline, constructive synthesis pipeline and can be implemented once Lipschitz bounds are specified.
```

**Evidence excerpt (verbatim):**

```text
The design process is an offline, constructive synthesis pipeline and can be implemented once Lipschitz bounds are specified.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 5

**Claim (verbatim):**

```text
The learned controller reproduces the closed-loop behavior of the original controller while reducing online computation.
```

**Evidence excerpt (verbatim):**

```text
We further demonstrate in simulation that the learned controller reproduces the closed-loop behavior of the original controller while reducing online computation.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 12. 3D Semantic Segmentation for Post-Disaster Assessment

- Cohort order: 5
- Paper ID: `2512.24593v1`
- Source: https://arxiv.org/abs/2512.24593v1
- Publication timestamp: 2025-12-31T03:30:58Z
- Copilot-priority count (triage only): 4/4

**Original abstract (verbatim):**

```text
The increasing frequency of natural disasters poses severe threats to human lives and leads to substantial economic losses. While 3D semantic segmentation is crucial for post-disaster assessment, existing deep learning models lack datasets specifically designed for post-disaster environments. To address this gap, we constructed a specialized 3D dataset using unmanned aerial vehicles (UAVs)-captured aerial footage of Hurricane Ian (2022) over affected areas, employing Structure-from-Motion (SfM) and Multi-View Stereo (MVS) techniques to reconstruct 3D point clouds. We evaluated the state-of-the-art (SOTA) 3D semantic segmentation models, Fast Point Transformer (FPT), Point Transformer v3 (PTv3), and OA-CNNs on this dataset, exposing significant limitations in existing methods for disaster-stricken regions. These findings underscore the urgent need for advancements in 3D segmentation techniques and the development of specialized 3D benchmark datasets to improve post-disaster scene understanding and response.
```

#### Claim 1

**Claim (verbatim):**

```text
A specialized 3D dataset was constructed using UAVs-captured aerial footage of Hurricane Ian.
```

**Evidence excerpt (verbatim):**

```text
To address this gap, we constructed a specialized 3D dataset using unmanned aerial vehicles (UAVs)-captured aerial footage of Hurricane Ian (2022) over affected areas
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
Structure-from-Motion and Multi-View Stereo techniques were employed to reconstruct 3D point clouds.
```

**Evidence excerpt (verbatim):**

```text
employing Structure-from-Motion (SfM) and Multi-View Stereo (MVS) techniques to reconstruct 3D point clouds
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
State-of-the-art 3D semantic segmentation models were evaluated on the constructed dataset.
```

**Evidence excerpt (verbatim):**

```text
We evaluated the state-of-the-art (SOTA) 3D semantic segmentation models, Fast Point Transformer (FPT), Point Transformer v3 (PTv3), and OA-CNNs on this dataset
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
Existing methods showed significant limitations in disaster-stricken regions.
```

**Evidence excerpt (verbatim):**

```text
exposing significant limitations in existing methods for disaster-stricken regions
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 13. RCSD: Reinforcement and Continual Learning for Domain-Specific Speculative Decoding

- Cohort order: 10
- Paper ID: `2610.29527v1`
- Source: https://arxiv.org/abs/2610.29527v1
- Publication timestamp: 2026-10-21T10:16:23Z
- Copilot-priority count (triage only): 4/4

**Original abstract (verbatim):**

```text
Speculative decoding accelerates large language model inference by employing a compact draft model to propose candidate tokens that are verified in parallel by a target model. Conventional training relies on soft-label distillation, which forces the draft model to mimic the target's full output distribution, including high-entropy regions that degrade acceptance rates and increase early rejection risk. We propose RCSD (Reinforcement and Continual Learning for Speculative Decoding), a training framework that aligns draft model optimization with the system-level objective of maximizing acceptance length. RCSD leverages naturally occurring accepted and rejected sequences during speculative inference to construct implicit preference pairs, with masked loss to avoid penalizing target-aligned tokens. Evaluated across multiple benchmarks, RCSD improves average acceptance length by 35% over HASS and achieves 1.35x faster end-to-end inference than HASS on practical workloads, without compromising generation quality.
```

#### Claim 1

**Claim (verbatim):**

```text
RCSD is a training framework that aligns draft model optimization with the system-level objective of maximizing acceptance length.
```

**Evidence excerpt (verbatim):**

```text
We propose RCSD (Reinforcement and Continual Learning for Speculative Decoding), a training framework that aligns draft model optimization with the system-level objective of maximizing acceptance length.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
RCSD constructs implicit preference pairs using naturally occurring accepted and rejected sequences during speculative inference.
```

**Evidence excerpt (verbatim):**

```text
RCSD leverages naturally occurring accepted and rejected sequences during speculative inference to construct implicit preference pairs, with masked loss to avoid penalizing target-aligned tokens.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
RCSD improves average acceptance length by 35% over HASS.
```

**Evidence excerpt (verbatim):**

```text
Evaluated across multiple benchmarks, RCSD improves average acceptance length by 35% over HASS and achieves 1.35x faster end-to-end inference than HASS on practical workloads, without compromising generation quality.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
RCSD achieves 1.35x faster end-to-end inference than HASS on practical workloads.
```

**Evidence excerpt (verbatim):**

```text
Evaluated across multiple benchmarks, RCSD improves average acceptance length by 35% over HASS and achieves 1.35x faster end-to-end inference than HASS on practical workloads, without compromising generation quality.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 14. Diff-IrisPAD: Modeling Bona Fide Iris Distributions for Unsupervised Presentation Attack Detection

- Cohort order: 11
- Paper ID: `2610.29611v1`
- Source: https://arxiv.org/abs/2610.29611v1
- Publication timestamp: 2026-10-21T11:51:28Z
- Copilot-priority count (triage only): 4/4

**Original abstract (verbatim):**

```text
Iris recognition systems are vulnerable to presentation attacks (PAs), including textured contact lenses, print replays, and synthetic irises. Existing PAD methods rely on supervised learning with attack data, limiting generalization to unseen attacks and new sensors. We propose Diff-IrisPAD, an unsupervised framework based on Brownian Bridge Diffusion that models bona fide iris distributions without using attack samples. The method reconstructs clean iris textures from degraded inputs and detects attacks via reconstruction inconsistency using ViT scoring and pixel-level measures. Experiments on a large-scale multi-sensor dataset (125K+ images, NIR and VIS, 8 attack types) show that Diff-IrisPAD achieves an overall ACER of 30.52, significantly outperforming diffusion-based baselines while demonstrating strong generalization to unseen attacks. These results highlight the effectiveness of diffusion-based bona fide modeling for robust and scalable iris PAD.
```

#### Claim 1

**Claim (verbatim):**

```text
Diff-IrisPAD is an unsupervised framework that models bona fide iris distributions without using attack samples.
```

**Evidence excerpt (verbatim):**

```text
We propose Diff-IrisPAD, an unsupervised framework based on Brownian Bridge Diffusion that models bona fide iris distributions without using attack samples.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
Diff-IrisPAD detects presentation attacks by identifying reconstruction inconsistency from degraded inputs.
```

**Evidence excerpt (verbatim):**

```text
The method reconstructs clean iris textures from degraded inputs and detects attacks via reconstruction inconsistency using ViT scoring and pixel-level measures.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
Diff-IrisPAD significantly outperforms diffusion-based baselines in performance.
```

**Evidence excerpt (verbatim):**

```text
Diff-IrisPAD achieves an overall ACER of 30.52, significantly outperforming diffusion-based baselines while demonstrating strong generalization to unseen attacks.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
Diff-IrisPAD demonstrates strong generalization to unseen attacks.
```

**Evidence excerpt (verbatim):**

```text
Diff-IrisPAD achieves an overall ACER of 30.52, significantly outperforming diffusion-based baselines while demonstrating strong generalization to unseen attacks.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 15. Every Part Has Its Role: Part-of-Speech Effects in LLM Post-Training

- Cohort order: 15
- Paper ID: `2610.29843v1`
- Source: https://arxiv.org/abs/2610.29843v1
- Publication timestamp: 2026-10-21T15:05:51Z
- Copilot-priority count (triage only): 4/4

**Original abstract (verbatim):**

```text
Large language models are typically trained with next-token prediction (NTP), which rewards predicting specific tokens rather than explicitly accounting for the semantic similarities between different words or expressions. Prior work has addressed this limitation by augmenting training data with minimally varying sentences that replace a target word with conceptually related alternatives, e.g., "The tired coach ran home" $\rightarrow$ {"The tired trainer ran home", "The tired instructor ran home", ...}. Such concept augmentation improves performance, but it remains unclear whether its effectiveness depends on where in the sentence the concept is expressed. We reproduce and extend prior work $\textit{beyond nouns}$ to verbs and adjectives, asking whether the part of speech (POS) carrying the concept signal affects perplexity and downstream performance. We find different patterns across evaluation settings: concept augmentation improves perplexity most consistently on news, independent of the POS used, whereas verbs provide the most reliable downstream gains. Despite these behavioral differences, representational analyses using CKA and linear probing show that the conditions yielding the largest downstream gains are not necessarily those that most alter the model's internal representations. Together, these results suggest that the effectiveness of concept augmentation depends on where and how conceptual information is introduced during training.
```

#### Claim 1

**Claim (verbatim):**

```text
Concept augmentation improves perplexity most consistently on news, independent of the part of speech used.
```

**Evidence excerpt (verbatim):**

```text
concept augmentation improves performance, but it remains unclear whether its effectiveness depends on where in the sentence the concept is expressed.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
Verbs provide the most reliable downstream gains from concept augmentation.
```

**Evidence excerpt (verbatim):**

```text
We find different patterns across evaluation settings: concept augmentation improves perplexity most consistently on news, independent of the POS used, whereas verbs provide the most reliable downstream gains.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
Representational analyses using CKA and linear probing show that the conditions yielding the largest downstream gains are not necessarily those that most alter the model's internal representations.
```

**Evidence excerpt (verbatim):**

```text
representational analyses using CKA and linear probing show that the conditions yielding the largest downstream gains are not necessarily those that most alter the model's internal representations.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
The effectiveness of concept augmentation depends on where and how conceptual information is introduced during training.
```

**Evidence excerpt (verbatim):**

```text
Together, these results suggest that the effectiveness of concept augmentation depends on where and how conceptual information is introduced during training.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 16. A Decade of Learning-Based Control: From Theoretic Foundations to Practical Deployment

- Cohort order: 19
- Paper ID: `2610.29187v1`
- Source: https://arxiv.org/abs/2610.29187v1
- Publication timestamp: 2026-10-21T04:18:47Z
- Copilot-priority count (triage only): 4/4

**Original abstract (verbatim):**

```text
Motivated by ten years of Learning-Based Control Invited Sessions at the IEEE Conference on Decision and Control (CDC), this tutorial paper reviews key advances at the intersection of machine learning and control. We focus on methods that combine the flexibility of machine learning techniques with the structure and theoretical foundations of control to design autonomous systems that are capable, reliable, and safe. We first introduce core notions for establishing stability and safety guarantees, then review approaches that learn dynamics models to improve control under uncertainty, and finally discuss data-driven methods that directly synthesize or learn policies, including reinforcement learning, imitation learning, and Bayesian optimization. We further discuss representative applications and open challenges. The goal is to provide an accessible entry point to the field and to support continued progress toward reliable learning-based control in real-world systems. To support learning and practical exploration, we share implementations and illustrative examples along with our discussion, together with additional resources on our website: https://learning-based-control.github.io/tutorial/.
```

#### Claim 1

**Claim (verbatim):**

```text
This tutorial paper reviews key advances at the intersection of machine learning and control.
```

**Evidence excerpt (verbatim):**

```text
this tutorial paper reviews key advances at the intersection of machine learning and control.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
The paper focuses on methods that combine the flexibility of machine learning techniques with the structure and theoretical foundations of control.
```

**Evidence excerpt (verbatim):**

```text
We focus on methods that combine the flexibility of machine learning techniques with the structure and theoretical foundations of control to design autonomous systems that are capable, reliable, and safe.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
The paper introduces core notions for establishing stability and safety guarantees.
```

**Evidence excerpt (verbatim):**

```text
We first introduce core notions for establishing stability and safety guarantees
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
The paper reviews approaches that learn dynamics models to improve control under uncertainty.
```

**Evidence excerpt (verbatim):**

```text
then review approaches that learn dynamics models to improve control under uncertainty
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 17. Sparsity Should Be ALLOTted by Output: Training-Free Allocation of Block-Sparse Attention for Video Diffusion Transformers

- Cohort order: 25
- Paper ID: `2610.29441v1`
- Source: https://arxiv.org/abs/2610.29441v1
- Publication timestamp: 2026-10-21T09:01:48Z
- Copilot-priority count (triage only): 4/6

**Original abstract (verbatim):**

```text
Full 3D attention is costly in video Diffusion Transformers. Block-sparse attention reduces this cost by computing only selected attention blocks. However, existing methods either overlook the potential to optimize sparsity allocation or rely on heuristic rules or local metrics to guide it. In this work, we observe that sparsifying attention in different layers and at different denoising steps affects final-video fidelity to substantially different degrees. Yet the identities of the most sensitive layer-step pairs remain nearly unchanged across inputs. Building on these findings, we propose Allocating Layer-step Latency by Output Tests (ALLOT), a training-free sparsity allocation method. Treating each layer-step pair as a cell, ALLOT estimates each cell's contribution to final-video error through (i) cell probing and (ii) trajectory calibration, then jointly optimizes cell densities under a measured-latency budget. It preserves existing selection strategies and kernels, replacing only the allocation component. At equal or shorter wall-clock time, ALLOT outperforms every compared allocation strategy with XAttention, with an 11.8 dB PSNR gain on HunyuanVideo. Extensive experiments across four additional published pipelines on Wan2.1, Wan2.2, and HunyuanVideo show that ALLOT outperforms or ties the default in all nine settings.
```

#### Claim 1

**Claim (verbatim):**

```text
Block-sparse attention reduces computational cost in video Diffusion Transformers by computing only selected attention blocks.
```

**Evidence excerpt (verbatim):**

```text
Full 3D attention is costly in video Diffusion Transformers. Block-sparse attention reduces this cost by computing only selected attention blocks.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
Existing methods for sparsity allocation in attention either overlook the potential to optimize sparsity allocation or rely on heuristic rules or local metrics.
```

**Evidence excerpt (verbatim):**

```text
However, existing methods either overlook the potential to optimize sparsity allocation or rely on heuristic rules or local metrics to guide it.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
ALLOT is a training-free sparsity allocation method that estimates each layer-step pair's contribution to final-video error through cell probing and trajectory calibration.
```

**Evidence excerpt (verbatim):**

```text
Building on these findings, we propose Allocating Layer-step Latency by Output Tests (ALLOT), a training-free sparsity allocation method. Treating each layer-step pair as a cell, ALLOT estimates each cell's contribution to final-video error through (i) cell probing and (ii) trajectory calibration
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
ALLOT jointly optimizes cell densities under a measured-latency budget while preserving existing selection strategies and kernels.
```

**Evidence excerpt (verbatim):**

```text
then jointly optimizes cell densities under a measured-latency budget. It preserves existing selection strategies and kernels, replacing only the allocation component.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 5

**Claim (verbatim):**

```text
ALLOT outperforms every compared allocation strategy with XAttention, achieving an 11.8 dB PSNR gain on HunyuanVideo.
```

**Evidence excerpt (verbatim):**

```text
At equal or shorter wall-clock time, ALLOT outperforms every compared allocation strategy with XAttention, with an 11.8 dB PSNR gain on HunyuanVideo.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 6

**Claim (verbatim):**

```text
ALLOT outperforms or ties the default in all nine settings across four additional published pipelines on Wan2.1, Wan2.2, and HunyuanVideo.
```

**Evidence excerpt (verbatim):**

```text
Extensive experiments across four additional published pipelines on Wan2.1, Wan2.2, and HunyuanVideo show that ALLOT outperforms or ties the default in all nine settings.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 18. ReSeg: Retraining-free segmentation of abdominal organs via generalizable semantic representation learning

- Cohort order: 28
- Paper ID: `2610.29090v1`
- Source: https://arxiv.org/abs/2610.29090v1
- Publication timestamp: 2026-10-21T02:31:19Z
- Copilot-priority count (triage only): 4/4

**Original abstract (verbatim):**

```text
Abdominal organ segmentation is essential in modern medical applications. While existing deep learning approaches demonstrate promising performance, their heavy reliance on large-scale image data raises concerns over generalization capability and privacy risks. This motivates the development of generalizable segmentation training paradigms based on domain-randomized image synthesis, facilitating generalization across unseen real image domains. However, existing paradigms either suffer from limited segmentation performance when applied to abdominal organs, or require dataset-specific finetuning. To address these limitations, we propose ReSeg, a novel two-stage retraining-free framework for domain-agnostic zero-shot abdominal organ segmentation. At the first stage, our organ-agnostic synthetic data-driven pretraining approach exploits semantically and visually diverse synthetic images generated by a dedicated data engine to optimize a Generalizable Semantic Representation Network (GSRNet). The network is thereby capable of learning semantic features robust against variations in anatomical structure, imaging contrast, resolution and spatial context, which provide universal representation capabilities that serve as a foundation for segmentation learning. Subsequently, in the second stage, we continue to train an Organ-specific Encoder-decoder Segmentation Network (OESNet), whose encoder is initialized with the pretrained weights. This training process is facilitated by another dedicated data engine, which generates diversified visual images while strictly retaining the inherent spatial layout of abdominal organs. Comprehensive evaluation on seven abdominal organ segmentation datasets across three different modalities including CT, MRI, and PET demonstrates that ReSeg consistently outperforms existing state-of-the-art (SOTA) methods while eliminating the need for real training images.
```

#### Claim 1

**Claim (verbatim):**

```text
ReSeg is a novel two-stage retraining-free framework for domain-agnostic zero-shot abdominal organ segmentation.
```

**Evidence excerpt (verbatim):**

```text
we propose ReSeg, a novel two-stage retraining-free framework for domain-agnostic zero-shot abdominal organ segmentation.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
The first stage of ReSeg uses a synthetic data-driven pretraining approach to optimize a Generalizable Semantic Representation Network (GSRNet).
```

**Evidence excerpt (verbatim):**

```text
At the first stage, our organ-agnostic synthetic data-driven pretraining approach exploits semantically and visually diverse synthetic images generated by a dedicated data engine to optimize a Generalizable Semantic Representation Network (GSRNet).
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
The GSRNet learns semantic features robust against variations in anatomical structure, imaging contrast, resolution and spatial context.
```

**Evidence excerpt (verbatim):**

```text
The network is thereby capable of learning semantic features robust against variations in anatomical structure, imaging contrast, resolution and spatial context, which provide universal representation capabilities that serve as a foundation for segmentation learning.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
ReSeg consistently outperforms existing state-of-the-art (SOTA) methods across three different modalities including CT, MRI, and PET.
```

**Evidence excerpt (verbatim):**

```text
Comprehensive evaluation on seven abdominal organ segmentation datasets across three different modalities including CT, MRI, and PET demonstrates that ReSeg consistently outperforms existing state-of-the-art (SOTA) methods while eliminating the need for real training images.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 19. Gradient Descent as Implicit EM in Distance-Based Neural Models

- Cohort order: 31
- Paper ID: `2512.24780v2`
- Source: https://arxiv.org/abs/2512.24780v2
- Publication timestamp: 2025-12-31T10:56:43Z
- Copilot-priority count (triage only): 4/5

**Original abstract (verbatim):**

```text
Neural networks trained with standard objectives exhibit behaviors characteristic of probabilistic inference: soft clustering, prototype specialization, and Bayesian uncertainty tracking. These phenomena appear across architectures -- in attention mechanisms, classification heads, and energy-based models -- yet existing explanations often rely on loose analogies to mixture models or post-hoc architectural interpretation. We provide a direct explanation. For any objective with log-sum-exp structure over distances or energies, the gradient with respect to each distance is exactly the negative posterior responsibility of the corresponding component: $\partial L / \partial d_j = -r_j$. The identity is algebraic, requiring only differentiability; it is a specialization of Fisher's identity, and its significance here is its address: standard neural objectives instantiate it without modification. The consequence is that gradient descent on such objectives performs generalized expectation-maximization implicitly, with responsibilities arising as gradients to be applied rather than auxiliary variables to be computed. This result unifies three regimes of learning: unsupervised mixture modeling, where responsibilities are fully latent; attention, where responsibilities are conditioned on queries; and cross-entropy classification, where supervision clamps responsibilities to targets. Our claims live at training time: the responsibility-weighted gradient dynamics recently documented in transformers follow from the objective's geometry. The in-context Bayesian computation that trained transformers perform at inference time is the endpoint of these dynamics, not their per-step content.
```

#### Claim 1

**Claim (verbatim):**

```text
Gradient descent on objectives with log-sum-exp structure over distances or energies yields the negative posterior responsibility of the corresponding component.
```

**Evidence excerpt (verbatim):**

```text
For any objective with log-sum-exp structure over distances or energies, the gradient with respect to each distance is exactly the negative posterior responsibility of the corresponding component: $\partial L / \partial d_j = -r_j$.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
The identity between gradient and posterior responsibility is algebraic and requires only differentiability.
```

**Evidence excerpt (verbatim):**

```text
The identity is algebraic, requiring only differentiability; it is a specialization of Fisher's identity, and its significance here is its address: standard neural objectives instantiate it without modification.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
Gradient descent on such objectives performs generalized expectation-maximization implicitly.
```

**Evidence excerpt (verbatim):**

```text
The consequence is that gradient descent on such objectives performs generalized expectation-maximization implicitly, with responsibilities arising as gradients to be applied rather than auxiliary variables to be computed.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
The result unifies three regimes of learning: unsupervised mixture modeling, attention, and cross-entropy classification.
```

**Evidence excerpt (verbatim):**

```text
This result unifies three regimes of learning: unsupervised mixture modeling, where responsibilities are fully latent; attention, where responsibilities are conditioned on queries; and cross-entropy classification, where supervision clamps responsibilities to targets.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 5

**Claim (verbatim):**

```text
The responsibility-weighted gradient dynamics in transformers follow from the objective's geometry.
```

**Evidence excerpt (verbatim):**

```text
Our claims live at training time: the responsibility-weighted gradient dynamics recently documented in transformers follow from the objective's geometry.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 20. Colorful Pinball: Density-Weighted Quantile Regression for Conditional Guarantee of Conformal Prediction

- Cohort order: 32
- Paper ID: `2512.24139v5`
- Source: https://arxiv.org/abs/2512.24139v5
- Publication timestamp: 2025-12-30T11:02:35Z
- Copilot-priority count (triage only): 4/4

**Original abstract (verbatim):**

```text
Although conformal prediction provides robust marginal coverage guarantees, achieving reliable conditional coverage for specific inputs remains challenging. While exact distribution-free conditional coverage is impossible with finite samples, recent work has focused on improving the conditional coverage of standard conformal procedures. Distinct from approaches that target relaxed notions of conditional coverage, we directly target the mean squared error of conditional coverage by refining the quantile regression components that underpin many conformal methods. Leveraging a Taylor expansion, we derive a sharp surrogate objective for quantile regression: a density-weighted pinball loss, where the weights are given by the conditional density of the nonconformity score evaluated at the true quantile. We propose a three-headed quantile network that estimates these weights via finite differences using auxiliary quantile levels at $1-α\pm δ$, subsequently fine-tuning the central quantile by optimizing the weighted loss. We provide a theoretical analysis with exact non-asymptotic guarantees characterizing the resulting excess risk. Extensive experiments on diverse high-dimensional real-world datasets demonstrate remarkable improvements in conditional coverage performance.
```

#### Claim 1

**Claim (verbatim):**

```text
The paper proposes a density-weighted pinball loss for quantile regression to improve conditional coverage.
```

**Evidence excerpt (verbatim):**

```text
Leveraging a Taylor expansion, we derive a sharp surrogate objective for quantile regression: a density-weighted pinball loss, where the weights are given by the conditional density of the nonconformity score evaluated at the true quantile.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
A three-headed quantile network is introduced to estimate the weights in the density-weighted pinball loss.
```

**Evidence excerpt (verbatim):**

```text
We propose a three-headed quantile network that estimates these weights via finite differences using auxiliary quantile levels at $1-α\pm δ$, subsequently fine-tuning the central quantile by optimizing the weighted loss.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
The paper provides theoretical analysis with exact non-asymptotic guarantees for the proposed method.
```

**Evidence excerpt (verbatim):**

```text
We provide a theoretical analysis with exact non-asymptotic guarantees characterizing the resulting excess risk.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
The method achieves significant improvements in conditional coverage performance on high-dimensional real-world datasets.
```

**Evidence excerpt (verbatim):**

```text
Extensive experiments on diverse high-dimensional real-world datasets demonstrate remarkable improvements in conditional coverage performance.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 21. Phase Transitions in Learning Driven by Extremal Data

- Cohort order: 33
- Paper ID: `2610.29531v1`
- Source: https://arxiv.org/abs/2610.29531v1
- Publication timestamp: 2026-10-21T10:22:18Z
- Copilot-priority count (triage only): 4/6

**Original abstract (verbatim):**

```text
We study an extremal regression problem, an example of multiple instance learning (MIL), where the predictors are given as multisets, called bags. The bag elements (called instances) possess hidden labels which are pooled to produce an observed bag-level label. Max pooling is common in MIL applications, but gives rise to vanishing gradients. To handle this, modern MIL pipelines approximate the max with a softmax, treating the sharpness as a learnable parameter, denoted $λ$. When the max pooling model is the true data generating process, learning will be successful when $λ$ is increased during gradient descent, thereby driving the dynamics into regions of parameter space with vanishing gradients. To understand the conditions under which gradient descent breaks down, we study a minimal model and derive a low dimensional projection of the gradient flow in the joint limit of large bags $n$ and high dimension $d$ with $α=\ln n/d$ fixed. The flow has two distinct phase transitions: an intrinsic freezing transition related to the random energy model of disordered systems, and a retrieval transition occurring in modern Hopfield networks. Numerical simulation confirms both the phase diagram and the convergence of the finite-size training gradient to its predicted asymptotic form.
```

#### Claim 1

**Claim (verbatim):**

```text
The study investigates an extremal regression problem in multiple instance learning where bag-level labels are derived from hidden instance labels.
```

**Evidence excerpt (verbatim):**

```text
We study an extremal regression problem, an example of multiple instance learning (MIL), where the predictors are given as multisets, called bags.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
Max pooling is commonly used in MIL applications but leads to vanishing gradients.
```

**Evidence excerpt (verbatim):**

```text
Max pooling is common in MIL applications, but gives rise to vanishing gradients.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
Modern MIL pipelines approximate max pooling with a softmax, treating sharpness as a learnable parameter denoted $λ$.
```

**Evidence excerpt (verbatim):**

```text
To handle this, modern MIL pipelines approximate the max with a softmax, treating the sharpness as a learnable parameter, denoted $λ$.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
When the max pooling model is the true data generating process, increasing $λ$ during gradient descent drives the dynamics into regions of parameter space with vanishing gradients.
```

**Evidence excerpt (verbatim):**

```text
When the max pooling model is the true data generating process, learning will be successful when $λ$ is increased during gradient descent, thereby driving the dynamics into regions of parameter space with vanishing gradients.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 5

**Claim (verbatim):**

```text
The gradient flow exhibits two distinct phase transitions: an intrinsic freezing transition and a retrieval transition.
```

**Evidence excerpt (verbatim):**

```text
The flow has two distinct phase transitions: an intrinsic freezing transition related to the random energy model of disordered systems, and a retrieval transition occurring in modern Hopfield networks.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 6

**Claim (verbatim):**

```text
Numerical simulations confirm the phase diagram and the convergence of the finite-size training gradient to its predicted asymptotic form.
```

**Evidence excerpt (verbatim):**

```text
Numerical simulation confirms both the phase diagram and the convergence of the finite-size training gradient to its predicted asymptotic form.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 22. MINER: Modeling Inter- and Intra-Person Variance for Reidentification

- Cohort order: 38
- Paper ID: `2610.28941v1`
- Source: https://arxiv.org/abs/2610.28941v1
- Publication timestamp: 2026-10-20T21:34:43Z
- Copilot-priority count (triage only): 4/5

**Original abstract (verbatim):**

```text
Clothes-Changing Person Re-Identification (CC-ReID) remains challenging due to drastic appearance shifts across outfits. Most prior works devise biometric signal-extraction heuristics to enhance inter-person variance, e.g., using segmentation masks, while leaving intra-person variance uncontrolled. We present MINER, a simple model-agnostic framework that suppresses garment bias by contrasting hard examples and adaptively balancing dataset-dependent intra- and inter-person variance. Extensive experiments show that MINER improves retrieval across CC-ReID benchmarks, achieving state-of-the-art performance on four datasets and ranking among the leaders in all three tracks of the open TVRID RGB-Depth ReID challenge.
```

#### Claim 1

**Claim (verbatim):**

```text
MINER is a model-agnostic framework that suppresses garment bias by contrasting hard examples.
```

**Evidence excerpt (verbatim):**

```text
We present MINER, a simple model-agnostic framework that suppresses garment bias by contrasting hard examples and adaptively balancing dataset-dependent intra- and inter-person variance.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
MINER adaptively balances dataset-dependent intra- and inter-person variance.
```

**Evidence excerpt (verbatim):**

```text
We present MINER, a simple model-agnostic framework that suppresses garment bias by contrasting hard examples and adaptively balancing dataset-dependent intra- and inter-person variance.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
MINER improves retrieval across CC-ReID benchmarks.
```

**Evidence excerpt (verbatim):**

```text
Extensive experiments show that MINER improves retrieval across CC-ReID benchmarks, achieving state-of-the-art performance on four datasets and ranking among the leaders in all three tracks of the open TVRID RGB-Depth ReID challenge.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
MINER achieves state-of-the-art performance on four datasets.
```

**Evidence excerpt (verbatim):**

```text
Extensive experiments show that MINER improves retrieval across CC-ReID benchmarks, achieving state-of-the-art performance on four datasets and ranking among the leaders in all three tracks of the open TVRID RGB-Depth ReID challenge.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 5

**Claim (verbatim):**

```text
MINER ranks among the leaders in all three tracks of the open TVRID RGB-Depth ReID challenge.
```

**Evidence excerpt (verbatim):**

```text
Extensive experiments show that MINER improves retrieval across CC-ReID benchmarks, achieving state-of-the-art performance on four datasets and ranking among the leaders in all three tracks of the open TVRID RGB-Depth ReID challenge.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 23. BRIDGE: An Acceptance Gate to Block False Improvements in Model Updates, with a Retrospective Clinical Evaluation

- Cohort order: 39
- Paper ID: `2610.29515v1`
- Source: https://arxiv.org/abs/2610.29515v1
- Publication timestamp: 2026-10-21T10:04:40Z
- Copilot-priority count (triage only): 4/5

**Original abstract (verbatim):**

```text
Models are updated repeatedly, and an update that looks better on validation data but not on new data is a false improvement that can misguide clinical decisions. The naive rule accepts every positive validation gain and is optimistic when the same data choose and judge the update. BRIDGE is a model-agnostic acceptance gate that decides each update from predictions and the available labels, with fixed settings. Each fold of the data judges the update chosen on the other folds (cross-fitting) to reduce selection bias; acceptance requires the gain's lower bootstrap bound to exceed a margin. The four settings are (A) 11 new datasets, (B) synthetic tasks, (C) 12 retrospective clinical tasks, and (D) 39 supporting datasets. The false-improvement rate falls from 19.1% (naive) to 1.1% (BRIDGE) in (A), 20.7% to 1.7% (B), 20.0% to 0% (C), and 12.5% to 0.5% (D); every 95% confidence interval of the reduction over datasets or tasks excludes zero (not over the clinical sources). An equal-size random draw from the naive acceptances contains more false improvements in (A)-(E) (post hoc, p<0.001). On the OpenML collection (E) of 14 new datasets, the false-improvement rate falls from 25.6% to 1.0%. BRIDGE removes 97% to 100% of the false improvements that the naive rule accepts, and its mean gain per deployed update is 1.8 to 3.1 times the naive rule's. The 95% upper bound on the false-improvement rate is below 5.5%: formal in (B) for independent tasks (3.56%), and conditional on the real data tested (0.33% to 5.40%).
```

#### Claim 1

**Claim (verbatim):**

```text
BRIDGE is a model-agnostic acceptance gate that decides each update from predictions and the available labels, with fixed settings.
```

**Evidence excerpt (verbatim):**

```text
BRIDGE is a model-agnostic acceptance gate that decides each update from predictions and the available labels, with fixed settings.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
Each fold of the data judges the update chosen on the other folds (cross-fitting) to reduce selection bias.
```

**Evidence excerpt (verbatim):**

```text
Each fold of the data judges the update chosen on the other folds (cross-fitting) to reduce selection bias;
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
The false-improvement rate falls from 19.1% (naive) to 1.1% (BRIDGE) in (A).
```

**Evidence excerpt (verbatim):**

```text
The false-improvement rate falls from 19.1% (naive) to 1.1% (BRIDGE) in (A), 20.7% to 1.7% (B), 20.0% to 0% (C), and 12.5% to 0.5% (D);
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
BRIDGE removes 97% to 100% of the false improvements that the naive rule accepts.
```

**Evidence excerpt (verbatim):**

```text
BRIDGE removes 97% to 100% of the false improvements that the naive rule accepts, and its mean gain per deployed update is 1.8 to 3.1 times the naive rule's.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 5

**Claim (verbatim):**

```text
The 95% upper bound on the false-improvement rate is below 5.5%: formal in (B) for independent tasks (3.56%), and conditional on the real data tested (0.33% to 5.40%).
```

**Evidence excerpt (verbatim):**

```text
The 95% upper bound on the false-improvement rate is below 5.5%: formal in (B) for independent tasks (3.56%), and conditional on the real data tested (0.33% to 5.40%).
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---

### 24. Scan or Index? large Evidence Coverage, Answer Quality, and Cost in Long-Document RAG

- Cohort order: 41
- Paper ID: `2610.28957v1`
- Source: https://arxiv.org/abs/2610.28957v1
- Publication timestamp: 2026-10-20T22:11:07Z
- Copilot-priority count (triage only): 4/4

**Original abstract (verbatim):**

```text
Scanning every passage in a long document seems thorough, but does it preserve more useful evidence or produce better answers? We compare 11 retrieval configurations spanning lexical and dense search, hybrid reranking, and full-document scanning with Jev, OpenAI Decisions, and Cloudflare Clef. Our evaluation uses 396 QASPER questions and 80 questions from eight complete textbooks, with common passages, a five-passage limit, and a fixed answer generator. On books, Hybrid + Jev achieves the highest observed evidence coverage (94.1%), compared with 88.7% for Jev full scan and 81.3\% for OpenAI dense retrieval. Full scans examine every passage initially, yet later reduction steps can discard relevant evidence. Higher evidence coverage also does not consistently produce better answers: Hybrid + Decisions achieves the highest observed book Answer Accuracy among retrieval methods (0.892), despite recovering less reference evidence. Full scanning incurs substantially higher latency on books under the tested deployments, while reusable dense retrieval has lower projected API cost than paid decision-based methods as queries accumulate. Most QASPER articles already fit within the hybrid candidate pool, limiting the benefit of scanning. These results highlight evidence retention, answer quality, and reuse cost as complementary criteria for choosing a long-document retrieval strategy.
```

#### Claim 1

**Claim (verbatim):**

```text
Hybrid + Jev achieves the highest observed evidence coverage on books.
```

**Evidence excerpt (verbatim):**

```text
Hybrid + Jev achieves the highest observed evidence coverage (94.1%), compared with 88.7% for Jev full scan and 81.3\% for OpenAI dense retrieval.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 2

**Claim (verbatim):**

```text
Hybrid + Decisions achieves the highest observed book Answer Accuracy among retrieval methods.
```

**Evidence excerpt (verbatim):**

```text
Hybrid + Decisions achieves the highest observed book Answer Accuracy among retrieval methods (0.892), despite recovering less reference evidence.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 3

**Claim (verbatim):**

```text
Full scanning incurs substantially higher latency on books under the tested deployments.
```

**Evidence excerpt (verbatim):**

```text
Full scanning incurs substantially higher latency on books under the tested deployments, while reusable dense retrieval has lower projected API cost than paid decision-based methods as queries accumulate.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

#### Claim 4

**Claim (verbatim):**

```text
Most QASPER articles already fit within the hybrid candidate pool, limiting the benefit of scanning.
```

**Evidence excerpt (verbatim):**

```text
Most QASPER articles already fit within the hybrid candidate pool, limiting the benefit of scanning.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] compound  [ ] unclear
- Reviewer decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

---
