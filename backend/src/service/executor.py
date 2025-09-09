"""
Simple script execution system for KVTM Auto
Handles script execution per device using subprocess only
"""

import subprocess
from typing import Dict

from loguru import logger

from ..libs.shell import Shell
from ..models.script import GameOptions
from . import adb, db
from .script import script_manager


class Executor:
    """Simple subprocess-based script executor"""

    def __init__(self):
        self._running_scripts: Dict[str, subprocess.Popen] = {}

    def run(self, device_id: str, script_id: str, game_options: GameOptions):
        """Execute a script on a device"""
        if self.is_running(device_id):
            logger.warning(f"Device {device_id} is already running a script")
            return

        script_path = script_manager.get_script_path(script_id)
        if not script_path:
            raise FileNotFoundError(f"Script {script_id} not found")

        # Get open_game script path if needed
        open_game_path = None
        if game_options.open_game:
            open_game_path = script_manager.get_script_path("open_game")

        # Build shell command using the Shell class
        cmd = Shell.build_script_execution_command(
            device_id=device_id,
            script_id=script_id,
            script_path=script_path,
            game_options=game_options,
            open_game_path=open_game_path
        )

        db.write_log(device_id, "Script started", script_id)
        logger.info(f"Executing: {' '.join(cmd)}")

        # Start subprocess
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd="/app",
            env={"PYTHONUNBUFFERED": "1"}
        )

        self._running_scripts[device_id] = process
        logger.info(f"Started script {script_id} on device {device_id} (PID: {process.pid})")

        # Monitor output in background (fire and forget)
        self._monitor_output(device_id, process)

    def _monitor_output(self, device_id: str, process: subprocess.Popen):
        """Monitor subprocess output and log to database"""
        for line in iter(process.stdout.readline, ''):
            if not line:
                break
            
            line = line.rstrip()
            # logger.info(f"[{device_id}] {line}")
            # Store raw subprocess output as simple logs
            db.write_simple_log(device_id, line)

        # Process finished, cleanup
        self._cleanup_device(device_id)
        logger.info(f"Script execution completed for device {device_id}")

    def stop(self, device_id: str, timeout: float = 5.0) -> bool:
        """Stop script execution for a device"""
        logger.info(f"Stopping script for device {device_id}")
        
        db.stop_device_script(device_id)
        
        if device_id not in self._running_scripts:
            return True

        process = self._running_scripts[device_id]
        
        if process.poll() is not None:
            self._cleanup_device(device_id)
            return True

        # Kill monkey processes
        adb.kill_monkey(device_id)

        # Terminate process
        process.terminate()
        process.wait(timeout=timeout)
        
        if process.poll() is None:
            process.kill()
            process.wait(timeout=2.0)

        self._cleanup_device(device_id)
        logger.info(f"Stopped script for device {device_id}")
        return True

    def is_running(self, device_id: str) -> bool:
        """Check if a device is running a script"""
        if device_id not in self._running_scripts:
            return False

        process = self._running_scripts[device_id]
        is_alive = process.poll() is None

        if not is_alive:
            self._cleanup_device(device_id)

        return is_alive

    def get_running_devices(self) -> list[str]:
        """Get list of devices currently running scripts"""
        running_devices = []
        
        for device_id in list(self._running_scripts.keys()):
            if self.is_running(device_id):
                running_devices.append(device_id)
        
        return running_devices

    def shutdown_all(self) -> dict:
        """Shutdown all running processes"""
        running_devices = list(self._running_scripts.keys())
        
        if not running_devices:
            return {"total": 0, "stopped": [], "failed": []}

        stopped_devices = []
        failed_devices = []
        
        for device_id in running_devices:
            if self.stop(device_id, timeout=3.0):
                stopped_devices.append(device_id)
            else:
                failed_devices.append(device_id)

        return {
            "total": len(running_devices),
            "stopped": stopped_devices,
            "failed": failed_devices
        }

    def _cleanup_device(self, device_id: str):
        """Clean up device execution resources"""
        if device_id in self._running_scripts:
            del self._running_scripts[device_id]
            logger.debug(f"Cleaned up resources for device {device_id}")


# Global executor instance
executor = Executor()