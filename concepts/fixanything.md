---
title: "FixAnything: 视频生成先验修复 3D 渲染伪影"
created: 2026-08-31
updated: 2026-08-31
type: concept
tags: [gaussian-splatting, video-diffusion, rendering, dpo, robot-env, reference]
sources: [raw/papers/fixanything-arxiv-2608-23549.md, raw/articles/fixanything-website.md]
confidence: high
---

# FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors

## 一、项目概览

FixAnything 是 CMU（Khiem Vuong, Deva Ramanan\*, Srinivasa Narasimhan\*，\* 表示 equal contribution/advising）在 ECCV 2026 的工作，arXiv:2608.23549（2026-08 提交）。核心主张：**一个通用视频扩散模型（Wan2.1-I2V-14B），只做最小修改 + 轻量 LoRA 微调（<1% 参数、最少 20 对视频），就能修复 3DGS / NeRF / mesh / 稀疏点云四种 3D 表示的渲染伪影**，并且输出保持 3D 一致（可被下游 SfM/重建使用）。

关键链接：
- 官网：https://fix-anything.github.io
- 论文：https://arxiv.org/abs/2608.23549
- 代码：Code — coming soon（发布时未开源）
- 会议：ECCV 2026

一句话概括：**把"修复渲染伪影"重新定义为 video-to-video 翻译**——劣化渲染虽然丑，但保留了相机轨迹和粗场景布局，这正是视频模型需要的控制信号；模型只需把"非自然视频"投影回"自然视频流形"。^[raw/papers/fixanything-arxiv-2608-23549.md]

## 二、背景与动机

3D 重建（NeRF/3DGS/mesh/点云）在**输入视图稀疏**或**新视角远离训练视图**时必然产生伪影：
- 3DGS → 场景中漂浮物（floaters）
- NeRF → 雾状几何幻觉
- mesh → 纹理扭曲
- 点云 → 空洞

这些伪影直接限制下游应用（内容创作、机器人仿真）——新视角渲染质量劣化到不可用。

现有解法是**每个表示配一个专用生成管线**（Nerfbusters 修 NeRF、3DGS-Enhancer 修 3DGS、ViewCrafter/GEN3C 做相机控制生成……）。问题：每次新表示出现就要重建架构、重新训练、重新造数据，无法规模化。

FixAnything 的回答：**所有表示的伪影有一个共同点——都偏离"自然视频"的流形，但同时保留相机轨迹与粗场景布局**。这个共享结构让一个预训练视频模型，经过最小适配，就能把劣化渲染"翻译"回自然视频流形。^[raw/papers/fixanything-arxiv-2608-23549.md]

## 三、核心技术

### 3.1 问题形式化（表示无关的渲染清理）

输入渲染视频 x ∈ ℝ^{T×3×H×W}，per-frame 二进制 mask m ∈ {0,1}^T（mᵢ=1 表示训练视角的干净帧，mᵢ=0 表示需要修复的劣化帧），输出干净视频 y。

核心设计：**整个渲染视频一次处理**，不是逐帧修——利用时间上下文，干净帧引导劣化帧的修复。mask 让模型知道"哪里该信、哪里该修"：干净帧保持不动（防止在已正确内容上幻觉），并作为 anchor 向相邻帧传播外观/光照/结构。

### 3.2 轻量适配：通道拼接 + LoRA

在预训练 VAE 的 latent 空间操作：
- 劣化视频 latent z_cond = E(x) 与加噪 latent z_t、mask m 沿通道维拼接：ẑ_t = [z_t; z_cond; m]
- rectified flow 插值：z_t = (1−t)·z_0 + t·ε
- flow matching 目标：L_FM = E[‖v − v_θ(ẑ_t, t)‖²]，v = ε − z_0
- **LoRA rank-64，<1% 参数**，基座模型和 VAE 冻结

为什么这么轻就够了：任务比"从零生成视频"窄得多——模型只需学会"condition 在劣化输入上"，不需要学会生成视频。**20 对配对视频就有效**（对比：prior 方法要 80K–150K 图像对）。^[raw/papers/fixanything-arxiv-2608-23549.md]

### 3.3 训练数据：DL3DV-10K 四种表示

