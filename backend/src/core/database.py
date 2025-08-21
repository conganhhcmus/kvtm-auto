"""
Database manager for device state persistence using JSON files
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger
from ..models import Device, DeviceStatus, Script


class Database:
    """JSON database manager for devices and scripts"""

    def __init__(self, data_dir: str = "data"):
        # Database operations will use the direct logger
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



    def _load_devices(self) -> List[Dict[str, Any]]:
        """Load devices data from JSON file"""
        try:
            with open(self.devices_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load devices data: {e}")
            return []

    def _save_devices(self, devices: List[Dict[str, Any]]) -> None:
        """Save devices data to JSON file"""
        try:
            with open(self.devices_file, "w") as f:
                json.dump(devices, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save devices data: {e}")

    def _load_scripts(self) -> List[Dict[str, Any]]:
        """Load scripts data from JSON file"""
        try:
            with open(self.scripts_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load scripts data: {e}")
            return []

    def _save_scripts(self, scripts_data: List[Dict[str, Any]]) -> None:
        """Save scripts data to JSON file"""
        try:
            with open(self.scripts_file, "w") as f:
                json.dump(scripts_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save scripts data: {e}")

    def get_all_scripts(self) -> List[Script]:
        """Get all scripts metadata as Script models"""
        scripts_raw = self._load_scripts()
        
        # Handle both flat array and wrapped object format
        if isinstance(scripts_raw, dict) and "scripts" in scripts_raw:
            scripts_data = scripts_raw["scripts"]
        else:
            scripts_data = scripts_raw
            
        scripts = []
        
        for script_meta in scripts_data:
            try:
                # Simple script model with only required fields
                script_dict = {
                    "id": script_meta.get("id", ""),
                    "name": script_meta.get("name", ""),
                    "description": script_meta.get("description"),
                    "order": script_meta.get("order", 0),
                    "recommend": script_meta.get("recommend", False),
                }
                script = Script(**script_dict)
                scripts.append(script)
            except Exception as e:
                logger.error(f"Failed to parse script metadata {script_meta.get('id', 'unknown')}: {e}")
                continue
        
        return scripts

    def get_script_by_id(self, script_id: str) -> Optional[Script]:
        """Get specific script metadata by ID as Script model"""
        scripts = self.get_all_scripts()
        for script in scripts:
            if script.id == script_id:
                return script
        return None

    def get_script_path(self, script_id: str) -> Path:
        """Get the file path for a script"""
        # Simple approach: script filename = script_id + .py
        backend_dir = self.data_dir.parent
        scripts_dir = backend_dir / "scripts"
        script_path = scripts_dir / f"{script_id}.py"
        
        if not script_path.exists():
            raise FileNotFoundError(f"Script file not found: {script_path}")
            
        return script_path

    def get_all_devices(self) -> List[Device]:
        """Get all devices as Device models"""
        devices_data = self._load_devices()
        devices = []
        
        for device_data in devices_data:
            try:
                device = Device(**device_data)
                devices.append(device)
            except Exception as e:
                device_id = device_data.get('id', 'unknown')
                logger.error(f"Failed to parse device data for {device_id}: {e}")
                continue
        
        return devices

    def get_device(self, device_id: str) -> Optional[Device]:
        """Get specific device as Device model"""
        devices = self._load_devices()
        for device_data in devices:
            if device_data.get("id") == device_id:
                try:
                    return Device(**device_data)
                except Exception as e:
                    logger.error(f"Failed to parse device data for {device_id}: {e}")
                    return None
        return None

    def save_device(self, device: Device) -> None:
        """Save Device model to JSON file"""
        devices = self._load_devices()
        device_dict = device.to_dict()
        device_dict["last_updated"] = datetime.now().isoformat()
        
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
        execution_id: str,
    ) -> None:
        """Set device current script"""
        device = self.get_device(device_id)
        if device:
            device.current_script = script_id
            device.device_running_id = execution_id
            device.device_status = DeviceStatus.RUNNING.value
            self.save_device(device)

    def stop_device_script(self, device_id: str) -> None:
        """Stop device script and clear current script"""
        device = self.get_device(device_id)
        if device and device.current_script:
            # Clear current script and set device as available
            device.current_script = None
            device.device_running_id = None
            device.device_status = DeviceStatus.AVAILABLE.value
            self.save_device(device)

    def _load_device_logs(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load device logs from JSON file"""
        try:
            with open(self.logs_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load device logs: {e}")
            return {}

    def _save_device_logs(self, logs_data: Dict[str, List[Dict[str, Any]]]) -> None:
        """Save device logs to JSON file"""
        try:
            with open(self.logs_file, "w") as f:
                json.dump(logs_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save device logs: {e}")

    def write_log(self, device_id: str, message: str, level: str = "INFO") -> None:
        """Write log entry for specific device"""
        try:
            logs_data = self._load_device_logs()
            
            if device_id not in logs_data:
                logs_data[device_id] = []
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "message": message
            }
            
            logs_data[device_id].append(log_entry)
            
            # Keep only last 1000 logs per device
            if len(logs_data[device_id]) > 1000:
                logs_data[device_id] = logs_data[device_id][-1000:]
            
            self._save_device_logs(logs_data)
            
        except Exception as e:
            logger.error(f"Failed to write log for device {device_id}: {e}")

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




# Global database instance
db = Database()
