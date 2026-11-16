# Independent input-relevance review — blinded packet

Reviewer copy: reviewer_2

## Instructions

Complete this review independently. Do not discuss questions or ratings with the other reviewer. Use only the question text and source papers in this packet; do not look up generation records or scores.
Question IDs and collection IDs are neutral identifiers. Evaluate every assigned question–paper pair in the blank form. The form also asks uniformly about topic fit and whether the supplied papers substantively support each question premise. Do not infer expected outcomes from the identifiers or order.

For each question–paper pair, assign one relevance rating:

- **0 — Unrelated/no grounding:** the paper is unrelated to the question premise or offers no grounding.
- **1 — Topical, not directly grounding:** the paper is on-topic but does not directly ground the question premise.
- **2 — Directly relevant evidence:** the paper provides directly relevant evidence for the question premise.

For each assigned question–collection association, independently answer whether it is in the same broad topic area and whether the supplied collection substantively supports the question premise. Add a short evidence note for each paper rating and association check. Use the form's reviewer code and UTC date fields; retain your original ratings and do not adjudicate with the other reviewer.

## Source collections

### Collection C-E5ACD7

#### Document D-B76C01

**Title:** Unpaired Image Enhancement with Quality-Attention Generative Adversarial Network

**Abstract:**

```text
In this work, we aim to learn an unpaired image enhancement model, which can enrich low-quality images with the characteristics of high-quality images provided by users. We propose a quality attention generative adversarial network (QAGAN) trained on unpaired data based on the bidirectional Generative Adversarial Network (GAN) embedded with a quality attention module (QAM). The key novelty of the proposed QAGAN lies in the injected QAM for the generator such that it learns domain-relevant quality attention directly from the two domains. More specifically, the proposed QAM allows the generator to effectively select semantic-related characteristics from the spatial-wise and adaptively incorporate style-related attributes from the channel-wise, respectively. Therefore, in our proposed QAGAN, not only discriminators but also the generator can directly access both domains which significantly facilitates the generator to learn the mapping function. Extensive experimental results show that, compared with the state-of-the-art methods based on unpaired learning, our proposed method achieves better performance in both objective and subjective evaluations.
```

#### Document D-84D9A1

**Title:** Towards Unsupervised Deep Image Enhancement with Generative Adversarial Network

**Abstract:**

```text
Improving the aesthetic quality of images is challenging and eager for the public. To address this problem, most existing algorithms are based on supervised learning methods to learn an automatic photo enhancer for paired data, which consists of low-quality photos and corresponding expert-retouched versions. However, the style and characteristics of photos retouched by experts may not meet the needs or preferences of general users. In this paper, we present an unsupervised image enhancement generative adversarial network (UEGAN), which learns the corresponding image-to-image mapping from a set of images with desired characteristics in an unsupervised manner, rather than learning on a large number of paired images. The proposed model is based on single deep GAN which embeds the modulation and attention mechanisms to capture richer global and local features. Based on the proposed model, we introduce two losses to deal with the unsupervised image enhancement: (1) fidelity loss, which is defined as a L2 regularization in the feature domain of a pre-trained VGG network to ensure the content between the enhanced image and the input image is the same, and (2) quality loss that is formulated as a relativistic hinge adversarial loss to endow the input image the desired characteristics. Both quantitative and qualitative results show that the proposed model effectively improves the aesthetic quality of images. Our code is available at: https://github.com/eezkni/UEGAN.
```

#### Document D-B561B6

**Title:** Low-Light Image Enhancement via Generative Perceptual Priors

**Abstract:**

