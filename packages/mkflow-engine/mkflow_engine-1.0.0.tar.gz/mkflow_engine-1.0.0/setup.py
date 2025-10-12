"""
工作流引擎安装配置
"""

from setuptools import setup, find_packages
import os

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 定义依赖项
requirements = [
    "jsonschema>=4.0.0",
    "click>=8.0.0", 
    "rich>=10.0.0",
    "pyyaml>=6.0"
]

setup(
    name="mkflow-engine",
    version="1.0.0",
    author="IDE Agent Workflow Team",
    author_email="team@mkflow_engine.org",
    description="基于六大原则的IDE Agent工作流引擎",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mkflow_engine/mkflow_engine",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "mkf=mkflow_engine.cli:main",
        "mkf-install=installer.custom_installer:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mkflow_engine": [
            "templates/*.mermaid",
            "templates/*.md",
            "core/*.json",
        ],
        "installer": [
            "*.py",
            "*.md",
        ],
    },
    include_package_data=True,
    keywords="workflow, agent, ide, automation, mermaid, json-schema",
    project_urls={
        "Documentation": "https://github.com/ARSENE2630/moke-work-flow/blob/master/README.md",
        "Source": "https://github.com/ARSENE2630/moke-work-flow",
        "Tracker": "https://github.com/ARSENE2630/moke-work-flow/issues",
    },
)