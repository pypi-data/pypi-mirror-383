import os
import json
import asyncio
import logging
import random
import traceback
from typing import Optional, Dict, List, Set, Tuple
from pyrogram import Client, errors

# ============================================================
# ⚙️ تنظیم لاگ دقیق برای دیباگ Pyrogram و SQLite
# ============================================================
os.makedirs("logs", exist_ok=True)
log_file = "logs/client_debug_log.txt"
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not any(isinstance(h, logging.FileHandler) and h.baseFilename.endswith(log_file) for h in logger.handlers):
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

logger.info("🧩 Client Manager started in DEBUG MODE.")

# ============================================================
# 🧱 ساختار داده‌ها
# ============================================================
client_pool: Dict[str, Client] = {}
client_locks: Dict[str, asyncio.Lock] = {}

ACCOUNTS_FOLDER = "acc"
ACCOUNTS_DATA_FOLDER = "acc_data"
os.makedirs(ACCOUNTS_FOLDER, exist_ok=True)
os.makedirs(ACCOUNTS_DATA_FOLDER, exist_ok=True)


# ============================================================
# 🧠 ساخت یا دریافت کلاینت
# ============================================================
async def get_or_start_client(phone_number: str) -> Optional[Client]:
    cli = client_pool.get(phone_number)
    try:
        if cli is not None and getattr(cli, "is_connected", False):
            logger.debug(f"{phone_number}: Already connected → {cli.session_name}")
            return cli

        cli = _make_client_from_json(phone_number)
        if cli is None:
            logger.error(f"{phone_number}: ❌ Could not build client (no JSON or invalid data)")
            return None

        session_db_path = f"{cli.session_name}.session"
        logger.debug(f"{phone_number}: Session DB path → {session_db_path}")

        if not os.path.exists(session_db_path):
            logger.warning(f"{phone_number}: Session file not found → {session_db_path}")
        else:
            size = os.path.getsize(session_db_path)
            logger.debug(f"{phone_number}: Session file exists ({size} bytes)")
            if not os.access(session_db_path, os.R_OK | os.W_OK):
                logger.warning(f"{phone_number}: ⚠️ No read/write permission for {session_db_path}")

        try:
            await cli.start()
            await asyncio.sleep(0.4)
            logger.info(f"{phone_number}: ✅ Client started successfully.")
        except errors.SessionPasswordNeeded:
            twofa = getattr(cli, "_twofa_password", None)
            if twofa:
                await cli.check_password(twofa)
                logger.info(f"{phone_number}: ✅ 2FA password applied.")
            else:
                logger.error(f"{phone_number}: ⚠️ 2FA required but missing.")
                return None
        except errors.AuthKeyDuplicated:
            logger.error(f"{phone_number}: ❌ AuthKeyDuplicated (session invalid).")
            return None
        except Exception as e:
            tb = traceback.format_exc(limit=3)
            logger.error(f"{phone_number}: ❌ Start failed - {type(e).__name__}: {e}\n{tb}")
            return None

        client_pool[phone_number] = cli
        client_locks.setdefault(phone_number, asyncio.Lock())
        return cli

    except Exception as e:
        tb = traceback.format_exc(limit=3)
        logger.critical(f"{phone_number}: 💥 Fatal error in get_or_start_client - {type(e).__name__}: {e}\n{tb}")
        return None


# ============================================================
# 🧩 ساخت کلاینت از JSON
# ============================================================
def _make_client_from_json(phone_number: str) -> Optional[Client]:
    try:
        data_path = os.path.join(ACCOUNTS_DATA_FOLDER, f"{phone_number}.json")
        if not os.path.exists(data_path):
            logger.error(f"{phone_number}: ⚠️ Account JSON not found → {data_path}")
            return None

        with open(data_path, "r", encoding="utf-8") as f:
            account_data = json.load(f)

        session_base = account_data.get("session")
        if not session_base:
            logger.error(f"{phone_number}: Missing 'session' key in JSON → {data_path}")
            return None

        session_path = os.path.join(ACCOUNTS_FOLDER, session_base)
        if not session_path.endswith(".session"):
            session_path += ".session"

        os.makedirs(os.path.dirname(session_path), exist_ok=True)

        logger.debug(f"{phone_number}: Final session path → {session_path}")

        api_id = account_data.get("api_id")
        api_hash = account_data.get("api_hash")
        if not api_id or not api_hash:
            logger.error(f"{phone_number}: Missing API credentials in JSON → {data_path}")
            return None

        cli = Client(
            name=session_path,
            api_id=int(api_id),
            api_hash=str(api_hash),
            sleep_threshold=30,
            workdir=os.path.join("acc_temp", phone_number),
            no_updates=True,
        )

        if account_data.get("2fa_password"):
            setattr(cli, "_twofa_password", account_data["2fa_password"])

        return cli

    except Exception as e:
        tb = traceback.format_exc(limit=3)
        logger.critical(f"{phone_number}: 💥 Error creating client - {type(e).__name__}: {e}\n{tb}")
        return None


