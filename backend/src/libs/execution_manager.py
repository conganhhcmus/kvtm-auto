import json
import os
import subprocess
import threading
from datetime import datetime

from models.execution import RunningScript
from models.game_options import GameOptions


class ExecutionManager:
    # Class-level shared state for all instances
    _running_scripts = {}

    def __init__(self, device_manager):
        self.device_manager = device_manager

    @property
    def running_scripts(self):
        return ExecutionManager._running_scripts

    def start_script(
        self, device_id, script_id, script_path, game_options=None, script_name=None
    ):
        device = self.device_manager.get_device(device_id)
        if not device:
            raise ValueError("Device not found")
        if device.status != "available":
            raise ValueError("Device is busy")

        try:
            # Prepare command arguments - use unbuffered Python output
            cmd_args = ["python", "-u", script_path, device_id]

            # Convert game_options to GameOptions model if it's a dict
            if game_options:
                if isinstance(game_options, dict):
                    game_options_obj = GameOptions.from_dict(game_options)
                elif isinstance(game_options, GameOptions):
                    game_options_obj = game_options
                else:
                    raise ValueError(
                        "game_options must be a dict or GameOptions instance"
                    )

                cmd_args.append(json.dumps(game_options_obj.to_dict()))

            process = subprocess.Popen(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Redirect stderr to stdout
                text=True,
                bufsize=1,  # Line buffering
                universal_newlines=True,
                cwd=os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))
                ),  # Set working directory to backend/src
            )

            device.status = "busy"
            device.current_script = script_id
            device.current_script_name = script_name
            device.game_options = game_options_obj.to_dict() if game_options else None

            # Add start log
            timestamp = datetime.now().strftime("%H:%M:%S")
            start_log = f"[{timestamp}]: Script {script_id} started"
            device.add_log(start_log)

            running_script = RunningScript(device_id, script_id, process)
            self.running_scripts[running_script.id] = running_script

            # Set execution_id on the device for tracking
            device.current_execution_id = running_script.id

            # Save device state after starting script
            self.device_manager._save_device_states()

            # Start log capture thread
            log_thread = threading.Thread(
                target=self._capture_logs,
                args=(running_script, device),
                daemon=True,
            )
            log_thread.start()
            running_script.log_thread = log_thread

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

            # Wait for log thread to finish (with timeout)
            if hasattr(running_script, "log_thread"):
                running_script.log_thread.join(timeout=2)

            device.status = "available"
            device.current_script = None
            device.current_script_name = None
            device.current_execution_id = None  # Clear execution_id when stopping
            device.game_options = None  # Clear game options when stopping

            # Add completion log
            timestamp = datetime.now().strftime("%H:%M:%S")
            completion_log = f"[{timestamp}]: Script execution stopped"
            device.add_log(completion_log)

            # Save device state after stopping
            self.device_manager._save_device_states()

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

    def _capture_logs(self, running_script, device):
        """Capture subprocess output and append to device logs in real-time"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            debug_log = f"[{timestamp}]: Log capture thread started"
            device.add_log(debug_log)

            while running_script.process.poll() is None:
                output = running_script.process.stdout.readline()
                if output:
                    # Format log with timestamp
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    log_entry = f"[{timestamp}]: {output.strip()}"
                    device.add_log(log_entry)

            # Capture any remaining output
            remaining_output = running_script.process.stdout.read()
            if remaining_output:
                for line in remaining_output.splitlines():
                    if line.strip():
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        log_entry = f"[{timestamp}]: {line.strip()}"
                        device.add_log(log_entry)

            # Clean up device state when script finishes naturally
            device.status = "available"
            device.current_script = None
            device.current_script_name = None
            device.current_execution_id = None
            device.game_options = None

            timestamp = datetime.now().strftime("%H:%M:%S")
            completion_log = f"[{timestamp}]: Script execution completed"
            device.add_log(completion_log)

            # Save device state after completion
            from libs.device_manager import DeviceManager

            device_manager = DeviceManager()
            device_manager._save_device_states()

            # Remove from running scripts
            if running_script.id in self.running_scripts:
                del self.running_scripts[running_script.id]

        except Exception as e:
            # Log capture error to device logs
            timestamp = datetime.now().strftime("%H:%M:%S")
            error_log = f"[{timestamp}]: Log capture error: {str(e)}"
            device.add_log(error_log)

            # Clean up device state even on error
            device.status = "available"
            device.current_script = None
            device.current_script_name = None
            device.current_execution_id = None
            device.game_options = None

            # Save device state after error
            from libs.device_manager import DeviceManager

            device_manager = DeviceManager()
            device_manager._save_device_states()

            # Remove from running scripts
            if running_script.id in self.running_scripts:
                del self.running_scripts[running_script.id]
