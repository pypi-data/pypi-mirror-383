"""
命令注册器

管理所有可用的工作流引擎命令
"""

from typing import Dict, List, Callable, Any
from dataclasses import dataclass


@dataclass
class Command:
    """命令数据类"""
    name: str
    description: str
    handler: Callable
    aliases: List[str] = None
    usage: str = ""
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []


class CommandRegistry:
    """命令注册器类"""
    
    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self.aliases: Dict[str, str] = {}
    
    def register(self, command: Command) -> None:
        """
        注册命令
        
        Args:
            command: 命令对象
        """
        self.commands[command.name] = command
        
        # 注册别名
        for alias in command.aliases:
            self.aliases[alias] = command.name
    
    def get_command(self, command_name: str) -> Command:
        """
        获取命令
        
        Args:
            command_name: 命令名称或别名
            
        Returns:
            Command: 命令对象
        """
        # 检查是否是别名
        actual_name = self.aliases.get(command_name, command_name)
        return self.commands.get(actual_name)
    
    def execute(self, command_name: str, *args, **kwargs) -> Any:
        """
        执行命令
        
        Args:
            command_name: 命令名称
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            Any: 命令执行结果
        """
        command = self.get_command(command_name)
        if not command:
            raise ValueError(f"未知命令: {command_name}")
        
        return command.handler(*args, **kwargs)
    
    def list_commands(self) -> List[Dict[str, str]]:
        """
        列出所有命令
        
        Returns:
            List: 命令信息列表
        """
        result = []
        for cmd in self.commands.values():
            result.append({
                'name': cmd.name,
                'description': cmd.description,
                'aliases': ', '.join(cmd.aliases),
                'usage': cmd.usage
            })
        return result
    
    def get_help(self, command_name: str = None) -> str:
        """
        获取帮助信息
        
        Args:
            command_name: 特定命令名称，None表示获取所有命令帮助
            
        Returns:
            str: 帮助信息
        """
        if command_name:
            command = self.get_command(command_name)
            if not command:
                return f"未知命令: {command_name}"
            
            help_text = f"命令: {command.name}\n"
            help_text += f"描述: {command.description}\n"
            if command.aliases:
                help_text += f"别名: {', '.join(command.aliases)}\n"
            if command.usage:
                help_text += f"用法: {command.usage}\n"
            return help_text
        else:
            help_text = "可用命令:\n"
            for cmd_info in self.list_commands():
                help_text += f"  {cmd_info['name']} - {cmd_info['description']}\n"
                if cmd_info['aliases']:
                    help_text += f"    别名: {cmd_info['aliases']}\n"
                if cmd_info['usage']:
                    help_text += f"    用法: {cmd_info['usage']}\n"
                help_text += "\n"
            return help_text


# 全局命令注册器实例
_registry = CommandRegistry()


def register_command(name: str, description: str, handler: Callable, 
                    aliases: List[str] = None, usage: str = "") -> None:
    """
    注册命令的便捷函数
    
    Args:
        name: 命令名称
        description: 命令描述
        handler: 命令处理函数
        aliases: 命令别名
        usage: 用法说明
    """
    command = Command(name, description, handler, aliases, usage)
    _registry.register(command)


def get_command_registry() -> CommandRegistry:
    """
    获取全局命令注册器
    
    Returns:
        CommandRegistry: 命令注册器实例
    """
    return _registry


def execute_command(command_name: str, *args, **kwargs) -> Any:
    """
    执行命令的便捷函数
    
    Args:
        command_name: 命令名称
        *args: 位置参数
        **kwargs: 关键字参数
        
    Returns:
        Any: 命令执行结果
    """
    return _registry.execute(command_name, *args, **kwargs)


def list_commands() -> List[Dict[str, str]]:
    """
    列出所有命令的便捷函数
    
    Returns:
        List: 命令信息列表
    """
    return _registry.list_commands()


def get_help(command_name: str = None) -> str:
    """
    获取帮助信息的便捷函数
    
    Args:
        command_name: 特定命令名称
        
    Returns:
        str: 帮助信息
    """
    return _registry.get_help(command_name)


# 示例命令处理函数
def init_command_handler(workflow_type: str = "official", **kwargs) -> str:
    """初始化命令处理函数"""
    return f"初始化工作流引擎，类型: {workflow_type}"


def stage_command_handler(stage_name: str, **kwargs) -> str:
    """阶段命令处理函数"""
    return f"进入阶段: {stage_name}"


def step_command_handler(step_name: str, **kwargs) -> str:
    """步骤命令处理函数"""
    return f"执行步骤: {step_name}"


def feedback_command_handler(**kwargs) -> str:
    """反馈命令处理函数"""
    return "查看当前反馈信息"


def pointer_command_handler(**kwargs) -> str:
    """指针命令处理函数"""
    return "查看当前指针位置"


def end_command_handler(**kwargs) -> str:
    """结束命令处理函数"""
    return "结束当前工作流"


# 注册示例命令
register_command(
    name="/init",
    description="初始化工作流引擎",
    handler=init_command_handler,
    aliases=["init", "initialize"],
    usage="/init [official|custom]"
)

register_command(
    name="/stage",
    description="进入特定阶段",
    handler=stage_command_handler,
    aliases=["stage", "phase"],
    usage="/stage <stage_name>"
)

register_command(
    name="/step",
    description="执行特定步骤",
    handler=step_command_handler,
    aliases=["step", "task"],
    usage="/step <step_name>"
)

register_command(
    name="/feedback",
    description="查看当前反馈",
    handler=feedback_command_handler,
    aliases=["feedback", "fb"],
    usage="/feedback"
)

register_command(
    name="/pointer",
    description="查看当前指针位置",
    handler=pointer_command_handler,
    aliases=["pointer", "pt"],
    usage="/pointer"
)

register_command(
    name="/end",
    description="结束当前工作流",
    handler=end_command_handler,
    aliases=["end", "finish"],
    usage="/end"
)

register_command(
    name="/help",
    description="显示帮助信息",
    handler=get_help,
    aliases=["help", "h"],
    usage="/help [command_name]"
)


# 使用示例
def main():
    """命令注册器使用示例"""
    # 获取命令注册器
    registry = get_command_registry()
    
    # 列出所有命令
    print("可用命令:")
    for cmd_info in registry.list_commands():
        print(f"  {cmd_info['name']}: {cmd_info['description']}")
    
    print("\n" + "="*50 + "\n")
    
    # 执行命令
    try:
        result = registry.execute("/init", "official")
        print(f"执行结果: {result}")
        
        result = registry.execute("help")  # 使用别名
        print(f"帮助信息:\n{result}")
    except ValueError as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()