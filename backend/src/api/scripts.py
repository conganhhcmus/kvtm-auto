"""
Script API endpoints for KVTM Auto
Simplified script metadata operations
"""


from fastapi import APIRouter, HTTPException

from ..service.database import db
from ..service.script import script_manager
from ..models.api import ScriptResponse, ScriptListResponse, ScriptDetailResponse

router = APIRouter()

# Scripts to hide from UI
HIDDEN_SCRIPTS = ["_core", "open_game"]


@router.get("/", response_model=ScriptListResponse)
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

    # Convert to ScriptResponse format
    script_responses = [
        ScriptResponse(
            id=script.id,
            name=script.name,
            description=script.description,
            order=script.order,
            recommend=script.recommend
        )
        for script in visible_scripts
    ]

    return ScriptListResponse(scripts=script_responses, total=len(script_responses))


@router.get("/{script_id}", response_model=ScriptDetailResponse)
async def get_script_detail(script_id: str):
    """Get detailed information for a specific script"""
    script = db.get_script(script_id)

    if not script:
        raise HTTPException(status_code=404, detail=f"Script {script_id} not found")

    # Get file system metadata
    script_path = script_manager.get_script_path(script_id)
    path_str = None
    last_modified = None

    if script_path and script_path.exists():
        path_str = str(script_path)
        try:
            import datetime
            timestamp = script_path.stat().st_mtime
            last_modified = datetime.datetime.fromtimestamp(timestamp).isoformat()
        except Exception:
            pass

    return ScriptDetailResponse(
        id=script.id,
        name=script.name,
        description=script.description,
        order=script.order,
        recommend=script.recommend,
        path=path_str,
        last_modified=last_modified
    )