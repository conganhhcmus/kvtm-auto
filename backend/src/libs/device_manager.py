import subprocess
import threading
from datetime import datetime

from libs.storage_manager import StorageManager
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
            self._storage = StorageManager()
            self._discovery_thread = None
            self._stop_discovery_flag = threading.Event()
            self._load_device_states()
            self._start_discovery()
            DeviceManager._initialized = True

    def _load_device_states(self):
        """Load saved device states from file"""
        saved_states = self._storage.load_device_state()
        for serial, state_data in saved_states.items():
            device = Device(serial)
            device.name = state_data.get("name", device.name)
            device.status = state_data.get(
                "status", "offline"
            )  # Default to offline until discovered
            device.last_seen = state_data.get("last_seen", datetime.now())
            device.current_script = state_data.get("current_script")
            device.current_execution_id = state_data.get("current_execution_id")
            device.screen_size = state_data.get("screen_size")
            self.devices[serial] = device

    def _save_device_states(self):
        """Save all device states to file"""
        self._storage.save_device_state(self.devices)

    def _start_discovery(self):
        """Background thread to discover connected devices"""
        # Stop existing thread if running
        if self._discovery_thread and self._discovery_thread.is_alive():
            self._stop_discovery_flag.set()
            self._discovery_thread.join(
                timeout=6
            )  # Wait max 6 seconds (1 cycle + buffer)
            self._stop_discovery_flag.clear()

        def discover():
            while not self._stop_discovery_flag.is_set():
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
                                self._save_device_states()  # Save when new device added
                            else:
                                self.devices[serial].last_seen = datetime.now()
                                if self.devices[serial].status == "offline":
                                    self.devices[serial].status = "available"
                                    self._save_device_states()  # Save when device comes online
                                # Fetch screen size if not already cached
                                if self.devices[serial].screen_size is None:
                                    self.devices[
                                        serial
                                    ].screen_size = get_device_screen_size(serial)
                                    self._save_device_states()  # Save when screen size updated

                    # Mark devices as offline if not found
                    for serial in list(self.devices.keys()):
                        if serial not in current_serials:
                            if self.devices[serial].status != "offline":
                                self.devices[serial].status = "offline"
                                self._save_device_states()  # Save when device goes offline

                except Exception as e:
                    print(f"Device discovery error: {e}")

                self._stop_discovery_flag.wait(
                    5
                )  # Check every 5 seconds, or exit immediately if flag is set

        self._discovery_thread = threading.Thread(target=discover, daemon=True)
        self._discovery_thread.start()

    def stop_discovery(self):
        """Gracefully stop the discovery thread"""
        if self._discovery_thread and self._discovery_thread.is_alive():
            self._stop_discovery_flag.set()
            self._discovery_thread.join(timeout=6)
            self._stop_discovery_flag.clear()

    def get_device(self, serial):
        return self.devices.get(serial)

    def list_devices(self):
        return list(self.devices.values())
