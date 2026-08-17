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

## 最终架构（2026-08-17 交叉溶解版 v3）

用户要求 FadeIn/FadeOut **同时发生**（串行三段式有"半头发/无头发"的空窗期）→ 改为**真·交叉溶解**：

- **替身渲染器（ghost）**：`头发/HairPony_Crossfade` + `头发/LowPonytail_A_Lapwing/LowPonytail_{Back,Bangs,RibbonA}_Crossfade`（复制原网格+骨骼，默认隐藏）。换色时新色先加载到替身（全透明），替身渐入的同时旧真身渐出，最后真身接棒、替身隐藏——同发型换色和跨发型换色统一处理。
- **`Hair_Cross_0..7.anim`**（0.25s，不循环）：所有真身溶解 0→1；目标发型的替身 1→0；结尾帧 PPtr 移交材质给真身 + m_IsActive 交接 + 目标真身溶解复位 0。
- **状态机极简**：每色常驻状态 `Color_0..7`（WD=off，motion=Hair_Cross_N）+ `AnyState → Color_N`（发色菜单=N，self=false，dur=0）。**无 Sensor 层、无 Trigger、无 Parameter Driver**。
- 控制器：`LapFX FT.controller` 末尾 Action_HairColor 层（**重点**——用户测试只用 Play+GestureManager，只读 descriptor 引用的控制器）；`LapwingBody FT.controller` 有同名预览层。
- 旧资产已删：Hair_FadeOut/FadeIn/Hair_Mat_0..7、HairHubFX.controller、发色菜单_1/2/3 孤儿参数（控制器+表达式资产均已清）。

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
- `Clips/Hair_FadeOut.anim` / `Hair_FadeIn.anim` — 溶解 `_DissolveParams.z` 0→1 / 1→0（0.25s，**最终版 4 个绑定**：HairPony 槽0 + LowPonytail Back/Bangs/RibbonA 槽0。RibbonB 已移除（场景非激活）；两个槽1 阴影材质（Lap_Shadow/FakeShadow）不参与溶解——Animation 窗口无法显示槽1 的材质数组绑定，且阴影短暂残留视觉可接受）
- `Clips/Hair_Mat_0..7.anim` — 2 帧：`m_IsActive` 网格开关 + `m_Materials.Array.data[0]` PPtr 材质槽（无 RibbonB）
- `HairHubFX.controller` — 见下

材质：9 个发色/阴影材质启用 `LIL_FEATURE_DISSOLVE` + `LIL_FEATURE_DissolveMask`，`_DissolveParams=(1,0,0,0.12)`（mode=1 遮罩、b=阈值、a=柔和）。lilToon 语义：`mask值 > b 可见`，b 从 0→1 即溶解消失；关键字门槛在 `lil_common_frag_alpha.hlsl`（`LIL_FEATURE_DISSOLVE`）与 `lil_common_frag.hlsl`（`LIL_FEATURE_DissolveMask`）。

## 控制器结构（MA MergeAnimator → FX，挂在 `头发` 组上）

- 参数：`发色菜单`(Int，同步，菜单不变)、`HairFadeTrigger`(Trigger，本地，**不进 Expression Parameters**)
- `Sensor_HairColor`（weight 1）：默认 `SensorIdle`(空)；`Sens_0..7` 空状态各带 VRC Avatar Parameter Driver → Set HairFadeTrigger；`Any State → Sens_N` 条件 `发色菜单 Equals N`，**CanTransitionToSelf 关**，duration 0
- `Action_HairColor`（weight 1）：`Idle`(默认) ← `FadeIn` ← `Mat_0..7` ← `FadeOut`；`Any State → FadeOut` 条件 HairFadeTrigger（自转关）；`FadeOut → Mat_N` 条件发色菜单=N 且 **Exit Time 1.0**（全透明才换）；`Mat_N → FadeIn`、`FadeIn → Idle` 均 Exit Time 1.0
- **所有状态 WD=off**（关键：否则 Mat_N 单帧会把 dissolve 重置回 0，换材质瞬间露馅）

旧系统拆除：LapFX FT.controller 删除 发色菜单/发色菜单_Local/发色菜单_Remote 三层（Local/Remote 原本 weight=0 是死代码）；删除 7 个 MA MaterialSwap 组件（**保留同 GO 的 MenuItem**，它负责设参数）；Android/Midnight avatars 未动（不同材质体系，Quest 用 VRCQuestToolsOutput 材质）。

