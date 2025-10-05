from flask import Blueprint, jsonify

from libs.device_manager import DeviceManager
from libs.script_manager import ScriptManager

device_bp = Blueprint("device_bp", __name__)

# Module-level singleton instance
device_manager = DeviceManager()
script_manager = ScriptManager("scripts")


@device_bp.route("/api/devices", methods=["GET"])
def list_devices():
    devices = device_manager.list_devices()
    return jsonify([device.to_dict() for device in devices])


@device_bp.route("/api/devices/<device_id>", methods=["GET"])
def get_device(device_id):
    device = device_manager.get_device(device_id)
    if not device:
        return jsonify({"error": "Device not found"}), 404

    # Get device dict and add script name
    device_dict = device.to_dict()
    if device.current_script:
        script = script_manager.get_script(device.current_script)
        device_dict["script_name"] = script.name if script else device.current_script
    else:
        device_dict["script_name"] = None

    return jsonify(device_dict)


@device_bp.route("/api/devices/<device_id>/logs", methods=["GET"])
def get_device_logs(device_id):
    device = device_manager.get_device(device_id)
    if not device:
        return jsonify({"error": "Device not found"}), 404
    return jsonify(device.get_logs(100))  # Return array directly
