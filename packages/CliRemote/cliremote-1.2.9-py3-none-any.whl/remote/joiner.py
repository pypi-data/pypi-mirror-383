# remote/joiner.py
import asyncio
import os
import logging
import re
from pyrogram import errors
from .precise_engine import PreciseTicker

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ساخت فولدر لاگ و هندلر مخصوص این ماژول
os.makedirs("logs", exist_ok=True)
file_handler = logging.FileHandler("logs/join_log.txt", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(formatter)
# اگر logger از قبل هندلر دارد، اضافه نکن (جلوگیری از duplicate)
if not any(isinstance(h, logging.FileHandler) and h.baseFilename.endswith("join_log.txt") for h in logger.handlers):
    logger.addHandler(file_handler)


def _normalize_target(raw: str):
    """
    ورودی متنوع را نرمالایز می‌کند و نوع را برمی‌گرداند:
    -> ('invite', invite_hash)    : برای لینک‌های دعوت (با یا بدون +)
    -> ('username', username)     : برای یوزرنیم‌ها (بدون @)
    -> ('chat_id', int_chat_id)   : برای chat_id عددی
    """
    if raw is None:
        return None, None

    s = str(raw).strip()

    # پاکسازی پروتکل و www
    s = re.sub(r'^(?:https?://)', '', s, flags=re.I)
    s = re.sub(r'^www\.', '', s, flags=re.I)

    # اگر شامل slash است، آخرین بخش مسیر را بگیر
    if '/' in s:
        s = s.split('/')[-1]

    # اگر کاربر به‌اشتباه از نقطه برای دامنه استفاده کرده (ex: Unity_Darkness.T.me)
    # سعی می‌کنیم قسمت قبل از .t.me یا .telegram.me را استخراج کنیم
    m = re.search(r'^(?P<name>.*?)\.(?:t\.me|telegram\.me)$', s, flags=re.I)
    if m:
        s = m.group("name")

    # حذف query params و <> اگر بودند
    s = s.split('?')[0].strip()
    s = s.strip('<> "\'')  # محافظت در برابر کاراکترهای نامطلوب

    # اگر شروع با @ بود، حذفش کن (username)
    if s.startswith('@'):
        s = s[1:].strip()

    # اگر شروع با + هست => invite hash (حذف + چون Pyrogram نیاز ندارد)
    if s.startswith('+'):
        return 'invite', s.lstrip('+').strip()

    # chat_id عددی (ممکن است منفی باشد)
    if s.lstrip('-').isdigit():
        try:
            return 'chat_id', int(s)
        except Exception:
            pass

    # بعضی invite-hash ها بدون + هم فرستاده می‌شوند (طول و کاراکترها را چک می‌کنیم)
    if re.match(r'^[A-Za-z0-9_\-]{8,}$', s):  # طول حداقلی 8 (ایمن و منعطف)
        # اگر طول مناسب برای invite باشد (معمولاً 20+)، آن را invite فرض کن.
        # اما اگر کوتاه و حتماً نام کاربری است، اینجا هم username پذیرفته می‌شود.
        if len(s) >= 20:
            return 'invite', s
        # اگر طول کمتر است و حروف/اعداد مناسب است، اما احتمال username هم وجود دارد.
        # تصمیم: اگر شامل حروف بزرگ/کوچک و _ یا - باشد و طول کمتر از 20، آن را username در نظر می‌گیریم.
        return 'username', s

    # fallback: treat as username
    return 'username', s


async def join_all(acc_list, link, get_or_start_client):
    """
    تمام اکانت‌ها را به لینک مشخص‌شده جوین می‌کند.
    لینک می‌تواند از نوع عمومی (username)، خصوصی (invite hash)، یا chat_id باشد.
    تمام لاگ‌ها در logs/join_log.txt ذخیره می‌شوند.
    """
    ticker = PreciseTicker(1.0)
    success, failed = 0, 0

    logger.info(f"🚀 شروع عملیات Join برای لینک: {link}")
    logger.info(f"📱 تعداد اکانت‌ها: {len(acc_list)}")

    # نرمالایز یک‌بار بیرون حلقه (اگر یک string واحد است)
    ttype, tval = _normalize_target(link)

    if ttype is None:
        logger.error("ورودی لینک خالی یا نامعتبر است.")
        return 0, len(acc_list)

    for phone in acc_list:
        try:
            cli = await get_or_start_client(phone)
            if not cli:
                logger.warning(f"{phone}: ❌ Client could not be started.")
                failed += 1
                await ticker.sleep()
                continue

            # بسته به نوع، اقدام مناسب انجام می‌شود
            if ttype == 'invite':
                invite_hash = str(tval).lstrip('+').strip()  # مطمئن شو + حذف شده
                try:
                    # import_chat_invite_link از invite_hash بدون + پشتیبانی می‌کند
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

            elif ttype == 'chat_id':
                chat_id = tval
                try:
                    await cli.join_chat(chat_id)
                    logger.info(f"{phone}: ✅ Joined chat_id {chat_id}")
                    success += 1
                except errors.UserAlreadyParticipant:
                    logger.info(f"{phone}: ⚙️ Already in chat_id {chat_id}")
                    success += 1
                except Exception as e:
                    logger.warning(f"{phone}: ❌ Failed to join chat_id {chat_id}: {type(e).__name__} - {e}")
                    failed += 1

            else:  # username
                username = str(tval).lstrip('@').strip()
                try:
                    await cli.join_chat(username)
                    logger.info(f"{phone}: ✅ Joined public chat @{username}")
                    success += 1

                except errors.UserAlreadyParticipant:
                    logger.info(f"{phone}: ⚙️ Already in public chat @{username}")
                    success += 1

                except errors.UsernameInvalid:
                    logger.warning(f"{phone}: ⚠️ Invalid username @{username}")
                    failed += 1

                except errors.ChannelPrivate:
                    logger.warning(f"{phone}: 🔒 Cannot access @{username} (private/restricted)")
                    failed += 1

                except errors.FloodWait as e:
                    logger.warning(f"{phone}: ⏰ FloodWait {e.value}s")
                    await asyncio.sleep(e.value)
                    failed += 1

                except Exception as e:
                    logger.warning(f"{phone}: ❌ Failed to join public chat @{username}: {type(e).__name__} - {e}")
                    failed += 1

        except Exception as e:
            logger.error(f"{phone}: 💥 Fatal join error {type(e).__name__} - {e}")
            failed += 1

        await ticker.sleep()

    logger.info(f"🎯 Join completed → Success: {success} | Failed: {failed}")
    logger.info("------------------------------------------------------\n")

    return success, failed