## 已知行为与坑（实现时踩过）

- **lilToon 渲染模式门槛**：`Hidden/lilToonOutline` 是不透明变体（UsePass → ltspass_opaque，LIL_RENDER=0），溶解代码被编译排除。发色材质必须用 `Hidden/lilToonCutoutOutline`（镂空+描边，LIL_RENDER=1），并保留 `LIL_FEATURE_DISSOLVE` + `LIL_FEATURE_DissolveMask` 关键字（换 shader 后关键字会重置，需重挂）。
- **表达式参数默认值残留**：`发色菜单` 在参数资产里默认=7（旧位编码 `发色菜单_1/2/3` 默认 1,1,1 的产物），需改为 0；位编码参数随旧层退役后应从资产中删除（省 3 同步槽）。
- **AAO 移除未使用对象 vs MA 合并源**：激活动画若只存在于 MA MergeAnimator 源里，AAO 的 removeUnusedObjects 分析（在 MA 合并前运行）看不到 → 默认隐藏的 LowPonytail 整组被当死物体删除。修复：PC 头像关掉 TraceAndOptimize.removeUnusedObjects；同时给每个头发渲染器加常驻 m_IsActive 关键帧防止 mesh 合并。
- **孤儿过渡（历史残留）**：4 个 LapFX 控制器各含 335 条 `m_DstState` 指向已删除状态的过渡（原作者工具残留，运行时无害）。它们会让遍历过渡的编辑器工具（Play 模式模拟/处理）中断 → **PC 头像 Play 模式 Animator 控制器变 null → 全部动画失效**。已用脚本清理（递归扫描 states+anyState+嵌套子状态机，移除 null 目标过渡）。
- **0 帧动画采样问题**：衣服/摸头动画（Default/Jacket/Demon/Cape 等）是 0 长度或单帧 clip，经 duration=0 的 AnyState 转换进入状态时，部分时序下首帧不被采样 → 状态机切换了但属性未写入，视觉延迟到下一次交互（症状：点换衣无效，换一次发色后衣服才变）。修复：所有相关 clip 补齐 2 帧（t=0 和 t=1/60 同值）。
- **脚本创建的材质属性绑定在 Animation 窗口显示 (缺失！)**：用脚本按路径字符串写入的绑定（`m_Materials.Array.data[0]._DissolveParams.z`），窗口在无法解析（未选中正确根物体/控制器不含该 clip）时显示"缺失"。不影响运行时；手动重录方法：选中 avatar 根 → 临时挂引用该 clip 的控制器（如 HairHubFX.controller）到场景 Animator → 动画窗口 Add Property 重新加材质属性（窗口写为 `材质._DissolveParams.z`，与脚本路径运行时等价）。重录绑定清单：FadeOut/FadeIn 各 7 组（HairPony 槽0+槽1、LowPonytail Back/Bangs/RibbonA/RibbonB 槽0 溶解 + Bangs 槽1 FakeShadow `_Color.a`），0.25s、t=0/t=0.25 两关键帧。
- **AnimatorControllerLayer 是 struct**：`ctrl.layers[i].name = x` 改的是副本，必须 `var l = ctrl.layers; l[i].x=...; ctrl.layers = l;`。`CreateAnimatorControllerAtPath` 自带 "Base Layer" 层。
- 出生时 Sensor 默认态触发一次 → 出生自带一次发色渐入（当作生成特效）
- 快速连续换色：trigger 残留导致透明期变长，但每次交换重读最新发色菜单值，落点正确
- 未验证项：VRC Parameter Driver 对 Trigger 参数的支持、实际游戏内溶解视觉效果（需上传 VRChat 实测）

## 回档

git 分支 `hair-dissolve-hub`，基线 `2fa2e05a`（main）。关键检查点：`a8e26dbf`（首版）、`115d41b5`（cutout/默认值/AAO 修复）、`386d6c64`（孤儿过渡清理 + Hub 并入 LapFX FT）。全部回滚：`git checkout main` 或 `git reset --hard 2fa2e05a`（先关 Unity）。

## Related

- [[lapwing-min-avatar-project|Lapwing-min Avatar Project]]
- [[unity-mcp-avatar-introspection|Unity MCP Avatar Introspection]]
- [[index|Wiki Index]]
