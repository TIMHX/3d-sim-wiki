---
title: PullPop 云粒子只触发一次
created: 2026-09-08
updated: 2026-09-08
type: troubleshooting
tags: [unity, vrchat, troubleshooting, workflow, vrchat-avatar]
sources: []
confidence: high
---

# PullPop 云粒子只触发一次（Write Defaults 不复位 m_IsActive）

NyaPPu PullPop 1.1.0 装在 `LapwingBody FT Midnight`（[[lapwing-min-avatar-project|Lapwing-min]]，Unity 2022.3.22f1）上，
拉动骨可以反复切换衣服菜单，但 cloud 粒子**只在第一次拉动时出现**，之后再拉毫无反应。
诊断全程通过 Unity MCP 完成，方法见 [[unity-mcp-avatar-introspection|Unity MCP Avatar Introspection]]。

## 结论（根因）

**PullPop 的效果复位 100% 依赖 Write Defaults，而 WD 在这个 avatar 上不会复位 `m_IsActive`。**

插件的 `Effect.anim` 只做一件事：把 `Target/ParticleTrigger` 的 `m_IsActive` 写成 1（单关键帧，`clip.length == 0`）。
`AnimationHelper.AddState()` 建的 Idle 状态**没有任何 motion**，靠 Unity 默认的 `writeDefaultValues = true` 把物体写回 0。
实测这一步不发生 → 物体第一次被打开后永远保持 active → `playOnAwake` 不再触发 → 粒子不重播。

衣服菜单每次都能换，是因为那条路走的是 **VRC Parameter Driver**（进状态执行一次），不依赖动画复位 —— 这正是两者表现不同的原因。

### 决定性证据（时间线采样，3 个拉→松循环）

```
拉 1  13.0s  st=0.43  eff=EFFECT  ptActive=0→1  ptCount=1  buf=0→1   ← 云出现
松 1  14.7s  st=0.05  eff=Idle    ptActive=1                          ← 没复位
拉 2  18.1s  st=0.46  eff=EFFECT  ptActive=1    ptCount=1  buf=1      ← 全程无变化
松 2  21.4s  st=0.02  eff=Idle    ptActive=1
拉 3  25.2s  st=0.44  eff=EFFECT  ptActive=1    ptCount=1  buf=1
松 3  28.2s  st=0.02  eff=Idle    ptActive=1
```

状态机三轮全部正常（`Idle ↔ EFFECT`），Stretch 正常爬升回落，`ptCount`/`buf` 纹丝不动。

## 修复

不改插件代码、不加动画层、不加物体，只利用组件自带的 `Effect Clip` 字段（插件的官方扩展点）：

1. 复制 `Assets/插件/NyaPPu/PullPop/Assets/Effect.anim` → `Assets/动画/PullPop Effect (Cloud).anim`
2. 补一个关闭关键帧，让它变成 0.2 秒的开→关脉冲：

```
t=0.0   Target/ParticleTrigger  m_IsActive = 1
t=0.2   Target/ParticleTrigger  m_IsActive = 0
```

3. 填进 `PullPop` 组件 `physBoneSettings[0].effectClip`

关键帧切线用 `Infinity`（常量），clip 的 `LoopTime` 保持关闭 → 播完停在 0，状态停留多久都无所谓。
音效走 state 上的 `VRCAnimatorPlayAudio`（进状态触发），不受影响。放在自己目录下，插件更新不会被覆盖。

> **状态：已验证成功（2026-09-08）。** NDMF 构建检查通过（`motion='PullPop Effect (Cloud)' len=0.2`，
> 路径正确重定向为 `Armature/Hips/Target/ParticleTrigger`，构建后初始 `activeSelf=False`），
> 用户在 Gesture Manager Play 模式下连续拉动，云粒子每次都正常出现。

## 最大的坑：Play 模式改场景物体会泄漏成 prefab override

调试期间在 Play 模式里用脚本 `SetActive(true)` 了场景中的 `ParticleTrigger`，
退出 Play 后这个改动**留在了场景里，变成 prefab instance 的 `m_IsActive: 1` override**
（磁盘上的 `.unity` 文件里没有该 override，纯内存脏数据）。

