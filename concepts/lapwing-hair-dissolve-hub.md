---
title: Lapwing 发色溶解 Hub（坐标溶解 · 单前沿交叉 · 双头像）
created: 2026-08-17
updated: 2026-08-19
type: summary
tags: [vrchat, unity, vrchat-avatar, asset-management]
sources: []
confidence: high
---

# Lapwing 发色溶解 Hub（坐标溶解 · 单前沿交叉 · 双头像）

Lapwing-min avatar 的发色切换从「瞬切」升级为「溶解消失 → 换材质 → 溶解出现」的可扩展机制。v4 起：溶解方式从遮罩改为**坐标+线**，交叉溶解改为**单前沿镜像扫掠**，并完整移植到 **Midnight avatar**。用例见 [[lapwing-min-avatar-project|Lapwing-min Avatar Project]]，构建方法见 [[unity-mcp-avatar-introspection|Unity MCP Avatar Introspection]]。

## 为什么不用攻略的两两交叉溶解

8 色两两配对需要 56 条过渡连线（O(N²)），加色不可扩展。Hub 机制把「检测变化」和「执行溶解」分层，加第 N+1 色 = 1 材质 + 1 动画 + 2 连线。

## 最终架构（2026-08-17 坐标单前沿版 v4，PC+Midnight 均用户确认可用）

### 材质溶解设置（9 个发色材质 + 阴影，共用资产）

lilToon 坐标模式溶解：`_DissolveParams=(3, 1, border, 0.12)`——x=3 坐标方式、y=1 线形状、z=边界(border)、w=模糊；`_DissolvePos=(0, 0.1, 0)` 溶解向量；`_DissolveNoiseStrength=0.1`。

可见条件：`dot(positionOS, normalize(_DissolvePos)) + 噪点 > border`。

**边界标定（用户实测）**：
- 完整显示：Pony `z=0`；LowPonytail `z=-0.1`（长发，0 会显示不全）
- 完全消失：`z=0.7`
- 噪点来自 `_DissolveNoiseMask` 贴图（`采样-0.5 × 强度`），本版本 `LIL_FEATURE_DissolveNoiseMask` 在 lil_replace_keywords.hlsl 里无条件 #define，无需材质关键字。⚠️ 当前噪点贴图槽位为空（用户删除 `Mask_Dissolve.png`，待重做；缺省采样按白 1.0 → 恒定 0.05 偏移，无噪点扰动但不报错）。

### 状态机（与 v3.2 相同的三层结构）

- **替身渲染器（ghost）**：`头发/HairPony_Crossfade` + `头发/LowPonytail_A_Lapwing/LowPonytail_{Back,Bangs,RibbonA}_Crossfade`（复制原网格+骨骼，默认隐藏；**渲染器组件必须 enabled，靠 GameObject inactive 隐藏**）。
- **触发门禁**：`Sensor_HairColor` 层（w=1）8 个常驻 Sens_N 状态各带 VRC Parameter Driver → Set HairFadeTrigger；`AnyState→Sens_N`（发色菜单=N, self=false）。触发器消费一次即消失。
- **三段流水线**（`Action_HairColor` 层，w=1，默认态 Promote_0）：`AnyState→Swap_N`【HairFadeTrigger + 发色菜单=N】→ `Swap_N`(2帧，仅 PPtr 换替身材质) →exit1→ `Cross_N`(**0.4s**，单前沿交叉) →exit1→ `Promote_N`(2帧，PPtr 移交真身+最终开关+溶解复位，常驻)。
- 所有状态 WD=off；Promote 必须带溶解复位键（真身复位到 完整值，否则 WD 残留把新材质写隐形）。

### 单前沿交叉（v4 关键设计）

v3.2 的「新旧同时反向交叉」产生**两股白色边缘**（旧发 0→0.7 边缘上移 + 新发 0.7→0 边缘下移）。v4 改为替身**方向翻转 + 边界镜像**，新旧边缘完全重合，一条前沿从下往上扫：