# ============================================================
# 🚀 Preload با لاگ کامل
# ============================================================
async def preload_clients(limit: Optional[int] = None) -> None:
    phones = list(get_active_accounts())
    if limit is not None:
        phones = phones[:max(0, int(limit))]

    if not phones:
        logger.info("⚙️ No accounts found for preload.")
        return

    logger.info(f"🚀 Preloading {len(phones)} clients...")
    ok, bad = 0, 0

    for idx, phone in enumerate(phones, 1):
        logger.info(f"🔹 [{idx}/{len(phones)}] Loading client {phone}")
        try:
            cli = await get_or_start_client(phone)
            if cli and getattr(cli, "is_connected", False):
                ok += 1
                logger.info(f"{phone}: ✅ Connected.")
            else:
                bad += 1
                logger.warning(f"{phone}: ❌ Not connected after start().")
        except Exception as e:
            bad += 1
            tb = traceback.format_exc(limit=3)
            logger.error(f"{phone}: ❌ Exception during preload - {type(e).__name__}: {e}\n{tb}")

        await asyncio.sleep(1.0)

    logger.info(f"🎯 Preload completed: OK={ok} | FAIL={bad}")


# ============================================================
# 🧹 توقف تمام کلاینت‌ها
# ============================================================
async def stop_all_clients() -> None:
    logger.info("🧹 Stopping all clients...")
    for phone, cli in list(client_pool.items()):
        try:
            await cli.stop()
            logger.info(f"{phone}: 📴 Stopped successfully.")
        except Exception as e:
            tb = traceback.format_exc(limit=2)
            logger.warning(f"{phone}: ⚠️ Error stopping client - {type(e).__name__}: {e}\n{tb}")
        finally:
            client_pool.pop(phone, None)
            await asyncio.sleep(0.3)
    logger.info("✅ All clients stopped cleanly.")


# ============================================================
# 📦 مدیریت JSON داده‌های اکانت
# ============================================================
def get_account_data(phone_number: str) -> Optional[Dict]:
    """
    خواندن داده‌های JSON اکانت از acc_data/{phone}.json
    """
    file_path = os.path.join(ACCOUNTS_DATA_FOLDER, f"{phone_number}.json")
    if not os.path.exists(file_path):
        logger.warning(f"{phone_number}: ⚠️ Account JSON not found at {file_path}")
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"{phone_number}: ⚠️ Error reading JSON - {type(e).__name__}: {e}")
        return None


def save_account_data(phone_number: str, data: Dict) -> None:
    """
    ذخیره اطلاعات JSON اکانت در acc_data/{phone}.json
    """
    os.makedirs(ACCOUNTS_DATA_FOLDER, exist_ok=True)
    file_path = os.path.join(ACCOUNTS_DATA_FOLDER, f"{phone_number}.json")
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"{phone_number}: 💾 Account data saved successfully → {file_path}")
    except Exception as e:
        logger.error(f"{phone_number}: ⚠️ Error saving JSON - {type(e).__name__}: {e}")


# ============================================================
# 📋 لیست اکانت‌های فعال
# ============================================================
def accounts() -> List[str]:
    accs: Set[str] = set()
    if not os.path.isdir(ACCOUNTS_FOLDER):
        return []
    for acc in os.listdir(ACCOUNTS_FOLDER):
        if acc.endswith(".session"):
            accs.add(acc.split(".")[0])
    return list(accs)


def get_active_accounts() -> Set[str]:
    return set(accounts())

