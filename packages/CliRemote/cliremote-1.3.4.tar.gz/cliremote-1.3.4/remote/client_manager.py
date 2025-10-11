# antispam_core/client_manager.py
import os
import json
import asyncio
import logging
import random
from typing import Optional, Dict, List, Set, Tuple
from pyrogram import Client , errors

logger = logging.getLogger(__name__)

# استخر کلاینت‌ها و قفل‌ها
client_pool: Dict[str, Client] = {}
client_locks: Dict[str, asyncio.Lock] = {}

# مسیرها/پوشه‌ها
ACCOUNTS_FOLDER = "acc"
ACCOUNTS_DATA_FOLDER = "acc_data"
os.makedirs(ACCOUNTS_DATA_FOLDER, exist_ok=True)


# ===============================
#   مدیریت سشن‌ها و کلاینت‌ها
# ===============================

async def get_or_start_client(phone_number: str) -> Optional[Client]:
    """
    دریافت یا راه‌اندازی کلاینت از فایل سشن.
    - اگر کلاینت موجود و متصل باشد همان را برمی‌گرداند.
    - در غیر اینصورت سعی به ساخت کلاینت از روی JSON و start کردن آن می‌کند.
    - در صورت نیاز به 2FA، با check_password تکمیل می‌شود.
    """
    cli = client_pool.get(phone_number)
    try:
        if cli is not None and getattr(cli, "is_connected", False):
            return cli

        cli = _make_client_from_json(phone_number)
        if cli is None:
            return None

        twofa = getattr(cli, "_twofa_password", None)

        try:
            # تلاش برای استارت معمولی
            await cli.start()
        except errors.SessionPasswordNeeded:
            # اگر پسورد 2FA نیاز بود، و داریم: چک کن
            if twofa:
                await cli.check_password(twofa)
            else:
                logger.error(f"2FA required for {phone_number} but no password provided.")
                return None

        client_pool[phone_number] = cli
        client_locks.setdefault(phone_number, asyncio.Lock())
        logger.info(f"Started client for {phone_number}")
        return cli

    except Exception as e:
        logger.error(f"Error starting client for {phone_number}: {type(e).__name__} - {e}")
        return None

async def stop_all_clients() -> None:
    """
    توقف و پاکسازی تمام کلاینت‌های فعال.
    """
    errs = 0
    for phone, cli in list(client_pool.items()):
        try:
            await cli.stop()
            logger.info(f"Stopped client for {phone}")
        except Exception as e:
            errs += 1
            logger.warning(f"Error stopping client for {phone}: {type(e).__name__} - {e}")
        finally:
            client_pool.pop(phone, None)
            client_locks.pop(phone, None)

    if errs:
        logger.info(f"Client pool shutdown had {errs} error(s)")


# ===============================
#   مدیریت داده‌های اکانت
# ===============================

def get_account_data(phone_number: str) -> Optional[Dict]:
    """
    خواندن داده‌های JSON اکانت از ACCOUNTS_DATA_FOLDER.
    انتظار می‌رود فایل {phone}.json موجود باشد.
    """
    file_path = os.path.join(ACCOUNTS_DATA_FOLDER, f"{phone_number}.json")
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading account data for {phone_number}: {type(e).__name__} - {e}")
        return None


def save_account_data(phone_number: str, data: Dict) -> None:
    """
    ذخیره اطلاعات JSON اکانت در ACCOUNTS_DATA_FOLDER.
    """
    file_path = os.path.join(ACCOUNTS_DATA_FOLDER, f"{phone_number}.json")
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"Account data saved for {phone_number}")
    except Exception as e:
        logger.error(f"Error saving account data for {phone_number}: {type(e).__name__} - {e}")


def accounts() -> List[str]:
    """
    لیست تمام اکانت‌های موجود در پوشه ACCOUNTS_FOLDER بر اساس فایل‌های .session
    """
    accs: Set[str] = set()
    if not os.path.isdir(ACCOUNTS_FOLDER):
        return []
    for acc in os.listdir(ACCOUNTS_FOLDER):
        if acc.endswith(".session"):
            accs.add(acc.split(".")[0])
    return list(accs)


