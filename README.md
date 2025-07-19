# ICSE2026_Submission

This is an anonymous artifact repository used for ICSE 2026

## Title: Modeling Like Peeling an Onion: Layerwise Analysis-Driven Automatic Behavioral Model Generation
<div align="center">
  <img src="Figures/motivation.png" alt="Motivation" />
  <p><em>Figure 1. Motivation</em></p>
</div>

### Abstract
As software complexity skyrockets and requirements evolve at breakneck speed, traditional human-centric behavioral modeling can no longer keep pace in terms of efficiency, accuracy, and scalability. While existing automated approaches can produce models, they still struggle with deep semantic understanding of textual requirements or with reasoning about intricate system logic, especially nested relationships. Inspired by the way seasoned analysts “peel back” layers of a problem, we propose **AutoBM**, an LLM-based framework that incrementally extracts behavioral nodes, dissects their hierarchical relations, and synthesizes them into executable, interpretable UML activity diagrams. Comprehensive evaluations on four open‑source datasets and two real‑world industrial systems show that AutoBM comprehensively outperforms state-of-the-art baselines in accuracy, completeness, and syntactic compliance: _F₁_ scores for behavioral node-extraction improve by up to 71.1 %, relation-extraction _F₁_ by 52.4 % relatively, and syntactic pass rates remain above 96.7 %. The framework also exhibits strong robustness to input perturbations, confirming its cross-domain generalizability. This paper is the first to tightly fuse human-inspired strategies with LLMs in behavior modeling, yielding an intelligent infrastructure that exhibits human-level logical understanding and generalization. By closing the modeling-skills gap, AutoBM delivers a next-generation, low-cost, and explainable solution for requirements engineering and AI-native software development.

