"""
Configuration management module for Telegram Auto-Messenger.
Provides configuration loading, validation, and hot-reload functionality.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AccountConfig:
    """Configuration for a single Telegram account."""
    api_id: int
    api_hash: str
    phone: str
    session_name: str
    enabled: bool = True


@dataclass  
class ScheduleConfig:
    """Configuration for scheduled messages."""
    name: str
    target: str  # Channel/group username or ID
    message: str
    interval: int  # Seconds between messages
    enabled: bool = True
    auto_delete: bool = False
    delete_after: int = 60  # Seconds to wait before deletion


@dataclass
class MonitorConfig:
    """Configuration for message monitoring and auto-reply."""
    name: str
    target: str  # Channel/group to monitor
    keywords: List[str]
    reply_message: str
    enabled: bool = True
    exact_match: bool = False


@dataclass
class SafetyConfig:
    """Safety configuration to avoid account bans."""
    min_message_delay: int = 5
    max_messages_per_hour: int = 20
    randomize_delays: bool = True
    max_random_delay: int = 10


@dataclass
class CultivationConfig:
    """Configuration for cultivation bot automation."""
    enabled: bool = False
    account_name: str = "account1"  # Which account to use
    channel: str = "@your_cultivation_channel"  # Channel to send commands to
    command: str = ".闭关修炼"  # Command to send
    auto_start: bool = False  # Start automatically when app starts
    response_timeout: int = 30  # Seconds to wait for bot response
    retry_on_failure: bool = True  # Retry if bot doesn't respond


@dataclass
class AppConfig:
    """Main application configuration."""
    accounts: List[AccountConfig] = field(default_factory=list)
    schedules: List[ScheduleConfig] = field(default_factory=list)
    monitors: List[MonitorConfig] = field(default_factory=list)
    cultivation: CultivationConfig = field(default_factory=CultivationConfig)
    log_enabled: bool = True  # Simple on/off logging control
    log_level: str = "INFO"
    log_to_file: bool = True  # Enable/disable file logging
    log_dir: str = "logs"  # Directory for log files
    hot_reload: bool = True
    hot_reload_interval: int = 30
    safety: SafetyConfig = field(default_factory=SafetyConfig)


class ConfigManager:
    """Manages application configuration with hot-reload support."""
    
    def __init__(self, config_path: str = "config/config.yml"):
        self.config_path = Path(config_path)
        self.config: Optional[AppConfig] = None
        self.logger = logging.getLogger(__name__)
        self._last_modified = 0
        
    def load_config(self) -> AppConfig:
        """Load configuration from YAML file."""
        try:
            if not self.config_path.exists():
                self.logger.warning(f"Config file {self.config_path} not found, creating default")
                self._create_default_config()
                
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            # Parse accounts
            accounts = []
            for acc_data in data.get('accounts', []):
                accounts.append(AccountConfig(**acc_data))
                
            # Parse schedules  
            schedules = []
            for sched_data in data.get('schedules', []):
                schedules.append(ScheduleConfig(**sched_data))
                
            # Parse monitors
            monitors = []
            for mon_data in data.get('monitors', []):
                monitors.append(MonitorConfig(**mon_data))
                
            # Parse cultivation config if present
            cultivation_data = data.get('cultivation', {})
            cultivation_config = CultivationConfig(**cultivation_data)
                
            # Create main config
            app_data = data.get('app', {})
            
            # Parse safety config if present
            safety_data = app_data.get('safety', {})
            safety_config = SafetyConfig(**safety_data)
            
            self.config = AppConfig(
                accounts=accounts,
                schedules=schedules, 
                monitors=monitors,
                cultivation=cultivation_config,
                safety=safety_config,
                **{k: v for k, v in app_data.items() if k != 'safety'}
            )
            
            self._last_modified = self.config_path.stat().st_mtime
            self.logger.info(f"Configuration loaded from {self.config_path}")
            return self.config
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise
            
    def _create_default_config(self):
        """Create a default configuration file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        default_config = {
            'app': {
                'log_enabled': True,
                'log_level': 'INFO',
                'log_to_file': True,
                'log_dir': 'logs',
                'hot_reload': True,
                'hot_reload_interval': 30,
                'safety': {
                    'min_message_delay': 5,
                    'max_messages_per_hour': 20,
                    'randomize_delays': True,
                    'max_random_delay': 10
                }
            },
            'accounts': [
                {
                    'api_id': 0,
                    'api_hash': 'your_api_hash_here',
                    'phone': '+1234567890',
                    'session_name': 'account1',
                    'enabled': False
                }
            ],
            'cultivation': {
                'enabled': False,
                'account_name': 'account1',
                'channel': '@your_cultivation_channel',
                'command': '.闭关修炼',
                'auto_start': False,
                'response_timeout': 30,
                'retry_on_failure': True
            },
            'schedules': [
                {
                    'name': 'example_schedule',
                    'target': '@your_channel',
                    'message': 'Hello from Telegram Auto-Messenger!',
                    'interval': 3600,
                    'enabled': False,
                    'auto_delete': False,
                    'delete_after': 60
                }
            ],
            'monitors': [
                {
                    'name': 'example_monitor',
                    'target': '@your_group',
                    'keywords': ['hello', 'help'],
                    'reply_message': 'Hello! How can I help you?',
                    'enabled': False,
                    'exact_match': False
                }
            ]
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
            
    def should_reload(self) -> bool:
        """Check if configuration file has been modified."""
        if not self.config or not self.config.hot_reload:
            return False
            
        try:
            current_modified = self.config_path.stat().st_mtime
            return current_modified > self._last_modified
        except OSError:
            return False
            
    def reload_if_changed(self) -> bool:
        """Reload configuration if file has changed."""
        if self.should_reload():
            self.logger.info("Configuration file changed, reloading...")
            self.load_config()
            return True
        return False
        
    def get_config(self) -> AppConfig:
        """Get current configuration, loading if necessary."""
        if self.config is None:
            self.load_config()
        return self.config
        
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        config = self.get_config()
        
        # Validate accounts
        if not config.accounts:
            errors.append("No accounts configured")
        else:
            for i, account in enumerate(config.accounts):
                if not account.api_id or account.api_id == 0:
                    errors.append(f"Account {i+1}: Invalid API ID")
                if not account.api_hash or account.api_hash == 'your_api_hash_here':
                    errors.append(f"Account {i+1}: Invalid API hash")
                if not account.phone:
                    errors.append(f"Account {i+1}: Phone number required")
                    
        # Validate schedules
        for i, schedule in enumerate(config.schedules):
            if schedule.enabled:
                if not schedule.target:
                    errors.append(f"Schedule {i+1}: Target required")
                if not schedule.message:
                    errors.append(f"Schedule {i+1}: Message required")
                if schedule.interval < 60:
                    errors.append(f"Schedule {i+1}: Interval must be at least 60 seconds")
                    
        # Validate monitors
        for i, monitor in enumerate(config.monitors):
            if monitor.enabled:
                if not monitor.target:
                    errors.append(f"Monitor {i+1}: Target required")
                if not monitor.keywords:
                    errors.append(f"Monitor {i+1}: Keywords required")
                if not monitor.reply_message:
                    errors.append(f"Monitor {i+1}: Reply message required")
                    
        return errors