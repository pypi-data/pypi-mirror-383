import time
import traceback
from functools import wraps
from typing import List

from loguru import logger

from huibiao_framework.backend import BasicException, BaseRespVo, CommonStatusCode
from huibiao_framework.backend.metrics.request_metrics import (
    request_operation_metrics_factory,
    RequestOperationMetrics,
)


class OperationTimeCostMetricSetting:

    __metric = None

    @classmethod
    def initialize(cls, buckets: List[float]):
        if cls.__metric is None:
            cls.__metric = request_operation_metrics_factory(buckets=buckets)
            logger.info(f"timing_and_exception_handler buckets => {buckets}")
        else:
            logger.warning("timing_and_exception_handler buckets already set!")

    @classmethod
    def get_metric_obj(cls) -> RequestOperationMetrics:
        assert cls.__metric is not None, \
            "Metric object is not initialized. Please call update_timing_and_exception_handler_buckets first"
        return cls.__metric


def timing_and_exception_handler(func):
    """
    装饰器：用于统计函数执行时间并捕获异常
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()

        request_id = kwargs.get("request_id", "unknown-reqid")

        try:
            # 执行原函数
            logger.info(f"ReqId: {request_id} | Function: {func.__name__} | Start")
            result = await func(*args, **kwargs)
            # 计算耗时
            elapsed_time = time.perf_counter() - start_time
            logger.info(
                f"ReqId: {request_id} | Function: {func.__name__} | COST:{elapsed_time:.4f}s"
            )
            OperationTimeCostMetricSetting.get_metric_obj().add(func.__name__, elapsed_time)
            return result
        except Exception as e:
            # 计算耗时
            elapsed_time = time.perf_counter() - start_time
            OperationTimeCostMetricSetting.get_metric_obj().add_error(func.__name__)
            # 记录异常信息和完整堆栈
            logger.error(
                f"ReqId: {request_id} | Function: {func.__name__} | COST:{elapsed_time:.4f}s | Exception: {str(e)}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            if isinstance(e, BasicException):
                return BaseRespVo(code=e.code, message=e.msg, result=None)
            return BaseRespVo.from_status_code(
                CommonStatusCode.INTERNAL_ERROR, msg=str(e)
            )

    return wrapper
