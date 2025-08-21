"""
Script API endpoints for KVTM Auto
Handles script metadata operations only
"""

from typing import List

from fastapi import APIRouter, HTTPException
from loguru import logger

from ..core import db
from ..models import Script

router = APIRouter()

@router.get("/", response_model=List[Script])
async def get_all_scripts():
    """Get all available scripts from metadata"""
    try:
        scripts = db.get_all_scripts()
        scripts.sort(key=lambda x: x.order)
        
        logger.info(f"Found {len(scripts)} scripts from metadata")
        return scripts
        
    except Exception as e:
        logger.error(f"Failed to get scripts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{script_id}", response_model=Script)
async def get_script_by_id(script_id: str):
    """Get specific script by ID"""
    try:
        script = db.get_script_by_id(script_id)
        
        if not script:
            raise HTTPException(status_code=404, detail=f"Script {script_id} not found")
            
        return script
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get script {script_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
