#!/bin/bash
set -e

VERSION=$(python setup.py --version)

echo "Publishing version $VERSION..."

# 运行测试
./scripts/build.sh

# 发布到PyPI
python -m twine upload dist/*

echo "Published version $VERSION successfully!" 