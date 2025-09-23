from flask import Blueprint, jsonify, request

from libs.device_manager import DeviceManager
from libs.execution_manager import ExecutionManager
from libs.script_manager import ScriptManager

execution_bp = Blueprint("execution_bp", __name__)


@execution_bp.route("/api/execute/start", methods=["POST"])
def start_script():
    data = request.json
    device_id = data.get("device_id")
    script_id = data.get("script_id")
    game_options = data.get("game_options", {})

    if not device_id or not script_id:
        return jsonify({"error": "Missing device_id or script_id"}), 400

    device_manager = DeviceManager()
    script_manager = ScriptManager("scripts")
    execution_manager = ExecutionManager(device_manager)

    device = device_manager.get_device(device_id)
    script = script_manager.get_script(script_id)

    if not device:
        return jsonify({"error": "Device not found"}), 404
    if not script:
        return jsonify({"error": "Script not found"}), 404

    try:
        running_script = execution_manager.start_script(
            device_id, script_id, script.path, game_options
        )
        return (
            jsonify(
                {
                    "execution_id": running_script.id,
                    "status": "started",
                    "device": device.to_dict(),
                    "script": script.to_dict(),
                }
            ),
            202,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@execution_bp.route("/api/execute/stop", methods=["POST"])
def stop_script():
    data = request.json
    execution_id = data.get("execution_id")

    if not execution_id:
        return jsonify({"error": "Missing execution_id"}), 400

    device_manager = DeviceManager()
    execution_manager = ExecutionManager(device_manager)

    try:
        execution_manager.stop_script(execution_id)
        return jsonify({"status": "stopped"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@execution_bp.route("/api/execute/stop-all", methods=["POST"])
def stop_all_scripts():
    device_manager = DeviceManager()
    execution_manager = ExecutionManager(device_manager)

    stopped_count, errors = execution_manager.stop_all_scripts()

    return jsonify({"stopped_count": stopped_count, "errors": errors}), 200