每个场景均匀采样 k∈[3,12] 帧作训练视图，提取至少经过其中 2 个的 61 帧轨迹，用四种表示渲染配对视频：
- **NeRF**：Nerfacto 在稀疏视图上训练（新视角模糊+雾）
- **3DGS**：gsplat 7K iterations **故意欠拟合**（训练视角干净、新视角可见伪影）
- **Mesh**：MapAnything 前馈重建 → 深度拟合三角网格（训练视角帧替换为原图，因为天空/遮挡边界深度不可靠）
- **稀疏点云**：只保留 COLMAP 在训练视图中可见的 keypoints（纹理缺失区域无点，训练视角帧替换为原图补充上下文）

### 3.4 Stage II：几何感知偏好优化（Flow-DPO）

SFT 模型偶尔会幻觉"单帧看着合理、跨视图几何不一致"的结构（如会移动的树状结构）。检测信号：**SfM 在这类输出上会恢复出错误相机位姿**。

- **Reward**：对输出视频跑 COLMAP（SuperPoint + LightGlue），与真值比较，报告 AUC@5°（RRA + RTA）
- **配对构建**：1000 个 DL3DV 场景，每个场景 5 个随机 seed 采样，按 AUC@5° 排序，保留 AUC gap ≥ 0.2 的配对
- **Flow-DPO 损失**：L_DPO = −E[log σ(−β/2·(Δ_w − Δ_l))]，Δ 是当前模型与 SFT reference 在流速预测上的 L2 差
- **效果**：AUC@5° 从 61.12 → 68.32（+7.2%），PSNR 17.51→17.65，**零推理开销**（几何先验 baked 进 LoRA 权重）^[raw/papers/fixanything-arxiv-2608-23549.md]

### 3.5 推理

用户提供渲染视频 x + mask m，从 t=1 的噪声采样，沿学到的 velocity field 积分到 t=0，默认 50 denoising steps。超过 61 帧的轨迹按重叠 chunk 处理（边界共享 clean anchor）。

## 四、实验设置

### 4.1 协议

- 微调：LoRA rank-64，500 对 DL3DV-10K 视频，先 288×512 再升 480×832，T=61 帧；SFT 3000 iter 单 H100；Flow-DPO 再 2000 iter
- 评估：DL3DV-10K 20 个 held-out 场景，均匀选 3/6/9 帧作训练视图，其余帧每 8 帧采样为 query 集
- 指标：PSNR/SSIM/LPIPS（图像质量）+ AUC@5°（几何一致性）

### 4.2 对比结果（DL3DV，FixAnything 单模型四种输入）

| Method | 3v PSNR | 3v SSIM | 3v LPIPS | 6v PSNR | 6v SSIM | 6v LPIPS | 9v PSNR | 9v SSIM | 9v LPIPS |
|---|---|---|---|---|---|---|---|---|---|
| 3DGS（稀疏重建） | 10.97 | 0.248 | 0.567 | 13.34 | 0.332 | 0.498 | 14.99 | 0.403 | 0.446 |
| RegNeRF | 11.46 | 0.214 | 0.600 | 12.69 | 0.236 | 0.579 | 12.33 | 0.219 | 0.598 |
| FreeNeRF | 10.91 | 0.211 | 0.595 | 12.13 | 0.230 | 0.576 | 12.85 | 0.241 | 0.573 |
| DNGaussian | 11.10 | 0.273 | 0.579 | 12.67 | 0.329 | 0.547 | 13.44 | 0.365 | 0.539 |
| FSGS | 12.22 | 0.296 | 0.535 | 13.73 | 0.429 | 0.540 | 15.52 | 0.468 | 0.416 |
| 3DGS-Enhancer | 14.33 | 0.424 | 0.464 | 16.94 | 0.565 | 0.356 | 18.50 | 0.630 | 0.305 |
| Xu et al. | 14.62 | 0.471 | 0.491 | 17.35 | 0.566 | 0.396 | 19.19 | 0.616 | 0.335 |
| Difix3D | 12.85 | 0.392 | 0.557 | 14.84 | 0.445 | 0.462 | 16.76 | 0.520 | 0.399 |
| Difix3D+ | 12.37 | 0.363 | 0.512 | 14.41 | 0.424 | 0.400 | 16.39 | 0.498 | 0.330 |
| **FixAnything w/ 3DGS** | **15.18** | 0.452 | 0.408 | **17.65** | 0.561 | 0.289 | **19.76** | 0.632 | 0.269 |
| FixAnything w/ mesh | **15.74** | 0.482 | 0.366 | **17.95** | 0.583 | 0.269 | **19.86** | 0.646 | 0.233 |
| FixAnything w/ 稀疏点云 | 15.52 | 0.463 | 0.381 | 17.74 | 0.568 | 0.271 | 19.72 | 0.624 | 0.241 |

