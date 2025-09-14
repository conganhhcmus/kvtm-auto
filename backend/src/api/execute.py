"""
Execute API endpoints for KVTM Auto
Simplified script execution operations
"""


from fastapi import APIRouter, BackgroundTasks, HTTPException

from ..models.api import StartRequest, StartResponse, StopRequest, StopResponse, StopAllResponse
from ..models.device import DeviceStatus
from ..models.script import GameOptions
from ..service.database import db
from ..service.executor import executor

router = APIRouter()


@router.post("/start", response_model=StartResponse)
async def start_script(request: StartRequest, background_tasks: BackgroundTasks):
    """Start script execution on device(s)"""
    # Normalize device_ids to list
    device_ids = [request.device_ids] if isinstance(request.device_ids, str) else request.device_ids
    
    if not device_ids:
        raise HTTPException(status_code=400, detail="No devices specified")

    # Use provided game_options or default
    game_options = request.game_options or GameOptions()
    game_options.max_loops = 1000  # Hardcoded max
    game_options.loop_delay = 1.0  # Hardcoded delay

    started_devices = []
    failed_devices = []

    for device_id in device_ids:
        device = db.get_device(device_id)
        
        if not device:
            failed_devices.append(device_id)
            continue

        if device.device_status != DeviceStatus.AVAILABLE.value or device.current_script:
            failed_devices.append(device_id)
            continue

        # Set device script and start execution
        db.set_device_script(device_id, request.script_id, game_options)
        
        background_tasks.add_task(
            executor.run,
            device_id=device_id,
            script_id=request.script_id,
            game_options=game_options,
        )
        
        started_devices.append(device_id)

    if not started_devices:
        raise HTTPException(status_code=400, detail="Failed to start script on any device")

    success_count = len(started_devices)
    total_count = len(device_ids)
    
    if success_count == total_count:
        message = f"Script {request.script_id} started on all {success_count} device(s)"
    else:
        message = f"Script {request.script_id} started on {success_count}/{total_count} device(s)"

    return StartResponse(
        message=message,
        started_devices=started_devices,
        failed_devices=failed_devices
    )


@router.post("/stop", response_model=StopResponse)
async def stop_script(request: StopRequest):
    """Stop script execution on device"""
    device = db.get_device(request.device_id)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if not device.current_script:
        raise HTTPException(status_code=400, detail="Device is not running any script")

    script_id = device.current_script
    executor.stop(request.device_id)
    
    return StopResponse(
        message=f"Script stopped on device {request.device_id}",
        script_id=script_id
    )


@router.post("/stop-all", response_model=StopAllResponse)
async def stop_all_scripts():
    """Stop all running scripts"""
    all_devices = db.get_all_devices()
    executor_running_devices = executor.get_running_devices()
    
    # Find devices that are running scripts
    running_devices = [
        device for device in all_devices 
        if (device.current_script and device.device_status == DeviceStatus.RUNNING.value) 
        or device.id in executor_running_devices
    ]
    
    if not running_devices:
        return StopAllResponse(
            message="No running devices found",
            total_devices=0,
            stopped_devices=[],
            failed_devices=[],
            device_details=[]
        )
    
    stopped_devices = []
    failed_devices = []
    device_details = []
    
    for device in running_devices:
        device_id = device.id
        script_id = device.current_script
        
        if executor.stop(device_id, timeout=3.0):
            stopped_devices.append(device_id)
            device_details.append({
                "device_id": device_id,
                "device_name": device.device_name,
                "script_id": script_id,
                "status": "stopped"
            })
        else:
            failed_devices.append(device_id)
            device_details.append({
                "device_id": device_id,
                "device_name": device.device_name,
                "script_id": script_id,
                "status": "failed"
            })
    
    total_devices = len(running_devices)
    success_count = len(stopped_devices)
    
    if success_count == total_devices:
        message = f"Successfully stopped scripts on all {success_count} device(s)"
    elif success_count == 0:
        message = f"Failed to stop scripts on all {total_devices} device(s)"
    else:
        message = f"Stopped scripts on {success_count}/{total_devices} device(s)"
    
    return StopAllResponse(
        message=message,
        total_devices=total_devices,
        stopped_devices=stopped_devices,
        failed_devices=failed_devices,
        device_details=device_details
    )