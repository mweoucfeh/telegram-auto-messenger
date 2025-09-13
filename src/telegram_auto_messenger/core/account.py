"""
Account management module for handling multiple Telegram accounts.
"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from telethon.sessions import StringSession

from ..config import AccountConfig, SafetyConfig
from ..utils.logger import get_logger


class TelegramAccount:
    """Represents a single Telegram account connection."""
    
    def __init__(self, config: AccountConfig, safety_config: SafetyConfig):
        self.config = config
        self.safety_config = safety_config
        self.client: Optional[TelegramClient] = None
        self.logger = get_logger(f"TelegramAccount.{config.session_name}")
        self.is_connected = False
        
        # Rate limiting tracking
        self.message_timestamps: List[datetime] = []
        self.last_message_time = 0.0
        
    async def connect(self) -> bool:
        """Connect to Telegram account."""
        try:
            # Create client with session file
            session_path = f"sessions/{self.config.session_name}.session"
            self.client = TelegramClient(
                session_path,
                self.config.api_id,
                self.config.api_hash
            )
            
            await self.client.connect()
            
            # Check if already authorized
            if not await self.client.is_user_authorized():
                await self._authorize()
                
            self.is_connected = True
            me = await self.client.get_me()
            self.logger.info(f"Connected as {me.first_name} ({me.phone})")
            return True
            
        except Exception as e:
            self.logger.exception(f"Failed to connect: {e}")
            self.is_connected = False
            return False
            
    async def _authorize(self):
        """Handle authorization flow."""
        try:
            # Send code request
            await self.client.send_code_request(self.config.phone)
            self.logger.info(f"Code sent to {self.config.phone}")
            
            # In a real implementation, you'd need to get this from user input
            # For now, we'll raise an exception to indicate manual intervention needed
            raise RuntimeError(
                f"Authorization required for {self.config.phone}. "
                "Please run the authorization process manually."
            )
            
        except SessionPasswordNeededError:
            # 2FA is enabled
            raise RuntimeError(
                f"2FA enabled for {self.config.phone}. "
                "Please run the authorization process manually."
            )
            
    async def disconnect(self):
        """Disconnect from Telegram."""
        if self.client and self.is_connected:
            await self.client.disconnect()
            self.is_connected = False
            self.logger.info("Disconnected")
            
    async def send_message(self, target: str, message: str) -> bool:
        """Send a message to target chat with safety measures."""
        if not self.is_connected or not self.client:
            self.logger.error("Account not connected")
            return False
        
        # Check rate limiting
        if not self._check_rate_limit():
            self.logger.warning("Rate limit exceeded, message not sent")
            return False
            
        # Apply safety delays
        await self._apply_safety_delay()
        
        try:
            await self.client.send_message(target, message)
            self.logger.info(f"Message sent to {target}")
            
            # Update tracking
            self._update_rate_tracking()
            return True
        except Exception as e:
            self.logger.exception(f"Failed to send message to {target}: {e}")
            return False
    
    def _check_rate_limit(self) -> bool:
        """Check if sending a message would exceed rate limits."""
        now = datetime.now()
        
        # Clean old timestamps (older than 1 hour)
        cutoff = now - timedelta(hours=1)
        self.message_timestamps = [ts for ts in self.message_timestamps if ts > cutoff]
        
        # Check if we're under the hourly limit
        return len(self.message_timestamps) < self.safety_config.max_messages_per_hour
    
    async def _apply_safety_delay(self):
        """Apply safety delays to avoid looking like a bot."""
        now = time.time()
        
        # Calculate minimum delay since last message
        time_since_last = now - self.last_message_time
        min_delay = self.safety_config.min_message_delay
        
        if time_since_last < min_delay:
            delay = min_delay - time_since_last
            
            # Add randomization if enabled
            if self.safety_config.randomize_delays:
                extra_delay = random.uniform(0, self.safety_config.max_random_delay)
                delay += extra_delay
                
            self.logger.debug(f"Applying safety delay: {delay:.2f}s")
            await asyncio.sleep(delay)
    
    def _update_rate_tracking(self):
        """Update rate limiting tracking after sending a message."""
        now = datetime.now()
        self.message_timestamps.append(now)
        self.last_message_time = time.time()
            
    async def delete_message(self, target: str, message_id: int) -> bool:
        """Delete a message."""
        if not self.is_connected or not self.client:
            return False
            
        try:
            await self.client.delete_messages(target, message_id)
            self.logger.info(f"Message {message_id} deleted from {target}")
            return True
        except Exception as e:
            self.logger.exception(f"Failed to delete message {message_id}: {e}")
            return False


class AccountManager:
    """Manages multiple Telegram accounts."""
    
    def __init__(self):
        self.accounts: Dict[str, TelegramAccount] = {}
        self.logger = get_logger("AccountManager")
        self.safety_config: Optional[SafetyConfig] = None
        
    def set_safety_config(self, safety_config: SafetyConfig):
        """Set safety configuration for all accounts."""
        self.safety_config = safety_config
        # Update existing accounts
        for account in self.accounts.values():
            account.safety_config = safety_config
        
    async def add_account(self, config: AccountConfig) -> bool:
        """Add and connect a new account."""
        if not config.enabled:
            self.logger.info(f"Account {config.session_name} is disabled, skipping")
            return False
            
        if config.session_name in self.accounts:
            self.logger.warning(f"Account {config.session_name} already exists")
            return False
        
        # Use default safety config if none set
        safety_config = self.safety_config or SafetyConfig()
        account = TelegramAccount(config, safety_config)
        success = await account.connect()
        
        if success:
            self.accounts[config.session_name] = account
            self.logger.info(f"Account {config.session_name} added successfully")
        else:
            self.logger.error(f"Failed to add account {config.session_name}")
            
        return success
        
    async def remove_account(self, session_name: str):
        """Remove an account."""
        if session_name in self.accounts:
            await self.accounts[session_name].disconnect()
            del self.accounts[session_name]
            self.logger.info(f"Account {session_name} removed")
            
    async def update_accounts(self, configs: List[AccountConfig]):
        """Update accounts based on new configuration."""
        # Remove accounts that are no longer in config or disabled
        current_names = set(self.accounts.keys())
        new_names = {cfg.session_name for cfg in configs if cfg.enabled}
        
        # Remove old accounts
        for name in current_names - new_names:
            await self.remove_account(name)
            
        # Add new accounts
        for config in configs:
            if config.enabled and config.session_name not in self.accounts:
                await self.add_account(config)
                
    async def disconnect_all(self):
        """Disconnect all accounts."""
        for account in self.accounts.values():
            await account.disconnect()
        self.accounts.clear()
        self.logger.info("All accounts disconnected")
        
    def get_account(self, session_name: str) -> Optional[TelegramAccount]:
        """Get account by session name."""
        return self.accounts.get(session_name)
        
    def get_connected_accounts(self) -> List[TelegramAccount]:
        """Get list of connected accounts."""
        return [acc for acc in self.accounts.values() if acc.is_connected]
        
    async def send_message_any(self, target: str, message: str) -> bool:
        """Send message using any available account."""
        connected = self.get_connected_accounts()
        if not connected:
            self.logger.error("No connected accounts available")
            return False
            
        # Try first available account
        return await connected[0].send_message(target, message)
        
    async def get_account_for_target(self, target: str) -> Optional[TelegramAccount]:
        """Get the best account for a specific target."""
        # For now, just return first connected account
        # In a more sophisticated implementation, you could:
        # - Check which accounts have access to the target
        # - Load balance between accounts
        # - Remember which account was used for which target
        connected = self.get_connected_accounts()
        return connected[0] if connected else None