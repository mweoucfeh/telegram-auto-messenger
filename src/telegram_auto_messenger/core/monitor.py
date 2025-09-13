"""
Message monitoring module for smart auto-replies.
"""

import asyncio
import re
from typing import Dict, List, Set
from telethon import events
from telethon.tl.types import Message

from ..config import MonitorConfig
from .account import AccountManager, TelegramAccount
from ..utils.logger import get_logger


class MessageMonitor:
    """Monitors messages and provides auto-replies based on keywords."""
    
    def __init__(self, config: MonitorConfig, account_manager: AccountManager):
        self.config = config
        self.account_manager = account_manager
        self.logger = get_logger(f"MessageMonitor.{config.name}")
        self.monitoring_account: Optional[TelegramAccount] = None
        self.is_monitoring = False
        self.processed_messages: Set[int] = set()  # To avoid duplicate processing
        
    async def start_monitoring(self) -> bool:
        """Start monitoring the target chat."""
        try:
            # Get account for monitoring
            self.monitoring_account = await self.account_manager.get_account_for_target(
                self.config.target
            )
            if not self.monitoring_account:
                self.logger.error("No available account for monitoring")
                return False
                
            # Add event handler
            self.monitoring_account.client.add_event_handler(
                self._handle_new_message,
                events.NewMessage(chats=self.config.target)
            )
            
            self.is_monitoring = True
            self.logger.info(f"Started monitoring {self.config.target}")
            return True
            
        except Exception as e:
            self.logger.exception(f"Failed to start monitoring: {e}")
            return False
            
    async def stop_monitoring(self):
        """Stop monitoring the target chat."""
        if self.monitoring_account and self.is_monitoring:
            try:
                # Remove event handler
                self.monitoring_account.client.remove_event_handler(
                    self._handle_new_message
                )
                self.is_monitoring = False
                self.logger.info(f"Stopped monitoring {self.config.target}")
            except Exception as e:
                self.logger.exception(f"Error stopping monitoring: {e}")
                
    async def _handle_new_message(self, event):
        """Handle new message events."""
        try:
            message = event.message
            
            # Skip if we've already processed this message
            if message.id in self.processed_messages:
                return
                
            # Skip messages from ourselves
            if message.out:
                return
                
            # Skip empty messages
            if not message.text:
                return
                
            # Check if message matches keywords
            if self._matches_keywords(message.text):
                await self._send_auto_reply(message)
                
            # Track processed message
            self.processed_messages.add(message.id)
            
            # Clean up old processed messages (keep only last 1000)
            if len(self.processed_messages) > 1000:
                old_messages = list(self.processed_messages)[:500]
                self.processed_messages -= set(old_messages)
                
        except Exception as e:
            self.logger.exception(f"Error handling new message: {e}")
            
    def _matches_keywords(self, text: str) -> bool:
        """Check if message text matches configured keywords."""
        text_lower = text.lower()
        
        for keyword in self.config.keywords:
            keyword_lower = keyword.lower()
            
            if self.config.exact_match:
                # Exact word match
                pattern = r'\b' + re.escape(keyword_lower) + r'\b'
                if re.search(pattern, text_lower):
                    return True
            else:
                # Substring match
                if keyword_lower in text_lower:
                    return True
                    
        return False
        
    async def _send_auto_reply(self, original_message: Message):
        """Send auto-reply to a message."""
        try:
            # Get account for sending reply
            reply_account = await self.account_manager.get_account_for_target(
                self.config.target
            )
            if not reply_account:
                self.logger.error("No available account for sending reply")
                return
                
            # Send reply
            success = await reply_account.send_message(
                self.config.target, 
                self.config.reply_message
            )
            
            if success:
                self.logger.info(
                    f"Auto-reply sent to {self.config.target} "
                    f"(triggered by: {original_message.text[:50]}...)"
                )
            else:
                self.logger.error("Failed to send auto-reply")
                
        except Exception as e:
            self.logger.exception(f"Error sending auto-reply: {e}")


class MonitorManager:
    """Manages multiple message monitors."""
    
    def __init__(self, account_manager: AccountManager):
        self.account_manager = account_manager
        self.monitors: Dict[str, MessageMonitor] = {}
        self.logger = get_logger("MonitorManager")
        
    async def add_monitor(self, config: MonitorConfig) -> bool:
        """Add a new message monitor."""
        if not config.enabled:
            self.logger.info(f"Monitor {config.name} is disabled, skipping")
            return False
            
        if config.name in self.monitors:
            self.logger.warning(f"Monitor {config.name} already exists, updating")
            await self.remove_monitor(config.name)
            
        try:
            monitor = MessageMonitor(config, self.account_manager)
            success = await monitor.start_monitoring()
            
            if success:
                self.monitors[config.name] = monitor
                self.logger.info(f"Monitor {config.name} added successfully")
            else:
                self.logger.error(f"Failed to add monitor {config.name}")
                
            return success
            
        except Exception as e:
            self.logger.exception(f"Failed to add monitor {config.name}: {e}")
            return False
            
    async def remove_monitor(self, name: str):
        """Remove a message monitor."""
        if name in self.monitors:
            monitor = self.monitors[name]
            await monitor.stop_monitoring()
            del self.monitors[name]
            self.logger.info(f"Monitor {name} removed")
            
    async def update_monitors(self, configs: List[MonitorConfig]):
        """Update monitors based on new configuration."""
        # Remove monitors that are no longer in config or disabled
        current_names = set(self.monitors.keys())
        new_names = {cfg.name for cfg in configs if cfg.enabled}
        
        # Remove old monitors
        for name in current_names - new_names:
            await self.remove_monitor(name)
            
        # Add new monitors
        for config in configs:
            if config.enabled:
                await self.add_monitor(config)
                
    async def stop_all_monitors(self):
        """Stop all message monitors."""
        for monitor in self.monitors.values():
            await monitor.stop_monitoring()
        self.monitors.clear()
        self.logger.info("All monitors stopped")
        
    def get_monitor_status(self) -> List[Dict]:
        """Get status of all monitors."""
        status = []
        for name, monitor in self.monitors.items():
            status.append({
                'name': name,
                'target': monitor.config.target,
                'keywords': monitor.config.keywords,
                'reply_message': monitor.config.reply_message,
                'enabled': monitor.config.enabled,
                'exact_match': monitor.config.exact_match,
                'is_monitoring': monitor.is_monitoring,
                'processed_count': len(monitor.processed_messages)
            })
        return status
        
    async def pause_monitor(self, name: str) -> bool:
        """Pause a specific monitor."""
        if name not in self.monitors:
            return False
            
        monitor = self.monitors[name]
        await monitor.stop_monitoring()
        self.logger.info(f"Monitor {name} paused")
        return True
        
    async def resume_monitor(self, name: str) -> bool:
        """Resume a specific monitor."""
        if name not in self.monitors:
            return False
            
        monitor = self.monitors[name]
        success = await monitor.start_monitoring()
        if success:
            self.logger.info(f"Monitor {name} resumed")
        return success