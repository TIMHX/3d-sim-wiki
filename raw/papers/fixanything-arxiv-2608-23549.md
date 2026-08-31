---
source_url: https://arxiv.org/abs/2608.23549
ingested: 2026-08-31
sha256: eb53f48a83635a593b34383e81bcb56cafa82810b8a0398951ed1c16b5cb7a33
---

##### Report GitHub Issue

Content selection saved. Describe the issue below:

![](/static/base/1.0.1/images/icons/smileybones-small.svg)
![arXiv logo](/static/base/1.0.1/images/arxiv-logo-primary-light.svg)

# FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors

###### Abstract

Rendering views using 3D scene representations such as Gaussian Splatting (3DGS), Neural Radiance Fields (NeRF), meshes, or even point clouds produces artifacts when input views are sparse or target views lie far from the input.
Recent work mitigates these artifacts using diffusion-based generative priors, but is specialized to individual representations and require custom architectures or extensive retraining.
We present FixAnything, a single model for fixing a wide range of rendering artifacts. It does so by repurposing a pretrained video generative model, leveraging its implicit multi-view priors with only minimal modification and lightweight finetuning.
Our key insight is that even noisily-rendered sequences preserve camera motion and coarse scene structure, allowing cleanup to be formulated as video-to-video translation.
To control what scene structure should be preserved, we introduce a binary mask denoting the clean pixels, enabling the model to anchor its output to high-quality inputs (e.g. training views) while refining the rest.
To encourage FixAnything to produce 3D-consistent renderings that support downstream reconstruction, we use camera pose accuracy (recovered via structure-from-motion) as a reward signal for direct preference optimization (DPO).
Across four distinct 3D representations, FixAnything consistently improves rendering quality with lightweight finetuning, demonstrating that a single generalist video prior can replace multiple specialist refinement pipelines.
The simplicity of the framework enables immediate adoption of stronger future video models without architectural redesign.

###### Keywords:

![Refer to caption](2608.23549v1/teaser_v3.png)

## 1 Introduction

