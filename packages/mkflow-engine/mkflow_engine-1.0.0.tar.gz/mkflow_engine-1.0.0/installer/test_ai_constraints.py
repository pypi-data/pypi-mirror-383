#!/usr/bin/env python3
"""
测试AI提示词约束文件生成功能

这个脚本用于验证安装器是否能正确生成符合要求的AI提示词约束文件。
"""

import os
import sys
import shutil
from pathlib import Path

def test_ai_constraints_generation():
    """测试AI提示词约束文件生成功能"""
    print("🧠 开始测试AI提示词约束文件生成...")
    
    # 添加项目根目录到Python路径
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # 导入安装器
    from installer.custom_installer import CustomInstaller
    
    # 创建测试目录
    test_dir = project_root / "test-ai-constraints"
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True)
    
    try:
        # 切换到测试目录
        original_cwd = os.getcwd()
        os.chdir(test_dir)
        
        print(f"📁 测试目录: {test_dir}")
        
        # 创建安装器实例
        installer = CustomInstaller('.')
        
        # 测试不同客户端的约束文件生成
        clients = ['trae', 'cursor', 'claude', 'default']
        
        for client in clients:
            print(f"\n🔧 测试 {client.upper()} 客户端约束文件...")
            
            # 生成约束内容
            constraints_content = installer._generate_constraints_content(client)
            
            # 验证内容
            required_sections = [
                "角色定义",
                "可用命令约束", 
                "回答策略约束",
                "技术约束",
                "特殊情况处理"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in constraints_content:
                    missing_sections.append(section)
            
            if missing_sections:
                print(f"❌ {client.upper()} 客户端约束文件缺少章节: {missing_sections}")
            else:
                print(f"✅ {client.upper()} 客户端约束文件结构完整")
            
            # 验证命令约束
            required_commands = [
                "/init", "/stage", "/step", "/feedback", 
                "/pointer", "/end", "/help", "/parse", "/run"
            ]
            
            missing_commands = []
            for command in required_commands:
                if command not in constraints_content:
                    missing_commands.append(command)
            
            if missing_commands:
                print(f"❌ {client.upper()} 客户端约束文件缺少命令: {missing_commands}")
            else:
                print(f"✅ {client.upper()} 客户端约束文件命令完整")
            
            # 验证策略约束
            strategy_keywords = [
                "命令优先原则", "结构化响应", "上下文保持", "错误处理"
            ]
            
            missing_strategies = []
            for strategy in strategy_keywords:
                if strategy not in constraints_content:
                    missing_strategies.append(strategy)
            
            if missing_strategies:
                print(f"❌ {client.upper()} 客户端约束文件缺少策略: {missing_strategies}")
            else:
                print(f"✅ {client.upper()} 客户端约束文件策略完整")
            
            # 保存约束文件
            constraints_file = test_dir / f"{client}_constraints.md"
            with open(constraints_file, 'w', encoding='utf-8') as f:
                f.write(constraints_content)
            
            print(f"📄 约束文件已保存: {constraints_file}")
        
        print("\n🎉 AI提示词约束文件生成测试完成！")
        
        # 显示示例约束文件内容
        print("\n📋 示例约束文件内容预览:")
        print("="*60)
        sample_content = installer._generate_constraints_content('trae')
        lines = sample_content.split('\n')[:20]  # 显示前20行
        for line in lines:
            print(line)
        print("... (内容截断)")
        print("="*60)
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 恢复原始工作目录
        os.chdir(original_cwd)
        
        # 清理测试目录（忽略权限错误）
        if test_dir.exists():
            try:
                shutil.rmtree(test_dir)
                print("🧹 测试目录已清理")
            except PermissionError:
                print("⚠️  部分文件无法删除（权限限制），但测试已完成")
            except Exception as e:
                print(f"⚠️  清理过程中出现错误: {e}")

def test_full_installation_with_constraints():
    """测试完整安装过程包含约束文件生成"""
    print("\n🚀 开始测试完整安装过程...")
    
    # 添加项目根目录到Python路径
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # 导入安装器
    from installer.custom_installer import CustomInstaller
    
    # 创建测试目录
    test_dir = project_root / "test-full-install"
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True)
    
    try:
        # 切换到测试目录
        original_cwd = os.getcwd()
        os.chdir(test_dir)
        
        print(f"📁 测试目录: {test_dir}")
        
        # 创建安装器实例并安装
        installer = CustomInstaller('.')
        installer.install_package()
        
        # 检查约束文件是否生成（支持多种客户端路径）
        possible_rules_dirs = [
            test_dir / 'rules',  # 默认路径
            test_dir / '.trae' / 'rules',  # Trae客户端路径
            test_dir / '.cursor' / 'rules',  # Cursor客户端路径
            test_dir / '.claude' / 'rules'  # Claude客户端路径
        ]
        
        constraints_file = None
        for rules_dir in possible_rules_dirs:
            potential_file = rules_dir / 'ide_agent_constraints.md'
            if potential_file.exists():
                constraints_file = potential_file
                break
        
        if constraints_file and constraints_file.exists():
            print("✅ AI提示词约束文件已生成")
            
            # 读取并验证约束文件内容
            with open(constraints_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 验证关键内容
            if "AI提示词约束" in content and "命令优先原则" in content:
                print("✅ 约束文件内容符合要求")
            else:
                print("❌ 约束文件内容不符合要求")
                
            # 显示约束文件路径
            print(f"📄 约束文件位置: {constraints_file}")
        else:
            print("❌ AI提示词约束文件未生成")
            # 列出所有可能的目录来帮助调试
            print("🔍 检查的目录:")
            for rules_dir in possible_rules_dirs:
                print(f"   - {rules_dir}: {'存在' if rules_dir.exists() else '不存在'}")
            
        print("🎉 完整安装测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 恢复原始工作目录
        os.chdir(original_cwd)
        
        # 清理测试目录（忽略权限错误）
        if test_dir.exists():
            try:
                shutil.rmtree(test_dir)
                print("🧹 测试目录已清理")
            except PermissionError:
                print("⚠️  部分文件无法删除（权限限制），但测试已完成")
            except Exception as e:
                print(f"⚠️  清理过程中出现错误: {e}")

if __name__ == "__main__":
    test_ai_constraints_generation()
    test_full_installation_with_constraints()