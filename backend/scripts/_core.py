"""
Core shared utilities for KVTM Auto scripts
Provides common functions and utilities that can be used by all scripts
"""

import time
from typing import Tuple, Optional
from src.models import Device, GameOptions


def wait_and_tap(x: int, y: int, device_id: str, wait_seconds: float = 1.0):
    """
    Wait for specified seconds then tap at coordinates
    
    Args:
        x: X coordinate
        y: Y coordinate 
        device_id: Device ID
        wait_seconds: Seconds to wait before tapping
    """
    time.sleep(wait_seconds)
    # adb will be injected by executor
    adb.tap(x, y, device_id)


def find_and_tap_template(screenshot_bytes: bytes, template_name: str, device_id: str, 
                         threshold: float = 0.8, wait_after: float = 1.0) -> bool:
    """
    Find template in screenshot and tap if found
    
    Args:
        screenshot_bytes: Screenshot data
        template_name: Template image filename (e.g., 'button.png')
        device_id: Device ID
        threshold: Match threshold (0.0 to 1.0)
        wait_after: Seconds to wait after tapping
        
    Returns:
        True if template found and tapped, False otherwise
    """
    # image will be injected by executor
    template_bytes = image.read_asset_image_bytes(template_name)
    coordinates = image.get_coordinate(screenshot_bytes, template_bytes, threshold=threshold)
    
    if coordinates:
        x, y = coordinates
        adb.tap(x, y, device_id)
        if wait_after > 0:
            time.sleep(wait_after)
        return True
    return False


def capture_and_find_template(device_id: str, template_name: str, 
                            threshold: float = 0.8) -> Optional[Tuple[int, int]]:
    """
    Capture screen and find template coordinates
    
    Args:
        device_id: Device ID
        template_name: Template image filename
        threshold: Match threshold
        
    Returns:
        Tuple of (x, y) coordinates if found, None otherwise
    """
    screenshot_bytes = adb.capture_screen(device_id)
    template_bytes = image.read_asset_image_bytes(template_name)
    return image.get_coordinate(screenshot_bytes, template_bytes, threshold=threshold)


def retry_until_success(func, max_attempts: int = 3, delay: float = 2.0, *args, **kwargs):
    """
    Retry a function until it succeeds or max attempts reached
    
    Args:
        func: Function to retry
        max_attempts: Maximum number of attempts
        delay: Delay between attempts
        *args, **kwargs: Arguments to pass to function
        
    Returns:
        Function result if successful
        
    Raises:
        Last exception if all attempts fail
    """
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_attempts - 1:
                time.sleep(delay)
            
    raise last_exception


def wait_for_template(device_id: str, template_name: str, timeout: float = 30.0, 
                     check_interval: float = 2.0, threshold: float = 0.8) -> Optional[Tuple[int, int]]:
    """
    Wait for template to appear on screen
    
    Args:
        device_id: Device ID
        template_name: Template image filename
        timeout: Maximum seconds to wait
        check_interval: Seconds between checks
        threshold: Match threshold
        
    Returns:
        Tuple of (x, y) coordinates if found within timeout, None otherwise
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        coordinates = capture_and_find_template(device_id, template_name, threshold)
        if coordinates:
            return coordinates
        time.sleep(check_interval)
    
    return None


def log_step(step_name: str, device_id: str, success: bool = True, message: str = ""):
    """
    Log a script step for debugging
    
    Args:
        step_name: Name of the step
        device_id: Device ID
        success: Whether step was successful
        message: Additional message
    """
    status = "SUCCESS" if success else "FAILED"
    full_message = f"[{step_name}] {status}"
    if message:
        full_message += f" - {message}"
    
    # db will be injected by executor
    db.write_log(device_id, full_message, "ERROR" if not success else "INFO")


# Common game actions
def close_and_open_app(package_name: str, device_id: str, wait_time: float = 10.0):
    """
    Close and reopen an application
    
    Args:
        package_name: App package name
        device_id: Device ID
        wait_time: Time to wait after opening
    """
    adb.close_app(package_name, device_id)
    time.sleep(2)
    adb.press_key(device_id, "KEYCODE_HOME")
    time.sleep(1)
    adb.open_app(package_name, device_id)
    time.sleep(wait_time)


def swipe_screen(device_id: str, direction: str = "up", distance: int = 500, duration: int = 1000):
    """
    Swipe screen in specified direction
    
    Args:
        device_id: Device ID
        direction: Direction to swipe ("up", "down", "left", "right")
        distance: Distance to swipe in pixels
        duration: Duration of swipe in milliseconds
    """
    screen_size = adb.get_screen_size(device_id)
    if not screen_size:
        raise RuntimeError("Could not get screen size")
    
    width, height = screen_size
    center_x, center_y = width // 2, height // 2
    
    if direction == "up":
        start_x, start_y = center_x, center_y + distance // 2
        end_x, end_y = center_x, center_y - distance // 2
    elif direction == "down":
        start_x, start_y = center_x, center_y - distance // 2
        end_x, end_y = center_x, center_y + distance // 2
    elif direction == "left":
        start_x, start_y = center_x + distance // 2, center_y
        end_x, end_y = center_x - distance // 2, center_y
    elif direction == "right":
        start_x, start_y = center_x - distance // 2, center_y
        end_x, end_y = center_x + distance // 2, center_y
    else:
        raise ValueError(f"Invalid direction: {direction}")
    
    adb.swipe(start_x, start_y, end_x, end_y, duration, device_id)