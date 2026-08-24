---
source_url: https://samchopra2003.github.io/physgs
ingested: 2026-08-24
sha256: 19686490ff54caef84952f2daaa9b6a98143b7d900cb48ac75a5dc997d77099f
---
# PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation

CVPR 2026

[Samarth Chopra](https://scholar.google.com/citations?user=Yc9_o-4AAAAJ&hl=en),  [Jing Liang](/everydayvla),  [Gershom Seneviratne](/everydayvla),  [Dinesh Manocha](/everydayvla)

University of Maryland, College Park

[arXiv](https://arxiv.org/abs/2511.18570)     [Code (Coming Soon)](/vla)

![PhysGS overview](./static/images/overview_enhanced.png) 

Top: Our method estimates per-point and dense physical properties (e.g., friction, hardness, density, stiffness, and mass) by combining vision-language material priors with Bayesian updates over 3D Gaussian splats. Bottom: PhysGS can also be deployed in outdoor environments to infer scene-level properties such as friction and predictive uncertainty; we visualize the total uncertainty (aleatoric + epistemic).

## Abstract

Understanding physical properties such as friction, stiffness, hardness, and material composition is essential for enabling robots to interact safely and effectively with their surroundings. However, existing 3D reconstruction methods focus on geometry and appearance and cannot infer these underlying physical properties. We present PhysGS, a Bayesian-inferred extension of 3D Gaussian Splatting that estimates dense, per-point physical properties from visual cues and vision-language priors.

We formulate property estimation as Bayesian inference over Gaussian splats, where material and property beliefs are iteratively refined as new observations arrive. PhysGS also models aleatoric and epistemic uncertainties, enabling uncertainty-aware object and scene interpretation.

Across object-scale (ABO-500), indoor, and outdoor real-world datasets, PhysGS improves accuracy of the mass estimation by up to 22.8%, reduces Shore hardness error by up to 61.2%, and lowers kinetic friction error by up to 18.1% compared to deterministic baselines. Our results demonstrate that PhysGS unifies 3D reconstruction, uncertainty modeling, and physical reasoning in a single, spatially continuous framework for dense physical property estimation.

![PhysGS architecture](./static/images/physgs_architecture.jpg) 

Given multi-view images, SAM provides part-level segmentations that are used for 3D Gaussian Splatting (3DGS) reconstruction. For each segmented part, a VLM produces material labels, density estimates, and confidence scores across multiple views. These observations are fused using Bayesian inference with uncertainty quantification to obtain final per-material property distributions. By propagating the estimated densities over the reconstructed 3D Gaussian field, PhysGS predicts per-point density and full-object mass.

## Results Overview

 ![PhysGS ABO-500 results](./static/images/abo_500_results.jpg) 

Given multi-view images, SAM provides part-level segmentations that are used for 3D Gaussian Splatting (3DGS) reconstruction. For each segmented part, a VLM produces material labels, density estimates, and confidence scores across multiple views. These observations are fused using Bayesian inference with uncertainty quantification to obtain final per-material property distributions. By propagating the estimated densities over the reconstructed 3D Gaussian field, PhysGS predicts per-point density and full-object mass.

   ![PhysGS outdoor visualization](./static/images/outdoor_viz.jpg) 

From a single RGB view, PhysGS predicts material segmentation, friction coefficients, Young's modulus, and total uncertainty (aleatoric + epistemic). The method captures broad material variations across natural terrain and vegetation while producing pixel-wise physical property estimates with associated confidence. Higher total uncertainty in Rows 2 and 3 corresponds to scenes with dense clutter and visually ambiguous regions, where SAM provides less precise part-level masks (e.g., separating leaf litter from wood or mud from grass).

   ![PhysGS fabric stiffness visualization](./static/images/fabric_viz.jpg) 

Given an input RGB image, PhysGS produces dense stiffness fields that capture material differences across corduroy, nylon ripstop, outdoor polyester, and pleather.

## Citation

```
@inproceedings{chopra2026physgs, title={PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation}, author={Chopra, Samarth and Liang, Jing and Seneviratne, Gershom and Manocha, Dinesh}, booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition}, pages={18980--18990}, year={2026} }
```
