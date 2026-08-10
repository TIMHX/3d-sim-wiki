---
title: Navigation Task 设计
created: 2026-08-10
updated: 2026-08-10
type: concept
tags: [isaaclab, navigation, g1, rsl-rl, scene-design]
related: [isaaclab-operation-manual, isaaclab-docker-env]
---

# Navigation Task 设计

G1 双足人形机器人导航任务 (`navigation_Z1-v0`)，基于 Isaac Lab 2.3.0 + Isaac Sim 5.1.0，PPO/RSL-RL 训练。导师项目分支 `GeorgiaTechLIDARGroup/IsaacLab @ 2.3.0/feature/navigation`。

## 文件结构

```
source/isaaclab_tasks/isaaclab_tasks/manager_based/navigation_Z1/
├── bipednavigationcfg.py     # 顶层入口: BipedNavigationEnvPlayCfg
├── __init__.py
├── cfg/
│   ├── scene_cfg.py          # 场景: terrain, robot, object, sensors
│   ├── event_cfg.py          # 重置: start position, joint reset
│   ├── commands_cfg.py       # 导航命令: velocity commands
│   ├── reward_cfg.py         # 奖励: termination_penalty
│   ├── observation_cfg.py    # 观测: pos, vel, forces, elevation
│   ├── termination_cfg.py    # 终止: timeout, bad_orientation
│   ├── terrain_cfg.py        # 地形生成器 (未使用 — 已注释)
│   ├── multi_terrain_cfg.py  # 多地形补丁 (未使用)
│   ├── curriculum_cfg.py     # 课程学习
│   ├── action_cfg.py         # 动作空间
│   ├── robot_config_base.py  # 机器人配置抽象基类
│   └── Enviornment_G1.py     # G1 特定配置
└── mdp/
    ├── events/
    └── observations/
```

## 初始化流程 (`gym.make("navigation_Z1-v0")`)

### 步骤 1-3: 场景加载

1. **Terrain** — 加载 `ENVIRONMENT_USD` (park simulation.usda)，放到 `/World/Environment`，`collision_group=-1`(全局碰撞)
2. **Robot** — 加载 `UNITREE_G1_29DOF_MIMIC_CFG` (unitree.py:1289)，放到 `{ENV_REGEX_NS}/Robot`
3. **Object** — 加载 `armchair_44468` (硬编码在 scene_cfg.py:57)，放到 `(2.1, -0.6)`，90° roll around X

机器人配置通过工厂函数获取:
```
ROBOT_TYPE = "Unitree_G1"
robot_misc_config = get_robot_config(ROBOT_TYPE)  → G1EnvironmentConfig()
ROBOT_CFG = getattr(unitree, robot_misc_config.robot_cfg_name)  → UNITREE_G1_29DOF_MIMIC_CFG
```

### 步骤 4: Sky Light

```python
sky_light = AssetBaseCfg(
    prim_path="/World/skyLight",
    spawn=DomeLightCfg(
        intensity=750.0,
        texture_file=f"{ISAAC_NUCLEUS_DIR}/Materials/Textures/Skies/PolyHaven/kloofendal_43d_clear_puresky_4k.hdr",
    ),
)
```

⚠️ 引用了 `ISAAC_NUCLEUS_DIR` 云端资产路径。容器内可能需要网络访问 NVIDIA Nucleus 服务器。

### 步骤 5: 传感器

| 传感器 | 类型 | Prim 路径 | 参数 |
|--------|------|-----------|------|
| height_scanner | MultiMeshRayCaster | pelvis | 1.6×1.0m grid, 0.1m res, yaw alignment |
| raycaster_elevmap | MultiMeshRayCaster | pelvis | 0.64×0.64m grid, 0.04m res |
| camera | TiledCamera | pelvis/front_cam | 1080×720 RGB-D, focal=24mm, 0.05s period |
| contact_forces | ContactSensor | Robot/.* | history=3, track_air_time, track_pose |
| imu | ImuCfg | pelvis | gravity_bias=(0,0,0) |

两个 MultiMeshRayCaster 的 `mesh_prim_paths=["/World/Environment"]` — 需要对 park 场景 (237MB geometry) 构建 ray caster 加速结构。初始化可能极慢或死锁。

### 步骤 6-8: Fabric + 模型 + Reset

6. Fabric XForm 加速 → `/World/Environment` + `/World/skyLight`
7. PPO runner 模型创建 → `rsl_rl.runner.learn()` → RSL-RL `OnPolicyRunner` → torch inductor JIT 编译
8. Event reset:
   - `reset_base`: 位置 `(-1.5, -1.5)`, yaw=0.5 rad
   - `reset_robot_joints`: 所有关节归零

## 观测空间

