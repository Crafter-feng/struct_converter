# Struct Converter

C语言结构体转换器 - 解析C代码并生成多种语言的绑定

## 功能特性

- 🚀 基于Tree-sitter的快速C代码解析
- 📦 支持结构体、联合体、枚举、typedef等C语言类型
- 🔧 可扩展的代码生成器架构
- 🎯 支持生成Python、C++、C等多种语言绑定
- 🧪 完整的单元测试覆盖
- 📊 详细的代码覆盖率报告

## 快速开始

### 使用UV (推荐)

UV是一个快速的Python包管理器和安装器。

#### 安装UV

```bash
# 使用pip安装
pip install uv

# 或使用官方安装脚本
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 安装项目

```bash
# 克隆项目
git clone <repository-url>
cd struct-converter

# 安装开发依赖
uv pip install -e .[test,dev]

# 或使用Makefile
make install-dev
```

#### 运行测试

```bash
# 运行所有测试
uv run pytest tests/

# 或使用Makefile
make test

# 运行测试并生成覆盖率报告
make test-coverage
```

### 使用传统pip

```bash
# 安装开发依赖
pip install -e .[test,dev]

# 运行测试
pytest tests/
```

## 开发指南

### 项目结构

```
struct-converter/
├── src/
│   ├── c_parser/           # C语言解析器
│   │   ├── core/          # 核心组件
│   │   ├── type_parser.py # 类型解析器
│   │   └── data_parser.py # 数据解析器
│   ├── c_converter/       # 代码转换器
│   │   ├── generators/    # 代码生成器
│   │   └── templates/     # 模板文件
│   └── cli.py            # 命令行接口
├── tests/                # 测试套件
├── config/              # 配置文件
├── pyproject.toml       # 项目配置
├── Makefile            # 便捷命令
└── README.md           # 项目文档
```

### 开发命令

#### 使用UV脚本

```bash
# 测试相关
uv run test                    # 运行所有测试
uv run test-unit              # 只运行单元测试
uv run test-integration       # 只运行集成测试
uv run test-coverage          # 运行测试并生成覆盖率报告
uv run test-fast              # 运行快速测试

# 代码质量
uv run lint                   # 代码检查
uv run lint-fix               # 自动修复代码问题
uv run format                 # 代码格式化
uv run format-check           # 检查代码格式
uv run sort                   # 导入排序
uv run type-check             # 类型检查
uv run security               # 安全检查

# 项目管理
uv run clean                  # 清理临时文件
uv run install-dev            # 安装开发依赖
```

#### 使用Makefile

```bash
# 查看所有可用命令
make help

# 开发环境设置
make dev-setup

# 代码质量检查
make quick-check

# 完整检查（包括测试和覆盖率）
make full-check

# 清理项目
make clean
```

#### 使用测试脚本

```bash
# 使用UV测试脚本
python tests/run_tests_uv.py --help

# 安装开发依赖
python tests/run_tests_uv.py --install-dev

# 运行测试
python tests/run_tests_uv.py --coverage

# 代码格式化
python tests/run_tests_uv.py --format

# 代码检查
python tests/run_tests_uv.py --lint
```

### 测试

项目包含完整的测试套件：

```bash
# 运行所有测试
make test

# 运行单元测试
make test-unit

# 运行集成测试
make test-integration

# 生成覆盖率报告
make test-coverage

# 运行快速测试（跳过慢速测试）
make test-fast
```

### 代码质量

项目使用多种工具确保代码质量：

```bash
# 代码格式化
make format

# 代码检查
make lint

# 类型检查
make type-check

# 安全检查
make security

# 快速质量检查
make quick-check
```

## 配置

项目使用`pyproject.toml`进行配置，包括：

- 项目元数据和依赖
- 测试配置（pytest）
- 代码格式化配置（black, isort）
- 代码检查配置（ruff, mypy, flake8）
- 覆盖率配置（coverage）
- UV脚本配置

## 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开Pull Request

### 开发环境设置

```bash
# 1. 克隆项目
git clone <repository-url>
cd struct-converter

# 2. 安装UV
pip install uv

# 3. 安装开发依赖
make dev-setup

# 4. 运行测试确保环境正常
make test
```

### 提交前检查

```bash
# 运行完整检查
make full-check

# 或分步检查
make quick-check
make test-coverage
make security
```

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 支持

如果您遇到问题或有建议，请：

1. 查看 [文档](docs/)
2. 搜索 [Issues](https://github.com/yourusername/struct-converter/issues)
3. 创建新的Issue

## 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新历史。
