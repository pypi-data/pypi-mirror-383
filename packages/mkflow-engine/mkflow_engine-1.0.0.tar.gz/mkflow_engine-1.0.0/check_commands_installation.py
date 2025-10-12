#!/usr/bin/env python3
"""
检查命令文档安装情况
验证AI提示词约束文件中的命令文档引用是否正确
"""

import os
import sys
from pathlib import Path

# 添加installer目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'installer'))

from custom_installer import CustomInstaller

def check_commands_installation():
    """检查命令文档安装情况"""
    print("🔍 检查命令文档安装情况...")
    
    # 创建临时测试目录
    test_dir = Path("test-commands-install")
    test_dir.mkdir(exist_ok=True)
    
    try:
        # 创建CustomInstaller实例
        installer = CustomInstaller(str(test_dir))
        
        # 模拟TRAE客户端环境
        trae_rules_dir = test_dir / '.trae' / 'rules'
        trae_rules_dir.mkdir(parents=True, exist_ok=True)
        
        # 安装约束文件和命令文档
        installer._install_constraints_file('trae')
        
        # 检查约束文件内容
        constraints_file = trae_rules_dir / 'ide_agent_constraints.md'
        if constraints_file.exists():
            print(f"✅ 约束文件已生成: {constraints_file}")
            
            # 读取约束文件内容
            with open(constraints_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查命令文档引用
            commands_dir = trae_rules_dir / 'commands'
            if commands_dir.exists():
                print(f"✅ 命令文档目录已创建: {commands_dir}")
                
                # 检查命令文档文件
                command_files = list(commands_dir.glob('*_command.md'))
                print(f"📄 找到 {len(command_files)} 个命令文档文件:")
                for cmd_file in command_files:
                    print(f"   - {cmd_file.name}")
                
                # 检查命令索引文件
                index_file = commands_dir / 'commands_index.md'
                if index_file.exists():
                    print(f"✅ 命令索引文件已创建: {index_file}")
                    
                    # 读取索引文件内容
                    with open(index_file, 'r', encoding='utf-8') as f:
                        index_content = f.read()
                    
                    # 验证约束文件中的命令文档引用
                    expected_path = str(commands_dir).replace('\\', '/')
                    if expected_path in content:
                        print("✅ 约束文件中命令文档路径引用正确")
                    else:
                        print("❌ 约束文件中命令文档路径引用不正确")
                        
                    # 检查关键元素
                    check_points = [
                        ("命令文档引用", "命令文档路径"),
                        ("命令文档路径", expected_path),
                        ("命令索引文件", "commands_index.md"),
                        ("init命令文档", "init_command.md"),
                        ("stage命令文档", "stage_command.md"),
                        ("step命令文档", "step_command.md"),
                        ("AI执行逻辑", "AI执行逻辑"),
                        ("文档引用原则", "文档引用原则")
                    ]
                    
                    all_passed = True
                    for check_name, check_value in check_points:
                        if check_value in content:
                            print(f"✅ {check_name} 检查通过")
                        else:
                            print(f"❌ {check_name} 检查失败")
                            all_passed = False
                    
                    if all_passed:
                        print("🎉 所有检查点通过！AI提示词约束文件生成正确")
                    else:
                        print("⚠️  部分检查点未通过，请检查约束文件生成逻辑")
                        
                    # 显示约束文件中的命令文档引用部分
                    print("\n📋 约束文件中的命令文档引用:")
                    lines = content.split('\n')
                    in_commands_section = False
                    for i, line in enumerate(lines):
                        if '命令文档引用' in line:
                            in_commands_section = True
                        if in_commands_section and line.strip() and not line.startswith('#'):
                            if '###' in line and '命令文档引用' not in line:
                                break
                            print(f"   {line}")
                            
                else:
                    print("❌ 命令索引文件未创建")
            else:
                print("❌ 命令文档目录未创建")
        else:
            print("❌ 约束文件未生成")
            
    finally:
        # 清理测试目录
        import shutil
        if test_dir.exists():
            shutil.rmtree(test_dir)
            print(f"🧹 测试目录已清理: {test_dir}")

if __name__ == "__main__":
    check_commands_installation()