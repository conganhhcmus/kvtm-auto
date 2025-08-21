"""
Script API endpoints for KVTM Auto
Handles script metadata operations only
"""

from typing import List

from fastapi import APIRouter, HTTPException
from loguru import logger

from ..core import db
from ..core.script import script_manager
from ..models import Script

router = APIRouter()

# Scripts to hide from UI
HIDDEN_SCRIPTS = ["_core", "open_game"]  # Add script IDs that should not be shown in UI

@router.get("/", response_model=List[Script])
async def get_all_scripts():
    """Get all available scripts by syncing filesystem discovery with database"""
    try:
        # Step 1: Discover scripts from filesystem using ScriptManager
        filesystem_scripts = script_manager.discover_scripts()
        logger.debug(f"Discovered {len(filesystem_scripts)} scripts from filesystem")
        
        # Step 2: Get existing scripts from database
        database_scripts = db.get_all_scripts()
        logger.debug(f"Found {len(database_scripts)} scripts in database")
        
        # Step 3: Sync filesystem scripts to database (filesystem is source of truth)
        db.save_scripts(filesystem_scripts)
        logger.info(f"Synced {len(filesystem_scripts)} scripts to database")
        
        # Step 4: Get updated scripts from database and filter hidden ones
        all_scripts = db.get_all_scripts()
        visible_scripts = [
            script for script in all_scripts 
            if script.id not in HIDDEN_SCRIPTS
        ]
        
        # Sort by order
        visible_scripts.sort(key=lambda x: x.order)
        
        logger.info(f"Returning {len(visible_scripts)} visible scripts (total: {len(all_scripts)})")
        return visible_scripts
        
    except Exception as e:
        logger.error(f"Failed to sync and get scripts: {e}")
        
        # Fallback: try to get scripts from database only
        try:
            logger.warning("Falling back to database-only scripts")
            all_scripts = db.get_all_scripts()
            
            # Filter out hidden scripts
            visible_scripts = [
                script for script in all_scripts 
                if script.id not in HIDDEN_SCRIPTS
            ]
            
            # Sort by order
            visible_scripts.sort(key=lambda x: x.order)
            
            logger.info(f"Fallback: returning {len(visible_scripts)} scripts from database")
            return visible_scripts
            
        except Exception as db_error:
            logger.error(f"Database fallback also failed: {db_error}")
            raise HTTPException(status_code=500, detail=f"Script retrieval failed: {str(e)}")


@router.get("/{script_id}", response_model=Script)
async def get_script_by_id(script_id: str):
    """Get specific script by ID from database"""
    try:
        # Check if script is hidden
        if script_id in HIDDEN_SCRIPTS:
            raise HTTPException(status_code=404, detail=f"Script {script_id} not found")
        
        # Get script from database
        script = db.get_script(script_id)
        
        if not script:
            # If not in database, try to sync from filesystem first
            try:
                filesystem_script = script_manager.get_script_by_id(script_id)
                if filesystem_script:
                    db.save_script(filesystem_script)
                    script = filesystem_script
                    logger.info(f"Synced script {script_id} from filesystem to database")
            except Exception as sync_error:
                logger.warning(f"Failed to sync script {script_id} from filesystem: {sync_error}")
        
        if not script:
            raise HTTPException(status_code=404, detail=f"Script {script_id} not found")
        
        return script
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get script {script_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
