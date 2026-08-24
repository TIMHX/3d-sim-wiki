---
title: "GaussGym: 3DGS 实景转仿真机器人训练框架"
created: 2026-08-24
updated: 2026-08-24
type: concept
tags: [gaussian-splatting, isaac-lab, rendering, physics, robot-env, reference]
sources: [raw/papers/gaussgym-arxiv-2510-15352.md, raw/articles/gaussgym-website.md, raw/articles/gaussgym-github-readme.md]
confidence: high
---

# GaussGym: 3DGS 实景转仿真机器人训练框架

## 一、项目概览

GaussGym 是一个开源的 real-to-sim（实景转仿真）框架，把 3D Gaussian Splatting（3DGS）作为 drop-in renderer 集成进 IsaacGym 类向量化物理模拟器，用于直接从 RGB 像素训练足式机器人（locomotion 与 navigation）策略。项目由 Alejandro Escontrela 主导（UC Berkeley BAIR 系，受 NSF 研究生奖学金、ONR MURI、Amazon、NVIDIA DGX 学术资助），论文发表于 arXiv 2510.15352（2025 年 10 月），代码、数据、预训练模型全部开源。

关键链接：
- 论文：https://arxiv.org/abs/2510.15352
- 代码：https://github.com/escontra/gauss_gym （370+ stars，Apache/MIT 类开源许可）
- 官网（含交互式场景演示）：https://gauss-gym.com
- 数据集：https://huggingface.co/collections/escontra/gauss-gym-datasets

核心数字：单张 RTX 4090 上 4096 个机器人、128 个场景、640×480 分辨率，达到每秒 100,000+ 模拟步（wall clock），跨 GPU 近线性扩展。论文发布约 5 天即登上 X 热点，2026 年 8 月时被引 29 次。

## 二、背景与动机

足式机器人 RL 的主流范式是 sim-to-real（先仿真后迁移）。现有 GPU 模拟器（Isaac Gym、Isaac Lab、ManiSkill、Genesis）物理精度足够，但视觉渲染要么慢要么假，导致绝大多数实机部署的策略只用 depth、elevation map 等几何输入，无法利用 RGB 里的语义线索（人行横道、水坑、彩色标志、禁区）。用 LiDAR/depth 的感知框架（如 Hoeller 2024）限制了任务范围。

3DGS（Kerbl 2023）用一批可微光栅化的有向 3D 高斯球表示辐射场，训练和渲染都远快于 NeRF，是替代 ray tracing 的高保真渲染方案。GaussGym 的核心主张是：把 3DGS 塞进向量化物理模拟，同时拿到"照片级视觉 + 超高吞吐"，把视觉 sim-to-real 从不可行变成可行。^[raw/articles/gaussgym-website.md]

## 三、核心技术

### 3.1 场景生成管线（capture 到 sim 只要分钟级）

输入来源极其多样：手机扫描（Polycam）、带位姿的 SLAM 采集、现有 3D 数据集（GrandTour、ARKitScenes）、手持视频、甚至生成式视频模型的输出（Veo）。统一流程：

1. VGGT（Visually Grounded Geometry Transformer）从图像/视频估计相机内外参、稠密点云和法线。生成视频模型的输出没有位姿，VGGT 直接补上。
2. NKSR（Neural Kernel Surface Reconstruction）从点云重建高分辨率碰撞网格，供物理引擎用。
3. gsplat 用 VGGT 点云直接初始化 3DGS，几何精度高、收敛快。
4. 所有资产自动对齐到统一的重力对齐世界坐标系。

对比 LucidSim：LucidSim 只支持手机扫描、需要手动对齐 mesh 与 3DGS、无向量化渲染。GaussGym 全自动对齐且原生支持大规模并行。^[raw/papers/gaussgym-arxiv-2510-15352.md]

### 3.2 3DGS 作为 drop-in renderer

Gaussian splats 跨环境并行光栅化，用多线程 PyTorch kernel 批量渲染，RGB 和 depth 用同一套 splat 表示，depth 渲染开销极小。物理碰撞用 NKSR mesh，视觉用 3DGS，两者在同一全局坐标系下严格同步。

### 3.3 吞吐量优化

