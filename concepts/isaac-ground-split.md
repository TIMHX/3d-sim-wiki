---
title: Isaac Ground Split
created: 2026-08-16
updated: 2026-08-16
type: concept
tags: [blender, isaac-lab, physics, modeling, robot-env]
confidence: high
---

# 地面按材质拆分(单 plane 多摩擦分区)

## 问题

地面常是一个 plane + 顶点/面级多材质(草地/泥土/混凝土)。但 [[isaac-env-export-pipeline]] 只能**每个对象映射一个 `_mu`**——单 plane 无法表达分区摩擦。

## 方法(烘焙 → 按材质切分)

1. **烘焙评估几何**(关键,把修饰器效果冻进网格):
   ```python
   dg = bpy.context.evaluated_depsgraph_get()
   ob_eval = ground.evaluated_get(dg)
   em = ob_eval.to_mesh()   # ← 必须走 evaluated_get!
   new_mesh = em.copy(); ob_eval.to_mesh_clear()
   ground.data = new_mesh; ground.modifiers.clear()
   ```
   - 坑:`ground.to_mesh()` 不带参数返回的是**未评估的基础网格**(Subdiv/Displace 全部丢失)
   - 烘焙前把 Subdiv 视口级设为渲染级(`m.levels = m.render_levels`),因为管线导出用渲染级,见 [[blender-usd-subdiv-render-levels]]
2. **编辑模式按材质分离**:`bpy.ops.mesh.separate(type='MATERIAL')`(C 算子,百万级面也快;bmesh 内存风险)
   - 分离后每个分片的材质槽自动剪枝为 1 个
3. 每片重命名为其材质名(`SURF__<zone>__muXXX`),复制管线属性(`material_mapping` 等)

## 不穿模保证(分区不变量)

分离片来自**同一个评估网格**:面集合两两不交、共享边界顶点完全相同 → 数学上无重叠、无 z-fighting、无裂缝。验证手段:**分离前后总面数逐位相等**(面数守恒)。

实测:Park 1,968,128 tris = grass 1,779,648 + dirt 188,480;Construction 3,936,256 quads = concrete + tracks + drydirt。

## 另一种做法:分层独立 plane

[[blender-construction-site-tutorial]] 采用另一种路线:BaseGround 打底,路径/混凝土层各自是**独立的 plane 叠在不同高度**(Z=0.03 等)。不需要面级材质拆分,代价是各层间靠高度差防穿插,且每层摩擦单一。逐面多材质的地面(如 Park 的草地+泥土)则必须用本页的材质拆分法。

## 摩擦分片绑定

每个 `SURF__<zone>__muXXX` 分片在 simulation.usda 里绑定对应 `PMAT__muXXX`,地面碰撞近似用 `none`(三角网格),见 [[isaac-friction-profiles]]。
