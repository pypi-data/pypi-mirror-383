# antispam_core/precise_engine.py
import asyncio
import time
from dataclasses import dataclass

@dataclass
class TickerStats:
    last_target_ns: int = 0
    last_wakeup_ns: int = 0
    last_jitter_ns: int = 0  # wakeup - target (>= 0)

class HiPrecisionTicker:
    """
    Drift-free asyncio ticker with hybrid coarse-sleep + fine spin.
    - Absolute scheduling: next_target = prev_target + period (no cumulative drift).
    - Coarse sleep via asyncio, then busy-wait for final microseconds.
    - Uses time.perf_counter_ns() (monotonic, high-resolution).

    Notes:
      * Sub-microsecond accuracy is NOT realistic on general OS with Python.
      * 'spin' burns CPU on the running core; keep margins reasonable.
      * Tune margins for your hardware/OS.

    Args:
      interval_sec: desired period in seconds (float).
      sleep_margin_ns: if remaining > (sleep_margin + spin_margin), we await asyncio.sleep.
      spin_margin_ns: final window to busy-wait (e.g., 50-200 µs).

    Stats:
      .stats.last_jitter_ns gives (actual_wakeup - scheduled_target) in ns.
    """

    __slots__ = (
        "period_ns", "sleep_margin_ns", "spin_margin_ns",
        "next_target_ns", "stats"
    )

    def __init__(self,
                 interval_sec: float,
                 sleep_margin_ns: int = 200_000,   # 200 µs
                 spin_margin_ns: int  = 50_000):   # 50 µs
        if interval_sec <= 0:
            raise ValueError("interval_sec must be > 0")
        self.period_ns = int(interval_sec * 1e9)
        if self.period_ns <= 1_000:  # sanity: <1 µs period is nonsense for Python
            raise ValueError("interval too small for Python environment")
        if sleep_margin_ns < 0 or spin_margin_ns < 0:
            raise ValueError("margins must be non-negative")
        self.sleep_margin_ns = int(sleep_margin_ns)
        self.spin_margin_ns  = int(spin_margin_ns)
        self.next_target_ns: int | None = None
        self.stats = TickerStats()

    async def sleep(self):
        now = time.perf_counter_ns()

        # First use: schedule at now + period (absolute target)
        if self.next_target_ns is None:
            self.next_target_ns = now + self.period_ns

        remaining = self.next_target_ns - now

        if remaining <= 0:
            # We're already late: skip sleeping, jump target forward
            # so we don't try to "catch up" with negative sleeps.
            self.stats.last_target_ns = self.next_target_ns
            self.stats.last_wakeup_ns = now
            self.stats.last_jitter_ns = now - self.next_target_ns
            self.next_target_ns = now + self.period_ns
            return

        # Coarse sleep: leave 'spin_margin_ns' to finish in busy-wait.
        # Also keep a 'sleep_margin_ns' cushion to reduce overshoot risk.
        coarse_threshold = self.sleep_margin_ns + self.spin_margin_ns
        if remaining > coarse_threshold:
            # target - spin_margin => leave that much for spinning
            coarse_sleep_ns = remaining - self.spin_margin_ns
            # asyncio.sleep takes seconds
            await asyncio.sleep(coarse_sleep_ns / 1e9)

        # Fine spin until target
        target = self.next_target_ns
        while True:
            now = time.perf_counter_ns()
            if now >= target:
                break
            # Tight spin: do nothing. If you see high CPU, you can insert
            # a minimal pause on some platforms via time.sleep(0) sporadically,
            # but that will hurt accuracy.

        # Record stats
        self.stats.last_target_ns = target
        self.stats.last_wakeup_ns = now
        self.stats.last_jitter_ns = now - target  # >= 0

        # Advance absolute target by exactly one period (no drift accumulation)
        self.next_target_ns = target + self.period_ns

    def reset(self):
        """Reset baseline; next sleep schedules from current time + period."""
        self.next_target_ns = None
        self.stats = TickerStats()
