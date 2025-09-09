"""
Open game script for KVTM Auto
Handles opening the game application with simple logging
"""

import time
import sys
import os

# Add the src directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from libs import adb
from _core import KeyCode
from _core import write_log, log_run_open_game

SCRIPT_META = {
    "id": "open_game",
    "name": "Open Game",
    "order": 0,
    "recommend": False,
    "description": "Opens the game application and waits for it to load"
}


def main(device, game_options, context):
    """
    Opens the game application on the device
    
    Args:
        device: Device model containing device information
        game_options: GameOptions model containing game configuration
        context: ScriptContext object for logging and control
    
    Returns:
        Dict with execution results
    """
    
    log_run_open_game(device.id)
    
    game_package = "vn.kvtm.js"
    
    # Close the app if it's running
    write_log(device.id, "Closing app if running")
    adb.close_app(game_package, device.id)

    # Press HOME key to ensure we're at the home screen
    write_log(device.id, "Pressing HOME key")
    adb.press_key(KeyCode.HOME.value, device.id)

    # Open the game application
    write_log(device.id, "Opening game")
    adb.open_app(game_package, device.id)
    
    # Wait for game to load (configurable timing)
    wait_time = getattr(game_options, 'game_load_wait', 5)
    write_log(device.id, "Waiting for game", f"{wait_time}s")
    time.sleep(wait_time)
    
    return {
        "success": True,
        "message": "Game opened successfully"
    }