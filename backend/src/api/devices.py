"""
Device API endpoints for KVTM Auto
Handles device discovery and logging only
"""

from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel

from ..core import adb, db
from ..models import Device, DeviceStatus

router = APIRouter()


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
