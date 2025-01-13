#!/bin/bash
set -e

echo "Setting up development environment..."

# 检测是否在conda环境中
if [[ ! -z "${CONDA_DEFAULT_ENV}" ]]; then
    echo "Using current conda environment: ${CONDA_DEFAULT_ENV}"
    
    # 在conda环境中直接安装依赖
    pip install -e ".[dev]"
else
    echo "Setting up virtual environment using venv..."
    
    # 创建并激活虚拟环境
    python -m venv .venv
    source .venv/bin/activate
    
    # 安装开发依赖
    pip install -e ".[dev]"
fi

# 安装pre-commit hooks
pre-commit install

echo "Development environment setup completed!" 