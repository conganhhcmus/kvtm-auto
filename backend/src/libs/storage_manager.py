import json
import threading
from datetime import datetime
from pathlib import Path


class StorageManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StorageManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.data_dir = Path(__file__).parent.parent / "data"
            self.logs_dir = self.data_dir / "logs"
            self.state_file = self.data_dir / "device_state.json"
            self._file_lock = threading.Lock()
            self._ensure_directories()
            StorageManager._initialized = True

    def _ensure_directories(self):
        """Create data and logs directories if they don't exist"""
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

    def append_log(self, device_serial, log_entry):
        """Thread-safe append log entry to device log file"""
        log_file = self.logs_dir / f"{device_serial}.log"
        with self._file_lock:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"{log_entry}\n")

    def read_logs(self, device_serial, limit=100):
        """Read last N logs from device log file"""
        log_file = self.logs_dir / f"{device_serial}.log"
        if not log_file.exists():
            return []

        with self._file_lock:
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Return last N lines, strip newlines
                return (
                    [line.strip() for line in lines[-limit:]]
                    if limit
                    else [line.strip() for line in lines]
                )

    def clear_logs(self, device_serial):
        """Thread-safe clear all logs for a device"""
        log_file = self.logs_dir / f"{device_serial}.log"
        with self._file_lock:
            if log_file.exists():
                log_file.unlink()  # Delete the file

    def save_device_state(self, devices):
        """Save all device states to JSON file"""
        with self._file_lock:
            state_data = {}
            for serial, device in devices.items():
                state_data[serial] = {
                    "name": device.name,
                    "status": device.status,
                    "last_seen": device.last_seen.isoformat(),
                    "current_script": device.current_script,
                    "current_execution_id": device.current_execution_id,
                    "screen_size": device.screen_size,
                }

            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state_data, f, indent=2)

    def load_device_state(self):
        """Load device states from JSON file"""
        if not self.state_file.exists():
            return {}

        with self._file_lock:
            with open(self.state_file, "r", encoding="utf-8") as f:
                state_data = json.load(f)
                # Convert ISO timestamps back to datetime
                for serial, data in state_data.items():
                    data["last_seen"] = datetime.fromisoformat(data["last_seen"])
                return state_data
