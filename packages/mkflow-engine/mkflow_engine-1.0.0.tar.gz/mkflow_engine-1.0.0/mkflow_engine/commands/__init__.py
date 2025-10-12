"""
命令注册器模块

包含CommandRegistry类和命令执行函数
"""

from .command_registry import CommandRegistry, execute_command, get_help

__all__ = ['CommandRegistry', 'execute_command', 'get_help']