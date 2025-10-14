# antispam_core/spammer.py
import asyncio
import random
import logging
import os
import threading
from datetime import datetime
from typing import Dict, Callable, Any, List

from .client_manager import *
from .analytics_manager import analytics
from pyrogram import errors

# ============================================================
# ⚙️ راه‌اندازی سیستم لاگ اختصاصی (با نانوثانیه)
# ============================================================
class NanoFormatter(logging.Formatter):
    """Formatter سفارشی برای نمایش زمان دقیق تا نانوثانیه."""
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created)
        ns = int((record.created - int(record.created)) * 1_000_000_000)
        return f"{dt.strftime('%Y-%m-%d %H:%M:%S')}.{ns:09d}"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

os.makedirs("logs", exist_ok=True)
file_handler = logging.FileHandler("logs/spam_log.txt", encoding="utf-8")
formatter = NanoFormatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# جلوگیری از افزودن تکراری handler
if not any(
    isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", "").endswith("spam_log.txt")
    for h in logger.handlers
):
    logger.addHandler(file_handler)

# ============================================================
# 📤 تابع کمکی ارسال (یک‌بار)
# ============================================================
async def _attempt_send(cli, acc_phone: str, target: str, text: str):
    """ارسال پیام یک‌بار با pyrogram"""
    await cli.send_message(target, text)

# ============================================================
# 📤 safe_send: no-delay on error + fast reconnect
# ============================================================
async def safe_send(acc_phone: str, spam_config: dict, text: str, remove_client_from_pool) -> bool:
    """
    نسخهٔ بهینه برای ارسال بدون تاخیر:
    - اگر client قطع شده باشد → reconnect سریع
    - در هر نوع خطای دیگر → بلافاصله False برمی‌گرداند و ادامه می‌دهد (بدون sleep)
    - هیچ‌گونه drift یا backoff ایجاد نمی‌شود
    """
    try:
        # دریافت یا ساخت client
        cli = await get_or_start_client(acc_phone)
        if not cli:
            logger.warning(f"{acc_phone}: ⚠️ Client not available.")
            return False

        # بررسی اتصال و تلاش سریع برای reconnect
        if not getattr(cli, "is_connected", False):
            try:
                await cli.start()
                logger.info(f"{acc_phone}: 🔄 Client reconnected successfully.")
            except Exception as e:
                logger.error(f"{acc_phone}: ❌ Reconnect failed - {type(e).__name__}: {e}")
                try:
                    remove_client_from_pool(acc_phone)
                except Exception:
                    pass
                return False

        # قفل‌های per-account برای جلوگیری از تداخل Pyrogram
        global client_locks
        try:
            client_locks
        except NameError:
            client_locks = {}

        if acc_phone not in client_locks:
            client_locks[acc_phone] = asyncio.Lock()

        async with client_locks[acc_phone]:
            try:
                # ارسال پیام
                await _attempt_send(cli, acc_phone, spam_config["spamTarget"], text)
                logger.debug(f"{acc_phone}: ✅ Message sent.")
                return True

            except (errors.UserDeactivated, errors.AuthKeyUnregistered):
                logger.warning(f"{acc_phone}: ⚠️ Account deactivated/unregistered.")
                try:
                    remove_client_from_pool(acc_phone)
                except Exception:
                    pass
                return False

            except errors.ChatWriteForbidden:
                logger.warning(f"{acc_phone}: 🚫 Cannot send to {spam_config['spamTarget']}")
                return False

            except (errors.FloodWait, asyncio.TimeoutError, errors.RPCError) as e:
                # خطاهای موقت
                logger.warning(f"{acc_phone}: ⚠️ Temporary error {type(e).__name__}: {e}")
                return False

            except Exception as e:
                logger.warning(f"{acc_phone}: ❌ Unexpected send error - {type(e).__name__}: {e}")
                return False

    except Exception as e:
        logger.error(f"{acc_phone}: 💥 Fatal send error {type(e).__name__}: {e}")
        try:
            remove_client_from_pool(acc_phone)
        except Exception:
            pass
        return False

