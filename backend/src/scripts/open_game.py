"""
Open game script for KVTM Auto
Handles opening the game application with simple logging
"""
import sys
import json
import argparse
from ._core import Core
from ..libs.adb import KeyCode
from ..models.device import Device
from ..models.script import GameOptions

SCRIPT_META = {
    "id": "open_game",
    "name": "Open Game",
    "order": 0,
    "recommend": False,
    "description": "Opens the game application and waits for it to load"
}


def main(device: Device, game_options: GameOptions):
    """
    Opens the game application on the device using Core helper

    Args:
        device: Device model containing device information
        game_options: GameOptions model containing game configuration

    Returns:
        Dict with execution results
    """

    # Create core helper with device.id
    core = Core(device.id)
    
    core.log("Run Open Game")
    
    game_package = "vn.kvtm.js"
    
    # Close the app if it's running
    close_result = core.close_app(game_package)
    if isinstance(close_result, dict) and not close_result.get("success", True):
        return close_result

    # Press HOME key to ensure we're at the home screen
    home_result = core.press_key(KeyCode.HOME.value)
    if isinstance(home_result, dict) and not home_result.get("success", True):
        return home_result

    # Open the game application
    open_result = core.open_app(game_package)
    if isinstance(open_result, dict) and not open_result.get("success", True):
        return open_result
    
    core.find_and_click("game.png")
    core.sleep(10)

    game_loaded = core.close_all_popup() and core.wait_for_image("shop-gem.png", 5)
    
    if game_loaded:
        return {
            "success": True,
            "message": f"{SCRIPT_META['name']} successfully"
        }
    else:
        return {
            "success": False,
            "message": f"{SCRIPT_META['name']} failure"
        }


if __name__ == "__main__":
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
        result = main(device, game_options)
        
        # Exit with appropriate code
        if result.get("success", False):
            sys.exit(0)
        else:
            print(f"Script failed: {result.get('message', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"ERROR: Script execution failed: {e}", file=sys.stderr)
        sys.exit(1)