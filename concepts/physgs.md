---
title: "PhysGS: Bayesian 3DGS 逐点物理属性估计"
created: 2026-08-31
updated: 2026-08-31
type: concept
tags: [gaussian-splatting, physics, uncertainty, vlm, friction, robot-env, reference]
sources: [raw/papers/physgs-arxiv-2511-18570.md, raw/articles/physgs-website.md]
confidence: high
---

# PhysGS: Bayesian 3DGS 逐点物理属性估计

## 一、项目概览

PhysGS（Physics Gaussian Splatting）是一个把 **Bayesian 推断嵌进 3D Gaussian Splatting** 的框架，从多视角 RGB 图像 + VLM（GPT-5）视觉语言先验，估计稠密、逐点的物理属性：摩擦系数、Shore 硬度、刚度、密度、质量，并输出校准过的 aleatoric（随机）与 epistemic（认知）不确定性。论文作者 Samarth Chopra、Jing Liang、Gershom Seneviratne、Dinesh Manocha（University of Maryland, College Park），发表于 CVPR 2026（pages 18980-18990），arXiv:2511.18570（2025-11-23 提交）。**代码已于 2026-06-27 开源（MIT）**：github.com/samchopra2003/PhysGS-Codebase。^[raw/papers/physgs-arxiv-2511-18570.md]

关键链接：
- 论文：https://arxiv.org/abs/2511.18570
- 官网：https://samchopra2003.github.io/physgs
- 代码：github.com/samchopra2003/PhysGS-Codebase（MIT，2026-06-27 开源；贝叶斯核心 filter_utils.py 可独立复用）
- CVPR Poster: https://cvpr.thecvf.com/virtual/2026/poster/36542

核心数字：相比最强确定性 baseline（NeRF2Physics），质量估计误差降 22.8%（APE），Shore 硬度误差降 61.2%（ADE），动摩擦误差降 18.1%（ALDE）。论文自评是"把 3D 重建、不确定性建模、物理推理统一进一个空间连续框架"。

## 二、背景与动机

机器人（导航、操作、手术）要安全交互，必须知道表面物理属性：摩擦、弹性、硬度、密度。但现有 3D 重建方法（occupancy grid、SDF、NeRF、3DGS）只重建几何和外观，不编码物理。两大难点：

1. **视觉相似、物理不同**：泥 vs 沥青、草 vs 岩石，外观接近但摩擦天差地别，纯几何表示无法区分。
2. **不确定性管理**：传感器噪声、光照、遮挡（aleatoric），模型训练数据不足导致的泛化失败（epistemic），都需要显式建模，否则下游规划/控制不可靠。

室内物理属性估计已有进展（NeRF2Physics、GaussianProperty），但 outdoor 场景基本空白；已有方法大多只针对一两个属性（摩擦、刚度），难以推广到多属性。PhysGS 的定位：**一个 Bayesian 公式统一多属性、点级+物体级、室内+室外、刚体+可变形物体**。^[raw/papers/physgs-arxiv-2511-18570.md]

## 三、核心技术

### 3.1 总管线（四步）

```
多视角 RGB 图像
   → SAM 分割（whole/part/sub-part 三级，置信度过滤）
   → 每部分构造 三图三联 prompt（完整图 + mask 叠加图 + 孤立 part 图）喂给 GPT-5
   → VLM 输出：材质标签 + 物理属性值 + 置信度 p ∈ [0,1]
   → Bayesian 融合（跨视角增量更新）→ 逐材质属性分布
   → 材质 legend 重着色 → 3DGS 重建语义 splat → 逐点属性场 + 物体级质量
```

关键设计：**VLM 的每一条候选预测都当作一个带置信度的观测**，Bayesian 推断把多视角证据融合成后验分布，而不是单视角拍板。^[raw/papers/physgs-arxiv-2511-18570.md]

### 3.2 离散材质：Dirichlet-Categorical 模型

材质标签是 Categorical 分布，参数 θ 上放 Dirichlet 先验（共轭，闭式更新）：

