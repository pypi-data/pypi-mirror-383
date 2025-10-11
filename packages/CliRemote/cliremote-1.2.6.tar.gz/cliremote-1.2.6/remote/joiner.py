# remote/joiner.py
import asyncio
import logging
import re
from pyrogram import errors
from .precise_engine import PreciseTicker

logger = logging.getLogger(__name__)

async def join_all(acc_list, link, get_or_start_client):
    """
    تمام اکانت‌ها را به لینک مشخص‌شده جوین می‌کند.
    لینک می‌تواند از نوع عمومی یا خصوصی باشد.
    """
    ticker = PreciseTicker(1.0)
    success, failed = 0, 0

    for phone in acc_list:
        try:
            cli = await get_or_start_client(phone)
            if not cli:
                logger.warning(f"{phone}: client not started.")
                failed += 1
                await ticker.sleep()
                continue

            # 🧩 پاکسازی لینک و تشخیص نوع
            clean_link = link.strip()

            # حذف پیشوندهای http / https
            clean_link = re.sub(r"^https?://", "", clean_link)

            # حذف دامنه تلگرام
            clean_link = re.sub(r"^(t\.me/|telegram\.me/)", "", clean_link)

            # حذف پارامترهای اضافی (مثل ?start=)
            clean_link = clean_link.split("?")[0].strip()

            # حذف @ در ابتدای نام کاربری
            if clean_link.startswith("@"):
                clean_link = clean_link[1:]

            # 📩 تشخیص لینک خصوصی یا عمومی
            # نمونه لینک خصوصی: https://t.me/+MJ35lbQVvrJmODk0  یا  https://t.me/joinchat/MJ35lbQVvrJmODk0
            if "joinchat" in clean_link or re.match(r"^[A-Za-z0-9_+\-]{20,}$", clean_link):
                # حذف بخش joinchat/ و علامت +
                invite_hash = clean_link.replace("joinchat/", "").lstrip("+").strip()

                try:
                    await cli.import_chat_invite_link(invite_hash)
                    logger.info(f"{phone}: joined private chat via invite {invite_hash}")
                    success += 1

                except errors.UserAlreadyParticipant:
                    logger.info(f"{phone}: already in chat")
                    success += 1

                except errors.InviteHashInvalid:
                    logger.warning(f"{phone}: invalid invite link ({invite_hash})")
                    failed += 1

                except errors.InviteHashExpired:
                    logger.warning(f"{phone}: invite link expired ({invite_hash})")
                    failed += 1

                except errors.FloodWait as e:
                    logger.warning(f"{phone}: FloodWait {e.value}s")
                    await asyncio.sleep(e.value)
                    failed += 1

                except Exception as e:
                    logger.warning(f"{phone}: failed to join private chat: {type(e).__name__} - {e}")
                    failed += 1

            else:
                # 🌐 گروه یا کانال عمومی
                try:
                    await cli.join_chat(clean_link)
                    logger.info(f"{phone}: joined public chat @{clean_link}")
                    success += 1

                except errors.UserAlreadyParticipant:
                    logger.info(f"{phone}: already in public chat")
                    success += 1

                except errors.UsernameInvalid:
                    logger.warning(f"{phone}: invalid username @{clean_link}")
                    failed += 1

                except errors.ChannelPrivate:
                    logger.warning(f"{phone}: cannot access @{clean_link} (private/restricted)")
                    failed += 1

                except errors.FloodWait as e:
                    logger.warning(f"{phone}: FloodWait {e.value}s")
                    await asyncio.sleep(e.value)
                    failed += 1

                except Exception as e:
                    logger.warning(f"{phone}: failed to join public chat: {type(e).__name__} - {e}")
                    failed += 1

        except Exception as e:
            logger.error(f"{phone}: fatal join error {type(e).__name__} - {e}")
            failed += 1

        await ticker.sleep()

    return success, failed
