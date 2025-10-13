# remote/admin_manager.py
import json, os, sys, logging
from pathlib import Path
from pyrogram import filters
from .config import OWNER_ID

logger = logging.getLogger(__name__)

def _project_root() -> Path:
    """
    ریشه پروژه = پوشه‌ای که main.py داخلش اجرا شده.
    """
    try:
        main_file = Path(sys.modules["__main__"].__file__).resolve()
        return main_file.parent
    except Exception:
        # fallback: اگر به هر دلیل __main__.__file__ نبود
        return Path(os.getcwd()).resolve()

PROJECT_ROOT = _project_root()
ADMINS_FILE = PROJECT_ROOT / "admins.json"   # ✅ کنار main.py

def _load_admins_from_file() -> list[int]:
    try:
        if ADMINS_FILE.exists():
            with ADMINS_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    out = []
                    for v in data:
                        try:
                            out.append(int(v))
                        except Exception:
                            logger.warning(f"Bad admin id in file: {v!r}")
                    return out
    except Exception as e:
        logger.warning(f"Error loading admins from {ADMINS_FILE}: {e}")
    return []

# لیست ادمین‌های موثر (فایل + Owner)
ADMINS: list[int] = []

def reload_admins():
    """فایل را می‌خواند و با OWNER_ID ادغام می‌کند؛ نتیجه در ADMINS."""
    file_admins = _load_admins_from_file()
    s = set(file_admins) | set(OWNER_ID)
    global ADMINS
    ADMINS = sorted(s)
    logger.info(f"Loaded admins ({ADMINS_FILE}): {ADMINS}")

def save_admins():
    """
    ذخیره در فایل کنار main.py.
    فقط ادمین‌های غیر-Owner را داخل فایل نگه می‌داریم (Ownerها از config می‌آیند).
    """
    try:
        file_list = [x for x in ADMINS if x not in set(OWNER_ID)]
        with ADMINS_FILE.open("w", encoding="utf-8") as f:
            json.dump(file_list, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved admins to {ADMINS_FILE}: {file_list}")
    except Exception as e:
        logger.error(f"Error saving admins: {e}")

# فیلترهای دسترسی
admin_filter = filters.create(
    lambda _, __, m: bool(getattr(m, "from_user", None)) and int(m.from_user.id) in ADMINS
)
owner_filter = filters.create(
    lambda _, __, m: bool(getattr(m, "from_user", None)) and int(m.from_user.id) in OWNER_ID
)

# ===== فرمان‌ها =====
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
            ADMINS[:] = sorted(set(ADMINS) | set(OWNER_ID))
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
