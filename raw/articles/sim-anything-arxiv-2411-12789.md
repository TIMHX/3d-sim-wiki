---
source_url: https://arxiv.org/abs/2411.12789
ingested: 2026-08-24
sha256: d9eec5fe58cda9013fcd3ca2bab24f87dc6f7645db8985d8c126f7ecdea5ed0d
---
##### Report GitHub Issue

Content selection saved. Describe the issue below:

![](/static/base/1.0.1/images/icons/smileybones-small.svg)
![arXiv logo](/static/base/1.0.1/images/arxiv-logo-primary-light.svg)

# Sim Anything: Automated 3D Physical Simulation of Open-world Scene with Gaussian Splatting

###### Abstract

Recent advancements in 3D generation models have opened new possibilities for simulating dynamic 3D object movements and customizing behaviors, yet creating this content remains challenging.
Current methods often require manual assignment of precise physical properties for simulations or rely on video generation models to predict them, which is computationally intensive.
In this paper, we rethink the usage of multi-modal large language model (MLLM) in physics-based simulation, and present Sim Anything, a physics-based approach that endows static 3D objects with interactive dynamics.
We begin with detailed scene reconstruction and object-level 3D open-vocabulary segmentation, progressing to multi-view image in-painting.
Inspired by human visual reasoning, we propose MLLM-based Physical Property Perception (MLLM-P3) to predict mean physical properties of objects in a zero-shot manner. Based on the mean values and the object’s geometry, the Material Property Distribution Prediction model (MPDP) model then estimates the full distribution, reformulating the problem as probability distribution estimation to reduce computational costs. Finally, we simulate objects in an open-world scene with particles sampled via the Physical-Geometric Adaptive Sampling (PGAS) strategy, efficiently capturing complex deformations and significantly reducing computational costs.
Extensive experiments and user studies demonstrate our Sim Anything achieves more realistic motion than state-of-the-art methods within 2 minutes on a single GPU.
Our project page is at <https://sim-gs.github.io/>.

![[Uncaptioned image]](2411.12789v1/first.png)

## 1 Introduction

