#!/usr/bin/env python3
"""
C Parser 测试运行脚本

使用方法:
    python run_tests.py                    # 运行所有测试
    python run_tests.py --unit            # 只运行单元测试
    python run_tests.py --integration     # 只运行集成测试
    python run_tests.py --coverage        # 运行测试并生成覆盖率报告
    python run_tests.py --help            # 显示帮助信息
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """运行命令并处理结果"""
    print(f"\n{'='*60}")
    if description:
        print(f"运行: {description}")
    print(f"命令: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"\n✅ {description} 成功完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} 失败 (退出码: {e.returncode})")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="C Parser 测试运行脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_tests.py                    # 运行所有测试
  python run_tests.py --unit            # 只运行单元测试
  python run_tests.py --integration     # 只运行集成测试
  python run_tests.py --coverage        # 运行测试并生成覆盖率报告
  python run_tests.py --file test_tree_sitter_utils.py  # 运行特定文件
  python run_tests.py --verbose         # 详细输出
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
    
    args = parser.parse_args()
    
    # 检查是否在正确的目录
    current_dir = Path(__file__).parent
    if not (current_dir / "conftest.py").exists():
        print("❌ 错误: 请在tests目录下运行此脚本")
        sys.exit(1)
    
    # 构建pytest命令
    cmd = ["python", "-m", "pytest"]
    
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
            "--cov=c_parser",
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
    success = run_command(cmd, "pytest测试")
    
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
