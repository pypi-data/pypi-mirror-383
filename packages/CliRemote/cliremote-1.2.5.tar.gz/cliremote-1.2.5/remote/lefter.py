# antispam_core/lefter.py
import asyncio, logging, re
from pyrogram import errors
from .precise_engine import PreciseTicker

logger = logging.getLogger(__name__)

async def leave_all(acc_list, chat_ref, get_or_start_client):
    """
    خروج از هر نوع چت:
    - پشتیبانی از chat_id، لینک عمومی، لینک خصوصی (joinchat/...)، یا username.
    """
    ticker = PreciseTicker(1.0)
    success, failed = 0, 0

    for phone in acc_list:
        try:
            cli = await get_or_start_client(phone)
            if not cli:
                failed += 1
                await ticker.sleep()
                continue

            target = str(chat_ref).strip()

            # 🧩 پاکسازی لینک و استخراج شناسه
            if target.startswith("https://"):
                target = target.replace("https://", "")
            if target.startswith("http://"):
                target = target.replace("http://", "")
            if target.startswith("t.me/"):
                target = target.split("t.me/")[1]
            elif target.startswith("telegram.me/"):
                target = target.split("telegram.me/")[1]
            if target.startswith("@"):
                target = target[1:]
            target = target.split("?")[0].strip()

            try:
                # 📦 اگر عددی است => chat_id مستقیم
                if target.lstrip("-").isdigit():
                    chat_id = int(target)
                    await cli.leave_chat(chat_id)
                    success += 1
                    logger.info(f"{phone} left chat_id {chat_id}")

                # 📩 اگر لینک خصوصی است
                elif "joinchat" in target or re.match(r"^[A-Za-z0-9_-]{20,}$", target):
                    invite_hash = target.replace("joinchat/", "")
                    try:
                        # سعی می‌کنیم اول وارد شویم، سپس خارج
                        chat = await cli.import_chat_invite_link(invite_hash)
                        await cli.leave_chat(chat.id)
                        success += 1
                        logger.info(f"{phone} left private chat via invite {invite_hash}")
                    except errors.InviteHashInvalid:
                        logger.warning(f"{phone}: invalid invite link")
                        failed += 1
                    except errors.InviteHashExpired:
                        logger.warning(f"{phone}: expired invite link")
                        failed += 1
                    except Exception as e:
                        logger.warning(f"{phone}: private leave failed {e}")
                        failed += 1

                # 🌐 لینک یا یوزرنیم عمومی
                else:
                    try:
                        await cli.leave_chat(target)
                        success += 1
                        logger.info(f"{phone} left {target}")
                    except errors.UserNotParticipant:
                        success += 1
                        logger.info(f"{phone}: not participant in {target}")
                    except errors.ChannelPrivate:
                        failed += 1
                        logger.warning(f"{phone}: cannot access {target} (private/restricted)")
                    except errors.FloodWait as e:
                        logger.warning(f"{phone}: FloodWait({e.value})")
                        await asyncio.sleep(e.value)
                        try:
                            await cli.leave_chat(target)
                            success += 1
                        except Exception as e2:
                            failed += 1
                            logger.error(f"{phone}: after FloodWait error {e2}")
                    except Exception as e:
                        failed += 1
                        logger.warning(f"{phone}: leave failed {e}")

            except Exception as e:
                failed += 1
                logger.error(f"{phone}: general leave error {e}")

        except Exception as e:
            logger.error(f"{phone}: fatal error {e}")
            failed += 1

        await ticker.sleep()

    return success, failed