后果极其隐蔽：下一次 NDMF 构建时该物体是 active 的 → Animator 绑定时捕获的 WD 默认值变成 `true`
→ Idle 状态每帧把它按成开着 → 观测到"WD 主动写 true"这种假象，直接导致一次错误定性。

**教训：**
- 诊断阶段在 Play 模式里只做**只读**观测，绝不 `SetActive` / 改组件字段
- 怀疑场景被污染时，用 `PrefabUtility.GetPropertyModifications` 查 override，
  并 grep 磁盘上的 `.unity` 文件确认 override 是否真的存在于已保存状态
- 撤销用 `PrefabUtility.RevertPropertyOverride(serializedProperty, InteractionMode.AutomatedAction)`，只回滚单个属性

## Gesture Manager 下读实时动画状态

**`Animator.GetLayerName` / `GetCurrentAnimatorStateInfo` 拿不到 FX 层** —— GM 用 PlayableGraph 驱动，
avatar 上 `Animator.runtimeAnimatorController == null`、`layerCount` 只有 base playable 的 4~5 层。
必须反射：

```
GestureManager (MonoBehaviour) .Module            → ModuleVrc3
ModuleVrc3._layers  : Dictionary<AnimLayerType, LayerData>   // key "FX"
LayerData.Playable  : AnimatorControllerPlayable             // ← 真正的 FX 层
LayerData.Parameters, LayerData.Weight, LayerData.Empty
ModuleVrc3.Params   : Dictionary<string, Vrc3Param>          // 487 个参数
Vrc3Param.FloatValue() / IntValue() / BoolValue()            // 是方法不是属性
```

`AnimatorControllerPlayable` 上有 `GetLayerCount/GetLayerName/GetCurrentAnimatorStateInfo/IsInTransition`，
但**没有** `GetAnimatorControllerParameterCount`。

## 可复用：只读时间线采样器

一问一答式的分步读取需要大量往返。改用 `EditorApplication.update` 回调 + `SessionState` 缓冲，
一次装载、用户自由操作、最后一次性取回完整时间线：

- 采样前把参数/Playable/Transform 全部解析成局部变量捕获进闭包，回调里不再做查找
- 只在关键值变化时追加一行，避免刷屏
- 回调里 `try/catch`，超时（如 45s）自我 `-=` 卸载 —— 动态编译的程序集被卸载后回调会失效，必须自限
- 域重载（进入 Play 模式）会清空订阅，所以**必须在进入 Play 模式之后**再装

## 无损构建探针

不进 Play 模式就能看构建后的动画器：

```
clone = Instantiate(avatarRoot);
nadena.dev.ndmf.AvatarProcessor.ProcessAvatar(clone);
// 读 clone 的 VRCAvatarDescriptor.baseAnimationLayers → AnimatorController
// 读完 DestroyImmediate(clone)，try/finally 保证清理
```

用它确认过：Effect 层两个 state 的 `writeDefaultValues` 都是 `True`（`MergeAnimator.matchAvatarWriteDefaults=true`，
宿主 FX `LapFX FT Midnight` 84 层、WD 368 on / 142 off），
以及 clip 路径被 NDMF 从 `Target/ParticleTrigger` 正确重定向为 `Armature/Hips/Target/ParticleTrigger`
（`Target` 被 MA Bone Proxy 挪到了 Hips 下）。

## PullPop 生成的状态机结构

`Generator.Generate()` 每个 PullPop 组件产出一个独立 controller，经 MA MergeAnimator 并入 FX：

| 层 | 状态 | 说明 |
|---|---|---|
| `PullPop/Gimmick (<参数名>)` | Idle + 每个值一个状态 | 状态上挂 `VRCAvatarParameterDriver`，无 motion |
| `PullPop/Effect (<参数名>)` | Idle + `Effect (<PBname>)` | Effect 状态挂 `effectClip` + `VRCAnimatorPlayAudio` |

进入条件（`ActivateCondition.Stretch`）：`<PB>_IsGrabbed == true && <PB>_Stretch > threshold && <toggleParam> == true`
退出条件：`<PB>_Stretch < threshold - 0.05`
Gimmick 层额外要求 `IsLocal`；Effect 层不要求（所以远程也能看到特效）。

