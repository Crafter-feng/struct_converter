.PHONY: help install install-dev test test-unit test-integration test-coverage lint format clean docs

# 默认目标
help:
	@echo "可用的命令:"
	@echo "  install        - 安装项目依赖"
	@echo "  install-dev    - 安装开发依赖"
	@echo "  test           - 运行所有测试"
	@echo "  test-unit      - 运行单元测试"
	@echo "  test-integration - 运行集成测试"
	@echo "  test-coverage  - 运行测试并生成覆盖率报告"
	@echo "  test-fast      - 运行快速测试（跳过慢速测试）"
	@echo "  lint           - 运行代码检查"
	@echo "  lint-fix       - 自动修复代码问题"
	@echo "  format         - 格式化代码"
	@echo "  format-check   - 检查代码格式"
	@echo "  sort           - 排序导入"
	@echo "  sort-check     - 检查导入排序"
	@echo "  type-check     - 运行类型检查"
	@echo "  security       - 运行安全检查"
	@echo "  clean          - 清理临时文件"
	@echo "  docs           - 构建文档"

# 安装依赖
install:
	uv pip install -e .

install-dev:
	uv pip install -e .[test,dev]

# 测试相关
test:
	uv run pytest tests/

test-unit:
	uv run pytest tests/ -m unit

test-integration:
	uv run pytest tests/ -m integration

test-coverage:
	uv run pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

test-fast:
	uv run pytest tests/ -m "not slow"

test-benchmark:
	uv run pytest tests/ -m benchmark

# 代码质量
lint:
	uv run ruff check src/ tests/

lint-fix:
	uv run ruff check --fix src/ tests/

format:
	uv run black src/ tests/

format-check:
	uv run black --check src/ tests/

sort:
	uv run isort src/ tests/

sort-check:
	uv run isort --check-only src/ tests/

type-check:
	uv run mypy src/

security:
	uv run bandit -r src/

# 清理
clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage htmlcov/ .mypy_cache/ .ruff_cache/

# 文档
docs:
	uv run sphinx-build -b html docs/ docs/_build/html

# 开发工作流
dev-setup: install-dev
	@echo "开发环境设置完成"

quick-check: lint format-check sort-check type-check
	@echo "代码质量检查完成"

full-check: quick-check test-coverage security
	@echo "完整检查完成"

# 使用传统pip的备用命令
pip-install:
	pip install -e .[test,dev]

pip-test:
	pytest tests/

pip-lint:
	ruff check src/ tests/

pip-format:
	black src/ tests/
