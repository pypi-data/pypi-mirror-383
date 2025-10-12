import random
import logging
from typing import Optional
from .client_manager import client_pool, get_active_accounts, get_or_start_client

logger = logging.getLogger(__name__)

async def get_any_client(message=None) -> Optional[object]:
    """
    یک کلاینت آماده برمی‌گرداند:
      1) اگر کلاینت متصل در pool هست، همان را برمی‌گرداند.
      2) وگرنه از بین active_accounts یکی را استارت می‌کند.
    """
    # Use any connected client
    for phone, cli in list(client_pool.items()):
        try:
            if getattr(cli, "is_connected", False):
                logger.debug("get_any_client: using connected client %s", phone)
                return cli
        except Exception:
            pass

    # Start one if needed
    accs = list(get_active_accounts())
    if not accs:
        logger.warning("get_any_client: no active accounts")
        return None

    random.shuffle(accs)
    for phone in accs:
        try:
            cli = await get_or_start_client(phone)
            if cli and getattr(cli, "is_connected", False):
                logger.info("get_any_client: started %s", phone)
                return cli
        except Exception as e:
            logger.warning("get_any_client: failed start %s: %s: %s", phone, type(e).__name__, e)

    logger.error("get_any_client: could not get any client")
    return None