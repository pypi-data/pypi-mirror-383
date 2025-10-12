
import os
import json
import asyncio
import logging
import random
import traceback
from typing import Optional, Dict, List, Set, Tuple
from pyrogram import Client, errors

# ============================================================
# ⚙️ دقیق‌ترین لاگ برای دیباگ Pyrogram/SQLite
# ============================================================
os.makedirs("logs", exist_ok=True)
LOG_FILE = "logs/client_debug_log.txt"
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not any(isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", "").endswith(LOG_FILE) for h in logger.handlers):
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

logger.info("🧩 Client Manager (DEBUG MODE) booted.")

# ============================================================
# 📁 مسیرها و استخرها
# ============================================================
ACCOUNTS_FOLDER = "acc"
ACCOUNTS_DATA_FOLDER = "acc_data"
os.makedirs(ACCOUNTS_FOLDER, exist_ok=True)
os.makedirs(ACCOUNTS_DATA_FOLDER, exist_ok=True)

client_pool: Dict[str, Client] = {}
client_locks: Dict[str, asyncio.Lock] = {}

# ============================================================
# 🔧 ابزارک‌ها
# ============================================================
def _ensure_dir(path: str):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        logger.error(f"⚠️ Cannot create directory {path}: {type(e).__name__}: {e}")

def _strip_session_ext(session_base: str) -> str:
    # "acc/123.session" -> "acc/123"; "123.session" -> "123"
    if session_base.endswith(".session"):
        return session_base[:-8]
    return session_base

# ============================================================
# 💾 JSON helpers
# ============================================================
def get_account_data(phone_number: str) -> Optional[Dict]:
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
    _ensure_dir(ACCOUNTS_DATA_FOLDER)
    file_path = os.path.join(ACCOUNTS_DATA_FOLDER, f"{phone_number}.json")
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"{phone_number}: 💾 Account data saved → {file_path}")
    except Exception as e:
        logger.error(f"{phone_number}: ⚠️ Error saving JSON - {type(e).__name__}: {e}")

# ============================================================
# 🧱 ساخت کلاینت از JSON (بدون پسوند .session در name)
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

        # Build session name WITHOUT .session extension
        if os.path.isabs(session_base) or os.path.dirname(session_base):
            session_name = _strip_session_ext(session_base)
        else:
            session_name = os.path.join(ACCOUNTS_FOLDER, _strip_session_ext(session_base))

        # Ensure parent dir exists
        _ensure_dir(os.path.dirname(session_name) or ".")

        api_id = account_data.get("api_id")
        api_hash = account_data.get("api_hash")
        if not api_id or not api_hash:
            logger.error(f"{phone_number}: Missing API credentials in JSON → {data_path}")
            return None

        # Separate workdir per account to avoid file collisions
        workdir = os.path.join("acc_temp", phone_number)
        _ensure_dir(workdir)

        cli = Client(
            name=session_name,          # <— NO .session here
            api_id=int(api_id),
            api_hash=str(api_hash),
            sleep_threshold=30,
            workdir=workdir,
            no_updates=True,
        )

        if account_data.get("2fa_password"):
            setattr(cli, "_twofa_password", account_data["2fa_password"])

        logger.debug(f"{phone_number}: Prepared Client(name={session_name})")
        return cli

    except Exception as e:
        tb = traceback.format_exc(limit=3)
        logger.critical(f"{phone_number}: 💥 Error creating client - {type(e).__name__}: {e}\n{tb}")
        return None

# ============================================================
# 🧠 دریافت/استارت کلاینت
# ============================================================
async def get_or_start_client(phone_number: str) -> Optional[Client]:
    cli = client_pool.get(phone_number)
    try:
        if cli is not None and getattr(cli, "is_connected", False):
            logger.debug(f"{phone_number}: Already connected → {getattr(cli, 'name', '?')}")
            return cli

        cli = _make_client_from_json(phone_number)
        if cli is None:
            logger.error(f"{phone_number}: ❌ Could not build client (invalid JSON/session)")
            return None

        # Compute expected session file path for logging
        session_file = f"{cli.name}.session"
        logger.debug(f"{phone_number}: Expected session file → {session_file}")
        if os.path.exists(session_file):
            try:
                size = os.path.getsize(session_file)
                logger.debug(f"{phone_number}: Session file exists ({size} bytes)")
            except Exception:
                logger.debug(f"{phone_number}: Session file exists (size unknown)")
        else:
            logger.debug(f"{phone_number}: Session file will be created by Pyrogram")

        # Start with careful handling
        try:
            await cli.start()
            await asyncio.sleep(0.4)  # brief pause helps SQLite on some FS
            logger.info(f"{phone_number}: ✅ Client started.")
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
# 🚀 Preload با فاصله ایمن
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

        await asyncio.sleep(0.8 + random.uniform(0.1, 0.3))

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
            client_locks.pop(phone, None)
            await asyncio.sleep(0.2)
    logger.info("✅ All clients stopped cleanly.")

# ============================================================
# 📋 لیست اکانت‌های فعال (بر اساس فایل‌های .session)
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
