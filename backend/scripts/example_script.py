"""
Example script for KVTM Auto
This demonstrates how to create a simple script that throws exceptions for error handling
"""

from src.core import adb, image
from src.models import Device, GameOptions


def main(device: Device, game_options: GameOptions, loop_index: int = 0):
    """
    Main script function - this is required for all scripts
    
    Args:
        device: Device model containing device information
        game_options: GameOptions model containing game configuration
        loop_index: Current loop iteration (0-based)
    """
    
    device_id = device.device_id
    
    # Step 1: Capture screen
    screen_size = adb.get_screen_size(device_id)
    screenshot_bytes = adb.capture_screen(device_id)
    
    # Step 2: Load template image
    template_bytes = image.read_asset_image_bytes('test.png')
    
    # Step 3: Find template in screenshot
    coordinates = image.get_coordinate(screenshot_bytes, template_bytes, threshold=0.8)
    
    if not coordinates:
        raise RuntimeError("Template not found in screenshot")
        
    x, y = coordinates
    
    # Step 4: Click on found coordinates
    adb.tap(x, y, device_id)
    
    return {
        "success": True,
        "message": "Example script completed - template found and clicked",
        "coordinates": coordinates
    }