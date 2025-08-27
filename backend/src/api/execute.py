"""
Execute API endpoints for KVTM Auto
Handles script execution operations (start/stop)
"""

from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from loguru import logger
from pydantic import BaseModel

from ..core import db, executor
from ..models import DeviceStatus, GameOptions

router = APIRouter()


class StartRequest(BaseModel):
    """Start script execution request"""

    device_id: str
    script_id: str
    game_options: Optional[GameOptions] = None


class StartResponse(BaseModel):
    """Start script execution response"""

    message: str


class StopRequest(BaseModel):
    """Stop script execution request"""

    device_id: str


class StopResponse(BaseModel):
    """Stop script execution response"""

    message: str
    script_id: str


class StatusResponse(BaseModel):
    """Execution status response"""

    device_id: str
    status: str
    script_id: Optional[str] = None


@router.post("/start", response_model=StartResponse)
async def start_script(request: StartRequest, background_tasks: BackgroundTasks):
    """Start script execution on device"""
    try:
        # Check if device exists
        device = db.get_device(request.device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        # Check if device is available
        if device.device_status != DeviceStatus.AVAILABLE.value:
            raise HTTPException(status_code=400, detail="Device is not available")

        if device.current_script:
            raise HTTPException(
                status_code=400, detail="Device is already running a script"
            )

        # Check if script exists in database
        if not db.script_exists(request.script_id):
            raise HTTPException(status_code=404, detail="Script not found")

        # Always use hardcoded values for max_loops and loop_delay
        game_options = request.game_options or GameOptions()
        game_options.max_loops = 1000  # Hardcoded max
        game_options.loop_delay = 1.0  # Hardcoded delay

        # Set device script (also sets status to running and saves)
        db.set_device_script(
            device_id=request.device_id,
            script_id=request.script_id,
            game_options=game_options,
        )

        logger.info(
            f"Starting script {request.script_id} on device {request.device_id}"
        )

        # Execute script in background
        background_tasks.add_task(
            executor.run,
            device_id=request.device_id,
            script_id=request.script_id,
            game_options=game_options,
        )

        return StartResponse(
            message=f"Script {request.script_id} started on device {request.device_id}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start script on device {request.device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop", response_model=StopResponse)
async def stop_script(request: StopRequest):
    """Stop current script execution on device"""
    try:
        device = db.get_device(request.device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        if not device.current_script:
            raise HTTPException(
                status_code=400, detail="Device is not running any script"
            )

        script_id = device.current_script

        executor.stop(request.device_id)
        # Stop device script (also sets status to available and saves)
        db.stop_device_script(request.device_id)

        logger.info(f"Stopped script {script_id} on device {request.device_id}")

        return StopResponse(
            message=f"Script stopped on device {request.device_id}", script_id=script_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop script on device {request.device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

