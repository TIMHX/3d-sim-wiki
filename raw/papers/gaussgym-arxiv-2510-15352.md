---
source_url: https://arxiv.org/abs/2510.15352
ingested: 2026-08-24
sha256: 9fa9200c8f5494c37841b281e6bc19ae2441a3fde5a812e21e09096907e148dd
---
##### Report GitHub Issue

Content selection saved. Describe the issue below:

![](/static/base/1.0.1/images/icons/smileybones-small.svg)
![arXiv logo](/static/base/1.0.1/images/arxiv-logo-primary-light.svg)

# GaussGym: An open-source real-to-sim framework for learning locomotion from pixels

###### Abstract

We present a novel approach for photorealistic robot simulation that integrates 3D Gaussian Splatting as a drop-in renderer within vectorized physics simulators such as IsaacGym. This enables unprecedented speed—exceeding 100,000 steps per second on consumer GPUs—while maintaining high visual fidelity, which we showcase across diverse tasks. We additionally demonstrate its applicability in a sim-to-real robotics setting. Beyond depth-based sensing, our results highlight how rich visual semantics improve navigation and decision-making, such as avoiding undesirable regions. We further showcase the ease of incorporating thousands of environments from iPhone scans, large-scale scene datasets (e.g., GrandTour, ARKit), and outputs from generative video models like Veo, enabling rapid creation of realistic training worlds. This work bridges high-throughput simulation and high-fidelity perception, advancing scalable and generalizable robot learning. All code and data will be open-sourced for the community to build upon. Videos, code, and data available at <https://escontrela.me/gauss_gym/>.

![Refer to caption](2510.15352v1/all_scenes_nonlinear_cropped.png)
![Refer to caption](2510.15352v1/data_nonlinear_cropped.png)

## 1 Introduction

