#!/usr/bin/env python3
"""
检查AI提示词约束文件内容
"""

import sys
sys.path.insert(0, '.')

from installer.custom_installer import CustomInstaller

# 创建安装器实例
installer = CustomInstaller('.')

# 生成AI提示词约束文件内容
content = installer._generate_constraints_content('trae')

# 显示完整内容
print('完整的AI提示词约束文件内容:')
print('='*80)
print(content)
print('='*80)

# 验证关键元素
print('\n🔍 验证关键元素:')
key_elements = [
    ('角色定义', '专业的工作流引擎AI助手'),
    ('可用命令约束', '/init'),
    ('命令优先原则', '优先推荐使用相应的工作流命令'),
    ('结构化响应', '结构清晰'),
    ('上下文保持', '保持上下文一致性'),
    ('错误处理', '清晰的错误信息'),
    ('技术约束', '工作流引擎路径'),
    ('特殊情况处理', '非工作流请求')
]

for element, keyword in key_elements:
    if keyword in content:
        print(f'✅ {element}: 包含关键字 "{keyword}"')
    else:
        print(f'❌ {element}: 缺少关键字 "{keyword}"')