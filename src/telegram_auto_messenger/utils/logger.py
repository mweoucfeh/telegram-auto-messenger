"""
Simple print-based logging utilities for the Telegram Auto-Messenger.
"""

import datetime
from typing import Optional


class SimpleLogger:
    """Simple logger that prints to console with on/off control."""
    
    def __init__(self, enabled: bool = True, level: str = "INFO"):
        self.enabled = enabled
        self.level = level.upper()
        self._levels = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}
        self._current_level = self._levels.get(self.level, 1)
        
    def _should_log(self, level: str) -> bool:
        """Check if message should be logged based on level."""
        return self.enabled and self._levels.get(level, 0) >= self._current_level
        
    def _format_message(self, level: str, message: str, name: str = "") -> str:
        """Format log message with timestamp."""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if name:
            return f"{timestamp} [{level:8s}] {name}: {message}"
        return f"{timestamp} [{level:8s}]: {message}"
        
    def debug(self, message: str, name: str = ""):
        """Log debug message."""
        if self._should_log("DEBUG"):
            print(self._format_message("DEBUG", message, name))
            
    def info(self, message: str, name: str = ""):
        """Log info message."""
        if self._should_log("INFO"):
            print(self._format_message("INFO", message, name))
            
    def warning(self, message: str, name: str = ""):
        """Log warning message."""
        if self._should_log("WARNING"):
            print(self._format_message("WARNING", message, name))
            
    def error(self, message: str, name: str = ""):
        """Log error message."""
        if self._should_log("ERROR"):
            print(self._format_message("ERROR", message, name))
            
    def critical(self, message: str, name: str = ""):
        """Log critical message."""
        if self._should_log("CRITICAL"):
            print(self._format_message("CRITICAL", message, name))


# Global logger instance
_global_logger: Optional[SimpleLogger] = None


def setup_logging(enabled: bool = True, level: str = "INFO"):
    """Setup simple print-based logging."""
    global _global_logger
    _global_logger = SimpleLogger(enabled, level)
    
    if enabled:
        _global_logger.info(f"Simple logging initialized (level: {level})")


def get_logger(name: str = "") -> SimpleLogger:
    """Get the global logger instance."""
    global _global_logger
    if _global_logger is None:
        setup_logging()
    return _global_logger


class LoggerMixin:
    """Mixin class to add logger property to any class."""
    
    @property
    def logger(self):
        """Get logger for this class."""
        return get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")