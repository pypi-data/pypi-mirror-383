# antispam_core/spammer_thread.py
import asyncio
import random
import threading
import shutil
import os
import logging
from datetime import datetime
from pyrogram import Client, errors
from collections import OrderedDict
from typing import Any, Dict
from .client_manager import get_account_data, accounts, ACCOUNTS_FOLDER
import sqlite3
from .client_manager import get_account_data, accounts
from .analytics_manager import analytics

# ============================================================
# ⚙️ سیستم لاگ جدید (با دقت نانوثانیه)
# ============================================================
class NanoFormatter(logging.Formatter):
    """Formatter سفارشی برای نمایش زمان تا نانوثانیه."""
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created)
        ns = int((record.created - int(record.created)) * 1_000_000_000)
        return f"{dt.strftime('%Y-%m-%d %H:%M:%S')}.{ns:09d}"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

os.makedirs("logs", exist_ok=True)
file_handler = logging.FileHandler("logs/spam_log.txt", encoding="utf-8")
file_handler.setFormatter(NanoFormatter("%(asctime)s - %(levelname)s - %(message)s"))

# جلوگیری از افزودن تکراری handler
if not any(
    isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", "").endswith("spam_log.txt")
    for h in logger.handlers
):
    logger.addHandler(file_handler)


# ============================================================
# 🧵 کلاس اصلی اسپمر
# ============================================================
class SpammerThread(threading.Thread):
    """
    SpammerThread:
    - منطق اجرای thread و event loop دقیقا مانند قبل حفظ شده.
    - ست‌بندی (config normalization) در self.config (OrderedDict) نگهداری می‌شود.
    - batching بر اساس BATCH_SIZE اضافه شده؛ پس از اتمام هر batch، sleep انجام می‌شود.
    """

    def __init__(self, spam_config: dict):
        super().__init__()
        self.is_running = False
        self.daemon = True
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.event_loop = None
        self.clients = []

        self.config: Dict[str, Any] = spam_config 
        
    def run(self):
        """تابع اصلی اسپمر در thread جداگانه"""
        self.is_running = True
        self.stop_event.clear()
        logger.info("🚀 اسپمر در حال اجرا است...")

        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)

        try:
            self.event_loop.run_until_complete(self._spammer_loop())
        except Exception as e:
            logger.exception(f"💥 خطای کلی در اسپمر: {e}")
        finally:
            try:
                self.event_loop.run_until_complete(self._disconnect_all_clients())
            except Exception:
                pass

            if self.event_loop:
                self.event_loop.close()
            self.is_running = False
            logger.info("🛑 اسپمر متوقف شد.")

    async def _disconnect_all_clients(self):
        """قطع ارتباط تمام کلاینت‌های فعال"""
        for client in list(self.clients):
            try:
                if client.is_connected:
                    await client.disconnect()
            except Exception:
                pass
        self.clients.clear()

    async def _spammer_loop(self):
        """حلقه اصلی اسپمر (حالا با batching بر اساس BATCH_SIZE)"""
        while not self.stop_event.is_set():
            try:
                accounts_list = accounts()
                if not accounts_list:
                    logger.warning("❌ هیچ اکانتی یافت نشد.")
                    await asyncio.sleep(5)
                    continue

                # خواندن پیکربندی
                caption = self.config.get("caption", "")
                text_candidates = self.config.get("texts", [])
                sleep_time = float(self.config.get("TimeSleep", 2))
                batch_size = int(self.config.get("BATCH_SIZE", 1))
                spam_targets = self.config.get("spamTarget", [])
                if isinstance(spam_targets, str):
                    spam_targets = [spam_targets]

                # ساخت متن نهایی (همان رفتار سابق)
                final_text = ""
                if text_candidates:
                    text_part = random.choice(text_candidates)
                    final_text = f"{text_part}\n{caption}" if caption else text_part
                else:
                    final_text = caption

                if self.config.get("is_menshen"):
                    user_id = self.config.get("useridMen")
                    mention_text = self.config.get("textMen", "")
                    mention_html = f"<a href='tg://user?id={user_id}'>{mention_text}</a>"
                    final_text = f"{final_text}\n{mention_html}"

                banned_accs = set()
                successful_sends = 0

                # تقسیم اکانت‌ها به batchها (حفظ ترتیب اصلی)
                batches = [accounts_list[i:i + batch_size] for i in range(0, len(accounts_list), batch_size)]

                for batch_idx, batch in enumerate(batches, start=1):
                    if self.stop_event.is_set():
                        break

                    logger.info(f"🔁 اجرای batch {batch_idx}/{len(batches)} با {len(batch)} اکانت")
 
                    for acc in batch:
                        if self.stop_event.is_set():
                            break

                        try:
                            client = await self._create_client(acc)
                            if not client:
                                continue

                            self.clients.append(client)
                            if not client.is_connected:
                                await client.connect()

                            for chat in spam_targets:
                                if self.stop_event.is_set():
                                    break
                                try:
                                    await client.send_message(chat_id=chat, text=final_text)
                                    logger.info(f"{acc}: ✅ پیام با موفقیت به {chat} ارسال شد.")
                                    successful_sends += 1 
                                    with self.lock:
                                        await analytics.update_stats(acc, True, chat)

                                except errors.PeerIdInvalid:
                                    err = f"{acc}: 🚫 دسترسی به {chat} ندارد."
                                    logger.warning(err)
                                    with self.lock:
                                        await analytics.update_stats(acc, False, chat)
                                    await asyncio.sleep(1)

                                except Exception as e:
                                    err = f"{acc}: ❌ خطا در ارسال پیام به {chat} → {e}"
                                    logger.error(err)
                                    with self.lock:
                                        await analytics.update_stats(acc, False, chat)
                                    await asyncio.sleep(1)

                            if client.is_connected:
                                await client.disconnect()
                            try:
                                self.clients.remove(client)
                            except ValueError:
                                pass

                        except errors.UserDeactivated:
                            err = f"{acc}: ⚠️ اکانت بن شده است."
                            logger.warning(err)
                            banned_accs.add(acc)
                            with self.lock:
                                await analytics.update_stats(acc, False, None)

                        except Exception as e:
                            err = f"{acc}: ❌ خطا در اتصال به اکانت → {e}"
                            logger.error(err)
                            with self.lock:
                                await analytics.update_stats(acc, False, None)
                    if self.stop_event.is_set():
                        break
                    logger.debug(f"⏸️ Batch {batch_idx} به پایان رسید — خواب {sleep_time}s قبل از batch بعدی")
                    await asyncio.sleep(sleep_time)

                logger.info(f"📊 پایان دور ارسال: {successful_sends} پیام موفق ارسال شد.")

                if not accounts_list or len(banned_accs) == len(accounts_list):
                    logger.warning("🚷 تمام اکانت‌ها مسدود یا غیرفعال شدند.")
                    break

                if "run" in self.config and not self.config.get("run", True):
                    logger.info("🔻 اجرای اسپمر توسط config متوقف شد (run=False).")
                    break

            except Exception as e:
                logger.exception(f"⚠️ خطای غیرمنتظره در حلقه اسپمر: {e}")
                await asyncio.sleep(5)

    async def _create_client(self, phone_number: str):
        """ایجاد کلاینت با مدیریت session (پایدارتر و با استفاده از ACCOUNTS_FOLDER)"""
        try:
            account_data = get_account_data(phone_number)
            if not account_data:
                logger.error(f"{phone_number}: داده حساب یافت نشد.")
                return None

            # استفاده از ACCOUNTS_FOLDER مرکزی (مثل نسخهٔ قدیمی)
            session_name = account_data.get("session")
            if not session_name:
                logger.error(f"{phone_number}: مقدار session در account_data موجود نیست.")
                return None

            session_base = os.path.join(ACCOUNTS_FOLDER, session_name)
            src_session_file = f"{session_base}.session"
            thread_session_base = f"{session_base}_thread_{threading.get_ident()}"
            dst_session_file = f"{thread_session_base}.session"

            # بررسی وجود فایل session مبدا و کپی امن آن
            if os.path.exists(src_session_file):
                try:
                    shutil.copy2(src_session_file, dst_session_file)
                    logger.debug(f"{phone_number}: copied session {src_session_file} -> {dst_session_file}")
                except Exception as e:
                    logger.error(f"{phone_number}: خطا در کپی session {src_session_file} -> {dst_session_file}: {e}")
                    # اگر کپی نشد، از ادامه ساخت client خودداری کن (به جای باز کردن DB خراب)
                    return None
            else:
                logger.warning(f"{phone_number}: فایل session مبدا یافت نشد: {src_session_file}. تلاش برای ایجاد client جدید بدون session.")

            # ساخت Client با نام session خاص thread
            try:
                client = Client(
                    thread_session_base,
                    api_id=int(account_data["api_id"]),
                    api_hash=account_data["api_hash"],
                    sleep_threshold=30
                )

                if account_data.get("2fa_password"):
                    client.password = account_data["2fa_password"]

                return client

            except sqlite3.DatabaseError as db_e:
                # خطاهای مربوط به sqlite را واضح لاگ کن
                logger.error(f"{phone_number}: sqlite DatabaseError هنگام ساخت Client -> {db_e}")
                # پاک‌سازی فایل کپی‌شده چون ممکنه خراب باشد
                try:
                    if os.path.exists(dst_session_file):
                        os.remove(dst_session_file)
                        logger.debug(f"{phone_number}: deleted possibly-bad session file {dst_session_file}")
                except Exception:
                    pass
                return None

            except Exception as e:
                logger.error(f"{phone_number}: خطا در ایجاد client -> {e}")
                # حذف احتمالی فایل کپی‌شده
                try:
                    if os.path.exists(dst_session_file):
                        os.remove(dst_session_file)
                except Exception:
                    pass
                return None

        except Exception as e:
            logger.error(f"{phone_number}: خطا در سطح بالاتر هنگام ایجاد client -> {e}")
            return None

    def stop(self):
        """توقف اسپمر"""
        self.stop_event.set()
        logger.info("🧩 درخواست توقف اسپمر ارسال شد.")
