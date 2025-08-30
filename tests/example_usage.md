# UV 使用示例

本文档展示了如何使用UV来管理和运行测试环境。

## 安装UV

### 方法1: 使用pip安装
```bash
pip install uv
```

### 方法2: 使用官方安装脚本
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 方法3: 使用包管理器
```bash
# macOS (使用Homebrew)
brew install uv

# Windows (使用Scoop)
scoop install uv

# Linux (使用Cargo)
cargo install uv
```

## 项目设置

### 1. 初始化项目
```bash
# 在项目根目录下
uv init
uv sync
```

### 2. 安装开发依赖
```bash
# 安装所有开发依赖
uv pip install -e .[test,dev]

# 或使用脚本
python tests/run_tests_uv.py --install-dev
```

## 运行测试

### 基本测试命令

```bash
# 运行所有测试
uv run pytest tests/

# 运行特定测试文件
uv run pytest tests/test_tree_sitter_utils.py

# 运行特定测试类
uv run pytest tests/test_tree_sitter_utils.py::TestTreeSitterUtils

# 运行特定测试方法
uv run pytest tests/test_tree_sitter_utils.py::TestTreeSitterUtils::test_initialization
```

### 使用UV脚本

```bash
# 运行所有测试
uv run test

# 只运行单元测试
uv run test-unit

# 只运行集成测试
uv run test-integration

# 运行测试并生成覆盖率报告
uv run test-coverage

# 运行快速测试（跳过慢速测试）
uv run test-fast

# 运行基准测试
uv run test-benchmark
```

### 使用Makefile

```bash
# 运行所有测试
make test

# 运行单元测试
make test-unit

# 运行集成测试
make test-integration

# 生成覆盖率报告
make test-coverage

# 运行快速测试
make test-fast
```

### 使用测试脚本

```bash
# 运行所有测试
python tests/run_tests_uv.py

# 只运行单元测试
python tests/run_tests_uv.py --unit

# 只运行集成测试
python tests/run_tests_uv.py --integration

# 运行测试并生成覆盖率报告
python tests/run_tests_uv.py --coverage

# 运行特定测试文件
python tests/run_tests_uv.py --file test_tree_sitter_utils.py

# 详细输出
python tests/run_tests_uv.py --verbose
```

## 代码质量检查

### 使用UV脚本

```bash
# 代码检查
uv run lint

# 自动修复代码问题
uv run lint-fix

# 代码格式化
uv run format

# 检查代码格式
uv run format-check

# 导入排序
uv run sort

# 检查导入排序
uv run sort-check

# 类型检查
uv run type-check

# 安全检查
uv run security
```

### 使用Makefile

```bash
# 代码检查
make lint

# 自动修复代码问题
make lint-fix

# 代码格式化
make format

# 检查代码格式
make format-check

# 导入排序
make sort

# 检查导入排序
make sort-check

# 类型检查
make type-check

# 安全检查
make security

# 快速质量检查
make quick-check

# 完整检查
make full-check
```

### 使用测试脚本

```bash
# 代码格式化
python tests/run_tests_uv.py --format

# 代码检查
python tests/run_tests_uv.py --lint
```

## 项目管理

### 安装依赖

```bash
# 安装项目依赖
uv pip install -e .

# 安装开发依赖
uv pip install -e .[test,dev]

# 安装所有依赖
uv pip install -e .[test,dev,docs]

# 使用UV脚本
uv run install-dev
uv run install-all
```

### 清理项目

```bash
# 清理临时文件
uv run clean

# 或使用Makefile
make clean
```

## 高级用法

### 并行测试

```bash
# 使用pytest-xdist进行并行测试
uv run pytest tests/ -n auto

# 指定进程数
uv run pytest tests/ -n 4
```

### 生成测试报告

```bash
# 生成HTML测试报告
uv run pytest tests/ --html=test-report.html --self-contained-html

# 生成JUnit XML报告
uv run pytest tests/ --junitxml=test-results.xml

# 生成覆盖率报告
uv run pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
```

### 调试测试

```bash
# 在测试失败时进入调试器
uv run pytest tests/ --pdb

# 显示详细输出
uv run pytest tests/ -v -s

# 只运行失败的测试
uv run pytest tests/ --lf

# 运行上次失败的测试
uv run pytest tests/ --ff
```

### 性能测试

```bash
# 运行基准测试
uv run pytest tests/ -m benchmark

# 生成性能报告
uv run pytest tests/ --benchmark-only --benchmark-sort=mean
```

## 故障排除

### 常见问题

1. **UV未安装**
   ```bash
   # 检查UV是否安装
   uv --version
   
   # 如果未安装，请按照上述方法安装
   ```

2. **依赖冲突**
   ```bash
   # 重新生成锁定文件
   uv lock --reinstall
   
   # 清理缓存
   uv cache clean
   ```

3. **虚拟环境问题**
   ```bash
   # UV自动管理虚拟环境，无需手动创建
   # 如果遇到问题，可以重新同步
   uv sync
   ```

4. **权限问题**
   ```bash
   # 在Windows上可能需要以管理员身份运行
   # 在Linux/macOS上可能需要使用sudo
   ```

### 调试技巧

```bash
# 查看UV环境信息
uv run python -c "import sys; print(sys.path)"

# 查看已安装的包
uv run pip list

# 查看项目配置
uv run python -c "import sys; print(sys.executable)"
```

## 最佳实践

1. **使用UV脚本**: 优先使用`pyproject.toml`中定义的UV脚本
2. **使用Makefile**: 对于复杂的开发工作流，使用Makefile
3. **定期同步**: 定期运行`uv sync`确保依赖是最新的
4. **清理缓存**: 遇到问题时清理UV缓存
5. **使用虚拟环境**: UV自动管理虚拟环境，无需手动创建

## 与CI/CD集成

### GitHub Actions示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup UV
      uses: astral-sh/setup-uv@v1
      with:
        version: "latest"
    
    - name: Install dependencies
      run: uv sync
    
    - name: Run tests
      run: uv run test
    
    - name: Run linting
      run: uv run lint
    
    - name: Run type checking
      run: uv run type-check
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### GitLab CI示例

```yaml
test:
  image: python:3.11
  before_script:
    - pip install uv
    - uv sync
  script:
    - uv run test
    - uv run lint
    - uv run type-check
```

这样，您就可以使用UV来高效地管理和运行测试环境了！
