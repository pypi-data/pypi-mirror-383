import asyncio
import time
from functools import wraps
from loguru import logger


def func_time_cost(step_name=None):
    """
    记录函数执行耗时，并支持指定步骤名称

    参数:
        step_name: 步骤名称，默认为函数名
    """

    def decorator(func):
        @wraps(func)  # 保留原函数元信息
        def wrapper(*args, **kwargs):
            nonlocal step_name
            step_name = step_name or func.__name__

            # 执行原函数并处理返回值
            result = None
            start_time = time.perf_counter()
            try:
                logger.debug(f"StepStart [{step_name}]")
                result = func(*args, **kwargs)

                # 检查是否为协程对象
                if asyncio.iscoroutine(result):

                    async def wrapped_coroutine():
                        try:
                            return await result
                        finally:
                            logger.debug(
                                f"StepTimeCost | [{step_name}][{time.perf_counter() - start_time:.6f}]秒"
                            )

                    return wrapped_coroutine()

                # 普通函数直接返回结果
                return result
            finally:
                # 普通函数在这里记录时间
                if not asyncio.iscoroutine(result):
                    logger.debug(
                        f"StepTimeCost | [{step_name}][{time.perf_counter() - start_time:.6f}]秒"
                    )

        return wrapper

    return decorator


class TimeCostTik:
    """
    用于记录连续时间点之间耗时的工具类。
    每次调用 `tik(name)` 会打印上一次调用到本次的时间差（阶段耗时），
    以及从初始化到当前的时间差（总耗时）。
    示例用法
    time_usage_tool = TimeUsageTool()
    time_usage_tool.tik("初始化")
    time.sleep(1)
    time_usage_tool.tik("阶段1")
    time.sleep(2)
    time_usage_tool.tik("阶段2")
    输出
    [初始化], 总耗时 0.500123 秒
    [阶段1], 阶段耗时 1.000456 秒, 总耗时 1.500579 秒
    [阶段2], 阶段耗时 2.000789 秒, 总耗时 3.501368 秒
    """

    def __init__(self, reqid: str):
        self._tik = None  # 上一次调用 tik 的时间
        self._start = None
        self.reqid = reqid

    def tik(self, name: str):
        """
        记录从上一次调用到本次的时间差（阶段耗时），
        并记录从初始化到当前的时间差（总耗时）。
        :param name: 标识当前阶段的名称
        """
        time_now = time.perf_counter()
        phase_cost = None
        if self._start is None:
            self._start = time_now
        total_cost = time_now - self._start

        if self._tik is not None:
            phase_cost = time_now - self._tik

        # 打印信息
        if phase_cost is not None:
            logger.debug(
                f"Reqid: {self.reqid} [{name}], 阶段耗时 {phase_cost:.3f} 秒, 总耗时 {total_cost:.3f} 秒"
            )
        else:
            logger.debug(
                f"Reqid: {self.reqid} [{name}], 总耗时 {total_cost:.3f} 秒"
            )  #  首次调用

        self._tik = time_now  # 更新上次调用时间为当前时间
