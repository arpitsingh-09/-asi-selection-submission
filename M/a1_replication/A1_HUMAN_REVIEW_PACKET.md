# Main Problem A1 — Human Review Packet

**Purpose:** review claim meaning and proposed same-category decoy candidates. No claim or decoy is pre-approved.
**Cohort:** committed 50-paper cohort; this packet includes the 43 papers whose extractor accepted 4–10 claims.
**Generated from saved evidence at:** 2026-11-14T13:16:16.088838Z
**Cohort SHA-256:** `2577e78a37f951785c577a0a045cc69a264d575ea1c82dc20f310c2fa2bd7702`
**Extraction file SHA-256:** `e498bff6ebb5faff663e43abb2f91e3597012c8ced354dbf1b15cde8c935ee44`
**Reviewer:** ____________________    **Review date (UTC):** ____________________

For each claim, judge whether its excerpt semantically supports the claim, whether the claim is atomic, and whether to accept it. For each proposed decoy, judge whether it is genuinely same-topic and cite evidence. The category match is only a candidate-selection aid, not a judgment.

## 1. Tubular Riemannian Laplace Approximations for Bayesian Neural Networks

- Paper ID: `2512.24381v2`
- Publication date: 2025-12-30T17:50:55Z
- Source: https://arxiv.org/abs/2512.24381v2
- Category metadata: `cs.LG`
- Abstract SHA-256: `a5e10a77198edbe29636e355a1f9315dfaa5b7c56f86859b600e0b726f4a0fe9`

**Source abstract (verbatim):**

```text
Laplace approximations are among the simplest and most practical methods for approximate Bayesian inference in neural networks, yet their Euclidean formulation struggles with the highly anisotropic, curved loss surfaces and large symmetry groups that characterize modern deep models. Recent work has proposed Riemannian and geometric Gaussian approximations to adapt to this structure. Building on these ideas, we introduce the Tubular Riemannian Laplace (TRL) approximation. TRL explicitly models the posterior as a probabilistic tube that follows a low-loss valley induced by functional symmetries, using a Fisher/Gauss-Newton metric to separate prior-dominated tangential uncertainty from data-dominated transverse uncertainty. We interpret TRL as a scalable reparametrised Gaussian approximation that utilizes implicit curvature estimates to operate in high-dimensional parameter spaces. Our empirical evaluation on ResNet-18 (CIFAR-10 and CIFAR-100) demonstrates that TRL achieves excellent calibration, matching or exceeding the reliability of Deep Ensembles (in terms of ECE) while requiring only a fraction (1/5) of the training cost. TRL effectively bridges the gap between single-model efficiency and ensemble-grade reliability.
```