# ============================================================
# 🗑️ حذف اکانت
# ============================================================
async def delete_account_cmd(message) -> None:
    """
    حذف اکانت مشخص شده
    دستور: /del <phone_number>
    """
    try:
        # استخراج شماره تلفن از پیام
        command_parts = message.text.split()
        if len(command_parts) < 2:
            await message.reply_text("⚠️ لطفاً شماره تلفن اکانت را وارد کنید:\n`/del 989123456789`")
            return

        phone_number = command_parts[1].strip()
        
        # بررسی وجود اکانت
        if phone_number not in get_active_accounts():
            await message.reply_text(f"❌ اکانت `{phone_number}` یافت نشد.")
            return

        # توقف کلاینت اگر در حال اجراست
        if phone_number in client_pool:
            try:
                cli = client_pool[phone_number]
                if getattr(cli, "is_connected", False):
                    await cli.stop()
                client_pool.pop(phone_number, None)
                client_locks.pop(phone_number, None)
                logger.info(f"{phone_number}: 📴 Client stopped for deletion.")
            except Exception as e:
                logger.warning(f"{phone_number}: ⚠️ Error stopping client before deletion - {e}")

        # حذف فایل‌های session
        session_deleted = False
        data_deleted = False
        
        session_files = [
            os.path.join(ACCOUNTS_FOLDER, f"{phone_number}.session"),
            os.path.join(ACCOUNTS_FOLDER, phone_number),  # برای حالت‌های مختلف نام session
            f"{phone_number}.session",  # در صورت وجود در مسیر جاری
        ]
        
        for session_file in session_files:
            if os.path.exists(session_file):
                try:
                    os.remove(session_file)
                    session_deleted = True
                    logger.info(f"{phone_number}: 🗑️ Session file deleted → {session_file}")
                except Exception as e:
                    logger.error(f"{phone_number}: ⚠️ Error deleting session file {session_file} - {e}")

        # حذف فایل داده‌های اکانت
        data_file = os.path.join(ACCOUNTS_DATA_FOLDER, f"{phone_number}.json")
        if os.path.exists(data_file):
            try:
                os.remove(data_file)
                data_deleted = True
                logger.info(f"{phone_number}: 🗑️ Account data deleted → {data_file}")
            except Exception as e:
                logger.error(f"{phone_number}: ⚠️ Error deleting account data {data_file} - {e}")

        # ارسال نتیجه به کاربر
        if session_deleted or data_deleted:
            await message.reply_text(f"✅ اکانت `{phone_number}` با موفقیت حذف شد.\n"
                                   f"• فایل session: {'✅' if session_deleted else '❌'}\n"
                                   f"• فایل داده: {'✅' if data_deleted else '❌'}")
            logger.info(f"{phone_number}: ✅ Account deletion completed.")
        else:
            await message.reply_text(f"⚠️ هیچ فایلی برای اکانت `{phone_number}` یافت نشد.")
            
    except Exception as e:
        error_msg = f"💥 خطا در حذف اکانت: {str(e)}"
        logger.error(f"delete_account_cmd error: {traceback.format_exc()}")
        await message.reply_text(error_msg)


# ============================================================
# 🗑️ حذف تمامی اکانت‌ها
# ============================================================
async def delete_all_accounts_cmd(message) -> None:
    """
    حذف تمامی اکانت‌ها
    دستور: /delall
    """
    try:
        # گرفتن تایید از کاربر
        confirm_text = "⚠️ **آیا مطمئن هستید که می‌خواهید تمامی اکانت‌ها را حذف کنید؟**\n\n"
        confirm_text += "این عمل غیرقابل بازگشت است!\n"
        confirm_text += "برای تایید، دستور زیر را ارسال کنید:\n`/delall confirm`"
        
        command_parts = message.text.split()
        if len(command_parts) < 2 or command_parts[1].strip().lower() != "confirm":
            await message.reply_text(confirm_text)
            return

        # توقف تمام کلاینت‌ها
        await stop_all_clients()

        # لیست تمام اکانت‌ها
        all_accounts = get_active_accounts()
        deleted_sessions = 0
        deleted_data_files = 0
        
        # حذف تمام فایل‌های session
        if os.path.exists(ACCOUNTS_FOLDER):
            for filename in os.listdir(ACCOUNTS_FOLDER):
                if filename.endswith('.session'):
                    try:
                        file_path = os.path.join(ACCOUNTS_FOLDER, filename)
                        os.remove(file_path)
                        deleted_sessions += 1
                        logger.info(f"🗑️ Session file deleted → {filename}")
                    except Exception as e:
                        logger.error(f"⚠️ Error deleting session file {filename} - {e}")

        # حذف تمام فایل‌های داده
        if os.path.exists(ACCOUNTS_DATA_FOLDER):
            for filename in os.listdir(ACCOUNTS_DATA_FOLDER):
                if filename.endswith('.json'):
                    try:
                        file_path = os.path.join(ACCOUNTS_DATA_FOLDER, filename)
                        os.remove(file_path)
                        deleted_data_files += 1
                        logger.info(f"🗑️ Account data deleted → {filename}")
                    except Exception as e:
                        logger.error(f"⚠️ Error deleting account data {filename} - {e}")

        # پاک کردن کش داخلی
        client_pool.clear()
        client_locks.clear()

        # ارسال نتیجه به کاربر
        result_msg = (f"✅ **حذف کامل اکانت‌ها انجام شد**\n\n"
                     f"• تعداد فایل‌های session حذف شده: `{deleted_sessions}`\n"
                     f"• تعداد فایل‌های داده حذف شده: `{deleted_data_files}`\n"
                     f"• تعداد اکانت‌های شناسایی شده: `{len(all_accounts)}`")
        
        await message.reply_text(result_msg)
        logger.info(f"🎯 All accounts deletion completed: {deleted_sessions} sessions, {deleted_data_files} data files")

    except Exception as e:
        error_msg = f"💥 خطا در حذف کامل اکانت‌ها: {str(e)}"
        logger.error(f"delete_all_accounts_cmd error: {traceback.format_exc()}")
        await message.reply_text(error_msg)