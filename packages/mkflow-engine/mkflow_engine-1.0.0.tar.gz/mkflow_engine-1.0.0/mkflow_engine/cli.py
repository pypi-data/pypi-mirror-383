"""
工作流引擎命令行接口
"""

import click
import sys
import os
from pathlib import Path

# 从包内导入模块
from .commands.command_registry import execute_command, get_help, list_commands
from .parser.mermaid_parser import MermaidParser, generate_mermaid_template
from .core.workflow_engine import WorkflowEngine


@click.group()
@click.version_option(version="1.0.0", prog_name="MK-FLOW")
def cli():
    """IDE Agent MKFlow引擎命令行工具"""
    pass


@cli.command()
@click.option('--type', '-t', default='official', 
              type=click.Choice(['official', 'custom']),
              help='初始化类型: official(官方模板) 或 custom(自定义)')
@click.option('--output', '-o', default='./workflows',
              help='输出目录路径')
@click.option('--template', default='flowchart',
              type=click.Choice(['flowchart', 'sequence']),
              help='Mermaid模板类型')
def init(type, output, template):
    """初始化工作流引擎"""
    try:
        # 创建输出目录
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 生成模板文件
        if type == 'official':
            mermaid_content = generate_mermaid_template(template)
            template_file = output_path / f"template_{template}.mermaid"
            
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(mermaid_content)
            
            # 创建配置文件
            config_content = f"""# 工作流引擎配置文件
workflow_type: {template}
initialized: true
date: {click.get_current_context().meta.get('start_time', 'unknown')}
"""
            config_file = output_path / "config.yaml"
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            click.echo(f"✅ 初始化完成!")
            click.echo(f"📁 输出目录: {output_path.absolute()}")
            click.echo(f"📄 模板文件: {template_file.name}")
            click.echo(f"⚙️  配置文件: config.yaml")
            
        else:
            click.echo("🔧 自定义模式: 请手动创建Mermaid文件")
            click.echo(f"📁 工作目录: {output_path.absolute()}")
        
        # 创建init.md文档
        init_doc = output_path / "init.md"
        with open(init_doc, 'w', encoding='utf-8') as f:
            f.write(generate_init_documentation())
        
        click.echo(f"📖 初始化文档: init.md")
        
    except Exception as e:
        click.echo(f"❌ 初始化失败: {e}", err=True)


@cli.command()
@click.argument('mermaid_file')
@click.option('--output', '-o', help='JSON输出文件路径')
@click.option('--validate/--no-validate', default=True, help='是否验证Schema')
def parse(mermaid_file, output, validate):
    """解析Mermaid文件并生成工作流JSON"""
    try:
        parser = MermaidParser()
        
        # 解析Mermaid文件
        workflow_data = parser.parse_file(mermaid_file)
        
        # 输出JSON
        import json
        json_output = json.dumps(workflow_data, indent=2, ensure_ascii=False)
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(json_output)
            click.echo(f"✅ JSON文件已生成: {output}")
        else:
            click.echo(json_output)
        
        # 验证Schema
        if validate:
            engine = WorkflowEngine()
            # 这里应该加载Schema文件进行验证
            # 简化实现：只输出验证提示
            click.echo("⚠️  Schema验证功能待实现")
        
    except Exception as e:
        click.echo(f"❌ 解析失败: {e}", err=True)


@cli.command()
@click.argument('stage_name')
def stage(stage_name):
    """进入特定阶段"""
    try:
        result = execute_command("/stage", stage_name)
        click.echo(f"🚀 {result}")
    except Exception as e:
        click.echo(f"❌ 执行失败: {e}", err=True)


@cli.command()
@click.argument('step_name')
def step(step_name):
    """执行特定步骤"""
    try:
        result = execute_command("/step", step_name)
        click.echo(f"📋 {result}")
    except Exception as e:
        click.echo(f"❌ 执行失败: {e}", err=True)


@cli.command()
def feedback():
    """查看当前反馈"""
    try:
        result = execute_command("/feedback")
        click.echo(f"💬 {result}")
    except Exception as e:
        click.echo(f"❌ 执行失败: {e}", err=True)


@cli.command()
def pointer():
    """查看当前指针位置"""
    try:
        result = execute_command("/pointer")
        click.echo(f"📍 {result}")
    except Exception as e:
        click.echo(f"❌ 执行失败: {e}", err=True)


@cli.command()
def end():
    """结束当前工作流"""
    try:
        result = execute_command("/end")
        click.echo(f"🏁 {result}")
    except Exception as e:
        click.echo(f"❌ 执行失败: {e}", err=True)


@cli.command()
@click.argument('command_name', required=False)
def help(command_name):
    """显示帮助信息"""
    try:
        result = get_help(command_name)
        click.echo(result)
    except Exception as e:
        click.echo(f"❌ 获取帮助失败: {e}", err=True)


