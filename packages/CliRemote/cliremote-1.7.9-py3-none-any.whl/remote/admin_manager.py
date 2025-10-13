# remote/admin_manager.py
import json, os, logging
from pyrogram import filters
from .config import OWNER_ID

logger = logging.getLogger(__name__)

# فایل کنار همین ماژول ذخیره شود، نه نسبت به cwd
BASE_DIR = os.path.dirname(__file__)
ADMINS_FILE = os.path.join(BASE_DIR, "admins.json")

def load_admins() -> list[int]:
    """
    بارگذاری لیست ادمین‌ها از فایل + اضافه‌کردن OWNER_ID
    """
    s = set(OWNER_ID)  # همیشه Ownerها باشند
    try:
        if os.path.exists(ADMINS_FILE):
            with open(ADMINS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for v in data:
                        try:
                            s.add(int(v))
                        except Exception:
                            logger.warning(f"Bad admin id in file: {v!r}")
    except Exception as e:
        logger.warning(f"Error loading admins: {e}")
    return list(s)

def save_admins():
    """ذخیره‌ی ادمین‌ها در فایل (بدون Ownerها، فقط ADMINS پویا)."""
    try:
        with open(ADMINS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(ADMINS), f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving admins: {e}")

ADMINS = load_admins()

# فیلترها (داینامیک: هر بار اجرا، مقدار فعلی لیست‌ها چک می‌شود)
admin_filter = filters.create(
    lambda _, __, m: bool(getattr(m, "from_user", None)) and int(m.from_user.id) in ADMINS
)
owner_filter = filters.create(
    lambda _, __, m: bool(getattr(m, "from_user", None)) and int(m.from_user.id) in OWNER_ID
)

# =============================
# فرمان‌های مدیریتی
# =============================
async def add_admin_cmd(message):
    try:
        parts = (message.text or "").split()
        if len(parts) < 2:
            await message.reply("مثال: /addadmin 123456789")
            return
        uid = int(parts[1])
        if uid in OWNER_ID:
            await message.reply("ادمین اصلی از قبل وجود دارد")
            return
        if uid not in ADMINS:
            ADMINS.append(uid)
            save_admins()
            await message.reply(f"ادمین جدید اضافه شد: <code>{uid}</code>")
            logger.info(f"Admin added: {uid}")
        else:
            await message.reply("قبلاً ادمین بود")
    except Exception as e:
        logger.error(f"add_admin_cmd error: {e}", exc_info=True)
        await message.reply(f"خطا: {e}")

async def del_admin_cmd(message):
    try:
        parts = (message.text or "").split()
        if len(parts) < 2:
            await message.reply("مثال: /deladmin 123456789")
            return
        uid = int(parts[1])
        if uid in OWNER_ID:
            await message.reply("❌ امکان حذف ادمین اصلی وجود ندارد")
            return
        if uid in ADMINS:
            ADMINS.remove(uid)
            save_admins()
            await message.reply(f"ادمین حذف شد: <code>{uid}</code>")
            logger.info(f"Admin removed: {uid}")
        else:
            await message.reply("کاربر ادمین نیست")
    except Exception as e:
        logger.error(f"del_admin_cmd error: {e}", exc_info=True)
        await message.reply(f"خطا: {e}")

async def list_admins_cmd(message):
    try:
        if not ADMINS:
            await message.reply("لیست ادمین‌ها خالی است.")
            return
        text = "👑 <b>ADMINS:</b>\n" + "\n".join([f"<code>{x}</code>" for x in ADMINS])
        await message.reply(text, disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"list_admins_cmd error: {e}", exc_info=True)
        await message.reply(f"خطا: {e}")
