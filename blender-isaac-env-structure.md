---
title: Blender Isaac Env Structure
created: 2026-08-16
updated: 2026-08-16
type: concept
tags: [blender, isaac-lab, scene-design, robot-env]
confidence: high
---

# Blender 场景 → Isaac 环境的结构约定

[[isaac-env-export-pipeline]] 的导入脚本对这些约定是硬依赖,违反即失败。

## 两层扁平层级(最重要)

USD 里每个物理物体必须是两层:

```
/Environment/<Object>       <- Blender 对象(Xform)
    └─ <MeshData>           <- 网格数据(Mesh)
```

- **禁止** EMPTY 父级包 MESH 子物体(三层结构会直接弄坏导入)
- 同一资产的多部件(野餐桌、手推车、树的树皮+树叶)在 Blender 里**合并成单个 MESH**,烘焙修饰器后再合并
- 同一资产的多个实例(石头 ×2、托盘 ×4)保持**独立对象**,不要合并

## 命名约定

- 所有物理物体名以 `__muXXX` 结尾(摩擦系数标记,如 `Wooden_Bench__mu045`)
- 地面分区命名 `SURF__<zone>__muXXX`,直接沿用材质名(如 `SURF__grass__mu080`)
- 标记物 Goal / Object(Obj1) / Start 是无子级的 EMPTY,位置由 `extract_markers.py` 输出到 `scene_markers.json`

## 集合

| 集合 | 内容 | 导出行为 |
|---|---|---|
| `SURFACES` | 地面 | 碰撞物体 |
| `STATIC_STRUCTURES` | 静止道具 | 碰撞物体,默认 `collision_hint=convex_hull` |
| `VISUAL_ONLY` | 纯视觉 | 只导出,`collision_enabled=false` |

## 拆分地面

单 plane 多材质(顶点/面级材质控制)在管线里只能映射一个 `_mu`,必须先按材质拆成独立平面,见 [[isaac-ground-split]]。
