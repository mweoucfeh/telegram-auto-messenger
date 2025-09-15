"""
Cultivation bot automation module for handling specific cultivation channel interactions.
Handles automatic .闭关修炼 commands with intelligent response parsing.
"""

import asyncio
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from telethon import events

from ..config import AccountConfig
from ..utils.logger import get_logger


class CultivationSession:
    """Represents a cultivation session for a specific account and channel."""
    
    def __init__(self, account_name: str, channel: str, command: str = ".闭关修炼"):
        self.account_name = account_name
        self.channel = channel
        self.command = command
        self.is_active = False
        self.last_attempt = None
        self.next_attempt = None
        self.wait_time_seconds = 0
        self.success_count = 0
        self.failure_count = 0
        self.logger = get_logger(f"CultivationSession.{account_name}")
        
    def parse_response(self, message_text: str) -> Optional[int]:
        """
        Parse bot response to extract wait time in seconds.
        
        Handles responses like:
        - "你感到一阵疲惫，需要打坐调息 13 分钟方可再次闭关。"
        - "灵气尚未平复，无法立即再次闭关。请在 11分钟36秒 后再试。"
        - "【闭关成功】..." (can also have wait times)
        
        Returns:
            int: Wait time in seconds, or None if unrecognized
        """
        try:
            # Check if this is a successful cultivation
            is_success = "【闭关成功】" in message_text or "修为增加了" in message_text
            
            # Pattern for wait time with minutes and seconds: "11分钟36秒"
            time_pattern = r'(\d+)分钟(\d+)秒'
            time_match = re.search(time_pattern, message_text)
            
            # Pattern for wait time in minutes only: "13 分钟"
            minute_pattern = r'(\d+)\s*分钟'
            minute_match = re.search(minute_pattern, message_text)
            
            wait_seconds = 0
            
            if time_match:
                minutes = int(time_match.group(1))
                seconds = int(time_match.group(2))
                wait_seconds = minutes * 60 + seconds
                self.logger.info(f"Parsed wait time: {minutes}m {seconds}s = {wait_seconds}s")
            elif minute_match:
                minutes = int(minute_match.group(1))
                wait_seconds = minutes * 60
                self.logger.info(f"Parsed wait time: {minutes}m = {wait_seconds}s")
            else:
                # No wait time found
                if is_success:
                    self.logger.info("Cultivation successful! No wait needed.")
                    self.success_count += 1
                    return 0
                else:
                    self.logger.warning(f"Could not parse wait time from: {message_text[:100]}...")
                    self.failure_count += 1
                    return None
            
            # If we found a wait time, determine if it's success or failure
            if is_success:
                self.success_count += 1
                self.logger.info(f"Cultivation successful! Wait time: {wait_seconds}s")
            else:
                self.failure_count += 1
                self.logger.info(f"Cultivation failed. Wait time: {wait_seconds}s")
                
            return wait_seconds
            
        except Exception as e:
            self.logger.exception(f"Error parsing response: {e}")
            return None
    
    def schedule_next_attempt(self, wait_seconds: int):
        """Schedule the next cultivation attempt."""
        if wait_seconds <= 0:
            # Success or immediate retry
            self.next_attempt = datetime.now() + timedelta(seconds=5)  # Small delay
        else:
            # Add a small random delay to avoid exact timing
            extra_delay = 10 + (wait_seconds * 0.1)  # 10s + 10% of wait time
            total_wait = wait_seconds + extra_delay
            self.next_attempt = datetime.now() + timedelta(seconds=total_wait)
            
        self.wait_time_seconds = wait_seconds
        self.logger.info(f"Next cultivation attempt scheduled for: {self.next_attempt}")
    
    def is_ready(self) -> bool:
        """Check if it's time for the next cultivation attempt."""
        if not self.next_attempt:
            return True
        return datetime.now() >= self.next_attempt
    
    def get_status(self) -> dict:
        """Get current session status."""
        return {
            'account': self.account_name,
            'channel': self.channel,
            'command': self.command,
            'is_active': self.is_active,
            'last_attempt': self.last_attempt,
            'next_attempt': self.next_attempt,
            'wait_time_seconds': self.wait_time_seconds,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'is_ready': self.is_ready()
        }


