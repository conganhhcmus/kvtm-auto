"""
Core shared utilities for KVTM Auto scripts
Provides common functions and utilities that can be used by all scripts
"""

import sys
import time
from typing import Optional

from ..libs.adb import adb, KeyCode
from ..libs.image import image
from ..libs.time_provider import time_provider
from ..service.database import db
from ..models.device import DeviceStatus


class Core:
    """
    Core automation class that provides clean API for all script operations
    Reduces device_id repetition with enhanced ADB shortcuts
    """

    def __init__(self, device_id: str):
        self.device_id = device_id

    def _is_stop(self):
        """Check if script should stop execution by checking device status"""
        if not self.device_id:
            return False

        device = db.get_device(self.device_id)
        if not device:
            return True  # Stop if device doesn't exist

        # Stop if device status is not RUNNING
        return device.device_status != DeviceStatus.RUNNING.value

    def log(self, action: str, index: Optional[str] = None):
        """Write script formatted log entry: [Time]: [Action] [Index]"""
        # Create formatted log message
        log_message = time_provider.create_log_message(action, index)
    
        # Always output to console for shell/subprocess visibility
        print(log_message, file=sys.stdout, flush=True)
    
        # Write to database
        db.write_script_log(self.device_id, log_message)

    def run(self, func):
        """Execute callable with automatic stop checking"""
        if self._is_stop():
            self.log(self.device_id, "Action interrupted", "execution stopped")
            return False

        return func()

    def sleep(self, seconds:float):
        if seconds <= 0:
            return

        # For short sleeps, just sleep normally
        if seconds <= 1.0:
            time.sleep(seconds)
            return

        # For longer sleeps, check stop signal periodically
        check_interval = 0.5
        elapsed = 0.0

        while elapsed < seconds:
            if self._is_stop():
                self.log("Sleep interrupted", "execution stopped")
                break

            sleep_time = min(check_interval, seconds - elapsed)
            time.sleep(sleep_time)
            elapsed += sleep_time
    
    # Image detection methods
    def find_and_click(self, asset_name: str, timeout: float = 10.0) -> bool:
        """Find and click an asset image"""
        """
        Find an asset image on screen and click it if found

        Args:
            asset_name: Name of asset file (e.g., 'game.png')
            device_id: Device ID for logging and stop checking
            timeout: Maximum time to search for image

        Returns:
            True if image found and clicked, False otherwise
        """
        self.log("Looking for", asset_name)

        start_time = time.time()

        while time.time() - start_time < timeout:
            if self._is_stop():
                return False

            # Capture screen and get template
            screen_result = self.capture_screen()
            if isinstance(screen_result, dict) and not screen_result.get("success", True):
                return False

            try:
                template_bytes = image.read_asset_image_bytes(asset_name)
                coordinates = image.get_coordinate(screen_result, template_bytes)

                if coordinates:
                    x, y = coordinates
                    # self._log(f"Found {asset_name} at", f"({x}, {y})")
                    click_result = self.tap(x, y)
                    if isinstance(click_result, dict) and not click_result.get("success", True):
                        return False
                    # self._log("Clicked", asset_name)
                    return True

            except FileNotFoundError:
                self.log("Asset not found", asset_name)
                return False
            except Exception as e:
                self.log(f"Error finding {asset_name}", str(e))
                return False

            self.sleep(0.5)

        self.log("Timeout looking for", asset_name)
        return False

    def wait_for_image(self, asset_name: str, timeout: float = 10.0) -> bool:
        """Wait for an asset image to appear"""
        """
        Wait for an asset image to appear on screen

        Args:
            asset_name: Name of asset file (e.g., 'game.png')
            device_id: Device ID for logging and stop checking
            timeout: Maximum time to wait for image

        Returns:
            True if image found within timeout, False otherwise
        """
        self.log("Waiting for", asset_name)

        start_time = time.time()

        while time.time() - start_time < timeout:
            if self._is_stop():
                return False

            # Capture screen and get template
            screen_result = self.capture_screen()
            if isinstance(screen_result, dict) and not screen_result.get("success", True):
                return False

            try:
                template_bytes = image.read_asset_image_bytes(asset_name)
                coordinates = image.get_coordinate(screen_result, template_bytes)

                if coordinates:
                    # self._log("Found", asset_name)
                    return True

            except FileNotFoundError:
                self.log("Asset not found", asset_name)
                return False
            except Exception as e:
                self.log(f"Error waiting for {asset_name}", str(e))
                return False

            self.sleep(0.5)

        self.log("Timeout waiting for", asset_name)
        return False


    def click_if_exists(self, asset_name: str) -> bool:
        """Click an asset image if it exists"""
        """ 
        Click an asset image if it exists on screen, continue if not found

        Args:
            asset_name: Name of asset file (e.g., 'game.png')
            device_id: Device ID for logging and stop checking

        Returns:
            True if image found and clicked, False if not found (not an error)
        """
        if self._is_stop():
            return False

        # Capture screen and get template
        screen_result = self.capture_screen()
        if isinstance(screen_result, dict) and not screen_result.get("success", True):
            return False

        try:
            template_bytes = image.read_asset_image_bytes(asset_name)
            coordinates = image.get_coordinate(screen_result, template_bytes)

            if coordinates:
                x, y = coordinates
                # self._log("Found and clicking", asset_name)
                click_result = self.tap(x, y)
                if isinstance(click_result, dict) and not click_result.get("success", True):
                    return False
                return True
            else:
                self.log("Not found", asset_name)
                return False

        except FileNotFoundError:
            self.log("Asset not found", asset_name)
            return False
        except Exception as e:
            self.log(f"Error checking {asset_name}", str(e))
            return False
    
    # ADB shortcut methods
    def tap(self, x: int, y: int):
        """Tap at specific coordinates with stop checking"""
        return self.run(lambda: adb.tap(x, y, self.device_id))
    
    def tap_by_percent(self, x: int, y: int):
        """Tap at specific coordinates with stop checking"""
        w, h = self.get_screen_size()
        x = round(w * x / 100)
        y = round(h * y / 100)
        return self.run(lambda: adb.tap(x, y, self.device_id))
    
    def press_key(self, keycode):
        """Press a key using Android keycode with stop checking"""
        return self.run(lambda: adb.press_key(keycode, self.device_id))
    
    def open_app(self, package_name: str):
        """Open an app by package name with stop checking"""
        return self.run(lambda: adb.open_app(package_name, self.device_id))
    
    def close_app(self, package_name: str):
        """Close an app by package name with stop checking"""
        return self.run(lambda: adb.close_app(package_name, self.device_id))
    
    def capture_screen(self):
        """Capture device screen with stop checking"""
        return self.run(lambda: adb.capture_screen(self.device_id))
    
    def get_screen_size(self):
        """Get device screen dimensions with stop checking"""
        return self.run(lambda: adb.get_screen_size(self.device_id))
    
    def close_all_popup(self):
        for _ in range(10):
            self.press_key(KeyCode.BACK.value)
            self.sleep(0.2)
    
        return self.click_if_exists("o-lai.png")
    
    def fail_result(self, message: str):
        return {
            "success": False,
            "message": message
        }
    
    def success_result(self, message: str):
        return {
            "success": True,
            "message": message
        }
    
    # auto core func
    def open_chest(self):
        can_open_chest = self.wait_for_image("ruong-bau.png", timeout = 3)

        if can_open_chest:
            self.tap_by_percent(35.0, 22.22)
            self.sleep(0.5)
            self.tap_by_percent(35.0, 22.22)
            self.find_and_click("ruong-go.png", timeout = 3)
            self.find_and_click("mo-ngay.png", timeout = 3)
            for _ in range(10):
                self.tap_by_percent(50.0, 62.22)
                self.sleep(0.2)
            self.close_all_popup()
        
        return self.success_result("Open chest successfully")