读表结论：
1. **FixAnything 用 3DGS 输入全面超过 3DGS-Enhancer/Xu et al./Difix3D+**（这些正是为 3DGS 定制的专用管线），而它是单模型同时管四种表示
2. **mesh 输入成绩最好，稀疏 COLMAP 点云紧随其后**——输入视觉信息远少于 3DGS 也能修到相当质量，说明"渲染主要起结构脚手架作用，视频先验负责填内容"
3. 稀疏重建方法全线垫底：正则化方法（RegNeRF/FreeNeRF/DNGaussian）改善几何但无法补全弱观测区域内容

### 4.3 消融

**Flow-DPO 的作用**（6 views）：

| Method | PSNR↑ | SSIM↑ | LPIPS↓ | AUC@5°↑ |
|---|---|---|---|---|
| SFT only | 17.51 | 0.554 | 0.296 | 61.12 |
| +DPO | 17.65 | 0.561 | 0.289 | **68.32** |

图像指标提升温和，**主要增益在几何一致性（AUC@5° +7.2%）**，且零推理开销。

**Mask 的作用**（6 views）：

| Variant | PSNR↑ | SSIM↑ | LPIPS↓ |
|---|---|---|---|
| No mask | 16.37 | 0.525 | 0.311 |
| With mask | 17.65 | 0.561 | 0.289 |

mask 带来 +1.3 dB PSNR。无 mask 时模型分不清"本来就干净的帧"和"轻度劣化帧"，在应保留的内容上幻觉。

**数据效率与推理速度**：

| Training vids | PSNR | SSIM | LPIPS |
|---|---|---|---|
| 20 | 16.70 | 0.531 | 0.309 |
| 50 | 17.20 | 0.548 | 0.297 |
| 100 | 17.45 | 0.556 | 0.292 |
| 500 | 17.65 | 0.561 | 0.289 |

20 对即有效，100 对后边际收益递减（预训练模型已含大部分先验，配对数据主要教 conditioning 机制）。

| Steps | PSNR | SSIM | LPIPS | Time (s) |
|---|---|---|---|---|
| 5 | 18.02 | 0.574 | 0.313 | 31 |
| 10 | 17.91 | 0.570 | 0.296 | 62 |
| 25 | 17.75 | 0.564 | 0.289 | 155 |
| 50 | 17.65 | 0.561 | 0.289 | 309 |

**5 steps 就够**（31s/61帧@480×832 单 H100，10× 加速），为蒸馏到实时清理铺路。

### 4.4 不确定性（讨论节）

5 个随机 seed 推理，逐像素标准差作不确定性估计：
- 天空/地面类区域：低不确定度（模型自信地传播输入纹理）
- 建筑等有多种合理补全的区域：高不确定度
- 与重建误差强相关：DL3DV 6 views 下，最自信 25% 像素 PSNR **25.7 dB** vs 最不自信 25% **14.4 dB**

即"哪里在幻觉"是可定位的，零训练成本（多次采样即可）。^[raw/papers/fixanything-arxiv-2608-23549.md]

## 五、与相关工作的关系

| 方法 | 表示 | 机制 | 数据量 | 3D 一致性 | 代码 |
|---|---|---|---|---|---|
| Nerfbusters | NeRF | 3D diffusion 正则化几何 | 大 | 隐式 | ✓ |
| ReconFusion | NeRF | PixelNeRF 条件逐视角生成 | 大 | 隐式 | ✓ |
| Difix3D+ | 图像 | 参考视角条件单步 image diffusion | 80K+ 图像对 | 弱（逐图修） | ✓ |
| FlowR | 稀疏重建 | 多视角 flow matching | 大 | 中等 | ✗ |
| 3DGS-Enhancer | 3DGS | 视频 LDM + 定制时空 decoder | 150K 图像对 | 中等 | ✓ |
| ViewCrafter / GEN3C | 点云 | 相机控制视频生成 | 大 | 中等 | ✓ |
| Xu et al. | 3DGS | 视频补全 + uncertainty 调制 | 大 | 中等 | ✗ |
| Epipolar-DPO / VideoGPA | T2V/I2V | 极几何/重建先验 DPO | — | 强 | 部分 |
| **FixAnything** | **4 种通用** | **Wan2.1-I2V + LoRA + mask + Flow-DPO** | **20–500 视频** | **强（位姿 reward）** | ✗ coming soon |

