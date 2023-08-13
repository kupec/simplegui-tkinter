import asyncio
import threading
import queue
from functools import wraps

from loguru import logger


coro_queue = queue.Queue(100)


def start_async_worker():
    def worker_thread():
        asyncio.run(worker())

    threading.Thread(target=worker_thread, daemon=True).start()


async def worker():
    tasks = set()

    while True:
        try:
            block = len(asyncio.all_tasks()) == 1
            coro = coro_queue.get(block)
        except queue.Empty:
            await asyncio.sleep(0.1)
        else:
            task = asyncio.create_task(task_wrapper(coro))
            tasks.add(task)
            task.add_done_callback(tasks.discard)

            coro_queue.task_done()


@logger.catch()
async def task_wrapper(coro):
    await coro


def async_task(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        coro_queue.put(fn(*args, **kwargs))

    return wrapper
