"""
Device API endpoints for KVTM Auto
Handles device discovery and logging only
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel

from ..core import adb, db
from ..models import Device, DeviceStatus, GameOptions

router = APIRouter()


class DeviceDetailResponse(BaseModel):
    """Response model for detailed device information"""

    # Basic device information
    id: str
    device_name: str
    device_status: str
    screen_size: Optional[List[int]] = None
    last_seen: Optional[str] = None
    
    # Script execution information
    current_script: Optional[str] = None
    script_name: Optional[str] = None
    game_options: Optional[GameOptions] = None
    
    # Additional device metadata (for future expansion)
    model: Optional[str] = None
    android_version: Optional[str] = None
    api_level: Optional[str] = None
    architecture: Optional[str] = None
    connection_type: Optional[str] = None
    ip_address: Optional[str] = None
    battery_level: Optional[int] = None
    screen_on: Optional[bool] = None
    cpu_usage: Optional[float] = None
    total_storage: Optional[str] = None
    available_storage: Optional[str] = None
    ram: Optional[str] = None
    current_auto: Optional[str] = None


class DeviceLogsResponse(BaseModel):
    """Response model for device logs"""

    device_id: str
    logs: List[dict]
    total_lines: int


@router.get("/", response_model=List[Device])
async def get_all_devices():
    """Get all devices with their status (auto-discovers devices from ADB)"""
    try:
        connected_device_ids = adb.get_list_devices()
        logger.info(f"Found {len(connected_device_ids)} connected devices")

        existing_devices = db.get_all_devices()

        connected_device_set = set(connected_device_ids)
        existing_device_map = {}
        for device in existing_devices:
            if isinstance(device, Device):
                existing_device_map[device.device_id] = device
            else:
                logger.warning(f"Skipping invalid device object: {device}")

        current_time = datetime.now().isoformat()
        devices_to_save = []

        for device_id in connected_device_ids:
            if device_id in existing_device_map:
                device = existing_device_map[device_id]
                
                # Preserve running status if device has current_script, otherwise set to available
                if not device.current_script:
                    device.device_status = DeviceStatus.AVAILABLE.value
                # If device has current_script, keep existing status (could be running)
                
                device.last_seen = current_time

                try:
                    screen_size = adb.get_screen_size(device_id)
                    device.screen_size = screen_size
                except Exception as e:
                    logger.warning(f"Could not get screen size for {device_id}: {e}")

                devices_to_save.append(device)
            else:
                try:
                    screen_size = adb.get_screen_size(device_id)
                except Exception as e:
                    logger.warning(f"Could not get screen size for {device_id}: {e}")
                    screen_size = None

                new_device = Device(
                    id=device_id,
                    device_name=f"Device {device_id}",
                    device_status=DeviceStatus.AVAILABLE.value,
                    screen_size=screen_size,
                    last_seen=current_time,
                )
                devices_to_save.append(new_device)

        # Remove devices that exist in database but not in ADB
        devices_to_remove = []
        for device in existing_devices:
            if (
                isinstance(device, Device)
                and device.device_id not in connected_device_set
            ):
                devices_to_remove.append(device.device_id)

        # Remove old devices from database
        if devices_to_remove:
            removed_count = db.remove_devices(devices_to_remove)
            logger.info(f"Removed {removed_count} disconnected devices from database")

        # Save connected devices (new and updated)
        for device in devices_to_save:
            db.save_device(device)

        # Clean up logs for removed devices
        current_device_ids = [device.device_id for device in devices_to_save]
        cleaned_logs_count = db.clean_device_logs(current_device_ids)
        if cleaned_logs_count > 0:
            logger.info(f"Cleaned logs for {cleaned_logs_count} removed devices")

        return db.get_all_devices()

    except Exception as e:
        logger.error(f"Failed to get devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}", response_model=DeviceDetailResponse)
async def get_device_detail(device_id: str):
    """Get detailed information for a specific device"""
    try:
        device = db.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

        # Prepare the response with basic device information
        response_data = {
            "id": device.device_id,
            "device_name": device.device_name,
            "device_status": device.device_status,
            "screen_size": list(device.screen_size) if device.screen_size else None,
            "last_seen": device.last_seen,
            "current_script": device.current_script,
            "game_options": device.game_options,
        }

        # If device is running a script, get script name
        if device.current_script:
            script = db.get_script(device.current_script)
            if script:
                response_data["script_name"] = script.name
                # Set current_auto for backward compatibility
                response_data["current_auto"] = script.name

        # For now, set default values for additional metadata
        # These could be enhanced in the future with real device info from ADB
        response_data.update({
            "model": f"Android Device {device_id}",
            "connection_type": "USB",
            "screen_on": True if device.device_status == "running" else None,
        })

        return DeviceDetailResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get device detail for {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/logs", response_model=DeviceLogsResponse)
async def get_device_logs(device_id: str, limit: int = 100):
    """Get device logs"""
    try:
        device = db.get_device(device_id)

        if not device:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

        logs = db.get_device_logs(device_id, limit=limit)

        return DeviceLogsResponse(device_id=device_id, logs=logs, total_lines=len(logs))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get logs for device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
