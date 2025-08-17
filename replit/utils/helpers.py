"""
Utility helper functions for the Ark Bot Manager
"""

import re
import json
import hashlib
import secrets
import string
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import os
import logging

def sanitize_input(input_str: str, max_length: int = 255) -> str:
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        input_str: Input string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not isinstance(input_str, str):
        return ""
    
    # Remove potential harmful characters
    sanitized = re.sub(r'[<>"\';\\]', '', input_str)
    
    # Limit length
    sanitized = sanitized[:max_length]
    
    # Strip whitespace
    return sanitized.strip()

def validate_discord_id(discord_id: str) -> bool:
    """
    Validate Discord user ID format
    
    Args:
        discord_id: Discord ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(discord_id, str):
        return False
    
    # Discord IDs are typically 17-19 digit numbers
    return re.match(r'^\d{17,19}$', discord_id) is not None

def validate_discord_channel_id(channel_id: str) -> bool:
    """
    Validate Discord channel ID format
    
    Args:
        channel_id: Channel ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    return validate_discord_id(channel_id)  # Same format

def format_points(points: int) -> str:
    """
    Format points with thousands separator
    
    Args:
        points: Point value to format
        
    Returns:
        Formatted points string
    """
    return f"{points:,}"

def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format currency amount
    
    Args:
        amount: Currency amount
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'CAD': 'C$',
        'AUD': 'A$'
    }
    
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:.2f}"

def parse_time_duration(duration_str: str) -> timedelta:
    """
    Parse duration string into timedelta
    
    Args:
        duration_str: Duration string like "1d 2h 30m" or "90m"
        
    Returns:
        Timedelta object
    """
    total_seconds = 0
    
    # Match patterns like 1d, 2h, 30m, 45s
    patterns = {
        r'(\d+)d': 86400,  # days
        r'(\d+)h': 3600,   # hours
        r'(\d+)m': 60,     # minutes
        r'(\d+)s': 1       # seconds
    }
    
    for pattern, multiplier in patterns.items():
        matches = re.findall(pattern, duration_str)
        for match in matches:
            total_seconds += int(match) * multiplier
    
    return timedelta(seconds=total_seconds)

def format_duration(duration: timedelta) -> str:
    """
    Format timedelta into human readable string
    
    Args:
        duration: Timedelta to format
        
    Returns:
        Formatted duration string
    """
    total_seconds = int(duration.total_seconds())
    
    if total_seconds < 60:
        return f"{total_seconds}s"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}m {seconds}s" if seconds else f"{minutes}m"
    elif total_seconds < 86400:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m" if minutes else f"{hours}h"
    else:
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        return f"{days}d {hours}h" if hours else f"{days}d"

def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token
    
    Args:
        length: Length of token to generate
        
    Returns:
        Secure random token
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_password(password: str, salt: str = None) -> tuple:
    """
    Hash a password with salt
    
    Args:
        password: Password to hash
        salt: Optional salt (generated if not provided)
        
    Returns:
        Tuple of (hashed_password, salt)
    """
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Use PBKDF2 for password hashing
    password_hash = hashlib.pbkdf2_hmac('sha256', 
                                      password.encode('utf-8'),
                                      salt.encode('utf-8'), 
                                      100000)  # 100k iterations
    
    return password_hash.hex(), salt

def verify_password(password: str, hashed: str, salt: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        password: Plain text password
        hashed: Hashed password
        salt: Salt used for hashing
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        test_hash, _ = hash_password(password, salt)
        return secrets.compare_digest(test_hash, hashed)
    except:
        return False

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely parse JSON string with fallback
    
    Args:
        json_str: JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """
    Safely serialize object to JSON string
    
    Args:
        obj: Object to serialize
        default: Default JSON string if serialization fails
        
    Returns:
        JSON string or default value
    """
    try:
        return json.dumps(obj, ensure_ascii=False, indent=None, separators=(',', ':'))
    except (TypeError, ValueError):
        return default

def validate_ip_address(ip: str) -> bool:
    """
    Validate IP address format
    
    Args:
        ip: IP address to validate
        
    Returns:
        True if valid, False otherwise
    """
    import ipaddress
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def validate_port(port: Union[str, int]) -> bool:
    """
    Validate port number
    
    Args:
        port: Port to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except (ValueError, TypeError):
        return False

def clean_filename(filename: str) -> str:
    """
    Clean filename by removing invalid characters
    
    Args:
        filename: Filename to clean
        
    Returns:
        Cleaned filename
    """
    # Remove invalid characters for filenames
    invalid_chars = r'<>:"/\\|?*'
    cleaned = re.sub(f'[{re.escape(invalid_chars)}]', '_', filename)
    
    # Remove leading/trailing periods and spaces
    cleaned = cleaned.strip('. ')
    
    # Ensure not empty
    return cleaned if cleaned else 'unnamed'

def ensure_directory_exists(path: str) -> bool:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        path: Directory path
        
    Returns:
        True if directory exists or was created, False otherwise
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError:
        return False

def get_file_size_human(size_bytes: int) -> str:
    """
    Convert file size to human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human readable size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"

def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to maximum length with suffix
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def extract_numbers(text: str) -> List[int]:
    """
    Extract all numbers from text
    
    Args:
        text: Text to extract numbers from
        
    Returns:
        List of extracted numbers
    """
    return [int(match) for match in re.findall(r'\d+', text)]

def is_valid_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def escape_discord_markdown(text: str) -> str:
    """
    Escape Discord markdown characters
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text
    """
    special_chars = ['*', '_', '`', '~', '|', '>', '\\']
    escaped = text
    
    for char in special_chars:
        escaped = escaped.replace(char, f'\\{char}')
    
    return escaped

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks of specified size
    
    Args:
        lst: List to split
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def retry_on_exception(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry function on exception
    
    Args:
        max_retries: Maximum number of retries
        delay: Delay between retries in seconds
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        raise e
                    logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
            
        return wrapper
    return decorator

def rate_limit(calls_per_second: float):
    """
    Decorator to rate limit function calls
    
    Args:
        calls_per_second: Maximum calls per second
    """
    import time
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
            
        return wrapper
    return decorator

class ConfigValidator:
    """Utility class for validating configuration values"""
    
    @staticmethod
    def validate_positive_int(value: Any, default: int = 0) -> int:
        """Validate and convert to positive integer"""
        try:
            num = int(value)
            return num if num > 0 else default
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def validate_port(value: Any, default: int = 8000) -> int:
        """Validate port number"""
        try:
            port = int(value)
            return port if 1 <= port <= 65535 else default
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def validate_string(value: Any, min_length: int = 0, max_length: int = 255, default: str = "") -> str:
        """Validate string length"""
        if not isinstance(value, str):
            return default
        
        value = value.strip()
        if len(value) < min_length or len(value) > max_length:
            return default
        
        return value
    
    @staticmethod
    def validate_boolean(value: Any, default: bool = False) -> bool:
        """Validate boolean value"""
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        
        return bool(value) if value is not None else default

def benchmark_function(func):
    """Decorator to benchmark function execution time"""
    def wrapper(*args, **kwargs):
        import time
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        duration = end_time - start_time
        logging.debug(f"Function {func.__name__} took {duration:.4f} seconds")
        
        return result
    return wrapper
