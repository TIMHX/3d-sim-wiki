---
title: Wiki Index
created: 2026-07-22
updated: 2026-08-16
type: meta
tags: [meta]
---

# Wiki Index

> 3D/Simulation/VR knowledge base — Blender, Isaac Lab, Gaussian Splatting, Unity, VRChat.
> Read this first to find relevant pages for any query.
> Last updated: 2026-08-16 | Total pages: 10

## Entities

- [[blender-shortcuts|Blender Keyboard Shortcuts]] — Complete hotkey reference: navigation, selection, modeling, sculpting, viewport
- [[blender-construction-site-tutorial|Construction Site Tutorial]] — Zero-to-scene Blender tutorial: 15m×15m construction site with terrain, paths, obstacles

## Concepts

- [[isaaclab-docker-env|IsaacLab Docker Environment (tim-pc)]] — Robot project Isaac Lab docker setup: repo, gh auth isolation, daily commands, GPU verification
- [[isaaclab-operation-manual|IsaacLab Operation Manual]] — 完整操作手册：容器生命周期、GUI/headless、导入 Blender 场景、navigation 训练/推理
- [[navigation-task-design|Navigation Task 设计]] — G1 双足导航任务完整设计：场景元素、初始化流程、观测/奖励/终止、传感器配置、资产依赖
- [[isaac-env-export-pipeline]] — Blender → Isaac 两步导出管线(宿主几何导出 + 容器物理生成)、profile 解析与盖章
- [[blender-isaac-env-structure]] — 场景结构约定:两层扁平层级、`__muXXX` 命名、集合
- [[isaac-ground-split]] — 地面按材质拆分:烘焙评估几何 → separate by material,不穿模分区不变量
- [[isaac-friction-profiles]] — PMAT__muXXX 摩擦材质:公式、解析链、碰撞近似

## Comparisons

## Queries

## Troubleshooting

- [[blender-usd-subdiv-render-levels]] — USD 导出评估渲染级细分(视口 3/渲染 2 导致 4× 面数爆炸)
