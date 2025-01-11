#!/bin/bash
set -e

echo "Setting up development environment..."

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 安装开发依赖
pip install -e ".[dev]"

# 安装pre-commit hooks
pre-commit install

echo "Development environment setup completed!" 