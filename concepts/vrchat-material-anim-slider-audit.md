---
title: VRChat 材质动画滑杆无效的审计（AudioLink 强度 / 发光 / 主题色）
created: 2026-11-24
updated: 2026-11-24
type: troubleshooting
tags: [unity, vrchat, vrchat-avatar, liltoon, poiyomi, audiolink, performance]
sources: []
confidence: high
---

# VRChat 材质动画滑杆无效的审计

背景：Lapwing（[[lapwing-min-avatar-project]]）的 Glow & Color 菜单（主题色 / 发光亮度 / AudioLink 强度）在 PC 衣服上「只有淡淡的光、滑杆没用」。逐个猜改不动，全量审计后一次找出全部原因。

## 症状 → 根因

| 症状 | 根因 | 修法 |
|---|---|---|
| 拨滑杆毫无变化 | PC/Quest 共用一份动画，PC 部件上只写了 Toon Standard 的属性（`_ALIntensity`、`_RimIntensity`），lilToon 没有 | 给本平台加一条真正存在的属性绑定 |
| 属性名对但没变化 | 名字写错（Poi 描边色相是 `_OutlineHue`，写成了 `_OutlineHueOffset`） | 改名 + Poi 标 Animated 重锁 |
| 默认值以上没变化 | 写的量会封顶：`_Emission2ndBlend`、Poi decal alpha（saturate） | 改写不封顶的量：lilToon `_Color3rd.a` / `_Emission2ndColor.a` / `_RimColor.a`（不截断的 lerp，>1 即放大）；Poi decal 用 `_AudioLinkDecalNEmission` |
| 某个光整个灭了 | 颜色动画只写 rgb，alpha 变 0（lilToon `_RimColor.a` 是强度；Legacy Additive 粒子 `_TintColor.a` 决定可见） | 补 alpha 曲线 |
| Poi 上 HasProperty 为真仍无效 | 锁定时没标 Animated，被编译成常量 | 查锁定 `.shader` 里有没有 `half _属性;`，没有就解锁→标 `<属性>Animated`→重锁 |
| 烘焙头像某部件颜色不对 / 变白 | 合并渲染器：材质动画写整个渲染器，眼睛、纹身、翅膀共用 `_Emission2ndColor` 互相覆盖 | 部件改用没人用的功能层（lilToon Main3rd 加法 + 不受光）；固定色部件用 `_Emission2ndBlendMask` 小 EXR 预乘原色 |

**gamma 陷阱**：动画写颜色属性时 Unity 做 gamma→线性转换，HDR 值也一样（曲线 8 = 线性 97）；alpha 不转换。做预乘遮罩要用线性值。

## 审计脚本要点

收集头像所有写材质的动画（FX、VRCFury、各 MA MergeAnimator，注意 pathMode 决定路径基准）→ 绑定解析到渲染器 → 对每条检查：属性是否存在、rgb 是否缺 alpha、开了 AudioLink 的材质有没有有效强度绑定、Poi 锁定后是不是变量。

## 验证手法

- 离线满节拍：全局 `_AudioTexture` 设成 128×64 全白线性贴图，lilToon/Poi 都按「AudioLink 在且全满」渲染。
- `AnimationMode.SampleAnimationClip` 对部分渲染器不生效 → 关键结论用手动 `SetPropertyBlock` 再确认。
- 判断画面属于哪个材质槽：把槽换成 null（渲成洋红）或开关渲染器做像素差分。**下结论前必须做**——这次曾把「上衣波纹贴图本身」误判成「皮肤穿出衣服」。

## 附：原生面捕转发参数压线冲 Good 评级

PC Good 档转发参数上限 20，Hash 原生面捕套件是 21。挑一个只线性驱动单个形状、没被其它门引用的参数（LipPucker），把 behavior 改成 `ApplyToBlendshape`（不计入转发数），表达式按原阈值缩放 `clamp(x/0.8,0,1)`；再给该头像复制一份 FTOnly 删掉那条混合树。验证：`FaceTrackingMappingValidator` 0 问题、NDMF 克隆构建后形状仍在、编辑器算评级。
