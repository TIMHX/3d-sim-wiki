---
title: Unity MCP Avatar Introspection
created: 2026-08-16
updated: 2026-08-16
type: concept
tags: [unity, vrchat, workflow, asset-management]
sources: []
confidence: high
---

# Unity MCP Avatar Introspection（用 Unity MCP 摸清 VRChat 项目结构）

用 Unity MCP 工具链对 VRChat avatar 项目做结构探查的可复用工作流。实战案例：[[lapwing-min-avatar-project|Lapwing-min Avatar Project]]。

## 工具选择

| 需求 | 工具 | 要点 |
|---|---|---|
| 列资产 | `assets-find` | filter 支持 `t:Prefab`/`t:AnimationClip` 等类型关键字；**AnimatorController 不在类型列表**，用 `glob:"*.controller"` |
| 读动画器 | `animator-get-data` | 大型控制器（LapFX 400+ 参数）会超 token 上限 → 结果存文件后 grep 提取 |
| 场景结构 | `scene-get-data` | `includeChildrenDepth:1` 拿根对象+直接子级即可定位所有 avatar 根 |
| 场景对象组件 | `gameobject-find` | `includeComponents:true` 看根上有哪些组件（Animator/VRCAvatarDescriptor/MA/AvatarOptimizer） |
| 任意逻辑读取 | `script-execute` | **主力工具**——Roslyn 动态编译 C#，可遍历场景、反射任意类型、枚举组件 |

## 大结果文件处理

`animator-get-data`/`assets-find` 超限时结果存到 `tool-results/*.txt`。无 jq 时用 grep 提取：
- 参数列表：`grep -oE '\{"name":"[^"]*","type":"[^"]*"' file | sort -u`
- 层名：`grep -oE '\{"name":"[^"]*","defaultWeight"' file`
- 按目录统计 clips：`grep -o '"assetPath":"[^"]*"' file | sed ... | sort | uniq -c`

## script-execute 反射模式（关键 API 坑）

1. **`VRCAvatarDescriptor` 的 `baseAnimLayers`/`specialAnimLayers` 不是属性** —— VRChat base SDK（com.vrchat.avatars）3.8+ 里它们是**字段**（还有 `expressionsMenu`、`expressionParameters`、`customExpressions`、`customizeAnimationLayers`）。`GetProperty()` 返回 null，必须 `GetField(...)`。SDK 3.8 之前叫 `baseAnimLayers`（属性）。
2. **组件字段枚举**：`GetFields(BindingFlags.Public|NonPublic|Instance|DeclaredOnly)` 沿 `BaseType` 链上溯到 MonoBehaviour，能定位任意版本 SDK 的成员名。
3. **MA 组件枚举**：`root.GetComponentsInChildren<ModularAvatarMergeAnimator>(true)` / `ModularAvatarMenuInstaller` / `ModularAvatarParameters`，读 `m.animator`→`AssetDatabase.GetAssetPath` 拿控制器路径；MenuInstaller 的 `menuToAppend == null` 表示安装到 avatar 根菜单。
4. **VRCFury 组件**：`GetComponentsInChildren<MonoBehaviour>(true)` 后按 `GetType().Namespace.StartsWith("VF")` 过滤。
5. **参数资产**：`AssetDatabase.LoadAssetAtPath` + 反射读 `parameters` 字段（name/valueType/saved/defaultValue）。
6. `gameobject-component-get` 的 `paths` 模式对未解析类型返回 `<unresolved>`，复杂类型改走 script-execute。

## 结构探查顺序（推荐）

1. `assets-find t:Prefab` + `glob:"*.controller"` + `scene-list-opened` —— 建立资产/控制器/场景地图
2. `scene-get-data`（depth 1）—— 定位全部 avatar 根（注意 `activeSelf:false` 的 Quest/备选版）
3. `gameobject-find` 根对象 —— 确认 Animator/Descriptor/优化组件
4. script-execute 反射 descriptor —— 拿到 playable layers / menu / params 实指路径
5. 逐控制器 `animator-get-data`（大的走文件+grep）—— 参数与层结构
6. script-execute 枚举 MA/VRCFury 组件 + 读参数资产尾部 —— 菜单/参数的构建期来源

## 判读要点（MA/NDMF 项目）

- 场景里 descriptor 的 menu/params **为空或占位**是正常的 —— 最终值由 MA MenuInstaller/MenuItem/Parameters 在 NDMF 构建期合并
- 场景 Animator 控制器 ≠ playable layers；以 descriptor 的 `baseAnimationLayers`/`specialAnimationLayers` 为准
- GoLoco/ABT 等插件的 Proxy 控制器（ProxyBase/ProxyAction/ProxySitting）会在构建时被 MA 替换为真实控制器

## Related

- [[lapwing-min-avatar-project|Lapwing-min Avatar Project]]
- [[index|Wiki Index]]
