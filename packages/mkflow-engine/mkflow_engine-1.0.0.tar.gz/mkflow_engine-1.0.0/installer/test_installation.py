"""
IDE Agent工作流引擎 - 安装测试脚本

测试自定义安装器的功能
"""

import os
import tempfile
import shutil
from pathlib import Path
from custom_installer import CustomInstaller, ClientDetector


def test_client_detection():
    """测试客户端检测功能"""
    print("🧪 测试客户端检测功能...")
    
    # 创建临时目录模拟不同客户端环境
    with tempfile.TemporaryDirectory() as temp_dir:
        # 测试Trae客户端
        trae_dir = Path(temp_dir) / "trae_test"
        trae_dir.mkdir()
        (trae_dir / ".trae").mkdir()
        
        detector = ClientDetector()
        client = detector.detect_client(str(trae_dir))
        assert client == 'trae', f"Expected 'trae', got '{client}'"
        print("✅ Trae客户端检测成功")
        
        # 测试Cursor客户端
        cursor_dir = Path(temp_dir) / "cursor_test"
        cursor_dir.mkdir()
        (cursor_dir / ".cursor").mkdir()
        
        client = detector.detect_client(str(cursor_dir))
        assert client == 'cursor', f"Expected 'cursor', got '{client}'"
        print("✅ Cursor客户端检测成功")
        
        # 测试Claude客户端
        claude_dir = Path(temp_dir) / "claude_test"
        claude_dir.mkdir()
        (claude_dir / ".claude").mkdir()
        
        client = detector.detect_client(str(claude_dir))
        assert client == 'claude', f"Expected 'claude', got '{client}'"
        print("✅ Claude客户端检测成功")
        
        # 测试默认客户端（无特定目录）
        default_dir = Path(temp_dir) / "default_test"
        default_dir.mkdir()
        
        client = detector.detect_client(str(default_dir))
        assert client is None, f"Expected None, got '{client}'"
        print("✅ 默认客户端检测成功")


def test_rules_path_generation():
    """测试rules路径生成功能"""
    print("\n🧪 测试rules路径生成功能...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        detector = ClientDetector()
        
        # 测试Trae客户端路径
        rules_path = detector.get_rules_path('trae', temp_dir)
        expected_path = Path(temp_dir) / '.trae' / 'rules'
        assert rules_path == expected_path, f"Expected {expected_path}, got {rules_path}"
        print("✅ Trae客户端rules路径生成成功")
        
        # 测试Cursor客户端路径
        rules_path = detector.get_rules_path('cursor', temp_dir)
        expected_path = Path(temp_dir) / '.cursor' / 'rules'
        assert rules_path == expected_path, f"Expected {expected_path}, got {rules_path}"
        print("✅ Cursor客户端rules路径生成成功")
        
        # 测试Claude客户端路径
        rules_path = detector.get_rules_path('claude', temp_dir)
        expected_path = Path(temp_dir) / '.claude' / 'rules'
        assert rules_path == expected_path, f"Expected {expected_path}, got {rules_path}"
        print("✅ Claude客户端rules路径生成成功")


def test_installer_creation():
    """测试安装器创建功能"""
    print("\n🧪 测试安装器创建功能...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建安装器实例
        installer = CustomInstaller(temp_dir)
        
        # 验证安装目录
        expected_install_dir = Path(temp_dir) / '.moke-core'
        assert installer.install_dir == expected_install_dir
        print("✅ 安装目录设置成功")
        
        # 验证基础目录
        assert installer.base_dir == Path(temp_dir)
        print("✅ 基础目录设置成功")
        
        # 验证客户端检测器
        assert hasattr(installer, 'client_detector')
        print("✅ 客户端检测器初始化成功")


def test_constraints_file_generation():
    """测试约束文件生成功能"""
    print("\n🧪 测试约束文件生成功能...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        installer = CustomInstaller(temp_dir)
        
        # 测试约束文件内容生成
        content = installer._generate_constraints_content('trae')
        
        # 验证基本内容
        assert "# IDE Agent工作流引擎 - 约束语句" in content
        assert "安装目录" in content
        assert "客户端类型" in content
        assert "TRAE" in content.upper()
        print("✅ 约束文件内容生成成功")


def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行IDE Agent工作流引擎安装器测试...\n")
    
    try:
        test_client_detection()
        test_rules_path_generation()
        test_installer_creation()
        test_constraints_file_generation()
        
        print("\n🎉 所有测试通过！安装器功能正常。")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)