关键技巧是把渲染频率与控制频率解耦：不在 50Hz 控制频率下每步渲染，而是按相机真实帧率（10Hz）渲染，视觉输入保真度不变，吞吐大幅提升。实际配置：control 50Hz、camera 10Hz、4096 envs、128 unique scenes、单卡 100K+ steps/s。

### 3.4 降低视觉 sim-to-real gap

- 运动模糊：沿相机速度方向渲染若干偏移帧再 alpha-blend 成一张图，模糊程度由快门速度参数化，训练时可随机化。爬楼梯、高速运动时效果尤其明显。
- 相机随机化：位姿、内参（焦距、主点）、外参全部可在向量化渲染器内随机化。
- Terrain-aware rewards：集成 NVIDIA Warp，直接从场景几何取 heightmap，不需要昂贵 ray casting。

### 3.5 多模态感知

同一 3DGS 表示可输出 RGB + depth + heightmap，depth 可配置真实传感器特性（量程、噪声），支持多模态策略和 terrain-based reward。

## 四、策略学习架构

单阶段端到端训练（不用 student-teacher 蒸馏，区别于 Miki 2022 类流水线）。结构：

- Recurrent encoder：每步把 DinoV2 对 RGB 帧的 embedding 与 proprioception（角速度、重力投影角、关节位置/速度、摆动相位）拼接，过 LSTM 得到融合时间动态与视觉语义的 latent。选 LSTM 而非 transformer 是为了实机推理速度。
- Voxel prediction head：把 latent 展开成 3D 网格，用 3D 转置卷积预测稠密 occupancy 和地形高度。这个辅助重建损失（用真值 mesh 监督）强制 latent 学会场景几何，显著加快学习速度和最终性能。
- Policy head：第二个 LSTM 消费 latent，输出关节位置偏移量的高斯分布参数。

观测空间：base 角速度、投影重力角、关节位置/速度、摆动相位、640×480 图像。奖励表（速度跟踪、方向惩罚、脚间距、stumble 检测等）见论文附录 A.2。^[raw/papers/gaussgym-arxiv-2510-15352.md]

## 五、实验结果

### 5.1 视觉导航：RGB 优于 depth 的关键证据

obstacle-field 实验：稀疏目标放在杂物后面，地面有黄色禁区 patch，进入得负奖励。RGB 策略学会绕开黄色 patch，depth-only 策略失败。这直接证明 RGB 提供了纯几何之外的语义信息，是论文最重要的论点之一。

### 5.2 视觉 locomotion 与 sim2real

- Unitree A1：RGB 策略学会精确落脚、适应楼梯台阶避免碰撞，零微调迁移到真实 17cm 楼梯。
- Booster T1：头戴相机训练，成功导航斜坡。
- 真实场景转移仍有精度下降，论文承认这是开放问题（详见局限）。

### 5.3 大规模 ablation（成功率 %，A1/T1）

| Scenario | Vision | Blind | Vision w/o voxel | Vision w/o DINO | Vision 1/10 scenes | Vision 1/2 scenes |
|---|---|---|---|---|---|---|
| Flat | 100.0/100.0 | 98.1/97.2 | 100.0/98.3 | 100/96.7 | 94.3/99.2 | 99.0/99.2 |
| Steep | 99.3/97.1 | 89.4/87.6 | 91.9/87.0 | 95.6/91.5 | 88.1/88.3 | 95.5/94.1 |
| Stairs (short) | 98.7/97.4 | 80.8/72.3 | 85.2/82.7 | 92.3/87.5 | 79.7/74.8 | 86.3/84.9 |
| Stairs (tall) | 94.4/92.5 | 74.0/60.5 | 80.8/76.3 | 88.3/82.8 | 67.3/58.2 | 83.9/75.2 |

结论：去掉 voxel 重建头、去掉预训练 DINO、减少场景数量都会掉性能。场景多样性（2500 个场景）贡献巨大，1/10 场景时 tall stairs 成功率从 94.4% 掉到 67.3%。

## 六、与相关工作对比

