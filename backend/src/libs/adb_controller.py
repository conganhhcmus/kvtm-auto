import os
import subprocess
import time

from enum import Enum
from .image_controller import image_controller


class EventCode(Enum):
    EV_SYN = 0
    EV_KEY = 1
    EV_ABS = 3
    BTN_TOUCH = 330
    ABS_MT_TRACKING_ID = 57
    ABS_MT_POSITION_X = 53
    ABS_MT_POSITION_Y = 54
    SYN_REPORT = 0


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


class _MultiTouchController:
    """Private controller for managing multiple touch pointers on a device"""

    def __init__(self, serial):
        self.serial = serial
        self.device = (
            "/dev/input/event2"  # Default touch device path for most emulators/devices
        )
        self.pointers = {}  # {pointer_id: (x, y)}
        self.next_pointer_id = 0

    @staticmethod
    def _send_event(serial, device, event_type, event_code, value):
        """Send touch event to device"""
        cmd = [
            "adb",
            "-s",
            serial,
            "shell",
            "sendevent",
            device,
            str(event_type),
            str(event_code),
            str(value),
        ]
        subprocess.run(
            cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

    def add_pointer(self, x, y):
        """Add a new touch pointer at the given coordinates"""
        pointer_id = self.next_pointer_id
        self.next_pointer_id += 1
        self.pointers[pointer_id] = (x, y)
        # Send DOWN event with tracking ID
        self._send_event(self.serial, self.device, EventCode.EV_ABS.value, EventCode.ABS_MT_TRACKING_ID.value, pointer_id)
        self._send_event(self.serial, self.device, EventCode.EV_KEY.value, EventCode.BTN_TOUCH.value, 1)
        self._send_event(self.serial, self.device, EventCode.EV_ABS.value, EventCode.ABS_MT_POSITION_X.value, x)
        self._send_event(self.serial, self.device, EventCode.EV_ABS.value, EventCode.ABS_MT_POSITION_Y.value, y)
        self._send_event(self.serial, self.device, EventCode.EV_SYN.value, EventCode.SYN_REPORT.value, 0)
        return pointer_id

    def move_pointer(self, pointer_id, x, y):
        """Move an existing pointer to new coordinates"""
        if pointer_id not in self.pointers:
            raise ValueError("Invalid pointer ID")
        self.pointers[pointer_id] = (x, y)
        # Send MOVE event
        self._send_event(self.serial, self.device, EventCode.EV_ABS.value, EventCode.ABS_MT_POSITION_X.value, x)
        self._send_event(self.serial, self.device, EventCode.EV_ABS.value, EventCode.ABS_MT_POSITION_Y.value, y)
        self._send_event(self.serial, self.device, EventCode.EV_SYN.value, EventCode.SYN_REPORT.value, 0)

    def remove_pointer(self, pointer_id):
        """Remove a touch pointer"""
        if pointer_id not in self.pointers:
            raise ValueError("Invalid pointer ID")
        x, y = self.pointers[pointer_id]
        # Send UP event
        self._send_event(self.serial, self.device, EventCode.EV_ABS.value, EventCode.ABS_MT_TRACKING_ID.value, -1)
        self._send_event(self.serial, self.device, EventCode.EV_KEY.value, EventCode.BTN_TOUCH.value, 0)
        self._send_event(self.serial, self.device, EventCode.EV_SYN.value, EventCode.SYN_REPORT.value, 0)
        del self.pointers[pointer_id]



class AdbController:
    # Assets directory relative to this file's location
    ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")

    def __init__(self, serial):
        self.serial = serial
        self._multi_touch = _MultiTouchController(self.serial)
        self.screen_width, self.screen_height = self._get_screen_size()

    def _get_screen_size(self):
        """Get device screen size"""
        try:
            result = subprocess.run(
                ["adb", "-s", self.serial, "shell", "wm", "size"],
                capture_output=True,
                check=True,
                text=True,
            )
            # Output format: "Physical size: 1080x1920"
            size_line = result.stdout.strip()
            size_part = size_line.split(": ")[1]  # Get "1080x1920"
            width, height = map(int, size_part.split("x"))
            return width, height
        except Exception as e:
            print(f"Error getting screen size: {e}")
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

    def tap(self, x, y):
        """Simulate a tap at (x, y)"""
        subprocess.run(
            ["adb", "-s", self.serial, "shell", "input", "tap", str(x), str(y)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def tap_by_percent(self, percent_x, percent_y):
        """Simulate a tap at percentage coordinates (0-100)"""
        if not (0 <= percent_x <= 100 and 0 <= percent_y <= 100):
            raise ValueError("Percentage coordinates must be between 0 and 100")

        x = int(self.screen_width * percent_x / 100)
        y = int(self.screen_height * percent_y / 100)
        self.tap(x, y)

    def capture_screen(self):
        """Capture device screen as PNG bytes"""
        result = subprocess.run(
            ["adb", "-s", self.serial, "shell", "screencap", "-p"],
            capture_output=True,
            check=True,
        )
        return result.stdout

    def find_image_on_screen(self, template_path, threshold=0.8, max_retries=3):
        """Find template image on screen using bytes-based approach"""
        for attempt in range(max_retries):
            try:
                screen_bytes = self.capture_screen()
                template_bytes = image_controller.read_asset_image_bytes(template_path)
                coords = image_controller.get_coordinate(
                    screen_bytes, template_bytes, threshold
                )
                if coords:
                    return coords
                if attempt < max_retries - 1:
                    time.sleep(0.5)  # Wait before retry
            except Exception as e:
                print(f"Error in find_image_on_screen (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.5)  # Wait before retry
        return None

    def click_image(self, template_path, threshold=0.8, max_retries=3):
        """Click on a template image found on screen using bytes-based approach"""
        for attempt in range(max_retries):
            try:
                screen_bytes = self.capture_screen()
                template_bytes = image_controller.read_asset_image_bytes(template_path)
                coords = image_controller.get_coordinate(
                    screen_bytes, template_bytes, threshold
                )

                if coords:
                    self.tap(*coords)
                    return True
                if attempt < max_retries - 1:
                    time.sleep(0.5)  # Wait before retry
            except Exception as e:
                print(f"Error in click_image (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.5)  # Wait before retry
        return False

    def click_text(self, target_text, lang="eng", max_retries=3):
        """Click on text found on screen using bytes-based approach"""
        for attempt in range(max_retries):
            try:
                screen_bytes = self.capture_screen()
                coords = image_controller.find_text_in_image_bytes(
                    screen_bytes, target_text, lang
                )
                if coords:
                    self.tap(*coords)
                    return True
                if attempt < max_retries - 1:
                    time.sleep(0.5)  # Wait before retry
            except Exception as e:
                print(f"Error in click_text (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.5)  # Wait before retry
        return False

    def add_pointer(self, x, y):
        """Add a new touch pointer at the given coordinates"""
        return self._multi_touch.add_pointer(x, y)

    def move_pointer(self, pointer_id, x, y):
        """Move an existing pointer to new coordinates"""
        self._multi_touch.move_pointer(pointer_id, x, y)

    def remove_pointer(self, pointer_id):
        """Remove a touch pointer"""
        self._multi_touch.remove_pointer(pointer_id)

    def get_active_pointers(self):
        """Get list of active pointer IDs"""
        return list(self._multi_touch.pointers.keys())

    def clear_all_pointers(self):
        """Remove all active pointers"""
        multi_touch = self._multi_touch
        for pointer_id in list(multi_touch.pointers.keys()):
            multi_touch.remove_pointer(pointer_id)

    def press_key(self, keycode):
        """Press a key using Android keycode"""
        subprocess.run(
            ["adb", "-s", self.serial, "shell", "input", "keyevent", str(keycode)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def close_app(self, package_name: str):
        """Force stop an app by package name"""
        subprocess.run(
            ["adb", "-s", self.serial, "shell", "am", "force-stop", package_name],
            check=True,
        )

    def open_app(self, package_name: str):
        """Open an app by package name"""
        subprocess.run(
            [
                "adb",
                "-s",
                self.serial,
                "shell",
                "monkey",
                "-p",
                package_name,
                "-c",
                "android.intent.category.LAUNCHER",
                "1",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def kill_monkey(self):
        """Kill all monkey processes on device"""
        subprocess.run(
            ["adb", "-s", self.serial, "shell", "pkill", "-f", "monkey"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def sleep(self, duration):
        """Sleep for a given duration in seconds"""
        time.sleep(duration)

    # High-level gesture methods
    def drag(self, points, duration=1.0, steps_per_segment=10):
        """
        Drag through multiple points without releasing the finger.
        Always supports multi-point paths for smooth, complex gestures.

        Args:
            points: List of (x, y) coordinate tuples
            duration: Total duration in seconds (default: 1.0)
            steps_per_segment: Number of interpolation steps between each point (default: 10)

        Examples:
            # Simple 2-point drag
            controller.drag([(100, 100), (300, 300)])

            # Multi-point path
            path = [(100, 100), (200, 100), (300, 200), (400, 300)]
            controller.drag(path)
        """
        # Validate input
        if not isinstance(points, (list, tuple)):
            raise ValueError("Points must be a list or tuple of coordinate pairs")

        if len(points) < 2:
            raise ValueError("Need at least 2 points for drag gesture")

        # Always use multitouch for precise control through all points
        controller = self._multi_touch
        start_point = points[0]
        pointer_id = controller.add_pointer(start_point[0], start_point[1])

        try:
            # Calculate timing
            total_segments = len(points) - 1
            segment_duration = duration / total_segments
            step_delay = segment_duration / steps_per_segment

            # Move through each segment
            for i in range(total_segments):
                current_point = points[i]
                next_point = points[i + 1]

                # Interpolate between current and next point
                for step in range(1, steps_per_segment + 1):
                    progress = step / steps_per_segment
                    current_x = int(
                        current_point[0] + (next_point[0] - current_point[0]) * progress
                    )
                    current_y = int(
                        current_point[1] + (next_point[1] - current_point[1]) * progress
                    )

                    controller.move_pointer(pointer_id, current_x, current_y)
                    self.sleep(step_delay)

        finally:
            controller.remove_pointer(pointer_id)
