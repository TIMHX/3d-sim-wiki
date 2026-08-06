---
title: Wiki Log
created: 2026-07-22
updated: 2026-07-22
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
