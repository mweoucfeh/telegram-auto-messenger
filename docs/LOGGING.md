# Enhanced Logging Guide

The Telegram Auto-Messenger now includes enhanced logging capabilities for better debugging and monitoring.

## Logging Features

### File Logging
- **Main Log**: `logs/telegram_auto_messenger.log` - Contains all log messages with rotation (10MB max, 5 backups)
- **Error Log**: `logs/errors.log` - Contains only ERROR and CRITICAL messages with full stack traces
- **Log Rotation**: Automatic log file rotation to prevent disk space issues

### Exception Handling
- **Enhanced Exception Logging**: Full stack traces for all exceptions
- **Context Information**: Logger names identify the component that logged the message
- **Console + File**: Messages appear both in console and log files

## Configuration

Add these options to your `config.yml` under the `app` section:

```yaml
app:
  log_enabled: true       # Enable/disable all logging
  log_level: "INFO"       # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
  log_to_file: true       # Enable/disable file logging
  log_dir: "logs"         # Directory for log files
```

## Usage Examples

### Basic Logging
```python
from telegram_auto_messenger.utils.logger import get_logger

logger = get_logger("MyComponent")
logger.info("Application started")
logger.warning("This is a warning")
logger.error("An error occurred")
```

### Exception Logging
```python
try:
    # Some operation that might fail
    risky_operation()
except Exception as e:
    logger.exception("Operation failed")
    # This will log the full stack trace
```

### Convenience Function
```python
from telegram_auto_messenger.utils.logger import log_exception

try:
    risky_operation()
except Exception:
    log_exception("Custom error message", "ComponentName")
```

## Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about application flow
- **WARNING**: Warning messages for potentially harmful situations
- **ERROR**: Error messages for errors that don't stop the application
- **CRITICAL**: Critical messages for serious errors

## PyCharm Integration

The enhanced logging works seamlessly with PyCharm:

1. **Console Output**: All logs appear in PyCharm's console during debugging
2. **Log Files**: View log files directly in PyCharm's file explorer
3. **Stack Traces**: Click on stack trace lines to navigate to source code
4. **Search**: Use PyCharm's search functionality to find specific log entries

## File Structure

```
project/
├── logs/                           # Log directory (auto-created)
│   ├── telegram_auto_messenger.log # Main log file
│   ├── telegram_auto_messenger.log.1  # Rotated log files
│   ├── telegram_auto_messenger.log.2
│   ├── errors.log                  # Error-only log file
│   └── errors.log.1               # Rotated error log files
└── config/
    └── config.yml                 # Configuration file
```

## Best Practices

1. **Use appropriate log levels**: Don't use DEBUG in production
2. **Include context**: Use logger names to identify components
3. **Log exceptions**: Always use `logger.exception()` in except blocks
4. **Monitor log files**: Check error.log regularly for issues
5. **Log rotation**: The system automatically manages log file sizes

## Troubleshooting

### No log files created
- Check that `log_to_file: true` in config
- Verify write permissions for the log directory
- Check console for "Failed to setup file logging" warnings

### Large log files
- Log rotation is automatic (10MB limit)
- Adjust log level to reduce verbosity
- Consider cleaning old rotated files periodically

### Missing stack traces
- Use `logger.exception()` instead of `logger.error()`
- Call within an except block for full stack trace capture