"""
Core shared utilities for KVTM Auto scripts
Provides common functions and utilities that can be used by all scripts
"""

import sys
import os
from typing import Tuple, Optional

# Add the src directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from libs import adb, image

# Simple logging function for CLI scripts
def write_log(device_id: str, action: str, index: Optional[str] = None):
    """Write simple formatted log entry: [Time]: [Action] [Index]"""
    import sys
    from typing import Optional
    
    # Import the time formatting utilities
    try:
        from libs.time_provider import create_log_message
    except ImportError:
        # Fallback if import fails
        from datetime import datetime
        def create_log_message(action: str, index: Optional[str] = None) -> str:
            now = datetime.now()
            time_str = f"[{now.strftime('%I:%M:%S %p')}]"
            if index:
                return f"{time_str}: {action} [{index}]"
            else:
                return f"{time_str}: {action}"
    
    # Create formatted log message
    log_message = create_log_message(action, index)
    
    # Always output to console for shell/subprocess visibility
    print(log_message, file=sys.stdout, flush=True)
    
    # Try to also write to database if available
    try:
        from service.database import Database
        db = Database()
        # Store the formatted message directly in the database
        db.write_simple_log(device_id, log_message)
    except Exception:
        # Database unavailable - console output is sufficient
        pass


# Convenience functions for common log actions
def log_run_open_game(device_id: str):
    """Log: [Time]: Run Open Game"""
    write_log(device_id, "Run Open Game")


def log_run_script(device_id: str, times: int):
    """Log: [Time]: Run Script [x] times"""
    write_log(device_id, "Run Script", f"{times} times")


def log_script_started(device_id: str, script_name: str):
    """Log: [Time]: Script started [script_name]"""
    write_log(device_id, "Script started", script_name)


def log_script_completed(device_id: str):
    """Log: [Time]: Script completed"""
    write_log(device_id, "Script completed")


def log_loop_iteration(device_id: str, current: int, total: int):
    """Log: [Time]: Loop [x/y]"""
    write_log(device_id, "Loop", f"{current}/{total}")


def log_waiting(device_id: str, seconds: float):
    """Log: [Time]: Waiting [x]s"""
    write_log(device_id, "Waiting", f"{seconds}s")


from enum import Enum

class KeyCode(Enum):
    UNKNOWN         = 0
    SOFT_LEFT       = 1
    SOFT_RIGHT      = 2
    HOME            = 3
    BACK            = 4
    CALL            = 5
    ENDCALL         = 6
    KEY_0           = 7
    KEY_1           = 8
    KEY_2           = 9
    KEY_3           = 10
    KEY_4           = 11
    KEY_5           = 12
    KEY_6           = 13
    KEY_7           = 14
    KEY_8           = 15
    KEY_9           = 16
    STAR            = 17
    POUND           = 18
    DPAD_UP         = 19
    DPAD_DOWN       = 20
    DPAD_LEFT       = 21
    DPAD_RIGHT      = 22
    DPAD_CENTER     = 23
    VOLUME_UP       = 24
    VOLUME_DOWN     = 25
    POWER           = 26
    CAMERA          = 27
    CLEAR           = 28
    #....
    COMMA           = 55
    PERIOD          = 56
    ALT_LEFT        = 57
    ALT_RIGHT       = 58
    SHIFT_LEFT      = 59
    SHIFT_RIGHT     = 60
    TAB             = 61
    SPACE           = 62
    ENTER           = 66
    DEL             = 67
    ESC             = 111