from typing import Callable
from datetime import timedelta
import asyncio


class Timer:
    def __init__(self, time_input: timedelta, func: Callable, repeat: bool = False):
        self.func = func
        self.is_running = False
        self.start_time = time_input
        self.time = self.start_time
        self.loop = asyncio.get_running_loop()
        self.repeat = repeat
        self.task = None

    async def start(self):
        self.is_running = True
        self.task = self.loop.create_task(self.update())

    async def update(self):
        second = timedelta(seconds=1)
        zero = timedelta(seconds=0)
        while self.is_running:
            try:
                await asyncio.sleep(1)
                self.time -= second
                if self.time <= zero and not self.repeat:
                    self.is_running = False
                    await self.func()
                    break
                elif self.time <= zero and self.repeat:
                    self.time = self.start_time
                    await self.func()
            except Exception:
                return
        return

    async def stop(self):
        self.time = self.start_time
        self.is_running = False

    def __eq__(self, other):
        return isinstance(other, Timer) and self.start_time == other.start_time


