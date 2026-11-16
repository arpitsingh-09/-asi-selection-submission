# A1 Human Review Form — Shortlisted Papers 1 and 2

Reviewer ID/code: AS-01

Review date: 2026-11-14

Record your independent judgments for each claim by comparing it with the
original abstract. No AI assessments or decisions are prefilled in this form.

## Paper 1 — Stream-DiffVSR: Low-Latency Streamable Video Super-Resolution via Auto-Regressive Diffusion

- Paper ID: `2512.23709v3`
- Source: https://arxiv.org/abs/2512.23709v3

### Original abstract (verbatim)

> Diffusion-based video super-resolution (VSR) methods deliver strong perceptual quality but are often unsuitable for latency-sensitive scenarios due to reliance on future frames and expensive multi-step denoising. We propose Stream-DiffVSR, a causally conditioned diffusion framework for efficient online VSR. Operating strictly on past frames, Stream-DiffVSR integrates a four-step distilled denoiser for fast inference, an Auto-regressive Temporal Guidance (ARTG) module that injects motion-aligned cues during latent denoising, and a lightweight temporal-aware decoder with a Temporal Processor Module (TPM) to enhance detail and temporal coherence. Unlike chunk-wise streaming inference, our strictly frame-by-frame causal design avoids sequence-level waiting, substantially reducing time-to-first-frame and end-to-end latency. Stream-DiffVSR processes 720p frames in 0.328 seconds on an RTX 4090 and consistently outperforms prior diffusion-based baselines. Compared with the online state-of-the-art TMP, it improves perceptual quality (LPIPS +0.095). Compared with prior diffusion-based VSR methods such as MGLD-VSR, it reduces per-frame runtime by over 130x. Moreover, Stream-DiffVSR substantially lowers time-to-first-frame for diffusion-based VSR, reducing initial delay from over 4600 seconds to 0.328 seconds, making diffusion-based VSR markedly more practical for low-latency online and streaming deployment. Project page: https://jamichss.github.io/stream-diffvsr-project-page/

### Claim 1

**Claim:** Stream-DiffVSR is a causally conditioned diffusion framework for efficient online video super-resolution.

**Supporting evidence excerpt:** “We propose Stream-DiffVSR, a causally conditioned diffusion framework for efficient online VSR.”

- Semantic support: [x] Supported  [ ] Unsupported  [ ] Unclear
- Atomicity: [x] Atomic  [ ] Compound  [ ] Unclear
- Rationale: The abstract directly supports the claim, and the claim expresses one scientific assertion.

### Claim 2

**Claim:** Stream-DiffVSR integrates a four-step distilled denoiser for fast inference.

**Supporting evidence excerpt:** “Stream-DiffVSR integrates a four-step distilled denoiser for fast inference,”

- Semantic support: [x] Supported  [ ] Unsupported  [ ] Unclear
- Atomicity: [x] Atomic  [ ] Compound  [ ] Unclear
- Rationale: The abstract directly confirms the use of a four-step distilled denoiser for fast inference. The claim expresses one scientific assertion.

### Claim 3

**Claim:** Stream-DiffVSR includes an Auto-regressive Temporal Guidance (ARTG) module that injects motion-aligned cues during latent denoising.

**Supporting evidence excerpt:** “an Auto-regressive Temporal Guidance (ARTG) module that injects motion-aligned cues during latent denoising,”

- Semantic support: [x] Supported  [ ] Unsupported  [ ] Unclear
- Atomicity: [x] Atomic  [ ] Compound  [ ] Unclear
- Rationale: The abstract directly confirms that the ARTG module injects motion-aligned cues during latent denoising. The claim describes one scientific mechanism and is atomic.

### Claim 4

**Claim:** Stream-DiffVSR employs a lightweight temporal-aware decoder with a Temporal Processor Module (TPM) to enhance detail and temporal coherence.

**Supporting evidence excerpt:** “and a lightweight temporal-aware decoder with a Temporal Processor Module (TPM) to enhance detail and temporal coherence.”

- Semantic support: [x] Supported  [ ] Unsupported  [ ] Unclear
- Atomicity: [x] Atomic  [ ] Compound  [ ] Unclear
- Rationale: The abstract directly supports the use of a temporal-aware decoder with the TPM module to improve detail and temporal coherence. The claim describes one scientific mechanism and is atomic.

### Claim 5

**Claim:** Stream-DiffVSR processes 720p frames in 0.328 seconds on an RTX 4090.

**Supporting evidence excerpt:** “Stream-DiffVSR processes 720p frames in 0.328 seconds on an RTX 4090”

- Semantic support: [x] Supported  [ ] Unsupported  [ ] Unclear
- Atomicity: [x] Atomic  [ ] Compound  [ ] Unclear
- Rationale: The abstract directly confirms the processing time of 0.328 seconds for 720p frames on an RTX 4090. The claim reports one performance measurement and is atomic.

### Claim 6

**Claim:** Stream-DiffVSR consistently outperforms prior diffusion-based baselines.

**Supporting evidence excerpt:** “and consistently outperforms prior diffusion-based baselines.”

