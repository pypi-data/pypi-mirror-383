#!/usr/bin/env python3
"""
自动化安装测试脚本
用于验证MK-FLOW工作流引擎安装器是否正常工作
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def test_installer():
    """测试安装器功能"""
    
    # 切换到test-installation目录
    test_dir = Path(__file__).parent / "test-installation"
    os.chdir(test_dir)
    
    print("🔧 开始测试MK-FLOW安装器...")
    
    # 检查是否已安装mkflow-engine
    try:
        # 检查虚拟环境中是否有安装器脚本
        scripts_dir = test_dir / ".venv" / "Scripts"
        installer_exe = scripts_dir / "mkflow-engine-install.exe"
        
        if not installer_exe.exists():
            print("❌ 安装器脚本不存在，需要先安装mkflow-engine包")
            return False
            
        print("✅ 安装器脚本已存在")
        
        # 运行安装器（非交互式模式）
        print("🚀 启动安装器...")
        
        # 使用subprocess运行安装器
        result = subprocess.run(
            [str(installer_exe)],
            capture_output=True,
            text=True,
            input="y\n",  # 自动输入y确认安装
            timeout=30
        )
        
        print("📋 安装器输出:")
        print(result.stdout)
        
        if result.returncode != 0:
            print(f"❌ 安装器执行失败，错误信息:")
            print(result.stderr)
            return False
            
        print("✅ 安装器执行成功")
        
        # 检查是否创建了.moke-core目录
        moke_core_dir = test_dir / ".moke-core"
        if moke_core_dir.exists():
            print("✅ .moke-core目录已创建")
            
            # 检查目录结构
            print("📁 检查目录结构:")
            for item in moke_core_dir.iterdir():
                print(f"   - {item.name}")
                
            # 检查rules目录
            rules_dir = moke_core_dir / "rules"
            if rules_dir.exists():
                print("✅ rules目录已创建")
                
                # 检查commands目录
                commands_dir = rules_dir / "commands"
                if commands_dir.exists():
                    print("✅ commands目录已创建")
                    
                    # 检查命令文档文件
                    command_files = list(commands_dir.glob("*_command.md"))
                    if command_files:
                        print(f"✅ 找到 {len(command_files)} 个命令文档文件")
                        for file in command_files:
                            print(f"   - {file.name}")
                    else:
                        print("❌ 未找到命令文档文件")
                        return False
                else:
                    print("❌ commands目录未创建")
                    return False
            else:
                print("❌ rules目录未创建")
                return False
                
        else:
            print("❌ .moke-core目录未创建")
            return False
            
        print("🎉 安装器测试通过！所有功能正常")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ 安装器执行超时")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("MK-FLOW 工作流引擎安装器自动化测试")
    print("=" * 60)
    
    success = test_installer()
    
    print("\n" + "=" * 60)
    if success:
        print("🎊 测试结果: 通过")
        sys.exit(0)
    else:
        print("💥 测试结果: 失败")
        sys.exit(1)

if __name__ == "__main__":
    main()