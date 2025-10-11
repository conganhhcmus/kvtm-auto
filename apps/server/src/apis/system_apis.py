from datetime import datetime

from flask import Blueprint, jsonify

from libs.device_manager import DeviceManager
from libs.execution_manager import ExecutionManager
from libs.script_manager import ScriptManager

system_bp = Blueprint("system_bp", __name__)


@system_bp.route("/health", methods=["GET"])
def health_check():
    device_manager = DeviceManager()
    script_manager = ScriptManager("scripts")
    execution_manager = ExecutionManager(device_manager)

    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "devices": len(device_manager.list_devices()),
            "scripts": len(script_manager.list_scripts()),
            "running_scripts": len(execution_manager.running_scripts),
        }
    )
