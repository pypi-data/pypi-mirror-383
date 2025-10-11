# antispam_core/batch_manager.py
import logging
from pyrogram import filters
from . import admin_manager
from .config import BATCH_SIZE

logger = logging.getLogger(__name__)

async def _set_batch_size_cmd(client, message):
    """تابع اصلی برای تغییر Batch Size"""
    global BATCH_SIZE
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("مثال: `set 3`")
            return

        val = int(parts[1])
        if val <= 0:
            await message.reply("عدد باید بزرگ‌تر از صفر باشد.")
            return

        BATCH_SIZE = val
        await message.reply(f"✅ Batch size set to: {val}")
    except ValueError:
        await message.reply("فرمت نادرست. مثال: `set 3`")
    except Exception as e:
        logger.error(f"Error setting batch size: {e}")
        await message.reply(f"⚠️ خطا در تنظیم batch size: {e}")

def get_batch_size() -> int:
    """برگرداندن مقدار فعلی Batch Size"""
    return BATCH_SIZE

