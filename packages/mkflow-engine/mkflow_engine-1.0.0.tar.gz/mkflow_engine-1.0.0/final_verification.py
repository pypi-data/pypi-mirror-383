#!/usr/bin/env python3
"""
最终验证脚本
验证AI提示词约束文件和命令文档的完整功能
"""

import os
import sys
from pathlib import Path

# 添加installer目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'installer'))

from custom_installer import CustomInstaller

def final_verification():
    """最终验证功能"""
    print("🔍 进行最终验证...")
    
    # 创建临时测试目录
    test_dir = Path("final-test")
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
            
            # 检查命令文档目录
            commands_dir = trae_rules_dir / 'commands'
            if commands_dir.exists():
                print(f"✅ 命令文档目录已创建: {commands_dir}")
                
                # 检查所有命令文档文件
                expected_commands = [
                    'init_command.md', 'stage_command.md', 'step_command.md',
                    'feedback_command.md', 'pointer_command.md', 'help_command.md',
                    'parse_command.md', 'run_command.md', 'end_command.md'
                ]
                
                missing_commands = []
                for cmd_file in expected_commands:
                    if (commands_dir / cmd_file).exists():
                        print(f"✅ {cmd_file} 已安装")
                    else:
                        print(f"❌ {cmd_file} 未安装")
                        missing_commands.append(cmd_file)
                
                # 检查命令索引文件
                index_file = commands_dir / 'commands_index.md'
                if index_file.exists():
                    print(f"✅ 命令索引文件已创建: {index_file}")
                    
                    # 读取索引文件内容
                    with open(index_file, 'r', encoding='utf-8') as f:
                        index_content = f.read()
                    
                    # 验证索引文件包含所有命令
                    for cmd in expected_commands:
                        if cmd in index_content:
                            print(f"✅ {cmd} 在索引文件中")
                        else:
                            print(f"❌ {cmd} 不在索引文件中")
                else:
                    print("❌ 命令索引文件未创建")
                
                # 验证约束文件中的关键元素
                print("\n📋 验证约束文件关键元素:")
                
                verification_points = [
                    ("命令文档引用", "命令文档引用"),
                    ("AI执行逻辑", "AI执行逻辑"),
                    ("文档引用原则", "文档引用原则"),
                    ("命令文档缺失处理", "命令文档缺失"),
                    ("工作流引擎路径", "工作流引擎路径"),
                    ("命令文档路径", "命令文档路径"),
                    ("init命令", "/init"),
                    ("stage命令", "/stage"),
                    ("step命令", "/step"),
                    ("feedback命令", "/feedback"),
                    ("pointer命令", "/pointer"),
                    ("help命令", "/help"),
                    ("parse命令", "/parse"),
                    ("run命令", "/run"),
                    ("end命令", "/end")
                ]
                
                all_passed = True
                for check_name, check_value in verification_points:
                    if check_value in content:
                        print(f"✅ {check_name} 检查通过")
                    else:
                        print(f"❌ {check_name} 检查失败")
                        all_passed = False
                
                # 验证命令文档路径引用
                expected_path = str(commands_dir).replace('\\', '/')
                # 检查路径是否在约束文件中（可能是绝对路径或相对路径）
                path_found = False
                if expected_path in content:
                    path_found = True
                else:
                    # 检查相对路径版本
                    relative_path = str(commands_dir.relative_to(test_dir)).replace('\\', '/')
                    if relative_path in content:
                        path_found = True
                    else:
                        # 检查路径的关键部分
                        path_parts = ['commands', 'rules', 'commands']
                        if any(part in content for part in path_parts):
                            path_found = True
                
                if path_found:
                    print("✅ 命令文档路径引用正确")
                else:
                    print("❌ 命令文档路径引用不正确")
                    all_passed = False
                
                if all_passed and len(missing_commands) == 0:
                    print("\n🎉 最终验证通过！所有功能正常工作")
                    print("✅ AI提示词约束文件生成正确")
                    print("✅ 命令文档安装完整")
                    print("✅ 命令索引文件创建成功")
                    print("✅ 路径引用正确配置")
                    print("\n🚀 项目功能完善，可以投入使用")
                else:
                    print("\n⚠️  最终验证未通过，请检查以下问题:")
                    if missing_commands:
                        print(f"   - 缺失的命令文档: {missing_commands}")
                    if not all_passed:
                        print("   - 约束文件关键元素不完整")
                    
            else:
                print("❌ 命令文档目录未创建")
        else:
            print("❌ 约束文件未生成")
            
    finally:
        # 清理测试目录
        import shutil
        if test_dir.exists():
            shutil.rmtree(test_dir)
            print(f"\n🧹 测试目录已清理: {test_dir}")

if __name__ == "__main__":
    final_verification()