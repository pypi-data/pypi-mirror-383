# antispam_core/joiner.py
import asyncio, logging, re
from pyrogram import errors
from .precise_engine import PreciseTicker

logger = logging.getLogger(__name__)

async def join_all(acc_list, link, get_or_start_client):
    ticker = PreciseTicker(1.0)
    success, failed = 0, 0

    for phone in acc_list:
        try:
            cli = await get_or_start_client(phone)
            if not cli:
                failed += 1
                await ticker.sleep()
                continue

            # 🧩 پاکسازی لینک و تشخیص نوع
            clean_link = link.strip()
            if clean_link.startswith("https://"):
                clean_link = clean_link.replace("https://", "")
            if clean_link.startswith("http://"):
                clean_link = clean_link.replace("http://", "")
            if clean_link.startswith("t.me/"):
                clean_link = clean_link.split("t.me/")[1]
            elif clean_link.startswith("telegram.me/"):
                clean_link = clean_link.split("telegram.me/")[1]
            if clean_link.startswith("@"):
                clean_link = clean_link[1:]
            clean_link = clean_link.split("?")[0].strip()

            # 📩 تشخیص لینک خصوصی یا عمومی
            if "joinchat" in clean_link or re.match(r"^[A-Za-z0-9_-]{20,}$", clean_link):
                invite_hash = clean_link.replace("joinchat/", "")
                try:
                    await cli.import_chat_invite_link(invite_hash)
                    logger.info(f"{phone} joined private chat via invite {invite_hash}")
                    success += 1
                except errors.UserAlreadyParticipant:
                    success += 1
                except errors.InviteHashInvalid:
                    logger.warning(f"{phone}: invalid invite link")
                    failed += 1
                except errors.InviteHashExpired:
                    logger.warning(f"{phone}: expired invite link")
                    failed += 1
                except Exception as e:
                    logger.warning(f"{phone}: failed to join private chat: {e}")
                    failed += 1

            else:
                # 🌐 گروه یا کانال عمومی
                try:
                    await cli.join_chat(clean_link)
                    logger.info(f"{phone} joined {clean_link}")
                    success += 1
                except errors.UserAlreadyParticipant:
                    success += 1
                except errors.UsernameInvalid:
                    logger.warning(f"{phone}: invalid username {clean_link}")
                    failed += 1
                except errors.ChannelPrivate:
                    logger.warning(f"{phone}: cannot access {clean_link} (private/restricted)")
                    failed += 1
                except Exception as e:
                    logger.warning(f"{phone}: join failed {e}")
                    failed += 1

        except Exception as e:
            logger.error(f"{phone}: fatal join error {e}")
            failed += 1

        await ticker.sleep()

    return success, failed
