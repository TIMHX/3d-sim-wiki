---
title: Wiki Index
created: 2026-07-22
updated: 2026-08-24
type: meta
tags: [meta]
---

# Wiki Index

> 3D/Simulation/VR knowledge base — Blender, Isaac Lab, Gaussian Splatting, Unity, VRChat.
> Read this first to find relevant pages for any query.
> Last updated: 2026-08-24 | Total pages: 16

## Entities

- [[blender-shortcuts|Blender Keyboard Shortcuts]] — Complete hotkey reference: navigation, selection, modeling, sculpting, viewport
- [[blender-construction-site-tutorial|Construction Site Tutorial]] — Zero-to-scene Blender tutorial: 15m×15m construction site with terrain, paths, obstacles

## Concepts

- [[gaussgym|GaussGym: 3DGS 实景转仿真机器人训练框架]] — 3DGS drop-in renderer + IsaacGym 向量化模拟，100K steps/s 视觉训练，2500 场景，literature review 报告
- [[physical-property-estimation-from-scans|扫描场景自动物理属性标注（摩擦/粗糙度）]] — PhysGS/Brandao/VLM-RAG/Sim Anything 四路线对比，衔接 PMAT__muXXX 体系的自动摩擦标注方案
- [[isaaclab-docker-env|IsaacLab Docker Environment (tim-pc)]] — Robot project Isaac Lab docker setup: repo, gh auth isolation, daily commands, GPU verification
- [[isaaclab-operation-manual|IsaacLab Operation Manual]] — 完整操作手册：容器生命周期、GUI/headless、导入 Blender 场景、navigation 训练/推理
- [[navigation-task-design|Navigation Task 设计]] — G1 双足导航任务完整设计：场景元素、初始化流程、观测/奖励/终止、传感器配置、资产依赖
- [[isaac-env-export-pipeline]] — Blender → Isaac 两步导出管线(宿主几何导出 + 容器物理生成)、profile 解析与盖章
- [[blender-isaac-env-structure]] — 场景结构约定:两层扁平层级、`__muXXX` 命名、集合
- [[isaac-ground-split]] — 地面按材质拆分:烘焙评估几何 → separate by material,不穿模分区不变量
- [[isaac-friction-profiles]] — PMAT__muXXX 摩擦材质:公式、解析链、碰撞近似
- [[unity-mcp-avatar-introspection|Unity MCP Avatar Introspection]] — 用 Unity MCP 摸清 VRChat 项目结构的工作流:工具选择、反射 API 坑、MA 判读要点

## Projects

- [[lapwing-min-avatar-project|Lapwing-min Avatar Project (VRChat)]] — Lapwing avatar 项目完整结构:4 avatars、playable layers、OSCm 表情追踪 FX、MA 菜单/参数、部件与资产目录
- [[lapwing-hair-dissolve-hub|Lapwing 发色溶解 Hub]] — O(N) 可扩展渐变换发色:颜色映射、lilToon 溶解配置、Sensor/Action 双控制器、WD/struct 等踩坑记录
- [[lapwing-clothes-dissolve|Lapwing 衣服溶解]] — Midnight 单网格换材质 + 单前沿交叉:材质组映射、替身取负镜像、边界标定、脚本加 behaviour 踩坑

## Comparisons

## Queries

## Troubleshooting

- [[blender-usd-subdiv-render-levels]] — USD 导出评估渲染级细分(视口 3/渲染 2 导致 4× 面数爆炸)
