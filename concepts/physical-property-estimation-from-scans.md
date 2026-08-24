---
title: "扫描场景自动物理属性标注（摩擦/粗糙度）"
created: 2026-08-24
updated: 2026-08-24
type: concept
tags: [gaussian-splatting, physics, rendering, robot-env, reference]
sources: [raw/articles/physgs-website.md, raw/articles/friction-from-vision-brandao-2016.md, raw/articles/vlm-friction-wip-arxiv-2409-09845.md, raw/articles/sim-anything-arxiv-2411-12789.md, raw/papers/gaussgym-arxiv-2510-15352.md]
confidence: medium
---

# 扫描场景自动物理属性标注（摩擦/粗糙度）

## 一、问题定义

[[gaussgym|GaussGym]] 的场景管线可以把 iPhone 扫描、视频模型输出自动变成带碰撞网格和 3DGS 渲染的仿真场景，但它对物理参数的处理是硬伤：所有资产用统一的摩擦等参数初始化，无法区分冰面、泥地、沙地。论文原话是限制了"how something looks and how it feels"（看起来什么样和摸起来什么样）的关联。这正是"扫描后自动标注表面摩擦力和粗糙度"要补的空白。

对我们机器人项目的意义：现有 IsaacLab 场景用 `PMAT__muXXX` 命名约定在 Blender 里手工标摩擦（见 [[isaac-friction-profiles]]），扫描进 sim 后若沿用这套流程，标注仍是手工活。自动标注的目标就是跳过这一步，从视觉直接产出可映射到 muXXX profile 的物理参数。

## 二、方法谱系

### 2.1 经典视觉摩擦估计（Friction from Vision, Brandao 2016）

最早系统研究"从图像估摩擦系数"的工作，来自 Waseda 大学（Brandao, Hashimoto, Takanishi），面向足式机器人运动规划。贡献了两个公开数据集：

- OSA+F：8 种材质、96 张图，标注人类的摩擦主观判断、光照、材质、纹理。
- GTF：14 种材质、43 张图，标了机器人脚底的静态摩擦系数（COF）真值 + 人类判断。

方法对比了内在图像（Retinex 分解 shading）、梯度图像、材质分类、text mining（词向量距离）四条路线。结论：材质标签是最强预测信号；人类视觉判断摩擦的表现甚至不如简单材质分类器（人会过度依赖 gloss 光泽等光照线索）；text mining 能提供无经验地形的先验。注意摩擦是接触对属性，依赖两个接触面，所以该数据集定位是量化"视觉信息到底能预测多少"，不是给所有机器人用的通用预测器。^[raw/articles/friction-from-vision-brandao-2016.md]

### 2.2 VLM 零样本摩擦估计（arXiv 2409.09845, 2024）

轮腿机器人安全 locomotion 工作，提出 FFV（Friction From Vision）模块：用 VLM + RAG（检索增强生成）从图像估计地面摩擦系数，不训练新网络、不需要配对的图像-摩擦数据集。动机是摩擦真值采集需要专门仪器，大规模标注数据是瓶颈，而 VLM 能用常识推理（识别香蕉皮滑，靠的是语义不是纯视觉）。把估出的 CoF 显式喂给 RL 策略，让机器人在接触前就减速。在仿真和实机 WIP（轮式倒立摆）上验证，滑面轨迹跟踪成功，纯 proprioception 基线失败。局限：实时性不足。^[raw/articles/vlm-friction-wip-arxiv-2409-09845.md]

### 2.3 3DGS 物理属性估计（PhysGS, CVPR 2026, 最贴近我们需求）

UMD 的 Samarth Chopra 等人工作，Bayesian 推断的 3DGS 扩展，是当前唯一在 3DGS 表示上做稠密逐点物理属性估计的方法：

- 流程：SAM 做部件级分割 → VLM 对每个部件产出材质标签、密度估计、置信度（多视图）→ Bayesian inference 融合观测 → 得到逐材质属性分布 → 传播到 3D 高斯场得到逐点属性。
- 输出：friction（摩擦）、hardness（硬度）、density（密度）、stiffness（刚度）、mass（质量），以及 aleatoric + epistemic 不确定性。
- 效果：ABO-500 物体级 + 室内 + 室外真实数据，mass 估计精度 +22.8%，Shore 硬度误差 -61.2%，kinetic friction 误差 -18.1%。
- 室外单张 RGB 就能出材质分割 + 摩擦系数 + Young's modulus + 不确定性热图，自然地形和植被都能覆盖。
- 代码 "Coming Soon"（2026 年 8 月时未开源）。^[raw/articles/physgs-website.md]

