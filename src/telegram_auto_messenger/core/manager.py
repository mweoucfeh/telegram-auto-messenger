"""
Main manager class for the Telegram Auto-Messenger application.
"""

import asyncio
import signal
from pathlib import Path
from typing import Optional

from ..config import ConfigManager, AppConfig
from .account import AccountManager
from .scheduler import MessageScheduler
from .monitor import MonitorManager
from ..utils.logger import setup_logging, get_logger


class TelegramManager:
    """Main manager class for the Telegram Auto-Messenger."""
    
    def __init__(self, config_path: str = "config/config.yml"):
        self.config_manager = ConfigManager(config_path)
        self.account_manager = AccountManager()
        self.message_scheduler = MessageScheduler(self.account_manager)
        self.monitor_manager = MonitorManager(self.account_manager)
        
        self.logger = get_logger("TelegramManager")
        self._running = False
        self._hot_reload_task: Optional[asyncio.Task] = None
        
    async def initialize(self) -> bool:
        """Initialize the application."""
        try:
            # Load configuration
            config = self.config_manager.load_config()
            
            # Setup logging
            setup_logging(config.log_enabled, config.log_level, config.log_to_file, config.log_dir)
            self.logger.info("Telegram Auto-Messenger initializing...")
            
            # Validate configuration
            errors = self.config_manager.validate_config()
            if errors:
                self.logger.error("Configuration validation failed:")
                for error in errors:
                    self.logger.error(f"  - {error}")
                return False
                
            # Initialize accounts
            await self._update_accounts(config)
            
            # Initialize scheduler and monitors
            await self._update_schedules(config)
            await self._update_monitors(config)
            
            self.logger.info("Telegram Auto-Messenger initialized successfully")
            return True
            
        except Exception as e:
            self.logger.exception(f"Failed to initialize: {e}")
            return False
            
    async def start(self):
        """Start the application."""
        if self._running:
            self.logger.warning("Application is already running")
            return
            
        self._running = True
        self.logger.info("Starting Telegram Auto-Messenger...")
        
        try:
            # Start scheduler
            await self.message_scheduler.start()
            
            # Start hot reload if enabled
            config = self.config_manager.get_config()
            if config.hot_reload:
                self._hot_reload_task = asyncio.create_task(self._hot_reload_loop(config))
                
            # Setup signal handlers
            self._setup_signal_handlers()
            
            self.logger.info("Telegram Auto-Messenger started successfully")
            
            # Keep running
            while self._running:
                await asyncio.sleep(1)
                
        except Exception as e:
            self.logger.exception(f"Error during execution: {e}")
        finally:
            await self.stop()
            
    async def stop(self):
        """Stop the application."""
        if not self._running:
            return
            
        self.logger.info("Stopping Telegram Auto-Messenger...")
        self._running = False
        
        try:
            # Cancel hot reload task
            if self._hot_reload_task:
                self._hot_reload_task.cancel()
                try:
                    await self._hot_reload_task
                except asyncio.CancelledError:
                    pass
                    
            # Stop monitors
            await self.monitor_manager.stop_all_monitors()
            
            # Stop scheduler
            await self.message_scheduler.stop()
            
            # Disconnect accounts
            await self.account_manager.disconnect_all()
                
            self.logger.info("Telegram Auto-Messenger stopped")
            
        except Exception as e:
            self.logger.exception(f"Error during shutdown: {e}")
            
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down...")
            self._running = False
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    async def _hot_reload_loop(self, config: AppConfig):
        """Hot reload configuration changes."""
        while self._running:
            try:
                await asyncio.sleep(config.hot_reload_interval)
                
                if self.config_manager.reload_if_changed():
                    self.logger.info("Configuration reloaded, updating components...")
                    new_config = self.config_manager.get_config()
                    
                    # Update logging if changed
                    setup_logging(new_config.log_enabled, new_config.log_level, new_config.log_to_file, new_config.log_dir)
                    
                    # Update components
                    await self._update_accounts(new_config)
                    await self._update_schedules(new_config)
                    await self._update_monitors(new_config)
                    
                    # Update hot reload interval if changed
                    config.hot_reload_interval = new_config.hot_reload_interval
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.exception(f"Error in hot reload loop: {e}")
                
    async def _update_accounts(self, config: AppConfig):
        """Update accounts based on configuration."""
        try:
            # Set safety config for account manager
            self.account_manager.set_safety_config(config.safety)
            
            await self.account_manager.update_accounts(config.accounts)
        except Exception as e:
            self.logger.exception(f"Failed to update accounts: {e}")
            
    async def _update_schedules(self, config: AppConfig):
        """Update schedules based on configuration."""
        try:
            self.message_scheduler.update_schedules(config.schedules)
        except Exception as e:
            self.logger.exception(f"Failed to update schedules: {e}")
            
    async def _update_monitors(self, config: AppConfig):
        """Update monitors based on configuration."""
        try:
            await self.monitor_manager.update_monitors(config.monitors)
        except Exception as e:
            self.logger.exception(f"Failed to update monitors: {e}")
            
    def get_status(self) -> dict:
        """Get overall application status."""
        config = self.config_manager.get_config()
        
        # Get connected accounts
        connected_accounts = self.account_manager.get_connected_accounts()
        
        return {
            'running': self._running,
            'config_path': str(self.config_manager.config_path),
            'hot_reload_enabled': config.hot_reload,
            'logging_enabled': config.log_enabled,
            'accounts': {
                'total_configured': len(config.accounts),
                'connected': len(connected_accounts),
                'account_names': [acc.config.session_name for acc in connected_accounts]
            },
            'scheduler': self.message_scheduler.get_scheduler_status(),
            'schedules': self.message_scheduler.get_schedule_status(),
            'monitors': self.monitor_manager.get_monitor_status()
        }
        
    async def send_test_message(self, target: str, message: str) -> bool:
        """Send a test message."""
        return await self.account_manager.send_message_any(target, message)
        
    async def execute_schedule_now(self, schedule_name: str) -> bool:
        """Execute a specific schedule immediately."""
        return await self.message_scheduler.send_now(schedule_name)
        
    def pause_schedule(self, schedule_name: str) -> bool:
        """Pause a specific schedule."""
        return self.message_scheduler.pause_schedule(schedule_name)
        
    def resume_schedule(self, schedule_name: str) -> bool:
        """Resume a specific schedule."""
        return self.message_scheduler.resume_schedule(schedule_name)
        
    async def pause_monitor(self, monitor_name: str) -> bool:
        """Pause a specific monitor."""
        return await self.monitor_manager.pause_monitor(monitor_name)
        
    async def resume_monitor(self, monitor_name: str) -> bool:
        """Resume a specific monitor."""
        return await self.monitor_manager.resume_monitor(monitor_name)