With the development in 3D representation, Neural Radiance Fields (NeRF) [mildenhall2021nerf](#bib.bib25) and 3D Gaussian Splatting (3DGS) [kerbl20233d](#bib.bib17) offer new perspectives for 3D reconstruction and 3D representation [wang2024prolificdreamer](#bib.bib37); [tang2023dreamgaussian](#bib.bib36). However, these approaches are unable to simulate interactions with 3D assets in simulation environments [savva2019habitat](#bib.bib33); [xia2018gibson](#bib.bib39), which is s critical for generating realistic object responses to novel interactions, such as external forces or agent manipulations in many applications, e.g., virtual reality [jiang2024vr](#bib.bib16), embodied intelligence [lu2024manigaussian](#bib.bib24).

Some recent approaches aim to bridge the gap between rendering and simulation integrating physics-based priors into 3D object representations using physical simulators [chen2022virtual](#bib.bib4); [qiu2024feature](#bib.bib28); [feng2024pie](#bib.bib7). For instance, PAC-NeRF [li2023pac](#bib.bib21) estimates the geometry and physical parameters of objects from multi-view videos and then integrates physical models with NeRF-based representations.
Similarly, PhysGaussian [xie2024physgaussian](#bib.bib40) first injects physical parameters into 3DGS objects, and then predicts motion using a physics-based simulator. However, their ability to handle real objects is limited, as they require a predefined material model with manually assigned parameters or rely on multi-view videos to predict the physical properties of each objects.

To automatically set parameters, some approaches [liu2024physics3d](#bib.bib22); [huang2024dreamphysics](#bib.bib14); [zhang2024physdreamer](#bib.bib45) leverage video generation models [blattmann2023stable](#bib.bib2) which are trained on real-world video data to estimate physical material parameters. For example, PhysDreamer [zhang2024physdreamer](#bib.bib45) employs stable video diffusion model to learn Young’s modulus of objects.
However, learning material physical properties from video diffusion priors is computationally expensive and time-consuming in practice. Moreover, video diffusion models have limited controllability and often fail to obey physical laws [ren2023dreamgaussian4d](#bib.bib31); [zhao2023animate124](#bib.bib50). Additionally, these models are also generally restricted to non-rigid objects, making them unsuitable for deriving the physical properties of large rigid objects (such as cup, bowl, and chairs).
However, humans are remarkably adept at predicting physical properties of objects based on visual information [fleming2014visual](#bib.bib8); [fleming2013perceptual](#bib.bib9). We therefore ask this question: how can we develop models for perceiving physics from just visual data?

To this end, we rethink physics-based simulation and the usage of multi-modal large language model (MLLM), such as GPT-4V [yang2023dawn](#bib.bib41). In this paper, we propose Sim Anything, a novel physics-based method that transforms static 3D objects into interactive ones capable of responding to new interactions, as shown in Fig. [1](#S0.F1 "Figure 1 ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting"). We first segment objects in an open-word scene with priors from foundation models [liu2023grounding](#bib.bib23); [kirillov2023segment](#bib.bib19); [zhang2024recognize](#bib.bib46).
Inspired by how humans predict physical properties of objects through visual data, our Sim Anything leverages MLLM-based Physical Property Perception (MLLM-P3) to predict the mean values of physical properties. Unlike previous methods [zhang2024physdreamer](#bib.bib45); [liu2024physics3d](#bib.bib22); [huang2024dreamphysics](#bib.bib14) iteratively refining each physical properties through video analysis, we reformulate this problem from a regression task to a probability distribution estimation task by predicting the full range of these properties based on the mean value and the object’s geometry, reducing computational demands.
Finally, our approach simulates object interactions in an open-world scene with driving particles sampled by the Physical-Geometric Adaptive Sampling (PGAS) strategy, enabling a seamless integration of realistic physics with adaptable sampling precision.
Extensive experiments and user studies demonstrate that Sim Anything achieves more accurate physical property prediction and synthesizes more realistic motion with much faster inference time. We provide an overview of the comparison to major prior works in Tab. [1](#S1.T1 "Table 1 ‣ 1 Introduction ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting"). In summary, our work makes the following contributions:

Sim Anything is the first to use MLLM for zero-shot physical property estimation of objects in 3D scenes.

We reformulate physical property estimation as a probability distribution task, enabling adaptable physical simulations with PGAS in open-world scenes.

Experiments show Sim Anything effectively predict physical properties and creates realistic 3D dynamics.

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| automatic parameter computation | fast inference time | physics-based deformation | static 3D object input | scene-wide physical simulation |  |
| ✗ | ✓ | ✓ | ✓ | ✗ | PhysGaussian [xie2024physgaussian](#bib.bib40) |
| ✗ | ✗ | ✗ | ✓ | ✗ | DreamGaussian4D [ren2023dreamgaussian4d](#bib.bib31) |
| ✗ | ✗ | ✗ | ✓ | ✗ | Animate124 [zhao2023animate124](#bib.bib50) |
| ✗ | ✓ | ✓ | ✗ | ✗ | PAC-NeRF [li2023pac](#bib.bib21) |
| ✗ | ✓ | ✓ | ✗ | ✗ | PIE-NeRF [feng2024pie](#bib.bib7) |
| ✗ | ✓ | ✓ | ✗ | ✗ | Spring-Gaus [zhong2024reconstruction](#bib.bib51) |
| ✓ | ✗ | ✓ | ✓ | ✗ | PhysDreamer [zhang2024physdreamer](#bib.bib45) |
| ✓ | ✗ | ✓ | ✓ | ✗ | DreamPhysics [huang2024dreamphysics](#bib.bib14) |
| ✓ | ✗ | ✓ | ✓ | ✗ | PhysDreamer [zhang2024physdreamer](#bib.bib45) |
| ✓ | ✗ | ✓ | ✓ | ✗ | Physics3D [liu2024physics3d](#bib.bib22) |
| ✓ | ✓ | ✓ | ✓ | ✓ | Ours |

## 2 Related Work

### 2.1 Dynamic 3D Animation

The demand for dynamic 3D animation creation has grown significantly across various applications, including video games, virtual reality, and robotic simulation [healey2021mixed](#bib.bib11); [zhao2024chase](#bib.bib47); [zhao2024sg](#bib.bib48); [zhao2024hfgs](#bib.bib49). With the success of video generative models, some methods [zhao2023animate124](#bib.bib50) have attempted to leverage video diffusion models to guide the prediction of 3D deformations. For instance, DreamGaussian4D [ren2023dreamgaussian4d](#bib.bib31) uses pre-generated videos to supervise the deformation of static scenes. However, the deformations produced by these methods may not always be accurate or physically plausible.

Recent works [modi2024simplicits](#bib.bib26); [zhong2024reconstruction](#bib.bib51) introduce physics simulation to the 3D deformation and enable synthesizing motions under any physical interactions. Virtual Elastic Objects [chen2022virtual](#bib.bib4) jointly reconstructs the geometry, appearances, and physical parameters of elastic objects with multi-view data. Spring-Gaus [zhong2024reconstruction](#bib.bib51) integrate a 3D Spring-Mass model into 3D Gaussian kernels, and then simulate elastic objects from videos of the object from multiple viewpoints.
PAC-NeRF [li2023pac](#bib.bib21) and PhysGaussian [xie2024physgaussian](#bib.bib40) integrate physics-based simulations with NeRF [mildenhall2021nerf](#bib.bib25) and 3DGS [kerbl20233d](#bib.bib17), respectively, to model the deformation of elastic objects. However, these methods either require manual setup of physical properties for 3D objects before simulation or depend on multi-view videos to predict physical properties.

To avoid manually setting parameters, some works estimate physical material parameters with video generation model [blattmann2023stable](#bib.bib2) to estimate physical material parameters [huang2024dreamphysics](#bib.bib14). PhysDreamer [zhang2024physdreamer](#bib.bib45) and DreamPhysics [huang2024dreamphysics](#bib.bib14) leverage video generation models to estimate physical material parameter (e.g., Young’s modulus), while Physics3D [liu2024physics3d](#bib.bib22) further optimizes a wider range of physical parameters for 3D objects. However, these methods are computationally expensive, as learning material properties through video diffusion priors is time-consuming. Moreover, the controllability of generated videos is limited, often deviating from physical laws [ren2023dreamgaussian4d](#bib.bib31); [zhao2023animate124](#bib.bib50), which we further demonstrate in the experimental Section [5.4](#S5.SS4 "5.4 Comparison with SOTA Methods ‣ 5 Experiments ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting").
Additionally, these models are typically restricted to non-rigid objects, making them unsuitable for determining the physical properties of large rigid objects, such as tables, chairs, and sofas. Inspired by how humans perceive physical properties of the objects  [fleming2014visual](#bib.bib8); [fleming2013perceptual](#bib.bib9), we propose leveraging multi-modal large language models (MLLMs) to zero-shot predict the mean values of physical properties for objects in a 3D scene, enabling faster inference times. We then use the proposed MPDP model to predict the full distribution of these properties.

### 2.2 Visual Physics Perception

Physics perception is a long-standing challenging problem [wu2015galileo](#bib.bib38). Previous studies demonstrate that deep learning models can potentially exhibit physical perception abilities similar to humans [bell2015material](#bib.bib1); [hu2011toward](#bib.bib12). Most prior research focuses on dynamically addressing object properties, either by observing the target’s behavior [li2023pac](#bib.bib21) or by interacting with it in a 3D physical engine [pinto2016curious](#bib.bib27); [yao2023estimating](#bib.bib42). Other works also explore the estimation of material properties directly from static images [bell2015material](#bib.bib1); [sharan2013recognizing](#bib.bib34). However, these works mostly focus on specific material properties, such as mass or tenderness, often relying on task-specific data. In contrast, we propose leveraging MLLM, such as GPT-4V [yang2023dawn](#bib.bib41), to generate a wide range of physical properties such as mass, Young’s modulus, and Poisson’s ratio in a zero-shot manner.

## 3 Preliminaries

### 3.1 Material Point Method

The Material Point Method (MPM)[hu2018moving](#bib.bib13) is a popular simulation framework for multi-physics phenomena due to its capability to handle topology changes and frictional interactions. Unlike mesh-based methods, MPM represents the continuum using particles in a grid-based space, making it well-suited for point-based 3D Gaussian representation. Following PhysGaussian[xie2024physgaussian](#bib.bib40), we define each Gaussian kernel’s time-dependent state as:

|  |  |  |  |
| --- | --- | --- | --- |
|  | xi​(t)=Δ⁡(xi,t),Σi​(t)=Fi​(t)​Σi​Fi​(t)T,x\_{i}(t)=\Delta(x\_{i},t),\ \Sigma\_{i}(t)=F\_{i}(t)\Sigma\_{i}F\_{i}(t)^{T}, |  | (1) |

where Δ⁡(⋅,t)\Delta(\cdot,t) and Fi​(t)F\_{i}(t) denote coordinate deformation and deformation gradient at timestep tt. The viewpoint must also adjust with the continuum rotation Ωi​(t)\Omega\_{i}(t) to match the view direction of the spherical harmonic coefficient CiC\_{i}.

### 3.2 3D Gaussian Splatting (3DGS)

3D Gaussian Splatting (3DGS) represents scenes as point clouds, with each point modeled as a 3D Gaussian defined by a center point 𝒳\mathcal{X} (mean) and a covariance matrix Σ\Sigma. Each Gaussian at 𝒳\mathcal{X} is given by G⁡(𝒳)=e−12​𝒳T​Σ−1​𝒳G(\mathcal{X})=e^{-\frac{1}{2}\mathcal{X}^{T}\Sigma^{-1}\mathcal{X}}. Σ\Sigma is decomposed into a scaling matrix 𝒮\mathcal{S} and rotation matrix ℛ\mathcal{R}, such that Σ=ℛ​𝒮​𝒮T​ℛT\Sigma=\mathcal{R}\mathcal{S}\mathcal{S}^{T}\mathcal{R}^{T}, with 𝒮\mathcal{S} and ℛ\mathcal{R} stored as vectors s∈ℝN×3s\in\mathbb{R}^{N\times 3} and r∈ℝN×4r\in\mathbb{R}^{N\times 4}, respectively. Differential splatting [yifan2019differentiable](#bib.bib44) applies a viewing transform WW and Jacobian JJ to compute the transformed covariance Σ′=J​W​Σ​WT​JT\Sigma^{\prime}=JW\Sigma W^{T}J^{T}, enabling novel view rendering. Each pixel color 𝒞\mathcal{C} is obtained by blending NN overlapping points:

|  |  |  |  |
| --- | --- | --- | --- |
|  | 𝒞=∑i∈Nci​αi​∏j=1i−1(1−αj),\mathcal{C}=\sum\_{i\in N}c\_{i}\alpha\_{i}\prod\_{j=1}^{i-1}(1-\alpha\_{j}), |  | (2) |

where cic\_{i} and αi\alpha\_{i} denote color and opacity, derived from the Gaussian with covariance Σ\Sigma and optimized parameters.

![Refer to caption](2411.12789v1/pipeline.png)

## 4 Method

Predicting various physical properties of 3D objects from static scene is an extremely challenging task due to limited supervisions. Instead of capturing physical data from generation models or multi-view videos [zhang2024physdreamer](#bib.bib45); [liu2024physics3d](#bib.bib22); [huang2024dreamphysics](#bib.bib14); [li2023pac](#bib.bib21); [zhong2024reconstruction](#bib.bib51); [feng2024pie](#bib.bib7), we reformulate this task from a new perspective, decomposing it into a set of sub-tasks.
Specifically, as shown in Fig. [2](#S3.F2 "Figure 2 ‣ 3.2 3D Gaussian Splatting (3DGS) ‣ 3 Preliminaries ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting"), we first segment the images with a set of foundation models [liu2023grounding](#bib.bib23); [kirillov2023segment](#bib.bib19); [zhang2024recognize](#bib.bib46) and lift these 2D segmented masks to segment 3D object in the scene via radiance fields rendering (Section [4.1](#S4.SS1 "4.1 3D Open-vocabulary Segmentation ‣ 4 Method ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting")). We propose MLLM-based Physical Property Perception (MLLM-P3) to predict the mean values of these properties (Section [4.2](#S4.SS2 "4.2 MLLM-based Physical Property Perception ‣ 4 Method ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting")). We then use the Material Property Distribution Prediction (MPDP) model to estimate the full distribution, simulating object dynamics with driving particles sampled using the Physical-Geometric Adaptive Sampling (PGAS) strategy (Section [4.3](#S4.SS3 "4.3 Physics-Based Dynamics ‣ 4 Method ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting")).

### 4.1 3D Open-vocabulary Segmentation

For each scene, we first train a 3DGS model on given images and camera poses. Inspired by prior work [ren2024grounded](#bib.bib32), we integrate 2D open-vocabulary models like Grounding DINO [liu2023grounding](#bib.bib23) for detection, SAM [kirillov2023segment](#bib.bib19) for segmentation, and RAM [zhang2024recognize](#bib.bib46) for tagging. These models automatically segment objects in images without textual input. Specifically, we use RAM to tag the image, Grounding DINO to create bounding boxes based on tags, and SAM to refine these boxes into precise masks. This approach enables full automatic image labeling using expert models.

After 2D open-vocabulary segmentation, each segmented image contains semantic features for each object. We project these 2D masks into 3D space using radiance field rendering. Inspired by recent work [zhao2024sg](#bib.bib48); [ye2023gaussian](#bib.bib43), each Gaussian retains its original attributes, with a learnable semantic attribute added for encoding object semantics. Using a zero-shot tracker [cheng2023tracking](#bib.bib5), we assign unique IDs to masks across views, helping distinguish categories within the 3D scene through differentiable rendering (see Fig.[2](#S3.F2 "Figure 2 ‣ 3.2 3D Gaussian Splatting (3DGS) ‣ 3 Preliminaries ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting")). Extracting objects from 3DGS introduces holes, which we inpaint using LaMa[suvorov2022resolution](#bib.bib35) to guide 3D Gaussian inpainting, keeping Gaussians outside holes fixed.

### 4.2 MLLM-based Physical Property Perception

The variety of materials in the world is vast and hard to define, with many appearing identical and indistinguishable by local appearance alone. However, humans can infer material composition by combining high-level reasoning about object semantics with low-level visual cues. Recent research [driess2023palm](#bib.bib6) has shown that multi-modal large language models (MLLM) excels in logical reasoning and decision-making for complex task. Inspired by how humans perceive and reason about physical properties of the objects they encounter, we propose MLLM-based Physical Property Perception (MLLM-P3) leveraging MLLM for open-vocabulary semantic reasoning about materials and their physical properties.

The segmented 3D scene in Section [4.1](#S4.SS1 "4.1 3D Open-vocabulary Segmentation ‣ 4 Method ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting") is usually tightly related to the physical properties of the 3D objects in it. We first select a canonical view and render an object in 3D scene based on the 3D Gaussian’s semantic attribute introduce Section [4.1](#S4.SS1 "4.1 3D Open-vocabulary Segmentation ‣ 4 Method ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting"). Then we use a VQA model, such as BLIP [li2022blip](#bib.bib20) to produce a text description of the image. This description, along with the image, are then passed to a Multi-modal Large Language Model (MLLM) such as GPT-4V [yang2023dawn](#bib.bib41), prompting it to return a dictionary containing K candidate materials and information on whether the object is rigid (related to the sampling method in Section [4.3](#S4.SS3 "4.3 Physics-Based Dynamics ‣ 4 Method ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting")). we compute the CLIP [radford2021learning](#bib.bib30) similarity score between the image and the materials in the dictionary to select the most matching material name. Finally, we prompt the MLLM with the selected material name, image, and text description to return a list of physical properties for the object, M=ρ,E,νM={\rho,E,\nu}, where ρ\rho is the density, EE is Young’s modulus, and ν\nu is Poisson’s ratio.

Although it is theoretically possible for MLLM to propose the materials directly from the image, we find decomposing the task into two parts produces more reliable results in our experiments. We will further demonstrate this in the experimental Section [5.5](#S5.SS5 "5.5 Ablation study ‣ 5 Experiments ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting").

![Refer to caption](2411.12789v1/sample.png)

### 4.3 Physics-Based Dynamics

Material Property Distribution Prediction.
Even for object composed of a single material, local physical properties exhibit inherent variations across different regions of the object [castaneda1995effect](#bib.bib3). Additionally, the physical properties estimated by multi-modal large language model (MLLM) may not capture the 3D structure of the object. To address these challenges, we propose material property distribution prediction (MPDP), and reformulate the problem from a regression task to a probability distribution estimation task.

Specifically, we train a network 𝒟θ\mathcal{D\_{\theta}} on part of synthesized dataset, using the object’s point cloud and predicted mean values (Section [4.2](#S4.SS2 "4.2 MLLM-based Physical Property Perception ‣ 4 Method ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting")) as input, and supervised by the physical properties of all particles predicted by Physics3D [liu2024physics3d](#bib.bib22). The remaining synthesized data is reserved for comparison in later experiments. The network is designed to predict the geometry-aware probability distribution 𝒫\mathcal{P} of physical properties across particles:

|  |  |  |  |
| --- | --- | --- | --- |
|  | 𝒫=𝒟θ​(𝒳),\begin{gathered}\mathcal{P}=\mathcal{D\_{\theta}}{(\mathcal{X})},\end{gathered} |  | (3) |

where 𝒳\mathcal{X} is the position of 3D Gaussians of the object. We then scale the distribution 𝒫\mathcal{P} by a global mean value predicted by the MLLM in Section [4.2](#S4.SS2 "4.2 MLLM-based Physical Property Perception ‣ 4 Method ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting") through element-wise multiplication, yielding the final physical property values for each point in the material field. This approach efficiently estimates per-point physical attributes, such as Young’s modulus and Poisson’s ratio, across the entire point cloud while avoiding the computational overhead of per-particle calculations.

Simulation with Physical-Geometric Adaptive Sampling.
Rendering high-fidelity 3D scene often needs millions of 3D Gaussians, which is significant computational demands for simulation. To reduce this burden, we implement a sub-sampling approach. Specifically, we design a Physical-Geometric Adaptive Sampling (PGAS) strategy. The original Poisson disk sampling requires that the distance between any two particles be larger than a threshold rr. Starting from an initial point, PDS then tries to fill a banded ring between rr and 2rr with new samples.

Our observation is that softer objects and those with complex shapes require more driving particles to accurately simulate their dynamics. To this end, we adaptively adjust the sample radius rr based on the object’s Young’s modulus EE predicted in Section [4.2](#S4.SS2 "4.2 MLLM-based Physical Property Perception ‣ 4 Method ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting") and curvature KK. The curvature KK is defined as:

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
|  | C=1n∑j=1n\displaystyle C=\frac{1}{n}\sum\_{j=1}^{n} | (𝒳j−𝒳¯)​(𝒳j−𝒳¯)T,\displaystyle(\mathcal{X}\_{j}-\bar{\mathcal{X}})(\mathcal{X}\_{j}-\bar{\mathcal{X}})^{T}, |  | (4) |
|  |  |  |  |  |
| --- | --- | --- | --- | --- |
|  | K=\displaystyle K= | λ3λ1+λ2+λ3,\displaystyle\frac{\lambda\_{3}}{\lambda\_{1}+\lambda\_{2}+\lambda\_{3}}, |  | (5) |

where 𝒳j\mathcal{X}\_{j} is the position of the jj-th 3D Gaussian of the object, 𝒳¯\bar{\mathcal{X}} is the mean position of all 3D Gaussians, and λ1,λ2,λ3\lambda\_{1},\lambda\_{2},\lambda\_{3} are the eigenvalues of the covariance matrix CC. Then, the sample radius rr is adjusted as:

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
|  | K^=min\displaystyle\hat{K}=\min | (Vm​a​x,max⁡(Vm​i​n,K)),\displaystyle(V\_{max},\max(V\_{min},K)), |  | (6) |
|  |  |  |  |  |
| --- | --- | --- | --- | --- |
|  | r^=\displaystyle\hat{r}= | min⁡(r,k​EK^​r),\displaystyle\min(r,k\sqrt{\frac{E}{\hat{K}}}r), |  | (7) |

where we set Vm​a​x=10V\_{max}=10, Vm​i​n=1V\_{min}=1, and k=10k=\sqrt{10} in our paper. Our sampling ensures that the distance between a particle and its nearest neighbor is at least r^\hat{r}. By using smaller radii for softer materials and high-curvature areas, PGAS captures fine details more accurately, enhancing model resolution in deformation simulations and complex surface reconstruction, as shown in Fig. [3](#S4.F3 "Figure 3 ‣ 4.2 MLLM-based Physical Property Perception ‣ 4 Method ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting").

MPM-Driven Physics-Based Dynamics.
To model physical properties, we employ MLS-MPM [hu2018moving](#bib.bib13) as our simulator. In MPM, a continuum is represented by particles distributed in a grid-based space, offering a distinct advantage over mesh-based methods. MPM can be seamlessly applied to 3D Gaussian Splatting (3DGS) in point-based representations. Building on PhysGaussian [xie2024physgaussian](#bib.bib40), we define a time-dependent state for each Gaussian kernel as follows:

|  |  |  |  |
| --- | --- | --- | --- |
|  | xi​(t)=Δ⁡(xi,t),Σi​(t)=Fi​(t)​Σi​Fi​(t)T,x\_{i}(t)=\Delta(x\_{i},t),\quad\Sigma\_{i}(t)=F\_{i}(t)\Sigma\_{i}F\_{i}(t)^{T}, |  | (8) |

where Δ⁡(⋅,t)\Delta(\cdot,t) and Fi​(t)F\_{i}(t) represent the coordinate deformation and deformation gradient at time tt. Additionally, to account for continuum rotation Ωi​(t)\Omega\_{i}(t), the rendering viewpoint is adjusted to align with the view direction of the spherical harmonic coefficient CiC\_{i}.

![Refer to caption](2411.12789v1/results_dreamer.png)
![Refer to caption](2411.12789v1/results_3D.png)

## 5 Experiments

### 5.1 Implementation Details

We initiate the process by reconstructing 3D Gaussians from multi-view images and execute internal particle filling operations to refine the representation further. Each Gaussian kernel is then associated with a set of physical properties targeted for optimization following [zhang2024physdreamer](#bib.bib45); [xie2024physgaussian](#bib.bib40). We then discretize the foreground region into a grid structure, typically sized at 64364^{3}. For the MPM simulation, we use 768 sub-steps per interval between video frames, resulting in a sub-step duration of 4.34×10−54.34\times 10^{-5} seconds to ensure precision and accuracy in simulation dynamics. All experiments are conducted on a single NVIDIA 3090 GPU. For more implementation details, please refer to the Supp.Mat.

### 5.2 Datasets

Open-word dataset. To evaluate the physical simulation accuracy in open-world 3D scenes, we chose some 3D scenes from LERF [kerr2023lerf](#bib.bib18) and Instruct-NeRF2NeRF [haque2023instruct](#bib.bib10).

PhysDreamer [zhang2024physdreamer](#bib.bib45). We also conduct experiments on the physical simulation of single objects on four real-world static scenes from PhysDreamer [zhang2024physdreamer](#bib.bib45) for fair comparison. Each scene includes an object and a background.

Synthesized dataset [liu2024physics3d](#bib.bib22). Following [liu2024physics3d](#bib.bib22), we utilize BlenderNeRF [Raafat\_BlenderNeRF\_2023](#bib.bib29) to synthesize several scenes. Five cases are used to train the proposed MPDP model (as introduced in Section [4.3](#S4.SS3 "4.3 Physics-Based Dynamics ‣ 4 Method ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting")), while the remaining four cases are reserved for subsequent comparisons.

### 5.3 Evaluation Metrics

We mainly focus on the motion realism and aesthetic quality of the synthesized 3D object motion in this task. To evaluate these aspects, we conduct a user study in which 42 participants rate each video based on motion realism. Additionally, we assess the aesthetic quality, particularly the naturalness of the videos, using the LAION aesthetic predictor, following [huang2024vbench](#bib.bib15). For further details about the user study, please refer to the Supp.Mat.

| Method: | RS | AS | Time |
| --- | --- | --- | --- |
| PhysGaussian [xie2024physgaussian](#bib.bib40) | 4.50 | 7.56 | - |
| PhysDreamer [zhang2024physdreamer](#bib.bib45) | 4.54 | 7.71 | - |
| DreamGaussian4D [ren2023dreamgaussian4d](#bib.bib31) | 4.57 | 7.28 | 0.1h |
| Sim Anything | 4.66 | 7.89 | 2min |

| Method: | RS | AS | Time |
| --- | --- | --- | --- |
| PhysGaussian [xie2024physgaussian](#bib.bib40) | 4.94 | 7.35 | - |
| DreamPhysics [huang2024dreamphysics](#bib.bib14) | 5.05 | 7.92 | 1.5h |
| Physics3D [liu2024physics3d](#bib.bib22) | 5.10 | 8.01 | 1.5h |
| DreamGaussian4D [ren2023dreamgaussian4d](#bib.bib31) | 4.98 | 6.81 | 0.1h |
| Sim Anything | 5.10 | 8.20 | 2min |

### 5.4 Comparison with SOTA Methods

We chose the performance from real-world static scenes from PhysGaussian [xie2024physgaussian](#bib.bib40) for fair comparison. We extensively compare our method with three the most recent methods: PhysGaussian [xie2024physgaussian](#bib.bib40), DreamGaussian4D [ren2023dreamgaussian4d](#bib.bib31), and PhysDreamer [zhang2024physdreamer](#bib.bib45). Tab. [2](#S5.T2 "Table 2 ‣ 5.3 Evaluation Metrics ‣ 5 Experiments ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting") presents the user study results (RS) and aesthetic score (AS) predicted by LAION aesthetic predictor following [huang2024vbench](#bib.bib15). Since PhysDreamer [zhang2024physdreamer](#bib.bib45) has not released its training code, we only compare the four evaluation scene and are unable to report its inference time. PhysDreamer [zhang2024physdreamer](#bib.bib45) scores lower than DreamGaussian4D [ren2023dreamgaussian4d](#bib.bib31) in RS and PhysGaussian [xie2024physgaussian](#bib.bib40) in AS, which indicates that pre-generated videos may not be a proper ground truth for supervision. Our Sim Anything achieves better performance in both metrics, which demonstrates that Sim Anything generates videos that are both realistic and physically plausible, with a high degree of naturalness.

Following [zhang2024physdreamer](#bib.bib45), we also compare the results with real captured videos in Fig. [4](#S4.F4 "Figure 4 ‣ 4.3 Physics-Based Dynamics ‣ 4 Method ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting"). We utilize space-time slices to present our comparisons, which depict time along the vertical axis and spatial slices of the object along the horizontal axis, as indicated by the red lines in the “object” column. Through these visualizations, we aim to elucidate the magnitude and frequencies of the oscillating motions under scrutiny. Sim Anything generates smooth and realistic motion patterns, accurately capturing the natural flow and details of real-world movements. Please see our project website videos for more video visualization.

We also evaluate our Sim Anything using the synthesized dataset [liu2024physics3d](#bib.bib22). We report the quantitative results against recent methods [xie2024physgaussian](#bib.bib40); [huang2024dreamphysics](#bib.bib14); [liu2024physics3d](#bib.bib22); [ren2023dreamgaussian4d](#bib.bib31) in Tab. [3](#S5.T3 "Table 3 ‣ 5.3 Evaluation Metrics ‣ 5 Experiments ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting"). Our method still generates the most consistent and natural motions. The visual results are shown in Fig. [5](#S4.F5 "Figure 5 ‣ 4.3 Physics-Based Dynamics ‣ 4 Method ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting").

![Refer to caption](2411.12789v1/ablation.png)

| GPT | BLIP | CLIP | w/o MPDP | PGAS | AS |
| --- | --- | --- | --- | --- | --- |
| ✓ |  |  | ✓ | ✓ | 4.47 |
| ✓ | ✓ |  | ✓ | ✓ | 4.59 |
| ✓ | ✓ | ✓ |  | ✓ | 4.64 |
| ✓ | ✓ | ✓ | ✓ |  | 4.62 |
| ✓ | ✓ | ✓ | ✓ | ✓ | 4.66 |

### 5.5 Ablation study

In this section, we conduct ablation experiments using PhysDreamer [zhang2024physdreamer](#bib.bib45) dataset to evaluate the effectiveness of our proposed modules.

Model for physical property perception. In Fig. [6](#S5.F6 "Figure 6 ‣ 5.4 Comparison with SOTA Methods ‣ 5 Experiments ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting") we compare two methods with our proposed MLLM-P3:
1) GPT: Predicting physical properties using only the image;
2) GPT+BLIP: Predicting properties with both the image and a text description from BLIP;
3) GPT+BLIP+CLIP (MLLM-P3): Generating a dictionary of K candidate materials with GPT, selecting the best match via CLIP, and then predicting properties using the image, description, and chosen material.
As shown in Tab. [4](#S5.T4 "Table 4 ‣ 5.4 Comparison with SOTA Methods ‣ 5 Experiments ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting"), MLLM-P3 performs best because there is inherent uncertainty in predicting materials based on just visual appearance or text description, as shown in Tab. [4](#S5.T4 "Table 4 ‣ 5.4 Comparison with SOTA Methods ‣ 5 Experiments ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting"), .

Material property distribution prediction. Material property distribution prediction is designed for complex physical properties distribution. As shown in Fig. [6](#S5.F6 "Figure 6 ‣ 5.4 Comparison with SOTA Methods ‣ 5 Experiments ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting") and Tab. [4](#S5.T4 "Table 4 ‣ 5.4 Comparison with SOTA Methods ‣ 5 Experiments ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting"), it is required to achieve optimal performance.

Sampling strategy selection. We also compare our proposed Physical-Geometric Adaptive Sampling (PGAS) strategy with K-Means sampling which is used in PhysDreamer [zhang2024physdreamer](#bib.bib45). The space-time slices of K-Means sampling is not quite consistent with the ground truth, while our final method can produce 4D content that is competitive to real-captured videos, as shown in Fig. [6](#S5.F6 "Figure 6 ‣ 5.4 Comparison with SOTA Methods ‣ 5 Experiments ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting"). The results in Tab.[4](#S5.T4 "Table 4 ‣ 5.4 Comparison with SOTA Methods ‣ 5 Experiments ‣ Sim Anything: Automated 3D Physical Simulation of Open-world Scenewith Gaussian Splatting") further confirm this, highlighting our method’s superiority in visual quality.

## 6 Conclusion

In this work, we introduce a framework, called Sim Anything, which generates physics-based dynamics and photo-realistic renderings.
We begin with precise scene reconstruction and object-level 3D open-vocabulary segmentation, followed by multi-view image in-painting. Then, we propose MLLM-based Physical Property Perception (MLLM-P3) to predict mean physical properties of objects. Using these mean values and object geometry, the Material Property Distribution Prediction model (MPDP) then estimates the complete distribution, reframing the task as probability distribution estimation to reduce computational costs. Finally, we simulate objects in an open-world scene with particles sampled via the Physical-Geometric Adaptive Sampling (PGAS) strategy. Extensive experiments and user studies show that Sim Anything produces more realistic motion than state-of-the-art methods within much faster inference time.
We believe that Sim Anything represents a meaningful advance toward more engaging and immersive virtual environments, unlocking diverse applications from realistic simulations to interactive virtual experiences.

Limitation and future work. In complex environments with partially occluded objects, our Sim Anything is unable to segment the entire object, resulting in unnatural simulations, which is not efficient for more real applications. In the future, we aim to utilize generation model to reconstruct the occluded parts of these objects, which will takes a significant step to open up a wide range of applications from realistic simulations to interactive virtual experiences.

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
