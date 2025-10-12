"""
IDE Agent工作流引擎 - 自定义安装器包

提供智能的安装功能，支持检测客户端类型并安装到指定目录
"""

from .custom_installer import CustomInstaller, ClientDetector

__all__ = ['CustomInstaller', 'ClientDetector']