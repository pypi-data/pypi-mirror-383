# antispam_core/precise_engine.py
import asyncio, time

class PreciseTicker:
    def __init__(self, interval: float):
        self.interval = float(interval)
        self.start_time = time.perf_counter()
        self.tick_count = 0

    async def sleep(self):
        """خواب دقیق در بازه‌های زمانی ثابت بدون انباشته شدن تاخیر"""
        self.tick_count += 1
        target = self.start_time + self.tick_count * self.interval
        delay = target - time.perf_counter()
        if delay > 0:
            await asyncio.sleep(delay)
        else:
            # اگر از زمان هدف گذشت، فقط ادامه بده بدون reset
            # (بهترین برای کنترل دقیق نرخ اجرا در طولانی‌مدت)
            pass

    def reset(self):
        self.start_time = time.perf_counter()
        self.tick_count = 0