import subprocess
import threading
import time
from datetime import datetime

from models.device import Device


def get_device_screen_size(serial):
    """Get device screen size as [width, height]"""
    try:
        result = subprocess.run(
            ["adb", "-s", serial, "shell", "wm", "size"],
            capture_output=True,
            text=True,
            check=True,
        )
        # Parse output like "Physical size: 1920x1080"
        for line in result.stdout.splitlines():
            if "Physical size:" in line:
                size_str = line.split("Physical size:")[-1].strip()
                width, height = map(int, size_str.split("x"))
                return [width, height]
        return None
    except Exception:
        return None


class DeviceManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DeviceManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.devices = {}
            self._start_discovery()
            DeviceManager._initialized = True

    def _start_discovery(self):
        """Background thread to discover connected devices"""

        def discover():
            while True:
                try:
                    result = subprocess.run(
                        ["adb", "devices"], capture_output=True, text=True
                    )
                    current_serials = set()

                    for line in result.stdout.splitlines()[1:]:
                        if line.strip():
                            serial = line.split()[0]
                            current_serials.add(serial)

                            if serial not in self.devices:
                                device = Device(serial)
                                # Fetch screen size if not already cached
                                if device.screen_size is None:
                                    device.screen_size = get_device_screen_size(serial)
                                self.devices[serial] = device
                            else:
                                self.devices[serial].last_seen = datetime.now()
                                if self.devices[serial].status == "offline":
                                    self.devices[serial].status = "available"
                                # Fetch screen size if not already cached
                                if self.devices[serial].screen_size is None:
                                    self.devices[
                                        serial
                                    ].screen_size = get_device_screen_size(serial)

                    # Mark devices as offline if not found
                    for serial in list(self.devices.keys()):
                        if serial not in current_serials:
                            self.devices[serial].status = "offline"

                except Exception as e:
                    print(f"Device discovery error: {e}")

                time.sleep(5)  # Check every 5 seconds

        threading.Thread(target=discover, daemon=True).start()

    def get_device(self, serial):
        return self.devices.get(serial)

    def list_devices(self):
        return list(self.devices.values())
