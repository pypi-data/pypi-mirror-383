# IDE Agent MKFlow 引擎

## 项目概述

这是一个基于Python的IDE Agent MKFlow引擎，旨在将Agent的回答方式转变为更符合垂直领域的工作流模式。

## 核心原则

- **阶段 (Stage)** → **步骤 (Step)** → **工作节点 (Work Node)** → **反馈 (Feedback)** → **结束 (End)** + **指针 (Point)**

## 技术栈

- Python 3.8+
- JSON & JSON Schema
- Mermaid.js
- Markdown
- 命令行工具
- uv (现代Python包管理器)

## 快速开始

### 安装

#### 方式一：智能安装（推荐）
```bash
# 使用自定义安装器，自动检测客户端类型
mkf-install

# 指定安装目录
mkf-install --install-dir /path/to/project

# 从本地包安装
mkf-install --package-path ./local-package.whl
```

#### 方式二：传统安装
```bash
# 使用uv安装
uv pip install mkflow_engine

# 或者从源码安装
uv pip install .

# 开发模式安装
uv pip install -e .
```

### 初始化
```bash
mkf init
```

### 使用命令
```bash
mkf stage <stage_name>
mkf step <step_name>
mkf feedback
mkf pointer
mkf end
```

## 项目结构

```
mkflow-engine/
├── core/           # 核心引擎
├── parser/         # 解析器
├── commands/       # 命令系统
├── templates/      # 模板文件
├── docs/          # 文档
└── installer/     # 安装程序
```

## 功能特性

1. **智能命令解析** - 支持自然语言命令识别
2. **可视化工作流** - 基于Mermaid的可视化流程
3. **实时反馈机制** - 动态反馈和状态跟踪
4. **模块化设计** - 可扩展的插件架构
5. **IDE集成** - 无缝集成到主流IDE中

## 开发指南

详见 [开发文档](./docs/development.md)

## 许可证

MIT License