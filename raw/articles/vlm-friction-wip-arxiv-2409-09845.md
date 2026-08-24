---
source_url: https://arxiv.org/abs/2409.09845
ingested: 2026-08-24
sha256: 808bdc0610484e43abbbdd0008a41d61ea1921086b43a19c73349b5cd3e6976f
---
##### Report GitHub Issue

Content selection saved. Describe the issue below:

![](/static/base/1.0.1/images/icons/smileybones-small.svg)
![arXiv logo](/static/base/1.0.1/images/arxiv-logo-primary-light.svg)

# Friction-Aware Safety Locomotion for Wheeled-legged Robots using Vision Language Models and Reinforcement Learning

###### Abstract

Controlling Wheeled-legged robots is challenging especially on slippery surfaces due to their dependence on continuous ground contact. Unlike quadrupeds or bipeds, which can leverage multiple fixed contact points for recovery, wheeled-legged robots are highly susceptible to slip, where even momentary loss of traction can result in irrecoverable instability. Anticipating ground physical properties such as friction before contact would allow proactive control adjustments, reducing slip risk. In this paper, we propose a friction-aware safety locomotion framework that integrates Vision-Language Models (VLMs) with a Reinforcement Learning (RL) policy. Our method employs a Retrieval-Augmented Generation (RAG) approach to estimate the Coefficient of Friction (CoF), which is then explicitly incorporated into the RL policy. This enables the robot to adapt its speed based on predicted friction conditions before contact. The framework is validated through experiments in both simulation and on a physical customized Wheeled Inverted Pendulum (WIP). Experimental results show that our approach successfully completes trajectory tracking tasks on slippery surfaces, whereas baseline methods relying solely on proprioceptive feedback fail. These findings highlight the importance and effectiveness of explicitly predicting and utilizing ground friction information for safe locomotion. They also point to a promising research direction in exploring the use of VLMs for estimating ground conditions, which remains a significant challenge for purely vision-based methods.

## I Introduction