### Dataset
We conduct experiments on six datasets, with their statistics summarized as follows:
- **Functional Scenario Descriptions (FSD)** comprises 116 natural language descriptions from embedded systems, encompassing deeply nested functional behaviors such as device control, data processing, and fault handling.
- **Real Automotive Case (RAC)** contains 20 requirement scenarios from the automotive domain, representing typical control logic and communication processes.
- **PURE Dataset (PURE)** [\[pure\]](https://zenodo.org/records/1414117) consists of 79 documents across multiple application domains and formats.
- **Business Process Dataset (BP)** [\[bp\]](https://github.com/lwx142857/bussiness-process) includes 30 examples of business software requirements, covering a range of operational scenarios.
- **User Stories Dataset (US)** [\[userstory\]](https://zenodo.org/records/13880060) comprises 22 sets of user stories collected from various open-source projects, reflecting typical agile requirements.
- **LM Challenges (LMC)** [\[lmc\]](https://github.com/hbourbouh/lm_challenges) features 10 requirements documents from the cyber-physical systems domain.

### Approach
<div align="center">
  <img src="Figures/overview.png" alt="Overview" />
  <p><em>Figure 2. Overview</em></p>
</div>

<div align="center">
  <img src="Figures/identify.png" width="50%" alt="Identify step prompt" />
  <p><em>Figure 3. Identify Step Prompt</em></p>
</div>

<div align="center">
  <img src="Figures/decompose.png" width="50%" alt="Decompose step prompt" />
  <p><em>Figure 4. Extract Step Prompt</em></p>
</div>

<div align="center">
  <img src="Figures/integrate.png" width="50%" alt="Integrate step prompt" />
  <p><em>Figure 5. Integrate Step Prompt</em></p>
</div>

### Requirements
- PlantUML: plantuml-1.2025.4.jar
- StanfordNLP: CoreNLP 4.5.10
- FastCoref: fastcoref 2.1.6
- en_core_web_sm-3.8.0.tar

### Experimental Results

#### Table I. Average Performance Scores on Behavioral Node and Relation Extraction for Each Method

| Dataset | Metric     | Zero-shot | Few-shot | CoT    | **AutoBM** | Zero-shot | Few-shot | CoT    | **AutoBM** |
|:-------:|:-----------|:---------:|:--------:|:------:|:----------:|:---------:|:--------:|:------:|:----------:|
| **FSD** | **Precision** | 0.6821    | 0.7540   | 0.7913 | **0.8654** | 0.6606    | 0.6544   | 0.5651 | **0.7111** |
|         | **Recall**    | 0.5932    | 0.7107   | 0.7481 | **0.8322** | 0.3711    | 0.4124   | 0.4420 | **0.5296** |
|         | **F₁**         | 0.6348    | 0.7318   | 0.7692 | **0.8484** | 0.4752    | 0.5059   | 0.4960 | **0.6071** |
| **RAC** | **Precision** | 0.6939    | 0.7500   | 0.6877 | **0.6905** | 0.4419    | 0.4713   | 0.3777 | **0.5008** |
|         | **Recall**    | 0.7858    | 0.7812   | 0.7904 | **0.8320** | 0.3953    | 0.3853   | 0.3568 | **0.5142** |
|         | **F₁**         | 0.7370    | 0.7653   | 0.7355 | **0.7547** | 0.4173    | 0.4240   | 0.3669 | **0.5074** |
| **PURE**| **Precision** | 0.7430    | 0.7925   | 0.8147 | **0.8891** | 0.5095    | 0.5910   | 0.4568 | **0.6341** |
|         | **Recall**    | 0.6654    | 0.7586   | 0.7852 | **0.8597** | 0.4524    | 0.5107   | 0.5031 | **0.5570** |
|         | **F₁**         | 0.7023    | 0.7752   | 0.7998 | **0.8742** | 0.4793    | 0.5479   | 0.4788 | **0.5931** |
| **BP**  | **Precision** | 0.6538    | 0.6717   | 0.5341 | **0.6515** | 0.4043    | 0.4586   | 0.3156 | **0.4523** |
|         | **Recall**    | 0.3479    | 0.4008   | 0.4536 | **0.5180** | 0.2129    | 0.2717   | 0.2661 | **0.3655** |
|         | **F₁**         | 0.4542    | 0.5020   | 0.4906 | **0.5772** | 0.2789    | 0.3412   | 0.2888 | **0.4043** |
| **US**  | **Precision** | 0.2210    | 0.2541   | 0.1214 | **0.5265** | 0.2914    | 0.3186   | 0.1629 | **0.5969** |
|         | **Recall**    | 0.6498    | 0.6756   | 0.6327 | **0.7895** | 0.9700    | 0.9543   | 0.9180 | **0.9329** |
|         | **F₁**         | 0.3299    | 0.3693   | 0.2037 | **0.6317** | 0.4482    | 0.4777   | 0.2802 | **0.7280** |
| **LMC** | **Precision** | 0.5095    | 0.5910   | 0.4568 | **0.6341** | 0.8093    | 0.8574   | 0.7474 | **0.8598** |
|         | **Recall**    | 0.4524    | 0.5107   | 0.5031 | **0.5570** | 0.6830    | 0.7108   | 0.8048 | **0.7293** |
|         | **F₁**         | 0.4793    | 0.5479   | 0.4788 | **0.5931** | 0.7408    | 0.7773   | 0.7750 | **0.7892** |

#### Table II. Average Pass Rate for Each Method

| Dataset | Zero-shot | Few-shot | CoT    | **AutoBM** |
|:-------:|:---------:|:--------:|:------:|:----------:|
| FSD     |   0.8261  |  0.9429  | 0.9321 | **0.9679** |
| RAC     |   0.9672  |  0.9545  | 0.9560 | **0.9708** |
| PURE    |   0.9464  |  0.9757  | 0.9479 | **0.9764** |
| BP      |   0.9730  |  0.8964  | 0.9864 | **0.9667** |
| US      |   0.9814  |  0.9506  | 0.9257 | **0.9914** |
| LMC     |   0.9879  |  0.9750  | 0.9743 | **0.9936** |

#### Table III. The Performance Score of AutoBM with Different Base Models

| LLM             | N‑Precision | N‑Recall | N‑F₁  | R‑Precision | R‑Recall | R‑F₁  | Pass Rate |
|:---------------:|:-----------:|:--------:|:-----:|:-----------:|:--------:|:-----:|:---------:|
| `gpt-4`         | 0.6584      | 0.8136   | 0.7278| 0.4815      | 0.5226   | 0.5012| 0.9172    |
| `gpt-4o`        | **0.6961**  | 0.8259   |0.7555 | **0.5319**  | 0.5310   |0.5314 | 0.8826    |
| `gpt-4.1`       | 0.6534      |**0.9091**|**0.7603**|0.5101    |**0.5896**|**0.5470**|**0.9587**|
| `qwen3-8b`      | 0.6007      | 0.7812   | 0.6792| 0.3467      | 0.4198   | 0.3797| 0.8574    |
| `qwen3-14b`     | 0.4075      | 0.7704   | 0.5330| 0.3186      | 0.4160   | 0.3608| **0.9482**|
| `qwen3-32b`     |**0.6204**   | 0.7581   |**0.6824**|**0.4172**|**0.4515**|**0.4337**|0.9206   |
| `glm-4-flash`   | 0.5719      | 0.7535   | 0.6503| 0.3922      | 0.4389   | 0.4142| 0.8734    |
| `glm-4-air`     |**0.6943**   | 0.7735   |**0.7318**|**0.4771**|0.4020   | 0.4364|**0.9548**|
| `glm-4-plus`    | 0.6181      |**0.8105**| 0.7013| 0.4105      |**0.4841**|**0.4443**|0.9392   |

<div align="center">
  <img src="Figures/llm.png" alt="Different Base Models" />
  <p><em>Figure 6. Different Base Models</em></p>
</div>

#### Table IV. The Performance Scores of AutoBM with Different Example Seeds

| Seed   | N‑Precision | N‑Recall | N‑F₁  |         | R‑Precision | R‑Recall | R‑F₁  |         | Pass Rate |        |
|:------:|:-----------:|:--------:|:-----:|:-------:|:-----------:|:--------:|:-----:|:-------:|:---------:|:------:|
| Seed A | 0.6905      | 0.8320   | 0.7547| --      | 0.5008      | 0.5142   | 0.5074| --      | 0.9708    | --     |
| Seed B | 0.6840      | 0.8255   | 0.7492| _0.73 %↓_| 0.4821      | 0.5010   | 0.4898| _3.47 %↓_| 0.9676    | _0.33 %↓_ |
| Seed C | 0.6702      | 0.8123   | 0.7350| _2.61 %↓_| 0.4955      | 0.5108   | 0.5035| _0.77 %↓_| 0.9690    | _0.18 %↓_ |

#### Table V. The Results of Ablation Study

| Configuration            | N‑Precision | N‑Recall | N‑F₁  |         | R‑Precision | R‑Recall | R‑F₁  |         | Pass Rate |        |
|:------------------------:|:-----------:|:--------:|:-----:|:-------:|:-----------:|:--------:|:-----:|:-------:|:---------:|:------:|
| **AutoBM**               | 0.6905      | 0.8320   | 0.7547| --      | 0.5008      | 0.5142   | 0.5074| --      | 0.9708    | --     |
| _w/o Identifier_         | 0.6356      | 0.7257   | 0.6777| _10.20 %↓_| 0.4178      | 0.4003   | 0.4089| _19.41 %↓_| 0.9614    | _0.97 %↓_ |
| _w/o Extractor_          | 0.6232      | 0.7288   | 0.6719| _10.97 %↓_| 0.3919      | 0.3886   | 0.3902| _23.10 %↓_| 0.9592    | _1.19 %↓_ |
| _w/o Constructor_        | 0.6019      | 0.6687   | 0.6336| _16.05 %↓_| 0.3519      | 0.3283   | 0.3397| _33.06 %↓_| 0.9316    | _4.04 %↓_ |
