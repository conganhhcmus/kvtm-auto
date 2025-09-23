import json
import subprocess
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


class ExecutionManager:
    def __init__(self, device_manager):
        self.running_scripts = {}
        self.device_manager = device_manager

    def start_script(self, device_id, script_id, script_path, game_options=None):
        device = self.device_manager.get_device(device_id)
        if not device:
            raise ValueError("Device not found")
        if device.status != "available":
            raise ValueError("Device is busy")

        try:
            # Prepare command arguments
            cmd_args = ["python", script_path, device_id]

            # Add game_options as JSON string if provided
            if game_options:
                cmd_args.append(json.dumps(game_options))

            process = subprocess.Popen(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            device.status = "busy"
            device.current_script = script_id

            running_script = RunningScript(device_id, script_id, process)
            self.running_scripts[running_script.id] = running_script

            return running_script
        except Exception as e:
            raise e

    def stop_script(self, execution_id):
        if execution_id not in self.running_scripts:
            raise ValueError("Execution not found")

        running_script = self.running_scripts[execution_id]
        device = self.device_manager.get_device(running_script.device_id)

        try:
            running_script.process.terminate()
            running_script.process.wait(timeout=5)

            device.status = "available"
            device.current_script = None

            del self.running_scripts[execution_id]
            return True
        except Exception as e:
            raise e

    def stop_all_scripts(self):
        stopped_count = 0
        errors = []

        for execution_id, running_script in list(self.running_scripts.items()):
            try:
                self.stop_script(execution_id)
                stopped_count += 1
            except Exception as e:
                errors.append(f"Execution {execution_id}: {str(e)}")

        return stopped_count, errors
