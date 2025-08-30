#!/usr/bin/env python3
"""
C Parser 测试运行脚本 (UV版本)

使用方法:
    python run_tests_uv.py                    # 运行所有测试
    python run_tests_uv.py --unit            # 只运行单元测试
    python run_tests_uv.py --integration     # 只运行集成测试
    python run_tests_uv.py --coverage        # 运行测试并生成覆盖率报告
    python run_tests_uv.py --help            # 显示帮助信息
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_uv_command(cmd, description=""):
    """运行uv命令并处理结果"""
    print(f"\n{'='*60}")
    if description:
        print(f"运行: {description}")
    print(f"命令: uv run {' '.join(cmd)}")
    print('='*60)
    
    try:
        # 使用uv run来执行命令
        result = subprocess.run(["uv", "run"] + cmd, check=True, capture_output=False)
        print(f"\n✅ {description} 成功完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} 失败 (退出码: {e.returncode})")
        return False
    except FileNotFoundError:
        print(f"\n❌ 错误: 未找到uv命令，请先安装uv")
        print("安装方法: pip install uv 或 curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="C Parser 测试运行脚本 (UV版本)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_tests_uv.py                    # 运行所有测试
  python run_tests_uv.py --unit            # 只运行单元测试
  python run_tests_uv.py --integration     # 只运行集成测试
  python run_tests_uv.py --coverage        # 运行测试并生成覆盖率报告
  python run_tests_uv.py --file test_tree_sitter_utils.py  # 运行特定文件
  python run_tests_uv.py --verbose         # 详细输出
  python run_tests_uv.py --install-dev     # 安装开发依赖
        """
    )
    
    parser.add_argument(
        '--unit', 
        action='store_true',
        help='只运行单元测试'
    )
    
    parser.add_argument(
        '--integration', 
        action='store_true',
        help='只运行集成测试'
    )
    
    parser.add_argument(
        '--coverage', 
        action='store_true',
        help='运行测试并生成覆盖率报告'
    )
    
    parser.add_argument(
        '--file', 
        type=str,
        help='运行特定的测试文件'
    )
    
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='详细输出'
    )
    
    parser.add_argument(
        '--html-report', 
        action='store_true',
        help='生成HTML测试报告'
    )
    
    parser.add_argument(
        '--install-dev', 
        action='store_true',
        help='安装开发依赖'
    )
    
    parser.add_argument(
        '--lint', 
        action='store_true',
        help='运行代码检查'
    )
    
    parser.add_argument(
        '--format', 
        action='store_true',
        help='格式化代码'
    )
    
    args = parser.parse_args()
    
    # 检查是否在正确的目录
    current_dir = Path(__file__).parent
    if not (current_dir / "conftest.py").exists():
        print("❌ 错误: 请在tests目录下运行此脚本")
        sys.exit(1)
    
    # 检查项目根目录是否有pyproject.toml
    project_root = current_dir.parent
    if not (project_root / "pyproject.toml").exists():
        print("❌ 错误: 项目根目录未找到pyproject.toml文件")
        sys.exit(1)
    
    # 安装开发依赖
    if args.install_dev:
        print("📦 安装开发依赖...")
        success = run_uv_command(
            ["pip", "install", "-e", ".[test,dev]"],
            "安装开发依赖"
        )
        if not success:
            sys.exit(1)
        print("✅ 开发依赖安装完成")
        return
    
    # 代码格式化
    if args.format:
        print("🎨 格式化代码...")
        success = run_uv_command(
            ["black", "src/", "tests/"],
            "代码格式化"
        )
        if success:
            success = run_uv_command(
                ["isort", "src/", "tests/"],
                "导入排序"
            )
        if not success:
            sys.exit(1)
        print("✅ 代码格式化完成")
        return
    
    # 代码检查
    if args.lint:
        print("🔍 运行代码检查...")
        success = run_uv_command(
            ["ruff", "check", "src/", "tests/"],
            "代码检查"
        )
        if success:
            success = run_uv_command(
                ["mypy", "src/"],
                "类型检查"
            )
        if not success:
            sys.exit(1)
        print("✅ 代码检查完成")
        return
    
    # 构建pytest命令
    cmd = ["pytest"]
    
    # 添加详细输出
    if args.verbose:
        cmd.extend(["-v", "-s"])
    
    # 添加测试选择
    if args.unit:
        cmd.extend(["-m", "unit"])
    elif args.integration:
        cmd.extend(["-m", "integration"])
    
    # 添加特定文件
    if args.file:
        test_file = current_dir / args.file
        if not test_file.exists():
            print(f"❌ 错误: 测试文件 {args.file} 不存在")
            sys.exit(1)
        cmd.append(str(test_file))
    else:
        cmd.append(".")
    
    # 添加覆盖率选项
    if args.coverage:
        cmd.extend([
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])
    
    # 添加HTML报告
    if args.html_report:
        cmd.extend([
            "--html=test-report.html",
            "--self-contained-html"
        ])
    
    # 运行测试
    success = run_uv_command(cmd, "pytest测试")
    
    if success:
        print("\n🎉 所有测试完成!")
        if args.coverage:
            print("📊 覆盖率报告已生成在 htmlcov/ 目录中")
        if args.html_report:
            print("📄 HTML测试报告已生成: test-report.html")
    else:
        print("\n💥 测试失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()
