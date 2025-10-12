import os
import json
import asyncio
import logging
import random
from typing import Optional, Dict, List, Set, Tuple
from pyrogram import Client, errors

logger = logging.getLogger(__name__)

# ============================================================
# ⚙️ استخر کلاینت‌ها و قفل‌ها
# ============================================================
client_pool: Dict[str, Client] = {}
client_locks: Dict[str, asyncio.Lock] = {}

# ============================================================
# 📁 مسیرها
# ============================================================
ACCOUNTS_FOLDER = "acc"
ACCOUNTS_DATA_FOLDER = "acc_data"
os.makedirs(ACCOUNTS_FOLDER, exist_ok=True)
os.makedirs(ACCOUNTS_DATA_FOLDER, exist_ok=True)

# ============================================================
# 🧠 ساخت یا دریافت کلاینت
# ============================================================
async def get_or_start_client(phone_number: str) -> Optional[Client]:
    """
    دریافت یا ساخت کلاینت از روی فایل سشن و اطلاعات JSON.
    اگر فعال باشد، همان instance را بازمی‌گرداند.
    """
    cli = client_pool.get(phone_number)
    try:
        # اگر کلاینت فعال و متصل است
        if cli is not None and getattr(cli, "is_connected", False):
            return cli

        cli = _make_client_from_json(phone_number)
        if cli is None:
            logger.error(f"{phone_number}: ❌ Unable to make client (missing or invalid session)")
            return None

        twofa = getattr(cli, "_twofa_password", None)

        # تلاش برای start
        try:
            await cli.start()
            await asyncio.sleep(0.5)  # فاصله برای جلوگیری از لاک sqlite
        except errors.SessionPasswordNeeded:
            if twofa:
                await cli.check_password(twofa)
            else:
                logger.error(f"{phone_number}: ⚠️ 2FA required but no password set.")
                return None
        except errors.AuthKeyDuplicated:
            logger.error(f"{phone_number}: ❌ AuthKeyDuplicated - session invalid.")
            return None
        except Exception as e:
            logger.error(f"{phone_number}: ❌ Error during start - {type(e).__name__}: {e}")
            return None

        client_pool[phone_number] = cli
        client_locks.setdefault(phone_number, asyncio.Lock())
        logger.info(f"{phone_number}: ✅ Client started successfully.")
        return cli

    except Exception as e:
        logger.error(f"{phone_number}: 💥 Fatal error in get_or_start_client - {type(e).__name__}: {e}")
        return None


# ============================================================
# 🛑 توقف و پاکسازی کلاینت‌ها
# ============================================================
async def stop_all_clients() -> None:
    """
    توقف تمام کلاینت‌های فعال و آزادسازی منابع.
    """
    errs = 0
    for phone, cli in list(client_pool.items()):
        try:
            await cli.stop()
            logger.info(f"{phone}: 📴 Client stopped successfully.")
        except Exception as e:
            errs += 1
            logger.warning(f"{phone}: ⚠️ Error stopping client - {type(e).__name__}: {e}")
        finally:
            client_pool.pop(phone, None)
            client_locks.pop(phone, None)
            await asyncio.sleep(0.2)

    if errs:
        logger.warning(f"⚠️ stop_all_clients finished with {errs} error(s).")
    else:
        logger.info("✅ All clients stopped cleanly.")


# ============================================================
# 📦 مدیریت داده‌های اکانت (JSON)
# ============================================================
def get_account_data(phone_number: str) -> Optional[Dict]:
    file_path = os.path.join(ACCOUNTS_DATA_FOLDER, f"{phone_number}.json")
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"{phone_number}: ⚠️ Error reading JSON - {type(e).__name__}: {e}")
        return None


def save_account_data(phone_number: str, data: Dict) -> None:
    file_path = os.path.join(ACCOUNTS_DATA_FOLDER, f"{phone_number}.json")
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"{phone_number}: 💾 Account data saved.")
    except Exception as e:
        logger.error(f"{phone_number}: ⚠️ Error saving JSON - {type(e).__name__}: {e}")


