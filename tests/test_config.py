"""
Test configuration management.
"""

import pytest
import tempfile
import yaml
from pathlib import Path

from telegram_auto_messenger.config import ConfigManager, AccountConfig, ScheduleConfig, MonitorConfig


def test_config_manager_create_default():
    """Test creating default configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yml"
        manager = ConfigManager(str(config_path))
        
        # Create default config
        manager._create_default_config()
        
        # Check file exists
        assert config_path.exists()
        
        # Load and verify structure
        with open(config_path) as f:
            data = yaml.safe_load(f)
            
        assert 'app' in data
        assert 'accounts' in data
        assert 'schedules' in data
        assert 'monitors' in data


def test_config_manager_load():
    """Test loading configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yml"
        
        # Create test config
        test_config = {
            'app': {
                'log_enabled': True,
                'log_level': 'DEBUG',
                'hot_reload': False
            },
            'accounts': [
                {
                    'api_id': 123456,
                    'api_hash': 'test_hash',
                    'phone': '+1234567890',
                    'session_name': 'test_session',
                    'enabled': True
                }
            ],
            'schedules': [
                {
                    'name': 'test_schedule',
                    'target': '@test_channel',
                    'message': 'Test message',
                    'interval': 3600,
                    'enabled': True,
                    'auto_delete': False,
                    'delete_after': 60
                }
            ],
            'monitors': [
                {
                    'name': 'test_monitor',
                    'target': '@test_group',
                    'keywords': ['test', 'help'],
                    'reply_message': 'Test reply',
                    'enabled': True,
                    'exact_match': False
                }
            ]
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(test_config, f)
            
        # Load config
        manager = ConfigManager(str(config_path))
        config = manager.load_config()
        
        # Verify app config
        assert config.log_enabled == True
        assert config.log_level == 'DEBUG'
        assert config.hot_reload is False
        
        # Verify accounts
        assert len(config.accounts) == 1
        account = config.accounts[0]
        assert account.api_id == 123456
        assert account.api_hash == 'test_hash'
        assert account.phone == '+1234567890'
        assert account.session_name == 'test_session'
        assert account.enabled is True
        
        # Verify schedules
        assert len(config.schedules) == 1
        schedule = config.schedules[0]
        assert schedule.name == 'test_schedule'
        assert schedule.target == '@test_channel'
        assert schedule.message == 'Test message'
        assert schedule.interval == 3600
        assert schedule.enabled is True
        assert schedule.auto_delete is False
        
        # Verify monitors
        assert len(config.monitors) == 1
        monitor = config.monitors[0]
        assert monitor.name == 'test_monitor'
        assert monitor.target == '@test_group'
        assert monitor.keywords == ['test', 'help']
        assert monitor.reply_message == 'Test reply'
        assert monitor.enabled is True
        assert monitor.exact_match is False


def test_config_validation():
    """Test configuration validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yml"
        
        # Create invalid config
        invalid_config = {
            'app': {
                'log_enabled': True
            },
            'accounts': [
                {
                    'api_id': 0,  # Invalid
                    'api_hash': 'your_api_hash_here',  # Invalid placeholder
                    'phone': '',  # Invalid
                    'session_name': 'test',
                    'enabled': True
                }
            ],
            'schedules': [
                {
                    'name': 'test',
                    'target': '',  # Invalid
                    'message': '',  # Invalid
                    'interval': 30,  # Too short
                    'enabled': True
                }
            ],
            'monitors': [
                {
                    'name': 'test',
                    'target': '',  # Invalid
                    'keywords': [],  # Invalid
                    'reply_message': '',  # Invalid
                    'enabled': True
                }
            ]
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(invalid_config, f)
            
        manager = ConfigManager(str(config_path))
        manager.load_config()
        errors = manager.validate_config()
        
        # Should have multiple validation errors
        assert len(errors) > 0
        
        # Check for specific error patterns
        error_text = ' '.join(errors)
        assert 'Invalid API ID' in error_text
        assert 'Invalid API hash' in error_text
        assert 'Phone number required' in error_text
        assert 'Target required' in error_text
        assert 'Message required' in error_text
        assert 'Keywords required' in error_text
        assert 'Reply message required' in error_text


def test_dataclass_creation():
    """Test dataclass creation."""
    # Test AccountConfig
    account = AccountConfig(
        api_id=123456,
        api_hash='test_hash',
        phone='+1234567890',
        session_name='test'
    )
    assert account.enabled is True  # Default value
    
    # Test ScheduleConfig  
    schedule = ScheduleConfig(
        name='test',
        target='@channel',
        message='Hello',
        interval=3600
    )
    assert schedule.enabled is True
    assert schedule.auto_delete is False
    assert schedule.delete_after == 60
    
    # Test MonitorConfig
    monitor = MonitorConfig(
        name='test',
        target='@group', 
        keywords=['help'],
        reply_message='Reply'
    )
    assert monitor.enabled is True
    assert monitor.exact_match is False