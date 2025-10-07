import threading
from datetime import datetime

from adbutils import AdbClient

from libs.storage_manager import StorageManager
from models.device import Device


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
            device.current_script_name = state_data.get("current_script_name")
            device.current_execution_id = state_data.get("current_execution_id")
            device.game_options = state_data.get("game_options")
            self.devices[serial] = device

    def _save_device_states(self):
        """Save all device states to file"""
        self._storage.save_device_state(self.devices)

    def _start_discovery(self):
        """Background thread to discover connected devices"""
        # Stop existing thread if running
        if self._discovery_thread and self._discovery_thread.is_alive():
            self._stop_discovery_flag.set()
            # Wait max 6 seconds (1 cycle + buffer)
            self._discovery_thread.join(timeout=6)
            self._stop_discovery_flag.clear()

        def discover():
            adb = AdbClient(host="127.0.0.1", port=5037)

            while not self._stop_discovery_flag.is_set():
                changed = False  # Track if any state changed this cycle

                try:
                    current_serials = set()

                    for device_info in adb.device_list():
                        serial = device_info.serial
                        current_serials.add(serial)

                        if serial not in self.devices:
                            device = Device(serial)
                            self.devices[serial] = device
                            changed = True  # New device added
                        else:
                            self.devices[serial].last_seen = datetime.now()

                            if self.devices[serial].status == "offline":
                                self.devices[serial].status = "available"
                                changed = True  # Device status changed

                    # Mark devices as offline if not found
                    for serial in list(self.devices.keys()):
                        if serial not in current_serials:
                            if self.devices[serial].status != "offline":
                                self.devices[serial].status = "offline"
                                changed = True  # Device went offline

                    # Save once per cycle if anything changed
                    if changed:
                        self._save_device_states()

                except Exception as e:
                    print(f"Device discovery error: {e}")

                # Check every 5 seconds, or exit immediately if flag is set
                self._stop_discovery_flag.wait(5)

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
