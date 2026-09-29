---
title: Lapwing-min Avatar Project (VRChat)
created: 2026-08-16
updated: 2026-09-29
type: summary
tags: [unity, vrchat, vrchat-avatar, asset-management]
sources: []
confidence: high
---

# Lapwing-min Avatar Project (VRChat)

Unity VRChat avatar 项目，本地路径 `E:\ALCOM_save\Lapwing-min`，主场景 `Assets/lapwing_scene.unity`。全部通过 Unity MCP 探查（方法见 [[unity-mcp-avatar-introspection]]）。

## 场景与 4 个 Avatars

场景根对象：4 个 avatar + Main Camera / Directional Light / FaceEmo / GestureManager / NDMF Activator。

| Avatar 根对象 | 激活 | 平台 | 场景 Animator 控制器 | 参数资产 |
|---|---|---|---|---|
| `LapwingBody FT` | ✅ | PC | `Assets/动画/LapwingBody FT.controller` | `LapExpressionParameters FT.asset` (180) |
| `LapwingBody FT Copy (Android)` | ❌ | Quest | `Assets/动画/LapwingBody FT min.controller` | `LapExpressionParameters FT min.asset` (172) |
| `LapwingBody FT Midnight` | ❌ | PC | `Assets/动画/Midnight/Lapwing Midnight.controller` | `Midnight/Midnight.asset` (178) |
| `LapwingBody FT Midnigh min (Android)` | ❌ | Quest | `Assets/动画/Midnight/Lapwing Midnight Min.controller` | `Midnight/Midnight_min.asset` (175) |

参数资产位于 `Assets/素体/Hash's_Things/Lapwing/menu&parameters/`。

## Playable Layers（VRCAvatarDescriptor）

4 个 avatar 共享同一骨架，只有 FX 层各自专属：

| 层 | 类型 | 控制器 |
|---|---|---|
| Base | Base | GoLoco `ProxyBase.controller`（MA 构建时替换为 GoLocoBaseWD） |
| Additive | Additive | `LapIdleLayer FT.controller`（眼球追踪 + OSCmooth Local/Remote 平滑 + Upright Idle） |
| Gesture | Gesture | `LapGesture.controller`（左右手各 8 手势：Fist/Open/Point/Peace/RockNRoll/Gun/ThumbsUp，参数 GestureLeft/Right） |
| Action | Action | GoLoco `ProxyAction.controller` |
| FX | FX | 各自专属（见下表） |
| Sitting | Sitting | GoLoco `ProxySitting.controller` |
| TPose | TPose | 默认 |
| IKPose | IKPose | `LapIKPose.controller` |

FX 层：`LapFX FT.controller`（PC）/ `LapFX FT min.controller`（Quest）/ `LapFX FT Midnight.controller`（PC）/ `LapFX FT Midnight Min.controller`（Quest），均位于 `Assets/素体/Hash's_Things/Lapwing/anim/controllers/` 或 `Assets/动画/Midnight/`。

## FX 层结构（LapFX）

参数 400+，三类：
- `FT/v2/*` — 面部追踪 blendshape 通道（44 个，如 BrowExpressionLeft/CheekPuffSuckLeft/EyeLidLeft/JawOpen/MouthX/TongueOut）
- `OSCm/Binary/{1,2,4,8,Negative}/*` — OSCmooth 二进制位编码参数（每通道 3~5 位），加 `OSCm/Local|Remote|Proxy(/Smooth)/FT/v2/*` 平滑/代理副本
- 菜单参数：`Expression`(Int)/`Expression_1~4`、`衣服菜单`/`发色菜单`(Int)+`_N` 位 Bool、`瞳色菜单`、`摸头`、`FTOn/FTOff/FTEffects`、`IsLocal`、`Viseme`、`Seated`

层结构（60+ 层）：Eye Tracking State → Visemes State → Face Tracking Blendtree → `_OSCmooth_Gen`（IsLocal 切换 Local/Remote 平滑器）→ **40 个 `_OSCm_FT/v2/*_Encode` 位编码层** → 功能层（FTOn/AllParts/DefaultFace/Left Hand/Right Hand/Expressions/LipSync/衣服菜单/发色菜单/Expression_Local/Expression_Remote/衣服菜单_Local/Remote/发色菜单_Local/Remote/摸头）。

## 菜单系统（MA 构建期生成）

关键点：场景内 descriptor 的 `expressionsMenu`（指向 `LapExpressionsMenu FT_empty.asset` 空菜单）和 `expressionParameters` 不是最终值 —— **菜单和参数在 NDMF 构建时由 Modular Avatar 合并生成**。

