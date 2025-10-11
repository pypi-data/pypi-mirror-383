import os
from prometheus_client import Histogram, Counter
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Optional


class RequestMonitorMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, buckets: Optional[List[float]] = None):
        super().__init__(app)

        # 设置默认 buckets，如果用户未提供则使用默认值
        default_buckets = [0.1, 0.5, 1, 3, 5]
        self.buckets = buckets if buckets is not None else default_buckets

        # 动态创建 Histogram 指标，使用传入的 buckets
        self.request_duration = Histogram(
            "http_request_duration_seconds",
            "Request duration in seconds",
            ["uri", "pid"],
            buckets=self.buckets,
        )

        # 错误请求计数器
        self.error_requests = Counter(
            "http_error_requests", "error HTTP requests", ["uri", "status"]
        )

    async def dispatch(self, request: Request, call_next):
        # 规范化路径：去掉末尾的斜杠（根路径除外）
        path = request.url.path
        normalized_path = path.rstrip("/") if path != "/" else path

        # 使用动态创建的 Histogram 指标
        with self.request_duration.labels(uri=normalized_path, pid=os.getpid()).time():
            response = await call_next(request)

            # 记录错误请求
            if response.status_code >= 400:
                self.error_requests.labels(
                    uri=normalized_path, status=response.status_code
                ).inc()

            return response
