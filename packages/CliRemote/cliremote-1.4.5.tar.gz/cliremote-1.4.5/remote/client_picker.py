# remote/client_picker.py
import random
import asyncio
import logging
from typing import Optional, Callable, Iterable

logger = logging.getLogger(__name__)

# ---- وابستگی‌های اصلی
# تلاش می‌کنیم client_manager را حتماً داشته باشیم
from . import client_manager

# get_active() را به‌صورت ایمن تعیین می‌کنیم:
def _resolve_get_active() -> Callable[[], Iterable[str]]:
    """
    سعی می‌کند منبع معتبر لیست اکانت‌های فعال را پیدا کند:
      1) client_manager.get_active_accounts()
      2) account_manager.get_active_accounts()
      3) account_manager.accounts()  (fallback)
      4) client_manager.accounts()   (fallback)
    و در نهایت اگر هیچ‌کدام نبود، یک فانکشنِ خالی برمی‌گرداند.
    """
    # 1) client_manager.get_active_accounts
    if hasattr(client_manager, "get_active_accounts"):
        return client_manager.get_active_accounts

    # 2) account_manager...
    try:
        from . import account_manager  # ممکن است وجود نداشته باشد
        if hasattr(account_manager, "get_active_accounts"):
            return account_manager.get_active_accounts
        if hasattr(account_manager, "accounts"):
            return lambda: set(account_manager.accounts())
    except Exception:
        pass

    # 3) fallback به client_manager.accounts
    if hasattr(client_manager, "accounts"):
        return lambda: set(client_manager.accounts())

    # 4) آخرین fallback: لیست خالی
    return lambda: set()

_get_active_accounts = _resolve_get_active()


async def get_any_client(message=None, max_attempts: int = 3) -> Optional[object]:
    """
    تلاش برای گرفتن یک کلاینت فعال از بین اکانت‌ها.
    - تا `max_attempts` بار با اکانت‌های تصادفی امتحان می‌کند.
    - اگر موفق نشد، پیام خطا (در صورت وجود message) ارسال می‌کند،
      سپس stop_all_clients() فراخوانی می‌شود و در نهایت None برمی‌گرداند.
    """
    try:
        acc_iter = _get_active_accounts()
        acc_list = list(acc_iter) if not isinstance(acc_iter, (list, set, tuple)) else list(acc_iter)
    except Exception as e:
        logger.error(f"❌ نتوانستم لیست اکانت‌ها را بگیرم: {type(e).__name__} - {e}")
        acc_list = []

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
            cli = await client_manager.get_or_start_client(phone)
            if cli and getattr(cli, "is_connected", True):
                logger.info(f"✅ اتصال موفق با اکانت {phone}")
                return cli
            else:
                logger.warning(f"⚠️ اکانت {phone} وصل نیست یا کلاینت معتبر برنگشته.")
        except Exception as e:
            logger.error(f"❌ خطا در اتصال {phone}: {type(e).__name__} - {e}")
            try:
                await asyncio.sleep(1)
            except Exception:
                pass

    # شکست پس از تلاش‌ها
    error_msg = f"❌ هیچ کلاینت فعالی پس از {max_attempts} تلاش یافت نشد. در حال ریست کامل کلاینت‌ها..."
    if message:
        try:
            await message.reply(error_msg)
        except Exception:
            pass
    logger.error(error_msg)

    try:
        await client_manager.stop_all_clients()
        logger.warning("🔄 تمام کلاینت‌ها ریست شدند (stop_all_clients فراخوانی شد).")
    except Exception as e:
        logger.error(f"⚠️ خطا در ریست کلاینت‌ها: {type(e).__name__} - {e}")

    return None
