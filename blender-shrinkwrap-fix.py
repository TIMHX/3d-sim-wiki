# ===== 施工场景路径贴合脚本 =====
# 粘贴到 Blender Scripting 工作区 → 点上方 Run Script 按钮（▶️）

import bpy

# ----- 1. 确保所有路径物体有足够的顶点 -----
for path_name in ['DirtPath', 'ConcretePath_H', 'ConcretePath_V']:
    obj = bpy.data.objects.get(path_name)
    if obj is None:
        print(f"⚠️  没找到 {path_name}，跳过")
        continue

    # 选中物体
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)

    # 进入编辑模式 → 细分
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=20)
    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"✅ {path_name} 已细分（20 次切割）")

# ----- 2. 加/更新 Shrinkwrap 修改器 -----
target = bpy.data.objects.get('BaseGround')
if target is None:
    print("❌ 找不到 BaseGround！请确认场景里有名为 BaseGround 的物体")
else:
    for path_name in ['DirtPath', 'ConcretePath_H', 'ConcretePath_V']:
        obj = bpy.data.objects.get(path_name)
        if obj is None:
            continue

        # 检查是否已有 Shrinkwrap
        mod = obj.modifiers.get('Shrinkwrap')
        if mod is None:
            mod = obj.modifiers.new(name='Shrinkwrap', type='SHRINKWRAP')

        mod.target = target
        mod.wrap_method = 'PROJECT'
        mod.wrap_mode = 'ON_SURFACE'
        mod.use_project_x = False
        mod.use_project_y = False
        mod.use_project_z = True   # 从上往下投影
        mod.use_negative_direction = False
        mod.use_positive_direction = True
        mod.offset = 0.02          # 高出地面 2cm
        mod.cull_face = 'OFF'
        print(f"✅ {path_name} Shrinkwrap 已配置：Z 轴投影 → BaseGround，Offset=0.02m")

print("\n===== 完成 =====")
print("旋转视角看路径是否贴合地形。如不贴合，按 Numpad 1 前视图截图发我。")