For mobile robots to act in unstructured real-world settings, they need to be able to accurately perceive the environment around them ([Gervet et al. 2023](#bib.bib22); [Chang et al. 2023](#bib.bib10)). Consider a robot that needs to reach target locations within the environment while navigating obstacles and interacting with man-made objects. Many such obstacles and environment affordances are only detectable through visual observations, such as crosswalks, puddles, or colored features.

The dominant paradigm for achieving locomotion on legged robots, sim-to-real ([Hwangbo et al. 2019](#bib.bib28)) reinforcement learning (RL), faces considerable challenges in fully leveraging visual properties of real-world environments. In principle, this approach allows a control policy trained in simulation to transfer to a real robot without adaptation, achieving robust locomotion. While existing simulators ([Makoviychuk et al. 2021a](#bib.bib38); [Todorov et al. 2012](#bib.bib58); [Tao et al. 2024](#bib.bib57); [Genesis 2024](#bib.bib21)) capture physics with sufficient fidelity for transfer, their treatment of visual information is often either too slow or too inaccurate, limiting the effectiveness of policy learning and transfer. Consequently, most perceptive locomotion frameworks in the literature rely on LiDAR or depth inputs ([Hoeller et al. 2024](#bib.bib24)), which restrict policies from exploiting semantic cues in the environment and narrow the range of tasks that can be realistically pursued in simulation.

With GaussGym, we present an open-source simulation framework that digitizes real-world and video model–generated environments, and simulates both their physics and photorealistic renderings to enable learning locomotion and navigation policies directly from RGB pixels. GaussGym builds on advances in 3D reconstruction and differentiable rendering to bring diverse input sources into simulation. The system is designed to accept a wide range of data, including smartphone scans, fully sensorized SLAM captures, existing 3D datasets, hand-held videos, and even outputs from generative video models. GaussGym is highly efficient, simulating hundreds of thousands of environment steps per second across 4,096 robots at 640×480640\times 480 resolution on a single RTX 4090 GPU.

To demonstrate the effectiveness of GaussGym for training visuomotor policies with RL, we train locomotion and navigation policies for both humanoid and quadrupedal robots. Despite the increased throughput and visual fidelity of GaussGym, training directly from RGB remains challenging, as policies must infer geometry from vision rather than rely on provided heightmaps or depth images. We address this by incorporating an auxiliary reconstruction loss guided by ground-truth mesh data, which significantly improves learning speed and performance. Finally, we show initial zero-shot transfer of visual locomotion policies trained in GaussGym to real-world stair climbing, marking a first step toward closing the visual sim-to-real gap. Beyond this demonstration, GaussGym democratizes access to photorealistic simulation and lays the foundation for future research on visual locomotion and navigation.

We summarize our contributions below:

GaussGym: a fast open-source photorealistic simulator with 2,500 scenes, supporting diverse scene creation from manual scans, open-source datasets, and generative video models.

We share findings on addressing the visual sim-to-real gap, showing that incorporating geometry reconstruction as an auxiliary task significantly improves stair-climbing performance.

We demonstrate the semantic reasoning of RGB navigation policies in a goal-reaching task, where policies trained on pixels successfully avoid undesired regions that are invisible to depth-only policies.

![Refer to caption](2510.15352v1/grindewald_nonlinear_cropped.png)
![Refer to caption](2510.15352v1/ryokan_nonlinear_cropped.png)
![Refer to caption](2510.15352v1/stairs_nonlinear_cropped.png)

## 2 Related Work

### 2.1 Sim-to-real RL for Locomotion

Simulation provides a scalable and cost-effective method for training RL locomotion and navigation policies, avoiding costly hardware data collection and unsafe real-world exploration while granting access to privileged information during training. The ideal simulator for developing these policies comprises several key properties: high throughput, accurate physics, and photorealistic rendering.

While rigid-body-dynamics CPU-based simulators like MuJoCo ([Todorov et al. 2012](#bib.bib58)), PyBullet ([Coumans & Bai 2016–2021](#bib.bib15)), and RaiSim ([Hwangbo et al. 2018](#bib.bib27)) enabled training and transferring of RL locomotion policies from simulation to the real world ([Tan et al. 2018](#bib.bib55)), the advent of GPU-accelerated simulators has democratized RL training by leveraging consumer-grade hardware for simulation. Platforms such as Isaac Gym ([Makoviychuk et al. 2021a](#bib.bib38)), Isaac Sim ([Makoviychuk et al. 2021b](#bib.bib39)), and others ([Tao et al. 2024](#bib.bib57); [Zakka et al. 2025](#bib.bib69); [Genesis 2024](#bib.bib21)) have been instrumental in this progression, supporting the rapid development and advances in legged locomotion ([Rudin et al. 2021](#bib.bib51)) and navigation ([Lee et al. 2024](#bib.bib35)).

Despite frameworks such as IsaacLab ([Makoviychuk et al. 2021b](#bib.bib39)), ManiSkill ([Tao et al. 2024](#bib.bib57)), and Genesis ([Genesis 2024](#bib.bib21)) supporting parallelized hardware-accelerated rendering, most locomotion policies deployed in the real world are restricted to geometric (e.g., depth, elevation maps) and proprioceptive inputs.
This can be explained by the visual-sim-to-real gap, lack of diverse assets capturing the real world, and the high throughput required for training RL policies.
Implicit learned scene representations, such as 3D Gaussian Splatting (3DGS) ([Kerbl et al. 2023](#bib.bib30)), offer a compelling alternative, directly improving visual fidelity and rendering throughput.

### 2.2 Scene Generation

Heuristic and handcrafted rules ([Rudin et al. 2021](#bib.bib51)), as well as procedural terrain generation ([Lee et al. 2024](#bib.bib35)), are commonly used to create environments for training locomotion and navigation policies. While these heuristic-based rules are effective for defining geometric terrains that lead to robust locomotion behaviors, they do not allow for specifying a meaningful visual appearance of the scene. Achieving realistic visuals requires composing scenes from textured assets.
Some works have attempted to import assets to be used for learning locomotion directly from video using SfM methods, however they do it without re-rendering the scene in RGB ([Allshire et al. 2025](#bib.bib2)). Asset libraries for realistic scene simulation are available through platforms like ReplicaCAD ([Szot et al. 2021](#bib.bib54)), LeVerb ([Xue et al. 2025](#bib.bib64)), and AI2-THOR ([Kolve et al. 2017](#bib.bib34)) (including iTHOR and RoboTHOR) or can be generated procedurally ([Deitke et al. 2022](#bib.bib17)). Alternatively, realistic scenes can be captured using specialized 3D scanners ([Chang et al. 2017](#bib.bib9); [Xia et al. 2018](#bib.bib63)) and then further integrated into simulation frameworks like Habitat ([Ramakrishnan et al. 2021](#bib.bib49)). However, most rendering pipelines rely on textured-mesh assets, which often result in lower visual fidelity.

Our approach builds on NeRF2Real ([Byravan et al. 2023](#bib.bib8)), which improves visual fidelity by capturing scenes with a Neural Radiance Field (NeRF), followed by mesh extraction and manual post-processing to train a locomotion policy. However, it is computationally expensive due to slow ray-tracing and lacks vectorization support.
([Zhu et al. 2025](#bib.bib71)) construct 3D Gaussians of multiple environments and train a visual high-level navigation policy.
Several works in robotic manipulation ([Torne et al. 2024](#bib.bib59); [Chen et al. 2024b](#bib.bib14)) adopt similar strategies, using 3DGS to create articulated scenes or train models to predict an object’s Unified Robot Description Format (URDF), including its actuation, from a single image ([Chen et al. 2024b](#bib.bib14)).
LucidSim ([Yu et al. 2024](#bib.bib65)) makes two key contributions: first, it employs a ControlNet diffusion model to generate visual training data from depth maps and semantic masks; second, it introduces a real-to-sim framework by training 3DGS and manually aligning reference frames with meshes created using Polycam for a select set of test scenes.
Today’s state-of-the-art world and video models trained on internet-scale video data demonstrate unprecedented levels of controllable video generation ([DeepMind 2025](#bib.bib16); [Bruce et al. 2024](#bib.bib7); [Google DeepMind 2025](#bib.bib23); [Wan et al. 2025](#bib.bib60)) and can synthesize multiple seconds of photorealistic, multi-view-consistent video. Although their slow inference speed renders them impractical as direct simulators, these models create opportunities to rethink scalable 3D asset and environment creation from simple text prompts. A comparison of simulators can be found in [table 1](#S2.T1 "In 2.3 Radiance Fields in Robotics ‣ 2 Related Work ‣ GaussGym: An open-source real-to-sim framework for learning locomotion from pixels").

### 2.3 Radiance Fields in Robotics

Neural Radiance Fields (NeRFs) ([Mildenhall et al. 2020](#bib.bib41)) are an attractive representation for high quality scene reconstruction from posed images, with an abundance of recent work on visual quality ([Adamkiewicz et al. 2022](#bib.bib1); [Barron et al. 2021](#bib.bib3); [Barron et al. 2022](#bib.bib4); [Ma et al. 2022](#bib.bib37); [Huang et al. 2022](#bib.bib26); [Sabour et al. 2023](#bib.bib52); [Philip & Deschaintre 2023](#bib.bib45)), large-scale scenes ([Tancik et al. 2023](#bib.bib56); [Wang et al. 2023](#bib.bib62); [Barron et al. 2023](#bib.bib5)), optimization speed ([Müller et al. 2022](#bib.bib42); [Chen et al. 2022](#bib.bib11); [Fridovich-Keil et al. 2023](#bib.bib20); [Yu et al. 2021](#bib.bib66)), dynamic scenes ([Park et al. 2021](#bib.bib44); [Li et al. 2023](#bib.bib36); [Pumarola et al. 2020](#bib.bib46)), and more.
They have shown promise in robot manipulation, beginning with leveraging NeRF as a high-quality visual reconstruction for grasping ([Kerr et al. 2022](#bib.bib31); [Ichnowski\* et al. 2020](#bib.bib29)) and more recently by leveraging its ability to embed higher dimensional features for language-guided manipulation ([Rashid et al. 2023](#bib.bib50); [Shen et al. 2023](#bib.bib53)). A core limitation of neural fields is their slow training speed, which 3D Gaussian Splatting (3DGS) mitigates ([Kerbl et al. 2023](#bib.bib30)) by representing radiance fields as a collection of oriented 3D gaussians which can be differentiably rasterized quickly on modern GPU hardware. Many works transfer high-dimensional feature fields to 3DGS for rapid training and rendering, as well as language-guided robot grasping, persistent Gaussian representations for manipulation, and visual imitation ([Zheng et al. 2024](#bib.bib70); [Qin et al. 2023](#bib.bib47); [Qiu et al. 2024](#bib.bib48); [Yu et al. 2025a](#bib.bib67); [Yu et al. 2025b](#bib.bib68); [Kerr et al. 2024](#bib.bib32)).

Radiance Fields have also shown promise as large-scale scene representations for navigation as a differentiable collision representation ([Adamkiewicz et al. 2022](#bib.bib1)), as a visual simulator for learning drone flight or autonomous driving from RGB pixels ([Khan et al. 2024](#bib.bib33); [Chen et al. 2025](#bib.bib13)), or as a scene representation to train locomotion affordance models with view augmentation ([Escontrela et al. 2025](#bib.bib18)). GaussGym draws inspiration from these results, but integrates high-fidelity environment visual simulation with contact physics from IsaacSim to enable locomotion. The most related prior work is LucidSim [Yu et al. 2024](#bib.bib65), which develops a similar splat-integrated simulator for evaluating locomotion policies. GaussGym takes a similar real-to-sim approach, but implements a framework which easily scales to thousands of scanned scenes, integrates tightly with massively parallel physics simulation, and presents a flexible framework for future research to build on.

![Refer to caption](2510.15352v1/splash_cropped.png)

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| Method | GaussGym | LucidSim | LeVerb | IsaacLab |
| Photrealistic | ✓ | ✓ | ✗ | ✗ |
| Temporally  consistent | ✓ | ✗ | ✓ | ✓ |
| FPS (vectorized) | 100,000†100{,}000^{\dagger} | Single env only | Not reported | 800‡800^{\ddagger} |
| FPS (per env) | 2525 | 33 | Not reported | 11 |
| Renderer | 3D Gaussian Splatting | ControlNet | Raytracing | Raytracing |
| Scene Creation | Smartphone scans,  Pre-existing datasets,  Video model outputs | Hand-designed  scenes | Hand-designed  scenes | Randomization  over primitives |

## 3 GaussGym

Figure [2](#S0.F2 "Figure 2 ‣ GaussGym: An open-source real-to-sim framework for learning locomotion from pixels") illustrates the overall GaussGym pipeline. Data can originate from posed datasets, casual smartphone scans, or even raw RGB sequences from video generation models. All inputs are standardized via the Visually Grounded Geometry Transformer (VGGT)  ([Wang et al. 2025](#bib.bib61)), which estimates camera intrinsics, extrinsics, dense point clouds, and normals. These intermediate representations are then passed to a neural surface reconstruction module to generate meshes, while Gaussian splats are initialized directly from VGGT point clouds to provide accurate geometry and rapid convergence. The resulting assets are automatically aligned in a shared global frame. During simulation, Gaussian Splatting is used as a drop-in renderer, producing photorealistic visuals at scale while remaining fully synchronized with physics for collision handling. This design allows GaussGym to combine diverse real-world and synthetic data sources with high-speed rendering for large-scale robot learning. Example scenes from various sources are visualized in [fig. 1](#S0.F1 "In GaussGym: An open-source real-to-sim framework for learning locomotion from pixels") and [fig. 3](#S1.F3 "In 1 Introduction ‣ GaussGym: An open-source real-to-sim framework for learning locomotion from pixels").

### 3.1 Data Collection and Processing

GaussGym is designed to flexibly ingest data from a wide range of sources. These include posed datasets such as ARKitScenes ([Baruch et al. 2021](#bib.bib6)) and GrandTour ([Frey et al. 2025](#bib.bib19)), smartphone captures with intrinsic calibration, and even unposed RGB sequences generated by modern video models such as Veo ([Google DeepMind 2025](#bib.bib23)).

All data are formatted into a common gravity-aligned reference frame before processing. We use VGGT to extract camera intrinsics, extrinsics, and dense scene representations including point clouds and surface normals. From these outputs, a Neural Kernel Surface Reconstruction (NKSR) ([Huang et al. 2023](#bib.bib25)) is used to produce high-quality meshes, while Gaussian splats are initialized directly from VGGT point clouds. Point-cloud initialization of Gaussian splats greatly improves geometric fidelity and accelerates convergence. Our approach achieves precise visual-geometric alignment, extending LucidSim’s real-to-sim pipeline ([Yu et al. 2024](#bib.bib65)), which is limited to smartphone scans, requires manual registration of the mesh and 3DGS, and does not provide vectorized rendering.

### 3.2 3D Gaussian Splatting as a Drop-in Renderer

Once reconstructed, Gaussian splats are rasterized in parallel across simulated environments. Unlike traditional raytracing or rasterization pipelines ([Xue et al. 2025](#bib.bib64); [Makoviychuk et al. 2021a](#bib.bib38)), splatting provides photorealistic rendering with minimal overhead and is highly amenable to vectorized execution. We batch-render splats across environments using multi-threaded PyTorch kernels, ensuring efficient GPU utilization and distributed training. Example RGB and depth renders for indoor and generative model scenes are are shown in [fig. 5](#S3.F5 "In 3.3 Optimizations for High-Throughput and Realism ‣ 3 GaussGym ‣ GaussGym: An open-source real-to-sim framework for learning locomotion from pixels") and [fig. 4](#S2.F4 "In 2.3 Radiance Fields in Robotics ‣ 2 Related Work ‣ GaussGym: An open-source real-to-sim framework for learning locomotion from pixels").

### 3.3 Optimizations for High-Throughput and Realism

To maximize efficiency, we decouple rendering from the proprioceptive control rate and simulation frequency: instead of rendering at the control frequency, we render at the camera’s true frame rate, which is normally slower than the control frequency.
This yields additional speed-ups while preserving high-fidelity visual input for the policy. To further reduce the Sim2Real gap, we introduce a simple but novel method to simulate motion blur: rendering a small set of frames offset along the camera’s velocity direction and alpha-blending them into a single image, which produces realistic blur artifacts that improve visual fidelity and robustness in transfer. This is especially noticeable in scenes with sudden jolts, such as climbing stairs or high-speed movements. Example motion blur sequences are shown in Appendix [fig. 10](#A1.F10 "In A.1 Additional Scenes and Motion Blur ‣ Appendix A Appendix ‣ GaussGym: An open-source real-to-sim framework for learning locomotion from pixels").

In practice, a single GPU can render up to 4,096 environments across 128 unique scenes at 100,000 simulator steps per second wall clock time, where the control and camera update rates in simulator time are 50Hz and 10Hz, respectively (on an RTX 4090). Scaling is near-linear across multiple GPUs, enabling distributed training on thousands of diverse, photorealistic scenes simultaneously. This throughput makes it possible to train vision-based locomotion policies with a level of scene diversity and realism previously unattainable in high-speed simulators.

![Refer to caption](2510.15352v1/scene_depth_nonlinear_cropped.png)
![Refer to caption](2510.15352v1/sim_A1_cropped.png)
![Refer to caption](2510.15352v1/real_A1_cropped.png)

## 4 Results

### 4.1 Training Environments Beyond Reality

GaussGym integrates data from smartphone scans and open-source datasets, but its standout capability is generating entirely new worlds from video models. This enables the creation of environments that are difficult or impossible to capture in the real world, such as caves, disaster zones, or even extraterrestrial terrains (Fig. [4](#S2.F4 "Figure 4 ‣ 2.3 Radiance Fields in Robotics ‣ 2 Related Work ‣ GaussGym: An open-source real-to-sim framework for learning locomotion from pixels")). The key enablers are the strong multi-view consistency of Veo and the robust camera estimation and dense point cloud generation of VGGT. Additional scenes and videos are available on our webpage.

### 4.2 Visual Locomotion and Navigation

To evaluate the benefits of photorealistic rendering in GaussGym, we focus on the task of visual stair climbing and visual navigation in diverse visually complex terrains.
We specifically choose to use an asymmetric actor-critic framework to learn from visual input, rather than relying on student-teacher distillation [Miki et al. 2022](#bib.bib40). Thus, we learn policies end-to-end in a single stage, foregoing the need for multi-stage training pipelines ([Hoeller et al. 2024](#bib.bib24)). Rewards and policy training details can be found in [section A.2](#A1.SS2 "A.2 Policy Learning ‣ Appendix A Appendix ‣ GaussGym: An open-source real-to-sim framework for learning locomotion from pixels").

#### 4.2.1 Neural Architecture

![Refer to caption](2510.15352v1/network_nonlinear_cropped.png)

At the core of our framework is a recurrent encoder that fuses visual and proprioceptive streams over time. At each timestep, proprioceptive measurements are concatenated with DinoV2 ([Oquab et al. 2023](#bib.bib43)) embeddings extracted from the raw RGB frame. These combined features are passed through an LSTM, producing a compact latent representation that captures both temporal dynamics and visual semantics. The choice of LSTM is motivated by the need for fast inference speed on the robot, thereby limiting the use of vanilla transformer architectures.

Two task-specific heads operate on this representation:
Voxel prediction head: The latent vector is unflattened into a coarse 3D grid and processed by a 3D transposed convolutional network. Successive transposed convolution layers upscale this grid into a dense volumetric prediction of occupancy and terrain heights. In doing so, the shared latent representation has to capture the geometry of the scene.
Visualized predictions are shown in [fig. 7](#S4.F7 "In 4.2.1 Neural Architecture ‣ 4.2 Visual Locomotion and Navigation ‣ 4 Results ‣ GaussGym: An open-source real-to-sim framework for learning locomotion from pixels").
Policy head: In parallel, a second LSTM consumes the latent representation together with its recurrent hidden state, and outputs the parameters of a Gaussian distribution over joint position offset actions.
Additional training details, including observation spaces, scene configurations, and rewards, are provided in [section A.2](#A1.SS2 "A.2 Policy Learning ‣ Appendix A Appendix ‣ GaussGym: An open-source real-to-sim framework for learning locomotion from pixels").

#### 4.2.2 Visual Locomotion Results

While the task of stair climbing can be solved purely through geometric or blind locomotion [Miki et al. 2022](#bib.bib40), it provides a valuable context for studying the behavior learned by our visual policy when approaching stairs.
Our policy, trained on the Unitree A1 using RGB image inputs, learns to precisely place its feet on stairs and adapt its gait to avoid colliding with stair risers within the simulation, as illustrated in [fig. 6(a)](#S3.F6.sf1 "In Figure 6 ‣ 3.3 Optimizations for High-Throughput and Realism ‣ 3 GaussGym ‣ GaussGym: An open-source real-to-sim framework for learning locomotion from pixels") and Appendix [fig. 11](#A1.F11 "In A.2 Policy Learning ‣ Appendix A Appendix ‣ GaussGym: An open-source real-to-sim framework for learning locomotion from pixels").
Therefore, allowing the policy to robustly match commanded velocities across terrains.
As a proof of concept, we successfully transfer this policy to the real world without additional fine-tuning (see [fig. 6(b)](#S3.F6.sf2 "In Figure 6 ‣ 3.3 Optimizations for High-Throughput and Realism ‣ 3 GaussGym ‣ GaussGym: An open-source real-to-sim framework for learning locomotion from pixels")).
Similarly, our policy, trained in simulation with a head-mounted camera on the Booster T1, learns to successfully navigate slopes.

#### 4.2.3 Visual Navigation Results

The visual navigation tasks consist of a sparse goal tracking task in which the agent must navigate around obstacles to reach distant waypoints.
To test the trained agent, we created an obstacle-field experiment ([fig. 8](#S4.F8 "In 4.2.3 Visual Navigation Results ‣ 4.2 Visual Locomotion and Navigation ‣ 4 Results ‣ GaussGym: An open-source real-to-sim framework for learning locomotion from pixels")). In this scenario a sparse goal was placed behind clutter, and a penalty region was introduced via a yellow patch on the floor. When the agent enters the penalty region it receives a negative reward signal during training. The RGB policy successfully avoided the patch, while the depth-only policy failed, demonstrating that RGB conveys rich semantic cues beyond geometric depth, enabling policies to reason about environmental semantics. Crucially, these results highlight the importance of using RGB input over depth-only sensing.

We furthermore performed a large-scale ablation of multiple design parameters. We tested our robots in 4 simulation scenarios (flat, steep, and short and tall stairs), as shown in Appendix [table 2](#A1.T2 "In A.2 Policy Learning ‣ Appendix A Appendix ‣ GaussGym: An open-source real-to-sim framework for learning locomotion from pixels"). In summary, not regressing on the voxel grid or not using a pre-trained DINO encoder reduces performance. Furthermore, training on a large number of scenes provides significant improvement in performance compared to using 10 %10\text{\,}\% or 50 %50\text{\,}\% of the scenes, highlighting the relevance of the seamless infrastructure to train across multiple scenes in GaussGym.

![Refer to caption](2510.15352v1/semantics_nonlinear_cropped.png)

## 5 Limitations

Visual sim-to-real transfer remains a difficult and largely unsolved problem, and GaussGym offers a promising platform for developing algorithms to narrow this gap. In simulation, our vision-based policies learned to avoid high-cost regions and achieved precise foothold placement. Yet, further experiments are required to assess generalization across a broader set of tasks. For example, our walking policy was not evaluated on unseen staircases during training, and we observed a decline in the precise foot placement seen in simulation when transferring to real-world scenarios.
Transferring visual policies to real hardware introduces additional challenges, including physical delays (e.g., image latency) and the reliance on egocentric observations. In contrast, geometry-based methods that leverage elevation maps and high-frequency state estimation (e.g., 400 Hz) substantially simplify the locomotion problem.

For tasks where visual information is critical—such as adhering to social norms (e.g., walking on a sidewalk or crosswalk)—GaussGym currently lacks automated mechanisms for generating cost or reward functions. Foundational language models could help shape agent behavior by defining these functions, but in this work we relied on hand-crafted cost terms.

Assets in GaussGym are initialized with uniform physical parameters (e.g., friction), which prevents accurate simulation of surfaces like ice, mud, or sand—limiting the connection between “how something looks and how it feels” [Chen et al. 2024a](#bib.bib12).

Although GaussGym builds on state-of-the-art vision models, it inherits their limitations. For example, Veo’s outputs can be inconsistent, sometimes requiring re-prompting, and offer limited camera control through text-only inputs. Future integration of more controllable and temporally consistent world models, such as Genie 3 ([DeepMind 2025](#bib.bib16)), presents a clear path to improvement. Finally, our methods for generating worlds from video models cannot yet handle dynamic scenes or simulate fluids and deformable assets beyond the simple rigid-body physics provided by IsaacGym.

## 6 Conclusion

We present GaussGym, a fast, open-source photorealistic simulator for training visual locomotion and navigation policies directly from RGB. GaussGym supports scenes from real-world robot deployments, smartphone scans, video-generation models, and existing datasets. Policies trained in GaussGym exhibit vision-perceptive behavior in simulation and show partial transfer to real-world scenarios. With this work, we provide an open baseline for training visual navigation and locomotion policies to benefit the research community. Just as earlier generations of massively parallel, GPU-based physics simulators democratized geometric locomotion learning, we expect GaussGym to accelerate progress and spur new advances in vision-based locomotion and navigation.

#### Acknowledgments

We would like to thank Brent Yi, Angjoo Kanazawa, Marco Hutter, Karen Liu, and Guanya Shi for their valuable feedback and support. This work was supported in part by an NSF Graduate Fellowship, the ONR MURI N00014-22-1-2773, the BAIR Industrial Consortium, and Amazon. We also thank NVIDIA for providing compute resources through the NVIDIA Academic DGX Grant.

## References

## Appendix A Appendix

### A.1 Additional Scenes and Motion Blur

![Refer to caption](2510.15352v1/large_scene_cropped.png)
![Refer to caption](2510.15352v1/motion_blur_nonlinear_cropped.png)

### A.2 Policy Learning

|  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | Vision | | Blind | | Vision  w/o voxel | | Vision  w/o DINO | | Vision  110\tfrac{1}{10} scenes | | Vision  12\tfrac{1}{2} scenes | |
| Scenario | A1 | T1 | A1 | T1 | A1 | T1 | A1 | T1 | A1 | T1 | A1 | T1 |
| Flat | 100.0 | 100.0 | 98.1 | 97.2 | 100.0 | 98.3 | 100 | 96.7 | 94.3 | 99.2 | 99.0 | 99.2 |
| Steep | 99.3 | 97.1 | 89.4 | 87.6 | 91.9 | 87.0 | 95.6 | 91.5 | 88.1 | 88.3 | 95.5 | 94.1 |
| Stairs (short) | 98.7 | 97.4 | 80.8 | 72.3 | 85.2 | 82.7 | 92.3 | 87.5 | 79.7 | 74.8 | 86.3 | 84.9 |
| Stairs (tall) | 94.4 | 92.5 | 74.0 | 60.5 | 80.8 | 76.3 | 88.3 | 82.8 | 67.3 | 58.2 | 83.9 | 75.2 |

![Refer to caption](2510.15352v1/foot_swing_nonlinear_cropped.png)

|  |  |  |
| --- | --- | --- |
| Reward | Expression | Weight |
| Ang Vel XY | ‖ω‖2\|\omega\|^{2} | -0.2 |
| Orientation | ‖α‖2\|\alpha\|^{2} | -0.5 |
| Action Rate | ‖qt∗−qt−1∗‖2\|q\_{t}^{\*}-q\_{t-1}^{\*}\|^{2} | -1.0 |
| Pose Deviation | ‖qt−q^‖2\|q\_{t}-\hat{q}\|^{2} | -0.5 |
| Feet Distance | (fleft,x​y−fright,x​y)<0.1(f\_{\text{left},xy}-f\_{\text{right},xy})<0.1 | -10.0 |
| Feet Phase | 1f,contact×ϕ≤0.251\_{f,\text{contact}}\times\phi\leq 0.25 | 5.0 |
| Stumble | ‖Ff,x​y‖≥2​‖Ff,z‖\|F\_{f,xy}\|\geq 2\|F\_{f,z}\| | -3.0 |

|  |  |  |
| --- | --- | --- |
| Reward | Expression | Weight |
| Linear Velocity Tracking | exp(−∥vx​y−vx​y∗∥2/0.25)\exp(-\|v\_{xy}-v\_{xy}^{\*}\|^{2}/0.25) | 1.0 |
| Angular Velocity Tracking | exp(−∥ωz−ωz∗∥2/0.25)\exp(-\|\omega\_{z}-\omega\_{z}^{\*}\|^{2}/0.25) | 0.5 |

|  |  |  |
| --- | --- | --- |
| Reward | Expression | Weight |
| Position tracking | 1t<1​(1−0.5​‖rx​y−rx​y∗‖)1\_{t<1}(1-0.5\|r\_{xy}-r\_{xy}^{\*}\|) | 10.0 |
| Yaw tracking | 1t<1​(1−0.5​‖ψ−ψ∗‖)1\_{t<1}(1-0.5\|\psi-\psi^{\*}\|) | 10.0 |

|  |
| --- |
| Observation |
| Base Ang Vel ωb\omega\_{b} |
| Projected Gravity Angle α\alpha |
| Joint Positions qq |
| Joint Velocities q˙\dot{q} |
| Swing phase ϕ\phi |
| Image I∈(640×480)I\in(640\times 480) |

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
