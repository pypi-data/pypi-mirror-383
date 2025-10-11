# remote/joiner.py
import asyncio
import logging
import re
from pyrogram import errors
from .precise_engine import PreciseTicker

# 🧾 تنظیمات ذخیره لاگ‌ها در فایل
logging.basicConfig(
    filename="join_log.txt",                # مسیر فایل لاگ
    level=logging.INFO,                     # سطح حداقل لاگ
    format="%(asctime)s - %(levelname)s - %(message)s",  # قالب نمایش
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)

async def join_all(acc_list, link, get_or_start_client):
    """
    تمام اکانت‌ها را به لینک مشخص‌شده جوین می‌کند.
    لینک می‌تواند از نوع عمومی یا خصوصی باشد.
    تمام لاگ‌ها در join_log.txt ذخیره می‌شوند.
    """
    ticker = PreciseTicker(1.0)
    success, failed = 0, 0

    logger.info(f"🚀 شروع عملیات Join برای لینک: {link}")
    logger.info(f"📱 تعداد اکانت‌ها: {len(acc_list)}")

    for phone in acc_list:
        try:
            cli = await get_or_start_client(phone)
            if not cli:
                logger.warning(f"{phone}: ❌ Client could not be started.")
                failed += 1
                await ticker.sleep()
                continue

            # 🧩 پاکسازی لینک و تشخیص نوع
            clean_link = link.strip()
            clean_link = re.sub(r"^https?://", "", clean_link)
            clean_link = re.sub(r"^(t\.me/|telegram\.me/)", "", clean_link)
            clean_link = clean_link.split("?")[0].strip()
            if clean_link.startswith("@"):
                clean_link = clean_link[1:]

            # 📩 تشخیص لینک خصوصی یا عمومی
            if "joinchat" in clean_link or re.match(r"^[A-Za-z0-9_+\-]{20,}$", clean_link):
                invite_hash = clean_link.replace("joinchat/", "").lstrip("+").strip()

                try:
                    await cli.import_chat_invite_link(invite_hash)
                    logger.info(f"{phone}: ✅ Joined private chat via invite {invite_hash}")
                    success += 1

                except errors.UserAlreadyParticipant:
                    logger.info(f"{phone}: ⚙️ Already in private chat.")
                    success += 1

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
                    logger.warning(f"{phone}: ❌ Failed to join private chat: {type(e).__name__} - {e}")
                    failed += 1

            else:
                # 🌐 گروه یا کانال عمومی
                try:
                    await cli.join_chat(clean_link)
                    logger.info(f"{phone}: ✅ Joined public chat @{clean_link}")
                    success += 1

                except errors.UserAlreadyParticipant:
                    logger.info(f"{phone}: ⚙️ Already in public chat.")
                    success += 1

                except errors.UsernameInvalid:
                    logger.warning(f"{phone}: ⚠️ Invalid username @{clean_link}")
                    failed += 1

                except errors.ChannelPrivate:
                    logger.warning(f"{phone}: 🔒 Cannot access @{clean_link} (private/restricted)")
                    failed += 1

                except errors.FloodWait as e:
                    logger.warning(f"{phone}: ⏰ FloodWait {e.value}s")
                    await asyncio.sleep(e.value)
                    failed += 1

                except Exception as e:
                    logger.warning(f"{phone}: ❌ Failed to join public chat: {type(e).__name__} - {e}")
                    failed += 1

        except Exception as e:
            logger.error(f"{phone}: 💥 Fatal join error {type(e).__name__} - {e}")
            failed += 1

        await ticker.sleep()

    logger.info(f"🎯 Join completed → Success: {success} | Failed: {failed}")
    logger.info("------------------------------------------------------\n")

    return success, failed
