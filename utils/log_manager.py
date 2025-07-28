import os.path
import socket
import sys
import time
from pathlib import Path

from loguru import logger


class LogManager:
    _instance = None

    # 单例模式,避免反复初始化日志管理器
    def __new__(cls, log_dir=None, file_level="INFO", console_level="INFO"):
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
            cls._instance._init_logger(log_dir, file_level, console_level)
        return cls._instance

    def _init_logger(self, log_dir, file_level, console_level):
        self._logger = logger
        self._logger.remove()  # 移除默认的console handle

        # 默认路径为当前执行脚本所在的目录
        if not log_dir:
            base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
            log_dir = os.path.join(base_dir, "log")
        Path(log_dir).mkdir(parents=True, exist_ok=True)

        # 日志文件完整路径
        log_file_name = self._generate_log_filename()
        self._log_path = os.path.join(log_dir, log_file_name)

        # 添加日志文件输出
        self._logger.add(
            self._log_path,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            ),
            level=file_level.upper(),
            enqueue=True,
            backtrace=True,
            diagnose=True
        )

        # 控制台输出
        self._logger.add(
            sys.stdout,
            format=(
                "<white>{time:YYYY-MM-DD HH:mm:ss}</white>|"
                "<level>{level: <8}</level> | <cyan>{message}</cyan>"
            ),
            level=console_level.upper(),
            enqueue=True
        )

    def _generate_log_filename(self):
        timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
        ip = self._get_host_ip().replace(".", "_")
        return f"TA-{timestamp}-{ip}.log"

    @staticmethod
    def _get_host_ip():
        try:
            with socket.socket(socket.AF_INET, socket.SOL_SOCKET) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"

    def get_logger(self):
        return self._logger

    def get_log_path(self):
        return self._log_path

        # 添加日志级别方法

    def debug(self, message, *args, **kwargs):
        self._logger.debug(message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        self._logger.info(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self._logger.warning(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self._logger.error(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        self._logger.critical(message, *args, **kwargs)

    def exception(self, message, *args, **kwargs):
        self._logger.exception(message, *args, **kwargs)
