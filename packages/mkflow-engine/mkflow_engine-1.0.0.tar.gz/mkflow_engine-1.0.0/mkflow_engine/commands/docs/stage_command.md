# /stage 命令文档

## 用途
管理工作流阶段，包括添加、修改或查看阶段。

## 触发条件
当用户需要管理工作流阶段时使用此命令。

## AI执行逻辑
1. 分析用户意图确定操作类型
2. 推荐使用此命令
3. 执行相应的阶段管理操作

## AI执行脚本
当AI识别到用户输入 `/stage` 命令时，需要在命令行执行以下操作：

```bash
# 添加新阶段
mkf-stage --add --name "阶段名称"

# 列出所有阶段
mkf-stage --list

# 查看阶段详情
mkf-stage --view --id 阶段ID

# 修改阶段信息
mkf-stage --modify --id 阶段ID --name "新阶段名称"
```

**执行说明：**
- 使用 `mkf-stage` 命令管理工作流阶段
- 通过不同的参数执行不同的操作：`--add`、`--list`、`--view`、`--modify`
- 添加阶段时需要指定 `--name` 参数
- 查看和修改阶段时需要指定 `--id` 参数

## 示例
```
/stage add name="需求分析"
/stage list
/stage view id=1
```