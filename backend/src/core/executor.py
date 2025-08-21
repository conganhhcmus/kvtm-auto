"""
Script execution system for KVTM Auto
Handles independent script execution per device with logging and looping
"""

import importlib.util
import multiprocessing
import time
import traceback
from pathlib import Path
from typing import Any, Dict

from loguru import logger

from ..models import GameOptions, Device
from . import adb, image, db



class Executor:
    """Handles script execution with device isolation"""

    def __init__(self):
        """Initialize executor with empty running scripts dict"""
        self._running_scripts: Dict[str, multiprocessing.Process] = {}

    def run(
        self,
        device_id: str,
        script_id: str,
        game_options: GameOptions,
    ):
        """Execute a script on a specific device"""
        try:
            # Check if device is already running a script
            if self.is_running(device_id):
                logger.warning(f"Device {device_id} is already running a script")
                return

            # Create and start execution process
            process = multiprocessing.Process(
                target=self._execute_script_process,
                args=(device_id, script_id, game_options),
                daemon=True,
            )

            self._running_scripts[device_id] = process
            process.start()

            logger.info(
                f"Started script {script_id} on device {device_id}"
            )

        except Exception as e:
            logger.error(f"Failed to start script execution: {e}")
            self._handle_script_error(device_id, script_id, str(e))

    def stop(self, device_id: str, force: bool = False, timeout: float = 5.0) -> bool:
        """Stop script execution for a device"""
        try:
            if device_id not in self._running_scripts:
                return True

            process = self._running_scripts[device_id]

            if not process.is_alive():
                self._cleanup_device(device_id)
                return True

            logger.info(f"Stopping script process for device {device_id}...")

            if force:
                # Force kill immediately
                logger.warning(f"Force killing script process for device {device_id}")
                process.kill()
            else:
                # Try graceful termination first
                process.terminate()

                # Wait for process to finish
                process.join(timeout=timeout)

                # Force kill if still running
                if process.is_alive():
                    logger.warning(
                        f"Script process for device {device_id} did not stop gracefully, force killing"
                    )
                    process.kill()
                    process.join(timeout=2.0)  # Wait a bit more after kill

            # Clean up
            self._cleanup_device(device_id)
            logger.info(f"Script process for device {device_id} stopped successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to stop script for device {device_id}: {e}")
            return False

    def is_running(self, device_id: str) -> bool:
        """Check if a device is currently running a script"""
        if device_id not in self._running_scripts:
            return False

        process = self._running_scripts[device_id]
        is_alive = process.is_alive()

        # Clean up if process is dead
        if not is_alive:
            self._cleanup_device(device_id)

        return is_alive

    def _execute_script_process(
        self,
        device_id: str,
        script_id: str,
        game_options: GameOptions,
    ):
        """Execute script in a separate process with looping support"""
        try:
            logger.info(f"Starting script execution: {script_id} on device {device_id}")

            # Log script start
            db.write_log(device_id, f"Script execution started: {script_id}")
            
            # Get loop configuration
            max_loops = game_options.max_loops
            loop_delay = game_options.loop_delay
            
            db.write_log(device_id, f"Script will run {max_loops} loop(s) with {loop_delay}s delay")

            # Prepare device info
            device = self._prepare_device_info(device_id)

            # Check if we need to run open-game script first
            should_open_game = game_options.open_game

            if should_open_game:
                db.write_log(device_id, "Running open-game script...")

                # Load and execute open-game script
                script_path = db.get_script_path("open_game")
                script_module = self._load_script_module(script_path)

                if not hasattr(script_module, "main"):
                    raise AttributeError("open_game script missing main function")

                db.write_log(device_id, "Open-game script loaded, executing...")

                # Execute open-game script
                result = script_module.main(
                    device=device, game_options=game_options
                )

                if result and not result.get("success", True):
                    error_msg = f"Open-game script failed: {result.get('message', 'Unknown error')}"
                    raise RuntimeError(error_msg)

                db.write_log(device_id, "Open-game script completed successfully")

            # Now execute the main script with looping
            db.write_log(device_id, f"Loading script {script_id}...")

            # Load main script
            script_path = db.get_script_path(script_id)
            script_module = self._load_script_module(script_path)

            if not hasattr(script_module, "main"):
                raise AttributeError(f"Script {script_id} missing main function")

            db.write_log(device_id, f"Script {script_id} loaded successfully")

            # Execute the main script with looping
            for loop_index in range(max_loops):
                db.write_log(device_id, f"Script loop iteration {loop_index + 1}/{max_loops}")
                
                # Execute script with loop index
                result = script_module.main(
                    device=device, 
                    game_options=game_options,
                    loop_index=loop_index
                )

                if result and not result.get("success", True):
                    error_msg = f"Script failed on loop {loop_index + 1}: {result.get('message', 'Unknown error')}"
                    raise RuntimeError(error_msg)

                # Check if script wants to continue looping
                if result and not result.get("continue_loop", True):
                    db.write_log(device_id, f"Script requested to stop looping at iteration {loop_index + 1}")
                    break

                # Add delay between loops (except for the last one)
                if loop_index < max_loops - 1 and loop_delay > 0:
                    db.write_log(device_id, f"Waiting {loop_delay}s before next loop...")
                    time.sleep(loop_delay)

            # Script completed successfully
            db.write_log(device_id, f"Script {script_id} completed successfully after {loop_index + 1} loop(s)")

            # Update final state
            db.stop_device_script(device_id)

            logger.info(
                f"Script {script_id} completed successfully on device {device_id}"
            )

        except Exception as e:
            error_msg = f"Script execution failed: {str(e)}"
            logger.error(f"Script {script_id} on device {device_id} failed: {e}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")

            db.write_log(device_id, f"ERROR: {error_msg}", "ERROR")
            self._handle_script_error(device_id, script_id, error_msg)

        finally:
            # Always clean up
            self._cleanup_device(device_id)

    def _load_script_module(self, script_path: Path):
        """Load a script module from file"""
        try:
            spec = importlib.util.spec_from_file_location("script_module", script_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load script from {script_path}")

            module = importlib.util.module_from_spec(spec)

            # Inject required modules into script namespace
            module.adb = adb
            module.image = image

            spec.loader.exec_module(module)
            return module

        except Exception as e:
            logger.error(f"Failed to load script module {script_path}: {e}")
            raise

    def _prepare_device_info(self, device_id: str) -> Device:
        """Prepare device information for script"""
        device_data = db.get_device(device_id)
        
        if device_data:
            # Use existing device data and update screen size
            try:
                screen_size = adb.get_screen_size(device_id)
                device_data.screen_size = screen_size
            except Exception as e:
                logger.warning(f"Could not get screen size for {device_id}: {e}")
            return device_data
        else:
            # Create new device with basic info
            screen_size = None
            try:
                screen_size = adb.get_screen_size(device_id)
            except Exception as e:
                logger.warning(f"Could not get screen size for {device_id}: {e}")
                
            return Device(
                device_id=device_id,
                device_name=f"Device {device_id}",
                screen_size=screen_size
            )

    def _handle_script_error(self, device_id: str, script_id: str, error_msg: str):
        """Handle script execution errors"""
        try:
            db.write_log(device_id, f"ERROR: {error_msg}", "ERROR")

            # Update device state to stop script
            db.stop_device_script(device_id)

        except Exception as e:
            logger.error(f"Failed to handle script error for device {device_id}: {e}")

    def _cleanup_device(self, device_id: str):
        """Clean up device execution resources"""
        try:
            # Remove from running scripts
            if device_id in self._running_scripts:
                del self._running_scripts[device_id]

            # Process cleanup completed

            logger.debug(f"Cleaned up execution resources for device {device_id}")

        except Exception as e:
            logger.error(f"Failed to cleanup device {device_id}: {e}")


# Global executor instance
executor = Executor()
