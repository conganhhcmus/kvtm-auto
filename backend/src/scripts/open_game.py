"""
Open game script for KVTM Auto
Handles opening the game application with simple logging
"""

import time

from ..libs.adb import adb
from ._core import KeyCode
from ._core import write_log, log_run_open_game, log_waiting, check_should_stop

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
        context: ScriptContext object for logging and control (None for CLI)
    
    Returns:
        Dict with execution results
    """
    
    log_run_open_game(device.id)
    
    # Check if we should stop
    if check_should_stop(context):
        return {"success": False, "message": "Script stopped by user"}
    
    game_package = "vn.kvtm.js"
    
    # Close the app if it's running
    write_log(device.id, "Closing app if running")
    adb.close_app(game_package, device.id)

    # Check stop signal
    if check_should_stop(context):
        return {"success": False, "message": "Script stopped by user"}

    # Press HOME key to ensure we're at the home screen
    write_log(device.id, "Pressing HOME key")
    adb.press_key(KeyCode.HOME.value, device.id)

    # Check stop signal
    if check_should_stop(context):
        return {"success": False, "message": "Script stopped by user"}

    # Open the game application
    write_log(device.id, "Opening game")
    adb.open_app(game_package, device.id)
    
    # Wait for game to load (configurable timing) with context-aware sleep
    wait_time = getattr(game_options, 'game_load_wait', 5)
    log_waiting(device.id, wait_time, context)
    
    # Final check
    if check_should_stop(context):
        return {"success": False, "message": "Script stopped by user"}
    
    return {
        "success": True,
        "message": "Game opened successfully"
    }


if __name__ == "__main__":
    import sys
    import json
    import argparse
    from ..models.device import Device
    from ..models.script import GameOptions
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Open Game Script")
    parser.add_argument("--device-id", required=True, help="Device ID")
    parser.add_argument("--options", required=True, help="Game options JSON")
    parser.add_argument("--loop-index", type=int, default=0, help="Loop index")
    
    args = parser.parse_args()
    
    try:
        # Parse game options
        options_data = json.loads(args.options)
        game_options = GameOptions(**options_data)
        
        # Create device object
        device = Device(id=args.device_id, name=f"Device {args.device_id}")
        
        # Execute script
        result = main(device, game_options, None)
        
        # Exit with appropriate code
        if result.get("success", False):
            sys.exit(0)
        else:
            print(f"Script failed: {result.get('message', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"ERROR: Script execution failed: {e}", file=sys.stderr)
        sys.exit(1)