@cli.command()
def list():
    """列出所有可用命令"""
    try:
        commands = list_commands()
        
        click.echo("可用命令:")
        click.echo("-" * 50)
        
        for cmd in commands:
            click.echo(f"命令: {cmd['name']}")
            click.echo(f"描述: {cmd['description']}")
            if cmd['aliases']:
                click.echo(f"别名: {cmd['aliases']}")
            if cmd['usage']:
                click.echo(f"用法: {cmd['usage']}")
            click.echo()
        
    except Exception as e:
        click.echo(f"❌ 列出命令失败: {e}", err=True)


@cli.command()
@click.argument('workflow_file')
@click.option('--interactive/--no-interactive', default=True, 
              help='是否交互式执行')
def run(workflow_file, interactive):
    """运行工作流文件"""
    try:
        # 加载工作流文件
        import json
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        
        # 创建工作流引擎实例
        engine = WorkflowEngine()
        workflow = engine.parse_workflow(workflow_data)
        
        click.echo(f"🚀 开始执行工作流: {workflow.name}")
        
        if interactive:
            # 交互式执行
            _run_interactive(engine, workflow)
        else:
            # 自动执行
            _run_automated(engine, workflow)
        
    except Exception as e:
        click.echo(f"❌ 运行工作流失败: {e}", err=True)


def _run_interactive(engine, workflow):
    """交互式执行工作流"""
    click.echo("\n📋 工作流阶段:")
    for i, stage in enumerate(workflow.stages, 1):
        click.echo(f"  {i}. {stage.name} - {stage.description or '无描述'}")
    
    # 选择阶段
    stage_choice = click.prompt("\n请选择要执行的阶段", type=int)
    
    if 1 <= stage_choice <= len(workflow.stages):
        selected_stage = workflow.stages[stage_choice - 1]
        engine.start_stage(selected_stage.id)
        
        click.echo(f"\n🚀 进入阶段: {selected_stage.name}")
        
        # 执行步骤
        for step in selected_stage.steps:
            if click.confirm(f"是否执行步骤: {step.name}"):
                engine.execute_step(step.id)
                
                # 执行工作节点
                for node in step.work_nodes:
                    if click.confirm(f"是否处理节点: {node.name} ({node.type.value})"):
                        result = engine.process_node(node.id)
                        click.echo(f"  结果: {result}")
        
        # 检查结束条件
        end_info = engine.check_end_conditions()
        if end_info:
            click.echo(f"\n🏁 {end_info['message']}")
        
        # 显示反馈
        feedbacks = engine.get_feedback()
        if feedbacks:
            click.echo("\n💬 执行反馈:")
            for fb in feedbacks[-5:]:  # 显示最后5条反馈
                click.echo(f"  {fb}")
    
    click.echo("\n✅ 工作流执行完成")


def _run_automated(engine, workflow):
    """自动执行工作流"""
    # 自动执行所有阶段和步骤
    for stage in workflow.stages:
        engine.start_stage(stage.id)
        click.echo(f"🚀 执行阶段: {stage.name}")
        
        for step in stage.steps:
            engine.execute_step(step.id)
            click.echo(f"  📋 执行步骤: {step.name}")
            
            for node in step.work_nodes:
                result = engine.process_node(node.id)
                click.echo(f"    🔧 处理节点: {node.name} - {result['feedback']}")
        
        # 检查结束条件
        end_info = engine.check_end_conditions()
        if end_info:
            click.echo(f"🏁 {end_info['message']}")
    
    click.echo("\n✅ 工作流自动执行完成")


def generate_init_documentation():
    """生成初始化文档"""
    return """# 工作流引擎初始化文档

## 项目概述

您已成功初始化IDE Agent工作流引擎。本项目基于六大原则设计：
- **阶段 (Stage)** → **步骤 (Step)** → **工作节点 (Work Node)** → **反馈 (Feedback)** → **结束 (End)** + **指针 (Point)**

## 文件结构

```
workflows/
├── template_flowchart.mermaid    # Mermaid流程图模板
├── config.yaml                   # 配置文件
└── init.md                       # 本文档
```

## 快速开始

### 1. 编辑Mermaid流程图

使用文本编辑器打开 `template_flowchart.mermaid` 文件，根据您的需求修改流程图。

### 2. 解析为工作流JSON

```bash
mkf parse template_flowchart.mermaid --output my_workflow.json
```

### 3. 运行工作流

```bash
mkf run my_workflow.json
```

## 可用命令

- `mkf init` - 初始化工作流
- `mkf parse <file>` - 解析Mermaid文件
- `mkf run <file>` - 运行工作流
- `mkf stage <name>` - 进入阶段
- `mkf step <name>` - 执行步骤
- `mkf feedback` - 查看反馈
- `mkf pointer` - 查看指针
- `mkf end` - 结束工作流
- `mkf help` - 显示帮助

## 开发指南

详见项目README文档。
"""


def main():
    """主入口函数"""
    cli()


if __name__ == "__main__":
    main()