#!/usr/bin/env python3
"""
Setup script for Wolfram Alpha MCP Server
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="wolfram-alpha-mcp-server-xiaomayisjh",
    version="1.0.0",
    author="Wolfram Alpha MCP Team",
    author_email="",
    description="Wolfram Alpha MCP Server - 使用移动端API的科学计算和事实查询工具",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/wolfram-alpha-mcp-server",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "wolfram-alpha-mcp=server_remote:main",
        ],
    },
    keywords="wolfram alpha, mcp, mathematics, science, calculation, api",
    project_urls={
        "Bug Reports": "https://github.com/your-username/wolfram-alpha-mcp-server/issues",
        "Source": "https://github.com/your-username/wolfram-alpha-mcp-server",
        "Documentation": "https://github.com/your-username/wolfram-alpha-mcp-server#readme",
    },
)
