import sys
from typing import Optional

from loguru import logger
import os


class LogSetup:
    FORMAT = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>p-{process}</cyan> | "
        "<cyan>t-{thread}</cyan> | "
        "<cyan>{thread.name}</cyan> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    __IS_SET_ROTATE = False

    @classmethod
    def rotate_daily(
        cls,
        *,
        log_dir: str,
        service_name: str,
        add_pid_suffix: bool = True,
        save_info: bool = True,
        save_debug: bool = True,
        stderr_colorize: bool = True,
        run_id_suffix: Optional[str] = None
    ):
        """
        日志输出终端和落盘
        : params: log_dir: 日志目录
        : params: service_name: 服务名
        : params: add_pid_suffix: 是否添加进程ID后缀
        : params: save_info: 是否保存INFO级别日志
        : params: save_debug: 是否保存DEBUG级别日志
        : params: stderr_colorize: 是否启用终端颜色显示
        : params: run_id_suffix: 运行ID后缀，用于避免多副本时的冲突
        """
        if cls.__IS_SET_ROTATE:
            return

        logger.remove()  # 清空设置，防止重复

        os.makedirs(log_dir, exist_ok=True)
        pid_suffix = f"_{os.getpid()}" if add_pid_suffix else ""
        run_id_suffix = f"_r{run_id_suffix}" if run_id_suffix else ""

        # 添加终端处理器（控制台输出）
        logger.add(
            sink=sys.stderr,  # 输出到标准错误流
            level="DEBUG",  # 终端显示更详细的DEBUG日志
            format=cls.FORMAT,
            colorize=stderr_colorize,  # 启用颜色显示
            backtrace=True,  # 堆栈信息显示在终端
        )

        if save_info:
            # 配置 INFO 及以上级别日志
            logger.add(
                os.path.join(log_dir, f"{service_name}_info{pid_suffix}{run_id_suffix}.log"),
                rotation="1 day",  # 每日滚动
                filter=lambda record: record["level"].no >= 20,
                format=cls.FORMAT,
                enqueue=True,
            )

        if save_debug:
            # 配置 DEBUG 级别日志
            logger.add(
                os.path.join(log_dir, f"{service_name}_debug{pid_suffix}{run_id_suffix}.log"),
                rotation="1 day",  # 每日滚动
                level="DEBUG",
                filter=lambda record: record["level"].no >= 10,
                format=cls.FORMAT,
                enqueue=True,
            )

        logger.info("日志设置完成")
        cls.__IS_SET_ROTATE = True
