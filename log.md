---
title: Wiki Log
created: 2026-07-22
updated: 2026-08-16
type: meta
tags: [meta]
---

# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: ingest, update, query, lint, create, archive, delete

## [2026-07-22] create | Wiki initialized
- Domain: 3D graphics, simulation, VR/AR, robotics environments
- Covering: Blender, Isaac Lab/Sim, Gaussian Splatting, Unity, VRChat
- Structure created with SCHEMA.md, index.md, log.md

## [2026-07-27] create | blender-construction-site-tutorial
- Zero-to-scene construction site for Ziwon Yoon's humanoid navigation VIP project
- 15m×15m, 3-layer build: BaseGround → paths (shortcut + detour) → obstacles (trash cans, material stacks, rebar, scaffold, mixer)
- Covers: Plane, Cube, Cylinder creation, Displace modifier, naming, proportional editing, Shift+D duplication, Ctrl+J merge
- Target: complete Blender beginner, no prior experience assumed

## [2026-07-22] create | blender-shortcuts
- Created [[blender-shortcuts|Blender Keyboard Shortcuts]] — comprehensive hotkey reference
- Categories: navigation, selection, transform, edit mode, object mode, sculpting, animation, viewport
- Sources: quickref.me, BringYourOwnLaptop (BYOL)
- Raw references saved to raw/references/
- 2026-07-22 (update): Added Alt-key shortcuts — edge loop/ring select, extrude menu, normals, shrink/fatten, beautify faces, tris-to-quads, clipping region, mask menu
- 2026-07-22 (update): Added H-key shortcuts — hide/unhide in Edit Mode, isolate geometry workflow
- 2026-07-22 (update): Added D-key shortcuts — duplicate-in-place (Shift+D+RMB), annotate tool (D+draw), erase annotations (D+D)
- 2026-07-22 (update): Expanded Navigation + Numpad section — orbit keys (2468), all axis views (front/back/right/left/top/bottom), quad view (Ctrl+Alt+Q), align camera to view, fly/walk mode, laptop/numpad-less setup
- 2026-08-06 (create): [[isaaclab-docker-env|IsaacLab Docker Environment (tim-pc)]] — robot project docker setup: repo @2.3.0/feature/navigation, gh auth isolation, isaac-lab-base image, daily commands, cleanup history
- 2026-08-06 (create): [[isaaclab-operation-manual|IsaacLab Operation Manual]] — 完整操作手册(容器/GUI/Blender场景导入/navigation训练)，替代分散的本地 markdown 副本

## [2026-08-16] create | Isaac env pipeline pages (first-hand, 5 pages)

- concepts/[[isaac-env-export-pipeline]] — 两步导出管线(宿主 Blender + 容器 authoring)，profile 解析与盖章
- concepts/[[blender-isaac-env-structure]] — 两层扁平层级、命名与集合约定
- concepts/[[isaac-ground-split]] — 地面按材质拆分方法与不穿模分区不变量
- concepts/[[isaac-friction-profiles]] — PMAT__muXXX 公式与碰撞近似
- [[blender-usd-subdiv-render-levels]] — 渲染级细分评估的坑(874M vs 237M 诊断)
- 来源:OpenViking 回忆机器人项目 Park/Construction 环境的完整实践(2026-08-15~16)

## [2026-08-16] update | isaaclab-operation-manual + index merge

- 刷新操作手册场景状态表:Park/Construction 的 simulation.usda 已于 2026-08-16 重新生成(原记录为"缺 simulation.usda")
- 新页面按 repo 惯例归入 concepts/(troubleshooting 页留在根),index 合并为 10 页

## [2026-08-16] update | 命名铁律 + 四场景重导出

- [[blender-isaac-env-structure]]:新增重复对象命名铁律(`基础名.NNN__muXXX`,严禁 `__muXXX.NNN`,后者 `.001` 会漏判回落 mu080)
- [[isaac-env-export-pipeline]]:环境规范名修正(construction_site→construction,补 park2/construction2)、补 create_environment.sh --template 与共享 profiles 6 码说明、铁律(严禁改脚本/repo static)
- 来源:2026-08-16 四场景(park/park2/construction/construction2)`.NNN` 改名 + 零脚本改动重导出 + 打包到 packages_20260816/

## [2026-08-16] create | Lapwing-min VRChat avatar project pages (first-hand, 2 pages)

- concepts/[[lapwing-min-avatar-project]] — Lapwing-min 项目完整结构:4 avatars(PC/Quest × 标准/Midnight)、playable layers 装配、OSCm/FT 表情追踪 FX 层(40 个位编码层)、MA 构建期菜单/参数、部件层级、资产目录、技术栈
- concepts/[[unity-mcp-avatar-introspection]] — Unity MCP 探查 VRChat 项目的工作流:assets-find/animator-get-data 大结果 grep 处理、script-execute 反射模式(SDK 3.8 descriptor 图层是字段不是属性)、MA/VRCFury 组件枚举、MA 项目判读要点
- 来源:2026-08-16 通过 Unity MCP 对 E:\ALCOM_save\Lapwing-min 的完整探查(asset 检索 + 控制器解析 + 场景反射)
- index 新增 Projects 分类,总页数 10 → 12