`Avatar Menu` 子物体树（MA MenuItem）：
- `Face&Gest`（SubMenu）→ Expressions / FT / ChangeDefaultFace(TwoAxisPuppet) / DisableGestureExControl(Toggle→GestureControlDisabled)
- `Cloths&Items`（SubMenu）→ Items / Cloths / Hair Color / Iris

每个配件 prefab 自带 MA MenuInstaller + MA MergeAnimator(FX) + MA Parameters，如：音波发卡(`kZHairVolFX.controller`)、CatMount、幽灵猫猫、StoZeroCustomEX(StoZero/StoZeroEX/CommonControll 三个控制器)、GogoLoco All(Base/Action/Sitting + GoAllMainMenu)。

## 部件层级（每个 avatar 根下）

- `Armature` / `Body` / `Body2`（体色变体 SkinnedMeshRenderer，无 Animator）/ `Sox`(EditorOnly) / `Underwear`
- `头发`：HairPony（激活）、LowPonytail_A_Lapwing（停用）
- `服装`：LapwingOriginal（激活）、Jacket、Demon、Heather（各有材质切换动画）
- `物品`：music_strap、音波发卡、CatMount、幽灵猫猫、StoZeroCustomEX、Maru_Glasses
- `插件`：GogoLoco All (Modular Avatar)

主 avatar 变换数：PC ~1008，Midnight ~1268，Quest 版 ~315/~465。

## 自定义动画

`Assets/动画/*.anim`：Jacket/Demon/Cape/hairPony/hairLowPony/Heather_1(×4)/Heather_2(×2)/Heather_knit(×2)/Touch_Head/Default_原始材质（PC+min 两套）。
`Assets/动画/Midnight/*.anim`：Black/BlackWhite/Brown/GreenWhite/Touch_Head/Default_原始材质 Midnight min。

场景自身控制器（`LapwingBody FT.controller` 等）为单层「材质菜单」控制器：状态 = Default/Jacket/Demon/Cape/hairPony/hairLowPony/Heather_x/Touch Head/原始材质，参数 = 头发菜单/瞳色菜单(Int)+位 Bool。注意 `Assets/动画/Body2.controller` 为空控制器（无参数无状态，疑似未使用）。

## Midnight 衣服溶解（2026-08-18）

Midnight 的 4 套衣服（BlackWhite/GreenWhite/Black/Brown）合并为单网格 + 材质切换 + 单前沿交叉溶解（复用发色 Hub），详见 [[lapwing-clothes-dissolve|Lapwing 衣服溶解]]。相关：删 3 套 prefab、建替身 `服装/Clothes_Crossfade`（共享骨架）、`Assets/动画/Midnight/Clothes/` 12 个 clip、`LapFX FT Midnight.controller` + `Lapwing Midnight.controller` 各加 Sensor_Clothes/Action_Clothes 两层。

## PullPop 拉动骨换衣（2026-09-08）

`LapwingBody FT Midnight` 上装了 NyaPPu PullPop 1.1.0（`PullPop (Cloud)` 预设），拉胸前动骨 `Pullpop`
循环切换 `衣服菜单`（Int 0~3，Forward 模式）并播放 pop 音效 + cloud 粒子。
构建期生成 `PullPop/Gimmick (衣服菜单)`（L60）和 `PullPop/Effect (衣服菜单)`（L61）两层并入 FX。

粒子只在第一次拉动时出现的根因与修复、以及 PhysBone 自然拉动配方，见
[[pullpop-cloud-particle-retrigger|PullPop 云粒子只触发一次]]。

## Quest 版 combine min (Android)：雨衣 × B 袖 + 夜店风材质（2026-09-28）

- Quest 只能用 `VRChat/Mobile/*`，Toon Standard 写死不透明 → PC 版「透明雨衣透出袖子」不可移植，改为几何方案：
  新对象 `Lapwing_B_Raincoat`（B 袖网格副本：肘以上收缩到 20% 并删深部、喇叭口下垂侧压到 0.65、接缝法线迁移自雨衣），由雨衣的 MA ObjectToggle 与原 B 互斥切换。
- 验证手段：NDMF 克隆构建探针；不构建克隆上同步旋转所有 armature 的 `LowerArm_L` 做弯肘；射线露出指标（需 `queriesHitBackfaces`，命中=露出）。坑：弯曲方向写反、硬删面出锯齿、过渡卡在关节。
- 材质：hair 系 matcap（sweetd1saster pack）对深色衣物用加法 0.35–0.6，fabric 系加法会洗白；Toon Standard rim 不受光照影响 → 霓虹描边；MinBrightness 0.03。发色菜单会覆盖头发材质（原全是 Toon Lit）。
- 调过的资产存档在 `Assets/QuestTuned/LapwingBody FT combine min/`（MoveAsset 保 GUID，附 README）。完整规格在项目 skill `lapwing-hair-dissolve` 第 11 节。
- Unity MCP 插件未注册时可 HTTP 直连 `127.0.0.1:8080/mcp`（streamable HTTP + mcp-session-id）。

