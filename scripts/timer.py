from typing import Callable
from datetime import timedelta
from threading import Thread
from time import sleep


class Timer:
    def __init__(self, time_input: timedelta, func: Callable):
        self.func = func
        self.is_running = False
        self.start_time = time_input
        self.time = self.start_time
        self.thread = None

    async def start(self):
        self.is_running = True
        self.thread = Thread(target=self.update)
        self.thread.start()

    def update(self):
        print(self.is_running)
        second = timedelta(seconds=1)
        zero = timedelta(seconds=0)
        while self.is_running:
            try:
                sleep(1)
                self.time -= second
                if self.time <= zero:
                    self.is_running = False
                    self.func()
                    break
            except Exception:
                return
        return

    async def stop(self):
        self.time = self.start_time
        self.is_running = False