| 维度 | GaussGym | LucidSim | LeVerb | IsaacLab |
|---|---|---|---|---|
| 照片级真实 | ✓ | ✓ | ✗ | ✗ |
| 时间一致 | ✓ | ✗ | ✓ | ✓ |
| 向量化 FPS | 100,000+ | 单环境 | 未报告 | 800 |
| 单环境 FPS | 25 | 3 | 未报告 | 1 |
| 渲染器 | 3DGS | ControlNet | Raytracing | Raytracing |
| 场景来源 | 手机扫描/数据集/视频模型 | 手工设计 | 手工设计 | 原语随机化 |

与 NeRF2Real（Byravan 2023）比：GaussGym 免去慢速 ray tracing 和手工 mesh 后处理。与 Escontrela 2025（同作者的 locomotion affordance 工作）一脉相承，GaussGym 是其向量化仿真底座。

## 七、代码与数据（工程视角）

仓库结构：`gauss_gym/envs/*/config.yaml`（a1、go1、t1、anymal_c，各配 vision 版）、`scene_generation/`（Polycam、Veo、数据集处理脚本）、`deployment/`（实机部署代码）、`docker/`。安装：`bash setup_dev.sh` 建独立 conda 环境（~/.gauss_gym_deps）。训练：`gauss_train --task=t1_vision --env.num_envs 2048`，自动从 HF 下载场景，viser 可视化（localhost:8080，可分享隧道），支持 wandb 日志。评估：`gauss_play --runner.load_run=<RUN_NAME>`，支持从 wandb/HF 拉 checkpoint。自建场景：Polycam Space 模式采集，导出 Raw Data + GLTF，nerfstudio 环境训练 splat，`generate_mesh_slices.py` 出碰撞网格，`--terrain.scenes.iphone_data.repo_id=local:<PATH>` 接入训练。场景数据在 HF 四个 repo：gauss_gym_arkit、gauss_gym_data、grand_tour_dataset（leggedrobotics）、veo_scenes。

注意：只有 a1 和 t1 配置在真机验证过；README 里 Release TODO 已全部勾掉（多卡训练、部署代码、预训练策略都已提供）。^[raw/articles/gaussgym-github-readme.md]

## 八、局限性（论文自述）

1. 视觉 sim-to-real 仍是未解决问题：策略未在训练未见过的楼梯上评估，实机落脚精度比仿真差。
2. 实机转移受图像延迟、egocentric 观测影响；几何方法（elevation map + 400Hz 状态估计）仍显著简化问题。
3. 缺少自动化 cost/reward 生成机制（如人行道、斑马线的社会规范），目前靠手工 cost。
4. 资产物理参数统一（摩擦等），无法模拟冰面、泥地、沙地，"看起来什么样和摸起来什么样"脱节。
5. 继承生成模型局限：Veo 输出偶发不一致需重新 prompt，只能文字控制相机。动态场景、流体、可变形资产还不支持（Genie 3 等世界模型是明确改进路径）。^[raw/papers/gaussgym-arxiv-2510-15352.md]

## 九、对机器人项目的启示

与本 wiki 的 [[isaaclab-operation-manual|IsaacLab Operation Manual]]、[[navigation-task-design|Navigation Task 设计]] 高度相关，是视觉导航训练的可选底座：

- 如果我们的 G1 导航任务想加"视觉语义"维度（比如避开特定颜色区域），GaussGym 的 RGB 管线 + 2500 场景是现成方案，而当前 IsaacLab 方案主要靠 [[isaaclab-docker-env|IsaacLab Docker Environment]] 里的深度/地形输入。
- GaussGym 场景生成管线（iPhone/Polycam 采集 → VGGT/NKSR/gsplat）与我们 GS 采集经验（[[blender-construction-site-tutorial|Construction Site Tutorial]] 之外的真实场景方向）可直接复用，iPhone 采集 + 4090 训练正好是我们已有的硬件组合。
- 注意迁移成本：GaussGym 用 IsaacGym（旧 API）而非 IsaacLab，自建环境需要把我们的 URDF 和任务配置移植过去。若导师要求 literature review 覆盖"real-to-sim 视觉训练"这一前沿，GaussGym 是 2025 下半年最具代表性的 open baseline。

## 参考来源

- arXiv 论文全文：raw/papers/gaussgym-arxiv-2510-15352.md
- 官网：raw/articles/gaussgym-website.md
- GitHub README：raw/articles/gaussgym-github-readme.md
