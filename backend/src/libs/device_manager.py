import subprocess
import threading
import time
from datetime import datetime


class Device:
    def __init__(self, serial):
        self.serial = serial
        self.status = "available"  # available, busy, offline
        self.last_seen = datetime.now()
        self.logs = []
        self.current_script = None

    def to_dict(self):
        return {
            "id": self.serial,
            "status": self.status,
            "last_seen": self.last_seen.isoformat(),
            "current_script": self.current_script,
        }


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
                                self.devices[serial] = Device(serial)
                            else:
                                self.devices[serial].last_seen = datetime.now()
                                if self.devices[serial].status == "offline":
                                    self.devices[serial].status = "available"

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
