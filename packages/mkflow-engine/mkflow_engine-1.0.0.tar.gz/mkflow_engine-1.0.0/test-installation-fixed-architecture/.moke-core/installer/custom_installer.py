"""
MK-FLOW 工作流引擎 - 自定义安装器

支持将包安装到指定目录，并根据客户端类型将约束文件放置到对应的rules目录
提供扩展包选项：代码开发工作流扩展包、内容创作SOP工作流扩展包
"""

import os
import re
import shutil
import sys
from pathlib import Path
from typing import Optional, Dict, List

# 蓝色主题颜色代码
class Colors:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# 扩展包类型
class ExtensionPackages:
    CODE_DEVELOPMENT = "code_development"
    CONTENT_CREATION = "content_creation"
    NONE = "none"


class ClientDetector:
    """客户端检测器"""
    
    CLIENT_PATTERNS = {
        'trae': r'\.trae',
        'cursor': r'\.cursor', 
        'claude': r'\.claude'
    }
    
    @classmethod
    def detect_client(cls, base_path: str) -> Optional[str]:
        """检测当前目录的客户端类型"""
        base_path = Path(base_path).resolve()
        
        # 检查当前目录及其父目录
        for path in [base_path] + list(base_path.parents):
            for client, pattern in cls.CLIENT_PATTERNS.items():
                if any(re.search(pattern, str(item.name), re.IGNORECASE) 
                       for item in path.iterdir() if item.is_dir()):
                    return client
        
        return None
    
    @classmethod
    def get_rules_path(cls, client: str, base_path: str) -> Path:
        """获取对应客户端的rules目录路径"""
        base_path = Path(base_path).resolve()
        
        if client == 'trae':
            return base_path / '.trae' / 'rules'
        elif client == 'cursor':
            return base_path / '.cursor' / 'rules'
        elif client == 'claude':
            return base_path / '.claude' / 'rules'
        else:
            raise ValueError(f"不支持的客户端类型: {client}")