```text
Although significant progress has been made in enhancing visibility, retrieving texture details, and mitigating noise in Low-Light (LL) images, the challenge persists in applying current Low-Light Image Enhancement (LLIE) methods to real-world scenarios, primarily due to the diverse illumination conditions encountered. Furthermore, the quest for generating enhancements that are visually realistic and attractive remains an underexplored realm. In response to these challenges, we introduce a novel \textbf{LLIE} framework with the guidance of \textbf{G}enerative \textbf{P}erceptual \textbf{P}riors (\textbf{GPP-LLIE}) derived from vision-language models (VLMs). Specifically, we first propose a pipeline that guides VLMs to assess multiple visual attributes of the LL image and quantify the assessment to output the global and local perceptual priors. Subsequently, to incorporate these generative perceptual priors to benefit LLIE, we introduce a transformer-based backbone in the diffusion process, and develop a new layer normalization (\textit{\textbf{GPP-LN}}) and an attention mechanism (\textit{\textbf{LPP-Attn}}) guided by global and local perceptual priors. Extensive experiments demonstrate that our model outperforms current SOTA methods on paired LL datasets and exhibits superior generalization on real-world data. The code is released at \url{https://github.com/LowLevelAI/GPP-LLIE}.
```

### Collection C-877C7D

#### Document D-DB4D08

**Title:** Overview of MediaEval 2020 Predicting Media Memorability Task: What Makes a Video Memorable?

**Abstract:**

```text
This paper describes the MediaEval 2020 \textit{Predicting Media Memorability} task. After first being proposed at MediaEval 2018, the Predicting Media Memorability task is in its 3rd edition this year, as the prediction of short-term and long-term video memorability (VM) remains a challenging task. In 2020, the format remained the same as in previous editions. This year the videos are a subset of the TRECVid 2019 Video-to-Text dataset, containing more action rich video content as compared with the 2019 task. In this paper a description of some aspects of this task is provided, including its main characteristics, a description of the collection, the ground truth dataset, evaluation metrics and the requirements for participants' run submissions.
```

#### Document D-C9ADFA

**Title:** Investigating Memorability of Dynamic Media

**Abstract:**

```text
The Predicting Media Memorability task in MediaEval'20 has some challenging aspects compared to previous years. In this paper we identify the high-dynamic content in videos and dataset of limited size as the core challenges for the task, we propose directions to overcome some of these challenges and we present our initial result in these directions.
```

#### Document D-132F4C

**Title:** Leveraging Audio Gestalt to Predict Media Memorability

**Abstract:**

```text
Memorability determines what evanesces into emptiness, and what worms its way into the deepest furrows of our minds. It is the key to curating more meaningful media content as we wade through daily digital torrents. The Predicting Media Memorability task in MediaEval 2020 aims to address the question of media memorability by setting the task of automatically predicting video memorability. Our approach is a multimodal deep learning-based late fusion that combines visual, semantic, and auditory features. We used audio gestalt to estimate the influence of the audio modality on overall video memorability, and accordingly inform which combination of features would best predict a given video's memorability scores.
```

## Questions

### Q-6C0C74

```text
  
How does the presence and variability of emotional cues in audio narration affect the memorability of educational videos compared to non-narrated, action-rich videos?
```

### Q-75BF83

```text
  
Can the integration of quality attention mechanisms with perceptual priors, as demonstrated in QAGAN and GPP-LLIE, lead to a more robust and user-adaptive unpaired image enhancement framework that simultaneously preserves content fidelity and enhances aesthetic quality without requiring paired training data?  
```

### Q-C4C5C7

```text
  
How can the integration of audio gestalt features with visual and semantic cues improve the prediction of short-term video memorability compared to using visual and semantic features alone?
```

### Q-8BB9ED

```text
  
How can generative adversarial networks (GANs) be adapted to enhance the perceptual realism of low-light images in a way that aligns with user preferences for aesthetic qualities such as color balance, contrast, and natural lighting, without requiring explicit paired training data or expert annotations?
```

## Assigned question–collection associations

Use these neutral IDs to locate the question and source collection in the sections above.

- Question Q-C4C5C7 — Collection C-877C7D
- Question Q-6C0C74 — Collection C-877C7D
- Question Q-75BF83 — Collection C-877C7D
- Question Q-75BF83 — Collection C-E5ACD7
- Question Q-C4C5C7 — Collection C-E5ACD7
- Question Q-8BB9ED — Collection C-E5ACD7
