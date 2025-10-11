# antispam_core/precise_engine.py
import asyncio, time

class PreciseTicker:
    def __init__(self, interval: float):
        self.interval = float(interval)
        self.next_tick = time.perf_counter()

    async def sleep(self):
        """خواب دقیق بدون drift در زمان"""
        self.next_tick += self.interval
        delay = self.next_tick - time.perf_counter()
        if delay > 0:
            await asyncio.sleep(delay)
        else:
            self.next_tick = time.perf_counter()  # ریست در صورت عقب افتادن

    def reset(self):
        self.next_tick = time.perf_counter()
