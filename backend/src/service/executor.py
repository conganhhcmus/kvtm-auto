"""
Simple script execution system for KVTM Auto
Handles script execution per device using direct import instead of subprocess
"""

from loguru import logger

from ..models.script import GameOptions
from ..libs.adb import adb
from .database import db
from .script import script_manager
from .script_runner import script_runner


class Executor:
    """Direct import-based script executor (like JavaScript imports)"""

    def __init__(self):
        # Delegate to script_runner for actual execution
        self._script_runner = script_runner

    def run(self, device_id: str, script_id: str, game_options: GameOptions):
        """Execute a script on a device using direct import"""
        if self.is_running(device_id):
            logger.warning(f"Device {device_id} is already running a script")
            return

        # Verify script exists
        script_path = script_manager.get_script_path(script_id)
        if not script_path:
            raise FileNotFoundError(f"Script {script_id} not found")

        # Verify open_game script exists if needed
        if game_options.open_game:
            open_game_path = script_manager.get_script_path("open_game")
            if not open_game_path:
                logger.warning("Open game script not found, disabling open_game option")
                game_options.open_game = False

        db.write_log(device_id, "Script started", script_id)
        logger.info(f"Starting direct execution of script {script_id} on device {device_id}")

        # Use script runner for direct execution
        self._script_runner.run_script(device_id, script_id, game_options)

    def stop(self, device_id: str, timeout: float = 5.0) -> bool:
        """Stop script execution for a device"""
        logger.info(f"Stopping script for device {device_id}")
        
        db.stop_device_script(device_id)
        
        # Kill monkey processes if any
        try:
            adb.kill_monkey(device_id)
        except Exception as e:
            logger.debug(f"Failed to kill monkey processes for {device_id}: {e}")

        # Stop script using script runner
        result = self._script_runner.stop_script(device_id, timeout)
        
        logger.info(f"Stopped script for device {device_id}")
        return result

    def is_running(self, device_id: str) -> bool:
        """Check if a device is running a script"""
        return self._script_runner.is_running(device_id)

    def get_running_devices(self) -> list[str]:
        """Get list of devices currently running scripts"""
        return self._script_runner.get_running_devices()

    def shutdown_all(self) -> dict:
        """Shutdown all running processes"""
        return self._script_runner.shutdown_all()


# Global executor instance
executor = Executor()