- 后验预测概率：f(z=i|Z,α) = α̃ᵢ / Σⱼ α̃ⱼ
- 后验参数更新：α̃ᵢ ← αᵢ(0) + Σ_{m:cₘ=i} λ·pₘ
  - λ 控制每条观测的证据强度，pₘ 是 VLM 置信度
- **置信度加权**：VLM 越不确定，对后验的贡献越小；多材质候选的置信度分布本身就是语义歧义的信号

### 3.3 连续属性：置信度加权矩累加

每个材质类 i 维护三个累加器（流式、不需存历史观测）：

- Wᵢ = Σ pₘ（总权重），Sᵢ = Σ pₘψₘ（一阶矩），Qᵢ = Σ pₘψₘ²（二阶矩）
- 后验均值 μᵢ = Sᵢ/Wᵢ，方差 σᵢ² = max(Qᵢ/Wᵢ − μᵢ², ε)
- 最终预测 = 高斯混合：f(ψ|Z,α) = Σᵢ (α̃ᵢ/Σⱼα̃ⱼ) · N(μᵢ, σᵢ²)，每个材质是一个高斯 mode，权重是 Dirichlet 后验

### 3.4 不确定性分解：Normal-Inverse-Gamma（NIG）先验

对每个材质的 (μᵢ, σᵢ²) 放 NIG 联合先验，参数 (τ, κ, α, β)。新观测 (ψₘ, pₘ) 到来时闭式更新四个参数（κ̃=κ+pₘ, τ̃=(κτ+pₘψₘ)/(κ+pₘ), α̃=α+pₘ/2, β̃=β+pₘκ(ψₘ−τ)²/(2(κ+pₘ))）。

总预测方差分解为两部分：

- **aleatoric**（数据本身噪声）: E[σᵢ²] = β̃/(α̃−1)
- **epistemic**（模型知识不足）: Var[μᵢ] = E[σᵢ²]/κ̃

语义：aleatoric 高 = 该材质类内部观测本身分散（感知噪声）；epistemic 高 = 证据不足或互相冲突（VLM 对材质犹豫、SAM mask 不干净）。这两者都是可解释的置信度信号，可用于 risk-sensitive 决策。^[raw/papers/physgs-arxiv-2511-18570.md]

### 3.5 语义 3DGS 重建

- VLM 输出 → 材质 legend（每材质唯一颜色）→ 场景图重着色 → 用 splatfacto-big（Nerfstudio）训 3DGS，20,000 iterations，RTX A5000，random scale 2.0 + random background
- 得到"语义 splat"后：逐点属性查询（摩擦、密度）+ 体积积分得总质量

## 四、实验设置

### 4.1 数据集

| 数据集 | 内容 | 用途 |
|---|---|---|
| ABO-500（NeRF2Physics 策展） | 500 件亚马逊商品，多视角图+mask+物理元数据；300 train/100 val/100 test | 质量估计 |
| 摩擦-硬度数据集（NeRF2Physics 策展） | 15 个家居物体、13 场景、多点 kinetic friction + Shore A/D 硬度实测 | 逐点摩擦/硬度 |
| RUGD、RELLIS-3D | 户外崎岖地形 | 户外场景级泛化（定性） |

### 4.2 质量估计（ABO-500 test，4 指标）

| Method | ADE↓ | ALDE↓ | APE↓ | MnRE↑ |
|---|---|---|---|---|
| Image2mass | 12.496 | 1.792 | 0.976 | 0.341 |
| 2D CNN | 15.431 | 1.609 | 14.459 | 0.362 |
| LLaVA | 17.328 | 1.893 | 1.837 | 0.306 |
| NeRF2Physics | 8.730 | 0.771 | 1.061 | 0.552 |
| **PhysGS (Ours)** | **8.254** | 0.999 | **0.819** | 0.474 |

PhysGS 在 ADE（−5.5%）和 APE（−22.8%）领先，但 ALDE 和 MnRE 反而略逊 NeRF2Physics，注意别过度解读（见局限）。

