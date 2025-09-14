"""
Example script for KVTM Auto
Demonstrates simple script usage with new logging format
"""

from ._core import Core
from ..models.device import Device
from ..models.script import GameOptions

SCRIPT_META = {
    "id": "auto-vai-xanh-la",
    "name": "Auto Vải Xanh Lá",
    "order": 1,
    "recommend": True,
    "description": "Sản xuất vải xanh lá"
}


def main(device: Device, game_options: GameOptions):
    """
    Main script function for both CLI and direct execution

    Args:
        device: Device model containing device information
        game_options: GameOptions model containing game configuration

    Returns:
        Dict with execution results
    """

    # Create core helper with device.id
    core = Core(device.id)
    
    if game_options.open_chest:
        core.open_chest()
    
    # Simulate some work with context-aware sleep
    core.sleep(1.0)
    
    return core.success_result(f"{SCRIPT_META['name']} completed successfully")
