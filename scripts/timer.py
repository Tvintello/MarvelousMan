from typing import Callable
import asyncio
from datetime import timedelta


class Timer:
    def __init__(self, time_input: timedelta, func: Callable):
        self.func = func
        self.is_running = False
        self.start_time = time_input
        self.time = self.start_time

    async def start(self):
        self.is_running = True
        second = timedelta(seconds=1)
        zero = timedelta(seconds=0)
        while self.is_running:
            try:
                await asyncio.sleep(1)
                self.time -= second
                if self.time <= zero:
                    self.is_running = False
                    await self.func()
                    break
            except Exception:
                break

    async def stop(self):
        self.time = self.start_time
        self.is_running = False


