# antispam_core/spammer.py
import asyncio
import random
import logging
import os
import math
from typing import Set, Dict
from pyrogram import errors
from .precise_engine import PreciseTicker
from . import client_manager
from .analytics_manager import analytics

# ============================================================
# ⚙️ راه‌اندازی سیستم لاگ اختصاصی
# ============================================================
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

os.makedirs("logs", exist_ok=True)
file_handler = logging.FileHandler("logs/spam_log.txt", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(formatter)

if not any(
    isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", "").endswith("spam_log.txt")
    for h in logger.handlers
):
    logger.addHandler(file_handler)

# ============================================================
# ✅ پیکربندی ایمن و پارامترهای پیش‌فرض
# ============================================================
MAX_RETRIES = 2                # تلاش مجدد حداکثر برای هر ارسال
BASE_BACKOFF = 1.5             # ضریب بک‌آف برای retries (s)
FLOOD_COOLDOWN_CAP = 3600     # حداکثر زمان cooldown برای FloodWait (s)

# نگهداری وضعیت cooldown برای اکانت‌ها (resume_timestamp)
_account_cooldowns: Dict[str, float] = {}

# قفل نگهداری همزمانی برای هر اکانت (از client_manager هم استفاده می‌شود)
# client_manager.client_locks باید دیکشنری‌ای موجود باشد، ولی اگر نباشد تعریف می‌کنیم
if not hasattr(client_manager, "client_locks"):
    client_manager.client_locks = {}

# ============================================================
# 🧰 توابع کمکی
# ============================================================
def is_in_cooldown(phone: str) -> bool:
    ts = _account_cooldowns.get(phone)
    if not ts:
        return False
    return ts > asyncio.get_event_loop().time()

def set_cooldown(phone: str, seconds: float):
    resume = asyncio.get_event_loop().time() + seconds
    _account_cooldowns[phone] = resume
    logger.info(f"{phone}: ⏳ Put on cooldown for {seconds:.1f}s (resume @ {resume:.1f})")

def clear_expired_cooldowns():
    now = asyncio.get_event_loop().time()
    expired = [p for p, t in _account_cooldowns.items() if t <= now]
    for p in expired:
        _account_cooldowns.pop(p, None)
        logger.info(f"{p}: ✅ Cooldown expired")

async def _attempt_send(cli, acc_phone: str, target: str, text: str):
    """Try to send once, raising exceptions up to caller to handle specialized behavior."""
    # Use pyrogram send_message
    await cli.send_message(target, text)

# ============================================================
# 📤 ارسال امن با retry، backoff و مدیریت FloodWait
# ============================================================
async def safe_send(acc_phone: str, spam_config: dict, text: str, remove_client_from_pool) -> bool:
    """
    ارسال امن برای هر اکانت:
      - مدیریت reconnect
      - تلاش محدود (MAX_RETRIES)
      - exponential backoff بین تلاش‌ها
      - مدیریت errors.FloodWait: برنامه‌ریزی cooldown برای اکانت
      - در صورت خطای غیرقابل‌برگشت، اکانت از pool حذف می‌شود (callback remove_client_from_pool)
    بازگشت: True اگر ارسال موفق باشد، False در غیر این صورت.
    """
    try:
        # اگر اکانت در cooldown است، زود بازگردان False (بدون تلاش)
        if is_in_cooldown(acc_phone):
            logger.info(f"{acc_phone}: ⚠️ Skipping send because account is in cooldown.")
            return False

        cli = await client_manager.get_or_start_client(acc_phone)
        if not cli:
            logger.warning(f"{acc_phone}: ⚠️ Client not available.")
            return False

        # اگر کلاینت قطع است، تلاش برای اتصال مجدد (کوتاه و محدود)
        if not getattr(cli, "is_connected", False):
            try:
                await cli.start()
                logger.info(f"{acc_phone}: 🔄 Client reconnected successfully.")
            except Exception as e:
                logger.error(f"{acc_phone}: ❌ Failed to reconnect - {type(e).__name__}: {e}")
                # احتمالاً مشکل جدی؛ حذف از pool
                try:
                    remove_client_from_pool(acc_phone)
                except Exception:
                    pass
                return False

        # اطمینان از وجود قفل برای این اکانت
        if acc_phone not in client_manager.client_locks:
            client_manager.client_locks[acc_phone] = asyncio.Lock()

        async with client_manager.client_locks[acc_phone]:
            attempt = 0
            while attempt <= MAX_RETRIES:
                try:
                    await _attempt_send(cli, acc_phone, spam_config["spamTarget"], text)
                    return True

                except errors.FloodWait as e:
                    # FloodWait: بلافاصله اکانت را cooldown کن و بازگشت False
                    wait = e.value if hasattr(e, "value") else getattr(e, "x", 0)
                    # حداقل و حداکثر را منطقی حفظ کن
                    wait = max(1, min(wait, FLOOD_COOLDOWN_CAP))
                    logger.warning(f"{acc_phone}: ⏰ FloodWait {wait}s (code:{getattr(e, 'value', 'n/a')})")
                    set_cooldown(acc_phone, wait)
                    # صبر در این تابع به اندازهٔ wait ضروری نیست — cooldown کافی است.
                    return False

                except (errors.UserDeactivated, errors.AuthKeyUnregistered) as e:
                    logger.warning(f"{acc_phone}: ⚠️ Account deactivated or unregistered - {type(e).__name__}")
                    try:
                        remove_client_from_pool(acc_phone)
                    except Exception:
                        pass
                    return False

                except errors.ChatWriteForbidden:
                    logger.warning(f"{acc_phone}: 🚫 Cannot send message to {spam_config['spamTarget']}")
                    return False

                except Exception as e:
                    # سایر خطاها: تلاش مجدد با backoff تصاعدی
                    attempt += 1
                    if attempt > MAX_RETRIES:
                        logger.warning(f"{acc_phone}: ❌ Send failed after {MAX_RETRIES} retries - {type(e).__name__}: {e}")
                        return False
                    backoff = BASE_BACKOFF * (2 ** (attempt - 1))
                    # حد معقول برای backoff (مثلاً 60s)
                    backoff = min(backoff, 60)
                    jitter = random.uniform(0.1, 0.5)
                    wait_time = backoff + jitter
                    logger.info(f"{acc_phone}: 🔁 Retry {attempt}/{MAX_RETRIES} after {wait_time:.1f}s due to {type(e).__name__}")
                    await asyncio.sleep(wait_time)
                    # then loop to retry

    except Exception as e:
        logger.error(f"{acc_phone}: 💥 Fatal send error {type(e).__name__} - {e}")
        try:
            remove_client_from_pool(acc_phone)
        except Exception:
            pass
        return False

# ============================================================
# 🚀 اجرای اسپمر اصلی (بهینه، دقیق و امن)
# ============================================================
async def run_spammer(spam_config: dict, get_spam_texts, make_mention_html, remove_client_from_pool):
    """
    Main spam loop:
      - uses PreciseTicker for consistent global pacing (interval = spam_config['TimeSleep'] or 1.0)
      - supports batching and concurrency per batch
      - manages per-account cooldowns to prevent FloodWaits
    Important params in spam_config:
      - 'TimeSleep': float (seconds) — global interval between batch starts (recommended 1.0)
      - 'BATCH_SIZE': int — number of accounts to run concurrently per batch
      - 'run': bool — keep loop running while True
      - 'spamTarget': str — chat/user target
      - 'caption', 'is_menshen', etc. as before
    """
    # prepare
    base_delay = float(spam_config.get("TimeSleep", 1.0))
    batch_size = max(1, int(spam_config.get("BATCH_SIZE", 1)))
    ticker = PreciseTicker(interval=base_delay)

    total_sent = 0

    logger.info(f"🚀 Spammer started | Delay: {base_delay}s | Batch size: {batch_size}")

    try:
        while spam_config.get("run", False):
            # cleanup expired cooldowns
            clear_expired_cooldowns()

            # refresh active accounts (live snapshot)
            active_accounts: Set[str] = set(client_manager.get_active_accounts())
            if not active_accounts:
                logger.warning("❌ هیچ اکانتی فعال نیست. اسپمر متوقف موقتاً.")
                await asyncio.sleep(1)
                continue

            # filter out accounts currently in cooldown
            acc_list = sorted([a for a in active_accounts if not is_in_cooldown(a)])
            if not acc_list:
                # همه در cooldown هستند — کمی صبر کن و ادامه بده
                logger.info("تمام اکانت‌ها در cooldown هستند؛ کمی صبر می‌کنیم...")
                await asyncio.sleep(min(5, base_delay))
                continue

            texts = get_spam_texts()
            if not texts:
                await asyncio.sleep(1)
                continue

            text = random.choice(texts)
            caption = spam_config.get("caption", "")
            if caption:
                text = f"{text}\n{caption}"

            if spam_config.get("is_menshen"):
                mention_html = make_mention_html(spam_config["useridMen"], spam_config["textMen"])
                text = f"{text}\n{mention_html}"

            # create batches
            batches = [acc_list[i:i + batch_size] for i in range(0, len(acc_list), batch_size)]

            # iterate batches; ticker ensures consistent spacing between batch starts
            for batch in batches:
                if not spam_config.get("run", False):
                    break

                # Launch send tasks for this batch concurrently but let safe_send control per-account locking
                tasks = [
                    asyncio.create_task(safe_send(acc, spam_config, text, remove_client_from_pool))
                    for acc in batch
                ]

                # Wait for all tasks to complete (but do not let one long task block next batch scheduling
                # because PreciseTicker is independent — we wait here to collect results and update stats.)
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # record analytics and logs
                for acc, res in zip(batch, results):
                    success = res is True
                    try:
                        await analytics.update_stats(acc, success, spam_config["spamTarget"])
                    except Exception:
                        # analytics mustn't break the loop
                        logger.debug("analytics.update_stats failed", exc_info=True)

                    if success:
                        logger.info(f"{acc}: ✅ Message sent successfully.")
                    else:
                        logger.warning(f"{acc}: ❌ Failed sending message (or in cooldown).")

                total_sent += sum(1 for r in results if r is True)

                # global pacing: wait exactly interval before starting next batch
                await ticker.sleep()

            # periodic progress log
            if total_sent and total_sent % 500 == 0:
                logger.info(f"📊 Progress update: {total_sent} messages sent so far...")

    except asyncio.CancelledError:
        logger.info("🛑 Spammer task cancelled.")
    except Exception as e:
        logger.exception(f"💥 Unhandled error in run_spammer: {type(e).__name__} - {e}")
    finally:
        logger.info("🛑 Spammer stopped gracefully.")
        logger.info(f"📈 Total messages successfully sent: {total_sent}")
        logger.info("------------------------------------------------------\n")
        # best-effort stop clients
        try:
            await client_manager.stop_all_clients()
        except Exception:
            logger.debug("stop_all_clients failed", exc_info=True)
