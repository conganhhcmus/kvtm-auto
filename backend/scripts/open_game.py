"""
Open game script for KVTM Auto
This script handles opening the game application before running other scripts
"""

import time
from src.core import adb, image
from src.models import Device, GameOptions

SCRIPT_META = {
    "id": "open_game",
    "name": "Open Game",
    "order": 0,
    "recommend": False,
    "description": "Opens the game application and verifies it loaded successfully"
}

def main(device: Device, game_options: GameOptions, loop_index: int = 0):
    """
    Opens the game application on the device
    
    Args:
        device: Device model containing device information
        game_options: GameOptions model containing game configuration
        loop_index: Current loop iteration (0-based)
    """
    
    device_id = device.device_id

    game_package = "vn.kvtm.js"

    adb.close_app(game_package, device_id)

    adb.press_key(device_id, "KEYCODE_HOME")

    adb.open_app(game_package, device_id)
    
    # Step 3: Wait for game to load
    time.sleep(10)
    
    # Step 4: Verify game is open (take screenshot to verify)
    screenshot_bytes = adb.capture_screen(device_id)

    template_bytes = image.read_asset_image_bytes('test.png')

    coordinates = image.get_coordinate(screenshot_bytes, template_bytes, threshold=0.8)

    if not coordinates:
        raise RuntimeError("Game not found in screenshot")
    
    return {
        "success": True,
        "message": "Game opened successfully"
    }