# ============================================================
# 📋 لیست اکانت‌ها
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
# 🔑 انتخاب api_id / api_hash تصادفی
# ============================================================
def get_app_info() -> List[str]:
    try:
        apis: Dict[int, Tuple[str, int]] = {
            1: ("debac98afc137d3a82df5454f345bf02", 23523087),
            2: ("b86bbf4b700b4e922fff2c05b3b8985f", 17221354),
            3: ("2345124333c84e4f72441606a08e882c", 21831682),
            4: ("1ebc2808ef58a95bc796590151c3e0d5", 14742007),
            5: ("b8eff20a7e8adcdaa3daa3bc789a5b41", 12176206),
        }
        api_hash, api_id = apis[random.randint(1, 5)]
        return [api_hash, api_id]
    except Exception as e:
        logger.error(f"⚙️ Error selecting app info - {type(e).__name__}: {e}")
        return []


# ============================================================
# 🧩 ساخت کلاینت از JSON
# ============================================================
def _make_client_from_json(phone_number: str) -> Optional[Client]:
    try:
        account_data = get_account_data(phone_number)
        if not account_data:
            logger.warning(f"{phone_number}: ⚠️ No account data found.")
            return None

        # مسیر فایل سشن
        session_base = account_data.get("session")
        if not session_base:
            logger.warning(f"{phone_number}: ⚠️ No 'session' in JSON.")
            return None

        session_path = (
            session_base
            if os.path.isabs(session_base) or os.path.dirname(session_base)
            else os.path.join(ACCOUNTS_FOLDER, session_base)
        )

        session_file = session_path if session_path.endswith(".session") else f"{session_path}.session"
        if not os.path.exists(session_file):
            logger.warning(f"{phone_number}: ⚠️ Session file not found: {session_file}")
            return None

        # api_id / api_hash
        api_id = account_data.get("api_id")
        api_hash = account_data.get("api_hash")
        if not api_id or not api_hash:
            alt = get_app_info()
            if len(alt) == 2:
                api_hash, api_id = alt[0], alt[1]
                logger.warning(f"{phone_number}: ℹ️ Used fallback API credentials.")
            else:
                return None

        cli = Client(
            name=session_path,  # مسیر دقیق سشن (جدا برای هر اکانت)
            api_id=int(api_id),
            api_hash=str(api_hash),
            workdir=os.path.join(ACCOUNTS_FOLDER, f"{phone_number}_data"),  # مسیر جدا برای فایل‌های داخلی
            sleep_threshold=30,
            no_updates=True,  # جلوگیری از اتصال به آپدیت‌های غیرضروری
        )

        # اگر پسورد 2FA وجود دارد، ضمیمه کن
        if account_data.get("2fa_password"):
            setattr(cli, "_twofa_password", account_data["2fa_password"])

        return cli

    except Exception as e:
        logger.error(f"{phone_number}: ❌ Error creating client - {type(e).__name__}: {e}")
        return None


# ============================================================
# 🚀 Preload (با تاخیر ایمن)
# ============================================================
async def preload_clients(limit: Optional[int] = None) -> None:
    phones = list(get_active_accounts())
    if limit is not None:
        phones = phones[:max(0, int(limit))]

    if not phones:
        logger.info("⚙️ No accounts to preload.")
        return

    logger.info(f"Preloading up to {len(phones)} client(s)...")
    ok, bad = 0, 0
    for idx, phone in enumerate(phones, start=1):
        try:
            cli = await get_or_start_client(phone)
            if cli and getattr(cli, "is_connected", False):
                ok += 1
            else:
                bad += 1
        except Exception as e:
            bad += 1
            logger.warning(f"{phone}: ⚠️ Preload failed - {type(e).__name__}: {e}")

        # فاصله کوچک بین هر start برای جلوگیری از قفل sqlite
        await asyncio.sleep(0.8 + random.uniform(0.1, 0.3))
        logger.debug(f"Finished preload {idx}/{len(phones)}")

    logger.info(f"✅ Preload finished → OK={ok} | FAIL={bad}")


def preload_clients_sync(limit: Optional[int] = None) -> None:
    asyncio.run(preload_clients(limit=limit))
