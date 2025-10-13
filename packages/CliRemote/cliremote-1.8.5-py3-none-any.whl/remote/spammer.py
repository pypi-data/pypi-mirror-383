# antispam_core/spammer.py
import asyncio
import random
import logging
import os
import math
from datetime import datetime
from typing import Set, Dict
from pyrogram import errors
from .precise_engine import PreciseTicker
from . import client_manager
from .analytics_manager import analytics

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

# استفاده از NanoFormatter به جای Formatter عادی
formatter = NanoFormatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# جلوگیری از افزودن تکراری handler
if not any(
    isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", "").endswith("spam_log.txt")
    for h in logger.handlers
):
    logger.addHandler(file_handler)

# ============================================================
# ✅ پیکربندی ایمن و پارامترهای پیش‌فرض
# ============================================================
MAX_RETRIES = 3
BASE_BACKOFF = 1.5
FLOOD_COOLDOWN_CAP = 3600
_account_cooldowns: Dict[str, float] = {}

if not hasattr(client_manager, "client_locks"):
    client_manager.client_locks = {}

# ============================================================
# 🧰 توابع کمکی
# ============================================================
async def _attempt_send(cli, acc_phone: str, target: str, text: str):
    """ارسال پیام یک‌بار با pyrogram"""
    await cli.send_message(target, text)

# ============================================================
# 📤 ارسال امن با retry، backoff و FloodWait
# ============================================================
async def safe_send(acc_phone: str, spam_config: dict, text: str, remove_client_from_pool) -> bool:
    try:
        cli = await client_manager.get_or_start_client(acc_phone)
        if not cli:
            logger.warning(f"{acc_phone}: ⚠️ Client not available.")
            return False

        if not getattr(cli, "is_connected", False):
            try:
                await cli.start()
                logger.info(f"{acc_phone}: 🔄 Client reconnected successfully.")
            except Exception as e:
                logger.error(f"{acc_phone}: ❌ Failed to reconnect - {type(e).__name__}: {e}")
                try:
                    remove_client_from_pool(acc_phone)
                except Exception:
                    pass
                return False

        if acc_phone not in client_manager.client_locks:
            client_manager.client_locks[acc_phone] = asyncio.Lock()

        async with client_manager.client_locks[acc_phone]:
            attempt = 0
            while attempt <= MAX_RETRIES:
                try:
                    await _attempt_send(cli, acc_phone, spam_config["spamTarget"], text)
                    return True

                except errors.FloodWait as e:
                    wait = e.value if hasattr(e, "value") else getattr(e, "x", 0)
                    wait = max(1, min(wait, FLOOD_COOLDOWN_CAP))
                    logger.warning(f"{acc_phone}: ⏰ FloodWait {wait}s (code:{getattr(e, 'value', 'n/a')})")
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
                    attempt += 1
                    if attempt > MAX_RETRIES:
                        logger.warning(f"{acc_phone}: ❌ Send failed after {MAX_RETRIES} retries - {type(e).__name__}: {e}")
                        return False
                    backoff = BASE_BACKOFF * (2 ** (attempt - 1))
                    backoff = min(backoff, 60)
                    jitter = random.uniform(0.1, 0.5)
                    wait_time = backoff + jitter
                    logger.info(f"{acc_phone}: 🔁 Retry {attempt}/{MAX_RETRIES} after {wait_time:.1f}s due to {type(e).__name__}")
                    await asyncio.sleep(wait_time)
    except Exception as e:
        logger.error(f"{acc_phone}: 💥 Fatal send error {type(e).__name__} - {e}")
        try:
            remove_client_from_pool(acc_phone)
        except Exception:
            pass
        return False

# ============================================================
# 🚀 اجرای اسپمر اصلی
# ============================================================
async def run_spammer(spam_config: dict, get_spam_texts, make_mention_html, remove_client_from_pool):
    base_delay = float(spam_config.get("TimeSleep", 1.0))
    batch_size = max(1, int(spam_config.get("BATCH_SIZE", 1)))
    ticker = PreciseTicker(interval=base_delay)
    total_sent = 0

    logger.info(f"🚀 Spammer started | Delay: {base_delay}s | Batch size: {batch_size}")

    try:
        while spam_config.get("run", False):
            active_accounts: Set[str] = set(client_manager.get_active_accounts())
            if not active_accounts:
                logger.warning("❌ هیچ اکانتی فعال نیست. اسپمر متوقف موقتاً.")
                await asyncio.sleep(1)
                continue

            acc_list = sorted([a for a in active_accounts])
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

            batches = [acc_list[i:i + batch_size] for i in range(0, len(acc_list), batch_size)]

            for batch in batches:
                if not spam_config.get("run", False):
                    break

                tasks = [
                    asyncio.create_task(safe_send(acc, spam_config, text, remove_client_from_pool))
                    for acc in batch
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for acc, res in zip(batch, results):
                    success = res is True
                    try:
                        await analytics.update_stats(acc, success, spam_config["spamTarget"])
                    except Exception:
                        logger.debug("analytics.update_stats failed", exc_info=True)

                    if success:
                        logger.info(f"{acc}: ✅ Message sent successfully.")
                    else:
                        logger.warning(f"{acc}: ❌ Failed sending message (or in cooldown).")

                total_sent += sum(1 for r in results if r is True)
                await ticker.sleep()

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
        try:
            await client_manager.stop_all_clients()
        except Exception:
            logger.debug("stop_all_clients failed", exc_info=True)
