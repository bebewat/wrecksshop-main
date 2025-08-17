"""
Enhanced logging system for the Ark Bot Manager
Provides comprehensive logging with multiple handlers and formatters
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional
import threading

class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels in console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to the levelname
        if hasattr(record, 'levelname'):
            colored_levelname = f"{self.COLORS.get(record.levelname, '')}{record.levelname}{self.COLORS['RESET']}"
            record.levelname = colored_levelname
        
        return super().format(record)

class DatabaseLogHandler(logging.Handler):
    """Custom log handler that writes to database"""
    
    def __init__(self, database_manager):
        super().__init__()
        self.db_manager = database_manager
        self.lock = threading.Lock()
    
    def emit(self, record):
        try:
            with self.lock:
                # Format the log record
                log_entry = self.format(record)
                
                # Extract information
                timestamp = datetime.fromtimestamp(record.created).isoformat()
                level = record.levelname
                message = record.getMessage()
                module = record.module if hasattr(record, 'module') else record.name
                
                # Store in database
                if hasattr(self.db_manager, 'get_connection'):
                    conn = self.db_manager.get_connection()
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO log_entries (timestamp, level, message, module)
                        VALUES (?, ?, ?, ?)
                    ''', (timestamp, level, message, module))
                    
                    conn.commit()
                    
        except Exception:
            # Don't log errors from the log handler to avoid recursion
            pass

def setup_logging(config_manager=None, database_manager=None) -> logging.Logger:
    """
    Setup comprehensive logging system
    
    Args:
        config_manager: Configuration manager instance
        database_manager: Database manager instance
        
    Returns:
        Configured logger instance
    """
    
    # Get configuration values
    if config_manager:
        log_level = config_manager.get('log_level', 'INFO')
        log_file = config_manager.get('log_file', 'logs/arkbot.log')
        max_log_size = config_manager.get('max_log_size', 10485760)  # 10MB
        backup_count = config_manager.get('log_backup_count', 5)
    else:
        log_level = 'INFO'
        log_file = 'logs/arkbot.log'
        max_log_size = 10485760
        backup_count = 5
    
    # Create logs directory
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger('arkbot')
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # File handler with rotation
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_log_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not setup file logging: {e}")
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Database handler (if database manager is available)
    if database_manager:
        try:
            db_handler = DatabaseLogHandler(database_manager)
            db_handler.setLevel(logging.INFO)  # Only log INFO and above to database
            db_handler.setFormatter(file_formatter)
            logger.addHandler(db_handler)
        except Exception as e:
            logger.warning(f"Could not setup database logging: {e}")
    
    # Log startup message
    logger.info("="*60)
    logger.info("Ark Bot Manager - Logging System Initialized")
    logger.info(f"Log Level: {log_level}")
    logger.info(f"Log File: {log_file}")
    logger.info("="*60)
    
    # Set up logging for other modules
    setup_module_loggers(logger)
    
    return logger

def setup_module_loggers(parent_logger: logging.Logger):
    """Setup loggers for different modules"""
    
    # Discord.py logging
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.WARNING)  # Reduce discord.py verbosity
    
    # Bot command logging
    commands_logger = logging.getLogger('arkbot.commands')
    commands_logger.setLevel(logging.INFO)
    
    # Database logging
    database_logger = logging.getLogger('arkbot.database')
    database_logger.setLevel(logging.INFO)
    
    # RCON logging
    rcon_logger = logging.getLogger('arkbot.rcon')
    rcon_logger.setLevel(logging.INFO)
    
    # Point system logging
    points_logger = logging.getLogger('arkbot.points')
    points_logger.setLevel(logging.INFO)
    
    # Shop logging
    shop_logger = logging.getLogger('arkbot.shop')
    shop_logger.setLevel(logging.INFO)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module
    
    Args:
        name: Logger name (e.g., 'arkbot.commands')
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

class LogContext:
    """Context manager for adding context to log messages"""
    
    def __init__(self, logger: logging.Logger, **context):
        self.logger = logger
        self.context = context
        self.old_factory = logging.getLogRecordFactory()
    
    def __enter__(self):
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self.old_factory)

def log_function_call(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        logger = get_logger(f'arkbot.{func.__module__}')
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {e}")
            raise
    
    return wrapper

def log_performance(func):
    """Decorator to log function performance"""
    def wrapper(*args, **kwargs):
        import time
        
        logger = get_logger(f'arkbot.performance')
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            
            if duration > 1.0:  # Log slow functions
                logger.warning(f"{func.__name__} took {duration:.2f} seconds")
            else:
                logger.debug(f"{func.__name__} took {duration:.3f} seconds")
            
            return result
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            logger.error(f"{func.__name__} failed after {duration:.3f} seconds: {e}")
            raise
    
    return wrapper

class StructuredLogger:
    """Structured logging for better log analysis"""
    
    def __init__(self, logger_name: str):
        self.logger = get_logger(logger_name)
    
    def log_event(self, event_type: str, message: str, **extra_data):
        """Log a structured event"""
        extra_data['event_type'] = event_type
        extra_data['timestamp'] = datetime.now().isoformat()
        
        # Format the log message
        formatted_message = f"[{event_type}] {message}"
        if extra_data:
            extra_parts = [f"{k}={v}" for k, v in extra_data.items() if k not in ['event_type', 'timestamp']]
            if extra_parts:
                formatted_message += f" | {', '.join(extra_parts)}"
        
        self.logger.info(formatted_message, extra=extra_data)
    
    def log_user_action(self, user_id: str, action: str, details: str = "", **extra):
        """Log user actions"""
        self.log_event(
            'USER_ACTION',
            f"User {user_id} performed {action}",
            user_id=user_id,
            action=action,
            details=details,
            **extra
        )
    
    def log_shop_purchase(self, user_id: str, item_name: str, price: int, **extra):
        """Log shop purchases"""
        self.log_event(
            'SHOP_PURCHASE',
            f"User {user_id} purchased {item_name} for {price} points",
            user_id=user_id,
            item_name=item_name,
            price=price,
            **extra
        )
    
    def log_points_transaction(self, user_id: str, amount: int, reason: str, **extra):
        """Log points transactions"""
        transaction_type = 'POINTS_ADDED' if amount > 0 else 'POINTS_REMOVED'
        self.log_event(
            transaction_type,
            f"User {user_id} {'+' if amount > 0 else ''}{amount} points: {reason}",
            user_id=user_id,
            amount=amount,
            reason=reason,
            **extra
        )
    
    def log_rcon_command(self, server: str, command: str, success: bool, **extra):
        """Log RCON commands"""
        status = 'SUCCESS' if success else 'FAILED'
        self.log_event(
            'RCON_COMMAND',
            f"RCON command on {server}: {command} [{status}]",
            server=server,
            command=command,
            success=success,
            **extra
        )
    
    def log_error(self, error_type: str, message: str, **extra):
        """Log errors with structured format"""
        self.log_event(
            'ERROR',
            f"{error_type}: {message}",
            error_type=error_type,
            **extra
        )

def setup_error_logging():
    """Setup global error logging"""
    logger = get_logger('arkbot.errors')
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    
    sys.excepthook = handle_exception

def create_daily_log_file(base_path: str) -> str:
    """Create a daily log file path"""
    today = datetime.now().strftime('%Y-%m-%d')
    base_dir = os.path.dirname(base_path)
    base_name = os.path.splitext(os.path.basename(base_path))[0]
    
    return os.path.join(base_dir, f"{base_name}_{today}.log")

def cleanup_old_logs(log_directory: str, days_to_keep: int = 30):
    """Cleanup old log files"""
    try:
        import glob
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        log_pattern = os.path.join(log_directory, "*.log*")
        
        deleted_count = 0
        for log_file in glob.glob(log_pattern):
            try:
                file_time = datetime.fromtimestamp(os.path.getctime(log_file))
                if file_time < cutoff_date:
                    os.remove(log_file)
                    deleted_count += 1
            except OSError:
                pass  # Skip files that can't be deleted
        
        if deleted_count > 0:
            logger = get_logger('arkbot.maintenance')
            logger.info(f"Cleaned up {deleted_count} old log files")
            
    except Exception as e:
        logger = get_logger('arkbot.maintenance')
        logger.error(f"Error during log cleanup: {e}")

# Initialize error logging when module is imported
setup_error_logging()