class CultivationManager:
    """Manages multiple cultivation sessions across accounts."""
    
    def __init__(self, account_manager):
        self.account_manager = account_manager
        self.sessions: Dict[str, CultivationSession] = {}
        self.logger = get_logger("CultivationManager")
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
        
    def add_session(self, account_name: str, channel: str, command: str = ".闭关修炼") -> bool:
        """Add a new cultivation session."""
        session_key = f"{account_name}:{channel}"
        
        if session_key in self.sessions:
            self.logger.warning(f"Session {session_key} already exists")
            return False
            
        session = CultivationSession(account_name, channel, command)
        self.sessions[session_key] = session
        self.logger.info(f"Added cultivation session: {session_key}")
        return True
    
    def remove_session(self, account_name: str, channel: str) -> bool:
        """Remove a cultivation session."""
        session_key = f"{account_name}:{channel}"
        
        if session_key in self.sessions:
            session = self.sessions[session_key]
            session.is_active = False
            del self.sessions[session_key]
            self.logger.info(f"Removed cultivation session: {session_key}")
            return True
        return False
    
    async def start_session(self, account_name: str, channel: str) -> bool:
        """Start a specific cultivation session."""
        session_key = f"{account_name}:{channel}"
        session = self.sessions.get(session_key)
        
        if not session:
            self.logger.error(f"Session {session_key} not found")
            return False
            
        account = self.account_manager.get_account(account_name)
        if not account or not account.is_connected:
            self.logger.error(f"Account {account_name} not connected")
            return False
        
        # Setup message handler for this session
        await self._setup_message_handler(account, session)
        
        session.is_active = True
        self.logger.info(f"Started cultivation session: {session_key}")
        return True
    
    async def stop_session(self, account_name: str, channel: str) -> bool:
        """Stop a specific cultivation session."""
        session_key = f"{account_name}:{channel}"
        session = self.sessions.get(session_key)
        
        if session:
            session.is_active = False
            self.logger.info(f"Stopped cultivation session: {session_key}")
            return True
        return False
    
    async def _setup_message_handler(self, account, session):
        """Setup message handler to monitor bot responses."""
        
        @account.client.on(events.NewMessage(chats=session.channel))
        async def handle_cultivation_response(event):
            if not session.is_active:
                return
                
            # Check if this is a response from the cultivation bot
            # Look for bot indicators in the message or sender
            sender = event.sender
            message_text = event.message.message
            
            # Check if this looks like a cultivation bot response
            is_bot_response = (
                "勤奋的灵魂" in getattr(sender, 'first_name', '') or
                "勤奋的灵魂" in getattr(sender, 'username', '') or
                any(keyword in message_text for keyword in [
                    "【闭关成功】", "闭关", "修为增加", "灵气尚未平复", 
                    "打坐调息", "分钟", "后再试"
                ])
            )
            
            if is_bot_response:
                self.logger.info(f"Received cultivation bot response: {message_text[:100]}...")
                wait_seconds = session.parse_response(message_text)
                
                if wait_seconds is not None:
                    session.schedule_next_attempt(wait_seconds)
    
    async def start_monitoring(self):
        """Start the cultivation monitoring loop."""
        if self._running:
            return
            
        self._running = True
        self.logger.info("Starting cultivation monitoring...")
        
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self):
        """Stop cultivation monitoring."""
        self._running = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
                
        # Deactivate all sessions
        for session in self.sessions.values():
            session.is_active = False
            
        self.logger.info("Stopped cultivation monitoring")
    
    async def _monitoring_loop(self):
        """Main monitoring loop for cultivation sessions."""
        while self._running:
            try:
                await asyncio.sleep(1)  # Check every second
                
                for session in list(self.sessions.values()):
                    if session.is_active and session.is_ready():
                        await self._attempt_cultivation(session)
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.exception(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _attempt_cultivation(self, session: CultivationSession):
        """Attempt cultivation for a session."""
        try:
            account = self.account_manager.get_account(session.account_name)
            if not account or not account.is_connected:
                self.logger.error(f"Account {session.account_name} not available")
                session.is_active = False
                return
            
            self.logger.info(f"Attempting cultivation: {session.account_name} -> {session.channel}")
            
            # Send cultivation command
            success = await account.send_message(session.channel, session.command)
            
            if success:
                session.last_attempt = datetime.now()
                # Schedule next attempt in case bot doesn't respond
                session.schedule_next_attempt(30)  # Default 30s wait
            else:
                self.logger.error(f"Failed to send cultivation command")
                # Retry in 60 seconds
                session.schedule_next_attempt(60)
                
        except Exception as e:
            self.logger.exception(f"Error during cultivation attempt: {e}")
            session.schedule_next_attempt(60)  # Retry in 1 minute
    
    def get_status(self) -> dict:
        """Get status of all cultivation sessions."""
        return {
            'running': self._running,
            'total_sessions': len(self.sessions),
            'active_sessions': sum(1 for s in self.sessions.values() if s.is_active),
            'sessions': [s.get_status() for s in self.sessions.values()]
        }
    
    async def execute_immediate(self, account_name: str, channel: str, command: str = ".闭关修炼") -> bool:
        """Execute cultivation command immediately without scheduling."""
        account = self.account_manager.get_account(account_name)
        if not account or not account.is_connected:
            self.logger.error(f"Account {account_name} not available")
            return False
        
        self.logger.info(f"Immediate cultivation: {account_name} -> {channel}")
        return await account.send_message(channel, command)