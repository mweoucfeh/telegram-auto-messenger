"""
Message scheduling module for automated message sending.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from ..config import ScheduleConfig
from .account import AccountManager
from ..utils.logger import get_logger


class ScheduledMessage:
    """Represents a scheduled message job."""
    
    def __init__(self, config: ScheduleConfig, account_manager: AccountManager):
        self.config = config
        self.account_manager = account_manager
        self.logger = get_logger(f"ScheduledMessage.{config.name}")
        self.job_id = f"schedule_{config.name}"
        self.last_message_id: Optional[int] = None
        self.last_sent_time: Optional[datetime] = None
        
    async def send_message(self):
        """Send the scheduled message."""
        try:
            # Get account for sending
            account = await self.account_manager.get_account_for_target(self.config.target)
            if not account:
                self.logger.error("No available account for sending message")
                return
                
            # Send message
            success = await account.send_message(self.config.target, self.config.message)
            if success:
                self.last_sent_time = datetime.now()
                self.logger.info(f"Scheduled message sent to {self.config.target}")
                
                # Schedule deletion if auto_delete is enabled
                if self.config.auto_delete and self.config.delete_after > 0:
                    asyncio.create_task(self._schedule_deletion(account))
            else:
                self.logger.error(f"Failed to send scheduled message to {self.config.target}")
                
        except Exception as e:
            self.logger.exception(f"Error sending scheduled message: {e}")
            
    async def _schedule_deletion(self, account):
        """Schedule message deletion after specified time."""
        try:
            await asyncio.sleep(self.config.delete_after)
            if self.last_message_id:
                await account.delete_message(self.config.target, self.last_message_id)
                self.logger.info(f"Scheduled message deleted after {self.config.delete_after}s")
        except Exception as e:
            self.logger.exception(f"Error deleting scheduled message: {e}")


class MessageScheduler:
    """Manages scheduled message sending."""
    
    def __init__(self, account_manager: AccountManager):
        self.account_manager = account_manager
        self.scheduler = AsyncIOScheduler()
        self.scheduled_messages: Dict[str, ScheduledMessage] = {}
        self.logger = get_logger("MessageScheduler")
        self._running = False
        
    async def start(self):
        """Start the scheduler."""
        if not self._running:
            self.scheduler.start()
            self._running = True
            self.logger.info("Message scheduler started")
            
    async def stop(self):
        """Stop the scheduler."""
        if self._running:
            self.scheduler.shutdown()
            self._running = False
            self.logger.info("Message scheduler stopped")
            
    def add_schedule(self, config: ScheduleConfig) -> bool:
        """Add a new scheduled message."""
        if not config.enabled:
            self.logger.info(f"Schedule {config.name} is disabled, skipping")
            return False
            
        if config.name in self.scheduled_messages:
            self.logger.warning(f"Schedule {config.name} already exists, updating")
            self.remove_schedule(config.name)
            
        try:
            # Create scheduled message
            scheduled_msg = ScheduledMessage(config, self.account_manager)
            
            # Add job to scheduler
            trigger = IntervalTrigger(seconds=config.interval)
            self.scheduler.add_job(
                scheduled_msg.send_message,
                trigger=trigger,
                id=scheduled_msg.job_id,
                name=f"Schedule: {config.name}",
                replace_existing=True
            )
            
            self.scheduled_messages[config.name] = scheduled_msg
            self.logger.info(f"Schedule {config.name} added (interval: {config.interval}s)")
            return True
            
        except Exception as e:
            self.logger.exception(f"Failed to add schedule {config.name}: {e}")
            return False
            
    def remove_schedule(self, name: str):
        """Remove a scheduled message."""
        if name in self.scheduled_messages:
            scheduled_msg = self.scheduled_messages[name]
            
            # Remove job from scheduler
            try:
                self.scheduler.remove_job(scheduled_msg.job_id)
            except Exception:
                pass  # Job might not exist
                
            del self.scheduled_messages[name]
            self.logger.info(f"Schedule {name} removed")
            
    def update_schedules(self, configs: List[ScheduleConfig]):
        """Update schedules based on new configuration."""
        # Remove schedules that are no longer in config or disabled
        current_names = set(self.scheduled_messages.keys())
        new_names = {cfg.name for cfg in configs if cfg.enabled}
        
        # Remove old schedules
        for name in current_names - new_names:
            self.remove_schedule(name)
            
        # Add/update schedules
        for config in configs:
            if config.enabled:
                self.add_schedule(config)
                
    def get_schedule_status(self) -> List[Dict]:
        """Get status of all schedules."""
        status = []
        for name, scheduled_msg in self.scheduled_messages.items():
            job = self.scheduler.get_job(scheduled_msg.job_id)
            status.append({
                'name': name,
                'target': scheduled_msg.config.target,
                'interval': scheduled_msg.config.interval,
                'enabled': scheduled_msg.config.enabled,
                'next_run': job.next_run_time if job else None,
                'last_sent': scheduled_msg.last_sent_time,
                'auto_delete': scheduled_msg.config.auto_delete,
                'delete_after': scheduled_msg.config.delete_after
            })
        return status
        
    def pause_schedule(self, name: str) -> bool:
        """Pause a specific schedule."""
        if name not in self.scheduled_messages:
            return False
            
        scheduled_msg = self.scheduled_messages[name]
        try:
            self.scheduler.pause_job(scheduled_msg.job_id)
            self.logger.info(f"Schedule {name} paused")
            return True
        except Exception as e:
            self.logger.exception(f"Failed to pause schedule {name}: {e}")
            return False
            
    def resume_schedule(self, name: str) -> bool:
        """Resume a specific schedule."""
        if name not in self.scheduled_messages:
            return False
            
        scheduled_msg = self.scheduled_messages[name]
        try:
            self.scheduler.resume_job(scheduled_msg.job_id)
            self.logger.info(f"Schedule {name} resumed")
            return True
        except Exception as e:
            self.logger.exception(f"Failed to resume schedule {name}: {e}")
            return False
            
    async def send_now(self, name: str) -> bool:
        """Send a scheduled message immediately."""
        if name not in self.scheduled_messages:
            self.logger.error(f"Schedule {name} not found")
            return False
            
        scheduled_msg = self.scheduled_messages[name]
        await scheduled_msg.send_message()
        return True
        
    def get_scheduler_status(self) -> Dict:
        """Get overall scheduler status."""
        return {
            'running': self._running,
            'total_jobs': len(self.scheduler.get_jobs()),
            'active_schedules': len(self.scheduled_messages),
            'uptime': getattr(self.scheduler, 'start_time', None)
        }