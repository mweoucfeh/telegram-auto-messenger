"""
Enhanced logging utilities for the Telegram Auto-Messenger with file support.
"""

import datetime
import logging
import logging.handlers
import os
import sys
import traceback
from pathlib import Path
from typing import Optional, Any


class SimpleLogger:
    """Enhanced logger with console and file output support."""
    
    def __init__(self, enabled: bool = True, level: str = "INFO", log_to_file: bool = True, log_dir: str = "logs"):
        self.enabled = enabled
        self.level = level.upper()
        self.log_to_file = log_to_file
        self.log_dir = Path(log_dir)
        self._levels = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}
        self._current_level = self._levels.get(self.level, 1)
        
        # Setup file logging if enabled
        self._file_logger = None
        if self.enabled and self.log_to_file:
            self._setup_file_logging()
        
    def _setup_file_logging(self):
        """Setup file logging with rotation."""
        try:
            # Create logs directory if it doesn't exist
            self.log_dir.mkdir(parents=True, exist_ok=True)
            
            # Setup file logger
            self._file_logger = logging.getLogger('telegram_auto_messenger')
            self._file_logger.setLevel(getattr(logging, self.level, logging.INFO))
            
            # Remove existing handlers to avoid duplicates
            for handler in self._file_logger.handlers[:]:
                self._file_logger.removeHandler(handler)
            
            # Main log file with rotation (10MB max, keep 5 files)
            main_log_file = self.log_dir / "telegram_auto_messenger.log"
            file_handler = logging.handlers.RotatingFileHandler(
                main_log_file, 
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            
            # Error log file for errors and critical messages
            error_log_file = self.log_dir / "errors.log"
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            
            # Detailed formatter for file logs
            file_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            error_handler.setFormatter(file_formatter)
            
            self._file_logger.addHandler(file_handler)
            self._file_logger.addHandler(error_handler)
            
            # Prevent propagation to root logger
            self._file_logger.propagate = False
            
        except Exception as e:
            # Fallback to console only if file setup fails
            print(f"Warning: Failed to setup file logging: {e}")
            self.log_to_file = False
            self._file_logger = None
        
    def _should_log(self, level: str) -> bool:
        """Check if message should be logged based on level."""
        return self.enabled and self._levels.get(level, 0) >= self._current_level
        
    def _format_message(self, level: str, message: str, name: str = "") -> str:
        """Format log message with timestamp."""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if name:
            return f"{timestamp} [{level:8s}] {name}: {message}"
        return f"{timestamp} [{level:8s}]: {message}"
    
    def _log_to_file(self, level: str, message: str, name: str = "", exc_info: Any = None):
        """Log message to file using standard logging."""
        if self._file_logger:
            try:
                logger_name = name if name else 'telegram_auto_messenger'
                file_logger = logging.getLogger(f'telegram_auto_messenger.{logger_name}' if name else 'telegram_auto_messenger')
                file_logger.setLevel(self._file_logger.level)
                
                # Copy handlers from main file logger if not already present
                if not file_logger.handlers:
                    for handler in self._file_logger.handlers:
                        file_logger.addHandler(handler)
                    file_logger.propagate = False
                
                # Map our levels to logging levels
                log_level = getattr(logging, level, logging.INFO)
                file_logger.log(log_level, message, exc_info=exc_info)
                
            except Exception as e:
                # Fallback: at least print the error
                print(f"File logging error: {e}")
        
    def debug(self, message: str, name: str = "", exc_info: Any = None):
        """Log debug message."""
        if self._should_log("DEBUG"):
            formatted_msg = self._format_message("DEBUG", message, name)
            print(formatted_msg)
            if self.log_to_file:
                self._log_to_file("DEBUG", message, name, exc_info)
            
    def info(self, message: str, name: str = "", exc_info: Any = None):
        """Log info message."""
        if self._should_log("INFO"):
            formatted_msg = self._format_message("INFO", message, name)
            print(formatted_msg)
            if self.log_to_file:
                self._log_to_file("INFO", message, name, exc_info)
            
    def warning(self, message: str, name: str = "", exc_info: Any = None):
        """Log warning message."""
        if self._should_log("WARNING"):
            formatted_msg = self._format_message("WARNING", message, name)
            print(formatted_msg)
            if self.log_to_file:
                self._log_to_file("WARNING", message, name, exc_info)
            
    def error(self, message: str, name: str = "", exc_info: Any = None):
        """Log error message."""
        if self._should_log("ERROR"):
            formatted_msg = self._format_message("ERROR", message, name)
            print(formatted_msg)
            if self.log_to_file:
                self._log_to_file("ERROR", message, name, exc_info)
            
    def critical(self, message: str, name: str = "", exc_info: Any = None):
        """Log critical message."""
        if self._should_log("CRITICAL"):
            formatted_msg = self._format_message("CRITICAL", message, name)
            print(formatted_msg)
            if self.log_to_file:
                self._log_to_file("CRITICAL", message, name, exc_info)
    
    def exception(self, message: str, name: str = ""):
        """Log an exception with full stack trace."""
        if self._should_log("ERROR"):
            # Get the current exception info
            exc_type, exc_value, exc_traceback = sys.exc_info()
            
            if exc_traceback is not None:
                # Format the full exception with traceback
                stack_trace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                full_message = f"{message}\nException details:\n{stack_trace}"
                
                # Print to console
                formatted_msg = self._format_message("ERROR", full_message, name)
                print(formatted_msg)
                
                # Log to file with exception info
                if self.log_to_file:
                    self._log_to_file("ERROR", message, name, exc_info=True)
            else:
                # No exception info available, log as regular error
                self.error(message, name)


# Global logger instance
_global_logger: Optional[SimpleLogger] = None


def setup_logging(enabled: bool = True, level: str = "INFO", log_to_file: bool = True, log_dir: str = "logs"):
    """Setup enhanced logging with file support."""
    global _global_logger
    _global_logger = SimpleLogger(enabled, level, log_to_file, log_dir)
    
    if enabled:
        _global_logger.info(f"Enhanced logging initialized (level: {level}, file: {log_to_file}, dir: {log_dir})")


def get_logger(name: str = "") -> SimpleLogger:
    """Get the global logger instance."""
    global _global_logger
    if _global_logger is None:
        setup_logging()
    return _global_logger


def log_exception(message: str = "An unexpected error occurred", logger_name: str = ""):
    """Convenience function to log current exception with stack trace."""
    logger = get_logger(logger_name)
    logger.exception(message, logger_name)


class LoggerMixin:
    """Mixin class to add logger property to any class."""
    
    @property
    def logger(self):
        """Get logger for this class."""
        return get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")