Ablation（Bayesian 更新的贡献，ABO-500 val）：Ours w/o BI vs Ours with BI，加 Bayesian 后 ADE 降 5.6%、APE 降 6.4%（9.728→9.187, 0.717→0.715，表中 w/o BI 的 APE 数值略有矛盾，以"论文称 ADE −5.6%/APE −6.4%"为准）。

### 4.3 逐点摩擦与硬度（真实测量）

| Shore Hardness (31点/11物体) | ADE↓ | ALDE↓ | APE↓ | MnRE↑ |
|---|---|---|---|---|
| GPT-4V | 32.752 | 0.330 | 0.304 | 0.758 |
| CLIP | 32.857 | 0.294 | 0.266 | 0.774 |
| NeRF2Physics | 34.295 | 0.315 | 0.276 | 0.765 |
| **PhysGS** | **12.721** | **0.193** | **0.222** | **0.839** |

| Kinetic Friction (6点/6物体) | ADE↓ | ALDE↓ | APE↓ | MnRE↑ |
|---|---|---|---|---|
| GPT-4V | 0.209 | 0.430 | 0.549 | 0.692 |
| CLIP | 0.222 | 0.455 | 0.602 | 0.654 |
| NeRF2Physics | 0.155 | 0.321 | 0.360 | 0.736 |
| **PhysGS** | **0.131** | **0.263** | 0.365 | **0.805** |

硬度 ADE 降 61.2%（对 NeRF2Physics），摩擦 ALDE 降 18.1%、MnRE +9.4%。注意：摩擦测试只有 6 个点、6 个物体，样本量极小，统计意义有限。^[raw/papers/physgs-arxiv-2511-18570.md]

### 4.4 不确定性行为（qualitative）

- 场景杂乱、SAM mask 不干净（枯叶 vs 木头、泥 vs 草分不开）→ total uncertainty 显著升高，epistemic 和 aleatoric 同时涨
- 大块空间连续表面（砾石、均匀草、天空）→ SAM 分割干净 → 不确定度低、属性预测稳定
- 即：**不确定性对分割质量敏感，且能如实反映证据可信度**，这是论文声称"calibrated uncertainty"的依据

## 五、与相关工作的关系

| 方法 | 表示 | 机制 | 不确定性 | 多属性 | 代码 |
|---|---|---|---|---|---|
| NeRF2Physics (ICRA 2024) | NeRF | 语言嵌入特征空间 + zero-shot kernel regression | ✗ | ✓ | ✓ |
| GaussianProperty | 3DGS | 同 NeRF2Physics 思路搬到高斯球 | ✗ | ✓ | 部分 |
| LERF / LangSplat | NeRF/3DGS | CLIP 特征蒸馏成可查询 3D 语言场 | ✗ | 语义非物理 | ✓ |
| EVORA | 2D 图 | evidential traction 分布，分 aleatoric/epistemic | ✓ | 摩擦为主 | ✓ |
| Ewen et al. | 2D 图 | 语义+连续属性联合信念 | ✓ | 摩擦为主 | ✗ |
| STEP | 2D 图 | CVaR 风险规划（DARPA SubT） | ✓ | traversability | ✗ |
| **PhysGS** | 3DGS | Dirichlet + NIG Bayesian 融合 VLM 先验 | ✓ | 摩擦/硬度/刚度/密度/质量 | ✓ MIT（2026-06 开源） |

关键差异：PhysGS 是第一个把**完整分层 Bayesian 推断（离散 Dirichlet + 连续 NIG）嵌入 3DGS** 的工作，同时覆盖点级和物体级、室内和室外。NeRF2Physics 是它的直接 baseline 和前身，PhysGS 用 3DGS（快、显式、可逐点查询）+ 显式不确定性换掉了 NeRF 的隐式场。

## 六、实现细节（工程视角）