class CustomInstaller:
    """自定义安装器"""
    
    def __init__(self, install_dir: str = None):
        self.install_dir = Path(install_dir or os.getcwd()) / '.moke-core'
        self.base_dir = Path(install_dir or os.getcwd())
        self.client_detector = ClientDetector()
    
    def install_package(self, package_path: str = None):
        """安装包到指定目录"""
        # 显示MK-FLOW标识和欢迎界面
        if not self._print_welcome_header():
            return  # 用户取消安装
        
        # 选择扩展包
        selected_package = self._select_extension_package()
        
        # 检测客户端类型
        client = self.client_detector.detect_client(self.base_dir)
        if client:
            print(f"{Colors.GREEN}✅ 检测到 {client.upper()} 客户端环境{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  未检测到特定客户端，使用默认配置{Colors.END}")
            client = 'default'
        
        # 创建安装目录
        self.install_dir.mkdir(parents=True, exist_ok=True)
        print(f"{Colors.BLUE}📁 创建安装目录: {self.install_dir}{Colors.END}")
        
        # 安装包文件
        self._install_package_files(package_path)
        
        # 安装约束文件
        self._install_constraints_file(client)
        
        # 创建客户端适配文件
        self._create_client_adapter(client)
        
        # 安装扩展包
        if selected_package != ExtensionPackages.NONE:
            self._install_extension_package(selected_package)
        
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 MK-FLOW 工作流引擎安装完成！{Colors.END}")
        self._print_installation_summary(client, selected_package)
    
    def _print_welcome_header(self):
        """打印欢迎界面和MK-FLOW标识"""
        # 大banner设计，参考BMAD安装器
        banner = f"""
{Colors.BLUE}{Colors.BOLD}
 ███╗   ███╗██╗  ██╗     ███████╗██╗      ██████╗ ██╗    ██╗
 ████╗ ████║██║ ██╔╝     ██╔════╝██║     ██╔═══██╗██║    ██║
 ██╔████╔██║█████╔╝█████╗█████╗  ██║     ██║   ██║██║ █╗ ██║
 ██║╚██╔╝██║██╔═██╗╚════╝██╔══╝  ██║     ██║   ██║██║███╗██║
 ██║ ╚═╝ ██║██║  ██╗     ██║     ███████╗╚██████╔╝╚███╔███╔╝
 ╚═╝     ╚═╝╚═╝  ╚═╝     ╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝ 
{Colors.END}

{Colors.CYAN}{Colors.BOLD}🚀 Universal Workflow Engine for AI Agent Development{Colors.END}
{Colors.CYAN}✨ Installer v1.0.0{Colors.END}
"""
        print(banner)
        
        # 显示默认安装位置
        default_install_path = self.install_dir.resolve()
        print(f"{Colors.YELLOW}📁 默认安装位置: {default_install_path}{Colors.END}")
        print(f"{Colors.YELLOW}💡 如需修改安装目录，请按 Ctrl+C 退出后重新运行{Colors.END}")
        print()
        
        # 确认继续安装
        try:
            # 检查是否有标准输入（管道输入）
            import sys
            if not sys.stdin.isatty():
                # 有管道输入，读取第一行并处理编码问题
                response = sys.stdin.readline().strip().lower()
                # 处理Windows命令行中的UTF-8 BOM编码问题
                if response.startswith('\ufeff'):  # UTF-8 BOM
                    response = response[1:]
                # 处理Windows PowerShell中的编码问题
                if response == '锘縴':  # Windows PowerShell中的'y'编码问题
                    response = 'y'
                print(f"{Colors.BLUE}是否继续安装？(y/n): {response}{Colors.END}")
            else:
                # 交互式输入
                response = input(f"{Colors.BLUE}是否继续安装？(y/n): {Colors.END}").strip().lower()
            
            if response not in ['y', 'yes']:
                print(f"{Colors.YELLOW}安装已取消{Colors.END}")
                return False  # 用户取消安装
            else:
                return True  # 用户确认继续安装
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}安装已取消{Colors.END}")
            return False  # 用户取消安装·   ·
    
    def _select_extension_package(self):
        """选择扩展包"""
        print(f"{Colors.BLUE}{Colors.BOLD}请选择要安装的扩展包：{Colors.END}")
        print(f"{Colors.CYAN}1. 代码开发工作流扩展包{Colors.END}")
        print(f"   - 包含代码开发相关的模板和工具")
        print(f"{Colors.CYAN}2. 内容创作SOP工作流扩展包{Colors.END}")
        print(f"   - 包含内容创作的标准操作流程")
        print(f"{Colors.CYAN}3. 不安装扩展包{Colors.END}")
        print(f"   - 仅安装核心工作流引擎")
        print()
        
        # 检查是否有标准输入（管道输入）
        import sys
        has_pipe_input = not sys.stdin.isatty()
        
        while True:
            try:
                if has_pipe_input:
                    # 有管道输入，使用默认选择（不安装扩展包）
                    choice = '3'
                    print(f"{Colors.BLUE}请输入选择 (1/2/3): {choice}{Colors.END}")
                else:
                    # 交互式输入
                    choice = input(f"{Colors.BLUE}请输入选择 (1/2/3): {Colors.END}").strip()
                
                if choice == '1':
                    print(f"{Colors.GREEN}✅ 已选择：代码开发工作流扩展包{Colors.END}")
                    return ExtensionPackages.CODE_DEVELOPMENT
                elif choice == '2':
                    print(f"{Colors.GREEN}✅ 已选择：内容创作SOP工作流扩展包{Colors.END}")
                    return ExtensionPackages.CONTENT_CREATION
                elif choice == '3':
                    print(f"{Colors.YELLOW}⚠️  已选择：不安装扩展包{Colors.END}")
                    return ExtensionPackages.NONE
                else:
                    print(f"{Colors.RED}❌ 无效选择，请输入1、2或3{Colors.END}")
                    if has_pipe_input:
                        # 管道输入模式下，无效选择也使用默认值
                        choice = '3'
                        print(f"{Colors.YELLOW}⚠️  使用默认选择：不安装扩展包{Colors.END}")
                        return ExtensionPackages.NONE
            except (KeyboardInterrupt, EOFError):
                if has_pipe_input:
                    # 管道输入模式下，EOF错误使用默认选择
                    print(f"{Colors.YELLOW}⚠️  使用默认选择：不安装扩展包{Colors.END}")
                    return ExtensionPackages.NONE
                else:
                    print(f"\n{Colors.RED}安装已取消{Colors.END}")
                    sys.exit(1)
    
    def _install_extension_package(self, package_type: str):
        """安装扩展包"""
        print(f"{Colors.BLUE}📦 开始安装扩展包...{Colors.END}")
        
        # 创建扩展包目录
        extensions_dir = self.install_dir / "extensions"
        extensions_dir.mkdir(exist_ok=True)
        
        if package_type == ExtensionPackages.CODE_DEVELOPMENT:
            self._install_code_development_package(extensions_dir)
        elif package_type == ExtensionPackages.CONTENT_CREATION:
            self._install_content_creation_package(extensions_dir)
    
    def _install_code_development_package(self, extensions_dir: Path):
        """安装代码开发工作流扩展包"""
        print(f"{Colors.BLUE}🔧 安装代码开发工作流扩展包...{Colors.END}")
        
        # 创建代码开发扩展包目录结构
        code_dev_dir = extensions_dir / "code_development"
        code_dev_dir.mkdir(exist_ok=True)
        
        # 创建模板文件
        templates_dir = code_dev_dir / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        # 创建示例工作流
        example_workflow = templates_dir / "code_review_workflow.json"
        example_workflow.write_text("""{
    "name": "代码审查工作流",
    "description": "自动化代码审查流程",
    "stages": [
        {
            "name": "代码分析",
            "steps": ["代码质量检查", "安全漏洞扫描", "性能分析"]
        }
    ]
}""")
        
        print(f"{Colors.GREEN}✅ 代码开发工作流扩展包安装完成{Colors.END}")
    
    def _install_content_creation_package(self, extensions_dir: Path):
        """安装内容创作SOP工作流扩展包"""
        print(f"{Colors.BLUE}📝 安装内容创作SOP工作流扩展包...{Colors.END}")
        
        # 创建内容创作扩展包目录结构
        content_dir = extensions_dir / "content_creation"
        content_dir.mkdir(exist_ok=True)
        
        # 创建SOP模板
        sop_dir = content_dir / "sop_templates"
        sop_dir.mkdir(exist_ok=True)
        
        # 创建内容创作工作流示例
        content_workflow = sop_dir / "blog_post_workflow.json"
        content_workflow.write_text("""{
    "name": "博客文章创作工作流",
    "description": "标准化博客文章创作流程",
    "stages": [
        {
            "name": "主题规划",
            "steps": ["确定主题", "研究关键词", "制定大纲"]
        }
    ]
}""")
        
        print(f"{Colors.GREEN}✅ 内容创作SOP工作流扩展包安装完成{Colors.END}")
    
    def _install_package_files(self, package_path: str = None):
        """安装包文件到.moke-core目录"""
        if package_path and os.path.exists(package_path):
            # 从指定路径安装
            print(f"📦 从本地路径安装: {package_path}")
            self._copy_package_from_path(package_path)
        else:
            # 使用uv安装
            print("📦 使用uv安装最新版本...")
            self._install_with_uv()
    
    def _install_with_uv(self):
        """使用uv安装包"""
        try:
            import subprocess
            
            # 检查uv是否可用
            result = subprocess.run(['uv', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ uv未安装，请先安装uv: https://github.com/astral-sh/uv")
                return
            
            # 检查本地是否有构建的包文件
            # 从当前目录向上查找项目根目录的dist目录
            current_path = Path.cwd()
            dist_dir = None
            
            # 向上查找包含pyproject.toml的项目根目录
            for path in [current_path] + list(current_path.parents):
                potential_dist = path / 'dist'
                pyproject_toml = path / 'pyproject.toml'
                
                if potential_dist.exists() and pyproject_toml.exists():
                    dist_dir = potential_dist
                    print(f"📦 使用本地dist目录: {dist_dir}")
                    break
            
            # 如果没找到，使用安装器所在目录的dist
            if dist_dir is None:
                dist_dir = Path(__file__).parent.parent / 'dist'
            
            if dist_dir.exists():
                # 查找最新的wheel包 - 注意包名使用下划线而不是连字符
                wheel_files = list(dist_dir.glob('mkflow_engine-*.whl'))
                if wheel_files:
                    # 使用最新的wheel包
                    latest_wheel = max(wheel_files, key=lambda x: x.stat().st_mtime)
                    cmd = [
                        'uv', 'pip', 'install', str(latest_wheel),
                        '--target', str(self.install_dir)
                    ]
                    print(f"📦 使用本地包安装: {latest_wheel.name}")
                else:
                    # 从PyPI安装
                    cmd = [
                        'uv', 'pip', 'install', 'mkflow_engine',
                        '--target', str(self.install_dir)
                    ]
                    print("📦 使用PyPI包安装")
            else:
                # 从PyPI安装
                cmd = [
                    'uv', 'pip', 'install', 'mkflow_engine',
                    '--target', str(self.install_dir)
                ]
                print("📦 使用PyPI包安装")
            
            print(f"🔧 执行命令: {' '.join(cmd)}")
            # 使用更安全的方法处理subprocess调用，避免编码问题
            try:
                # 不使用text=True，直接处理字节流
                result = subprocess.run(cmd, capture_output=True, text=False)
                
                # 手动处理输出编码
                stdout = result.stdout.decode('utf-8', errors='ignore')
                stderr = result.stderr.decode('utf-8', errors='ignore')
                
                if result.returncode == 0:
                    print("✅ 包安装成功")
                    if stdout:
                        print(f"📋 安装输出: {stdout}")
                else:
                    print(f"❌ 包安装失败: {stderr}")
            except Exception as e:
                print(f"❌ 包安装过程中出错: {e}")
                # 即使有编码错误，也尝试继续安装
                print("⚠️  继续安装过程...")
                
        except Exception as e:
            print(f"❌ 安装过程中出错: {e}")
    
    def _copy_package_from_path(self, package_path: str):
        """从本地路径复制包文件"""
        try:
            source_path = Path(package_path)
            
            if source_path.is_dir():
                # 复制整个目录
                shutil.copytree(source_path, self.install_dir / 'mkflow_engine', 
                              dirs_exist_ok=True)
            else:
                # 复制单个文件
                shutil.copy2(source_path, self.install_dir)
                
            print("✅ 本地包文件复制完成")
        except Exception as e:
            print(f"❌ 文件复制失败: {e}")
    
    def _install_constraints_file(self, client: str):
        """安装约束文件到对应客户端的rules目录"""
        if client == 'default':
            # 默认情况下安装到当前目录的rules
            rules_dir = self.base_dir / 'rules'
        else:
            rules_dir = self.client_detector.get_rules_path(client, self.base_dir)
        
        # 创建rules目录
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        # 约束文件路径
        constraints_file = rules_dir / 'ide_agent_constraints.md'
        
        # 创建约束文件内容
        constraints_content = self._generate_constraints_content(client)
        
        # 写入约束文件
        with open(constraints_file, 'w', encoding='utf-8') as f:
            f.write(constraints_content)
        
        print(f"📄 约束文件已安装到: {constraints_file}")
        
        # 安装命令文档到rules/commands目录
        self._install_commands_documentation(rules_dir)
    
    def _install_commands_documentation(self, rules_dir: Path):
        """安装命令文档到rules目录"""
        commands_dir = rules_dir / 'commands'
        commands_dir.mkdir(parents=True, exist_ok=True)
        
        # 源命令文档目录 - 从mkflow_engine包内获取
        try:
            # 获取mkflow_engine包的安装路径
            import mkflow_engine
            package_path = Path(mkflow_engine.__file__).parent
            source_commands_dir = package_path / 'commands' / 'docs'
            print(f"🔍 从包内获取命令文档: {source_commands_dir}")
        except ImportError:
            # 如果包未安装，使用备用路径
            source_commands_dir = Path(__file__).parent.parent / 'mkflow_engine' / 'commands' / 'docs'
            print(f"🔍 使用备用路径获取命令文档: {source_commands_dir}")
        
        # 检查源命令文档目录是否存在且包含完整文档
        source_has_complete_docs = False
        if source_commands_dir.exists():
            print(f"🔍 找到命令文档目录: {source_commands_dir}")
            
            # 检查是否包含完整的9个命令文档
            required_files = [
                'init_command.md', 'stage_command.md', 'step_command.md',
                'feedback_command.md', 'pointer_command.md', 'end_command.md',
                'help_command.md', 'parse_command.md', 'run_command.md'
            ]
            
            existing_files = [f.name for f in source_commands_dir.glob('*.md')]
            missing_files = [f for f in required_files if f not in existing_files]
            
            if not missing_files:
                source_has_complete_docs = True
                print("✅ 源目录包含完整的命令文档")
            else:
                print(f"{Colors.YELLOW}⚠️ 源目录缺少命令文档: {missing_files}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️ 命令文档目录不存在: {source_commands_dir}{Colors.END}")
            print(f"🔍 当前工作目录: {Path.cwd()}")
            print(f"🔍 检查路径是否存在: {Path.cwd() / '.trae' / 'rules' / 'commands'}")
        
        # 如果源目录不存在或不完整，创建完整的默认命令文档
        if not source_has_complete_docs:
            print(f"{Colors.YELLOW}⚠️ 创建完整的默认命令文档文件{Colors.END}")
            self._create_default_command_docs(commands_dir)
        else:
            # 复制所有命令文档文件
            for md_file in source_commands_dir.glob('*.md'):
                if md_file.is_file():
                    dest_file = commands_dir / md_file.name
                    shutil.copy2(md_file, dest_file)
                    print(f"📄 命令文档已安装: {dest_file}")
        
        # 创建命令索引文件
        self._create_commands_index(commands_dir)
    
    def _create_default_command_docs(self, commands_dir: Path):
        """创建完整的默认命令文档文件"""
        
        # 1. init_command.md
        init_content = """# /init 命令文档

## 用途
初始化一个新的工作流实例。

## 触发条件
当用户请求开始新的工作流程时使用此命令。

## AI执行逻辑
1. 检测用户意图是否需要初始化工作流
2. 推荐使用此命令
3. 创建新的工作流实例

## AI执行脚本
```python
# 检测用户意图是否需要初始化工作流
if "开始" in user_input or "初始化" in user_input or "新建" in user_input:
    # 推荐使用/init命令
    return "检测到您需要初始化工作流，建议使用命令：/init project_name=\"项目名称\""

# 执行/init命令
if command == "/init":
    # 解析参数
    project_name = extract_parameter("project_name", user_input)
    
    # 创建工作流实例
    workflow = WorkflowEngine(project_name)
    
    # 返回初始化结果
    return f"✅ 工作流初始化成功！项目名称：{project_name}"
```

## 示例
```
/init project_name="新项目"
```"""
        
        # 2. stage_command.md
        stage_content = """# /stage 命令文档

## 用途
管理工作流阶段，包括添加、修改或查看阶段。

## 触发条件
当用户需要管理工作流阶段时使用此命令。

## AI执行逻辑
1. 分析用户意图确定操作类型
2. 推荐使用此命令
3. 执行相应的阶段管理操作

## AI执行脚本
```python
# 检测用户意图是否需要阶段管理
if "阶段" in user_input or "步骤" in user_input or "流程" in user_input:
    # 推荐使用/stage命令
    return "检测到您需要管理工作流阶段，建议使用命令：/stage [add|list|view|modify]"

# 执行/stage命令
if command == "/stage":
    # 解析操作类型
    operation = extract_operation(user_input)  # add, list, view, modify
    
    if operation == "add":
        stage_name = extract_parameter("name", user_input)
        # 添加新阶段
        workflow.add_stage(stage_name)
        return f"✅ 阶段添加成功：{stage_name}"
    
    elif operation == "list":
        # 列出所有阶段
        stages = workflow.list_stages()
        return f"📋 当前阶段列表：{stages}"
    
    elif operation == "view":
        stage_id = extract_parameter("id", user_input)
        # 查看阶段详情
        stage_info = workflow.view_stage(stage_id)
        return f"🔍 阶段详情：{stage_info}"
```

## 示例
```
/stage add name="需求分析"
/stage list
/stage view id=1
```"""
        
        # 3. step_command.md
        step_content = """# /step 命令文档

## 用途
执行具体的处理步骤。

## 触发条件
用户需要执行特定操作时使用此命令。

## AI执行逻辑
1. 识别用户请求的具体操作类型
2. 推荐使用此命令
3. 执行相应的步骤操作

## AI执行脚本
```python
# 检测用户意图是否需要执行步骤
if "执行" in user_input or "操作" in user_input or "处理" in user_input:
    # 推荐使用/step命令
    return "检测到您需要执行具体操作，建议使用命令：/step [execute|status|complete]"

# 执行/step命令
if command == "/step":
    # 解析操作类型
    operation = extract_operation(user_input)  # execute, status, complete
    
    if operation == "execute":
        step_name = extract_parameter("name", user_input)
        # 执行步骤
        result = workflow.execute_step(step_name)
        return f"✅ 步骤执行完成：{step_name}，结果：{result}"
    
    elif operation == "status":
        # 查看步骤状态
        status = workflow.get_step_status()
        return f"📊 当前步骤状态：{status}"
    
    elif operation == "complete":
        step_id = extract_parameter("id", user_input)
        # 标记步骤完成
        workflow.complete_step(step_id)
        return f"✅ 步骤标记完成：{step_id}"
```

## 示例
```
/step execute name="需求分析"
/step status
/step complete id=1
```"""
        
        # 4. feedback_command.md
        feedback_content = """# /feedback 命令文档

## 用途
收集和处理用户反馈。

## 触发条件
用户提供反馈或需要反馈机制时使用此命令。

## AI执行逻辑
1. 识别用户是否需要查看或提供反馈
2. 推荐使用此命令
3. 执行相应的反馈操作

## AI执行脚本
```python
# 检测用户意图是否需要反馈
if "反馈" in user_input or "评价" in user_input or "建议" in user_input:
    # 推荐使用/feedback命令
    return "检测到您需要反馈功能，建议使用命令：/feedback [provide|view|list]"

# 执行/feedback命令
if command == "/feedback":
    # 解析操作类型
    operation = extract_operation(user_input)  # provide, view, list
    
    if operation == "provide":
        feedback_text = extract_parameter("text", user_input)
        # 收集反馈
        workflow.collect_feedback(feedback_text)
        return "✅ 反馈已收集，感谢您的意见！"
    
    elif operation == "view":
        feedback_id = extract_parameter("id", user_input)
        # 查看反馈详情
        feedback = workflow.view_feedback(feedback_id)
        return f"📝 反馈详情：{feedback}"
    
    elif operation == "list":
        # 列出所有反馈
        feedbacks = workflow.list_feedbacks()
        return f"📋 反馈列表：{feedbacks}"
```

## 示例
```
/feedback provide text="功能很好用"
/feedback list
/feedback view id=1
```"""
        
        # 5. pointer_command.md
        pointer_content = """# /pointer 命令文档

## 用途
管理工作流执行指针。

## 触发条件
需要跟踪或管理执行位置时使用此命令。

## AI执行逻辑
1. 识别用户是否需要指针操作
2. 推荐使用此命令
3. 执行相应的指针管理操作

## AI执行脚本
```python
# 检测用户意图是否需要指针操作
if "位置" in user_input or "指针" in user_input or "进度" in user_input:
    # 推荐使用/pointer命令
    return "检测到您需要管理执行指针，建议使用命令：/pointer [set|get|move|reset]"

# 执行/pointer命令
if command == "/pointer":
    # 解析操作类型
    operation = extract_operation(user_input)  # set, get, move, reset
    
    if operation == "set":
        position = extract_parameter("position", user_input)
        # 设置指针位置
        workflow.set_pointer(position)
        return f"📍 指针已设置到：{position}"
    
    elif operation == "get":
        # 获取当前指针位置
        pointer = workflow.get_pointer()
        return f"📍 当前指针位置：{pointer}"
    
    elif operation == "move":
        direction = extract_parameter("direction", user_input)  # next, prev
        # 移动指针
        new_position = workflow.move_pointer(direction)
        return f"📍 指针已移动到：{new_position}"
    
    elif operation == "reset":
        # 重置指针
        workflow.reset_pointer()
        return "📍 指针已重置到初始位置"
```

## 示例
```
/pointer set position="需求分析"
/pointer get
/pointer move direction="next"
```"""
        
        # 6. end_command.md
        end_content = """# /end 命令文档

## 用途
正常结束工作流执行。

## 触发条件
工作流完成或用户要求结束时使用此命令。

## AI执行逻辑
1. 检测工作流完成状态
2. 推荐使用此命令
3. 执行工作流结束操作

## AI执行脚本
```python
# 检测用户意图是否需要结束工作流
if "结束" in user_input or "完成" in user_input or "退出" in user_input:
    # 推荐使用/end命令
    return "检测到您需要结束工作流，建议使用命令：/end"

# 执行/end命令
if command == "/end":
    # 检查工作流是否可结束
    if workflow.can_end():
        # 结束工作流
        result = workflow.end()
        return f"✅ 工作流已结束。结果：{result}"
    else:
        return "⚠️ 工作流尚未完成，无法结束。请先完成所有步骤。"
```

## 示例
```
/end
```"""
        
        # 7. help_command.md
        help_content = """# /help 命令文档

## 用途
显示可用命令和用法。

## 触发条件
用户请求帮助时使用此命令。

## AI执行逻辑
直接执行帮助命令。

## AI执行脚本
```python
# 检测用户意图是否需要帮助
if "帮助" in user_input or "help" in user_input or "命令" in user_input:
    # 直接执行/help命令
    return execute_help_command()

# 执行/help命令
if command == "/help":
    # 显示所有可用命令
    commands = workflow.list_commands()
    help_text = "📋 可用命令列表：\n"
    for cmd in commands:
        help_text += f"- {cmd['name']}: {cmd['description']}\n"
    
    return help_text
```

## 示例
```
/help
```"""
        
        # 8. parse_command.md
        parse_content = """# /parse 命令文档

## 用途
将Mermaid文件解析为工作流JSON。

## 触发条件
用户提供Mermaid文件时使用此命令。

## AI执行逻辑
1. 检测Mermaid文件存在
2. 推荐使用此命令
3. 执行解析操作

## AI执行脚本
```python
# 检测用户意图是否需要解析Mermaid
if "mermaid" in user_input.lower() or ".mmd" in user_input or "流程图" in user_input:
    # 推荐使用/parse命令
    return "检测到您需要解析Mermaid流程图，建议使用命令：/parse file=\"文件路径\""

# 执行/parse命令
if command == "/parse":
    # 解析文件路径
    file_path = extract_parameter("file", user_input)
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return f"❌ 文件不存在：{file_path}"
    
    # 解析Mermaid文件
    workflow_json = workflow.parse_mermaid(file_path)
    
    return f"✅ Mermaid文件解析成功！工作流JSON：{workflow_json}"
```

## 示例
```
/parse file="workflow.mmd"
```"""
        
        # 9. run_command.md
        run_content = """# /run 命令文档

## 用途
执行完整的工作流。

## 触发条件
用户要求运行工作流时使用此命令。

## AI执行逻辑
1. 检测工作流文件存在
2. 推荐使用此命令
3. 执行工作流运行操作

## AI执行脚本
```python
# 检测用户意图是否需要运行工作流
if "运行" in user_input or "执行" in user_input or "启动" in user_input:
    # 推荐使用/run命令
    return "检测到您需要运行工作流，建议使用命令：/run"

# 执行/run命令
if command == "/run":
    # 检查工作流是否可运行
    if workflow.is_runnable():
        # 运行工作流
        result = workflow.run()
        return f"✅ 工作流运行完成！结果：{result}"
    else:
        return "⚠️ 工作流无法运行，请检查配置和依赖。"
```

## 示例
```
/run
```"""
        
        # 创建所有命令文档文件
        command_files = [
            ('init_command.md', init_content),
            ('stage_command.md', stage_content),
            ('step_command.md', step_content),
            ('feedback_command.md', feedback_content),
            ('pointer_command.md', pointer_content),
            ('end_command.md', end_content),
            ('help_command.md', help_content),
            ('parse_command.md', parse_content),
            ('run_command.md', run_content)
        ]
        
        for filename, content in command_files:
            file_path = commands_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📄 默认命令文档已创建: {file_path}")
    
    def _create_commands_index(self, commands_dir: Path):
        """创建命令索引文件"""
        index_content = """# 工作流引擎命令索引

## 可用命令列表

以下是工作流引擎支持的所有命令，点击命令名称查看详细文档：

### 核心工作流命令
- [init_command.md](init_command.md) - `/init` 初始化工作流
- [stage_command.md](stage_command.md) - `/stage` 管理工作流阶段  
- [step_command.md](step_command.md) - `/step` 执行工作流步骤
- [feedback_command.md](feedback_command.md) - `/feedback` 提供反馈机制
- [pointer_command.md](pointer_command.md) - `/pointer` 指针管理
- [end_command.md](end_command.md) - `/end` 结束工作流

### 辅助命令
- [help_command.md](help_command.md) - `/help` 获取帮助信息
- [parse_command.md](parse_command.md) - `/parse` 解析Mermaid流程图
- [run_command.md](run_command.md) - `/run` 运行工作流

## AI执行指导

每个命令文档都包含详细的AI执行脚本，指导AI如何：
1. **检测用户意图** - 识别何时应该推荐使用特定命令
2. **解析命令参数** - 从用户输入中提取必要参数
3. **执行具体操作** - 调用相应的工作流引擎方法
4. **返回结构化响应** - 提供清晰的执行结果和下一步建议

## 使用说明

AI助手在执行工作流相关操作时，应该：
1. 根据用户意图选择合适的命令
2. 参考对应命令的详细文档和AI执行脚本
3. 按照文档中的执行逻辑操作
4. 返回结构化的响应结果

## 快速参考

| 命令 | 用途 | 触发条件 | AI执行逻辑 |
|------|------|----------|------------|
| `/init` | 初始化工作流 | 开始新工作流程 | 检测初始化意图，创建实例 |
| `/stage` | 管理阶段 | 需要阶段操作 | 分析操作类型，执行阶段管理 |
| `/step` | 执行步骤 | 需要具体操作 | 识别操作类型，执行步骤 |
| `/feedback` | 收集反馈 | 需要反馈机制 | 识别反馈需求，收集/查看反馈 |
| `/pointer` | 管理指针 | 需要跟踪位置 | 识别指针操作，管理执行位置 |
| `/end` | 结束工作流 | 工作流完成 | 检测完成状态，结束工作流 |
| `/help` | 获取帮助 | 请求帮助时 | 直接显示命令列表 |
| `/parse` | 解析流程图 | 提供Mermaid文件时 | 检测文件存在，解析为JSON |
| `/run` | 运行工作流 | 要求运行工作流时 | 检查可运行性，执行工作流 |

## 命令参数说明

### 参数提取函数
每个命令文档中的AI执行脚本都使用了以下辅助函数：
- `extract_parameter(param_name, user_input)` - 从用户输入中提取指定参数
- `extract_operation(user_input)` - 从用户输入中识别操作类型

### 参数格式
- 参数格式：`参数名="参数值"`
- 示例：`/init project_name="新项目"`

---
*此索引文件由IDE Agent工作流引擎自动生成*
*AI必须参考命令文档中的执行脚本进行具体操作*"""
        
        index_file = commands_dir / 'commands_index.md'
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print(f"📄 命令索引文件已创建: {index_file}")
    
    def _generate_constraints_content(self, client: str) -> str:
        """生成AI提示词约束文件内容"""
        # 获取命令文档路径
        if client == 'default':
            commands_path = self.base_dir / 'rules' / 'commands'
        else:
            rules_dir = self.client_detector.get_rules_path(client, self.base_dir)
            commands_path = rules_dir / 'commands'
        
        return f"""# IDE Agent工作流引擎 - AI提示词约束

## 角色定义
你是一个专业的工作流引擎AI助手，必须严格按照工作流引擎制定的策略来回答用户问题。

## 可用命令约束

### 命令文档引用
在执行任何工作流命令前，你必须先参考对应的命令文档：
- **命令文档路径**: `{commands_path}`
- **命令索引文件**: `{commands_path}/commands_index.md`

### 核心工作流命令
你必须优先使用以下工作流命令来处理用户请求：

1. **`/init`** - 初始化工作流
   - **文档**: `{commands_path}/init_command.md`
   - 用途：创建新的工作流实例
   - 触发条件：用户请求开始新的工作流程
   - AI执行逻辑：检测用户意图是否需要初始化工作流，推荐使用命令

2. **`/stage`** - 管理工作流阶段
   - **文档**: `{commands_path}/stage_command.md`
   - 用途：添加、修改或查看工作流阶段
   - 触发条件：用户需要管理工作流阶段时
   - AI执行逻辑：分析用户意图确定操作类型，推荐使用命令

3. **`/step`** - 执行工作流步骤
   - **文档**: `{commands_path}/step_command.md`
   - 用途：执行具体的处理步骤
   - 触发条件：用户需要执行特定操作时
   - AI执行逻辑：识别用户请求的具体操作类型，推荐使用命令

4. **`/feedback`** - 提供反馈机制
   - **文档**: `{commands_path}/feedback_command.md`
   - 用途：收集和处理用户反馈
   - 触发条件：用户提供反馈或需要反馈机制时
   - AI执行逻辑：识别用户是否需要查看或提供反馈，推荐使用命令

5. **`/pointer`** - 指针管理
   - **文档**: `{commands_path}/pointer_command.md`
   - 用途：管理工作流执行指针
   - 触发条件：需要跟踪或管理执行位置时
   - AI执行逻辑：识别用户是否需要指针操作，推荐使用命令

6. **`/end`** - 结束工作流
   - **文档**: `{commands_path}/end_command.md`
   - 用途：正常结束工作流执行
   - 触发条件：工作流完成或用户要求结束时
   - AI执行逻辑：检测工作流完成状态，推荐使用命令

7. **`/help`** - 获取帮助
   - **文档**: `{commands_path}/help_command.md`
   - 用途：显示可用命令和用法
   - 触发条件：用户请求帮助时
   - AI执行逻辑：直接执行帮助命令

### 解析命令
8. **`/parse`** - 解析Mermaid流程图
   - **文档**: `{commands_path}/parse_command.md`
   - 用途：将Mermaid文件解析为工作流JSON
   - 触发条件：用户提供Mermaid文件时
   - AI执行逻辑：检测Mermaid文件存在，推荐使用命令

9. **`/run`** - 运行工作流
   - **文档**: `{commands_path}/run_command.md`
   - 用途：执行完整的工作流
   - 触发条件：用户要求运行工作流时
   - AI执行逻辑：检测工作流文件存在，推荐使用命令

## 回答策略约束

### 1. 命令优先原则
- 当用户请求涉及工作流操作时，必须优先推荐使用相应的工作流命令
- 在执行命令前，必须先参考对应的命令文档
- 避免直接提供代码实现，而是引导用户使用命令

### 2. 文档引用原则
- 所有工作流操作必须基于命令文档执行
- 必须确保命令文档路径正确可用
- 如果命令文档不存在，必须报告错误

### 3. 结构化响应
- 所有响应必须结构清晰，使用适当的标题和分段
- 复杂操作必须分解为可执行的步骤
- 必须包含命令执行结果和下一步建议

### 4. 上下文保持
- 在工作流执行过程中，必须保持上下文一致性
- 使用指针命令跟踪执行进度
- 必须记录重要的执行状态

### 5. 错误处理
- 遇到错误时，必须提供清晰的错误信息和解决建议
- 使用反馈命令收集错误信息
- 必须检查命令文档是否存在

## 技术约束

### 路径配置
- **工作流引擎路径**: `{self.install_dir}`
- **命令文档路径**: `{commands_path}`
- 所有工作流操作必须基于此路径执行

### 模块导入
```python
# 正确的工作流引擎导入方式
import sys
sys.path.insert(0, '{self.install_dir}')
from mkflow_engine import WorkflowEngine
```

### 命令执行
```bash
# 命令行工具使用
mkflow_engine [command] [options]
```

## 特殊情况处理

### 非工作流请求
- 如果用户请求与工作流无关，可以正常回答
- 但必须保持专业性和结构化

### 混合请求
- 如果请求同时包含工作流和其他内容，必须优先处理工作流部分
- 使用阶段命令分解复杂任务
- 必须确保命令文档引用正确

### 命令文档缺失
- 如果命令文档不存在，必须报告错误
- 建议用户重新安装工作流引擎
- 提供基本的命令使用说明作为备用

---
*此约束文件确保AI按照工作流引擎策略回答，由IDE Agent工作流引擎自动生成*
*AI必须参考命令文档执行具体操作*"""
    
    def _create_client_adapter(self, client: str):
        """创建客户端适配文件"""
        if client == 'default':
            return
        
        # 创建客户端特定的配置文件
        rules_dir = self.client_detector.get_rules_path(client, self.base_dir)
        config_file = rules_dir / 'mkflow_engine_config.yaml'
        
        config_content = f"""# IDE Agent工作流引擎 - {client.upper()}客户端配置

mkflow_engine:
  install_dir: "{self.install_dir}"
  client_type: "{client}"
  rules_dir: "{rules_dir}"
  
  # 命令配置
  commands:
    prefix: "/"
    supported:
      - "/init"
      - "/stage"
      - "/step" 
      - "/feedback"
      - "/pointer"
      - "/end"
      - "/help"
  
  # 路径配置
  paths:
    templates: "{self.install_dir}/mkflow_engine/templates"
schemas: "{self.install_dir}/mkflow_engine/core"
    
# 自动生成时间: {self._get_current_time()}
"""
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"⚙️  {client.upper()}客户端适配文件已创建: {config_file}")
    
    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _print_installation_summary(self, client: str, package_type: str):
        """打印安装摘要"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}" + "="*60 + Colors.END)
        print(f"{Colors.BLUE}{Colors.BOLD}📋 安装摘要{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}" + "="*60 + Colors.END)
        print(f"{Colors.CYAN}📁 安装目录: {self.install_dir}{Colors.END}")
        print(f"{Colors.CYAN}👤 客户端: {client.upper() if client != 'default' else '默认'}{Colors.END}")
        print(f"{Colors.CYAN}📄 约束文件: {self.client_detector.get_rules_path(client, self.base_dir) if client != 'default' else self.base_dir / 'rules'}/ide_agent_constraints.md{Colors.END}")
        
        # 显示扩展包信息
        if package_type == ExtensionPackages.CODE_DEVELOPMENT:
            print(f"{Colors.GREEN}📦 扩展包: 代码开发工作流扩展包{Colors.END}")
            print(f"{Colors.CYAN}   📁 模板位置: {self.install_dir / 'extensions' / 'code_development' / 'templates'}{Colors.END}")
        elif package_type == ExtensionPackages.CONTENT_CREATION:
            print(f"{Colors.GREEN}📦 扩展包: 内容创作SOP工作流扩展包{Colors.END}")
            print(f"{Colors.CYAN}   📁 模板位置: {self.install_dir / 'extensions' / 'content_creation' / 'sop_templates'}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}📦 扩展包: 无{Colors.END}")
        
        print(f"\n{Colors.BLUE}{Colors.BOLD}🚀 使用说明:{Colors.END}")
        print(f"{Colors.CYAN}1. 设置PYTHONPATH环境变量包含安装目录{Colors.END}")
        print(f"{Colors.CYAN}2. 导入: from mkflow_engine import WorkflowEngine{Colors.END}")
        print(f"{Colors.CYAN}3. 使用命令行工具: mkflow_engine --help{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}" + "="*60 + Colors.END)
        print(f"\n{Colors.GREEN}{Colors.BOLD}✨ 感谢使用MK-FLOW工作流引擎！{Colors.END}")


def main():
    """
    自定义安装器的主函数入口
    
    功能：
    - 解析命令行参数
    - 初始化自定义安装器
    - 执行安装流程
    
    使用示例：
    python -m installer.custom_installer
    mkflow-engine-install
    """
    import argparse
    
    # 创建参数解析器
    parser = argparse.ArgumentParser(
        description='MK-FLOW 工作流引擎自定义安装器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  mkf-install
mkf-install                    # 在当前目录安装
mkf-install --dir /path/to/project  # 在指定目录安装
mkf-install --package ./local.whl   # 从本地包安装
        """
    )
    
    # 添加参数
    parser.add_argument(
        '--dir', 
        dest='install_dir',
        help='指定安装目录（默认为当前目录）'
    )
    parser.add_argument(
        '--package',
        dest='package_path',
        help='指定本地包文件路径（默认为使用uv安装）'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='MK-FLOW 工作流引擎安装器 v1.0.0'
    )
    
    # 解析参数
    args = parser.parse_args()
    
    try:
        # 创建安装器实例
        installer = CustomInstaller(args.install_dir)
        
        # 执行安装
        installer.install_package(args.package_path)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}安装过程被用户中断{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}安装过程中发生错误: {e}{Colors.END}")
        sys.exit(1)


if __name__ == '__main__':
    main()