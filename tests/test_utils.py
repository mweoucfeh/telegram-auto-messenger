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
    """Test database manager (now no-op)."""
    db = DatabaseManager()
    
    # Initialize (no-op)
    await db.initialize()
    
    # Test logging operations (all no-ops now)
    await db.log_message(
        account_name="test_account",
        target="@test_channel",
        message_text="Test message",
        message_id=12345,
        success=True
    )
    
    await db.log_schedule_execution(
        schedule_name="test_schedule",
        target="@test_channel", 
        message_text="Scheduled message",
        success=True,
        execution_time_ms=100
    )
    
    await db.log_monitor_activity(
        monitor_name="test_monitor",
        target="@test_group",
        trigger_message="help me",
        reply_message="How can I help?",
        success=True
    )
    
    await db.log_app_event(
        event_type="startup",
        description="Application started",
        details="All systems operational"
    )
    
    await db.log_account_status(
        account_name="test_account",
        status="connected",
        details="Successfully connected to Telegram"
    )
    
    # Test data retrieval (all return empty now)
    messages = await db.get_message_history(limit=10)
    assert len(messages) == 0  # No-op returns empty list
    
    schedules = await db.get_schedule_history(limit=10)
    assert len(schedules) == 0  # No-op returns empty list
    
    monitors = await db.get_monitor_history(limit=10)
    assert len(monitors) == 0  # No-op returns empty list
    
    # Test statistics (returns empty stats)
    stats = await db.get_statistics()
    assert stats['messages']['total'] == 0
    assert stats['schedules']['total'] == 0
    assert stats['monitors']['total'] == 0
    
    # Test cleanup (no-op)
    deleted = await db.cleanup_old_data(30)
    assert deleted == 0
    
    # Test close (no-op)
    await db.close()


def test_logger_setup():
    """Test logger setup."""
    # Test basic setup
    setup_logging(True, 'INFO')
    logger = get_logger('test')
    assert logger._current_level <= 1  # INFO level
    
    # Test debug setup
    setup_logging(True, 'DEBUG')
    logger = get_logger('test_debug')
    assert logger._current_level <= 0  # DEBUG level
    
    # Test disabled logging
    setup_logging(False, 'INFO')
    logger = get_logger('test_disabled')
    assert logger.enabled is False