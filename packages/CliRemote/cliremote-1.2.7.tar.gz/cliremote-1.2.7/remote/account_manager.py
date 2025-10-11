# antispam_core/account_manager.py
import os, asyncio, json, logging
from typing import Optional, Dict, List
from pyrogram import Client, errors
from .client_manager import (
    ACCOUNTS_FOLDER, 
    get_account_data, 
    save_account_data, 
    stop_all_clients, 
    accounts, 
    client_pool, 
    client_locks
)

logger = logging.getLogger(__name__)
login = {}

# ==========================
# افزودن اکانت جدید
# ==========================
async def add_account_cmd(message, get_app_info):
    try:
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            await message.reply('مثال: `add +989123456789`')
            return

        phone_number = parts[1].strip()
        session_file = os.path.join(ACCOUNTS_FOLDER, f'{phone_number}.session')

        if os.path.exists(session_file):
            await message.reply('این اکانت وجود دارد!')
            return

        global login
        api = get_app_info()
        if not api or len(api) < 2:
            await message.reply('مشکل در API!')
            return

        login['id'] = int(api[1])
        login['hash'] = api[0]
        login['number'] = phone_number
        login['api_data'] = {
            'api_id': api[1],
            'api_hash': api[0],
            'phone_number': phone_number,
            'session': phone_number,
            '2fa_password': None
        }

        try:
            login['client'] = Client(name=session_file.replace('.session', ''), api_id=login['id'], api_hash=login['hash'])
            await login['client'].connect()
            login['response'] = await login['client'].send_code(phone_number)
            await message.reply(f'✅ کد تأیید به {phone_number} ارسال شد.\n`code 12345`')
        except errors.BadRequest as e:
            await message.reply(f'Bad request: {str(e)}')
        except errors.FloodWait as e:
            await message.reply(f'Flood wait: {e.value} sec')
        except Exception as e:
            await message.reply(f'Connection error: {str(e)}')
    except Exception as e:
        await message.reply(f'خطا: {str(e)}')


# ==========================
# تأیید کد ورود
# ==========================
async def set_code_cmd(message):
    global login
    parts = message.text.split(' ', 1)
    if len(parts) < 2:
        await message.reply('`code 12345`')
        return
    code = parts[1].strip()

    try:
        await login['client'].sign_in(login['number'], login['response'].phone_code_hash, code)
        await login['client'].disconnect()
        save_account_data(login['number'], login['api_data'])
        await message.reply(f"✅ اکانت اضافه شد!\n├ شماره: {login['number']}")
        login = {}
    except errors.SessionPasswordNeeded:
        await message.reply('🔒 لطفا رمز را با `pass your_password` بدهید')
    except errors.BadRequest:
        await message.reply('ورود با مشکل مواجه شد')
    except Exception as e:
        await message.reply(f'⚠️ خطا در ورود: {e}')


# ==========================
# افزودن رمز دومرحله‌ای
# ==========================
async def set_2fa_cmd(message):
    global login
    parts = message.text.split(' ', 1)
    if len(parts) < 2:
        await message.reply('`pass my_password`')
        return
    password = parts[1].strip()
    try:
        await login['client'].check_password(password)
        login['api_data']['2fa_password'] = password
        save_account_data(login['number'], login['api_data'])
        await message.reply(f"✅ اکانت با موفقیت اضافه شد!\n├ شماره: {login['number']}")
        await login['client'].disconnect()
        login = {}
    except errors.BadRequest:
        await message.reply('رمز اشتباه است!')
    except Exception as e:
        await message.reply(f'⚠️ خطا در ثبت پسورد: {e}')


# ==========================
# حذف یک اکانت خاص
# ==========================
def remove_client_from_pool(phone_number: str):
    cli = client_pool.get(phone_number)
    if cli:
        try:
            asyncio.create_task(cli.stop())
        except:
            pass
        client_pool.pop(phone_number, None)
        client_locks.pop(phone_number, None)


async def delete_account_cmd(message):
    try:
        phone_number = message.text.split()[1]
        main_path = f'{ACCOUNTS_FOLDER}/{phone_number}.session'
        remove_client_from_pool(phone_number)
        if os.path.isfile(main_path):
            os.unlink(main_path)
            await message.reply('<b>Account deleted successfully.</b>')
        else:
            await message.reply('<b>Account not found in database.</b>')
    except IndexError:
        await message.reply('Please enter phone number')
    except Exception as e:
        await message.reply(f'<b>Error deleting account: {str(e)}</b>')


# ==========================
# حذف تمام اکانت‌ها
# ==========================
async def delete_all_accounts_cmd(message):
    try:
        accountss = accounts()
        count = len(accountss)
        await stop_all_clients()
        for session in accountss:
            main_path = f'{ACCOUNTS_FOLDER}/{session}.session'
            try:
                os.unlink(main_path)
            except Exception:
                pass
        await message.reply(f'<b>{count} accounts deleted.</b>')
    except Exception as e:
        await message.reply(f'<b>Error deleting all accounts: {str(e)}</b>')
