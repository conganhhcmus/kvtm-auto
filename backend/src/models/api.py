"""
API models for KVTM Auto Backend
Unified request/response models for all API endpoints
"""

from typing import List, Optional, Union
from pydantic import BaseModel

from .script import GameOptions


# Execute API Models
class StartRequest(BaseModel):
    """Start script execution request"""
    device_ids: Union[str, List[str]]
    script_id: str
    game_options: Optional[GameOptions] = None


class StartResponse(BaseModel):
    """Start script execution response"""
    message: str
    started_devices: List[str]
    failed_devices: List[str]


class StopRequest(BaseModel):
    """Stop script execution request"""
    device_id: str


class StopResponse(BaseModel):
    """Stop script execution response"""
    message: str
    script_id: str


class StopAllRequest(BaseModel):
    """Stop all running scripts request"""
    pass


class StopAllResponse(BaseModel):
    """Stop all running scripts response"""
    message: str
    total_devices: int
    stopped_devices: List[str]
    failed_devices: List[str]
    device_details: List[dict]


class StatusResponse(BaseModel):
    """Execution status response"""
    device_id: str
    status: str
    script_id: Optional[str] = None


# Device API Models
class DeviceDetailResponse(BaseModel):
    """Response model for detailed device information"""
    id: str
    device_name: str
    device_status: str
    screen_size: Optional[List[int]] = None
    last_seen: Optional[str] = None
    current_script: Optional[str] = None
    game_options: Optional[GameOptions] = None
    script_name: Optional[str] = None
    current_auto: Optional[str] = None
    model: Optional[str] = None
    connection_type: Optional[str] = None
    screen_on: Optional[bool] = None


class DeviceLogsResponse(BaseModel):
    """Response model for device logs"""
    device_id: str
    logs: List[dict]
    total_lines: int


# Script API Models
class ScriptResponse(BaseModel):
    """Response model for script information"""
    id: str
    name: str
    description: Optional[str] = None
    order: int = 0
    recommend: bool = False


class ScriptListResponse(BaseModel):
    """Response model for script list"""
    scripts: List[ScriptResponse]
    total: int


class ScriptDetailResponse(BaseModel):
    """Response model for detailed script information"""
    id: str
    name: str
    description: Optional[str] = None
    order: int = 0
    recommend: bool = False
    path: Optional[str] = None
    last_modified: Optional[str] = None