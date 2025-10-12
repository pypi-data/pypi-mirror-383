#!/usr/bin/env python3
"""测试安装器路径查找逻辑"""

import sys
from pathlib import Path

def test_path_finding():
    """测试路径查找逻辑"""
    print("=== 测试安装器路径查找逻辑 ===")
    
    # 模拟安装器的路径查找逻辑
    print(f"1. 当前工作目录: {Path.cwd()}")
    print(f"2. 安装器文件路径: {Path(__file__)}")
    
    # 检查当前工作目录的.trae/rules/commands
    source_commands_dir = Path.cwd() / '.trae' / 'rules' / 'commands'
    print(f"3. 检查路径: {source_commands_dir}")
    print(f"   存在: {source_commands_dir.exists()}")
    if source_commands_dir.exists():
        print(f"   文件列表: {list(source_commands_dir.glob('*.md'))}")
    
    # 检查安装器所在目录的上级目录
    installer_path = Path(__file__)
    print(f"4. 安装器路径: {installer_path}")
    print(f"   是否在.venv目录中: {'.venv' in str(installer_path)}")
    
    if '.venv' in str(installer_path):
        print("5. 在打包环境中，向上查找项目根目录...")
        current_path = installer_path
        while current_path.parent != current_path:  # 直到根目录
            test_path = current_path / '.trae' / 'rules' / 'commands'
            print(f"   检查路径: {test_path}")
            print(f"   存在: {test_path.exists()}")
            if test_path.exists():
                print(f"   ✅ 找到命令文档目录: {test_path}")
                print(f"   文件列表: {list(test_path.glob('*.md'))}")
                break
            current_path = current_path.parent
    
    print("=== 测试完成 ===")

if __name__ == "__main__":
    test_path_finding()