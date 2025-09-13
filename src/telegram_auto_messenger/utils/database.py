"""
Database management utilities for the Telegram Auto-Messenger.
"""

import asyncio
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime


class DatabaseManager:
    """Manages SQLite database operations."""
    
    def __init__(self, database_path: str = "data/telegram_auto_messenger.db"):
        self.database_path = Path(database_path)
        self.logger = logging.getLogger(__name__)
        self._connection: Optional[sqlite3.Connection] = None
        
    async def initialize(self):
        """Initialize database and create tables."""
        # Create data directory
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Connect to database
        await self._connect()
        
        # Create tables
        await self._create_tables()
        
        self.logger.info(f"Database initialized: {self.database_path}")
        
    async def _connect(self):
        """Connect to the database."""
        self._connection = sqlite3.connect(
            str(self.database_path),
            check_same_thread=False
        )
        self._connection.row_factory = sqlite3.Row
        
    async def _create_tables(self):
        """Create database tables."""
        tables = [
            # Message log table
            """
            CREATE TABLE IF NOT EXISTS message_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                account_name TEXT NOT NULL,
                target TEXT NOT NULL,
                message_text TEXT NOT NULL,
                message_id INTEGER,
                message_type TEXT DEFAULT 'sent',
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT
            )
            """,
            
            # Schedule execution log
            """
            CREATE TABLE IF NOT EXISTS schedule_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                schedule_name TEXT NOT NULL,
                target TEXT NOT NULL,
                message_text TEXT NOT NULL,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT,
                execution_time_ms INTEGER
            )
            """,
            
            # Monitor activity log
            """
            CREATE TABLE IF NOT EXISTS monitor_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                monitor_name TEXT NOT NULL,
                target TEXT NOT NULL,
                trigger_message TEXT NOT NULL,
                reply_message TEXT NOT NULL,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT
            )
            """,
            
            # Application events log
            """
            CREATE TABLE IF NOT EXISTS app_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                details TEXT
            )
            """,
            
            # Account status log
            """
            CREATE TABLE IF NOT EXISTS account_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                account_name TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT
            )
            """
        ]
        
        cursor = self._connection.cursor()
        for table_sql in tables:
            cursor.execute(table_sql)
        self._connection.commit()
        cursor.close()
        
    async def log_message(self, account_name: str, target: str, message_text: str, 
                         message_id: Optional[int] = None, message_type: str = "sent",
                         success: bool = True, error_message: Optional[str] = None):
        """Log a message operation."""
        cursor = self._connection.cursor()
        cursor.execute(
            """
            INSERT INTO message_log 
            (account_name, target, message_text, message_id, message_type, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (account_name, target, message_text, message_id, message_type, success, error_message)
        )
        self._connection.commit()
        cursor.close()
        
    async def log_schedule_execution(self, schedule_name: str, target: str, message_text: str,
                                   success: bool = True, error_message: Optional[str] = None,
                                   execution_time_ms: Optional[int] = None):
        """Log a schedule execution."""
        cursor = self._connection.cursor()
        cursor.execute(
            """
            INSERT INTO schedule_log 
            (schedule_name, target, message_text, success, error_message, execution_time_ms)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (schedule_name, target, message_text, success, error_message, execution_time_ms)
        )
        self._connection.commit()
        cursor.close()
        
    async def log_monitor_activity(self, monitor_name: str, target: str, trigger_message: str,
                                 reply_message: str, success: bool = True, 
                                 error_message: Optional[str] = None):
        """Log a monitor activity."""
        cursor = self._connection.cursor()
        cursor.execute(
            """
            INSERT INTO monitor_log 
            (monitor_name, target, trigger_message, reply_message, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (monitor_name, target, trigger_message, reply_message, success, error_message)
        )
        self._connection.commit()
        cursor.close()
        
    async def log_app_event(self, event_type: str, description: str, details: Optional[str] = None):
        """Log an application event."""
        cursor = self._connection.cursor()
        cursor.execute(
            """
            INSERT INTO app_events (event_type, description, details)
            VALUES (?, ?, ?)
            """,
            (event_type, description, details)
        )
        self._connection.commit()
        cursor.close()
        
    async def log_account_status(self, account_name: str, status: str, details: Optional[str] = None):
        """Log account status change."""
        cursor = self._connection.cursor()
        cursor.execute(
            """
            INSERT INTO account_status (account_name, status, details)
            VALUES (?, ?, ?)
            """,
            (account_name, status, details)
        )
        self._connection.commit()
        cursor.close()
        
    async def get_message_history(self, limit: int = 100, account_name: Optional[str] = None,
                                 target: Optional[str] = None) -> List[Dict]:
        """Get message history."""
        cursor = self._connection.cursor()
        
        query = "SELECT * FROM message_log"
        params = []
        conditions = []
        
        if account_name:
            conditions.append("account_name = ?")
            params.append(account_name)
        if target:
            conditions.append("target = ?")
            params.append(target)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        
        return [dict(row) for row in rows]
        
    async def get_schedule_history(self, limit: int = 100, 
                                  schedule_name: Optional[str] = None) -> List[Dict]:
        """Get schedule execution history."""
        cursor = self._connection.cursor()
        
        query = "SELECT * FROM schedule_log"
        params = []
        
        if schedule_name:
            query += " WHERE schedule_name = ?"
            params.append(schedule_name)
            
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        
        return [dict(row) for row in rows]
        
    async def get_monitor_history(self, limit: int = 100,
                                 monitor_name: Optional[str] = None) -> List[Dict]:
        """Get monitor activity history."""
        cursor = self._connection.cursor()
        
        query = "SELECT * FROM monitor_log"
        params = []
        
        if monitor_name:
            query += " WHERE monitor_name = ?"
            params.append(monitor_name)
            
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        
        return [dict(row) for row in rows]
        
    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        cursor = self._connection.cursor()
        
        stats = {}
        
        # Message statistics
        cursor.execute("SELECT COUNT(*) as total, COUNT(CASE WHEN success = 1 THEN 1 END) as successful FROM message_log")
        row = cursor.fetchone()
        stats['messages'] = dict(row) if row else {'total': 0, 'successful': 0}
        
        # Schedule statistics
        cursor.execute("SELECT COUNT(*) as total, COUNT(CASE WHEN success = 1 THEN 1 END) as successful FROM schedule_log")
        row = cursor.fetchone()
        stats['schedules'] = dict(row) if row else {'total': 0, 'successful': 0}
        
        # Monitor statistics
        cursor.execute("SELECT COUNT(*) as total, COUNT(CASE WHEN success = 1 THEN 1 END) as successful FROM monitor_log")
        row = cursor.fetchone()
        stats['monitors'] = dict(row) if row else {'total': 0, 'successful': 0}
        
        # Recent activity (last 24 hours)
        cursor.execute("""
            SELECT COUNT(*) as count FROM message_log 
            WHERE timestamp > datetime('now', '-1 day')
        """)
        row = cursor.fetchone()
        stats['messages_24h'] = row['count'] if row else 0
        
        cursor.close()
        return stats
        
    async def cleanup_old_data(self, days: int = 30):
        """Clean up old data from database."""
        cursor = self._connection.cursor()
        
        tables = ['message_log', 'schedule_log', 'monitor_log', 'app_events', 'account_status']
        total_deleted = 0
        
        for table in tables:
            cursor.execute(
                f"DELETE FROM {table} WHERE timestamp < datetime('now', '-{days} days')"
            )
            total_deleted += cursor.rowcount
            
        self._connection.commit()
        cursor.close()
        
        if total_deleted > 0:
            self.logger.info(f"Cleaned up {total_deleted} old records")
            
        return total_deleted
        
    async def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            self.logger.info("Database connection closed")