"""
IDE Agent工作流引擎包

基于六大原则设计：阶段→步骤→工作节点→反馈→结束+指针
"""

__version__ = "1.0.0"
__author__ = "IDE Agent Workflow Team"
__description__ = "基于六大原则的IDE Agent工作流引擎"

# 导入核心组件
from .core.workflow_engine import WorkflowEngine
from .parser.mermaid_parser import MermaidParser
from .commands.command_registry import CommandRegistry, execute_command, get_help

__all__ = [
    'WorkflowEngine',
    'MermaidParser', 
    'CommandRegistry',
    'execute_command',
    'get_help'
]