| 绑定 | 曲线 |
|---|---|
| 真身（旧发） | z：Pony `0→0.7`，LowPony `-0.1→0.7` |
| 替身（新发） | `_DissolvePos.y=-0.1`（动画绑定，仅替身路径）；z：Pony `0→-0.7`，LowPony `0.1→-0.7` |

镜像原理：替身可见条件变为 `y < -border`，其前沿 `-border` 与真身前沿 `border` 始终相等。Promote 无需复位 `_DissolvePos`（绑定只在替身路径上，PPtr 移交后真身材质默认向量不受影响）。

### 动画资产（Assets/动画/HairDissolve/Clips/）

- `Hair_Swap_N`（8）：2 帧 PPtr 换替身材质（无溶解曲线）
- `Hair_Cross_N`（8）：0.4s；真身 4 渲染器 x=3/y=1/w=0.12 + z 扫掠；替身 z 镜像扫掠 + `_DissolvePos.y=-0.1` + m_IsActive(1→0)
- `Hair_Promote_N`（8）：2 帧；PPtr 移交 + m_IsActive + 复位键（x=3/y=1/w=0.12/z=完整值；Pony=0, LowPony=-0.1）

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

Midnight 菜单只暴露 1~7（Black/White/Gold_Low/Brown_Low/Beige_Low/Black_Low/White_Low），映射与 PC 相同。

## Midnight 移植（2026-08-17，用户确认成功）

Midnight 与 PC 共用全部头发材质（同 GUID）且头发模型一致 → 24 个 clip 直接复用，标定通用。移植内容：

- **4 个替身渲染器**：场景内新建 `*_Crossfade`（克隆网格 `Instantiate(sharedMesh)`、共享 bones/rootBone、材质取源数组前 N 个、渲染器设置镜像 PC 替身；GO inactive）
- **`Assets/动画/Midnight/LapFX FT Midnight.controller`**（descriptor FX）：+HairFadeTrigger 参数、克隆 Sensor_HairColor(9 态)+Action_HairColor(24 态) 两层（状态/过渡/条件/VRC Parameter Driver 行为全部程序化克隆自 LapFX FT Active，WD=off、exit-time 链条逐项验证）
- **`Assets/动画/Midnight/Lapwing Midnight.controller`**（场景预览 Animator 用）：同步两层
- **`.../Midnight/Midnight.asset`**：发色菜单 default 7→0
- **Midnight TraceAndOptimize.removeUnusedObjects=False**（防 AAO 剥离默认隐藏的替身；场景 YAML 字段名即 `removeUnusedObjects`，Unity 属性反射需 NonPublic）
- 用户已自行清理：旧 `发色菜单_Local/Remote` 层、位编码 `发色菜单_1/2/3` 参数；MA MenuItem 菜单（Hair Color 7 项）保留
- 未动：Android 两头像（Quest 材质体系）、瞳色菜单、衣服菜单、摸头

## 已知行为与坑（实现时踩过）