**Extracted claims (4; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
The Tubular Riemannian Laplace (TRL) approximation models the posterior as a probabilistic tube that follows a low-loss valley induced by functional symmetries.
```

Evidence excerpt (verbatim):

```text
TRL explicitly models the posterior as a probabilistic tube that follows a low-loss valley induced by functional symmetries
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
TRL uses a Fisher/Gauss-Newton metric to separate prior-dominated tangential uncertainty from data-dominated transverse uncertainty.
```

Evidence excerpt (verbatim):

```text
using a Fisher/Gauss-Newton metric to separate prior-dominated tangential uncertainty from data-dominated transverse uncertainty
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
TRL is interpreted as a scalable reparametrised Gaussian approximation that utilizes implicit curvature estimates to operate in high-dimensional parameter spaces.
```

Evidence excerpt (verbatim):

```text
We interpret TRL as a scalable reparametrised Gaussian approximation that utilizes implicit curvature estimates to operate in high-dimensional parameter spaces
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
TRL achieves excellent calibration, matching or exceeding the reliability of Deep Ensembles in terms of ECE while requiring only a fraction (1/5) of the training cost.
```

Evidence excerpt (verbatim):

```text
Our empirical evaluation on ResNet-18 (CIFAR-10 and CIFAR-100) demonstrates that TRL achieves excellent calibration, matching or exceeding the reliability of Deep Ensembles (in terms of ECE) while requiring only a fraction (1/5) of the training cost.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.24139v5`
- Title: Colorful Pinball: Density-Weighted Quantile Regression for Conditional Guarantee of Conformal Prediction
- Publication date: 2025-12-30T11:02:35Z
- Source: https://arxiv.org/abs/2512.24139v5
- Candidate selection metadata: same broad category `cs.LG`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Although conformal prediction provides robust marginal coverage guarantees, achieving reliable conditional coverage for specific inputs remains challenging. While exact distribution-free conditional coverage is impossible with finite samples, recent work has focused on improving the conditional coverage of standard conformal procedures. Distinct from approaches that target relaxed notions of conditional coverage, we directly target the mean squared error of conditional coverage by refining the quantile regression components that underpin many conformal methods. Leveraging a Taylor expansion, we derive a sharp surrogate objective for quantile regression: a density-weighted pinball loss, where the weights are given by the conditional density of the nonconformity score evaluated at the true quantile. We propose a three-headed quantile network that estimates these weights via finite differences using auxiliary quantile levels at $1-α\pm δ$, subsequently fine-tuning the central quantile by optimizing the weighted loss. We provide a theoretical analysis with exact non-asymptotic guarantees characterizing the resulting excess risk. Extensive experiments on diverse high-dimensional real-world datasets demonstrate remarkable improvements in conditional coverage performance.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 2. DepState-JEPA: Learning Depth-Grounded State Representation for Visual Perception and Manipulation

- Paper ID: `2610.29246v1`
- Publication date: 2026-10-21T05:51:06Z
- Source: https://arxiv.org/abs/2610.29246v1
- Category metadata: `cs.CV`
- Abstract SHA-256: `5bec2768715ac90188685a5d90e344c92a3dc39d1ecaf5d7c5a1baff69963f68`

**Source abstract (verbatim):**

```text
Predictive representations for robot manipulation should connect scene geometry with the state changes induced by actions. Our intuition is that understanding what an action will change starts with understanding where things are: complementary RGB and depth observations ground a common scene representation from which to infer those changes. Guided by this intuition, we introduce \textbf{DepState-JEPA}, a dual-stream RGB--Depth joint-embedding predictive architecture that connects spatial understanding with action-conditioned prediction through a shared latent state, \textbf{DepState}. Built on V-JEPA~2.1, the framework uses depth both as a complementary observation stream and to ground both modalities in metric 3D space, aggregating shared information into DepState while retaining modality-private features for decoding. Ray-conditioned readouts predict local features without target depth; after an action-conditioned transition, the same decoders predict future RGB and depth features using the predicted state and fixed initial private features. Robot-state readouts provide recursive proprioceptive inputs; object-trajectory supervision and calibrated forward kinematics shape state learning through motion targets and joint--TCP consistency. Comparisons show stronger RGB-encoder transfer after RGB-D adaptation, feature completion, conditioned visual forecasting, and manipulation success. Within-model ablations identify contributions from depth content, metric coordinates, and future-state matching, with additional control gains from FK regularization.
```

**Extracted claims (5; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
Depth is used both as a complementary observation stream and to ground both modalities in metric 3D space.
```

Evidence excerpt (verbatim):

```text
Built on V-JEPA~2.1, the framework uses depth both as a complementary observation stream and to ground both modalities in metric 3D space, aggregating shared information into DepState while retaining modality-private features for decoding.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
Ray-conditioned readouts predict local features without target depth.
```

Evidence excerpt (verbatim):

```text
Ray-conditioned readouts predict local features without target depth; after an action-conditioned transition, the same decoders predict future RGB and depth features using the predicted state and fixed initial private features.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
Robot-state readouts provide recursive proprioceptive inputs.
```

Evidence excerpt (verbatim):

```text
Robot-state readouts provide recursive proprioceptive inputs; object-trajectory supervision and calibrated forward kinematics shape state learning through motion targets and joint--TCP consistency.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
Comparisons show stronger RGB-encoder transfer after RGB-D adaptation, feature completion, conditioned visual forecasting, and manipulation success.
```

Evidence excerpt (verbatim):

```text
Comparisons show stronger RGB-encoder transfer after RGB-D adaptation, feature completion, conditioned visual forecasting, and manipulation success.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
Within-model ablations identify contributions from depth content, metric coordinates, and future-state matching.
```

Evidence excerpt (verbatim):

```text
Within-model ablations identify contributions from depth content, metric coordinates, and future-state matching, with additional control gains from FK regularization.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.23709v3`
- Title: Stream-DiffVSR: Low-Latency Streamable Video Super-Resolution via Auto-Regressive Diffusion
- Publication date: 2025-12-29T18:59:57Z
- Source: https://arxiv.org/abs/2512.23709v3
- Candidate selection metadata: same broad category `cs.CV`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Diffusion-based video super-resolution (VSR) methods deliver strong perceptual quality but are often unsuitable for latency-sensitive scenarios due to reliance on future frames and expensive multi-step denoising. We propose Stream-DiffVSR, a causally conditioned diffusion framework for efficient online VSR. Operating strictly on past frames, Stream-DiffVSR integrates a four-step distilled denoiser for fast inference, an Auto-regressive Temporal Guidance (ARTG) module that injects motion-aligned cues during latent denoising, and a lightweight temporal-aware decoder with a Temporal Processor Module (TPM) to enhance detail and temporal coherence. Unlike chunk-wise streaming inference, our strictly frame-by-frame causal design avoids sequence-level waiting, substantially reducing time-to-first-frame and end-to-end latency. Stream-DiffVSR processes 720p frames in 0.328 seconds on an RTX 4090 and consistently outperforms prior diffusion-based baselines. Compared with the online state-of-the-art TMP, it improves perceptual quality (LPIPS +0.095). Compared with prior diffusion-based VSR methods such as MGLD-VSR, it reduces per-frame runtime by over 130x. Moreover, Stream-DiffVSR substantially lowers time-to-first-frame for diffusion-based VSR, reducing initial delay from over 4600 seconds to 0.328 seconds, making diffusion-based VSR markedly more practical for low-latency online and streaming deployment. Project page: https://jamichss.github.io/stream-diffvsr-project-page/
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 3. Certified Neural Approximation of Robust Nonlinear Model Predictive Control

- Paper ID: `2610.29559v1`
- Publication date: 2026-10-21T10:46:55Z
- Source: https://arxiv.org/abs/2610.29559v1
- Category metadata: `cs.LG`
- Abstract SHA-256: `1cfc20820fe83e72bd1d773a14acd83ba0bfdf003bdf11991d586037a681caad`

**Source abstract (verbatim):**

```text
Model predictive control is a high-performance control method, but it incurs comparatively high online computational costs across many control tasks and is challenging to realize in low-level hardware settings. To address this, we present a framework for generating neural network controllers that provably inherit the safety and stability guarantees of a robust model predictive policy. In contrast to approaches based on post-verification or additional online safety filters, our method provides constructive, a priori design conditions that ensure preservation of recursive feasibility and stability before deployment. We treat the approximation error as a bounded input disturbance, which is addressed in the MPC design. This allows the neural network controller to directly inherit robustness from the underlying model predictive controller, which enables the transfer of guarantees to the approximation. The design process is an offline, constructive synthesis pipeline and can be implemented once Lipschitz bounds are specified. We further demonstrate in simulation that the learned controller reproduces the closed-loop behavior of the original controller while reducing online computation.
```

**Extracted claims (5; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
A framework is presented for generating neural network controllers that provably inherit the safety and stability guarantees of a robust model predictive policy.
```

Evidence excerpt (verbatim):

```text
we present a framework for generating neural network controllers that provably inherit the safety and stability guarantees of a robust model predictive policy.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
The method provides constructive, a priori design conditions that ensure preservation of recursive feasibility and stability before deployment.
```

Evidence excerpt (verbatim):

```text
our method provides constructive, a priori design conditions that ensure preservation of recursive feasibility and stability before deployment.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
The approximation error is treated as a bounded input disturbance, which is addressed in the MPC design.
```

Evidence excerpt (verbatim):

```text
We treat the approximation error as a bounded input disturbance, which is addressed in the MPC design.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
The design process is an offline, constructive synthesis pipeline and can be implemented once Lipschitz bounds are specified.
```

Evidence excerpt (verbatim):

```text
The design process is an offline, constructive synthesis pipeline and can be implemented once Lipschitz bounds are specified.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
The learned controller reproduces the closed-loop behavior of the original controller while reducing online computation.
```

Evidence excerpt (verbatim):

```text
We further demonstrate in simulation that the learned controller reproduces the closed-loop behavior of the original controller while reducing online computation.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.24139v5`
- Title: Colorful Pinball: Density-Weighted Quantile Regression for Conditional Guarantee of Conformal Prediction
- Publication date: 2025-12-30T11:02:35Z
- Source: https://arxiv.org/abs/2512.24139v5
- Candidate selection metadata: same broad category `cs.LG`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Although conformal prediction provides robust marginal coverage guarantees, achieving reliable conditional coverage for specific inputs remains challenging. While exact distribution-free conditional coverage is impossible with finite samples, recent work has focused on improving the conditional coverage of standard conformal procedures. Distinct from approaches that target relaxed notions of conditional coverage, we directly target the mean squared error of conditional coverage by refining the quantile regression components that underpin many conformal methods. Leveraging a Taylor expansion, we derive a sharp surrogate objective for quantile regression: a density-weighted pinball loss, where the weights are given by the conditional density of the nonconformity score evaluated at the true quantile. We propose a three-headed quantile network that estimates these weights via finite differences using auxiliary quantile levels at $1-α\pm δ$, subsequently fine-tuning the central quantile by optimizing the weighted loss. We provide a theoretical analysis with exact non-asymptotic guarantees characterizing the resulting excess risk. Extensive experiments on diverse high-dimensional real-world datasets demonstrate remarkable improvements in conditional coverage performance.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 4. ALIAS: Evaluating Performance and Memorization in LLM-Written TLA+ Specifications

- Paper ID: `2610.29767v1`
- Publication date: 2026-10-21T14:02:02Z
- Source: https://arxiv.org/abs/2610.29767v1
- Category metadata: `cs.CL`
- Abstract SHA-256: `56a6d358ba1af35ecc28871834cd6b3ec73348a47bcd06fefc701a82dd966079`

**Source abstract (verbatim):**

```text
Memorization inflates the benchmark scores of large language models (LLMs), since a model can reproduce answers it saw in training. Researchers test for it with consistent identifier renaming (CIR), which gives every identifier in a task a new name, and treat a lower score on the renamed task as evidence of recall. We test this method on the Temporal Logic of Actions Plus (TLA+) language, whose model checker acts as an oracle by confirming whether a renamed task preserves the exact behaviors of the original. Across 111 TLA+-Bench tasks, renaming lowers the correctness of Claude Opus 4.8 from 28% to 18% and of GPT-5 from 9% to 7%. Most of this decrease comes from how the test grades, which requires exact names that most descriptions never state. Grading by behavior shrinks the decrease to about 3 percentage points for Opus 4.8 and to 0 for GPT-5. In two model families fine-tuned on disjoint halves of the tasks, renaming removes about half of the training gain in likelihood and costs 4.9 percentage points (Qwen) and 1.3 percentage points (Gemma) on unseen tasks. A lower score after renaming therefore mixes memorization, name-based grading, and the cost of new names.
```

**Extracted claims (4; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
Renaming identifiers in TLA+ specifications reduces the correctness scores of LLM-generated specifications.
```

Evidence excerpt (verbatim):

```text
renaming lowers the correctness of Claude Opus 4.8 from 28% to 18% and of GPT-5 from 9% to 7%.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
The decrease in correctness scores is largely due to the test grading requiring exact names that are often not stated in the descriptions.
```

Evidence excerpt (verbatim):

```text
Most of this decrease comes from how the test grades, which requires exact names that most descriptions never state.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
Grading by behavior instead of exact names reduces the impact of renaming on correctness scores.
```

Evidence excerpt (verbatim):

```text
Grading by behavior shrinks the decrease to about 3 percentage points for Opus 4.8 and to 0 for GPT-5.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
Renaming identifiers in fine-tuned models reduces the training gain in likelihood and affects performance on unseen tasks.
```

Evidence excerpt (verbatim):

```text
In two model families fine-tuned on disjoint halves of the tasks, renaming removes about half of the training gain in likelihood and costs 4.9 percentage points (Qwen) and 1.3 percentage points (Gemma) on unseen tasks.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2610.28586v1`
- Title: Capable Teacher, Myopic Scorer: Reward-Free Teacher Repair for Agentic On-Policy Distillation
- Publication date: 2026-10-20T17:40:08Z
- Source: https://arxiv.org/abs/2610.28586v1
- Candidate selection metadata: same broad category `cs.CL`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Agentic on-policy distillation (OPD) trains a student agent on its own trajectories while a teacher scores every token. A natural explanation of where it goes wrong is compounding error: the student's mistakes carry its trajectories beyond the region where the teacher is reliable, so recent methods keep training inside that region, through episode-length curricula, teacher-guided turns, prefix replay, or teacher intervention where the two disagree. We show this explanation is incomplete. From the states where the student departs most from the teacher, the teacher's own takeovers still finish the task, yet the student trained on its token scores keeps running out of turns. We attribute this to the myopia of next-token scoring. The teacher rates each token without seeing where the episode ends, so its scores let through the safe, delaying moves that outcome-based RL would punish with zero reward, a penalty agentic OPD lacks. We call this difference between what the teacher does and what it scores the rollout-scorer gap. We propose Rollout-to-Scorer Distillation (R2S), which repairs the scorer before distillation by mining high-disagreement states from the untrained student, running teacher takeovers from them, keeping the states where enough takeovers pass a reward-free check such as consensus or an LLM judge, and fine-tuning the teacher to give its takeover-informed scores on every assistant token from the divergence turn onward, without the takeover in context. The repaired teacher is frozen as the sole scorer for standard OPD, requiring no task reward during repair or training. Across three environments, two teachers and four students, R2S outperforms three state-of-the-art agentic-OPD methods in all twelve teacher-student-environment cells, by 12.8 success points on average over the best of them in each cell. Project page: https://tree-shu-zhao.github.io/r2s/.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 5. 3D Semantic Segmentation for Post-Disaster Assessment

- Paper ID: `2512.24593v1`
- Publication date: 2025-12-31T03:30:58Z
- Source: https://arxiv.org/abs/2512.24593v1
- Category metadata: `cs.CV`
- Abstract SHA-256: `571968c317888e7916eae007e20937de86d51c5b1b28ad955945ff95f5d5bc37`

**Source abstract (verbatim):**

```text
The increasing frequency of natural disasters poses severe threats to human lives and leads to substantial economic losses. While 3D semantic segmentation is crucial for post-disaster assessment, existing deep learning models lack datasets specifically designed for post-disaster environments. To address this gap, we constructed a specialized 3D dataset using unmanned aerial vehicles (UAVs)-captured aerial footage of Hurricane Ian (2022) over affected areas, employing Structure-from-Motion (SfM) and Multi-View Stereo (MVS) techniques to reconstruct 3D point clouds. We evaluated the state-of-the-art (SOTA) 3D semantic segmentation models, Fast Point Transformer (FPT), Point Transformer v3 (PTv3), and OA-CNNs on this dataset, exposing significant limitations in existing methods for disaster-stricken regions. These findings underscore the urgent need for advancements in 3D segmentation techniques and the development of specialized 3D benchmark datasets to improve post-disaster scene understanding and response.
```

**Extracted claims (4; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
A specialized 3D dataset was constructed using UAVs-captured aerial footage of Hurricane Ian.
```

Evidence excerpt (verbatim):

```text
To address this gap, we constructed a specialized 3D dataset using unmanned aerial vehicles (UAVs)-captured aerial footage of Hurricane Ian (2022) over affected areas
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
Structure-from-Motion and Multi-View Stereo techniques were employed to reconstruct 3D point clouds.
```

Evidence excerpt (verbatim):

```text
employing Structure-from-Motion (SfM) and Multi-View Stereo (MVS) techniques to reconstruct 3D point clouds
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
State-of-the-art 3D semantic segmentation models were evaluated on the constructed dataset.
```

Evidence excerpt (verbatim):

```text
We evaluated the state-of-the-art (SOTA) 3D semantic segmentation models, Fast Point Transformer (FPT), Point Transformer v3 (PTv3), and OA-CNNs on this dataset
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
Existing methods showed significant limitations in disaster-stricken regions.
```

Evidence excerpt (verbatim):

```text
exposing significant limitations in existing methods for disaster-stricken regions
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.23709v3`
- Title: Stream-DiffVSR: Low-Latency Streamable Video Super-Resolution via Auto-Regressive Diffusion
- Publication date: 2025-12-29T18:59:57Z
- Source: https://arxiv.org/abs/2512.23709v3
- Candidate selection metadata: same broad category `cs.CV`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Diffusion-based video super-resolution (VSR) methods deliver strong perceptual quality but are often unsuitable for latency-sensitive scenarios due to reliance on future frames and expensive multi-step denoising. We propose Stream-DiffVSR, a causally conditioned diffusion framework for efficient online VSR. Operating strictly on past frames, Stream-DiffVSR integrates a four-step distilled denoiser for fast inference, an Auto-regressive Temporal Guidance (ARTG) module that injects motion-aligned cues during latent denoising, and a lightweight temporal-aware decoder with a Temporal Processor Module (TPM) to enhance detail and temporal coherence. Unlike chunk-wise streaming inference, our strictly frame-by-frame causal design avoids sequence-level waiting, substantially reducing time-to-first-frame and end-to-end latency. Stream-DiffVSR processes 720p frames in 0.328 seconds on an RTX 4090 and consistently outperforms prior diffusion-based baselines. Compared with the online state-of-the-art TMP, it improves perceptual quality (LPIPS +0.095). Compared with prior diffusion-based VSR methods such as MGLD-VSR, it reduces per-frame runtime by over 130x. Moreover, Stream-DiffVSR substantially lowers time-to-first-frame for diffusion-based VSR, reducing initial delay from over 4600 seconds to 0.328 seconds, making diffusion-based VSR markedly more practical for low-latency online and streaming deployment. Project page: https://jamichss.github.io/stream-diffvsr-project-page/
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 6. Extending Affordance Segmentation for Wearable Robots to Multi-Object Images

- Paper ID: `2610.29474v1`
- Publication date: 2026-10-21T09:30:14Z
- Source: https://arxiv.org/abs/2610.29474v1
- Category metadata: `cs.CV`
- Abstract SHA-256: `9862bb993de45fbbd0a95492cbb07df18e2709d53d4972ea1216d120319f0eb1`

**Source abstract (verbatim):**

```text
This paper proposes a refinement to existing vision-based portable pipelines for the recognition of graspable object parts. Such pipelines can effectively support automatic grasp selection and preshaping in upper-limb prosthetic devices. However, realistic scenarios in which multiple objects are present still represent a challenge. The proposed method exploits a minor modification to the conventional hardware setup and a custom training approach to extend the applicability of vision-based pipelines. A laser pointer is introduced in the setup as an effective mechanism for object disambiguation. Accordingly, a suitable retraining of the deep convolutional neural networks supporting recognition of graspable parts is implemented. A mixed reality strategy allows the reuse of available high-quality segmentation masks to generate realistic images procedurally, extending the range of scenarios supported by the final device. Experimental results confirm that the proposed pipeline improves target disambiguation accuracy by up to 9% compared with existing solutions, while preserving the computational cost.
```

**Extracted claims (5; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
The proposed method improves target disambiguation accuracy by up to 9% compared with existing solutions.
```

Evidence excerpt (verbatim):

```text
Experimental results confirm that the proposed pipeline improves target disambiguation accuracy by up to 9% compared with existing solutions
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
A laser pointer is introduced as an effective mechanism for object disambiguation in the hardware setup.
```

Evidence excerpt (verbatim):

```text
A laser pointer is introduced in the setup as an effective mechanism for object disambiguation.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
The method involves a minor modification to the conventional hardware setup.
```

Evidence excerpt (verbatim):

```text
The proposed method exploits a minor modification to the conventional hardware setup
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
A custom training approach is implemented to extend the applicability of vision-based pipelines.
```

Evidence excerpt (verbatim):

```text
and a custom training approach to extend the applicability of vision-based pipelines.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
A mixed reality strategy allows the reuse of high-quality segmentation masks to generate realistic images procedurally.
```

Evidence excerpt (verbatim):

```text
A mixed reality strategy allows the reuse of available high-quality segmentation masks to generate realistic images procedurally
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2610.29246v1`
- Title: DepState-JEPA: Learning Depth-Grounded State Representation for Visual Perception and Manipulation
- Publication date: 2026-10-21T05:51:06Z
- Source: https://arxiv.org/abs/2610.29246v1
- Candidate selection metadata: same broad category `cs.CV`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Predictive representations for robot manipulation should connect scene geometry with the state changes induced by actions. Our intuition is that understanding what an action will change starts with understanding where things are: complementary RGB and depth observations ground a common scene representation from which to infer those changes. Guided by this intuition, we introduce \textbf{DepState-JEPA}, a dual-stream RGB--Depth joint-embedding predictive architecture that connects spatial understanding with action-conditioned prediction through a shared latent state, \textbf{DepState}. Built on V-JEPA~2.1, the framework uses depth both as a complementary observation stream and to ground both modalities in metric 3D space, aggregating shared information into DepState while retaining modality-private features for decoding. Ray-conditioned readouts predict local features without target depth; after an action-conditioned transition, the same decoders predict future RGB and depth features using the predicted state and fixed initial private features. Robot-state readouts provide recursive proprioceptive inputs; object-trajectory supervision and calibrated forward kinematics shape state learning through motion targets and joint--TCP consistency. Comparisons show stronger RGB-encoder transfer after RGB-D adaptation, feature completion, conditioned visual forecasting, and manipulation success. Within-model ablations identify contributions from depth content, metric coordinates, and future-state matching, with additional control gains from FK regularization.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 7. Stream-DiffVSR: Low-Latency Streamable Video Super-Resolution via Auto-Regressive Diffusion

- Paper ID: `2512.23709v3`
- Publication date: 2025-12-29T18:59:57Z
- Source: https://arxiv.org/abs/2512.23709v3
- Category metadata: `cs.CV`
- Abstract SHA-256: `0494042c174fbf648f2fbea7fe4943ef06dbbb2dcdd29a737e6335fb6ef4c201`

**Source abstract (verbatim):**

```text
Diffusion-based video super-resolution (VSR) methods deliver strong perceptual quality but are often unsuitable for latency-sensitive scenarios due to reliance on future frames and expensive multi-step denoising. We propose Stream-DiffVSR, a causally conditioned diffusion framework for efficient online VSR. Operating strictly on past frames, Stream-DiffVSR integrates a four-step distilled denoiser for fast inference, an Auto-regressive Temporal Guidance (ARTG) module that injects motion-aligned cues during latent denoising, and a lightweight temporal-aware decoder with a Temporal Processor Module (TPM) to enhance detail and temporal coherence. Unlike chunk-wise streaming inference, our strictly frame-by-frame causal design avoids sequence-level waiting, substantially reducing time-to-first-frame and end-to-end latency. Stream-DiffVSR processes 720p frames in 0.328 seconds on an RTX 4090 and consistently outperforms prior diffusion-based baselines. Compared with the online state-of-the-art TMP, it improves perceptual quality (LPIPS +0.095). Compared with prior diffusion-based VSR methods such as MGLD-VSR, it reduces per-frame runtime by over 130x. Moreover, Stream-DiffVSR substantially lowers time-to-first-frame for diffusion-based VSR, reducing initial delay from over 4600 seconds to 0.328 seconds, making diffusion-based VSR markedly more practical for low-latency online and streaming deployment. Project page: https://jamichss.github.io/stream-diffvsr-project-page/
```

**Extracted claims (9; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
Stream-DiffVSR is a causally conditioned diffusion framework for efficient online video super-resolution.
```

Evidence excerpt (verbatim):

```text
We propose Stream-DiffVSR, a causally conditioned diffusion framework for efficient online VSR.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
Stream-DiffVSR integrates a four-step distilled denoiser for fast inference.
```

Evidence excerpt (verbatim):

```text
Stream-DiffVSR integrates a four-step distilled denoiser for fast inference,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
Stream-DiffVSR includes an Auto-regressive Temporal Guidance (ARTG) module that injects motion-aligned cues during latent denoising.
```

Evidence excerpt (verbatim):

```text
an Auto-regressive Temporal Guidance (ARTG) module that injects motion-aligned cues during latent denoising,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
Stream-DiffVSR employs a lightweight temporal-aware decoder with a Temporal Processor Module (TPM) to enhance detail and temporal coherence.
```

Evidence excerpt (verbatim):

```text
and a lightweight temporal-aware decoder with a Temporal Processor Module (TPM) to enhance detail and temporal coherence.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
Stream-DiffVSR processes 720p frames in 0.328 seconds on an RTX 4090.
```

Evidence excerpt (verbatim):

```text
Stream-DiffVSR processes 720p frames in 0.328 seconds on an RTX 4090
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 6

Claim (verbatim):

```text
Stream-DiffVSR consistently outperforms prior diffusion-based baselines.
```

Evidence excerpt (verbatim):

```text
and consistently outperforms prior diffusion-based baselines.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 7

Claim (verbatim):

```text
Compared with the online state-of-the-art TMP, Stream-DiffVSR improves perceptual quality (LPIPS +0.095).
```

Evidence excerpt (verbatim):

```text
Compared with the online state-of-the-art TMP, it improves perceptual quality (LPIPS +0.095).
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 8

Claim (verbatim):

```text
Compared with prior diffusion-based VSR methods such as MGLD-VSR, Stream-DiffVSR reduces per-frame runtime by over 130x.
```

Evidence excerpt (verbatim):

```text
Compared with prior diffusion-based VSR methods such as MGLD-VSR, it reduces per-frame runtime by over 130x.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 9

Claim (verbatim):

```text
Stream-DiffVSR substantially lowers time-to-first-frame for diffusion-based VSR, reducing initial delay from over 4600 seconds to 0.328 seconds.
```

Evidence excerpt (verbatim):

```text
Moreover, Stream-DiffVSR substantially lowers time-to-first-frame for diffusion-based VSR, reducing initial delay from over 4600 seconds to 0.328 seconds,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2610.29611v1`
- Title: Diff-IrisPAD: Modeling Bona Fide Iris Distributions for Unsupervised Presentation Attack Detection
- Publication date: 2026-10-21T11:51:28Z
- Source: https://arxiv.org/abs/2610.29611v1
- Candidate selection metadata: same broad category `cs.CV`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate postdates focal and is temporally ineligible on current evidence
- Source abstract (verbatim):

```text
Iris recognition systems are vulnerable to presentation attacks (PAs), including textured contact lenses, print replays, and synthetic irises. Existing PAD methods rely on supervised learning with attack data, limiting generalization to unseen attacks and new sensors. We propose Diff-IrisPAD, an unsupervised framework based on Brownian Bridge Diffusion that models bona fide iris distributions without using attack samples. The method reconstructs clean iris textures from degraded inputs and detects attacks via reconstruction inconsistency using ViT scoring and pixel-level measures. Experiments on a large-scale multi-sensor dataset (125K+ images, NIR and VIS, 8 attack types) show that Diff-IrisPAD achieves an overall ACER of 30.52, significantly outperforming diffusion-based baselines while demonstrating strong generalization to unseen attacks. These results highlight the effectiveness of diffusion-based bona fide modeling for robust and scalable iris PAD.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 8. Parallelizable Probabilistic Latent Reasoning for Diverse Reasoning Trajectories

- Paper ID: `2610.29385v1`
- Publication date: 2026-10-21T08:11:52Z
- Source: https://arxiv.org/abs/2610.29385v1
- Category metadata: `cs.LG`
- Abstract SHA-256: `0c1327b26dbf24f43d24f9ae32d9f3299fe5cff100fb4eedb9ce862733015653`

**Source abstract (verbatim):**

```text
Language models relying on verbalized Chain-of-Thought (CoT) are constrained to token-by-token generation in the language space, where many tokens serve textual coherence rather than core reasoning. This entangles genuine differences in logical trajectories with superficial variations in verbalization. Moving reasoning into a compact, continuous latent space offers a promising alternative for efficiently representing and exploring diverse reasoning trajectories. However, current latent models remain largely deterministic, capturing only a single reasoning trajectory rather than modeling a distribution over multiple valid alternatives. While stochastic approaches parameterize distributions over latent reasoning steps, they frequently suffer from unstable optimization and limited empirical performance. Furthermore, their reliance on autoregressive latent prediction during training precludes effective parallelization, leading to prohibitively long training times. To overcome these bottlenecks, we propose Probabilistic Latent Reasoning Models (PLRM), a parallelizable variational framework for probabilistic latent reasoning. PLRM adopts a JEPA-style objective in which the posterior infers latent distributions in parallel from observed reasoning trajectories, while the prior learns to predict the subsequent latent distribution via teacher forcing. To model heterogeneous reasoning processes, we introduce a discrete strategy variable together with a mixture-based prior, allowing the model to preserve the Gaussian-mixture structure induced by multiple distinct reasoning trajectories rather than collapsing them into a single Gaussian. Across diverse benchmarks, PLRM achieves performance competitive with deterministic latent reasoning models on single-trajectory datasets while enabling efficient training and consistently outperforming competing stochastic baselines on multi-trajectory datasets.
```

**Extracted claims (9; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
Language models relying on verbalized Chain-of-Thought (CoT) are constrained to token-by-token generation in the language space.
```

Evidence excerpt (verbatim):

```text
Language models relying on verbalized Chain-of-Thought (CoT) are constrained to token-by-token generation in the language space,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
Moving reasoning into a compact, continuous latent space offers a promising alternative for efficiently representing and exploring diverse reasoning trajectories.
```

Evidence excerpt (verbatim):

```text
Moving reasoning into a compact, continuous latent space offers a promising alternative for efficiently representing and exploring diverse reasoning trajectories.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
Current latent models remain largely deterministic, capturing only a single reasoning trajectory rather than modeling a distribution over multiple valid alternatives.
```

Evidence excerpt (verbatim):

```text
However, current latent models remain largely deterministic, capturing only a single reasoning trajectory rather than modeling a distribution over multiple valid alternatives.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
Stochastic approaches parameterize distributions over latent reasoning steps but frequently suffer from unstable optimization and limited empirical performance.
```

Evidence excerpt (verbatim):

```text
While stochastic approaches parameterize distributions over latent reasoning steps, they frequently suffer from unstable optimization and limited empirical performance.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
PLRM adopts a JEPA-style objective in which the posterior infers latent distributions in parallel from observed reasoning trajectories.
```

Evidence excerpt (verbatim):

```text
PLRM adopts a JEPA-style objective in which the posterior infers latent distributions in parallel from observed reasoning trajectories,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 6

Claim (verbatim):

```text
PLRM introduces a discrete strategy variable together with a mixture-based prior to model heterogeneous reasoning processes.
```

Evidence excerpt (verbatim):

```text
To model heterogeneous reasoning processes, we introduce a discrete strategy variable together with a mixture-based prior,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 7

Claim (verbatim):

```text
PLRM preserves the Gaussian-mixture structure induced by multiple distinct reasoning trajectories rather than collapsing them into a single Gaussian.
```

Evidence excerpt (verbatim):

```text
allowing the model to preserve the Gaussian-mixture structure induced by multiple distinct reasoning trajectories rather than collapsing them into a single Gaussian.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 8

Claim (verbatim):

```text
PLRM achieves performance competitive with deterministic latent reasoning models on single-trajectory datasets.
```

Evidence excerpt (verbatim):

```text
Across diverse benchmarks, PLRM achieves performance competitive with deterministic latent reasoning models on single-trajectory datasets while enabling efficient training and consistently outperforming competing stochastic baselines on multi-trajectory datasets.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 9

Claim (verbatim):

```text
PLRM consistently outperforms competing stochastic baselines on multi-trajectory datasets.
```

Evidence excerpt (verbatim):

```text
Across diverse benchmarks, PLRM achieves performance competitive with deterministic latent reasoning models on single-trajectory datasets while enabling efficient training and consistently outperforming competing stochastic baselines on multi-trajectory datasets.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.24139v5`
- Title: Colorful Pinball: Density-Weighted Quantile Regression for Conditional Guarantee of Conformal Prediction
- Publication date: 2025-12-30T11:02:35Z
- Source: https://arxiv.org/abs/2512.24139v5
- Candidate selection metadata: same broad category `cs.LG`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Although conformal prediction provides robust marginal coverage guarantees, achieving reliable conditional coverage for specific inputs remains challenging. While exact distribution-free conditional coverage is impossible with finite samples, recent work has focused on improving the conditional coverage of standard conformal procedures. Distinct from approaches that target relaxed notions of conditional coverage, we directly target the mean squared error of conditional coverage by refining the quantile regression components that underpin many conformal methods. Leveraging a Taylor expansion, we derive a sharp surrogate objective for quantile regression: a density-weighted pinball loss, where the weights are given by the conditional density of the nonconformity score evaluated at the true quantile. We propose a three-headed quantile network that estimates these weights via finite differences using auxiliary quantile levels at $1-α\pm δ$, subsequently fine-tuning the central quantile by optimizing the weighted loss. We provide a theoretical analysis with exact non-asymptotic guarantees characterizing the resulting excess risk. Extensive experiments on diverse high-dimensional real-world datasets demonstrate remarkable improvements in conditional coverage performance.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 9. Seeing through Denoising: Frequency-guided One-step Denoising for Infrared Small Target Detection

- Paper ID: `2610.29361v1`
- Publication date: 2026-10-21T07:51:11Z
- Source: https://arxiv.org/abs/2610.29361v1
- Category metadata: `cs.CV`
- Abstract SHA-256: `491aa19fef0f8c67873ecfd116137c1573b3bd0611c5582af49a6ca47b9ef811`

**Source abstract (verbatim):**

```text
Infrared small target detection (IRSTD) is a challenging task due to the extremely small size of targets, low signal-to-noise ratios, and heavy background clutter in infrared imagery. While the progress of deep learning has advanced this field, existing methods primarily adopt discriminative paradigms that directly map images to target masks, overlooking the potential of generative modeling. In this paper, we propose DiffIRSTD, a novel generative framework that reformulates infrared small target detection as a background reconstruction problem. Instead of explicitly predicting target regions, we reinterpret small targets as noise-like signals and leverage a diffusion-based model to recover a clean, target-free background from a perturbed input image. The residual between the reconstructed background and the original image is then exploited to highlight candidate target regions, providing explicit cues for subsequent detection. To address the computational cost typically associated with diffusion sampling, we introduce a one-step denoising strategy that enables efficient background reconstruction while maintaining practical inference speed. Furthermore, we present a frequency-guided perception loss to preserve high-frequency background details and focus more on the reconstruction quality of target regions. More importantly, our DiffIRSTD operates as a plug-and-play framework, compatible with existing IRSTD models without increasing the computational complexity of detectors. Extensive experiments on IRSTD-1K, NUAA-SIRST, and NUDT-SIRST datasets demonstrate the superiority of our method, achieving state-of-the-art performance across three benchmarks.
```

**Extracted claims (6; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
The paper proposes a novel generative framework for infrared small target detection that reformulates the task as a background reconstruction problem.
```

Evidence excerpt (verbatim):

```text
In this paper, we propose DiffIRSTD, a novel generative framework that reformulates infrared small target detection as a background reconstruction problem.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
The method reinterprets small targets as noise-like signals and uses a diffusion-based model to recover a clean, target-free background from a perturbed input image.
```

Evidence excerpt (verbatim):

```text
Instead of explicitly predicting target regions, we reinterpret small targets as noise-like signals and leverage a diffusion-based model to recover a clean, target-free background from a perturbed input image.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
The residual between the reconstructed background and the original image is used to highlight candidate target regions.
```

Evidence excerpt (verbatim):

```text
The residual between the reconstructed background and the original image is then exploited to highlight candidate target regions, providing explicit cues for subsequent detection.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
A frequency-guided perception loss is presented to preserve high-frequency background details and focus on the reconstruction quality of target regions.
```

Evidence excerpt (verbatim):

```text
Furthermore, we present a frequency-guided perception loss to preserve high-frequency background details and focus more on the reconstruction quality of target regions.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
The proposed framework is compatible with existing IRSTD models without increasing the computational complexity of detectors.
```

Evidence excerpt (verbatim):

```text
More importantly, our DiffIRSTD operates as a plug-and-play framework, compatible with existing IRSTD models without increasing the computational complexity of detectors.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 6

Claim (verbatim):

```text
Extensive experiments on IRSTD-1K, NUAA-SIRST, and NUDT-SIRST datasets demonstrate the superiority of the method, achieving state-of-the-art performance across three benchmarks.
```

Evidence excerpt (verbatim):

```text
Extensive experiments on IRSTD-1K, NUAA-SIRST, and NUDT-SIRST datasets demonstrate the superiority of our method, achieving state-of-the-art performance across three benchmarks.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2610.29246v1`
- Title: DepState-JEPA: Learning Depth-Grounded State Representation for Visual Perception and Manipulation
- Publication date: 2026-10-21T05:51:06Z
- Source: https://arxiv.org/abs/2610.29246v1
- Candidate selection metadata: same broad category `cs.CV`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Predictive representations for robot manipulation should connect scene geometry with the state changes induced by actions. Our intuition is that understanding what an action will change starts with understanding where things are: complementary RGB and depth observations ground a common scene representation from which to infer those changes. Guided by this intuition, we introduce \textbf{DepState-JEPA}, a dual-stream RGB--Depth joint-embedding predictive architecture that connects spatial understanding with action-conditioned prediction through a shared latent state, \textbf{DepState}. Built on V-JEPA~2.1, the framework uses depth both as a complementary observation stream and to ground both modalities in metric 3D space, aggregating shared information into DepState while retaining modality-private features for decoding. Ray-conditioned readouts predict local features without target depth; after an action-conditioned transition, the same decoders predict future RGB and depth features using the predicted state and fixed initial private features. Robot-state readouts provide recursive proprioceptive inputs; object-trajectory supervision and calibrated forward kinematics shape state learning through motion targets and joint--TCP consistency. Comparisons show stronger RGB-encoder transfer after RGB-D adaptation, feature completion, conditioned visual forecasting, and manipulation success. Within-model ablations identify contributions from depth content, metric coordinates, and future-state matching, with additional control gains from FK regularization.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 10. RCSD: Reinforcement and Continual Learning for Domain-Specific Speculative Decoding

- Paper ID: `2610.29527v1`
- Publication date: 2026-10-21T10:16:23Z
- Source: https://arxiv.org/abs/2610.29527v1
- Category metadata: `cs.CL`
- Abstract SHA-256: `5800c5adb25d78732a98925bbb13a42fb29105bdcd9e6eb0f3336ffcec87faa1`

**Source abstract (verbatim):**

```text
Speculative decoding accelerates large language model inference by employing a compact draft model to propose candidate tokens that are verified in parallel by a target model. Conventional training relies on soft-label distillation, which forces the draft model to mimic the target's full output distribution, including high-entropy regions that degrade acceptance rates and increase early rejection risk. We propose RCSD (Reinforcement and Continual Learning for Speculative Decoding), a training framework that aligns draft model optimization with the system-level objective of maximizing acceptance length. RCSD leverages naturally occurring accepted and rejected sequences during speculative inference to construct implicit preference pairs, with masked loss to avoid penalizing target-aligned tokens. Evaluated across multiple benchmarks, RCSD improves average acceptance length by 35% over HASS and achieves 1.35x faster end-to-end inference than HASS on practical workloads, without compromising generation quality.
```

**Extracted claims (4; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
RCSD is a training framework that aligns draft model optimization with the system-level objective of maximizing acceptance length.
```

Evidence excerpt (verbatim):

```text
We propose RCSD (Reinforcement and Continual Learning for Speculative Decoding), a training framework that aligns draft model optimization with the system-level objective of maximizing acceptance length.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
RCSD constructs implicit preference pairs using naturally occurring accepted and rejected sequences during speculative inference.
```

Evidence excerpt (verbatim):

```text
RCSD leverages naturally occurring accepted and rejected sequences during speculative inference to construct implicit preference pairs, with masked loss to avoid penalizing target-aligned tokens.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
RCSD improves average acceptance length by 35% over HASS.
```

Evidence excerpt (verbatim):

```text
Evaluated across multiple benchmarks, RCSD improves average acceptance length by 35% over HASS and achieves 1.35x faster end-to-end inference than HASS on practical workloads, without compromising generation quality.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
RCSD achieves 1.35x faster end-to-end inference than HASS on practical workloads.
```

Evidence excerpt (verbatim):

```text
Evaluated across multiple benchmarks, RCSD improves average acceptance length by 35% over HASS and achieves 1.35x faster end-to-end inference than HASS on practical workloads, without compromising generation quality.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2610.29424v1`
- Title: A KAN-based Non-linear Factorization for Embedding Layer Compression
- Publication date: 2026-10-21T08:49:06Z
- Source: https://arxiv.org/abs/2610.29424v1
- Candidate selection metadata: same broad category `cs.CL`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Among existing embedding compression approaches, low-rank factorization provides a simple and mathematically principled solution by approximating the embedding matrix with a reduced-rank decomposition. However, its practical effectiveness is often limited, as the resulting linear bottleneck constrains representational capacity. To overcome these limitations, we propose an enhanced factorization scheme that increases expressive power by introducing learnable non-linear projections within the compressed embedding layer. Our method is inspired by the Kolmogorov Arnold Networks (KAN) paradigm, which replaces fixed linear transformations with learnable univariate functions. Despite promising results in other domains, applications of KANs in NLP remain scarce and have so far been largely limited to final or task specific layers, rather than core representational components such as embedding layers. We evaluate the proposed approach by integrating the compressed embedding layer into the Skip-gram framework and comparing it against a standard low-rank baseline under matched parameter budgets on the Word Analogy and Semantic Similarity benchmarks. We further introduce an effective initialization strategy from a pre-trained, uncompressed embedding layer. The behavior of the model is analyzed both immediately after initialization and after a brief post-initialization refinement phase, considering training with the standard Skip-gram objective as well as variants augmented with distillation from the original embedding layer. Overall, our results show that augmenting low-rank factorization with learnable non-linear projections effectively mitigates the limitations of linear bottlenecks, yielding more faithful compressed embeddings under fixed dimensionality and suggesting a promising direction for embedding layer compression beyond purely linear methods.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 11. Diff-IrisPAD: Modeling Bona Fide Iris Distributions for Unsupervised Presentation Attack Detection

- Paper ID: `2610.29611v1`
- Publication date: 2026-10-21T11:51:28Z
- Source: https://arxiv.org/abs/2610.29611v1
- Category metadata: `cs.CV`
- Abstract SHA-256: `e7854518d602e9ad65084bafd5b99f8568d7b5ceea2eb780e34511ed53d8562b`

**Source abstract (verbatim):**

```text
Iris recognition systems are vulnerable to presentation attacks (PAs), including textured contact lenses, print replays, and synthetic irises. Existing PAD methods rely on supervised learning with attack data, limiting generalization to unseen attacks and new sensors. We propose Diff-IrisPAD, an unsupervised framework based on Brownian Bridge Diffusion that models bona fide iris distributions without using attack samples. The method reconstructs clean iris textures from degraded inputs and detects attacks via reconstruction inconsistency using ViT scoring and pixel-level measures. Experiments on a large-scale multi-sensor dataset (125K+ images, NIR and VIS, 8 attack types) show that Diff-IrisPAD achieves an overall ACER of 30.52, significantly outperforming diffusion-based baselines while demonstrating strong generalization to unseen attacks. These results highlight the effectiveness of diffusion-based bona fide modeling for robust and scalable iris PAD.
```

**Extracted claims (4; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
Diff-IrisPAD is an unsupervised framework that models bona fide iris distributions without using attack samples.
```

Evidence excerpt (verbatim):

```text
We propose Diff-IrisPAD, an unsupervised framework based on Brownian Bridge Diffusion that models bona fide iris distributions without using attack samples.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
Diff-IrisPAD detects presentation attacks by identifying reconstruction inconsistency from degraded inputs.
```

Evidence excerpt (verbatim):

```text
The method reconstructs clean iris textures from degraded inputs and detects attacks via reconstruction inconsistency using ViT scoring and pixel-level measures.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
Diff-IrisPAD significantly outperforms diffusion-based baselines in performance.
```

Evidence excerpt (verbatim):

```text
Diff-IrisPAD achieves an overall ACER of 30.52, significantly outperforming diffusion-based baselines while demonstrating strong generalization to unseen attacks.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
Diff-IrisPAD demonstrates strong generalization to unseen attacks.
```

Evidence excerpt (verbatim):

```text
Diff-IrisPAD achieves an overall ACER of 30.52, significantly outperforming diffusion-based baselines while demonstrating strong generalization to unseen attacks.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.24593v1`
- Title: 3D Semantic Segmentation for Post-Disaster Assessment
- Publication date: 2025-12-31T03:30:58Z
- Source: https://arxiv.org/abs/2512.24593v1
- Candidate selection metadata: same broad category `cs.CV`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
The increasing frequency of natural disasters poses severe threats to human lives and leads to substantial economic losses. While 3D semantic segmentation is crucial for post-disaster assessment, existing deep learning models lack datasets specifically designed for post-disaster environments. To address this gap, we constructed a specialized 3D dataset using unmanned aerial vehicles (UAVs)-captured aerial footage of Hurricane Ian (2022) over affected areas, employing Structure-from-Motion (SfM) and Multi-View Stereo (MVS) techniques to reconstruct 3D point clouds. We evaluated the state-of-the-art (SOTA) 3D semantic segmentation models, Fast Point Transformer (FPT), Point Transformer v3 (PTv3), and OA-CNNs on this dataset, exposing significant limitations in existing methods for disaster-stricken regions. These findings underscore the urgent need for advancements in 3D segmentation techniques and the development of specialized 3D benchmark datasets to improve post-disaster scene understanding and response.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 12. A Transfer Learning-Driven Methodology for Efficient and Sustainable Indoor Localization Using VLC

- Paper ID: `2610.29594v1`
- Publication date: 2026-10-21T11:33:42Z
- Source: https://arxiv.org/abs/2610.29594v1
- Category metadata: `cs.LG`
- Abstract SHA-256: `1b8caaf758cf4fda8df770bcc0fa951bac9cbccaa2e0f6851c64c5b1cee9668c`

**Source abstract (verbatim):**

```text
The rapid expansion of the Internet of Things enables seamless collaboration among connected devices, making indoor localization a critical component of industrial automation. However, conventional localization techniques struggle in dynamic environments. These methods depend on extensive, frequent data collection and environment-specific calibration, limiting scalability, interoperability, and effective use of prior research while imposing significant energy penalties that hinder practical deployment. To address these challenges, we propose an energy-efficient transfer learning (TL) based approach for visible light communication based indoor localization. Our method leverages TL to tackle environmental variability, including lighting fluctuations and physical obstacles that typically degrade localization performance, while simultaneously reducing computational overhead and energy consumption compared to conventional approaches. We also introduce a novel model efficiency (ME) metric, designed to integrate localization accuracy, energy efficiency, data efficiency, and transfer gain into a single evaluative measure for comprehensive optimization. Evaluations on a real-world dataset collected from a BOSCH factory demonstrate that our model achieves a 47% improvement in localization accuracy compared to a conventional model that does not utilize TL, and achieves up to 67.5% ME with TL models, compared to only 10.4% in conventional models under high-noise conditions. These results underscore the potential of our approach to deliver a highly efficient and scalable indoor localization system suitable for energy-constrained industrial applications.
```

**Extracted claims (5; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
The proposed method utilizes transfer learning to address environmental variability in indoor localization.
```

Evidence excerpt (verbatim):

```text
Our method leverages TL to tackle environmental variability, including lighting fluctuations and physical obstacles that typically degrade localization performance
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
The method reduces computational overhead and energy consumption compared to conventional approaches.
```

Evidence excerpt (verbatim):

```text
Our method leverages TL to tackle environmental variability, including lighting fluctuations and physical obstacles that typically degrade localization performance, while simultaneously reducing computational overhead and energy consumption compared to conventional approaches
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
A novel model efficiency (ME) metric is introduced to evaluate localization performance.
```

Evidence excerpt (verbatim):

```text
We also introduce a novel model efficiency (ME) metric, designed to integrate localization accuracy, energy efficiency, data efficiency, and transfer gain into a single evaluative measure for comprehensive optimization
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
The proposed method achieves a 47% improvement in localization accuracy compared to conventional models.
```

Evidence excerpt (verbatim):

```text
Evaluations on a real-world dataset collected from a BOSCH factory demonstrate that our model achieves a 47% improvement in localization accuracy compared to a conventional model that does not utilize TL
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
The proposed method achieves up to 67.5% ME with TL models under high-noise conditions.
```

Evidence excerpt (verbatim):

```text
and achieves up to 67.5% ME with TL models, compared to only 10.4% in conventional models under high-noise conditions
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2610.29515v1`
- Title: BRIDGE: An Acceptance Gate to Block False Improvements in Model Updates, with a Retrospective Clinical Evaluation
- Publication date: 2026-10-21T10:04:40Z
- Source: https://arxiv.org/abs/2610.29515v1
- Candidate selection metadata: same broad category `cs.LG`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Models are updated repeatedly, and an update that looks better on validation data but not on new data is a false improvement that can misguide clinical decisions. The naive rule accepts every positive validation gain and is optimistic when the same data choose and judge the update. BRIDGE is a model-agnostic acceptance gate that decides each update from predictions and the available labels, with fixed settings. Each fold of the data judges the update chosen on the other folds (cross-fitting) to reduce selection bias; acceptance requires the gain's lower bootstrap bound to exceed a margin. The four settings are (A) 11 new datasets, (B) synthetic tasks, (C) 12 retrospective clinical tasks, and (D) 39 supporting datasets. The false-improvement rate falls from 19.1% (naive) to 1.1% (BRIDGE) in (A), 20.7% to 1.7% (B), 20.0% to 0% (C), and 12.5% to 0.5% (D); every 95% confidence interval of the reduction over datasets or tasks excludes zero (not over the clinical sources). An equal-size random draw from the naive acceptances contains more false improvements in (A)-(E) (post hoc, p<0.001). On the OpenML collection (E) of 14 new datasets, the false-improvement rate falls from 25.6% to 1.0%. BRIDGE removes 97% to 100% of the false improvements that the naive rule accepts, and its mean gain per deployed update is 1.8 to 3.1 times the naive rule's. The 95% upper bound on the false-improvement rate is below 5.5%: formal in (B) for independent tasks (3.56%), and conditional on the real data tested (0.33% to 5.40%).
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 13. StressRoBERTa: Cross-Condition Transfer Learning from Depression, Anxiety, and PTSD to Stress Detection

- Paper ID: `2512.23813v1`
- Publication date: 2025-12-29T19:16:14Z
- Source: https://arxiv.org/abs/2512.23813v1
- Category metadata: `cs.CL`
- Abstract SHA-256: `3dd3be0ba571430be5f92edd432e0e91955e344931404104e2cf2fe8c785175c`

**Source abstract (verbatim):**

```text
The prevalence of chronic stress represents a significant public health concern, with social media platforms like Twitter serving as important venues for individuals to share their experiences. This paper introduces StressRoBERTa, a cross-condition transfer learning approach for automatic detection of self-reported chronic stress in English tweets. The investigation examines whether continual training on clinically related conditions (depression, anxiety, PTSD), disorders with high comorbidity with chronic stress, improves stress detection compared to general language models and broad mental health models. RoBERTa is continually trained on the Stress-SMHD corpus (108M words from users with self-reported diagnoses of depression, anxiety, and PTSD) and fine-tuned on the SMM4H 2022 Task 8 dataset. StressRoBERTa achieves 82% F1-score, outperforming the best shared task system (79% F1) by 3 percentage points. The results demonstrate that focused cross-condition transfer from stress-related disorders (+1% F1 over vanilla RoBERTa) provides stronger representations than general mental health training. Evaluation on Dreaddit (81% F1) further demonstrates transfer from clinical mental health contexts to situational stress discussions.
```

**Extracted claims (5; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
StressRoBERTa is a cross-condition transfer learning approach for automatic detection of self-reported chronic stress in English tweets.
```

Evidence excerpt (verbatim):

```text
This paper introduces StressRoBERTa, a cross-condition transfer learning approach for automatic detection of self-reported chronic stress in English tweets.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
Continual training on clinically related conditions (depression, anxiety, PTSD) improves stress detection compared to general language models and broad mental health models.
```

Evidence excerpt (verbatim):

```text
The investigation examines whether continual training on clinically related conditions (depression, anxiety, PTSD), disorders with high comorbidity with chronic stress, improves stress detection compared to general language models and broad mental health models.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
StressRoBERTa achieves an F1-score of 82%, outperforming the best shared task system by 3 percentage points.
```

Evidence excerpt (verbatim):

```text
StressRoBERTa achieves 82% F1-score, outperforming the best shared task system (79% F1) by 3 percentage points.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
Focused cross-condition transfer from stress-related disorders provides stronger representations than general mental health training.
```

Evidence excerpt (verbatim):

```text
The results demonstrate that focused cross-condition transfer from stress-related disorders (+1% F1 over vanilla RoBERTa) provides stronger representations than general mental health training.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
Evaluation on Dreaddit shows that transfer from clinical mental health contexts to situational stress discussions achieves an F1-score of 81%.
```

Evidence excerpt (verbatim):

```text
Evaluation on Dreaddit (81% F1) further demonstrates transfer from clinical mental health contexts to situational stress discussions.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.23647v1`
- Title: Nested Browser-Use Learning for Agentic Information Seeking
- Publication date: 2025-12-29T17:59:14Z
- Source: https://arxiv.org/abs/2512.23647v1
- Candidate selection metadata: same broad category `cs.CL`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Information-seeking (IS) agents have achieved strong performance across a range of wide and deep search tasks, yet their tool use remains largely restricted to API-level snippet retrieval and URL-based page fetching, limiting access to the richer information available through real browsing. While full browser interaction could unlock deeper capabilities, its fine-grained control and verbose page content returns introduce substantial complexity for ReAct-style function-calling agents. To bridge this gap, we propose Nested Browser-Use Learning (NestBrowse), which introduces a minimal and complete browser-action framework that decouples interaction control from page exploration through a nested structure. This design simplifies agentic reasoning while enabling effective deep-web information acquisition. Empirical results on challenging deep IS benchmarks demonstrate that NestBrowse offers clear benefits in practice. Further in-depth analyses underscore its efficiency and flexibility.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 14. Reader--Writer Coupling in Transformer MLPs

- Paper ID: `2610.29340v1`
- Publication date: 2026-10-21T07:35:23Z
- Source: https://arxiv.org/abs/2610.29340v1
- Category metadata: `cs.CL`
- Abstract SHA-256: `85a3255a7d5a80e92339d0ba6431d9c0485ff3e081c24f3228240e9071b04a18`

**Source abstract (verbatim):**

```text
A transformer MLP gives each hidden channel two roles: a reader that decides when the channel responds, and a writer that decides what it adds back to the residual stream. Read as a key--value memory, the layer can be measured one factor set at a time: the pairing of readers to writers is carried only by their shared index, invisible to any quantity computed from one factor set alone. Yet training couples the two factors through their joint update, so we ask what reading them together shows. The block supplies the joint instrument: the MLP writes back into the very stream it reads, so the exact Jacobian of its update is square, and its agreement with its own transpose resolves into reader--writer terms whose inner products give each channel, read as a couple, a signed pairing coordinate. Ranked by this coordinate, each block we measure has a small core of strongly coupled channels; where initialization gives either sign equally, the core is nearly all opposed: each writer points against the direction its reader responds to. This opposed core recurs from the smallest models trained from scratch to released checkpoints; its sign is in place within a few percent of training and holds while the coupling grows. Read as couples, most channels return their contribution against the reader that fired it, and the readers of later blocks take it up; few show in the logits. Training holds the couples in place: flipping the opposed writers moves the output toward common tokens, and a writer permuted onto another reader regrows to fit that reader while the reader stays.
```

**Extracted claims (5; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
A transformer MLP assigns each hidden channel two roles: a reader that decides when the channel responds, and a writer that decides what it adds back to the residual stream.
```

Evidence excerpt (verbatim):

```text
A transformer MLP gives each hidden channel two roles: a reader that decides when the channel responds, and a writer that decides what it adds back to the residual stream.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
Ranked by this coordinate, each block we measure has a small core of strongly coupled channels.
```

Evidence excerpt (verbatim):

```text
Ranked by this coordinate, each block we measure has a small core of strongly coupled channels;
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
This opposed core recurs from the smallest models trained from scratch to released checkpoints; its sign is in place within a few percent of training and holds while the coupling grows.
```

Evidence excerpt (verbatim):

```text
This opposed core recurs from the smallest models trained from scratch to released checkpoints; its sign is in place within a few percent of training and holds while the coupling grows.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
Read as couples, most channels return their contribution against the reader that fired it, and the readers of later blocks take it up; few show in the logits.
```

Evidence excerpt (verbatim):

```text
Read as couples, most channels return their contribution against the reader that fired it, and the readers of later blocks take it up; few show in the logits.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
Training holds the couples in place: flipping the opposed writers moves the output toward common tokens, and a writer permuted onto another reader regrows to fit that reader while the reader stays.
```

Evidence excerpt (verbatim):

```text
Training holds the couples in place: flipping the opposed writers moves the output toward common tokens, and a writer permuted onto another reader regrows to fit that reader while the reader stays.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.23049v1`
- Title: Accelerating Language Model Workflows with Prompt Choreography
- Publication date: 2025-12-28T19:21:11Z
- Source: https://arxiv.org/abs/2512.23049v1
- Candidate selection metadata: same broad category `cs.CL`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Large language models are increasingly deployed in multi-agent workflows. We introduce Prompt Choreography, a framework that efficiently executes LLM workflows by maintaining a dynamic, global KV cache. Each LLM call can attend to an arbitrary, reordered subset of previously encoded messages. Parallel calls are supported. Though caching messages' encodings sometimes gives different results from re-encoding them in a new context, we show in diverse settings that fine-tuning the LLM to work with the cache can help it mimic the original results. Prompt Choreography significantly reduces per-message latency (2.0--6.2$\times$ faster time-to-first-token) and achieves substantial end-to-end speedups ($>$2.2$\times$) in some workflows dominated by redundant computation.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 15. Every Part Has Its Role: Part-of-Speech Effects in LLM Post-Training

- Paper ID: `2610.29843v1`
- Publication date: 2026-10-21T15:05:51Z
- Source: https://arxiv.org/abs/2610.29843v1
- Category metadata: `cs.CL`
- Abstract SHA-256: `a29ffc1e03695496d1e26f146aa88f6951dd176f795b6cbcfa1c97d1ae5f4c72`

**Source abstract (verbatim):**

```text
Large language models are typically trained with next-token prediction (NTP), which rewards predicting specific tokens rather than explicitly accounting for the semantic similarities between different words or expressions. Prior work has addressed this limitation by augmenting training data with minimally varying sentences that replace a target word with conceptually related alternatives, e.g., "The tired coach ran home" $\rightarrow$ {"The tired trainer ran home", "The tired instructor ran home", ...}. Such concept augmentation improves performance, but it remains unclear whether its effectiveness depends on where in the sentence the concept is expressed. We reproduce and extend prior work $\textit{beyond nouns}$ to verbs and adjectives, asking whether the part of speech (POS) carrying the concept signal affects perplexity and downstream performance. We find different patterns across evaluation settings: concept augmentation improves perplexity most consistently on news, independent of the POS used, whereas verbs provide the most reliable downstream gains. Despite these behavioral differences, representational analyses using CKA and linear probing show that the conditions yielding the largest downstream gains are not necessarily those that most alter the model's internal representations. Together, these results suggest that the effectiveness of concept augmentation depends on where and how conceptual information is introduced during training.
```

**Extracted claims (4; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
Concept augmentation improves perplexity most consistently on news, independent of the part of speech used.
```

Evidence excerpt (verbatim):

```text
concept augmentation improves performance, but it remains unclear whether its effectiveness depends on where in the sentence the concept is expressed.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
Verbs provide the most reliable downstream gains from concept augmentation.
```

Evidence excerpt (verbatim):

```text
We find different patterns across evaluation settings: concept augmentation improves perplexity most consistently on news, independent of the POS used, whereas verbs provide the most reliable downstream gains.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
Representational analyses using CKA and linear probing show that the conditions yielding the largest downstream gains are not necessarily those that most alter the model's internal representations.
```

Evidence excerpt (verbatim):

```text
representational analyses using CKA and linear probing show that the conditions yielding the largest downstream gains are not necessarily those that most alter the model's internal representations.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
The effectiveness of concept augmentation depends on where and how conceptual information is introduced during training.
```

Evidence excerpt (verbatim):

```text
Together, these results suggest that the effectiveness of concept augmentation depends on where and how conceptual information is introduced during training.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.24939v1`
- Title: Vibe Coding, Interface Flattening
- Publication date: 2025-12-31T16:00:59Z
- Source: https://arxiv.org/abs/2512.24939v1
- Candidate selection metadata: same broad category `cs.CL`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Large language models are reshaping programming by enabling 'vibe coding': the development of softwares through natural-language interaction with model-driven toolchains. This article argues that vibe coding is best understood as interface flattening, a reconfiguration in which previously distinct modalities (GUI, CLI, and API) appear to converge into a single conversational surface, even as the underlying chain of translation from intention to machinic effect lengthens and thickens. Drawing on Friedrich Kittler's materialist media theory and Alexander Galloway's account of interfaces as sites of protocol control, the paper situates programming as a historically localised interface arrangement rather than an essential relation to computation. Through a materialist reconstruction of the contemporary vibe-coding stack, it shows how remote compute infrastructures, latency and connectivity, structured outputs, function/tool calling, and interoperability standards such as the Model Context Protocol relocate control and meaning-making power to model and protocol providers. The apparent democratisation of technical capability therefore depends on new dependencies and new literacies. By foregrounding the tension between experiential flattening and infrastructural thickening, I demonstrate how LLM-mediated development redistributes symbolic labour/power, obscures responsibility, and privatises competencies previously dispersed across programming communities, contributing a critical lens on the political economy of AI-mediated human-computer interaction.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 16. Nested Browser-Use Learning for Agentic Information Seeking

- Paper ID: `2512.23647v1`
- Publication date: 2025-12-29T17:59:14Z
- Source: https://arxiv.org/abs/2512.23647v1
- Category metadata: `cs.CL`
- Abstract SHA-256: `fde71dd935acb953bc5d01bcd48f0d6c3351db6a66126761baf134c114e7893c`

**Source abstract (verbatim):**

```text
Information-seeking (IS) agents have achieved strong performance across a range of wide and deep search tasks, yet their tool use remains largely restricted to API-level snippet retrieval and URL-based page fetching, limiting access to the richer information available through real browsing. While full browser interaction could unlock deeper capabilities, its fine-grained control and verbose page content returns introduce substantial complexity for ReAct-style function-calling agents. To bridge this gap, we propose Nested Browser-Use Learning (NestBrowse), which introduces a minimal and complete browser-action framework that decouples interaction control from page exploration through a nested structure. This design simplifies agentic reasoning while enabling effective deep-web information acquisition. Empirical results on challenging deep IS benchmarks demonstrate that NestBrowse offers clear benefits in practice. Further in-depth analyses underscore its efficiency and flexibility.
```

**Extracted claims (4; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
The proposed method introduces a minimal and complete browser-action framework that decouples interaction control from page exploration through a nested structure.
```

Evidence excerpt (verbatim):

```text
we propose Nested Browser-Use Learning (NestBrowse), which introduces a minimal and complete browser-action framework that decouples interaction control from page exploration through a nested structure.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
NestBrowse simplifies agentic reasoning while enabling effective deep-web information acquisition.
```

Evidence excerpt (verbatim):

```text
This design simplifies agentic reasoning while enabling effective deep-web information acquisition.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
Empirical results on challenging deep IS benchmarks demonstrate that NestBrowse offers clear benefits in practice.
```

Evidence excerpt (verbatim):

```text
Empirical results on challenging deep IS benchmarks demonstrate that NestBrowse offers clear benefits in practice.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
Further in-depth analyses underscore the efficiency and flexibility of NestBrowse.
```

Evidence excerpt (verbatim):

```text
Further in-depth analyses underscore its efficiency and flexibility.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.23049v1`
- Title: Accelerating Language Model Workflows with Prompt Choreography
- Publication date: 2025-12-28T19:21:11Z
- Source: https://arxiv.org/abs/2512.23049v1
- Candidate selection metadata: same broad category `cs.CL`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Large language models are increasingly deployed in multi-agent workflows. We introduce Prompt Choreography, a framework that efficiently executes LLM workflows by maintaining a dynamic, global KV cache. Each LLM call can attend to an arbitrary, reordered subset of previously encoded messages. Parallel calls are supported. Though caching messages' encodings sometimes gives different results from re-encoding them in a new context, we show in diverse settings that fine-tuning the LLM to work with the cache can help it mimic the original results. Prompt Choreography significantly reduces per-message latency (2.0--6.2$\times$ faster time-to-first-token) and achieves substantial end-to-end speedups ($>$2.2$\times$) in some workflows dominated by redundant computation.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 17. Deep Learning Approach for the Diagnosis of Pediatric Pneumonia Using Chest X-ray Imaging

- Paper ID: `2601.00041v1`
- Publication date: 2025-12-31T00:07:06Z
- Source: https://arxiv.org/abs/2601.00041v1
- Category metadata: `cs.CV`
- Abstract SHA-256: `8c67da8c8b0f572b3e8e9af39f9b3f575bf6a41ad51409d21997fc3db995d798`

**Source abstract (verbatim):**

```text
Pediatric pneumonia remains a leading cause of morbidity and mortality in children worldwide. Timely and accurate diagnosis is critical but often challenged by limited radiological expertise and the physiological and procedural complexity of pediatric imaging. This study investigates the performance of state-of-the-art convolutional neural network (CNN) architectures ResNetRS, RegNet, and EfficientNetV2 using transfer learning for the automated classification of pediatric chest Xray images as either pneumonia or normal.A curated subset of 1,000 chest X-ray images was extracted from a publicly available dataset originally comprising 5,856 pediatric images. All images were preprocessed and labeled for binary classification. Each model was fine-tuned using pretrained ImageNet weights and evaluated based on accuracy and sensitivity. RegNet achieved the highest classification performance with an accuracy of 92.4 and a sensitivity of 90.1, followed by ResNetRS (accuracy: 91.9, sensitivity: 89.3) and EfficientNetV2 (accuracy: 88.5, sensitivity: 88.1).
```

**Extracted claims (4; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
The study investigates the performance of state-of-the-art convolutional neural network architectures for the automated classification of pediatric chest X-ray images as either pneumonia or normal.
```

Evidence excerpt (verbatim):

```text
This study investigates the performance of state-of-the-art convolutional neural network (CNN) architectures ResNetRS, RegNet, and EfficientNetV2 using transfer learning for the automated classification of pediatric chest Xray images as either pneumonia or normal.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
A curated subset of 1,000 chest X-ray images was extracted from a publicly available dataset for binary classification.
```

Evidence excerpt (verbatim):

```text
A curated subset of 1,000 chest X-ray images was extracted from a publicly available dataset originally comprising 5,856 pediatric images.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
Each model was fine-tuned using pretrained ImageNet weights and evaluated based on accuracy and sensitivity.
```

Evidence excerpt (verbatim):

```text
Each model was fine-tuned using pretrained ImageNet weights and evaluated based on accuracy and sensitivity.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
RegNet achieved the highest classification performance with an accuracy of 92.4 and a sensitivity of 90.1.
```

Evidence excerpt (verbatim):

```text
RegNet achieved the highest classification performance with an accuracy of 92.4 and a sensitivity of 90.1, followed by ResNetRS (accuracy: 91.9, sensitivity: 89.3) and EfficientNetV2 (accuracy: 88.5, sensitivity: 88.1).
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.24016v2`
- Title: FitControler: Toward Fit-Aware Virtual Try-On
- Publication date: 2025-12-30T06:31:19Z
- Source: https://arxiv.org/abs/2512.24016v2
- Candidate selection metadata: same broad category `cs.CV`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Realistic virtual try-on (VTON) concerns not only faithful rendering of garment details but also coordination of the style. Prior art typically pursues the former, but neglects a key factor that shapes the holistic style -- garment fit. Garment fit delineates how a garment aligns with the body of a wearer and is a fundamental element in fashion design. In this work, we introduce fit-aware VTON and present FitControler, a learnable plug-in that can seamlessly integrate into modern VTON models to enable customized fit control. To achieve this, we highlight two challenges: i) how to delineate layouts of different fits and ii) how to render the garment that matches the layout. FitControler first features a fit-aware layout generator to redraw the body-garment layout conditioned on a set of delicately processed garment-agnostic representations, and a multi-scale fit injector is then used to deliver layout cues to enable layout-driven VTON. In particular, we build a fit-aware VTON dataset termed Fit4Men, including 13,000 body-garment pairs of different fits, covering both tops and bottoms, and featuring varying camera distances and body poses. Two fit consistency metrics are also introduced to assess the fitness of generations. Extensive experiments show that FitControler can work with various VTON models and achieve accurate fit control. Code and data will be released.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 18. ARM: A Learnable, Plug-and-Play Module for CLIP-based Open-vocabulary Semantic Segmentation

- Paper ID: `2512.24224v1`
- Publication date: 2025-12-30T13:38:30Z
- Source: https://arxiv.org/abs/2512.24224v1
- Category metadata: `cs.CV`
- Abstract SHA-256: `b818907b4b9ca0fd7c63649068132ff3212f6fd4257d6a729944cdc84a737b77`

**Source abstract (verbatim):**

```text
Open-vocabulary semantic segmentation (OVSS) is fundamentally hampered by the coarse, image-level representations of CLIP, which lack precise pixel-level details. Existing training-free methods attempt to resolve this by either importing priors from costly external foundation models (e.g., SAM, DINO) or by applying static, hand-crafted heuristics to CLIP's internal features. These approaches are either computationally expensive or sub-optimal. We propose the Attention Refinement Module (ARM), a lightweight, learnable module that effectively unlocks and refines CLIP's internal potential. Unlike static-fusion methods, ARM learns to adaptively fuse hierarchical features. It employs a semantically-guided cross-attention block, using robust deep features (K, V) to select and refine detail-rich shallow features (Q), followed by a self-attention block. The key innovation lies in a ``train once, use anywhere" paradigm. Trained once on a general-purpose dataset (e.g., COCO-Stuff), ARM acts as a universal plug-and-play post-processor for diverse training-free frameworks. Extensive experiments show that ARM consistently boosts baseline performance on multiple benchmarks with negligible inference overhead, establishing an efficient and effective paradigm for training-free OVSS.
```

**Extracted claims (4; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
ARM is a lightweight, learnable module that effectively unlocks and refines CLIP's internal potential.
```

Evidence excerpt (verbatim):

```text
We propose the Attention Refinement Module (ARM), a lightweight, learnable module that effectively unlocks and refines CLIP's internal potential.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
ARM learns to adaptively fuse hierarchical features using a semantically-guided cross-attention block.
```

Evidence excerpt (verbatim):

```text
ARM learns to adaptively fuse hierarchical features. It employs a semantically-guided cross-attention block, using robust deep features (K, V) to select and refine detail-rich shallow features (Q)
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
ARM is trained once on a general-purpose dataset and acts as a universal plug-and-play post-processor for diverse training-free frameworks.
```

Evidence excerpt (verbatim):

```text
The key innovation lies in a ``train once, use anywhere" paradigm. Trained once on a general-purpose dataset (e.g., COCO-Stuff), ARM acts as a universal plug-and-play post-processor for diverse training-free frameworks.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
Extensive experiments show that ARM consistently boosts baseline performance on multiple benchmarks with negligible inference overhead.
```

Evidence excerpt (verbatim):

```text
Extensive experiments show that ARM consistently boosts baseline performance on multiple benchmarks with negligible inference overhead, establishing an efficient and effective paradigm for training-free OVSS.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.24016v2`
- Title: FitControler: Toward Fit-Aware Virtual Try-On
- Publication date: 2025-12-30T06:31:19Z
- Source: https://arxiv.org/abs/2512.24016v2
- Candidate selection metadata: same broad category `cs.CV`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Realistic virtual try-on (VTON) concerns not only faithful rendering of garment details but also coordination of the style. Prior art typically pursues the former, but neglects a key factor that shapes the holistic style -- garment fit. Garment fit delineates how a garment aligns with the body of a wearer and is a fundamental element in fashion design. In this work, we introduce fit-aware VTON and present FitControler, a learnable plug-in that can seamlessly integrate into modern VTON models to enable customized fit control. To achieve this, we highlight two challenges: i) how to delineate layouts of different fits and ii) how to render the garment that matches the layout. FitControler first features a fit-aware layout generator to redraw the body-garment layout conditioned on a set of delicately processed garment-agnostic representations, and a multi-scale fit injector is then used to deliver layout cues to enable layout-driven VTON. In particular, we build a fit-aware VTON dataset termed Fit4Men, including 13,000 body-garment pairs of different fits, covering both tops and bottoms, and featuring varying camera distances and body poses. Two fit consistency metrics are also introduced to assess the fitness of generations. Extensive experiments show that FitControler can work with various VTON models and achieve accurate fit control. Code and data will be released.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 19. A Decade of Learning-Based Control: From Theoretic Foundations to Practical Deployment

- Paper ID: `2610.29187v1`
- Publication date: 2026-10-21T04:18:47Z
- Source: https://arxiv.org/abs/2610.29187v1
- Category metadata: `cs.LG`
- Abstract SHA-256: `8edf923316ec2687ec57e17cd008ee972d8e21c2465c3c2ae31c5a47dd9e9b12`

**Source abstract (verbatim):**

```text
Motivated by ten years of Learning-Based Control Invited Sessions at the IEEE Conference on Decision and Control (CDC), this tutorial paper reviews key advances at the intersection of machine learning and control. We focus on methods that combine the flexibility of machine learning techniques with the structure and theoretical foundations of control to design autonomous systems that are capable, reliable, and safe. We first introduce core notions for establishing stability and safety guarantees, then review approaches that learn dynamics models to improve control under uncertainty, and finally discuss data-driven methods that directly synthesize or learn policies, including reinforcement learning, imitation learning, and Bayesian optimization. We further discuss representative applications and open challenges. The goal is to provide an accessible entry point to the field and to support continued progress toward reliable learning-based control in real-world systems. To support learning and practical exploration, we share implementations and illustrative examples along with our discussion, together with additional resources on our website: https://learning-based-control.github.io/tutorial/.
```

**Extracted claims (4; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
This tutorial paper reviews key advances at the intersection of machine learning and control.
```

Evidence excerpt (verbatim):

```text
this tutorial paper reviews key advances at the intersection of machine learning and control.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
The paper focuses on methods that combine the flexibility of machine learning techniques with the structure and theoretical foundations of control.
```

Evidence excerpt (verbatim):

```text
We focus on methods that combine the flexibility of machine learning techniques with the structure and theoretical foundations of control to design autonomous systems that are capable, reliable, and safe.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
The paper introduces core notions for establishing stability and safety guarantees.
```

Evidence excerpt (verbatim):

```text
We first introduce core notions for establishing stability and safety guarantees
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
The paper reviews approaches that learn dynamics models to improve control under uncertainty.
```

Evidence excerpt (verbatim):

```text
then review approaches that learn dynamics models to improve control under uncertainty
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.24827v3`
- Title: Inter-Agent Relative Representations for Multi-Agent Option Discovery
- Publication date: 2025-12-31T12:39:22Z
- Source: https://arxiv.org/abs/2512.24827v3
- Candidate selection metadata: same broad category `cs.LG`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Temporally extended actions improve the ability to explore and plan in single-agent settings. In multi-agent settings, the exponential growth of the joint state space with the number of agents makes coordinated behaviours even more valuable. Yet, this same exponential growth renders the design of multi-agent options particularly challenging. Existing multi-agent option discovery methods often sacrifice coordination by producing loosely coupled or fully independent behaviours. Toward addressing these limitations, we describe a novel approach for multi-agent option discovery. Specifically, we propose a joint-state abstraction that compresses the state space while preserving the information necessary to discover strongly coordinated behaviours. Our approach builds on the inductive bias that synchronisation over agent states provides a natural foundation for coordination in the absence of explicit objectives. We first approximate a fictitious state of maximal alignment with the team, the \textit{Fermat} state, and use it to define a measure of \textit{spreadness}, capturing team-level misalignment on each individual state dimension. Building on this representation, we then employ a neural graph Laplacian estimator to derive options that capture state synchronisation patterns between agents. We evaluate the resulting options across multiple scenarios in two simulated multi-agent domains, showing that they yield stronger downstream coordination capabilities compared to alternative option discovery methods.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 20. RangeNav: Task-Aligned LiDAR Range-Image Pretraining for Robot Navigation

- Paper ID: `2610.29845v1`
- Publication date: 2026-10-21T15:06:08Z
- Source: https://arxiv.org/abs/2610.29845v1
- Category metadata: `cs.LG`
- Abstract SHA-256: `777014bc564c94d0e41ce7a0fb7f063a5ae9c90e5a3ac8b0f3145ab58ccf1c31`

**Source abstract (verbatim):**

```text
Autonomous mobile robots operating in dense crowds and cluttered sites require $360^\circ$ perception to react to surrounding hazards. While panoramic LiDAR offers full-surround coverage, learning representations within reinforcement learning (RL) is sample-inefficient under sparse rewards, and existing 3D pretrained point-cloud encoders are too memory-heavy for massively parallel RL simulation. We present RangeNav, a compact (183k parameters) LiDAR range-image encoder pretrained entirely on synthetic data. RangeNav uses anisotropic convolutions and circular padding to handle the extreme aspect ratio and azimuthal seam of range images. We pretrain the network using a navigation-aligned objective combining range reconstruction, semantic segmentation, and bird's-eye-view (BEV) prediction, then freeze it for policy learning. In simulation, adding semantic and BEV supervision increases success rates over a reconstruction-only baseline by an average of 32.03 and 23.73 percentage points (pp) in procedurally generated training and out-of-distribution realistic test environments, respectively. Zero-shot real-world deployments on a Unitree B2-W quadruped demonstrate robust navigation through dense crowds, low-light settings, and construction zones where limited-field-of-view depth policies struggle. Code and models will be open-sourced.
```

**Extracted claims (4; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
RangeNav is a compact LiDAR range-image encoder pretrained entirely on synthetic data.
```

Evidence excerpt (verbatim):

```text
We present RangeNav, a compact (183k parameters) LiDAR range-image encoder pretrained entirely on synthetic data.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
RangeNav uses anisotropic convolutions and circular padding to handle the extreme aspect ratio and azimuthal seam of range images.
```

Evidence excerpt (verbatim):

```text
RangeNav uses anisotropic convolutions and circular padding to handle the extreme aspect ratio and azimuthal seam of range images.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
RangeNav is pretrained using a navigation-aligned objective combining range reconstruction, semantic segmentation, and bird's-eye-view (BEV) prediction.
```

Evidence excerpt (verbatim):

```text
We pretrain the network using a navigation-aligned objective combining range reconstruction, semantic segmentation, and bird's-eye-view (BEV) prediction
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
Adding semantic and BEV supervision increases success rates over a reconstruction-only baseline by an average of 32.03 and 23.73 percentage points in procedurally generated training and out-of-distribution realistic test environments, respectively.
```

Evidence excerpt (verbatim):

```text
In simulation, adding semantic and BEV supervision increases success rates over a reconstruction-only baseline by an average of 32.03 and 23.73 percentage points (pp) in procedurally generated training and out-of-distribution realistic test environments, respectively.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2610.29219v1`
- Title: PerSPL: Personalized Semi-supervised Preference Learning
- Publication date: 2026-10-21T05:21:36Z
- Source: https://arxiv.org/abs/2610.29219v1
- Candidate selection metadata: same broad category `cs.LG`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Personalized reward models require user-specific preference comparisons, but collecting such feedback is costly and provides only limited supervision for each user. At the same time, large pools of responses can be generated without user identities or preference labels, yet existing personalized reward models leave this data unused. Directly learning from these responses is difficult because pairwise objectives constrain relative scores within a prompt, whereas pseudo-labeling individual responses requires scores that are comparable across prompts for the same user. We propose \textbf{PerSPL} (Personalized Semi-supervised Preference Learning), a backbone-agnostic framework that uses pair-mean score centering to stabilize this cross-prompt score coordinate and iteratively turns unlabeled responses into user-specific training signals. Against seven representative baselines across four benchmarks---PersonalLLM, HelpSteer2, Reddit TLDR, and Chatbot Arena---PerSPL achieves the highest reported mean accuracy among the evaluated methods for both seen and unseen users. The two latter benchmarks provide real-user preference comparisons in summarization and open-domain chatbot interaction, respectively. These results indicate that unlabeled responses can provide additional supervision for personalized reward modeling when per-user preference labels are scarce.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 21. A KAN-based Non-linear Factorization for Embedding Layer Compression

- Paper ID: `2610.29424v1`
- Publication date: 2026-10-21T08:49:06Z
- Source: https://arxiv.org/abs/2610.29424v1
- Category metadata: `cs.CL`
- Abstract SHA-256: `683360124f8335c955bd5f1f6cbfed44075d90aa9deaf7a724c1bebdde615170`

**Source abstract (verbatim):**

```text
Among existing embedding compression approaches, low-rank factorization provides a simple and mathematically principled solution by approximating the embedding matrix with a reduced-rank decomposition. However, its practical effectiveness is often limited, as the resulting linear bottleneck constrains representational capacity. To overcome these limitations, we propose an enhanced factorization scheme that increases expressive power by introducing learnable non-linear projections within the compressed embedding layer. Our method is inspired by the Kolmogorov Arnold Networks (KAN) paradigm, which replaces fixed linear transformations with learnable univariate functions. Despite promising results in other domains, applications of KANs in NLP remain scarce and have so far been largely limited to final or task specific layers, rather than core representational components such as embedding layers. We evaluate the proposed approach by integrating the compressed embedding layer into the Skip-gram framework and comparing it against a standard low-rank baseline under matched parameter budgets on the Word Analogy and Semantic Similarity benchmarks. We further introduce an effective initialization strategy from a pre-trained, uncompressed embedding layer. The behavior of the model is analyzed both immediately after initialization and after a brief post-initialization refinement phase, considering training with the standard Skip-gram objective as well as variants augmented with distillation from the original embedding layer. Overall, our results show that augmenting low-rank factorization with learnable non-linear projections effectively mitigates the limitations of linear bottlenecks, yielding more faithful compressed embeddings under fixed dimensionality and suggesting a promising direction for embedding layer compression beyond purely linear methods.
```

**Extracted claims (6; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
The proposed method introduces learnable non-linear projections within the compressed embedding layer to increase expressive power.
```

Evidence excerpt (verbatim):

```text
To overcome these limitations, we propose an enhanced factorization scheme that increases expressive power by introducing learnable non-linear projections within the compressed embedding layer.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
The method is inspired by the Kolmogorov Arnold Networks (KAN) paradigm, which replaces fixed linear transformations with learnable univariate functions.
```

Evidence excerpt (verbatim):

```text
Our method is inspired by the Kolmogorov Arnold Networks (KAN) paradigm, which replaces fixed linear transformations with learnable univariate functions.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
The proposed approach integrates the compressed embedding layer into the Skip-gram framework and compares it against a standard low-rank baseline under matched parameter budgets.
```

Evidence excerpt (verbatim):

```text
We evaluate the proposed approach by integrating the compressed embedding layer into the Skip-gram framework and comparing it against a standard low-rank baseline under matched parameter budgets on the Word Analogy and Semantic Similarity benchmarks.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
An effective initialization strategy is introduced from a pre-trained, uncompressed embedding layer.
```

Evidence excerpt (verbatim):

```text
We further introduce an effective initialization strategy from a pre-trained, uncompressed embedding layer.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
The behavior of the model is analyzed both immediately after initialization and after a brief post-initialization refinement phase.
```

Evidence excerpt (verbatim):

```text
The behavior of the model is analyzed both immediately after initialization and after a brief post-initialization refinement phase, considering training with the standard Skip-gram objective as well as variants augmented with distillation from the original embedding layer.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 6

Claim (verbatim):

```text
The results show that augmenting low-rank factorization with learnable non-linear projections effectively mitigates the limitations of linear bottlenecks.
```

Evidence excerpt (verbatim):

```text
Overall, our results show that augmenting low-rank factorization with learnable non-linear projections effectively mitigates the limitations of linear bottlenecks, yielding more faithful compressed embeddings under fixed dimensionality and suggesting a promising direction for embedding layer compression beyond purely linear methods.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.23647v1`
- Title: Nested Browser-Use Learning for Agentic Information Seeking
- Publication date: 2025-12-29T17:59:14Z
- Source: https://arxiv.org/abs/2512.23647v1
- Candidate selection metadata: same broad category `cs.CL`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Information-seeking (IS) agents have achieved strong performance across a range of wide and deep search tasks, yet their tool use remains largely restricted to API-level snippet retrieval and URL-based page fetching, limiting access to the richer information available through real browsing. While full browser interaction could unlock deeper capabilities, its fine-grained control and verbose page content returns introduce substantial complexity for ReAct-style function-calling agents. To bridge this gap, we propose Nested Browser-Use Learning (NestBrowse), which introduces a minimal and complete browser-action framework that decouples interaction control from page exploration through a nested structure. This design simplifies agentic reasoning while enabling effective deep-web information acquisition. Empirical results on challenging deep IS benchmarks demonstrate that NestBrowse offers clear benefits in practice. Further in-depth analyses underscore its efficiency and flexibility.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 22. Automated Analysis of Sustainability Reports: Using Large Language Models for the Extraction and Prediction of EU Taxonomy-Compliant KPIs

- Paper ID: `2512.24289v1`
- Publication date: 2025-12-30T15:28:03Z
- Source: https://arxiv.org/abs/2512.24289v1
- Category metadata: `cs.CL`
- Abstract SHA-256: `fae127044f11de07824a80b958ca24ae3be880f69923838c0b544743d03592c5`

**Source abstract (verbatim):**

```text
The manual, resource-intensive process of complying with the EU Taxonomy presents a significant challenge for companies. While Large Language Models (LLMs) offer a path to automation, research is hindered by a lack of public benchmark datasets. To address this gap, we introduce a novel, structured dataset from 190 corporate reports, containing ground-truth economic activities and quantitative Key Performance Indicators (KPIs). We use this dataset to conduct the first systematic evaluation of LLMs on the core compliance workflow. Our results reveal a clear performance gap between qualitative and quantitative tasks. LLMs show moderate success in the qualitative task of identifying economic activities, with a multi-step agentic framework modestly enhancing precision. Conversely, the models comprehensively fail at the quantitative task of predicting financial KPIs in a zero-shot setting. We also discover a paradox, where concise metadata often yields superior performance to full, unstructured reports, and find that model confidence scores are poorly calibrated. We conclude that while LLMs are not ready for full automation, they can serve as powerful assistive tools for human experts. Our dataset provides a public benchmark for future research.
```

**Extracted claims (7; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
A structured dataset containing ground-truth economic activities and quantitative Key Performance Indicators (KPIs) is introduced from 190 corporate reports.
```

Evidence excerpt (verbatim):

```text
To address this gap, we introduce a novel, structured dataset from 190 corporate reports, containing ground-truth economic activities and quantitative Key Performance Indicators (KPIs).
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
The first systematic evaluation of LLMs on the core compliance workflow is conducted using the introduced dataset.
```

Evidence excerpt (verbatim):

```text
We use this dataset to conduct the first systematic evaluation of LLMs on the core compliance workflow.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
LLMs show moderate success in the qualitative task of identifying economic activities, with a multi-step agentic framework modestly enhancing precision.
```

Evidence excerpt (verbatim):

```text
LLMs show moderate success in the qualitative task of identifying economic activities, with a multi-step agentic framework modestly enhancing precision.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
LLMs comprehensively fail at the quantitative task of predicting financial KPIs in a zero-shot setting.
```

Evidence excerpt (verbatim):

```text
Conversely, the models comprehensively fail at the quantitative task of predicting financial KPIs in a zero-shot setting.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
A paradox is discovered where concise metadata often yields superior performance to full, unstructured reports.
```

Evidence excerpt (verbatim):

```text
We also discover a paradox, where concise metadata often yields superior performance to full, unstructured reports,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 6

Claim (verbatim):

```text
Model confidence scores are found to be poorly calibrated.
```

Evidence excerpt (verbatim):

```text
and find that model confidence scores are poorly calibrated.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 7

Claim (verbatim):

```text
LLMs are concluded to be not ready for full automation but can serve as powerful assistive tools for human experts.
```

Evidence excerpt (verbatim):

```text
We conclude that while LLMs are not ready for full automation, they can serve as powerful assistive tools for human experts.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.23049v1`
- Title: Accelerating Language Model Workflows with Prompt Choreography
- Publication date: 2025-12-28T19:21:11Z
- Source: https://arxiv.org/abs/2512.23049v1
- Candidate selection metadata: same broad category `cs.CL`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Large language models are increasingly deployed in multi-agent workflows. We introduce Prompt Choreography, a framework that efficiently executes LLM workflows by maintaining a dynamic, global KV cache. Each LLM call can attend to an arbitrary, reordered subset of previously encoded messages. Parallel calls are supported. Though caching messages' encodings sometimes gives different results from re-encoding them in a new context, we show in diverse settings that fine-tuning the LLM to work with the cache can help it mimic the original results. Prompt Choreography significantly reduces per-message latency (2.0--6.2$\times$ faster time-to-first-token) and achieves substantial end-to-end speedups ($>$2.2$\times$) in some workflows dominated by redundant computation.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 23. Leveraging Time-Series Foundation Models for Financial Crime Detection

- Paper ID: `2610.29667v1`
- Publication date: 2026-10-21T12:42:17Z
- Source: https://arxiv.org/abs/2610.29667v1
- Category metadata: `cs.LG`
- Abstract SHA-256: `99002eca38a8f535eaa5a9c91837a9fb3a722b133b8ff1a5eb2dd34eee8ef657`

**Source abstract (verbatim):**

```text
Financial crime detection requires identifying illicit activity within large transaction networks, where suspicious behaviour is rare and unfolds over time. Existing graph-based methods capture relationships among accounts but typically underuse the temporal behaviour encoded in account transaction histories. We introduce Temporal-Context Edge Enrichment (TCEE), a framework that addresses this gap by summarising each account's transaction history with a frozen time-series foundation model (TSFM), and enriching each transaction's representation with the relevant temporal context from these summaries. These enriched representations can be scored directly for edge classification, or fed into a graph neural network (GNN) as edge features to capture broader structural information. Across six AMLWorld datasets, TCEE improves PR-AUC over the strongest evaluated baseline on five by a relative 10.8% on average, while training 6.0x faster end-to-end. Feeding TCEE's representations into a GNN raises PR-AUC a further 4.8% on the four smaller datasets. On an Ethereum phishing dataset, we show that TSFM-generated account representations fed into a GNN are also effective for node classification, improving PR-AUC by 14.5% over the strongest baseline. As TSFMs continue to advance, our results suggest they can strengthen financial crime detection by capturing temporal signals that complement graph-based approaches.
```

**Extracted claims (5; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
Temporal-Context Edge Enrichment (TCEE) addresses the gap in existing graph-based methods by summarizing each account's transaction history with a frozen time-series foundation model (TSFM).
```

Evidence excerpt (verbatim):

```text
Existing graph-based methods capture relationships among accounts but typically underuse the temporal behaviour encoded in account transaction histories.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
TCEE enriches each transaction's representation with relevant temporal context from TSFM summaries to improve edge classification or provide edge features for graph neural networks (GNNs).
```

Evidence excerpt (verbatim):

```text
These enriched representations can be scored directly for edge classification, or fed into a graph neural network (GNN) as edge features to capture broader structural information.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
TCEE improves PR-AUC over the strongest evaluated baseline on five out of six AMLWorld datasets by an average of 10.8% while training 6.0x faster end-to-end.
```

Evidence excerpt (verbatim):

```text
Across six AMLWorld datasets, TCEE improves PR-AUC over the strongest evaluated baseline on five by a relative 10.8% on average, while training 6.0x faster end-to-end.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
Feeding TCEE's enriched representations into a GNN further increases PR-AUC by 4.8% on four smaller datasets.
```

Evidence excerpt (verbatim):

```text
Feeding TCEE's representations into a GNN raises PR-AUC a further 4.8% on the four smaller datasets.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
TSFM-generated account representations fed into a GNN are effective for node classification on an Ethereum phishing dataset, improving PR-AUC by 14.5% over the strongest baseline.
```

Evidence excerpt (verbatim):

```text
On an Ethereum phishing dataset, we show that TSFM-generated account representations fed into a GNN are also effective for node classification, improving PR-AUC by 14.5% over the strongest baseline.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.24780v2`
- Title: Gradient Descent as Implicit EM in Distance-Based Neural Models
- Publication date: 2025-12-31T10:56:43Z
- Source: https://arxiv.org/abs/2512.24780v2
- Candidate selection metadata: same broad category `cs.LG`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Neural networks trained with standard objectives exhibit behaviors characteristic of probabilistic inference: soft clustering, prototype specialization, and Bayesian uncertainty tracking. These phenomena appear across architectures -- in attention mechanisms, classification heads, and energy-based models -- yet existing explanations often rely on loose analogies to mixture models or post-hoc architectural interpretation. We provide a direct explanation. For any objective with log-sum-exp structure over distances or energies, the gradient with respect to each distance is exactly the negative posterior responsibility of the corresponding component: $\partial L / \partial d_j = -r_j$. The identity is algebraic, requiring only differentiability; it is a specialization of Fisher's identity, and its significance here is its address: standard neural objectives instantiate it without modification. The consequence is that gradient descent on such objectives performs generalized expectation-maximization implicitly, with responsibilities arising as gradients to be applied rather than auxiliary variables to be computed. This result unifies three regimes of learning: unsupervised mixture modeling, where responsibilities are fully latent; attention, where responsibilities are conditioned on queries; and cross-entropy classification, where supervision clamps responsibilities to targets. Our claims live at training time: the responsibility-weighted gradient dynamics recently documented in transformers follow from the objective's geometry. The in-context Bayesian computation that trained transformers perform at inference time is the endpoint of these dynamics, not their per-step content.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 24. Probing the Limits of Compressive Memory: A Study of Infini-Attention in Small-Scale Pretraining

- Paper ID: `2512.23862v1`
- Publication date: 2025-12-29T21:02:14Z
- Source: https://arxiv.org/abs/2512.23862v1
- Category metadata: `cs.CL`
- Abstract SHA-256: `61b5ab68143890ded51d16aebf862ec6c7d26fa62dab1eb45ed360ea60fc084e`

**Source abstract (verbatim):**

```text
This study investigates small-scale pretraining for Small Language Models (SLMs) to enable efficient use of limited data and compute, improve accessibility in low-resource settings and reduce costs. To enhance long-context extrapolation in compact models, we focus on Infini-attention, which builds a compressed memory from past segments while preserving local attention. In our work, we conduct an empirical study using 300M-parameter LLaMA models pretrained with Infini-attention. The model demonstrates training stability and outperforms the baseline in long-context retrieval. We identify the balance factor as a key part of the model performance, and we found that retrieval accuracy drops with repeated memory compressions over long sequences. Even so, Infini-attention still effectively compensates for the SLM's limited parameters. Particularly, despite performance degradation at a 16,384-token context, the Infini-attention model achieves up to 31% higher accuracy than the baseline. Our findings suggest that achieving robust long-context capability in SLMs benefits from architectural memory like Infini-attention.
```

**Extracted claims (6; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
Infini-attention enables compact models to maintain training stability and outperform baselines in long-context retrieval.
```

Evidence excerpt (verbatim):

```text
The model demonstrates training stability and outperforms the baseline in long-context retrieval.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
The balance factor is identified as a critical component influencing model performance.
```

Evidence excerpt (verbatim):

```text
We identify the balance factor as a key part of the model performance,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
Repeated memory compressions over long sequences lead to a decline in retrieval accuracy.
```

Evidence excerpt (verbatim):

```text
we found that retrieval accuracy drops with repeated memory compressions over long sequences.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
Infini-attention compensates for the limited parameters of Small Language Models (SLMs) in long-context tasks.
```

Evidence excerpt (verbatim):

```text
Infini-attention still effectively compensates for the SLM's limited parameters.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
Infini-attention achieves up to 31% higher accuracy than the baseline in long-context retrieval tasks.
```

Evidence excerpt (verbatim):

```text
the Infini-attention model achieves up to 31% higher accuracy than the baseline.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 6

Claim (verbatim):

```text
Infini-attention contributes to achieving robust long-context capability in Small Language Models (SLMs).
```

Evidence excerpt (verbatim):

```text
Our findings suggest that achieving robust long-context capability in SLMs benefits from architectural memory like Infini-attention.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2601.11573v1`
- Title: An Empirical Analysis of Fine-Tuning Large Language Models on Bioinformatics Literature: PRSGPT and BioStarsGPT
- Publication date: 2025-12-29T19:09:12Z
- Source: https://arxiv.org/abs/2601.11573v1
- Candidate selection metadata: same broad category `cs.CL`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Large language models (LLMs) often lack specialized knowledge for complex bioinformatics applications. We present a reproducible pipeline for fine-tuning LLMs on specialized bioinformatics data, demonstrated through two use cases: PRSGPT, focused on polygenic risk score (PRS) tools, and BioStarsGPT, trained on community forum discussions. The nine-step pipeline integrates diverse data sources, structured preprocessing, prompt-based question-answer (QA) generation (via Google Gemini), natural language inference (NLI) for quality control, semantic deduplication, clustering-based data splitting, and parameter-efficient fine-tuning using LoRA. We fine-tuned three LLMs (LLaMA-3.2-3B, Qwen2.5-7B, Gemma) and benchmarked them on over 14 lexical and semantic metrics. Qwen2.5-7B emerged as the best performer, with BLEU-4 and ROUGE-1 improvements of 82\% and 70\% for PRSGPT and 6\% and 18\% for BioStarsGPT, respectively. The open-source datasets produced include over 28,000 QA pairs for PRSGPT and 154,282 for BioStarsGPT. Human evaluation of PRSGPT yielded 61.9\% accuracy on the PRS tools comparison task, comparable to Google Gemini (61.4\%), but with richer methodological detail and accurate citations. BioStarsGPT demonstrated 59\% conceptual accuracy across 142 curated bioinformatics questions. Our pipeline enables scalable, domain-specific fine-tuning of LLMs. It enables privacy-preserving, locally deployable bioinformatics assistants, explores their practical applications, and addresses the challenges, limitations, and mitigation strategies associated with their development and use.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 25. Sparsity Should Be ALLOTted by Output: Training-Free Allocation of Block-Sparse Attention for Video Diffusion Transformers

- Paper ID: `2610.29441v1`
- Publication date: 2026-10-21T09:01:48Z
- Source: https://arxiv.org/abs/2610.29441v1
- Category metadata: `cs.CV`
- Abstract SHA-256: `4e679ed9c6f783283303d53b940e5121fc09666c136a491ea6cc1b4807a0d075`

**Source abstract (verbatim):**

```text
Full 3D attention is costly in video Diffusion Transformers. Block-sparse attention reduces this cost by computing only selected attention blocks. However, existing methods either overlook the potential to optimize sparsity allocation or rely on heuristic rules or local metrics to guide it. In this work, we observe that sparsifying attention in different layers and at different denoising steps affects final-video fidelity to substantially different degrees. Yet the identities of the most sensitive layer-step pairs remain nearly unchanged across inputs. Building on these findings, we propose Allocating Layer-step Latency by Output Tests (ALLOT), a training-free sparsity allocation method. Treating each layer-step pair as a cell, ALLOT estimates each cell's contribution to final-video error through (i) cell probing and (ii) trajectory calibration, then jointly optimizes cell densities under a measured-latency budget. It preserves existing selection strategies and kernels, replacing only the allocation component. At equal or shorter wall-clock time, ALLOT outperforms every compared allocation strategy with XAttention, with an 11.8 dB PSNR gain on HunyuanVideo. Extensive experiments across four additional published pipelines on Wan2.1, Wan2.2, and HunyuanVideo show that ALLOT outperforms or ties the default in all nine settings.
```

**Extracted claims (6; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
Block-sparse attention reduces computational cost in video Diffusion Transformers by computing only selected attention blocks.
```

Evidence excerpt (verbatim):

```text
Full 3D attention is costly in video Diffusion Transformers. Block-sparse attention reduces this cost by computing only selected attention blocks.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
Existing methods for sparsity allocation in attention either overlook the potential to optimize sparsity allocation or rely on heuristic rules or local metrics.
```

Evidence excerpt (verbatim):

```text
However, existing methods either overlook the potential to optimize sparsity allocation or rely on heuristic rules or local metrics to guide it.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
ALLOT is a training-free sparsity allocation method that estimates each layer-step pair's contribution to final-video error through cell probing and trajectory calibration.
```

Evidence excerpt (verbatim):

```text
Building on these findings, we propose Allocating Layer-step Latency by Output Tests (ALLOT), a training-free sparsity allocation method. Treating each layer-step pair as a cell, ALLOT estimates each cell's contribution to final-video error through (i) cell probing and (ii) trajectory calibration
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
ALLOT jointly optimizes cell densities under a measured-latency budget while preserving existing selection strategies and kernels.
```

Evidence excerpt (verbatim):

```text
then jointly optimizes cell densities under a measured-latency budget. It preserves existing selection strategies and kernels, replacing only the allocation component.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
ALLOT outperforms every compared allocation strategy with XAttention, achieving an 11.8 dB PSNR gain on HunyuanVideo.
```

Evidence excerpt (verbatim):

```text
At equal or shorter wall-clock time, ALLOT outperforms every compared allocation strategy with XAttention, with an 11.8 dB PSNR gain on HunyuanVideo.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 6

Claim (verbatim):

```text
ALLOT outperforms or ties the default in all nine settings across four additional published pipelines on Wan2.1, Wan2.2, and HunyuanVideo.
```

Evidence excerpt (verbatim):

```text
Extensive experiments across four additional published pipelines on Wan2.1, Wan2.2, and HunyuanVideo show that ALLOT outperforms or ties the default in all nine settings.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.24473v1`
- Title: F2IDiff: Real-world Image Super-resolution using Feature to Image Diffusion Foundation Model
- Publication date: 2025-12-30T21:37:35Z
- Source: https://arxiv.org/abs/2512.24473v1
- Candidate selection metadata: same broad category `cs.CV`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
With the advent of Generative AI, Single Image Super-Resolution (SISR) quality has seen substantial improvement, as the strong priors learned by Text-2-Image Diffusion (T2IDiff) Foundation Models (FM) can bridge the gap between High-Resolution (HR) and Low-Resolution (LR) images. However, flagship smartphone cameras have been slow to adopt generative models because strong generation can lead to undesirable hallucinations. For substantially degraded LR images, as seen in academia, strong generation is required and hallucinations are more tolerable because of the wide gap between LR and HR images. In contrast, in consumer photography, the LR image has substantially higher fidelity, requiring only minimal hallucination-free generation. We hypothesize that generation in SISR is controlled by the stringency and richness of the FM's conditioning feature. First, text features are high level features, which often cannot describe subtle textures in an image. Additionally, Smartphone LR images are at least $12MP$, whereas SISR networks built on T2IDiff FM are designed to perform inference on much smaller images ($<1MP$). As a result, SISR inference has to be performed on small patches, which often cannot be accurately described by text feature. To address these shortcomings, we introduce an SISR network built on a FM with lower-level feature conditioning, specifically DINOv2 features, which we call a Feature-to-Image Diffusion (F2IDiff) Foundation Model (FM). Lower level features provide stricter conditioning while being rich descriptors of even small patches.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 26. FitControler: Toward Fit-Aware Virtual Try-On

- Paper ID: `2512.24016v2`
- Publication date: 2025-12-30T06:31:19Z
- Source: https://arxiv.org/abs/2512.24016v2
- Category metadata: `cs.CV`
- Abstract SHA-256: `d375d5f2e13e00d1e341b294d11098e783a696dc8d627639a3fb933aac91a720`

**Source abstract (verbatim):**

```text
Realistic virtual try-on (VTON) concerns not only faithful rendering of garment details but also coordination of the style. Prior art typically pursues the former, but neglects a key factor that shapes the holistic style -- garment fit. Garment fit delineates how a garment aligns with the body of a wearer and is a fundamental element in fashion design. In this work, we introduce fit-aware VTON and present FitControler, a learnable plug-in that can seamlessly integrate into modern VTON models to enable customized fit control. To achieve this, we highlight two challenges: i) how to delineate layouts of different fits and ii) how to render the garment that matches the layout. FitControler first features a fit-aware layout generator to redraw the body-garment layout conditioned on a set of delicately processed garment-agnostic representations, and a multi-scale fit injector is then used to deliver layout cues to enable layout-driven VTON. In particular, we build a fit-aware VTON dataset termed Fit4Men, including 13,000 body-garment pairs of different fits, covering both tops and bottoms, and featuring varying camera distances and body poses. Two fit consistency metrics are also introduced to assess the fitness of generations. Extensive experiments show that FitControler can work with various VTON models and achieve accurate fit control. Code and data will be released.
```

**Extracted claims (6; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
FitControler is a learnable plug-in that can seamlessly integrate into modern VTON models to enable customized fit control.
```

Evidence excerpt (verbatim):

```text
we introduce fit-aware VTON and present FitControler, a learnable plug-in that can seamlessly integrate into modern VTON models to enable customized fit control.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
FitControler features a fit-aware layout generator to redraw the body-garment layout conditioned on a set of delicately processed garment-agnostic representations.
```

Evidence excerpt (verbatim):

```text
FitControler first features a fit-aware layout generator to redraw the body-garment layout conditioned on a set of delicately processed garment-agnostic representations,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
FitControler uses a multi-scale fit injector to deliver layout cues to enable layout-driven VTON.
```

Evidence excerpt (verbatim):

```text
and a multi-scale fit injector is then used to deliver layout cues to enable layout-driven VTON.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
A fit-aware VTON dataset termed Fit4Men is built, including 13,000 body-garment pairs of different fits, covering both tops and bottoms, and featuring varying camera distances and body poses.
```

Evidence excerpt (verbatim):

```text
we build a fit-aware VTON dataset termed Fit4Men, including 13,000 body-garment pairs of different fits, covering both tops and bottoms, and featuring varying camera distances and body poses.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
Two fit consistency metrics are introduced to assess the fitness of generations.
```

Evidence excerpt (verbatim):

```text
Two fit consistency metrics are also introduced to assess the fitness of generations.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 6

Claim (verbatim):

```text
Extensive experiments show that FitControler can work with various VTON models and achieve accurate fit control.
```

Evidence excerpt (verbatim):

```text
Extensive experiments show that FitControler can work with various VTON models and achieve accurate fit control.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.23709v3`
- Title: Stream-DiffVSR: Low-Latency Streamable Video Super-Resolution via Auto-Regressive Diffusion
- Publication date: 2025-12-29T18:59:57Z
- Source: https://arxiv.org/abs/2512.23709v3
- Candidate selection metadata: same broad category `cs.CV`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Diffusion-based video super-resolution (VSR) methods deliver strong perceptual quality but are often unsuitable for latency-sensitive scenarios due to reliance on future frames and expensive multi-step denoising. We propose Stream-DiffVSR, a causally conditioned diffusion framework for efficient online VSR. Operating strictly on past frames, Stream-DiffVSR integrates a four-step distilled denoiser for fast inference, an Auto-regressive Temporal Guidance (ARTG) module that injects motion-aligned cues during latent denoising, and a lightweight temporal-aware decoder with a Temporal Processor Module (TPM) to enhance detail and temporal coherence. Unlike chunk-wise streaming inference, our strictly frame-by-frame causal design avoids sequence-level waiting, substantially reducing time-to-first-frame and end-to-end latency. Stream-DiffVSR processes 720p frames in 0.328 seconds on an RTX 4090 and consistently outperforms prior diffusion-based baselines. Compared with the online state-of-the-art TMP, it improves perceptual quality (LPIPS +0.095). Compared with prior diffusion-based VSR methods such as MGLD-VSR, it reduces per-frame runtime by over 130x. Moreover, Stream-DiffVSR substantially lowers time-to-first-frame for diffusion-based VSR, reducing initial delay from over 4600 seconds to 0.328 seconds, making diffusion-based VSR markedly more practical for low-latency online and streaming deployment. Project page: https://jamichss.github.io/stream-diffvsr-project-page/
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 27. Lifting Vision: Ground to Aerial Localization with Reasoning Guided Planning

- Paper ID: `2512.24404v1`
- Publication date: 2025-12-30T18:36:39Z
- Source: https://arxiv.org/abs/2512.24404v1
- Category metadata: `cs.CV`
- Abstract SHA-256: `30b16275ba4a8d43b8936314d038726b609debcc505323f0648e3fb3f894afdc`

**Source abstract (verbatim):**

```text
Multimodal intelligence development recently show strong progress in visual understanding and high level reasoning. Though, most reasoning system still reply on textual information as the main medium for inference. This limit their effectiveness in spatial tasks such as visual navigation and geo-localization. This work discuss about the potential scope of this field and eventually propose an idea visual reasoning paradigm Geo-Consistent Visual Planning, our introduced framework called Visual Reasoning for Localization, or ViReLoc, which performs planning and localization using only visual representations. The proposed framework learns spatial dependencies and geometric relations that text based reasoning often suffer to understand. By encoding step by step inference in the visual domain and optimizing with reinforcement based objectives, ViReLoc plans routes between two given ground images. The system also integrates contrastive learning and adaptive feature interaction to align cross view perspectives and reduce viewpoint differences. Experiments across diverse navigation and localization scenarios show consistent improvements in spatial reasoning accuracy and cross view retrieval performance. These results establish visual reasoning as a strong complementary approach for navigation and localization, and show that such tasks can be performed without real time global positioning system data, leading to more secure navigation solutions.
```

**Extracted claims (6; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
The proposed framework, ViReLoc, performs planning and localization using only visual representations.
```

Evidence excerpt (verbatim):

```text
The proposed framework learns spatial dependencies and geometric relations that text based reasoning often suffer to understand.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
ViReLoc encodes step by step inference in the visual domain and optimizes with reinforcement based objectives.
```

Evidence excerpt (verbatim):

```text
By encoding step by step inference in the visual domain and optimizing with reinforcement based objectives, ViReLoc plans routes between two given ground images.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
ViReLoc integrates contrastive learning and adaptive feature interaction to align cross view perspectives and reduce viewpoint differences.
```

Evidence excerpt (verbatim):

```text
The system also integrates contrastive learning and adaptive feature interaction to align cross view perspectives and reduce viewpoint differences.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
Experiments across diverse navigation and localization scenarios show consistent improvements in spatial reasoning accuracy and cross view retrieval performance.
```

Evidence excerpt (verbatim):

```text
Experiments across diverse navigation and localization scenarios show consistent improvements in spatial reasoning accuracy and cross view retrieval performance.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
The results establish visual reasoning as a strong complementary approach for navigation and localization.
```

Evidence excerpt (verbatim):

```text
These results establish visual reasoning as a strong complementary approach for navigation and localization,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 6

Claim (verbatim):

```text
The proposed approach enables tasks to be performed without real time global positioning system data.
```

Evidence excerpt (verbatim):

```text
and show that such tasks can be performed without real time global positioning system data, leading to more secure navigation solutions.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.24224v1`
- Title: ARM: A Learnable, Plug-and-Play Module for CLIP-based Open-vocabulary Semantic Segmentation
- Publication date: 2025-12-30T13:38:30Z
- Source: https://arxiv.org/abs/2512.24224v1
- Candidate selection metadata: same broad category `cs.CV`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Open-vocabulary semantic segmentation (OVSS) is fundamentally hampered by the coarse, image-level representations of CLIP, which lack precise pixel-level details. Existing training-free methods attempt to resolve this by either importing priors from costly external foundation models (e.g., SAM, DINO) or by applying static, hand-crafted heuristics to CLIP's internal features. These approaches are either computationally expensive or sub-optimal. We propose the Attention Refinement Module (ARM), a lightweight, learnable module that effectively unlocks and refines CLIP's internal potential. Unlike static-fusion methods, ARM learns to adaptively fuse hierarchical features. It employs a semantically-guided cross-attention block, using robust deep features (K, V) to select and refine detail-rich shallow features (Q), followed by a self-attention block. The key innovation lies in a ``train once, use anywhere" paradigm. Trained once on a general-purpose dataset (e.g., COCO-Stuff), ARM acts as a universal plug-and-play post-processor for diverse training-free frameworks. Extensive experiments show that ARM consistently boosts baseline performance on multiple benchmarks with negligible inference overhead, establishing an efficient and effective paradigm for training-free OVSS.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 28. ReSeg: Retraining-free segmentation of abdominal organs via generalizable semantic representation learning

- Paper ID: `2610.29090v1`
- Publication date: 2026-10-21T02:31:19Z
- Source: https://arxiv.org/abs/2610.29090v1
- Category metadata: `cs.CV`
- Abstract SHA-256: `9564aa9b223d5347916a9f1ffdb5f06fa67b74a1fb0efba715eafe746e708422`

**Source abstract (verbatim):**

```text
Abdominal organ segmentation is essential in modern medical applications. While existing deep learning approaches demonstrate promising performance, their heavy reliance on large-scale image data raises concerns over generalization capability and privacy risks. This motivates the development of generalizable segmentation training paradigms based on domain-randomized image synthesis, facilitating generalization across unseen real image domains. However, existing paradigms either suffer from limited segmentation performance when applied to abdominal organs, or require dataset-specific finetuning. To address these limitations, we propose ReSeg, a novel two-stage retraining-free framework for domain-agnostic zero-shot abdominal organ segmentation. At the first stage, our organ-agnostic synthetic data-driven pretraining approach exploits semantically and visually diverse synthetic images generated by a dedicated data engine to optimize a Generalizable Semantic Representation Network (GSRNet). The network is thereby capable of learning semantic features robust against variations in anatomical structure, imaging contrast, resolution and spatial context, which provide universal representation capabilities that serve as a foundation for segmentation learning. Subsequently, in the second stage, we continue to train an Organ-specific Encoder-decoder Segmentation Network (OESNet), whose encoder is initialized with the pretrained weights. This training process is facilitated by another dedicated data engine, which generates diversified visual images while strictly retaining the inherent spatial layout of abdominal organs. Comprehensive evaluation on seven abdominal organ segmentation datasets across three different modalities including CT, MRI, and PET demonstrates that ReSeg consistently outperforms existing state-of-the-art (SOTA) methods while eliminating the need for real training images.
```

**Extracted claims (4; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
ReSeg is a novel two-stage retraining-free framework for domain-agnostic zero-shot abdominal organ segmentation.
```

Evidence excerpt (verbatim):

```text
we propose ReSeg, a novel two-stage retraining-free framework for domain-agnostic zero-shot abdominal organ segmentation.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
The first stage of ReSeg uses a synthetic data-driven pretraining approach to optimize a Generalizable Semantic Representation Network (GSRNet).
```

Evidence excerpt (verbatim):

```text
At the first stage, our organ-agnostic synthetic data-driven pretraining approach exploits semantically and visually diverse synthetic images generated by a dedicated data engine to optimize a Generalizable Semantic Representation Network (GSRNet).
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
The GSRNet learns semantic features robust against variations in anatomical structure, imaging contrast, resolution and spatial context.
```

Evidence excerpt (verbatim):

```text
The network is thereby capable of learning semantic features robust against variations in anatomical structure, imaging contrast, resolution and spatial context, which provide universal representation capabilities that serve as a foundation for segmentation learning.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
ReSeg consistently outperforms existing state-of-the-art (SOTA) methods across three different modalities including CT, MRI, and PET.
```

Evidence excerpt (verbatim):

```text
Comprehensive evaluation on seven abdominal organ segmentation datasets across three different modalities including CT, MRI, and PET demonstrates that ReSeg consistently outperforms existing state-of-the-art (SOTA) methods while eliminating the need for real training images.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.23709v3`
- Title: Stream-DiffVSR: Low-Latency Streamable Video Super-Resolution via Auto-Regressive Diffusion
- Publication date: 2025-12-29T18:59:57Z
- Source: https://arxiv.org/abs/2512.23709v3
- Candidate selection metadata: same broad category `cs.CV`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Diffusion-based video super-resolution (VSR) methods deliver strong perceptual quality but are often unsuitable for latency-sensitive scenarios due to reliance on future frames and expensive multi-step denoising. We propose Stream-DiffVSR, a causally conditioned diffusion framework for efficient online VSR. Operating strictly on past frames, Stream-DiffVSR integrates a four-step distilled denoiser for fast inference, an Auto-regressive Temporal Guidance (ARTG) module that injects motion-aligned cues during latent denoising, and a lightweight temporal-aware decoder with a Temporal Processor Module (TPM) to enhance detail and temporal coherence. Unlike chunk-wise streaming inference, our strictly frame-by-frame causal design avoids sequence-level waiting, substantially reducing time-to-first-frame and end-to-end latency. Stream-DiffVSR processes 720p frames in 0.328 seconds on an RTX 4090 and consistently outperforms prior diffusion-based baselines. Compared with the online state-of-the-art TMP, it improves perceptual quality (LPIPS +0.095). Compared with prior diffusion-based VSR methods such as MGLD-VSR, it reduces per-frame runtime by over 130x. Moreover, Stream-DiffVSR substantially lowers time-to-first-frame for diffusion-based VSR, reducing initial delay from over 4600 seconds to 0.328 seconds, making diffusion-based VSR markedly more practical for low-latency online and streaming deployment. Project page: https://jamichss.github.io/stream-diffvsr-project-page/
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 29. Vibe Coding, Interface Flattening

- Paper ID: `2512.24939v1`
- Publication date: 2025-12-31T16:00:59Z
- Source: https://arxiv.org/abs/2512.24939v1
- Category metadata: `cs.CL`
- Abstract SHA-256: `6a5a67301f88fec18b29e1fdbe4e26a13f7604a3b237f8fd6c12bd529fb78aca`

**Source abstract (verbatim):**

```text
Large language models are reshaping programming by enabling 'vibe coding': the development of softwares through natural-language interaction with model-driven toolchains. This article argues that vibe coding is best understood as interface flattening, a reconfiguration in which previously distinct modalities (GUI, CLI, and API) appear to converge into a single conversational surface, even as the underlying chain of translation from intention to machinic effect lengthens and thickens. Drawing on Friedrich Kittler's materialist media theory and Alexander Galloway's account of interfaces as sites of protocol control, the paper situates programming as a historically localised interface arrangement rather than an essential relation to computation. Through a materialist reconstruction of the contemporary vibe-coding stack, it shows how remote compute infrastructures, latency and connectivity, structured outputs, function/tool calling, and interoperability standards such as the Model Context Protocol relocate control and meaning-making power to model and protocol providers. The apparent democratisation of technical capability therefore depends on new dependencies and new literacies. By foregrounding the tension between experiential flattening and infrastructural thickening, I demonstrate how LLM-mediated development redistributes symbolic labour/power, obscures responsibility, and privatises competencies previously dispersed across programming communities, contributing a critical lens on the political economy of AI-mediated human-computer interaction.
```

**Extracted claims (4; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
Vibe coding is best understood as interface flattening, a reconfiguration in which previously distinct modalities appear to converge into a single conversational surface.
```

Evidence excerpt (verbatim):

```text
This article argues that vibe coding is best understood as interface flattening, a reconfiguration in which previously distinct modalities (GUI, CLI, and API) appear to converge into a single conversational surface
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
Programming is situated as a historically localised interface arrangement rather than an essential relation to computation.
```

Evidence excerpt (verbatim):

```text
the paper situates programming as a historically localised interface arrangement rather than an essential relation to computation
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
Remote compute infrastructures, latency and connectivity, structured outputs, function/tool calling, and interoperability standards such as the Model Context Protocol relocate control and meaning-making power to model and protocol providers.
```

Evidence excerpt (verbatim):

```text
remote compute infrastructures, latency and connectivity, structured outputs, function/tool calling, and interoperability standards such as the Model Context Protocol relocate control and meaning-making power to model and protocol providers
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
The apparent democratisation of technical capability depends on new dependencies and new literacies.
```

Evidence excerpt (verbatim):

```text
The apparent democratisation of technical capability therefore depends on new dependencies and new literacies
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.23647v1`
- Title: Nested Browser-Use Learning for Agentic Information Seeking
- Publication date: 2025-12-29T17:59:14Z
- Source: https://arxiv.org/abs/2512.23647v1
- Candidate selection metadata: same broad category `cs.CL`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Information-seeking (IS) agents have achieved strong performance across a range of wide and deep search tasks, yet their tool use remains largely restricted to API-level snippet retrieval and URL-based page fetching, limiting access to the richer information available through real browsing. While full browser interaction could unlock deeper capabilities, its fine-grained control and verbose page content returns introduce substantial complexity for ReAct-style function-calling agents. To bridge this gap, we propose Nested Browser-Use Learning (NestBrowse), which introduces a minimal and complete browser-action framework that decouples interaction control from page exploration through a nested structure. This design simplifies agentic reasoning while enabling effective deep-web information acquisition. Empirical results on challenging deep IS benchmarks demonstrate that NestBrowse offers clear benefits in practice. Further in-depth analyses underscore its efficiency and flexibility.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 30. Benchmarking and Error Analysis of Deep Search and Deep Research LLM Agents

- Paper ID: `2610.29346v1`
- Publication date: 2026-10-21T07:38:29Z
- Source: https://arxiv.org/abs/2610.29346v1
- Category metadata: `cs.LG`
- Abstract SHA-256: `e8bbba261917ffdb03fba30653b2481da4977712c81baac7567b916a39ecbcb4`

**Source abstract (verbatim):**

```text
As Large Language Models (LLMs) evolve into autonomous Deep Search and Deep Research Agents capable of executing long-horizon, multi-step tasks, evaluating their reliability becomes increasingly critical. However, existing evaluation paradigms predominantly focus on final task outcomes, leaving a significant gap in understanding the intermediate execution traces, where agents are highly susceptible to various errors. To address this critical gap, we introduce a comprehensive methodology and analytical framework designed specifically to diagnose errors in intermediate workflows. Building upon this framework, we establish a structured taxonomy that categorizes these vulnerabilities into two primary dimensions: System-Level Errors and Task-Level Errors. Through a systematic examination of step-by-step execution traces and agent-environment interactions, we reveal how these underlying errors affect overall performance. Finally, through empirical experiments and systematic analysis of the identified error types, we provide actionable design guidelines, aiming to enhance the robustness, reasoning capabilities, and reliability of Deep Search and Deep Research agents.
```

**Extracted claims (4; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
A comprehensive methodology and analytical framework are introduced to diagnose errors in intermediate workflows of Deep Search and Deep Research agents.
```

Evidence excerpt (verbatim):

```text
To address this critical gap, we introduce a comprehensive methodology and analytical framework designed specifically to diagnose errors in intermediate workflows.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
A structured taxonomy is established that categorizes vulnerabilities into two primary dimensions: System-Level Errors and Task-Level Errors.
```

Evidence excerpt (verbatim):

```text
Building upon this framework, we establish a structured taxonomy that categorizes these vulnerabilities into two primary dimensions: System-Level Errors and Task-Level Errors.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
Systematic examination of step-by-step execution traces and agent-environment interactions reveals how underlying errors affect overall performance.
```

Evidence excerpt (verbatim):

```text
Through a systematic examination of step-by-step execution traces and agent-environment interactions, we reveal how these underlying errors affect overall performance.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
Empirical experiments and systematic analysis of identified error types provide actionable design guidelines to enhance the robustness, reasoning capabilities, and reliability of Deep Search and Deep Research agents.
```

Evidence excerpt (verbatim):

```text
Finally, through empirical experiments and systematic analysis of the identified error types, we provide actionable design guidelines, aiming to enhance the robustness, reasoning capabilities, and reliability of Deep Search and Deep Research agents.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.24381v2`
- Title: Tubular Riemannian Laplace Approximations for Bayesian Neural Networks
- Publication date: 2025-12-30T17:50:55Z
- Source: https://arxiv.org/abs/2512.24381v2
- Candidate selection metadata: same broad category `cs.LG`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Laplace approximations are among the simplest and most practical methods for approximate Bayesian inference in neural networks, yet their Euclidean formulation struggles with the highly anisotropic, curved loss surfaces and large symmetry groups that characterize modern deep models. Recent work has proposed Riemannian and geometric Gaussian approximations to adapt to this structure. Building on these ideas, we introduce the Tubular Riemannian Laplace (TRL) approximation. TRL explicitly models the posterior as a probabilistic tube that follows a low-loss valley induced by functional symmetries, using a Fisher/Gauss-Newton metric to separate prior-dominated tangential uncertainty from data-dominated transverse uncertainty. We interpret TRL as a scalable reparametrised Gaussian approximation that utilizes implicit curvature estimates to operate in high-dimensional parameter spaces. Our empirical evaluation on ResNet-18 (CIFAR-10 and CIFAR-100) demonstrates that TRL achieves excellent calibration, matching or exceeding the reliability of Deep Ensembles (in terms of ECE) while requiring only a fraction (1/5) of the training cost. TRL effectively bridges the gap between single-model efficiency and ensemble-grade reliability.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 31. Gradient Descent as Implicit EM in Distance-Based Neural Models

- Paper ID: `2512.24780v2`
- Publication date: 2025-12-31T10:56:43Z
- Source: https://arxiv.org/abs/2512.24780v2
- Category metadata: `cs.LG`
- Abstract SHA-256: `917f5441ed5e62252c55e01cfd94b42c8b41913c87e76ae5287c19c3105e61dc`

**Source abstract (verbatim):**

```text
Neural networks trained with standard objectives exhibit behaviors characteristic of probabilistic inference: soft clustering, prototype specialization, and Bayesian uncertainty tracking. These phenomena appear across architectures -- in attention mechanisms, classification heads, and energy-based models -- yet existing explanations often rely on loose analogies to mixture models or post-hoc architectural interpretation. We provide a direct explanation. For any objective with log-sum-exp structure over distances or energies, the gradient with respect to each distance is exactly the negative posterior responsibility of the corresponding component: $\partial L / \partial d_j = -r_j$. The identity is algebraic, requiring only differentiability; it is a specialization of Fisher's identity, and its significance here is its address: standard neural objectives instantiate it without modification. The consequence is that gradient descent on such objectives performs generalized expectation-maximization implicitly, with responsibilities arising as gradients to be applied rather than auxiliary variables to be computed. This result unifies three regimes of learning: unsupervised mixture modeling, where responsibilities are fully latent; attention, where responsibilities are conditioned on queries; and cross-entropy classification, where supervision clamps responsibilities to targets. Our claims live at training time: the responsibility-weighted gradient dynamics recently documented in transformers follow from the objective's geometry. The in-context Bayesian computation that trained transformers perform at inference time is the endpoint of these dynamics, not their per-step content.
```

**Extracted claims (5; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
Gradient descent on objectives with log-sum-exp structure over distances or energies yields the negative posterior responsibility of the corresponding component.
```

Evidence excerpt (verbatim):

```text
For any objective with log-sum-exp structure over distances or energies, the gradient with respect to each distance is exactly the negative posterior responsibility of the corresponding component: $\partial L / \partial d_j = -r_j$.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
The identity between gradient and posterior responsibility is algebraic and requires only differentiability.
```

Evidence excerpt (verbatim):

```text
The identity is algebraic, requiring only differentiability; it is a specialization of Fisher's identity, and its significance here is its address: standard neural objectives instantiate it without modification.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
Gradient descent on such objectives performs generalized expectation-maximization implicitly.
```

Evidence excerpt (verbatim):

```text
The consequence is that gradient descent on such objectives performs generalized expectation-maximization implicitly, with responsibilities arising as gradients to be applied rather than auxiliary variables to be computed.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
The result unifies three regimes of learning: unsupervised mixture modeling, attention, and cross-entropy classification.
```

Evidence excerpt (verbatim):

```text
This result unifies three regimes of learning: unsupervised mixture modeling, where responsibilities are fully latent; attention, where responsibilities are conditioned on queries; and cross-entropy classification, where supervision clamps responsibilities to targets.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
The responsibility-weighted gradient dynamics in transformers follow from the objective's geometry.
```

Evidence excerpt (verbatim):

```text
Our claims live at training time: the responsibility-weighted gradient dynamics recently documented in transformers follow from the objective's geometry.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.24381v2`
- Title: Tubular Riemannian Laplace Approximations for Bayesian Neural Networks
- Publication date: 2025-12-30T17:50:55Z
- Source: https://arxiv.org/abs/2512.24381v2
- Candidate selection metadata: same broad category `cs.LG`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Laplace approximations are among the simplest and most practical methods for approximate Bayesian inference in neural networks, yet their Euclidean formulation struggles with the highly anisotropic, curved loss surfaces and large symmetry groups that characterize modern deep models. Recent work has proposed Riemannian and geometric Gaussian approximations to adapt to this structure. Building on these ideas, we introduce the Tubular Riemannian Laplace (TRL) approximation. TRL explicitly models the posterior as a probabilistic tube that follows a low-loss valley induced by functional symmetries, using a Fisher/Gauss-Newton metric to separate prior-dominated tangential uncertainty from data-dominated transverse uncertainty. We interpret TRL as a scalable reparametrised Gaussian approximation that utilizes implicit curvature estimates to operate in high-dimensional parameter spaces. Our empirical evaluation on ResNet-18 (CIFAR-10 and CIFAR-100) demonstrates that TRL achieves excellent calibration, matching or exceeding the reliability of Deep Ensembles (in terms of ECE) while requiring only a fraction (1/5) of the training cost. TRL effectively bridges the gap between single-model efficiency and ensemble-grade reliability.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 32. Colorful Pinball: Density-Weighted Quantile Regression for Conditional Guarantee of Conformal Prediction

- Paper ID: `2512.24139v5`
- Publication date: 2025-12-30T11:02:35Z
- Source: https://arxiv.org/abs/2512.24139v5
- Category metadata: `cs.LG`
- Abstract SHA-256: `434f02c3d2f50a7cb1dfc1da3e4cb3eb7c8161a6a64cf75e1a4ee40c3b2f2948`

**Source abstract (verbatim):**

```text
Although conformal prediction provides robust marginal coverage guarantees, achieving reliable conditional coverage for specific inputs remains challenging. While exact distribution-free conditional coverage is impossible with finite samples, recent work has focused on improving the conditional coverage of standard conformal procedures. Distinct from approaches that target relaxed notions of conditional coverage, we directly target the mean squared error of conditional coverage by refining the quantile regression components that underpin many conformal methods. Leveraging a Taylor expansion, we derive a sharp surrogate objective for quantile regression: a density-weighted pinball loss, where the weights are given by the conditional density of the nonconformity score evaluated at the true quantile. We propose a three-headed quantile network that estimates these weights via finite differences using auxiliary quantile levels at $1-α\pm δ$, subsequently fine-tuning the central quantile by optimizing the weighted loss. We provide a theoretical analysis with exact non-asymptotic guarantees characterizing the resulting excess risk. Extensive experiments on diverse high-dimensional real-world datasets demonstrate remarkable improvements in conditional coverage performance.
```

**Extracted claims (4; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
The paper proposes a density-weighted pinball loss for quantile regression to improve conditional coverage.
```

Evidence excerpt (verbatim):

```text
Leveraging a Taylor expansion, we derive a sharp surrogate objective for quantile regression: a density-weighted pinball loss, where the weights are given by the conditional density of the nonconformity score evaluated at the true quantile.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
A three-headed quantile network is introduced to estimate the weights in the density-weighted pinball loss.
```

Evidence excerpt (verbatim):

```text
We propose a three-headed quantile network that estimates these weights via finite differences using auxiliary quantile levels at $1-α\pm δ$, subsequently fine-tuning the central quantile by optimizing the weighted loss.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
The paper provides theoretical analysis with exact non-asymptotic guarantees for the proposed method.
```

Evidence excerpt (verbatim):

```text
We provide a theoretical analysis with exact non-asymptotic guarantees characterizing the resulting excess risk.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
The method achieves significant improvements in conditional coverage performance on high-dimensional real-world datasets.
```

Evidence excerpt (verbatim):

```text
Extensive experiments on diverse high-dimensional real-world datasets demonstrate remarkable improvements in conditional coverage performance.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2610.29219v1`
- Title: PerSPL: Personalized Semi-supervised Preference Learning
- Publication date: 2026-10-21T05:21:36Z
- Source: https://arxiv.org/abs/2610.29219v1
- Candidate selection metadata: same broad category `cs.LG`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate postdates focal and is temporally ineligible on current evidence
- Source abstract (verbatim):

```text
Personalized reward models require user-specific preference comparisons, but collecting such feedback is costly and provides only limited supervision for each user. At the same time, large pools of responses can be generated without user identities or preference labels, yet existing personalized reward models leave this data unused. Directly learning from these responses is difficult because pairwise objectives constrain relative scores within a prompt, whereas pseudo-labeling individual responses requires scores that are comparable across prompts for the same user. We propose \textbf{PerSPL} (Personalized Semi-supervised Preference Learning), a backbone-agnostic framework that uses pair-mean score centering to stabilize this cross-prompt score coordinate and iteratively turns unlabeled responses into user-specific training signals. Against seven representative baselines across four benchmarks---PersonalLLM, HelpSteer2, Reddit TLDR, and Chatbot Arena---PerSPL achieves the highest reported mean accuracy among the evaluated methods for both seen and unseen users. The two latter benchmarks provide real-user preference comparisons in summarization and open-domain chatbot interaction, respectively. These results indicate that unlabeled responses can provide additional supervision for personalized reward modeling when per-user preference labels are scarce.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 33. Phase Transitions in Learning Driven by Extremal Data

- Paper ID: `2610.29531v1`
- Publication date: 2026-10-21T10:22:18Z
- Source: https://arxiv.org/abs/2610.29531v1
- Category metadata: `cs.LG`
- Abstract SHA-256: `11e5fc2b9a8838324bb86dd11cf3620996295d23172f2f3b36d763194af1fe26`

**Source abstract (verbatim):**

```text
We study an extremal regression problem, an example of multiple instance learning (MIL), where the predictors are given as multisets, called bags. The bag elements (called instances) possess hidden labels which are pooled to produce an observed bag-level label. Max pooling is common in MIL applications, but gives rise to vanishing gradients. To handle this, modern MIL pipelines approximate the max with a softmax, treating the sharpness as a learnable parameter, denoted $λ$. When the max pooling model is the true data generating process, learning will be successful when $λ$ is increased during gradient descent, thereby driving the dynamics into regions of parameter space with vanishing gradients. To understand the conditions under which gradient descent breaks down, we study a minimal model and derive a low dimensional projection of the gradient flow in the joint limit of large bags $n$ and high dimension $d$ with $α=\ln n/d$ fixed. The flow has two distinct phase transitions: an intrinsic freezing transition related to the random energy model of disordered systems, and a retrieval transition occurring in modern Hopfield networks. Numerical simulation confirms both the phase diagram and the convergence of the finite-size training gradient to its predicted asymptotic form.
```

**Extracted claims (6; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
The study investigates an extremal regression problem in multiple instance learning where bag-level labels are derived from hidden instance labels.
```

Evidence excerpt (verbatim):

```text
We study an extremal regression problem, an example of multiple instance learning (MIL), where the predictors are given as multisets, called bags.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
Max pooling is commonly used in MIL applications but leads to vanishing gradients.
```

Evidence excerpt (verbatim):

```text
Max pooling is common in MIL applications, but gives rise to vanishing gradients.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
Modern MIL pipelines approximate max pooling with a softmax, treating sharpness as a learnable parameter denoted $λ$.
```

Evidence excerpt (verbatim):

```text
To handle this, modern MIL pipelines approximate the max with a softmax, treating the sharpness as a learnable parameter, denoted $λ$.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
When the max pooling model is the true data generating process, increasing $λ$ during gradient descent drives the dynamics into regions of parameter space with vanishing gradients.
```

Evidence excerpt (verbatim):

```text
When the max pooling model is the true data generating process, learning will be successful when $λ$ is increased during gradient descent, thereby driving the dynamics into regions of parameter space with vanishing gradients.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
The gradient flow exhibits two distinct phase transitions: an intrinsic freezing transition and a retrieval transition.
```

Evidence excerpt (verbatim):

```text
The flow has two distinct phase transitions: an intrinsic freezing transition related to the random energy model of disordered systems, and a retrieval transition occurring in modern Hopfield networks.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 6

Claim (verbatim):

```text
Numerical simulations confirm the phase diagram and the convergence of the finite-size training gradient to its predicted asymptotic form.
```

Evidence excerpt (verbatim):

```text
Numerical simulation confirms both the phase diagram and the convergence of the finite-size training gradient to its predicted asymptotic form.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2610.29515v1`
- Title: BRIDGE: An Acceptance Gate to Block False Improvements in Model Updates, with a Retrospective Clinical Evaluation
- Publication date: 2026-10-21T10:04:40Z
- Source: https://arxiv.org/abs/2610.29515v1
- Candidate selection metadata: same broad category `cs.LG`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Models are updated repeatedly, and an update that looks better on validation data but not on new data is a false improvement that can misguide clinical decisions. The naive rule accepts every positive validation gain and is optimistic when the same data choose and judge the update. BRIDGE is a model-agnostic acceptance gate that decides each update from predictions and the available labels, with fixed settings. Each fold of the data judges the update chosen on the other folds (cross-fitting) to reduce selection bias; acceptance requires the gain's lower bootstrap bound to exceed a margin. The four settings are (A) 11 new datasets, (B) synthetic tasks, (C) 12 retrospective clinical tasks, and (D) 39 supporting datasets. The false-improvement rate falls from 19.1% (naive) to 1.1% (BRIDGE) in (A), 20.7% to 1.7% (B), 20.0% to 0% (C), and 12.5% to 0.5% (D); every 95% confidence interval of the reduction over datasets or tasks excludes zero (not over the clinical sources). An equal-size random draw from the naive acceptances contains more false improvements in (A)-(E) (post hoc, p<0.001). On the OpenML collection (E) of 14 new datasets, the false-improvement rate falls from 25.6% to 1.0%. BRIDGE removes 97% to 100% of the false improvements that the naive rule accepts, and its mean gain per deployed update is 1.8 to 3.1 times the naive rule's. The 95% upper bound on the false-improvement rate is below 5.5%: formal in (B) for independent tasks (3.56%), and conditional on the real data tested (0.33% to 5.40%).
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 34. Accelerating Language Model Workflows with Prompt Choreography

- Paper ID: `2512.23049v1`
- Publication date: 2025-12-28T19:21:11Z
- Source: https://arxiv.org/abs/2512.23049v1
- Category metadata: `cs.CL`
- Abstract SHA-256: `43396723c4573ff64c034b136ea76e3b2a2b3e2df4018eb9008fffa0a118c23f`

**Source abstract (verbatim):**

```text
Large language models are increasingly deployed in multi-agent workflows. We introduce Prompt Choreography, a framework that efficiently executes LLM workflows by maintaining a dynamic, global KV cache. Each LLM call can attend to an arbitrary, reordered subset of previously encoded messages. Parallel calls are supported. Though caching messages' encodings sometimes gives different results from re-encoding them in a new context, we show in diverse settings that fine-tuning the LLM to work with the cache can help it mimic the original results. Prompt Choreography significantly reduces per-message latency (2.0--6.2$\times$ faster time-to-first-token) and achieves substantial end-to-end speedups ($>$2.2$\times$) in some workflows dominated by redundant computation.
```

**Extracted claims (5; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
Prompt Choreography introduces a framework that efficiently executes LLM workflows by maintaining a dynamic, global KV cache.
```

Evidence excerpt (verbatim):

```text
We introduce Prompt Choreography, a framework that efficiently executes LLM workflows by maintaining a dynamic, global KV cache.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
Each LLM call in Prompt Choreography can attend to an arbitrary, reordered subset of previously encoded messages.
```

Evidence excerpt (verbatim):

```text
Each LLM call can attend to an arbitrary, reordered subset of previously encoded messages.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
Prompt Chore, Choreography supports parallel calls in LLM workflows.
```

Evidence excerpt (verbatim):

```text
Parallel calls are supported.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
Caching messages' encodings sometimes gives different results from re-encoding them in a new context.
```

Evidence excerpt (verbatim):

```text
Though caching messages' encodings sometimes gives different results from re-encoding them in a new context, we show in diverse settings that fine-tuning the LLM to work with the cache can help it mimic the original results.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
Fine-tuning the LLM to work with the cache can help it mimic the original results of re-encoding messages in a new context.
```

Evidence excerpt (verbatim):

```text
Though caching messages' encodings sometimes gives different results from re-encoding them in a new context, we show in diverse settings that fine-tuning the LLM to work with the cache can help it mimic the original results.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2601.11573v1`
- Title: An Empirical Analysis of Fine-Tuning Large Language Models on Bioinformatics Literature: PRSGPT and BioStarsGPT
- Publication date: 2025-12-29T19:09:12Z
- Source: https://arxiv.org/abs/2601.11573v1
- Candidate selection metadata: same broad category `cs.CL`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate postdates focal and is temporally ineligible on current evidence
- Source abstract (verbatim):

```text
Large language models (LLMs) often lack specialized knowledge for complex bioinformatics applications. We present a reproducible pipeline for fine-tuning LLMs on specialized bioinformatics data, demonstrated through two use cases: PRSGPT, focused on polygenic risk score (PRS) tools, and BioStarsGPT, trained on community forum discussions. The nine-step pipeline integrates diverse data sources, structured preprocessing, prompt-based question-answer (QA) generation (via Google Gemini), natural language inference (NLI) for quality control, semantic deduplication, clustering-based data splitting, and parameter-efficient fine-tuning using LoRA. We fine-tuned three LLMs (LLaMA-3.2-3B, Qwen2.5-7B, Gemma) and benchmarked them on over 14 lexical and semantic metrics. Qwen2.5-7B emerged as the best performer, with BLEU-4 and ROUGE-1 improvements of 82\% and 70\% for PRSGPT and 6\% and 18\% for BioStarsGPT, respectively. The open-source datasets produced include over 28,000 QA pairs for PRSGPT and 154,282 for BioStarsGPT. Human evaluation of PRSGPT yielded 61.9\% accuracy on the PRS tools comparison task, comparable to Google Gemini (61.4\%), but with richer methodological detail and accurate citations. BioStarsGPT demonstrated 59\% conceptual accuracy across 142 curated bioinformatics questions. Our pipeline enables scalable, domain-specific fine-tuning of LLMs. It enables privacy-preserving, locally deployable bioinformatics assistants, explores their practical applications, and addresses the challenges, limitations, and mitigation strategies associated with their development and use.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 35. An Empirical Analysis of Fine-Tuning Large Language Models on Bioinformatics Literature: PRSGPT and BioStarsGPT

- Paper ID: `2601.11573v1`
- Publication date: 2025-12-29T19:09:12Z
- Source: https://arxiv.org/abs/2601.11573v1
- Category metadata: `cs.CL`
- Abstract SHA-256: `cd07038759b1f076707b498e1f1b47c870a2cfdc129dfc72904befe519faf497`

**Source abstract (verbatim):**

```text
Large language models (LLMs) often lack specialized knowledge for complex bioinformatics applications. We present a reproducible pipeline for fine-tuning LLMs on specialized bioinformatics data, demonstrated through two use cases: PRSGPT, focused on polygenic risk score (PRS) tools, and BioStarsGPT, trained on community forum discussions. The nine-step pipeline integrates diverse data sources, structured preprocessing, prompt-based question-answer (QA) generation (via Google Gemini), natural language inference (NLI) for quality control, semantic deduplication, clustering-based data splitting, and parameter-efficient fine-tuning using LoRA. We fine-tuned three LLMs (LLaMA-3.2-3B, Qwen2.5-7B, Gemma) and benchmarked them on over 14 lexical and semantic metrics. Qwen2.5-7B emerged as the best performer, with BLEU-4 and ROUGE-1 improvements of 82\% and 70\% for PRSGPT and 6\% and 18\% for BioStarsGPT, respectively. The open-source datasets produced include over 28,000 QA pairs for PRSGPT and 154,282 for BioStarsGPT. Human evaluation of PRSGPT yielded 61.9\% accuracy on the PRS tools comparison task, comparable to Google Gemini (61.4\%), but with richer methodological detail and accurate citations. BioStarsGPT demonstrated 59\% conceptual accuracy across 142 curated bioinformatics questions. Our pipeline enables scalable, domain-specific fine-tuning of LLMs. It enables privacy-preserving, locally deployable bioinformatics assistants, explores their practical applications, and addresses the challenges, limitations, and mitigation strategies associated with their development and use.
```

**Extracted claims (8; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
A reproducible pipeline for fine-tuning large language models on specialized bioinformatics data is presented.
```

Evidence excerpt (verbatim):

```text
We present a reproducible pipeline for fine-tuning LLMs on specialized bioinformatics data, demonstrated through two use cases: PRSGPT, focused on polygenic risk score (PRS) tools, and BioStarsGPT, trained on community forum discussions.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
The pipeline integrates diverse data sources, structured preprocessing, prompt-based question-answer generation, natural language inference for quality control, semantic deduplication, clustering-based data splitting, and parameter-efficient fine-tuning using LoRA.
```

Evidence excerpt (verbatim):

```text
The nine-step pipeline integrates diverse data sources, structured preprocessing, prompt-based question-answer (QA) generation (via Google Gemini), natural language inference (NLI) for quality control, semantic deduplication, clustering-based data splitting, and parameter-efficient fine-tuning using LoRA.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
Three large language models were fine-tuned and benchmarked on over 14 lexical and semantic metrics.
```

Evidence excerpt (verbatim):

```text
We fine-tuned three LLMs (LLaMA-3.2-3B, Qwen2.5-7B, Gemma) and benchmarked them on over 14 lexical and semantic metrics.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
Qwen2.5-7B emerged as the best performer with significant improvements in BLEU-4 and ROUGE-1 scores for both PRSGPT and BioStarsGPT.
```

Evidence excerpt (verbatim):

```text
Qwen2.5-7B emerged as the best performer, with BLEU-4 and ROUGE-1 improvements of 82\% and 70\% for PRSGPT and 6\% and 18\% for BioStarsGPT, respectively.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
Human evaluation of PRSGPT yielded 61.9% accuracy on the PRS tools comparison task, comparable to Google Gemini.
```

Evidence excerpt (verbatim):

```text
Human evaluation of PRSGPT yielded 61.9\% accuracy on the PRS tools comparison task, comparable to Google Gemini (61.4\%), but with richer methodological detail and accurate citations.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 6

Claim (verbatim):

```text
BioStarsGPT demonstrated 59% conceptual accuracy across 142 curated bioinformatics questions.
```

Evidence excerpt (verbatim):

```text
BioStarsGPT demonstrated 59\% conceptual accuracy across 142 curated bioinformatics questions.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 7

Claim (verbatim):

```text
The open-source datasets produced include over 28,000 QA pairs for PRSGPT and 154,282 for BioStarsGPT.
```

Evidence excerpt (verbatim):

```text
The open-source datasets produced include over 28,000 QA pairs for PRSGPT and 154,282 for BioStarsGPT.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 8

Claim (verbatim):

```text
The pipeline enables scalable, domain-specific fine-tuning of LLMs and supports privacy-preserving, locally deployable bioinformatics assistants.
```

Evidence excerpt (verbatim):

```text
Our pipeline enables scalable, domain-specific fine-tuning of LLMs. It enables privacy-preserving, locally deployable bioinformatics assistants, explores their practical applications, and addresses the challenges, limitations, and mitigation strategies associated with their development and use.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.23049v1`
- Title: Accelerating Language Model Workflows with Prompt Choreography
- Publication date: 2025-12-28T19:21:11Z
- Source: https://arxiv.org/abs/2512.23049v1
- Candidate selection metadata: same broad category `cs.CL`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Large language models are increasingly deployed in multi-agent workflows. We introduce Prompt Choreography, a framework that efficiently executes LLM workflows by maintaining a dynamic, global KV cache. Each LLM call can attend to an arbitrary, reordered subset of previously encoded messages. Parallel calls are supported. Though caching messages' encodings sometimes gives different results from re-encoding them in a new context, we show in diverse settings that fine-tuning the LLM to work with the cache can help it mimic the original results. Prompt Choreography significantly reduces per-message latency (2.0--6.2$\times$ faster time-to-first-token) and achieves substantial end-to-end speedups ($>$2.2$\times$) in some workflows dominated by redundant computation.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 36. Capable Teacher, Myopic Scorer: Reward-Free Teacher Repair for Agentic On-Policy Distillation

- Paper ID: `2610.28586v1`
- Publication date: 2026-10-20T17:40:08Z
- Source: https://arxiv.org/abs/2610.28586v1
- Category metadata: `cs.CL`
- Abstract SHA-256: `d2000a59706ce8e4aca6e0f2753f554a30712fb1f875172116b49ef49518c970`

**Source abstract (verbatim):**

```text
Agentic on-policy distillation (OPD) trains a student agent on its own trajectories while a teacher scores every token. A natural explanation of where it goes wrong is compounding error: the student's mistakes carry its trajectories beyond the region where the teacher is reliable, so recent methods keep training inside that region, through episode-length curricula, teacher-guided turns, prefix replay, or teacher intervention where the two disagree. We show this explanation is incomplete. From the states where the student departs most from the teacher, the teacher's own takeovers still finish the task, yet the student trained on its token scores keeps running out of turns. We attribute this to the myopia of next-token scoring. The teacher rates each token without seeing where the episode ends, so its scores let through the safe, delaying moves that outcome-based RL would punish with zero reward, a penalty agentic OPD lacks. We call this difference between what the teacher does and what it scores the rollout-scorer gap. We propose Rollout-to-Scorer Distillation (R2S), which repairs the scorer before distillation by mining high-disagreement states from the untrained student, running teacher takeovers from them, keeping the states where enough takeovers pass a reward-free check such as consensus or an LLM judge, and fine-tuning the teacher to give its takeover-informed scores on every assistant token from the divergence turn onward, without the takeover in context. The repaired teacher is frozen as the sole scorer for standard OPD, requiring no task reward during repair or training. Across three environments, two teachers and four students, R2S outperforms three state-of-the-art agentic-OPD methods in all twelve teacher-student-environment cells, by 12.8 success points on average over the best of them in each cell. Project page: https://tree-shu-zhao.github.io/r2s/.
```

**Extracted claims (5; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
The student agent's mistakes lead to trajectories beyond the teacher's reliable region.
```

Evidence excerpt (verbatim):

```text
A natural explanation of where it goes wrong is compounding error: the student's mistakes carry its trajectories beyond the region where the teacher is reliable,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
The teacher's next-token scoring is myopic and allows safe, delaying moves that outcome-based RL would punish.
```

Evidence excerpt (verbatim):

```text
The teacher rates each token without seeing where the episode ends, so its scores let through the safe, delaying moves that outcome-based RL would punish with zero reward,
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
The rollout-scorer gap is the difference between what the teacher does and what it scores.
```

Evidence excerpt (verbatim):

```text
We call this difference between what the teacher does and what it scores the rollout-scorer gap.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
R2S repairs the scorer before distillation by mining high-disagreement states and fine-tuning the teacher with takeover-informed scores.
```

Evidence excerpt (verbatim):

```text
We propose Rollout-to-Scorer Distillation (R2S), which repairs the scorer before distillation by mining high-disagreement states from the untrained student, running teacher takeovers from them, keeping the states where enough takeovers pass a reward-free check such as consensus or an LLM judge, and fine-tuning the teacher to give its takeover-informed scores on every assistant token from the divergence turn onward, without the takeover in context.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
R2S outperforms three state-of-the-art agentic-OPD methods across three environments, two teachers, and four students.
```

Evidence excerpt (verbatim):

```text
R2S outperforms three state-of-the-art agentic-OPD methods in all twelve teacher-student-environment cells, by 12.8 success points on average over the best of them in each cell.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.24939v1`
- Title: Vibe Coding, Interface Flattening
- Publication date: 2025-12-31T16:00:59Z
- Source: https://arxiv.org/abs/2512.24939v1
- Candidate selection metadata: same broad category `cs.CL`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Large language models are reshaping programming by enabling 'vibe coding': the development of softwares through natural-language interaction with model-driven toolchains. This article argues that vibe coding is best understood as interface flattening, a reconfiguration in which previously distinct modalities (GUI, CLI, and API) appear to converge into a single conversational surface, even as the underlying chain of translation from intention to machinic effect lengthens and thickens. Drawing on Friedrich Kittler's materialist media theory and Alexander Galloway's account of interfaces as sites of protocol control, the paper situates programming as a historically localised interface arrangement rather than an essential relation to computation. Through a materialist reconstruction of the contemporary vibe-coding stack, it shows how remote compute infrastructures, latency and connectivity, structured outputs, function/tool calling, and interoperability standards such as the Model Context Protocol relocate control and meaning-making power to model and protocol providers. The apparent democratisation of technical capability therefore depends on new dependencies and new literacies. By foregrounding the tension between experiential flattening and infrastructural thickening, I demonstrate how LLM-mediated development redistributes symbolic labour/power, obscures responsibility, and privatises competencies previously dispersed across programming communities, contributing a critical lens on the political economy of AI-mediated human-computer interaction.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 37. Cross-Area Transfer Learning for VLC-based Indoor Localization with a Transfer Efficiency Score

- Paper ID: `2610.29638v1`
- Publication date: 2026-10-21T12:18:14Z
- Source: https://arxiv.org/abs/2610.29638v1
- Category metadata: `cs.LG`
- Abstract SHA-256: `acbcd428ed9ab13e7bd66dcb6b7a660f36ede50ab426cf82b98d23650a6b83b2`

**Source abstract (verbatim):**

```text
Indoor localization systems are critical for Industry-4.0 applications. Visible Light Communication (VLC)-based systems offer advantages such as immunity to electromagnetic interference, high accuracy, and energy efficiency, but their performance is hindered by environmental variability across deployment areas. This paper presents a transfer learning (TL) framework for VLC-based indoor localization that enhances cross-area robustness while reducing data requirements. Using real-world measurements from four distinct areas of a Bosch manufacturing facility, we show that fine-tuning a deep neural network (DNN) pre-trained on source area data with only 40% of target-area measurements recovers 97% of full-data performance, thereby reducing the amount of target data needed. We further introduce the Transfer Efficiency Score (TES), a composite metric that identifies the most effective source models for transfer without exhaustive evaluation. Guided by TES, the framework selects the best source model, yielding localization errors as low as 40.9 cm with success rates above 86%. Validation on an unseen area confirms its generalization capability, with a 3.28 cm mean error achieved using the TES-selected source model. Overall, the proposed framework provides a scalable and data-efficient pathway for industrial VLC localization, substantially reducing deployment costs and computational burden while maintaining high accuracy in diverse and dynamic environments.
```

**Extracted claims (5; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
A transfer learning framework for VLC-based indoor localization enhances cross-area robustness while reducing data requirements.
```

Evidence excerpt (verbatim):

```text
This paper presents a transfer learning (TL) framework for VLC-based indoor localization that enhances cross-area robustness while reducing data requirements.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
Fine-tuning a deep neural network pre-trained on source area data with only 40% of target-area measurements recovers 97% of full-data performance.
```

Evidence excerpt (verbatim):

```text
Using real-world measurements from four distinct areas of a Bosch manufacturing facility, we show that fine-tuning a deep neural network (DNN) pre-trained on source area data with only 40% of target-area measurements recovers 97% of full-data performance, thereby reducing the amount of target data needed.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
The Transfer Efficiency Score (TES) is a composite metric that identifies the most effective source models for transfer without exhaustive evaluation.
```

Evidence excerpt (verbatim):

```text
We further introduce the Transfer Efficiency Score (TES), a composite metric that identifies the most effective source models for transfer without exhaustive evaluation.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
The framework selects the best source model guided by TES, yielding localization errors as low as 40.9 cm with success rates above 86%.
```

Evidence excerpt (verbatim):

```text
Guided by TES, the framework selects the best source model, yielding localization errors as low as 40.9 cm with success rates above 86%.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
Validation on an unseen area confirms the framework's generalization capability, achieving a 3.28 cm mean error using the TES-selected source model.
```

Evidence excerpt (verbatim):

```text
Validation on an unseen area confirms its generalization capability, with a 3.28 cm mean error achieved using the TES-selected source model.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.24780v2`
- Title: Gradient Descent as Implicit EM in Distance-Based Neural Models
- Publication date: 2025-12-31T10:56:43Z
- Source: https://arxiv.org/abs/2512.24780v2
- Candidate selection metadata: same broad category `cs.LG`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Neural networks trained with standard objectives exhibit behaviors characteristic of probabilistic inference: soft clustering, prototype specialization, and Bayesian uncertainty tracking. These phenomena appear across architectures -- in attention mechanisms, classification heads, and energy-based models -- yet existing explanations often rely on loose analogies to mixture models or post-hoc architectural interpretation. We provide a direct explanation. For any objective with log-sum-exp structure over distances or energies, the gradient with respect to each distance is exactly the negative posterior responsibility of the corresponding component: $\partial L / \partial d_j = -r_j$. The identity is algebraic, requiring only differentiability; it is a specialization of Fisher's identity, and its significance here is its address: standard neural objectives instantiate it without modification. The consequence is that gradient descent on such objectives performs generalized expectation-maximization implicitly, with responsibilities arising as gradients to be applied rather than auxiliary variables to be computed. This result unifies three regimes of learning: unsupervised mixture modeling, where responsibilities are fully latent; attention, where responsibilities are conditioned on queries; and cross-entropy classification, where supervision clamps responsibilities to targets. Our claims live at training time: the responsibility-weighted gradient dynamics recently documented in transformers follow from the objective's geometry. The in-context Bayesian computation that trained transformers perform at inference time is the endpoint of these dynamics, not their per-step content.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 38. MINER: Modeling Inter- and Intra-Person Variance for Reidentification

- Paper ID: `2610.28941v1`
- Publication date: 2026-10-20T21:34:43Z
- Source: https://arxiv.org/abs/2610.28941v1
- Category metadata: `cs.CV`
- Abstract SHA-256: `e472846bfa7415264e1b01d4a60c754d0494199dc659903528433c56db4900a2`

**Source abstract (verbatim):**

```text
Clothes-Changing Person Re-Identification (CC-ReID) remains challenging due to drastic appearance shifts across outfits. Most prior works devise biometric signal-extraction heuristics to enhance inter-person variance, e.g., using segmentation masks, while leaving intra-person variance uncontrolled. We present MINER, a simple model-agnostic framework that suppresses garment bias by contrasting hard examples and adaptively balancing dataset-dependent intra- and inter-person variance. Extensive experiments show that MINER improves retrieval across CC-ReID benchmarks, achieving state-of-the-art performance on four datasets and ranking among the leaders in all three tracks of the open TVRID RGB-Depth ReID challenge.
```

**Extracted claims (5; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
MINER is a model-agnostic framework that suppresses garment bias by contrasting hard examples.
```

Evidence excerpt (verbatim):

```text
We present MINER, a simple model-agnostic framework that suppresses garment bias by contrasting hard examples and adaptively balancing dataset-dependent intra- and inter-person variance.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
MINER adaptively balances dataset-dependent intra- and inter-person variance.
```

Evidence excerpt (verbatim):

```text
We present MINER, a simple model-agnostic framework that suppresses garment bias by contrasting hard examples and adaptively balancing dataset-dependent intra- and inter-person variance.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
MINER improves retrieval across CC-ReID benchmarks.
```

Evidence excerpt (verbatim):

```text
Extensive experiments show that MINER improves retrieval across CC-ReID benchmarks, achieving state-of-the-art performance on four datasets and ranking among the leaders in all three tracks of the open TVRID RGB-Depth ReID challenge.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
MINER achieves state-of-the-art performance on four datasets.
```

Evidence excerpt (verbatim):

```text
Extensive experiments show that MINER improves retrieval across CC-ReID benchmarks, achieving state-of-the-art performance on four datasets and ranking among the leaders in all three tracks of the open TVRID RGB-Depth ReID challenge.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
MINER ranks among the leaders in all three tracks of the open TVRID RGB-Depth ReID challenge.
```

Evidence excerpt (verbatim):

```text
Extensive experiments show that MINER improves retrieval across CC-ReID benchmarks, achieving state-of-the-art performance on four datasets and ranking among the leaders in all three tracks of the open TVRID RGB-Depth ReID challenge.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.24404v1`
- Title: Lifting Vision: Ground to Aerial Localization with Reasoning Guided Planning
- Publication date: 2025-12-30T18:36:39Z
- Source: https://arxiv.org/abs/2512.24404v1
- Candidate selection metadata: same broad category `cs.CV`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Multimodal intelligence development recently show strong progress in visual understanding and high level reasoning. Though, most reasoning system still reply on textual information as the main medium for inference. This limit their effectiveness in spatial tasks such as visual navigation and geo-localization. This work discuss about the potential scope of this field and eventually propose an idea visual reasoning paradigm Geo-Consistent Visual Planning, our introduced framework called Visual Reasoning for Localization, or ViReLoc, which performs planning and localization using only visual representations. The proposed framework learns spatial dependencies and geometric relations that text based reasoning often suffer to understand. By encoding step by step inference in the visual domain and optimizing with reinforcement based objectives, ViReLoc plans routes between two given ground images. The system also integrates contrastive learning and adaptive feature interaction to align cross view perspectives and reduce viewpoint differences. Experiments across diverse navigation and localization scenarios show consistent improvements in spatial reasoning accuracy and cross view retrieval performance. These results establish visual reasoning as a strong complementary approach for navigation and localization, and show that such tasks can be performed without real time global positioning system data, leading to more secure navigation solutions.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 39. BRIDGE: An Acceptance Gate to Block False Improvements in Model Updates, with a Retrospective Clinical Evaluation

- Paper ID: `2610.29515v1`
- Publication date: 2026-10-21T10:04:40Z
- Source: https://arxiv.org/abs/2610.29515v1
- Category metadata: `cs.LG`
- Abstract SHA-256: `862ece15bac439b294acf4a9a890a6ec56a2d96675d11e8b7365d4d28ed71d76`

**Source abstract (verbatim):**

```text
Models are updated repeatedly, and an update that looks better on validation data but not on new data is a false improvement that can misguide clinical decisions. The naive rule accepts every positive validation gain and is optimistic when the same data choose and judge the update. BRIDGE is a model-agnostic acceptance gate that decides each update from predictions and the available labels, with fixed settings. Each fold of the data judges the update chosen on the other folds (cross-fitting) to reduce selection bias; acceptance requires the gain's lower bootstrap bound to exceed a margin. The four settings are (A) 11 new datasets, (B) synthetic tasks, (C) 12 retrospective clinical tasks, and (D) 39 supporting datasets. The false-improvement rate falls from 19.1% (naive) to 1.1% (BRIDGE) in (A), 20.7% to 1.7% (B), 20.0% to 0% (C), and 12.5% to 0.5% (D); every 95% confidence interval of the reduction over datasets or tasks excludes zero (not over the clinical sources). An equal-size random draw from the naive acceptances contains more false improvements in (A)-(E) (post hoc, p<0.001). On the OpenML collection (E) of 14 new datasets, the false-improvement rate falls from 25.6% to 1.0%. BRIDGE removes 97% to 100% of the false improvements that the naive rule accepts, and its mean gain per deployed update is 1.8 to 3.1 times the naive rule's. The 95% upper bound on the false-improvement rate is below 5.5%: formal in (B) for independent tasks (3.56%), and conditional on the real data tested (0.33% to 5.40%).
```

**Extracted claims (5; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
BRIDGE is a model-agnostic acceptance gate that decides each update from predictions and the available labels, with fixed settings.
```

Evidence excerpt (verbatim):

```text
BRIDGE is a model-agnostic acceptance gate that decides each update from predictions and the available labels, with fixed settings.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
Each fold of the data judges the update chosen on the other folds (cross-fitting) to reduce selection bias.
```

Evidence excerpt (verbatim):

```text
Each fold of the data judges the update chosen on the other folds (cross-fitting) to reduce selection bias;
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
The false-improvement rate falls from 19.1% (naive) to 1.1% (BRIDGE) in (A).
```

Evidence excerpt (verbatim):

```text
The false-improvement rate falls from 19.1% (naive) to 1.1% (BRIDGE) in (A), 20.7% to 1.7% (B), 20.0% to 0% (C), and 12.5% to 0.5% (D);
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
BRIDGE removes 97% to 100% of the false improvements that the naive rule accepts.
```

Evidence excerpt (verbatim):

```text
BRIDGE removes 97% to 100% of the false improvements that the naive rule accepts, and its mean gain per deployed update is 1.8 to 3.1 times the naive rule's.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
The 95% upper bound on the false-improvement rate is below 5.5%: formal in (B) for independent tasks (3.56%), and conditional on the real data tested (0.33% to 5.40%).
```

Evidence excerpt (verbatim):

```text
The 95% upper bound on the false-improvement rate is below 5.5%: formal in (B) for independent tasks (3.56%), and conditional on the real data tested (0.33% to 5.40%).
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2610.29192v1`
- Title: Curvature-Scaled Sharpness-Aware Minimization: Convergence Beyond Smoothness
- Publication date: 2026-10-21T04:26:54Z
- Source: https://arxiv.org/abs/2610.29192v1
- Candidate selection metadata: same broad category `cs.LG`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Sharpness-Aware Minimization (SAM) has established itself as a widely used method for training deep neural networks. Despite its popularity, existing convergence guarantees for SAM-type methods require smoothness, a restrictive assumption. Generalized smoothness conditions have recently been proposed in the analysis of gradient methods but remain underexplored for SAM. To analyze the effect of SAM's perturbation under generalized smoothness, we use relative gradient distortion to quantify how the sharpness-aware direction departs from the original gradient. Under $(L_0,L_1)$-smoothness, we show that this distortion can become unbounded near stationarity for SAM and at large gradients for its unnormalized variant (USAM), with examples where SAM cycles and USAM diverges. We then establish a necessary condition for uniform distortion control among perturbations along the gradient whose nonnegative multipliers depend only on its norm. Motivated by this condition, we propose Curvature-Scaled SAM (CS-SAM), which scales both the perturbation and the descent step by suitable curvature upper bounds, and prove that it uniformly bounds the distortion. Under both $(L_0,L_1)$- and $(H_0,H_1)$-smoothness, we establish deterministic $\mathcal{O}(1/T)$ rates for the best squared gradient norm on nonconvex objectives, last-iterate $\mathcal{O}(1/T)$ rates for the function gap on convex objectives with a minimizer, and linear convergence under the Polyak-Lojasiewicz condition. With zero perturbation, our guarantees recover the rates for gradient descent with $(L_0,L_1)$- or $(H_0,H_1)$-based step-sizes. Minibatch experiments on computer vision tasks demonstrate competitive performance for both variants, with the $(H_0,H_1)$ variant achieving the highest mean best-test accuracy in all four settings against tuned SAM and USAM with constant and cosine annealing schedules.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 40. F2IDiff: Real-world Image Super-resolution using Feature to Image Diffusion Foundation Model

- Paper ID: `2512.24473v1`
- Publication date: 2025-12-30T21:37:35Z
- Source: https://arxiv.org/abs/2512.24473v1
- Category metadata: `cs.CV`
- Abstract SHA-256: `f96da9ac4d981e09d250d0543f9fda4ccbc4767ebd9673da8789455875417fa0`

**Source abstract (verbatim):**

```text
With the advent of Generative AI, Single Image Super-Resolution (SISR) quality has seen substantial improvement, as the strong priors learned by Text-2-Image Diffusion (T2IDiff) Foundation Models (FM) can bridge the gap between High-Resolution (HR) and Low-Resolution (LR) images. However, flagship smartphone cameras have been slow to adopt generative models because strong generation can lead to undesirable hallucinations. For substantially degraded LR images, as seen in academia, strong generation is required and hallucinations are more tolerable because of the wide gap between LR and HR images. In contrast, in consumer photography, the LR image has substantially higher fidelity, requiring only minimal hallucination-free generation. We hypothesize that generation in SISR is controlled by the stringency and richness of the FM's conditioning feature. First, text features are high level features, which often cannot describe subtle textures in an image. Additionally, Smartphone LR images are at least $12MP$, whereas SISR networks built on T2IDiff FM are designed to perform inference on much smaller images ($<1MP$). As a result, SISR inference has to be performed on small patches, which often cannot be accurately described by text feature. To address these shortcomings, we introduce an SISR network built on a FM with lower-level feature conditioning, specifically DINOv2 features, which we call a Feature-to-Image Diffusion (F2IDiff) Foundation Model (FM). Lower level features provide stricter conditioning while being rich descriptors of even small patches.
```

**Extracted claims (4; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
Strong generation can lead to undesirable hallucinations in flagship smartphone cameras.
```

Evidence excerpt (verbatim):

```text
However, flagship smartphone cameras have been slow to adopt generative models because strong generation can lead to undesirable hallucinations.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
For substantially degraded LR images, strong generation is required and hallucinations are more tolerable.
```

Evidence excerpt (verbatim):

```text
For substantially degraded LR images, as seen in academia, strong generation is required and hallucinations are more tolerable because of the wide gap between LR and HR images.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
Smartphone LR images have substantially higher fidelity, requiring only minimal hallucination-free generation.
```

Evidence excerpt (verbatim):

```text
In contrast, in consumer photography, the LR image has substantially higher fidelity, requiring only minimal hallucination-free generation.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
SISR inference has to be performed on small patches, which often cannot be accurately described by text feature.
```

Evidence excerpt (verbatim):

```text
As a result, SISR inference has to be performed on small patches, which often cannot be accurately described by text feature.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.24224v1`
- Title: ARM: A Learnable, Plug-and-Play Module for CLIP-based Open-vocabulary Semantic Segmentation
- Publication date: 2025-12-30T13:38:30Z
- Source: https://arxiv.org/abs/2512.24224v1
- Candidate selection metadata: same broad category `cs.CV`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Open-vocabulary semantic segmentation (OVSS) is fundamentally hampered by the coarse, image-level representations of CLIP, which lack precise pixel-level details. Existing training-free methods attempt to resolve this by either importing priors from costly external foundation models (e.g., SAM, DINO) or by applying static, hand-crafted heuristics to CLIP's internal features. These approaches are either computationally expensive or sub-optimal. We propose the Attention Refinement Module (ARM), a lightweight, learnable module that effectively unlocks and refines CLIP's internal potential. Unlike static-fusion methods, ARM learns to adaptively fuse hierarchical features. It employs a semantically-guided cross-attention block, using robust deep features (K, V) to select and refine detail-rich shallow features (Q), followed by a self-attention block. The key innovation lies in a ``train once, use anywhere" paradigm. Trained once on a general-purpose dataset (e.g., COCO-Stuff), ARM acts as a universal plug-and-play post-processor for diverse training-free frameworks. Extensive experiments show that ARM consistently boosts baseline performance on multiple benchmarks with negligible inference overhead, establishing an efficient and effective paradigm for training-free OVSS.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 41. Scan or Index? large Evidence Coverage, Answer Quality, and Cost in Long-Document RAG

- Paper ID: `2610.28957v1`
- Publication date: 2026-10-20T22:11:07Z
- Source: https://arxiv.org/abs/2610.28957v1
- Category metadata: `cs.CL`
- Abstract SHA-256: `dccfdcfc39336472bd9526185ad583434466d482bd943691ab96744a2e4bb49f`

**Source abstract (verbatim):**

```text
Scanning every passage in a long document seems thorough, but does it preserve more useful evidence or produce better answers? We compare 11 retrieval configurations spanning lexical and dense search, hybrid reranking, and full-document scanning with Jev, OpenAI Decisions, and Cloudflare Clef. Our evaluation uses 396 QASPER questions and 80 questions from eight complete textbooks, with common passages, a five-passage limit, and a fixed answer generator. On books, Hybrid + Jev achieves the highest observed evidence coverage (94.1%), compared with 88.7% for Jev full scan and 81.3\% for OpenAI dense retrieval. Full scans examine every passage initially, yet later reduction steps can discard relevant evidence. Higher evidence coverage also does not consistently produce better answers: Hybrid + Decisions achieves the highest observed book Answer Accuracy among retrieval methods (0.892), despite recovering less reference evidence. Full scanning incurs substantially higher latency on books under the tested deployments, while reusable dense retrieval has lower projected API cost than paid decision-based methods as queries accumulate. Most QASPER articles already fit within the hybrid candidate pool, limiting the benefit of scanning. These results highlight evidence retention, answer quality, and reuse cost as complementary criteria for choosing a long-document retrieval strategy.
```

**Extracted claims (4; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
Hybrid + Jev achieves the highest observed evidence coverage on books.
```

Evidence excerpt (verbatim):

```text
Hybrid + Jev achieves the highest observed evidence coverage (94.1%), compared with 88.7% for Jev full scan and 81.3\% for OpenAI dense retrieval.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
Hybrid + Decisions achieves the highest observed book Answer Accuracy among retrieval methods.
```

Evidence excerpt (verbatim):

```text
Hybrid + Decisions achieves the highest observed book Answer Accuracy among retrieval methods (0.892), despite recovering less reference evidence.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
Full scanning incurs substantially higher latency on books under the tested deployments.
```

Evidence excerpt (verbatim):

```text
Full scanning incurs substantially higher latency on books under the tested deployments, while reusable dense retrieval has lower projected API cost than paid decision-based methods as queries accumulate.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
Most QASPER articles already fit within the hybrid candidate pool, limiting the benefit of scanning.
```

Evidence excerpt (verbatim):

```text
Most QASPER articles already fit within the hybrid candidate pool, limiting the benefit of scanning.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.24939v1`
- Title: Vibe Coding, Interface Flattening
- Publication date: 2025-12-31T16:00:59Z
- Source: https://arxiv.org/abs/2512.24939v1
- Candidate selection metadata: same broad category `cs.CL`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Large language models are reshaping programming by enabling 'vibe coding': the development of softwares through natural-language interaction with model-driven toolchains. This article argues that vibe coding is best understood as interface flattening, a reconfiguration in which previously distinct modalities (GUI, CLI, and API) appear to converge into a single conversational surface, even as the underlying chain of translation from intention to machinic effect lengthens and thickens. Drawing on Friedrich Kittler's materialist media theory and Alexander Galloway's account of interfaces as sites of protocol control, the paper situates programming as a historically localised interface arrangement rather than an essential relation to computation. Through a materialist reconstruction of the contemporary vibe-coding stack, it shows how remote compute infrastructures, latency and connectivity, structured outputs, function/tool calling, and interoperability standards such as the Model Context Protocol relocate control and meaning-making power to model and protocol providers. The apparent democratisation of technical capability therefore depends on new dependencies and new literacies. By foregrounding the tension between experiential flattening and infrastructural thickening, I demonstrate how LLM-mediated development redistributes symbolic labour/power, obscures responsibility, and privatises competencies previously dispersed across programming communities, contributing a critical lens on the political economy of AI-mediated human-computer interaction.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 42. GoiBERT: Compact Vietnamese Language Models via Two-Stage Knowledge Distillation

- Paper ID: `2610.30067v1`
- Publication date: 2026-10-21T17:24:36Z
- Source: https://arxiv.org/abs/2610.30067v1
- Category metadata: `cs.CL`
- Abstract SHA-256: `5ca14265b2283bd04e349428319422e22c707e16656f75dca68fe0b4a234f46b`

**Source abstract (verbatim):**

```text
Vietnamese pre-trained encoders have improved rapidly, but the strongest ones are large, multilingual-vocabulary models or depend on external word segmentation, which makes them costly to deploy. We present GoiBERT, a family of two compact Vietnamese encoders with 26M and 49M parameters that operate directly on raw text. GoiBERT learns from two complementary teachers. A same-tokenizer Vietnamese encoder first teaches general-purpose representations. A much larger teacher then provides task-level guidance through soft labels that are generated without ever labeling its own training data. Across eight benchmarks covering text classification, aspect-based sentiment analysis, natural language inference, and named entity recognition, GoiBERT-large achieves the highest average score among non-teacher models. It does so with fewer than half the parameters of the strongest compact baseline and twice its throughput. GoiBERT-base retains 99% of that baseline's performance at a quarter of its size. Our analysis shows that compression is nearly lossless for sentiment and classification tasks but remains costly for inference and entity recognition, which points to clear directions for future work. Our code and models are available at: https://github.com/Nhantran65/GoiBERT.git
```

**Extracted claims (5; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
GoiBERT is a family of compact Vietnamese encoders with 26M and 49M parameters that operate directly on raw text.
```

Evidence excerpt (verbatim):

```text
GoiBERT, a family of two compact Vietnamese encoders with 26M and 49M parameters that operate directly on raw text.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
GoiBERT learns from two complementary teachers: a same-tokenizer Vietnamese encoder and a much larger teacher that provides task-level guidance through soft labels.
```

Evidence excerpt (verbatim):

```text
GoiBERT learns from two complementary teachers. A same-tokenizer Vietnamese encoder first teaches general-purpose representations. A much larger teacher then provides task-level guidance through soft labels that are generated without ever labeling its own training data.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
GoiBERT-large achieves the highest average score among non-teacher models across eight benchmarks.
```

Evidence excerpt (verbatim):

```text
GoiBERT-large achieves the highest average score among non-teacher models. It does so with fewer than half the parameters of the strongest compact baseline and twice its throughput.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
GoiBERT-base retains 99% of the performance of the strongest compact baseline at a quarter of its size.
```

Evidence excerpt (verbatim):

```text
GoiBERT-base retains 99% of that baseline's performance at a quarter of its size.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 5

Claim (verbatim):

```text
Compression is nearly lossless for sentiment and classification tasks but remains costly for inference and entity recognition.
```

Evidence excerpt (verbatim):

```text
Our analysis shows that compression is nearly lossless for sentiment and classification tasks but remains costly for inference and entity recognition, which points to clear directions for future work.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2610.28957v1`
- Title: Scan or Index? large Evidence Coverage, Answer Quality, and Cost in Long-Document RAG
- Publication date: 2026-10-20T22:11:07Z
- Source: https://arxiv.org/abs/2610.28957v1
- Candidate selection metadata: same broad category `cs.CL`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Scanning every passage in a long document seems thorough, but does it preserve more useful evidence or produce better answers? We compare 11 retrieval configurations spanning lexical and dense search, hybrid reranking, and full-document scanning with Jev, OpenAI Decisions, and Cloudflare Clef. Our evaluation uses 396 QASPER questions and 80 questions from eight complete textbooks, with common passages, a five-passage limit, and a fixed answer generator. On books, Hybrid + Jev achieves the highest observed evidence coverage (94.1%), compared with 88.7% for Jev full scan and 81.3\% for OpenAI dense retrieval. Full scans examine every passage initially, yet later reduction steps can discard relevant evidence. Higher evidence coverage also does not consistently produce better answers: Hybrid + Decisions achieves the highest observed book Answer Accuracy among retrieval methods (0.892), despite recovering less reference evidence. Full scanning incurs substantially higher latency on books under the tested deployments, while reusable dense retrieval has lower projected API cost than paid decision-based methods as queries accumulate. Most QASPER articles already fit within the hybrid candidate pool, limiting the benefit of scanning. These results highlight evidence retention, answer quality, and reuse cost as complementary criteria for choosing a long-document retrieval strategy.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---

## 43. Detecting and Mitigating Treatment Leakage in Text-Based Causal Inference: Distillation and Sensitivity Analysis

- Paper ID: `2601.02400v1`
- Publication date: 2025-12-30T20:36:09Z
- Source: https://arxiv.org/abs/2601.02400v1
- Category metadata: `cs.CL`
- Abstract SHA-256: `3c19252f8aaeea94d2a2b68728940761085c0802d7caa6ffc4c0bad830574ae8`

**Source abstract (verbatim):**

```text
Text-based causal inference increasingly employs textual data as proxies for unobserved confounders, yet this approach introduces a previously undertheorized source of bias: treatment leakage. Treatment leakage occurs when text intended to capture confounding information also contains signals predictive of treatment status, thereby inducing post-treatment bias in causal estimates. Critically, this problem can arise even when documents precede treatment assignment, as authors may employ future-referencing language that anticipates subsequent interventions. Despite growing recognition of this issue, no systematic methods exist for identifying and mitigating treatment leakage in text-as-confounder applications. This paper addresses this gap through three contributions. First, we provide formal statistical and set-theoretic definitions of treatment leakage that clarify when and why bias occurs. Second, we propose four text distillation methods -- similarity-based passage removal, distant supervision classification, salient feature removal, and iterative nullspace projection -- designed to eliminate treatment-predictive content while preserving confounder information. Third, we validate these methods through simulations using synthetic text and an empirical application examining International Monetary Fund structural adjustment programs and child mortality. Our findings indicate that moderate distillation optimally balances bias reduction against confounder retention, whereas overly stringent approaches degrade estimate precision.
```

**Extracted claims (4; text preserved verbatim):**

### Claim 1

Claim (verbatim):

```text
Treatment leakage in text-based causal inference occurs when text intended to capture confounding information also contains signals predictive of treatment status.
```

Evidence excerpt (verbatim):

```text
Treatment leakage occurs when text intended to capture confounding information also contains signals predictive of treatment status, thereby inducing post-treatment bias in causal estimates.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 2

Claim (verbatim):

```text
Formal statistical and set-theoretic definitions of treatment leakage are provided to clarify when and why bias occurs.
```

Evidence excerpt (verbatim):

```text
First, we provide formal statistical and set-theoretic definitions of treatment leakage that clarify when and why bias occurs.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 3

Claim (verbatim):

```text
Four text distillation methods are proposed to eliminate treatment-predictive content while preserving confounder information.
```

Evidence excerpt (verbatim):

```text
Second, we propose four text distillation methods -- similarity-based passage removal, distant supervision classification, salient feature removal, and iterative nullspace projection -- designed to eliminate treatment-predictive content while preserving confounder information.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

### Claim 4

Claim (verbatim):

```text
Moderate distillation optimally balances bias reduction against confounder retention, whereas overly stringent approaches degrade estimate precision.
```

Evidence excerpt (verbatim):

```text
Our findings indicate that moderate distillation optimally balances bias reduction against confounder retention, whereas overly stringent approaches degrade estimate precision.
```

- Semantic support: [ ] supported  [ ] unsupported  [ ] unclear
- Atomicity: [ ] atomic  [ ] not atomic  [ ] unclear
- Decision: [ ] accept  [ ] reject  [ ] unsure
- Evidence reference / rationale: ____________________________________

**Proposed same-topic decoy — NOT verified:**

- Candidate ID: `2512.23049v1`
- Title: Accelerating Language Model Workflows with Prompt Choreography
- Publication date: 2025-12-28T19:21:11Z
- Source: https://arxiv.org/abs/2512.23049v1
- Candidate selection metadata: same broad category `cs.CL`; deterministic seed 49; this does not establish semantic same-topic validity.
- Temporal relation: candidate is no later than focal
- Source abstract (verbatim):

```text
Large language models are increasingly deployed in multi-agent workflows. We introduce Prompt Choreography, a framework that efficiently executes LLM workflows by maintaining a dynamic, global KV cache. Each LLM call can attend to an arbitrary, reordered subset of previously encoded messages. Parallel calls are supported. Though caching messages' encodings sometimes gives different results from re-encoding them in a new context, we show in diverse settings that fine-tuning the LLM to work with the cache can help it mimic the original results. Prompt Choreography significantly reduces per-message latency (2.0--6.2$\times$ faster time-to-first-token) and achieves substantial end-to-end speedups ($>$2.2$\times$) in some workflows dominated by redundant computation.
```

- Same-topic decision: [ ] yes  [ ] no  [ ] unclear
- Independent evidence reference: ____________________________________
- Reviewer ID/date: _________________________________________________

---
