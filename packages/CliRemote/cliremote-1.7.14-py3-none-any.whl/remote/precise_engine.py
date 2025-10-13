# antispam_core/precise_engine.py
import asyncio
import time

class PreciseTicker:
    """
    A drift-free ticker.
    Usage:
      ticker = PreciseTicker(interval=1.0)
      while running:
          # do work
          await ticker.sleep()
    Behavior:
      - Ensures interval spacing between wakes without accumulating drift.
      - If the work took longer than the interval, it schedules next wake as now + interval
        (so it doesn't try to "catch up" by sleeping negative amounts).
      - On first use, it sets the baseline relative to time.perf_counter().
    """
    def __init__(self, interval: float):
        if interval <= 0:
            raise ValueError("interval must be > 0")
        self.interval = float(interval)
        self.next_tick = None

    async def sleep(self):
        now = time.perf_counter()
        if self.next_tick is None:
            # first tick: schedule next at now + interval
            self.next_tick = now + self.interval

        delay = self.next_tick - now

        if delay > 0:
            # normal case: wait remaining time
            await asyncio.sleep(delay)
            # advance to next slot
            self.next_tick += self.interval
        else:
            # work took longer than interval; reset baseline to now + interval
            self.next_tick = now + self.interval
            # don't sleep now (we are already late)

    def reset(self):
        """Reset baseline so next sleep schedules from current time."""
        self.next_tick = None
