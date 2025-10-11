import os
import time
from enum import Enum
from functools import wraps

from adbutils import AdbError, AdbClient

from .image_controller import image_controller


def retry_on_error(max_attempts=3, delay=0.5, return_value=None):
    """
    Decorator to retry a function on error with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts (default: 3)
        delay: Initial delay between attempts in seconds (default: 0.5)
        return_value: Value to return on final failure (default: None)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (
                    IOError,
                    AdbError,
                ):
                    current_delay = delay * (2**attempt)  # Exponential backoff
                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                    else:
                        return return_value
                except Exception as e:
                    print(
                        f"{func.__name__} encountered unexpected error: {e.__class__.__name__}: {e}"
                    )
                    return return_value
            return return_value

        return wrapper

    return decorator


class EventCode(Enum):
    EV_SYN = 0
    EV_ABS = 3
    ABS_MT_POSITION_X = 53
    ABS_MT_POSITION_Y = 54
    SYN_REPORT = 0
    SYN_MT_REPORT = 2


class KeyCode(Enum):
    UNKNOWN = 0
    SOFT_LEFT = 1
    SOFT_RIGHT = 2
    HOME = 3
    BACK = 4
    CALL = 5
    ENDCALL = 6
    KEY_0 = 7
    KEY_1 = 8
    KEY_2 = 9
    KEY_3 = 10
    KEY_4 = 11
    KEY_5 = 12
    KEY_6 = 13
    KEY_7 = 14
    KEY_8 = 15
    KEY_9 = 16
    STAR = 17
    POUND = 18
    DPAD_UP = 19
    DPAD_DOWN = 20
    DPAD_LEFT = 21
    DPAD_RIGHT = 22
    DPAD_CENTER = 23
    VOLUME_UP = 24
    VOLUME_DOWN = 25
    POWER = 26
    CAMERA = 27
    CLEAR = 28
    # ....
    COMMA = 55
    PERIOD = 56
    ALT_LEFT = 57
    ALT_RIGHT = 58
    SHIFT_LEFT = 59
    SHIFT_RIGHT = 60
    TAB = 61
    SPACE = 62
    ENTER = 66
    DEL = 67
    ESC = 111


class AdbController:
    # Assets directory relative to this file's location
    ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")

    def __init__(self, serial):
        # Connect to ADB server at 127.0.0.1:5037 (standard port)
        self.adb = AdbClient(host="127.0.0.1", port=5037)
        self.device = self.adb.device(serial=serial)
        self.serial = serial
        self.screen_width, self.screen_height = self._get_screen_size()

        # Default touch device path for most emulators/devices
        self.touch_device = "/dev/input/event2"
        # BlueStacks Virtual Touch uses 0-32767 coordinate range
        self.device_max_x = 32767
        self.device_max_y = 32767

    def _get_screen_size(self):
        """Get device screen size using adbutils"""
        try:
            width, height = self.device.window_size()
            return width, height
        except Exception:
            # Default fallback values
            return 1080, 1920

    def _resolve_asset_path(self, image_path):
        """Resolve asset path. If just filename, prepend assets directory."""
        if os.path.isabs(image_path) or os.sep in image_path:
            # Already a path (absolute or relative with directory)
            return image_path
        else:
            # Just a filename, look in assets directory
            return os.path.join(self.ASSETS_DIR, image_path)

    def _convert_to_device_coords(self, screen_x, screen_y):
        """Convert percentage coordinates (0.0-1.0) to device coordinates for BlueStacks Virtual Touch"""
        device_x = int(screen_x * self.device_max_x)
        device_y = int(screen_y * self.device_max_y)
        return device_x, device_y

    def _pixel_to_percent(self, x, y):
        """Convert pixel coordinates to percentage coordinates (0.0-1.0)"""
        percent_x = x / self.screen_width
        percent_y = y / self.screen_height
        return percent_x, percent_y

    @retry_on_error(return_value=False)
    def tap(self, x, y):
        """Simulate a tap at (x, y) using adbutils"""
        self.device.click(x, y)
        return True

    @retry_on_error()
    def capture_screen(self):
        """Capture device screen as PNG bytes using adbutils screenshot"""
        import io

        # Use built-in screenshot method which returns PIL.Image
        pil_image = self.device.screenshot()

        # Convert PIL Image to PNG bytes for image_controller
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        return buffer.getvalue()

    @retry_on_error()
    def find_image_on_screen(self, template_path, threshold=0.9):
        """Find template image on screen using bytes-based approach. Returns percentage coordinates (0.0-1.0)."""
        screen_bytes = self.capture_screen()
        template_bytes = image_controller.read_asset_image_bytes(template_path)
        coords = image_controller.get_coordinate(
            screen_bytes, template_bytes, threshold
        )
        if coords:
            # Convert pixel coordinates to percentage
            return self._pixel_to_percent(coords[0], coords[1])
        raise IOError(f"Image '{template_path}' not found on screen")

    @retry_on_error(return_value=False)
    def click_image(self, template_path, threshold=0.9):
        """Click on a template image found on screen using bytes-based approach"""
        screen_bytes = self.capture_screen()
        template_bytes = image_controller.read_asset_image_bytes(template_path)
        coords = image_controller.get_coordinate(
            screen_bytes, template_bytes, threshold
        )

        if coords:
            self.tap(*coords)
            return True
        raise IOError(f"Image '{template_path}' not found on screen")

    @retry_on_error(return_value=False)
    def click_text(self, target_text, lang="eng"):
        """Click on text found on screen using bytes-based approach"""
        screen_bytes = self.capture_screen()
        coords = image_controller.find_text_in_image_bytes(
            screen_bytes, target_text, lang
        )
        if coords:
            self.tap(*coords)
            return True
        raise IOError(f"Text '{target_text}' not found on screen")

    @retry_on_error(return_value=False)
    def press_key(self, keycode):
        """Press a key using Android keycode via adbutils"""
        self.device.keyevent(str(keycode))
        return True

    @retry_on_error(return_value=False)
    def close_app(self, package_name: str):
        """Force stop an app by package name using adbutils"""
        self.device.app_stop(package_name)
        return True

    @retry_on_error(return_value=False)
    def open_app(self, package_name: str, activity: str = None):
        """Open an app by package name using adbutils"""
        self.device.app_start(package_name, activity)
        return True

    def sleep(self, duration):
        """Sleep for a given duration in seconds"""
        time.sleep(duration)

    @retry_on_error(return_value=False)
    def swipe(self, x1, y1, x2, y2, duration=300):
        """
        Swipe from (x1, y1) to (x2, y2) using adbutils

        Args:
            x1, y1: Starting coordinates
            x2, y2: Ending coordinates
            duration: Duration of swipe in milliseconds (default: 300)
        """
        # adbutils.swipe() expects duration in seconds
        self.device.swipe(x1, y1, x2, y2, duration / 1000)
        return True

    # High-level gesture methods

    @retry_on_error(return_value=False)
    def drag(self, points):
        """
        Smooth drag through a series of points using sendevent.

        Args:
            points: List of (x, y) coordinate tuples

        Examples:
            # Drag through multiple points
            controller.drag([(100, 100), (300, 300)])

            # Complex path
            path = [(100, 100), (200, 100), (300, 200), (400, 300)]
            controller.drag(path)
        """
        if not isinstance(points, (list, tuple)):
            raise ValueError("Points must be a list or tuple of coordinate pairs")

        if len(points) < 2:
            raise ValueError("Need at least 2 points for drag gesture")

        # Validate all points first
        for point in points:
            if not isinstance(point, (list, tuple)) or len(point) != 2:
                raise ValueError(f"Invalid point format: {point}")

        # Build single shell command with all sendevent operations
        device = self.touch_device
        commands = []

        for point in points:
            device_x, device_y = self._convert_to_device_coords(point[0], point[1])

            # Touch events for this point
            commands.extend(
                [
                    f"sendevent {device} {EventCode.EV_ABS.value} {EventCode.ABS_MT_POSITION_X.value} {device_x}",
                    f"sendevent {device} {EventCode.EV_ABS.value} {EventCode.ABS_MT_POSITION_Y.value} {device_y}",
                    f"sendevent {device} {EventCode.EV_SYN.value} {EventCode.SYN_MT_REPORT.value} 0",
                    f"sendevent {device} {EventCode.EV_SYN.value} {EventCode.SYN_REPORT.value} 0",
                ]
            )

        # Add release events
        commands.extend(
            [
                f"sendevent {device} {EventCode.EV_SYN.value} {EventCode.SYN_MT_REPORT.value} 0",
                f"sendevent {device} {EventCode.EV_SYN.value} {EventCode.SYN_REPORT.value} 0",
                f"sendevent {device} {EventCode.EV_SYN.value} {EventCode.SYN_MT_REPORT.value} 0",
                f"sendevent {device} {EventCode.EV_SYN.value} {EventCode.SYN_REPORT.value} 0",
            ]
        )

        # Execute single optimized command via adbutils
        full_command = "; ".join(commands)
        self.device.shell(full_command)
        return True
