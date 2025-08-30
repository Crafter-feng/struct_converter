# C Parser 测试套件

本目录包含了c_parser模块的完整单元测试套件。

## 测试文件结构

```
tests/
├── conftest.py              # pytest配置和通用fixtures
├── test_tree_sitter_utils.py # TreeSitterUtils测试
├── test_expression_parser.py # ExpressionParser测试
├── test_data_manager.py     # DataManager测试
├── test_type_manager.py     # TypeManager测试
├── test_type_parser.py      # CTypeParser测试
├── test_data_parser.py      # CDataParser测试
├── pytest.ini              # pytest配置文件
├── run_tests.py            # 传统测试运行脚本
├── run_tests_uv.py         # UV测试运行脚本
├── README.md               # 本文件
└── fixtures/               # 测试数据文件
    └── c_files/
        ├── test_structs.h  # 测试用头文件
        └── test_data.c     # 测试用源文件
```

## 环境设置

### 使用UV (推荐)

UV是一个快速的Python包管理器和安装器。

#### 安装UV

```bash
# 使用pip安装
pip install uv

# 或使用官方安装脚本
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 初始化项目

```bash
# 在项目根目录下
uv init
uv sync
```

#### 安装开发依赖

```bash
# 安装所有开发依赖
uv pip install -e .[test,dev]

# 或使用脚本
python tests/run_tests_uv.py --install-dev
```

### 使用传统pip

```bash
# 安装开发依赖
pip install -e .[test,dev]
```

## 运行测试

### 使用UV (推荐方式)

#### 运行所有测试

```bash
# 使用UV脚本
python tests/run_tests_uv.py

# 或直接使用UV
uv run pytest tests/
```

#### 运行特定类型的测试

```bash
# 只运行单元测试
python tests/run_tests_uv.py --unit

# 只运行集成测试
python tests/run_tests_uv.py --integration

# 运行测试并生成覆盖率报告
python tests/run_tests_uv.py --coverage

# 运行快速测试（跳过慢速测试）
python tests/run_tests_uv.py --fast
```

#### 代码质量检查

```bash
# 代码格式化
python tests/run_tests_uv.py --format

# 代码检查
python tests/run_tests_uv.py --lint

# 运行特定测试文件
python tests/run_tests_uv.py --file test_tree_sitter_utils.py
```

### 使用传统pytest

#### 运行所有测试

```bash
# 在项目根目录下运行
pytest tests/

# 或者在tests目录下运行
cd tests
pytest
```

#### 运行特定测试文件

```bash
# 运行TreeSitterUtils测试
pytest tests/test_tree_sitter_utils.py

# 运行ExpressionParser测试
pytest tests/test_expression_parser.py

# 运行DataManager测试
pytest tests/test_data_manager.py
```

#### 运行特定测试类

```bash
# 运行TestTreeSitterUtils类
pytest tests/test_tree_sitter_utils.py::TestTreeSitterUtils

# 运行TestExpressionParser类
pytest tests/test_expression_parser.py::TestExpressionParser
```

#### 运行特定测试方法

```bash
# 运行特定测试方法
pytest tests/test_tree_sitter_utils.py::TestTreeSitterUtils::test_initialization

# 运行包含特定名称的测试
pytest -k "initialization"
```

#### 运行标记的测试

```bash
# 只运行单元测试
pytest -m unit

# 只运行集成测试
pytest -m integration

# 跳过慢速测试
pytest -m "not slow"
```

## 测试覆盖率

### 使用UV

```bash
# 运行测试并生成覆盖率报告
python tests/run_tests_uv.py --coverage

# 或直接使用UV
uv run pytest --cov=src --cov-report=html --cov-report=term-missing tests/
```

### 使用传统方式

```bash
# 安装覆盖率工具
pip install pytest-cov

# 运行测试并生成覆盖率报告
pytest --cov=c_parser tests/

# 生成HTML覆盖率报告
pytest --cov=c_parser --cov-report=html tests/
```

## UV脚本命令

项目配置了多个UV脚本，可以在`pyproject.toml`中查看：

```bash
# 测试相关
uv run test                    # 运行所有测试
uv run test-unit              # 只运行单元测试
uv run test-integration       # 只运行集成测试
uv run test-coverage          # 运行测试并生成覆盖率报告
uv run test-fast              # 运行快速测试
uv run test-benchmark         # 运行基准测试