Wheeled-legged robots combine the speed of wheels with the adaptability of legs, making them ideal for applications from industrial automation to disaster response [[1](#bib.bib1), [2](#bib.bib2), [3](#bib.bib3)]. These systems are particularly vulnerable when traversing slippery terrain compared to quadrupedal or bipedal robots, primarily due to their reliance on continuous rolling contact with the ground. Once slipping occurs, the wheels can lose effective traction and continue spinning without generating meaningful ground reaction forces. This loss of contact makes it extremely difficult for the system to stabilize or recover from disturbances. Such robots would greatly benefit from the ability to predict environmental conditions like slippery surfaces or foot sinkage through exteroceptive sensing before making contact.

Most control strategies for wheeled-legged robots rely on direct interaction with the terrain, requiring physical contact and adaptation through proprioceptive feedback. Although both model-based approaches [[2](#bib.bib2), [4](#bib.bib4)] and reinforcement learning (RL)-based locomotion controllers [[5](#bib.bib5), [6](#bib.bib6), [7](#bib.bib7), [8](#bib.bib8), [9](#bib.bib9), [10](#bib.bib10)] have demonstrated the ability to handle complex terrains in legged systems, they cannot be directly applied to wheeled-legged platforms due to their distinct contact dynamics. Hybrid approaches that combine model-based and learning-based methods have been proposed to leverage the advantages of both and mitigate their respective limitations [[11](#bib.bib11), [12](#bib.bib12), [13](#bib.bib13)]. However, as all of these methods depend solely on proprioceptive sensing, they require reactive recovery strategies to adapt the robot’s behavior after a slip occurs, limiting their effectiveness in preventing falls proactively.

![Refer to caption](2409.09845v2/concept_fig_new.png)

One promising direction is to estimate ground properties, such as friction, using vision-based methods. However, friction inherently depends on contact interactions and force transmission, making it difficult to estimate accurately from visual information alone. Learning friction estimation in simulation is also challenging since replicating the physical effects of terrain interaction (e.g., stiffness and friction) remains difficult. Friction-From-Vision (FFV) is not a new topic, but a generalizable solution and a large-scale dataset are still lacking. Collecting ground-truth friction coefficients typically requires specialized physical instrumentation, which poses a significant barrier to building large-scale, labeled datasets.

To enable safer locomotion of wheeled-legged robots on slippery surfaces, we propose a friction-aware control framework that integrates a VLM with RL. Using prompt engineering—such as material descriptions—the VLM infers the ground CoF, allowing the robot to proactively adapt its behavior based on anticipated terrain conditions. This approach addresses the limitations of purely vision-based methods, which lack the semantic understanding required to reason about friction. For instance, identifying a banana peel as slippery relies on commonsense knowledge, not just visual cues. By employing the Retrieval-Augmented Generation (RAG) technique, our method estimates CoF without requiring paired image-friction datasets or collecting ground-truth labels. This eliminates the need to train a new estimator from scratch and enables efficient, scalable friction inference.

The contributions of this paper are threefold. First, we propose a friction-aware RL locomotion framework that integrates a VLM for the control of wheeled humanoid robots. Second, we introduce a vision-based friction estimation module that utilizes the RAG technique in conjunction with a VLM to estimate ground friction coefficients without requiring the training of a new neural network or collecting paired datasets. Third, we demonstrate the effectiveness of the proposed framework through hardware experiments on a physical WIP, a reduced-order model of a wheeled-legged robot, showing improved safety and tracking performance compared to classical controllers and proprioception-based RL policies.

## II Related Works

### II-A Friction from Vision.

Estimating ground friction remains a challenge without a universal solution. Variations in image intensity suggest rough surfaces, correlating with higher friction. Humans often assess slipperiness through visual cues like surface gloss and roughness, though these perceptions can be imprecise [[14](#bib.bib14), [15](#bib.bib15)]. Some methods predict friction by identifying surface types and referencing known databases [[16](#bib.bib16)], but these are limited by the lack of a comprehensive friction-vision dataset and environmental factors. VLMs excel in visual-language reasoning tasks, often achieving impressive zero-shot and few-shot performance with minimal training. Inspired by [[17](#bib.bib17)], which used text mining to infer CoF, we propose leveraging VLMs’ strong generalization and reasoning abilities with visual data to estimate CoF across surfaces.

### II-B Locomotion with Friction

Recent research on quadruped locomotion highlights robustness and agility, focusing on navigating difficult terrains and performing parkour-like tasks [[6](#bib.bib6), [7](#bib.bib7), [18](#bib.bib18), [19](#bib.bib19), [20](#bib.bib20)]. Similarly, humanoid locomotion has been extensively studied using both model-based and model-free methods [[21](#bib.bib21), [22](#bib.bib22), [23](#bib.bib23), [24](#bib.bib24), [25](#bib.bib25)].

Anticipating environmental challenges is crucial for robots to avoid accidents and improve task performance. For example, incorporating visual information increased success rates in stair climbing from 40% to 100% [[8](#bib.bib8)], and bipedal robots have been shown to select less slippery paths for safer navigation [[16](#bib.bib16)]. This highlights the importance of integrating environmental factors into RL to prevent slips and enhance safety. Recent work also addresses locomotion on slippery ground but requires extensive training [[26](#bib.bib26)].

## III Methods

The proposed ground friction-aware locomotion framework comprises two key components: 1) the FFV module, which uses VLMs to estimate the ground friction coefficient (ftf\_{t}) from images, and 2) an RL policy trained entirely in simulation, then transferred to the real world with zero-shot learning. The procedure of our framework is shown in Fig. [1](#S1.F1 "Fig. 1 ‣ I Introduction ‣ Friction-Aware Safety Locomotion for Wheeled-legged Robots using Vision Language Models and Reinforcement Learning").

### III-A Friction Estimation using Vision Language Models

We introduce the FFV module, which employs a selected VLM to estimate the COF of the ground. We chose GPT4-o due to its performance and convenient API. To have a good friction estimation, we need both vision information and a dataset consisting of friction information of common surfaces to refer to. In this situation, several approaches to utilizing VLMs can be considered, ranked in terms of modification to VLMs: pretraining on a specialized dataset, fine-tuning [[27](#bib.bib27)], RAG [[28](#bib.bib28)], and prompt engineering. While pretraining and fine-tuning yield promising results, they demand large-scale datasets, which are currently lacking. To address this limitation, we employ RAG with an open-source dataset, supplemented by 94 text-based friction coefficient references [[29](#bib.bib29), [30](#bib.bib30)]. The dataset used is the Ground-Truth coefficient of Friction dataset (GTF) [[17](#bib.bib17)], comprising 129 images of 43 walkable surfaces.

For each walkable surface in the GTF, we utilized a pre-trained CLIP visual encoder to encode the original image xi,i∈Nx\_{i},i\in N, where NN is the total number of surfaces, into features fimgi∈ℝD,i∈[1,N]f\_{\text{img}}^{i}\in\mathbb{R}^{D},i\in[1,N], DD represents the dimension of the CLIP features. The format of the text friction coefficient data is similar to:

For each piece of data, we construct a simple prompt tit\_{i} as ”[Material] and [Against Material]”, i∈M,i\in M, where MM is the number of text friction coefficient data entries, and use the pre-trained CLIP text encoder to encode tit\_{i} into features ftexti∈ℝD,i∈[1,M]f\_{\text{text}}^{i}\in\mathbb{R}^{D},i\in[1,M]. Subsequently, pairs of image feature-image path and text feature-text are cached in a cache file. For the input image yy, we still use the CLIP visual encoder to encode its features as fyf\_{y}. We read all fxf\_{x} and ftextf\_{\text{text}} from the cache file. Then they are concatenated into two matrices, Fimg∈ℝN×DF\_{\text{img}}\in\mathbb{R}^{N\times D} and Ftext∈ℝM×DF\_{\text{text}}\in\mathbb{R}^{M\times D}. We calculate the cosine similarity between fyf\_{y} and FtextF\_{\text{text}}, and between fyf\_{y} and FimgF\_{\text{img}},

|  |  |  |  |
| --- | --- | --- | --- |
|  | cosine\_similarity​(fy,Ftext)=fy⋅FtextT‖fy‖​‖Ftext‖cosine\_similarity​(fy,Fimg)=fy⋅FimgT‖fy‖​‖Fimg‖\begin{split}\text{cosine\\_similarity}(f\_{y},F\_{\text{text}})=\frac{f\_{y}\cdot F\_{\text{text}}^{T}}{\|f\_{y}\|\|F\_{\text{text}}\|}\\ \text{cosine\\_similarity}(f\_{y},F\_{\text{img}})=\frac{f\_{y}\cdot F\_{\text{img}}^{T}}{\|f\_{y}\|\|F\_{\text{img}}\|}\end{split} |  | (1) |

takes the top KK as cached knowledge from the image and text caches, and input them together with the input prompt into GPT4-o. The input prompt defines the format of the text returned by GPT4-o, so the estimated CoF value can be obtained using regular matching in the text returned by GPT4-o. Each estimation takes around 5 seconds, affected by internet condition and server burden.

### III-B Friction-Aware Reinforcement Learning

Using history of proprioception as an observation in RL policies has become a standard approach in legged robot control [[6](#bib.bib6), [7](#bib.bib7), [18](#bib.bib18), [19](#bib.bib19), [20](#bib.bib20)]. The underlying assumption is that proprioceptive data contains enough information to replace privileged parameters such as ground friction. The inherent limitation of this method is that it requires the robot to experience new situations for the proprioception history to capture meaningful data. While this can be done in real-time, for systems with limited ground contact points, reacting and recovering is particularly challenging. A good example is to imagine a human wearing wheeled skates, trying to regain balance to avoid falling—such recovery. For this reason, we decided to explicitly incorporate an estimated ground friction coefficient in the RL policy, rather than relying solely on the robot’s proprioception. We trained the RL policy separately from a VLM in simulation. To consider the VLM’s estimation error, we introduced Gaussian noise and random estimation errors in the estimated value, which was then fed into the RL policy.

Observation. Having more information does not always mean better performance. Some of it may be redundant and sometimes even increases the reality gap [[31](#bib.bib31)]. In a classical approach, slipping in the WIP system is examined in [[32](#bib.bib32)], where the absolute slip γ\gamma is defined as r​α˙−x˙2​π​r\frac{r\dot{\alpha}-\dot{x}}{2\pi r}. Here, rr is a wheel radius, α˙\dot{\alpha} is the angular velocity, and x˙\dot{x} is the linear velocity. The extended equation for calculating friction is f^=μ​sign​(γ)\hat{f}=\mu\text{sign}(\gamma) where μ\mu is the friction coefficient. Inspired by this, we designed our observation space as follows:

|  |  |  |  |
| --- | --- | --- | --- |
|  | ot={xw,x˙w,β,β˙,xt​r,at−1,ct,μ^}\begin{split}o\_{t}=\{x\_{w},\dot{x}\_{w},\beta,\dot{\beta},x\_{tr},a\_{t-1},c\_{t},\hat{\mu}\}\end{split} |  | (2) |

where, xwx\_{w} and x˙w\dot{x}\_{w} represent the angular position and velocity of the wheel, while β\beta and β˙\dot{\beta} denote the angular position and velocity of the pole joint. The variable at−1a\_{t-1} is the previous action, ctc\_{t} is the user command, and μ^\hat{\mu} is the estimated friction from the VLM. Additionally, xt​rx\_{tr} refers to the position of the translation joint. It is important to note that xt​rx\_{tr}, a global position, is not accessible in the real world and is not accurate even if visual odometry is used. When there’s a sudden change in xt​rx\_{tr}, we cannot tell whether it’s caused by slipping or sensor noise, making this information unreliable. But we observed that including xt​rx\_{tr} in the observation space improves the tracking performance and stability during RL policy training. This is because the xt​rx\_{tr} provides the RL policy with additional information about slip, given slipping is caused by the disparity between xt​rx\_{tr} and xwx\_{w}. As a training trick, we initially used xt​rx\_{tr} and construct the reward function to reduce the disparity between xt​rx\_{tr} and xwx\_{w} so the policy is trying to learn to ”avoid slipping”. When the reward value converges and the performance is stable, we substitute the xt​rx\_{tr} with xwx\_{w} in the deployment stage.

Action Space. The action ata\_{t} represents the desired velocity for the wheel joint. Empirically, we found that using velocity mode with a built-in PD controller (kp=0,kd=3k\_{p}=0,k\_{d}=3) leads to faster training convergence and simplifies sim-to-real transfer compared to directly learning the torque.

Reward Function. The reward function is designed considering the five major components as follows.

|  |  |  |  |
| --- | --- | --- | --- |
|  | Rt=1−βt2⏟Keep balance−0.01​|x˙t|+0.005​|β˙t|⏟Penalty for oscillation−3​|x˙t−r​α˙t|⏟Avoid Slipping+0.3​ζtet+0.01​aj,t2⏟Tracking Component−(Al+(Ah−Al)​ζt)​aj,t2⏟Output penalty\begin{split}R\_{t}=&\underbrace{1-\beta\_{t}^{2}}\_{\text{Keep balance}}-\underbrace{0.01|\dot{x}\_{t}|+0.005|\dot{\beta}\_{t}|}\_{\text{Penalty for oscillation}}-\underbrace{3|\dot{x}\_{t}-r\dot{\alpha}\_{t}|}\_{\text{Avoid Slipping}}\\ &+\underbrace{\frac{0.3\zeta\_{t}}{e\_{t}+0.01}a\_{j,t}^{2}}\_{\text{Tracking Component}}-\underbrace{(A\_{l}+(A\_{h}-A\_{l})\zeta\_{t})a\_{j,t}^{2}}\_{\text{Output penalty}}\end{split} |  | (3) |

This encourages the system to track the desired velocity while maintaining stability and preventing slip. Since we use a single actuator to balance and track the signal, producing smooth outputs is crucial for effective sim-to-real transfer. The output penalty term is designed to penalize actions that apply excessive force or velocity in the system, ensuring smoother control. The AlA\_{l} and AhA\_{h} are two predefined parameters, the lowest output penalty and the highest output penalty, respectively. We observed that incorporating the ”avoiding slipping” term significantly enhances tracking performance.

Curriculum Learning. In the reward function ([3](#S3.E3 "In III-B Friction-Aware Reinforcement Learning ‣ III Methods ‣ Friction-Aware Safety Locomotion for Wheeled-legged Robots using Vision Language Models and Reinforcement Learning")), the term ζt\zeta\_{t} contributes to curriculum learning and is defined as follows.

|  |  |  |  |
| --- | --- | --- | --- |
|  | ζt=(t​a​n​h​(T¯t/Tm​a​x∗8−3)+1)/2\zeta\_{t}=(tanh(\bar{T}\_{t}/T\_{max}\*8-3)+1)/2 |  | (4) |

where T¯t\bar{T}\_{t} is the current mean episode length and Tm​a​xT\_{max} is the maximum episode length. Initially, the focus of the training process is on learning balancing, gradually transitioning attention towards the tracking task. The tanh\tanh function ensures that this parameter increases slowly during the early stages of training, allowing the policy to focus on easier tasks.

![Refer to caption](2409.09845v2/experiment_setup.png)

## IV Experiments

### IV-A Customized Wheeled-Inverted Pendulum

A customized WIP was developed to verify the proposed framework’s feasibility, as shown in Fig. [2](#S3.F2 "Fig. 2 ‣ III-B Friction-Aware Reinforcement Learning ‣ III Methods ‣ Friction-Aware Safety Locomotion for Wheeled-legged Robots using Vision Language Models and Reinforcement Learning")(a, b). This system is a simplified version of the wheeled-legged robot, SATYRR [[1](#bib.bib1)]. Unlike the traditional inverted pendulum, our WIP system includes a wheel joint and a roll joint, causing slipping to happen more easily and making control more challenging. For example, when the wheel accelerates aggressively, it often lifts off and loses contact with the ground.

### IV-B Simulation and Hardware details

Hardware Setup. The system employs the same actuators as a wheeled humanoids [[3](#bib.bib3)], with an inertial measurement unit (VN-100, VectorNav, USA) mounted on the pole link. We used a RealSense (D405 model) camera to obtain the ground images. Five types of surface materials (rubber, anti-slip tape, wood, cardboard, and grass) and two wheels with different friction conditions are used in the real-world tracking task. The control loop runs at 400 Hz, and the RL policy’s decision frequency is 50 Hz. All software is connected via the Robot Operating System (ROS).

Simulation Environment Setup.
We utilize the IsaacGym simulator to train our RL policy and all baselines for WIP. We configure the static and dynamic friction of the ground to be 0, and we adjust the friction condition of the WIP’s wheel accordingly. IsaacGym calculates the CoF between two surfaces as the average of the CoFs of each surface.

| Model | Network | Model | Network |
| --- | --- | --- | --- |
| Actor | FC (10, 64) | Adaptation Module | Conv1d |
| Lrelu | Length = 40 |
| FC (64, 64) | Num of Kernels = 64 |
| Lrelu | Kernel Size = 3 |
| FC (64, 1) | Stride = 1 |
| Critic | FC (10, 64) | Padding = 1 |
| Lrelu | FC(2560, 256) |
| FC (64, 64) | Relu |
| Lrelu | FC(256, 64) |
| FC (64, 1) | Relu |
| Environment Encoder | FC (1, 2) | FC(64, 8) |
| Lrelu | Relu |
| FC (2, 1) |  | FC(8, 1) |

### IV-C Experimental Plan

The experiments aim to: 1) validate the friction estimation performance of the FFV module; 2) assess how effectively our framework completes the tracking task without failure across various surface types compared to baseline methods; and 3) analyze the impact of incorporating privileged information xt​rx\_{tr} into the observation space.

Ground Friction Coefficient Estimation of FFV Module. We evaluated the FFV module using the GTF dataset [[17](#bib.bib17)], with Root Mean Squared Error (RMSE) as the metric and 2-, 5-, and 10-fold cross-validation following [[17](#bib.bib17)]. For baselines, we compared against a vision-based method from [[16](#bib.bib16)] and the Word Material-Material similarity (WordMM) method from [[17](#bib.bib17)], representing vision-only and commonsense-based friction estimation, respectively. The former uses a CNN trained on GTF, but due to outdated code, we implemented a Vision Transformer (ViT) [[33](#bib.bib33)] following the same training pipeline.

Safety Tracking Performance Evaluation. We conducted safety-tracking tasks in simulation and the real world using our WIP. We prioritize success rate as our primary evaluation criterion while also assessing the tracking performance of our method and baseline approaches. For the baselines, the classical LQR [[34](#bib.bib34)], PPO [[35](#bib.bib35)], PPO with Domain Randomization (DR)[[36](#bib.bib36)] and Teacher and Student Policy from RMA [[9](#bib.bib9)], which are commonly used to control wheeled robots, are selected. In the observation part, the main difference between ours and PPO is that our method uses CoF explicitly. To ensure fairness of comparison and follow the common trend, we use the DR technique for friction in PPO.

![Refer to caption](2409.09845v2/Friction_estimation_result.png)

To implement RMA, the privileged information includes the CoF, with the encoder network generating an extrinsic vector ztz\_{t} of size 1 based on this coefficient. To ensure a fair comparison, we keep the control frequency, environment setup, and training duration consistent across all methods, training each policy until reward saturation. We select a neural network that achieves as high a reward as possible without exhibiting high-frequency outputs characteristic of bang-bang control, in order to minimize the sim-to-real gap.

![Refer to caption](2409.09845v2/vlm_material.png)

Ablation Study on Translation Joint.
It is not natural to adopt translation joints as observations because it is difficult to obtain actual values from hardware. As discussed in Section [III-B](#S3.SS2 "III-B Friction-Aware Reinforcement Learning ‣ III Methods ‣ Friction-Aware Safety Locomotion for Wheeled-legged Robots using Vision Language Models and Reinforcement Learning"), the difference between the velocity of the translation joint and that of the wheel joint is crucial for detecting slip. In the ablation study, we focus on evaluating the impact of incorporating the translation joint on RL tracking performance in slippery conditions. In addition, we also explore how simple Domain Randomization (DR) [[36](#bib.bib36)] can contribute to the anti-slip effect.

|  |  |  |
| --- | --- | --- |
|  |  |  |

## V Results and Analysis

### V-A Friction Coefficient Estimation Results

The friction coefficient estimation results are summarized in Fig. [3](#S4.F3 "Fig. 3 ‣ IV-C Experimental Plan ‣ IV Experiments ‣ Friction-Aware Safety Locomotion for Wheeled-legged Robots using Vision Language Models and Reinforcement Learning"). Despite the FFV module with VLM performs a bit worse than a Vision Transformer (ViT) and Word MM, our FFV module provides reasonably accurate values, particularly for materials that are known to be more slippery or rough (see Fig. [3](#S4.F3 "Fig. 3 ‣ IV-C Experimental Plan ‣ IV Experiments ‣ Friction-Aware Safety Locomotion for Wheeled-legged Robots using Vision Language Models and Reinforcement Learning")-C). Moreover, it is quite obvious that ViT module tends to overfit due to the limited size of the training dataset.

We observed that FFV module has ability to handle edge cases involving additional material properties, we altered surface conditions by adding substances like water or oil and evaluated each model’s response. As shown in Fig. [4](#S4.F4 "Fig. 4 ‣ IV-C Experimental Plan ‣ IV Experiments ‣ Friction-Aware Safety Locomotion for Wheeled-legged Robots using Vision Language Models and Reinforcement Learning"), ViT fails to respond appropriately—for example, it predicts a higher CoF for an oil-covered surface than for a dry one. In contrast, the VLM, leveraging the RAG approach, adjusts its estimates more reasonably, suggesting that it can better incorporate contextual cues such as surface material or added substances. WordMM assumes perfect surface-type classification, which explains its relatively strong performance under these conditions.

### V-B Tracking Performance Comparison in Simulation

We report the simulation tracking performance comparison results in Fig. [5](#S4.F5 "Fig. 5 ‣ IV-C Experimental Plan ‣ IV Experiments ‣ Friction-Aware Safety Locomotion for Wheeled-legged Robots using Vision Language Models and Reinforcement Learning"). Our method attained the smallest tracking error, even outperforming the teacher policy slightly. This suggests that incorporating the friction coefficient into an RL policy is more effective than relying on the encoder network’s latent vector. A similar finding is reported in [[37](#bib.bib37)], where the estimator is trained directly rather than using a latent vector. The student policy shows significantly higher tracking error variability compared to other methods. We observed that while the adaptation module can reproduce the encoder network using only the robot’s proprioception history, the system tends to fall suddenly and cannot recover due to its limited contact points with the ground. This suggests that relying solely on proprioception may not be ideal for learning recovery motions (e.g., RMA) in systems with few degrees of freedom and contact points. Using a DR can enhance the robustness of a RL policy, but its overall effectiveness is constrained, offering only marginal improvements. Furthermore, we observed that incorporating a translational joint significantly enhances tracking performance. This is attributed to the fact that relying solely on the wheel joint does not provide sufficient information to accurately capture slip behavior. In the case of LQR, the lack of knowledge about ground friction causes the system to focus solely on minimizing tracking error, which often leads to failure.

We compare all algorithms in simulation and present the resulting trajectories in Fig. [8](#S5.F8 "Fig. 8 ‣ V-C Tracking Performance Comparison in Physical System. ‣ V Results and Analysis ‣ Friction-Aware Safety Locomotion for Wheeled-legged Robots using Vision Language Models and Reinforcement Learning") for detailed analysis. Methods that do not utilize the translation joint show relatively low initial tracking error but struggle to follow high-magnitude desired trajectories, resulting in stationary behavior and large steady-state errors. In contrast, our method produces the smoothest trajectories, suggesting better sim-to-real transferability, which is further validated in hardware experiments. Additionally, our approach achieves the highest reward in simulation, indicating that incorporating both friction and translation joint information is essential for learning smooth and adaptive tracking behavior.

We conducted an additional experiment to analyze the sensitivity of wheeled robot control to the accuracy of the predicted CoF. In simulation, we fixed the input CoF provided to the policy and uniformly randomized the actual environment CoF between 0.5 and 1.5. The resulting tracking error and success rate (number of successful trials out of 50) are reported in Fig. [9](#S5.F9 "Fig. 9 ‣ V-C Tracking Performance Comparison in Physical System. ‣ V Results and Analysis ‣ Friction-Aware Safety Locomotion for Wheeled-legged Robots using Vision Language Models and Reinforcement Learning"), with corresponding real-world results shown in Fig. [8](#S5.F8 "Fig. 8 ‣ V-C Tracking Performance Comparison in Physical System. ‣ V Results and Analysis ‣ Friction-Aware Safety Locomotion for Wheeled-legged Robots using Vision Language Models and Reinforcement Learning").b. The simulation setup follows the same configuration described in the main manuscript.

Our method achieves almost the highest success rate and lowest tracking error when the input CoF closely matches the actual environment CoF. When the predicted CoF is lower than the ground truth, the policy behaves conservatively, which increases stability and success rate but may result in higher tracking error. Conversely, when the predicted CoF exceeds the actual value, the policy becomes overly aggressive, increasing the risk of slippage and decreasing the success rate. These findings highlight the importance of accurate CoF estimation for achieving both safe and precise locomotion.

### V-C Tracking Performance Comparison in Physical System.

The tracking performance results in the real world are presented in Fig. [7](#S5.F7 "Fig. 7 ‣ V-C Tracking Performance Comparison in Physical System. ‣ V Results and Analysis ‣ Friction-Aware Safety Locomotion for Wheeled-legged Robots using Vision Language Models and Reinforcement Learning"), where we observed that only our framework and LQR were successfully transferred to the physical system. Other methods, such as PPO and RMA, demonstrated either overly aggressive or conservative behaviors, resulting in oscillations or stationary states. Although LQR performas the worst in simulation, it can still be transferred to the real system because in simulation, the rigid bodies are perfect and they lose contact much easier than reality while in real system, the rubber wheel acts as a buffer to allow constant rolling contact with the ground. Meaning aggressive motions would become even more aggressive in reality than simulation. Specifically, for RMA, the output variance, as noted in the simulation, was large, often leading to more aggressive motions. In contrast, domain randomization with PPO tended to produce more conservative actions, like stationary motions, to prevent falls. For systems with slippery surfaces and few contact points, this may not be a surprising result. A good example is to compare standing on one foot versus using both hands and feet to support yourself when rollerblading on slippery terrain. This challenge also lies in how quickly we can detect slip and how fast the system can react. Proprioception, which relies on recording history data, often introduces delays in response. With only a single contact point, the system lacks additional mechanical options to stabilize the robot once slip occurs, making rapid recovery difficult. This highlights the importance of using a VLM to predict terrain slipperiness in advance.

Compared to LQR, our framework achieves better tracking with smoother, less aggressive motions. While the LQR-controlled inverted pendulum was tuned to be robust enough to complete most tasks, it failed on the most slippery surface due to its inability to adapt to varying ground conditions. Lacking awareness of surface properties, the LQR controller attempts to follow the reference trajectory blindly, leading to contact loss and system failure under low-friction scenarios. In contrast, our framework adjusts its motion based on estimated surface conditions, enhancing robustness and stability.

![Refer to caption](2409.09845v2/real_result.png)

| Ground Type | w2 + c1 | w2 + c2 | w1 + c3 | w1 + c4 | w1 + c5 | Overall |
| --- | --- | --- | --- | --- | --- | --- |
| LQR | 3/3 | 3/3 | 3/3 | 3/3 | 0/2 | 12/14 |
| Ours | 3/3 | 3/3 | 3/3 | 3/3 | 5/5 | 17/17 |

![Refer to caption](2409.09845v2/response_different_cof.png)

## VI Discussion and Limitations

While our algorithm demonstrated superior performance compared to other baselines, there are still several factors that require improvement. Firstly, while our customized WIP system is more complex than traditional designs, it remains considerably simpler than wheeled humanoids [[1](#bib.bib1)]. However, we believe that our algorithm can maintain its effectiveness and versatility, given its potential for seamless integration into various other applications. This is primarily because our vision-based FFV module can be seamlessly integrated into any reinforcement learning policy, making it adaptable across different hardware platforms. Secondly, the FFV module’s estimation speed is relatively slow, primarily constrained by the processing speed of OpenAI server. This is the biggest barrier to our methodology updating ground information in real time but we believe that this can be improved in the near future. Unless the ground state changes dramatically in real-time, anticipating and adjusting behavior based on the expected ground state where the robot is going to traverse on a few seconds later is enough. Estimating the friction of the surface that humans will be on a few seconds later is sufficient. One interesting avenue for future work could involve applying our algorithm to tele-operation scenarios [[38](#bib.bib38)], aiming to mitigate human errors by dynamically adjusting the user’s commands to accomplish tasks more safely. Thirdly, the absence of a large-scale friction dataset limits the accuracy of friction estimation. While VLMs combined with the RAG technique can produce reasonable predictions, there is significant potential for improvement through the use of large datasets to fine-tune or pretrain a foundation model specifically for physical parameter estimation.

Regarding sim-to-real transfer, we identified several key factors that significantly affect success. First, the presence of additional passive mechanisms, such as roll and translation joints—which are not present in typical mobile wheeled-legged robots—makes transfer more difficult. These passive joints introduce high, unmodeled friction and cannot be directly controlled in either simulation or the real world. As a result, the system frequently exhibits point contact between the wheels and the ground, which rigid-body simulators struggle to handle accurately. Second, smooth action outputs are critical. While some policies may achieve high rewards in simulation, they often exhibit bang-bang behavior with high-frequency switching, which is unrealistic and can be harmful to physical hardware. Ensuring smoother control trajectories improves robustness and safety during real-world execution. Third, using a compact observation space improves transferability. Larger observation spaces introduce more variability and potential overfitting to simulation-specific features, increasing the likelihood of unexpected behavior in the real world.

## VII Conclusion

In this work, friction-aware safety locomotion framework using vision language models is proposed. We first introduce the FFV module with VLMs, which can estimate the ground friction coefficient—a parameter that is difficult to measure and for which there is limited dataset availability. Although it still has limitations in real-time performance, it can predict the risk of the system falling in advance and further improve driving safety by reasonably understanding the ground condition by utilizing texture information, thereby successfully completing driving tasks. We demonstrate both in simulation and in the real world, showing that it enables adaptive behavior in wheeled robots and helps mitigate slip risks across various ground surfaces. Our implementation is straightforward and integrates seamlessly with existing PPO-based methods without requiring structural changes. We believe our work opens up intriguing research directions, such as exploring whether a VLM can be used to assess physics parameters beyond just friction.

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
