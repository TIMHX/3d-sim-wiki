---
title: IsaacLab Operation Manual
created: 2026-08-06
updated: 2026-08-06
type: concept
tags: [isaac-lab, robot-env, workflow, troubleshooting]
confidence: high
---

# IsaacLab 机器人项目操作手册

> tim-pc Ubuntu · GeorgiaTechLIDARGroup/IsaacLab @ `2.3.0/feature/navigation` · 2026-08-06
> 环境已配置完成：Docker 29.7.1 + NVIDIA Container Toolkit + 镜像 `isaac-lab-base`（Isaac Sim 5.1.0）

---

## 0. 概念速览

```
宿主(tim-pc)  ~/robot/IsaacLab  ←→  容器(isaac-lab-base)  /workspace/isaaclab
    ├── source/  （task 定义）          ├── source/   （bind mount，实时同步）
    ├── scripts/ （训练/工具脚本）      ├── scripts/  （bind mount，实时同步）
    ├── logs/    （训练产物）           ├── logs/     （bind mount，实时同步）
    └── docker/  （容器管理）
```

**关键点**：宿主改 `source/`、`scripts/` 立刻在容器内生效（bind mount），无需重建镜像。
**注意**：bind mount 的是宿主目录，容器内修改也会写回宿主。

---

## 1. 容器生命周期

```bash
# 在宿主上操作（SSH 或桌面终端都行，docker 组已配好，无需 sudo）

cd ~/robot/IsaacLab

./docker/container.py start          # 启动容器（后台，已存在则直接拉起）
./docker/container.py enter          # 进入容器 bash（日常开发都在这里）
./docker/container.py stop           # 停止并删除容器（镜像保留）
./docker/container.py build          # 只重建镜像（改了 Dockerfile 才需要）

# 验证容器状态
docker ps --format '{{.Names}} {{.Status}}'
```

首次进入容器后：
```bash
# 容器内已有 alias（.bashrc 配好）
isaaclab    # = /workspace/isaaclab/isaaclab.sh
python      # = Isaac Sim 内置 python（带 CUDA/torch）
```

---

## 2. 打开软件（Isaac Sim GUI vs headless）

tim-pc 有桌面（Gnome :0），两种模式：

### 2.1 图形界面（看得见仿真画面）
```bash
# 在 tim-pc 的桌面终端里（不是 SSH 无转发终端）：
cd ~/robot/IsaacLab
./docker/container.py enter
# 容器内：
isaaclab -p scripts/tools/blender_isaac/view_environment.py --usd scripts/tools/blender_isaac/environments/<env>/simulation.usda
```
X11 转发说明：容器配置支持 X11，但需要 `DISPLAY` 环境变量。
- 直接坐 tim-pc 前开终端 → 自动带 :0，直接能出画面
- SSH 进去 → 需 `ssh -X` 转发（画面较卡，不推荐训练时用）

### 2.2 headless（无画面，训练用）
```bash
# 容器内：训练/推理脚本默认 headless，加 --headless 显式指定
isaaclab -p scripts/reinforcement_learning/rsl_rl/train.py --task navigation_Z1-v0 --headless
```

---

## 3. 导入你自己的 Blender 环境（Construction / Park）

项目组在 repo 内置了完整管线：`scripts/tools/blender_isaac/`（详见其 README.md）。

**你的两个场景现状**（已检查）：
| 场景 | 位置 | 状态 |
|------|------|------|
| Construction | `~/blender_proj/Construction/` | 有 geometry.usdc + physics_profiles.json，**缺 simulation.usda** |
| Park | `~/blender_proj/Park/` | 有 geometry.usdc + physics_profiles.json，**缺 simulation.usda** |

参考模板：`~/Downloads/example_env/`（完整，含 simulation.usda，是导师给的 example）。

### 3.1 把场景放进 repo（一次）
```bash
# 宿主上
cd ~/robot/IsaacLab/scripts/tools/blender_isaac/environments/
mkdir -p construction_site park
cp -r ~/blender_proj/Construction/construction_site/   # 场景文件+textures
cp -r ~/blender_proj/Park/park/
# 最终结构：environments/<name>/geometry.usdc + physics_profiles.json + textures/
```

### 3.2 生成 simulation.usda（在容器内，关键步骤）
```bash
# 宿主：进入容器
cd ~/robot/IsaacLab && ./docker/container.py enter

# 容器内（每个场景跑一次）：
export ENVIRONMENT_NAME=construction_site
./isaaclab.sh -p scripts/tools/blender_isaac/author_environment_physics.py \
  "scripts/tools/blender_isaac/environments/${ENVIRONMENT_NAME}" --strict
# 生成 simulation.usda + simulation.usda.report.json

export ENVIRONMENT_NAME=park
./isaaclab.sh -p scripts/tools/blender_isaac/author_environment_physics.py \
  "scripts/tools/blender_isaac/environments/${ENVIRONMENT_NAME}" --strict
```

