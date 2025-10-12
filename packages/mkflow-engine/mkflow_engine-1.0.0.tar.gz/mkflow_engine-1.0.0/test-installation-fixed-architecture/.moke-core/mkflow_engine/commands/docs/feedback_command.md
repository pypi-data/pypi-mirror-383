# /feedback 命令文档

## 用途
收集和处理用户反馈。

## 触发条件
用户提供反馈或需要反馈机制时使用此命令。

## AI执行逻辑
1. 识别用户是否需要查看或提供反馈
2. 推荐使用此命令
3. 执行相应的反馈操作

## AI执行脚本
当AI识别到用户输入 `/feedback` 命令时，需要在命令行执行以下操作：

```bash
# 提供反馈
mkf-feedback --provide --text "反馈内容"

# 查看反馈详情
mkf-feedback --view --id 反馈ID

# 列出所有反馈
mkf-feedback --list
```

**执行说明：**
- 使用 `mkf-feedback` 命令管理用户反馈
- 通过不同的参数执行不同的操作：`--provide`、`--view`、`--list`
- 提供反馈时需要指定 `--text` 参数
- 查看反馈详情时需要指定 `--id` 参数

## 示例
```
/feedback provide text="功能很好用"
/feedback list
/feedback view id=1
```