- Semantic support: [x] Supported  [ ] Unsupported  [ ] Unclear
- Atomicity: [x] Atomic  [ ] Compound  [ ] Unclear
- Rationale: The abstract directly states that Stream-DiffVSR outperforms prior diffusion-based baselines. The claim describes one performance comparison and is atomic.

### Claim 7

**Claim:** Compared with the online state-of-the-art TMP, Stream-DiffVSR improves perceptual quality (LPIPS +0.095).

**Supporting evidence excerpt:** “Compared with the online state-of-the-art TMP, it improves perceptual quality (LPIPS +0.095).”

- Semantic support: [x] Supported  [ ] Unsupported  [ ] Unclear
- Atomicity: [x] Atomic  [ ] Compound  [ ] Unclear
- Rationale: The abstract directly supports the reported LPIPS improvement of +0.095 compared with TMP. The claim expresses one performance comparison and is atomic.

### Claim 8

**Claim:** Compared with prior diffusion-based VSR methods such as MGLD-VSR, Stream-DiffVSR reduces per-frame runtime by over 130x.

**Supporting evidence excerpt:** “Compared with prior diffusion-based VSR methods such as MGLD-VSR, it reduces per-frame runtime by over 130x.”

- Semantic support: [x] Supported  [ ] Unsupported  [ ] Unclear
- Atomicity: [x] Atomic  [ ] Compound  [ ] Unclear
- Rationale: The abstract directly supports the claim that Stream-DiffVSR reduces per-frame runtime by over 130× compared with MGLD-VSR and other diffusion-based methods. The claim expresses one performance comparison and is atomic.

### Claim 9

**Claim:** Stream-DiffVSR substantially lowers time-to-first-frame for diffusion-based VSR, reducing initial delay from over 4600 seconds to 0.328 seconds.

**Supporting evidence excerpt:** “Moreover, Stream-DiffVSR substantially lowers time-to-first-frame for diffusion-based VSR, reducing initial delay from over 4600 seconds to 0.328 seconds,”

- Semantic support: [x] Supported  [ ] Unsupported  [ ] Unclear
- Atomicity: [x] Atomic  [ ] Compound  [ ] Unclear
- Rationale: The abstract directly supports the reduction in time-to-first-frame from over 4600 seconds to 0.328 seconds. The claim describes one latency improvement and is atomic.

## Paper 2 — Parallelizable Probabilistic Latent Reasoning for Diverse Reasoning Trajectories

- Paper ID: `2610.29385v1`
- Source: https://arxiv.org/abs/2610.29385v1

### Original abstract (verbatim)

> Language models relying on verbalized Chain-of-Thought (CoT) are constrained to token-by-token generation in the language space, where many tokens serve textual coherence rather than core reasoning. This entangles genuine differences in logical trajectories with superficial variations in verbalization. Moving reasoning into a compact, continuous latent space offers a promising alternative for efficiently representing and exploring diverse reasoning trajectories. However, current latent models remain largely deterministic, capturing only a single reasoning trajectory rather than modeling a distribution over multiple valid alternatives. While stochastic approaches parameterize distributions over latent reasoning steps, they frequently suffer from unstable optimization and limited empirical performance. Furthermore, their reliance on autoregressive latent prediction during training precludes effective parallelization, leading to prohibitively long training times. To overcome these bottlenecks, we propose Probabilistic Latent Reasoning Models (PLRM), a parallelizable variational framework for probabilistic latent reasoning. PLRM adopts a JEPA-style objective in which the posterior infers latent distributions in parallel from observed reasoning trajectories, while the prior learns to predict the subsequent latent distribution via teacher forcing. To model heterogeneous reasoning processes, we introduce a discrete strategy variable together with a mixture-based prior, allowing the model to preserve the Gaussian-mixture structure induced by multiple distinct reasoning trajectories rather than collapsing them into a single Gaussian. Across diverse benchmarks, PLRM achieves performance competitive with deterministic latent reasoning models on single-trajectory datasets while enabling efficient training and consistently outperforming competing stochastic baselines on multi-trajectory datasets.

### Claim 1

**Claim:** Language models relying on verbalized Chain-of-Thought (CoT) are constrained to token-by-token generation in the language space.

**Supporting evidence excerpt:** “Language models relying on verbalized Chain-of-Thought (CoT) are constrained to token-by-token generation in the language space,”

- Semantic support: [x] Supported  [ ] Unsupported  [ ] Unclear
- Atomicity: [x] Atomic  [ ] Compound  [ ] Unclear
- Rationale: The abstract directly states that verbalized Chain-of-Thought reasoning requires token-by-token generation in language space. The claim expresses one scientific assertion and is atomic.

### Claim 2

**Claim:** Moving reasoning into a compact, continuous latent space offers a promising alternative for efficiently representing and exploring diverse reasoning trajectories.

**Supporting evidence excerpt:** “Moving reasoning into a compact, continuous latent space offers a promising alternative for efficiently representing and exploring diverse reasoning trajectories.”

