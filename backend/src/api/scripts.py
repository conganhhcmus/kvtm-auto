"""
Script API endpoints for KVTM Auto
Simplified script metadata operations
"""

from typing import List

from fastapi import APIRouter, HTTPException
from loguru import logger

from ..service.database import db
from ..service.script import script_manager
from ..models.script import Script
from ..models.api import ScriptListResponse, ScriptDetailResponse

router = APIRouter()

# Scripts to hide from UI
HIDDEN_SCRIPTS = ["_core", "open_game"]


@router.get("/", response_model=List[Script])
async def get_all_scripts():
    """Get all available scripts"""
    # Discover scripts from filesystem
    filesystem_scripts = script_manager.discover_scripts()
    
    # Sync to database
    db.save_scripts(filesystem_scripts)
    
    # Filter hidden scripts and sort
    visible_scripts = [
        script for script in filesystem_scripts if script.id not in HIDDEN_SCRIPTS
    ]
    
    # Sort by recommend (True first), then by order
    visible_scripts.sort(key=lambda x: (not x.recommend, x.order))
    
    return visible_scripts


@router.get("/{script_id}", response_model=Script)
async def get_script_detail(script_id: str):
    """Get detailed information for a specific script"""
    script = db.get_script(script_id)
    
    if not script:
        raise HTTPException(status_code=404, detail=f"Script {script_id} not found")
    
    return script