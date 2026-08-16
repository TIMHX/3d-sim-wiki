---
title: Isaac Env Export Pipeline
created: 2026-08-16
updated: 2026-08-16
type: concept
tags: [isaac-lab, isaac-sim, blender, export-import, workflow, robot-env]
confidence: high
---

# Isaac 环境导出管线(Blender → Isaac)

静态环境(地面 + 固定物体)从 Blender 到 Isaac Sim/Lab 的标准两步管线,位于仓库 `scripts/tools/blender_isaac/`。

## 位置

| 视角 | 路径 |
|---|---|
| 宿主(Host) | `/home/xing/robot/IsaacLab` |
| 容器(Docker `isaac-lab-base`) | `/workspace/isaaclab`(bind mount 仅 `source`、`scripts`、`tools`、`logs`、`docs`、`data_storage`) |
| 环境包暂存 | `scripts/tools/blender_isaac/environments/<name>/`(规范名:`park`、`park2`、`construction`、`construction2`;目录名即环境 ID) |

环境包布局:`scene.blend` / `environment.json` / `physics_profiles.json` / `geometry.usdc` / `simulation.usda` / `simulation.usda.report.json` / `textures/`。

脚手架用 `create_environment.sh <name> --template <repo>/scripts/tools/blender_isaac/scene_example.blend`(默认模板文件名是旧的 `blender_isaac_static_environment_example.blend`);共享 `physics_profiles.json` 只有 6 码(mu080/070/060/055/050/045),导出脚本 `sync_used_profiles` 自动补缺 mu035/040/065。**铁律:严禁改动导师 repo 的脚本/格式,只产 blender 场景 + zip 交付,场景命名去适配脚本,不 reverse。**

环境搭建与容器日常操作见 [[isaaclab-docker-env]];面向用户的运行步骤(复制场景、容器内执行、接入 task)见 [[isaaclab-operation-manual]],本页记管线内部机制。

## 第一步:几何导出(宿主机,headless Blender)

```bash
blender <env>/scene.blend --background \
  --python scripts/tools/blender_isaac/export_environment_usd.py
```

- 集合 `SURFACES` + `STATIC_STRUCTURES` 的对象 = 碰撞物体;`VISUAL_ONLY`(可选)= 只导出无碰撞
- 导出前在内存中给每个对象盖章:`physics_profile`、`collision_enabled`、`collision_hint`(不自动保存 .blend)
- profile 解析顺序:① `physics_profile` 自定义属性(对象或父级)② 名字里的 `__muXXX` 标记 ③ 默认 `PMAT__mu080`
- 自动把缺失的 profile 写进 `physics_profiles.json`(只增不改已有值)
- `bpy.ops.wm.usd_export`:triangulate、meters、root `/Environment`、custom props → `userProperties` 命名空间
- 同时刷新 `environment.json`(exported_mesh_objects、used_physics_profiles)
- **注意:导出评估的是渲染级细分**,详见 [[blender-usd-subdiv-render-levels]]

## 第二步:物理生成(容器内,Isaac Sim)

```bash
docker exec isaac-lab-base bash -c \
  'cd /workspace/isaaclab && ./isaaclab.sh -p scripts/tools/blender_isaac/author_environment_physics.py \
   scripts/tools/blender_isaac/environments/<name> --strict'
```

- 读 `geometry.usdc` 作 sublayer,写 `simulation.usda`(overlay)+ report.json
- 每个 `PMAT__muXXX` profile 生成一个共享物理材质(见 [[isaac-friction-profiles]])
- `--strict` 时遇到未知 profile 直接失败;报告里验证 mesh/collision/binding 数量守恒
- **坑**:脚本正常写完输出后,Isaac Sim 关闭阶段会 segfault(退出码非 0)——无害,以 report 文件为准

## 什么变更后要重新导出

| 变更 | 几何导出 | 物理生成 |
|---|---:|---:|
| 几何/UV/材质/集合 | ✅ | ✅ |
| 只改摩擦数值 | — | ✅ |
| 新增 mu 码 | ✅(自动补 profile) | ✅ |

## 结构要求

对象必须是两层扁平 prim(`/Environment/<对象>/<网格>`),EMPTY 父级会弄坏导入,见 [[blender-isaac-env-structure]];单 plane 多材质地面必须先拆分成独立平面,见 [[isaac-ground-split]]。
