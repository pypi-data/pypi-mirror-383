# antispam_core/lefter.py
import asyncio
import logging
import re
from pyrogram import errors
from .precise_engine import PreciseTicker

# 🧾 تنظیمات ذخیره لاگ در فایل left_log.txt
logging.basicConfig(
    filename="left_log.txt",                # نام فایل لاگ
    level=logging.INFO,                     # سطح لاگ‌ها (INFO و بالاتر)
    format="%(asctime)s - %(levelname)s - %(message)s",  # قالب لاگ
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)
logger = logging.getLogger(__name__)

async def leave_all(acc_list, chat_ref, get_or_start_client):
    """
    خروج از هر نوع چت:
    - پشتیبانی از chat_id، لینک عمومی، لینک خصوصی (joinchat/...)، یا username.
    تمام لاگ‌ها در فایل left_log.txt ذخیره می‌شوند.
    """
    ticker = PreciseTicker(1.0)
    success, failed = 0, 0

    logger.info(f"🚪 شروع عملیات Leave برای چت: {chat_ref}")
    logger.info(f"📱 تعداد اکانت‌ها: {len(acc_list)}")

    for phone in acc_list:
        try:
            cli = await get_or_start_client(phone)
            if not cli:
                logger.warning(f"{phone}: ❌ Client could not be started.")
                failed += 1
                await ticker.sleep()
                continue

            target = str(chat_ref).strip()

            # 🧩 پاکسازی لینک و استخراج شناسه
            target = re.sub(r"^https?://", "", target)
            target = re.sub(r"^(t\.me/|telegram\.me/)", "", target)
            target = target.split("?")[0].strip()
            if target.startswith("@"):
                target = target[1:]

            try:
                # 📦 اگر عددی است => chat_id مستقیم
                if target.lstrip("-").isdigit():
                    chat_id = int(target)
                    await cli.leave_chat(chat_id)
                    success += 1
                    logger.info(f"{phone}: ✅ Left chat_id {chat_id}")

                # 📩 اگر لینک خصوصی است
                elif "joinchat" in target or re.match(r"^[A-Za-z0-9_+\-]{20,}$", target):
                    invite_hash = target.replace("joinchat/", "").lstrip("+").strip()
                    try:
                        # وارد شدن موقت برای خروج
                        chat = await cli.import_chat_invite_link(invite_hash)
                        await cli.leave_chat(chat.id)
                        success += 1
                        logger.info(f"{phone}: ✅ Left private chat via invite {invite_hash}")
                    except errors.InviteHashInvalid:
                        logger.warning(f"{phone}: ⚠️ Invalid invite link ({invite_hash})")
                        failed += 1
                    except errors.InviteHashExpired:
                        logger.warning(f"{phone}: ⏳ Invite link expired ({invite_hash})")
                        failed += 1
                    except errors.FloodWait as e:
                        logger.warning(f"{phone}: ⏰ FloodWait {e.value}s")
                        await asyncio.sleep(e.value)
                        failed += 1
                    except Exception as e:
                        logger.warning(f"{phone}: ❌ Private leave failed: {type(e).__name__} - {e}")
                        failed += 1

                # 🌐 لینک یا یوزرنیم عمومی
                else:
                    try:
                        await cli.leave_chat(target)
                        success += 1
                        logger.info(f"{phone}: ✅ Left public chat @{target}")
                    except errors.UserNotParticipant:
                        success += 1
                        logger.info(f"{phone}: ⚙️ Not participant in @{target}")
                    except errors.ChannelPrivate:
                        failed += 1
                        logger.warning(f"{phone}: 🔒 Cannot access @{target} (private/restricted)")
                    except errors.FloodWait as e:
                        logger.warning(f"{phone}: ⏰ FloodWait {e.value}s")
                        await asyncio.sleep(e.value)
                        try:
                            await cli.leave_chat(target)
                            success += 1
                            logger.info(f"{phone}: ✅ Left after FloodWait @{target}")
                        except Exception as e2:
                            failed += 1
                            logger.error(f"{phone}: ❌ After FloodWait error: {e2}")
                    except Exception as e:
                        failed += 1
                        logger.warning(f"{phone}: ❌ Leave failed: {type(e).__name__} - {e}")

            except Exception as e:
                failed += 1
                logger.error(f"{phone}: 💥 General leave error {type(e).__name__} - {e}")

        except Exception as e:
            logger.error(f"{phone}: 💥 Fatal error {type(e).__name__} - {e}")
            failed += 1

        await ticker.sleep()

    logger.info(f"🎯 Leave completed → Success: {success} | Failed: {failed}")
    logger.info("------------------------------------------------------\n")

    return success, failed
