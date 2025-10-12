# /pointer 命令文档

## 用途
管理工作流执行指针。

## 触发条件
需要跟踪或管理执行位置时使用此命令。

## AI执行逻辑
1. 识别用户是否需要指针操作
2. 推荐使用此命令
3. 执行相应的指针管理操作

## AI执行脚本
当AI识别到用户输入 `/pointer` 命令时，需要在命令行执行以下操作：

```bash
# 设置指针位置
mkf-pointer --set --position "位置名称"

# 获取当前指针位置
mkf-pointer --get

# 移动指针
mkf-pointer --move --direction next
mkf-pointer --move --direction prev

# 重置指针
mkf-pointer --reset
```

**执行说明：**
- 使用 `mkf-pointer` 命令管理工作流执行指针
- 通过不同的参数执行不同的操作：`--set`、`--get`、`--move`、`--reset`
- 设置指针时需要指定 `--position` 参数
- 移动指针时需要指定 `--direction` 参数（next 或 prev）

## 示例
```
/pointer set position="需求分析"
/pointer get
/pointer move direction="next"
```