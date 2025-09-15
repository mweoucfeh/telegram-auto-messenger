"""
Tests for cultivation bot functionality.
"""

import pytest
from datetime import datetime, timedelta
from src.telegram_auto_messenger.core.cultivation import CultivationSession, CultivationManager


def test_cultivation_session_creation():
    """Test creating a cultivation session."""
    session = CultivationSession("account1", "@test_channel", ".闭关修炼")
    
    assert session.account_name == "account1"
    assert session.channel == "@test_channel"
    assert session.command == ".闭关修炼"
    assert session.is_active == False
    assert session.success_count == 0
    assert session.failure_count == 0


def test_parse_successful_response():
    """Test parsing successful cultivation response."""
    session = CultivationSession("account1", "@test_channel")
    
    success_message = """【闭关成功】
你福至心灵，成功炼化灵气，基础修为增加了 49 点。
因【星宫】灵脉加持，你额外获得了 29 点修为！
本次闭关，你的修为最终增加了 78 点。

当前境界: 筑基后期
当前修为: 1298 / 30000

你感到一阵疲惫，需要打坐调息 13 分钟方可再次闭关。"""
    
    wait_seconds = session.parse_response(success_message)
    
    # Should return wait time from the last line
    assert wait_seconds == 13 * 60  # 13 minutes in seconds
    assert session.success_count == 1


def test_parse_failure_response():
    """Test parsing failure cultivation response."""
    session = CultivationSession("account1", "@test_channel")
    
    failure_message = "灵气尚未平复，无法立即再次闭关。请在 11分钟36秒 后再试。"
    
    wait_seconds = session.parse_response(failure_message)
    
    assert wait_seconds == (11 * 60) + 36  # 11 minutes 36 seconds
    assert session.failure_count == 1


def test_parse_simple_minutes():
    """Test parsing simple minute wait time."""
    session = CultivationSession("account1", "@test_channel")
    
    message = "你感到一阵疲惫，需要打坐调息 5 分钟方可再次闭关。"
    
    wait_seconds = session.parse_response(message)
    
    assert wait_seconds == 5 * 60  # 5 minutes


def test_parse_success_no_wait():
    """Test parsing success with no wait required."""
    session = CultivationSession("account1", "@test_channel")
    
    success_message = """【闭关成功】
你福至心灵，成功炼化灵气，基础修为增加了 49 点。"""
    
    wait_seconds = session.parse_response(success_message)
    
    assert wait_seconds == 0  # No wait needed
    assert session.success_count == 1


def test_schedule_next_attempt():
    """Test scheduling next cultivation attempt."""
    session = CultivationSession("account1", "@test_channel")
    
    # Test immediate retry (success case)
    session.schedule_next_attempt(0)
    assert session.next_attempt is not None
    assert session.next_attempt > datetime.now()
    
    # Test with wait time
    wait_seconds = 300  # 5 minutes
    session.schedule_next_attempt(wait_seconds)
    expected_time = datetime.now() + timedelta(seconds=wait_seconds + 10 + (wait_seconds * 0.1))
    
    # Should be scheduled for roughly wait_seconds + extra delay
    time_diff = abs((session.next_attempt - expected_time).total_seconds())
    assert time_diff < 5  # Allow 5 second tolerance


def test_session_ready_check():
    """Test session ready checking."""
    session = CultivationSession("account1", "@test_channel")
    
    # Initially ready (no next_attempt set)
    assert session.is_ready() == True
    
    # Schedule for future
    session.next_attempt = datetime.now() + timedelta(seconds=60)
    assert session.is_ready() == False
    
    # Schedule for past
    session.next_attempt = datetime.now() - timedelta(seconds=1)
    assert session.is_ready() == True


def test_session_status():
    """Test getting session status."""
    session = CultivationSession("account1", "@test_channel", ".test")
    session.is_active = True
    session.success_count = 5
    session.failure_count = 2
    
    status = session.get_status()
    
    assert status['account'] == "account1"
    assert status['channel'] == "@test_channel"
    assert status['command'] == ".test"
    assert status['is_active'] == True
    assert status['success_count'] == 5
    assert status['failure_count'] == 2
    assert 'is_ready' in status


def test_cultivation_manager_session_management():
    """Test cultivation manager session management."""
    # Mock account manager
    class MockAccountManager:
        def get_account(self, name):
            return None
    
    manager = CultivationManager(MockAccountManager())
    
    # Add session
    success = manager.add_session("account1", "@channel1", ".test")
    assert success == True
    assert len(manager.sessions) == 1
    
    # Try to add duplicate
    success = manager.add_session("account1", "@channel1", ".test2")
    assert success == False  # Should fail
    assert len(manager.sessions) == 1
    
    # Remove session
    success = manager.remove_session("account1", "@channel1")
    assert success == True
    assert len(manager.sessions) == 0
    
    # Try to remove non-existent
    success = manager.remove_session("account1", "@channel1")
    assert success == False


def test_cultivation_manager_status():
    """Test cultivation manager status."""
    manager = CultivationManager(None)
    
    # Add a few sessions
    manager.add_session("account1", "@channel1")
    manager.add_session("account2", "@channel2")
    
    status = manager.get_status()
    
    assert status['running'] == False
    assert status['total_sessions'] == 2
    assert status['active_sessions'] == 0
    assert len(status['sessions']) == 2


if __name__ == "__main__":
    pytest.main([__file__])