### 2.4 语义自动化路线（Sim Anything, arXiv 2411.12789）

复旦大学等的工作，目标是把静态 3DGS 场景变成可交互物理仿真，物理参数全自动：

- 流程：3D 重建 + 开词汇分割（RAM 打标 + Grounding DINO 检测 + SAM 分割）→ 多视图 inpainting → MLLM-P3 零样本预测物体物理属性均值 → MPDP 模型按均值和几何估计完整属性分布（把回归改成分布估计，省算力）→ PGAS 自适应粒子采样驱动仿真。
- 单张 GPU 上 2 分钟内完成，效果超过 SOTA，对比表里是唯一同时满足"自动参数 + 快推理 + 物理变形 + 静态输入 + 场景级仿真"的。
- 局限：遮挡严重的物体分割不完整，仿真会不自然。
- 对操纵/物体动力学有用，但对"地面摩擦"这种大面积表面属性，它更偏物体级而非逐点稠密。^[raw/articles/sim-anything-arxiv-2411-12789.md]

## 三、三条路线的定位对比

| 方法 | 粒度 | 输入 | 摩擦输出 | 是否需要真值数据集 | 状态 |
|---|---|---|---|---|---|
| Brandao 2016 | 表面级 | 单张图 | COF（特征/材质/text mining） | 有 GTF 数据集可基准 | 2016，经典基线 |
| VLM+RAG (2409.09845) | 表面级 | 单张图 | CoF（VLM 常识） | 不需要 | 2024，实机验证 |
| PhysGS | 逐点稠密 | 多视图 3DGS | friction/hardness/density 等 | 不需要（VLM 先验） | CVPR 2026，代码未开源 |
| Sim Anything | 物体级 | 3DGS 场景 | 物理属性均值 + 分布 | 不需要（MLLM 零样本） | 2024，代码未确认开源 |

## 四、与 GaussGym / 我们工作流的衔接

1. 场景管线复用：GaussGym 的 Polycam 扫描管线（VGGT → NKSR + gsplat）产出的碰撞网格和 3DGS 就是自动标注的输入载体。PhysGS 直接在 3DGS 上做逐点估计，天然契合。
2. 标注映射：估计出的摩擦系数可以离散化映射到现有 `PMAT__muXXX` 命名（mu080/mu100 等，公式见 [[isaac-friction-profiles]]），再按 [[isaac-ground-split]] 的按材质拆分流程生成物理分区，全链路自动化。
3. 粗糙度的信号源（研究切入点）：
   - 3DGS 的 SH 球谐系数含 view-dependent 外观，高粗糙度表面反光扩散、光泽弱，与 specular 程度相关。
   - NKSR mesh 的局部几何起伏（法线方差、曲率）是几何粗糙度代理。
   - 两者可以融合，比纯视觉方法多一个几何通道。
4. 验证闭环：估完摩擦后可以用 IsaacLab 的滑倒测试（在估计表面上跑策略，看是否与真机表现一致）做自动校验，这也是 literature review 里可以写的评估方案。

## 五、推荐路线（更新版）

- 短期（工程）：GaussGym 管线进扫描场景，摩擦沿用手工 PMAT 流程。成本最低，先打通"扫描 → 仿真"。
- 中期（研究增量，可对导师提）：以 PhysGS 为技术起点做自动摩擦/粗糙度标注，输出映射到 muXXX profile。PhysGS 代码未开源是个机会也是风险，风险是只能复现，机会是复现过程中可以加自己的改进（比如用我们的 mesh 几何通道补粗糙度）。
- 备选：VLM+RAG 路线实现最简单（无需训练），可以先做 prototype 验证"视觉估摩擦在足式导航上够不够用"，再决定是否上 3DGS 稠密路线。

## 参考来源

- PhysGS 官网：raw/articles/physgs-website.md
- Friction from Vision (Brandao 2016)：raw/articles/friction-from-vision-brandao-2016.md
- VLM 摩擦估计 (2409.09845)：raw/articles/vlm-friction-wip-arxiv-2409-09845.md
- Sim Anything (2411.12789)：raw/articles/sim-anything-arxiv-2411-12789.md
- 关联：GaussGym 报告 [[gaussgym]]，摩擦材质体系 [[isaac-friction-profiles]]，地面拆分 [[isaac-ground-split]]