### 3.3 验证场景能加载
```bash
# 容器内
./isaaclab.sh -p scripts/tools/blender_isaac/view_environment.py \
  --usd "scripts/tools/blender_isaac/environments/construction_site/simulation.usda"
# 画面空白时：Stage 树选 /Environment → 按 F 框选
```

### 3.4 让 navigation task 用你的场景
当前 `navigation_Z1` task 的 `ENVIRONMENT_USD` 硬编码在：
`source/isaaclab_tasks/isaaclab_tasks/manager_based/navigation_Z1/cfg/scene_cfg.py:118`
指向 `environments/example_env/simulation.usda`（当前不存在）。

修改方式（二选一）：
```python
# 方式A：直接改 scene_cfg.py（推荐先这样跑通）
ENVIRONMENT_USD = str(Path("/workspace/isaaclab/scripts/tools/blender_isaac/environments/construction_site/simulation.usda").resolve())
```
```bash
# 方式B：git 本地分支管理（避免覆盖导师代码）
git checkout -b feature/local-env
# 改完 scene_cfg.py 后 commit
```

---

## 4. 运行模拟（navigation task 交互演示）

项目组脚本 `scripts/reinforcement_learning/navigation_using_policy/`：
- `navigation.py` — 单环境导航演示（键盘速度指令，带相机/LiDAR/数据记录）
- `navigation_ros_test.py` — 带 ROS 集成的完整版本
- `biped_navigation.py` — 多环境演示

```bash
# 容器内（有 checkpoint 时）
./isaaclab.sh -p scripts/reinforcement_learning/navigation_using_policy/navigation.py \
  --task navigation_Z1-v0 --num_envs 1 --enable_camera \
  --checkpoint /workspace/isaaclab/logs/rsl_rl/<experiment>/<run>/model_XXXX.pt

# 没 checkpoint 也能起（会从随机策略开始，机器人乱走但能看场景）
./isaaclab.sh -p scripts/reinforcement_learning/navigation_using_policy/navigation.py \
  --task navigation_Z1-v0 --num_envs 1 --enable_camera
```

---

## 5. Navigation 算法训练

task 已注册：`navigation_Z1-v0`（G1 29-DOF 双足机器人，PPO/RSL-RL）。
目前 `logs/` 为空 → 从零训练。

### 5.1 首次训练（headless，后台跑）
```bash
# 宿主：起一个后台训练（推荐 tmux/byobu 或 nohup）
cd ~/robot/IsaacLab && ./docker/container.py enter

# 容器内
cd /workspace/isaaclab
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task navigation_Z1-v0 --num_envs 4096 --headless \
  --max_iterations 10000 2>&1 | tee ~/train_log.txt
```
产物在 `/workspace/isaaclab/logs/rsl_rl/<experiment_name>/`（bind mount → 宿主 `~/robot/IsaacLab/logs/`）。

### 5.2 断点续训
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task navigation_Z1-v0 --num_envs 4096 --headless \
  --resume true  # 或指定 --load_run <run_dir> --load_checkpoint model_XXXX.pt
```

### 5.3 训练后导出 policy + 在导航脚本里用
```bash
# 导出 jit（供 inference 用）
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/export_policy.py \
  --task navigation_Z1-v0 --load_run <run_dir> --checkpoint model_XXXX.pt

# 然后照第 4 节用 --checkpoint 加载
```

---

## 6. 常用参数速查

| 参数 | 说明 |
|------|------|
| `--task navigation_Z1-v0` | 项目导航任务（G1 双足） |
| `--num_envs N` | 并行环境数（4096 训练 / 1 演示） |
| `--headless` | 无 GUI（训练用） |
| `--enable_camera` | 开启相机传感器（演示用） |
| `--checkpoint <path>` | 加载模型 |
| `--resume` | 续训 |
| `--video` | 录制视频 |

---

## 7. 排错速查

| 症状 | 处理 |
|------|------|
| `could not select device driver "nvidia"` | nvidia-container-toolkit 没装/daemon 没重启（已装好，重跑 `sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker`） |
| 容器起不来 | `docker logs isaac-lab-base` 看日志 |
| 画面空白 | viewport → Stage 选 /Environment → F 框选 |
| 场景没更新 | 改了 geometry 必须重跑 Blender 导出 + author_environment_physics |
| 训练 OOM | 减 `--num_envs`（4096→2048） |
| git push 报认证 | 直接可用（gh credential helper 已绑定 github.gatech.edu），确认当前目录是 ~/robot/IsaacLab |

---

## 8. 参考链接

- 场景管线 README：`~/robot/IsaacLab/scripts/tools/blender_isaac/README.md`（最详细）
- Docker 文档：`~/robot/IsaacLab/docs/source/deployment/docker.rst`
- 导师示例环境：`~/Downloads/example_env/`（完整模板）
- 环境配置总览：[[isaaclab-docker-env]]
