---
name: desktop-pet
description: "Hermes Desktop Pet — 小黑猫。浮窗桌宠，实时显示 Hermes 状态，自由漫步/奔跑/睡觉。"
version: 1.0.0
author: Hermes Agent
tags: [desktop-pet, cat, macos, pet, floating-window, PySide6]
---

# Hermes Desktop Pet — 小黑猫 🐱

一只会跑会睡的桌面小黑猫，实时显示 Hermes Agent 状态。

## 功能

- **浮窗显示** — 无边框透明窗口，置顶在所有窗口之上
- **实时状态** — 自动连接 Hermes API (端口 9119) 显示当前状态
- **自由漫步** — 空闲时慢走，工作时满屏飞奔，睡觉时趴着飘 Zzz
- **状态对应行为**：

  | 状态 | 猫的行为 |
  |------|---------|
  | 🟢 待命中 | 慢悠悠散步 |
  | 🟡 思考中 | 眼睛发光，小步踱步 |
  | 🔴 工作中 | 满屏狂奔，四脚狂蹬 |
  | ⚪ 离线 | 原地趴着睡，飘 Zzz |

- **侧身猫咪** — 侧面视角，四腿奔跑动画，两颗小虎牙
- **拖拽移动** — 鼠标拖到任何位置
- **右键菜单** — 置顶开关 / 退出
- **开机自启** — macOS launchd 自动启动

## 前置要求

- macOS
- Hermes Agent 已运行且 API 端口 9119 可访问
- Python 3.9+
- PySide6_Essentials

## 安装

### 1. 安装 PySide6

```bash
# 国内用户用清华镜像更快
~/.hermes/hermes-agent/venv/bin/pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple PySide6_Essentials
```

### 2. 复制文件

从 skill 目录复制脚本到桌面宠物目录：

```bash
SKILL_DIR=~/.hermes/skills/macos-automation/desktop-pet
mkdir -p ~/.hermes/desktop-pet
cp "$SKILL_DIR/scripts/pet.py" ~/.hermes/desktop-pet/
cp "$SKILL_DIR/scripts/launch.sh" ~/.hermes/desktop-pet/
chmod +x ~/.hermes/desktop-pet/launch.sh
```

### 3. 启动

```bash
~/.hermes/hermes-agent/venv/bin/python3 ~/.hermes/desktop-pet/pet.py &
```

### 4. (可选) 开机自启

```bash
mkdir -p ~/.hermes/logs
cp "$SKILL_DIR/scripts/com.hermes.desktop-pet.plist" ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.hermes.desktop-pet.plist
```

## 管理

```bash
# 启动
launchctl load ~/Library/LaunchAgents/com.hermes.desktop-pet.plist

# 停止
launchctl unload ~/Library/LaunchAgents/com.hermes.desktop-pet.plist

# 查看状态
launchctl list | grep desktop-pet

# 手动启动
~/.hermes/hermes-agent/venv/bin/python3 ~/.hermes/desktop-pet/pet.py &
```

## 文件结构

```
~/.hermes/desktop-pet/
├── pet.py          # 主程序
└── launch.sh       # 启动脚本
~/Library/LaunchAgents/
└── com.hermes.desktop-pet.plist  # 开机自启
```

## 卸载

```bash
launchctl unload ~/Library/LaunchAgents/com.hermes.desktop-pet.plist
rm ~/Library/LaunchAgents/com.hermes.desktop-pet.plist
rm -rf ~/.hermes/desktop-pet
```

## 技术说明

- 基于 PySide6 (Qt6)，纯 Python 实现
- 通过 Hermes API (`http://localhost:9119/api/status`) 获取状态
- 每 2 秒轮询一次状态
- 30fps 动画 + 50fps 移动
- macOS launchd 开机自启
- 使用 AppKit 原生 API 强制置顶