构建期插件会**直接改写 PhysBone 组件**：`parameter` 为空则填 `PullPopPB_<i>_<j>`；
`maxStretch <= 0` 改成 1；`radius <= 0` 改成 0.01；`autoFixCollision` 时把
`radiusCurve` 设成 `Linear(0.999→0, 1→1)`，即**只有骨链末端有碰撞半径**，中间骨节不会蹭到身体。

## 粒子链结构（Cloud 预设）

```
Target/ParticleTrigger   playOnAwake=1  loop=0  duration=1  lifetime=1000  burst  maxParticles=100
   └ subEmitter(Birth) → Buffer Particle   simSpace=World  playOnAwake=0  lifetime=1000
        └ subEmitter(Birth) → Cloud        simSpace=Local  lifetime=0.5   ← 可见的云
```

整条链靠 `ParticleTrigger` 这个 GameObject 的**激活边沿**驱动，所以"关→开"必须真实发生。
`Buffer Particle` 的粒子寿命 1000 秒，粒子数只增不减，是判断"这一轮到底有没有发射"的最佳指标。
已实测：手动 `SetActive(false)` → `SetActive(true)` 两轮都能正常重播（buf 4→5），**粒子系统本身没有问题**。

## PhysBone：让拉动自然

原始配置（自建，很粗糙）：

```
Pullpop 挂在 avatar 根节点（不是骨骼）    子物体：0 个（或只有 Contact 物体）
pull=1  spring=1  stiffness=0.2  grabMovement=0.5
maxStretch=0  limitType=None  allowGrabbing=Other  allowPosing=False  multiChildType=Ignore
```

三个硬伤：

1. **没有骨链**。PhysBone 靠子 Transform 组成链条才有物理感；根节点下没有子物体等于几乎不动。
   插件原本演示拉头发之所以自然，是因为头发本身有好几节骨。
2. **把 ContactSender/Receiver 挂在 PhysBone 根下会被当成骨链子节点**，且 `multiChildType=Ignore`
   遇到多个子物体会直接忽略 —— 反而把链彻底废掉。Contact 要放到链外，或加进 `ignoreTransforms`。
3. 挂在 avatar 根节点不跟随身体；`allowGrabbing=Other` 表示自己抓不到；`grabMovement=0.5` 手感发飘。

改法（挂胸口）：

```
Armature/Hips/Spine/Chest/Pullpop            // 重新父级化时保持世界坐标不变
  └ Pullpop_1 → Pullpop_2 → Pullpop_3        // 每节 localPosition = (0,0,0.03)，共 9cm
allowGrabbing=True  allowPosing=False  grabMovement=0
maxStretch=1  pull=0.2  spring=0.8  stiffness=0.1  radius=0.15
```

`allowPosing=False` 保证松手立刻回弹，Stretch 才能跌破退出阈值、让状态机回到 Idle。

用户实测手感可用，后续按喜好微调 `pull` / `spring` / `stiffness` / 链长即可。

## 其它 API 坑

- `VRCPhysBone` **没有** `isGrabbed` / `stretch` 运行时属性（只有配置字段），实时值要从动画器参数读
- 用 `Resources.FindObjectsOfTypeAll<T>()` 才能拿到 inactive 物体，并用 `gameObject.scene.name != null` 过滤掉资产实例
- 方向判定：PhysBone 暴露的 `_IsGrabbed/_IsPosed/_Angle/_Stretch/_Squish` **都不含方向信息**，
  `_Stretch` 只表示"被拉长了多少"，往哪个方向拉都一样。真要方向判定只能上 Contact，
  但把动骨本身做正经（挂对骨骼 + 真骨链 + 合适参数）通常就够自然了

## Related

- [[lapwing-min-avatar-project|Lapwing-min Avatar Project]]
- [[unity-mcp-avatar-introspection|Unity MCP Avatar Introspection]]
- [[lapwing-clothes-dissolve|Lapwing 衣服溶解]]
- [[index|Wiki Index]]
