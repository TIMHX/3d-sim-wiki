---
source_url: https://fix-anything.github.io/
ingested: 2026-08-31
type: raw
---

# FixAnything: 3D-Consistent Rendering Refinement via Video Generative Priors

官方项目页 (2026-08-31 抓取)：

- 作者：Khiem Vuong, Deva Ramanan*, Srinivasa Narasimhan*（CMU，* 表示 equal contribution/advising）
- 会议：ECCV 2026
- arXiv: 2608.23549 | 代码 Coming Soon | BibTeX 见页面
- TL;DR：一个通用视频模型修复任意 3D 表示（3DGS/NeRF/mesh/稀疏点云）的渲染伪影，仅需最小修改 + 轻量微调，复用预训练视频扩散模型。
- 关键洞察：
  1. (Degraded) render IS camera control —— 任何表示的渲染都保留相机轨迹和粗场景布局，提供控制信号
  2. 非常稀疏的点云（如 COLMAP）就够视频模型获得有效相机控制，仅需 ~20 对视频的 LoRA 微调
  3. 位姿精度作为 DPO 的 reward —— COLMAP 从输出恢复的相机位姿 AUC@5° 作为 reward，Flow-DPO 引导模型输出几何一致结果（61.1 → 68.3 AUC@5°）
- 方法：Wan2.1-I2V-14B 视频扩散模型两阶段适应：
  - Stage I 监督微调：劣化渲染的 VAE latent 与噪声 latent 通道拼接 + per-frame 二进制 mask（trust/fix）；DL3DV-10K 四种表示渲染配对视频联合训练；rank-64 LoRA（<1% 参数），3000 iter 单 H100，最少 20 对视频
  - Stage II 几何感知偏好优化：模型偶发跨视图不一致的幻觉结构；用 COLMAP 恢复位姿精度（AUC@5°）作为 reward，多 rollout 排序配对（AUC gap ≥ 0.2），Flow-DPO 微调 LoRA
- 不确定性：5 seeds 推理逐像素 std 作为不确定性估计，与重建误差强相关（DL3DV 6 views：最自信 25% 像素 PSNR 25.7 dB vs 最不自信 25% 14.4 dB）
- 跨数据集泛化：MipNeRF-360、LLFF 上 3DGS 输入达到与 SOTA 相当性能，LPIPS 明显改善
