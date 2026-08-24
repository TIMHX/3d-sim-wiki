---
title: Wiki Log
created: 2026-07-22
updated: 2026-08-24
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

## [2026-08-06 (create): [[isaaclab-docker-env|IsaacLab Docker Environment (tim-pc)]] — robot project docker setup: repo @2.3.0/feature/navigation, gh auth isolation, isaac-lab-base image, daily commands, cleanup history
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

## [2026-08-17] create | lapwing-hair-dissolve-hub (first-hand, 1 page)

- concepts/[[lapwing-hair-dissolve-hub]] — 发色溶解 Hub 完整实现记录:8 色映射表、lilToon `_DissolveParams.z` 溶解语义与关键字门槛、Sensor/Action 控制器结构、AnimatorControllerLayer struct 坑、WD=off 必要性、验证结果(9 次 NDMF 处理零 MA 错误)、git 回档点
- 来源:2026-08-16~17 通过 Unity MCP 全流程实现(材质/动画/控制器/MA 装配/NDMF 克隆体验证)
- index 总页数 12 → 13

## [2026-08-17] update | lapwing-hair-dissolve-hub
- v4 rewrite: coordinate/line dissolve (_DissolveParams=(3,1,border,0.12), 完整 Pony=0 / LowPony=-0.1, 消失=0.7)
- Single-front mirrored ghost sweep: ghost _DissolvePos.y=-0.1 + mirrored border; cross duration 0.25s→0.4s
- Midnight avatar full port (ghosts ×4, LapFX FT Midnight controller 2 layers cloned, params default 0, AAO removeUnusedObjects off) — user verified
- Noise texture slot currently empty (user deleted Mask_Dissolve.png, TBD)

## [2026-08-17] create | lapwing-clothes-dissolve-analysis
- Can the hair dissolve hub generalize to clothing? Material-only = O(n) direct port
- Different-mesh outfits: per-pair naive = O(n²); single-front mirror imposes pairwise constraints → per-outfit calibration also O(n²) in effect quality
- Escape hatch: one global unified sweep range + ONE shared Cross clip → O(1) calibration, O(1) per new outfit, O(n+m) total; trade-offs documented

## [2026-08-18] create | lapwing-clothes-dissolve (first-hand implementation)
- concepts/[[lapwing-clothes-dissolve]] — Midnight 衣服溶解落地:4 套衣服是同网格换材质(情形 A O(n))、单网格合并+替身共享骨架、单前沿取负镜像、边界标定 complete=-1.0/gone=0.6、Sensor/Action 两层
- 踩坑:替身镜像必须取负(非 2*complete-z)、clip 需显式 x/y/w 常量、rootBone 共享、complete 不能压最低点(严格不等式露白边)、脚本加 behaviour 需 CreateInstance+AddObjectToAsset
- update:[[lapwing-clothes-dissolve-analysis]] 标注情形 A 已落地;[[lapwing-min-avatar-project]] 增衣服溶解节
- 来源:2026-08-18 通过 Unity MCP 全流程实现,用户 Play 验证通过
- index 总页数 13 → 14

## [2026-08-19] update | lapwing-hair-dissolve-hub
- 新增坑：Midnight `头发/HairPony_Crossfade` 替身 `m_Mesh` 指向已删 GUID（`2dd8ed6f…`）→ `sharedMesh=null` → Cross 阶段不渲染（光头）→ Promote 瞬现
- 教训：控制器/动画/材质全共享且等价，唯一差异在场景替身 mesh 引用；「同动画同材质」不能排除场景层差异，排查需逐替身验 `sharedMesh != null`
- 修复：改回真身同款 BakedMesh `HairPony(Clone).asset`（guid 25b2ce01…）

## [2026-08-19] update | lapwing-hair-dissolve-hub + lapwing-clothes-dissolve
- 新增坑：溶解门禁 trigger（HairFadeTrigger/ClothesFadeTrigger）是 VRChat 本地信号——expression params 无 Trigger 类型、trigger 瞬态消费，远程/mirror 完全没动静（本地正常；PC 旧衣服 synced Bool 直驱故远程正常）
- 修复（用户 VRChat 实测成功）：Trigger(9)→Bool(4) + expression params 加 Bool synced + Sensor 置 true + Action 过渡 `==true` + Swap 首态复位 false
- 子坑：复位必须放首态 Swap 不能放尾态 Promote，否则 bool 在 Cross 0.4s 期间仍 true 致 `AnyState→Swap` 重入、Swap↔Cross 高速闪烁

## [2026-08-24] ingest | GaussGym literature review (机器人项目)
- 研究 gauss-gym.com / arXiv 2510.15352 / github.com/escontra/gauss_gym / HF datasets，机器人项目导师布置的 literature review
- 创建 [[gaussgym|GaussGym: 3DGS 实景转仿真机器人训练框架]] — 全面报告：场景生成管线(VGGT/NKSR/gsplat)、3DGS drop-in renderer、吞吐优化(100K steps/s)、运动模糊、DinoV2+LSTM 架构、RGB vs depth 实验、ablation、对比表、代码数据、局限性、对机器人项目启示
- Raw 源归档：raw/papers/gaussgym-arxiv-2510-15352.md、raw/articles/gaussgym-github-readme.md、raw/articles/gaussgym-website.md（均带 sha256 frontmatter）
- 更新 index.md（Concepts 新增 gaussgym，Total pages 14 → 15）
