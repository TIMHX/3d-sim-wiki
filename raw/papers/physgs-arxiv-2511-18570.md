---
source_url: https://arxiv.org/abs/2511.18570
ingested: 2026-08-31
sha256: 72cb0fd6f02cf78607c4e60bf1d65ac87d6fdc0c67bafa16c8bb6735256f05c0
---

##### Report GitHub Issue

Content selection saved. Describe the issue below:

![](/static/base/1.0.1/images/icons/smileybones-small.svg)
![arXiv logo](/static/base/1.0.1/images/arxiv-logo-primary-light.svg)

# PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation

###### Abstract

Understanding physical properties such as friction, stiffness, hardness, and material composition is essential for enabling robots to interact safely and effectively with their surroundings. However, existing 3D reconstruction methods focus on geometry and appearance and cannot infer these underlying physical properties. We present PhysGS, a Bayesian-inferred extension of 3D Gaussian Splatting that estimates dense, per-point physical properties from visual cues and vision–language priors. We formulate property estimation as Bayesian inference over Gaussian splats, where material and property beliefs are iteratively refined as new observations arrive. PhysGS also models aleatoric and epistemic uncertainties, enabling uncertainty-aware object and scene interpretation. Across object-scale (ABO-500), indoor, and outdoor real-world datasets, PhysGS improves accuracy of the mass estimation by up to 22.8%, reduces Shore hardness error by up to 61.2%, and lowers kinetic friction error by up to 18.1% compared to deterministic baselines. Our results demonstrate that PhysGS unifies 3D reconstruction, uncertainty modeling, and physical reasoning in a single, spatially continuous framework for dense physical property estimation.
Additional results are available at [https://samchopra2003.github.io/physgs](https://samchopra2003.github.io/physgs/).

![Refer to caption](2511.18570v1/overview_enhanced.png)

## 1 Introduction

Understanding the physical properties of real-world environments is critical for enabling robots to interact safely and effectively with their surroundings [[63](#bib.bib6), [36](#bib.bib32), [11](#bib.bib4), [5](#bib.bib43)]. This capability is essential across a wide range of domains such as navigation [[56](#bib.bib12), [34](#bib.bib31)], manipulation [[31](#bib.bib29), [1](#bib.bib28)], and surgical robotics [[31](#bib.bib29), [62](#bib.bib27), [39](#bib.bib26)], and is required in both complex indoor [[63](#bib.bib6), [60](#bib.bib7), [40](#bib.bib13)] and outdoor [[34](#bib.bib31), [11](#bib.bib4), [48](#bib.bib30)] environments. In particular, accurately estimating physical attributes such as friction [[34](#bib.bib31), [11](#bib.bib4)], elasticity [[56](#bib.bib12)], hardness [[5](#bib.bib43)], and density [[60](#bib.bib7)] is essential for safe and robust robot interaction with diverse and unstructured real-world scenarios.

In general, estimating physical properties from visual sensors remains a challenging task due to two primary reasons [[11](#bib.bib4), [60](#bib.bib7)]. First, visually similar but physically distinct regions (e.g., mud vs. asphalt, or grass vs. rock) are often difficult to distinguish, leading to brittle planning and control in complex scenes [[11](#bib.bib4), [10](#bib.bib5)]. While conventional 3D mapping approaches, such as occupancy grids [[8](#bib.bib1)], signed distance fields [[38](#bib.bib2)], or implicit neural representations [[37](#bib.bib3), [26](#bib.bib23)], can provide rich geometric detail, they primarily focus on recovering object shape, and typically fail to encode physical properties or material categories.
Second, although recent work has made progress in estimating physical properties in indoor environments [[63](#bib.bib6), [60](#bib.bib7), [40](#bib.bib13)], outdoor scenes remain underexplored. Existing methods often focus on one or two specific physical properties of outdoor objects or terrains, such as friction [[34](#bib.bib31), [11](#bib.bib4), [5](#bib.bib43)], pliability [[56](#bib.bib12)], or stiffness [[5](#bib.bib43)], and are not easily generalizable to a broader set of physical attributes.

Recent advances in 3D vision and semantic perception have increasingly focused on linking visual appearance to underlying physical attributes, enabling models to distinguish between rigid, deformable, slippery, and compliant surfaces [[63](#bib.bib6), [60](#bib.bib7), [11](#bib.bib4), [10](#bib.bib5), [5](#bib.bib43)]. In parallel, vision-language models (VLMs) have demonstrated the ability to capture latent physical properties, such as friction and elasticity, with multimodal inputs [[63](#bib.bib6)]. These models can qualitatively reason about forces, materials, and object dynamics from language and imagery [[55](#bib.bib10), [64](#bib.bib11), [40](#bib.bib13), [59](#bib.bib14), [49](#bib.bib15)], highlighting their potential as semantic priors for physical inference.

However, a core challenge in estimating physical properties from visual sensors
is managing the uncertainty inherent in both sensing and inference. Visual and depth observations are often degraded by sensor noise, lighting variation, occlusion, and calibration drift [[52](#bib.bib17), [53](#bib.bib16), [54](#bib.bib18), [6](#bib.bib19)]. This type of uncertainty, known as aleatoric uncertainty, captures measurement noise and perceptual ambiguity [[25](#bib.bib20), [3](#bib.bib9)]. Simultaneously, learning-based models trained on limited or domain-specific datasets frequently struggle to generalize to novel textures, materials, and environmental conditions [[25](#bib.bib20), [24](#bib.bib21), [18](#bib.bib22)]. This is referred to as epistemic uncertainty, which reflects the model’s incomplete or imperfect knowledge of the world, often due to insufficient or biased training data [[25](#bib.bib20), [3](#bib.bib9)].

Main Contributions:
We propose a 3D physical property estimation framework that integrates Bayesian inference into the Gaussian Splatting optimization process, treating each Gaussian primitive as a probabilistic entity whose properties are updated via posterior refinement. This enables PhysGS to estimate both point-level physical properties (e.g., friction, hardness, stiffness, density) and object-level quantities (e.g., total mass), while producing calibrated aleatoric and epistemic uncertainty.
Our novel contributions include:

Bayesian-Inferred Gaussian Splatting. We embed Bayesian updates within the Gaussian Splatting pipeline, allowing each Gaussian’s physical property values to be updated through confidence-weighted posterior refinement from observations.

Unified multi-property estimation across scales. A single Bayesian formulation supports diverse physical properties, including friction, hardness, stiffness, density, and mass, at both the point level and the object level, enabling fine-grained property mapping and global aggregation within the same framework.

Generality across environments and object types. PhysGS is broadly applicable to a wide range of indoor and outdoor scenes and operates on both rigid and deformable objects, including vegetation, soil, and everyday household materials, enabling consistent physical property estimation across heterogeneous real-world settings.

Across all datasets, including ABO-500, and a real-world friction–hardness dataset, PhysGS achieves strong gains over prior methods such as NeRF2Physics, CLIP-based recognition, and direct VLM regression. We observe improvements of up to 61.2% in Shore hardness error, 18.1% in kinetic friction error, and 22.8% in mass-density error.

## 2 Related Work

### 2.1 Visual Property Fields

A major line of work estimates physical properties by associating scene objects with open-vocabulary physical semantics, querying where specific physical property appear in observed spaces. LERF grounds CLIP embeddings [[45](#bib.bib37)] within NeRF, distilling multi-scale language features into a dense, queryable 3D field that produces 3D relevancy maps for text prompts [[27](#bib.bib24)]. Closely related open-vocabulary 3D mapping approaches propagate physical–semantic features into 3D reconstructions for zero-shot recognition and retrieval [[43](#bib.bib25), [22](#bib.bib33)].

With the rise of 3D Gaussian Splatting (3DGS)[[26](#bib.bib23)], several methods directly inject language or semantic features into Gaussian primitives, yielding fast, explicit, and queryable 3D fields.
LangSplat [[44](#bib.bib34)] distills 2D CLIP features into a 3D language field over Gaussians for open-vocabulary search.
Related efforts [[16](#bib.bib35), [21](#bib.bib36)] assign semantic Gaussians for open-vocabulary 3D understanding, showing that explicit Gaussian fields are well-suited for encoding and rendering high-dimensional properties beyond color.

Based on visual–semantic cues, recent work has further incorporated language-context features to enhance physical property estimation [[63](#bib.bib6), [60](#bib.bib7)]. NeRF2Physics[[63](#bib.bib6)] constructs a language-embedded 3D feature space and performs zero-shot kernel regression to estimate per-point physical properties, while GaussianProperty[[60](#bib.bib7)] extends this idea to 3D Gaussians.

### 2.2 Uncertainty-Aware and Probabilistic Scene Understanding

In vision and robotics, uncertainty is typically decomposed into aleatoric (data or sensor noise) and epistemic (model or knowledge) components. This formulation has become standard for loss design, model calibration, and risk-sensitive decision making in perception systems [[25](#bib.bib20), [3](#bib.bib9), [4](#bib.bib39)]. Prior work formalizes these notions for vision-based tasks and demonstrates how to jointly learn uncertainty with outputs such as depth or segmentation, or to approximate Bayesian inference via dropout or ensembles, thereby improving robustness and out-of-distribution behavior [[24](#bib.bib21), [14](#bib.bib40), [32](#bib.bib41)].

Estimating the physical properties of real-world environments from sensors inherently involves uncertainty. Several approaches introduce probabilistic maps, tail-risk measures, and confidence-aware policies to quantify and mitigate this uncertainty [[5](#bib.bib43), [12](#bib.bib42), [13](#bib.bib44), [41](#bib.bib45), [9](#bib.bib46)]. STEP [[12](#bib.bib42)] models traversability as a stochastic variable and plans using a CVaR-based risk formulation, validated across diverse field environments and the DARPA SubT Challenge. Evidential and Bayesian formulations extend this concept by outputting full distributions rather than point estimates, enabling online belief updates from new observations [[3](#bib.bib9), [4](#bib.bib39), [11](#bib.bib4), [10](#bib.bib5)]. EVORA [[3](#bib.bib9)] learns evidential traction distributions, explicitly separating aleatoric and epistemic components to assess motion risk, while Ewen et al. [[11](#bib.bib4), [10](#bib.bib5)] maintain joint beliefs over semantics and continuous properties to predict physical property maps (e.g. friction).

Beyond 2D perception, uncertainty has been integrated into NeRF and 3D Gaussian Splatting (3DGS) frameworks to quantify ambiguity arising from sparse views, occlusions, and under-constrained geometry [[33](#bib.bib8), [47](#bib.bib51)]. Recent works estimate spatial uncertainty post hoc for pre-trained NeRFs [[15](#bib.bib47), [33](#bib.bib8)], propose probabilistic NeRFs [[19](#bib.bib48)], or directly model uncertainty in 3DGS [[28](#bib.bib50)] via variational or evidential objectives, including dynamic and 4D settings [[29](#bib.bib49)]. Complementary efforts have explored uncertainty-aware on variational Gaussian splatting and SLAM pipelines that propagate uncertainty in pose and structure, demonstrating that per-Gaussian uncertainty can substantially enhance mapping robustness and downstream reasoning [[47](#bib.bib51), [20](#bib.bib52), [46](#bib.bib53)].

## 3 Proposed Approach

In this section, we outline our Bayesian framework for dense physical property estimation. We begin with a Dirichlet–Categorical model for fusing confidence-weighted material labels across views (Sec. [3.1](#S3.SS1 "3.1 Preliminaries ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation"), [3.2](#S3.SS2 "3.2 Bayesian Inference for Material Property Estimation ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation")), then extend it to continuous properties using a Normal–Inverse–Gamma prior to obtain calibrated aleatoric and epistemic uncertainty (Sec. [3.3](#S3.SS3 "3.3 Uncertainty-Aware Property Fields ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation")). We then describe how these Bayesian updates integrate with 3D Gaussian Splatting, segmentation, and VLM prompting to produce per-point property fields and object-level estimates (Sec. [3.4](#S3.SS4 "3.4 Learning Semantics and Physical Properties ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation")).

![Refer to caption](2511.18570v1/architecture.png)

### 3.1 Preliminaries

#### Dirichlet–Categorical formulation.

We model discrete material labels produced by the VLM using a Categorical distribution and
place a Dirichlet prior over its parameters. The Dirichlet distribution is the conjugate prior
to the Categorical likelihood, enabling closed-form Bayesian updates as new observations are
incorporated across views.

The Categorical distribution parameterized by 𝜽∈[0,1]K\boldsymbol{\theta}\in[0,1]^{K} represents the probability that an observation belongs to class ii:

|  |  |  |  |
| --- | --- | --- | --- |
|  | f⁡(z=i∣𝜽)=θi.f(z=i\mid\boldsymbol{\theta})=\theta\_{i}. |  | (1) |

The Dirichlet distribution defines a continuous KK-variate prior over 𝜽\boldsymbol{\theta}, parameterized by 𝜶∈ℝ>0K\boldsymbol{\alpha}\in\mathbb{R}\_{>0}^{K}, as

|  |  |  |  |
| --- | --- | --- | --- |
|  | f⁡(𝜽∣𝜶)=Γ⁡(∑k=1Kαk)∏k=1KΓ⁡(αk)​∏k=1Kθkαk−1,f(\boldsymbol{\theta}\mid\boldsymbol{\alpha})=\frac{\Gamma(\sum\_{k=1}^{K}\alpha\_{k})}{\prod\_{k=1}^{K}\Gamma(\alpha\_{k})}\prod\_{k=1}^{K}\theta\_{k}^{\alpha\_{k}-1}, |  | (2) |

where Γ⁡(⋅)\Gamma(\cdot) is the Gamma function.

Given a set of nn observed material labels
𝒵={z1,…,zn}\mathcal{Z}=\{z\_{1},\dots,z\_{n}\} drawn from a Categorical distribution,
the posterior predictive probability that a new observation belongs to material class ii is

|  |  |  |  |
| --- | --- | --- | --- |
|  | f⁡(z=i∣𝒵,𝜶)=∫𝜽f⁡(z=i∣𝜽)​f​(𝜽∣𝒵,𝜶)​𝑑𝜽.f(z=i\mid\mathcal{Z},\boldsymbol{\alpha})=\int\_{\boldsymbol{\theta}}f(z=i\mid\boldsymbol{\theta})\,f(\boldsymbol{\theta}\mid\mathcal{Z},\boldsymbol{\alpha})\,d\boldsymbol{\theta}. |  | (3) |

Using conjugacy of the Dirichlet prior and Categorical likelihood,
the integral simplifies to the closed-form expression

|  |  |  |  |
| --- | --- | --- | --- |
|  | f⁡(z=i∣Z,𝜶)=α~i∑j=1Kα~j,f(z=i\mid Z,\boldsymbol{\alpha})=\frac{\tilde{\alpha}\_{i}}{\sum\_{j=1}^{K}\tilde{\alpha}\_{j}}, |  | (4) |

where the posterior parameters are recursively updated as

|  |  |  |  |
| --- | --- | --- | --- |
|  | α~i←αi(0)+∑m:cm=iλpm,\tilde{\alpha}\_{i}\leftarrow\alpha\_{i}(0)+\sum\_{m:\,c\_{m}=i}\lambda\,p\_{m}, |  | (5) |

with λ\lambda controlling the evidence strength contributed by each observation and pmp\_{m}
denoting the confidence provided by the VLM for the mm-th prediction.

### 3.2 Bayesian Inference for Material Property Estimation

We introduce our hierarchical Bayesian framework for estimating material-specific physical properties from confidence-weighted observations. Building on the Dirichlet–Categorical model of [[10](#bib.bib5)], we extend it with a continuous posterior to jointly infer material class and properties such as friction, density, and hardness.

Continuous property estimation.
While the Dirichlet–Categorical formulation governs the discrete class probabilities,
we also require an estimate of the continuous physical property ψ\psi associated with each material.
For each material class ii, we maintain confidence-weighted accumulators that enable
incremental computation of the first and second moments using a running mean and variance formulation
proposed by  [[57](#bib.bib54)] and generalized by  [[42](#bib.bib55)]:

|  |  |  |  |
| --- | --- | --- | --- |
|  | Wi=∑mpm,Si=∑mpm​ψm,Qi=∑mpm​ψm2,W\_{i}=\sum\_{m}p\_{m},\qquad S\_{i}=\sum\_{m}p\_{m}\,\psi\_{m},\qquad Q\_{i}=\sum\_{m}p\_{m}\,\psi\_{m}^{2}, |  | (6) |

representing the total weight, first moment, and second moment, respectively.
These accumulators allow efficient online updates without requiring access to past observations,
which is particularly beneficial in streaming or on-the-fly reconstruction settings.

The posterior mean and variance for material ii are then estimated as

|  |  |  |  |
| --- | --- | --- | --- |
|  | μi=SiWi,σi2=max⁡(QiWi−μi2,ϵ),\mu\_{i}=\frac{S\_{i}}{W\_{i}},\qquad\sigma\_{i}^{2}=\max\!\left(\frac{Q\_{i}}{W\_{i}}-\mu\_{i}^{2},\,\epsilon\right), |  | (7) |

yielding a Gaussian posterior

|  |  |  |  |
| --- | --- | --- | --- |
|  | p⁡(ψi∣Z)=𝒩⁡(μi,σi2),p(\psi\_{i}\mid Z)=\mathcal{N}(\mu\_{i},\sigma\_{i}^{2}), |  | (8) |

which represents the system’s belief over the continuous physical property for material ii given all confidence-weighted evidence ZZ. This formulation integrates naturally with the Dirichlet update by providing confidence-weighted, incremental, and uncertainty-aware refinement as new observations become available.

Hierarchical posterior.
The resulting model is hierarchical in nature, jointly estimating the discrete material identity zz and continuous physical property ψ\psi:

|  |  |  |  |
| --- | --- | --- | --- |
|  | p(z,ψ∣Z,𝜶)=p(ψ∣z,Z)p(z∣Z,𝜶),p(z,\psi\mid Z,\boldsymbol{\alpha})=p(\psi\mid z,Z)\,p(z\mid Z,\boldsymbol{\alpha}), |  | (9) |

where p⁡(z∣Z,𝜶)p(z\mid Z,\boldsymbol{\alpha}) is the Dirichlet–Categorical posterior
and p⁡(ψ∣z,Z)p(\psi\mid z,Z) is the Gaussian posterior.
Applying the Law of Total Probability as in [[10](#bib.bib5)],
the overall predictive distribution over physical properties is

|  |  |  |  |
| --- | --- | --- | --- |
|  | f⁡(ψ∣Z,𝜶)=∑i=1Kf⁡(ψ∣z=i)​f​(z=i∣Z,𝜶).f(\psi\mid Z,\boldsymbol{\alpha})=\sum\_{i=1}^{K}f(\psi\mid z=i)\,f(z=i\mid Z,\boldsymbol{\alpha}). |  | (10) |

Substituting Eq. ([8](#S3.E8 "Equation 8 ‣ 3.2 Bayesian Inference for Material Property Estimation ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation")) into Eq. ([10](#S3.E10 "Equation 10 ‣ 3.2 Bayesian Inference for Material Property Estimation ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation"))
gives a closed-form multimodal Gaussian mixture for the predicted material properties:

|  |  |  |  |
| --- | --- | --- | --- |
|  | f⁡(ψ∣Z,𝜶)=∑i=1Kα~i∑j=1Kα~j​𝒩​(μi,σi2).f(\psi\mid Z,\boldsymbol{\alpha})=\sum\_{i=1}^{K}\frac{\tilde{\alpha}\_{i}}{\sum\_{j=1}^{K}\tilde{\alpha}\_{j}}\,\mathcal{N}(\mu\_{i},\sigma\_{i}^{2}). |  | (11) |

This mixture formulation expresses the full posterior as a
weighted sum of unimodal Gaussian components, where each mode corresponds to a material class
and is weighted by its recursively updated class likelihood from the Dirichlet posterior.

### 3.3 Uncertainty-Aware Property Fields

Uncertainty modeling via the Normal–Inverse–Gamma prior.
For each material ii, the joint prior over the mean μi\mu\_{i}
and variance σi2\sigma\_{i}^{2} of the property ψ\psi is given by

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
|  | p(μi,σi2∣τi,κi,αi,βi)=\displaystyle p(\mu\_{i},\sigma\_{i}^{2}\mid\tau\_{i},\kappa\_{i},\alpha\_{i},\beta\_{i})\;= | 𝒩(μi|τi,σi2κi)\displaystyle\mathcal{N}\!\left(\mu\_{i}\,\middle|\,\tau\_{i},\tfrac{\sigma\_{i}^{2}}{\kappa\_{i}}\right) |  | (12) |
|  |  | Inv-Gamma(σi2|αi,βi),\displaystyle\mathrm{Inv\text{-}Gamma}\!\left(\sigma\_{i}^{2}\,\middle|\,\alpha\_{i},\beta\_{i}\right), |  |

where
τi\tau\_{i} denotes the prior mean,
κi\kappa\_{i} controls the precision on μi\mu\_{i} (i.e., the strength of accumulated evidence),
and (αi,βi)(\alpha\_{i},\beta\_{i}) are the shape and scale parameters governing the uncertainty in σi2\sigma\_{i}^{2}.

Predictive Uncertainty update.
Given a new observation ψm\psi\_{m} associated with material class ii
and its confidence pmp\_{m}, the posterior parameters
(τ~i,κ~i,α~i,β~i)(\tilde{\tau}\_{i},\tilde{\kappa}\_{i},\tilde{\alpha}\_{i},\tilde{\beta}\_{i})
can be updated in closed-form, allowing sequential fusion of confidence-weighted evidence without storing past data.
This conjugate formulation provides closed-form expressions for the predictive
mean and variance of the property ψi\psi\_{i}.

The total predictive uncertainty decomposes into two components:

|  |  |  |  |
| --- | --- | --- | --- |
|  | Var⁡[ψi]=𝔼⁡[σi2]⏟aleatoric+Var⁡[μi]⏟epistemic.\mathrm{Var}[\psi\_{i}]=\underbrace{\mathbb{E}[\sigma\_{i}^{2}]}\_{\text{aleatoric}}+\underbrace{\mathrm{Var}[\mu\_{i}]}\_{\text{epistemic}}. |  | (13) |

The first term represents aleatoric uncertainty, which arises from
inherent noise in the observations and variability within each material class.
The second term represents epistemic uncertainty, corresponding to
uncertainty in the estimated mean that decreases as more high-confidence
evidence is incorporated.
For implementation, we compute these moments directly from the NIG parameters:

|  |  |  |  |
| --- | --- | --- | --- |
|  | 𝔼⁡[σi2]=β~iα~i−1,Var⁡[μi]=𝔼⁡[σi2]κ~i.\mathbb{E}[\sigma\_{i}^{2}]=\frac{\tilde{\beta}\_{i}}{\tilde{\alpha}\_{i}-1},\qquad\mathrm{Var}[\mu\_{i}]=\frac{\mathbb{E}[\sigma\_{i}^{2}]}{\tilde{\kappa}\_{i}}. |  | (14) |

The resulting aleatoric, epistemic, and total predictive uncertainties provide
interpretable measures of confidence in both the per-class property estimates
and the overall reconstruction. Regions with high aleatoric uncertainty reflect
sensor or perceptual noise, while high epistemic uncertainty indicates
insufficient or conflicting evidence about the underlying material properties.

### 3.4 Learning Semantics and Physical Properties

Semantic Segmentation.
Given a multi-view image dataset, we employ SAM [[30](#bib.bib38)] to produce pixel-accurate masks that decompose each object into hierarchical levels (whole, part, and sub-part), facilitating fine-grained semantic understanding.
The model outputs multiple candidate masks at different granularities, which we refine by discarding redundant or low-confidence predictions using SAM’s built-in IoU and stability measures.
The resulting segmentation maps capture precise object boundaries and semantically coherent regions, forming the basis for our downstream physical property estimation.

VLM Prompting.
For each segmented image, we construct a vision–language prompt comprising a triplet of images arranged side by side, following the design of [[60](#bib.bib7)]. The left image presents the complete object, the middle image overlays the segmentation mask, and the right image isolates the masked region of interest. Given an input image II, this process yields kk visual prompts corresponding to the kk masks predicted by SAM.
We additionally condition the VLM with a structured textual query that instructs it to (i) provide a concise caption of the segmented part, (ii) identify its predominant material, and (iii) infer relevant physical properties such as friction, density, etc. The model is further asked to report a normalized confidence score within [0,1][0,1], representing its belief in the prediction.

3D Gaussian Splatting.
Given the VLM responses and the refined physical property estimates from our Bayesian inference scheme, we construct a material legend assigning each material a unique color. The corresponding scene images are recolored accordingly and used as semantic inputs for 3DGS reconstruction. This yields a semantic splat that supports dense property inference, such as mass estimation.

Physical Property Estimation.
Using the reconstructed 3D Gaussian field and inferred material properties, we perform per-point and dense physical property estimation. Each voxel is associated with a predicted property value (e.g., friction or density), enabling spatial queries for per-point properties or integration over the volume to obtain aggregate measures such as total mass.

## 4 Experiments and Results

![Refer to caption](2511.18570v1/abo_500_results.png)

### 4.1 Implementation Details

We employ the splatfacto-big variant of Nerfstudio [[51](#bib.bib63)] for 3D Gaussian Splatting, using default parameters except for a random scale of 2.02.0 and a random background color. Each scene is trained for 20,00020{,}000 iterations on an NVIDIA RTX A5000 GPU.

For image segmentation, we use SAM [[30](#bib.bib38)] to obtain whole, part, and sub-part material decompositions. Material property estimation is performed using GPT-5 as the vision–language model (VLM), conditioned on structured visual–text prompts derived from the segmented images.

### 4.2 Mass Estimation

Dataset.
We employ the ABO dataset [[7](#bib.bib58)] for evaluating mass prediction, which includes a large set of consumer products listed on Amazon along with multi-view imagery, segmentation masks, physical measurements, and metadata. Specifically, we make use of the representative multi-view benchmark ABO-500 curated by  [[63](#bib.bib6)], which selects a balanced subset of 500 items from the entire ABO dataset. It is divided into 300 training, 100 validation, and 100 testing instances.

Metrics.
Following prior work on visual mass estimation [[50](#bib.bib57)], we evaluate using four complementary metrics that measure both absolute and relative error between the predicted mass m^\hat{m} and the ground-truth mass mm:

Absolute Difference Error (ADE): |m−m^||m-\hat{m}|,

Absolute Log Difference Error (ALDE): |ln⁡m−ln⁡m^||\ln m-\ln\hat{m}|,

Absolute Percentage Error (APE): |m−m^m|\big|\frac{m-\hat{m}}{m}\big|,

Minimum Ratio Error (MnRE): min⁡(mm^,m^m)\min\left(\frac{m}{\hat{m}},\frac{\hat{m}}{m}\right).

Baselines.
We compare our system against several visual and multimodal baselines on the ABO-500 dataset:

Image2mass [[50](#bib.bib57)]: a CNN that infers mass directly from RGB images and 3D bounding box dimensions.

2D CNN: a lightweight regression model built upon a frozen ResNet50 [[17](#bib.bib59)] backbone, fine-tuned with additional layers for scalar mass prediction.

LLaVA [[35](#bib.bib56)]: a vision-language model designed for instruction following.

NeRF2Physics [[63](#bib.bib6)]: a NeRF-based approach that jointly estimates 3D geometry and per-point physical properties such as density, friction, and stiffness. It predicts mass by integrating predicted density across the reconstructed volume.

Qualitative Results.
Figure [3](#S4.F3 "Figure 3 ‣ 4 Experiments and Results ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation") presents qualitative results on the ABO-500 dataset. For each object, we compare the material segmentation and mass-density predictions from NeRF2Physics with those produced by PhysGS. Our method yields substantially cleaner material segmentations with fewer spurious labels and more coherent part boundaries, while also producing sharper and more stable mass-density fields. These improvements are consistent across a wide range of object categories, demonstrating the advantage of combining vision-language priors with Bayesian inference over 3D Gaussian splats.

Quantitative Results.
We evaluate the accuracy of our method on mass estimation using the ABO-500 test set (100 objects). As shown in Table [1](#S4.T1 "Table 1 ‣ 4.2 Mass Estimation ‣ 4 Experiments and Results ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation"), traditional 2D methods such as Image2mass  [[50](#bib.bib57)] and 2D CNNs exhibit high mass estimation error due to their inability to capture 3D structure or material composition. VLM approaches (e.g. LLaVA [[35](#bib.bib56)]) show similar limitations, producing noisy predictions that vary across views. NeRF2Physics improves accuracy by exploiting neural radiance fields, and achieves the best ALDE (0.771) and MnRE (0.552) among existing baselines. PhysGS achieves the best performance on two key metrics: it reduces ADE from 8.730 to 8.254, corresponding to a 5.5% improvement, and reduces APE from 1.061 to 0.819, a substantial 22.8% improvement over NeRF2Physics.

Ablation Study.
Table [2](#S4.T2 "Table 2 ‣ 4.2 Mass Estimation ‣ 4 Experiments and Results ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation") shows that incorporating Bayesian inference yields clear gains over both NeRF2Physics and our non-Bayesian variant. Updating material and property beliefs across additional views reduces ADE by 5.6% and improves APE by 6.4% compared to the version without Bayesian updates. These improvements demonstrate that aggregating multi-view evidence to refine the posterior distribution leads to more accurate mass estimation, confirming the benefit of treating physical properties as latent variables that are iteratively updated rather than fixed from single-view predictions.

| Method | ADE (↓\downarrow) | ALDE (↓\downarrow) | APE (↓\downarrow) | MnRE (↑\uparrow) |
| --- | --- | --- | --- | --- |
| Image2mass [[50](#bib.bib57)] | 12.496 | 1.792 | 0.976 | 0.341 |
| 2D CNN | 15.431 | 1.609 | 14.459 | 0.362 |
| LLaVA [[35](#bib.bib56)] | 17.328 | 1.893 | 1.837 | 0.306 |
| NeRF2Physics [[63](#bib.bib6)] | 8.730 | 0.771 | 1.061 | 0.552 |
| Ours | 8.254 | 0.999 | 0.819 | 0.474 |

| Method | ADE (↓\downarrow) | ALDE (↓\downarrow) | APE (↓\downarrow) | MnRE (↑\uparrow) |
| --- | --- | --- | --- | --- |
| NeRF2Physics [[63](#bib.bib6)] | 9.786 | 0.61 | 0.931 | 0.609 |
| Ours (w/o BI) | 9.728 | 0.770 | 0.717 | 0.561 |
| Ours (with BI) | 9.187 | 0.827 | 0.715 | 0.539 |

![Refer to caption](2511.18570v1/friction_hardness_results.png)

|  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Shore Hardness (31 points, 11 objects) | | | | | Kinetic Friction (6 points, 6 objects) | | | | |
| Method | ADE (↓\downarrow) | ALDE (↓\downarrow) | APE (↓\downarrow) | MnRE (↑\uparrow) | Method | ADE (↓\downarrow) | ALDE (↓\downarrow) | APE (↓\downarrow) | MnRE (↑\uparrow) |
| GPT-4V [[61](#bib.bib60)] | 32.752 | 0.330 | 0.304 | 0.758 | GPT-4V [[61](#bib.bib60)] | 0.209 | 0.430 | 0.549 | 0.692 |
| CLIP [[45](#bib.bib37)] | 32.857 | 0.294 | 0.266 | 0.774 | CLIP [[45](#bib.bib37)] | 0.222 | 0.455 | 0.602 | 0.654 |
| NeRF2Physics [[63](#bib.bib6)] | 34.295 | 0.315 | 0.276 | 0.765 | NeRF2Physics [[63](#bib.bib6)] | 0.155 | 0.321 | 0.360 | 0.736 |
| Ours | 12.721 | 0.193 | 0.222 | 0.839 | Ours | 0.131 | 0.263 | 0.365 | 0.805 |

![Refer to caption](2511.18570v1/outdoor_viz.png)

### 4.3 Friction and Hardness Estimation

Dataset.
To evaluate our model’s ability to infer dense, spatially varying physical properties within objects, we leverage the friction and hardness dataset containing paired image and real-world measurement data, curated by  [[63](#bib.bib6)].
This dataset includes 15 household objects captured across 13 scenes, using multi-view RGB images paired with per-point measurements of kinetic friction coefficient and Shore A/D hardness.

Metrics.
We report the same evaluation metrics for per-point friction and hardness estimation used in evaluation for mass estimation as above: ADE, ALDE, APE, MnRE.

Baselines.
As before, we compare our method to several visual and multimodal baselines.

GPT-4V [[61](#bib.bib60)]: A large vision–language model capable of processing masked regions in its prompt.

CLIP [[45](#bib.bib37)]: A vision–language baseline that uses global CLIP embeddings from the canonical view of the scene, rather than the fused multi-view patch features used in our method. This baseline evaluates how well static visual–semantic representations can generalize to physical property prediction.

NeRF2Physics [[63](#bib.bib6)]: Same as in mass estimation baseline.

Qualitative Results.
Figure [4](#S4.F4 "Figure 4 ‣ 4.2 Mass Estimation ‣ 4 Experiments and Results ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation") presents qualitative results for friction and Shore hardness estimation on real objects. From a single RGB view, PhysGS produces dense per-point friction and hardness fields across materials such as rubber, leather, plastic, and metal. The predictions capture fine-grained material differences and exhibit clean boundaries between regions with distinct friction and hardness characteristics, reflecting the system’s ability to localize subtle variations in contact and deformation properties.

Quantitative Results.
Table [3](#S4.T3 "Table 3 ‣ 4.2 Mass Estimation ‣ 4 Experiments and Results ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation") reports results for per-point Shore A/D hardness and kinetic friction estimation on our real-world dataset. Across all hardness metrics, PhysGS achieves substantial gains over existing approaches. Relative to the best baseline, our method reduces ADE by 61.2%, lowers ALDE by 34.4%, and decreases APE by 16.5%, while improving MnRE by 8.4%. For kinetic friction, PhysGS again outperforms the strongest baseline (NeRF2Physics) on the majority of metrics, reducing ADE by 15.5% and ALDE by 18.1%, and increasing MnRE by 9.4%. These gains highlight the benefit of integrating multi-view evidence through Bayesian inference, which refines the posterior distribution of material properties beyond what single-view or deterministic models can infer.

### 4.4 Applications: Outdoor Scene Understanding

PhysGS can also estimate physical properties of outdoor environments, such as friction and stiffness, which are important for reasoning about natural, vegetation-rich terrain [[5](#bib.bib43)]. Our method also provides per-pixel uncertainty (aleatoric + epistemic) for these estimates. We demonstrate this capability on the RUGD [[58](#bib.bib61)] and RELLIS-3D [[23](#bib.bib62)] datasets (Figure [3](#S4.T3 "Table 3 ‣ 4.2 Mass Estimation ‣ 4 Experiments and Results ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation")), which contain challenging outdoor scenes where accurate physical property prediction and uncertainty assessment are essential for interpreting complex terrain.

## 5 Conclusion, Limitations and Future Work

We presented PhysGS, a Bayesian-inferred 3D Gaussian Splatting framework for estimating dense physical properties from RGB images and vision-language priors. Across indoor and outdoor real-world datasets, PhysGS achieves consistent gains over existing approaches. On ABO-500, our method improves mass estimation by 5.5% in ADE and 22.8% in APE. PhysGS also reduces Shore hardness error by up to 61.2% and kinetic friction error by up to 18.1% relative to the strongest baselines. Outdoor experiments on RUGD and RELLIS-3D further show that the method generalizes to complex natural environments, capturing material segmentation, friction, stiffness, and uncertainty.

A primary limitation of PhysGS lies in its sensitivity to segmentation quality. When part-level masks merge visually similar materials or fail to isolate fine-grained regions, the downstream physical property estimates inherit this ambiguity, reducing material separation and increasing predictive uncertainty. This effect is visible in Fig. [5](#S4.F5 "Figure 5 ‣ 4.2 Mass Estimation ‣ 4 Experiments and Results ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation"), where cluttered outdoor regions lead to less precise SAM masks and correspondingly higher total uncertainty. Future work may incorporate VLM-guided segmentation refinement or confidence-based mask filtering to automatically reject low-quality masks and preserve fine-grained material structure.

## References

Supplementary Material

## A. Full Bayesian and Uncertainty Formulation

### A.1. Observation Model

For completeness, we describe the observation model used in PhysGS. Each observation corresponds to a segmented region of the scene and contains semantic (material) and physical (property) information extracted from the vision–language model (VLM). The role of these observations in the Bayesian updates is described in Sec. [3](#S3 "3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation").

Observation tuple.
For the mm-th segmented region, we define

|  |  |  |  |
| --- | --- | --- | --- |
|  | 𝒪m=(cm,pm,ψm),\mathcal{O}\_{m}=\big(c\_{m},\;p\_{m},\;\psi\_{m}\big), |  | (15) |

where cmc\_{m} is the predicted material class, pmp\_{m} is the confidence produced by the VLM, and ψm\psi\_{m} is the predicted physical property (e.g., friction, hardness, stiffness, density).
Across multiple views, the full set of observations is

|  |  |  |  |
| --- | --- | --- | --- |
|  | Z={𝒪1,…,𝒪M}.Z=\{\mathcal{O}\_{1},\dots,\mathcal{O}\_{M}\}. |  | (16) |

The tuple (cm,pm,ψm)(c\_{m},p\_{m},\psi\_{m}) constitutes a noisy measurement of the latent variables (zm,μzm,σzm2)(z\_{m},\mu\_{z\_{m}},\sigma\_{z\_{m}}^{2}). In particular, the predicted class cmc\_{m} serves as a noisy proxy for the true (unobserved) material label zmz\_{m}, while the VLM estimate ψm\psi\_{m} provides a noisy observation of the underlying material-specific physical property whose distribution is governed by (μzm,σzm2)(\mu\_{z\_{m}},\sigma\_{z\_{m}}^{2}). These observed quantities supply the confidence-weighted evidence used in the Bayesian updates that follow.

### A.2. Dirichlet–Categorical Posterior

The material fusion process follows the Dirichlet–Categorical formulation introduced in Sec. [3.1](#S3.SS1 "3.1 Preliminaries ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation").
The Categorical likelihood and Dirichlet prior correspond to Eqs. ([1](#S3.E1 "Equation 1 ‣ Dirichlet–Categorical formulation. ‣ 3.1 Preliminaries ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation"))–([2](#S3.E2 "Equation 2 ‣ Dirichlet–Categorical formulation. ‣ 3.1 Preliminaries ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation")).

The posterior Dirichlet parameters update as in Eq. ([5](#S3.E5 "Equation 5 ‣ Dirichlet–Categorical formulation. ‣ 3.1 Preliminaries ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation")):

|  |  |  |  |
| --- | --- | --- | --- |
|  | α~i=αi(0)+∑m:cm=iλpm.\tilde{\alpha}\_{i}=\alpha\_{i}(0)+\sum\_{m:\,c\_{m}=i}\lambda\,p\_{m}. |  | (17) |

The resulting posterior predictive distribution over material classes is given in Eq. ([4](#S3.E4 "Equation 4 ‣ Dirichlet–Categorical formulation. ‣ 3.1 Preliminaries ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation")).

### A.3. Continuous Property Estimation

Continuous physical properties are fused using confidence-weighted running moments as introduced in Sec. [3.2](#S3.SS2 "3.2 Bayesian Inference for Material Property Estimation ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation") of the main paper.
The accumulators WiW\_{i}, SiS\_{i}, and QiQ\_{i} match Eq. ([6](#S3.E6 "Equation 6 ‣ 3.2 Bayesian Inference for Material Property Estimation ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation")) in the main paper.

The posterior mean and variance follow Eq. ([7](#S3.E7 "Equation 7 ‣ 3.2 Bayesian Inference for Material Property Estimation ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation")) in the main paper:

|  |  |  |  |
| --- | --- | --- | --- |
|  | μi=SiWi,σi2=max⁡(QiWi−μi2,ϵ).\mu\_{i}=\frac{S\_{i}}{W\_{i}},\qquad\sigma\_{i}^{2}=\max\!\left(\frac{Q\_{i}}{W\_{i}}-\mu\_{i}^{2},\;\epsilon\right). |  | (18) |

This defines the Gaussian posterior p⁡(ψi∣Z)p(\psi\_{i}\mid Z) shown in Eq. ([8](#S3.E8 "Equation 8 ‣ 3.2 Bayesian Inference for Material Property Estimation ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation")) of the main paper.

### A.4. Mixture Formulation

Marginalizing over discrete material classes using the hierarchical model in Sec. [3.2](#S3.SS2 "3.2 Bayesian Inference for Material Property Estimation ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation") leads directly to the mixture distribution shown in Eq. ([11](#S3.E11 "Equation 11 ‣ 3.2 Bayesian Inference for Material Property Estimation ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation")), combining material probabilities with the class-conditional Gaussian property estimates.

### A.5. Normal–Inverse–Gamma Posterior

We extend our continuous estimator with the Normal–Inverse–Gamma (NIG) prior introduced in Sec. [3.3](#S3.SS3 "3.3 Uncertainty-Aware Property Fields ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation").
The joint prior over (μi,σi2)(\mu\_{i},\sigma\_{i}^{2}) matches Eq. ([12](#S3.E12 "Equation 12 ‣ 3.3 Uncertainty-Aware Property Fields ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation")).

Given a weighted observation (ψm,pm)(\psi\_{m},p\_{m}), the closed-form posterior updates (Eqs. ([13](#S3.E13 "Equation 13 ‣ 3.3 Uncertainty-Aware Property Fields ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation"))–([14](#S3.E14 "Equation 14 ‣ 3.3 Uncertainty-Aware Property Fields ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation"))) are:

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
|  | κ~i\displaystyle\tilde{\kappa}\_{i} | =κi+pm,\displaystyle=\kappa\_{i}+p\_{m}, |  | (19) |
|  |  |  |  |  |
| --- | --- | --- | --- | --- |
|  | τ~i\displaystyle\tilde{\tau}\_{i} | =κi​τi+pm​ψmκi+pm,\displaystyle=\frac{\kappa\_{i}\tau\_{i}+p\_{m}\psi\_{m}}{\kappa\_{i}+p\_{m}}, |  | (20) |
|  |  |  |  |  |
| --- | --- | --- | --- | --- |
|  | α~i\displaystyle\tilde{\alpha}\_{i} | =αi+pm2,\displaystyle=\alpha\_{i}+\tfrac{p\_{m}}{2}, |  | (21) |
|  |  |  |  |  |
| --- | --- | --- | --- | --- |
|  | β~i\displaystyle\tilde{\beta}\_{i} | =βi+pm​κi​(ψm−τi)22​(κi+pm).\displaystyle=\beta\_{i}+\frac{p\_{m}\kappa\_{i}(\psi\_{m}-\tau\_{i})^{2}}{2(\kappa\_{i}+p\_{m})}. |  | (22) |

### A.6. Predictive Uncertainty

The decomposition of predictive uncertainty into aleatoric and epistemic components follows Eq. ([13](#S3.E13 "Equation 13 ‣ 3.3 Uncertainty-Aware Property Fields ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation")).
The predictive moments correspond directly to Eq. ([14](#S3.E14 "Equation 14 ‣ 3.3 Uncertainty-Aware Property Fields ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation")):

|  |  |  |  |
| --- | --- | --- | --- |
|  | 𝔼⁡[σi2]=β~iα~i−1,Var⁡[μi]=𝔼⁡[σi2]κ~i.\mathbb{E}[\sigma\_{i}^{2}]=\frac{\tilde{\beta}\_{i}}{\tilde{\alpha}\_{i}-1},\qquad\mathrm{Var}[\mu\_{i}]=\frac{\mathbb{E}[\sigma\_{i}^{2}]}{\tilde{\kappa}\_{i}}. |  | (23) |

Aleatoric uncertainty reflects inherent variability within a material class, while epistemic uncertainty captures uncertainty in the estimated mean due to limited or inconsistent evidence.

### A.7. MMSE Estimate

As shown in Eq. ([7](#S3.E7 "Equation 7 ‣ 3.2 Bayesian Inference for Material Property Estimation ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation")), the posterior mean μi\mu\_{i} is the minimum mean-square-error (MMSE) estimator:

|  |  |  |  |
| --- | --- | --- | --- |
|  | ψ^i=μi.\hat{\psi}\_{i}=\mu\_{i}. |  | (24) |

This corresponds to the property value that minimizes expected squared error and is therefore used as the single representative estimate for each material class.

### A.8. Full Probabilistic Model

The complete hierarchical model underlying PhysGS is summarized in Sec. [3](#S3 "3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation") of the main paper and depicted in Fig. [2](#S3.F2 "Figure 2 ‣ 3 Proposed Approach ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation").
For completeness, we restate the probabilistic structure:

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
|  | 𝜽\displaystyle\boldsymbol{\theta} | ∼Dirichlet⁡(𝜶⁡(0)),\displaystyle\sim\mathrm{Dirichlet}(\boldsymbol{\alpha}(0)), |  | (25) |
|  |  |  |  |  |
| --- | --- | --- | --- | --- |
|  | zm\displaystyle z\_{m} | ∼Categorical⁡(𝜽),\displaystyle\sim\mathrm{Categorical}(\boldsymbol{\theta}), |  | (26) |
|  |  |  |  |  |
| --- | --- | --- | --- | --- |
|  | (μi,σi2)\displaystyle(\mu\_{i},\sigma\_{i}^{2}) | ∼NIG⁡(τi,κi,αi,βi),\displaystyle\sim\mathrm{NIG}(\tau\_{i},\kappa\_{i},\alpha\_{i},\beta\_{i}), |  | (27) |
|  |  |  |  |  |
| --- | --- | --- | --- | --- |
|  | ψm\displaystyle\psi\_{m} | ∼𝒩⁡(μzm,σzm2).\displaystyle\sim\mathcal{N}(\mu\_{z\_{m}},\sigma\_{z\_{m}}^{2}). |  | (28) |

This formulation provides the full probabilistic backbone through which PhysGS jointly infers materials, continuous properties, and calibrated uncertainty. First, a Dirichlet prior is placed over the material probabilities 𝜽\boldsymbol{\theta}, reflecting initial uncertainty about the frequency of each material class. Each segmented region then draws a material label zmz\_{m} from this Categorical distribution. For every material class ii, the mean and variance of its physical property are modeled using a Normal–Inverse–Gamma (NIG) prior, which captures both uncertainty in the material’s typical property value and its intrinsic variability. Finally, the observed physical property ψm\psi\_{m} for region mm is sampled from the Gaussian distribution associated with its material label. Together, this hierarchy defines how materials and their continuous properties jointly generate the observations used in the Bayesian inference procedure.

## B. Additional Results

### B.1. Stiffness Estimation

| Method | ADE (↓\downarrow) | ALDE (↓\downarrow) | APE (↓\downarrow) | MnRE (↑\uparrow) |
| --- | --- | --- | --- | --- |
| GPT-4V | 0.563 | 2.380 | 19.986 | 0.210 |
| GPT-5 | 0.126 | 1.053 | 2.887 | 0.452 |
| Ours | 0.040 | 0.725 | 1.338 | 0.553 |

![Refer to caption](2511.18570v1/fabric_viz.png)

Dataset.
We employ the MIT Fabric Properties Dataset  [[2](#bib.bib64)] for evaluating mass prediction, 30 different types of real fabric along with measurements of their material properties. Since these are all videos, we curate an image dataset from this, where all the different fabrics are evaluated for their bending stiffness. While these are video datasets, they are captured from a single view, and thus we evaluate our model on one image per fabric. We pick the first frame of every video.

Metrics.
We report the same evaluation metrics for bending stiffness estimation (lbf-in2) used in evaluation for mass estimation as above: ADE, ALDE, APE, MnRE.

Baselines.
We compare our model against several visual and multimodal baselines on the ABO-500 dataset:

GPT-4V: We provide GPT-4V with the image, and ask it to estimate the physical stiffness of the fabric.

GPT-5: Same prompt as GPT-4V.

Quantitative Results.
Table [4](#Sx2.T4 "Table 4 ‣ B.1. Stiffness Estimation ‣ B. Additional Results ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation") reports quantitative results comparing our method against GPT-4V and GPT-5 VLM baselines. Across all metrics, PhysGS achieves the strongest performance, reducing ADE by 68.3% compared to GPT-5 and by more than an order of magnitude compared to GPT-4V. Our method also attains the highest MnRE score, indicating substantially improved scale consistency in stiffness estimation. These gains highlight the effectiveness of our Bayesian fusion framework in capturing fine-grained material compliance even in visually ambiguous textile structures.

Qualitative Results.
Figure [6](#Sx2.F6 "Figure 6 ‣ B.1. Stiffness Estimation ‣ B. Additional Results ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation") presents qualitative bending stiffness estimation results on real fabric samples from the MIT Fabric Properties dataset. The dataset contains diverse materials with visually similar appearances but substantially different mechanical behavior, making stiffness prediction particularly challenging. Across a variety of textile types, including corduroy, nylon ripstop, outdoor polyester, and pleather, PhysGS produces dense stiffness fields that clearly delineate material differences. Each predicted stiffness map exhibits smooth spatial variation and preserves mask-level boundaries, reflecting the underlying compliance characteristics of each fabric.

### B.2. Terrain Friction Estimation

Dataset.
We evaluate terrain friction prediction using the Terrain Class Friction dataset from [[11](#bib.bib4)]. The dataset contains paired RGB images and friction measurements for seven common indoor and outdoor terrain classes, including carpet, concrete, laminated flooring, rubber, pebbles, rocks, and wood (see Table [5](#Sx2.T5 "Table 5 ‣ B.2. Terrain Friction Estimation ‣ B. Additional Results ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation")). Following the protocol in [[11](#bib.bib4)], we assess prediction accuracy against the mean coefficients of friction obtained from their unimodal Gaussian fits for each terrain class.

| Terrain Class | 𝝁\boldsymbol{\mu} | 𝝈\boldsymbol{\sigma} |
| --- | --- | --- |
| Concrete | 0.543 | 0.065 |
| Pebbles | 0.428 | 0.059 |
| Rocks | 0.478 | 0.113 |
| Wood | 0.372 | 0.055 |
| Rubber | 0.616 | 0.048 |
| Carpet | 0.583 | 0.068 |
| Laminated Flooring | 0.311 | 0.045 |

| Method | ADE (↓\downarrow) | ALDE (↓\downarrow) | APE (↓\downarrow) | MnRE (↑\uparrow) |
| --- | --- | --- | --- | --- |
| GPT-4V | 0.129 | 0.315 | 0.286 | 0.747 |
| GPT-5 | 0.146 | 0.253 | 0.291 | 0.779 |
| Ours | 0.126 | 0.251 | 0.290 | 0.783 |

![Refer to caption](2511.18570v1/terrain_friction_viz.png)

Metrics.
We report the same evaluation metrics for terrain friction estimation (lbf-in2) used in evaluation for mass estimation as above: ADE, ALDE, APE, MnRE.

Baselines.
We compare our model against several visual and multimodal baselines on the ABO-500 dataset:

GPT-4V: We provide GPT-4V with the image, and ask it to estimate the friction of the terrain.

GPT-5: Same prompt as GPT-4V.

Quantitative Results.
Table [6](#Sx2.T6 "Table 6 ‣ B.2. Terrain Friction Estimation ‣ B. Additional Results ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation") reports quantitative results comparing our method against GPT-4V and GPT-5 VLM baselines. As the dataset consists of single-object, mostly homogeneous surfaces, the benefits of precise part-level segmentation are limited in this setting. Nevertheless, our hierarchical prompting scheme enables both global and local reasoning by guiding the VLM to focus on the dominant surface region while still incorporating contextual cues such as reflectance, roughness, and material structure. Across all four metrics, ADE, ALDE, APE, and MnRE, our method performs on par with or better than GPT-4V and GPT-5.

Qualitative Results. Figure [7](#Sx2.F7 "Figure 7 ‣ B.2. Terrain Friction Estimation ‣ B. Additional Results ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation") presents qualitative friction estimation results on samples from the Terrain Class Friction dataset. Given an input RGB image, PhysGS produces smooth and spatially consistent friction fields that align with the visual regions of each surface. The predicted maps clearly distinguish materials such as carpet, wood, and composite flooring, capturing their characteristic friction patterns while preserving coherent region boundaries.

### B.3. Outdoor Scene Analysis

![Refer to caption](2511.18570v1/bad_sam_masks.png)

Figure [5](#S4.F5 "Figure 5 ‣ 4.2 Mass Estimation ‣ 4 Experiments and Results ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation") shows qualitative results of PhysGS applied to outdoor environments with diverse terrain types, vegetation, and natural materials. From a single RGB image, our model predicts material segmentation, friction coefficients, stiffness (Young’s modulus) fields, and total uncertainty (aleatoric + epistemic). These results demonstrate the ability of PhysGS to extend beyond controlled indoor settings and operate on unstructured outdoor scenes.

Across all examples, the predicted material maps provide reasonable semantic decomposition of natural surfaces such as gravel, grass, bark, mud, water, and leaf litter. The corresponding friction and stiffness fields reflect meaningful physical differences between these materials: solid regions such as rock, concrete, or bark consistently receive higher stiffness values, whereas deformable surfaces such as mud and grass yield lower estimated moduli. Friction estimates likewise align with expected terrain properties, capturing transitions between slippery, saturated mud and higher-friction vegetation or gravel.

The total uncertainty maps reveal a strong correlation between uncertainty and the quality of SAM-generated segmentations, consistent with the discussion in the limitations section (see Sec. [5](#S5 "5 Conclusion, Limitations and Future Work ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation")). Rows 2 and 3 in Figure [5](#S4.F5 "Figure 5 ‣ 4.2 Mass Estimation ‣ 4 Experiments and Results ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation") contain dense clutter, irregular textures, or ambiguous boundaries (e.g., intertwined vegetation or mud–grass transitions), leading SAM to produce noisier part-level masks. As illustrated explicitly in Figure [8](#Sx2.F8 "Figure 8 ‣ B.3. Outdoor Scene Analysis ‣ B. Additional Results ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation"), these mask inaccuracies propagate into the part images and result in less reliable material evidence.
In such cases, PhysGS assigns noticeably higher total uncertainty, driven by both epistemic uncertainty from inconsistent material cues and aleatoric uncertainty arising from intra-region variability.

Conversely, rows 1 and 4 in Figure [5](#S4.F5 "Figure 5 ‣ 4.2 Mass Estimation ‣ 4 Experiments and Results ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation") contain large, spatially coherent surfaces (e.g., gravel, sky, uniform grass), where SAM produces cleaner segmentations. In these settings, PhysGS yields lower uncertainty and more stable physical predictions across the scene. Taken together, these results, supported by both Figures [5](#S4.F5 "Figure 5 ‣ 4.2 Mass Estimation ‣ 4 Experiments and Results ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation") and [8](#Sx2.F8 "Figure 8 ‣ B.3. Outdoor Scene Analysis ‣ B. Additional Results ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation"), demonstrate that the Bayesian uncertainty estimates are meaningfully sensitive to segmentation quality and reliably signal when the input evidence is less trustworthy.

## C. Additional Experimental Details

![Refer to caption](2511.18570v1/GPT_fabric_prompt.png)

### C.1. Prompting Details

Figures [9](#Sx3.F9 "Figure 9 ‣ C. Additional Experimental Details ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation") and [10](#Sx3.F10 "Figure 10 ‣ C.2. Baseline Details ‣ C. Additional Experimental Details ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation") show the exact prompting configurations, inspired by [[60](#bib.bib7)], used for the MIT Fabric Properties dataset and the RUGD outdoor dataset. In both cases, the VLM is provided with the original RGB image, a segmentation-mask overlay, and an isolated part image. The text prompt directs the model to ignore masked regions and focus only on the visible segment, ensuring that predictions are part-specific rather than influenced by the surrounding scene. We also maintain separate indoor and outdoor material libraries so the VLM selects from the most appropriate set of materials for each environment.

For each part, the VLM returns one or more candidate materials with associated physical properties and confidence scores. Each of these candidate predictions is treated as a confidence-weighted observation within our Bayesian framework, allowing PhysGS to fuse evidence across views and produce consistent material and property estimates. Importantly, the distribution of confidence across multiple materials provides a direct signal of semantic ambiguity. When the VLM is uncertain, often due to noisy or imprecise SAM segmentations, the confidence spread increases, which propagates into higher predictive uncertainty in our property fields, consistent with the trends discussed in the limitations section (Sec. [5](#S5 "5 Conclusion, Limitations and Future Work ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation")).

### C.2. Baseline Details

To benchmark PhysGS against existing vision–language models, we evaluate GPT-4V and GPT-5 on the MIT Fabric Properties and Terrain Class Friction datasets using a simplified prompting strategy tailored for fair comparison (see Figure [11](#Sx3.F11 "Figure 11 ‣ C.2. Baseline Details ‣ C. Additional Experimental Details ‣ PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation")). For each image, the VLM receives only the raw RGB frame and is instructed to (1) describe the dominant visible region, (2) predict the most likely material based solely on visual appearance, and (3) estimate a friction coefficient, stiffness value, and confidence score.

This baseline prompt does not include segmentation cues or part-based isolation, and therefore tests each VLM’s ability to infer material and physical properties directly from appearance alone.
The resulting predictions serve as a reference for evaluating the gains provided by our part-aware prompting, used in PhysGS.

![Refer to caption](2511.18570v1/outdoor_prompt.png)
![Refer to caption](2511.18570v1/baseline_prompt.png)
![[LOGO]][IMAGE]

## Instructions for reporting errors

We are continuing to improve HTML versions of papers, and your feedback helps enhance accessibility and mobile
support. To report errors in the HTML that will help us improve conversion and rendering, choose any of the
methods listed below:

**Tip:** You can select the relevant text first, to include it in your report.

Our team has already identified [the following issues](https://github.com/arXiv/html_feedback/issues). We appreciate your time reviewing and reporting rendering errors we
may not have found yet. Your efforts will help us improve the HTML versions for all readers, because disability
should not be a barrier to accessing research. Thank you for your continued support in championing open access for
all.

Have a free development cycle? Help support accessibility at arXiv! Our collaborators at LaTeXML maintain a [list of packages that need conversion](https://github.com/brucemiller/LaTeXML/wiki/Porting-LaTeX-packages-for-LaTeXML), and welcome [developer contributions](https://github.com/brucemiller/LaTeXML/issues).

![Simons Foundation](/static/base/1.0.1/images/funders/simons-foundation.png)
![Simons Foundation International](/static/base/1.0.1/images/funders/simons-foundation-international.png)
![Schmidt Sciences](/static/base/1.0.1/images/funders/schmidt-sciences.png)