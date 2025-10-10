# antispam_core/help_menu.py
from pyrogram import filters
from . import admin_manager

HELP_TEXT = """
**📱 Accounts**
Manage linked accounts securely.
- Add account → `add +989127682443`
- Enter verification code → `code 09080`
- Set password → `pass YOURPASSWORD`
- Delete account → `del +989127682443`
- Delete all accounts → `delall`
- List accounts → `listacc`
- Clean pv/gp/channel/bots → `delallpvgpchenl`
- Send all sessions → `givesessions`
- Send all data sessions → `givedatasessions`
- Terminate all other sessions → `delalldevices`

**💬 Messaging**
Send and manage automated messages.
- Start messaging loop → `spam LINK`
- Stop messaging loop → `stop`
- Set delay (seconds) → `speed 5`
- Add message text → `text YOUR TEXT`
- Clear all texts → `ctext`
- Show texts → `shtext`
- Add caption → `cap YOUR CAPTION`
- Clear caption → `ccap`
- Show caption → `shcap`
- Set group size for spam → `set 5`
- Show stats → `stats`
- Set mention → `setmenshen TEXT USERID`
- Remove mention → `remenshen`

**👥 Groups & Profile**
Join or leave groups and manage profile details.
- Join by link → `join LINK`
- Leave chat → `left CHAT_ID`
- Set profile photo (reply to photo) → `setPic`
- Set display name → `name NAME`
- Set bio → `bio BIO`
- Set Username → `username USERNAME`
- Clean Username → `remusername`
- Remove all profile photos → `delallprofile`
- Change profile photos privacy → `profilesettings 1|2|3`
- Block user → `block @USERNAME | reply | USERID`
- Unblock user → `unblock @USERNAME | reply | USERID`

**🛡 Admins**
Manage admin access.
- Add admin → `addadmin USER_ID`
- Remove admin → `deladmin USER_ID`
- List admins → `admins`
"""

async def start_handler_cmd(message):
    """نمایش منوی راهنما (start command)"""
    await message.reply(HELP_TEXT)
