"""
Script models for KVTM Auto Backend
Simple script models for basic script management
"""

from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator, validator


class GameOptions(BaseModel):
    """Model for game configuration options."""

    open_game: bool = Field(
        default=False,
        description="Whether to run script open_game.py in scripts folder",
    )
    open_chest: bool = Field(default=False, description="Whether to open chest in game")
    sell_items: bool = Field(
        default=False, description="Whether to sell items after crafting"
    )
    max_loops: int = Field(
        default=1000,
        description="Maximum number of times to loop the script execution (hardcoded)",
    )
    loop_delay: float = Field(
        default=1.0, description="Delay between loop iterations in seconds (hardcoded)"
    )
    game_load_wait: float = Field(
        default=10.0, description="Time to wait for game to load in seconds"
    )

    @field_validator("open_game", "open_chest", "sell_items", mode="before")
    @classmethod
    def convert_yes_no_to_bool(cls, value: Union[str, bool]) -> bool:
        """Convert yes/no strings to boolean values."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("yes", "y", "true", "1")
        return bool(value)

    @field_validator("max_loops")
    @classmethod
    def validate_max_loops(cls, value: int) -> int:
        """Validate max_loops is positive."""
        if value < 1:
            raise ValueError("max_loops must be at least 1")
        if value > 1000:
            raise ValueError("max_loops cannot exceed 1000")
        return value

    @field_validator("loop_delay", "game_load_wait")
    @classmethod
    def validate_delays(cls, value: float) -> float:
        """Validate delay values are non-negative."""
        if value < 0:
            raise ValueError("Delay values must be non-negative")
        return value

    def __str__(self) -> str:
        """String representation of game options."""
        return (
            f"GameOptions(open_game={self.open_game}, "
            f"open_chest={self.open_chest}, sell_items={self.sell_items}, "
            f"max_loops={self.max_loops}, loop_delay={self.loop_delay}, "
            f"game_load_wait={self.game_load_wait})"
        )


class Script(BaseModel):
    """Simple script model"""

    id: str = Field(
        ..., description="Unique script identifier (same as script filename)"
    )
    name: str = Field(..., description="Human-readable script name")
    description: Optional[str] = Field(None, description="Script description")
    order: int = Field(default=0, description="Display order")
    recommend: bool = Field(default=False, description="Whether script is recommended")

    @validator("id")
    def validate_id(cls, v):
        if not v or not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Script ID must be alphanumeric or contain underscores/hyphens"
            )
        return v

    @validator("order")
    def validate_order(cls, v):
        if v < 0:
            raise ValueError("Order must be non-negative")
        return v
