"""
Open game script for KVTM Auto
Handles opening the game application with simple logging
"""
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
    if not close_result:
        return core.fail_result("Cannot close app by package name")

    # Press HOME key to ensure we're at the home screen
    home_result = core.press_key(KeyCode.HOME.value)
    if not home_result:
        return core.fail_result("Cannot press HOME key")

    # Open the game application
    open_result = core.open_app(game_package)
    if not open_result:
        return core.fail_result("Cannot open app by package name")
    
    core.find_and_click("game.png")
    core.sleep(10)

    game_loaded = core.close_all_popup() and core.wait_for_image("shop-gem.png", 5)
    
    if game_loaded:
        return core.success_result(f"{SCRIPT_META['name']} successfully")
    else:
        return core.fail_result(f"{SCRIPT_META['name']} failure")