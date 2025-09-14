"""
Direct script execution system for KVTM Auto
Handles direct import and execution of script modules without shell commands
"""

import importlib
import threading
import time
from typing import Dict, Optional, Any

from loguru import logger

from ..models.device import Device, DeviceStatus
from ..models.script import GameOptions
from .database import db
from ..libs.time_provider import time_provider



def _should_stop_execution(device_id: str) -> bool:
    """Check if script execution should stop by checking device status"""
    device = db.get_device(device_id)
    if not device:
        return True  # Stop if device doesn't exist
    # Stop if device status is not RUNNING
    return device.device_status != DeviceStatus.RUNNING.value


class ScriptRunner:
    """Direct Python script execution system"""

    def __init__(self):
        self._running_threads: Dict[str, threading.Thread] = {}
    
    def run_script(
        self,
        device_id: str,
        script_id: str,
        game_options: GameOptions
    ):
        """Execute a script directly by importing and calling its main function"""
        if self.is_running(device_id):
            logger.warning(f"Device {device_id} is already running a script")
            return

        # Start execution in separate thread
        thread = threading.Thread(
            target=self._execute_script_with_loops,
            args=(device_id, script_id, game_options),
            daemon=True
        )
        self._running_threads[device_id] = thread
        thread.start()

        logger.info(f"Started direct execution of script {script_id} on device {device_id}")
    
    def _execute_script_with_loops(
        self,
        device_id: str,
        script_id: str,
        game_options: GameOptions
    ):
        """Execute script with looping logic"""
        try:
            device = Device(id=device_id, name=f"Device {device_id}")

            # Execute open_game script if needed
            if game_options.open_game:
                try:
                    self._run_single_script(device, "open_game", game_options)
                    if _should_stop_execution(device_id):
                        return
                except Exception as e:
                    logger.error(f"Open game script failed: {e}")
                    db.write_script_log(device_id, f"ERROR: Open game failed: {e}")
                    return
                
            # Execute main script with loops
            for loop_index in range(game_options.max_loops):
                if _should_stop_execution(device_id):
                    break

                try:
                    db.write_script_log(
                        device_id,
                        f"[{self._get_current_time()}]: Loop [{loop_index + 1}/{game_options.max_loops}]"
                    )

                    result = self._run_single_script(device, script_id, game_options)

                    if not result or not result.get("success", True):
                        error_msg = result.get("message", "Script execution failed") if result else "Script returned no result"
                        db.write_script_log(device_id, f"ERROR: {error_msg}")
                        break

                    # Loop delay
                    if loop_index < game_options.max_loops - 1 and game_options.loop_delay > 0:
                        if _should_stop_execution(device_id):
                            break
                        db.write_script_log(
                            device_id,
                            f"[{self._get_current_time()}]: Waiting [{game_options.loop_delay}s]"
                        )
                        # Check for stop during sleep in smaller intervals
                        sleep_time = game_options.loop_delay
                        while sleep_time > 0 and not _should_stop_execution(device_id):
                            interval = min(0.5, sleep_time)
                            time.sleep(interval)
                            sleep_time -= interval

                except Exception as e:
                    logger.error(f"Script execution failed on loop {loop_index + 1}: {e}")
                    db.write_script_log(device_id, f"ERROR: Loop {loop_index + 1} failed: {e}")
                    break

            if not _should_stop_execution(device_id):
                db.write_script_log(
                    device_id,
                    f"[{self._get_current_time()}]: Script completed successfully after {game_options.max_loops} loop(s)"
                )

        except Exception as e:
            logger.error(f"Script execution failed for device {device_id}: {e}")
            db.write_script_log(device_id, f"ERROR: Script execution failed: {e}")
        finally:
            self._cleanup_device(device_id)
    
    def _run_single_script(
        self,
        device: Device,
        script_id: str,
        game_options: GameOptions
    ) -> Optional[Dict[str, Any]]:
        """Execute a single script by importing and calling main function"""
        try:
            # Import script module dynamically
            module_name = f"src.scripts.{script_id}"
            module = importlib.import_module(module_name)

            # Get main function
            if not hasattr(module, 'main'):
                raise AttributeError(f"Script {script_id} does not have a main function")

            main_function = getattr(module, 'main')

            # Execute script - device.id is available in device object
            result = main_function(device, game_options)
            return result

        except ImportError as e:
            raise Exception(f"Failed to import script {script_id}: {e}")
        except Exception as e:
            raise Exception(f"Script {script_id} execution failed: {e}")
    
    def stop_script(self, device_id: str, timeout: float = 5.0) -> bool:
        """Stop script execution for a device"""
        logger.info(f"Stopping direct script execution for device {device_id}")

        # Update database - this sets the stop signal
        db.stop_device_script(device_id)

        # Wait for thread to finish
        if device_id in self._running_threads:
            thread = self._running_threads[device_id]
            thread.join(timeout=timeout)

            if thread.is_alive():
                logger.warning(f"Script thread for device {device_id} did not stop gracefully")
                return False

        self._cleanup_device(device_id)
        logger.info(f"Stopped direct script execution for device {device_id}")
        return True
    
    def is_running(self, device_id: str) -> bool:
        """Check if a device is running a script"""
        if device_id not in self._running_threads:
            return False
        
        thread = self._running_threads[device_id]
        is_alive = thread.is_alive()
        
        if not is_alive:
            self._cleanup_device(device_id)
        
        return is_alive
    
    def get_running_devices(self) -> list[str]:
        """Get list of devices currently running scripts"""
        running_devices = []
        
        for device_id in list(self._running_threads.keys()):
            if self.is_running(device_id):
                running_devices.append(device_id)
        
        return running_devices
    
    def shutdown_all(self) -> dict:
        """Shutdown all running scripts"""
        running_devices = list(self._running_threads.keys())
        
        if not running_devices:
            return {"total": 0, "stopped": [], "failed": []}
        
        stopped_devices = []
        failed_devices = []
        
        for device_id in running_devices:
            if self.stop_script(device_id, timeout=3.0):
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
        if device_id in self._running_threads:
            del self._running_threads[device_id]

        # Release device in database
        db.stop_device_script(device_id)
        logger.debug(f"Cleaned up direct execution resources for device {device_id}")
    
    def _get_current_time(self) -> str:
        """Get current time in log format"""
        return time_provider.format_time_for_log().strip('[]')


# Global script runner instance
script_runner = ScriptRunner()