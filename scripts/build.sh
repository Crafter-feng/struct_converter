#!/bin/bash
set -e

echo "Cleaning up old builds..."
rm -rf build/ dist/ *.egg-info/

echo "Running tests..."
pytest

echo "Building package..."
python -m build

echo "Running type checks..."
mypy src

echo "Running linters..."
flake8 src
pylint src

echo "Build completed successfully!" 