The quality of 3D reconstruction has improved dramatically in recent years, but a gap remains: when input views are sparse or novel viewpoints lie far from training views, every 3D representation produces artifacts.
3DGS [[13](#bib.bib3)] produces floaters across the scene, NeRF [[23](#bib.bib2)] hallucinates foggy geometry, mesh reconstructions suffer from texture distortions, and point clouds leave holes. These artifacts directly limit downstream applications, where the visual quality of novel views may degrade to the point where they are unusable for content creation or robotics.
The dominant approach to improve the quality of these renderings has been to build a specialist generative pipeline that removes the artifacts of that particular representation: 3D or per-image diffusion priors for NeRF [[34](#bib.bib12), [35](#bib.bib10), [36](#bib.bib13)], video diffusion models tailored to 3DGS [[20](#bib.bib9), [37](#bib.bib33)], and camera-controlled video generation conditioned on explicit geometry [[43](#bib.bib11), [28](#bib.bib32), [9](#bib.bib16)].
While effective individually, such a bespoke approach is difficult to scale: each time a new representation emerges or an existing one is improved, a new pipeline must be built, with its own architecture, training data, and conditioning mechanism.

This raises a natural question: can a single generalist replace this growing family of specialists? We show the answer is yes. Despite looking visually distinct, artifacts from different representations share a common property: they all deviate from the manifold of natural videos, while preserving the underlying camera trajectory and coarse scene layout. A pretrained video model, with minimal adaptation, can exploit this shared structure to translate (or project) degraded renderings onto the manifold of natural videos.

We present FixAnything, a framework that realizes this generalist approach.
FixAnything takes as input a video rendered along a camera trajectory and directly produces a cleaned version, naturally preserving temporal coherence across views (see [Fig. 1](#S0.F1 "In FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors")).
We make use of a video diffusion model (Wan2.1 [[32](#bib.bib15)]) with minor architectural changes: the rendering video is concatenated as conditioning input in latent space, and only a lightweight LoRA [[10](#bib.bib26)] is trained to adapt the model for this task.
A per-frame binary mask distinguishes clean reference frames (which the model should trust and preserve) from degraded frames (which need fixing), anchoring each restoration to known high-quality views (e.g. training views).
We generate training pairs from DL3DV-10K [[17](#bib.bib28)] using videos rendered from four different 3D representations including 3DGS, NeRF, meshes, and sparse point clouds. Because the pretrained model already understands natural videos, as few as 20 paired videos suffice for effective training.

Interestingly, we find that different 3D representations achieve comparable quality after cleanup. This is particularly remarkable for sparse (COLMAP [[29](#bib.bib27)]) point clouds, which often act as a prerequisite for other 3D representations such as 3DGS and NeRF (since they require posed input images). Our results suggest that such “intermediate” 3D representations may not be needed given a sufficiently powerful generative model. Indeed, video generation can already interpolate between two input frames (e.g., “first-last-frame-to-video” generation [[32](#bib.bib15)]). However, such models generate the most-likely camera path rather than conditioning on one provided by a rendering engine. We show that sparse point cloud renders are sufficient for exposing this camera path, avoiding the need to teach the generative model about SE⁡(3)\mathrm{SE}(3) camera coordinates (e.g., using Plücker coordinates [[26](#bib.bib29), [44](#bib.bib30)] which typically requires far more than 20 finetuning videos [[46](#bib.bib1)]).

However, one final challenge is that the generated videos may not be 3D consistent, which may prevent downstream applications such as 3D reconstruction. Rather than building geometric constraints into the architecture, we treat geometric consistency as a preference optimization problem: for each training video, we sample multiple outputs with different random seeds, rank them by how accurately structure-from-motion [[29](#bib.bib27)] recovers their camera poses, and apply Flow-DPO [[19](#bib.bib21)] to steer the model toward geometrically coherent outputs.
This bakes the geometric consistency into the model during training, improving pose estimation accuracy by 7.2% (AUC@5°) with no additional inference cost.

Despite its simplicity, FixAnything matches or exceeds specialist methods while generalizing across representations.
Because the adaptation requires no architectural changes and updates less than 1% of parameters, the same recipe can be applied to newer video foundation models as they become available, requiring only a new LoRA training run on limited (academic-scale) compute.

In summary, our contributions are:

A generalist framework that takes rendering videos along camera trajectories of a 3D representation as input and fixes artifacts with a single model, without architectural changes to the base video model.

A mask-aware conditioning mechanism that distinguishes frames to trust from frames to fix, combined with data-efficient training that achieves effective results with limited paired data.

A geometry-aware preference optimization that bakes multi-view consistency into the model using camera pose accuracy as a reward signal via Flow-DPO.

## 2 Related Work

#### Sparse-view novel view synthesis.

NeRF [[23](#bib.bib2)] and 3DGS [[13](#bib.bib3)] achieve high-fidelity rendering when dense input views are available, but their quality degrades sharply under sparse-view settings due to the lack of multi-view supervision.
Many methods address this by introducing regularization during reconstruction.
RegNeRF [[24](#bib.bib5)] penalizes rendered patches at unobserved viewpoints to smooth geometry, while FreeNeRF [[38](#bib.bib6)] applies frequency and occlusion regularization to prevent overfitting.
DSNeRF [[5](#bib.bib42)] and SparseNeRF [[33](#bib.bib43)] leverage depth cues to stabilize geometry under sparse supervision.
On the 3DGS side, DNGaussian [[15](#bib.bib7)] and FSGS [[47](#bib.bib8)] also introduce similar geometric constraints to improve stability in sparse-view settings.
While these approaches reduce artifacts, they remain constrained by the available observations. This faithfulness to input views is desirable when sufficient multi-view coverage exists, but it also limits their ability to infer plausible content in regions that are weakly observed or unseen. In such cases, incorporating generative priors can provide reasonable completions while maintaining consistency with observed views.

#### Generative priors for novel view synthesis and 3D enhancement.

Recent work leverages pretrained generative models to improve 3D reconstructions beyond what the input views alone can support.
Nerfbusters [[34](#bib.bib12)] trains a 3D diffusion prior to directly regularize NeRF geometry, removing floater artifacts in 3D space.
ReconFusion [[36](#bib.bib13)] generates novel views one at a time, conditioned on PixelNeRF [[42](#bib.bib44)] features from nearby cameras, and uses them to regularize NeRF training.
Difix3D+ [[35](#bib.bib10)] applies a single-step image diffusion model conditioned on a reference view to fix individual renderings, then progressively distills the cleaned images back into the 3D representation.
FlowR [[8](#bib.bib34)] trains a multi-view flow matching model that jointly processes multiple views to map degraded renderings from sparse reconstructions to their dense-reconstruction counterparts.
These methods process views independently or in small multi-view sets, and rely on the underlying 3D representation to enforce global consistency.

Other works repurpose video diffusion models [[3](#bib.bib14), [32](#bib.bib15), [39](#bib.bib45), [1](#bib.bib46)] for 3D and novel view synthesis tasks.
ViewCrafter [[43](#bib.bib11)] and GEN3C [[28](#bib.bib32)] use camera-controlled video generation conditioned on rendered point clouds to synthesize novel views from sparse inputs.
3DGS-Enhancer [[20](#bib.bib9)] trains a video latent diffusion model with a custom spatial-temporal decoder to restore view-consistent renderings, then finetunes the 3DGS model on the enhanced views.
Xu et al. [[37](#bib.bib33)] recast sparse-view NVS as test-time video completion, using a pretrained video diffusion model with uncertainty-aware modulation to generate pseudo-views that densify 3DGS supervision.
A common pattern across all these methods is specialization: each targets a specific representation, introduces custom architecture components, and requires large-scale paired or annotated data.
FixAnything instead adapts a single pretrained video model to handle four representation types with no architectural changes and orders of magnitude less training data.

#### Preference optimization for diffusion models.

Direct Preference Optimization (DPO) [[27](#bib.bib22)] was originally proposed for aligning language models with human preferences without training an explicit reward model.
The idea has since been extended to generative vision models. For instance, Diffusion-DPO [[31](#bib.bib23)] adapts the framework to noise-prediction diffusion models for image generation.
For modern video generators based on rectified flow [[18](#bib.bib19), [21](#bib.bib20)], Flow-DPO [[19](#bib.bib21)] reformulates the preference loss in terms of velocity prediction and demonstrates improvements in visual quality and text alignment for text-to-video models.
These prior works optimize for human aesthetic preferences or prompt fidelity.
As concurrent works, Epipolar-DPO [[14](#bib.bib24)] uses the Sampson distance from epipolar geometry as a reward signal to improve 3D consistency in text-to-video and image-to-video generation, and VideoGPA [[7](#bib.bib25)] distills dense geometric priors from reconstruction foundation models into video diffusion models via DPO.
Our work shares the motivation of using geometric consistency as a preference signal but applies it to a different setting: rather than improving general-purpose video generation from text or a single image, we target rendering cleanup for 3D reconstructions, using camera pose accuracy from structure-from-motion as the reward to ensure that refined videos support downstream 3D tasks.

## 3 Method

![Refer to caption](2608.23549v1/model_arch_v2.png)
![Refer to caption](2608.23549v1/dpo_framework_v2.png)

[Fig. 2](#S3.F2 "In 3 Method ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors") provides an overview of FixAnything.
We first formulate the problem as representation-agnostic rendering cleanup ([Sec. 3.1](#S3.SS1 "3.1 Representation-Agnostic Rendering Cleanup ‣ 3 Method ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors")), then describe how a pretrained video diffusion model is adapted for this task with minimal changes ([Sec. 3.2](#S3.SS2 "3.2 Lightweight Adaptation of a Pretrained Video Model ‣ 3 Method ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors")).
[Sec. 3.3](#S3.SS3 "3.3 Training Data ‣ 3 Method ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors") details the training data, and [Sec. 3.4](#S3.SS4 "3.4 Geometry-Aware Preference Optimization ‣ 3 Method ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors") introduces a preference optimization stage that further encourages geometric consistency for the model.

### 3.1 Representation-Agnostic Rendering Cleanup

Given any 3D representation, we can render a video along an arbitrary camera trajectory.
Some frames along this trajectory, at exact or near training viewpoints, will look clean, while others contain artifacts.
Rather than fixing frames independently, FixAnything processes the entire rendering video at once, leveraging temporal context from clean frames to guide the cleanup of degraded ones.

Concretely, let 𝐱∈ℝT×3×H×W\mathbf{x}\in\mathbb{R}^{T\times 3\times H\times W} be a rendering video along a camera trajectory, and let 𝐦∈{0,1}T\mathbf{m}\in\{0,1\}^{T} be a binary mask where 𝐦i=1\mathbf{m}\_{i}=1 marks frames rendered from training viewpoints (clean) and 𝐦i=0\mathbf{m}\_{i}=0 marks the rest (degraded).
FixAnything produces a clean video 𝐲∈ℝT×3×H×W\mathbf{y}\in\mathbb{R}^{T\times 3\times H\times W} that preserves scene content and camera motion while fixing degraded frames.
This formulation is representation-agnostic as renderings from NeRF, 3DGS, meshes, and point clouds look different, but all preserve the camera trajectory and coarse scene layout, providing the structure a pretrained video model can leverage to remove artifacts ([Fig. 3](#S3.F3 "In 3.1 Representation-Agnostic Rendering Cleanup ‣ 3 Method ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors")).

![Refer to caption](2608.23549v1/data_artifact_types.png)

### 3.2 Lightweight Adaptation of a Pretrained Video Model

FixAnything builds on Wan2.1-I2V-14B [[32](#bib.bib15)], a DiT-based [[25](#bib.bib47)] image-to-video diffusion model trained with rectified flow.
We repurpose it for rendering cleanup by channel-wise concatenating the rendering video as conditioning signal and training a lightweight LoRA [[10](#bib.bib26)] adapter, keeping the architecture unchanged.

#### Conditioning via channel concatenation.

We operate in the latent space of the pretrained VAE.
Let 𝐳cond=ℰ⁡(𝐱)\mathbf{z}\_{\mathrm{cond}}=\mathcal{E}(\mathbf{x}) denote the VAE-encoded latent of the degraded video and 𝐳0=ℰ⁡(𝐲)\mathbf{z}\_{0}=\mathcal{E}(\mathbf{y}) the latent of the clean target.
At each timestep t∈[0,1]t\in[0,1], we form the noised latent via the rectified flow interpolation:

|  |  |  |  |
| --- | --- | --- | --- |
|  | 𝐳t=(1−t)​𝐳0+t​ϵ,ϵ∼𝒩⁡(𝟎,𝐈).\mathbf{z}\_{t}=(1-t)\,\mathbf{z}\_{0}+t\,\boldsymbol{\epsilon},\hskip 10.00002pt\boldsymbol{\epsilon}\sim\mathcal{N}(\mathbf{0},\mathbf{I}). |  | (1) |

The degraded video latent 𝐳cond\mathbf{z}\_{\mathrm{cond}} carries the camera trajectory and coarse scene layout that the model should preserve; we inject it by concatenating with 𝐳t\mathbf{z}\_{t} and a spatially broadcast version of the mask 𝐦\mathbf{m} along the channel dimension:

|  |  |  |  |
| --- | --- | --- | --- |
|  | 𝐳^t=[𝐳t;𝐳cond;𝐦],\hat{\mathbf{z}}\_{t}=[\mathbf{z}\_{t}\,;\,\mathbf{z}\_{\mathrm{cond}}\,;\,\mathbf{m}], |  | (2) |

where [⋅;⋅][\cdot\,;\,\cdot] denotes channel-wise concatenation.
Given this augmented input, the model 𝐯θ\mathbf{v}\_{\theta} predicts the velocity field 𝐯=ϵ−𝐳0\mathbf{v}=\boldsymbol{\epsilon}-\mathbf{z}\_{0} and is trained with the flow matching objective [[21](#bib.bib20), [18](#bib.bib19)]:

|  |  |  |  |
| --- | --- | --- | --- |
|  | ℒFM=𝔼𝐳0,ϵ,t​[‖𝐯−𝐯θ​(𝐳^t,t)‖2].\mathcal{L}\_{\mathrm{FM}}=\mathbb{E}\_{\mathbf{z}\_{0},\,\boldsymbol{\epsilon},\,t}\left[\left\|\mathbf{v}-\mathbf{v}\_{\theta}(\hat{\mathbf{z}}\_{t},t)\right\|^{2}\right]. |  | (3) |

#### Mask-aware conditioning: what to trust vs. what to fix.

A rendering video from a sparse reconstruction is not uniformly degraded.
Frames near training viewpoints may look nearly perfect, while frames further away can be severely corrupted.
Naively asking a generative model to “clean up” the entire video has a problem: the model cannot easily distinguish frames that are already correct from those that need fixing, and may hallucinate over content that should be preserved.

The mask 𝐦\mathbf{m} resolves this by making the distinction explicit: entries corresponding to training poses are set to 11 (trust) and all others to 00 (fix).
This provides two signals.
First, it knows which frames to leave untouched, preventing unnecessary hallucination over already-clean content.
Second, the clean frames become anchors that provide context for the degraded ones: the model can propagate appearance, lighting, and scene structure from trusted/clean frames to their neighbors, rather than guessing from scratch.
Although the mask itself is binary, its temporal arrangement is informative: degradation severity typically increases with distance from the nearest anchor, so the model implicitly learns to modulate the strength of its refinement accordingly.
[Fig. 4](#S3.F4 "In Mask-aware conditioning: what to trust vs. what to fix. ‣ 3.2 Lightweight Adaptation of a Pretrained Video Model ‣ 3 Method ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors") illustrates both effects, and quantitatively, removing the mask degrades PSNR by 1.3 dB ([Tab. 3](#S4.T3 "In 4.3 Effect of Geometry-Aware Preference Optimization ‣ 4 Experiments ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors")).

![Refer to caption](2608.23549v1/mask_comparison.png)

#### LoRA finetuning.

We adapt the model using LoRA [[10](#bib.bib26)] with rank 6464, updating less than 1% of the total parameters while keeping the base model weights and the VAE frozen.
This minimal adaptation is sufficient because the task is narrower than general video generation: the model only needs to learn to condition on the degraded input, not to generate videos entirely from scratch.

### 3.3 Training Data

We build training data of paired videos of degraded renderings and their clean ground-truth counterparts from DL3DV-10K [[17](#bib.bib28)], which provides diverse videos with precomputed COLMAP [[29](#bib.bib27)] reconstructions.
For each scene, we uniformly sample k∈[3,12]k\in[3,12] frames as training views and extract 61-frame trajectories that pass through at least two of them.
We then render each trajectory from four representation types to produce diverse degraded-clean pairs ([Fig. 3](#S3.F3 "In 3.1 Representation-Agnostic Rendering Cleanup ‣ 3 Method ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors")):

NeRF [[23](#bib.bib2)]: we run Nerfacto [[30](#bib.bib31)] on the sparse training views, with characteristic blur and fog artifacts at novel viewpoints.

3DGS [[13](#bib.bib3)]: we initialize from a random point cloud and fit a model with gsplat [[40](#bib.bib35)] for 7K iterations, deliberately underfitting so that novel viewpoints exhibit visible artifacts while training viewpoints render cleanly.

Meshes: we run MapAnything [[12](#bib.bib36)], a feed-forward 3D reconstruction model, on the training views and fit a triangular mesh from the predicted depths. Frames at training viewpoints are replaced with the original images because depth is unreliable at sky regions and occlusion boundaries.

Sparse point clouds: we retain only COLMAP keypoints visible in the selected training views. Because these points exist only at detected keypoints and lack coverage in textureless regions (e.g., sky or walls), we replace frames at training viewpoints with the captured images to provide richer context.

#### Data efficiency.

As the pretrained video model already encodes strong priors about videos, the training data only needs to teach it to condition on degraded input, a simpler task than learning video generation from scratch.
Therefore, LoRA finetuning requires remarkably little data: 20 paired videos already produce effective rendering cleanup, and scaling to 500 yields further improvements ([Tab. 5](#S4.T5 "In Data efficiency and inference speed. ‣ 4.4 Ablation Studies ‣ 4 Experiments ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors")).
By comparison, prior methods require 80K–150K image pairs [[35](#bib.bib10), [20](#bib.bib9)].

### 3.4 Geometry-Aware Preference Optimization

The flow matching loss ([Eq. 3](#S3.E3 "In Conditioning via channel concatenation. ‣ 3.2 Lightweight Adaptation of a Pretrained Video Model ‣ 3 Method ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors")) encourages per-frame visual quality but does not explicitly enforce multi-view geometric consistency.
In practice, the supervised fine-tuning (SFT) model sometimes hallucinates structures that look plausible in individual frames but are geometrically inconsistent across views.
[Fig. 5](#S3.F5 "In Flow-DPO training. ‣ 3.4 Geometry-Aware Preference Optimization ‣ 3 Method ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors") (row 2) shows a typical failure: the model generates a tree-like structure (red boxes) that shifts position and shape across frames.
When SfM (e.g., COLMAP [[29](#bib.bib27)]) is run on such outputs, it tracks these inconsistent features and recovers incorrect camera poses, a signal that we can use to improve the model.

#### Pose accuracy as a reward.

We quantify geometric consistency by measuring how well camera poses can be recovered from a generated video.
For each output, we run COLMAP [[29](#bib.bib27)] with SuperPoint [[6](#bib.bib37)] features and LightGlue [[16](#bib.bib38)] matching to estimate their camera poses, and compare against the known ground-truth.
We report the Area Under the Curve at a 5° threshold (AUC@5°) over both relative rotation accuracy (RRA) and relative translation accuracy (RTA) [[11](#bib.bib39)].
Geometrically consistent videos yield high AUC because SfM reliably recovers their poses; videos with hallucinated or inconsistent geometry produce low scores.

#### Constructing preference pairs.

For a separate set of 1,000 DL3DV scenes, we generate five candidate outputs per scene using different random seeds and rank them by AUC@5°.
We construct preference pairs (𝐲w,𝐲l)(\mathbf{y}\_{w},\mathbf{y}\_{l}) by pairing higher-ranked outputs against lower-ranked ones, retaining only pairs with an AUC gap of at least 0.2 to ensure a clear preference signal.

#### Flow-DPO training.

We optimize the model using Flow-DPO [[19](#bib.bib21)], which adapts DPO [[27](#bib.bib22)] to rectified flow models.
Let 𝐯w=ϵw−𝐳0w\mathbf{v}^{w}=\boldsymbol{\epsilon}^{w}-\mathbf{z}\_{0}^{w} and 𝐯l=ϵl−𝐳0l\mathbf{v}^{l}=\boldsymbol{\epsilon}^{l}-\mathbf{z}\_{0}^{l} denote the target velocity fields for the preferred and dispreferred samples.
The loss is:

|  |  |  |  |
| --- | --- | --- | --- |
|  | ℒDPO=−𝔼⁡[log⁡σ⁡(−β2​(Δw−Δl))],\mathcal{L}\_{\mathrm{DPO}}=-\mathbb{E}\left[\log\sigma\!\left(-\frac{\beta}{2}\left(\Delta\_{w}-\Delta\_{l}\right)\right)\right], |  | (4) |

where Δw=‖𝐯w−𝐯θ​(𝐳tw,t)‖2−‖𝐯w−𝐯ref​(𝐳tw,t)‖2\Delta\_{w}=\|\mathbf{v}^{w}-\mathbf{v}\_{\theta}(\mathbf{z}\_{t}^{w},t)\|^{2}-\|\mathbf{v}^{w}-\mathbf{v}\_{\mathrm{ref}}(\mathbf{z}\_{t}^{w},t)\|^{2} and Δl\Delta\_{l} is defined analogously for the dispreferred sample, with 𝐯ref\mathbf{v}\_{\mathrm{ref}} being the SFT (LoRA finetuned) checkpoint.
This loss steers the model toward outputs that SfM methods can reconstruct accurately.
Because the geometric prior is baked into the learned LoRA adapter during training, no pose estimation is needed at inference.

![Refer to caption](2608.23549v1/dpo_comparison.png)

### 3.5 Inference

At inference time, the user provides a rendering video 𝐱\mathbf{x} and a mask 𝐦\mathbf{m} indicating which frames are clean.
FixAnything produces a cleaned video by sampling from Gaussian noise ϵ∼𝒩⁡(𝟎,𝐈)\boldsymbol{\epsilon}\sim\mathcal{N}(\mathbf{0},\mathbf{I}) at t=1t=1 and integrating the learned velocity field 𝐯θ\mathbf{v}\_{\theta} toward t=0t=0, with the rendering video and mask provided as conditioning via channel concatenation ([Eq. 2](#S3.E2 "In Conditioning via channel concatenation. ‣ 3.2 Lightweight Adaptation of a Pretrained Video Model ‣ 3 Method ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors")).
The process follows the standard flow matching ODE, and we use 50 denoising steps by default.
For scenes with more frames than the model’s temporal window, we split the video into overlapping chunks of 61 frames.
Notably, we observe that reducing the number of denoising steps to 5 still produces reasonable results with a 10×\times speedup ([Tab. 5](#S4.T5 "In Data efficiency and inference speed. ‣ 4.4 Ablation Studies ‣ 4 Experiments ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors")).

## 4 Experiments

### 4.1 Experimental Setup

#### Implementation details.

We finetune Wan2.1-I2V-14B [[32](#bib.bib15)] using LoRA with rank 64 on 500 paired DL3DV-10K [[17](#bib.bib28)] videos at 288×512288\times 512 resolution first, then upgrade to 480×832480\times 832 with T=61T{=}61 frames per video.
SFT training runs for 3000 iterations on a single H100 GPU.
Flow-DPO training uses the SFT checkpoint as reference and further optimizes the LoRA adapter for 2000 additional iterations.
At inference, we use 50 denoising steps by default and process videos in overlapping chunks of 61 frames.

#### Dataset and evaluation protocol.

Following the test splits of 3DGS-Enhancer [[20](#bib.bib9)] and Xu et al. [[37](#bib.bib33)], we evaluate on 20 held-out scenes from DL3DV-10K dataset [[17](#bib.bib28)], where we uniformly select 3, 6, or 9 frames as training views from each test scene.
The remaining frames (excluding training views) are sampled at every 8th frame to form the query set.
We report standard metrics PSNR, SSIM, and LPIPS [[45](#bib.bib40)] to measure synthesized image quality, and AUC@5° of relative rotation accuracy (RRA) and relative translation accuracy (RTA) to measure geometric consistency of the generated videos.

#### Baselines.

We compare against two groups of methods.
Sparse-view reconstruction methods train a 3D representation using few input views: 3DGS [[13](#bib.bib3)], RegNeRF [[24](#bib.bib5)], FreeNeRF [[38](#bib.bib6)], DNGaussian [[15](#bib.bib7)], and FSGS [[47](#bib.bib8)].
Post-hoc enhancement methods refine the output of an existing reconstruction (3DGS rendering): 3DGS-Enhancer [[20](#bib.bib9)], Xu et al. [[37](#bib.bib33)], and Difix3D+ [[35](#bib.bib10)].
For FixAnything, we report results using four different input representations, all built from the same sparse training views following the protocol in [Sec. 3.3](#S3.SS3 "3.3 Training Data ‣ 3 Method ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors").
All four use the same single model, and only the rendering input changes.

### 4.2 Comparison with Prior Methods

[Tab. 1](#S4.T1 "In 4.2 Comparison with Prior Methods ‣ 4 Experiments ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors") compares FixAnything against prior methods on DL3DV under 3-view, 6-view, and 9-view settings.

|  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | 3 Views | | | 6 Views | | | 9 Views | | |
| Method | PSNR↑\uparrow | SSIM↑\uparrow | LPIPS↓\downarrow | PSNR↑\uparrow | SSIM↑\uparrow | LPIPS↓\downarrow | PSNR↑\uparrow | SSIM↑\uparrow | LPIPS↓\downarrow |
| Sparse-view reconstruction | | | | | | | | | |
| 3DGS [[13](#bib.bib3)]† | 10.97 | 0.248 | 0.567 | 13.34 | 0.332 | 0.498 | 14.99 | 0.403 | 0.446 |
| RegNeRF [[24](#bib.bib5)]† | 11.46 | 0.214 | 0.600 | 12.69 | 0.236 | 0.579 | 12.33 | 0.219 | 0.598 |
| FreeNeRF [[38](#bib.bib6)]† | 10.91 | 0.211 | 0.595 | 12.13 | 0.230 | 0.576 | 12.85 | 0.241 | 0.573 |
| DNGaussian [[15](#bib.bib7)]† | 11.10 | 0.273 | 0.579 | 12.67 | 0.329 | 0.547 | 13.44 | 0.365 | 0.539 |
| FSGS [[47](#bib.bib8)]† | 12.22 | 0.296 | 0.535 | 13.73 | 0.429 | 0.540 | 15.52 | 0.468 | 0.416 |
| Post-hoc enhancement (3DGS rendering) | | | | | | | | | |
| 3DGS-Enhancer [[20](#bib.bib9)]† | 14.33 | 0.424 | 0.464 | 16.94 | 0.565 | 0.356 | 18.50 | 0.630 | 0.305 |
| Xu et al. [[37](#bib.bib33)]† | 14.62 | 0.471 | 0.491 | 17.35 | 0.566 | 0.396 | 19.19 | 0.616 | 0.335 |
| Difix3D [[35](#bib.bib10)] | 12.85 | 0.392 | 0.557 | 14.84 | 0.445 | 0.462 | 16.76 | 0.520 | 0.399 |
| Difix3D+ [[35](#bib.bib10)] | 12.37 | 0.363 | 0.512 | 14.41 | 0.424 | 0.400 | 16.39 | 0.498 | 0.330 |
| FixAnything (Ours) – single model | | | | | | | | | |
| w/ NeRF rendering | 14.22 | 0.427 | 0.451 | 17.01 | 0.522 | 0.329 | 18.86 | 0.605 | 0.297 |
| w/ 3DGS rendering | 15.18 | 0.452 | 0.408 | 17.65 | 0.561 | 0.289 | 19.76 | 0.632 | 0.269 |
| w/ mesh rendering | 15.74 | 0.482 | 0.366 | 17.95 | 0.583 | 0.269 | 19.86 | 0.646 | 0.233 |
| w/ sparse SfM points | 15.52 | 0.463 | 0.381 | 17.74 | 0.568 | 0.271 | 19.72 | 0.624 | 0.241 |

Sparse-view reconstruction methods struggle in this setting: 3DGS produces visible floater artifacts, while regularization-based approaches (RegNeRF, FreeNeRF, DNGaussian) improve geometry but cannot complete content in under-observed regions.
Among post-hoc enhancement methods, 3DGS-Enhancer [[20](#bib.bib9)], Xu et al. [[37](#bib.bib33)], and Difix3D+ [[35](#bib.bib10)] demonstrate the value of generative priors, achieving substantial gains over all sparse-view baselines.
FixAnything achieves competitive or superior performance on the 3DGS input while being simpler to implement and easier to adapt to future video backbones.
[Fig. 7](#S4.F7 "In 4.2 Comparison with Prior Methods ‣ 4 Experiments ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors") shows a qualitative comparison with Difix3D and Difix3D+ which produce sharper individual images but struggle with cross-view consistency, whereas FixAnything produces temporally coherent output.

Notably, the same model also cleans up mesh renderings and sparse point clouds to comparable quality ([Tab. 1](#S4.T1 "In 4.2 Comparison with Prior Methods ‣ 4 Experiments ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors"), bottom rows), despite these inputs providing far less visual information than 3DGS.
[Fig. 6](#S4.F6 "In 4.2 Comparison with Prior Methods ‣ 4 Experiments ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors") shows qualitative results: even when the input consists of sparse COLMAP keypoints with clean
training views interspersed along the trajectory, the model produces dense, photorealistic output.
This supports the finding from [Sec. 3.1](#S3.SS1 "3.1 Representation-Agnostic Rendering Cleanup ‣ 3 Method ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors") that the rendering primarily serves as a structural scaffold while the video prior fills in the rest.

In supplementary materials, we further evaluate our model on MipNeRF-360 [[2](#bib.bib4)] and LLFF [[22](#bib.bib17)], where FixAnything (using 3DGS input) achieves comparable performance to SOTA methods [[43](#bib.bib11), [37](#bib.bib33)] with a notable improvement in LPIPS, showing strong cross-dataset generalization.

![Refer to caption](2608.23549v1/tracks_results.png)
![Refer to caption](2608.23549v1/qualitative_compare.png)

### 4.3 Effect of Geometry-Aware Preference Optimization

[Tab. 3](#S4.T3 "In 4.3 Effect of Geometry-Aware Preference Optimization ‣ 4 Experiments ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors") compares the SFT-only model against the full model after Flow-DPO training, with camera pose accuracy as a reward signal to construct preference pairs for Flow-DPO ([Sec. 3.4](#S3.SS4 "3.4 Geometry-Aware Preference Optimization ‣ 3 Method ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors")).
While image quality metrics (PSNR, SSIM, LPIPS) improve modestly, the primary gain is in geometric consistency: AUC@5° improves by 7.2%, so COLMAP recovers more accurate camera poses from the DPO-refined outputs.
[Fig. 5](#S3.F5 "In Flow-DPO training. ‣ 3.4 Geometry-Aware Preference Optimization ‣ 3 Method ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors") illustrates why: the SFT-only model can produce frames that look clean but contain hallucinations (red boxes), causing SfM to fail.
After Flow-DPO training, these hallucinations are suppressed and the model produces geometrically coherent output closely matching the ground truth.
Crucially, this improvement comes at no additional inference cost as the geometric prior is baked into the model weights (LoRA adapter) during DPO training.

| Method | PSNR↑\uparrow | SSIM↑\uparrow | LPIPS↓\downarrow | AUC@5°↑\uparrow |
| --- | --- | --- | --- | --- |
| SFT only | 17.51 | 0.554 | 0.296 | 61.12 |
| +DPO | 17.65 | 0.561 | 0.289 | 68.32 |

| Variant | PSNR↑\uparrow | SSIM↑\uparrow | LPIPS↓\downarrow |
| --- | --- | --- | --- |
| No mask | 16.37 | 0.525 | 0.311 |
| With mask | 17.65 | 0.561 | 0.289 |

### 4.4 Ablation Studies

We ablate the remaining design choices on DL3DV-10K with 6 training views.

#### Mask-aware conditioning.

[Tab. 3](#S4.T3 "In 4.3 Effect of Geometry-Aware Preference Optimization ‣ 4 Experiments ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors") compares a variant with all mask entries set to 1 (no trust/fix distinction) against the full model.
Providing the mask improves PSNR by 1.3 dB: without it, the model must infer degradation severity from the visual signal alone, which is ambiguous since some clean frames resemble mildly degraded ones, causing hallucination over content that should be preserved.

#### Data efficiency and inference speed.

[Tab. 5](#S4.T5 "In Data efficiency and inference speed. ‣ 4.4 Ablation Studies ‣ 4 Experiments ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors") shows that 20 paired videos already produce effective cleanup, with diminishing returns beyond 100, showing that the pretrained model already captures most necessary priors and the paired data primarily teaches the conditioning mechanism.
[Tab. 5](#S4.T5 "In Data efficiency and inference speed. ‣ 4.4 Ablation Studies ‣ 4 Experiments ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors") shows that reducing denoising steps from 50 to 5 yields comparable quality across all metrics while providing a 10×10\times speedup, generating a 61-frame clip at 480×832480{\times}832 resolution in 31 seconds on a single H100.
This opens the door to further acceleration through distillation [[41](#bib.bib41)], potentially enabling real-time rendering cleanup.

| Training vids. | PSNR↑\uparrow | SSIM↑\uparrow | LPIPS↓\downarrow |
| --- | --- | --- | --- |
| 20 | 16.70 | 0.531 | 0.309 |
| 50 | 17.20 | 0.548 | 0.297 |
| 100 | 17.45 | 0.556 | 0.292 |
| 500 | 17.65 | 0.561 | 0.289 |

| Steps | PSNR↑\uparrow | SSIM↑\uparrow | LPIPS↓\downarrow | Time (s) |
| --- | --- | --- | --- | --- |
| 5 | 18.02 | 0.574 | 0.313 | 31 |
| 10 | 17.91 | 0.570 | 0.296 | 62 |
| 25 | 17.75 | 0.564 | 0.289 | 155 |
| 50 | 17.65 | 0.561 | 0.289 | 309 |

## 5 Discussion: Hallucination and Uncertainty

A natural concern with generative cleanup is *hallucination*.
We define *hallucination* as content the model must invent when it is not seen in the input views.
However, we emphasize that hallucination is not inherently a failure: it is what makes generative cleanup useful by plausibly filling in unobserved regions, and it becomes a failure only when it contradicts the existing observations.

This raises a practical question: can we tell where the model is hallucinating?
As a preliminary analysis, we run inference N=5N{=}5 times with different random seeds and use the per-pixel standard deviation as an uncertainty estimate ([Fig. 8](#S5.F8 "In 5 Discussion: Hallucination and Uncertainty ‣ FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors"); black pixels denote occluded or unobserved regions).
Sky- and ground-like regions show *low* uncertainty, where the model confidently propagates the input texture, while regions with multiple plausible completions (e.g., buildings) show *high* uncertainty.
This uncertainty measurement also correlates well with regions of high reconstruction error: on DL3DV (6 views), the mean PSNR over the most-confident 25% of pixels is 25.7 dB versus 14.4 dB over the least-confident 25%.
This points to a simple, training-free way to quantify uncertainty, a promising step toward making generative cleanup more reliable.

![Refer to caption](2608.23549v1/uncertainty.png)

## 6 Conclusion

We present a single model for removing artifacts across multiple 3D representations, including 3DGS, NeRF, meshes, and point clouds, by finetuning a pretrained video diffusion model on a modest set of paired videos. Our results suggest that many representations can be cleaned up equally well, raising questions about common reconstruction pipelines. Given NN input images, existing workflows typically estimate camera poses with COLMAP, learn a representation such as NeRF or 3DGS from the posed views, and finally refine rendered views with a generative model. Our experiments indicate that comparable results can be obtained by instead rendering sparse COLMAP point clouds (optionally meshed via multi-view stereo) and applying generative cleanup directly.

More broadly, our observations suggest that the main difficulty in novel-view rendering arises in regions that are weakly observed or unobserved. In these areas, classical reconstruction methods struggle because the problem becomes one of plausible completion rather than geometric inference. This points to an alternative strategy: reconstruct reliable geometry where observations exist, and use generative models to infer missing content where they do not. Future work could explore feeding such generative predictions back into reconstruction pipelines to produce more complete and consistent 3D scene models.

Acknowledgments
We thank Shubham Tulsiani, Nikhil Keetha, Sriram Narayanan, Anurag Ghosh, and other members of Deva’s and Srinivas’ groups at CMU for their valuable feedback and suggestions at various stages of this project.
This work used Bridges-2 [[4](#bib.bib18)] at Pittsburgh Supercomputing Center through allocation cis240119p from the Advanced Cyberinfrastructure Coordination Ecosystem: Services & Support (ACCESS) program, which is supported by National Science Foundation grants #2138259, #2138286, #2138307, #2137603, and #2138296.
This work was supported by Intelligence Advanced Research Projects Activity (IARPA) via Department of Interior/Interior Business Center (DOI/IBC) contract number 140D0423C0074. The U.S. Government is authorized to reproduce and distribute reprints for Governmental purposes notwithstanding any copyright annotation thereon. Disclaimer: The views and conclusions contained herein are those of the authors and should not be interpreted as necessarily representing the official policies or endorsements, either expressed or implied, of IARPA, DOI/IBC, or the U.S. Government.

## References

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