def get_app_info() -> List[str]:
    """
    برگرداندن تصادفی یک جفت (api_hash, api_id) از میان چند مقدار.
    اگر خطایی رخ دهد، لیست خالی برمی‌گرداند.
    """
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
        logger.error(f"Error reading app info: {type(e).__name__} - {e}")
        return []


def get_active_accounts() -> Set[str]:
    """
    برگرداندن مجموعه‌ی اکانت‌های فعال (بر مبنای وجود فایل session).
    """
    return set(accounts())


def _make_client_from_json(phone_number: str) -> Optional[Client]:
    """
    ایجاد Client از اطلاعات JSON ذخیره‌شده.
    ساختار مورد انتظار فایل {phone}.json:
      {
        "session": "<session base name or path inside ACCOUNTS_FOLDER>",
        "api_id": 12345,
        "api_hash": "xxxxxxxxxxxxxxxxxxxx",
        "2fa_password": "optional"
      }
    """
    try:
        account_data = get_account_data(phone_number)
        if not account_data:
            logger.error(f"No account data found for {phone_number}")
            return None

        # نام/مسیر سشن
        session_base = account_data.get("session")
        if not session_base:
            logger.error(f"No 'session' field in account data for {phone_number}")
            return None

        # اگر کاربر فقط base name داده باشد، کنار ACCOUNTS_FOLDER قرار می‌گیرد
        session_path = (
            session_base
            if os.path.isabs(session_base) or os.path.dirname(session_base)
            else os.path.join(ACCOUNTS_FOLDER, session_base)
        )

        # اطمینان از وجود فایل .session
        session_file = session_path if session_path.endswith(".session") else f"{session_path}.session"
        if not os.path.exists(session_file):
            logger.error(f"Session file not found for {phone_number}: {session_file}")
            return None

        # api_id/api_hash
        api_id = account_data.get("api_id")
        api_hash = account_data.get("api_hash")
        if not api_id or not api_hash:
            # fallback اختیاری
            alt = get_app_info()
            if len(alt) == 2:
                api_hash, api_id = alt[0], alt[1]
                logger.warning(f"api_id/api_hash not in json for {phone_number}; using fallback.")
            else:
                logger.error(f"Missing api_id/api_hash for {phone_number}")
                return None

        cli = Client(
            name=session_path,           # مسیر/نام سشن
            api_id=int(api_id),
            api_hash=str(api_hash),
            sleep_threshold=30,
        )

        # 2FA (در صورت وجود) — برای استفاده هنگام start در get_or_start_client ذخیره می‌کنیم
        if account_data.get("2fa_password"):
            setattr(cli, "_twofa_password", account_data["2fa_password"])

        return cli
    except Exception as e:
        logger.error(f"Error creating client for {phone_number}: {type(e).__name__} - {e}")
        return None


# ===============================
#   Preload (اختیاری)
# ===============================

async def preload_clients(limit: Optional[int] = None) -> None:
    """
    به صورت اختیاری: تعدادی از اکانت‌ها را از پیش راه‌اندازی می‌کند.
    - limit: اگر None باشد همه را تلاش می‌کند؛ در غیر این صورت تا سقف limit.
    نکته: این تابع خودکار اجرا نمی‌شود؛ باید در main.py یا هوک استارتاپ صدا زده شود.
    """
    phones = list(get_active_accounts())
    if limit is not None:
        phones = phones[:max(0, int(limit))]

    if not phones:
        logger.info("No accounts to preload.")
        return

    logger.info(f"Preloading up to {len(phones)} client(s)...")
    ok, bad = 0, 0
    for phone in phones:
        try:
            cli = await get_or_start_client(phone)
            if cli and getattr(cli, "is_connected", False):
                ok += 1
            else:
                bad += 1
        except Exception as e:
            bad += 1
            logger.warning(f"Preload failed for {phone}: {type(e).__name__} - {e}")

    logger.info(f"Preload finished: OK={ok}  FAIL={bad}")


def preload_clients_sync(limit: Optional[int] = None) -> None:
    """
    نسخه‌ی sync برای اسکریپت‌هایی که حلقه‌ی event ندارند.
    توصیه می‌شود در برنامه‌های async از نسخه‌ی async استفاده شود.
    """
    asyncio.run(preload_clients(limit=limit))
