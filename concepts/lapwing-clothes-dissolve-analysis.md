---
title: Lapwing 服装溶解复杂度分析（能否复用发色 Hub）
created: 2026-08-17
updated: 2026-08-17
type: analysis
tags: [vrchat, unity, vrchat-avatar, algorithm]
sources: []
confidence: high
---

# Lapwing 服装溶解复杂度分析（能否复用发色 Hub）

发色溶解 Hub（见 [[lapwing-hair-dissolve-hub|Lapwing 发色溶解 Hub]]）能否用于衣服切换的复杂度分析。结论：**材质替换情形 O(n) 直接可行；不同模型情形在"逐对定制"或"逐件标定"下是 O(n²)，但采用全局统一扫描区间 + 单共享 Cross clip 可压回 O(n+m)**。

## 情形 A：只换材质（同网格）——O(n)

网格固定、只有材质 GUID 变化，与头发系统完全同构：Swap/Promote 的 PPtr 曲线 O(n)，Cross 浮点曲线与 N 无关。加第 n+1 个材质 = 1 材质 + 1 组 PPtr 键。

## 情形 B：不同模型（多件衣服不同网格）——朴素方案 O(n²)

PC 服装是多个不同网格（LapwingOriginal/Jacket/Demon/Heather 等）。朴素思路是每对 (从,到) 一条专属过渡 → n² 条过渡、n² 个 clip。

### 单前沿镜像的隐藏配对约束（关键洞察）

单前沿要求出/入两条扫掠逐点互为相反数：`border_出(t) = -border_入(t)` ∀t。头发系统成立是因为新旧头发是同一网格同一坐标范围。不同网格下：

- 出场的 A：`a_vis → G`；入场的 B 镜像：`-a_vis → -G`
- B 的隐藏起点要求 `-a_vis ≤ min_y_B` ⟺ **A 的完整值 ≤ B 的底部**——跨衣服不等式，随配对变化

→ per-outfit 标定无法同时满足所有配对；要保逐对精确的前沿重合就得逐对重标定，**效果质量层面是 O(n²)**，且每新增一件衣服牵动所有既有配对。

## 逃生门：全局统一扫描区间 → 标定 O(1)

所有衣服放弃自己的完整值，共用一次性选定的保守区间（如 [-0.5, 1.0]）：

- 出场：`global_min → global_max`
- 入场（镜像）：`-global_min → -global_max`

任意 (A,B) 配对前沿自动逐点重合，零配对约束。加第 n+1 件 = 零标定（绑定值照抄全局常量）。

**代价**：① 扫描节奏全局统一（小件衣服在 0.4s 前半段就扫完，视觉是早消失/早出现，无错位）；② 要求所有衣服 pivot/朝向一致、坐标范围落在全局区间内（VRChat 衣服通常满足，特例单独处理）；③ 全局区间选保守就永不再动。

## 复杂度对照表

| 方案 | 标定 | 加一件衣服 | 总维护 |
|---|---|---|---|
| 逐对定制 | O(n²) | O(n) | O(n²) |
| per-outfit 标定 + 单前沿 | O(n²)（镜像配对约束） | O(n) | O(n²) |
| 全局统一区间 + 1 个共享 Cross | O(1) | O(1) | O(n+m) |

**严格线性的两个必要条件**：① 全局统一区间（放弃逐件标定）；② Cross 只用 1 个共享 clip（沿用头发 per-N 副本结构会导致每加一件改 n 个 clip = O(n)/次）。线性不是免费的：要求"效果全局统一化"；想保留个性化标定，n² 就是真实价格。

## 其他移植成本（非复杂度）

- 每件衣服材质需 lilToon CutoutOutline 变体 + 溶解启用
- 入场衣服可互相当替身（无需复制网格），但镜像翻转 `_DissolvePos.y` 会写到真实渲染器 → Promote 需按 N 复位（O(n) 复位键）
- AAO：大量默认隐藏衣服需常驻 m_IsActive 键；PC 的 removeUnusedObjects 已关
- 建议先做 2 套衣服小规模单前沿验证再铺开

## Related

- [[lapwing-hair-dissolve-hub|Lapwing 发色溶解 Hub]]
- [[lapwing-min-avatar-project|Lapwing-min Avatar Project]]
- [[index|Wiki Index]]
