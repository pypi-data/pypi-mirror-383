# antispam_core/spammer.py
import asyncio, random, logging
from pyrogram import errors
from .precise_engine import PreciseTicker
from .client_manager import get_or_start_client, get_active_accounts, client_locks, stop_all_clients
from .analytics_manager import analytics

logger = logging.getLogger(__name__)

async def run_spammer(spam_config, get_spam_texts, make_mention_html, remove_client_from_pool):
    """
    🎯 اسپمر هماهنگ، پایدار و بدون Drift.
    از سیستم مدیریت کلاینت و تحلیل آماری پشتیبانی می‌کند.
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

    logger.info(f"🚀 Spammer started | Accounts: {len(active_accounts)} | Delay: {base_delay}s | Batch: {batch_size}")

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
                if not success:
                    logger.debug(f"Account {acc} failed sending.")
            total_sent += len(batch)
            await ticker.sleep()

        if total_sent and total_sent % 500 == 0:
            logger.info(f"📊 {total_sent} messages sent so far...")

    # 🛑 توقف کامل
    logger.info("🛑 Spammer stopped gracefully.")
    await stop_all_clients()


# ============================================================
# 📤 ارسال امن پیام
# ============================================================
async def safe_send(acc_phone: str, spam_config: dict, text: str, remove_client_from_pool):
    """
    ارسال امن برای هر اکانت با کنترل FloodWait و Reconnect
    """
    try:
        cli = await get_or_start_client(acc_phone)
        if not cli:
            return False

        if not getattr(cli, "is_connected", False):
            try:
                await cli.start()
            except Exception:
                remove_client_from_pool(acc_phone)
                return False

        if acc_phone not in client_locks:
            client_locks[acc_phone] = asyncio.Lock()

        async with client_locks[acc_phone]:
            try:
                await cli.send_message(spam_config["spamTarget"], text)
                return True

            except errors.FloodWait as e:
                wait = min(e.value, 60)
                logger.warning(f"{acc_phone}: FloodWait({wait}s)")
                await asyncio.sleep(wait)
                return False

            except (errors.UserDeactivated, errors.AuthKeyUnregistered):
                remove_client_from_pool(acc_phone)
                return False

            except Exception as e:
                logger.warning(f"{acc_phone}: send error {e}")
                return False

    except Exception as e:
        logger.error(f"{acc_phone}: fatal send error {e}")
        return False