# 代码质量
uv run lint                   # 代码检查
uv run lint-fix               # 自动修复代码问题
uv run format                 # 代码格式化
uv run format-check           # 检查代码格式
uv run sort                   # 导入排序
uv run sort-check             # 检查导入排序
uv run type-check             # 类型检查
uv run security               # 安全检查

# 项目管理
uv run clean                  # 清理临时文件
uv run install-dev            # 安装开发依赖
uv run install-all            # 安装所有依赖
```

## 测试类型说明

### 单元测试 (Unit Tests)
- 测试单个函数或方法的功能
- 使用mock对象隔离依赖
- 快速执行，不依赖外部资源
- 标记为`@pytest.mark.unit`

### 集成测试 (Integration Tests)
- 测试多个组件之间的交互
- 可能使用真实的文件或数据库
- 执行时间较长
- 标记为`@pytest.mark.integration`

### 慢速测试 (Slow Tests)
- 需要大量计算或I/O操作的测试
- 标记为`@pytest.mark.slow`
- 可以通过`-m "not slow"`跳过

### 基准测试 (Benchmark Tests)
- 性能测试
- 标记为`@pytest.mark.benchmark`
- 使用pytest-benchmark插件

## 测试数据

### fixtures/c_files/
包含用于测试的C语言文件：
- `test_structs.h`: 包含各种结构体、联合体、枚举定义
- `test_data.c`: 包含全局变量定义和初始化

### conftest.py
定义了通用的测试fixtures：
- `sample_c_code`: 示例C代码字符串
- `sample_c_file`: 临时C文件
- `type_manager`: TypeManager实例
- `data_manager`: DataManager实例
- `expression_parser`: ExpressionParser实例
- `type_parser`: CTypeParser实例
- `data_parser`: CDataParser实例

## 测试最佳实践

1. **测试隔离**: 每个测试应该独立运行，不依赖其他测试的状态
2. **Mock外部依赖**: 使用unittest.mock来模拟外部依赖
3. **测试边界条件**: 包括正常情况、边界情况和错误情况
4. **描述性测试名称**: 测试方法名应该清楚地描述测试内容
5. **断言清晰**: 使用明确的断言来验证结果
6. **使用标记**: 为测试添加适当的标记（unit, integration, slow等）

## 调试测试

### 运行单个测试并显示详细输出

```bash
# 使用UV
uv run pytest tests/test_tree_sitter_utils.py::TestTreeSitterUtils::test_initialization -v -s

# 使用脚本
python tests/run_tests_uv.py --file test_tree_sitter_utils.py --verbose
```

### 在测试失败时进入调试器

```bash
uv run pytest tests/test_tree_sitter_utils.py --pdb
```

### 生成测试报告

```bash
# 生成JUnit XML报告
uv run pytest --junitxml=test-results.xml tests/

# 生成HTML报告
uv run pytest --html=test-report.html --self-contained-html tests/
```

## 持续集成

这些测试可以集成到CI/CD流程中：

```yaml
# GitHub Actions示例
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
```

## 故障排除

### 常见问题

1. **UV未安装**: 确保已正确安装UV
   ```bash
   pip install uv
   ```

2. **导入错误**: 确保src目录在Python路径中（pyproject.toml已配置）

3. **Mock错误**: 检查mock对象的路径是否正确

4. **文件权限**: 确保测试有权限创建临时文件

5. **依赖冲突**: 使用UV可以更好地管理依赖冲突

### 调试技巧

1. 使用`print()`或`logger.debug()`在测试中添加调试信息
2. 使用`pytest.set_trace()`在测试中设置断点
3. 检查mock对象的调用情况：`mock_obj.assert_called_with(expected_args)`
4. 使用UV的虚拟环境隔离：`uv run python -c "import sys; print(sys.path)"`

### UV特定问题

1. **锁定文件**: 如果遇到依赖问题，可以重新生成锁定文件
   ```bash
   uv lock --reinstall
   ```

2. **缓存问题**: 清理UV缓存
   ```bash
   uv cache clean
   ```

3. **虚拟环境**: UV自动管理虚拟环境，无需手动创建
