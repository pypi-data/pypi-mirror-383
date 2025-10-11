import asyncio
import os
from abc import ABC, abstractmethod
from typing import List, Type

import psutil
from prometheus_client import Gauge

from loguru import logger


class AbstractMetricCollector(ABC):
    """指标收集器抽象基类"""

    def __init__(self, process: psutil.Process, pid: int, **kwargs):
        self.process = process
        self.pid = pid

    @abstractmethod
    async def collect(self):
        """收集指标数据"""
        pass


class CPUMetricCollector(AbstractMetricCollector):
    """CPU使用率指标收集器"""

    def __init__(self, process: psutil.Process, pid: int):
        super().__init__(process, pid)
        self.gauge = Gauge(
            "cpu_usage_percent",
            "CPU usage in percent",
            ["pid"],
            multiprocess_mode="all",
        )

    async def collect(self):
        cpu_usage = self.process.cpu_percent()
        self.gauge.labels(pid=self.pid).set(cpu_usage)


class MemoryMetricCollector(AbstractMetricCollector):
    """内存使用量指标收集器"""

    def __init__(self, process: psutil.Process, pid: int):
        super().__init__(process, pid)
        self.gauge_rss = Gauge(
            "resident_memory_usage_mb",
            "Resident Memory usage in MB",
            ["pid"],
            multiprocess_mode="all"
        )
        self.gauge_vms = Gauge(
            "virtual_memory_usage_mb",
            "Virtual Memory usage in MB",
            ["pid"],
            multiprocess_mode="all"
        )

    async def collect(self):
        memory_info = self.process.memory_info()
        rss = memory_info.rss / (1024 * 1024) # resident set size resident set size
        vms = memory_info.vms / (1024 * 1024) # virtual memory size
        self.gauge_rss.labels(pid=self.pid).set(rss)
        self.gauge_vms.labels(pid=self.pid).set(vms)


class ThreadCountMetricCollector(AbstractMetricCollector):
    """线程数指标收集器"""

    def __init__(self, process: psutil.Process, pid: int):
        super().__init__(process, pid)
        self.gauge = Gauge(
            "thread_count", "Number of threads", ["pid"], multiprocess_mode="all"
        )

    async def collect(self):
        thread_count = self.process.num_threads()
        self.gauge.labels(pid=self.pid).set(thread_count)


class SystemMetricsMonitor:
    """系统指标监控器 - 采用组装模式"""

    def __init__(self):
        self.pid = os.getpid()
        self.process = psutil.Process(self.pid)
        self.collectors: List[AbstractMetricCollector] = []

    def add(self, collector_classes: Type[AbstractMetricCollector], **kwargs) -> 'SystemMetricsMonitor':
        self.collectors.append(collector_classes(self.process, self.pid, **kwargs))
        return self

    def cpu(self):
        return self.add(CPUMetricCollector)

    def memory(self):
        return self.add(MemoryMetricCollector)

    def thread(self):
        return self.add(ThreadCountMetricCollector)

    def register_default_collectors(self) -> 'SystemMetricsMonitor':
        """
        组装默认指标收集器
        """
        self.add(CPUMetricCollector)
        self.add(MemoryMetricCollector)
        self.add(ThreadCountMetricCollector)
        return self

    async def run_monitor(self, interval_sec: int = 10):
        """运行监控任务"""

        async def work():
            while True:
                # 执行所有收集器的收集任务
                for collector in self.collectors:
                    await collector.collect()

                await asyncio.sleep(interval_sec)

        if len(self.collectors) == 0:
            self.register_default_collectors()

        logger.info(f"Start system metrics monitor, interval: {interval_sec}s, collector num = {len(self.collectors)}")

        asyncio.create_task(work())
