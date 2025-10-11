# antispam_core/client_manager.py
import os, json, asyncio, logging , random
from typing import Optional, Dict, List
from pyrogram import Client

logger = logging.getLogger(__name__)

client_pool: Dict[str, Client] = {}
client_locks: Dict[str, asyncio.Lock] = {}

ACCOUNTS_FOLDER = 'acc'
ACCOUNTS_DATA_FOLDER = 'acc_data'
os.makedirs(ACCOUNTS_DATA_FOLDER, exist_ok=True)

# ===============================
#   مدیریت سشن‌ها و کلاینت‌ها
# ===============================

async def get_or_start_client(phone_number: str) -> Optional[Client]:
    """دریافت یا راه‌اندازی کلاینت از فایل سشن"""
    cli = client_pool.get(phone_number)
    try:
        if cli is not None and getattr(cli, 'is_connected', False):
            return cli
        cli = _make_client_from_json(phone_number)
        if cli is None:
            return None
        await cli.start()
        client_pool[phone_number] = cli
        client_locks.setdefault(phone_number, asyncio.Lock())
        logger.info(f'Started client for {phone_number}')
        return cli
    except Exception as e:
        logger.error(f'Error starting client for {phone_number}: {e}')
        return None


async def stop_all_clients():
    """توقف و پاکسازی تمام کلاینت‌های فعال"""
    errs = 0
    for phone, cli in list(client_pool.items()):
        try:
            await cli.stop()
            logger.info(f'Stopped client for {phone}')
        except Exception as e:
            errs += 1
            logger.warning(f'Error stopping client for {phone}: {e}')
        finally:
            client_pool.pop(phone, None)
            client_locks.pop(phone, None)
    if errs:
        logger.info(f'Client pool shutdown had {errs} error(s)')


# ===============================
#   مدیریت داده‌های اکانت
# ===============================

def get_account_data(phone_number: str) -> Optional[Dict]:
    """خواندن داده‌های json اکانت"""
    file_path = os.path.join(ACCOUNTS_DATA_FOLDER, f'{phone_number}.json')
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f'Error reading account data for {phone_number}: {e}')
        return None


def save_account_data(phone_number: str, data: Dict):
    """ذخیره اطلاعات json اکانت"""
    file_path = os.path.join(ACCOUNTS_DATA_FOLDER, f'{phone_number}.json')
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f'Account data saved for {phone_number}')
    except Exception as e:
        logger.error(f'Error saving account data for {phone_number}: {e}')

def accounts() -> List[str]:
    """لیست تمام اکانت‌های موجود در پوشه acc"""
    accs = set()
    if not os.path.isdir(ACCOUNTS_FOLDER):
        return []
    for acc in os.listdir(ACCOUNTS_FOLDER):
        if acc.endswith('.session'):
            accs.add(acc.split('.')[0])
    return list(accs)

def get_app_info() -> List[str]:
    try:
        apis = {1: ['debac98afc137d3a82df5454f345bf02', 23523087], 2: ['b86bbf4b700b4e922fff2c05b3b8985f', 17221354], 3: ['2345124333c84e4f72441606a08e882c', 21831682], 4: ['1ebc2808ef58a95bc796590151c3e0d5', 14742007], 5: ['b8eff20a7e8adcdaa3daa3bc789a5b41', 12176206]}
        return apis[random.randint(1, 5)]
    except Exception as e:
        logger.error(f'Error reading app info: {e}')
        return []
    
def get_active_accounts() -> set:
    """برگرداندن مجموعه‌ی اکانت‌های فعال"""
    return set(accounts())


def _make_client_from_json(phone_number: str) -> Optional[Client]:
    """ایجاد Client از اطلاعات JSON ذخیره‌شده"""
    try:
        account_data = get_account_data(phone_number)
        if not account_data:
            logger.error(f'No account data found for {phone_number}')
            return None

        session_path = os.path.join(ACCOUNTS_FOLDER, account_data['session'])
        if not os.path.exists(session_path + '.session'):
            logger.error(f'Session file not found for {phone_number}')
            return None

        cli = Client(
            session_path,
            api_id=int(account_data['api_id']),
            api_hash=account_data['api_hash'],
            sleep_threshold=30
        )

        if account_data.get('2fa_password'):
            cli.password = account_data['2fa_password']

        return cli
    except Exception as e:
        logger.error(f'Error creating client for {phone_number}: {e}')
        return None
