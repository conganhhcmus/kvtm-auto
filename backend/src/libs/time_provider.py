"""
Time provider utilities for consistent UTC and GMT+7 timestamp handling
"""

from datetime import datetime, timezone, timedelta
from typing import Optional


GMT_PLUS_7 = timezone(timedelta(hours=7))


def utc_now() -> datetime:
    """Get current datetime in UTC timezone"""
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    """Get current datetime in UTC timezone as ISO format string"""
    return utc_now().isoformat()


def utc_now_timestamp() -> float:
    """Get current timestamp in UTC timezone as float (Unix timestamp)"""
    return utc_now().timestamp()


def local_now() -> datetime:
    """Get current datetime in GMT+7 timezone (local time)"""
    return datetime.now(GMT_PLUS_7)


def local_now_iso() -> str:
    """Get current datetime in GMT+7 timezone as ISO format string"""
    return local_now().isoformat()


def local_now_timestamp() -> float:
    """Get current timestamp in GMT+7 timezone as float (Unix timestamp)"""
    return local_now().timestamp()


def format_datetime_local(dt: Optional[datetime] = None) -> str:
    """
    Format datetime to GMT+7 timezone ISO string
    If dt is None, uses current time
    """
    if dt is None:
        dt = local_now()
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc).astimezone(GMT_PLUS_7)
    else:
        dt = dt.astimezone(GMT_PLUS_7)
    
    return dt.isoformat()


def parse_to_local(timestamp_str: str) -> datetime:
    """
    Parse ISO timestamp string and convert to GMT+7
    """
    dt = datetime.fromisoformat(timestamp_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.astimezone(GMT_PLUS_7)


def format_time_for_log() -> str:
    """
    Format current local time as [HH:MM:SS AM/PM] for simple log display
    Example: [12:34:56 PM]
    """
    now = local_now()
    return f"[{now.strftime('%I:%M:%S %p')}]"


def create_log_message(action: str, index: Optional[str] = None) -> str:
    """
    Create formatted log message: [Time]: [Action] [Index]
    
    Args:
        action: The action being performed (e.g., "Run Open Game", "Run Script")
        index: Optional index/count (e.g., "5" for "Run Script [5] times")
    
    Returns:
        Formatted log message like "[12:34:56 PM]: Run Script [5] times"
    """
    time_str = format_time_for_log()
    
    if index:
        return f"{time_str}: {action} [{index}]"
    else:
        return f"{time_str}: {action}"