"""Device models for KVTM Auto Backend."""

from enum import Enum
from typing import Optional, Tuple

from pydantic import BaseModel, Field

from .script import GameOptions


class DeviceStatus(Enum):
    """Device status."""

    AVAILABLE = "available"
    RUNNING = "running"


class Device(BaseModel):
    """Comprehensive device model for API responses and script parameters."""

    device_id: str = Field(alias="id", description="Unique device identifier")
    device_name: str = Field(description="Device display name")
    device_status: str = Field(
        default=DeviceStatus.AVAILABLE.value, description="Current device status"
    )

    # Additional fields for API and database compatibility
    screen_size: Optional[Tuple[int, int]] = Field(
        default=None, description="Device screen dimensions"
    )
    last_seen: Optional[str] = Field(default=None, description="Last seen timestamp")
    current_script: Optional[str] = Field(
        default=None, description="Currently running script ID"
    )
    game_options: Optional[GameOptions] = Field(
        default=None, description="Game options when script is running"
    )

    class Config:
        populate_by_name = True

    def __init__(self, **data):
        # Auto-generate device_name from device_id if not provided
        if "device_name" not in data and ("id" in data or "device_id" in data):
            device_id = data.get("id") or data.get("device_id")
            data["device_name"] = f"Device {device_id}"
        super().__init__(**data)

    @property
    def id(self) -> str:
        """Backward compatibility property."""
        return self.device_id

    @property
    def name(self) -> str:
        """Backward compatibility property."""
        return self.device_name

    @property
    def status(self) -> str:
        """Backward compatibility property."""
        return self.device_status

    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return self.model_dump(by_alias=True, exclude_none=True)
