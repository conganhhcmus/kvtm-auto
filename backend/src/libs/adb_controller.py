import os
import subprocess
import time
import threading
from functools import wraps

from enum import Enum
from .image_controller import image_controller


def retry_on_error(max_attempts=3, delay=0.5, return_value=None, skip_log=True):
    """
    Decorator to retry a function on error.

    Args:
        max_attempts: Maximum number of attempts (default: 3)
        delay: Delay between attempts in seconds (default: 0.5)
        return_value: Value to return on final failure (default: None)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_attempts - 1:
                        if not skip_log:
                            print(
                                f"Error in {func.__name__} (attempt {attempt + 1}/{max_attempts}): {e}"
                            )
                        time.sleep(delay)
                    else:
                        if not skip_log:
                            print(
                                f"Error in {func.__name__} (attempt {attempt + 1}/{max_attempts}): {e}"
                            )
                            print(
                                f"{func.__name__} failed after {max_attempts} attempts"
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


class _ShellSession:
    """Manages a persistent ADB shell session for a device"""

    def __init__(self, serial):
        self.serial = serial
        self._process = None
        self._lock = threading.Lock()
        self._marker = f"<<<CMD_DONE_{serial}>>>"
        self._start_shell()

    def _start_shell(self):
        """Start the persistent shell subprocess"""
        try:
            self._process = subprocess.Popen(
                ["adb", "-s", self.serial, "shell"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
            )
        except Exception as e:
            print(f"Error starting shell session for {self.serial}: {e}")
            self._process = None

    def _ensure_running(self):
        """Ensure shell is running, restart if needed"""
        if self._process is None or self._process.poll() is not None:
            if self._process is not None:
                print(f"Shell session died for {self.serial}, restarting...")
            self._start_shell()

    def execute(self, command, timeout=5):
        """
        Execute a command in the shell and wait for completion.

        Args:
            command: Shell command to execute
            timeout: Maximum time to wait for command completion (seconds)

        Returns:
            True if command executed successfully, False otherwise
        """
        with self._lock:
            try:
                self._ensure_running()
                if self._process is None:
                    return False

                # Send command followed by marker
                full_command = f"{command} 2>&1; echo '{self._marker}'\n"
                self._process.stdin.write(full_command)
                self._process.stdin.flush()

                # Wait for marker in output
                start_time = time.time()
                while time.time() - start_time < timeout:
                    line = self._process.stdout.readline()
                    if self._marker in line:
                        return True

                # Timeout - kill and restart shell
                print(f"Command timed out for {self.serial}: {command}")
                try:
                    self._process.kill()
                    self._process.wait(timeout=1)
                except Exception:
                    pass
                self._process = None
                self._start_shell()  # Restart shell for next command
                return False

            except Exception as e:
                print(f"Error executing command in shell for {self.serial}: {e}")
                # Clean up process before setting to None
                if self._process:
                    try:
                        self._process.kill()
                        self._process.wait(timeout=1)
                    except Exception:
                        pass
                self._process = None
                return False

    def close(self):
        """Close the shell session"""
        if self._process:
            try:
                self._process.stdin.write("exit\n")
                self._process.stdin.flush()
                self._process.wait(timeout=2)
            except Exception:
                pass
            finally:
                try:
                    self._process.terminate()
                    self._process.wait(timeout=1)
                except Exception:
                    self._process.kill()
                self._process = None


class AdbController:
    # Assets directory relative to this file's location
    ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")

    def __init__(self, serial):
        self.serial = serial
        self._shell = _ShellSession(serial)
        self.screen_width, self.screen_height = self._get_screen_size()

        # Touch device attributes
        self.touch_device = (
            "/dev/input/event2"  # Default touch device path for most emulators/devices
        )
        # BlueStacks Virtual Touch uses 0-32767 coordinate range
        self.device_max_x = 32767
        self.device_max_y = 32767

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

    def _convert_to_device_coords(self, screen_x, screen_y):
        """Convert screen coordinates to device coordinates for BlueStacks Virtual Touch"""
        device_x = int((screen_x / self.screen_width) * self.device_max_x)
        device_y = int((screen_y / self.screen_height) * self.device_max_y)
        return device_x, device_y

    @retry_on_error(return_value=False, skip_log=False)
    def tap(self, x, y):
        """Simulate a tap at (x, y)"""
        result = self._shell.execute(f"input tap {x} {y}")
        if not result:
            raise Exception(f"Failed to tap at ({x}, {y})")
        return result

    @retry_on_error(skip_log=False)
    def capture_screen(self):
        """Capture device screen as PNG bytes"""
        result = subprocess.run(
            ["adb", "-s", self.serial, "shell", "screencap", "-p"],
            capture_output=True,
            check=True,
        )
        return result.stdout

    @retry_on_error()
    def find_image_on_screen(self, template_path, threshold=0.9):
        """Find template image on screen using bytes-based approach"""
        screen_bytes = self.capture_screen()
        template_bytes = image_controller.read_asset_image_bytes(template_path)
        coords = image_controller.get_coordinate(
            screen_bytes, template_bytes, threshold
        )
        if coords:
            return coords
        raise Exception("Image not found on screen")

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
        raise Exception("Image not found on screen")

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
        raise Exception(f"Text '{target_text}' not found on screen")

    @retry_on_error(return_value=False, skip_log=False)
    def press_key(self, keycode):
        """Press a key using Android keycode"""
        result = self._shell.execute(f"input keyevent {keycode}")
        if not result:
            raise Exception(f"Failed to press key {keycode}")
        return result

    @retry_on_error(return_value=False, skip_log=False)
    def close_app(self, package_name: str):
        """Force stop an app by package name"""
        result = self._shell.execute(f"am force-stop {package_name}")
        if not result:
            raise Exception(f"Failed to close app {package_name}")
        return result

    @retry_on_error(return_value=False, skip_log=False)
    def open_app(self, package_name: str):
        """Open an app by package name"""
        result = self._shell.execute(
            f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1"
        )
        if not result:
            raise Exception(f"Failed to open app {package_name}")
        return result

    @retry_on_error(return_value=False, skip_log=False)
    def kill_monkey(self):
        """Kill all monkey processes on device"""
        result = self._shell.execute("pkill -f monkey")
        if not result:
            raise Exception("Failed to kill monkey process")
        return result

    def sleep(self, duration):
        """Sleep for a given duration in seconds"""
        time.sleep(duration)

    @retry_on_error(return_value=False, skip_log=False)
    def swipe(self, x1, y1, x2, y2, duration=300):
        """
        Swipe from (x1, y1) to (x2, y2)

        Args:
            x1, y1: Starting coordinates
            x2, y2: Ending coordinates
            duration: Duration of swipe in milliseconds (default: 300)
        """
        result = self._shell.execute(f"input swipe {x1} {y1} {x2} {y2} {duration}")
        if not result:
            raise Exception(f"Failed to swipe from ({x1}, {y1}) to ({x2}, {y2})")
        return result

    # High-level gesture methods

    @retry_on_error(return_value=False, skip_log=False)
    def drag(self, points):
        """
        Smooth drag through a series of points.

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
            ]
        )

        # Execute single optimized command
        full_command = "; ".join(commands)
        result = self._shell.execute(full_command, timeout=30)
        if not result:
            raise Exception(f"Failed to drag through {len(points)} points")
        return result

    def close(self):
        """Close the ADB controller and cleanup resources"""
        if self._shell:
            self._shell.close()