- Semantic support: [x] Supported  [ ] Unsupported  [ ] Unclear
- Atomicity: [ ] Atomic  [x] Compound  [ ] Unclear
- Rationale: The abstract supports the benefits of continuous latent reasoning, but the claim combines two separable benefits: efficiently representing reasoning trajectories and exploring diverse trajectories. Therefore, it is supported but compound.

### Claim 3

**Claim:** Current latent models remain largely deterministic, capturing only a single reasoning trajectory rather than modeling a distribution over multiple valid alternatives.

**Supporting evidence excerpt:** “However, current latent models remain largely deterministic, capturing only a single reasoning trajectory rather than modeling a distribution over multiple valid alternatives.”

- Semantic support: [x] Supported  [ ] Unsupported  [ ] Unclear
- Atomicity: [x] Atomic  [ ] Compound  [ ] Unclear
- Rationale: The abstract states that current latent models are largely deterministic and capture only one reasoning trajectory rather than multiple alternatives. The claim describes one limitation and is atomic.

### Claim 4

**Claim:** Stochastic approaches parameterize distributions over latent reasoning steps but frequently suffer from unstable optimization and limited empirical performance.

**Supporting evidence excerpt:** “While stochastic approaches parameterize distributions over latent reasoning steps, they frequently suffer from unstable optimization and limited empirical performance.”

- Semantic support: [x] Supported  [ ] Unsupported  [ ] Unclear
- Atomicity: [ ] Atomic  [x] Compound  [ ] Unclear
- Rationale: The abstract supports the claim, but it combines multiple assertions about stochastic approaches: their distribution modeling, unstable optimization, and limited empirical performance. Therefore, it is supported but compound.

### Claim 5

**Claim:** PLRM adopts a JEPA-style objective in which the posterior infers latent distributions in parallel from observed reasoning trajectories.

**Supporting evidence excerpt:** “PLRM adopts a JEPA-style objective in which the posterior infers latent distributions in parallel from observed reasoning trajectories,”

- Semantic support: [x] Supported  [ ] Unsupported  [ ] Unclear
- Atomicity: [x] Atomic  [ ] Compound  [ ] Unclear
- Rationale: The abstract explicitly describes PLRM’s JEPA-style objective and parallel posterior inference from observed reasoning trajectories. The claim expresses one scientific mechanism and is atomic.

### Claim 6

**Claim:** PLRM introduces a discrete strategy variable together with a mixture-based prior to model heterogeneous reasoning processes.

**Supporting evidence excerpt:** “To model heterogeneous reasoning processes, we introduce a discrete strategy variable together with a mixture-based prior,”

- Semantic support: [x] Supported  [ ] Unsupported  [ ] Unclear
- Atomicity: [x] Atomic  [ ] Compound  [ ] Unclear
- Rationale: The abstract confirms that PLRM introduces a discrete strategy variable and a mixture-based prior to model heterogeneous reasoning processes. These components form one proposed modeling mechanism, so the claim can be considered atomic.

### Claim 7

**Claim:** PLRM preserves the Gaussian-mixture structure induced by multiple distinct reasoning trajectories rather than collapsing them into a single Gaussian.

**Supporting evidence excerpt:** “allowing the model to preserve the Gaussian-mixture structure induced by multiple distinct reasoning trajectories rather than collapsing them into a single Gaussian.”

- Semantic support: [x] Supported  [ ] Unsupported  [ ] Unclear
- Atomicity: [x] Atomic  [ ] Compound  [ ] Unclear
- Rationale: The abstract directly states that PLRM preserves the Gaussian-mixture structure of distinct reasoning trajectories instead of collapsing them into a single Gaussian. The claim expresses one scientific property and is atomic.

### Claim 8

**Claim:** PLRM achieves performance competitive with deterministic latent reasoning models on single-trajectory datasets.

**Supporting evidence excerpt:** “Across diverse benchmarks, PLRM achieves performance competitive with deterministic latent reasoning models on single-trajectory datasets while enabling efficient training and consistently outperforming competing stochastic baselines on multi-trajectory datasets.”

- Semantic support: [x] Supported  [ ] Unsupported  [ ] Unclear
- Atomicity: [x] Atomic  [ ] Compound  [ ] Unclear
- Rationale: The abstract states that PLRM achieves performance competitive with deterministic latent reasoning models on single-trajectory datasets. The claim describes one performance comparison and is atomic.

### Claim 9

**Claim:** PLRM consistently outperforms competing stochastic baselines on multi-trajectory datasets.

**Supporting evidence excerpt:** “Across diverse benchmarks, PLRM achieves performance competitive with deterministic latent reasoning models on single-trajectory datasets while enabling efficient training and consistently outperforming competing stochastic baselines on multi-trajectory datasets.”

- Semantic support: [x] Supported  [ ] Unsupported  [ ] Unclear
- Atomicity: [x] Atomic  [ ] Compound  [ ] Unclear
- Rationale: The abstract explicitly states that PLRM consistently outperforms competing stochastic baselines on multi-trajectory datasets. The claim describes one performance comparison and is atomic.
