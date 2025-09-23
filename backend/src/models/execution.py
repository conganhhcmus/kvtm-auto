import uuid
from datetime import datetime


class RunningScript:
    def __init__(self, device_id, script_id, process):
        self.id = str(uuid.uuid4())
        self.device_id = device_id
        self.script_id = script_id
        self.process = process
        self.start_time = datetime.now()
        self.status = "running"

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "script_id": self.script_id,
            "start_time": self.start_time.isoformat(),
            "status": self.status,
        }
