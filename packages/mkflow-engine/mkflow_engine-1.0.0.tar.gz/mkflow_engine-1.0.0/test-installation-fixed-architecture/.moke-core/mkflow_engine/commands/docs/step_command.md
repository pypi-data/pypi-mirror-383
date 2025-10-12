# /step 命令文档

## 用途
执行具体的处理步骤。

## 触发条件
用户需要执行特定操作时使用此命令。

## AI执行逻辑
1. 识别用户请求的具体操作类型
2. 推荐使用此命令
3. 执行相应的步骤操作

## AI执行脚本
当AI识别到用户输入 `/step` 命令时，需要在命令行执行以下操作：

```bash
# 执行具体步骤
mkf-step --execute --name "步骤名称"

# 查看步骤状态
mkf-step --status

# 标记步骤完成
mkf-step --complete --id 步骤ID
```

**执行说明：**
- 使用 `mkf-step` 命令管理工作流步骤
- 通过不同的参数执行不同的操作：`--execute`、`--status`、`--complete`
- 执行步骤时需要指定 `--name` 参数
- 标记步骤完成时需要指定 `--id` 参数

## 示例
```
/step execute name="需求分析"
/step status
/step complete id=1
```