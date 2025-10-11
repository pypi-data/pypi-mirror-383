from typing import Optional, List
from prometheus_client import Histogram, Counter
import os
from loguru import logger


class RequestOperationMetrics:
    """
    如果启动prometheus则使用此类
    """

    def __init__(self, buckets: Optional[List[float]] = None):
        default_buckets = [0.1, 0.5, 1, 3, 5]
        self.buckets = buckets if buckets is not None else default_buckets
        self.pid = os.getpid()

    def add(self, key, cost): ...

    def add_error(self, key): ...


class PrometheusRequestOperationMetrics(RequestOperationMetrics):
    """
    算法接口中算法操作的耗时统计
    """

    def __init__(self, buckets: Optional[List[float]] = None):
        super().__init__(buckets=buckets)

        self.ops_duration = Histogram(
            "operation_duration_seconds",
            "Operation duration in seconds",
            ["operation", "pid"],
            buckets=self.buckets,
        )
        self.ops_error_cnt = Counter(
            "operation_errors_total",
            "The total number of errors in operations.",
            ["operation", "pid"],
        )

    def add(self, key, cost):
        self.ops_duration.labels(operation=key, pid=self.pid).observe(cost)

    def add_error(self, key):
        self.ops_error_cnt.labels(operation=key, pid=self.pid).inc(1)


def request_operation_metrics_factory(buckets: Optional[List[float]] = None) -> RequestOperationMetrics:
    is_use_prometheus: str = os.environ.get("ignore_request_operation_metrics", "True")
    if is_use_prometheus.lower() == "true":
        logger.debug("Use prometheus RequestOperationMetrics")
        return PrometheusRequestOperationMetrics(buckets=buckets)
    else:
        logger.debug("Use empty RequestOperationMetrics")
        return RequestOperationMetrics(buckets=buckets)