- 3DGS：Nerfstudio splatfacto-big，20K iter，RTX A5000
- 分割：SAM（whole/part/sub-part 层级，按 IoU/stability 过滤冗余低置信 mask）
- VLM：GPT-5（2026 年初配置），结构化三图 prompt（左整图、中 mask 叠加、右孤立 part），文本指令要求 ①caption ②材质 ③物理属性 ④置信度 [0,1]；室内外分别维护独立材质库
- Baseline prompt（公平对比）：GPT-4V/GPT-5 只收裸 RGB，无分割线索，要求直接报材质+摩擦+刚度+置信度——测试"纯外观推理"的上限
- 观测模型：Oₘ = (cₘ, pₘ, ψₘ)，cₘ 是 VLM 预测材质（真实材质的噪声代理），ψₘ 是属性观测，pₘ 是置信度

## 七、局限性（论文自述 + 我的补充）

论文自认：
1. **对分割质量敏感**：part mask 把视觉相似材质合并、或没隔离细粒度区域时，属性估计继承歧义，不确定性上升。未来方向：VLM-guided 分割细化、置信度 mask 过滤。
2. 阴影演化、材质参数自动赋值未解决（Material parameters are manually set）。
3. 摩擦估计样本量极小（6 点），统计可靠性存疑（我的补充）。

我的补充（工程视角）：
1. **落地障碍已解除（2026-06-27 代码 MIT 开源）**：github.com/samchopra2003/PhysGS-Codebase。贝叶斯核心 filter_utils.py（~100 行 numpy）可独立复用，prompt 设计（gpt_inference.py）可直接借鉴。但全管线复现需修 requirements（含本机路径 file:/// 依赖、openai 0.28 旧版）、配 Nerfstudio、VLM 可切 qwen-vl-max（--vlm qwen）。
2. **VLM 依赖**：GPT-5 是闭源商业 API，每次推理花钱且不透明；换成开源 VLM（Qwen-VL、InternVL）性能未知，论文无 ablation。
3. **SAM + GPT-5 两段式**：误差级联，SAM mask 错 → GPT-5 对错的部分推理 → Bayesian 再自信地把错误信念固化（置信度加权只能缓解不能消除）。
4. **评估局限**：ABO-500 是商品（家具、瓶子），摩擦-硬度数据集是 15 个家居物体，outdoor 只有 qualitative 展示没有数值。
5. "逐点"的实现路径是"逐材质"：属性先按材质类估计，再 propagate 到 3D 场里的点。材质分类错了，点就错了。

## 八、对本项目（机器人导航 + IsaacLab）的启示

PhysGS 是我们"扫描场景自动物理标注"调研（[[physical-property-estimation-from-scans]]）里最贴近目标的一条路线：

- **输出可直接映射 PMAT__muXXX**：逐点摩擦 → 按区域聚合成 PMAT__mu080/mu100 等材质名 → 喂给 [[isaac-friction-profiles]] 的解析链，比手工标注快一个量级。
- **不确定性是加分项**：epistemic 高估的区域 = 该去实地测摩擦的地方（主动采样引导），比单点估计更工程友好。
- **粗糙度信号源**：SH 系数 + mesh 几何起伏（[[physical-property-estimation-from-scans]] 已记录）与 PhysGS 的硬度/刚度互补。
- **落地路径（已更新）**：代码已 MIT 开源。①最快：直接复用官方 filter_utils.py 贝叶斯核心 + gpt_inference.py 的 friction prompt，接我们自己的分割和 VLM（可切 qwen-vl-max）搭简化版；②完整复现：修 requirements 后跑官方 abo_500 管线做对比实验；③参考 Ewen et al./EVORA 自研（见 [[physical-property-estimation-from-scans]] 的 VLM+RAG 方案，最快 prototype）。
- **与 GaussGym 衔接**：GaussGym（[[gaussgym]]）解决"场景怎么来"（扫描→sim 分钟级），PhysGS 解决"场景物理属性怎么标"（逐点摩擦/硬度），两者合起来正好补上 GaussGym 自认的"资产物理参数统一"短板。

## 参考来源

- arXiv 论文全文：raw/papers/physgs-arxiv-2511-18570.md
- 官网：raw/articles/physgs-website.md
- 关联页面：[[physical-property-estimation-from-scans]]、[[gaussgym]]、[[isaac-friction-profiles]]
