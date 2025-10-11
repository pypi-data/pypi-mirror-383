# antispam_core/getcode_controller.py
import os, logging
from pyrogram import Client
logger = logging.getLogger(__name__)

async def handle_getcode_cmd(message, get_app_info):
    """
    فرمان /gcode
    پیام آخر از 777000 را از سشن اکانت خواسته‌شده می‌خواند.
    """
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply('لطفا شماره را وارد کنید\nمثال: gcode +989123456789')
            return

        number = parts[1]
        session_path = f'acc/{number}.session'
        if not os.path.exists(session_path):
            await message.reply('<b>شماره مورد نظر وجود ندارد.</b>')
            return

        info = get_app_info()
        if not info or len(info) < 2:
            await message.reply('<b>خطا در دریافت اطلاعات API</b>')
            return

        api_hash = info[0]
        api_id = info[1]

        try:
            async with Client(f'acc/{number}', api_id, api_hash) as cli:
                messages = [msg async for msg in cli.get_chat_history(777000, limit=1)]
                if messages and messages[0].text:
                    await message.reply(messages[0].text)
                else:
                    await message.reply('هیچ پیامی از تلگرام دریافت نشد')
        except Exception as e:
            logger.error(f"Error while reading code for {number}: {e}")
            await message.reply(f'<b>هنگام فراخوانی سشن خطایی رخ داد:</b>\n{str(e)}')

    except Exception as e:
        logger.error(f"getcode unknown error: {e}")
        await message.reply(f'<b>خطای ناشناخته:</b> {str(e)}')
