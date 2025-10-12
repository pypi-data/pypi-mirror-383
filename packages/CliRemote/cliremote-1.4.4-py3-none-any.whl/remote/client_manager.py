import os
import json
import asyncio
import logging
import random
import traceback
from typing import Optional, Dict, List, Set, Tuple
from pyrogram import Client, errors

# ============================================================
# ⚙️ تنظیم لاگ دقیق و مجزا برای دیباگ دیتابیس‌ها
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
# ⚙️ ساختارهای ذخیره‌سازی
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
    """
    ساخت یا گرفتن کلاینت از فایل سشن (با لاگ‌های بسیار دقیق برای تشخیص ارورهای SQLite)
    """
    cli = client_pool.get(phone_number)
    try:
        if cli is not None and getattr(cli, "is_connected", False):
            logger.debug(f"{phone_number}: Already connected → {cli.session_name}")
            return cli

        cli = _make_client_from_json(phone_number)
        if cli is None:
            logger.error(f"{phone_number}: ❌ Client creation failed (make_client_from_json returned None)")
            return None

        # لاگ مسیر سشن
        session_db_path = f"{cli.session_name}.session"
        logger.debug(f"{phone_number}: Session file path → {session_db_path}")

        # چک وجود فایل
        if not os.path.exists(session_db_path):
            logger.warning(f"{phone_number}: Session file missing → {session_db_path}")
        else:
            size = os.path.getsize(session_db_path)
            logger.debug(f"{phone_number}: Session file exists ({size} bytes)")

        # چک دسترسی
        if not os.access(session_db_path, os.R_OK | os.W_OK):
            logger.warning(f"{phone_number}: ⚠️ No read/write permission for {session_db_path}")

        try:
            await cli.start()
            await asyncio.sleep(0.4)
            logger.info(f"{phone_number}: ✅ Client started successfully")
        except errors.SessionPasswordNeeded:
            twofa = getattr(cli, "_twofa_password", None)
            if twofa:
                await cli.check_password(twofa)
                logger.info(f"{phone_number}: ✅ 2FA password applied successfully.")
            else:
                logger.error(f"{phone_number}: ⚠️ 2FA required but password missing.")
                return None
        except Exception as e:
            tb = traceback.format_exc(limit=3)
            logger.error(f"{phone_number}: ❌ Pyrogram start() failed → {type(e).__name__}: {e}\nTraceback:\n{tb}")
            return None

        client_pool[phone_number] = cli
        client_locks.setdefault(phone_number, asyncio.Lock())
        return cli

    except Exception as e:
        tb = traceback.format_exc(limit=3)
        logger.critical(f"{phone_number}: 💥 Fatal error in get_or_start_client() → {type(e).__name__}: {e}\nTraceback:\n{tb}")
        return None


# ============================================================
# 🧱 ساخت کلاینت از JSON
# ============================================================
def _make_client_from_json(phone_number: str) -> Optional[Client]:
    try:
        data_path = os.path.join(ACCOUNTS_DATA_FOLDER, f"{phone_number}.json")
        if not os.path.exists(data_path):
            logger.error(f"{phone_number}: ⚠️ JSON file not found → {data_path}")
            return None

        with open(data_path, "r", encoding="utf-8") as f:
            account_data = json.load(f)

        session_base = account_data.get("session")
        if not session_base:
            logger.error(f"{phone_number}: Missing 'session' in JSON → {data_path}")
            return None

        # مسیر دقیق سشن
        session_path = os.path.join(ACCOUNTS_FOLDER, session_base)
        if not session_path.endswith(".session"):
            session_path += ".session"

        # مسیر SQLite
        db_dir = os.path.dirname(os.path.abspath(session_path))
        if not os.path.exists(db_dir):
            logger.warning(f"{phone_number}: Creating missing folder for session → {db_dir}")
            os.makedirs(db_dir, exist_ok=True)

        logger.debug(f"{phone_number}: Final session path → {session_path}")

        # بررسی وجود فایل SQLite (قبل از start)
        if os.path.exists(session_path):
            logger.debug(f"{phone_number}: Session file already present ({os.path.getsize(session_path)} bytes)")
        else:
            logger.debug(f"{phone_number}: Session file will be created by Pyrogram")

        api_id = account_data.get("api_id")
        api_hash = account_data.get("api_hash")
        if not api_id or not api_hash:
            logger.error(f"{phone_number}: Missing api_id/api_hash in JSON → {data_path}")
            return None

        cli = Client(
            name=session_path,
            api_id=int(api_id),
            api_hash=str(api_hash),
            sleep_threshold=30,
            workdir=os.path.join("acc_temp", phone_number),
            no_updates=True
        )

        if account_data.get("2fa_password"):
            setattr(cli, "_twofa_password", account_data["2fa_password"])

        return cli

    except Exception as e:
        tb = traceback.format_exc(limit=3)
        logger.critical(f"{phone_number}: 💥 Error creating client instance → {type(e).__name__}: {e}\nTraceback:\n{tb}")
        return None


# ============================================================
# 🧩 Preload Clients (دقیق)
# ============================================================
async def preload_clients(limit: Optional[int] = None) -> None:
    phones = list(get_active_accounts())
    if limit is not None:
        phones = phones[:max(0, int(limit))]

    logger.info(f"🚀 Starting preload for {len(phones)} account(s)...")

    ok, bad = 0, 0
    for idx, phone in enumerate(phones, 1):
        logger.info(f"🔹 [{idx}/{len(phones)}] Preloading {phone} ...")
        try:
            cli = await get_or_start_client(phone)
            if cli and getattr(cli, "is_connected", False):
                ok += 1
                logger.info(f"{phone}: ✅ Connected OK.")
            else:
                bad += 1
                logger.warning(f"{phone}: ❌ Not connected after start().")
        except Exception as e:
            bad += 1
            tb = traceback.format_exc(limit=3)
            logger.error(f"{phone}: ❌ Exception during preload → {type(e).__name__}: {e}\n{tb}")

        # فاصله ایمن بین استارت‌ها برای SQLite
        await asyncio.sleep(1.0)

    logger.info(f"🎯 Preload completed: OK={ok} | FAIL={bad}")


# ============================================================
# 🧹 Stop all
# ============================================================
async def stop_all_clients() -> None:
    logger.info("🧹 Stopping all clients...")
    for phone, cli in list(client_pool.items()):
        try:
            await cli.stop()
            logger.info(f"{phone}: 📴 Stopped cleanly.")
        except Exception as e:
            tb = traceback.format_exc(limit=2)
            logger.warning(f"{phone}: ⚠️ Error stopping client → {type(e).__name__}: {e}\n{tb}")
        finally:
            client_pool.pop(phone, None)
            await asyncio.sleep(0.3)
    logger.info("✅ stop_all_clients finished.")


# ============================================================
# 🔍 کمکی‌ها
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
