#!/usr/bin/env python3
"""
测试交互式安装脚本
模拟用户输入来测试安装器的交互功能
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from installer.custom_installer import CustomInstaller

def test_interactive_installation():
    """测试交互式安装"""
    print("🚀 开始测试交互式安装...")
    
    # 创建测试安装目录
    test_dir = Path("test-interactive-installation")
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建安装器实例
    installer = CustomInstaller(test_dir)
    
    # 模拟用户输入
    def mock_input(prompt):
        print(prompt, end="")
        if "是否继续安装" in prompt:
            return "y"  # 确认继续安装
        elif "请输入选择" in prompt:
            return "1"  # 选择代码开发扩展包
        else:
            return ""
    
    # 临时替换input函数
    original_input = __builtins__.input
    __builtins__.input = mock_input
    
    try:
        # 运行安装
        installer.install_package()
        print("✅ 交互式安装测试完成！")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        # 恢复原始input函数
        __builtins__.input = original_input
    
    # 检查安装结果
    if (test_dir / ".moke-core").exists():
        print("✅ 核心包安装成功")
    
    if (test_dir / ".moke-core" / "extensions" / "code_development").exists():
        print("✅ 代码开发扩展包安装成功")
    
    if (test_dir / ".trae").exists():
        print("✅ 客户端配置安装成功")

if __name__ == "__main__":
    test_interactive_installation()