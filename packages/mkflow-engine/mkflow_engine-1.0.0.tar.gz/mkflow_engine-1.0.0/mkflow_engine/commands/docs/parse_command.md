# /parse 命令文档

## 用途
将Mermaid文件解析为工作流JSON。

## 触发条件
用户提供Mermaid文件时使用此命令。

## AI执行逻辑
1. 检测Mermaid文件存在
2. 推荐使用此命令
3. 执行解析操作

## AI执行脚本
当AI识别到用户输入 `/parse` 命令时，需要在命令行执行以下操作：

```bash
# 解析Mermaid文件
mkf-parse --file "文件路径.mmd"

# 或者使用完整路径执行
.moke-core/bin/mkf-parse --file "文件路径.mmd"
```

**执行说明：**
- 使用 `mkf-parse` 命令将Mermaid文件解析为工作流JSON
- 通过 `--file` 参数指定Mermaid文件路径
- 命令会检查文件是否存在，如果不存在则返回错误信息
- 解析成功后会生成对应的工作流JSON结构

## 示例
```
/parse file="workflow.mmd"
```