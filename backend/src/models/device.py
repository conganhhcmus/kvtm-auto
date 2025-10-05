from datetime import datetime

from libs.storage_manager import StorageManager


class Device:
    # Serial to friendly name mapping
    SERIAL_NAME_MAP = {
        "emulator-5554": "Kai",
        "emulator-5564": "Cong Anh",
        "emulator-5574": "My Hanh",
    }

    def __init__(self, serial):
        self.serial = serial
        self.name = self.SERIAL_NAME_MAP.get(
            serial, serial
        )  # Use mapping or fallback to serial
        self.status = "available"  # available, busy, offline
        self.last_seen = datetime.now()
        self.current_script = None
        self.current_script_name = None  # Track display name of current script
        self.current_execution_id = None  # Track current execution ID for running scripts
        self.game_options = None  # Track game options for current execution
        self._storage = StorageManager()

    def add_log(self, log_entry):
        """Add log entry to file"""
        self._storage.append_log(self.serial, log_entry)

    def get_logs(self, limit=100):
        """Get recent logs from file"""
        return self._storage.read_logs(self.serial, limit)

    def clear_logs(self):
        """Clear all logs for this device"""
        self._storage.clear_logs(self.serial)

    def to_dict(self):
        return {
            "id": self.serial,
            "name": self.name,
            "status": self.status,
            "last_seen": self.last_seen.isoformat(),
            "current_script": self.current_script,
            "current_script_name": self.current_script_name,
            "current_execution_id": self.current_execution_id,
            "game_options": self.game_options,
        }