# ============================================================
# 🚀 run_spammer: drift-free batch scheduling (async core)
# ============================================================
async def run_spammer(spam_config: dict,
                      get_spam_texts: Callable[[], List[str]],
                      make_mention_html: Callable[[Any, str], str],
                      remove_client_from_pool: Callable[[str], None]):
    """
    اجرای دقیق اسپمر با زمان‌بندی بدون drift.
    بین شروع هر batch دقیقاً TimeSleep ثانیه فاصله خواهد بود.
    (این تابع همان API قبل را حفظ کرده و اکنون در یک Thread اجرا خواهد شد.)
    """

    base_delay = float(spam_config.get("TimeSleep", 2.0))   # مثال: 2
    batch_size = max(1, int(spam_config.get("BATCH_SIZE", 2)))
    loop = asyncio.get_event_loop()
    total_sent = 0

    logger.info(f"🚀 Spammer started | Delay: {base_delay:.3f}s | Batch size: {batch_size}")

    try:
        # زمان مرجع برای شروع اولین batch
        next_batch_start = loop.time()

        while spam_config.get("run", False):
            active_accounts = sorted(get_active_accounts())
            if not active_accounts:
                logger.warning("❌ هیچ اکانتی فعال نیست. اسپمر متوقف موقتاً.")
                await asyncio.sleep(1)
                next_batch_start = loop.time()
                continue

            texts = get_spam_texts()
            if not texts:
                await asyncio.sleep(1)
                next_batch_start = loop.time()
                continue

            # تقسیم اکانت‌ها به batchهای مساوی
            batches = [active_accounts[i:i + batch_size] for i in range(0, len(active_accounts), batch_size)]

            for batch_idx, batch in enumerate(batches, start=1):
                if not spam_config.get("run", False):
                    break

                now = loop.time()
                wait = next_batch_start - now
                if wait > 0:
                    # خواب دقیق تا زمان هدف
                    await asyncio.sleep(wait)

                batch_start_real = loop.time()
                drift = batch_start_real - next_batch_start
                logger.info(
                    f"⏱️ Batch {batch_idx:03d} started | target={next_batch_start:.6f} | real={batch_start_real:.6f} | drift={drift:+.4f}s | size={len(batch)}"
                )

                # آماده‌سازی متن مشترک این batch
                text = random.choice(texts)
                caption = spam_config.get("caption", "")
                if caption:
                    text = f"{text}\n{caption}"
                if spam_config.get("is_menshen"):
                    mention_html = make_mention_html(spam_config["useridMen"], spam_config["textMen"])
                    text = f"{text}\n{mention_html}"

                # اجرای هم‌زمان ارسال‌ها برای هر اکانت
                tasks = [
                    asyncio.create_task(safe_send(acc, spam_config, text, remove_client_from_pool))
                    for acc in batch
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # ثبت نتایج هر اکانت
                for acc, res in zip(batch, results):
                    success = (res is True)
                    try:
                        await analytics.update_stats(acc, success, spam_config["spamTarget"])
                    except Exception:
                        logger.debug("analytics.update_stats failed", exc_info=True)

                    if success:
                        logger.info(f"{acc}: ✅ Message sent successfully.")
                    else:
                        logger.warning(f"{acc}: ❌ Failed sending message (or in cooldown).")

                total_sent += sum(1 for r in results if r is True)

                # تعیین زمان شروع batch بعدی (بدون drift)
                next_batch_start = batch_start_real + base_delay
                logger.debug(f"📅 Next batch scheduled at {next_batch_start:.6f} (delay={base_delay:.3f}s)\n")

            # گزارش دوره‌ای
            if total_sent and total_sent % 100 == 0:
                logger.info(f"📊 Progress: {total_sent} messages sent so far...")

    except asyncio.CancelledError:
        logger.info("🛑 Spammer task cancelled.")
    except Exception as e:
        logger.exception(f"💥 Unhandled error in run_spammer: {type(e).__name__} - {e}")
    finally:
        logger.info("🛑 Spammer stopped gracefully.")
        logger.info(f"📈 Total messages successfully sent: {total_sent}")
        logger.info("------------------------------------------------------\n")
        try:
            await stop_all_clients()
        except Exception:
            logger.debug("stop_all_clients failed", exc_info=True)

# ============================================================
# 🧵 Threaded Runner: اجرای run_spammer داخل یک Thread
# ============================================================
class SpammerThreadingRunner(threading.Thread):
    """
    اجرای اسپمر داخل یک Thread اختصاصی (event loop جدا).
    API بیرونی تغییری نمی‌کند: همان spam_config و توابع کمکی را می‌گیرد.
    """
    def __init__(self,
                 spam_config: Dict[str, Any],
                 get_spam_texts: Callable[[], List[str]],
                 make_mention_html: Callable[[Any, str], str],
                 remove_client_from_pool: Callable[[str], None]):
        super().__init__(daemon=True)
        self.spam_config = spam_config or {}
        self.get_spam_texts = get_spam_texts
        self.make_mention_html = make_mention_html
        self.remove_client_from_pool = remove_client_from_pool

        self._stop_event = threading.Event()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._task: asyncio.Task | None = None

    def run(self):
        """راه‌اندازی event loop اختصاصی و اجرای کوروتین اصلی."""
        logger.info("🚀 Starting SpammerThreadingRunner...")
        try:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

            # اطمینان از run=True در شروع (متغیر موجود حفظ می‌شود)
            if "run" not in self.spam_config:
                self.spam_config["run"] = True

            self._task = self._loop.create_task(
                run_spammer(self.spam_config, self.get_spam_texts, self.make_mention_html, self.remove_client_from_pool)
            )

            self._loop.run_until_complete(self._task)

        except Exception as e:
            logger.exception(f"💥 Fatal error in SpammerThreadingRunner: {e}")
        finally:
            try:
                if self._loop and not self._loop.is_closed():
                    self._loop.run_until_complete(stop_all_clients())
            except Exception:
                pass
            try:
                if self._loop and not self._loop.is_closed():
                    self._loop.stop()
                    self._loop.close()
            except Exception:
                pass
            logger.info("🛑 SpammerThreadingRunner stopped.")

    def stop(self):
        """درخواست توقفِ امن از بیرونِ Thread."""
        logger.info("🧩 Stop requested for SpammerThreadingRunner.")
        # احترام به همان فلگ run که در کد شما استفاده می‌شود
        try:
            self.spam_config["run"] = False
        except Exception:
            pass

        # کنسل کردن تسک اصلی داخل لوپ
        if self._loop:
            def _cancel_task():
                if self._task and not self._task.done():
                    self._task.cancel()
            try:
                self._loop.call_soon_threadsafe(_cancel_task)
            except Exception:
                pass

# ============================================================
# 🧩 Helper sync API (اختیاری): شروع/توقف ساده
# ============================================================
# یک سینگلتون کوچک برای راحتی — در صورت نیاز
_spammer_runner_singleton: SpammerThreadingRunner | None = None

def start_spammer_thread(spam_config: dict,
                         get_spam_texts: Callable[[], List[str]],
                         make_mention_html: Callable[[Any, str], str],
                         remove_client_from_pool: Callable[[str], None]) -> SpammerThreadingRunner:
    """
    شروع اسپمر در یک Thread. همان spam_config و توابع کمکی را می‌گیرد.
    """
    global _spammer_runner_singleton
    if _spammer_runner_singleton and _spammer_runner_singleton.is_alive():
        logger.info("ℹ️ Spammer thread is already running.")
        return _spammer_runner_singleton

    runner = SpammerThreadingRunner(spam_config, get_spam_texts, make_mention_html, remove_client_from_pool)
    runner.start()
    _spammer_runner_singleton = runner
    return runner

def stop_spammer_thread():
    """توقف امن ترد اسپمر (اگر فعال باشد)."""
    global _spammer_runner_singleton
    if _spammer_runner_singleton and _spammer_runner_singleton.is_alive():
        _spammer_runner_singleton.stop()
        _spammer_runner_singleton.join(timeout=5)
        _spammer_runner_singleton = None
        logger.info("✅ Spammer thread joined and cleared.")
    else:
        logger.info("ℹ️ No running spammer thread to stop.")
