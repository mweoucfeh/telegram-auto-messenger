"""
Test utilities.
"""

import pytest
import asyncio
import tempfile
from pathlib import Path

from telegram_auto_messenger.utils.database import DatabaseManager
from telegram_auto_messenger.utils.logger import setup_logging, get_logger


@pytest.mark.asyncio
async def test_database_manager():
    """Test database manager functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        
        # Initialize database
        db = DatabaseManager(str(db_path))
        await db.initialize()
        
        # Test message logging
        await db.log_message(
            account_name="test_account",
            target="@test_channel",
            message_text="Test message",
            message_id=12345,
            success=True
        )
        
        # Test schedule logging
        await db.log_schedule_execution(
            schedule_name="test_schedule",
            target="@test_channel", 
            message_text="Scheduled message",
            success=True,
            execution_time_ms=100
        )
        
        # Test monitor logging
        await db.log_monitor_activity(
            monitor_name="test_monitor",
            target="@test_group",
            trigger_message="help me",
            reply_message="How can I help?",
            success=True
        )
        
        # Test app event logging
        await db.log_app_event(
            event_type="startup",
            description="Application started",
            details="All systems operational"
        )
        
        # Test account status logging
        await db.log_account_status(
            account_name="test_account",
            status="connected",
            details="Successfully connected to Telegram"
        )
        
        # Test data retrieval
        messages = await db.get_message_history(limit=10)
        assert len(messages) == 1
        assert messages[0]['account_name'] == 'test_account'
        assert messages[0]['target'] == '@test_channel'
        
        schedules = await db.get_schedule_history(limit=10)
        assert len(schedules) == 1
        assert schedules[0]['schedule_name'] == 'test_schedule'
        
        monitors = await db.get_monitor_history(limit=10)
        assert len(monitors) == 1
        assert monitors[0]['monitor_name'] == 'test_monitor'
        
        # Test statistics
        stats = await db.get_statistics()
        assert stats['messages']['total'] == 1
        assert stats['schedules']['total'] == 1
        assert stats['monitors']['total'] == 1
        
        # Close database
        await db.close()


def test_logger_setup():
    """Test logger setup."""
    # Test basic setup
    setup_logging('INFO')
    logger = get_logger('test')
    assert logger.level <= 20  # INFO level
    
    # Test debug setup
    setup_logging('DEBUG')
    logger = get_logger('test_debug')
    assert logger.level <= 10  # DEBUG level
    
    # Test with log file
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"
        setup_logging('INFO', str(log_file))
        
        logger = get_logger('test_file')
        logger.info("Test message")
        
        # Check if log file was created
        assert log_file.exists()
        
        # Check if message was logged
        with open(log_file) as f:
            content = f.read()
            assert "Test message" in content