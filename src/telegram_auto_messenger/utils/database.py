"""
Placeholder database module - database functionality removed per requirements.
All database operations are now no-ops to maintain compatibility.
"""

from typing import List, Dict, Optional, Any


class DatabaseManager:
    """Placeholder database manager - all operations are no-ops."""
    
    def __init__(self, database_path: str = ""):
        """Initialize placeholder database manager."""
        pass
        
    async def initialize(self):
        """No-op initialization."""
        pass
        
    async def log_message(self, account_name: str, target: str, message_text: str, 
                         message_id: Optional[int] = None, message_type: str = "sent",
                         success: bool = True, error_message: Optional[str] = None):
        """No-op message logging."""
        pass
        
    async def log_schedule_execution(self, schedule_name: str, target: str, message_text: str,
                                   success: bool = True, error_message: Optional[str] = None,
                                   execution_time_ms: Optional[int] = None):
        """No-op schedule execution logging."""
        pass
        
    async def log_monitor_activity(self, monitor_name: str, target: str, trigger_message: str,
                                 reply_message: str, success: bool = True, 
                                 error_message: Optional[str] = None):
        """No-op monitor activity logging."""
        pass
        
    async def log_app_event(self, event_type: str, description: str, details: Optional[str] = None):
        """No-op app event logging."""
        pass
        
    async def log_account_status(self, account_name: str, status: str, details: Optional[str] = None):
        """No-op account status logging."""
        pass
        
    async def get_message_history(self, limit: int = 100, account_name: Optional[str] = None,
                                 target: Optional[str] = None) -> List[Dict]:
        """Return empty history."""
        return []
        
    async def get_schedule_history(self, limit: int = 100, 
                                  schedule_name: Optional[str] = None) -> List[Dict]:
        """Return empty history."""
        return []
        
    async def get_monitor_history(self, limit: int = 100,
                                 monitor_name: Optional[str] = None) -> List[Dict]:
        """Return empty history."""
        return []
        
    async def get_statistics(self) -> Dict[str, Any]:
        """Return empty statistics."""
        return {
            'messages': {'total': 0, 'successful': 0},
            'schedules': {'total': 0, 'successful': 0},
            'monitors': {'total': 0, 'successful': 0},
            'messages_24h': 0
        }
        
    async def cleanup_old_data(self, days: int = 30):
        """No-op cleanup."""
        return 0
        
    async def close(self):
        """No-op close."""
        pass