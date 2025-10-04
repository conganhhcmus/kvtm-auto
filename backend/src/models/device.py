import threading
from datetime import datetime


class Device:
    # Serial to friendly name mapping
    SERIAL_NAME_MAP = {
        "emulator-5554": "Kai",
        "emulator-5564": "Cong Anh",
        "emulator-5574": "My Hanh",
    }

    def __init__(self, serial):
        self.serial = serial
        self.name = self.SERIAL_NAME_MAP.get(serial, serial)  # Use mapping or fallback to serial
        self.status = "available"  # available, busy, offline
        self.last_seen = datetime.now()
        self.logs = []
        self.current_script = None
        self.current_execution_id = None  # Track current execution ID for running scripts
        self.screen_size = None  # [width, height] - will be populated during discovery
        self._log_lock = threading.Lock()  # Thread-safe log operations

    def add_log(self, log_entry):
        """Thread-safe method to add log entry with size limit"""
        with self._log_lock:
            self.logs.append(log_entry)
            # Keep only last 1000 logs to prevent memory issues
            if len(self.logs) > 1000:
                self.logs = self.logs[-1000:]

    def get_logs(self, limit=100):
        """Get recent logs with optional limit"""
        with self._log_lock:
            return self.logs[-limit:] if limit else self.logs[:]

    def to_dict(self):
        return {
            "id": self.serial,
            "name": self.name,
            "status": self.status,
            "last_seen": self.last_seen.isoformat(),
            "current_script": self.current_script,
            "current_execution_id": self.current_execution_id,
            "screen_size": self.screen_size,
        }
