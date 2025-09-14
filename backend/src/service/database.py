"""
Database manager for device state persistence using JSON files with file locking
"""

import fcntl
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from ..libs.time_provider import time_provider
from ..models.device import Device, DeviceStatus
from ..models.script import Script, GameOptions


class Database:
    """JSON database manager for devices and scripts"""

    def __init__(self, data_dir: str = "src/data"):
        # Database operations will use the direct logger
        # Convert to absolute path to avoid working directory issues
        if not Path(data_dir).is_absolute():
            # Get the backend directory (parent of src)
            backend_dir = Path(__file__).parent.parent.parent
            self.data_dir = backend_dir / data_dir
        else:
            self.data_dir = Path(data_dir)
        self.devices_file = self.data_dir / "devices.json"
        self.scripts_file = self.data_dir / "scripts.json"
        self.logs_file = self.data_dir / "logs.json"

        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize files if not exist
        if not self.devices_file.exists():
            self._save_devices([])
        if not self.scripts_file.exists():
            self._save_scripts([])
        if not self.logs_file.exists():
            self._save_device_logs({})

    def _acquire_file_lock(self, file_handle, timeout: float = 5.0) -> bool:
        """Acquire exclusive file lock with timeout"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                fcntl.flock(file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return True
            except (IOError, OSError):
                time.sleep(0.1)
        return False

    def _release_file_lock(self, file_handle):
        """Release file lock"""
        try:
            fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)
        except (IOError, OSError) as e:
            logger.warning(f"Failed to release file lock: {e}")

    def _load_devices(self) -> List[Dict[str, Any]]:
        """Load devices data from JSON file with file locking"""
        try:
            with open(self.devices_file, "r") as f:
                if self._acquire_file_lock(f):
                    try:
                        data = json.load(f)
                        return data
                    finally:
                        self._release_file_lock(f)
                else:
                    logger.warning("Failed to acquire file lock for reading devices data")
                    # Fallback: try without lock
                    f.seek(0)
                    return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load devices data: {e}")
            return []

    def _save_devices(self, devices: List[Dict[str, Any]]) -> None:
        """Save devices data to JSON file with file locking"""
        try:
            # Write to temporary file first, then rename for atomic operation
            temp_file = self.devices_file.with_suffix('.tmp')
            
            with open(temp_file, "w") as f:
                if self._acquire_file_lock(f):
                    try:
                        json.dump(devices, f, indent=2, default=str)
                        f.flush()
                    finally:
                        self._release_file_lock(f)
                else:
                    logger.warning("Failed to acquire file lock for writing devices data")
                    # Write anyway, but log the warning
                    json.dump(devices, f, indent=2, default=str)
                    f.flush()
            
            # Atomic rename
            temp_file.replace(self.devices_file)
            
        except Exception as e:
            logger.error(f"Failed to save devices data: {e}")
            # Clean up temp file if it exists
            temp_file = self.devices_file.with_suffix('.tmp')
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    pass

    def _load_scripts(self) -> List[Dict[str, Any]]:
        """Load scripts data from JSON file with file locking"""
        try:
            with open(self.scripts_file, "r") as f:
                if self._acquire_file_lock(f):
                    try:
                        data = json.load(f)
                        return data
                    finally:
                        self._release_file_lock(f)
                else:
                    logger.warning("Failed to acquire file lock for reading scripts data")
                    f.seek(0)
                    return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load scripts data: {e}")
            return []

    def _save_scripts(self, scripts_data: List[Dict[str, Any]]) -> None:
        """Save scripts data to JSON file with file locking"""
        try:
            temp_file = self.scripts_file.with_suffix('.tmp')
            
            with open(temp_file, "w") as f:
                if self._acquire_file_lock(f):
                    try:
                        json.dump(scripts_data, f, indent=2, default=str)
                        f.flush()
                    finally:
                        self._release_file_lock(f)
                else:
                    logger.warning("Failed to acquire file lock for writing scripts data")
                    json.dump(scripts_data, f, indent=2, default=str)
                    f.flush()
            
            temp_file.replace(self.scripts_file)
            
        except Exception as e:
            logger.error(f"Failed to save scripts data: {e}")
            temp_file = self.scripts_file.with_suffix('.tmp')
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    pass

    def get_scripts_data(self) -> List[Dict[str, Any]]:
        """Get raw scripts data from JSON file"""
        scripts_raw = self._load_scripts()

        # Handle both flat array and wrapped object format
        if isinstance(scripts_raw, dict) and "scripts" in scripts_raw:
            return scripts_raw["scripts"]
        else:
            return scripts_raw

    def save_scripts_data(self, scripts_data: List[Dict[str, Any]]) -> None:
        """Save raw scripts data to JSON file"""
        self._save_scripts(scripts_data)

    def get_all_devices(self) -> List[Device]:
        """Get all devices as Device models"""
        devices_data = self._load_devices()
        devices = []

        for device_data in devices_data:
            try:
                if not isinstance(device_data, dict):
                    logger.warning(
                        f"Skipping invalid device data (not dict): {device_data}"
                    )
                    continue

                # Convert game_options dict to GameOptions model if present
                if device_data.get("game_options") and isinstance(device_data["game_options"], dict):
                    device_data["game_options"] = GameOptions(**device_data["game_options"])
                
                device = Device(**device_data)
                devices.append(device)
            except Exception as e:
                device_id = (
                    device_data.get("id", "unknown")
                    if isinstance(device_data, dict)
                    else "unknown"
                )
                logger.error(f"Failed to parse device data for {device_id}: {e}")
                logger.debug(f"Device data: {device_data}")
                continue

        return devices

    def get_device(self, device_id: str) -> Optional[Device]:
        """Get specific device as Device model"""
        devices = self._load_devices()
        for device_data in devices:
            if device_data.get("id") == device_id:
                try:
                    # Convert game_options dict to GameOptions model if present
                    if device_data.get("game_options") and isinstance(device_data["game_options"], dict):
                        device_data["game_options"] = GameOptions(**device_data["game_options"])
                    
                    return Device(**device_data)
                except Exception as e:
                    logger.error(f"Failed to parse device data for {device_id}: {e}")
                    return None
        return None

    def save_device(self, device: Device) -> None:
        """Save Device model to JSON file"""
        devices = self._load_devices()
        device_dict = device.to_dict()
        device_dict["last_updated"] = time_provider.local_now_iso()

        # Find existing device or create new one
        device_found = False
        for i, existing_device in enumerate(devices):
            if existing_device.get("id") == device.device_id:
                devices[i] = device_dict
                device_found = True
                break

        if not device_found:
            devices.append(device_dict)

        self._save_devices(devices)
        logger.info(f"Device {device.device_id} saved successfully")

    def set_device_status(self, device_id: str, status: DeviceStatus) -> None:
        """Set device status"""
        device = self.get_device(device_id)
        if device:
            device.device_status = status.value
            self.save_device(device)

    def set_device_script(
        self,
        device_id: str,
        script_id: str,
        game_options: Optional[GameOptions] = None,
    ) -> None:
        """Set device current script and game options"""
        device = self.get_device(device_id)
        if device:
            device.current_script = script_id
            device.device_status = DeviceStatus.RUNNING.value
            device.game_options = game_options
            self.save_device(device)

    def stop_device_script(self, device_id: str) -> None:
        """Stop device script and clear current script"""
        device = self.get_device(device_id)
        if device and device.current_script:
            # Clear current script, game options and set device as available
            device.current_script = None
            device.game_options = None
            device.device_status = DeviceStatus.AVAILABLE.value
            self.save_device(device)

    def _load_device_logs(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load device logs from JSON file"""
        try:
            with open(self.logs_file, "r") as f:
                content = f.read().strip()
                if not content:
                    logger.warning("Device logs file is empty, initializing with empty dict")
                    return {}
                return json.loads(content)
        except FileNotFoundError:
            logger.info("Device logs file not found, initializing with empty dict")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse device logs JSON: {e}")
            # Try to backup corrupted file
            try:
                backup_file = self.logs_file.with_suffix('.backup')
                self.logs_file.rename(backup_file)
                logger.info(f"Corrupted logs file backed up to {backup_file}")
            except Exception as backup_error:
                logger.error(f"Failed to backup corrupted logs file: {backup_error}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error loading device logs: {e}")
            return {}

    def _save_device_logs(self, logs_data: Dict[str, List[Dict[str, Any]]]) -> None:
        """Save device logs to JSON file with atomic write"""
        try:
            # Write to temporary file first, then rename for atomic operation
            temp_file = self.logs_file.with_suffix('.tmp')
            
            with open(temp_file, "w") as f:
                json.dump(logs_data, f, indent=2, default=str)
                f.flush()
            
            # Atomic rename
            temp_file.replace(self.logs_file)
            
        except Exception as e:
            logger.error(f"Failed to save device logs: {e}")
            # Clean up temp file if it exists
            temp_file = self.logs_file.with_suffix('.tmp')
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    pass

    def write_log(self, device_id: str, action: str, index: Optional[str] = None) -> None:
        """Write formatted log entry for specific device: [Time]: [Action] [Index]"""
        formatted_message = time_provider.create_log_message(action, index)
        self.write_script_log(device_id, formatted_message)

    def write_script_log(self, device_id: str, formatted_message: str) -> None:
        """Write pre-formatted log message for specific device"""
        logs_data = self._load_device_logs()

        if device_id not in logs_data:
            logs_data[device_id] = []

        # Store the formatted message directly (no timestamp/level needed)
        log_entry = {
            "message": formatted_message,
            "level": "INFO",
            "created_at": time_provider.local_now_iso()  # Keep for internal sorting/management
        }

        logs_data[device_id].append(log_entry)

        # Keep only last 1000 logs per device
        if len(logs_data[device_id]) > 1000:
            logs_data[device_id] = logs_data[device_id][-1000:]

        self._save_device_logs(logs_data)

    def write_legacy_log(self, device_id: str, message: str, level: str = "INFO") -> None:
        """Legacy log method for backward compatibility"""
        logs_data = self._load_device_logs()

        if device_id not in logs_data:
            logs_data[device_id] = []

        log_entry = {
            "timestamp": time_provider.local_now_iso(),
            "level": level,
            "message": message,
        }

        logs_data[device_id].append(log_entry)

        # Keep only last 1000 logs per device
        if len(logs_data[device_id]) > 1000:
            logs_data[device_id] = logs_data[device_id][-1000:]

        self._save_device_logs(logs_data)

    def get_device_logs(self, device_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get logs for specific device"""
        try:
            logs_data = self._load_device_logs()
            device_logs = logs_data.get(device_id, [])

            if limit:
                return device_logs[-limit:]
            return device_logs

        except Exception as e:
            logger.error(f"Failed to get logs for device {device_id}: {e}")
            return []

    def clear_device_logs(self, device_id: str) -> None:
        """Clear logs for specific device"""
        try:
            logs_data = self._load_device_logs()

            if device_id in logs_data:
                logs_data[device_id] = []
                self._save_device_logs(logs_data)

        except Exception as e:
            logger.error(f"Failed to clear logs for device {device_id}: {e}")

    def get_all_scripts(self) -> List[Script]:
        """Get all scripts as Script models"""
        scripts_data = self._load_scripts()
        scripts = []

        for script_data in scripts_data:
            try:
                if not isinstance(script_data, dict):
                    logger.warning(
                        f"Skipping invalid script data (not dict): {script_data}"
                    )
                    continue

                script = Script(**script_data)
                scripts.append(script)
            except Exception as e:
                script_id = (
                    script_data.get("id", "unknown")
                    if isinstance(script_data, dict)
                    else "unknown"
                )
                logger.error(f"Failed to parse script data for {script_id}: {e}")
                logger.debug(f"Script data: {script_data}")
                continue

        return scripts

    def get_script(self, script_id: str) -> Optional[Script]:
        """Get specific script as Script model"""
        scripts_data = self._load_scripts()
        for script_data in scripts_data:
            if script_data.get("id") == script_id:
                try:
                    return Script(**script_data)
                except Exception as e:
                    logger.error(f"Failed to parse script data for {script_id}: {e}")
                    return None
        return None

    def save_script(self, script: Script) -> None:
        """Save Script model to JSON file"""
        scripts_data = self._load_scripts()
        script_dict = script.model_dump()
        script_dict["last_updated"] = time_provider.local_now_iso()

        # Find existing script or create new one
        script_found = False
        for i, existing_script in enumerate(scripts_data):
            if existing_script.get("id") == script.id:
                scripts_data[i] = script_dict
                script_found = True
                break

        if not script_found:
            scripts_data.append(script_dict)

        self._save_scripts(scripts_data)
        logger.info(f"Script {script.id} saved successfully")

    def save_scripts(self, scripts: List[Script]) -> None:
        """Save multiple Script models to JSON file"""
        scripts_data = []
        for script in scripts:
            script_dict = script.model_dump()
            script_dict["last_updated"] = time_provider.local_now_iso()
            scripts_data.append(script_dict)

        self._save_scripts(scripts_data)
        logger.info(f"Saved {len(scripts)} scripts to database")

    def script_exists(self, script_id: str) -> bool:
        """Check if script exists in database"""
        return self.get_script(script_id) is not None

    def remove_device(self, device_id: str) -> bool:
        """Remove specific device from database"""
        devices = self._load_devices()
        initial_count = len(devices)
        
        devices = [device for device in devices if device.get("id") != device_id]
        
        if len(devices) < initial_count:
            self._save_devices(devices)
            logger.info(f"Device {device_id} removed from database")
            return True
        else:
            logger.warning(f"Device {device_id} not found in database")
            return False

    def remove_devices(self, device_ids: List[str]) -> int:
        """Remove multiple devices from database"""
        devices = self._load_devices()
        initial_count = len(devices)
        
        device_id_set = set(device_ids)
        devices = [device for device in devices if device.get("id") not in device_id_set]
        
        removed_count = initial_count - len(devices)
        if removed_count > 0:
            self._save_devices(devices)
            logger.info(f"Removed {removed_count} devices from database: {device_ids}")
        
        return removed_count

    def clean_device_logs(self, existing_device_ids: List[str]) -> int:
        """Remove logs for devices that no longer exist"""
        logs_data = self._load_device_logs()
        initial_log_count = len(logs_data)
        
        existing_device_set = set(existing_device_ids)
        cleaned_logs = {
            device_id: logs for device_id, logs in logs_data.items() 
            if device_id in existing_device_set
        }
        
        removed_log_count = initial_log_count - len(cleaned_logs)
        if removed_log_count > 0:
            self._save_device_logs(cleaned_logs)
            logger.info(f"Cleaned logs for {removed_log_count} non-existent devices")
        
        return removed_log_count


# Global database instance
db = Database()