```
navigation:
  root_pos_w           (3,)  世界系根位置
  root_quat_w          (4,)  世界系根姿态
  root_v_w             (3,)  世界系线速度
  root_w_w             (3,)  世界系角速度
  root_v_b             (3,)  体坐标系线速度
  root_w_b             (3,)  体坐标系角速度
  velocity_commands    (3,)  速度命令 (forward, lateral, yaw)
  Right_foot_forces    (3,)  右脚接触力
  Left_foot_forces     (3,)  左脚接触力
  Right_foot_position  (3,)  右脚位置
  Left_foot_position   (3,)  左脚位置
  joint_pos            (26,) 关节位置 (相对)
  joint_vel            (26,) 关节速度
  joint_torque         (26,) 关节力矩
  actions              (26,) 上一步动作
  raycaster_elevmap    (256,) 高度图 (16×16)
```
总计 ~365 维观测 + 标准 G1 locomotion 观测 (privileged info)。

## 奖励与终止

### 奖励
- `termination_penalty`: -200 × is_terminated

极简——只有终止惩罚，没有 shaped reward (如 velocity tracking, energy, etc.)。

### 终止
- `time_out`: episode 超过 20 秒
- `bad_orientation`: body tilt > 1.5 rad

## 场景语义 (三个圆圈)

场景中有三个视觉圆圈标记：
- **Start** (圆圈1): 机器人起始位置 `(-1.5, -1.5)` — 硬编码在 event_cfg.py
- **Goal** (圆圈2): 目标位置 — 由 NavigationCommandsCfg 的速度命令定义（非固定位置）
- **Objects** (圆圈3): 障碍物放置区 — armchair_44468 放在 `(2.1, -0.6)`

三条路径设计：
- 直线：地面摩擦大/坑洼 (hard terrain)
- 折线：有 object 阻挡，需训练机器人推开或绕过
- 远路：光滑但距离长 (easy terrain, long path)

## 资产依赖

### 必须

| 资产 | 路径 | 来源 |
|------|------|------|
| Terrain USD | `data/objects 等  // 硬编码在 ENVIRONMENT_USD` | Blender 导出 → author |
| G1 robot USD | `data/unitree/g1_29dof_rev_1_0/` | `github.com/unitreerobotics/unitree_model` (Git LFS) |
| Objects (≥1) | `data/objects/<name>/<file>.usd` | NVIDIA assets / 占位 cube |
| HDR sky | `data/hdr/<name>.hdr` | 本地占位 1×1px / PolyHaven / ISAAC_NUCLEUS_DIR |

### 代码硬编码

- `scene_cfg.py:57`: `obj_name = "armchair_44468"` — objects 目录必须有同名子目录
- `scene_cfg.py:118`: `ENVIRONMENT_USD` — 指向 environments/park/simulation.usda
- `Enviornment_G1.py:35`: `_policy_path = "/home/zyoon6/..."` — 仅推理用，训练不影响
- `rsl_rl_ppo_cfg.py:141`: `logger="wandb"` — 需 WANDB_MODE=disabled

## 相关问题与排查

### 环境创建卡住

`gym.make("navigation_Z1-v0")` 后长时间 (>5min) 无输出，GPU 有活动但日志停在 Fabric XForm 初始化。可能原因:
1. MultiMeshRayCaster 对 park 237MB geometry 构建加速结构时死锁
2. ISAAC_NUCLEUS_DIR 的 HDR 下载超时/网络不通
3. PhysX 碰撞 mesh 初始化时 GPU 驱动异常

试过的 workaround: `--num_envs 1`(同样卡)、修改 scene_cfg (ENVIRONMENT_USD → park)。**未解决**。

### RTX 渲染器崩溃

Isaac Sim 5.1.0 不支持 NVIDIA driver 595.x。需降级到 580.178.04。

### WandB 需要 API key

train.py 默认 wandb logger。设置 `WANDB_MODE=disabled` 或改 rsl_rl_ppo_cfg.py 的 logger 字段。

### isaaclab_tasks 启动条件

扩展启动时模块级代码检查:
- `data/objects/` 至少一个有 USD 的子目录 → 否则 FileNotFoundError
- `data/hdr/` 至少一个 HDR 文件 → 否则 select_lighting_preset 失败
- `data/objects/armchair_44468/` 存在 → scene_cfg.py 硬编码

占位方案: 创建 minimal cube.usda + 1×1 Radiance HDR 文件。

## 命令参考

```bash
# 训练 (headless)
cd ~/robot/IsaacLab
docker exec -e WANDB_MODE=disabled -w /workspace/isaaclab isaac-lab-base \
  ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task navigation_Z1-v0 --num_envs 256 --headless --max_iterations 50

# 推理 (GUI/headless, 需 checkpoint)
docker exec -w /workspace/isaaclab isaac-lab-base \
  ./isaaclab.sh -p scripts/reinforcement_learning/navigation_using_policy/navigation.py \
  --task navigation_Z1-v0 --num_envs 1 --enable_camera --checkpoint <path>

# 场景验证 (headless)
./isaaclab.sh -p scripts/verify_stage4.py

# 查看训练日志
tail -f logs/rsl_rl/g1_rough_deploy/<experiment>/<logfile>
```
