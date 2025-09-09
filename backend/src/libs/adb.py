"""
ADB (Android Debug Bridge) operations for device control.

IMPORTANT: This module uses subprocess.run() for ALL operations to ensure clean process management.
DO NOT replace with subprocess.Popen() or persistent shell connections as they can cause:
- Orphaned subprocess processes when script processes are terminated
- Application restart issues due to resource cleanup problems  
- Process leakage that interferes with the main application lifecycle

Each ADB command creates a short-lived process that completes and cleans up automatically.
"""

import subprocess
import time
from typing import List, Optional, Tuple

EVENT = "/dev/input/event1"


class ADB:
    """Android Debug Bridge operations for device control"""

    @staticmethod
    def _build_adb_command(device_id: Optional[str], *args) -> List[str]:
        """Build ADB command with optional device ID"""
        cmd = ["adb"]
        if device_id:
            cmd += ["-s", device_id]
        cmd.extend(args)
        return cmd

    @staticmethod
    def _send_event(cmd: str, device_id: Optional[str] = None):
        """Send low-level touch event to device"""
        args = ADB._build_adb_command(device_id, "shell", "sendevent", EVENT) + cmd.split()
        subprocess.run(args)

    @staticmethod
    def _touch_down(x: int, y: int, device_id: Optional[str] = None):
        """Send touch down event"""
        ADB._send_event("3 57 0", device_id)  # ABS_MT_TRACKING_ID = 0
        ADB._send_event("1 330 1", device_id)  # BTN_TOUCH down
        ADB._send_event(f"3 53 {x}", device_id)  # ABS_MT_POSITION_X
        ADB._send_event(f"3 54 {y}", device_id)  # ABS_MT_POSITION_Y
        ADB._send_event("0 0 0", device_id)  # SYN_REPORT

    @staticmethod
    def _touch_up(device_id: Optional[str] = None):
        """Send touch up event"""
        ADB._send_event(f"3 57 -1", device_id)  # BTN_TOUCH up (tracking ID 0)
        ADB._send_event(f"0 0 0", device_id)  # SYN_REPORT

    @staticmethod
    def _touch_move(x: int, y: int, device_id: Optional[str] = None):
        """Send touch move event"""
        ADB._send_event(f"3 53 {x}", device_id)  # ABS_MT_POSITION_X
        ADB._send_event(f"3 54 {y}", device_id)  # ABS_MT_POSITION_Y
        ADB._send_event(f"0 0 0", device_id)  # SYN_REPORT

    @staticmethod
    def action(
        points: List[Tuple[int, int]],
        delay: float = 0.01,
        device_id: Optional[str] = None,
    ):
        """Perform swipe/drag action through multiple points"""
        ADB._touch_down(points[0][0], points[0][1], device_id)
        time.sleep(delay)

        for point in points[1:]:
            ADB._touch_move(point[0], point[1], device_id)
            time.sleep(delay)
        ADB._touch_up(device_id)

    @staticmethod
    def tap(x: int, y: int, device_id: Optional[str] = None):
        """Tap at specific coordinates"""
        args = ADB._build_adb_command(device_id, "shell", "input", "tap", str(x), str(y))
        subprocess.run(args)

    @staticmethod
    def get_screen_size(device_id: Optional[str] = None) -> Tuple[int, int]:
        """Get device screen dimensions"""
        args = ADB._build_adb_command(device_id, "shell", "wm", "size")
        result = subprocess.run(args, capture_output=True, text=True)

        # data sample: Physical size: 1280x720
        return tuple(map(int, result.stdout.split(":")[1].strip().split("x")))

    @staticmethod
    def capture_screen(device_id: Optional[str] = None) -> bytes:
        """Capture device screen as PNG bytes"""
        args = ADB._build_adb_command(device_id, "shell", "screencap", "-p")
        result = subprocess.run(args, capture_output=True)

        return result.stdout

    @staticmethod
    def get_list_devices() -> List[str]:
        """Get list of connected devices"""
        args = ADB._build_adb_command(None, "devices")
        result = subprocess.run(args, capture_output=True, text=True)

        # data sample:
        # List of devices attached
        # emulator-5554	device
        # emulator-5556	device
        return [
            line.split()[0]
            for line in result.stdout.splitlines()
            if line.strip() and "\t" in line
        ]

    @staticmethod
    def press_key(keycode, device_id: Optional[str] = None):
        """Press a key using Android keycode"""
        args = ADB._build_adb_command(device_id, "shell", "input", "keyevent", str(keycode))
        subprocess.run(args)

    @staticmethod
    def close_app(package_name: str, device_id: Optional[str] = None):
        """Force stop an app by package name"""
        args = ADB._build_adb_command(device_id, "shell", "am", "force-stop", package_name)
        subprocess.run(args)

    @staticmethod
    def open_app(package_name: str, device_id: Optional[str] = None):
        """Open an app by package name"""
        args = ADB._build_adb_command(
            device_id,
            "shell",
            "monkey",
            "-p",
            package_name,
            "-c",
            "android.intent.category.LAUNCHER",
            "1",
        )
        subprocess.run(args)

    @staticmethod
    def kill_monkey(device_id: Optional[str] = None):
        """Kill all monkey processes on device"""
        args = ADB._build_adb_command(device_id, "shell", "pkill", "-f", "monkey")
        subprocess.run(args)

# Global ADB instance
adb = ADB()