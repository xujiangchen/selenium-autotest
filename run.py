import os
import sys
import subprocess
import argparse
from pathlib import Path

from utils.log_manager import LogManager

# 项目根目录（根据实际路径调整）
BASE_DIR = Path(__file__).parent

logger = LogManager()


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Run pytest tests with custom options.")
    # pytest 标记（marker）筛选测试用例
    parser.add_argument(
        "-m", "--mark",
        help="Run tests with specific marker (e.g., 'smoke')",
        default=""
    )
    # 通过关键字表达式筛选测试用例
    parser.add_argument(
        "-k", "--keyword",
        help="Run tests matching keyword expression",
        default=""
    )
    # 指定测试环境（如开发环境 dev、预发布环境 staging）
    parser.add_argument(
        "-e", "--env",
        help="Test environment (e.g., 'dev', 'staging')",
        default="dev"
    )
    parser.add_argument(
        "-b", "--browser",
        help="What browser to use",
        default="Chrome"
    )
    # 指定allure 报告的位置，默认为项目根目录
    parser.add_argument(
        "--allure",
        type=str,
        default=BASE_DIR / "allure-results",
        help="Generate Allure report after tests and specify the output directory"
    )
    # 是否清理之前的测试结果
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean previous test results"
    )
    return parser.parse_args()


def clean_results(allure_path):
    """清理历史测试结果"""
    if allure_path.exists():
        for file in allure_path.glob("*"):
            file.unlink()
    logger.info("🧹 Cleaned previous test results.")


def run_pytest(args):
    """执行 pytest 命令"""
    cmd = ["pytest"]
    # 添加 pytest 参数
    if args.mark:
        cmd.extend(["-m", args.mark])
    if args.keyword:
        cmd.extend(["-k", args.keyword])
    if args.clean:
        clean_results(args.allure)

    # 指定 Allure 结果目录
    cmd.extend(["--alluredir", str(args.allure)])

    # 设置环境变量（case可以通过 conftest.py 或 pytest_configure 读取）
    os.environ["TEST_ENV"] = args.env

    # 设置浏览器类型
    os.environ["TEST_BROWSER"] = args.browser

    # 执行命令
    logger.info(f"🚀 Running pytest with command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=BASE_DIR)
    return result.returncode == 0


def generate_reports(args):
    # """生成allure测试报告"""
    # 从 args 中获取用户指定的路径
    allure_dir = Path(args.allure)
    report_dir = Path(args.allure).parent / "allure-report"

    if not allure_dir.exists() or not any(allure_dir.iterdir()):
        logger.warning("⚠️ No Allure results found. Skipping report generation.")
        return

    logger.info(f"📊 Generating Allure report to: {report_dir}")
    try:
        # 生成报告（支持自定义输出目录）
        subprocess.run(
            ["allure", "generate", str(allure_dir), "-o", str(report_dir), "--clean"],
            check=True
        )
        logger.info(f"✅ Report generated successfully at: {report_dir}")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to generate Allure report: {e}")
    except FileNotFoundError:
        logger.error("❌ Allure command not found. Please install Allure first.")


def main():
    logger.info("======================== Start running test case ======================================== ")
    args = parse_args()
    success = run_pytest(args)
    logger.info("======================== End running test case ======================================== ")
    if success:
        generate_reports(args)
        sys.exit(0)
    else:
        logger.error("❌ Tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
