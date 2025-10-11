import threading
import time
from pydantic import BaseModel, Field
from typing import List, Optional
import os
from datetime import datetime, timedelta
from loguru import logger


class LogInfo(BaseModel):
    """
    日志信息
    """
    file_path: str = Field(..., description="日志文件路径")
    file_size: Optional[int] = None  # 日志文件大小
    create_time: Optional[datetime] = None  # 日志文件创建时间
    modify_time: Optional[datetime] = None  # 日志文件修改时间
    access_time: Optional[datetime] = None  # 日志文件访问时间

    @classmethod
    def gen(cls, file_path: str):
        if not os.path.exists(file_path):
            return cls(file_path=file_path)
        return cls(
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            create_time=datetime.fromtimestamp(os.path.getctime(file_path)),
            modify_time=datetime.fromtimestamp(os.path.getmtime(file_path)),
            access_time=datetime.fromtimestamp(os.path.getatime(file_path)),
        )


class LogCleaner:
    """
    清理时间较长的日志，默认保留60天的日志
    """

    def __init__(self, log_dir: str, retention_day: int = 60):
        """
        :param log_dir: 日志目录
        :param retention_day: 保留天数
        """
        self.retention_day = retention_day
        self.log_dir = log_dir
        self.current_time: datetime = datetime.now()
        self.threshold_time: datetime = self.current_time - timedelta(
            days=self.retention_day
        )

    def scan_log(self) -> List[LogInfo]:
        """
        扫描日志目录，返回所有日志文件
        """
        log_files = []
        if os.path.exists(self.log_dir):
            log_files = [
                LogInfo.gen(os.path.join(self.log_dir, file))
                for file in os.listdir(self.log_dir)
                if file.endswith(".log")
            ]
        return log_files

    def judge_is_old_log(self, log_file: LogInfo) -> bool:
        """
        判断日志文件是否过期
        过期标准:
        """
        if log_file.modify_time and log_file.modify_time < self.threshold_time:
            return True
        return False

    def extract_old_log(self) -> List[LogInfo]:
        """
        提取过期的日志文件
        """
        log_files = self.scan_log()

        if not log_files:
            logger.debug("No log files found")
            return []

        logger.debug(
            f"[ExtractOldLogFiles]: scan [{len(log_files)}] logs from [{self.log_dir}]"
        )

        old_log_files = [o for o in log_files if self.judge_is_old_log(o)]

        logger.debug(
            f"[ExtractOldLogFiles]: extract [{len(old_log_files)}] old logs, threshold day [{self.threshold_time}]"
        )

        return old_log_files

    def delete_log(self, log_file: List[LogInfo]):
        """
        删除日志文件
        """
        if log_file:
            logger.debug(f"[DeleteLogFiles]: Start to delete [{len(log_file)}] logs")
            cnt = 0
            for log in log_file:
                try:
                    os.remove(log.file_path)
                    logger.debug(f"[DeleteLogFiles]: Delete log [{log.file_path}]")
                    cnt += 1
                except FileNotFoundError as e:
                    logger.warning(
                        f"[DeleteLogFiles]: Failed to delete log [{log.file_path}], error [{e}]"
                    )

            logger.debug(f"[DeleteLogFiles]: Delete [{cnt}]/[{len(log_file)}] logs")

    def delete_lod_log(self):
        """
        删除过时的日志文件
        """
        old_logs = self.extract_old_log()
        self.delete_log(old_logs)

    @classmethod
    def schedule_run(cls, log_dir: str, retention_day: int = 60):
        """
        启动线程，定时清理日志
        """
        # 创建线程
        interval = 60 * 60 * 24

        def worker():
            while True:
                log_cleaner = LogCleaner(log_dir, retention_day)
                logger.debug(
                    f"pid={os.getpid()} | [ScheduleRun]: Start to run log cleaner, log dir [{log_dir}], retention day [{retention_day}]"
                )
                log_cleaner.delete_lod_log()
                time.sleep(interval)  # 暂停一天

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
