---
title: Isaac Friction Profiles
created: 2026-08-16
updated: 2026-08-16
type: concept
tags: [isaac-lab, physics, robot-env]
confidence: high
---

# Isaac 摩擦材质(PMAT__muXXX)

## 数值公式

| 字段 | 值 |
|---|---|
| static_friction | mu / 100 |
| dynamic_friction | 0.9 × static_friction |
| restitution | 0.0 |

例:`PMAT__mu055` → static 0.55,dynamic 0.495,restitution 0。

## 解析链

1. 对象/父级的 `physics_profile` 自定义属性(`mu080` 或 `PMAT__mu080` 均可)
2. 名字里的 `__muXXX` 标记(正则 `(?:^|__)mu(\d{3})`)
3. 默认 `PMAT__mu080`(管线 [[isaac-env-export-pipeline]] 导出时盖章,保证 authoring 必能解析)

## 配置与产物

- 每个环境自己的 `physics_profiles.json` 必须包含场景用到的**所有** mu 码;`--strict` 时缺失即失败
- authoring 在 `/Environment/PhysicsMaterials` 下为每个 profile 生成共享物理材质,以 `strongerThanDescendants` + purpose `"physics"` 绑定到碰撞 prim
- 当前 profile 集合:
  - Park:`mu035 / mu045 / mu050 / mu060 / mu070 / mu080`
  - Construction:`mu040 / mu045 / mu050 / mu055 / mu060 / mu065 / mu070 / mu080`

## 碰撞近似

| 物体 | approximation | 说明 |
|---|---|---|
| 地面 `SURF__*` | `none` | 三角网格精确碰撞 |
| 结构体 | `convexHull` | 导出器默认盖章 `collision_hint=convex_hull`,艺术家可用属性覆盖 |
