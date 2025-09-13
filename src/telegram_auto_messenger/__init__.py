# Package initialization
__version__ = "1.0.0"
__author__ = "telegram-auto-messenger"
__email__ = "admin@example.com"
__description__ = "A comprehensive Telegram auto-messenger with multi-account support"

from .core.manager import TelegramManager
from .core.scheduler import MessageScheduler
from .core.monitor import MessageMonitor
from .core.account import AccountManager

__all__ = [
    "TelegramManager",
    "MessageScheduler", 
    "MessageMonitor",
    "AccountManager",
]