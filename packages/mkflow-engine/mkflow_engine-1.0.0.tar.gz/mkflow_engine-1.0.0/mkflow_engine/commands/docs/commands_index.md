# 工作流引擎命令索引

## 可用命令列表

以下是工作流引擎支持的所有命令，点击命令名称查看详细文档：

### 核心工作流命令
- [init_command.md](init_command.md) - `/init` 初始化工作流
- [stage_command.md](stage_command.md) - `/stage` 管理工作流阶段  
- [step_command.md](step_command.md) - `/step` 执行工作流步骤
- [feedback_command.md](feedback_command.md) - `/feedback` 提供反馈机制
- [pointer_command.md](pointer_command.md) - `/pointer` 指针管理
- [end_command.md](end_command.md) - `/end` 结束工作流

### 辅助命令
- [help_command.md](help_command.md) - `/help` 获取帮助信息
- [parse_command.md](parse_command.md) - `/parse` 解析Mermaid流程图
- [run_command.md](run_command.md) - `/run` 运行工作流

## AI执行指导

每个命令文档都包含详细的AI执行脚本，指导AI在识别到用户输入特定命令时，需要在命令行执行相应的mkf-*命令：

1. **识别命令触发** - 当用户输入`/init`、`/stage`等命令时
2. **解析命令参数** - 从用户输入中提取必要参数
3. **执行命令行操作** - 调用相应的mkf-*命令行工具
4. **返回执行结果** - 显示命令行执行结果和状态

## 使用说明

AI助手在执行工作流相关操作时，应该：
1. 根据用户输入的`/`命令识别需要执行的操作
2. 参考对应命令的详细文档和AI执行脚本
3. 在命令行中执行相应的mkf-*命令
4. 返回命令行的执行结果和状态信息

## 快速参考

| 命令 | 用途 | 触发条件 | AI执行逻辑 |
|------|------|----------|------------|
| `/init` | 初始化工作流 | 开始新工作流程 | 检测初始化意图，创建实例 |
| `/stage` | 管理阶段 | 需要阶段操作 | 分析操作类型，执行阶段管理 |
| `/step` | 执行步骤 | 需要具体操作 | 识别操作类型，执行步骤 |
| `/feedback` | 收集反馈 | 需要反馈机制 | 识别反馈需求，收集/查看反馈 |
| `/pointer` | 管理指针 | 需要跟踪位置 | 识别指针操作，管理执行位置 |
| `/end` | 结束工作流 | 工作流完成 | 检测完成状态，结束工作流 |
| `/help` | 获取帮助 | 请求帮助时 | 直接显示命令列表 |
| `/parse` | 解析流程图 | 提供Mermaid文件时 | 检测文件存在，解析为JSON |
| `/run` | 运行工作流 | 要求运行工作流时 | 检查可运行性，执行工作流 |

## 命令参数说明

### 参数提取函数
每个命令文档中的AI执行脚本都使用了以下辅助函数：
- `extract_parameter(param_name, user_input)` - 从用户输入中提取指定参数
- `extract_operation(user_input)` - 从用户输入中识别操作类型

### 参数格式
- 参数格式：`参数名="参数值"`
- 示例：`/init project_name="新项目"`

---
*此索引文件由IDE Agent工作流引擎自动生成*
*AI必须参考命令文档中的执行脚本进行具体操作*