# SG-Net paraphrase pilot validation

**Status:** PILOT ONLY — NOT APPROVED FOR BULK SCORING  
**Focal paper:** `2012.13915v2`  
**Model:** `qwen3:8b`

## Important generation distinction

The candidate title and candidate abstract were generated in separate runs using different prompts. They are recorded together for review, **not as a finalized paired paraphrase**.

## Original title

SG-Net: Syntax Guided Transformer for Language Representation

## Candidate title

Syntax-Guided Transformer Architecture for Enhanced Language Representation

## Original abstract

Understanding human language is one of the key themes of artificial intelligence. For language representation, the capacity of effectively modeling the linguistic knowledge from the detail-riddled and lengthy texts and getting rid of the noises is essential to improve its performance. Traditional attentive models attend to all words without explicit constraint, which results in inaccurate concentration on some dispensable words. In this work, we propose using syntax to guide the text modeling by incorporating explicit syntactic constraints into attention mechanisms for better linguistically motivated word representations. In detail, for self-attention network (SAN) sponsored Transformer-based encoder, we introduce syntactic dependency of interest (SDOI) design into the SAN to form an SDOI-SAN with syntax-guided self-attention. Syntax-guided network (SG-Net) is then composed of this extra SDOI-SAN and the SAN from the original Transformer encoder through a dual contextual architecture for better linguistics inspired representation. The proposed SG-Net is applied to typical Transformer encoders. Extensive experiments on popular benchmark tasks, including machine reading comprehension, natural language inference, and neural machine translation show the effectiveness of the proposed SG-Net design.

## Candidate abstract

Understanding human language remains a central focus in artificial intelligence. Effective modeling of linguistic knowledge from detailed and lengthy texts, while eliminating noise, is crucial for enhancing performance. Traditional attention mechanisms lack explicit constraints, leading to focus on irrelevant words. This study introduces a method that leverages syntax to guide text modeling by integrating explicit syntactic constraints into attention mechanisms, aiming to produce more linguistically informed word representations. Specifically, for the Transformer-based encoder utilizing a self-attention network (SAN), we integrate the syntactic dependency of interest (SDOI) design into the SAN to create an SDOI-SAN that employs syntax-guided self-attention. The syntax-guided network (SG-Net) combines this modified SDOI-SAN with the original SAN from the Transformer encoder via a dual contextual architecture to achieve linguistics-inspired representations. The proposed SG-Net is implemented within standard Transformer encoders. Extensive experiments on widely used benchmark tasks—such as machine reading comprehension, natural language inference, and neural machine translation—demonstrate the effectiveness of the proposed SG-Net design.

## Claim-preservation review

### C1

**Original claim:** The authors propose a method called SG-Net that incorporates syntax-guided self-attention into a Transformer encoder to improve language representation.

**Assessment:** Plausibly preserved, but not independently verified.

**Notes:** The candidate describes syntax-guided self-attention and linguistically informed representations; exact phrase 'language representation' is absent.

### C2

**Original claim:** SG-Net uses a dual contextual architecture composed of an SDOI-SAN and the original SAN from the Transformer encoder.

**Assessment:** Key components retained; wording requires review.

**Notes:** Both SDOI-SAN and the original SAN are mentioned in the dual contextual architecture.

### C3

**Original claim:** The proposed SG-Net design is applied to typical Transformer encoders.

**Assessment:** Potential scope change.

**Notes:** 'Implemented within standard Transformer encoders' is not guaranteed to be equivalent to 'applied to typical Transformer encoders'.

### C4

**Original claim:** Extensive experiments on benchmark tasks demonstrate the effectiveness of SG-Net.

**Assessment:** Broad conclusion retained; wording requires review.

**Notes:** The candidate mentions extensive experiments, all three task names, and effectiveness.

## Known limitations

- The wording changes noted in the JSON record require review.
- Lexical overlap does not prove semantic equivalence.
- This pilot is not evidence that the procedure works reliably for all 300 focal papers.
- Do not score this candidate as the final paraphrased-copy condition yet.

## Data integrity

The original manipulation plan, synthetic-paper records, and scoring results were not modified by this command.
