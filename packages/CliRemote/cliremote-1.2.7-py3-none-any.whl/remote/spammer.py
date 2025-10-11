# antispam_core/spammer.py
import asyncio
import random
import logging
from pyrogram import errors
from .precise_engine import PreciseTicker
from .client_manager import (
    get_or_start_client,
    get_active_accounts,
    client_locks,
    stop_all_clients
)
from .analytics_manager import analytics

# 🧾 تنظیمات ذخیره لاگ‌ها در فایل spam_log.txt
logging.basicConfig(
    filename="spam_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)
logger = logging.getLogger(__name__)


# ============================================================
# 🚀 اجرای اسپمر اصلی
# ============================================================
async def run_spammer(spam_config, get_spam_texts, make_mention_html, remove_client_from_pool):
    """
    🎯 اسپمر هماهنگ، پایدار و بدون Drift.
    از سیستم مدیریت کلاینت و تحلیل آماری پشتیبانی می‌کند.
    تمام لاگ‌ها در فایل spam_log.txt ذخیره می‌شوند.
    """

    # ✅ آماده‌سازی اکانت‌ها
    active_accounts = set(get_active_accounts())
    if not active_accounts:
        logger.warning("❌ هیچ اکانتی فعال نیست. اسپمر متوقف شد.")
        return

    batch_size = max(1, int(spam_config.get("BATCH_SIZE", 1)))
    base_delay = float(spam_config.get("TimeSleep", 1.0))
    ticker = PreciseTicker(interval=base_delay)
    total_sent = 0

    logger.info(
        f"🚀 Spammer started | Accounts: {len(active_accounts)} | Delay: {base_delay}s | Batch: {batch_size}"
    )

    # 🔁 اجرای اصلی حلقه اسپم
    while spam_config.get("run", False):
        texts = get_spam_texts()
        if not texts:
            await asyncio.sleep(1)
            continue

        text = random.choice(texts)
        caption = spam_config.get("caption", "")
        if caption:
            text += f"\n{caption}"

        if spam_config.get("is_menshen"):
            mention_html = make_mention_html(spam_config["useridMen"], spam_config["textMen"])
            text += f"\n{mention_html}"

        acc_list = sorted(active_accounts)
        batches = [acc_list[i:i + batch_size] for i in range(0, len(acc_list), batch_size)]

        for batch in batches:
            if not spam_config.get("run", False):
                break

            send_tasks = [
                safe_send(acc, spam_config, text, remove_client_from_pool)
                for acc in batch
            ]
            results = await asyncio.gather(*send_tasks, return_exceptions=True)

            for acc, ok in zip(batch, results):
                success = ok is True
                await analytics.update_stats(acc, success, spam_config["spamTarget"])

                if success:
                    logger.info(f"{acc}: ✅ Message sent successfully.")
                else:
                    logger.warning(f"{acc}: ❌ Failed sending message.")

            total_sent += len(batch)
            await ticker.sleep()

        if total_sent and total_sent % 500 == 0:
            logger.info(f"📊 Progress update: {total_sent} messages sent so far...")

    # 🛑 توقف کامل اسپمر
    logger.info("🛑 Spammer stopped gracefully.")
    logger.info(f"📈 Total messages attempted: {total_sent}")
    logger.info("------------------------------------------------------\n")

    await stop_all_clients()


# ============================================================
# 📤 ارسال امن پیام
# ============================================================
async def safe_send(acc_phone: str, spam_config: dict, text: str, remove_client_from_pool):
    """
    ارسال امن برای هر اکانت با کنترل FloodWait و Reconnect.
    در صورت خطا، لاگ‌ها در spam_log.txt ثبت می‌شوند.
    """
    try:
        cli = await get_or_start_client(acc_phone)
        if not cli:
            logger.warning(f"{acc_phone}: ⚠️ Client not available.")
            return False

        # اگر کلاینت قطع است، تلاش برای اتصال مجدد
        if not getattr(cli, "is_connected", False):
            try:
                await cli.start()
                logger.info(f"{acc_phone}: 🔄 Client reconnected successfully.")
            except Exception as e:
                logger.error(f"{acc_phone}: ❌ Failed to reconnect - {type(e).__name__}: {e}")
                remove_client_from_pool(acc_phone)
                return False

        # قفل برای کنترل هم‌زمانی
        if acc_phone not in client_locks:
            client_locks[acc_phone] = asyncio.Lock()

        async with client_locks[acc_phone]:
            try:
                await cli.send_message(spam_config["spamTarget"], text)
                logger.info(f"{acc_phone}: ✅ Sent message to {spam_config['spamTarget']}")
                return True

            except errors.FloodWait as e:
                wait = min(e.value, 60)
                logger.warning(f"{acc_phone}: ⏰ FloodWait {wait}s")
                await asyncio.sleep(wait)
                return False

            except (errors.UserDeactivated, errors.AuthKeyUnregistered):
                logger.warning(f"{acc_phone}: ⚠️ Account deactivated or unregistered.")
                remove_client_from_pool(acc_phone)
                return False

            except errors.ChatWriteForbidden:
                logger.warning(f"{acc_phone}: 🚫 Cannot send message to {spam_config['spamTarget']}")
                return False

            except Exception as e:
                logger.warning(f"{acc_phone}: ❌ Send error {type(e).__name__} - {e}")
                return False

    except Exception as e:
        logger.error(f"{acc_phone}: 💥 Fatal send error {type(e).__name__} - {e}")
        return False
