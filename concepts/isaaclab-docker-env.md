---
title: IsaacLab Docker Environment (tim-pc)
created: 2026-08-06
updated: 2026-08-06
type: concept
tags: [isaac-lab, robot-env, workflow, troubleshooting]
confidence: high
---

# IsaacLab Docker Environment (tim-pc)

机器人项目（Georgia Tech LIDAR Group）的 Isaac Lab 运行环境。采用 **docker 容器方案**，不需要手动安装 Isaac Sim。

## Repo & Git 配置

- Repo: `GeorgiaTechLIDARGroup/IsaacLab` @ branch `2.3.0/feature/navigation`
- 位置: `~/robot/IsaacLab`（tim-pc Ubuntu）
- 认证: gh CLI 2.97.0 + gatech token（xhong34），credential helper **仅绑定 github.gatech.edu**
- 私人 github.com 凭据不受影响（按 hostname 隔离）
- 后续 git pull/push 零认证直接做

## 环境组件

| 组件 | 版本/说明 |
|------|-----------|
| Docker | 29.7.1 + compose v5.4.0 + buildx |
| NVIDIA Container Toolkit | 1.19.1（GPU 直通必需，nvidia runtime 已注册） |
| 镜像 | `isaac-lab-base`（46.5GB 磁盘 / 15.9GB 内容，含 Isaac Sim 5.1.0） |
| 容器 | `isaac-lab-base`（base profile） |
| 验证 | torch 2.7.0+cu128, CUDA=True, RTX 4090 24GB |

## 日常命令

```bash
cd ~/robot/IsaacLab
./docker/container.py start          # 启动容器（首次会 build）
./docker/container.py enter          # 进入容器 bash
./docker/container.py stop           # 停止并移除容器
./docker/container.py build          # 只构建不启动
./docker/container.py copy           # 从容器复制 logs/产物到宿主
```

容器内已配 alias（.bashrc）：`isaaclab`、`python`、`python3`、`pip`、`tensorboard`。

容器内训练示例：
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Velocity-Rough-G1-29dof-v0 --num_envs 4096 --headless
```

ROS2 profile（如需要）: `./docker/container.py start ros2 --files docker-compose.ros2-hostfs.yaml`

## 关键配置点

- X11 转发默认关: `.container.cfg` 设 `X11_FORWARDING_ENABLED=1` 可开（带渲染仿真用）
- 镜像基础: `nvcr.io/nvidia/isaac-sim:5.1.0`（`docker/.env.base` 里 `ISAACSIM_VERSION`）
- 缓存走 docker named volumes（isaac-cache-*），不依赖宿主目录

## 历史清理（2026-08-06）

迁移前清理了手动安装环境（共释放 ~80G）：
- `~/isaacsim`(54G) + `~/isaaclab`(20G) + `~/isaaclab-6`(843M) 已删
- Omniverse 缓存（~/.cache/ov 5.7G 等）+ IsaacSim.desktop 已删
- ROS2 全套 296 包 + /opt/ros + ros2 apt 源已卸载（卸载前确认无其他依赖）

## 相关

- [[blender-construction-site-tutorial]] — 场景建模流程（robot env 设计上游）
- [[isaaclab-operation-manual]] — 完整操作手册（容器/导入 Blender 场景/训练 navigation 的逐步命令）
