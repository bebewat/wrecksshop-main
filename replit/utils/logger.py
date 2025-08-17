"""
Logging utility for the Ark Discord Bot
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional
from utils.config import Config

class Logger:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.logger = None
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        try:
            # Get logging configuration
            log_config = self.config.get('logging', {})
            log_level = log_config.get('level', 'INFO')
            log_file = log_config.get('file', 'logs/bot.log')
            max_file_size = log_config.get('max_file_size', 10485760)  # 10MB
            backup_count = log_config.get('backup_count', 5)
            
            # Ensure log directory exists
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            # Create logger
            self.logger = logging.getLogger('ArkBot')
            self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
            
            # Clear existing handlers
            self.logger.handlers.clear()
            
            # File handler with rotation
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Add handlers
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            
            # Log startup
            self.logger.info("Logging system initialized")
            
        except Exception as e:
            print(f"Error setting up logging: {e}")
            # Fallback to basic logging
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            self.logger = logging.getLogger('ArkBot')
    
    def debug(self, message: str):
        """Log debug message"""
        if self.logger:
            self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        if self.logger:
            self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        if self.logger:
            self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        if self.logger:
            self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        if self.logger:
            self.logger.critical(message)
    
    def log_exception(self, message: str = "An exception occurred"):
        """Log exception with traceback"""
        if self.logger:
            self.logger.exception(message)
    
    def log_bot_event(self, event_type: str, event_data: dict):
        """Log bot-specific events"""
        try:
            message = f"Bot Event [{event_type}]: {event_data}"
            self.info(message)
        except Exception as e:
            self.error(f"Error logging bot event: {e}")
    
    def log_command(self, user_id: str, command: str, success: bool = True):
        """Log bot command usage"""
        try:
            status = "SUCCESS" if success else "FAILED"
            message = f"Command [{status}] User: {user_id}, Command: {command}"
            self.info(message)
        except Exception as e:
            self.error(f"Error logging command: {e}")
    
    def log_purchase(self, user_id: str, item_name: str, cost: int, success: bool = True):
        """Log purchase events"""
        try:
            status = "SUCCESS" if success else "FAILED"
            message = f"Purchase [{status}] User: {user_id}, Item: {item_name}, Cost: {cost}"
            self.info(message)
        except Exception as e:
            self.error(f"Error logging purchase: {e}")
    
    def log_rcon_command(self, server: str, command: str, success: bool = True):
        """Log RCON command execution"""
        try:
            status = "SUCCESS" if success else "FAILED"
            message = f"RCON [{status}] Server: {server}, Command: {command}"
            self.info(message)
        except Exception as e:
            self.error(f"Error logging RCON command: {e}")
    
    def log_database_operation(self, operation: str, table: str, success: bool = True):
        """Log database operations"""
        try:
            status = "SUCCESS" if success else "FAILED"
            message = f"Database [{status}] Operation: {operation}, Table: {table}"
            self.debug(message)
        except Exception as e:
            self.error(f"Error logging database operation: {e}")
    
    def log_security_event(self, event_type: str, user_id: str, details: str):
        """Log security-related events"""
        try:
            message = f"Security [{event_type}] User: {user_id}, Details: {details}"
            self.warning(message)
        except Exception as e:
            self.error(f"Error logging security event: {e}")
    
    def get_logs(self, lines: int = 100) -> str:
        """Get recent log entries"""
        try:
            log_config = self.config.get('logging', {})
            log_file = log_config.get('file', 'logs/bot.log')
            
            if not os.path.exists(log_file):
                return "No log file found."
            
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                return ''.join(recent_lines)
                
        except Exception as e:
            return f"Error reading log file: {e}"
    
    def clear_logs(self):
        """Clear log files"""
        try:
            log_config = self.config.get('logging', {})
            log_file = log_config.get('file', 'logs/bot.log')
            
            if os.path.exists(log_file):
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write("")
                self.info("Log files cleared")
                return True
            return False
            
        except Exception as e:
            self.error(f"Error clearing logs: {e}")
            return False
    
    def export_logs(self, export_path: str, date_filter: Optional[str] = None) -> bool:
        """Export logs to file with optional date filter"""
        try:
            log_config = self.config.get('logging', {})
            log_file = log_config.get('file', 'logs/bot.log')
            
            if not os.path.exists(log_file):
                return False
            
            with open(log_file, 'r', encoding='utf-8') as source:
                with open(export_path, 'w', encoding='utf-8') as target:
                    if date_filter:
                        # Filter by date
                        for line in source:
                            if date_filter in line:
                                target.write(line)
                    else:
                        # Export all
                        target.write(source.read())
            
            self.info(f"Logs exported to {export_path}")
            return True
            
        except Exception as e:
            self.error(f"Error exporting logs: {e}")
            return False
    
    def get_log_stats(self) -> dict:
        """Get logging statistics"""
        try:
            log_config = self.config.get('logging', {})
            log_file = log_config.get('file', 'logs/bot.log')
            
            stats = {
                'log_file': log_file,
                'file_exists': os.path.exists(log_file),
                'file_size': 0,
                'total_lines': 0,
                'error_count': 0,
                'warning_count': 0,
                'info_count': 0
            }
            
            if os.path.exists(log_file):
                stats['file_size'] = os.path.getsize(log_file)
                
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        stats['total_lines'] += 1
                        if ' - ERROR - ' in line:
                            stats['error_count'] += 1
                        elif ' - WARNING - ' in line:
                            stats['warning_count'] += 1
                        elif ' - INFO - ' in line:
                            stats['info_count'] += 1
            
            return stats
            
        except Exception as e:
            self.error(f"Error getting log stats: {e}")
            return {}
    
    def cleanup_old_logs(self, days: int = 30):
        """Clean up old log files"""
        try:
            log_config = self.config.get('logging', {})
            log_file = log_config.get('file', 'logs/bot.log')
            log_dir = os.path.dirname(log_file)
            
            if not os.path.exists(log_dir):
                return
            
            cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
            
            for file_name in os.listdir(log_dir):
                file_path = os.path.join(log_dir, file_name)
                if (os.path.isfile(file_path) and 
                    file_name.endswith('.log') and
                    os.path.getmtime(file_path) < cutoff_time):
                    
                    os.remove(file_path)
                    self.info(f"Removed old log file: {file_name}")
            
        except Exception as e:
            self.error(f"Error cleaning up old logs: {e}")
    
    def set_log_level(self, level: str):
        """Change log level dynamically"""
        try:
            if self.logger:
                self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
                self.info(f"Log level changed to {level.upper()}")
        except Exception as e:
            self.error(f"Error setting log level: {e}")
