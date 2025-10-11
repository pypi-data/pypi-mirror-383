
# utils-like: client_picker.py
import random
import asyncio
import logging
from typing import Optional

try:
    from .client_manager import get_or_start_client, stop_all_clients
except Exception:
    from client_manager import get_or_start_client, stop_all_clients

try:
    from . import account_manager
except Exception:
    import account_manager

logger = logging.getLogger(__name__)

async def get_any_client(message=None, max_attempts: int = 3) -> Optional[object]:
    acc_list = account_manager.get_active_accounts()
    if not acc_list:
        if message:
            try:
                await message.reply("⚠️ هیچ اکانت فعالی برای اتصال وجود ندارد.")
            except Exception:
                pass
        logger.warning("⚠️ هیچ اکانت فعالی در دسترس نیست.")
        return None

    tried = set()
    for attempt in range(1, max_attempts + 1):
        if len(tried) == len(acc_list):
            break
        phone = random.choice([p for p in acc_list if p not in tried])
        tried.add(phone)
        logger.info(f"🔁 تلاش {attempt}/{max_attempts} برای اتصال با اکانت {phone}")
        try:
            cli = await get_or_start_client(phone)
            if cli and getattr(cli, "is_connected", True):
                logger.info(f"✅ اتصال موفق با اکانت {phone}")
                return cli
            else:
                logger.warning(f"⚠️ اکانت {phone} وصل نیست یا کلاینت معتبری برنگشته.")
        except Exception as e:
            logger.error(f"❌ خطا در اتصال {phone}: {type(e).__name__} - {e}")
            try:
                await asyncio.sleep(1)
            except Exception:
                pass

    error_msg = f"❌ هیچ کلاینت فعالی پس از {max_attempts} تلاش یافت نشد. در حال ریست کامل کلاینت‌ها..."
    if message:
        try:
            await message.reply(error_msg)
        except Exception:
            pass
    logger.error(error_msg)
    try:
        await stop_all_clients()
        logger.warning("🔄 تمام کلاینت‌ها ریست شدند (stop_all_clients فراخوانی شد).")
    except Exception as e:
        logger.error(f"⚠️ خطا در ریست کلاینت‌ها: {type(e).__name__} - {e}")
    return None
