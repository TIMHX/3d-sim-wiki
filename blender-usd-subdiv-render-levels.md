---
title: Blender USD Subdiv Render Levels
created: 2026-08-16
updated: 2026-08-16
type: troubleshooting
tags: [blender, isaac-lab, export-import, troubleshooting]
confidence: high
---

# 坑:USD 导出用渲染级细分,不是视口级

## 症状

Park 场景重新导出后 `geometry.usdc` 874M,而旧导出只有 237M——同一场景几何,文件大了 3.7 倍。

## 根因

`bpy.ops.wm.usd_export`(即 [[isaac-env-export-pipeline]] 的第一步)评估的是**渲染级 Subdiv 细分**(`render_levels`)。Park 地面 Subdiv 视口=3 / 渲染=2:

| 评估级别 | 地面面数 | 导出体积 |
|---|---|---|
| 视口 3 | 3,936,256 quads | 874M ✗ |
| 渲染 2 | 984,064 quads | ~237M ✓ |

地面按视口级烘焙后修饰器已销毁,导出必然用 4× 面数。

## 诊断方法

1. 旧 `geometry.usdc` 导入 Blender 数面数:`Plane` = 1,968,128 tris → 984,064 quads = 渲染 2 级 ✓
2. 对照源文件视口/渲染评估(`m.levels` / `m.render_levels`)的面数,哪个吻合就是哪个级别
3. Subdiv **4/4**(视口=渲染)的场景无此差异(Construction 455M → 456M ✓)

## 修复

- **预防**:烘焙前 `m.levels = m.render_levels` 再评估([[isaac-ground-split]] 的烘焙步骤必须做这步)
- **补救**(修饰器栈已丢):从旧 `geometry.usdc` 导入地面网格重建——旧导出面就是旧模拟的真实表面(含逐面材质分配),导入后按材质 `separate` 即可,见 [[isaac-ground-split]]

## 影响

- 碰撞:地面 approximation `none` 用三角网格,4× 面数 = 4× PhysX cook 负担
- 几何一致性:模拟地面应逐面匹配旧导出,否则机器人接触的地形变了
