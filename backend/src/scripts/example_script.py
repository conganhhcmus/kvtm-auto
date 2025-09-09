"""
Example script for KVTM Auto
Demonstrates simple script usage with new logging format
"""

import time
import sys
import os

# Add the src directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from libs import adb
from _core import KeyCode
from _core import write_log, log_script_started

SCRIPT_META = {
    "id": "example_script",
    "name": "Example Script",
    "order": 1,
    "recommend": True,
    "description": "Example script demonstrating simple core module usage"
}


def main(device, game_options, context):
    """
    Main script function for CLI execution
    
    Args:
        device: Device model containing device information
        game_options: GameOptions model containing game configuration
        context: ScriptContext object for logging and control
    
    Returns:
        Dict with execution results
    """
    
    log_script_started(device.id, "Example Script")
    
    write_log(device.id, "Performing example operations")
    write_log(device.id, "KeyCode HOME", str(KeyCode.HOME.value))
    
    # Simulate some work
    write_log(device.id, "Waiting", "1s")
    time.sleep(1)
    
    write_log(device.id, "Script completed")
    
    return {
        "success": True,
        "message": "Example script completed successfully"
    }