## Quest 版三头像统一 + 10MB 下载墙（2026-09-29）

- 头发：Midnight min (Android) 收入 HairPony / LowPonytail（带 PB）/ LpwPony，发色菜单每项 = MA ObjectToggle（切发型）+ MaterialSetter（切色），无动画层。主头发：combine=HairPony、Copy=LowPonytail，其余头发 PB 删除（Quest PB ≤ 8）。
- 眼睛"游戏里很暗"：Toon Lit 在暗光被压黑、Toon Standard 皮肤不会 → 眼睛/瞳色原地转 Toon Standard + `_EmissionMap`=主贴图 0.35。
- Cyber = 照搬 PC Midnight：关 outer×4/armbadge/belt、开雨衣。⚠️ 用户在 PC 版手调的是**雨衣骨架**（Chest/UpperArm/Hood/Visor 等 8 根）+ `Hood_Deform` 形态键 → 复刻衣服要逐骨 diff 拷贝，不能只对齐根物体。帽子 Visor 随雨衣一并搬（+1 PB）。
- 减面：lilNDMFMeshSimplifier 组件（构建时生效，原 FBX 不动）；细饰边要开 PreserveBorderEdges/UVSeam。⚠️ 反射烘焙出的网格在编辑器 SMR 上渲染不出，验证只看 NDMF 构建克隆。
- 下载体积：⚠️ **贴图才是杠杆**——网格原始 23.6MB 但 LZMA 压到约 1/5，ASTC 贴图几乎压不动。Avatar Compressor 预设 HighQuality→Quality：贴图 6.9→2.3MB（HighQuality 会跳过所有 512 图）；嫌糊的个别贴图用 `FrozenTextures` 单独冻结（Divisor 相对源图，1024 源要 512 设 2），inner 冻结后合计 2.89MB。原生 Iris 用 MaterialSetter 替代 MaterialSwap 以免 From 材质进包。
- 精确体积探针：NDMF 克隆构建 → `EditorUtility.CollectDependencies` → 按 `Texture2D.format` 的 ASTC 块大小逐 mip 计算（`VRCExpressions* Icon.png` 是编辑器图标误报）。
- 细节与脚本在项目 skill `lapwing-hair-dissolve` 第 12–12.12 节；资产存档 `Assets/QuestTuned/<avatar>/README.md`。

## Assets 目录（顶层）

`素体`(Lapwing 身体/衣服/头发/鞋/包 prefab + Hash's_Things FT 变体)、`衣服`(Heather Jacket_Type1/2/OFF × 8 角色、midnightschool 10 色、天使恶魔、oathjacket)、`头发`(long straight hair、Lapwing长发 LowPonytail A/B)、`配件`(AlcoholSet/BlackCatMount/Glitch/STELLA MaruChainGlasses/strongzero StoZero/世界轴/吊坠眼镜/幽灵猫猫/音量发卡)、`妆容`(451 文件)、`动画`、`插件`(ABT/GoGo/GoLoco/MeshDeleterWithTexture/参数压缩器)、`VRCQuestToolsOutput`、根目录 `prefab-id-v1_avtr_*.prefab`（已上传 avatar 副本）。

## 技术栈

Modular Avatar + NDMF + VRCFury（`Packages/com.vrcfury.temp/Builds/` 有 Lapwing_Midnight 构建记录）+ AvatarOptimizer（根上 TextureCompressor/TraceAndOptimize）+ OSCmooth + FaceEmo + GestureManager + liltoon + AudioLink + GoGo/GoLoco + ABT。

## Unity API 注意

VRChat base SDK（com.vrchat.avatars）3.8+：`VRCAvatarDescriptor` 的图层/菜单/参数是**字段**（`baseAnimationLayers`、`specialAnimationLayers`、`expressionsMenu`、`expressionParameters`），不是属性 —— 反射读取时 `GetProperty` 返回 null，必须用 `GetField`。

## Related

- [[unity-mcp-avatar-introspection|Unity MCP Avatar Introspection]]
- [[pullpop-cloud-particle-retrigger|PullPop 云粒子只触发一次]]
- [[index|Wiki Index]]