定位：第一个"**通用**"渲染清理模型——不针对特定表示、无架构改动、数据需求低两个数量级。方法论上贡献了三点：表示无关的渲染清理形式化、mask-aware conditioning、把几何一致性当偏好优化问题（位姿精度当 reward）。

## 六、实现细节（工程视角）

- 基座：Wan2.1-I2V-14B（DiT，rectified flow）
- LoRA rank-64（<1% 参数），VAE + 基座冻结
- 训练：SFT 3000 iter + Flow-DPO 2000 iter，单 H100
- 推理：50 steps（5 steps 可 10× 加速），61 帧 chunk 重叠处理
- 位姿评估：COLMAP + SuperPoint + LightGlue，AUC@5°（RRA+RTA）

## 七、局限性（论文自述 + 我的补充）

论文自认/隐含：
1. **幻觉不可避免**：模型必须在未观测区域"发明"内容，只在"与已有观测矛盾"时才算失败。这是生成式补全的本质，不是 bug
2. 不确定性分析是 preliminary（5 seeds 简单 std），没有系统校准
3. 长轨迹靠分块，chunk 边界的全局一致性靠 anchor 共享，理论上有限制
4. 评估数据集是 DL3DV（航拍/大场景为主），室内小物体场景覆盖少

我的补充（工程视角）：
1. **代码未开源**（Coming Soon），与 PhysGS 同样的问题——想复现只能等
2. **推理开销**：视频扩散模型 61 帧要 31s（H100 5 steps）——对机器人实时训练循环还是太慢；离线离线批量可用
3. 对**训练视图 mask 的依赖**：mask 由"哪些帧是训练视角"决定，实际应用中要知道相机位姿和训练集，若位姿估计本身有噪声，mask 标注会错
4. **对机器人渲染质量提升有直接价值**：GaussGym 这类 3DGS 训练渲染器，稀疏视角伪影会导致策略学到错误视觉特征；FixAnything 可以离线清洗训练渲染视频

## 八、对本项目（机器人导航 + IsaacLab）的启示

FixAnything 是我们文献综述系列的第三篇，与前两篇（[[gaussgym]]、[[physgs]]）正好构成闭环：

- **补 GaussGym 的渲染质量短板**：GaussGym 用 3DGS 渲染器训练机器人，但 3DGS 稀疏视角伪影（floaters）会污染视觉策略训练。FixAnything 的 3DGS 输入版本（PSNR 17.65 @6 views）正好做离线清洗：扫描 → 3DGS → 渲染轨迹视频 → FixAnything 修复 → 干净的训练视觉流。
- **稀疏点云路线对我们极有价值**：FixAnything 证明稀疏 COLMAP 点云 + 视频先验就能出高质量渲染（19.72 PSNR @9 views）。这意味着我们的扫描管线（Polycam/COLMAP）可以**跳过 NKSR mesh / 3DGS 训练**，直接渲染点云轨迹 + 生成式修复，省掉中间重建步骤——与 [[physical-property-estimation-from-scans]] 里"视觉给相对形状"的结论呼应。
- **不确定性 = 渲染可靠性地图**：5-seed std 告诉我们哪里是模型"编的"（高不确定），对应场景中弱观测区域——可以指导补扫（哪里再多拍几张照片）或者把高不确定区域排除出策略训练采样。
- **与 PhysGS 的衔接**：PhysGS 需要 3DGS 重建质量好才能准确估计物理属性；FixAnything 清洗后的渲染/重建可以作为 PhysGS 的输入增强。
- **与 Blender 流程的关系**：我们的手工 Blender 场景不需要这个（渲染本来干净），但它让"扫描真实场景"路线的视觉质量追上手工场景，缩小 sim 与实景的视觉 gap。
- **落地路径**：等代码开源 → 用 GaussGym 的扫描输出（COLMAP 点云或 3DGS 渲染）跑 FixAnything 离线清洗 → 对比清洗前后策略训练表现。注意推理时间（31s/61帧）决定它是离线预处理，不是在线渲染。

## 参考来源

- arXiv 论文全文：raw/papers/fixanything-arxiv-2608-23549.md
- 官网：raw/articles/fixanything-website.md
- 关联页面：[[gaussgym]]、[[physgs]]、[[physical-property-estimation-from-scans]]