- **lilToon 渲染模式门槛**：`Hidden/lilToonOutline` 是不透明变体，溶解代码被编译排除。发色材质必须用 `Hidden/lilToonCutoutOutline`（LIL_RENDER=1）。
- **表达式参数默认值残留**：`发色菜单` 曾默认=7（旧位编码 1,1,1 产物），需改为 0；位编码参数随旧层退役后从资产删除（省 3 同步槽）。Midnight 同样处理过。
- **AAO 移除未使用对象 vs MA 合并源**：激活动画若只存在于 MA MergeAnimator 源里，AAO 的 removeUnusedObjects 分析看不到 → 默认隐藏的 LowPonytail 整组被当死物体删除。修复：PC+Midnight 头像关掉 TraceAndOptimize.removeUnusedObjects；同时每个头发渲染器有常驻 m_IsActive 关键帧防止 mesh 合并。
- **孤儿过渡（历史残留）**：旧 LapFX 控制器各含 335 条 `m_DstState` 指向已删除状态的过渡，会让遍历过渡的编辑器工具在 Play 模式中断（Animator 控制器变 null）。PC 已清理；Midnight 移植时扫描为 0（用户清理时已顺带解决）。
- **0 帧动画采样问题**：衣服/摸头等单帧 clip 经 duration=0 的 AnyState 转换进入状态时，首帧可能不被采样。修复：所有相关 clip 补齐 2 帧（t=0 和 t=1/60 同值）。
- **脚本创建的材质属性绑定在 Animation 窗口显示 (缺失！)**：不影响运行时。手动重录方法见旧版本记录。
- **AnimatorControllerLayer 是 struct**：`ctrl.layers[i].x = ...` 改的是副本，必须 `var l = ctrl.layers; l[i].x=...; ctrl.layers = l;`。
- **状态机克隆（移植 Midnight 时）**：AnimatorController 无层拷贝 API，需程序化克隆状态/过渡/条件/行为；StateMachineBehaviour 的 List 字段要 MemberwiseClone 深拷贝，否则两控制器共享引用。
- **出生时 Sensor 默认态触发一次** → 出生自带一次发色渐入（当作生成特效）
- 快速连续换色：trigger 残留导致透明期变长，但每次交换重读最新发色菜单值，落点正确
- 未验证项：实际游戏内溶解视觉效果（需上传 VRChat 实测）
- **替身 mesh 引用失效（2026-08-19，Midnight `HairPony_Crossfade`）**：移植替身时 `SkinnedMeshRenderer.m_Mesh` 指向已删除 GUID（`2dd8ed6f…`，`GUIDToAssetPath` 返回空），`sharedMesh=null`。症状：Cross 阶段替身不渲染 → 旧发溶出露光头 → Promote 新色瞬现（假"瞬间切换"）。控制器/动画/材质全部共享且等价，唯一差异在场景替身 mesh 引用 —— 所以「两者用同一组动画和材质」不能排除场景层差异。排查：逐替身验证 `sharedMesh != null`（其余 3 个 LowPonytail 替身、Clothes_Crossfade 12 渲染器均正常，仅 HairPony 坏）。修复：`m_Mesh` 改回真身同款 BakedMesh（`{fileID:4300000, guid:25b2ce0173cf3a046b4efd62a4749621}` = `HairPony(Clone).asset`）。
- **trigger 是 VRChat 本地信号，远程不溶解（2026-08-19，用户 VRChat 实测修复）**：溶解门禁 `HairFadeTrigger`/`ClothesFadeTrigger` 原本是 Unity Animator Trigger（type 9）——VRChat expression parameters 只有 Int/Float/Bool、**没有 Trigger 类型**，trigger 是瞬态信号只在本地消费，远程/mirror 副本收不到 → 远程「完全没动静」（本地正常；PC 旧衣服系统用 synced Bool 直驱所以远程正常）。修复：① 控制器参数 Trigger(9)→Bool(4)；② expression params 加同名 Bool + `networkSynced=1`；③ Sensor 层 Parameter Driver 置 true；④ Action 过渡条件用 `==true`（`If` 模式）；⑤ **Swap（链条首态）加 Parameter Driver 复位 false**。关键：复位必须放**首态 Swap**，不能放尾态 Promote——bool 在 Cross 0.4s 期间仍为 true 会让 `AnyState→Swap` 持续重入打断 Cross，造成 Swap↔Cross 高速闪烁。4 控制器（FX+场景预览 × PC/Midnight）全改。

## 回档

git 分支 `hair-dissolve-hub`，基线 `2fa2e05a`（main）。关键检查点：`a8e26dbf`（首版）→ `115d41b5`（cutout/默认值/AAO）→ `386d6c64`（孤儿过渡+Hub 并入）→ `9b94d690`（坐标模式 z 规则+x/y/w）→ `a0ef883c`（单前沿镜像 0.4s）→ `6e22eab7`（Midnight 移植）→ `0a764338`（测试后场景存档）。全部回滚：`git checkout main` 或 `git reset --hard 2fa2e05a`（先关 Unity）。

## Related

- [[lapwing-min-avatar-project|Lapwing-min Avatar Project]]
- [[unity-mcp-avatar-introspection|Unity MCP Avatar Introspection]]
- [[index|Wiki Index]]
