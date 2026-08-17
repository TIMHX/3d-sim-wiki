---
title: Lapwing 发色溶解 Hub（可扩展渐变换发色）
created: 2026-08-17
updated: 2026-08-17
type: summary
tags: [vrchat, unity, vrchat-avatar, asset-management]
sources: []
confidence: high
---

# Lapwing 发色溶解 Hub（可扩展渐变换发色）

Lapwing-min avatar 的发色切换从「瞬切」升级为「溶解消失 → 全透明瞬间换材质 → 溶解出现」的 O(N) 可扩展机制。用例见 [[lapwing-min-avatar-project|Lapwing-min Avatar Project]]，构建方法见 [[unity-mcp-avatar-introspection|Unity MCP Avatar Introspection]]。

## 为什么不用攻略的两两交叉溶解

8 色两两配对需要 56 条过渡连线（O(N²)），加色不可扩展。Hub 机制把「检测变化」和「执行溶解」分层，加第 N+1 色 = 1 材质 + 1 动画 + 2 连线。

## 颜色映射（发色菜单 Int → 发型/材质）

| 值 | 发型 | HairPony 槽0 | LowPonytail ×4 槽0 |
|---|---|---|---|
| 0 | Pony（原发色，仅出生/复位） | Lap_Hair | LowPonytail_07 |
| 1 | Pony | Lap_HairBrown | 07 |
| 2 | Pony | Lap_HairWhite | 07 |
| 3 | LowPony | Lap_Hair | LowPonytail_06 |
| 4 | LowPony | Lap_Hair | LowPonytail_04 |
| 5 | LowPony | Lap_Hair | LowPonytail_05 |
| 6 | LowPony | Lap_Hair | LowPonytail_09 |
| 7 | LowPony | Lap_Hair | LowPonytail_08 |

渲染器路径（相对 avatar 根）：`头发/HairPony`（槽0 发色 + 槽1 Lap_Shadow）、`头发/LowPonytail_A_Lapwing/LowPonytail_{Back,Bangs,RibbonA,RibbonB}`（槽0 发色；Bangs 槽1 = FakeShadow，无溶解属性，改用 `_Color.a` 淡出）。注意 `Lap_Shadow` 同时被 Body 槽2 引用——动画按渲染器路径绑定，只影响 HairPony 实例，不影响身体。

## 资产（Assets/动画/HairDissolve/）

- `Mask_Dissolve.png` — 共享溶解遮罩（256² 垂直渐变 0.02→1 + 噪声，自下而上溶解），程序生成
- `Clips/Hair_FadeOut.anim` / `Hair_FadeIn.anim` — 溶解 `_DissolveParams.z` 0→1 / 1→0（0.25s，7 个绑定：5 发色槽 + HairPony 槽1 阴影 + FakeShadow alpha）
- `Clips/Hair_Mat_0..7.anim` — 2 帧：`m_IsActive` 网格开关 + `m_Materials.Array.data[0]` PPtr 材质槽
- `HairHubFX.controller` — 见下

材质：9 个发色/阴影材质启用 `LIL_FEATURE_DISSOLVE` + `LIL_FEATURE_DissolveMask`，`_DissolveParams=(1,0,0,0.12)`（mode=1 遮罩、b=阈值、a=柔和）。lilToon 语义：`mask值 > b 可见`，b 从 0→1 即溶解消失；关键字门槛在 `lil_common_frag_alpha.hlsl`（`LIL_FEATURE_DISSOLVE`）与 `lil_common_frag.hlsl`（`LIL_FEATURE_DissolveMask`）。

## 控制器结构（MA MergeAnimator → FX，挂在 `头发` 组上）

- 参数：`发色菜单`(Int，同步，菜单不变)、`HairFadeTrigger`(Trigger，本地，**不进 Expression Parameters**)
- `Sensor_HairColor`（weight 1）：默认 `SensorIdle`(空)；`Sens_0..7` 空状态各带 VRC Avatar Parameter Driver → Set HairFadeTrigger；`Any State → Sens_N` 条件 `发色菜单 Equals N`，**CanTransitionToSelf 关**，duration 0
- `Action_HairColor`（weight 1）：`Idle`(默认) ← `FadeIn` ← `Mat_0..7` ← `FadeOut`；`Any State → FadeOut` 条件 HairFadeTrigger（自转关）；`FadeOut → Mat_N` 条件发色菜单=N 且 **Exit Time 1.0**（全透明才换）；`Mat_N → FadeIn`、`FadeIn → Idle` 均 Exit Time 1.0
- **所有状态 WD=off**（关键：否则 Mat_N 单帧会把 dissolve 重置回 0，换材质瞬间露馅）

旧系统拆除：LapFX FT.controller 删除 发色菜单/发色菜单_Local/发色菜单_Remote 三层（Local/Remote 原本 weight=0 是死代码）；删除 7 个 MA MaterialSwap 组件（**保留同 GO 的 MenuItem**，它负责设参数）；Android/Midnight avatars 未动（不同材质体系，Quest 用 VRCQuestToolsOutput 材质）。

## 已知行为与坑（实现时踩过）

- **AnimatorControllerLayer 是 struct**：`ctrl.layers[i].name = x` 改的是副本，必须 `var l = ctrl.layers; l[i].x=...; ctrl.layers = l;`。`CreateAnimatorControllerAtPath` 自带 "Base Layer" 层。
- 出生时 Sensor 默认态触发一次 → 出生自带一次发色渐入（当作生成特效）
- 快速连续换色：trigger 残留导致透明期变长，但每次交换重读最新发色菜单值，落点正确
- 悬空 PPtr 警告（LapFX 内 2 处 fileID）与 Thry `IsLocal` 条件警告为**改动前已存在**
- 未验证项：VRC Parameter Driver 对 Trigger 参数的支持、实际游戏内溶解视觉效果（需 Play 模式/VRChat 实测）

## 回档

git 分支 `hair-dissolve-hub`，基线 `2fa2e05a`（main）。全部回滚：`git checkout main` 或 `git reset --hard 2fa2e05a`（先关 Unity）。

## Related

- [[lapwing-min-avatar-project|Lapwing-min Avatar Project]]
- [[unity-mcp-avatar-introspection|Unity MCP Avatar Introspection]]
- [[index|Wiki Index]]
