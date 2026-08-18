---
title: Lapwing 衣服溶解（Midnight 单网格换材质 + 单前沿交叉）
created: 2026-08-18
updated: 2026-08-18
type: summary
tags: [vrchat, unity, vrchat-avatar, asset-management]
sources: []
confidence: high
---

# Lapwing 衣服溶解（Midnight 单网格换材质 + 单前沿交叉）

把发色溶解 Hub（见 [[lapwing-hair-dissolve-hub]]）复用到 Midnight 衣服切换的落地实现，验证了复杂度分析（[[lapwing-clothes-dissolve-analysis]]）里的**情形 A：只换材质（同网格）= O(n)**。用户 2026-08-18 确认成功。

## 关键前提：4 套衣服其实是同一套网格

`LapwingBody FT Midnight/服装` 下 4 套（BlackWhite/GreenWhite/Black/Brown）是同一套 midnightschool 校服网格（同 FBX GUID），只差材质。原方案用 4 个 prefab + `m_IsActive` 开关切换 → 60 个 SkinnedMeshRenderer + 4 套 `Armature.1` 骨架 + 4 套颜色贴图。

**换色只涉及 4 个材质组（12 个渲染器）**，另有 3 个渲染器恒用 `color1/parts.mat` 不变色（不参与溶解）：

| 材质组 | 渲染器数 | BlackWhite | GreenWhite | Black | Brown |
|---|---|---|---|---|---|
| inner | 3 | color4 | color6 | color7 | color8 |
| outer | 4 | color4 | color6 | color7 | color8 |
| parts | 4 | color4 | color6 | color7 | color8 |
| tights | 1 | color4 | color6 | color7 | color8 |

## 单网格合并

- 删 GreenWhite/Black/Brown，保留 BlackWhite（真身）。
- 建替身 `服装/Clothes_Crossfade`：12 个变色渲染器，**共享真身的 `Armature.1` 骨架**（bones 按相对路径重绑），`rootBone` 也共享（真身 rootBone = `AutoAnchorObject`）；GameObject `activeSelf=false` 隐藏，渲染器组件 `enabled=true`。

## 材质溶解设置

- 全部切透明渲染模式（opaque `lilToonOutline` 溶解代码被编译排除）：inner/outer/tights → `lilToonTransparentOutline`，parts → `lilToonTwoPassTransparentOutline`（透明两 pass，丝袜）。
- `_DissolveParams=(3, 1, -1.0, 0.10)`（x=坐标 y=线 z=边界 w=模糊）、`_DissolvePos=(0, 0.10, 0, 0)`。
- 可见条件：`dot(positionOS, normalize(_DissolvePos)) > border` ⟺ `positionOS.y > border`（**严格大于**）。

## 单前沿镜像（复用头发 v4）

| 绑定 | 曲线 |
|---|---|
| 真身（旧色） | z：`-1.0 → 0.6` |
| 替身（新色） | `_DissolvePos.y=-0.1`（动画绑定）；z：**取负** `1.0 → -0.6` |

镜像原理：替身可见条件翻转为 `y < -border`，其前沿 `-border` 与真身前沿 `border` 逐点重合。

## 边界标定（用户实测）

各部位 `[完整, 消失]` 不同：stocking `[-0.9, 0]`、loafer `[-0.9, -0.5]`、gartarbelt `[-0.2, 0]`、body `[-0.3, 0.6]`。通用区间：**complete = -1.0**（网格最低点 -0.9 再下探留 blur 余量）、**gone = 0.6**。

⚠️ complete 不能正好压在网格最低点：严格不等式 `y > border` 会让最低点（鞋底）在复位时溶解掉一圈露白边。

## 状态机（两控制器都加，同头发两层结构）

- **触发门禁** `Sensor_Clothes`(w=1)：AnyState→Sens_N `[衣服菜单=N, self=false]` + VRC Parameter Driver → Set `ClothesFadeTrigger`。
- **三段流水线** `Action_Clothes`(w=1, 默认 Promote_0)：AnyState→Swap_N `[ClothesFadeTrigger + 衣服菜单=N]` → Swap_N(2帧 PPtr 换替身材质) →exit1→ Cross_N(0.4s 单前沿) →exit1→ Promote_N(2帧 PPtr 移交真身+复位 z=-1.0+关替身)。
- 全 WD=off；`ClothesFadeTrigger` 是控制器本地 Trigger（不进 expression parameters，同 HairFadeTrigger）。
- 颜色映射：衣服菜单 0=BlackWhite / 1=GreenWhite / 2=Black / 3=Brown。

## 踩坑（实现时踩过）

- **替身镜像必须取负（-z），不是 `2*complete - z`**。用错公式替身整段全可见 → 新色瞬间满屏 → "瞬间切换"假象。
- **Cross/Promote clip 必须显式带 x/y/w 常量曲线**（x=3/y=1/w=0.10），缺了材质实例的 dissolve 模式不生效 → 无溶解。头发 clip 也有，直接照抄结构。
- **替身 rootBone 必须共享真身**，null 会被剔除不渲染。
- **脚本加 StateMachineBehaviour**：`AddStateMachineBehaviour` 有返回值但 `st.behaviours` 数组不更新，要 `ScriptableObject.CreateInstance` + `AssetDatabase.AddObjectToAsset` + 手动塞进 `st.behaviours`。
- 两控制器都要加层：`LapFX FT Midnight.controller`（descriptor FX，Play+GestureManager 测试用）+ `Lapwing Midnight.controller`（场景预览 Animator，录制动画用）。

## Related

- [[lapwing-hair-dissolve-hub|Lapwing 发色溶解 Hub]]
- [[lapwing-clothes-dissolve-analysis|Lapwing 服装溶解复杂度分析]]
- [[lapwing-min-avatar-project|Lapwing-min Avatar Project]]
- [[index|Wiki Index]]
