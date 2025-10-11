# antispam_core/analytics_manager.py
import json, os, logging
from datetime import datetime
from . import admin_manager

logger = logging.getLogger(__name__)
STATS_FILE = "analytics_stats.json"

class Analytics:
    def __init__(self):
        self.stats = {
            "total_sent": 0,
            "successful": 0,
            "failed": 0,
            "account_performance": {},
            "hourly_activity": {h: 0 for h in range(24)},
        }
        self.load()

    # --------------------------
    # ذخیره و بارگذاری داده‌ها
    # --------------------------
    def save(self):
        try:
            with open(STATS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving stats: {e}")

    def load(self):
        try:
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.stats.update(data)
                        logger.info("📈 Analytics data loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading stats: {e}")

    # --------------------------
    # بروزرسانی آمارها
    # --------------------------
    async def update_stats(self, account: str, success: bool, chat_id: int = None):
        try:
            self.stats["total_sent"] += 1
            if success:
                self.stats["successful"] += 1
            else:
                self.stats["failed"] += 1

            hour = datetime.now().hour
            self.stats["hourly_activity"][hour] += 1

            if account not in self.stats["account_performance"]:
                self.stats["account_performance"][account] = {"success": 0, "total": 0}

            self.stats["account_performance"][account]["total"] += 1
            if success:
                self.stats["account_performance"][account]["success"] += 1

            # ذخیره خودکار پس از هر بروزرسانی
            self.save()
        except Exception as e:
            logger.error(f"Error in update_stats: {e}")


analytics = Analytics()

# --------------------------
# دستور /stats
# --------------------------
async def show_stats_cmd(message):
    try:
        stats = analytics.stats
        total = stats["total_sent"]
        success_rate = stats["successful"] / total * 100 if total > 0 else 0

        report_msg = (
            "📊 <b>آمار کلی ارسال‌ها:</b>\n"
            f"🔹 کل ارسال‌ها: {stats['total_sent']}\n"
            f"✅ موفق: {stats['successful']}\n"
            f"❌ ناموفق: {stats['failed']}\n"
            f"📈 نرخ موفقیت: {success_rate:.2f}%\n\n"
        )

        # نمایش آمار بر اساس حساب‌ها
        if stats["account_performance"]:
            report_msg += "<b>📋 عملکرد هر اکانت:</b>\n"
            for acc, data in stats["account_performance"].items():
                total_acc = data["total"]
                rate = (data["success"] / total_acc * 100) if total_acc else 0
                report_msg += f"• {acc}: {rate:.1f}% ({data['success']}/{total_acc})\n"

        await message.reply(report_msg)
    except Exception as e:
        logger.error(f"Error showing stats: {e}")
        await message.reply(f"خطا در نمایش آمار: {e}")
