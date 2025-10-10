import inspect
import asyncio
import nest_asyncio
from concurrent.futures import ThreadPoolExecutor

nest_asyncio.apply()

# 全局线程池，用于在单独线程中运行异步函数
_async_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="AsyncCallback")


def _run_async_in_thread(coro_func, args, kwargs):
    """在独立线程中运行异步函数"""

    def run_in_new_loop():
        # 在新线程中创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            if inspect.isasyncgenfunction(coro_func):

                async def collect_async_gen():
                    return [item async for item in coro_func(*args, **kwargs)]

                return loop.run_until_complete(collect_async_gen())
            else:
                coro = coro_func(*args, **kwargs)
                return loop.run_until_complete(coro)
        finally:
            loop.close()

    future = _async_executor.submit(run_in_new_loop)
    return future.result()


def call_func(func, args=None, kwargs=None):
    """
    args:是一个元组
    kwargs:是一个字典
    """
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}

    if inspect.isgeneratorfunction(func):
        return list(func(*args, **kwargs))
    elif inspect.isasyncgenfunction(func) or inspect.iscoroutinefunction(func):
        # 对于异步函数，总是在独立线程中运行
        return _run_async_in_thread(func, args, kwargs)
    else:
        return func(*args, **kwargs)
